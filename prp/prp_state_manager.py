# prp/prp_state_manager.py
import copy

from cfg.logger_config import logger
from prp.prp_const import PRP_OPT_STATE_UPDATE, PRP_ACK, PRP_NACK, PRP_IS_ACK


class PRPStateManager:
    """
    Verantwortlich für:
    - Lokale States (_own_states)
    - Remote States (_remote_states)
    - Pending ACKs für State-Updates
    - Encoding/Decoding von State-Payloads (Handshake + OPT 26)
    - Validierung bei lokalen State-Änderungen
    - Private-State-Schutz
    """

    def __init__(self, prp_root):
        self._prp_root = prp_root

        # =======================================================
        # Init Own States / States der eigenen Station
        self._own_states = dict(
            # == Handshake / Station Cap
            stat_identy     = None,  # Station Identy Obj / !! PRIVATE !!!

            # == Remote Monitor
            cli_rem_mon     = False,    # TODO Remote Monitor CLI Stream
            gui_rem_mon     = False,    # Remote Monitor Stream
            rem_mon_port    = 0,        # Port Filter
            rem_mon_incl    = [],       # Incl Filter
            rem_mon_excl    = [],       # Excl Filter

            # == Batch Mode / vorrest nur für Mon Stream
            batch_mode      = 'auto',   # 'auto', 'on', 'off'
            batch_wait      = 60,       # Sekunden Pakete sammeln

            # == Remote CTL/States
            cli_esc         = False,    # CLI-ESC Mode (sendet CLI Stream komprimiert)

            # == Login/Auth
            login_ok        = False,    # Auth OK / !! PRIVATE !!!
        )

        # == Benötigt Rechte
        self._check_rights = ('gui_rem_mon', 'cli_rem_mon', 'cli_esc')

        # =======================================================
        # Init Remote States / Bestätigt States der Gegenstation
        self._remote_states     = copy.deepcopy(self._own_states)

        # == !! PRIVATE STATES !!
        self._private_states    = {'login_ok', 'stat_identy'}

        # == Remote States ACK
        self._pending_remote_states = {}  # opt_id → state_cfg

        # Key-Index für stabile Serialisierung
        self._ordered_keys  = list(self._own_states.keys())

    # ===================================================================
    # Lokale States (Own)
    # ===================================================================
    def get_own(self, key: str):
        return self._own_states.get(key)

    def set_own(self, key: str, value):
        if key not in self._own_states:
            logger.error(f"PRPStateManager: Unbekannter Key '{key}'")
            return False

        current = self._own_states[key]
        current_type = type(current)

        # Typprüfung
        if current_type is list:
            if not isinstance(value, (list, tuple)):
                logger.error(f"PRPStateManager: Key '{key}' erwartet list/tuple")
                return False
        elif key == 'batch_mode':
            if value not in ('auto', 'on', 'off'):
                logger.error(f"PRPStateManager: Ungültiger batch_mode '{value}'")
                return False
        elif not isinstance(value, current_type):
            logger.error(f"PRPStateManager: Key '{key}' erwartet {current_type}, bekam {type(value)}")
            return False

        # Plausibilität
        if key == 'rem_mon_port' and not (0 <= value <= 19):
            logger.error(f"PRPStateManager: rem_mon_port außerhalb 0-19: {value}")
            return False

        if key in self._private_states:
            logger.warning(f"Lokaler Zugriff auf privaten State '{key}' = {value}")

        self._own_states[key] = value
        logger.debug(f"PRP State updated: {key} = {value}")
        return True

    def update_own(self, cfg: dict):
        """Validiert und setzt mehrere States atomar"""
        if not isinstance(cfg, dict):
            logger.error("PRPStateManager: update_own erwartet dict")
            return False
        if not cfg:
            return True

        validated = {}
        for key, value in cfg.items():
            if key not in self._own_states:
                logger.error(f"PRPStateManager: Unbekannter Key '{key}'")
                return False

            current_type = type(self._own_states[key])
            if current_type is list and not isinstance(value, (list, tuple)):
                logger.error(f"PRPStateManager: Key '{key}' erwartet list/tuple")
                return False
            if key == 'batch_mode' and value not in ('auto', 'on', 'off'):
                logger.error(f"PRPStateManager: Ungültiger batch_mode '{value}'")
                return False
            if not isinstance(value, current_type):
                logger.error(f"PRPStateManager: Key '{key}' erwartet {current_type}")
                return False
            if key == 'rem_mon_port' and not (0 <= value <= 19):
                logger.error(f"PRPStateManager: rem_mon_port außerhalb 0-19")
                return False

            validated[key] = value

        for key, value in validated.items():
            if key in self._check_rights:
                if not self._prp_root.prp_rights.is_function_allowed(self._prp_root.to_call_str, key):
                    continue
            self._own_states[key] = value
            logger.debug(f"PRP State updated: {key} = {value}")

        logger.info(f"PRPStateManager: {len(validated)} States aktualisiert")
        return True

    @property
    def own(self):
        return self._own_states

    @property
    def remote(self):
        return self._remote_states
    # ===================================================================
    # Remote States
    # ===================================================================
    def get_remote(self, key: str):
        return self._remote_states.get(key)

    def set_remote(self, key: str, value):
        if key in self._remote_states:
            self._remote_states[key] = value

    def update_remote(self, cfg: dict):
        self._remote_states.update(cfg)

    # ===================================================================
    # Pending ACKs
    # ===================================================================
    def add_pending(self, opt_id: int, cfg: dict):
        if opt_id in self._pending_remote_states:
            logger.warning(f"PRPStateManager: OPT-ID {opt_id} bereits pending – überschreibe")
        self._pending_remote_states[opt_id] = cfg

    def ack_pending_remote_states(self, opt_id: int):
        if not self._ack_pending(opt_id):
            logger.error(
                f"RPR: ACK-BufferError: OPT-ID({opt_id}) nicht gefunden in self._pending_remote_states.")
            logger.error("RPR:   self._pending_remote_states:")
            for k, val in self._pending_remote_states.items():
                logger.error(f"RPR:   {k}: {val}")
            return
        # Update Remote States
        self._ack_pending(opt_id)
        # Lösche aus Pending Buffer
        self.del_pending(opt_id)

    def _ack_pending(self, opt_id: int):
        if opt_id not in self._pending_remote_states:
            logger.error(f"PRPStateManager: ACK für unbekannte OPT-ID {opt_id}")
            return False
        cfg = self._pending_remote_states.pop(opt_id)
        self.update_remote(cfg)
        return True

    def del_pending(self, opt_id: int):
        self._pending_remote_states.pop(opt_id, None)

    @property
    def pending_states(self):
        return self._pending_remote_states

    # ===================================================================
    # State Encoding / Decoding
    # ===================================================================
    def encode_updates(self, updates: dict):
        """Serialisiert nur öffentliche States"""
        payload = bytearray()
        for key, value in updates.items():
            if key not in self._ordered_keys:
                continue
            if key in self._private_states:
                logger.warning(f"PRPStateManager: Versuch privaten State '{key}' zu senden – blockiert")
                continue

            key_id = self._ordered_keys.index(key)
            value_bytes = self._encode_value(key, value)
            if value_bytes is None:
                continue

            payload.append(key_id)
            payload.append(len(value_bytes))
            payload.extend(value_bytes)

        return bytes(payload)

    def decode_payload(self, payload: bytes):
        """Dekodiert State-Payload (Handshake oder OPT 26)"""
        i = 0
        updates = {}
        while i + 2 <= len(payload):
            key_id = payload[i]
            val_len = payload[i + 1]
            i += 2
            if i + val_len > len(payload):
                break

            if key_id >= len(self._ordered_keys):
                i += val_len
                continue

            key = self._ordered_keys[key_id]
            if key in self._private_states:
                logger.warning(f"PRPStateManager: Empfangen privater State '{key}' – ignoriert")
                i += val_len
                continue

            value_data = payload[i:i + val_len]
            value = self._decode_value(key, value_data)
            if value is not None:
                updates[key] = value

            i += val_len

        return updates

    @staticmethod
    def _encode_value(key: str, value):
        if key in ['cli_rem_mon', 'gui_rem_mon', 'cli_esc', 'login_ok']:
            return bytes([1 if value else 0])
        if key == 'rem_mon_port':
            return bytes([value & 0xFF])
        if key == 'batch_wait':
            return value.to_bytes(2, 'little')
        if key == 'batch_mode':
            modes = {'auto': 0, 'on': 1, 'off': 2}
            return bytes([modes.get(value, 0)])
        if key in ['rem_mon_incl', 'rem_mon_excl']:
            if not value:
                return b'\x00\x00'
            return '\x00'.join(value).encode('UTF-8', 'ignore') + b'\x00\x00'
        return None

    @staticmethod
    def _decode_value(key: str, data: bytes):
        if key in ['cli_rem_mon', 'gui_rem_mon', 'cli_esc', 'login_ok']:
            return bool(data[0])
        if key == 'rem_mon_port':
            return data[0]
        if key == 'batch_wait':
            return int.from_bytes(data, 'little')
        if key == 'batch_mode':
            modes = {0: 'auto', 1: 'on', 2: 'off'}
            return modes.get(data[0], 'auto')
        if key in ['rem_mon_incl', 'rem_mon_excl']:
            if len(data) < 2 or data[-2:] != b'\x00\x00':
                return []
            parts = data[:-2].split(b'\x00')
            return [p.decode('UTF-8', 'ignore') for p in parts if p]
        return None

    # ===================================================================
    # Helper
    # ===================================================================
    def is_private(self, key: str):
        return key in self._private_states

    def has_changed(self, updates: dict, key: str):
        return key in updates and updates[key] != self.get_own(key)

    # ===================================================================
    # API für PRP Protokoll handler
    # ===================================================================

    def rx_remote_state_update(self, payload: bytes):
        updates = self.decode_payload(payload)
        if not updates:
            self._tx_resp_remote_state_update(applied_updates=None)
            self._prp_root.handle_response(PRP_OPT_STATE_UPDATE)
            return

        # Prüfe Rechte + Validierung → sammle erlaubte
        applied_updates = {}
        for key, value in updates.items():
            if key in self._check_rights:
                if not self._prp_root.prp_rights.is_function_allowed(self._prp_root.to_call_str, key):
                    logger.info(f"PRP State: {key} abgelehnt (Rechte fehlen)")
                    continue
            # Weitere Validierung...
            if self.set_own(key, value):  # Oder direkt in update_own
                applied_updates[key] = value

        # Response mit tatsächlich übernommenen States
        self._tx_resp_remote_state_update(applied_updates=applied_updates)

        # Aktionen ausführen (z. B. Monitor abort bei gui_rem_mon=False)
        self._response_state_update(applied_updates)

        self._prp_root.handle_response(PRP_OPT_STATE_UPDATE)

    # == Response
    def _tx_resp_remote_state_update(self, applied_updates: dict = None):
        """Sendet Response mit den tatsächlich übernommenen States"""
        if applied_updates is None:
            # Fallback: Alles abgelehnt → NACK + leer
            data = PRP_NACK
        else:
            # Encode nur die übernommenen Keys (oder alle relevanten)
            data = self.encode_updates(applied_updates)
            if not data:
                data = PRP_ACK  # Leeres ACK wenn nichts geändert

        self._prp_root.prp_tx(
            opt_id=PRP_OPT_STATE_UPDATE,
            tx_flag=False,
            data=data,
            prio=True
        )

    def rx_resp_remote_state_update(self, payload: bytes):
        """Empfängt Response auf eigenes State-Update"""
        pending = self.pending_states.get(PRP_OPT_STATE_UPDATE, {})

        if len(payload) == 1:
            if payload == PRP_NACK:
                logger.warning(f"PRP: State-Update komplett abgelehnt - UID: {self._prp_root.uid}")
                # Pending behalten für Retry? Oder löschen?
                # self.del_pending(PRP_OPT_STATE_UPDATE)  # Optional: löschen
                return

            if payload == PRP_ACK:
                logger.info("PRP: State-Update akzeptiert (keine Änderung nötig)")
                # Alles übernommen → remote = pending
                self.update_remote(pending)
                self.del_pending(PRP_OPT_STATE_UPDATE)
                return

        # Vollständige Response: Parse die bestätigten States
        confirmed_states = self.decode_payload(payload)
        logger.info(f"PRP: State-Update bestätigt: {confirmed_states}")

        # Immer remote_states mit bestätigten Werten aktualisieren
        self.update_remote(confirmed_states)

        if not pending:
            logger.debug("PRP: Kein pending Update vorhanden")
            return

        # Vergleich: Welche gesendeten States wurden übernommen?
        all_confirmed = True
        for key, sent_val in pending.items():
            recv_val = confirmed_states.get(key)
            if recv_val != sent_val:
                logger.warning(f"PRP: {key} nicht übernommen (gesendet: {sent_val}, bestätigt: {recv_val})")
                all_confirmed = False
            else:
                logger.debug(f"PRP: {key} erfolgreich übernommen")

        # Nur pending löschen, wenn alles bestätigt wurde
        if all_confirmed:
            logger.info("PRP: Alle gesendeten States bestätigt → pending gelöscht")
            self.del_pending(PRP_OPT_STATE_UPDATE)
        else:
            logger.info("PRP: Teilweise Übernahme → pending bleibt für Retry")
            # Optional: Retry-Logik später

    # == Response nach, erhalten eines Updates
    def _response_state_update(self, state_update: dict):
        """ Checke State-updates auf Änderungen und führe Action aus """
        # == Remote Monitor
        if self.has_changed(state_update, 'gui_rem_mon'):
            # == Remote Monitor STOP
            if not state_update['gui_rem_mon']:
                # == Lösche TX-Buffer & sende ABORT-Resp
                self._prp_root.prp_remote_monitor.abort()
                return
        # == CLI-ESC Sync
        if self.has_changed(state_update, 'cli_esc'):
            # == Sync CLI-ESC Own State with remote State
            self.set_remote('cli_esc', state_update['cli_esc'])
