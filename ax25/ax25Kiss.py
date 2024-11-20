# from config_station import DefaultPort
from cfg.constant import TNC_KISS_CMD, TNC_KISS_END_CMD


class Kiss(object):
    """
    Idea from:
    https://github.com/ampledata/kiss

    TODO: MultiKiss ( Direwolf Channels )
    CH0 Data: \xc0\x00 <AX25-Frame> \x0c\xc0'
    CH1 Data: \xc0\x10 <AX25-Frame> \x0c\xc0'
    CH2 Data: \xc0\x20 <AX25-Frame> \x0c\xc0'
    ...

    """

    def __init__(self, port_cfg: dict):
        self.is_enabled = True
        # self.port_cfg = port_cfg
        self.is_enabled = port_cfg.get('parm_kiss_is_on', True)

        # CFG Flags
        self._DATA_FRAME = b'\x00'  # Channel 0
        self._RETURN = b'\xFF'
        # self.START = b'$0'
        self._JHOST0 = bytes.fromhex('11241B404B0D')  # jhost0 - DC1+CAN+ESC+'@K'  Da fehlt aber noch CR

        # self._START_TNC_DEFAULT = TNC_KISS_CMD  # TNC2 KISS MODE   b'\x1b@K'
        self._START_TNC_DEFAULT = port_cfg.get('parm_kiss_init_cmd', TNC_KISS_CMD)  # TNC2 KISS MODE   b'\x1b@K'
        # self._END_TNC_DEFAULT = TNC_KISS_END_CMD  # TNC2 KISS MODE   b'\x1b@K'
        self._END_TNC_DEFAULT = port_cfg.get('parm_kiss_end_cmd', TNC_KISS_END_CMD)  # TNC2 KISS MODE   b'\x1b@K'

        # ESC & END Flags
        self._FEND = b'\xC0'
        self._FESC = b'\xDB'
        self._TFEND = b'\xDC'
        self._TFESC = b'\xDD'
        # KISS_ON = 'KISS $0B'
        # self.KISS_OFF = b''.join([self._FEND, self._RETURN, self._FEND, self._FEND])
        # ???? self.KISS_OFF = b''.join([self.FEND, self.RETURN, self.FEND]) ????
        # self.txd_frame = lambda: self.TX_DELAY + bytes.fromhex(hex(self.port_cfg.parm_kiss_TXD)[2:])
        self._txd_frame = lambda: b'\xC0\x01' + bytes.fromhex(hex(port_cfg.get('parm_kiss_TXD', 35))[2:].zfill(2)) + b'\xC0'
        # self.txd_frame_ch1 = lambda: b'\xC0\x11' + bytes.fromhex(hex(self.port_cfg.parm_kiss_TXD)[2:]) + b'\xC0'
        self._pers_frame = lambda: b'\xC0\x02' + bytes.fromhex(hex(port_cfg.get('parm_kiss_Pers', 160))[2:].zfill(2)) + b'\xC0'
        self._slot_frame = lambda: b'\xC0\x03' + bytes.fromhex(hex(port_cfg.get('parm_kiss_Slot', 30))[2:].zfill(2)) + b'\xC0'
        self._tail_frame = lambda: b'\xC0\x04' + bytes.fromhex(hex(port_cfg.get('parm_kiss_Tail', 15))[2:].zfill(2)) + b'\xC0'
        self._duplex_frame = lambda: b'\xC0\x05' + bytes.fromhex(
            str(port_cfg.get('parm_kiss_F_Duplex', 0)).zfill(2)) + b'\xC0'
        # self.hw_frame = lambda: b'\x06' + bytes.fromhex(hex(20)[2:]) + b'\xC0'
        self._kiss_data_frame = lambda inp: self._FEND + self._DATA_FRAME + inp + self._FEND
        # "FEND is sent as FESC, TFEND"
        # 0xC0 is sent as 0xDB 0xDC
        self._FESC_TFEND = b''.join([self._FESC, self._TFEND])

        # "FESC is sent as FESC, TFESC"
        # 0xDB is sent as 0xDB 0xDD
        self._FESC_TFESC = b''.join([self._FESC, self._TFESC])

        # self.set_param = self.build_kiss_param_frame()

    def set_all_parameter(self):
        return b''.join([
            self._txd_frame(),
            self._pers_frame(),
            self._slot_frame(),
            self._tail_frame(),
            self._duplex_frame(),
        ])

    def de_kiss(self, inp: b''):
        """
        Code from: https://github.com/ampledata/kiss
        Escape special codes, per KISS spec.
        "If the FEND or FESC codes appear in the data to be transferred, they
        need to be escaped. The FEND code is then sent as FESC, TFEND and the
        FESC is then sent as FESC, TFESC."
        - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
        """
        if self.is_enabled:
            if inp[:2] == self._FEND + self._DATA_FRAME \
                    and inp[-1:] == self._FEND \
                    and len(inp) > 14:
                return inp[2:-1].replace(
                    self._FESC_TFESC,
                    self._FESC
                ).replace(
                    self._FESC_TFEND,
                    self._FEND
                )
            else:
                return b''
        return inp

    def kiss(self, inp: b''):
        """
        Code from: https://github.com/ampledata/kiss
        Recover special codes, per KISS spec.
        "If the FESC_TFESC or FESC_TFEND escaped codes appear in the data received,
        they need to be recovered to the original codes. The FESC_TFESC code is
        replaced by FESC code and FESC_TFEND is replaced by FEND code."
        - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
        """
        if self.is_enabled:
            return self._kiss_data_frame(
                inp.replace(
                    self._FESC,
                    self._FESC_TFESC
                ).replace(
                    self._FEND,
                    self._FESC_TFEND
                )
            )
        return inp

    def device_kiss_end(self):
        # return b''.join([self.FEND, self.RETURN, self.FEND])
        return self._END_TNC_DEFAULT

    def device_kiss_start_1(self):
        return self._START_TNC_DEFAULT
