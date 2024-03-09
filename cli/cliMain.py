from datetime import datetime
import pickle
import logging

import ax25.ax25Connection
from cfg import constant, config_station
from cli.BaycomLogin import BaycomLogin
from cli.StringVARS import replace_StringVARS
from cli.cliStationIdent import get_station_id_obj
from cfg.constant import STATION_ID_ENCODING_REV
from fnc.str_fnc import get_time_delta, find_decoding, get_timedelta_str_fm_sec, get_timedelta_CLIstr, \
    convert_str_to_datetime
from cfg.string_tab import STR_TABLE
from fnc.ax25_fnc import validate_call
from UserDB.UserDBmain import Client, USER_DB
from ax25.ax25UI_Pipe import AX25Pipe

logger = logging.getLogger(__name__)


class DefaultCLI(object):
    cli_name = ''  # DON'T CHANGE!
    service_cli = True
    c_text = '-= Test C-TEXT =-\r\r'
    bye_text = '73 ...\r'
    prompt = ''
    prefix = b'//'
    sw_id = ''

    def __init__(self, connection):
        # print("CLI-INIT")
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

        self.connection = connection
        self.port_handler = self.connection.port_handler
        self.own_port = self.connection.own_port
        # self.channel_index = self.connection.ch_index
        if self.connection.gui is None:
            self.gui = False
        else:
            self.gui = self.connection.gui
        self.my_call_str = self.connection.my_call_str
        self.to_call_str = self.connection.to_call_str
        self.user_db = USER_DB
        self.user_db_ent: Client = self.connection.user_db_ent
        self.encoding = 'UTF-8', 'ignore'
        self.stat_identifier_str = ''
        if self.user_db_ent:
            self.encoding = self.user_db_ent.Encoding, 'ignore'
            self.stat_identifier_str = self.user_db_ent.software_str
            if self.user_db_ent.CText:
                self.c_text = str(self.user_db_ent.CText)

        self.stat_identifier = get_station_id_obj(self.stat_identifier_str)
        # print(f"CLI STST ID : {self.stat_identifier}")
        # print(f"CLI STST str : {self.stat_identifier_str}")

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
        self.new_last_line = b''
        self.parameter = []
        self.sys_login = None
        self.sysop_priv = False
        # Crone
        self.cron_state_exec = {
            0: self.cron_s0,  # No CMDs / Doing nothing
            100: self.cron_s_quit  # QUIT
        }
        # Standard Commands ( GLOBAL )
        self.commands = {
            # CMD: (needed lookup len(cmd), cmd_fnc, HElp-Str)
            'QUIT': (1, self._cmd_q, 'Quit'),
            'BYE': (1, self._cmd_q, 'Bye'),
            'CONNECT': (1, self._cmd_connect, 'Connect'),
            'ECHO': (1, self._cmd_echo, 'Echo'),
            'PORT': (1, self.cmd_port, 'Ports'),
            'MH': (0, self._cmd_mh, 'MYHeard List'),
            'LMH': (0, self._cmd_mhl, 'Long MYHeard List'),
            'AXIP': (2, self._cmd_axip, 'AXIP-MH List'),
            'ATR': (2, self.cmd_aprs_trace, 'APRS-Tracer'),
            'DXLIST': (2, self._cmd_dxlist, 'DX/Tracer Alarm List'),
            'LCSTATUS': (2, self.cmd_lcstatus, STR_TABLE['cmd_help_lcstatus'][self.connection.cli_language]),
            'WX': (0, self.cmd_wx, STR_TABLE['cmd_help_wx'][self.connection.cli_language]),
            'BELL': (2, self.cmd_bell, STR_TABLE['cmd_help_bell'][self.connection.cli_language]),

            'INFO': (1, self.cmd_i, 'Info'),
            'LINFO': (2, self.cmd_li, 'Long Info'),
            'NEWS': (2, self.cmd_news, 'NEWS'),
            'VERSION': (3, self.cmd_ver, 'Version'),
            'USER': (0, self.cmd_user_db_detail, STR_TABLE['cmd_help_user_db'][self.connection.cli_language]),
            'NAME': (1, self.cmd_set_name, STR_TABLE['cmd_help_set_name'][self.connection.cli_language]),
            'QTH': (0, self.cmd_set_qth, STR_TABLE['cmd_help_set_qth'][self.connection.cli_language]),
            'LOC': (0, self.cmd_set_loc, STR_TABLE['cmd_help_set_loc'][self.connection.cli_language]),
            'ZIP': (0, self.cmd_set_zip, STR_TABLE['cmd_help_set_zip'][self.connection.cli_language]),
            'PRMAIL': (0, self.cmd_set_pr_mail, STR_TABLE['cmd_help_set_prmail'][self.connection.cli_language]),
            'EMAIL': (0, self.cmd_set_e_mail, STR_TABLE['cmd_help_set_email'][self.connection.cli_language]),
            'WEB': (3, self.cmd_set_http, STR_TABLE['cmd_help_set_http'][self.connection.cli_language]),
            'LANG': (0, self._cmd_lang, STR_TABLE['cli_change_language'][self.connection.cli_language]),
            'UMLAUT': (2, self.cmd_umlaut, STR_TABLE['auto_text_encoding'][self.connection.cli_language]),
            'POPT': (0, self.cmd_popt_banner, 'PoPT Banner'),
            'HELP': (1, self.cmd_help, STR_TABLE['help'][self.connection.cli_language]),
            '?': (0, self.cmd_shelp, STR_TABLE['cmd_shelp'][self.connection.cli_language]),

        }

        self.str_cmd_exec = {
            b'#REQUESTNAME:': self.str_cmd_req_name,
            b'#NAM#': self.cmd_set_name,
            b'#QTH#': self.cmd_set_qth,
            b'#LOC#': self.cmd_set_loc,
        }

        self.state_exec = {
            0: self.s0,  # C-Text
            1: self.s1,  # Cmd Handler
            2: self.s2,  # Nothing / no remote !!! Override in NODECLI ...
            3: self.s3,  # Baycom Login Shit
            4: self.s4,  # Try to connect other Station ( C CMD )
            5: self.s5,  # Nothing / no remote
        }
        self.cmd_exec_ext = {}  # Extern Command's ??
        self.cron_state_exec_ext = {}  # Extern Tasks ??
        self.state_exec_ext = {}  # Extern State Tab ??
        # self.init()
        self.cron_state_exec.update(self.cron_state_exec_ext)
        self.commands.update(self.cmd_exec_ext)
        self.state_exec.update(self.state_exec_ext)
        if type(self.prefix) is str:  # Fix for old CFG Files
            self.prefix = self.prefix.encode(self.encoding[0], self.encoding[1])

    """
    def init(self):
        self.cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {}
    """

    def build_prompt(self):
        self.prompt = f"\r<{self.prompt}>{self.my_call_str}>"

    def get_ts_prompt(self):
        return f"\r{self.my_call_str} ({datetime.now().strftime('%H:%M:%S')})>"

    def send_output(self, ret, env_vars=True):
        if ret:
            if type(ret) is str:
                if env_vars:
                    ret = replace_StringVARS(ret,
                                             port=self.own_port,
                                             port_handler=self.port_handler,
                                             connection=self.connection,
                                             user_db=self.user_db)
                ret = ret.encode(self.encoding[0], self.encoding[1])
                ret = ret.replace(b'\n', b'\r')
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
        if self.prefix:
            self.input = self.input.replace(b'\n', b'\r')
            # self.input = self.input.split(b'\r')[0]
            self.input = self.input.split(b'\r')
            while self.input:
                if self.input[0]:
                    break
                else:
                    self.input = self.input[1:]
            if not self.input:
                return False
            self.input = self.input[0]

            if self.input[:len(self.prefix)] == self.prefix:
                self.parameter = []
                cmd = self.input[len(self.prefix):]
                cmd = cmd.split(b' ')
                if len(cmd) > 1:
                    self.input = cmd[1:]
                    self.parameter = cmd[1:]
                else:
                    self.input = b''

                cmd = cmd[0]
                self.cmd = cmd \
                    .upper() \
                    .replace(b' ', b'') \
                    .replace(b'\r', b'')
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
        else:
            self.input = b''
        cmd = cmd[0]
        self.cmd = cmd \
            .upper() \
            .replace(b'\r', b'') \
            .replace(b'//', b'')

        return False

    def load_fm_file(self, filename: str):
        try:
            with open(constant.CFG_data_path +
                      constant.CFG_usertxt_path +
                      self.stat_cfg_index_call + '/' +
                      filename, 'rb') as inp:
                return pickle.load(inp)
        except FileNotFoundError:
            return ''
        except EOFError:
            return ''

    def start_baycom_login(self, login_cmd=''):
        if self.sys_login is None:
            if self.user_db_ent:
                if self.user_db_ent.sys_pw:
                    self.sys_login = BaycomLogin(
                        sys_pw_parm=self.user_db_ent.sys_pw_parm,
                        sys_pw=self.user_db_ent.sys_pw,
                        login_cmd=login_cmd
                    )
                    self.send_output(self.sys_login.start(), env_vars=False)
                    self.change_cli_state(3)

    def _send_sw_id(self):
        if not self.sw_id:
            return ""
        unknown = '?'
        didadit = ''  # True = 'D'
        txt_enc = '4'  # UTF-8
        if self.user_db_ent:
            if self.user_db_ent.Name:
                unknown = ''
            if self.user_db_ent.Encoding:
                try:
                    txt_enc = str(STATION_ID_ENCODING_REV[self.user_db_ent.Encoding])
                except KeyError:
                    logger.error(f"KeyERROR STATION_ID_ENCODING_REV (constant.py): {self.user_db_ent.Encoding}")
        flag = txt_enc + didadit + unknown
        return '{' + f"{self.sw_id}-{constant.VER}-{flag}" + '}\r'

    def _set_user_db_software_id(self):
        if self.user_db_ent:
            self.user_db_ent.software_str = str(self.stat_identifier.id_str)
            self.user_db_ent.Software = str(self.stat_identifier.software) + '-' + str(self.stat_identifier.version)
            # if not self.user_db_ent.TYP:
            self.user_db_ent.TYP = str(self.stat_identifier.typ)

    def _software_identifier(self):
        res = self._find_sw_identifier()
        if res and self.stat_identifier:
            # print(f"SW-ID flag: {self.stat_identifier.flags}")
            # print(f"SW-ID txt_encoding: {self.stat_identifier.txt_encoding}")
            if self.stat_identifier.knows_me is not None:
                if not self.stat_identifier.knows_me:
                    self._send_name_cmd_back()
            if self.stat_identifier.txt_encoding is not None:
                self.encoding = self.stat_identifier.txt_encoding, 'ignore'
                if self.user_db_ent:
                    self.user_db_ent.Encoding = self.stat_identifier.txt_encoding

    def _send_name_cmd_back(self):
        name = self.connection.stat_cfg.stat_parm_Name
        if name:
            if self.stat_identifier is not None:
                if self.stat_identifier:
                    if self.stat_identifier.typ == 'SYSOP':
                        self.send_output(f'\r//N {name}\r', env_vars=False)
                    else:
                        self.send_output(f'\rN {name}\r', env_vars=False)

    def _find_sw_identifier(self):

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
                    self.stat_identifier = temp_stat_identifier
                    self._set_user_db_software_id()
                    return True
        elif not self.last_line and self.stat_identifier:
            inp_lines = self.raw_input
            inp_lines = inp_lines.replace(b'\n', b'\r')
            inp_lines = inp_lines.decode(self.encoding[0], 'ignore')
            inp_lines = inp_lines.split('\r')
            # print(f"find_stat_identifier inp_lines: {inp_lines}")
            for li in inp_lines:
                temp_stat_identifier = get_station_id_obj(li)
                if temp_stat_identifier is not None:
                    if self.stat_identifier.id_str != temp_stat_identifier.id_str:
                        self.stat_identifier = temp_stat_identifier
                        self._set_user_db_software_id()
                        return True
        return False

    def _find_cmd(self):
        # TODO AGAIN
        if self.cmd:
            inp_cmd = str(self.cmd.decode(self.encoding[0], 'ignore'))
            inp_cmd = inp_cmd.replace(' ', '')
            cmds = list(self.commands.keys())
            treffer = []
            for cmd in cmds:
                if self.commands[cmd][0]:
                    if inp_cmd == cmd[:self.commands[cmd][0]]:
                        self.cmd = b''
                        ret = tuple(self.commands[cmd])[1]()
                        self.new_last_line = b''
                        if ret:
                            return ret
                        return ''
                if inp_cmd == cmd[:len(inp_cmd)]:
                    treffer.append(cmd)
            if not treffer:
                return f"\r # {STR_TABLE['cmd_not_known'][self.connection.cli_language]}\r"
            if len(treffer) > 1:
                return (f"\r # {STR_TABLE['cmd_not_known'][self.connection.cli_language]}"
                        f"\r # {(' '.join(treffer))} ?\r")
            self.cmd = b''
            if not callable(self.commands[treffer[0]][1]):
                return ''
            ret = tuple(self.commands[treffer[0]])[1]()
            # self.last_line = b''
            self.new_last_line = b''
            if ret:
                return ret
            return ''

        return f"\r # {STR_TABLE['cmd_not_known'][self.connection.cli_language]}\r"

    def _exec_cmd(self):
        self.input = self.last_line + self.input
        if self.is_prefix():
            return self._find_cmd()
        # Message is for User ( Text , Chat )
        if self.prefix:
            return ''
        # CMD Input for No User Terminals ( Node ... )
        ret = self._find_cmd()
        if self.crone_state_index not in [100] and \
                self.state_index not in [2, 4]:  # Not Quit
            ret += self.get_ts_prompt()
        return ret

    def _exec_str_cmd(self):
        inp_lines = self.last_line + self.raw_input
        inp_lines = inp_lines.replace(b'\n', b'\r')
        inp_lines = inp_lines.split(b'\r')
        ret = ''
        self.new_last_line = inp_lines[-1]
        for li in inp_lines:
            for str_cmd in list(self.str_cmd_exec.keys()):
                if str_cmd in li:
                    self.cmd = str_cmd
                    self.parameter = [li[len(str_cmd):]]
                    ret = self.str_cmd_exec[str_cmd]()
                    self.cmd = b''
                    self.send_output(ret, env_vars=False)
                    self.last_line = b''
                    self.new_last_line = b''
                    return ret
        return ret

    def send_prompt(self):
        self.send_output(self.get_ts_prompt())

    def _decode_param(self, defaults=None):
        if defaults is None:
            defaults = []
        if type(defaults) is not list:
            defaults = []
        tmp = []
        if not defaults:
            for el in self.parameter:
                tmp.append(el.decode(self.encoding[0], 'ignore').replace('\r', ''))
        else:
            for el in defaults:
                if len(self.parameter) > len(tmp):
                    tmp_parm = self.parameter[len(tmp)].decode(self.encoding[0], 'ignore').replace('\r', '')
                    try:
                        tmp_parm = type(el)(tmp_parm)
                    except ValueError:
                        tmp_parm = defaults[len(tmp)]
                else:
                    tmp_parm = defaults[len(tmp)]
                tmp.append(tmp_parm)
        self.parameter = list(tmp)

    def _cmd_connect(self):
        # print(f'cmd_connect() param: {self.parameter}')
        self._decode_param()
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
        port_tr = False
        if len(self.parameter) > 1:
            if self.parameter[-1].isdigit():
                port_tr = True
                port_id = int(self.parameter[-1])
                if port_id not in self.port_handler.get_all_ports().keys():
                    ret = '\r # Ungültiger Port..\r'
                    return ret
            if port_tr:
                parm = self.parameter[1:-1]
            else:
                parm = self.parameter[1:]

            for call in parm:
                tmp_call = validate_call(call)
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
            self.state_index = 4
            return conn[1]
        return f'\r*** Link Busy: {conn[1]}\r'

    def _cmd_echo(self):  # Quit
        ret = ''
        # print(f"Echo Param: {self.parameter}")
        for el in self.parameter:
            ret += el.decode(self.encoding[0], self.encoding[1]) + ' '
        # print(f"Echo ret: {ret}")
        return ret[:-1] + '\r'

    def _cmd_q(self):  # Quit
        # self.connection: AX25Conn
        # self.connection.tx_buf_rawData += self.bye_text.encode(self.encoding[0], self.encoding[1])
        conn_dauer = get_time_delta(self.time_start)
        ret = f"\r # {STR_TABLE['time_connected'][self.connection.cli_language]}: {conn_dauer}\r\r"
        ret += self.bye_text + '\r'
        self.send_output(ret, env_vars=True)
        self.crone_state_index = 100  # Quit State
        return ''

    def _cmd_lang(self):
        if not self.parameter:
            return f'\r # {STR_TABLE["cli_no_lang_param"][self.connection.cli_language]}{" ".join(list(constant.LANG_IND.keys()))}\r'
        self._decode_param()
        if self.parameter[0].upper() in constant.LANG_IND.keys():
            self.connection.set_user_db_language(constant.LANG_IND[self.parameter[0].upper()])
            return f'\r # {STR_TABLE["cli_lang_set"][self.connection.cli_language]}\r'
        return f'\r # {STR_TABLE["cli_no_lang_param"][self.connection.cli_language]}{" ".join(list(constant.LANG_IND.keys()))}\r'

    def _cmd_dxlist(self):
        parm = 10
        if self.parameter:
            try:
                parm = int(self.parameter[0])
            except ValueError:
                pass
        ret = self._get_alarm_out_cli(max_ent=parm)

        return ret + '\r'

    def _get_alarm_out_cli(self, max_ent=10):
        alarm_his = dict(self.port_handler.get_MH().dx_alarm_perma_hist)
        alarm_his.update(dict(self.port_handler.get_aprs_ais().be_tracer_alarm_hist))
        if not alarm_his:
            return f'\r # {STR_TABLE["cli_no_data"][self.connection.cli_language]}\r'
        out = '\r'
        out += "-----Time-Port---Call------via-------LOC------Dist(km)--Type---\r"
        max_c = 0
        key_list = list(alarm_his.keys())
        key_list.sort(reverse=True)
        for _k in key_list:
            max_c += 1
            if max_c > max_ent:
                break
            time_delta_str = get_timedelta_CLIstr(alarm_his[_k]['ts'])
            via = alarm_his[_k]['via']
            loc = alarm_his[_k]['loc']
            dis = str(alarm_his[_k]['dist'])
            typ = alarm_his[_k]['typ']
            port = str(alarm_his[_k]['port_id'])
            call = alarm_his[_k]['call_str']

            out += f' {time_delta_str} {port:6} {call:10}{via:10}{loc:9}{dis:10}{typ}\r'

        return out

    def _cmd_axip(self):
        parm = 10
        if self.parameter:
            try:
                parm = int(self.parameter[0])
            except ValueError:
                pass
        ret = self._get_axip_out_cli(max_ent=parm)

        return ret + '\r'

    def _get_axip_out_cli(self, max_ent=10):
        _ent = self.port_handler.get_MH().get_sort_mh_entry('last', reverse=False)
        if not _ent:
            return f'\r # {STR_TABLE["cli_no_data"][self.connection.cli_language]}\r'
        max_c = 0
        out = '\r'
        # out += '\r                       < AXIP - Clients >\r\r'
        out += '-Call------IP:Port---------------------------Last------------\r'
        for k in _ent.keys():
            if _ent[k].axip_add[0]:
                max_c += 1
                if max_c > max_ent:
                    break
                out += ' {:9} {:33} {:8}\r'.format(
                    _ent[k].own_call,
                    _ent[k].axip_add[0] + ':' + str(_ent[k].axip_add[1]),
                    get_timedelta_CLIstr(_ent[k].last_seen, r_just=False)
                )
        return out

    def _cmd_mh(self):
        last_port_id = len(self.port_handler.get_all_port_ids())
        if last_port_id > 20:
            max_ent = int(last_port_id)
        else:
            max_ent = 20
        self._decode_param(defaults=[
            max_ent,  # Entry's
            -1,  # Port
        ])
        # print(self.parameter)
        # print(max_ent)
        parm = self.parameter[0]
        if parm < last_port_id:
            port = self.parameter[0]
            if self.parameter[1] == -1:
                parm = 20
            else:
                parm = self.parameter[1]
        else:
            port = self.parameter[1]

        ret = self._get_mh_out_cli(max_ent=parm, port_id=port)

        return ret + '\r'

    def _get_mh_out_cli(self, max_ent=20, port_id=-1):
        sort_list = self.port_handler.get_MH().get_sort_mh_entry('last', False)
        if not sort_list:
            return f'\r # {STR_TABLE["cli_no_data"][self.connection.cli_language]}\r'
        out = ''
        c = 0
        max_c = 0

        for call in list(sort_list.keys()):
            if port_id == -1 or port_id == sort_list[call].port_id:
                max_c += 1
                if max_c > max_ent:
                    break
                time_delta_str = get_timedelta_CLIstr(sort_list[call].last_seen)
                _call_str = sort_list[call].own_call
                if sort_list[call].route:
                    _call_str += '*'
                out += f'{time_delta_str} P:{sort_list[call].port_id:2} {_call_str:10}'.ljust(27, " ")

                c += 1
                if c == 2:  # Breite
                    c = 0
                    out += '\r'
        if not out:
            return f'\r # {STR_TABLE["cli_no_data"][self.connection.cli_language]}\r'
        return '\r' + out

    def _cmd_mhl(self):
        last_port_id = len(self.port_handler.get_all_port_ids())
        if last_port_id > 10:
            max_ent = int(last_port_id)
        else:
            max_ent = 10
        self._decode_param(defaults=[
            max_ent,  # Entry's
            -1,  # Port
        ])

        parm = self.parameter[0]
        if parm < last_port_id:
            port = self.parameter[0]
            if self.parameter[1] == -1:
                parm = 10
            else:
                parm = self.parameter[1]
        else:
            port = self.parameter[1]

        ret = self._get_mh_long_out_cli(max_ent=parm, port_id=port)

        return ret + '\r'

    def _get_mh_long_out_cli(self, max_ent=10, port_id=-1):
        sort_list = self.port_handler.get_MH().get_sort_mh_entry('last', False)
        if not sort_list:
            return f'\r # {STR_TABLE["cli_no_data"][self.connection.cli_language]}\r'
        out = ''
        max_c = 0
        """
        tp = 0
        tb = 0
        rj = 0
        """

        for call in list(sort_list.keys()):
            if port_id == -1 or port_id == sort_list[call].port_id:
                max_c += 1
                if max_c > max_ent:
                    break
                time_delta_str = get_timedelta_CLIstr(sort_list[call].last_seen)
                via = sort_list[call].route
                if via:
                    via = via[-1]
                else:
                    via = ''
                loc = ''
                dis = ''
                typ = ''
                userdb_ent = USER_DB.get_entry(sort_list[call].own_call, add_new=False)
                if userdb_ent:
                    loc = userdb_ent.LOC
                    if userdb_ent.Distance:
                        dis = str(userdb_ent.Distance)
                    typ = userdb_ent.TYP

                out += (f' {time_delta_str:9}{str(sort_list[call].port_id).ljust(5)}{sort_list[call].own_call:10}'
                        f'{via:10}{loc:9}{dis:10}{typ:7}{sort_list[call].pac_n}')

                out += '\r'
        if not out:
            return f'\r # {STR_TABLE["cli_no_data"][self.connection.cli_language]}\r'
        return "\r-----Time-Port-Call------via-------LOC------Dist(km)--Type---Packets\r" + out

    def cmd_wx(self):
        """ WX Stations """
        if self.port_handler.aprs_ais is None:
            return f'\r # {STR_TABLE["cli_no_wx_data"][self.connection.cli_language]}\r\r'
        parm = 10
        ret = ''
        self._decode_param()
        if self.parameter:
            if self.parameter[0].isdigit():
                try:
                    parm = int(self.parameter[0])
                except ValueError:
                    pass
                ret = self._get_wx_cli_out(max_ent=parm)
            else:
                call = validate_call(self.parameter[0])
                if call:
                    le = parm
                    if len(self.parameter) == 2:
                        try:
                            le = int(self.parameter[1])
                        except ValueError:
                            pass
                    ret = self._get_wx_fm_call_cli_out(call=call, max_ent=le)
        else:
            ret = self._get_wx_cli_out(max_ent=parm)
        if not ret:
            return f'\r # {STR_TABLE["cli_no_wx_data"][self.connection.cli_language]}\r\r'
        return ret + '\r'

    def _get_wx_fm_call_cli_out(self, call, max_ent=10):
        data = list(self.port_handler.aprs_ais.get_wx_data().get(call, ''))
        if not data:
            return ''
        data.reverse()
        max_c = 0
        loc = f'{data[0].get("locator", "------")[:6]}({round(data[0].get("distance", -1))}km)'
        out = '\r'
        out += f'WX-Station: {call}\r'
        out += f'Locator   : {loc}\r'
        out += f'Comment   : {data[0].get("comment", "")}\r'
        out += f'Datapoints: {len(data)}\r\r'
        out += '-----Last-Port--Temp-Press---Hum-Lum-Rain(24h)-WindGust\r'
        for el in data:
            max_c += 1
            if max_c > max_ent:
                break
            # _ent = self.port_handler.aprs_ais.aprs_wx_msg_pool[k][-1]
            td = get_timedelta_CLIstr(el['rx_time'])
            pres = f'{el["weather"].get("pressure", 0):.2f}'
            rain = f'{el["weather"].get("rain_24h", 0):.3f}'
            out += f'{td.rjust(9):10}{el.get("port_id", ""):6}'
            out += f'{str(round(el["weather"].get("temperature", 0))):5}'
            out += f'{pres:7} '
            out += f'{el["weather"].get("humidity", 0):3} '
            out += f'{el["weather"].get("luminosity", 0):3} '
            out += f'{rain:9} '
            out += f'{el["weather"].get("wind_gust", 0):.3f}\r'
        return out

    def _get_wx_cli_out(self, max_ent=10):
        db = self.port_handler.get_database()
        if not db:
            return ''

        # _data = self.port_handler.aprs_ais.get_wx_entry_sort_distance()
        data = db.aprsWX_get_data_f_CLItree(last_rx_days=3)
        if not data:
            return ''

        max_c = 0
        out = '\r-----Last-Port--Call------LOC-------------Temp-Press---Hum-Lum-Rain(24h)-\r'
        for el in data:
            max_c += 1
            if max_c > max_ent:
                break
            # _ent = self.port_handler.aprs_ais.aprs_wx_msg_pool[k][-1]
            td = get_timedelta_CLIstr(convert_str_to_datetime(el[0]))
            loc = f'{el[3].upper()[:6]}({int(el[4])}km)'
            pres = f'{el[5]}'
            rain = f'{el[7]}'
            out += f'{td.rjust(9):10}{el[2]:6}{el[1]:10}{loc:16}'
            out += f'{el[8]:5}'
            out += f'{pres:7} '
            out += f'{el[6]:3} '
            out += f'{el[9]:3} '
            out += f'{rain:6}\r'
        return out

    def cmd_aprs_trace(self):
        """APRS Tracer"""
        if self.port_handler.aprs_ais is None:
            return f'\r # {STR_TABLE["cli_no_tracer_data"][self.connection.cli_language]}\r\r'
        parm = 10
        if self.parameter:
            try:
                parm = int(self.parameter[0])
            except ValueError:
                pass
        data = self.port_handler.aprs_ais.tracer_traces_get()
        if not data:
            return f'\r # {STR_TABLE["cli_no_tracer_data"][self.connection.cli_language]}\r\r'
        intervall = self.port_handler.aprs_ais.be_tracer_interval
        active = self.port_handler.aprs_ais.be_tracer_active
        last_send = self.port_handler.aprs_ais.tracer_get_last_send()
        last_send = get_timedelta_str_fm_sec(last_send, r_just=False)
        if not active:
            intervall_str = 'off'
        else:
            intervall_str = str(intervall)
        # out = '\r # APRS-Tracer Beacon\r\r'
        out = '\r'
        out += f'Tracer Port     : {self.port_handler.aprs_ais.be_tracer_port}\r'
        out += f'Tracer Call     : {self.port_handler.aprs_ais.be_tracer_station}\r'
        out += f'Tracer WIDE Path: {self.port_handler.aprs_ais.be_tracer_wide}\r'
        out += f'Tracer intervall: {intervall_str}\r'
        out += f'Auto Tracer     : {constant.BOOL_ON_OFF.get(self.port_handler.aprs_ais.be_auto_tracer_active, False).lower()}\r'
        # out += f'APRS-Server     : {constant.BOOL_ON_OFF.get(self.port_handler.aprs_ais., False).lower()}\r'
        out += f'Last Trace send : {last_send}\r\r'
        out += '-----Last-Port--Call------LOC-------------Path----------------------------------\r'
        max_c = 0
        for k in data:
            max_c += 1
            if max_c > parm:
                break
            ent = data[k][-1]
            td = get_timedelta_CLIstr(ent['rx_time'])
            # path = ', '.join(ent.get('path', []))
            loc = f'{ent.get("locator", "------")[:6]}({round(ent.get("distance", -1))}km)'
            call = ent.get('call', '')
            path_raw = ent.get('path', [])
            path = ''
            c = 0
            for _el in path_raw:
                path += f'{_el}> '
                c += 1
                if c == 3:
                    path += '\r' + ''.rjust(42, ' ')
                    c = 0

            out += f'{td.rjust(9):10}{ent.get("port_id", "-"):6}{call:10}{loc:16}'
            out += f'{path[:-2]}'
            out += '\r'

        return out + '\r'

    @staticmethod
    def cmd_popt_banner():
        ret = '\r$$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|\r' \
              '$$  __$$\ $$  __$$\    $$  __$$\|__$$ __|\r' \
              '$$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |\r' \
              '$$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |\r' \
              '$$  ____/ $$ |  $$ |   $$  ____/   $$ |\r' \
              '$$ |      $$ |  $$ |   $$ |        $$ |\r' \
              '$$ |       $$$$$$  |   $$ |        $$ |\r' \
              '\__|yton   \______/ther\__|acket   \__|erminal\r\r' \
              'Version: {}\r\r\r'.format(constant.VER)
        return ret

    @staticmethod
    def cmd_ver():
        ret = '\r-= P.yton o.ther P.acket T.erminal =-\r' \
              '-= Version: {} \r\r'.format(constant.VER)
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
            max_entry = 20  # TODO: from parameter
            _db_list = list(self.user_db.db.keys())
            header = "\r" \
                     f" USER-DB - {len(_db_list)} Calls\r" \
                     "------------------------------------\r"
            ent_ret = ""
            _db_list.sort()
            c = 0
            for call in _db_list:
                ent_ret += f"{call}\r"
                c += 1
                if c >= max_entry:
                    break
            ent_ret += "------------------------------------\r\r"
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
            self.user_db_ent.Name = self.parameter[0] \
                .decode(self.encoding[0], self.encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
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
            self.user_db_ent.QTH = self.parameter[0] \
                .decode(self.encoding[0], self.encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
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
                if self.user_db_ent.Distance:
                    return f"\r # Locator: {self.user_db_ent.LOC} > {round(self.user_db_ent.Distance)} km\r"
                return f"\r # Locator: {self.user_db_ent.LOC}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.LOC = self.parameter[0] \
                .decode(self.encoding[0], self.encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            self.connection.set_distance()
            if self.user_db_ent.Distance:
                return "\r" \
                       f"{STR_TABLE['cli_loc_set'][self.connection.cli_language]}: {self.user_db_ent.LOC}" \
                       "\r"
            return "\r" \
                   f"{STR_TABLE['cli_loc_set'][self.connection.cli_language]}: {self.user_db_ent.LOC} > {round(self.user_db_ent.Distance)} km" \
                   "\r"

        logger.error("User-DB Error. cmd_set_loc NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_set_zip(self):
        if not self.parameter:
            if self.user_db_ent:
                return f"\r # ZIP: {self.user_db_ent.ZIP}\r"
            return "\r # USER-DB Error !\r"
        if self.user_db_ent:
            self.user_db_ent.ZIP = self.parameter[0] \
                .decode(self.encoding[0], self.encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
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
            self.user_db_ent.PRmail = self.parameter[0] \
                .decode(self.encoding[0], self.encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
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
            self.user_db_ent.Email = self.parameter[0] \
                .decode(self.encoding[0], self.encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
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
            self.user_db_ent.HTTP = self.parameter[0] \
                .decode(self.encoding[0], self.encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self.user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_http_set'][self.connection.cli_language]}: {self.user_db_ent.HTTP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_http NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def cmd_port(self):  # TODO Pipe
        ret = f"\r      < {STR_TABLE['port_overview'][self.connection.cli_language]} >\r\r"
        ret += "-#--Name----PortTyp--Stations--Typ------Digi-\r"
        for port_id in self.port_handler.ax25_ports.keys():
            port = self.port_handler.ax25_ports[port_id]
            name = str(port.portname).ljust(7)
            typ = port.port_typ.ljust(7)
            if port.dualPort_primaryPort in [port, None]:

                stations = port.my_stations
                if not stations:
                    stations = ['']
                digi = ''

                if stations[0] in port.digi_calls and stations[0]:
                    digi = '(DIGI)'
                if stations[0] in port.port_cfg.parm_cli.keys():
                    digi = f"{port.port_cfg.parm_cli[stations[0]].ljust(7)} " + digi

                ret += f" {str(port_id).ljust(2)} {name} {typ}  {stations[0].ljust(9)} {digi}\r"
                for stat in stations[1:]:
                    digi = ''
                    if stat in port.digi_calls:
                        digi = '(DIGI)'
                    if stat in port.port_cfg.parm_cli.keys():
                        digi = f"{port.port_cfg.parm_cli[stat].ljust(7)} " + digi
                    ret += f"                     {stat.ljust(9)} {digi}\r"
            else:
                if port.dualPort_primaryPort:
                    ret += f" {str(port_id).ljust(2)} {name} {typ}  Dual-Port: Secondary from Port {port.dualPort_primaryPort.port_id} \r"
        ret += '\r'
        return ret

    def cmd_lcstatus(self):
        """ Long Connect-Status """
        ret = '\r'
        ret += "--Ch--Port--MyCall----Call------Name----------LOC----QTH-----------Connect\r"
        all_conn = self.port_handler.get_all_connections()
        for k in all_conn.keys():
            ch = k
            conn = all_conn[k]
            time_start = conn.time_start  # TODO DateSTR
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
        # ret = f"\r   < {STR_TABLE['help'][self.connection.cli_language]} >\r"
        ret = "\r"
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
            if self.commands[k][2]:
                ret += '\r {}{:10} = {}'.format(self.prefix.decode('UTF-8', 'ignore'),
                                                k,
                                                self.commands[k][2])
        ret += '\r\r'
        return ret

    def cmd_shelp(self):
        ret = '\r # '
        c = 0
        cmds = list(self.commands.keys())
        cmds.sort()
        for k in cmds:
            ret += (k + ' ')
            if len(ret) - c > 60:
                ret += '\r # '
                c += 60
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

    def cmd_bell(self):
        if not self.connection.noty_bell:
            self.connection.noty_bell = True
            msg = b' '.join(self.parameter)
            msg = msg.decode(self.encoding[0], self.encoding[1])
            self.port_handler.set_noty_bell_PH(self.connection.ch_index, msg)
            return f'\r # {STR_TABLE["cmd_bell"][self.connection.cli_language]}\r'
        return f'\r # {STR_TABLE["cmd_bell_again"][self.connection.cli_language]}\r'

    ##############################################
    def str_cmd_req_name(self):
        name = self.connection.stat_cfg.stat_parm_Name
        qth = self.connection.stat_cfg.stat_parm_QTH
        loc = self.connection.stat_cfg.stat_parm_LOC
        if name:
            name = f'\r#NAM# {name}\r'
        if qth:
            qth = f'\r#QTH# {qth}\r'
        if loc:
            if hasattr(self.stat_identifier, 'software'):
                if 'PoPT' == self.stat_identifier.software:
                    loc = f'\r#LOC# {loc}\r'
            else:
                try:
                    loc = f'\r#LOC# {loc[:6]}\r'
                except IndexError:
                    loc = ''
        tmp = self.parameter[0]
        cmd_dict = {
            b'+++#': name + qth + loc,
            b'++-#': name + qth,
            b'+--#': name,
            b'+-+#': name + loc,
            b'--+#': loc,
            b'-++#': qth + loc,
        }
        req_name = '-'
        req_qth = '-'
        req_loc = '-'
        if self.user_db_ent:
            if not self.user_db_ent.Name:
                req_name = '+'
            if not self.user_db_ent.QTH:
                req_qth = '+'
            if not self.user_db_ent.LOC:
                req_loc = '+'
        req_str = req_name + req_qth + req_loc
        if '+' in req_str:
            req_str = '\r#REQUESTNAME:' + req_str + '#\r'
        else:
            req_str = ''
        if tmp in cmd_dict.keys():
            return cmd_dict[tmp] + req_str
        return ''

    ##############################################
    def cli_exec(self, inp=b''):
        # print(f"cli_exec {self.cli_name}: {self.connection.uid} - SI: {self.state_index} - CSI: {self.crone_state_index}")
        # print(f"cli_exec {self.cli_name}: {self.connection.uid} - raw-input: {inp}")
        # if not self.connection.is_link:
        self.raw_input = bytes(inp)
        ret = self.state_exec[self.state_index]()
        self.send_output(ret)

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
            return self._send_sw_id() + self.c_text
        else:
            return self._send_sw_id() + self.c_text + self.get_ts_prompt()

    def s1(self):
        self._software_identifier()
        ########################
        # Check String Commands
        if not self._exec_str_cmd():
            self.input = self.raw_input
            self.send_output(self._exec_cmd())
        self.last_line = self.new_last_line
        return ''

    def s2(self):
        """ Do nothing / No Remote"""
        """ !!! Override in NODECLI"""
        return ""

    def s3(self):
        """ Sys Login """
        if self.sys_login is None:
            self.change_cli_state(1)
            return ""

        inp = self.raw_input.decode(self.encoding[0], 'ignore')
        if 'OK\r' in inp:
            del self.sys_login
            self.sys_login = None
            # print("END")
            self.sysop_priv = True
            if self.gui:
                self.gui.on_channel_status_change()
            self.change_cli_state(1)
            return ''
        res = self.sys_login.step(inp)
        if not res:
            if self.sys_login.fail_counter > 1:
                del self.sys_login
                self.sys_login = None
                print("Priv: Failed !")
                logger.warning("Priv: Failed !")
                if self.gui:
                    self.gui.on_channel_status_change()
                self.change_cli_state(1)
            return ""
        if self.sys_login.attempt_count == self.sys_login.attempts:
            del self.sys_login
            self.sys_login = None
            # print("END")
            self.sysop_priv = True
            if self.gui:
                self.gui.on_channel_status_change()
            self.change_cli_state(1)
        return res

    def s4(self):
        """ ry to connect other Station ( C CMD ) """
        if self.connection.LINK_Connection:
            self.connection.link_disco()
        self.change_cli_state(1)
        return self.get_ts_prompt()

    def s5(self):
        """ Do nothing / No Remote"""
        return ""
    @staticmethod
    def cron_s0():
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
    service_cli = True
    c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    bye_text = '73 ...\r'
    prompt = 'PoPT-NODE>'
    prefix = b''
    sw_id = 'PoPTNode'

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
    service_cli = False
    c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    bye_text = '73 ...\r'
    prompt = 'TEST-STATION-User-CLI>'
    prefix = b'//'
    sw_id = 'PoPT'

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
    service_cli = True
    c_text = ''
    bye_text = ''
    prompt = ''
    prefix = b''

    def cli_exec(self, inp=b''):
        pass

    def _exec_cmd(self):
        pass

    def cli_cron(self):
        pass


CLI_OPT = {
    UserCLI.cli_name: UserCLI,
    NodeCLI.cli_name: NodeCLI,
    NoneCLI.cli_name: NoneCLI,
    'PIPE': AX25Pipe
}
