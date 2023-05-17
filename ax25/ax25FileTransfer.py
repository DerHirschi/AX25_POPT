import time


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
            'Text': TextMODE_TX,
        }
        self.e = False
        self.done = False
        self.last_tx = 0
        self.data = b''
        self.data_tx_buf = b''
        try:
            f = open(self.param_filename, 'rb')
        except PermissionError:
            self.e = True
        else:
            if f is not None:
                self.data = f.read()
        if not self.data:
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
        if not self.data:
            self.e = True
            return False
        if self.param_protocol in self.prot_dict.keys():
            self.class_protocol = self.prot_dict[self.param_protocol](self)
            self.class_protocol.init()
            self.e = False
            return True
        self.e = True
        return False

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


class DefaultMODE_TX(object):
    def __init__(self, ft_root):
        self.ft_root = ft_root
        self.connection = ft_root.connection
        self.state_tab = {}
        self.state = 0
        self.e = True   # No Prot set
        #self.done = False

    def init(self):
        pass

    def mode_wait_for_free_tx_buf(self):
        pass

    def crone_mode(self):
        if not self.e:
            if self.state in self.state_tab:
                self.state_tab[self.state]()
                return True
        self.e = True
        return False


class TextMODE_TX(DefaultMODE_TX):
    def init(self):
        self.ft_root.data_tx_buf = bytes(self.ft_root.data)
        self.state_tab = {
            0: self.mode_wait_for_free_tx_buf,
            1: self.mode_s1,    # W/O Wait / direct to tx_buff
            2: self.mode_s2     # With wait handling
        }

        self.state = 0
        self.e = False

    def mode_wait_for_free_tx_buf(self):
        if not self.connection.tx_buf_rawData:
            if self.ft_root.param_wait:
                self.state = 2
            else:
                self.state = 1

    def mode_s1(self):
        # ret = bytes(self.ft_root.data_out)
        self.connection.send_data(bytes(self.ft_root.data_tx_buf), file_trans=True)
        self.ft_root.data_tx_buf = b''
        self.ft_root.done = True
        return True

    def mode_s2(self):
        """ :returns doesn't matter """
        if self.ft_root.reset_timer():
            tmp_len = self.ft_root.param_PacLen * self.ft_root.param_MaxFrame
            if len(self.ft_root.data_tx_buf) < tmp_len:
                tmp = self.ft_root.data_tx_buf
                tmp_len = len(tmp)
                self.ft_root.done = True
            else:
                tmp = self.ft_root.data_tx_buf[:tmp_len]
            self.connection.send_data(tmp, file_trans=True)
            self.ft_root.data_tx_buf = self.ft_root.data_tx_buf[tmp_len:]
            return True
        return True
