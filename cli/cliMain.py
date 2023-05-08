from datetime import datetime
import pickle
import logging

import ax25.ax25Connection
import config_station
from cli.cliStationIdent import get_station_id_obj
from fnc.str_fnc import get_time_delta, find_decoding
from string_tab import STR_TABLE
from fnc.ax25_fnc import validate_call
from ax25.ax25Error import AX25EncodingERROR
from UserDB.UserDBmain import Client

logger = logging.getLogger(__name__)


class DefaultCLI(object):
    cli_name = ''  # DON'T CHANGE!
    c_text = '-= Test C-TEXT =-\r\r'
    bye_text = '73 ...\r'
    prompt = ''
    prefix = b'//'

    def __init__(self, connection):
        print("CLI-INIT")
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
        self.my_call_str = self.connection.my_call_str
        self.to_call_str = self.connection.to_call_str
        self.mh_list = self.connection.mh
        self.user_db = self.connection.user_db
        self.user_db_ent: Client = self.connection.user_db_ent
        self.encoding = 'UTF-8', 'ignore'
        self.stat_identifier_str = ''
        if self.user_db_ent:
            self.encoding = self.user_db_ent.Encoding, 'ignore'
            self.stat_identifier_str = self.user_db_ent.Software
            if self.user_db_ent.CText:
                self.c_text = str(self.user_db_ent.CText)

        self.stat_identifier = get_station_id_obj(self.stat_identifier_str)

        self.c_text = self.c_text.replace('\n', '\r')
        self.bye_text = self.bye_text.replace('\n', '\r')
        self.prompt = self.prompt.replace('\n', '').replace('\r', '')

        self.time_start = datetime.now()

        self.state_index = 0
        self.crone_state_index = 0
        self.input = b''
        self.raw_input = b''
        self.cmd = b''
        self.last_line = b''
        self.parameter = []
        # Crone
        self.cron_state_exec = {
            0: self.cron_s0,        # No CMDs / Doing nothing
            100: self.cron_s_quit   # QUIT
        }
        # Standard Commands ( GLOBAL )
        self.commands = {
            b'QUIT': (self.cmd_q, 'Quit'),
            b'BYE': (self.cmd_q, ''),
            b'CONNECT': (self.cmd_connect, 'Connect'),
            b'PORT': (self.cmd_port, 'Ports'),
            b'MH': (self.cmd_mh, 'MYHeard Liste'),
            b'INFO': (self.cmd_i, 'Info'),
            b'LINFO': (self.cmd_li, 'Lange Info'),
            b'LCSTATUS': (self.cmd_lcstatus, STR_TABLE['cmd_help_lcstatus'][self.connection.cli_language]),
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
            b'UMLAUT': (self.cmd_umlaut, STR_TABLE['auto_text_encoding'][self.connection.cli_language]),
        }

        self.str_cmd_exec = {
            b'#REQUESTNAME:': self.str_cmd_req_name,
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
        if type(self.prefix) == str:  # Fix for old CFG Files
            self.prefix = self.prefix.encode(self.encoding[0], self.encoding[1])

    """
    def init(self):
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {}
    """

    def build_prompt(self):
        pass
        self.prompt = f"\r<{self.prompt}>{self.my_call_str}>"
        # self.prompt = self.prompt

    def get_ts_prompt(self):
        return f"\r{self.my_call_str} ({datetime.now().strftime('%H:%M:%S')})>"

    def send_output(self, ret):
        if ret:
            if type(ret) == str:
                # gui_out = str(ret)
                ret = ret.encode(self.encoding[0], self.encoding[1])
                ret = ret.replace(b'\n', b'\r')
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
        # TODO Cleanup !!!!
        # print(self.input)
        if self.prefix:
            self.input = self.input.replace(b'\n', b'\r')
            # self.input = self.input.split(b'\r')[0]
            self.input = self.input.split(b'\r')
            # print(self.input)
            while self.input:
                if self.input[0]:
                    break
                else:
                    self.input = self.input[1:]
            if not self.input:
                return False
            self.input = self.input[0]

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

    def set_user_db_software_id(self):
        if self.user_db_ent:
            self.user_db_ent.software_str = str(self.stat_identifier.id_str)
            self.user_db_ent.Software = str(self.stat_identifier.software) + '-' + str(self.stat_identifier.version)
            if not self.user_db_ent.TYP:
                self.user_db_ent.TYP = str(self.stat_identifier.typ)

    def find_stat_identifier(self):
        # print(f"find_stat_identifier self.stat_identifier: {self.stat_identifier}")
        if self.stat_identifier is None:
            inp_lines = self.last_line + self.raw_input
            inp_lines = inp_lines.replace(b'\n', b'\r')
            inp_lines = inp_lines.decode(self.encoding[0], 'ignore')
            inp_lines = inp_lines.split('\r')
            # print(f"find_stat_identifier inp_lines: {inp_lines}")
            for li in inp_lines:
                temp_stat_identifier = get_station_id_obj(li)
                if temp_stat_identifier is not None:
                    """
                    if self.stat_identifier is None:
                        self.stat_identifier = temp_stat_identifier
                        self.set_user_db_software_id()
                        return
                    """
                    """
                    if hasattr(self.stat_identifier, 'id_str'):
                        if self.stat_identifier.id_str != temp_stat_identifier.id_str:
                            self.stat_identifier = temp_stat_identifier
                            self.set_user_db_software_id()
                            return
                    """
                    self.stat_identifier = temp_stat_identifier
                    self.set_user_db_software_id()
                    return

    def find_cmd(self):
        if self.cmd:
            cmds = list(self.commands.keys())
            treffer = []
            for cmd in cmds:
                if self.cmd == cmd[:len(self.cmd)]:
                    treffer.append(cmd)
            if not treffer:
                return f"\r # {STR_TABLE['cmd_not_known'][self.connection.cli_language]}\r"
            self.cmd = b''
            ret = self.commands[treffer[0]][0]()
            if ret is None:
                return ''
            return ret

        return f"\r # {STR_TABLE['cmd_not_known'][self.connection.cli_language]}\r"

    def exec_cmd(self):
        if self.is_prefix():
            return self.find_cmd()
        # Message is for User ( Text , Chat )
        if self.prefix:
            return ''
        # CMD Input for No User Terminals ( Node ... )
        ret = self.find_cmd()
        if self.crone_state_index != 100 and self.state_index != 2:  # Not Quit
            ret += self.get_ts_prompt()
        return ret
        # self.send_output(ret)

    def exec_str_cmd(self):
        inp_lines = self.last_line + self.raw_input
        inp_lines = inp_lines.replace(b'\n', b'\r')
        inp_lines = inp_lines.split(b'\r')
        _ret = ''
        for li in inp_lines:
            for str_cmd in list(self.str_cmd_exec.keys()):
                if str_cmd in li:
                    self.cmd = str_cmd
                    self.parameter = [li[len(str_cmd):]]
                    #print(f"str_cmd cmd: {str_cmd}")
                    #print(f"str_cmd par: {self.parameter}")
                    _ret = self.str_cmd_exec[str_cmd]()
                    self.cmd = b''
                    self.send_output(_ret)
        self.last_line = inp_lines[-1]
        return _ret
        # self.raw_input = b''

    def send_prompt(self):
        self.send_output(self.get_ts_prompt())

    def decode_param(self):
        tmp = []
        for el in self.parameter:
            tmp.append(el.decode(self.encoding[0], 'ignore').replace('\r', '').replace('\n', ''))
        self.parameter = list(tmp)

    def cmd_connect(self):
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
        # print(f"Echo Param: {self.parameter}")
        for el in self.parameter:
            ret += el.decode(self.encoding[0], self.encoding[1]) + ' '
        # print(f"Echo ret: {ret}")
        return ret[:-1] + '\r'

    def cmd_q(self):  # Quit
        # self.connection: AX25Conn
        # self.connection.tx_buf_rawData += self.bye_text.encode(self.encoding[0], self.encoding[1])
        conn_dauer = get_time_delta(self.time_start)
        ret = f"\r # {STR_TABLE['time_connected'][self.connection.cli_language]}: {conn_dauer}\r\r"
        ret += self.bye_text + '\r'
        self.send_output(ret)
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
            return ret.replace('\n', '\r')
        else:
            return self.stat_cfg.stat_parm_cli_itext.replace('\n', '\r')

    def cmd_li(self):
        ret = self.load_fm_file(self.stat_cfg_index_call + '.litx')
        if ret:
            return ret.replace('\n', '\r')
        else:
            return self.stat_cfg.stat_parm_cli_longitext.replace('\n', '\r')

    def cmd_news(self):
        ret = self.load_fm_file(self.stat_cfg_index_call + '.atx')
        if ret:
            return ret.replace('\n', '\r')
        else:
            return self.stat_cfg.stat_parm_cli_akttext.replace('\n', '\r')

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
                                att not in self.user_db.not_public_vars:
                            if getattr(ent, att):
                                ent_ret += f"| {att.ljust(10)}: {getattr(ent, att)}\r"

                    ent_ret += "|-------------------\r\r"
                    return header + ent_ret

            return "\r" \
                   f"{STR_TABLE['cli_no_user_db_ent'][self.connection.cli_language]}" \
                   "\r"

    def cmd_set_name(self):
        if not self.parameter:
            if self.user_db_ent:
                return f" #\r Name: {self.user_db_ent.Name}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.Name = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_name_set'][self.connection.cli_language]}: {self.user_db_ent.Name}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_name NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_qth(self):
        if not self.parameter:
            if self.user_db_ent:
                return f"\r # QTH: {self.user_db_ent.QTH}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.QTH = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_qth_set'][self.connection.cli_language]}: {self.user_db_ent.QTH}" \
                   "\r"

        logger.error("User-DB Error. cli_qth_set NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_loc(self):
        if not self.parameter:
            if self.user_db_ent:
                return f"\r # Locator: {self.user_db_ent.LOC}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.LOC = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_loc_set'][self.connection.cli_language]}: {self.user_db_ent.LOC}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_loc NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_zip(self):
        if not self.parameter:
            if self.user_db_ent:
                return f"\r # ZIP: {self.user_db_ent.ZIP}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.ZIP = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_zip_set'][self.connection.cli_language]}: {self.user_db_ent.ZIP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_zip NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_pr_mail(self):
        if not self.parameter:
            if self.user_db_ent:
                return f"\r # PR-Mail: {self.user_db_ent.PRmail}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.PRmail = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_prmail_set'][self.connection.cli_language]}: {self.user_db_ent.PRmail}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_pr_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_e_mail(self):
        if not self.parameter:
            if self.user_db_ent:
                return f"\r # E-Mail: {self.user_db_ent.Email}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.Email = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_email_set'][self.connection.cli_language]}: {self.user_db_ent.Email}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_e_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_http(self):
        if not self.parameter:
            if self.user_db_ent:
                return f"\r # WEB: {self.user_db_ent.HTTP}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.HTTP = self.parameter[0]\
                .decode(self.encoding[0], self.encoding[1]).\
                replace(' ', '').\
                replace('\n', '').\
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_http_set'][self.connection.cli_language]}: {self.user_db_ent.HTTP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_http NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_port(self):     # TODO Pipe
        ret = f"\r      < {STR_TABLE['port_overview'][self.connection.cli_language]} >\r\r"
        ret += "-#--Name----PortTyp--Stations--Typ------Digi-\r"
        for port_id in self.port_handler.ax25_ports.keys():
            port = self.port_handler.ax25_ports[port_id]
            name = str(port.portname).ljust(7)
            typ = port.port_typ.ljust(7)
            stations = port.my_stations
            if not stations:
                stations = ['']
            digi = ''

            if stations[0] in port.stupid_digi_calls and stations[0]:
                digi = '(DIGI)'
            if stations[0] in port.port_cfg.parm_cli.keys():
                digi = f"{port.port_cfg.parm_cli[stations[0]].cli_name.ljust(7)} " + digi

            ret += f" {str(port_id).ljust(2)} {name} {typ}  {stations[0].ljust(9)} {digi}\r"
            for stat in stations[1:]:
                digi = ''
                if stat in port.stupid_digi_calls:
                    digi = '(DIGI)'
                if stat in port.port_cfg.parm_cli.keys():
                    digi = f"{port.port_cfg.parm_cli[stat].cli_name.ljust(7)} " + digi
                ret += f"                     {stat.ljust(9)} {digi}\r"
        ret += '\r'
        return ret

    def cmd_lcstatus(self):
        """ Long Connect-Status """
        # ret = f"\r      < {STR_TABLE['port_overview'][self.connection.cli_language]} >\r\r"
        ret = '\r'
        ret += "  Ch  Port  MyCall    Call      Name          LOC    QTH           Connect\r"
        ret += "---------------------------------------------------------------------------\r"
        all_conn = self.port_handler.all_connections
        for k in all_conn.keys():
            ch = k
            conn = all_conn[k]
            time_start = conn.time_start    # TODO DateSTR
            port_id = conn.own_port.port_id
            my_call = conn.my_call_str
            to_call = conn.to_call_str
            db_ent = conn.user_db_ent
            name = ''
            loc = ''
            qth = ''
            if db_ent:
                name = db_ent.Name
                loc = db_ent.LOC
                qth = db_ent.QTH
            if self.connection.ch_index == ch:
                ret += ">"
            else:
                ret += " "

            ret += f" {str(ch).ljust(3)} " \
                   f"{str(port_id).ljust(3)}   " \
                   f"{my_call.ljust(9)} " \
                   f"{to_call.ljust(9)} " \
                   f"{name.ljust(13)[:13]} " \
                   f"{loc.ljust(6)[:6]} " \
                   f"{qth.ljust(13)[:13]} " \
                   f"{time_start.strftime('%H:%M:%S')}\r"

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

    def cmd_umlaut(self):
        # print(self.parameter)
        if not self.parameter:
            return f"\r{STR_TABLE['cli_text_encoding_no_param'][self.connection.cli_language]}: {self.encoding[0]}\r"
        res = find_decoding(self.parameter[0].replace(b'\r', b''))
        if not res:
            return f"\r{STR_TABLE['cli_text_encoding_error_not_found'][self.connection.cli_language]}\r"
        self.encoding = res, self.encoding[1]
        if self.user_db_ent:
            self.user_db_ent.Encoding = str(res)
        return f"\r{STR_TABLE['cli_text_encoding_set'][self.connection.cli_language]} {res}\r"

    def str_cmd_req_name(self):
        name = self.connection.stat_cfg.stat_parm_Name
        qth = self.connection.stat_cfg.stat_parm_QTH
        loc = self.connection.stat_cfg.stat_parm_LOC
        if name:
            name = f'#NAM# {name}\r'
        if qth:
            qth = f'#QTH# {qth}\r'
        if loc:
            loc = f'#LOC# {loc}\r'
        tmp = self.parameter[0]
        cmd_dict = {
            b'+++#': name + qth + loc,
            b'++-#': name + qth,
            b'+--#': name,
            b'+-+#': name + loc,
            b'--+#': loc,
            b'-++#': qth + loc,
        }
        if tmp in cmd_dict.keys():
            return cmd_dict[tmp]
        return ''

    def cli_exec(self, inp=b''):
        if not self.connection.is_link:
            self.raw_input = bytes(inp)
            _ret = self.state_exec[self.state_index]()
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
        self.state_index = 1
        if self.prefix:
            return self.c_text
        else:
            return self.c_text + self.get_ts_prompt()

    def s1(self):
        self.find_stat_identifier()
        if self.stat_identifier is None:
            if self.last_line:
                self.stat_identifier = False
        """    
        print(f"\n\ns1 id: {self.stat_identifier}\n"
              f"s1 inp: {self.raw_input}\n\n")
        """
        ########################
        # Check String Commands
        if not self.exec_str_cmd():
            self.input = self.raw_input
            self.send_output(self.exec_cmd())
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
