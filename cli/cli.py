import datetime
import pickle
import logging

import ax25.ax25Connection
import config_station
from string_tab import STR_TABLE
from fnc.ax25_fnc import validate_call
from ax25.ax25Error import AX25EncodingERROR
from UserDB.UserDB import Client

logger = logging.getLogger(__name__)


class DefaultCLI(object):
    cli_name = ''  # DON'T CHANGE !
    c_text = '-= Test C-TEXT =-\r\r'
    bye_text = '73 ...\r'
    prompt = ''
    prefix = b'//'

    def __init__(self, connection):
        stat_cfg = connection.stat_cfg
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
        self.port_handler = self.connection.port_handler
        self.own_port = self.connection.own_port
        # self.channel_index = self.connection.ch_index
        if self.connection.gui is None:
            self.gui = False
        else:
            self.gui = self.connection.gui
        # self.connection = connection
        # self.my_call = self.connection.ax25_out_frame.from_call.call
        self.my_call_str = self.connection.my_call_str
        # self.to_call = self.connection.ax25_out_frame.to_call.call
        self.to_call_str = self.connection.to_call_str
        self.mh_list = self.connection.mh
        self.user_db = self.connection.user_db
        self.user_db_ent: Client = self.connection.user_db_ent
        if self.user_db_ent.CText:
            self.c_text = str(self.user_db_ent.CText)
        self.c_text = self.c_text.replace('\n', '\r')
        self.bye_text = self.bye_text.replace('\n', '\r')
        self.prompt = self.prompt.replace('\n', '\r')

        self.state_index = 0
        self.crone_state_index = 0
        self.input = b''
        self.raw_input = b''
        self.cmd = b''
        self.last_line = b''
        self.parameter: [bytes] = []
        self.encoding = 'UTF-8', 'ignore'
        # Crone
        self.cron_state_exec = {
            0: self.cron_s0,        # No CMDs / Doing nothing
            100: self.cron_s_quit  # QUIT
        }
        # Standard Commands ( GLOBAL )
        self.commands = {
            b'QUIT': (self.cmd_q, 'Quit'),
            b'CONNECT': (self.cmd_connect, 'Connect'),
            b'PORT': (self.cmd_port, 'Ports'),
            b'MH': (self.cmd_mh, 'MYHeard Liste'),
            b'INFO': (self.cmd_i, 'Info'),
            b'LINFO': (self.cmd_li, 'Lange Info'),
            b'NEWS': (self.cmd_news, 'NEWS'),
            b'ECHO': (self.cmd_echo, 'Echo'),
            b'VERSION': (self.cmd_ver, 'Version'),
            b'HELP': (self.cmd_help, STR_TABLE['help'][self.connection.cli_language]),
            b'?': (self.cmd_help, ''),
            b'NAME': (self.cmd_set_name, STR_TABLE['cmd_help_set_name'][self.connection.cli_language]),
            b'QTH': (self.cmd_set_qth, STR_TABLE['cmd_help_set_qth'][self.connection.cli_language]),
            b'LOC': (self.cmd_set_loc, STR_TABLE['cmd_help_set_loc'][self.connection.cli_language]),
            b'ZIP': (self.cmd_set_zip, STR_TABLE['cmd_help_set_zip'][self.connection.cli_language]),
            b'PRMAIL': (self.cmd_set_pr_mail, STR_TABLE['cmd_help_set_prmail'][self.connection.cli_language]),
            b'EMAIL': (self.cmd_set_e_mail, STR_TABLE['cmd_help_set_email'][self.connection.cli_language]),
            b'WEB': (self.cmd_set_http, STR_TABLE['cmd_help_set_http'][self.connection.cli_language]),
            b'USER': (self.cmd_user_db_detail, STR_TABLE['cmd_help_user_db'][self.connection.cli_language]),
        }

        self.str_cmd_exec = {
            b'#REQUESTNAME:+++#': self.str_cmd_req_name,
            b'#REQUESTNAME:++-#': self.str_cmd_req_name,
            b'#REQUESTNAME:+--#': self.str_cmd_req_name,
            b'#REQUESTNAME:+-+#': self.str_cmd_req_name,
            b'#REQUESTNAME:--+#': self.str_cmd_req_name,
            b'#REQUESTNAME:-++#': self.str_cmd_req_name,
        }

        self.state_exec = {
            0: self.s0,  # C-Text
            1: self.s1,  # Cmd Handler
            2: self.s2,  # Nothing / no remote
        }
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {}
        # self.init()
        self.cron_state_exec.update(self.cron_state_exec_ext)
        self.commands.update(self.cmd_exec_ext)
        self.state_exec.update(self.state_exec_ext)

    """
    def init(self):
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {}
    """

    def build_prompt(self):
        self.prompt = '\r{}<>{}'.format(
            str(self.my_call_str).replace('\r', ''),
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

    """
    def get_parameter(self):
        param = self.input
        self.parameter = self.input
    """

    def is_prefix(self):
        if self.prefix:
            # print(self.input)
            self.input = self.input.replace(b'\n', b'\r')
            self.input = self.input.split(b'\r')[0]
            """
            while self.input[:1] in [b'\r', b'\n']:
                self.input = self.input[1:]
                if not self.input:
                    return False
            """
            # print(self.input)
            """
            if type(self.prefix) == str:    # Fix for old CFG Files
                self.prefix = self.prefix.encode('UTF-8', 'ignore')
            """
            # print(self.prefix)
            if self.input[:len(self.prefix)] == self.prefix:
                # print(self.input)
                self.parameter = []
                cmd = self.input[len(self.prefix):]
                cmd = cmd.split(b' ')
                if len(cmd) > 1:
                    self.input = cmd[1:]
                    self.parameter = cmd[1:]
                    # print("input INP: {}".format(self.input))
                    # print("parameter INP: {}".format(self.parameter))
                else:
                    self.input = b''

                cmd = cmd[0]
                self.cmd = cmd \
                    .upper() \
                    .replace(b' ', b'') \
                    .replace(b'\r', b'') \
                    .replace(b'\n', b'')
                # self.input = self.input[len(self.prefix):]
                return True
            else:
                # Message is for User ( Text , Chat )
                return False
        # CMD Input for No User Terminals ( Node ... )
        self.parameter = []
        cmd = self.input
        cmd = cmd.split(b' ')
        if len(cmd) > 1:
            self.input = cmd[1:]
            self.parameter = cmd[1:]
            # print("input INP: {}".format(self.input))
            # print("parameter INP: {}".format(self.parameter))
        else:
            self.input = b''
        cmd = cmd[0]
        self.cmd = cmd \
            .upper() \
            .replace(b'\r', b'') \
            .replace(b'\n', b'')
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

    def find_cmd(self):
        cmds = list(self.commands.keys())
        treffer = []
        for cmd in cmds:
            if self.cmd == cmd[:len(self.cmd)]:
                treffer.append(cmd)
        if not treffer:
            return '\r # Dieses Kommando ist dem System nicht bekannt\r'
        """
        if len(treffer) > 1:
            ret = '\r # Ungenaue Eingabe, mehrere Kommandos erkannt:\r'
            ret += ' #\r'
            for cmd_str in treffer:
                ret += f" # {cmd_str.decode('UTF-8')}\r"
            return ret
        """
        self.cmd = b''
        return self.commands[treffer[0]][0]()

    def exec_cmd(self):
        # TODO Cleanup
        if self.is_prefix():
            ret = self.find_cmd()
        # Message is for User ( Text , Chat )
        elif self.prefix:
            ret = ''
        # CMD Input for No User Terminals ( Node ... )
        else:
            ret = self.find_cmd()
            if self.crone_state_index != 100 and self.state_index != 2:  # Not Quit
                if ret is None:
                    ret = ''
            ret += self.prompt

        self.send_output(ret)

    def send_prompt(self):
        self.send_output(self.prompt)

    def decode_param(self):
        tmp = []
        for el in self.parameter:
            tmp.append(el.decode('ASCII', 'ignore').replace('\r', '').replace('\n', ''))
        self.parameter = list(tmp)

    def cmd_connect(self):  # DUMMY
        # print(f'cmd_connect() param: {self.parameter}')
        self.decode_param()
        # print(f'cmd_connect() param.decode: {self.parameter}')

        if not self.parameter:
            ret = '\r # Bitte Call eingeben..\r'
            return ret

        dest_call = validate_call(self.parameter[0])
        if not dest_call:
            ret = '\r # Ungültiger Ziel Call..\r'
            return ret

        # port_id = self.own_port.port_id
        port_id = -1
        vias = [self.connection.my_call_str]
        if len(self.parameter) > 1:
            if self.parameter[-1].isdigit():
                port_id = int(self.parameter[-1])
                if port_id not in self.port_handler.ax25_ports.keys():
                    ret = '\r # Ungültiger Port..\r'
                    return ret
            if self != -1:
                parm = self.parameter[1:-1]
            else:
                parm = self.parameter[1:]

            for call in parm:
                try:
                    tmp_call = validate_call(call)
                except AX25EncodingERROR:
                    break
                if tmp_call:
                    vias.append(tmp_call)
                else:
                    break

        conn = self.port_handler.new_outgoing_connection(
            own_call=self.connection.to_call_str,
            dest_call=dest_call,
            via_calls=vias,
            port_id=port_id,
            link_conn=self.connection,
            # link_call=str(self.connection.my_call_str)
        )
        if conn[0]:
            self.state_index = 2
            return conn[1]
        return '\r*** Link Busy\r'

    def cmd_echo(self):  # Quit
        ret = ''
        for el in self.parameter:
            ret += el.decode(self.encoding[0], self.encoding[1]) + ' '
        return ret[:-1]

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
              '\__|yton   \______/ther\__|acket   \__|erminal\r\r' \
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

    def cmd_user_db_detail(self):
        if not self.parameter:
            header = "\r" \
                     "| USER-DB\r" \
                     "|-------------------\r"
            ent_ret = ""
            for call in self.user_db.db.keys():
                ent_ret += f"| {call}\r"
            ent_ret += "|-------------------\r\r"
            return header + ent_ret
        else:
            call_str = self.parameter[0].decode(self.encoding[0], self.encoding[1])
            call_str = validate_call(call_str)

            if call_str:
                if call_str in self.user_db.db.keys():
                    header = "\r" \
                             f"| USER-DB: {call_str}\r" \
                             "|-------------------\r"
                    ent = self.user_db.db[call_str]
                    ent_ret = ""
                    for att in dir(ent):
                        if '__' not in att and \
                                att not in [
                                    'call_str',
                                    'is_new',
                                ]:
                            if getattr(ent, att):
                                ent_ret += f"| {att.ljust(10)}: {getattr(ent, att)}\r"

                    ent_ret += "|-------------------\r\r"
                    return header + ent_ret

            return "\r" \
                   f"{STR_TABLE['cli_no_user_db_ent'][self.connection.cli_language]}" \
                   "\r"

    def cmd_set_name(self):
        if self.user_db_ent:
            self.user_db_ent.Name = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_name_set'][self.connection.cli_language]}: {self.user_db_ent.Name}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_name NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_qth(self):
        if self.user_db_ent:
            self.user_db_ent.QTH = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_qth_set'][self.connection.cli_language]}: {self.user_db_ent.QTH}" \
                   "\r"

        logger.error("User-DB Error. cli_qth_set NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_loc(self):
        if self.user_db_ent:
            self.user_db_ent.LOC = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_loc_set'][self.connection.cli_language]}: {self.user_db_ent.LOC}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_loc NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_zip(self):
        if self.user_db_ent:
            self.user_db_ent.ZIP = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_zip_set'][self.connection.cli_language]}: {self.user_db_ent.ZIP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_zip NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_pr_mail(self):
        if self.user_db_ent:
            self.user_db_ent.PRmail = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_prmail_set'][self.connection.cli_language]}: {self.user_db_ent.PRmail}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_pr_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_e_mail(self):
        if self.user_db_ent:
            self.user_db_ent.Email = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_email_set'][self.connection.cli_language]}: {self.user_db_ent.Email}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_e_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_http(self):
        if self.user_db_ent:
            self.user_db_ent.HTTP = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_http_set'][self.connection.cli_language]}: {self.user_db_ent.HTTP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_http NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_port(self):
        ret = f"\r   < {STR_TABLE['port_overview'][self.connection.cli_language]} >\r\r"
        ret += "-#-Name------Stations---------\r"
        for port_id in self.port_handler.ax25_ports.keys():
            port = self.port_handler.ax25_ports[port_id]
            name = str(port.portname).ljust(7)
            stations = str(port.my_stations)\
                .replace('[','') \
                .replace(']','') \
                .replace(',','') \
                .replace("'", "")
            ret += f" {port_id} {name}   {stations}\r"
        ret += '\r'
        return ret

    def cmd_help(self):
        ret = f"\r   < {STR_TABLE['help'][self.connection.cli_language]} >\r"
        """
        c = 1
        new_cmd = {}

        treffer = list(self.commands.keys())
        tmp = []
        old_cmds = list(self.commands.keys())
        while treffer:
            print(treffer)
            for cmd in list(treffer):
                if cmd[:c] not in tmp:
                    treffer.remove(cmd)
                    tmp.append(cmd[:c])
                else:
                    treffer.append(cmd)
                    tmp.remove(cmd[:c])
            for el in list(old_cmds):
                if el not in treffer:
                    new_cmd[el] = f"({el[:c].decode('UTF-8')}){el[c:].decode('UTF-8')}"
                    old_cmds.remove(el)

            # treffer = []
            tmp = []
            c += 1
        """
        # for k in new_cmd.keys():
        for k in list(self.commands.keys()):
            if self.commands[k][1]:
                ret += '\r {}{:10} = {}'.format(self.prefix.decode('UTF-8', 'ignore'),
                                               k.decode('UTF-8', 'ignore'),
                                               self.commands[k][1])
        ret += '\r\r'
        return ret

    def str_cmd_req_name(self):
        # print("REQ NAME")
        name = self.connection.stat_cfg.stat_parm_Name
        qth = self.connection.stat_cfg.stat_parm_QTH
        loc = self.connection.stat_cfg.stat_parm_LOC
        if name:
            name = f'#NAM# {name}\r'
        if qth:
            qth = f'#QTH# {qth}\r'
        if loc:
            loc = f'#LOC# {loc}\r'

        tmp = self.cmd.split(b':')[1]
        tmp = tmp[:-1]
        cmd_dict = {
            b'+++': name + qth + loc,
            b'++-': name + qth,
            b'+--': name,
            b'+-+': name + loc,
            b'--+': loc,
            b'-++': qth + loc,
        }
        if tmp in cmd_dict.keys():
            return cmd_dict[tmp]
        return ''

    def cli_exec(self, inp=b''):
        if not self.connection.is_link:
            self.raw_input = bytes(inp)
            _ret = self.state_exec[self.state_index]()
            if _ret:
                _ret = _ret.replace('\n', '\r')
                self.send_output(_ret)

    def cli_cron(self):
        """ Global Crone Tasks """
        if not self.connection.is_link:
            self.cli_state_crone()

    def cli_state_crone(self):
        """ State Crone Tasks """
        ret = self.cron_state_exec[self.crone_state_index]()
        self.send_output(ret)

    def s0(self):  # C-Text
        # self.build_prompt()
        self.state_index = 1
        if self.prefix:
            return self.c_text
        else:
            return self.c_text + self.prompt

    def s1(self):
        if type(self.prefix) == str:  # Fix for old CFG Files
            self.prefix = self.prefix.encode('UTF-8', 'ignore')
        self.input = self.last_line + self.raw_input
        self.exec_cmd()
        ########################
        # Check String Commands
        inp_lines = self.last_line + self.raw_input
        inp_lines = inp_lines.replace(b'\n', b'\r')
        inp_lines = inp_lines.split(b'\r')
        for li in inp_lines:
            # for k in list(self.str_cmd_exec.keys()):
            # if li in k:
            if li in self.str_cmd_exec.keys():
                self.cmd = li
                # self.parameter
                _ret = self.str_cmd_exec[li]()
                self.cmd = b''
                self.send_output(_ret)
        self.last_line = inp_lines[-1]
        self.raw_input = b''
        return ''

    def s2(self):
        return ""

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
    prompt = 'PoPT-NODE>'
    prefix = b''

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
    cli_name = 'USER'  # DON'T CHANGE !
    c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    bye_text = '73 ...\r'
    prompt = 'TEST-STATION-User-CLI>'
    prefix = b'//'

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
    cli_name = 'NO-CLI'  # DON'T CHANGE !

    def exec_cmd(self):
        pass

    def cli_cron(self):
        pass
