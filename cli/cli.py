# import ax25.ax25Statistics


class DefaultCLI(object):
    c_text = '-= Test C-TEXT =-\r\r'
    bye_text = '73 ...\r'
    prompt = 'TEST-STATION>'
    prefix = '//'

    def __init__(self, connection):
        # self.connection: AX25Conn
        self.connection = connection
        self.my_call = connection.ax25_out_frame.from_call.call
        self.my_call_str = connection.ax25_out_frame.from_call.call_str
        self.to_call = connection.ax25_out_frame.to_call.call
        self.to_call_str = connection.ax25_out_frame.to_call.call_str
        self.mh_list = connection.mh
        self.state_index = 0
        self.crone_state_index = 0
        self.input = b''
        self.encoding = 'UTF-8', 'ignore'
        # Crone
        self.cron_state_exec = {
            0: self.cron_s0,
            100: self.cron_s_quit   # QUIT
        }
        # Standard Commands ( GLOBAL )
        self.cmd_exec = {
            'Q': (self.cmd_q, 'Quit'),
            'MH': (self.cmd_mh, 'MYHeard List'),
        }
        self.state_exec = {
            0: self.s0,  # C-Text
            1: self.s1,  # Cmd Handler
        }
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {}
        self.init()
        self.cron_state_exec.update(self.cron_state_exec_ext)
        self.cmd_exec.update(self.cmd_exec_ext)
        self.state_exec.update(self.state_exec_ext)

    def init(self):
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {}

    def build_prompt(self):
        self.prompt = '\r{}<>{}'.format(
            str(self.my_call).replace('\r', ''),
            str(self.prompt).replace('\r', ''))

    def change_cli_state(self, state: int):
        self.state_index = state

    def is_prefix(self):
        if self.prefix:
            if self.input[:len(self.prefix)] == self.prefix.encode(self.encoding[0], self.encoding[1]):
                self.input = self.input[len(self.prefix):] \
                    .decode(self.encoding[0], self.encoding[1]) \
                    .upper() \
                    .replace(' ', '') \
                    .replace('\r', '') \
                    .replace('\n', '')
                return True
            else:
                # Message is for User ( Text , Chat )
                return False
        # CMD Input for No User Terminals ( Node ... )
        self.input = self.input \
            .decode(self.encoding[0], self.encoding[1]) \
            .upper() \
            .replace(' ', '') \
            .replace('\r', '') \
            .replace('\n', '')
        return False

    def exec_cmd(self):
        if self.is_prefix():
            if self.input in self.cmd_exec.keys():
                ret = self.cmd_exec[self.input][0]()
            else:
                ret = 'Dieses Kommando ist dem System nicht bekannt\r'
        # Message is for User ( Text , Chat )
        elif self.prefix:
            ret = ''
        # CMD Input for No User Terminals ( Node ... )
        else:
            if self.input in self.cmd_exec.keys():
                ret = self.cmd_exec[self.input][0]()
                if self.crone_state_index != 100:   # Not Quit
                    ret += self.prompt
            else:
                ret = 'Dieses Kommando ist dem System nicht bekannt\r'
                ret += self.prompt
        if ret:
            if type(ret) == str:
                ret = ret.encode(self.encoding[0], self.encoding[1])
            self.connection.tx_buf_rawData += ret

    def cmd_q(self):  # Quit
        # self.connection: AX25Conn
        self.connection.tx_buf_rawData += self.bye_text.encode(self.encoding[0], self.encoding[1])
        self.crone_state_index = 100  # Quit State
        return ''

    def cmd_mh(self):
        return self.mh_list.mh_out_cli()

    def cli_exec(self, inp=b''):
        self.input = inp
        ret = self.state_exec[self.state_index]()
        if ret:
            if type(ret) == str:
                ret = ret.encode(self.encoding[0], self.encoding[1])
            self.connection.tx_buf_rawData += ret

    def cli_cron(self):
        """ Global Crone Tasks """
        self.cli_state_crone()

    def cli_state_crone(self):
        """ State Crone Tasks """
        ret = self.cron_state_exec[self.crone_state_index]()
        if ret:
            if type(ret) == str:
                ret = ret.encode(self.encoding[0], self.encoding[1])
            self.connection.tx_buf_rawData += ret

    def s0(self):  # C-Text
        self.build_prompt()
        self.state_index = 1
        return self.c_text + self.prompt

    def s1(self):
        self.exec_cmd()
        return ''

    def cron_s0(self):
        """ Dummy for doing nothing """
        return ''

    def cron_s_quit(self):
        # self.connection: AX25Conn
        if not self.connection.tx_buf_rawData and \
                not self.connection.tx_buf_unACK and \
                not self.connection.tx_buf_2send:
            if self.connection.zustand_exec.stat_index not in [0, 1, 4]:
                self.connection.zustand_exec.change_state(4)


class NodeCLI(DefaultCLI):
    c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    bye_text = '73 ...\r'
    prompt = 'TEST-STATION-2>'
    prefix = '//'
    # Extra CMDs for this CLI

    def init(self):
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {
            2: self.s2
        }

    def s2(self):
        return self.bye_text
