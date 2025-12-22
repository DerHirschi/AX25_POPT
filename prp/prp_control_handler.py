# prp/prp_control_handler.py
from cfg.logger_config import logger
from prp.prp_const import PRP_OPT_21, PRP_OPT_DISCO, PRP_OPT_ESC_CLI, PRP_OPT_PRP_BATCH


class PRPControlHandler:
    """
    Verantwortlich für allgemeine Steuerbefehle (CTL)
    - OPT 21: Abort (CLI-ESC Abbruch)
    - OPT 22: Disconnect
    """

    def __init__(self, prp_root):
        self._prp_root  = prp_root
        self._tx_buffer = prp_root.prp_tx_buffer
        self._protocol  = prp_root.prp_protocol
        self._cli_esc   = prp_root.prp_cli_esc

    # ===================================================================
    # Öffentliche API
    # ===================================================================
    def handle_remote_mon_abort(self):
        """Client: Sendet Abort-Request (Remote Monitor Stop)"""
        if not self._prp_root.is_handshake:
            return False
        self._handle_rem_mon_abort_request()
        return True

    def send_cli_esc_abort_request(self):
        if not self._prp_root.is_handshake:
            return False

        logger.debug(f"PRP Control: Sende Abort-Request – UID: {self._prp_root.uid}")
        self._handle_cli_esc_abort_request()
        return True

    def send_disconnect(self):
        """Client: Startet Disconnect"""
        if not self._prp_root.is_handshake:
            return False

        logger.info(f"PRP Control: Sende Disconnect – UID: {self._prp_root.uid}")
        self._prp_root.prp_tx(opt_id=PRP_OPT_DISCO, tx_flag=True, data=b'', prio=True)
        return True

    # ===================================================================
    # Eingehende Nachrichten (vom ProtocolHandler aufgerufen)
    # ===================================================================
    def handle_abort(self, tx: bool, payload: bytes):
        """OPT 21: Abort"""
        if tx:
            # Empfangen: Abort-Request → Server bricht Senden ab
            self._handle_cli_esc_abort_request()
        else:
            # Empfangen: Abort-Response → Client bricht Empfang ab
            self._handle_abort_response()

    def handle_disconnect(self, tx: bool, payload: bytes):
        """OPT 22: Disconnect"""
        if tx:
            # Empfangen: Disconnect-Request → Server trennt
            self._handle_disconnect_request()

    # ===================================================================
    # Interne Logik
    # ===================================================================
    def _handle_rem_mon_abort_request(self):
        logger.debug(f"PRP Control: Sende Abort-Frame – UID: {self._prp_root.uid}")
        # == lösche TX Buffer
        self._tx_buffer.del_tx_buff(PRP_OPT_PRP_BATCH)
        # == Sende Abort Frame
        self._prp_root.prp_tx(opt_id=PRP_OPT_21, tx_flag=False, data=b'', prio=True)

    def _handle_cli_esc_abort_request(self):
        """Server: Empfängt Abort-Request (Client bricht großes CLI-ESC-Paket ab)"""
        logger.info(f"PRP Control: Abort-Request empfangen – breche Senden ab – UID: {self._prp_root.uid}")

        # Status an GUI
        self._cli_esc.send_abort_sender_status()

        logger.debug(f"PRP: Lösche TX-Buffer (aktuellen Frame)und sende Abort RESP Frame: {self._prp_root.uid}")
        # TX-Buffer für CLI-ESC leeren
        self._tx_buffer.del_tx_buff(PRP_OPT_ESC_CLI)

        # Abort-Response senden
        self._prp_root.prp_tx(opt_id=PRP_OPT_21, tx_flag=False, data=b'', prio=True)

    def _handle_abort_response(self):
        """Client: Empfängt Abort-Response (Server hat Empfang abgebrochen)"""
        logger.info(f"PRP Control: Abort-Response empfangen – breche Empfang ab – UID: {self._prp_root.uid}")


    # == Disco
    def _handle_disconnect_request(self):
        """Server: Empfängt Disconnect"""
        logger.info(f"PRP Control: Disconnect empfangen – trenne Verbindung – UID: {self._prp_root.uid}")

        # Remote Monitor deaktivieren
        self._prp_root.prp_state_manager.set_own('gui_rem_mon', False)
        self._prp_root.prp_state_manager.set_own('cli_rem_mon', False)

        # TX-Buffer leeren
        self._tx_buffer.del_tx_buff(None)

        # Verbindung trennen
        self._prp_root.connection.conn_disco()