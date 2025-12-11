"""
(P)oPT (R)emote (P)rotocol
"""
import copy
import datetime
import hashlib
import os
import time

from ax25.ax25Error import AX25DecodingERROR
from cfg.logger_config import logger
from fnc.ax25_fnc import reverse_uid
from fnc.crc_fnc import crc16_ccitt
from fnc.lzhuf import LZHUF_Comp
from ax25.ax25dec_enc import AX25Frame, bytearray2hexstr
from fnc.str_fnc import version_tuple

####################################################################################
PRP_SW_RESTR             = 'PoPT'      # Software restriction
PRP_VER_RESTR            = '2.123.7'   # Version restriction
PRP_VER_RESTR_BATCH_MODE = '2.123.9'   # Version restriction
####################################################################################
PRP_FLAG = b'\x8D\x81'      # PRP Flag
####################################################################################
# ESC & END Flags
PRP_FEND  = b'\x8D'
PRP_FESC  = b'\x8F'
PRP_TFEND = b'\x92'
PRP_TFESC = b'\x9B'

PRP_FESC_TFEND = b''.join([PRP_FESC, PRP_TFEND])    # "FEND is sent as FESC, TFEND"  /  0x8D is sent as 0x8F 0x92
PRP_FESC_TFESC = b''.join([PRP_FESC, PRP_TFESC])    # "FESC is sent as FESC, TFESC"  /  0x8F is sent as 0x8F 0x9B
####################################################################################
# OPT-ID ≥ 20
PRP_OPT_RM_START        = 20 # Leer
PRP_OPT_RM_STOP         = 21 # Remote Monitor Stop
PRP_OPT_DISCO           = 22 # Connection (soft)Disco
PRP_OPT_LOGIN_REQ       = 23 # Login Request
PRP_OPT_LOGIN_RESP      = 24 # Login Response
PRP_OPT_LOGOUT          = 25 # Logout
PRP_OPT_STATE_UPDATE    = 26 # State Update > PRP Einstellungen/Zustände ändern
PRP_OPT_ESC_CLI         = 62 # Payload wird an CLI durchgereicht
PRP_OPT_PRP_BATCH       = 63 # PRP-Frame Batch processing
####################################################################################
# ACK / Reposnse
PRP_DONT_ACK = (PRP_OPT_DISCO, PRP_OPT_LOGIN_REQ)
PRP_ACK      = b'O'
PRP_NACK     = b'F'
####################################################################################
# OPT Tab für Monitor
PRP_CTL_TAB = {
                20: 'RM Start/Update',
                21: 'RM Stop',
                22: 'Disconnect',
                23: 'Login REQ',
                24: 'Login RESP',
                25: 'Logout',
                26: 'State Update',
                62: 'CLI-ESC',
                63: 'BATCH',
               }
####################################################################################
# Response (GUI Handling)
# PRP_RM_RESP_START   = 'rsp_start'   # Remote Monitor Start/Update
# PRP_RM_RESP_STOP    = 'rsp_stop'    # Remote Monitor Stop
PRP_RM_RESP_LOGIN   = 'rsp_login'   # Remote Login OK
PRP_RM_RESP_LOGOUT  = 'rsp_logout'  # Remote Login FAILED | Logout
####################################################################################
# Parameter
PRP_BATCH_MAX_PAY  = 1024   # Max Raw-Data(PRP-Frames size) Threshold for Batch
PRP_BATCH_MIN_PACK = 4      # Min PRP-Frames to send as Batch
####################################################################################
DBUG_PW = 'test1234'


def pack_6bit_int_and_bool(value: int, flag1: bool = False, flag2: bool = False):
    """
    by Grok-AI
    Packt einen 6-Bit-Integer (0–63) und zwei boolesche Flags in ein einzelnes Byte.

    Bit-Aufbau:
        Bit 7       → flag2
        Bit 6       → flag1
        Bit 5–0     → value (6 Bit)

    Beispiel:
        value=45, flag1=True, flag2=False  → 0b00101101 → 45 + 64 = 109 → b'm'
    """
    if not (0 <= value <= 63):
        raise ValueError("6-Bit-Wert muss zwischen 0 und 63 liegen")

    byte_value = (
            (value & 0b00111111) |  # Bits 0–5: Wert
            ((1 if flag1 else 0) << 6) |  # Bit 6: flag1
            ((1 if flag2 else 0) << 7)  # Bit 7: flag2
    )

    return bytes([byte_value])

def unpack_6bit_int_and_bool(data):
    """
    by Grok-AI
    Entpackt ein Byte, das mit pack_6bit_int_and_bool() gepackt wurde.

    Rückgabe: (value: int, flag1: bool, flag2: bool)
    """
    if len(data) < 1:
        raise ValueError("Mindestens ein Byte erforderlich")

    byte  = data[0]
    value = byte & 0b00111111  # Bits 0–5
    flag1 = bool(byte & 0b01000000)  # Bit 6 → 64
    flag2 = bool(byte & 0b10000000)  # Bit 7 → 128

    return value, flag1, flag2

def pack_time_hms(datetime_now):
    """
    by Grok-AI
    Packt aktuelle Uhrzeit (HH:MM:SS) in 3 Bytes BCD – super platzsparend und 100% verlustfrei
    """
    now = datetime_now
    hh = now.hour
    mm = now.minute
    ss = now.second

    # BCD: jedes Nibble = eine Dezimalstelle (0–9)
    return bytes([
        (hh // 10 << 4) | (hh % 10),  # Stunde  00–23 → 0x00–0x23
        (mm // 10 << 4) | (mm % 10),  # Minute  00–59 → 0x00–0x59
        (ss // 10 << 4) | (ss % 10),  # Sekunde 00–59 → 0x00–0x59
    ])

def unpack_time_hms_to_datetime(data: bytes):
    """
    by Grok-AI
    Wandelt die 3 BCD-Bytes wieder in ein echtes datetime-Objekt um
    (Datum = heute, also perfekt für Anzeige im Log oder GUI)
    """
    if len(data) < 3:
        raise ValueError("Brauche 3 Bytes für HH:MM:SS")

    hh = ((data[0] >> 4) & 0x0F) * 10 + (data[0] & 0x0F)
    mm = ((data[1] >> 4) & 0x0F) * 10 + (data[1] & 0x0F)
    ss = ((data[2] >> 4) & 0x0F) * 10 + (data[2] & 0x0F)

    # Heutiges Datum + empfangene Uhrzeit
    return datetime.datetime.now().replace(hour=hh, minute=mm, second=ss, microsecond=0)

# --------------------------------------------------------------
# PRP-METADATEN-DECODER (nur Header, keine Payload-Dekodierung!)
# --------------------------------------------------------------
# Rückgabe: dict mit:
#   'prp_frames'    → Anzahl enthaltener PRP-Frames (bei Batch)
#   'opt_id'        → 0–63 (Port-ID oder Steuerbefehl)
#   'opt_typ'       → Typ Steuerbefehle
#   'tx'            → True = gesendet, False = empfangen
#   'compressed'    → True wenn F2=1 (LZHUF)
#   'payload_len'   → Länge des (escaped) Payloads
#   'is_batch'      → True wenn OPT-ID == 63
#   'raw_len'       → Gesamtlänge des PRP-Pakets
# --------------------------------------------------------------

def decode_prp_metadata(raw_ax25_payload: bytes):
    """
    Vorlage by Grok AI
    Schneller PRP-Header-Parser für Monitor – nur Metadaten, keine Dekompression, kein Unescaping.
    Gibt None zurück, wenn kein gültiges PRP-Paket erkannt wurde.
    """
    # TODO bessere PRP-Paket validierung.
    #  PRP-Frames mit unbekannter OPT und unplausibler len werden als PRP dekodiert.
    payload_len = len(raw_ax25_payload)
    # Min: FLAG(2) + OPT(1) + LEN(2)
    if payload_len < 5:
        return None, raw_ax25_payload
    # PRP Flag in Payload ?
    if not PRP_FLAG in raw_ax25_payload:
        return None, raw_ax25_payload

    i          = 0
    prp_frames = []
    rest_data  = bytearray()
    while i < payload_len:
        # Flag in rest payload ? > Return
        if not PRP_FLAG in raw_ax25_payload[i:]:
            rest_data += raw_ax25_payload[i:]
            return prp_frames, rest_data
        # < 5 Bytes, Paket kann nicht ausgewertet werden. > Return
        if payload_len - i < 5:
            rest_data += raw_ax25_payload[i:]
            return prp_frames, rest_data
        # PRP-Flag bei i:i +2 ? > weiter
        if raw_ax25_payload[i:i + 2] != PRP_FLAG:
            rest_data += raw_ax25_payload[i].to_bytes(1)
            i         += 1
            continue
        # Versuche Header zu dekodieren
        try:
            # Header
            opt_byte  = int(raw_ax25_payload[2]).to_bytes(1)
            prp_len   = int.from_bytes(raw_ax25_payload[3:5], 'little')
            total_len = 5 + prp_len + 2  # Header(5) + Payload + CRC(2)
            # Opt
            opt_id, tx_flag, compressed = unpack_6bit_int_and_bool(opt_byte)
            opt_typ = PRP_CTL_TAB.get(opt_id, '')
            port_id = opt_id if opt_id < 20 else None
            # Validiere ob Opt Typ existiert
            if port_id is None and not opt_typ:
                rest_data += raw_ax25_payload[i].to_bytes(1)
                i += 1
                continue
            # PRP Batch Packet ?
            is_batch = (opt_id == 63)

            prp_frames.append({
                'is_prp'        : True,
                'opt_id'        : opt_id,
                'opt_typ'       : opt_typ,
                'port_id'       : port_id,
                'tx'            : tx_flag,
                'compressed'    : compressed,
                'payload_len'   : prp_len,
                'total_len'     : total_len,
                'is_batch'      : is_batch,
                'ctl_type'      : 'PRP-Batch' if is_batch else
                                  ('PRP-Mon' if opt_id < 20 else 'PRP-Cmd'),
            })
            i = i + total_len

        except Exception as ex:
            null       = ex   # Make my IDE happy :-)
            rest_data += raw_ax25_payload[i].to_bytes(1)
            i         += 1
            continue

    return prp_frames, rest_data

class PRPremote:
    def __init__(self, port_handler , connection):
        self._port_handler = port_handler
        self._connection   = connection
        self._get_uid      = lambda : self._connection.uid

        #################################
        # Decoding Resterampe
        self._rest_buffer       = bytearray()

        #################################
        # Meta Daten für QSO-Status Msg
        self._next_pack_meta: None | tuple  = None  # RX (opt-id, prp-payload-len) Zum Berechnen des der Größe des Restpaketes
        self._last_pack_meta: None | tuple  = None  # TX (org-payload-len, prp-pack-len) Für Status Meldungen

        #################################
        # Own States / States der eigenen Station
        self._own_states = dict(
            # == Monitor
            cli_rem_mon     =  False,   # TODO Remote Monitor CLI Stream
            gui_rem_mon     =  False,   # Remote Monitor Stream
            rem_mon_port    = 0,        # Port Filter
            rem_mon_incl    = [],       # Incl Filter
            rem_mon_excl    = [],       # Excl Filter
            # == Batch Mode / vorrest nur für Mon Stream
            batch_mode      = 'auto',   # 'auto', 'on', 'off'
            batch_wait      = 30,       # Sekunden Pakete sammeln
            # == Remote CTL/States
            cli_esc         = False,    # CLI-ESC Mode (sendet CLI Stream komprimiert)
            # !! PRIVATE !!!
            login_ok        = False,    # Auth OK
        )
        # == State I/O
        self._get_own_state    = lambda k     : self._own_states[k]
        self._set_own_state    = lambda k, val: self._own_states.update({k: val})
        self._update_own_state = lambda cfg   : self._own_states.update(cfg)

        # == !! PRIVATE STATES !!
        self._private_state    = ['login_ok']
        # == State I/O
        self._is_private_state = lambda state_key: state_key in self._private_state

        #################################
        # Remote States / Bestätigt States der Gegenstation
        self._remote_states       = copy.deepcopy(self._own_states)     # Kopie von _own_states
        # == State I/O
        self._get_remote_state    = lambda k     : self._remote_states[k]
        self._set_remote_state    = lambda k, val: self._remote_states.update({k: val})
        self._update_remote_state = lambda cfg   : self._remote_states.update(cfg)
        # == Für GUI / State I/O
        self._get_remote_states   = lambda       : dict(self._remote_states)

        #################################
        # Remote States ACK
        self._pending_remote_states        = {}    # OPT ID, Remote-State CFG
        # == State I/O
        self._update_pending_remote_states = lambda opt_id, state_cfg: self._pending_remote_states.update({opt_id: state_cfg})
        self._get_pending_remote_state     = lambda opt_id           : self._pending_remote_states.get(opt_id, None)
        self._set_pending_remote_state     = lambda opt_id, state_key, val: self._pending_remote_states.update({opt_id: {state_key: val}})

        #################################
        # Login
        self._login_nonce    = None
        self._password_hash  = None  # sha256(password)
        # == Self / State I/O
        self._is_login_ok    = lambda      : self._own_states.get('login_ok', False)
        self._set_login_ok   = lambda is_ok: self._own_states.update({'login_ok': is_ok})
        # == Remote / State I/O
        self._is_login_resp  = lambda      : self._remote_states.get('login_ok', False)
        self._set_login_resp = lambda is_ok: self._remote_states.update({'login_ok': is_ok})

        #################################
        # Batch Mode
        # == CTL
        self._batch_buffer       = []   # Buffer ax25frame_conf Buffer
        self._batch_timer        = time.time() + self._own_states.get('batch_wait', 30)
        # == Self / State I/O
        self._batch_wait         = lambda : self._own_states.get('batch_wait', 30)
        self._is_batch_mode      = lambda : True if self._own_states.get('batch_mode', 'auto') == 'on'   else False
        self._is_batch_mode_auto = lambda : True if self._own_states.get('batch_mode', 'auto') == 'auto' else False
        self._set_batch_mode     = lambda mode: self._own_states.update({'batch_mode': mode})
        # == Remote / State I/O
        # self._remote_is_batch_mode      = lambda: True if self._remote_states.get('batch_mode', 'auto') == 'on' else False
        # self._remote_is_batch_mode_auto = lambda: True if self._remote_states.get('batch_mode', 'auto') == 'auto' else False
        self._remote_set_batch_mode     = lambda mode: self._remote_states.update({'batch_mode': mode})

        #################################
        # CLI ESC / Komprimiert senden
        # == Self / State I/O
        self._is_cli_esc_mode         = lambda: self._own_states.get('cli_esc', False)
        self._set_cli_esc_mode        = lambda is_on: self._own_states.update({'cli_esc': is_on})
        # == Remote / State I/O
        self._remote_is_cli_esc_mode  = lambda: self._remote_states.get('cli_esc', False)
        self._remote_set_cli_esc_mode = lambda is_on: self._remote_states.update({'cli_esc': is_on})

    #####################################
    # Tasker (ax25Conn)
    def tasker(self):
        """ Called fm ax25Conn """
        self._remote_monitor_batch_update()
        return True

    #####################################
    # PRP ENC/DEC
    def _encode_prp_frame(self, opt_id: int, tx: bool, data: bytes, compress=True, send_uncompressed=True):
        send_compressed = False
        data_len        = len(data)
        comp_data_len   = len(data)
        if data:
            if compress:
                # LZHUF it
                lzhuf = LZHUF_Comp()
                compressed_data = lzhuf.encode(data)
                len_compressed = len(compressed_data)
                if len_compressed < data_len:
                    comp_data_len   = len_compressed
                    send_compressed = True
                    data = compressed_data
            # Wenn nicht zu komprimieren geht und nicht send_uncompressed, nicht senden!
            # Für CLI-ESC Mode
            if not send_compressed and not send_uncompressed:
                return None
            # Escaping
            data = data.replace(PRP_FESC, PRP_FESC_TFESC)
            data = data.replace(PRP_FEND, PRP_FESC_TFEND)

        # Meta Date für Status Msg
        self._last_pack_meta = data_len, comp_data_len
        # Building Packet
        data_to_send  = bytearray()
        data_to_send += pack_6bit_int_and_bool(value=int(opt_id), flag1=tx, flag2=send_compressed)
        data_to_send += len(data).to_bytes(2, 'little')
        data_to_send += data
        # CRC
        crc           = crc16_ccitt(data_to_send)   # 2 Bytes - little
        # Adding Flag and CRC / Flag + Packet + CRC
        data_to_send  = PRP_FLAG + data_to_send + crc

        return data_to_send

    def _decode_prp_frame(self, data: bytes):
        opt_byte = data[2:3]
        # length = data[3:5] # little
        payload  = data[5:-2]
        checksum = data[-2:]
        ################################################################
        # Checking Checksum
        crc16    = crc16_ccitt(data[2:-2])
        if crc16 != checksum:
            logger.error(f"PRP: Checksum Error - UID: {self._get_uid()}")
            logger.error(f"PRP: Packet CRC: {checksum} - Calc CRC: {crc16}")
            #logger.error(f"PRP: Packet CRC: {checksum.to_bytes(2, 'little')} - Calc CRC: {crc16.to_bytes(2, 'little')}")
            logger.error( "PRP: PRP-Frame:")
            logger.error(f"PRP:   ORG: {data}")
            logger.error(f"PRP:   HEX: {bytearray2hexstr(data)}")
            raise EncodingWarning
        ################################################################
        # Unescaping
        payload = payload.replace(PRP_FESC_TFEND, PRP_FEND)
        payload = payload.replace(PRP_FESC_TFESC, PRP_FESC)
        ################################################################
        # Decoding OPT Byte
        opt_id, tx, is_compressed = unpack_6bit_int_and_bool(opt_byte)
        if is_compressed:
            lzhuf   = LZHUF_Comp()
            payload = lzhuf.decode(payload)
        ################################################################
        # 0 - 19 = Port ID
        if opt_id in range(20):
            try:
                return self._decode_remote_mon_frame(payload, opt_id, tx), b''
            except AX25DecodingERROR:
                logger.warning("-------------------------------------------------------------------")
                logger.warning(f'PRP Remote Monitor: decoding UID: {self._get_uid()}')
                logger.warning(f'PRP Remote Monitor: prp frame org {data}')
                logger.warning(f'PRP Remote Monitor: prp frame hex {bytearray2hexstr(data)}')
                logger.warning(f'PRP Remote Monitor: ax25_frame org {payload}')
                logger.warning(f'PRP Remote Monitor: ax25_frame hex {bytearray2hexstr(payload)}')
                logger.warning("-------------------------------------------------------------------")
                return None, b''

        ################################################################
        # TX = Send CMD(True) / Response CMD(False) /
        # 20 - 63 = CMD'S

        # =============================================
        # tx=False → Zentrale Response/ACK-Behandlung
        # Nur für PRP States !!
        # =============================================
        if not tx and opt_id not in PRP_DONT_ACK:
            ack = True if payload == PRP_ACK else False
            if ack:
                # ACK CFG und update Remote-States
                self._ack_pending_remote_states(opt_id)
            else:
                # Optional: Pending löschen oder retry
                self._del_pending_remote_states(opt_id)
            # Response Handler / GUI Updates usw.
            self._local_response_handler(opt_id, resp_ok=ack)

        # =============================================
        #  tx=True → das sind Commands vom Remote
        # =============================================

        """ Remote Monitor Update 20 """
        if opt_id == PRP_OPT_RM_START:
            if tx:
                self._rx_rem_mon_update(payload)
            else:
                self._rx_resp_rem_mon_update()
            return None, b''

        """ Remote Monitor Stop 21 """
        if opt_id == PRP_OPT_RM_STOP:
            if tx:
                self._rx_cmd_stop_gui_remote_mon()
            else:
                self._rx_resp_cmd_stop_gui_remote_mon()
            return None, b''

        """ Disconnect 22 """
        if opt_id == PRP_OPT_DISCO:
            if tx:
                self._rx_cmd_disco()
            return None, b''

        """ Login Request 23 """
        if opt_id == PRP_OPT_LOGIN_REQ:
            if tx:
                self._rx_cmd_login_request()
            else:
                self._rx_cmd_login_challenge(payload)
            return None, b''

        """ Login Response 24 """
        if opt_id == PRP_OPT_LOGIN_RESP:
            if tx:
                self._rx_cmd_login_response(payload)
            else:
                self._rx_cmd_login_ack(payload)
            return None, b''

        """ Logout 25 """
        if opt_id == PRP_OPT_LOGOUT:
            if tx:
                self._rx_cmd_logout()
            else:
                self._rx_cmd_logout_response()
            return None, b''

        """ State Update 26 """
        if opt_id == PRP_OPT_STATE_UPDATE:
            if tx:
                self._rx_remote_state_update(payload)
            else:
                self._rx_resp_remote_state_update(payload)
            return None, b''

        """ CLI Escape 62 """
        if opt_id == PRP_OPT_ESC_CLI:
            if tx:
                return None, self._prp_rx_esc_cli(payload)
            else:
                pass
            return None, b''

        """ Batch Mode 63 """
        if opt_id == PRP_OPT_PRP_BATCH:
            if tx:
                return None, self._prp_rx_batch(payload)
            else:
                pass
            return None, b''
        """ OPT ID existiert nicht """
        logger.warning(f"PRP: Unknown OPT-ID({opt_id})")
        logger.warning( "PRP:    Perhaps you are using an older version of PopT,")
        logger.warning(f"PRP:    that does not support OPT({opt_id}) ?")
        return None, b''

    #####################################
    # PRP I/O - TX/RX
    def _prp_tx(self, opt_id: int, tx_flag: bool, data: bytes, prio=False, compress=True, send_uncompressed=True):
        data2send = self._encode_prp_frame(
            opt_id=opt_id,
            tx=tx_flag,
            data=data,
            compress=compress,
            send_uncompressed=send_uncompressed
        )
        if not data2send:
            # Lösche Meta Daten für Status Meldungen
            self._last_pack_meta = None
            return False
        # An AX25Conn senden
        self._connection.send_remote_data(data2send, prio=prio)
        return True

    def prp_rx(self, data: bytes):
        # Opt by Grok-AI
        # Kombiniere mit Buffer, falls vorhanden
        if self._rest_buffer:
            data = self._rest_buffer + data
            self._rest_buffer = bytearray()

        rest_data  = bytearray()  # Sammelt den Non-Remote-Monitor-Stream
        data_len   = len(data)
        i = 0

        while i < data_len:
            # Suche nächsten Frame-Start (8D 81)
            if data[i:i + 2] == PRP_FLAG:
                self._next_pack_meta = None
                # Potenzieller Frame-Start gefunden
                if i + 5 > data_len:
                    # Header unvollständig -> puffern
                    self._rest_buffer   = data[i:]
                    break

                length = int.from_bytes(data[i + 3:i + 5], 'little')
                #        Header(5)+ len+ CRC(2)
                frame_end = i + 5 + length + 2

                if frame_end > data_len:
                    # Frame Status
                    opt_id, _, _        = unpack_6bit_int_and_bool(data[i + 2:i + 3])
                    self._next_pack_meta = opt_id, length

                    # Frame unvollständig -> puffern
                    self._rest_buffer   = data[i:]
                    break

                # Komplettes Frame extrahiert!
                rem_mon_pack = data[i:frame_end]
                try:
                    rest_data += self._prp_rx_process(rem_mon_pack)
                    self._next_pack_meta = None
                except EncodingWarning:
                    logger.debug("PRP: Data Chunk:")
                    logger.debug(f"PRP:   DATA  : {data}")
                    logger.debug(f"PRP:   DATA H: {bytearray2hexstr(data)}")
                    logger.debug(f"PRP:   REST  : {rest_data}")
                    logger.debug(f"PRP:   REST H: {bytearray2hexstr(rest_data)}")

                i = frame_end  # Springe zum nächsten Byte nach dem Frame
                continue

            # Kein Frame-Start: Dieses Byte gehört zum Rest-Stream
            rest_data.append(data[i])
            i += 1

        # Wenn Rest nach letztem Frame übrig zu rest_data hinzufügen (aber hier schon in Schleife gehandhabt)
        if rest_data == PRP_FEND:   # == 8D ?
            self._rest_buffer  += rest_data
            return b''

        return bytes(rest_data)

    # ====== Processing PRP-Frame
    def _prp_rx_process(self, rem_mon_frame: bytes):
        try:
            decoded_ax25pack, cli_payload = self._decode_prp_frame(rem_mon_frame)
        except EncodingWarning as ex:
            raise ex
        if decoded_ax25pack:
            # TODO Failsafe Response handler self._set_remote_state('gui_rem_mon', True)
            # GUI Handling - Remote Monitor Frame
            if not hasattr(self._port_handler, 'handle_remote_monitor_rx'):
                logger.error("Attribute Error Port-Handler: handle_remote_monitor_rx ")
                return cli_payload
            self._port_handler.handle_remote_monitor_rx(decoded_ax25pack, self._get_uid())
        return cli_payload

    # ====== PRP Batch Mode I/O
    def _prp_batch_tx(self, prp_frames: list[bytes]):
        """ Fasst mehrere PRP-Frames zu einem komprimierten Frame zusammen """
        if not prp_frames:
            return

        batch_data = bytearray()
        n = 0
        for prp_frame in prp_frames:
            batch_data += prp_frame
            n          += 1
            # Max Rohdaten Größe erreicht ?
            batch_data_len = len(batch_data)
            if (batch_data_len >= PRP_BATCH_MAX_PAY and
                len(prp_frames) - n > PRP_BATCH_MIN_PACK) :
                data2send = self._encode_prp_frame(opt_id=PRP_OPT_PRP_BATCH, tx=True, data=batch_data, compress=True)
                if not data2send:
                    batch_data = bytearray()
                    continue
                logger.debug(f"Sende Batch len      : {len(batch_data)} Bytes")
                logger.debug(f"Sende Batch-Paket len: {len(data2send)} Bytes")
                logger.debug(f"Comp Ratio           : {len(batch_data) / len(data2send)}")
                self._connection.send_remote_data(data2send, prio=False)
                batch_data = bytearray()
        # Und den Rest
        if batch_data:
            data2send = self._encode_prp_frame(opt_id=PRP_OPT_PRP_BATCH, tx=True, data=batch_data, compress=True)
            if not data2send:
                return
            logger.debug(f"Sende Batch Rest len      : {len(batch_data)} Bytes")
            logger.debug(f"Sende Batch-Paket Rest len: {len(data2send)} Bytes")
            logger.debug(f"Comp Ratio Rest           : {len(batch_data) / len(data2send)}")
            self._connection.send_remote_data(data2send, prio=False)

    def _prp_rx_batch(self, payload: bytes):
        """ Empfange PRP-Paket Batch """
        data_len  = len(payload)
        i         = 0
        cli_data  = bytearray() # CLI ESC Data
        while i < data_len:
            if payload[i:i + 2] != PRP_FLAG:
                logger.warning("PRP-Batch: PRP_FLAG not found in Datastream")
                logger.warning(f" Payload HEX: {bytearray2hexstr(payload)}")
                logger.warning(f" Index      : {i}")
                i += 1
                continue
            length    = int.from_bytes(payload[i + 3:i + 5], 'little')
            #        Header(5)+ len+ CRC(2)
            frame_end = i + 5 + length + 2
            # Komplettes Frame extrahiert!
            rem_mon_pack = payload[i:frame_end]
            try:
                cli_data += self._prp_rx_process(rem_mon_pack)
            except EncodingWarning:
                logger.warning("PRP-Batch: Data Chunk:")
                logger.warning(f" Payload HEX: {bytearray2hexstr(payload)}")
                logger.warning(f" Index      : {i}")
            # Springe zum nächsten Byte nach dem Frame
            i = frame_end

        return cli_data

    # ====== CLI Escape I/O
    @staticmethod
    def _prp_rx_esc_cli(payload: bytes):
        """ Empfange CLI Escape """
        return payload

    def prp_tx_esc_cli(self, payload: bytes):
        """ Sende CLI Escape - AX25Conn.send_data() """
        # ESC-CLI Mode ist deaktiviert
        if not self._is_cli_esc_mode():
            return False
        # Wird nur gesendet, wenn es sich lohnt (Komprimierung)
        send_as_prp = self._prp_tx(opt_id=PRP_OPT_ESC_CLI,
                                   tx_flag=            True,
                                   data=               payload,
                                   prio=               True,
                                   compress=           True,
                                   send_uncompressed=  False
                                   )
        # Wenn gesendet nicht gesendet, lösche Metadaten für Status MSG
        if not send_as_prp:
            self._last_pack_meta = None
        # Zurück zur AX25Conn.send_data()
        return send_as_prp

    #####################################
    # Remote State ACK I/O
    def _ack_pending_remote_states(self, opt_id: int):
        if opt_id not in self._pending_remote_states:
            logger.error(
                f"RPR: ACK-BufferError: OPT-ID({opt_id}) nicht gefunden in self._pending_remote_states.")
            logger.error("RPR:   self._pending_remote_states:")
            for k, val in self._pending_remote_states.items():
                logger.error(f"RPR:   {k}: {val}")
            return
        # Hole cfg aus ACK-Buffer
        ack_cfg = self._pending_remote_states[opt_id]
        print(f"ACK Update rm_states ack_cfg: {ack_cfg}")
        print(f"ACK Update rm_states PS 1: {self._remote_states}")
        # Update Remote States
        self._update_remote_state(ack_cfg)
        print(f"ACK Update rm_states PS 2: {self._remote_states}")
        # Lösche aus Pending Buffer
        del self._pending_remote_states[opt_id]

    def _add_pending_remote_states_cfg(self, opt_id: int, rem_state_cfg: dict):
        if opt_id in self._pending_remote_states:
            logger.warning(f"PRP: OPT-ID({opt_id}) ist bereit im AXK-Buffer")
            logger.warning(f"PRP:   CFG im Buffer: {self._pending_remote_states[opt_id]}")
            logger.warning(f"PRP:   Neue CfFG    : {rem_state_cfg}")
        # Erstmal überschreiben
        self._update_pending_remote_states(opt_id, rem_state_cfg)

    def _del_pending_remote_states(self, opt_id: int):
        if opt_id not in self._pending_remote_states:
            return
        del self._pending_remote_states[opt_id]

    #####################################
    # Remote Monitor Stream
    def remote_monitor_update(self, ax25frame_conf: dict):
        """ Called fm port_handler > connection.update_monitor() """
        if (not self._get_own_state('cli_rem_mon') and
            not self._get_own_state('gui_rem_mon')):
            return

        port_id = ax25frame_conf.get('port', -1)
        if port_id != self._get_own_state('rem_mon_port'):
            return

        from_call   = ax25frame_conf.get('from_call_str', '')
        to_call     = ax25frame_conf.get('to_call_str', '')
        frame_uid   = ax25frame_conf.get('uid', '')
        my_uid      = str(self._get_uid())
        my_uid_rev  = reverse_uid(my_uid)
        incl_filter = self._get_own_state('rem_mon_incl')
        excl_filter = self._get_own_state('rem_mon_excl')

        # Own Connection Filter
        if frame_uid == my_uid or frame_uid == my_uid_rev:
            return

        if (
            (to_call   == self._connection.to_call_str_add and
            from_call  == self._connection.my_call_str_add)
            or
            (from_call == self._connection.to_call_str_add and
             to_call   == self._connection.my_call_str_add)
            ): return

        # Exclude Filter
        if (from_call in excl_filter or
            to_call   in excl_filter):
            return

        # Include Filter
        if incl_filter:
            if (
                not from_call in incl_filter and
                not to_call   in incl_filter
            ): return

        # CLI Monitor Stream Output
        if self._get_own_state('cli_rem_mon'):
            # TODO
            self._connection.cli.cli_update_monitor(ax25frame_conf)

        # Batch Mode
        if (self._is_batch_mode() or
           # Wenn schon etwas im batch-tx-buffer ist ansonsten Sequenz fehler
           self._batch_buffer     or
           # Auto Batch Mode
           (self._is_batch_mode_auto() and not self._connection.can_send_next_prp_batch())
        ):
            self._batch_buffer.append(ax25frame_conf)
            return

        # PoPT Remote Monitor GUI
        if self._get_own_state('gui_rem_mon'):
            self._encode_remote_mon_frame(ax25frame_conf)

    def _remote_monitor_batch_update(self):
        """ Batch Mode Task """
        if not self._batch_buffer:
            # Timer resetten, wenn keine Pakete gesammelt wurde
            self._batch_timer = time.time() + self._batch_wait()
            return

        # Buffer Limit
        is_buffer_limit = True if len(self._batch_buffer) > 30 else False

        # Nicht Task Timer und nicht Buffer-Limit
        if self._batch_timer > time.time() and not is_buffer_limit:
            return

        # Sammeln, solange AX25Conn noch was zum Senden hat
        if not self._connection.can_send_next_prp_batch() and not is_buffer_limit:
            return

        # Reset Task Timer
        self._batch_timer = time.time() + self._batch_wait()

        # Send as Batch or Single ?
        batch_len     = len(self._batch_buffer)
        send_as_batch = False if batch_len <= PRP_BATCH_MIN_PACK else True

        batch_data: list[bytes] = []
        while self._batch_buffer:
            ax25frame = self._batch_buffer.pop(0)
            # Batch zu klein. Sende Frames einzeln
            if not send_as_batch:
                # Auto Compressed
                self._encode_remote_mon_frame(ax25frame)
                continue

            # PoPT Remote Monitor
            ax25_rawFrame = ax25frame.get('ax25_raw', b'')
            port_id       = ax25frame.get('port', -1)
            tx            = ax25frame.get('tx', False)
            rx_time       = ax25frame.get('rx_time', datetime)
            dec_rx_time   = pack_time_hms(rx_time)
            ax25_data   = bytearray()
            ax25_data  += dec_rx_time
            ax25_data  += ax25_rawFrame
            batch_data.append(self._encode_prp_frame(opt_id=int(port_id), tx=tx, data=ax25_data, compress=False))

        if batch_data:
            self._prp_batch_tx(batch_data)

    def _encode_remote_mon_frame(self, ax25frame_conf: dict):
        ax25_rawFrame = ax25frame_conf.get('ax25_raw', b'')
        tx            = ax25frame_conf.get('tx', False)
        port_id       = ax25frame_conf.get('port', 0)
        rx_time       = ax25frame_conf.get('rx_time', datetime)
        dec_rx_time   = pack_time_hms(rx_time)
        ax25_data  = bytearray()
        ax25_data += dec_rx_time
        ax25_data += ax25_rawFrame
        self._prp_tx(opt_id=int(port_id), tx_flag=tx, data=ax25_data, prio=False)

    @staticmethod
    def _decode_remote_mon_frame(ax25_data, port_id, tx):
        rx_time = unpack_time_hms_to_datetime(ax25_data[:3])
        payload = ax25_data[3:]
        ax25frame = AX25Frame()
        try:
            ax25frame.decode_ax25frame(payload)
        except AX25DecodingERROR:
            raise AX25DecodingERROR
        ax25frame_conf = ax25frame.get_frame_conf()
        ax25frame_conf['tx']      = tx
        ax25frame_conf['rx_time'] = rx_time
        ax25frame_conf['port']    = port_id
        return ax25frame_conf

    #####################################
    # CTL CMDs
    # =============================
    # Response Handler
    def _local_response_handler(self, opt_id: int, resp_ok=True):
        """ Lokaler Response Handler """
        #################################
        # Opt bezogener RESP
        # == Login
        if opt_id == PRP_OPT_LOGIN_RESP:
            print(self._get_remote_state('login_ok'))
            if resp_ok:
                self._port_handler.handle_prp_response(PRP_RM_RESP_LOGIN, self._get_uid())
                return
            self._port_handler.handle_prp_response(PRP_RM_RESP_LOGOUT, self._get_uid())
            return
        # == Logout
        elif opt_id == PRP_OPT_LOGOUT:
            self._port_handler.handle_prp_response(PRP_RM_RESP_LOGOUT, self._get_uid())
            return
        #################################
        # Globaler RESP für Remote Monitor
        self._port_handler.handle_prp_response('', self._get_uid())

    # =============================
    # States Update via Remote / By Grok AI
    def send_remote_state_update(self, state_updates: dict):
        # send_remote_state_update({'batch_mode': 'off', 'cli_esc': True})
        if not self._check_version():
            return False

        # update abgleichen mit _remote_states was sich geändert hat
        update_to_send = {}
        for k, v in state_updates.items():
            if k not in self._remote_states:
                continue
            if self._get_remote_state(k) != v:
                update_to_send[k] = v
        logger.debug(f"PRP: Sende State Update: {self._get_uid()}")
        for k, v in update_to_send.items():
            logger.debug(f"PRP: {k}:{v}")

        # Pending für ACK
        self._add_pending_remote_states_cfg(PRP_OPT_STATE_UPDATE, update_to_send)

        bin_payload = self._encode_state_updates(update_to_send)
        if not bin_payload:
            return False

        return self._prp_tx(
            opt_id=PRP_OPT_STATE_UPDATE,
            tx_flag=True,
            data=bin_payload,
            prio=True,
            compress=True
        )

    def _rx_remote_state_update(self, payload: bytes):
        i = 0
        updates = {}

        while i + 2 < len(payload):
            key_id = payload[i]
            val_len = payload[i + 1]
            i += 2
            if i + val_len > len(payload):
                break

            key = self._get_state_key_by_id(key_id)
            if not key:
                i += val_len
                continue

            # Sensible Keys blockieren
            if key == 'login_ok':
                logger.warning("PRP: Remote versucht login_ok zu ändern – ignoriert!")
                i += val_len
                continue

            value_data = payload[i:i + val_len]
            # Dekodierung mit Key-Name
            # == bool
            if key in ['cli_rem_mon', 'gui_rem_mon', 'cli_esc', 'login_ok']:
                value = bool(value_data[0])
            # == int 1 Byte / 256
            elif key == 'rem_mon_port':
                value = value_data[0]
            # == int 2 Bytes - little
            elif key == 'batch_wait':
                value = int.from_bytes(value_data, 'little')
            # == dict batch mode
            elif key == 'batch_mode':
                modes = {0: 'auto', 1: 'on', 2: 'off'}
                value = modes.get(value_data[0], 'auto')
            # == list
            elif key in ['rem_mon_incl', 'rem_mon_excl']:
                if len(value_data) < 2 or value_data[-2:] != b'\x00\x00':
                    value = []  # Korrupte Daten
                else:
                    parts = value_data[:-2].split(b'\x00')
                    value = [p.decode('UTF-8', 'ignore') for p in parts if p]
            else:
                i += val_len
                continue

            updates[key] = value
            i += val_len

        if updates:
            self._update_own_state(updates)
            logger.info(f"PRP: Dynamisches State-Update empfangen: {updates}")
            # Send Responde
            self._tx_resp_remote_state_update(success=True)
        else:
            self._tx_resp_remote_state_update(success=False)

    # == Encoding
    def _encode_state_updates(self, state_updates: dict):
        payload      = bytearray()
        ordered_keys = list(self._own_states.keys())  # Fixe Reihenfolge

        for key, value in state_updates.items():
            if key not in ordered_keys:
                continue  # Unbekannter oder nicht erlaubter Key

            # Sensible Keys explizit verbieten (z.B. login_ok darf nicht remote gesetzt werden!)
            if self._is_private_state(key):
                logger.warning(f"PRP: Versuch, sensiblen State '{key}' remote zu ändern – blockiert!")
                continue

            key_id = ordered_keys.index(key)
            value_bytes = self._encode_state_value(key, value)  # Key-Name statt ID übergeben
            if value_bytes is None:
                continue

            payload.append(key_id)                    # 1 Byte ID
            payload.append(len(value_bytes))          # 1 Byte Länge
            payload.extend(value_bytes)

        return bytes(payload)

    @staticmethod
    def _encode_state_value(key: str, value):
        # == bool
        if key in ['cli_rem_mon', 'gui_rem_mon', 'cli_esc', 'login_ok']:
            return bytes([0x01 if value else 0x00])

        # == int 1 Byte / 256
        elif key == 'rem_mon_port':
            return bytes([value & 0xFF])

        # == int 2 Bytes - little
        elif key == 'batch_wait':
            return value.to_bytes(2, 'little')

        # == dict batch mode
        elif key == 'batch_mode':
            modes = {'auto': 0, 'on': 1, 'off': 2}
            return bytes([modes.get(value, 0)])

        # == list
        elif key in ['rem_mon_incl', 'rem_mon_excl']:
            if not value:
                return b'\x00\x00'  # Leere Liste
            data = '\x00'.join(value).encode('UTF-8', 'ignore')
            return data + b'\x00\x00'

        return None  # Unbekannter Key

    # == Response
    def _tx_resp_remote_state_update(self, success: bool):
        """ TX Respond State Update (ACK) """
        data = PRP_ACK if success else PRP_NACK
        self._prp_tx(opt_id=PRP_OPT_STATE_UPDATE, tx_flag=False, data=data, prio=True)

    def _rx_resp_remote_state_update(self, payload: bytes):
        """ RX Respond State Update (ACK) """
        if payload == PRP_ACK:
            logger.info("PRP: Remote State-Update erfolgreich bestätigt.")
            logger.debug(f"PRP: Bestätige State Update: {self._get_uid()}")
            for k, v in self._remote_states.items():
                logger.debug(f"PRP: {k}:{v}")
        else:
            logger.warning(f"PRP: Remote State-Update fehlgeschlagen! - UID: {self._get_uid()}")

    # == Helper
    def _get_state_key_by_id(self, key_id: int):
        """ Gibt ID von self._own_states.keys() zurück."""
        keys = list(self._own_states.keys())
        if 0 <= key_id < len(keys):
            return keys[key_id]
        return None

    # =============================
    # ====== OPT-ID 20 leer
    def send_rem_mon_update(self, cfg: dict):
        """ Wird nicht mehr verwendet  """
        if not self._check_version():
            return
        # CFG in ACK Buffer
        self._add_pending_remote_states_cfg(PRP_OPT_RM_START, cfg)
        data = b''
        # PRP Paket erstellen & senden
        self._prp_tx(opt_id=PRP_OPT_RM_START, tx_flag=True, data=data, prio=True)

    def _rx_rem_mon_update(self, payload: bytes):
        """ Empfange Remote Monito Cfg """
        # Sende ACK
        self._tx_resp_rem_mon_update()

    def _tx_resp_rem_mon_update(self):
        """ TX Respond Remote Monitor CFG update """
        self._prp_tx(opt_id=PRP_OPT_RM_START, tx_flag=False, data=PRP_ACK, prio=True)

    def _rx_resp_rem_mon_update(self):
        """ RX Respond Remote Monitor CFG update """
        pass

    # =============================
    # ====== Remote Mon Stop CMD
    def cmd_stop_gui_remote_mon(self):
        """ TX Start CMD """
        if not self._check_version():
            return
        # CFG in ACK Buffer
        self._set_pending_remote_state(PRP_OPT_RM_STOP, 'gui_rem_mon', False)
        # PRP Senden
        self._prp_tx(opt_id=PRP_OPT_RM_STOP, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_stop_gui_remote_mon(self):
        """ RX Stop CMD """
        # Zustand updaten
        self._set_own_state('gui_rem_mon', False)
        # Clear remote-protocol buffer
        self._connection.clear_tx_buff_prp()
        # Send Response
        self._tx_resp_cmd_stop_gui_remote_mon()

    def _tx_resp_cmd_stop_gui_remote_mon(self):
        """ TX Respond Stop CMD """
        self._prp_tx(opt_id=PRP_OPT_RM_STOP, tx_flag=False, data=PRP_ACK, prio=True)

    def _rx_resp_cmd_stop_gui_remote_mon(self):
        """ RX Respond Stop CMD """
        pass

    # =============================
    # ====== Disconnect CMD
    def cmd_disco(self):
        """ TX Start Disco CMD """
        if not self._check_version():
            return
        self._prp_tx(opt_id=PRP_OPT_DISCO, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_disco(self):
        """ RX Start Disco CMD """
        self._connection.conn_disco()

    # =============================
    # ====== Login Stuff
    def cmd_login_request(self, password: str):
        """Client fordert Login-Challenge an"""
        if not self._check_version():
            return
        # TODO Password fm DB or GUI
        self._password_hash = hashlib.sha256(DBUG_PW.encode()).digest()
        self._add_pending_remote_states_cfg(PRP_OPT_LOGIN_RESP, {'login_ok': True})
        self._prp_tx(PRP_OPT_LOGIN_REQ, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_login_request(self):
        """Client fordert Login-Challenge an"""
        nonce = os.urandom(16)
        self._login_nonce = nonce
        self._prp_tx(PRP_OPT_LOGIN_REQ, tx_flag=False, data=nonce, prio=True)

    def _rx_cmd_login_challenge(self, payload):
        """Client erhält Nonce vom Server"""
        self._login_nonce = payload
        print("LOGIN Challenge erhalten.")
        self._cmd_login_send_response()

    def _cmd_login_send_response(self):
        if not self._login_nonce:
            print("Keine Challenge empfangen!")
            return

        h = hashlib.sha256(self._password_hash + self._login_nonce).digest()
        self._prp_tx(PRP_OPT_LOGIN_RESP, tx_flag=True, data=h, prio=True)

    def _rx_cmd_login_response(self, payload):
        """Server prüft kryptografische Antwort"""
        # TODO password_hash fm userdb
        password      = DBUG_PW
        password_hash = hashlib.sha256(password.encode()).digest()

        if not self._login_nonce or not password_hash:
            self._send_login_ack(False)
            print('Login error !')
            return

        expected = hashlib.sha256(password_hash + self._login_nonce).digest()

        if expected == payload:
            print('Login accepted !')
            self._set_login_ok(True)
            self._send_login_ack(True)
        else:
            print('Login failed !')
            self._set_login_ok(False)
            self._send_login_ack(False)

        self._login_nonce   = None
        self._password_hash = None

    def _send_login_ack(self, ok: bool):
        data = PRP_ACK if ok else PRP_NACK
        self._prp_tx(PRP_OPT_LOGIN_RESP, tx_flag=False, data=data, prio=True)

    def _rx_cmd_login_ack(self, payload: bytes):
        if payload == PRP_ACK:
            logger.info("LOGIN erfolgreich!")
        else:
            self._set_login_resp(False)  # oder direkt False setzen
            logger.warning("LOGIN fehlgeschlagen!")

    # =============================
    # ====== Logout Stuff
    def cmd_logout(self):
        """ Client sendet Logout """
        if not self._check_version():
            return
        self._add_pending_remote_states_cfg(PRP_OPT_LOGOUT, {'login_ok': False})
        self._prp_tx(PRP_OPT_LOGOUT, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_logout(self):
        """ Server bestätigt Logout """
        print('Received Logout CMD')
        self._set_login_ok(False)
        self._prp_tx(PRP_OPT_LOGOUT, tx_flag=False, data=b'', prio=True)

    def _rx_cmd_logout_response(self):
        """ Client empfängt Logout bestätigung """
        print("LOGOUT erfolgreich!")
        self._set_login_ok(False)

    #####################################
    # Helper
    def _check_version(self):
        stat_id = self._connection.cli.stat_identifier
        if PRP_SW_RESTR not in stat_id.software:
            logger.warning(f"PRP: This function is just available with {PRP_SW_RESTR}. {stat_id.software}")
            return False
        if version_tuple(stat_id.version) < version_tuple(PRP_VER_RESTR):
            logger.warning(f"PRP: This function is just available with {PRP_SW_RESTR} Version:")
            logger.warning(f"PRP: Version >= {PRP_VER_RESTR}")
            return False
        return True

    #####################################
    # Lokale State I/O
    # === self._own_states I/O
    def get_own_states(self):
        return dict(self._own_states)

    def set_own_state(self, state_key: str, value):
        # Opt: by Grok-AI
        if state_key not in self._own_states:
            logger.error(f"PRP State-Tab KeyError: Unbekannter Key '{state_key}'")
            return False

        current_value = self._get_own_state(state_key)
        current_type  = type(current_value)

        # Spezielle Typprüfung für Listen
        if current_type is list:
            if not isinstance(value, (list, tuple)):
                logger.error(
                    f"PRP State-Tab ValueError: Key '{state_key}' erwartet list oder tuple, bekam {type(value)}")
                return False
        # Spezielle Prüfung für batch_mode
        elif state_key == 'batch_mode':
            if value not in ('auto', 'on', 'off'):
                logger.error(f"PRP State-Tab ValueError: batch_mode muss 'auto', 'on' oder 'off' sein, nicht '{value}'")
                return False
        # Normale Typprüfung
        elif not isinstance(value, current_type):
            logger.error(f"PRP State-Tab ValueError: Key '{state_key}' erwartet {current_type}, bekam {type(value)}")
            logger.error(f"  Wert: {value}")
            return False

        # Private States loggen (aber erlauben, da lokal)
        if self._is_private_state(state_key):
            logger.warning(f"Lokaler Zugriff auf privaten State '{state_key}' = {value}")

        self._set_own_state(state_key, value)
        logger.debug(f"PRP State updated: {state_key} = {value}")
        return True

    def update_own_states(self, state_cfg: dict):
        """
        by Grok-AI
        Updated mehrere _own_states auf einmal aus einem Dict.
        Validiert jeden Eintrag (Key, Typ, Wert) vor dem Setzen.
        Bei einem einzigen Fehler wird KEINE Änderung vorgenommen.

        Beispiel:
            self.update_own_states({
                'gui_rem_mon': True,
                'rem_mon_port': 5,
                'batch_mode': 'off',
                'rem_mon_incl': ['DB0LJ', 'DL1ABC']
            })

        Rückgabe: True = alles erfolgreich gesetzt, False = mind. ein Fehler
        """
        if not isinstance(state_cfg, dict):
            logger.error("PRP update_own_states: Eingabe muss ein Dictionary sein!")
            return False

        if not state_cfg:
            logger.debug("PRP update_own_states: Leeres Update-Dict – nichts zu tun.")
            return True

        # Schritt 1: Alle Updates vorab validieren (ohne zu schreiben)
        validated_updates = {}
        for key, value in state_cfg.items():
            if key not in self._own_states:
                logger.error(f"PRP update_own_states: Unbekannter State-Key '{key}'")
                return False

            current_value = self._get_own_state(key)
            current_type = type(current_value)

            # --- Typprüfung ---
            if current_type is list:
                if not isinstance(value, (list, tuple)):
                    logger.error(f"PRP update_own_states: Key '{key}' erwartet list/tuple, bekam {type(value)}")
                    return False
            elif key == 'batch_mode':
                if value not in ('auto', 'on', 'off'):
                    logger.error(
                        f"PRP update_own_states: batch_mode ungültiger Wert '{value}' (erlaubt: auto, on, off)")
                    return False
            elif not isinstance(value, current_type):
                logger.error(f"PRP update_own_states: Key '{key}' erwartet {current_type}, bekam {type(value)}")
                return False

            # --- Wertplausibilität (optional erweitern) ---
            if key == 'rem_mon_port':
                if not (0 <= value <= 19):  # Ports typischerweise 0–19
                    logger.error(f"PRP update_own_states: rem_mon_port außerhalb gültigem Bereich (0-19): {value}")
                    return False
            elif key == 'batch_wait':
                if not (1 <= value <= 3600):  # 1 Sekunde bis 1 Stunde sinnvoll
                    logger.warning(f"PRP update_own_states: batch_wait ungewöhnlicher Wert: {value}s")

            # --- Private States nur loggen (nicht blockieren, da lokal) ---
            if self._is_private_state(key):
                logger.warning(f"Lokaler Update privater State '{key}' = {value}")

            validated_updates[key] = value

        # Schritt 2: Alle validierten Updates auf einmal anwenden
        for key, value in validated_updates.items():
            self._set_own_state(key, value)
            logger.debug(f"PRP State updated: {key} = {value}")

        logger.info(f"PRP update_own_states: Erfolgreich {len(validated_updates)} States aktualisiert.")
        return True

    # === self._remote_states I/O
    def get_rem_states(self):
        return self._get_remote_states()

    def get_rem_state_by_key(self, state_key: str):
        if not state_key in self._remote_states:
            return None
        return self._get_remote_state(state_key)

    # === CLI-ESC Status Meldungen für gui.QSO
    def get_cli_esc_send_status(self):
        """
        Gibt den Status eines gesendeten CLI-ESC-Frames zurück, falls vorhanden.
        """
        if self._last_pack_meta is None:
            return None

        len_payload, len_compressed = self._last_pack_meta
        compression_ratio = round((len_payload / len_compressed) * 100)

        return f"PRP ▲ Compressed({compression_ratio}%) - {len_compressed} Bytes / {len_payload} Bytes"

    def get_incomplete_cli_esc_status(self):
        """
        Gibt den Status eines unvollständigen CLI-ESC-Frames zurück, falls vorhanden.
        """
        if self._next_pack_meta is None or len(self._rest_buffer) < 5:
            return None  # Kein unvollständiges Frame oder Header unvollständig

        # Nur für CLI-ESC (OPT 62, TX-Flag)
        if self._next_pack_meta[0] != PRP_OPT_ESC_CLI:
            return None

        # Berechne Fortschritt
        total_bytes    = 7 + self._next_pack_meta[1]  # Flag(2) + OPT(1) + LEN(2) + Payload + CRC(2)
        received_bytes = len(self._rest_buffer)
        if received_bytes >= total_bytes:
            return None  # Vollständig (sollte nicht passieren, aber sicher)

        # Baue String zusammen
        percent = int((received_bytes / total_bytes) * 100)
        pr_ten  = round(percent / 10)
        pr_rest = 10 - pr_ten
        # Download Bar
        bar     = f"[{'#' * pr_ten}{'.' * pr_rest}]"
        return f"PRP ▼ {bar}({percent}%) - {max(0, received_bytes - 7)} Bytes / {self._next_pack_meta[1]} Bytes"
