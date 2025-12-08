"""
══════════════════════════════════════════════════════════════════════════
          PoPT-REMOTE PROTOKOLL (PRP) – Spezifikation
══════════════════════════════════════════════════════════════════════════
Version 1.1  –  Dezember 2025
══════════════════════════════════════════════════════════════════════════
                 Remote Protocol v1.1
══════════════════════════════════════════════════════════════════════════
1. Allgemeine Paketstruktur (gilt für ALLE Pakete)
══════════════════════════════════════════════════════════════════════════

+--------+--------+--------+--------+-------------+----- ~ ----------+--------+--------+
|  FLAG  |  FLAG  | OPTBYTE|  LEN (2 Byte little) |    PAYLOAD       | CRC16  | CRC16  |
|  0x8D  |  0x81  |        |  LSB         MSB     |  variable Länge  | low    | high   |
+--------+--------+--------+--------+-------------+----- ~ ----------+--------+--------+
   0         1        2        3         4             5 ...  5+L-1      L+5    L+6

  • FLAG-Sequenz      = immer 0x8D 0x81              - 2 Bytes
  • OPTBYTE           = siehe Abschnitt 2            - 1 Byte
  • LEN               = Länge des PAYLOADs(Escaped)  - 2 Bytes
  • PAYLOAD           = escaped, ggf. vorher LZHUF-komprimiert
  • CRC               = CRC16                        - 2 Bytes

CRC16-CCITT: Polynomial 0x1021, Init 0xFFFF, Final-XOR 0x0000 (KISS-Standard)

══════════════════════════════════════════════════════════════════════════
2. OPTBYTE – Aufbau (1 Byte)
══════════════════════════════════════════════════════════════════════════

Bit    7   6   5   4   3   2   1   0
     +---+---+---+---+---+---+---+---+
     |F2 |F1 |      OPT-ID (0-63)    |
     +---+---+---+---+---+---+---+---+

  F2 = 1 → Payload ist LZHUF-komprimiert
  F1 = 1 → Frame war TX (gesendet), 0 → RX (empfangen)
  OPT-ID 0…19  → Port-ID für normale Monitor-Frames
  OPT-ID 20…63 → Steuerbefehle

══════════════════════════════════════════════════════════════════════════
3. Escaping
══════════════════════════════════════════════════════════════════════════

0x8D (FEND)  → ersetze durch 0x8F 0x92
0x8F (FESC)  → ersetze durch 0x8F 0x9B

Empfangsseite:
  0x8F 0x9B  → ersetze durch 0x8F
  0x8F 0x92  → ersetze durch 0x8D

═════════════════════════════════════════════════════════════════════════════
4. Monitor-Frame (OPT-ID = 0 … 19)
══════════════════════════════════════════════════════════════════════════

Payload VOR Kompression und Escaping:

+--------------------------------+-------------------------------+
|       3 Byte BCD Zeit          |   rohes AX.25-Frame (wie vom  |
|          HH:MM:SS              |   Radio empfangen/gesendet)   |
+--------------------------------+-------------------------------+

Beispiel (16:47:08):
16 47 08 A0 84 ... (komplettes AX.25-Paket)

→ optional LZHUF-komprimiert (nur wenn kürzer)
→ dann escaped
→ dann in das Grundpaket (Abschnitt 1) verpackt

══════════════════════════════════════════════════════════════════════════
5. Steuerbefehle (OPT-ID ≥ 20)
══════════════════════════════════════════════════════════════════════════

OPT-ID | Richtung TX (CMD)  | Richtung RX (ACK)   | Payload
-------+--------------------+---------------------+------------------------
 20    | Remote-Mon START   | ACK START           | "port:incl:excl" (UTF-8) (siehe 5.1) / leer
 21    | Remote-Mon STOP    | ACK STOP            | leer
 22    | Disconnect         | (kein ACK)          | leer
 23    | Login Request      | Login Challenge     | leer / 16-Byte Nonce
 24    | Login Response     | Login ACK           | SHA256(pw_hash + nonce) / b"OK" oder b"FAIL"
 25    | Logout             | ACK Logout          | leer
 63    | PRP-Batch Frames   | (kein ACK)          | RPR-Frames als Batch

5.1 START-Befehl (OPT-ID 20, F1 = 1) – Payload (UTF-8)

"<PortID>:<Include-Calls>:<Exclude-Calls>"

Beispiele:
  "2:DB0LJ,DL1ABC:DJ5ABC"     → Port 2, nur diese Calls, Rest ausblenden
  "0::"                       → Port 0, alles anzeigen (keine Filter)
  "5:DB0ABC:"                 → Port 5, nur DB0ABC erlaubt, Rest ausblenden

══════════════════════════════════════════════════════════════════════════
6. Kompressions-Logik
══════════════════════════════════════════════════════════════════════════

- LZHUF wird angewendet
- Wenn komprimiertes Ergebnis kürzer → F2 = 1 und komprimiertes Payload senden
- Sonst                              → F2 = 0 und Original-Payload senden
- Empfänger dekomrimiert nur, wenn     F2 = 1

══════════════════════════════════════════════════════════════════════════
7. Komplettes Beispiel (Monitor-Frame, Port 13, TX, nicht komprimiert)
══════════════════════════════════════════════════════════════════════════

Payload nach Escaping: 26 Byte
Gesendet wird (Hex):

8D 81 6D 1A 00 16 47 08 A0 84 ... (26 Byte escaped Payload) ... A7 3F

Aufschlüsselung:
8D 81     → Flag
6D        → OPTBYTE = 0b01101101 → Port 13, TX=1, F2=0
1A 00     → LEN = 26 (little-endian, = 0x001A)
16 47 08  → BCD-Zeit 16:47:08
...       → escaped AX.25-Frame
A7 3F     → CRC16 über Bytes 2 bis 30 (OPTBYTE bis letztes Payload-Byte)

══════════════════════════════════════════════════════════════════════════
8. Zusammenfassungstabelle
══════════════════════════════════════════════════════════════════════════

ID-Bereich | Bedeutung                  | Payload vor Escaping/Kompression
-----------+----------------------------+---------------------------------
 0 – 19    | Monitor-Frame Port X       | 3 Byte BCD-Zeit + rohes AX.25-Frame
 --        | -------------------------- | --------------------------------
 20        | Remote-Mon START           | "port:incl:excl" (nur bei CMD)
 20        | ACK START                  | leer
 21        | Remote-Mon STOP            | leer
 21        | ACK STOP                   | leer
 22        | Disconnect                 | leer
 --        | -------------------------- | --------------------------------
 23        | Login Request              | leer
 23        | ACK Login Request          | 6-Byte Nonce
 24        | Login Response             | SHA256(pw_hash+nonce)
 24        | ACK Login Response         | b'OK or b'FAIL'
 25        | Logout                     | leer
 25        | ACK Logout                 | leer
 ...
 ...
 63        | PRP-BATCH                  | PRP-Frame Batch

══════════════════════════════════════════════════════════════════════════
Ende der Spezifikation
══════════════════════════════════════════════════════════════════════════
Idee
Batch Prezess OPT 63
mehrere RPP-Frames werden in ein Batch zusammen gefasst und koprimiert

"""
import datetime
import hashlib
import os
import time

from ax25.ax25Error import AX25DecodingERROR
from cfg.default_config import getNew_remote_mon_cfg
from cfg.logger_config import logger
from fnc.ax25_fnc import reverse_uid
from fnc.crc_fnc import crc16_ccitt
from fnc.lzhuf import LZHUF_Comp
from ax25.ax25dec_enc import AX25Frame, bytearray2hexstr
from fnc.str_fnc import version_tuple

####################################################################################
PRP_SW_RESTR             = 'PoPTNode'  # Software restriction
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
PRP_OPT_RM_START        = 20 # Remote Monitor Start/Update
PRP_OPT_RM_STOP         = 21 # Remote Monitor Stop
PRP_OPT_DISCO           = 22 # Connection (soft)Disco
PRP_OPT_LOGIN_REQ       = 23 # Login Request
PRP_OPT_LOGIN_RESP      = 24 # Login Response
PRP_OPT_LOGOUT          = 25 # Logout
PRP_OPT_PRP_BATCH       = 63 # PRP-Frame Batch processing
####################################################################################
# Response (GUI Handling)
PRP_RM_RESP_START   = 'rsp_start'   # Remote Monitor Start/Update
PRP_RM_RESP_STOP    = 'rsp_stop'    # Remote Monitor Stop
PRP_RM_RESP_LOGIN   = 'rsp_login'   # Remote Login OK
PRP_RM_RESP_LOGOUT  = 'rsp_logout'  # Remote Login FAILED | Logout
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

    byte = data[0]
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

class PRPremote:
    def __init__(self, port_handler , connection):
        self._port_handler      = port_handler
        self._connection        = connection

        ################################
        # Remote Monitor
        self._remote_mon_conf       = getNew_remote_mon_cfg()
        self._remote_monitor_buffer = bytearray()

        ################################
        # States
        self._remote_states = dict(
            gui_rem_mon=False,
            login_ok=False,
            batch_mode=True,
        )

        ################################
        # Login
        self._login_nonce   = None
        self._password_hash = None  # sha256(password)
        self._is_login_ok   = lambda : self._remote_states.get('login_ok', False)
        self._set_login_ok  = lambda is_ok: self._remote_states.update({'login_ok': is_ok})

        ################################
        # Batch Mode
        self._max_batch_paylod = 1512 # Bytes
        self._min_batch_packet = 4    # PRP-Frames
        self._batch_buffer     = []
        self._batch_timer_par  = 15
        self._batch_timer      = time.time() + self._batch_timer_par
        self._is_batch_mode    = lambda : self._remote_states.get('batch_mode', False)
        self._set_batch_mode   = lambda is_on: self._remote_states.update({'batch_mode': is_on})

    #######################################
    # Tasker
    def tasker(self):
        """ Called fm ax25Conn """
        self._remote_monitor_batch_update()

        return True
    #######################################
    # PRP ENC/DEC
    @staticmethod
    def _encode_prp_frame(opt_id: int, tx: bool, data: bytes, compress=True):
        send_compressed = False
        if data:
            if compress:
                # LZHUF it
                lzhuf = LZHUF_Comp()
                compressed_data = lzhuf.encode(data)
                if len(compressed_data) < len(data):
                    send_compressed = True
                    data = compressed_data
            # Escaping
            data = data.replace(PRP_FESC, PRP_FESC_TFESC)
            data = data.replace(PRP_FEND, PRP_FESC_TFEND)

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
            logger.error(f"PRP: Checksum Error - UID: {self._connection.uid}")
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
                return self._decode_remote_mon_frame(payload, opt_id, tx)
            except AX25DecodingERROR:
                logger.warning("-------------------------------------------------------------------")
                logger.warning(f'Remote Monitor: decoding UID: {self._connection.uid}')
                logger.warning(f'Remote Monitor: prp frame org {data}')
                logger.warning(f'Remote Monitor: prp frame hex {bytearray2hexstr(data)}')
                logger.warning(f'Remote Monitor: ax25_frame org {payload}')
                logger.warning(f'Remote Monitor: ax25_frame hex {bytearray2hexstr(payload)}')
                logger.warning("-------------------------------------------------------------------")
                return None
        ################################################################
        # 20 - 63 = CMD'S
        # TX = Send CMD(True) / Response CMD(False) /
        """ Remote Monitor Start 20 """
        if opt_id == PRP_OPT_RM_START:
            if tx:
                self._rx_cmd_gui_remote_mon(payload)
            else:
                self._rx_resp_cmd_start_gui_remote_mon()
            return None

        """ Remote Monitor Stop 21 """
        if opt_id == PRP_OPT_RM_STOP:
            if tx:
                self._rx_cmd_stop_gui_remote_mon()
            else:
                self._rx_resp_cmd_stop_gui_remote_mon()
            return None

        """ Disconnect 22 """
        if opt_id == PRP_OPT_DISCO:
            if tx:
                self._rx_cmd_disco()
            return None

        """ Login Request 23 """
        if opt_id == PRP_OPT_LOGIN_REQ:
            if tx:
                self._rx_cmd_login_request()
            else:
                self._rx_cmd_login_challenge(payload)
            return None

        """ Login Response 24 """
        if opt_id == PRP_OPT_LOGIN_RESP:
            if tx:
                self._rx_cmd_login_response(payload)
            else:
                self._rx_cmd_login_ack(payload)
            return None

        """ Logout 25 """
        if opt_id == PRP_OPT_LOGOUT:
            if tx:
                self._rx_cmd_logout()
            else:
                self._rx_cmd_logout_response()
            return None

        """ Batch Mode 63 """
        if opt_id == PRP_OPT_PRP_BATCH:
            if tx:
                self._rx_prp_batch(payload)
            else:
                pass
            return None
        return None
    #############################################
    # I/O - TX/RX
    def _prp_tx(self, opt_id: int, tx_flag: bool, data: bytes, prio=False):
        data2send = self._encode_prp_frame(opt_id=opt_id, tx=tx_flag, data=data, compress=True)
        if not data2send:
            return
        self._connection.send_remote_data(data2send, prio=prio)

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
            if (batch_data_len >= self._max_batch_paylod and
                len(prp_frames) - n > self._min_batch_packet) :
                data2send = self._encode_prp_frame(opt_id=PRP_OPT_PRP_BATCH, tx=True, data=batch_data, compress=True)
                if not data2send:
                    batch_data = bytearray()
                    continue
                print(f"Sende Batch len      : {len(batch_data)} Bytes")
                print(f"Sende Batch-Paket len: {len(data2send)} Bytes")
                print(f"Comp Ratio           : {len(batch_data) / len(data2send)}")
                self._connection.send_remote_data(data2send, prio=False)
                batch_data = bytearray()
        # Und den Rest
        if batch_data:
            data2send = self._encode_prp_frame(opt_id=PRP_OPT_PRP_BATCH, tx=True, data=batch_data, compress=True)
            if not data2send:
                return
            print(f"Sende Batch Rest len      : {len(batch_data)} Bytes")
            print(f"Sende Batch-Paket Rest len: {len(data2send)} Bytes")
            print(f"Comp Ratio Rest           : {len(batch_data) / len(data2send)}")
            self._connection.send_remote_data(data2send, prio=False)

    def prp_rx(self, data: bytes):
        # Opt by Grok-AI
        # Kombiniere mit Buffer, falls vorhanden
        if self._remote_monitor_buffer:
            data = self._remote_monitor_buffer + data
            self._remote_monitor_buffer = bytearray()
        rest_data  = bytearray()  # Sammelt den Non-Remote-Monitor-Stream
        i = 0
        data_len = len(data)

        while i < data_len:
            # Suche nächsten Frame-Start (8D 81)
            if data[i:i + 2] == PRP_FLAG:
                # Potenzieller Frame-Start gefunden
                if i + 5 > data_len:
                    # Header unvollständig -> puffern
                    self._remote_monitor_buffer = data[i:]
                    break

                length = int.from_bytes(data[i + 3:i + 5], 'little')
                #        Header(5)+ len+ CRC(2)
                frame_end = i + 5 + length + 2

                if frame_end > data_len:
                    # Frame unvollständig -> puffern
                    self._remote_monitor_buffer = data[i:]
                    break

                # Komplettes Frame extrahiert!
                rem_mon_pack = data[i:frame_end]
                try:
                    self._prp_rx_process(rem_mon_pack)
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
            self._remote_monitor_buffer += rest_data
            return b''

        return bytes(rest_data)

    def _prp_rx_process(self, rem_mon_frame: bytes):
        try:
            decoded_ax25pack = self._decode_prp_frame(rem_mon_frame)
        except EncodingWarning as ex:
            raise ex
        if not decoded_ax25pack:
            return
        self._remote_states['gui_rem_mon'] = True
        # GUI Handling - Remote Monitor Frame
        if not hasattr(self._port_handler, 'handle_remote_monitor_rx'):
            logger.error("Attribute Error Port-Handler: handle_remote_monitor_rx ")
            return
        self._port_handler.handle_remote_monitor_rx(decoded_ax25pack, self._connection.uid)

    #######################################
    # Remote Monitor
    def remote_monitor_update(self, ax25frame_conf: dict):
        """ Called fm port_handler > connection.update_monitor() """
        if (not self._remote_mon_conf.get('cli_mon', False) and
            not self._remote_mon_conf.get('gui_mon', False)):
            return

        port_id = ax25frame_conf.get('port', -1)
        if port_id != self._remote_mon_conf.get('mon_port', -2):
            return

        from_call   = ax25frame_conf.get('from_call_str', '')
        to_call     = ax25frame_conf.get('to_call_str', '')
        frame_uid   = ax25frame_conf.get('uid', '')
        my_uid      = str(self._connection.uid)
        my_uid_rev  = reverse_uid(my_uid)
        incl_filter = self._remote_mon_conf.get('incl_call', [])
        excl_filter = self._remote_mon_conf.get('excl_call', [])

        # Own Connection Filter
        if frame_uid == my_uid or frame_uid == my_uid_rev:
            return

        if ((
                to_call == self._connection.to_call_str_add and
                from_call == self._connection.my_call_str_add
            ) or
            (
                    from_call == self._connection.to_call_str_add and
                    to_call == self._connection.my_call_str_add
            )): return

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

        # Batch Mode
        if self._is_batch_mode():
            self._batch_buffer.append(ax25frame_conf)

        # PoPT Remote Monitor
        elif self._remote_mon_conf.get('gui_mon', False):
            self._encode_remote_mon_frame(ax25frame_conf)

        # CLI Monitor Output
        if self._remote_mon_conf.get('cli_mon', False):
            # TODO
            self._connection.cli.cli_update_monitor(ax25frame_conf)


    def _remote_monitor_batch_update(self):
        """ Batch Mode Task """
        if not self._is_batch_mode():
            return

        # Buffer Limit
        is_buffer_limit = True if len(self._batch_buffer) > 30 else False

        # Task Timer
        if self._batch_timer > time.time() and not is_buffer_limit:
            return

        # Sammeln, solange AX25Conn noch was zum Senden hat
        if self._connection.get_remote_prio_q() and not is_buffer_limit:
            return

        # Reset Task Timer
        self._batch_timer = time.time() + self._batch_timer_par

        # Send as Batch or Single ?
        batch_len     = len(self._batch_buffer)
        send_as_batch = False if batch_len <= self._min_batch_packet else True

        batch_data: list[bytes] = []
        while self._batch_buffer:
            ax25frame = self._batch_buffer.pop(0)
            # Batch zu klein. Sende Frames einzeln
            if not send_as_batch:
                self._encode_remote_mon_frame(ax25frame)
                print("Single Packet send")
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

    ##############################################
    # CTL CMDs
    # =============================
    # ====== Remote Mon Start CMD
    def cmd_start_gui_remote_mon(self, cfg: dict):
        """ TX Start CMD """
        if not self._check_version():
            return

        port_id = cfg.get('mon_port', 0)
        incl_filter = ','.join(cfg.get('incl_call', []))
        excl_filter = ','.join(cfg.get('excl_call', []))

        data = f"{port_id}:{incl_filter}:{excl_filter}".encode('UTF-8', 'ignore')

        self._prp_tx(opt_id=PRP_OPT_RM_START, tx_flag=True, data=data, prio=True)

    def _rx_cmd_gui_remote_mon(self, payload: bytes):
        """ RX Start CMD """
        data  = payload.decode('UTF-8', 'ignore')
        param = data.split(':')
        if len(param) != 3:
            logger.error("Parameter Error (_start_gui_remote_mon): ")
            logger.error(f"Parameter: {param}")
            return
        try:
            port_id = int(param[0])
        except ValueError:
            logger.error("Value Error port_id (_start_gui_remote_mon): ")
            logger.error(f"Parameter: {param}")
            return
        incl_filter = param[1].split(',')
        excl_filter = param[2].split(',')
        while '' in incl_filter:
            incl_filter.remove('')
        while '' in excl_filter:
            excl_filter.remove('')

        cfg = dict(
            cli_mon=False,
            gui_mon=True,
            mon_port=port_id,
            incl_call=incl_filter,  # Call Filter
            excl_call=excl_filter,  # Call Filter
        )
        print(f"set_remote_mon: {cfg}")
        self._tx_resp_cmd_start_gui_remote_mon()
        self._remote_mon_conf.update(cfg)

    def _tx_resp_cmd_start_gui_remote_mon(self):
        """ TX Respond Stop CMD """
        self._prp_tx(opt_id=PRP_OPT_RM_START, tx_flag=False, data=b'', prio=True)

    def _rx_resp_cmd_start_gui_remote_mon(self):
        """ RX Respond Stop CMD """
        self._remote_states['gui_rem_mon'] = True
        self._port_handler.handle_remote_monitor_response(PRP_RM_RESP_START, self._connection.uid)

    # =============================
    # ====== Remote Mon Stop CMD
    def cmd_stop_gui_remote_mon(self):
        """ TX Start CMD """
        if not self._check_version():
            return
        self._prp_tx(opt_id=PRP_OPT_RM_STOP, tx_flag=True, data=b'', prio=True)

    def _rx_cmd_stop_gui_remote_mon(self):
        """ RX Stop CMD """
        cfg = dict(
            gui_mon=False,
        )
        print(f"set_remote_mon: {cfg}")
        self._remote_mon_conf.update(cfg)
        # Clear remote-protocol buffer
        self._connection.clear_tx_buff_prio()
        # Send Response
        self._tx_resp_cmd_stop_gui_remote_mon()

    def _tx_resp_cmd_stop_gui_remote_mon(self):
        """ TX Respond Stop CMD """
        self._prp_tx(opt_id=PRP_OPT_RM_STOP, tx_flag=False, data=b'', prio=True)

    def _rx_resp_cmd_stop_gui_remote_mon(self):
        """ RX Respond Stop CMD """
        self._remote_states['gui_rem_mon'] = False
        self._port_handler.handle_remote_monitor_response(PRP_RM_RESP_STOP, self._connection.uid)

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
        password = DBUG_PW
        password_hash = hashlib.sha256(password.encode()).digest()

        if not self._login_nonce or not password_hash:
            self._send_login_ack(False)
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
        data = b"OK" if ok else b"FAIL"
        self._prp_tx(PRP_OPT_LOGIN_RESP, tx_flag=False, data=data, prio=True)

    def _rx_cmd_login_ack(self, payload):
        answer = payload.decode("ascii", "ignore")
        if answer == "OK":
            self._set_login_ok(True)
            self._port_handler.handle_remote_monitor_response(PRP_RM_RESP_LOGIN, self._connection.uid)
            print("LOGIN erfolgreich!")
        else:
            self._set_login_ok(False)
            self._port_handler.handle_remote_monitor_response(PRP_RM_RESP_LOGOUT, self._connection.uid)
            print("LOGIN fehlgeschlagen!")

    # =============================
    # ====== Logout Stuff
    def cmd_logout(self):
        """ Client sendet Logout """
        if not self._check_version():
            return
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
        self._port_handler.handle_remote_monitor_response(PRP_RM_RESP_LOGOUT, self._connection.uid)

    # =============================
    # ====== PRP Batch Mode
    def _rx_prp_batch(self, payload: bytes):
        """ Empfange PRP-Paket Batch """
        data_len  = len(payload)
        for i in range(data_len):
            if payload[i:i + 2] != PRP_FLAG:
                continue
            length    = int.from_bytes(payload[i + 3:i + 5], 'little')
            #        Header(5)+ len+ CRC(2)
            frame_end = i + 5 + length + 2
            # Komplettes Frame extrahiert!
            rem_mon_pack = payload[i:frame_end]
            try:
                self._prp_rx_process(rem_mon_pack)
            except EncodingWarning:
                logger.debug("PRP BATCH: Data Chunk:")
                logger.debug(f"PRP:   DATA  : {payload}")
                logger.debug(f"PRP:   DATA H: {bytearray2hexstr(payload)}")


    ##############################################
    # CTL Local
    def update_cfg(self, cfg: dict):
        print(f"set_remote_mon: {cfg}")
        self._remote_mon_conf.update(cfg)

    ##############################################
    # Helper
    def _check_version(self):
        stat_id = self._connection.cli.stat_identifier
        if stat_id.software != PRP_SW_RESTR:
            logger.warning(f"PRP: This function is just available with {PRP_SW_RESTR}. {stat_id.software}")
            return False
        if version_tuple(stat_id.version) < version_tuple(PRP_VER_RESTR):
            logger.warning(f"PRP: This function is just available with {PRP_SW_RESTR} Version:")
            logger.warning(f"PRP: Version >= {PRP_VER_RESTR}")
            return False
        return True

    ##############################################
    # Getta
    def get_remote_states(self):
        return self._remote_states
