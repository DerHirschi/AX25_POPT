import time


class FileTX(object):
    def __init__(self,
                 filename: str,
                 protocol: str,
                 tx_wait: int = 0
                 ):
        self.param_filename = str(filename)
        self.param_protocol = str(protocol)
        self.param_wait = int(tx_wait)

        self.state_tab = {}
        self.state_exec = None
        self.state = 0

        self.e = False
        self.last_tx = 0
        self.data = b''
        self.data_out = b''
        try:
            f = open(self.param_filename, 'rb')
        except PermissionError:
            self.e = True
        else:
            if f is not None:
                self.data = f.read()

        self.change_settings()

    def change_settings(self):
        {
            'Text': self.proto_text,
            'AutoBin': self.dummy,
        }[self.param_protocol]()

    def proto_text(self):
        self.data_out = bytes(self.data)

    def dummy(self):
        pass

    def reset_timer(self):
        if self.param_wait:
            self.last_tx = self.param_wait + time.time()
