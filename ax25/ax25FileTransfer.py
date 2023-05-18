import time

from constant import FT_MODES


def init_crctab():
    """ By: ChatGP """
    crctab = [0] * 256
    bitrmdrs = [0x9188, 0x48C4, 0x2462, 0x1231, 0x8108, 0x4084, 0x2042, 0x1021]

    for n in range(256):
        r = 0
        for m in range(8):
            mask = 0x0080 >> m
            if n & mask:
                r = bitrmdrs[m] ^ r
        crctab[n] = r

    return crctab


def calculate_crc(data, polynomial):
    """ By: ChatGP """
    crc = 0x0000
    for byte in data:
        crc = crc ^ (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ polynomial
            else:
                crc = crc << 1
    return crc & 0xFFFF


class FileTX(object):
    def __init__(self,
                 filename: str,
                 protocol: str == '',
                 connection,
                 tx_wait: int = 0,
                 ):
        self.param_filename = str(filename)
        self.param_protocol = str(protocol)
        self.param_wait = int(tx_wait)
        self.param_PacLen = connection.parm_PacLen
        self.param_MaxFrame = connection.parm_MaxFrame
        self.connection = connection

        self.prot_dict = {
            FT_MODES[0]: TextMODE_TX,
            FT_MODES[1]: AutoBinMODE_TX,
        }
        self.e = False
        self.done = False
        self.last_tx = 0
        self.raw_data = b''
        self.raw_data_len = 0
        self.raw_data_crc = 0
        self.ft_tx_buf = b''
        self.ft_rx_buf = b''
        self.crc_tab = init_crctab()
        try:
            self.process_file(self.param_filename)
        except PermissionError:
            self.e = True
        if not self.raw_data:
            self.e = True
        # self.ft_init()

        if self.param_protocol in self.prot_dict.keys():
            self.class_protocol = self.prot_dict[self.param_protocol](self)
            self.class_protocol.init()
        else:
            self.class_protocol = DefaultMODE_TX(self)

    def process_file(self, filename):
        """ by: Chat GB """
        with open(filename, 'rb') as file:
            buf = file.read()
            crc = 0
            length = len(buf)
            for byte in buf:
                crc = self.crc_tab[(crc >> 8) & 0xFF] ^ ((crc << 8) & 0xFFFF) ^ byte

        self.raw_data = buf
        self.raw_data_len = length
        self.raw_data_crc = crc

    def ft_init(self):
        """
        {
            'Text': self.proto_text,
            'AutoBin': self.dummy,
        }[self.param_protocol]()
        """
        if not self.raw_data:
            self.e = True
            return False
        if self.param_protocol in self.prot_dict.keys():
            self.class_protocol = self.prot_dict[self.param_protocol](self)
            self.class_protocol.init()
            self.e = False
            return True
        self.e = True
        return False

    def ft_can_start(self):
        if not self.connection.tx_buf_rawData and \
                not self.connection.rx_buf_rawData:
            return True
        return False

    def ft_can_stop(self):
        if not self.connection.tx_buf_rawData:
            return True
        return False

    def ft_flush_buff(self):
        self.ft_rx_buf = b''
        self.ft_tx_buf = b''
        self.connection.tx_buf_rawData = b''

    def ft_mode_wait_for_end(self):
        if self.ft_can_stop():
            self.ft_end()

    def ft_end(self):
        self.done = True

    def ft_abort(self):
        self.class_protocol.exec_abort()

    def reset_timer(self):
        if self.param_wait:
            if self.last_tx < time.time():
                self.last_tx = self.param_wait + time.time()
                return True
            return False
        return True

    def ft_crone(self):
        if self.done:
            if self.class_protocol is not None:
                del self.class_protocol
                self.class_protocol = None
            return False
        if not self.e:
            return self.class_protocol.crone_mode()

    def ft_rx(self):
        self.ft_rx_buf += bytes(self.connection.rx_buf_rawData)
        self.connection.rx_buf_rawData = b''
        """
        if not self.e:
            self.class_protocol.crone_mode()
        """

    def send_data(self, data):
        self.connection.send_data(data, file_trans=True)


class DefaultMODE_TX(object):
    def __init__(self, ft_root):
        self.ft_root: FileTX = ft_root
        self.connection = ft_root.connection
        self.ft_root.ft_tx_buf = bytes(self.ft_root.raw_data)
        self.state_tab = {}
        self.header = b''
        self.state = 0
        self.e = True  # No Prot set
        # self.done = False

    def init(self):
        pass

    def crone_mode(self):
        if not self.e:
            if self.state in self.state_tab:
                self.state_tab[self.state]()
                return True
        self.e = True
        return False

    def send_data(self, data):
        self.ft_root.send_data(data=data)

    def exec_abort(self):
        pass


class TextMODE_TX(DefaultMODE_TX):
    def init(self):
        self.state_tab = {
            0: self.mode_wait_for_start,
            1: self.mode_s1,  # W/O Wait / direct to tx_buff
            2: self.mode_s2,  # With wait handling
            3: self.ft_root.ft_mode_wait_for_end,
        }
        self.state = 0
        self.e = False

    def mode_wait_for_start(self):
        if self.ft_root.ft_can_start():
            if self.ft_root.param_wait:
                self.state = 2
            else:
                self.state = 1

    def mode_s1(self):
        self.send_data(bytes(self.ft_root.ft_tx_buf))
        self.ft_root.ft_tx_buf = b''
        self.state = 3
        return True

    def mode_s2(self):
        """ :returns doesn't matter """
        if self.ft_root.reset_timer():
            tmp_len = self.ft_root.param_PacLen * self.ft_root.param_MaxFrame
            if len(self.ft_root.ft_tx_buf) < tmp_len:
                tmp = self.ft_root.ft_tx_buf
                tmp_len = len(tmp)
                # self.ft_root.done = True
                self.state = 3
            else:
                tmp = self.ft_root.ft_tx_buf[:tmp_len]
            self.send_data(tmp)
            self.ft_root.ft_tx_buf = self.ft_root.ft_tx_buf[tmp_len:]
            return True
        return True

    def exec_abort(self):
        self.ft_root.ft_flush_buff()
        # self.send_data(b'#ABORT#\r')
        self.e = True
        self.state = 3

class AutoBinMODE_TX(DefaultMODE_TX):
    """
    Not sure if that is AutoBin or Bin
    Have no Specs.
    Also, it seems WinSTOP has a Bug with CRC in some of his FT Protocols.
    """

    def init(self):
        # self.ft_root.ft_tx_buf = bytes(self.ft_root.data)
        self.state_tab = {
            0: self.mode_wait_for_free_tx_buf,
            1: self.mode_init,
            2: self.mode_init_resp,
            3: self.mode_tx_data,
            4: self.mode_tx_data_steps,
            5: self.mode_tx_end_resp,
            9: self.ft_root.ft_mode_wait_for_end,
        }
        """ Simple Mode .. There seems another Mode but i can't find any specs. """
        # self.header = f'\r#BIN#{self.ft_root.raw_data_len}\r'.encode('ASCII')
        pos = '0' * 8   # Don't know how to decode. Maybe it's a Timestamp but results don't match.
        # pos += '1'
        filename = self.ft_root.param_filename.split('/')[-1].upper()
        filename = filename.replace(' ', '_')
        self.header = f"\r#BIN#{self.ft_root.raw_data_len}#|{int(self.ft_root.raw_data_crc)}#${pos}#{filename}\r".encode('ASCII')
        """ 
        'EXT. MODE'
        Header from WinSTOP: #BIN#5314#|40769#$54E3A0D1#fbb.conf 
        """
        self.state = 0
        self.e = False

    def mode_wait_for_free_tx_buf(self):
        if self.ft_root.ft_can_start():
            self.state = 1

    def mode_init(self):
        self.send_data(self.header)
        self.state = 2

    def mode_init_resp(self):
        if self.ft_root.ft_rx_buf:
            lines = self.ft_root.ft_rx_buf.split(b'\r')
            # print(f"M IRS {lines}")
            self.ft_root.ft_rx_buf = b''
            lines = [x for x in lines if x != b'']
            if lines:
                if lines[-1] == b'#OK#':
                    if self.ft_root.param_wait:
                        self.state = 4
                    else:
                        self.state = 3
                    self.state_tab[self.state]()
                elif b'#ABORT#' in lines:
                    self.exec_abort()

    def mode_tx_data(self):
        if not self.check_abort():
            self.send_data(bytes(self.ft_root.ft_tx_buf))
            self.ft_root.ft_tx_buf = b''
            self.state = 5
            return True

    def mode_tx_data_steps(self):
        if not self.check_abort():
            if self.ft_root.reset_timer():
                tmp_len = self.ft_root.param_PacLen * self.ft_root.param_MaxFrame
                if len(self.ft_root.ft_tx_buf) < tmp_len:
                    tmp = self.ft_root.ft_tx_buf
                    tmp_len = len(tmp)
                    # self.ft_root.done = True
                    self.state = 5
                else:
                    tmp = self.ft_root.ft_tx_buf[:tmp_len]
                self.send_data(tmp)
                self.ft_root.ft_tx_buf = self.ft_root.ft_tx_buf[tmp_len:]

    def mode_tx_end_resp(self):
        self.send_data(f'\rBIN-TX OK #{int(self.ft_root.raw_data_crc)}\r\r'.encode('ASCII'))
        self.state = 9
        """
        if self.ft_root.ft_rx_buf:
            lines = self.ft_root.ft_rx_buf.split(b'\r')
            self.ft_root.ft_rx_buf = b''
            if lines[-1] == b'#OK#':
                # self.send_data(b'BIN-TX OK #25059\r')
                self.send_data(f'BIN-TX OK #{int(self.ft_root.raw_data_crc)}\r'.encode('ASCII'))
                self.state = 9
            elif b'#ABORT#' in lines:
                self.exec_abort()
        """

    def check_abort(self):
        if self.ft_root.ft_rx_buf:
            lines = self.ft_root.ft_rx_buf.split(b'\r')
            self.ft_root.ft_rx_buf = b''
            if b'#ABORT#' in lines:
                self.exec_abort()
                return True
        return False

    def exec_abort(self):
        self.ft_root.ft_flush_buff()
        self.send_data(b'#ABORT#\r')
        self.e = True
        self.state = 9

