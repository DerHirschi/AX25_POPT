import pickle

import ax25.ax25Connection
import config_station
import main


class DefaultCLI(object):
    cli_name = ''  # DON'T CHANGE !
    c_text = '-= Test C-TEXT =-\r\r'
    bye_text = '73 ...\r'
    prompt = 'TEST-STATION>'
    prefix = '//'

    def __init__(self, connection, stat_cfg=None):
        if stat_cfg is not None:
            # Override with optional Station Config Param
            if hasattr(stat_cfg, 'stat_parm_cli_ctext'):
                if stat_cfg.stat_parm_cli_ctext:
                    self.c_text = stat_cfg.stat_parm_cli_ctext
            if hasattr(stat_cfg, 'stat_parm_cli_bye_text'):
                if stat_cfg.stat_parm_cli_bye_text:
                    self.bye_text = stat_cfg.stat_parm_cli_bye_text
            if hasattr(stat_cfg, 'stat_parm_cli_prompt'):
                if stat_cfg.stat_parm_cli_prompt:
                    self.prompt = stat_cfg.stat_parm_cli_prompt
            self.stat_cfg_index_call = stat_cfg.stat_parm_Call
            self.stat_cfg = stat_cfg
        else:
            self.stat_cfg = config_station.DefaultStation()
            self.stat_cfg_index_call = self.stat_cfg.stat_parm_Call

        self.connection: ax25.ax25Connection.AX25Conn = connection
        # self.channel_index = self.connection.ch_index
        if self.connection.gui is None:
            self.gui = False
        else:
            self.gui = self.connection.gui
        # self.connection = connection
        self.my_call = connection.ax25_out_frame.from_call.call
        self.my_call_str = connection.ax25_out_frame.from_call.call_str
        self.to_call = connection.ax25_out_frame.to_call.call
        self.to_call_str = connection.ax25_out_frame.to_call.call_str
        self.mh_list = connection.mh
        self.state_index = 0
        self.crone_state_index = 0
        self.input = b''
        self.cmd = b''
        self.encoding = 'UTF-8', 'ignore'
        # Crone
        self.cron_state_exec = {
            0: self.cron_s0,
            100: self.cron_s_quit  # QUIT
        }
        # Standard Commands ( GLOBAL )
        self.cmd_exec = {
            'Q': (self.cmd_q, 'Quit'),
            'C': (self.cmd_connect, 'Connect ! funktioniert noch nicht !'),
            'MH': (self.cmd_mh, 'MYHeard Liste'),
            'I': (self.cmd_i, 'Info'),
            'LI': (self.cmd_li, 'Lange Info'),
            'NE': (self.cmd_news, 'NEWS'),
            'NEWS': (self.cmd_news, 'NEWS'),
            'V': (self.cmd_ver, 'Version'),
            'VER': (self.cmd_ver, 'Version'),
            'H': (self.cmd_help, 'Hilfe'),
            '?': (self.cmd_help, 'Hilfe'),
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

    def send_output(self, ret):
        if ret:
            if type(ret) == str:
                # gui_out = str(ret)
                ret = ret.encode(self.encoding[0], self.encoding[1])
            # self.send_2_gui(ret)
            self.connection.tx_buf_rawData += ret
    """
    def send_2_gui(self, data):  
        if data:
            if type(data) != str:
                data = data.decode(self.encoding[0], self.encoding[1])
            # print(data + ' <CLI> ' + str(self.connection.ch_index))
            self.gui.cli_echo(data, self.connection.ch_index)
    """

    def change_cli_state(self, state: int):
        self.state_index = state

    def is_prefix(self):
        if self.prefix:
            if self.input[:len(self.prefix)] == self.prefix.encode(self.encoding[0], self.encoding[1]):
                self.cmd = self.input[len(self.prefix):]
                self.cmd = self.cmd.split(b' ')
                if len(self.cmd) > 1:
                    self.input = self.cmd[1:]
                    print("is_prefix INP: {}".format(self.input))
                else:
                    self.input = b''
                self.cmd = self.cmd[0]
                self.cmd = self.cmd \
                    .decode(self.encoding[0], self.encoding[1]) \
                    .upper() \
                    .replace(' ', '') \
                    .replace('\r', '') \
                    .replace('\n', '')
                # self.input = self.input[len(self.prefix):]
                return True
            else:
                # Message is for User ( Text , Chat )
                return False
        # CMD Input for No User Terminals ( Node ... )
        self.cmd = self.input
        self.cmd = self.cmd.split(b' ')
        if len(self.cmd) > 1:
            self.input = self.cmd[1:]
            print("is_prefix INP: {}".format(self.input))
        else:
            self.input = b''
        self.cmd = self.cmd[0]
        self.cmd = self.cmd \
            .decode(self.encoding[0], self.encoding[1]) \
            .upper() \
            .replace(' ', '') \
            .replace('\r', '') \
            .replace('\n', '')
        return False

    def load_fm_file(self, filename: str):
        try:
            with open(config_station.CFG_data_path +
                      config_station.CFG_usertxt_path +
                      self.stat_cfg_index_call + '/' +
                      filename, 'rb') as inp:
                return pickle.load(inp)
        except FileNotFoundError:
            return ''
        except EOFError:
            return ''

    def exec_cmd(self):
        if self.is_prefix():
            if self.cmd in self.cmd_exec.keys():
                print("INP: {}".format(self.input))
                ret = self.cmd_exec[self.cmd][0]()
                self.cmd = b''
            else:
                ret = 'Dieses Kommando ist dem System nicht bekannt\r'
        # Message is for User ( Text , Chat )
        elif self.prefix:
            ret = ''
        # CMD Input for No User Terminals ( Node ... )
        else:
            if self.cmd in self.cmd_exec.keys():
                print("INP: {}".format(self.input))
                ret = self.cmd_exec[self.cmd][0]()
                self.cmd = b''
                if self.crone_state_index != 100:  # Not Quit
                    ret += self.prompt
            else:
                ret = 'Dieses Kommando ist dem System nicht bekannt\r'
                ret += self.prompt
        self.send_output(ret)
        """
        if ret:
            if type(ret) == str:
                ret = ret.encode(self.encoding[0], self.encoding[1])
            self.connection.tx_buf_rawData += ret
        """

    def cmd_connect(self):
        pass

    def cmd_q(self):  # Quit
        # self.connection: AX25Conn
        # self.connection.tx_buf_rawData += self.bye_text.encode(self.encoding[0], self.encoding[1])
        self.send_output(self.bye_text)
        self.crone_state_index = 100  # Quit State
        return ''

    def cmd_mh(self):
        ret = self.mh_list.mh_out_cli()
        return ret + '\r'

    def cmd_ver(self):
        ret = '\r$$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|\r' \
                '$$  __$$\ $$  __$$\    $$  __$$\|__$$ __|\r' \
                '$$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |\r' \
                '$$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |\r' \
                '$$  ____/ $$ |  $$ |   $$  ____/   $$ |\r' \
                '$$ |      $$ |  $$ |   $$ |        $$ |\r' \
                '$$ |       $$$$$$  |   $$ |        $$ |\r' \
                '\__|yton   \______/ther\__|acket   \__|erminal\r\r'\
                'Version: {}\r\r\r'.format(config_station.VER)
        return ret

    def cmd_i(self):
        ret = self.load_fm_file(self.stat_cfg_index_call + '.itx')
        if ret:
            return ret
        else:
            return self.stat_cfg.stat_parm_cli_itext

    def cmd_li(self):
        ret = self.load_fm_file(self.stat_cfg_index_call + '.litx')
        if ret:
            return ret
        else:
            return self.stat_cfg.stat_parm_cli_longitext

    def cmd_news(self):
        ret = self.load_fm_file(self.stat_cfg_index_call + '.atx')
        if ret:
            return ret
        else:
            return self.stat_cfg.stat_parm_cli_akttext

    def cmd_help(self):
        ret = '\r   < Hilfe >\r'
        for k in self.cmd_exec.keys():
            ret += '\r {:3} > {}'.format(k, self.cmd_exec[k][1])
        ret += '\r\r\r'
        return ret

    def cli_exec(self, inp=b''):
        if not self.connection.is_link:
            # self.send_2_gui(inp)
            self.input = inp
            _ret = self.state_exec[self.state_index]()
            self.send_output(_ret)
            """
            if ret:
                if type(ret) == str:
                    ret = ret.encode(self.encoding[0], self.encoding[1])
                self.connection.tx_buf_rawData += ret
           """

    def cli_cron(self):
        """ Global Crone Tasks """
        if not self.connection.is_link:
            self.cli_state_crone()

    def cli_state_crone(self):
        """ State Crone Tasks """
        ret = self.cron_state_exec[self.crone_state_index]()
        self.send_output(ret)
        # self.send_output('TEST')
        # self.send_output(b'TEST bytes')
        """
        if ret:
            if type(ret) == str:
                ret = ret.encode(self.encoding[0], self.encoding[1])
            self.connection.tx_buf_rawData += ret
        """

    def s0(self):  # C-Text
        self.build_prompt()
        self.state_index = 1
        if self.prefix:
            return self.c_text
        else:
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
    cli_name = 'NODE'  # DON'T CHANGE !
    c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    bye_text = '73 ...\r'
    prompt = 'TEST-STATION-NODE-CLI>'
    prefix = ''

    # Extra CMDs for this CLI

    def init(self):
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {
            2: self.s2
        }

    def s2(self):
        return self.bye_text


class UserCLI(DefaultCLI):
    cli_name = 'USER'   # DON'T CHANGE !
    c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    bye_text = '73 ...\r'
    prompt = 'TEST-STATION-User-CLI>'
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


class NoneCLI(DefaultCLI):
    """ ? To Disable CLI / Remote ? """
    cli_name = 'NO-CLI'   # DON'T CHANGE !

    def exec_cmd(self):
        pass

    def cli_cron(self):
        pass
