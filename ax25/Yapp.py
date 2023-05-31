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
            'Abort': self.abort,
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
                      'CN':   'Abort',
                      'Other':   'Abort',
                      'Timeout': 'Abort',
                  }),
            'SH': ('HD',    # HDR
                   {
                       'RF': 'SD',
                       'RT': 'SD',  # YappC
                       'NR': 'Start/Done',
                       # IF (RESUME)
                       # 'RE': """ Move file position then """ 'SD'
                       'CN':   'Abort',
                       'Other':   'Abort',
                       'Timeout': 'Abort',
                   }),
            'SD': ('DT',    # DATA
                   {
                       # 'CN': 'Abort',
                       False: 'SD',         # Not EOF
                       True:  'SE',         # EOF
                   }),
            'SE': ('EF',    # EOF
                   {
                       # 'AF': 'SH', # TODO     # More Files
                       'AF': 'ST',      # No More Files
                       'CN':   'Abort',
                       'Other':   'Abort',
                       'Timeout': 'Abort'
                   }),
            'ST': ('ET',    # EOT
                   {
                       'AT':      'Start/Done',
                       'CN':   'Abort',
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
                          '': 'Start/Done',
                          'CA': 'Start/Done'
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
                               '':   ('Start/Done', 'Start/Done'),
                               'ET': ('Start/Done', 'Start/Done'),
                               'CN': ('Start/Done', 'Start/Done'),
                           },
            'Abort': {
                          '':   ('CA', 'Start/Done'),
                          'CN': ('CA', 'Start/Done'),
                          'DT': ('CA', 'Start/Done'),
                          'EF': ('CA', 'Start/Done'),
                          'HD': ('CA', 'Start/Done'),
                          'SI': ('CA', 'Start/Done'),
                          'ET': ('CA', 'Start/Done'),
                          'NR': ('CA', 'Start/Done'),
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
        # self.file_size = 0
        self.file_time = '4e4e'  # '12:30:45'
        self.file_date = '4e4e'  # '2023-05-18'
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
            # self.file_size = len(self.ft_class.ft_root.ft_tx_buf)
            self.e = False
            return True
        return False

    def init_rx(self):
        # if self.check_init():
        self.TX = False
        self.state = 'R'
        self.e = False
        return True
        # return False

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
        print(f"Yapp done - self.TX: {self.TX}")
        self.Done = True
        # self.ft_class.close_file()

    def abort(self):
        self.ft_class.close_file()
        print(f"Yapp abort - self.TX: {self.TX}")
        self.Done = True
        # self.e = True
        self.ft_class.abort = True
        self.ft_class.state = 9

    def exec_abort(self):
        # self.ft_class.close_file()
        self.state = 'Abort'
        self.exec_state_tab()

    def check_packet_length(self):
        if len(self.rx_pack_buff) >= 2:
            packet_length = self.rx_pack_buff[1]
            if self.rx_pack_buff.startswith(b'\x02'):
                if packet_length == 0:
                    packet_length = 256
            if len(self.rx_pack_buff[2:]) >= packet_length:
                return packet_length
            else:
                return len(self.rx_pack_buff[2:]) - packet_length
        return -1

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
                        if pack_typ == 'DT':
                            self.ft_class.send_data(pack_data)
                            self.tx_last_pack = pack_data
                            return True
                        if pack_data != self.tx_last_pack and self.param_proto_conn:
                            self.ft_class.send_data(pack_data)
                            self.tx_last_pack = pack_data
                            return True
        return False

    def yapp_rx(self, data_in: b''):
        if data_in:
            self.rx_pack_buff += data_in
        if 1 < len(self.rx_pack_buff) != self.rx_pac_len:
            while len(self.rx_pack_buff) > 1:
                self.rx_pac_len = 0
                res = self.pack_types_dec.get(bytes([self.rx_pack_buff[0]]), False)
                if res:
                    res = res()
                    if res:
                        self.rx_pac_type = res
                        # STATES EXEC
                        res = self.exec_state_tab()
                        if not res:
                            print("Yapp State Tab no results")
                            logger.error("Yapp State Tab no results")
                            logger.error(f"data_in: {data_in}")
                            logger.error(f"rx_pack_buff: {self.rx_pack_buff}")
                            self.e = True
                            self.rx_pack_buff = self.rx_pack_buff[1:]
                            self.exec_abort()
                            return
                        if self.rx_pac_len > 1:
                            self.rx_pack_buff = self.rx_pack_buff[self.rx_pac_len:]
                            self.rx_pac_len = len(self.rx_pack_buff)
                        else:
                            self.rx_pac_len = len(self.rx_pack_buff)
                            return
                    else:
                        print("Yapp pack decoding Error")
                        logger.error("Yapp pack decoding Error")
                        logger.error(f"data_in: {data_in}")
                        logger.error(f"rx_pack_buff: {self.rx_pack_buff}")
                        logger.error(f"state: {self.state}")
                        self.e = True
                        self.rx_pack_buff = self.rx_pack_buff[1:]
                        self.exec_abort()
                        return
                else:
                    print("Yapp pack not Found")
                    #logger.error("Yapp pack not Found")
                    #logger.error(f"data_in: {data_in}")
                    #logger.error(f"rx_pack_buff: {self.rx_pack_buff}")
                    #self.e = True
                    self.rx_pack_buff = self.rx_pack_buff[1:]
                    #self.exec_abort()
                    #return

    def yapp_cron(self):
        # if self.TX:
        self.exec_state_tab()
        # self.ft_class.thread = None
        # return ret

    def exec_state_tab(self):
        # STATES
        if self.TX:
            # Send File
            resp, tmp_state_tab = self.tx_state_table.get(self.state, ('', {}))
            self.state = tmp_state_tab.get(self.rx_pac_type, self.state)
        else:
            # Receive File
            if self.state not in self.rx_state_table:
                print(f"YAPP RX NOT STATE: {self.state}")
                return False
            #print(f"YAPP RX self.rx_pac_type: {self.rx_pac_type}")
            # resp, self.state = self.rx_state_table[self.state].get(self.rx_pac_type, ('CN', 'CW'))
            resp, self.state = self.rx_state_table[self.state].get(self.rx_pac_type, ('', self.state))
            #print(f"YAPP RX STATE: {self.state}")
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
        # return 'RF', 'RD'
        if self.ft_class.e:
            return 'NR', 'Start/Done'
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
        if self.state not in ['RH', 'R']:
            return False
        self.rx_pac_len = 2
        return 'SI'

    def enc_HD(self):
        """ Send_Hdr """
        #  SOH   len  (Filename)  NUL  (File Size in ASCII)  NUL  (Opt)
        # [SOH] [Len] [Filename] [NUL] [File Size] [NUL] [Date] [Time] [NUL]
        ret = self.file_name.encode() + \
              NUL + \
              str(self.ft_class.ft_root.raw_data_len).encode('ASCII') + \
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
        if self.state != 'RH':
            return False

        pac_len = self.check_packet_length()
        self.rx_pac_len = pac_len + 2

        if pac_len > 0:
            data = self.rx_pack_buff[2:self.rx_pac_len]
            print(f"YAPP dec_HD data : {data}")
            data_parts = data.split(NUL)
            tmp = []
            for el in data_parts:
                if el:
                    tmp.append(el)
            data_parts = tmp
            print(f"YAPP dec_HD data_parts : {data_parts}")
            try:
                file_name = data_parts[0].decode('ASCII')
            except UnicodeDecodeError:
                self.rx_pac_len = 0
                return False
            try:
                size = int(data_parts[1])
            except ValueError:
                self.rx_pac_len = 0
                return False
            if len(data_parts) > 2:
                self.ext_header = True
                # self.YappC = True

            self.ft_class.filename = file_name
            self.ft_class.ft_root.param_filename = file_name
            self.ft_class.ft_root.raw_data_len = size
            self.ft_class.open_file()
            if self.ft_class.e:
                self.ft_class.e = False
                self.exec_abort()
            print(f"YAPP dec_HD size : {size}")
            print(f"YAPP dec_HD self.ft_class.e : {self.ft_class.e}")
            # return 'RF', 'RD'
            return 'HD'
        return False

    def enc_DT(self):
        """ Send_Data """
        #  STX   len   (Data)    {if len=0 then data length = 256}
        # [STX] [Len] [Datas] [Checksum]

        # data_len = self.param_PacLen - 2
        data_len = self.ft_class.ft_root.param_PacLen - 2
        if self.YappC or self.Resume:
            data_len -= 2  # TODO on 8 Bit CRC - 1
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
            print(f"Yapp DT data: {data}")
            print(f"Yapp DT CRC: {checksum}")
            return self.build_frame(pack_typ=b'\x02', data=data) + hex(checksum).encode()
        return self.build_frame(pack_typ=b'\x02', data=data)

    def dec_DT(self):
        """ Send_Data """
        # if self.state not in ['RD', 'Abort', 'Start/Done']:
        if self.state not in ['RD']:
            return False
        pac_len = self.check_packet_length()
        if not pac_len:
            return False
        self.rx_pac_len = pac_len + 2
        if pac_len > 0:
            data = self.rx_pack_buff[2:self.rx_pac_len]
            self.ft_class.ft_root.can_rnr = True
            if self.YappC or self.Resume:
                print("YAPP C DT DEC !!!!")
                self.rx_pac_len = pac_len + 2           # TODO + 1 if 8 Bit CRC
                chk_sum = self.rx_pack_buff[pac_len: self.rx_pac_len]
                calc_chk_sum = get_crc(data)
                if chk_sum == calc_chk_sum:     # TODO Maybe Checksum is not right (8 bit like x-modem ?)
                    self.ft_class.write_to_file(data)
                    # print(f"Yapp get data: {data}")
                    return 'DT'
                else:
                    logger.error(f"Yapp CRC-Error: chk_sum: {chk_sum} | calc_chk_sum: {calc_chk_sum}")
                    print(f"Yapp CRC-Error: chk_sum: {chk_sum} | calc_chk_sum: {calc_chk_sum}")
                    logger.error(f"Yapp CRC-Error: self.rx_pack_buff {self.rx_pack_buff} | hex: {self.rx_pack_buff.hex()}")
                    print(f"Yapp CRC-Error: self.rx_pack_buff {self.rx_pack_buff} | hex: {self.rx_pack_buff.hex()}")
                    self.ft_class.write_to_file(data)
                    return 'DT'    # ABORT ?
            else:
                self.ft_class.write_to_file(data)
                return 'DT'
        elif pac_len < 0:
            return 'DT'

        return False

    def enc_EF(self):
        """ Send_EOF """
        return b'\x03\x01'

    def dec_EF(self):
        """ Send_EOF """
        if self.state != 'RD':
            return False
        #if self.ft_class.ft_root.raw_data_len > len(self.ft_class.ft_root.raw_data):
        #    return False
        if len(self.rx_pack_buff) >= 2:
            if bytes([self.rx_pack_buff[1]]) == b'\x01':
                print(f"YAPP EOF !!")
                self.rx_pac_len = 2
                self.ft_class.close_file()
                return 'EF'
        self.rx_pac_len = 0
        return False

    def enc_ET(self):
        """ Send_EOT """
        return b'\x04\x01'

    def dec_ET(self):
        """ Send_EOT """
        if self.state not in ['RH', 'Start/Done']:
            return False
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
        if self.state != 'R':
            return False
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
        print("YAPP enc_CN !!")
        # CAN  len  (Optional Reason in ASCII)
        ret = b'\x18\x00'
        # self.ft_class.send_data(b'\x06\x05')
        self.ft_class.abort = True
        self.Done = True
        return ret

    def dec_CN(self):
        """ Cancel """
        print("YAPP dec_CN !!")
        pac_len = self.check_packet_length()
        if pac_len < 0:
            self.rx_pac_len = pac_len + 2
            return 'CN'
        if b'\x18\x00' in self.rx_pack_buff:
            # CAN  len  (Optional Reason in ASCII)
            print(f"YAPP dec_CN - (b'\x18' + NUL): {self.rx_pack_buff}")
            self.rx_pac_len = 2
            return 'CN'
        #if len(self.rx_pack_buff[2:]) != pac_len:
        #    return False
        tmp = self.rx_pack_buff[2:pac_len + 2]
        # if tmp.isalnum():
        self.rx_pac_len = 2 + pac_len
        print(f"YAPP ABORT REASON: {tmp}")
        print(f"YAPP dec_CN - self.rx_pack_buff: {self.rx_pack_buff}")
        return 'CN'
        #return False

    def enc_CA(self):
        """ Can_Ack """
        return b'\x06\x05'

    def dec_CA(self):
        """ Can_Ack """
        # if self.state not in ['CW', 'Abort', 'Start/Done']:
        if self.state not in ['CW', 'Abort', 'SD']:
            return False
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
