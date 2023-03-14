# from config_station import DefaultPort


class Kiss(object):
    """
    Idea from:
    https://github.com/ampledata/kiss
    """
    def __init__(self, port_cfg):
        self.is_enabled = True
        self.port_cfg = port_cfg
        self.is_enabled = self.port_cfg.parm_kiss_is_on
        """
        self.txd = self.port_cfg.parm_kiss_TXD
        self.pers = self.port_cfg.parm_kiss_Pers
        self.slot = self.port_cfg.parm_kiss_Slot
        self.tail = self.port_cfg.parm_kiss_Tail
        self.f_duplex = self.port_cfg.parm_kiss_F_Duplex
        """
        # CFG Flags
        self.DATA_FRAME = b'\x00'
        self.RETURN = b'\xFF'
        self.START = b'$0'
        # ESC & END Flags
        self.FEND = b'\xC0'
        self.FESC = b'\xDB'
        self.TFEND = b'\xDC'
        self.TFESC = b'\xDD'
        # KISS_ON = 'KISS $0B'
        self.KISS_OFF = b''.join([self.FEND, self.RETURN, self.FEND, self.FEND])
        # self.txd_frame = lambda: self.TX_DELAY + bytes.fromhex(hex(self.port_cfg.parm_kiss_TXD)[2:])
        self.txd_frame = lambda: b'\xC0\x01' + bytes.fromhex(hex(self.port_cfg.parm_kiss_TXD)[2:]) + b'\xC0'
        self.pers_frame = lambda: b'\xC0\x02' + bytes.fromhex(hex(self.port_cfg.parm_kiss_Pers)[2:]) + b'\xC0'
        self.slot_frame = lambda: b'\xC0\x03' + bytes.fromhex(hex(self.port_cfg.parm_kiss_Slot)[2:]) + b'\xC0'
        self.tail_frame = lambda: b'\xC0\x04' + bytes.fromhex(hex(self.port_cfg.parm_kiss_Tail)[2:]) + b'\xC0'
        self.duplex_frame = lambda: b'\xC0\x05' + bytes.fromhex(str(self.port_cfg.parm_kiss_F_Duplex).zfill(2)) + b'\xC0'
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

    def device_kiss_end(self):
        return b''.join([self.FEND, self.RETURN, self.FEND])

    def device_kiss_start(self):
        return b''.join([self.FEND, self.DATA_FRAME, self.START, self.FEND])

