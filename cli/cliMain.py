from datetime import datetime

from cfg import constant
from cfg.popt_config import POPT_CFG
from cli.BaycomLogin import BaycomLogin
from cli.StringVARS import replace_StringVARS
from cli.cliStationIdent import get_station_id_obj
from cfg.constant import STATION_ID_ENCODING_REV
from fnc.ascii_graph import generate_ascii_graph
from fnc.file_fnc import get_str_fm_file
from fnc.str_fnc import get_time_delta, find_decoding, get_timedelta_str_fm_sec, get_timedelta_CLIstr, \
    convert_str_to_datetime, zeilenumbruch_lines, get_strTab, zeilenumbruch
from fnc.ax25_fnc import validate_ax25Call
from UserDB.UserDBmain import USER_DB
from cfg.logger_config import logger


class DefaultCLI(object):
    cli_name = ''  # DON'T CHANGE!
    service_cli = True
    prefix = b'//'
    sw_id = ''
    can_sidestop = True
    new_mail_noty = False

    def __init__(self, connection):
        self._logTag = f"CLI-{self.cli_name}: "
        logger.debug(self._logTag + "Init")
        stat_cfg: dict              = connection.get_stat_cfg()
        self._stat_cfg_index_call   = stat_cfg.get('stat_parm_Call', 'NOCALL')

        self._c_text                = self._load_fm_file(self._stat_cfg_index_call + '.ctx')
        self._connection            = connection
        self._port_handler          = self._connection.get_port_handler_CONN()
        self._own_port              = self._connection.own_port
        # self.channel_index = self._connection.ch_index
        self._gui                   = self._port_handler.get_gui()

        self._my_call_str           = self._connection.my_call_str
        self._to_call_str           = self._connection.to_call_str
        self._to_call               = self._connection.to_call_str.split('-')[0]
        self._user_db               = USER_DB
        self._user_db_ent           = self._connection.user_db_ent
        self._cli_lang              = self._connection.cli_language
        self._encoding              = 'UTF-8', 'ignore'
        self._stat_identifier_str   = ''
        if self._user_db_ent:
            self._encoding            = self._user_db_ent.Encoding, 'ignore'
            self._stat_identifier_str = self._user_db_ent.software_str
            if self._user_db_ent.CText:
                self._c_text          = str(self._user_db_ent.CText)

        self.stat_identifier    = get_station_id_obj(self._stat_identifier_str)
        # print(f"CLI STST ID : {self.stat_identifier}")
        # print(f"CLI STST str : {self.stat_identifier_str}")

        self._c_text            = self._c_text.replace('\n', '\r')

        self.time_start         = datetime.now()

        self._state_index       = 0
        self._crone_state_index = 0
        self._ss_state          = 0

        self._input             = b''
        self._raw_input         = b''
        self._cmd               = b''
        self._last_line         = b''
        self._new_last_line     = b''   # TODO ???????????????????????
        self._parameter         = []
        self._env_var_cmd       = False

        self._sys_login         = None
        self.sysop_priv         = False

        self._tx_buffer         = b''
        self._getTabStr = lambda str_k: get_strTab(str_k, self._cli_lang)
        # self._user_db_ent.cli_sidestop = 20
        # Crone
        self._cron_state_exec = {
            0:   self._cron_s0,     # No CMDs / Do nothing
            100: self._cron_s_quit  # QUIT
        }
        # Standard Commands ( GLOBAL )
        self._command_set = {
            # CMD: (needed lookup len(cmd), cmd_fnc, Help-Str, Str-Vars)
            'QUIT':     (1, self._cmd_q,                    'Quit',             True),
            'BYE':      (1, self._cmd_q,                    'Bye',              True),
            'ECHO':     (1, self._cmd_echo,                 'Echo',             False),
            # NODE Stuff
            'CONNECT':  (1, self._cmd_connect,              'Connect',           False),
            'C!':       (2, self._cmd_connect_exclusive,    'Connect Exclusive (No MH-Path-Lookup)', False),
            'PORT':     (1, self._cmd_port,                 'Ports',             False),
            'MH':       (0, self._cmd_mh,                   'MYHeard List',      False),
            'LMH':      (0, self._cmd_mhl,                  'Long MYHeard List', False),
            'AXIP':     (2, self._cmd_axip,                 'AXIP-MH List',      False),
            'DXLIST':   (2, self._cmd_dxlist,               'DX/Tracer Alarm List', False),
            'LCSTATUS': (2, self._cmd_lcstatus,             self._getTabStr('cmd_help_lcstatus'), False),
            # APRS Stuff
            'ATR':      (2, self._cmd_aprs_trace,           'APRS-Tracer', False),
            'WX':       (0, self._cmd_wx,                   self._getTabStr('cmd_help_wx'), False),
            # User/Station Info
            'BELL':     (2, self._cmd_bell,                 self._getTabStr('cmd_help_bell'), False),
            'INFO':     (1, self._cmd_i,                    'Info', True),
            'LINFO':    (2, self._cmd_li,                   'Long Info', True),
            'NEWS':     (2, self._cmd_news,                 'NEWS', True),
            # USER DB
            'USER':     (2, self._cmd_user_db_detail,       self._getTabStr('cmd_help_user_db'), False),
            'NAME':     (1, self._cmd_set_name,             self._getTabStr('cmd_help_set_name'), False),
            'QTH':      (3, self._cmd_set_qth,              self._getTabStr('cmd_help_set_qth'), False),
            'LOC':      (0, self._cmd_set_loc,              self._getTabStr('cmd_help_set_loc'), False),
            'ZIP':      (0, self._cmd_set_zip,              self._getTabStr('cmd_help_set_zip'), False),
            'PRMAIL':   (0, self._cmd_set_pr_mail,          self._getTabStr('cmd_help_set_prmail'), False),
            'EMAIL':    (0, self._cmd_set_e_mail,           self._getTabStr('cmd_help_set_email'), False),
            'WEB':      (3, self._cmd_set_http,             self._getTabStr('cmd_help_set_http'),  False),

            # CLI OPT
            'OP':       (2, self._cmd_op,                   self._getTabStr('cmd_op'), False),
            'LANG':     (4, self._cmd_lang,                 self._getTabStr('cli_change_language'), False),
            'UMLAUT':   (2, self._cmd_umlaut,               self._getTabStr('auto_text_encoding'), False),
            #
            'VERSION':  (3, self._cmd_ver,                  'Version', False),
            'POPT':     (0, self._cmd_popt_banner,          'PoPT Banner', False),
            'HELP':     (1, self._cmd_help,                 self._getTabStr('help'), False),
            '?':        (0, self._cmd_shelp,                self._getTabStr('cmd_shelp'), False),
        }
        self._commands_cfg  = list(self._command_set.keys())
        self._commands      = {}

        self._str_cmd_exec = {
            b'#REQUESTNAME:': self.str_cmd_req_name,
            b'#NAM#': self._cmd_set_name,
            b'#QTH#': self._cmd_set_qth,
            b'#LOC#': self._cmd_set_loc,
        }

        self._state_exec = {
            0: self._s0,  # C-Text
            1: self._s1,  # Cmd Handler
            2: self._s2,  # Nothing / no remote !!! Override in NODECLI / cmd_q...
            3: self._s3,  # Baycom Login Shit
            4: self._s4,  # Try to connect other Station ( C CMD )
            5: self._s5,  # Nothing / no remote
            6: self._s6,  # Auto Baycom Login Shit
            7: self._s7,  # Box Side Stop / Paging | Wait for input
        }

        self.init()

        for cmd_key in self._commands_cfg:
            if cmd_key not in self._command_set:
                logger.error(self._logTag + f"__init__: cmd_key {cmd_key} not in _command_set")
                continue
            self._commands[cmd_key] = self._command_set.get(cmd_key,
                                                            (0,
                                                            lambda : logger.error(self._logTag + f'cmd_kexError: {cmd_key}'),
                                                            'CLI-Error',
                                                             False)
                                                            )

        if not self.can_sidestop:
            if 'OP' in self._commands:
                del self._commands['OP']
        self._baycom_auto_login()
        """
        if type(self.prefix) is str:  # Fix for old CFG Files
            self.prefix = self.prefix.encode(self._encoding[0], self._encoding[1])
        """


    def init(self):
        pass


    def get_ts_prompt(self):
        return f"\r{self._my_call_str} ({datetime.now().strftime('%H:%M:%S')})>"

    def _send_output(self, ret, env_vars=True):
        if ret:
            if type(ret) is str:
                if env_vars:
                    ret = replace_StringVARS(ret,
                                             port=self._own_port,
                                             port_handler=self._port_handler,
                                             connection=self._connection,
                                             user_db=self._user_db)
                # ret = zeilenumbruch_lines(ret)
                ret = ret.encode(self._encoding[0], self._encoding[1])
                ret = ret.replace(b'\n', b'\r')
            if all((
                    self.can_sidestop,
                    self._user_db_ent.cli_sidestop)):
                self._send_out_sidestop(ret)
                return
            self._connection.tx_buf_rawData += ret

    def _send_out_sidestop(self, cli_out: bytes):
        if not self._user_db_ent.cli_sidestop:
            self._connection.tx_buf_rawData += cli_out
            self.change_cli_state(1)
            return
        tmp = cli_out.split(b'\r')
        out_lines = b'\r'.join(tmp[:self._user_db_ent.cli_sidestop])
        self._tx_buffer = b'\r'.join(tmp[self._user_db_ent.cli_sidestop:])
        if not self._tx_buffer:
            self._connection.tx_buf_rawData += cli_out
            self.change_cli_state(1)
            return
        if self._ss_state == 0:
            out_lines += self._getTabStr('op_prompt_0').encode(self._encoding[0], self._encoding[1])
        elif self._ss_state == 1:
            out_lines += self._getTabStr('op_prompt_1').encode(self._encoding[0], self._encoding[1])
        self._connection.tx_buf_rawData += out_lines
        self.change_cli_state(7)

    """
    def send_2_gui(self, data):  
        if data:
            if type(data) != str:
                data = data.decode(self.encoding[0], self.encoding[1])
            # print(data + ' <CLI> ' + str(self._connection.ch_index))
            self._gui.cli_echo(data, self._connection.ch_index)
    """

    def change_cli_state(self, state: int):
        # print(f"CLI change state: {state} - {self._state_index}")
        self._state_index = state

    def is_prefix(self):
        # Optimized by GROK (x.com)
        if not self.prefix:
            # Handle case where there is no prefix
            self._parameter = []
            cmd_parts = self._input.split(b' ')
            self._input = cmd_parts[1:] if len(cmd_parts) > 1 else b''
            self._parameter = self._input
            self._cmd = cmd_parts[0].upper().replace(b'\r', b'').replace(b'//', b'')
            return False

            # Remove newlines and split by '\r'
        lines = self._input.replace(b'\n', b'\r').split(b'\r')

        # Find the first non-empty line
        for line in lines:
            if line:
                self._input = line
                break
        else:
            # If no non-empty lines found
            return False

        # Check if the input starts with the prefix
        if self._input.startswith(self.prefix):
            cmd_part = self._input[len(self.prefix):].split(b' ', 1)
            self._cmd = cmd_part[0].upper().replace(b'\r', b'')
            self._parameter = cmd_part[1:] if len(cmd_part) > 1 else []
            self._input = self._parameter
            return True

        # If the prefix does not match, treat as user message
        self._parameter = []
        cmd_parts = self._input.split(b' ', 1)
        self._cmd = cmd_parts[0].upper().replace(b'\r', b'')
        self._parameter = cmd_parts[1:] if len(cmd_parts) > 1 else []
        self._input = self._parameter
        return False

    def _load_fm_file(self, filename: str):
        file_n = constant.CFG_data_path + \
                 constant.CFG_usertxt_path + \
                 self._stat_cfg_index_call + '/' + \
                 filename
        out = get_str_fm_file(file_n)
        if out:
            return zeilenumbruch_lines(out)
        return ''

    def start_baycom_login(self):
        if self._sys_login is None:
            if self._user_db_ent:
                if self._user_db_ent.sys_pw:
                    login_cmd = self._user_db_ent.sys_pw_parm[-1]
                    self._sys_login = BaycomLogin(
                        sys_pw_parm=self._user_db_ent.sys_pw_parm,
                        sys_pw=self._user_db_ent.sys_pw,
                        login_cmd=login_cmd,
                    )
                    self._send_output(self._sys_login.start(), env_vars=False)
                    self.change_cli_state(3)

    def _baycom_auto_login(self):
        if self._sys_login:
            return False
        if not self._user_db_ent:
            return False
        if not hasattr(self._user_db_ent, 'sys_pw_autologin'):
            return False
        if not self._user_db_ent.sys_pw_autologin:
            return False
        self._sys_login = BaycomLogin(
            sys_pw_parm=self._user_db_ent.sys_pw_parm,
            sys_pw=self._user_db_ent.sys_pw,
        )
        self._sys_login.attempts = 1
        self.change_cli_state(6)
        return True

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
            if not self._user_db_ent.TYP:
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
                        self._send_output(f'\r//N {name}\r', env_vars=False)
                    else:
                        self._send_output(f'\rN {name}\r', env_vars=False)

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
            self._env_var_cmd = False
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
                            self._env_var_cmd = self._commands[cmd][3]
                            return ret
                        return ''
                if inp_cmd == cmd[:len(inp_cmd)]:
                    treffer.append(cmd)
            if not treffer:
                return f"\r # {self._getTabStr('cmd_not_known')}\r"
            if len(treffer) > 1:
                return (f"\r # {self._getTabStr('cmd_not_known')}"
                        f"\r # {(' '.join(treffer))} ?\r")
            self._cmd = b''
            if not callable(self._commands[treffer[0]][1]):
                return ''
            ret = tuple(self._commands[treffer[0]])[1]()
            # self.last_line = b''
            self._new_last_line = b''
            if ret:
                self._env_var_cmd = self._commands[treffer[0]][3]
                return ret
            return ''

        return f"\r # {self._getTabStr('cmd_not_known')}\r"

    def _exec_cmd(self):
        self._input = self._last_line + self._input
        if self.is_prefix():
            return self._find_cmd()
        # Message is for User ( Text , Chat )
        if self.prefix:
            return ''
        self._ss_state = 0  # Reset Side Stop State to default
        # CMD Input for No User Terminals ( Node ... )
        ret = self._find_cmd()
        if self._crone_state_index not in [100] and \
                self._state_index not in [2, 4, 8]:  # Not Quit| 8 = BBS send msg
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
                    self._send_output(ret, env_vars=False)
                    self._last_line = b''
                    self._new_last_line = b''
                    return ret
        return ret

    def send_prompt(self):
        self._send_output(self.get_ts_prompt(), env_vars=False)

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
                        tmp_parm = el
                else:
                    tmp_parm = el
                tmp.append(tmp_parm)
        self._parameter = list(tmp)
    #########################################################
    def _cmd_connect(self, exclusive=False):
        self._decode_param()
        if not self._parameter:
            return f"\r {self._getTabStr('cmd_c_noCall')}\r"

        dest_call = str(self._parameter[0]).upper()
        if not validate_ax25Call(dest_call):
            return f"\r {self._getTabStr('cmd_c_badCall')}\r"

        port_id = -1
        vias = []
        port_tr = False
        if len(self._parameter) > 1:
            if self._parameter[-1].isdigit():
                port_tr = True
                try:
                    port_id = int(self._parameter[-1])
                    if port_id not in self._port_handler.get_all_ports().keys():
                        return f"\r {self._getTabStr('cmd_c_noPort')}\r"
                except ValueError:
                    return f"\r {self._getTabStr('cmd_c_badPort')}\r"

            via_params = self._parameter[1:-1] if port_tr else self._parameter[1:]
            vias = [call.upper() for call in via_params if validate_ax25Call(call.upper())]

        conn = self._port_handler.new_outgoing_connection(
                own_call=self._to_call_str,
                dest_call=dest_call,
                via_calls=vias,
                port_id=port_id,
                link_conn=self._connection,
                exclusive=exclusive
                # link_call=str(self._connection.my_call_str)
            )
        if conn[0]:
            self._state_index = 4
            return conn[1]
        return f'\r*** Link Busy: {conn[1]}\r'

    def _cmd_connect_exclusive(self):
        return self._cmd_connect(exclusive=True)

    def _cmd_echo(self):  # Quit
        ret = ''
        for el in self._parameter:
            ret += el.decode(self._encoding[0], self._encoding[1]) + ' '
        return ret[:-1] + '\r'

    def _cmd_q(self):  # Quit
        # self._connection: AX25Conn
        # self._connection.tx_buf_rawData += self.bye_text.encode(self.encoding[0], self.encoding[1])
        conn_dauer = get_time_delta(self.time_start)
        ret = f"\r # {self._getTabStr('time_connected')}: {conn_dauer}\r\r"
        ret += self._load_fm_file(self._stat_cfg_index_call + '.btx') + '\r'
        self._send_output(ret, env_vars=True)
        self._crone_state_index = 100  # Quit State
        return ''

    def _cmd_lang(self):
        if not self._parameter:
            return f'\r # {self._getTabStr("cli_no_lang_param")}{" ".join(list(constant.LANG_IND.keys()))}\r'
        self._decode_param()
        if self._parameter[0].upper() in constant.LANG_IND.keys():
            self._connection.set_user_db_language(constant.LANG_IND[self._parameter[0].upper()])
            return f'\r # {self._getTabStr("cli_lang_set")}\r'
        return f'\r # {self._getTabStr("cli_no_lang_param")}{" ".join(list(constant.LANG_IND.keys()))}\r'

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
            return f'\r # {self._getTabStr("cli_no_data")}\r'
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
            return f'\r # {self._getTabStr("cli_no_data")}\r'
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
            return f'\r # {self._getTabStr("cli_no_data")}\r'
        out = ''
        c = 0
        max_c = 0

        for call in list(sort_list.keys()):
            if port_id == -1 or port_id == sort_list[call].port_id:
                max_c += 1
                if max_c > max_ent:
                    break
                time_delta_str = get_timedelta_CLIstr(sort_list[call].last_seen)
                call_str = sort_list[call].own_call
                if sort_list[call].route:
                    call_str += '*'
                out += f'{time_delta_str} P:{sort_list[call].port_id:2} {call_str:10}'.ljust(27, " ")

                c += 1
                if c == 2:  # Breite
                    c = 0
                    out += '\r'
        if not out:
            return f'\r # {self._getTabStr("cli_no_data")}\r'
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
            return f'\r # {self._getTabStr("cli_no_data")}\r'
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
            return f'\r # {self._getTabStr("cli_no_data")}\r'
        return "\r-----Time-Port-Call------via-------LOC------Dist(km)--Type---Packets\r" + out

    def _cmd_wx(self):
        """ WX Stations """
        if self._port_handler.aprs_ais is None:
            return f'\r # {self._getTabStr("cli_no_wx_data")}\r\r'
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
            return f'\r # {self._getTabStr("cli_no_wx_data")}\r\r'
        return ret + '\r'

    def _get_wx_fm_call_cli_out(self, call, max_ent=10):
        data       = list(self._port_handler.aprs_ais.get_wx_data_f_call(call))
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
        time_range = 72
        init_time  = data[0][15].split(' ')[-1].split(':')[0]
        init_dict  = {}
        if data[0][5]:
            try:
                init_dict['temp'] = float(data[0][5])
            except ValueError:
                pass
        if  data[0][0]:
            try:
                init_dict['pres'] = float(data[0][0])
            except ValueError:
                pass
        if  data[0][1]:
            try:
                init_dict['hum'] = float(data[0][1])
            except ValueError:
                pass

        temp_graph_data = [init_dict]
        for el in data:
            time_st = el[15].split(' ')[-1].split(':')[0]
            if  str(time_st) != str(init_time):
                max_c += 1
                if max_c <= max_ent:
                    # graph_data.append({'temp': float(el[5])})
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


                temp_dict = {}
                if 'temp' in init_dict:
                    try:
                        temp_dict['temp'] = float(el[5])
                    except ValueError:
                        pass
                if 'pres' in init_dict:
                    try:
                        temp_dict['pres'] = float(el[0])
                    except ValueError:
                        pass
                if 'hum' in init_dict:
                    try:
                        temp_dict['hum'] = float(el[1])
                    except ValueError:
                        pass
                temp_graph_data.append(temp_dict)
                init_time = time_st
            if len(temp_graph_data) >= time_range :
                break

        if 'temp' in init_dict:
            datasets = {'temp': '+'}
            temp_graph = generate_ascii_graph(temp_graph_data,
                                         f"{self._getTabStr('temperature')}(C) - {call} - {time_range} {self._getTabStr('hours')}",
                                         datasets,
                                         chart_type='line',
                                         graph_height=12,
                                         graph_width=time_range,
                                         expand=True )
            out += '\r'
            out += '\r'
            out += temp_graph

        if 'pres' in init_dict:
            datasets = {'pres': '+'}
            press_graph = generate_ascii_graph(temp_graph_data,
                                              f"{self._getTabStr('wx_press')}(hPa) - {call} - {time_range} {self._getTabStr('hours')}",
                                              datasets,
                                              chart_type='line',
                                              graph_height=12,
                                              graph_width=time_range,
                                              expand=True)
            out += '\r'
            out += '\r'
            out += press_graph

        if 'hum' in init_dict:
            datasets = {'hum': '+'}
            hum_graph = generate_ascii_graph(temp_graph_data,
                                              f"{self._getTabStr('wx_hum')}(%) - {call} - {time_range} {self._getTabStr('hours')}",
                                              datasets,
                                              chart_type='line',
                                              graph_height=12,
                                              graph_width=time_range,
                                              expand=True)

            out += '\r'
            out += '\r'
            out += hum_graph

        out += '\r'
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
            return f'\r # {self._getTabStr("cli_no_tracer_data")}\r\r'
        parm = 10
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except ValueError:
                pass
        data = self._port_handler.aprs_ais.tracer_traces_get()
        if not data:
            return f'\r # {self._getTabStr("cli_no_tracer_data")}\r\r'
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
            # max_lines = 20  # TODO: from parameter
            db_list = list(self._user_db.db.keys())
            header = "\r" \
                     f" USER-DB - {len(db_list)} Calls\r" \
                     "-------------------------------------------------------------------------------\r"
            ent_ret = ""
            db_list.sort()
            # c = 0
            # colum_c = 0
            for call in db_list:
                ent_ret += f"{call} "
                """
                colum_c += 1
                if colum_c > 6:
                    ent_ret += "\r"
                    colum_c = 0
                    c += 1
                """
                """
                if c >= max_lines:
                    break
                """
            ent_ret = zeilenumbruch(ent_ret)
            ent_ret += "\r-------------------------------------------------------------------------------\r\r"
            return header + ent_ret
        else:
            call_str = self._parameter[0].decode(self._encoding[0], self._encoding[1]).upper()
            db_ent = self._user_db.get_entry(call_str, add_new=False)
            if db_ent:
                header = "\r" \
                         f"| USER-DB: {call_str}\r" \
                         "|-------------------\r"
                ent = db_ent
                ent_ret = ""
                for att in dir(ent):
                    if '__' not in att and \
                            att not in self._user_db.not_public_vars:
                        if getattr(ent, att):
                            ent_ret += f"| {att.ljust(10)}: {getattr(ent, att)}\r"
                ent_ret += "|-------------------\r\r"
                return header + ent_ret

            return "\r" \
                   f"{self._getTabStr('cli_no_user_db_ent')}" \
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
                   f"{self._getTabStr('cli_name_set')}: {self._user_db_ent.Name}" \
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
                   f"{self._getTabStr('cli_qth_set')}: {self._user_db_ent.QTH}" \
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
                       f"{self._getTabStr('cli_loc_set')}: {self._user_db_ent.LOC}" \
                       "\r"
            return "\r" \
                   f"{self._getTabStr('cli_loc_set')}: {self._user_db_ent.LOC} > {round(self._user_db_ent.Distance)} km" \
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
                   f"{self._getTabStr('cli_zip_set')}: {self._user_db_ent.ZIP}" \
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
                   f"{self._getTabStr('cli_prmail_set')}: {self._user_db_ent.PRmail}" \
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
                   f"{self._getTabStr('cli_email_set')}: {self._user_db_ent.Email}" \
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
                   f"{self._getTabStr('cli_http_set')}: {self._user_db_ent.HTTP}" \
                   "\r"

        logger.error("User-DB Error. cmd_set_http NO ENTRY FOUND !")
        return "\r # USER-DB Error !\r"

    def _cmd_port(self):  # TODO Pipe
        ret = f"\r      < {self._getTabStr('port_overview')} >\r\r"
        ret += "-#--Name----PortTyp----------Stations--Typ------Digi-\r"
        for port_id in self._port_handler.ax25_ports.keys():
            port = self._port_handler.ax25_ports[port_id]
            name = str(port.portname).ljust(7)
            typ = port.port_typ.ljust(15)
            if port.dualPort_primaryPort in [port, None]:

                stations = self._port_handler.get_stat_calls_fm_port(port_id)
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
                    ret += f"                             {stat.ljust(9)} {digi}\r"
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

        return ret + "\r"

    def _cmd_help(self):
        # ret = f"\r   < {self._getTabStr('help')} >\r"
        ret = "\r"
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
            return f"\r{self._getTabStr('cli_text_encoding_no_param')}: {self._encoding[0]}\r"
        res = find_decoding(self._parameter[0].replace(b'\r', b''))
        if not res:
            return f"\r{self._getTabStr('cli_text_encoding_error_not_found')}\r"
        self._encoding = res, self._encoding[1]
        if self._user_db_ent:
            self._user_db_ent.Encoding = str(res)
        return f"\r{self._getTabStr('cli_text_encoding_set')} {res}\r"

    def _cmd_bell(self):
        if not self._connection.noty_bell:
            self._connection.noty_bell = True
            msg = b' '.join(self._parameter)
            msg = msg.decode(self._encoding[0], self._encoding[1])
            self._port_handler.set_noty_bell_PH(self._connection.ch_index, msg)
            return f'\r # {self._getTabStr("cmd_bell")}\r'
        return f'\r # {self._getTabStr("cmd_bell_again")}\r'

    def _cmd_op(self):
        if not self._parameter:
            self._user_db_ent.cli_sidestop = 0
            ""
            return self._getTabStr('box_cmd_op1')
        try:
            self._user_db_ent.cli_sidestop = int(self._parameter[0])
        except ValueError:
            return self._getTabStr('box_cmd_op2')
        return self._getTabStr('box_cmd_op3').format(self._user_db_ent.cli_sidestop)

    ##############################################
    def str_cmd_req_name(self):
        stat_cfg: dict = self._connection.get_stat_cfg()
        name = stat_cfg.get('stat_parm_Name', '')
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
        # print(self._state_index)

        self._raw_input = bytes(inp)
        ret = self._state_exec[self._state_index]()
        # print(f"CLI: ret: {ret}")
        if ret:
            self._send_output(ret, env_vars=False)

    def cli_cron(self):
        """ Global Crone Tasks """
        if not self._connection.is_link:
            self.cli_state_crone()

    def cli_state_crone(self):
        """ State Crone Tasks """
        ret = self._cron_state_exec[self._crone_state_index]()
        if ret:
            self._send_output(ret, env_vars=False)

    def _s0(self):  # C-Text
        self._state_index = 1
        ret = self._send_sw_id()
        ret += self._c_text
        # bbs = self._port_handler.get_bbs()
        """
        if hasattr(bbs, 'get_new_pn_count_by_call'):
            new_mail = bbs.get_new_pn_count_by_call(self._to_call)
            if new_mail:
                ret += self._getTabStr('box_new_mail_ctext').format(new_mail)
        """
        if self.cli_name == 'USER':
            self._send_output(ret, env_vars=True)
            return ''
        self._send_output(ret + self.get_ts_prompt(), env_vars=True)
        return ''

    def _s1(self):
        # print("CMD-Handler S1")
        if not self.stat_identifier:
            self._software_identifier()
        """
        BBS / evtl. NODE, MCAST
        if any((
                self.stat_identifier.typ in ['BBS', 'NODE'],
                self._user_db_ent.TYP in NO_REMOTE_STATION_TYPE,
                self._connection.bbs_connection,
        )):
            return 
        """
        ########################
        # Check String Commands
        if not self._exec_str_cmd():
            self._input = self._raw_input
            self._send_output(self._exec_cmd(), self._env_var_cmd)
        self._last_line = self._new_last_line
        return ''

    def _s2(self):
        """ Do nothing / No Remote"""
        """ !!! Override in NODECLI"""
        return ""

    def _s3(self):
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

    def _s4(self):
        """ try to connect other Station ( C CMD ) """
        if self._connection.LINK_Connection:
            # print(f'CLI LinkDisco : {self._connection.uid}')
            self._connection.link_disco()
        self.change_cli_state(1)
        return self.get_ts_prompt()

    @staticmethod
    def _s5():
        """ Do nothing / No Remote"""
        return ""

    def _s6(self):
        """ Auto Sys Login """
        if self._sys_login is None:
            # print(1)
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

            if self._sys_login.fail_counter > 20:
                del self._sys_login
                self._sys_login = None
                # print("Priv: Failed !")
                logger.warning(self._logTag + "Priv: Failed !")
                if self._gui:
                    self._gui.on_channel_status_change()
                self.change_cli_state(1)

            # print("----")
            # self._sys_login.attempts += 1
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

    def _s7(self):
        """ Side Stop / Paging"""
        if not self._tx_buffer:
            logger.warning(self._logTag + f"CLI: _s7: No tx_buffer but in S7 !!")
            self.change_cli_state(1)
            return
        if not self._user_db_ent.cli_sidestop:
            logger.warning(self._logTag + f"CLI: _s7: No UserOpt but in S7 !!")
            self.change_cli_state(1)
            return
        if not self._raw_input:
            return
        if self._raw_input in [b'\r', b'\n']:
            self._send_out_sidestop(self._tx_buffer)
            return
        if self._raw_input in [b'a\r', b'A\r', b'a\n', b'A\n']:
            self._tx_buffer = b''
            self.send_prompt()
            self.change_cli_state(1)
            return
        if self._raw_input in [b'o\r', b'O\r', b'o\n', b'O\n']:
            self._connection.tx_buf_rawData += bytearray(self._tx_buffer)
            self._tx_buffer = b''
            self.change_cli_state(1)
            return


    @staticmethod
    def _cron_s0():
        """ Dummy for doing nothing """
        return ''

    def _cron_s_quit(self):
        # self._connection: AX25Conn
        if not self._connection.tx_buf_rawData and \
                not self._connection.tx_buf_unACK and \
                not self._connection.tx_buf_2send:
            if self._connection.zustand_exec.stat_index not in [0, 1, 4]:
                self._connection.zustand_exec.change_state(4)

class NoneCLI(DefaultCLI):
    """ ? To Disable CLI / Remote ? """
    cli_name = 'NO-CLI'  # DON'T CHANGE !
    service_cli = False
    # _c_text = ''
    # bye_text = ''
    prefix = b''
    can_sidestop = False
    new_mail_noty = False

    def init(self):
        self._commands_cfg = []

    def cli_exec(self, inp=b''):
        pass

    def _exec_cmd(self):
        return ''

    def cli_cron(self):
        pass

    def _baycom_auto_login(self):
        return False
