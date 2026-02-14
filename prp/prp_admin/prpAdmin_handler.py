# prp/prp_admin/prpAdmin_handler.py
"""
PRP-Admin-Paket:
Frame-Struktur (nach bestehender PRP-Spec):
+--------+--------+--------+--------+--------+-----------+-------+----- ~ ----------------+--------+--------+
|  FLAG  |  FLAG  | OPTBYTE|   LEN (2B LE)   | ADMIN-FLAG|  SEQ  |        PAYLOAD         | CRC16  | CRC16  |
|  0x8D  |  0x81  |   27   |   LSB  MSB      |  (1 Byte) | (1B)  |    (var, opt. enc)     | low    | high   |
+--------+--------+--------+--------+--------+-----------+-------+----- ~ ----------------+--------+--------+

OPTBYTE (wie bei allen PRP-Steuerbefehlen):
    Bit 7 6 5 4 3 2 1 0
    +---+---+---+---+---+---+---+---+
    |F2 |F1 | 0   1   1   0   1   1 |   ← 27 = 0x1B → Bits 0-5 = 011011
    +---+---+---+---+---+---+---+---+
    Bit 7 = F2 (Compressed)
    Bit 6 = F1 (TX=1 = Request, TX=0 = Response)
    Bits 5-0 = 27 (0x1B)


PRP-ADMIN-FLAG-Byte (Byte 5):
Bit 7 6 5 4 3 2 1 0
    +---+---+---+---+---+---+---+---+
    |E  |R  |R  | Sub-OP-ID (0-31)  |
    +---+---+---+---+---+---+---+---+
    Bit 7 = E (Encrypted: Payload ab Byte 7 verschlüsselt)
    Bit 6-5 = Reserved (für Zukunft: Multi-Part, Priority, etc.)
    Bit 4-0 = Sub-OP-ID (0–31 → 32 Admin-Funktionen)

SEQ-Byte (Byte 6):
  - uint8, Modulo 256 (0–255)

PAYLOAD (ab Byte 7):
  - Variable Länge
  - Wenn E=1 → verschlüsselt
  - Inhalt abhängig von Sub-OP-ID (z. B. binär, JSON, Text)


"""
from datetime import datetime

from cfg.logger_config import PRP_ADMIN_LOG
from prp.prp_const import PRP_OPT_PRP_ADMIN, PRP_FNC_PRP_ADMIN

from .prpAdmin_decoder import PRPAdminDecoder
from .prpAdmin_processor import PRPAdminProcessor

logger = PRP_ADMIN_LOG


# Sub-OP-IDs (0–31)
ADMIN_SUB_OP = {
    'GET_CONFIG':       0,
    'SET_CONFIG':       1,
    'GET_USERDB':       2,
    'SET_USERDB':       3,
    'GET_STATS':        4,
    'CLEAR_STATS':      5,
    'GET_LOGS':         6,
    'CLEAR_LOGS':       7,
    'DISCONNECT_ALL':   8,
    'RESTART_POPT':     9,
    'REBOOT':           10,
    'SHUTDOWN':         11,
}

SUB_OP_NAME = {v: k for k, v in ADMIN_SUB_OP.items()}


class PRPAdminHandler:
    def __init__(self, prp_root):
        self._prp_root              = prp_root
        self._init_client_call      = str(self._prp_root.to_call_str)

        self._prp_rights_manager    = prp_root.prp_rights

        # PRP-Admin Classes
        self._decoder   = PRPAdminDecoder()
        self._processor = PRPAdminProcessor(self)

        # Module (später befüllen)
        self._modules = []
        self._module_map = {}

        # Pending Requests (Client-Seite)
        self._pending_requests = {}

    @property
    def prp_root(self):
        return self._prp_root

    @property
    def uid(self):
        return str(self._prp_root.uid)

    @property
    def has_admin_access(self):
        if self._init_client_call != self._prp_root.to_call_str:
            logger.error(
                f"PRP Admin [{self.uid}]: Zugriff Verweigert! Client Call hat sich geändert! {self._init_client_call} > {self._prp_root.to_call_str}")
            return False
        return self._prp_rights_manager.is_function_allowed(self._prp_root.to_call_str, PRP_FNC_PRP_ADMIN)

    # ===================================================================
    # Öffentliche API
    # ===================================================================
    def handle_admin_frame(self, payload: bytes, is_tx: bool, prio=True):
        """is_tx = True → eingehender Request (Server), False → Response (Client)"""
        seq_nr = self._prp_root.prp_transport.get_current_seq(
                                                              prio=prio,)
        if not self.has_admin_access and is_tx:
            self.send_nack()
            return

        decoded = self._decoder.decode_payload(payload)
        data    = decoded['data']

        if decoded['encrypted']:
            try:
                # TODO Crypto
                data = self._prp_root.auth.decrypt_payload(data)
            except Exception as ex:
                null = ex
                if is_tx:
                    self.send_nack()
                return

        if is_tx:
            # Server: Request empfangen
            self._processor.process_request(self.uid, decoded['sub_op_id'], seq_nr, data)
        else:
            # Client: Response empfangen
            self._handle_response(seq_nr, decoded['sub_op_id'], data)

    def handle_cli_input(self, payload):
        if not self.has_admin_access:
            logger.warning(f"PRP Admin [{self.uid}]: Zugriff verweigert (keine Admin-Rechte)")
            return ''
        # TODO: CLI-Parser später
        return ''

    # ===================================================================
    # Client: Admin-Request senden
    # ===================================================================
    def send_admin_request(self, sub_op_id, payload=b'', encrypted=False):
        if sub_op_id not in self._module_map:
            logger.error(f"PRP Admin: Unbekannte Sub-OP {sub_op_id}")
            return False

        # Seq vom Processor holen (Client-Seite verwendet expected_seq als next send)
        #seq = self._processor.get_next_seq(self.uid)
        admin_flag = (0x80 if encrypted else 0x00) | (sub_op_id & 0x1F)

        full_payload = bytearray()
        full_payload.append(admin_flag)
        #full_payload.append(seq)
        full_payload.extend(payload)

        if encrypted:
            # TODO Crypto
            full_payload[1:] = self._prp_root.auth.encrypt_payload(full_payload[1:])

        success = self._send_admin_frame(request=True, data=bytes(full_payload))
        if isinstance(success, int):
            seq     = int(success)
            success = True # int 0 = True
        else:
            seq = 0

        if success:
            self._pending_requests[seq] = {
                'op': sub_op_id,
                'ts': datetime.now(),
                'callback': self._default_response_callback
            }

        return success

    # ===================================================================
    # Server: Sub-OP ausführen
    # ===================================================================
    def execute_sub_op(self, uid, sub_op_id, payload):
        module = self._module_map.get(sub_op_id)
        if not module:
            logger.warning(f"PRP Admin [{uid}]: Unbekannte Sub-OP {sub_op_id}")
            self.send_nack()
            return

        if not self.has_admin_access:
            logger.warning(f"PRP Admin [{uid}]: Zugriff verweigert")
            self.send_nack()
            return

        try:
            response = module.handle(payload)
            self.send_response(response)
        except Exception as e:
            logger.error(f"PRP Admin [{uid}]: Sub-OP Fehler {sub_op_id}: {e}")
            self.send_nack()

    # ===================================================================
    # Client: Response empfangen
    # ===================================================================
    def _handle_response(self, seq, sub_op_id, payload):
        pending = self._pending_requests.get(seq)
        if not pending:
            logger.debug(f"PRP Admin [{self.uid}]: Unerwartete Response Seq {seq}")
            return

        try:
            pending['callback'](sub_op_id, payload)
        except Exception as e:
            logger.error(f"PRP Admin [{self.uid}]: Callback-Fehler: {e}")

        del self._pending_requests[seq]

    # ===================================================================
    # Response/NACK senden (Server)
    # ===================================================================
    def send_response(self, data=b'', encrypted=False):
        # Seq = 0 für Responses
        admin_flag = (0x80 if encrypted else 0x00)
        full_payload = bytearray([admin_flag, 0]) + data
        self._send_admin_frame(request=False, data=bytes(full_payload))

    def send_nack(self):
        self._send_admin_frame(request=False, data=b'\x00\x00')  # Flag=0, Seq=0

    def _default_response_callback(self, sub_op_id, payload):
        op_name = SUB_OP_NAME.get(sub_op_id, "UNKNOWN_OP")
        logger.info(f"PRP Admin Response [{self.uid}]: {op_name} – {len(payload)} Bytes")

    # ===================================================================
    # Frame senden
    # ===================================================================
    def _send_admin_frame(self, request, data, prio=True):
        """

        :param request:
        :param data:
        :param prio:
        :return: seq(int) or None
        """
        return self._prp_root.prp_tx_reliable(opt_id=PRP_OPT_PRP_ADMIN, tx_flag=request, data=data, prio=prio)

