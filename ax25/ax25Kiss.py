# from config_station import DefaultPort


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

    def __init__(self, port_cfg):
        self.is_enabled = True
        self.port_cfg = port_cfg
        self.is_enabled = self.port_cfg.parm_kiss_is_on

        # CFG Flags
        self.DATA_FRAME = b'\x00'  # Channel 0
        self.RETURN = b'\xFF'
        # self.START = b'$0'
        self.JHOST0 = bytes.fromhex('11241B404B0D')  # jhost0 - DC1+CAN+ESC+'@K'  Da fehlt aber noch CR
        # self.START_TNC2 = bytes.fromhex('11241B404B0D')  # TNC2 KISS MODE
        # self.START_TNC_DEFAULT = bytes.fromhex('1B404B')  # TNC2 KISS MODE   b'\x1b@K'
        # self.START_TNC_DEFAULT = b'KISS ON\r\n'  # TNC2 KISS MODE   b'\x1b@K'
        # self.START_TNC_DEFAULT = b'KISS ON\r'  # TNC2 KISS MODE   b'\x1b@K'
        self.START_TNC_DEFAULT = b'KISSM\r'  # TNC2 KISS MODE   b'\x1b@K'
        # self.START_TNC_DEFAULT = bytes.fromhex('11241B404B0D')  # TNC2 KISS MODE   b'\x1b@K'
        # KISS END self.START_TNC_DEFAULT = bytes.fromhex('C0FFC0')  # TNC2 KISS MODE   b'\x1b@K'
        # self.START_TNC_DEFAULT = b'KISSM\r\n '  # TNC2 KISS MODE   b'\x1b@K'
        # ESC & END Flags
        self.FEND = b'\xC0'
        self.FESC = b'\xDB'
        self.TFEND = b'\xDC'
        self.TFESC = b'\xDD'
        # KISS_ON = 'KISS $0B'
        self.KISS_OFF = b''.join([self.FEND, self.RETURN, self.FEND, self.FEND])
        # self.txd_frame = lambda: self.TX_DELAY + bytes.fromhex(hex(self.port_cfg.parm_kiss_TXD)[2:])
        self.txd_frame = lambda: b'\xC0\x01' + bytes.fromhex(hex(self.port_cfg.parm_kiss_TXD)[2:].zfill(2)) + b'\xC0'
        # self.txd_frame_ch1 = lambda: b'\xC0\x11' + bytes.fromhex(hex(self.port_cfg.parm_kiss_TXD)[2:]) + b'\xC0'
        self.pers_frame = lambda: b'\xC0\x02' + bytes.fromhex(hex(self.port_cfg.parm_kiss_Pers)[2:].zfill(2)) + b'\xC0'
        self.slot_frame = lambda: b'\xC0\x03' + bytes.fromhex(hex(self.port_cfg.parm_kiss_Slot)[2:].zfill(2)) + b'\xC0'
        self.tail_frame = lambda: b'\xC0\x04' + bytes.fromhex(hex(self.port_cfg.parm_kiss_Tail)[2:].zfill(2)) + b'\xC0'
        self.duplex_frame = lambda: b'\xC0\x05' + bytes.fromhex(
            str(self.port_cfg.parm_kiss_F_Duplex).zfill(2)) + b'\xC0'
        # self.hw_frame = lambda: b'\x06' + bytes.fromhex(hex(20)[2:]) + b'\xC0'
        self.kiss_data_frame = lambda inp: self.FEND + self.DATA_FRAME + inp + self.FEND
        # "FEND is sent as FESC, TFEND"
        # 0xC0 is sent as 0xDB 0xDC
        self.FESC_TFEND = b''.join([self.FESC, self.TFEND])

        # "FESC is sent as FESC, TFESC"
        # 0xDB is sent as 0xDB 0xDD
        self.FESC_TFESC = b''.join([self.FESC, self.TFESC])

        # self.set_param = self.build_kiss_param_frame()

    def set_all_parameter(self):
        return b''.join([
            self.txd_frame(),
            self.pers_frame(),
            self.slot_frame(),
            self.tail_frame(),
            self.duplex_frame(),
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
            if inp[:2] == self.FEND + self.DATA_FRAME \
                    and inp[-1:] == self.FEND \
                    and len(inp) > 14:
                return inp[2:-1].replace(
                    self.FESC_TFESC,
                    self.FESC
                ).replace(
                    self.FESC_TFEND,
                    self.FEND
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
            return self.kiss_data_frame(
                inp.replace(
                    self.FESC,
                    self.FESC_TFESC
                ).replace(
                    self.FEND,
                    self.FESC_TFEND
                )
            )
        return inp

    @staticmethod
    def device_kiss_end():
        # return b''.join([self.FEND, self.RETURN, self.FEND])
        return bytes.fromhex('C0FFC0')

    def device_jhost(self):
        return self.JHOST0

    def device_kiss_start_1(self):
        # return b''.join([self.FEND, self.DATA_FRAME, self.START, self.FEND])
        # return b''.join([self.START_TNC_DEFAULT, self.START_TNC2])
        # return b''.join([self.START_TNC2])
        return b''.join([self.START_TNC_DEFAULT])
