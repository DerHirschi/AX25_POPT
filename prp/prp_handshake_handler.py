# prp/prp_handshake_handler.py
from cfg.logger_config import logger
from cli.cliStationIdent import get_station_id_obj
from fnc.str_fnc import version_tuple
from prp.prp_const import PRP_OPT_20, PRP_NACK, PRP_VER_RESTR_HANDSHAKE


class PRPHandshakeHandler:
    """
    Verantwortlich für den kompletten PRP-Handshake (OPT 20)
    inkl. Station-Identität und initialem State-Exchange.
    """

    def __init__(self, prp_root):
        self._prp_root      = prp_root
        self._state_manager = self._prp_root.prp_state_manager

        self._set_own_identy    = lambda val: self._state_manager.set_own('stat_identy', val)

        self._get_remote_identy = lambda:     self._state_manager.get_remote('stat_identy')
        self._set_remote_identy = lambda val: self._state_manager.set_remote('stat_identy', val)

        # Eigenen Stat Identy setzen
        self._set_own_identy(self.get_own_stat_identy())

        self._pending       = False  # Warte auf Response?

    @property
    def is_pending(self):
        return self._pending

    @property
    def is_completed(self):
        return self._state_manager.get_remote('stat_identy') is not None and not self._pending

    # ===================================================================
    # Öffentliche API
    # ===================================================================
    def initiate(self, short_format=False):
        """
        Startet den Handshake (CMD senden).
        Wird z. B. von CLI oder GUI aufgerufen.
        """
        own_identy = self.get_own_stat_identy()
        if not own_identy or not hasattr(own_identy, 'id_str'):
            logger.error("PRP Handshake: Keine eigene Station-Identität verfügbar")
            return False

        logger.info(f"PRP: Initiere Handshake mit {self._prp_root.uid}")

        self._set_own_identy(own_identy)
        self._pending = True
        self._notify_gui()

        identy_bytes = str(own_identy.id_str).encode('ASCII', 'ignore')

        if short_format:
            self._prp_root.prp_tx(opt_id=PRP_OPT_20, tx_flag=True, data=identy_bytes, prio=True)
            return True

        # Langes Format mit initialen States
        states_bytes = self._state_manager.encode_updates(self._state_manager.own)
        data = identy_bytes + b'\x00' + states_bytes

        self._prp_root.prp_tx(opt_id=PRP_OPT_20, tx_flag=True, data=data, prio=True)
        return True

    def handle_cmd(self, payload: bytes):
        """Empfängt Handshake-CMD (tx=True)"""
        if b'\x00' not in payload:
            return self._handle_short_format(payload)

        return self._handle_long_format(payload)

    def handle_resp(self, payload: bytes):
        """Empfängt Handshake-RESP (tx=False). Gibt True bei Erfolg zurück."""
        if payload == PRP_NACK:
            self._pending = False
            logger.warning(f"PRP: Handshake abgelehnt von {self._prp_root.uid}")
            self._set_remote_identy(None)
            self._notify_gui()
            return False

        if b'\x00' not in payload:
            success = self._handle_short_format(payload)
            if success:
                self._pending = False
                self._notify_gui()
            return success

        return self._handle_long_format(payload, is_response=True)

    def _send_response(self, success: bool, short_format=False):
        """Sendet Handshake-Response"""
        if not success:
            self._prp_root.prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=PRP_NACK, prio=True)
            return

        own_identy = self.get_own_stat_identy()
        if not own_identy or not hasattr(own_identy, 'id_str'):
            self._prp_root.prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=PRP_NACK, prio=True)
            return

        identy_bytes = str(own_identy.id_str).encode('ASCII', 'ignore')

        if short_format:
            self._prp_root.prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=identy_bytes, prio=True)
            return

        states_bytes = self._state_manager.encode_updates(self._state_manager.own)
        data = identy_bytes + b'\x00' + states_bytes
        self._prp_root.prp_tx(opt_id=PRP_OPT_20, tx_flag=False, data=data, prio=True)

    # ===================================================================
    # Interne Handler
    # ===================================================================
    def _handle_short_format(self, payload: bytes, is_response=False):
        """Altes Format: Nur Station-Identität"""
        try:
            identy_str = payload.decode('ASCII')
        except UnicodeDecodeError:
            logger.error(f"PRP Handshake: Unicode-Fehler bei Identität – UID: {self._prp_root.uid}")
            self._send_response(False)
            return False

        remote_identy = get_station_id_obj(identy_str)
        if remote_identy is None:
            logger.warning(f"PRP Handshake: Ungültige Identität empfangen – UID: {self._prp_root.uid}")
            self._send_response(False)
            return False

        logger.info(f"PRP Handshake: Identität akzeptiert – {remote_identy.software} {remote_identy.version}")
        self._set_remote_identy(remote_identy)

        if not is_response:
            self._send_response(True, short_format=True)

        return True

    def _handle_long_format(self, payload: bytes, is_response=False):
        """Neues Format: Identität + States"""
        identy_part, states_part = payload.split(b'\x00', 1)

        try:
            identy_str = identy_part.decode('ASCII')
        except UnicodeDecodeError:
            logger.error(f"PRP Handshake: Unicode-Fehler bei Identität – UID: {self._prp_root.uid}")
            self._send_response(False)
            return False

        remote_identy = get_station_id_obj(identy_str)
        if remote_identy is None:
            logger.warning(f"PRP Handshake: Ungültige Identität – UID: {self._prp_root.uid}")
            self._send_response(False)
            return False

        self._set_remote_identy(remote_identy)
        logger.info(f"PRP Handshake: Identität akzeptiert – {remote_identy.software} {remote_identy.version}")

        # States verarbeiten
        if states_part:
            updates = self._state_manager.decode_payload(states_part)
            if updates:
                self._state_manager.update_remote(updates)
                logger.info(f"PRP: Initiale Remote-States übernommen: {updates}")

        if not is_response:
            self._send_response(True)

        if is_response:
            self._pending = False
        self._notify_gui()

        return True

    def _notify_gui(self):
        gui = self._prp_root.gui
        if hasattr(gui, 'init_popt_remote'):
            gui.init_popt_remote(self._prp_root.uid)

    # ===================================================================
    # Helper
    # ===================================================================
    def get_own_stat_identy(self):
        """ Holt eigens Stat Identy Obj von CLI """
        if not hasattr(self._prp_root.cli, 'get_own_stat_identy'):
            logger.error(f"PRP: Attribute Error: _get_own_stat_identy")
            return None
        return self._prp_root.cli.get_own_stat_identy()

    # ===================================================================
    # CLI-Integration
    # ===================================================================
    def init_from_cli(self, remote_identy):
        """Wird von CLI aufgerufen, wenn Gegenstation identifiziert wurde"""
        if 'PoPT' not in remote_identy.software:
            logger.debug("PRP: Keine PoPT-Station – kein Handshake nötig")
            return

        if version_tuple(remote_identy.version) < version_tuple(PRP_VER_RESTR_HANDSHAKE):
            logger.warning("PRP: Gegenstation zu alt für Handshake")
            return

        self._set_remote_identy(remote_identy)
        self.initiate(short_format=False)
        self._notify_gui()