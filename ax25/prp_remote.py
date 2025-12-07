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

  • FLAG-Sequenz      = immer 0x8D 0x81        - 2 Bytes
  • OPTBYTE           = siehe Abschnitt 2      - 1 Byte
  • LEN               = Länge des PAYLOADs     - 2 Bytes
  • PAYLOAD           = escaped, ggf. vorher LZHUF-komprimiert
  • CRC               = CRC16                  - 2 Bytes

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
 20    | Remote-Mon START   | ACK START           | siehe 5.1
 21    | Remote-Mon STOP    | ACK STOP            | leer
 22    | Disconnect         | (kein ACK)          | leer

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

Angenommenes Payload nach Escaping: 26 Byte
z. B. Zeit 16:47:08 + kurzes AX.25-Frame → escaped Payload = 26 Byte

Gesendet wird (Hex):

8D 81 6D 1A 00 16 47 08 A0 84 ... (26 Byte Payload) ... A7 3F

Aufschlüsselung:
8D 81     → Flag
6D        → OPTBYTE = 0b01101101 → Port 13, TX=1, komprimiert=0
1A 00     → Länge = 26 Byte Payload (nach Un-Escaping)
16 47 08  → BCD-Zeit 16:47:08
...       → Rest des AX25-Frames
A7 3F     → CRC16-CCITT über alles ab Byte 2 (OPTBYTE) bis letztes Payload-Byte
            (in diesem Beispiel: CRC = 0x3FA7)

══════════════════════════════════════════════════════════════════════════
8. Zusammenfassungstabelle
══════════════════════════════════════════════════════════════════════════

ID-Bereich | Bedeutung                  | Payload vor Escaping/Kompression
-----------+----------------------------+----------------------------------------
 0 – 19    | Monitor-Frame Port X       | 3 Byte BCD-Zeit + rohes AX.25-Frame
 20        | Remote-Mon START           | "port:incl:excl" (nur bei CMD)
 20        | ACK START                  | leer
 21        | Remote-Mon STOP            | leer
 21        | ACK STOP                   | leer
 22        | Disconnect                 | leer

══════════════════════════════════════════════════════════════════════════
Ende der Spezifikation
══════════════════════════════════════════════════════════════════════════
"""
import datetime

from ax25.ax25Error import AX25DecodingERROR
from cfg.default_config import getNew_remote_mon_cfg
from cfg.logger_config import logger
from fnc.ax25_fnc import reverse_uid
from fnc.crc_fnc import crc16_ccitt
from fnc.lzhuf import LZHUF_Comp
from ax25.ax25dec_enc import AX25Frame, bytearray2hexstr
from fnc.str_fnc import version_tuple

##################################################
PRP_SW_RESTR  = 'PoPTNode'  # Software restriction
PRP_VER_RESTR = '2.123.7'   # Version restriction
##################################################
PRP_FLAG = b'\x8D\x81'      # PRP Flag
##################################################
# ESC & END Flags
PRP_FEND  = b'\x8D'
PRP_FESC  = b'\x8F'
PRP_TFEND = b'\x92'
PRP_TFESC = b'\x9B'

PRP_FESC_TFEND = b''.join([PRP_FESC, PRP_TFEND])    # "FEND is sent as FESC, TFEND"  /  0x8D is sent as 0x8F 0x92
PRP_FESC_TFESC = b''.join([PRP_FESC, PRP_TFESC])    # "FESC is sent as FESC, TFESC"  /  0x8F is sent as 0x8F 0x9B
##################################################
# OPT-ID ≥ 20
PRP_OPT_RM_START    = 20 # Remote Monitor Start/Update
PRP_OPT_RM_STOP     = 21 # Remote Monitor Stop
PRP_OPT_DISCO       = 22 # Connection (soft)Disco
##################################################
# Response (GUI Handling)
PRP_RM_RESP_START   = 'rsp_start'   # Remote Monitor Start/Update
PRP_RM_RESP_STOP    = 'rsp_stop'    # Remote Monitor Stop

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
        self._remote_mon_conf   = getNew_remote_mon_cfg()
        self._remote_monitor_buffer = bytearray()
        # States
        self._remote_states = dict(
            gui_rem_mon=False,
        )
        # Debugging
        self._tx_seq = 0
        self._rx_seq = 0

    #######################################
    # PRP ENC/DEC
    @staticmethod
    def _encode_prp_frame(opt_id: int, tx: bool, data: bytes):
        send_compressed = False
        if data:
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
        # Unescaping
        payload = payload.replace(PRP_FESC_TFEND, PRP_FEND)
        payload = payload.replace(PRP_FESC_TFESC, PRP_FESC)
        # Decoding
        opt_id, tx, is_compressed = unpack_6bit_int_and_bool(opt_byte)
        if is_compressed:
            lzhuf = LZHUF_Comp()
            payload = lzhuf.decode(payload)

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
        # 20 - 63 = CMD'S
        # TX = Send CMD(True) / ACK CMD(False) /
        if opt_id == PRP_OPT_RM_START:
            """ Remote Monitor Start """
            if tx:
                self._rx_cmd_gui_remote_mon(payload)
            else:
                self._rx_resp_cmd_start_gui_remote_mon()
            return None
        if opt_id == PRP_OPT_RM_STOP:
            """ Remote Monitor Stop """
            if tx:
                self._rx_cmd_stop_gui_remote_mon()
            else:
                self._rx_resp_cmd_stop_gui_remote_mon()
            return None
        if opt_id == PRP_OPT_DISCO:
            """ Disconnect """
            if tx:
                self._rx_cmd_disco()
            return None

        return None

    #############################################
    # I/O - TX/RX
    def _prp_tx(self, opt_id: int, tx_flag: bool, data: bytes, prio=False):
        data2send = self._encode_prp_frame(opt_id=opt_id, tx=tx_flag, data=data)
        if not data2send:
            return
        self._connection.send_remote_data(data2send, prio=prio)

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
        """ Called fm port_handler.update_monitor() """
        if not any((
                self._remote_mon_conf.get('cli_mon', False),
                self._remote_mon_conf.get('gui_mon', False)
        )):
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
        if any((
            frame_uid == my_uid,
            frame_uid == my_uid_rev
        )):
            return

        if any((
            all((
                to_call   == self._connection.to_call_str_add,
                from_call == self._connection.my_call_str_add,
            )),
            all((
                from_call == self._connection.to_call_str_add,
                to_call   == self._connection.my_call_str_add,
            )),
        )):
            return

        # Exclude Filter
        if any((
            from_call in excl_filter,
            to_call   in excl_filter
        )): return

        # Include Filter
        if incl_filter:
            if not any((
                from_call in incl_filter,
                to_call   in incl_filter
            )): return

        # CLI Monitor Output
        if self._remote_mon_conf.get('cli_mon', False):
            # TODO
            self._connection.cli.cli_update_monitor(ax25frame_conf)
        # PoPT Remote Monitor
        if self._remote_mon_conf.get('gui_mon', False):
            self._encode_remote_mon_frame(ax25frame_conf)

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
