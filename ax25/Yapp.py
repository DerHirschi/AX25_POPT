import logging
from fnc.crc_fnc import get_crc

logger = logging.getLogger(__name__)
NUL = b'\x00'
"""
YAPP_HEADERS = [
    b'\x06\x01',
    b'\x06\x02',
    b'\x06\x06',
    b'\x06\x03',
    b'\x06\x04',
    b'\x05\x01',
    # b'\x01',
    # b'\x02',
    b'\x03\x01',
    b'\x04\x01',
    # b'\x15',
    # b'\x18',
    b'\x06\x05',
    # b'\x05',
    # b'\x10',
]
YAPP_HEADERS_W_LEN = [
    b'\x01',
    b'\x02',
    b'\x15',
    b'\x18',
    b'\x10'
]
"""


class Yapp(object):
    def __init__(self, ft_class):
        self.ft_class = ft_class
        # self.param_PacLen = ft_class.ft_root.param_PacLen
        self.param_MaxFrame = ft_class.ft_root.param_MaxFrame
        self.param_proto_conn = True
        self.pack_types_enc = {
            'RR': self.enc_RR,
            'RF': self.enc_RF,  # Normal Yapp reply
            'RT': self.enc_RT,  # Extended Yapp reply
            'AF': self.enc_AF,
            'AT': self.enc_AT,
            'SI': self.enc_SI,
            'HD': self.enc_HD,
            'DT': self.enc_DT,
            'EF': self.enc_EF,
            'ET': self.enc_ET,
            'NR': self.enc_NR,
            'RE': self.enc_RE,
            'CN': self.enc_CN,
            'CA': self.enc_CA,

            # Used in Server mode
            'RI': self.enc_RI,
            'TX': self.enc_TX,

            # Unimplemented - Reserved for Server Commands
            'UU': self.enc_UU,
            'Start/Done': self.done,
        }
        self.pack_types_dec = {
            b'\x06': self.dec_RR_RF_RT_AF_AT_CA,
            b'\x05': self.dec_SI_RI_UU,
            b'\x01': self.dec_HD,
            b'\x02': self.dec_DT,
            b'\x03': self.dec_EF,
            b'\x04': self.dec_ET,
            b'\x15': self.dec_NR_OR_RE,
            b'\x18': self.dec_CN,

            # Used in Server mode
            b'\x10': self.dec_TX,
            # b'\x0502':   self.dec_RI,

            # Unimplemented - Reserved for Server Commands
            # b'\x05':     self.dec_UU,
        }
        """ State Tab Sending File """
        self.tx_state_table = {
            'S': ('SI',     # SEND
                  {
                      'RR': 'SH',
                      'RF': 'SD',
                      'NR': 'Start/Done',
                      'RI': 'S',
                      # First few timeouts    S
                      # Other/Timeout         Abort
                      'Other':   'Abort',
                      'Timeout': 'Abort',
                  }),
            'SH': ('HD',    # HDR
                   {
                       'RF': 'SD',
                       'NR': 'Start/Done',
                       # IF (RESUME)
                       # 'RE': """ Move file position then """ 'SD'
                       'Other':   'Abort',
                       'Timeout': 'Abort',
                   }),
            'SD': ('DT',    # DATA
                   {
                       False: 'SD',     # Not EOF
                       True:  'SE'      # EOF
                   }),
            'SE': ('EF',    # EOF
                   {
                       # 'AF': 'SH', # TODO     # More Files
                       'AF': 'ST',      # No More Files
                       'Other':   'Abort',
                       'Timeout': 'Abort'
                   }),
            'ST': ('ET',    # EOT
                   {
                       'AT':      'Start/Done',
                       'Other':   'Start/Done',
                       'Timeout': 'Start/Done',
                   }),
            'Abort': ('CN',
                      {
                          '': 'Start/Done',
                          'CA': 'Start/Done',
                      }),
            'Start/Done': ('Start/Done',
                      {
                          '': 'Start/Done'
                      }),
        }
        """ State Tab Receiving File """
        self.rx_state_table = {
            'R': {      # REC
                # On:      (Resp, State)
                'SI':      self.resp_R_SI(),
                'NR':      ('', 'Start/Done'),
                'CN':      ('CA', 'Start/Done'),
                'Other':   ('CN', 'CW'),
                'Timeout': ('CN', 'CW')
            },
            'RH': {
                'HD':      self.resp_R_HD(),
                'SI':      ('', 'RH'),
                'ET':      ('AT', 'Start/Done'),
                'CN':      ('CA', 'Start/Done'),
                'Other':   ('CN', 'CW'),
                'Timeout': ('CN', 'CW')
            },
            'RD': {
                'DT':      ('', 'RD'),       # store_data()
                'EF':      ('AF', 'RH'),     # close_File()
                'CN':      ('CA', 'Start/Done'),
                'Other':   ('CN', 'CW'),
                'Timeout': ('CN', 'CW')
            },
            'CW': {
                'CA': ('', 'Start/Done'),
                'CN': ('CA', 'CW'),
                # 'Timeout': (fnc_set_error(), 'Start/Done'),
            },
            'Start/Done': {
                               '': ('', 'Start/Done')  # TODO done_fnc()
                           },
        }
        """ Flags """
        self.ext_header = False
        self.YappC = False
        self.e = True
        self.Resume = False
        self.Done = False
        self.TX = None       # Sending or Receiving
        self.state = ''

        # self.file_name = ''
        self.file_name = self.ft_class.filename
        self.file_size = 0
        self.file_time = ''  # '12:30:45'
        self.file_date = ''  # '2023-05-18'
        # self.file_rawdata = b''
        # self.file_rawdata = self.ft_class.ft_root.ft_tx_buf
        self.rx_pack_buff = b''
        self.rx_pac_type = ''
        self.rx_pac_len = 0
        self.tx_last_pack = b''

    def init_tx(self):
        # print("Yapp INIT")
        if self.check_init():
            # print("Yapp INIT Check OK")
            self.TX = True
            self.state = 'S'
            self.file_size = len(self.ft_class.ft_root.ft_tx_buf)
            self.e = False
            return True
        return False

    def init_rx(self):
        if self.check_init():
            # TODO Feed in Header
            self.TX = False
            self.state = 'R'
            self.e = False
            return True
        return False

    """
    def send_init_pack(self):
        if self.TX:
            self.yapp_tx('SI')
    """

    def check_init(self):
        if not self.ft_class.ft_root.ft_tx_buf:
            print("Yapp INIT Check - NO ft_class.ft_root.ft_tx_buf")
            logger.error("Yapp INIT Check - NO ft_class.ft_root.ft_tx_buf")
            return False
        if not self.file_name:
            print("Yapp INIT Check - NO file_name")
            logger.error("Yapp INIT Check - NO file_name")
            return False
        return True

    def done(self):
        self.Done = True

    def exec_abort(self):
        self.state = 'Abort'

    def check_packet_length(self):
        if len(self.rx_pack_buff) >= 2:
            packet_length = self.rx_pack_buff[1]
            if self.rx_pack_buff.startswith(b'\x02'):
                if not packet_length:
                    packet_length = 256
                # Exclude checksum length for DT packets
            if len(self.rx_pack_buff[2:]) >= packet_length:
                return packet_length
        return False

    def yapp_tx(self, pack_typ: ''):
        if pack_typ:
            pack_data = None
            if pack_typ == 'DT':
                if self.ft_class.can_send():
                    pack_data = self.pack_types_enc.get(pack_typ, False)
            else:
                pack_data = self.pack_types_enc.get(pack_typ, False)
            # print(f"yapp_tx: pack_typ: {pack_typ} - pack_data: {pack_data}")
            if pack_data is not None:
                if pack_data:
                    pack_data = pack_data()
                    if pack_data:
                        if pack_data != self.tx_last_pack and self.param_proto_conn:
                            self.ft_class.send_data(pack_data)
                            self.tx_last_pack = pack_data
                            return True
        return False

    def yapp_rx(self, data_in: b''):
        # print(f"Yapp in:     {data_in}")
        # print(f"Yapp in hex: {data_in.hex()}")
        e = True
        rest = b''
        if data_in:
            self.rx_pack_buff += data_in
            while self.rx_pack_buff:
                self.rx_pac_len = 0
                res = self.pack_types_dec.get(bytes([self.rx_pack_buff[0]]), False)
                if res:
                    res = res()
                    if res:
                        self.rx_pac_type = res
                        # STATES EXEC
                        res = self.exec_state_tab()
                        if not res:
                            rest += bytes([self.rx_pack_buff[0]])
                            self.rx_pack_buff = self.rx_pack_buff[1:]
                        elif self.rx_pac_len:
                            self.rx_pack_buff = self.rx_pack_buff[self.rx_pac_len:]
                            rest = b''
                            e = False
                    else:
                        rest += bytes([self.rx_pack_buff[0]])
                        self.rx_pack_buff = self.rx_pack_buff[1:]
                else:
                    rest += bytes([self.rx_pack_buff[0]])
                    self.rx_pack_buff = self.rx_pack_buff[1:]
            self.rx_pack_buff = rest
        return e

    def yapp_cron(self):
        return self.exec_state_tab()

    def exec_state_tab(self):
        # STATES
        if self.TX:
            # Send File
            resp, tmp_state_tab = self.tx_state_table.get(self.state, ('', {}))
            self.state = tmp_state_tab.get(self.rx_pac_type, self.state)
        else:
            # Receive File
            if self.state not in self.rx_state_table:
                return False
            resp, self.state = self.rx_state_table[self.state].get(self.rx_pac_type, ('CN', 'CW'))
        if resp:
            self.yapp_tx(resp)
        return True

    def resp_R_SI(self):
        """
        R (Rec)     SI (ready)                       RR              RH
                    SI (opt)*       open file        RF              RD
                    SI (not ready)                   NR              Start/Done
        :return: Send Pkt, Next State
        """
        """
        if not open_file:
            return 'NR', 'Start/Done'
        """
        return 'RR', 'RH'

    def resp_R_HD(self):
        """
        RH (Hdr)    HD               open file       RF              RD
                    HD (no room)                     NR              Start/Done

        IF (RESUME)
                    HD Already       open file for   RE              RD
                    have file!      append at -256
                                    byte from EOF

        ELSE        HD Already have file!!           NR              Start/Done

                    SI                                               RH
                    ET                               AT              Start/Done
                    Other/Timeout                                    Abort
        :return: Send Pkt, Next State
        """
        return 'RF', 'RD'

    def clean_rx_buf(self):
        # self.rx_pac_type = ''
        self.rx_pack_buff = b''

    def build_frame(self, pack_typ: b'', data: b''):
        return pack_typ + bytes([len(data)]) + data

    def dec_NR_OR_RE(self):
        if len(self.rx_pack_buff) > 2:
            if self.rx_pack_buff[2] == ord('R'):
                return self.dec_RE()  # Decode as Resume
        return self.dec_NR()  # Decode as Not_Rdy

    def dec_RR_RF_RT_AF_AT_CA(self):
        if len(self.rx_pack_buff) >= 2:
            ret = {
                b'\x01': self.dec_RR,
                b'\x02': self.dec_RF,  # Normal Yapp reply
                b'\x06': self.dec_RT,  # Extended Yapp reply
                b'\x03': self.dec_AF,
                b'\x04': self.dec_AT,
                b'\x05': self.dec_CA,
            }.get(bytes([self.rx_pack_buff[1]]), False)
            if not ret:
                return False
            return ret()

    def dec_SI_RI_UU(self):
        if len(self.rx_pack_buff) >= 2:
            ret = {
                b'\x01': self.dec_SI,
                b'\x02': self.dec_RI,  # Used in Server mode
            }.get(
                bytes([self.rx_pack_buff[1]]),
                self.dec_UU  # Unimplemented - Reserved for Server Commands
            )
            return ret()

    """ Packet definitions """
    def enc_RR(self):
        """ Rcv_Rdy """
        return b'\x06\x01'

    def dec_RR(self):
        """ Rcv_Rdy """
        self.rx_pac_len = 2
        return 'RR'

    def enc_RF(self):
        """ Rcv_File > Normal Yapp reply """
        return b'\x06\x02'

    def dec_RF(self):
        """ Rcv_File > Normal Yapp reply """
        self.rx_pac_len = 2
        return 'RF'

    def enc_RT(self):
        """ Receive_TPK > Extended Yapp reply """
        return b'\x06\x06'

    def dec_RT(self):
        """ Receive_TPK > Extended Yapp reply """
        self.rx_pac_len = 2
        return 'RT'

    def enc_AF(self):
        """ Ack_EOF """
        return b'\x06\x03'  # [1.1]

    def dec_AF(self):
        """ Ack_EOF """
        self.rx_pac_len = 2
        return 'AF'  # [1.1]

    def enc_AT(self):
        """ Ack_EOT """
        return b'\x06\x04'  # [1.1]

    def dec_AT(self):
        """ Ack_EOT """
        self.rx_pac_len = 2
        return 'AT'  # [1.1]

    def enc_SI(self):
        """ Send_Init """
        return b'\x05\x01'

    def dec_SI(self):
        """ Send_Init """
        self.rx_pac_len = 2
        return 'SI'

    def enc_HD(self):
        """ Send_Hdr """
        #  SOH   len  (Filename)  NUL  (File Size in ASCII)  NUL  (Opt)
        # [SOH] [Len] [Filename] [NUL] [File Size] [NUL] [Date] [Time] [NUL]
        ret = self.file_name.encode() + \
              NUL + \
              str(self.file_size).encode('ASCII') + \
              NUL
        if self.ext_header:
            ret = ret + \
                  self.file_date.encode() + \
                  self.file_time.encode() + \
                  NUL

        return self.build_frame(pack_typ=b'\x01', data=ret)

    def dec_HD(self):
        """ Send_Hdr """
        #  SOH   len  (Filename)  NUL  (File Size in ASCII)  NUL  (Opt)
        # [SOH] [Len] [Filename] [NUL] [File Size] [NUL] [Date] [Time] [NUL]
        self.rx_pac_len = 2  # TODO !!!
        return 'HD'

    def enc_DT(self):
        """ Send_Data """
        #  STX   len   (Data)    {if len=0 then data length = 256}
        # [STX] [Len] [Datas] [Checksum]

        # data_len = self.param_PacLen - 2
        data_len = self.ft_class.ft_root.param_PacLen - 2
        if self.YappC or self.Resume:
            data_len = - 2  # TODO on 8 Bit CRC - 1
        if len(self.ft_class.ft_root.ft_tx_buf) < data_len:
            data_len = len(self.ft_class.ft_root.ft_tx_buf)
        data = self.ft_class.ft_root.ft_tx_buf[:data_len]
        self.ft_class.ft_root.ft_tx_buf = self.ft_class.ft_root.ft_tx_buf[data_len:]
        # checksum = bytes([get_crc(data)])   # TODO Maybe Checksum is not right (8 bit like x-modem ?)
        checksum = get_crc(data)   # TODO Maybe Checksum is not right (8 bit like x-modem ?)
        # print(f"Yapp DT CRC: {checksum}")
        if not self.ft_class.ft_root.ft_tx_buf:
            self.state = 'SE'
        if self.YappC or self.Resume:
            return self.build_frame(pack_typ=b'\x02', data=data) + checksum
        return self.build_frame(pack_typ=b'\x02', data=data)

    def dec_DT(self):
        """ Send_Data """
        pac_len = self.check_packet_length()
        if pac_len:
            if self.YappC or self.Resume:
                data = self.rx_pack_buff[2:pac_len]
                self.rx_pac_len = pac_len + 2           # TODO + 1 if 8 Bit CRC
                chk_sum = self.rx_pack_buff[pac_len: self.rx_pac_len]
                calc_chk_sum = get_crc(data)
                if chk_sum == calc_chk_sum:     # TODO Maybe Checksum is not right (8 bit like x-modem ?)
                    self.ft_class.ft_root.ft_tx_buf += data
                    # print(f"Yapp get data: {data}")
                    return 'DT'
                else:
                    logger.error(f"Yapp CRC-Error: chk_sum: {chk_sum} | calc_chk_sum: {calc_chk_sum}")
                    print(f"Yapp CRC-Error: chk_sum: {chk_sum} | calc_chk_sum: {calc_chk_sum}")
                    logger.error(f"Yapp CRC-Error: self.rx_pack_buff {self.rx_pack_buff} | hex: {self.rx_pack_buff.hex()}")
                    print(f"Yapp CRC-Error: self.rx_pack_buff {self.rx_pack_buff} | hex: {self.rx_pack_buff.hex()}")
                    return False    # ABORT ?
            else:
                self.rx_pac_len = pac_len
            return 'DT'
        #  STX   len   (Data)    {if len=0 then data length = 256}
        # [STX] [Len] [Datas] [Checksum]
        self.rx_pac_len = 0
        return False

    def enc_EF(self):
        """ Send_EOF """
        return b'\x03\x01'

    def dec_EF(self):
        """ Send_EOF """
        if len(self.rx_pack_buff) == 2:
            if bytes([self.rx_pack_buff[1]]) == b'\x01':
                self.rx_pac_len = 2
                return 'EF'
        self.rx_pac_len = 0
        return False

    def enc_ET(self):
        """ Send_EOT """
        return b'\x04\x01'

    def dec_ET(self):
        """ Send_EOT """
        if len(self.rx_pack_buff) == 2:
            if bytes([self.rx_pack_buff[1]]) == b'\x01':
                self.rx_pac_len = 2
                return 'ET'
        self.rx_pac_len = 0
        return False

    def enc_NR(self):
        """ Not_Rdy """
        # NAK  len  (Optional Reason in ASCII)
        ret = b'\x15' + NUL
        return ret

    def dec_NR(self):
        """ Not_Rdy """
        # NAK  len  (Optional Reason in ASCII)
        self.rx_pac_len = 2 # TODO !!!
        return 'NR'

    def enc_RE(self, received_length=0):
        """ Resume """
        # [NAK] [Len] [R] [NUL] [Received Length] [NUL] [C] [NUL] (for YappC)
        # [NAK] [Len] [R] [NUL] [Received Length] [NUL] (for Yapp)
        ret = b'R' + NUL + bytes([received_length]) + NUL
        if self.YappC:
            ret += b'C' + NUL
        return self.build_frame(pack_typ=b'\x15', data=ret)

    def dec_RE(self):
        """ Resume """
        # [NAK] [Len] [R] [NUL] [Received Length] [NUL] [C] [NUL] (for YappC)
        # [NAK] [Len] [R] [NUL] [Received Length] [NUL] (for Yapp)
        if self.check_packet_length():
            if len(self.rx_pack_buff) >= 6:
                if self.rx_pack_buff[2] == ord('R'):
                    received_length = self.rx_pack_buff[4]
                    if len(self.rx_pack_buff) > 6:
                        if self.rx_pack_buff[6] == ord('C'):
                            self.YappC = True
                    else:
                        self.YappC = False
                    self.rx_pac_len = received_length
                    return 'RE', received_length
        self.rx_pac_len = 0
        return False

    def enc_CN(self):
        """ Cancel """
        # CAN  len  (Optional Reason in ASCII)
        ret = b'\x18' + NUL
        self.ft_class.abort = True
        self.Done = True
        return ret

    def dec_CN(self):
        """ Cancel """
        # CAN  len  (Optional Reason in ASCII)
        self.rx_pac_len = 2  # TODO !!!
        return 'CN'

    def enc_CA(self):
        """ Can_Ack """
        return b'\x06\x05'

    def dec_CA(self):
        """ Can_Ack """
        self.rx_pac_len = 2
        return 'CA'

    """ Following are for use in Server mode """

    def enc_RI(self):
        """ Rcv_Init """
        # ENQ   02   len   (Filespec requested - wildcard allowed)
        ret = b'\x05\x02'
        return ret

    def dec_RI(self):
        """ Rcv_Init """
        # ENQ   02   len   (Filespec requested - wildcard allowed)
        self.rx_pac_len = 2  # TODO !!!
        return 'RI'

    def enc_TX(self):
        """ Text """
        # DLE   len  (ASCII text for display)  {to send text from server}
        ret = b'\x10' + NUL
        return ret

    def dec_TX(self):
        """ Text """
        # DLE   len  (ASCII text for display)  {to send text from server}
        self.rx_pac_len = 2  # TODO !!!
        return 'TX'

    """ Unimplemented - Reserved for Server Commands """

    def enc_UU(self):
        """ Commands """
        # DLE   len  (ASCII text for display)  {to send text from server}
        # ret = b'\x0503'
        # ret = b'\x0504'
        # ...
        ret = b'\x05\xFF'
        return ret

    def dec_UU(self):
        """ Commands """
        # DLE   len  (ASCII text for display)  {to send text from server}
        # ret = b'\x0503'
        # ret = b'\x0504'
        # ...
        # ret = b'\x05FF'
        self.rx_pac_len = 2  # TODO !!!
        return 'UU'
