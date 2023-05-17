import time

from constant import FT_MODES


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
        self.ft_tx_buf = b''
        self.ft_rx_buf = b''
        try:
            f = open(self.param_filename, 'rb')
        except PermissionError:
            self.e = True
        else:
            if f is not None:
                self.raw_data = f.read()
        if not self.raw_data:
            self.e = True
        # self.ft_init()

        if self.param_protocol in self.prot_dict.keys():
            self.class_protocol = self.prot_dict[self.param_protocol](self)
            self.class_protocol.init()
        else:
            self.class_protocol = DefaultMODE_TX(self)

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

    def ft_end(self):
        self.done = True

    def ft_mode_wait_for_end(self):
        if self.ft_can_stop():
            self.ft_end()

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
        self.ft_root = ft_root
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
        # ret = bytes(self.ft_root.data_out)
        self.send_data(bytes(self.ft_root.ft_tx_buf))
        self.ft_root.ft_tx_buf = b''
        # self.ft_root.done = True
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
            # 1: self.mode_s1,    # W/O Wait / direct to tx_buff
            # 2: self.mode_s2     # With wait handling
        }
        """ Simple Mode .. There seems another Mode but i can't find any specs. """
        self.header = f'\r#BIN#{len(self.ft_root.ft_tx_buf)}\r'.encode('ASCII')
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
        resp = b'#OK#'
        if self.connection.rx_buf_rawData:
            pass
