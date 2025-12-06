import datetime

from ax25.ax25Error import AX25DecodingERROR
from cfg.constant import REM_MON_RESP_START, REM_MON_RESP_STOP
from cfg.default_config import getNew_remote_mon_cfg
from cfg.logger_config import logger
from fnc.ax25_fnc import reverse_uid
from fnc.lzhuf import LZHUF_Comp
from ax25.ax25dec_enc import AX25Frame, bytearray2hexstr
from fnc.str_fnc import version_tuple

REM_MON_FLAG = b'\x8D\x81'
##############################################
# ESC & END Flags
FEND  = b'\x8D'
FESC  = b'\x8F'
TFEND = b'\x92'
TFESC = b'\x9B'

FESC_TFEND = b''.join([FESC, TFEND])    # "FEND is sent as FESC, TFEND"  /  0x8D is sent as 0x8F 0x92
FESC_TFESC = b''.join([FESC, TFESC])    # "FESC is sent as FESC, TFESC"  /  0x8F is sent as 0x8F 0x9B

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

class RemoteMonitor:
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
    # TX
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
            self._connection.cli.cli_update_monitor(ax25frame_conf)
        # PoPT Remote Monitor
        if self._remote_mon_conf.get('gui_mon', False):
            self._remote_mon_tx(ax25frame_conf)

    def _remote_mon_tx(self, ax25frame_conf: dict):
        data_to_send = self._encode_remote_mon_frame(ax25frame_conf)
        if data_to_send:
            #logger.debug('= Gesendet' + '=' * 38)
            #logger.debug(f"SEQ: {self._tx_seq}")
            #logger.debug(f"Hex: {bytearray2hexstr(data_to_send)}")
            #logger.debug('= Gesendet ENDE' + '=' * 35)
            self._connection.send_remote_data(data_to_send)
            #self._tx_seq += 1
    #############################################
    # Encoding
    def _encode_remote_mon_frame(self, ax25frame_conf: dict):
        ax25_rawFrame   = ax25frame_conf.get('ax25_raw', b'')
        tx              = ax25frame_conf.get('tx', False)
        port_id         = ax25frame_conf.get('port', 0)
        rx_time         = ax25frame_conf.get('rx_time', datetime)
        dec_rx_time     = pack_time_hms(rx_time)
        ax25_data = bytearray()
        ax25_data += dec_rx_time
        ax25_data += ax25_rawFrame

        return self._encode_remote_frame(
            opt_id=int(port_id),
            tx=tx,
            data=ax25_data
        )

    @staticmethod
    def _encode_remote_frame(opt_id: int, tx: bool, data: bytes):
        send_compressed = False
        if data:
            # LZHUF it
            lzhuf = LZHUF_Comp()
            compressed_data = lzhuf.encode(data)
            if len(compressed_data) < len(data):
                send_compressed = True
                data = compressed_data
            # Escaping
            data = data.replace(FESC, FESC_TFESC)
            data = data.replace(FEND, FESC_TFEND)
        # Building Packet
        data_to_send = bytearray()
        data_to_send += REM_MON_FLAG  # C0 F0
        data_to_send += pack_6bit_int_and_bool(value=int(opt_id), flag1=tx, flag2=send_compressed)
        data_to_send += len(data).to_bytes(2, 'little')
        data_to_send += data
        return data_to_send
    #############################################
    # RX
    def remote_mon_rx(self, data: bytes):
        # Opt by Grok-AI
        # Kombiniere mit Buffer, falls vorhanden
        if self._remote_monitor_buffer:
            data = self._remote_monitor_buffer + data
            self._remote_monitor_buffer = bytearray()
        #debug_data = bytes(data)
        rest_data  = bytearray()  # Sammelt den Non-Remote-Monitor-Stream
        i = 0
        data_len = len(data)
        #logger.debug('= ! Empfangen ROH !' + '=' * 31)
        #logger.debug(f"SEQ: {self._rx_seq}")
        #logger.debug(f"Hex: {bytearray2hexstr(data)}")
        #logger.debug('= ! Empfangen ROH ! ENDE' + '=' * 26)
        while i < data_len:
            # Suche nächsten Frame-Start (C0 F0)
            if data[i:i + 2] == REM_MON_FLAG:
                # Potenzieller Frame-Start gefunden
                if i + 5 > data_len:
                    # Header unvollständig -> puffern
                    self._remote_monitor_buffer = data[i:]
                    break

                length = int.from_bytes(data[i + 3:i + 5], 'little')
                frame_end = i + 5 + length

                if frame_end > data_len:
                    # Frame unvollständig -> puffern
                    self._remote_monitor_buffer = data[i:]
                    break

                # Komplettes Frame extrahiert!
                rem_mon_pack = data[i:frame_end]
                self._remote_mon_rx_process(rem_mon_pack)

                i = frame_end  # Springe zum nächsten Byte nach dem Frame
                continue

            # Kein Frame-Start: Dieses Byte gehört zum Rest-Stream
            rest_data.append(data[i])
            i += 1

        # Wenn Rest nach letztem Frame übrig, zu rest_data hinzufügen (aber hier schon in Schleife gehandhabt)
        if rest_data == b'\xc0':
            self._remote_monitor_buffer += rest_data
            return b''
        """
        if rest_data:
            logger.debug("REST")
            logger.debug(f"SEQ: {self._rx_seq}")
            logger.debug(f"Rest    : {rest_data}")
            logger.debug(f"Data    : {debug_data}")
            logger.debug(f"Rest hex: {rest_data.hex()}")
            logger.debug(f"Data hex: {debug_data.hex()}")
        """
        return bytes(rest_data)

    def _remote_mon_rx_process(self, rem_mon_frame: bytes):
        #logger.debug('= Empfangen' + '=' * 38)
        #logger.debug(f"SEQ: {self._rx_seq}")
        #logger.debug(f"Hex: {bytearray2hexstr(rem_mon_frame)}")
        #logger.debug('= Empfangen ENDE' + '=' * 34)
        #self._rx_seq += 1
        decoded_ax25pack = self._decode_remote_mon_frame(rem_mon_frame)
        if not decoded_ax25pack:
            return
        if not hasattr(self._port_handler, 'handle_remote_monitor_rx'):
            logger.error("Attribute Error Port-Handler: handle_remote_monitor_rx ")
            return
        self._remote_states['gui_rem_mon'] = True
        self._port_handler.handle_remote_monitor_rx(decoded_ax25pack, self._connection.uid)

    ##############################################
    # Decoding
    def _decode_remote_mon_frame(self, data: bytes):
        opt_byte = data[2:3]
        # length = data[3:5] # little
        payload = data[5:]
        # Unescaping
        payload = payload.replace(FESC_TFEND, FEND)
        payload = payload.replace(FESC_TFESC, FESC)
        # Decoding
        opt_id, tx, is_compressed = unpack_6bit_int_and_bool(opt_byte)
        if is_compressed:
            lzhuf = LZHUF_Comp()
            payload = lzhuf.decode(payload)

        # 0 - 19 = Port ID
        if opt_id in range(20):
            try:
                return self._decode_ax25frame(payload, opt_id, tx)
            except AX25DecodingERROR:
                logger.warning("-------------------------------------------------------------------")
                logger.warning(f'Remote Monitor: decoding: ')
                logger.warning(f'Remote Monitor: data org {data}')
                logger.warning(f'Remote Monitor: data hex {bytearray2hexstr(data)}')
                logger.warning(f'Remote Monitor: ax25_frame org {payload}')
                logger.warning(f'Remote Monitor: ax25_frame hex {bytearray2hexstr(payload)}')
                logger.warning("-------------------------------------------------------------------")
                return None
        # 20 - 63 = CMD'S
        # TX = Send CMD(True) / ACK CMD(False) /
        if opt_id == 20:
            """ Remote Monitor Start """
            if tx:
                self._rx_cmd_gui_remote_mon(payload)
            else:
                self._rx_resp_cmd_start_gui_remote_mon()
            return None
        if opt_id == 21:
            """ Remote Monitor Stop """
            if tx:
                self._rx_cmd_stop_gui_remote_mon()
            else:
                self._rx_resp_cmd_stop_gui_remote_mon()
            return None
        if opt_id == 22:
            """ Disconnect """
            if tx:
                self._rx_cmd_disco()
            return None

        return None

    @staticmethod
    def _decode_ax25frame(ax25_data, port_id, tx):
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
    # ====== Remote Mon Start CMD
    def cmd_start_gui_remote_mon(self, cfg: dict):
        """ TX Start CMD """
        if not self._check_version():
            return

        port_id = cfg.get('port', 0)
        incl_filter = ','.join(cfg.get('incl_call', []))
        excl_filter = ','.join(cfg.get('excl_call', []))

        data = f"{port_id}:{incl_filter}:{excl_filter}".encode('UTF-8', 'ignore')
        data2send = self._encode_remote_frame(opt_id=20, tx=True, data=data)
        if not data2send:
            return
        self._connection.send_remote_data(data2send)

    def _rx_cmd_gui_remote_mon(self, payload: bytes):
        """ RX Start CMD """
        data = payload.decode('UTF-8', 'ignore')
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
        data2send = self._encode_remote_frame(opt_id=20, tx=False, data=b'')
        if not data2send:
            return
        self._connection.send_remote_data(data2send)

    def _rx_resp_cmd_start_gui_remote_mon(self):
        """ RX Respond Stop CMD """
        self._remote_states['gui_rem_mon'] = True
        self._port_handler.handle_remote_monitor_response(REM_MON_RESP_START, self._connection.uid)

    # ====== Remote Mon Stop CMD
    def cmd_stop_gui_remote_mon(self):
        """ TX Start CMD """
        if not self._check_version():
            return
        data2send = self._encode_remote_frame(opt_id=21, tx=True, data=b'')
        if not data2send:
            return
        self._connection.send_remote_data(data2send)

    def _rx_cmd_stop_gui_remote_mon(self):
        """ RX Stop CMD """
        cfg = dict(
            gui_mon=False,
        )
        print(f"set_remote_mon: {cfg}")
        self._tx_resp_cmd_stop_gui_remote_mon()
        self._remote_mon_conf.update(cfg)

    def _tx_resp_cmd_stop_gui_remote_mon(self):
        """ TX Respond Stop CMD """
        data2send = self._encode_remote_frame(opt_id=21, tx=False, data=b'')
        if not data2send:
            return
        self._connection.send_remote_data(data2send)

    def _rx_resp_cmd_stop_gui_remote_mon(self):
        """ RX Respond Stop CMD """
        self._remote_states['gui_rem_mon'] = False
        self._port_handler.handle_remote_monitor_response(REM_MON_RESP_STOP, self._connection.uid)

    # ====== Disconnect CMD
    def cmd_disco(self):
        """ TX Start Disco CMD """
        if not self._check_version():
            return
        data2send = self._encode_remote_frame(opt_id=22, tx=True, data=b'')
        if not data2send:
            return
        self._connection.send_remote_data(data2send)

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
        if stat_id.software != 'PoPTNode':
            logger.warning(f"This function is just available with a PoPT-Station. {stat_id.software}")
            return False
        if version_tuple(stat_id.version) < version_tuple('2.123.1'):
            logger.warning("This function is just available with a PoPT-Station Version.")
            logger.warning("Version >= 2.123.1")
            return False
        return True

    ##############################################
    # Getta
    def get_remote_states(self):
        return self._remote_states