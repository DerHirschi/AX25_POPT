from datetime import datetime

from cfg import constant
from cfg.popt_config import POPT_CFG
from cli.BaycomLogin import BaycomLogin
from cli.StringVARS import replace_StringVARS
from cli.cliStationIdent import get_station_id_obj
from cfg.constant import STATION_ID_ENCODING_REV
from fnc.file_fnc import get_str_fm_file
from fnc.socket_fnc import get_ip_by_hostname
from fnc.str_fnc import get_time_delta, find_decoding, get_timedelta_str_fm_sec, get_timedelta_CLIstr, \
    convert_str_to_datetime
from cfg.string_tab import STR_TABLE
from fnc.ax25_fnc import validate_ax25Call
from UserDB.UserDBmain import USER_DB
from cfg.logger_config import logger


class DefaultCLI(object):
    cli_name = ''  # DON'T CHANGE!
    service_cli = True
    # c_text = '-= Test C-TEXT =-\r\r'
    # bye_text = '73 ...\r'
    # prompt = ''
    prefix = b'//'
    sw_id = ''

    def __init__(self, connection):
        # print("CLI-INIT")
        logger.debug(f"CLI-{self.cli_name}: Init")
        stat_cfg: dict = connection.get_stat_cfg()
        self._stat_cfg_index_call = stat_cfg.get('stat_parm_Call', 'NOCALL')

        self._c_text = self._load_fm_file(self._stat_cfg_index_call + '.ctx')
        self._connection = connection
        self._port_handler = self._connection.get_port_handler_CONN()
        self._own_port = self._connection.own_port
        # self.channel_index = self._connection.ch_index
        self._gui = self._port_handler.get_gui()

        self._my_call_str = self._connection.my_call_str
        self._to_call_str = self._connection.to_call_str
        self._user_db = USER_DB
        self._user_db_ent = self._connection.user_db_ent
        self._encoding = 'UTF-8', 'ignore'
        self._stat_identifier_str = ''
        if self._user_db_ent:
            self._encoding = self._user_db_ent.Encoding, 'ignore'
            self._stat_identifier_str = self._user_db_ent.software_str
            if self._user_db_ent.CText:
                self._c_text = str(self._user_db_ent.CText)

        self.stat_identifier = get_station_id_obj(self._stat_identifier_str)
        # print(f"CLI STST ID : {self.stat_identifier}")
        # print(f"CLI STST str : {self.stat_identifier_str}")

        self._c_text = self._c_text.replace('\n', '\r')

        self.time_start = datetime.now()

        self._state_index = 0
        self._crone_state_index = 0
        self._input = b''
        self._raw_input = b''
        self._cmd = b''
        self._last_line = b''
        self._new_last_line = b''   # TODO ???????????????????????
        self._parameter = []
        self._sys_login = None
        self.sysop_priv = False
        # Crone
        self._cron_state_exec = {
            0: self.cron_s0,  # No CMDs / Doing nothing
            100: self.cron_s_quit  # QUIT
        }
        # Standard Commands ( GLOBAL )
        self._commands = {
            # CMD: (needed lookup len(cmd), cmd_fnc, HElp-Str)
            'QUIT': (1, self._cmd_q, 'Quit'),
            'BYE': (1, self._cmd_q, 'Bye'),
            'CONNECT': (1, self._cmd_connect, 'Connect'),
            'ECHO': (1, self._cmd_echo, 'Echo'),
            'PORT': (1, self._cmd_port, 'Ports'),
            'MH': (0, self._cmd_mh, 'MYHeard List'),
            'LMH': (0, self._cmd_mhl, 'Long MYHeard List'),
            'AXIP': (2, self._cmd_axip, 'AXIP-MH List'),
            'ATR': (2, self._cmd_aprs_trace, 'APRS-Tracer'),
            'DXLIST': (2, self._cmd_dxlist, 'DX/Tracer Alarm List'),
            'LCSTATUS': (2, self._cmd_lcstatus, STR_TABLE['cmd_help_lcstatus'][self._connection.cli_language]),
            'WX': (0, self._cmd_wx, STR_TABLE['cmd_help_wx'][self._connection.cli_language]),
            'BELL': (2, self._cmd_bell, STR_TABLE['cmd_help_bell'][self._connection.cli_language]),

            'INFO': (1, self._cmd_i, 'Info'),
            'LINFO': (2, self._cmd_li, 'Long Info'),
            'NEWS': (2, self._cmd_news, 'NEWS'),
            'VERSION': (3, self._cmd_ver, 'Version'),
            'USER': (0, self._cmd_user_db_detail, STR_TABLE['cmd_help_user_db'][self._connection.cli_language]),
            'NAME': (1, self._cmd_set_name, STR_TABLE['cmd_help_set_name'][self._connection.cli_language]),
            'QTH': (0, self._cmd_set_qth, STR_TABLE['cmd_help_set_qth'][self._connection.cli_language]),
            'LOC': (0, self._cmd_set_loc, STR_TABLE['cmd_help_set_loc'][self._connection.cli_language]),
            'ZIP': (0, self._cmd_set_zip, STR_TABLE['cmd_help_set_zip'][self._connection.cli_language]),
            'PRMAIL': (0, self._cmd_set_pr_mail, STR_TABLE['cmd_help_set_prmail'][self._connection.cli_language]),
            'EMAIL': (0, self._cmd_set_e_mail, STR_TABLE['cmd_help_set_email'][self._connection.cli_language]),
            'WEB': (3, self._cmd_set_http, STR_TABLE['cmd_help_set_http'][self._connection.cli_language]),
            'LANG': (0, self._cmd_lang, STR_TABLE['cli_change_language'][self._connection.cli_language]),
            'UMLAUT': (2, self._cmd_umlaut, STR_TABLE['auto_text_encoding'][self._connection.cli_language]),
            'POPT': (0, self._cmd_popt_banner, 'PoPT Banner'),
            'HELP': (1, self._cmd_help, STR_TABLE['help'][self._connection.cli_language]),
            '?': (0, self._cmd_shelp, STR_TABLE['cmd_shelp'][self._connection.cli_language]),

        }

        self._str_cmd_exec = {
            b'#REQUESTNAME:': self.str_cmd_req_name,
            b'#NAM#': self._cmd_set_name,
            b'#QTH#': self._cmd_set_qth,
            b'#LOC#': self._cmd_set_loc,
        }

        self._state_exec = {
            0: self.s0,  # C-Text
            1: self.s1,  # Cmd Handler
            2: self.s2,  # Nothing / no remote !!! Override in NODECLI ...
            3: self.s3,  # Baycom Login Shit
            4: self.s4,  # Try to connect other Station ( C CMD )
            5: self.s5,  # Nothing / no remote
        }
        self._cmd_exec_ext = {}  # Extern Command's ??
        self._cron_state_exec_ext = {}  # Extern Tasks ??
        self._state_exec_ext = {}  # Extern State Tab ??
        self.init()
        self._cron_state_exec.update(self._cron_state_exec_ext)
        self._commands.update(self._cmd_exec_ext)
        self._state_exec.update(self._state_exec_ext)
        """
        if type(self.prefix) is str:  # Fix for old CFG Files
            self.prefix = self.prefix.encode(self._encoding[0], self._encoding[1])
        """


    def init(self):
        """
        self._cmd_exec_ext = {}
        self.cron_state_exec_ext = {}
        self.state_exec_ext = {}
        """
        pass


    def get_ts_prompt(self):
        return f"\r{self._my_call_str} ({datetime.now().strftime('%H:%M:%S')})>"

    def send_output(self, ret, env_vars=True):
        if ret:
            if type(ret) is str:
                if env_vars:
                    ret = replace_StringVARS(ret,
                                             port=self._own_port,
                                             port_handler=self._port_handler,
                                             connection=self._connection,
                                             user_db=self._user_db)
                ret = ret.encode(self._encoding[0], self._encoding[1])
                ret = ret.replace(b'\n', b'\r')
            self._connection.tx_buf_rawData += ret

    """
    def send_2_gui(self, data):  
        if data:
            if type(data) != str:
                data = data.decode(self.encoding[0], self.encoding[1])
            # print(data + ' <CLI> ' + str(self._connection.ch_index))
            self._gui.cli_echo(data, self._connection.ch_index)
    """

    def change_cli_state(self, state: int):
        self._state_index = state

    def is_prefix(self):
        # TODO Cleanup !!!!
        if self.prefix:
            self._input = self._input.replace(b'\n', b'\r')
            # self.input = self.input.split(b'\r')[0]
            self._input = self._input.split(b'\r')
            while self._input:
                if self._input[0]:
                    break
                else:
                    self._input = self._input[1:]
            if not self._input:
                return False
            self._input = self._input[0]

            if self._input[:len(self.prefix)] == self.prefix:
                self._parameter = []
                cmd = self._input[len(self.prefix):]
                cmd = cmd.split(b' ')
                if len(cmd) > 1:
                    self._input = cmd[1:]
                    self._parameter = cmd[1:]
                else:
                    self._input = b''

                cmd = cmd[0]
                self._cmd = cmd \
                    .upper() \
                    .replace(b' ', b'') \
                    .replace(b'\r', b'')
                # self.input = self.input[len(self.prefix):]
                return True
            else:
                # Message is for User ( Text , Chat )
                return False
        # CMD Input for No User Terminals ( Node ... )
        self._parameter = []
        cmd = self._input
        cmd = cmd.split(b' ')
        if len(cmd) > 1:
            self._input = cmd[1:]
            self._parameter = cmd[1:]
        else:
            self._input = b''
        cmd = cmd[0]
        self._cmd = cmd \
            .upper() \
            .replace(b'\r', b'') \
            .replace(b'//', b'')

        return False

    def _load_fm_file(self, filename: str):
        file_n = constant.CFG_data_path + \
                 constant.CFG_usertxt_path + \
                 self._stat_cfg_index_call + '/' + \
                 filename
        out = get_str_fm_file(file_n)
        if out:
            return out
        return ''

    def start_baycom_login(self, login_cmd=''):
        if self._sys_login is None:
            if self._user_db_ent:
                if self._user_db_ent.sys_pw:
                    self._sys_login = BaycomLogin(
                        sys_pw_parm=self._user_db_ent.sys_pw_parm,
                        sys_pw=self._user_db_ent.sys_pw,
                        login_cmd=login_cmd
                    )
                    self.send_output(self._sys_login.start(), env_vars=False)
                    self.change_cli_state(3)

    def _send_sw_id(self):
        if not self.sw_id:
            return ""
        unknown = '?'
        didadit = ''  # True = 'D'
        txt_enc = '4'  # UTF-8
        if self._user_db_ent:
            if self._user_db_ent.Name:
                unknown = ''
            if self._user_db_ent.Encoding:
                try:
                    txt_enc = str(STATION_ID_ENCODING_REV[self._user_db_ent.Encoding])
                except KeyError:
                    logger.error(f"KeyERROR STATION_ID_ENCODING_REV (constant.py): {self._user_db_ent.Encoding}")
        flag = txt_enc + didadit + unknown
        return '{' + f"{self.sw_id}-{constant.VER}-{flag}" + '}\r'

    def _set_user_db_software_id(self):
        if self._user_db_ent:
            self._user_db_ent.software_str = str(self.stat_identifier.id_str)
            self._user_db_ent.Software = str(self.stat_identifier.software) + '-' + str(self.stat_identifier.version)
            # if not self._user_db_ent.TYP:
            self._user_db_ent.TYP = str(self.stat_identifier.typ)

    def _software_identifier(self):
        res = self._find_sw_identifier()
        if res and self.stat_identifier:
            # print(f"SW-ID flag: {self.stat_identifier.flags}")
            # print(f"SW-ID txt_encoding: {self.stat_identifier.txt_encoding}")
            if self.stat_identifier.knows_me is not None:
                if not self.stat_identifier.knows_me:
                    self._send_name_cmd_back()
            if self.stat_identifier.txt_encoding is not None:
                self._encoding = self.stat_identifier.txt_encoding, 'ignore'
                if self._user_db_ent:
                    self._user_db_ent.Encoding = self.stat_identifier.txt_encoding

    def _send_name_cmd_back(self):

        stat_cfg: dict = self._connection.get_stat_cfg()
        name = stat_cfg.get('stat_parm_Name', '')
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
            inp_lines = self._last_line + self._raw_input
            inp_lines = inp_lines.replace(b'\n', b'\r')
            inp_lines = inp_lines.decode(self._encoding[0], 'ignore')
            inp_lines = inp_lines.split('\r')
            # print(f"find_stat_identifier inp_lines: {inp_lines}")
            for li in inp_lines:
                temp_stat_identifier = get_station_id_obj(li)
                if temp_stat_identifier is not None:
                    self.stat_identifier = temp_stat_identifier
                    self._set_user_db_software_id()
                    return True
        elif not self._last_line and self.stat_identifier:
            inp_lines = self._raw_input
            inp_lines = inp_lines.replace(b'\n', b'\r')
            inp_lines = inp_lines.decode(self._encoding[0], 'ignore')
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
        if self._cmd:
            inp_cmd = str(self._cmd.decode(self._encoding[0], 'ignore'))
            inp_cmd = inp_cmd.replace(' ', '')
            cmds = list(self._commands.keys())
            treffer = []
            for cmd in cmds:
                if self._commands[cmd][0]:
                    if inp_cmd == cmd[:self._commands[cmd][0]]:
                        self._cmd = b''
                        ret = tuple(self._commands[cmd])[1]()
                        self._new_last_line = b''
                        if ret:
                            return ret
                        return ''
                if inp_cmd == cmd[:len(inp_cmd)]:
                    treffer.append(cmd)
            if not treffer:
                return f"\r # {STR_TABLE['cmd_not_known'][self._connection.cli_language]}\r"
            if len(treffer) > 1:
                return (f"\r # {STR_TABLE['cmd_not_known'][self._connection.cli_language]}"
                        f"\r # {(' '.join(treffer))} ?\r")
            self._cmd = b''
            if not callable(self._commands[treffer[0]][1]):
                return ''
            ret = tuple(self._commands[treffer[0]])[1]()
            # self.last_line = b''
            self._new_last_line = b''
            if ret:
                return ret
            return ''

        return f"\r # {STR_TABLE['cmd_not_known'][self._connection.cli_language]}\r"

    def _exec_cmd(self):
        self._input = self._last_line + self._input
        if self.is_prefix():
            return self._find_cmd()
        # Message is for User ( Text , Chat )
        if self.prefix:
            return ''
        # CMD Input for No User Terminals ( Node ... )
        ret = self._find_cmd()
        if self._crone_state_index not in [100] and \
                self._state_index not in [2, 4]:  # Not Quit
            ret += self.get_ts_prompt()
        return ret

    def _exec_str_cmd(self):
        inp_lines = self._last_line + self._raw_input
        inp_lines = inp_lines.replace(b'\n', b'\r')
        inp_lines = inp_lines.split(b'\r')
        ret = ''
        self._new_last_line = inp_lines[-1]
        for li in inp_lines:
            for str_cmd in list(self._str_cmd_exec.keys()):
                if str_cmd in li:
                    self._cmd = str_cmd
                    self._parameter = [li[len(str_cmd):]]
                    ret = self._str_cmd_exec[str_cmd]()
                    self._cmd = b''
                    self.send_output(ret, env_vars=False)
                    self._last_line = b''
                    self._new_last_line = b''
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
            for el in self._parameter:
                tmp.append(el.decode(self._encoding[0], 'ignore').replace('\r', ''))
        else:
            for el in defaults:
                if len(self._parameter) > len(tmp):
                    tmp_parm = self._parameter[len(tmp)].decode(self._encoding[0], 'ignore').replace('\r', '')
                    try:
                        tmp_parm = type(el)(tmp_parm)
                    except ValueError:
                        tmp_parm = defaults[len(tmp)]
                else:
                    tmp_parm = defaults[len(tmp)]
                tmp.append(tmp_parm)
        self._parameter = list(tmp)

    def _cmd_connect(self):
        # print(f'cmd_connect() param: {self.parameter}')
        self._decode_param()
        # print(f'cmd_connect() param.decode: {self.parameter}')

        if not self._parameter:
            ret = '\r # Bitte Call eingeben..\r'
            return ret

        dest_call = str(self._parameter[0]).upper()
        if not validate_ax25Call(dest_call):
            ret = '\r # Ungültiger Ziel Call..\r'
            return ret

        # port_id = self.own_port.port_id
        port_id = -1
        # vias = [self._connection.my_call_str]
        vias = []
        port_tr = False
        if len(self._parameter) > 1:
            if self._parameter[-1].isdigit():
                port_tr = True
                try:
                    port_id = int(self._parameter[-1])
                except ValueError:
                    ret = '\r # Ungültige Port angabe..\r'
                    return ret

                if port_id not in self._port_handler.get_all_ports().keys():
                    ret = '\r # Ungültiger Port..\r'
                    return ret
            if port_tr:
                parm = self._parameter[1:-1]
            else:
                parm = self._parameter[1:]

            for call in parm:
                if validate_ax25Call(call.upper()):
                    vias.append(call.upper())
                else:
                    break

        conn = self._port_handler.new_outgoing_connection(
            own_call=self._to_call_str,
            dest_call=dest_call,
            via_calls=vias,
            port_id=port_id,
            link_conn=self._connection,
            # link_call=str(self._connection.my_call_str)
        )
        if conn[0]:
            self._state_index = 4
            return conn[1]
        return f'\r*** Link Busy: {conn[1]}\r'

    def _cmd_echo(self):  # Quit
        ret = ''
        # print(f"Echo Param: {self.parameter}")
        for el in self._parameter:
            ret += el.decode(self._encoding[0], self._encoding[1]) + ' '
        # print(f"Echo ret: {ret}")
        return ret[:-1] + '\r'

    def _cmd_q(self):  # Quit
        # self._connection: AX25Conn
        # self._connection.tx_buf_rawData += self.bye_text.encode(self.encoding[0], self.encoding[1])
        conn_dauer = get_time_delta(self.time_start)
        ret = f"\r # {STR_TABLE['time_connected'][self._connection.cli_language]}: {conn_dauer}\r\r"
        ret += self._load_fm_file(self._stat_cfg_index_call + '.btx') + '\r'
        self.send_output(ret, env_vars=True)
        self._crone_state_index = 100  # Quit State
        return ''

    def _cmd_lang(self):
        if not self._parameter:
            return f'\r # {STR_TABLE["cli_no_lang_param"][self._connection.cli_language]}{" ".join(list(constant.LANG_IND.keys()))}\r'
        self._decode_param()
        if self._parameter[0].upper() in constant.LANG_IND.keys():
            self._connection.set_user_db_language(constant.LANG_IND[self._parameter[0].upper()])
            return f'\r # {STR_TABLE["cli_lang_set"][self._connection.cli_language]}\r'
        return f'\r # {STR_TABLE["cli_no_lang_param"][self._connection.cli_language]}{" ".join(list(constant.LANG_IND.keys()))}\r'

    def _cmd_dxlist(self):
        parm = 10
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except ValueError:
                pass
        ret = self._get_alarm_out_cli(max_ent=parm)

        return ret + '\r'

    def _get_alarm_out_cli(self, max_ent=10):
        alarm_his = dict(self._port_handler.get_MH().dx_alarm_perma_hist)
        alarm_his.update(dict(self._port_handler.get_aprs_ais().be_tracer_alarm_hist))
        if not alarm_his:
            return f'\r # {STR_TABLE["cli_no_data"][self._connection.cli_language]}\r'
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
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except ValueError:
                pass
        ret = self._get_axip_out_cli(max_ent=parm)

        return ret + '\r'

    def _get_axip_out_cli(self, max_ent=10):
        ent = self._port_handler.get_MH().get_sort_mh_entry('last', reverse=False)
        dbl_ent = []
        if not ent:
            return f'\r # {STR_TABLE["cli_no_data"][self._connection.cli_language]}\r'
        max_c = 0
        out = '\r'
        # out += '\r                       < AXIP - Clients >\r\r'
        out += '-Call------IP:Port---------------------------Last------------\r'
        for k in ent.keys():
            if ent[k].own_call not in dbl_ent:
                dbl_ent.append(ent[k].own_call)
                axip_add = self._port_handler.get_MH().get_AXIP_fm_DB_MH(ent[k].own_call)
                if axip_add[0]:
                    max_c += 1
                    if max_c > max_ent:
                        break
                    out += ' {:9} {:33} {:8}\r'.format(
                        ent[k].own_call,
                        axip_add[0] + ':' + str(axip_add[1]),
                        get_timedelta_CLIstr(ent[k].last_seen, r_just=False)
                    )
        return out

    def _cmd_mh(self):
        last_port_id = len(self._port_handler.get_all_port_ids())
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
        parm = self._parameter[0]
        if parm < last_port_id:
            port = self._parameter[0]
            if self._parameter[1] == -1:
                parm = 20
            else:
                parm = self._parameter[1]
        else:
            port = self._parameter[1]

        ret = self._get_mh_out_cli(max_ent=parm, port_id=port)

        return ret + '\r'

    def _get_mh_out_cli(self, max_ent=20, port_id=-1):
        sort_list = self._port_handler.get_MH().get_sort_mh_entry('last', False)
        if not sort_list:
            return f'\r # {STR_TABLE["cli_no_data"][self._connection.cli_language]}\r'
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
            return f'\r # {STR_TABLE["cli_no_data"][self._connection.cli_language]}\r'
        return '\r' + out

    def _cmd_mhl(self):
        last_port_id = len(self._port_handler.get_all_port_ids())
        if last_port_id > 10:
            max_ent = int(last_port_id)
        else:
            max_ent = 10
        self._decode_param(defaults=[
            max_ent,  # Entry's
            -1,  # Port
        ])

        parm = self._parameter[0]
        if parm < last_port_id:
            port = self._parameter[0]
            if self._parameter[1] == -1:
                parm = 10
            else:
                parm = self._parameter[1]
        else:
            port = self._parameter[1]

        ret = self._get_mh_long_out_cli(max_ent=parm, port_id=port)

        return ret + '\r'

    def _get_mh_long_out_cli(self, max_ent=10, port_id=-1):
        sort_list = self._port_handler.get_MH().get_sort_mh_entry('last', False)
        if not sort_list:
            return f'\r # {STR_TABLE["cli_no_data"][self._connection.cli_language]}\r'
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
            return f'\r # {STR_TABLE["cli_no_data"][self._connection.cli_language]}\r'
        return "\r-----Time-Port-Call------via-------LOC------Dist(km)--Type---Packets\r" + out

    def _cmd_wx(self):
        """ WX Stations """
        if self._port_handler.aprs_ais is None:
            return f'\r # {STR_TABLE["cli_no_wx_data"][self._connection.cli_language]}\r\r'
        parm = 10
        ret = ''
        self._decode_param()
        if self._parameter:
            if self._parameter[0].isdigit():
                try:
                    parm = int(self._parameter[0])
                except ValueError:
                    pass
                ret = self._get_wx_cli_out(max_ent=parm)
            else:
                call = str(self._parameter[0]).upper()
                if validate_ax25Call(call):
                    le = parm
                    if len(self._parameter) == 2:
                        try:
                            le = int(self._parameter[1])
                        except ValueError:
                            pass
                    ret = self._get_wx_fm_call_cli_out(call=call, max_ent=le)
        else:
            ret = self._get_wx_cli_out(max_ent=parm)
        if not ret:
            return f'\r # {STR_TABLE["cli_no_wx_data"][self._connection.cli_language]}\r\r'
        return ret + '\r'

    def _get_wx_fm_call_cli_out(self, call, max_ent=10):
        data = list(self._port_handler.aprs_ais.get_wx_data_f_call(call))
        if not data:
            return ''
        data.reverse()
        data_len = len(data)
        max_c = 0
        loc = f'{data[0][12][:6]}({data[0][16]}km)'
        out = '\r'
        out += f'WX-Station: {call}\r'
        out += f'Locator   : {loc}\r'
        out += f'Comment   : {data[0][11]}\r'
        out += f'Datapoints: {data_len}\r\r'
        out += '-----Last-Port--Temp-Press---Hum-Lum-Rain(24h)-WindGust\r'
        for el in data:
            max_c += 1
            if max_c > max_ent:
                break
            # _ent = self._port_handler.aprs_ais.aprs_wx_msg_pool[k][-1]
            # td = get_timedelta_CLIstr(el[15].split(' ')[-1])
            td = el[15].split(' ')[-1]
            # pres = f'{el[0]:.2f}'
            pres = f'{el[0]}'
            # rain = f'{el[3]:.3f}'
            rain = f'{el[3]}'
            # out += f'{td.rjust(9):10}{"":6}'
            out += f'{td.rjust(9):10}{el[-1]:6}'
            out += f'{str(el[5]):5}'
            out += f'{pres:7} '
            out += f'{el[1]:3} '
            out += f'{el[9]:3} '
            out += f'{rain:9} '
            # out += f'{el[7]:.3f}\r'
            out += f'{el[7]}\r'
        return out

    def _get_wx_cli_out(self, max_ent=10):
        db = self._port_handler.get_database()
        if not db:
            return ''

        # _data = self._port_handler.aprs_ais.get_wx_entry_sort_distance()
        data = db.aprsWX_get_data_f_CLItree(last_rx_days=3)
        if not data:
            return ''

        max_c = 0
        out = '\r-----Last-Port--Call------LOC-------------Temp-Press---Hum-Lum-Rain(24h)-\r'
        for el in data:
            max_c += 1
            if max_c > max_ent:
                break
            # _ent = self._port_handler.aprs_ais.aprs_wx_msg_pool[k][-1]
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

    def _cmd_aprs_trace(self):
        """APRS Tracer"""
        if self._port_handler.aprs_ais is None:
            return f'\r # {STR_TABLE["cli_no_tracer_data"][self._connection.cli_language]}\r\r'
        parm = 10
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except ValueError:
                pass
        data = self._port_handler.aprs_ais.tracer_traces_get()
        if not data:
            return f'\r # {STR_TABLE["cli_no_tracer_data"][self._connection.cli_language]}\r\r'
        intervall = self._port_handler.aprs_ais.be_tracer_interval
        active = self._port_handler.aprs_ais.be_tracer_active
        last_send = self._port_handler.aprs_ais.tracer_get_last_send()
        last_send = get_timedelta_str_fm_sec(last_send, r_just=False)
        if not active:
            intervall_str = 'off'
        else:
            intervall_str = str(intervall)
        # out = '\r # APRS-Tracer Beacon\r\r'
        out = '\r'
        out += f'Tracer Port     : {self._port_handler.aprs_ais.be_tracer_port}\r'
        out += f'Tracer Call     : {self._port_handler.aprs_ais.be_tracer_station}\r'
        out += f'Tracer WIDE Path: {self._port_handler.aprs_ais.be_tracer_wide}\r'
        out += f'Tracer intervall: {intervall_str}\r'
        out += f'Auto Tracer     : {constant.BOOL_ON_OFF.get(self._port_handler.aprs_ais.be_auto_tracer_active, False).lower()}\r'
        # out += f'APRS-Server     : {constant.BOOL_ON_OFF.get(self._port_handler.aprs_ais., False).lower()}\r'
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
    def _cmd_popt_banner():
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
    def _cmd_ver():
        ret = '\r-= P.yton o.ther P.acket T.erminal =-\r' \
              '-= Version: {} \r\r'.format(constant.VER)
        return ret

    def _cmd_i(self):
        ret = self._load_fm_file(self._stat_cfg_index_call + '.itx')
        return ret.replace('\n', '\r')


    def _cmd_li(self):
        ret = self._load_fm_file(self._stat_cfg_index_call + '.litx')
        return ret.replace('\n', '\r')


    def _cmd_news(self):
        ret = self._load_fm_file(self._stat_cfg_index_call + '.atx')
        return ret.replace('\n', '\r')


    def _cmd_user_db_detail(self):
        if not self._parameter:
            max_entry = 20  # TODO: from parameter
            _db_list = list(self._user_db.db.keys())
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
            call_str = self._parameter[0].decode(self._encoding[0], self._encoding[1]).upper()

            if validate_ax25Call(call_str):
                if call_str in self._user_db.db.keys():
                    header = "\r" \
                             f"| USER-DB: {call_str}\r" \
                             "|-------------------\r"
                    ent = self._user_db.db[call_str]
                    ent_ret = ""
                    for att in dir(ent):
                        if '__' not in att and \
                                att not in self._user_db.not_public_vars:
                            if getattr(ent, att):
                                ent_ret += f"| {att.ljust(10)}: {getattr(ent, att)}\r"

                    ent_ret += "|-------------------\r\r"
                    return header + ent_ret

            return "\r" \
                   f"{STR_TABLE['cli_no_user_db_ent'][self._connection.cli_language]}" \
                   "\r"

    def _cmd_set_name(self):
        if not self._parameter:
            if self._user_db_ent:
                return f" #\r Name: {self._user_db_ent.Name}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.Name = self._parameter[0] \
                .decode(self._encoding[0], self._encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_name_set'][self._connection.cli_language]}: {self._user_db_ent.Name}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_name NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_set_qth(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # QTH: {self._user_db_ent.QTH}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.QTH = self._parameter[0] \
                .decode(self._encoding[0], self._encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_qth_set'][self._connection.cli_language]}: {self._user_db_ent.QTH}" \
                   "\r"

        logger.error("User-DB Error. cli_qth_set NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_set_loc(self):
        if not self._parameter:
            if self._user_db_ent:
                if self._user_db_ent.Distance:
                    return f"\r # Locator: {self._user_db_ent.LOC} > {round(self._user_db_ent.Distance)} km\r"
                return f"\r # Locator: {self._user_db_ent.LOC}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.LOC = self._parameter[0] \
                .decode(self._encoding[0], self._encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = datetime.now()
            # self._connection.set_distance()
            self._user_db.set_distance(self._user_db_ent.call_str)
            if self._user_db_ent.Distance:
                return "\r" \
                       f"{STR_TABLE['cli_loc_set'][self._connection.cli_language]}: {self._user_db_ent.LOC}" \
                       "\r"
            return "\r" \
                   f"{STR_TABLE['cli_loc_set'][self._connection.cli_language]}: {self._user_db_ent.LOC} > {round(self._user_db_ent.Distance)} km" \
                   "\r"

        logger.error("User-DB Error. cmd_set_loc NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_set_zip(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # ZIP: {self._user_db_ent.ZIP}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.ZIP = self._parameter[0] \
                .decode(self._encoding[0], self._encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_zip_set'][self._connection.cli_language]}: {self._user_db_ent.ZIP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_zip NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_set_pr_mail(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # PR-Mail: {self._user_db_ent.PRmail}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.PRmail = self._parameter[0] \
                .decode(self._encoding[0], self._encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_prmail_set'][self._connection.cli_language]}: {self._user_db_ent.PRmail}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_pr_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_set_e_mail(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # E-Mail: {self._user_db_ent.Email}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.Email = self._parameter[0] \
                .decode(self._encoding[0], self._encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_email_set'][self._connection.cli_language]}: {self._user_db_ent.Email}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_e_mail NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_set_http(self):
        if not self._parameter:
            if self._user_db_ent:
                return f"\r # WEB: {self._user_db_ent.HTTP}\r"
            return "\r # USER-DB Error !\r"
        if self._user_db_ent:
            self._user_db_ent.HTTP = self._parameter[0] \
                .decode(self._encoding[0], self._encoding[1]). \
                replace(' ', ''). \
                replace('\n', ''). \
                replace('\r', '')
            self._user_db_ent.last_edit = datetime.now()
            return "\r" \
                   f"{STR_TABLE['cli_http_set'][self._connection.cli_language]}: {self._user_db_ent.HTTP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_http NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_port(self):  # TODO Pipe
        ret = f"\r      < {STR_TABLE['port_overview'][self._connection.cli_language]} >\r\r"
        ret += "-#--Name----PortTyp--Stations--Typ------Digi-\r"
        for port_id in self._port_handler.ax25_ports.keys():
            port = self._port_handler.ax25_ports[port_id]
            name = str(port.portname).ljust(7)
            typ = port.port_typ.ljust(7)
            if port.dualPort_primaryPort in [port, None]:

                stations = port.my_stations
                if not stations:
                    stations = ['']
                digi = ''

                if POPT_CFG.get_digi_CFG_for_Call(stations[0]).get('digi_enabled', False) and stations[0]:
                    digi = '(DIGI)'
                if POPT_CFG.get_stat_CFG_fm_call(stations[0]):
                    digi = f"{POPT_CFG.get_stat_CFG_fm_call(stations[0]).get('stat_parm_cli', 'NO-CLI').ljust(7)} " + digi

                ret += f" {str(port_id).ljust(2)} {name} {typ}  {stations[0].ljust(9)} {digi}\r"
                for stat in stations[1:]:
                    digi = ''
                    if POPT_CFG.get_digi_CFG_for_Call(stat).get('digi_enabled', False):
                        digi = '(DIGI)'
                    if POPT_CFG.get_stat_CFG_fm_call(stat):
                        digi = f"{POPT_CFG.get_stat_CFG_fm_call(stat).get('stat_parm_cli', 'NO-CLI').ljust(7)} " + digi
                    ret += f"                     {stat.ljust(9)} {digi}\r"
            else:
                if port.dualPort_primaryPort:
                    ret += f" {str(port_id).ljust(2)} {name} {typ}  Dual-Port: Secondary from Port {port.dualPort_primaryPort.port_id} \r"
        ret += '\r'
        return ret

    def _cmd_lcstatus(self):
        """ Long Connect-Status """
        ret = '\r'
        ret += "--Ch--Port--MyCall----Call------Name----------LOC----QTH-----------Connect\r"
        all_conn = self._port_handler.get_all_connections()
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
            if self._connection.ch_index == ch:
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

    def _cmd_help(self):
        # ret = f"\r   < {STR_TABLE['help'][self._connection.cli_language]} >\r"
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
        for k in list(self._commands.keys()):
            if self._commands[k][2]:
                ret += '\r {}{:10} = {}'.format(self.prefix.decode('UTF-8', 'ignore'),
                                                k,
                                                self._commands[k][2])
        ret += '\r\r'
        return ret

    def _cmd_shelp(self):
        ret = '\r # '
        c = 0
        cmds = list(self._commands.keys())
        cmds.sort()
        for k in cmds:
            ret += (k + ' ')
            if len(ret) - c > 60:
                ret += '\r # '
                c += 60
        ret += '\r\r'
        return ret

    def _cmd_umlaut(self):
        # print(self.parameter)
        if not self._parameter:
            return f"\r{STR_TABLE['cli_text_encoding_no_param'][self._connection.cli_language]}: {self._encoding[0]}\r"
        res = find_decoding(self._parameter[0].replace(b'\r', b''))
        if not res:
            return f"\r{STR_TABLE['cli_text_encoding_error_not_found'][self._connection.cli_language]}\r"
        self._encoding = res, self._encoding[1]
        if self._user_db_ent:
            self._user_db_ent.Encoding = str(res)
        return f"\r{STR_TABLE['cli_text_encoding_set'][self._connection.cli_language]} {res}\r"

    def _cmd_bell(self):
        if not self._connection.noty_bell:
            self._connection.noty_bell = True
            msg = b' '.join(self._parameter)
            msg = msg.decode(self._encoding[0], self._encoding[1])
            self._port_handler.set_noty_bell_PH(self._connection.ch_index, msg)
            return f'\r # {STR_TABLE["cmd_bell"][self._connection.cli_language]}\r'
        return f'\r # {STR_TABLE["cmd_bell_again"][self._connection.cli_language]}\r'

    ##############################################
    def str_cmd_req_name(self):
        name = self._connection.stat_cfg.stat_parm_Name
        qth = self._gui.own_qth
        # qth = self._connection.stat_cfg.stat_parm_QTH
        loc = self._gui.own_loc
        # loc = self._connection.stat_cfg.stat_parm_LOC
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
        tmp = self._parameter[0]
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
        if self._user_db_ent:
            if not self._user_db_ent.Name:
                req_name = '+'
            if not self._user_db_ent.QTH:
                req_qth = '+'
            if not self._user_db_ent.LOC:
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
        # print(f"cli_exec {self.cli_name}: {self._connection.uid} - SI: {self.state_index} - CSI: {self.crone_state_index}")
        # print(f"cli_exec {self.cli_name}: {self._connection.uid} - raw-input: {inp}")
        # if not self._connection.is_link:
        self._raw_input = bytes(inp)
        ret = self._state_exec[self._state_index]()
        self.send_output(ret)

    def cli_cron(self):
        """ Global Crone Tasks """
        if not self._connection.is_link:
            self.cli_state_crone()

    def cli_state_crone(self):
        """ State Crone Tasks """
        ret = self._cron_state_exec[self._crone_state_index]()
        self.send_output(ret)

    def s0(self):  # C-Text
        self._state_index = 1
        if self.prefix:
            return self._send_sw_id() + self._c_text
        else:
            return self._send_sw_id() + self._c_text + self.get_ts_prompt()

    def s1(self):
        self._software_identifier()
        ########################
        # Check String Commands
        if not self._exec_str_cmd():
            self._input = self._raw_input
            self.send_output(self._exec_cmd())
        self._last_line = self._new_last_line
        return ''

    def s2(self):
        """ Do nothing / No Remote"""
        """ !!! Override in NODECLI"""
        return ""

    def s3(self):
        """ Sys Login """
        if self._sys_login is None:
            self.change_cli_state(1)
            return ""

        inp = self._raw_input.decode(self._encoding[0], 'ignore')
        if 'OK\r' in inp:
            del self._sys_login
            self._sys_login = None
            # print("END")
            self.sysop_priv = True
            if self._gui:
                self._gui.on_channel_status_change()
            self.change_cli_state(1)
            return ''
        res = self._sys_login.step(inp)
        if not res:
            if self._sys_login.fail_counter > 1:
                del self._sys_login
                self._sys_login = None
                # print("Priv: Failed !")
                logger.warning("Priv: Failed !")
                if self._gui:
                    self._gui.on_channel_status_change()
                self.change_cli_state(1)
            return ""
        if self._sys_login.attempt_count == self._sys_login.attempts:
            del self._sys_login
            self._sys_login = None
            # print("END")
            self.sysop_priv = True
            if self._gui:
                self._gui.on_channel_status_change()
            self.change_cli_state(1)
        return res

    def s4(self):
        """ ry to connect other Station ( C CMD ) """
        if self._connection.LINK_Connection:
            # print(f'CLI LinkDisco : {self._connection.uid}')
            self._connection.link_disco()
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
        # self._connection: AX25Conn
        if not self._connection.tx_buf_rawData and \
                not self._connection.tx_buf_unACK and \
                not self._connection.tx_buf_2send:
            if self._connection.zustand_exec.stat_index not in [0, 1, 4]:
                self._connection.zustand_exec.change_state(4)


class NodeCLI(DefaultCLI):
    cli_name = 'NODE'  # DON'T CHANGE !
    service_cli = True
    # _c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    # bye_text = '73 ...\r'
    # prompt = 'PoPT-NODE>'
    prefix = b''
    sw_id = 'PoPTNode'

    # Extra CMDs for this CLI

    def init(self):
        """
        self._cmd_exec_ext = {}
        self._cron_state_exec_ext = {}
        self._state_exec_ext = {
            2: self.s2
        }
        """
        pass

    def s2(self):
        return self._cmd_q()


class UserCLI(DefaultCLI):
    cli_name = 'USER'  # DON'T CHANGE !
    service_cli = False
    # _c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    # bye_text = '73 ...\r'
    # prompt = 'TEST-STATION-User-CLI>'
    prefix = b'//'
    sw_id = 'PoPT'

    # Extra CMDs for this CLI

    def init(self):
        """
        self._cmd_exec_ext = {}
        self._cron_state_exec_ext = {}
        self._state_exec_ext = {
            2: self.s2
        }
        """
        pass

    def s2(self):
        return self._cmd_q()

class NoneCLI(DefaultCLI):
    """ ? To Disable CLI / Remote ? """
    cli_name = 'NO-CLI'  # DON'T CHANGE !
    service_cli = False
    # _c_text = ''
    # bye_text = ''
    prefix = b''

    def cli_exec(self, inp=b''):
        pass

    def _exec_cmd(self):
        pass

    def cli_cron(self):
        pass

class MCastCLI(DefaultCLI):
    cli_name = 'MCAST'  # DON'T CHANGE !
    service_cli = True
    prefix = b''
    sw_id = 'PoPTMCast'

    # Extra CMDs for this CLI

    def init(self):
        # NO USER-DB Ctext
        self._c_text = self._load_fm_file(self._stat_cfg_index_call + '.ctx')
        self._c_text = self._c_text.replace('\n', '\r')
        # Standard Commands ( GLOBAL )
        self._commands = {
            # CMD: (needed lookup len(cmd), cmd_fnc, HElp-Str)
            'QUIT': (1, self._cmd_q, 'Quit'),
            'BYE': (1, self._cmd_q, 'Bye'),
            'AXIP': (2, self._cmd_axip, 'AXIP-MH List'),
            'LCSTATUS': (2, self._cmd_lcstatus, STR_TABLE['cmd_help_lcstatus'][self._connection.cli_language]),
            'BELL': (2, self._cmd_bell, STR_TABLE['cmd_help_bell'][self._connection.cli_language]),
            # MCAST ######################################################
            'CH': (2, self._cmd_mcast_move_channel, STR_TABLE['cmd_help_mcast_move_ch'][self._connection.cli_language]),
            'CHLIST': (3, self._cmd_mcast_channels, STR_TABLE['cmd_help_mcast_channels'][self._connection.cli_language]),
            'CHINFO': (3, self._cmd_mcast_channel_info, STR_TABLE['cmd_help_mcast_ch_info'][self._connection.cli_language]),
            'SETAXIP': (5, self._cmd_mcast_set_member_axip, STR_TABLE['cmd_help_mcast_set_axip'][self._connection.cli_language]),
            ##############################################################
            'INFO': (1, self._cmd_i, 'Info'),
            'LINFO': (2, self._cmd_li, 'Long Info'),
            'NEWS': (2, self._cmd_news, 'NEWS'),
            'VERSION': (3, self._cmd_ver, 'Version'),
            'USER': (0, self._cmd_user_db_detail, STR_TABLE['cmd_help_user_db'][self._connection.cli_language]),
            'NAME': (1, self._cmd_set_name, STR_TABLE['cmd_help_set_name'][self._connection.cli_language]),
            'QTH': (0, self._cmd_set_qth, STR_TABLE['cmd_help_set_qth'][self._connection.cli_language]),
            'LOC': (0, self._cmd_set_loc, STR_TABLE['cmd_help_set_loc'][self._connection.cli_language]),
            'ZIP': (0, self._cmd_set_zip, STR_TABLE['cmd_help_set_zip'][self._connection.cli_language]),
            'PRMAIL': (0, self._cmd_set_pr_mail, STR_TABLE['cmd_help_set_prmail'][self._connection.cli_language]),
            'EMAIL': (0, self._cmd_set_e_mail, STR_TABLE['cmd_help_set_email'][self._connection.cli_language]),
            'WEB': (3, self._cmd_set_http, STR_TABLE['cmd_help_set_http'][self._connection.cli_language]),
            'LANG': (0, self._cmd_lang, STR_TABLE['cli_change_language'][self._connection.cli_language]),
            'UMLAUT': (2, self._cmd_umlaut, STR_TABLE['auto_text_encoding'][self._connection.cli_language]),
            'HELP': (1, self._cmd_help, STR_TABLE['help'][self._connection.cli_language]),
            '?': (0, self._cmd_shelp, STR_TABLE['cmd_shelp'][self._connection.cli_language]),

        }
        self._state_exec = {
            0: self.s0,  # C-Text
            1: self.s1,  # Cmd Handler
        }

    ###############################################

    def cli_exec(self, inp=b''):
        self._raw_input = bytes(inp)
        ret = self._state_exec[self._state_index]()
        self.send_output(ret)

    def cli_cron(self):
        """ Global Crone Tasks """
        if not self._connection.is_link:
            self.cli_state_crone()

    def cli_state_crone(self):
        """ State Crone Tasks """
        ret = self._cron_state_exec[self._crone_state_index]()
        self.send_output(ret)

    def s0(self):  # C-Text
        self._state_index = 1
        out =  self._send_sw_id()
        out += self._c_text
        out += f"\r{self._cmd_mcast_channels()}"
        out += f"\r # {self._register_mcast_member()}\r" # TODO Extra CMD etc.
        out += self.get_ts_prompt()
        return out

    def s1(self):
        self._software_identifier()
        ########################
        # Check String Commands
        if not self._exec_str_cmd():
            self._input = self._raw_input
            self.send_output(self._exec_cmd())
        self._last_line = self._new_last_line
        return ''

    #############################################################
    def _register_mcast_member(self):
        mcast_server = self._port_handler.get_mcast_server()
        if not hasattr(mcast_server, 'register_new_member'):
            logger.error("CLI: Attribute Error Mcast-Server. _register_mcast_member()")
            return 'CLI: Attribute Error Mcast-Server'
        return mcast_server.register_new_member(self._to_call_str)

    def _cmd_mcast_move_channel(self):
        mcast_server = self._port_handler.get_mcast_server()
        if not hasattr(mcast_server, 'move_channel'):
            logger.error("CLI: Attribute Error Mcast-Server. _cmd_mcast_move_channel()")
            return '\r # MCast: Attribute Error Mcast-Server\r'

        if not self._parameter:
            return "\r # MCast: Error ! Invalid Channel !\r"
        try:
            ch_id = int(self._parameter[0])
        except (ValueError, IndexError):
            return "\r # MCast: Error ! Invalid Channel !\r"
        return mcast_server.move_channel(member_call=str(self._to_call_str), channel_id=ch_id)

    def _cmd_mcast_channel_info(self):
        mcast_server = self._port_handler.get_mcast_server()
        if not hasattr(mcast_server, 'get_channel_info_fm_member'):
            logger.error("CLI: Attribute Error Mcast-Server. _cmd_mcast_channel_info()")
            return '\r # MCast: Attribute Error Mcast-Server\r'
        # if not self._parameter:
        return mcast_server.get_channel_info_fm_member(member_call=str(self._to_call_str))

    def _cmd_mcast_channels(self):
        mcast_server = self._port_handler.get_mcast_server()
        if not hasattr(mcast_server, 'get_channels'):
            logger.error("CLI: Attribute Error Mcast-Server. _cmd_mcast_channels()")
            return '\r # MCast: Attribute Error Mcast-Server\r'
        return mcast_server.get_channels()

    def _cmd_mcast_set_member_axip(self):
        mcast_server = self._port_handler.get_mcast_server()
        if not all((
                hasattr(mcast_server, 'get_member_ip'),
                hasattr(mcast_server, 'set_member_ip'),
                        )):
            logger.error("CLI: Attribute Error Mcast-Server. _cmd_mcast_set_member_axip()")
            return '\r # MCast: Attribute Error Mcast-Server\r'
        if not self._parameter:
            mcast_member_ip = mcast_server.get_member_ip(self._to_call_str)
            if len(mcast_member_ip) < 2:
                logger.error(f"CLI: No Address found for {self._to_call_str} !")
                return f"\r # MCast: No Address found for {self._to_call_str} !\r"
            ret = f"\r # MCast: Current AXIP Address for {self._to_call_str}:\r"
            ret +=  f" # Address: {mcast_member_ip[0]}\r"
            ret +=  f" # Port: {mcast_member_ip[1]}\r\r"
            return ret
        else:
            inv_param_msg = ('\r # MCast: Invalid Parameter / Invalid Address'
                            '\r # SETAXIP xxxx.dyndns.com 8093'
                            '\r # or'
                            '\r # SETAXIP 11.11.11.11 8093\r\r')
            if len(self._parameter) != 2:
                return inv_param_msg
            try:
                address = bytes(self._parameter[0]).decode(self._encoding[0], 'ignore')
                port = int(self._parameter[1])
            except (IndexError, ValueError):
                return inv_param_msg
            mcast_member_ip = mcast_server.get_member_ip(self._to_call_str)
            chk_ret = get_ip_by_hostname(address)
            chk_ret_mcast = get_ip_by_hostname(mcast_member_ip[0])
            if not chk_ret:
                ret = '\r # MCast: Invalid IP-Address or Domain Name\r'
                ret += inv_param_msg
                return ret
            if len(mcast_member_ip) < 2:
                logger.error(f"CLI: No Address found for {self._to_call_str} !")
                return f"\r # MCast: No Address found for {self._to_call_str} !\r"
            if chk_ret_mcast != chk_ret:
                return f"\r # MCast: The address you entered is not the same one you called from!\r"
            if mcast_member_ip[1] != port:
                return f"\r # MCast: The Port you entered is not the same one you called from!\r"
            user_db = self._user_db
            if not hasattr(user_db, 'set_AXIP'):
                logger.error("CLI: Attribute Error Mcast-Server. _cmd_mcast_set_member_axip() - User-DB")
                return '\r # MCast: Attribute Error Mcast-Server\r'
            if not user_db.set_AXIP(self._to_call_str, (address, port), new_user=True):
                logger.error(f"CLI: Error UserDB set_AXIP: {(address, port)}")
                return f'\r # MCast: Error ! UserDB set_AXIP: {(address, port)}\r'
            if not mcast_server.set_member_ip(self._to_call_str, (address, port)):
                logger.error(f"CLI: Error MCast set_member_ip: {(address, port)}")
                return f'\r # MCast: Error ! MCast set_member_ip: {(address, port)}\r'
            ret = f"\r # MCast: New AXIP Address set successfully\r"

            ret += f"\r # MCast: Current AXIP Address for {self._to_call_str}:\r"
            ret += f" # Address: {address}\r"
            ret += f" # Port: {port}\r\r"
            return ret



CLI_OPT = {
    UserCLI.cli_name: UserCLI,
    NodeCLI.cli_name: NodeCLI,
    NoneCLI.cli_name: NoneCLI,
    'PIPE': NoneCLI,
    MCastCLI.cli_name: MCastCLI,
}
