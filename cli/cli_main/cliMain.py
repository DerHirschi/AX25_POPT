from datetime import datetime

from cfg.popt_config import POPT_CFG
from cli.cli_commands.cli_cmd_aprsChat import CliCmdAprsChat
from cli.cli_commands.cli_cmd_help import CliCmdHelp
#from cli.cli_commands.cli_cmd_poker import CliCmdPoker
from cli.cli_main.BaycomLogin import BaycomLogin
from cli.StringVARS import replace_StringVARS
from cli.cliStationIdent import get_station_id_obj
from cfg.constant import STATION_ID_ENCODING_REV, VER, CFG_data_path, CFG_usertxt_path, LANG_IND, CLI_TYP_SYSOP
from cli.cli_commands.cli_cmd_infos import CliCmdInfos
from cli.cli_commands.cli_cmd_myHeard import CliCmdMyHeard
from cli.cli_commands.cli_cmd_statistics import CliCmdStatistics
from cli.cli_commands.cli_cmd_status import CliCmdStatus
from cli.cli_commands.cli_cmd_userDB import CliCmdUserDB
from cli.cli_const import CLI_DEF_CMD_BASIC
from cli.cli_main.cliMain_StrCmds import CliStrCommands
from fnc.file_fnc import get_str_fm_file
from fnc.str_fnc import get_time_delta, find_decoding, zeilenumbruch_lines, get_strTab, find_eol
from fnc.ax25_fnc import validate_ax25Call
from UserDB.UserDBmain import USER_DB
from cfg.logger_config import logger
from prp.prp_const import PRP_OPT_ESC_CLI


class DefaultCLI(object):
    cli_name      = ''  # DON'T CHANGE!
    service_cli   = True
    prefix        = b'//'
    sw_id         = ''
    can_sidestop  = True
    new_aprs_msg_noty = False

    def __init__(self, connection):
        self._logTag = f"CLI-{self.cli_name}: "
        logger.debug(self._logTag + "Init")
        stat_cfg: dict              = connection.get_stat_cfg
        self._stat_cfg_index_call   = stat_cfg.get('stat_parm_Call', 'NOCALL')

        self._c_text                = self.load_fm_file(self._stat_cfg_index_call + '.ctx')
        self._connection            = connection
        self._own_port              = connection.own_port
        self._port_handler          = connection.own_port.port_get_PH()
        # self.channel_index = self._connection.ch_index
        # self._gui                   = self._port_handler.get_gui()

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

        # ==== Station Identy
        # == Gegenstation
        self.stat_identifier        = get_station_id_obj(self._stat_identifier_str)
        self._stat_identifier_found = False
        # == Eigener Identy
        # self._own_stat_identifier   = get_station_id_obj(self._get_own_identy_str())
        self.get_own_stat_identy    = lambda : get_station_id_obj(self._get_own_identy_str())

        # ====================
        self._c_text            = self._c_text.replace('\n', '\r')

        self.time_start         = datetime.now()

        self._state_index       = 0
        self._crone_state_index = 0
        self._ss_state          = 0

        self._input             = b''
        self._raw_input         = b''
        self._cmd               = b''
        self._last_line         = b''
        self.new_last_line      = b''   # TODO ???????????????????????
        self._parameter         = []
        self._env_var_cmd       = False
        self.skip_prompt        = False

        self._sys_login         = None
        self.sysop_priv         = False

        self.rtt_active         = False

        self._tx_buffer         = bytearray()
        self._getTabStr_CLI = lambda str_k: get_strTab(str_k, self._cli_lang)
        self._getTabStr_GUI = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # self._user_db_ent.cli_sidestop = 20
        # Crone
        self._cron_state_exec = {
            0:   self._cron_s0,     # No CMDs / Do nothing
            100: self._cron_s_quit  # QUIT
        }
        # ============================================
        # Command sets Init
        self._statistics_cmds = CliCmdStatistics(self)
        self._my_heard_cmds   = CliCmdMyHeard(self)
        self._infos_cmds      = CliCmdInfos(self)
        self._status_cmds     = CliCmdStatus(self)
        self._user_db_cmds    = CliCmdUserDB(self)
        self._help_cmds       = CliCmdHelp(self)
        self._aprs_chat_cmds  = CliCmdAprsChat(self)
        #self._poker_cmds      = CliCmdPoker(self)

        # Standard Commands ( GLOBAL )
        self._command_set = {

            # CMD: (needed lookup len(cmd), cmd_fnc, Help-Str, Str-Vars allowed)
            'QUIT':     (1, self._cmd_q,                            'Quit',              True),
            'BYE':      (1, self._cmd_q,                            'Bye',               True),
            'ECHO':     (1, self._cmd_echo,                         'Echo',              False),

            # NODE Stuff
            'CONNECT':  (1, self._cmd_connect,                      'Connect',           False),
            'C!':       (2, self._cmd_connect_exclusive,            'Connect Exclusive (No MH-Path-Lookup)', False),
            'CONV':     (3, self._cmd_conv,                         'Converse',                                 False),

            # Statistics
            'PSTAT':    (2, self._statistics_cmds.cmd_pstat,        f"Port {self._getTabStr_CLI('statistic')}", False),
            'BWSTAT':   (2, self._statistics_cmds.cmd_bwstat,       self._getTabStr_CLI('cmd_help_bwstat'),     False),
            'CSTAT':    (2, self._statistics_cmds.cmd_cstats,       self._getTabStr_CLI('cmd_help_cstat'),      False),
            'WX':       (0, self._statistics_cmds.cmd_wx,           self._getTabStr_CLI('cmd_help_wx'),         False),

            # MH
            'MH':       (0, self._my_heard_cmds.cmd_mh,             'MYHeard List',                         False),
            'LMH':      (0, self._my_heard_cmds.cmd_mhl,            'Long MYHeard List',                    False),
            'AXIP':     (2, self._my_heard_cmds.cmd_axip,           'AXIP-MH List',                         False),
            'DXLIST':   (2, self._my_heard_cmds.cmd_dxlist,         'DX/Tracer Alarm List',                 False),
            'CHIST':    (3, self._my_heard_cmds.cmd_chist,          self._getTabStr_CLI('cmd_help_chist'),  False),
            'ATR':      (2, self._my_heard_cmds.cmd_aprs_trace,     'APRS-Tracer',                          False),

            # Status
            'PORT':     (1, self._status_cmds.cmd_port,             'Ports',                                    False),
            'LCSTATUS': (2, self._status_cmds.cmd_lcstatus,         self._getTabStr_CLI('cmd_help_lcstatus'),   False),

            #
            'CH':       (2, self._cmd_ch,                           self._getTabStr_CLI('cmd_help_ch'),         False),
            'RTT':      (2, self._cmd_rtt,                          self._getTabStr_CLI('cmd_help_rtt'),        False),
            # Remote Monitor
            # 'PREMON':   (2, self._cmd_set_gui_remote_mon,         "PoPT Remote Monitor", False),

            # APRS Chat
            'ACHAT':    (2, self._aprs_chat_cmds.cmd_aprs_chat,     'APRS Chat / Messenger',                       False),
            'AMSGS':    (2, self._aprs_chat_cmds.cmd_aprs_msgs,     'APRS Messages',                       False),
            #
            'BELL':     (2, self._cmd_bell,                         self._getTabStr_CLI('cmd_help_bell'),   False),

            # User/Station Info
            'INFO':     (1, self._infos_cmds.cmd_i,                 'Info',                                 True),
            'LINFO':    (2, self._infos_cmds.cmd_li,                'Long Info',                            True),
            'NEWS':     (2, self._infos_cmds.cmd_news,              'NEWS',                                 True),
            'POPT':     (4, self._infos_cmds.cmd_popt_banner,       'PoPT Banner',                          False),
            'VERSION':  (3, self._infos_cmds.cmd_ver,               'Version',                              False),

            # USER DB
            'USER':     (2, self._user_db_cmds.cmd_user_db_detail,  self._getTabStr_CLI('cmd_help_user_db'),    False),
            'NAME':     (1, self._user_db_cmds.cmd_set_name,        self._getTabStr_CLI('cmd_help_set_name'),   False),
            'QTH':      (3, self._user_db_cmds.cmd_set_qth,         self._getTabStr_CLI('cmd_help_set_qth'),    False),
            'LOC':      (3, self._user_db_cmds.cmd_set_loc,         self._getTabStr_CLI('cmd_help_set_loc'),    False),
            'ZIP':      (3, self._user_db_cmds.cmd_set_zip,         self._getTabStr_CLI('cmd_help_set_zip'),    False),
            'PRMAIL':   (2, self._user_db_cmds.cmd_set_pr_mail,     self._getTabStr_CLI('cmd_help_set_prmail'), False),
            'EMAIL':    (0, self._user_db_cmds.cmd_set_e_mail,      self._getTabStr_CLI('cmd_help_set_email'),  False),
            'WEB':      (3, self._user_db_cmds.cmd_set_http,        self._getTabStr_CLI('cmd_help_set_http'),   False),

            # CLI OPT
            'OP':       (2, self._cmd_op, self._getTabStr_CLI('cmd_op'), False),
            'LANG':     (4, self._cmd_lang, self._getTabStr_CLI('cli_change_language'), False),
            'UMLAUT':   (2, self._cmd_umlaut, self._getTabStr_CLI('auto_text_encoding'), False),
            #
            'HELP':     (1, self._help_cmds.cmd_help,                         self._getTabStr_CLI('help'),        False),
            '?':        (0, self._help_cmds.cmd_shelp,                        self._getTabStr_CLI('cmd_shelp'),   False),
            # Poker
            #'POKER':    (3, self._poker_cmds.cmd_poker,             "Poker (Texas Hold'em)",            False),

        }

        self._StrCommands  = CliStrCommands(self)

        self._state_exec = {
            0: self._s0,  # C-Text
            1: self._s1,  # Cmd Handler
            2: self._s2,  # Nothing / no remote !!! Override in NODECLI / cmd_q...
            3: self._s3,  # Baycom Login Shit
            4: self._s4,  # Try to connect other Station ( C CMD )
            5: self._s5,  # Nothing / no remote
            6: self._s6,  # Auto Baycom Login Shit
            7: self._s7,  # Box Side Stop / Paging | Wait for input
            8: self._aprs_chat_cmds.s8_aprs_chat,  # APRS Chat Mode
        }

        self.init()

        if not self.can_sidestop:
            if 'OP' in self._command_set:
                del self._command_set['OP']
        self._baycom_auto_login()


    def init(self):
        pass

    ########################################################
    # CMD Classes
    @property
    def user_db_cmds(self):
        return self._user_db_cmds

    ########################################################
    @property
    def connection(self):
        return self._connection

    @property
    def popt_handler(self):
        return self._port_handler

    @property
    def own_port(self):
        return self._own_port

    @property
    def userDB(self):
        return self._user_db

    @property
    def userDB_ent(self):
        return self._connection.user_db_ent

    @property
    def cli_lang(self):
        return self._connection.cli_language

    @property
    def cli_encoding(self):
        return self._encoding

    @property
    def stat_cfg_index_call(self):
        return self._stat_cfg_index_call

    @property
    def command_set(self):
        return self._command_set

    @property
    def state_index(self):
        return self._state_index

    #######################
    # Input Parameter
    @property
    def parameter(self):
        return self._parameter

    def set_parameter(self, new_parameter: list):
        self._parameter = list(new_parameter)

    #######################
    # Input
    @property
    def raw_input(self):
        return self._raw_input

    def set_input(self, val):
        self._input = val

    ########################################################
    @property
    def _gui(self):
        return self._port_handler.get_gui()

    @property
    def _prp(self):
        if hasattr(self._connection, 'prp'):
            return self._connection.prp
        return None

    ##################################
    # Rechte / CMD Update
    def get_allowed_cmds(self):
        if hasattr(self._prp, 'prp_rights'):
            allowed = self._prp.prp_rights.get_allowed_cli_commands(self._connection.to_call_str, self.cli_name)
            return [cmd for cmd in self._command_set if cmd in allowed]

        logger.error("CLI: PRP-Rechte Manager nicht gefunden. AttributeError")
        return [cmd for cmd in self._command_set if cmd in CLI_DEF_CMD_BASIC]

    ##################################
    # Helper
    # TX-Stuff
    def get_ts_prompt(self):
        return f"\r{self._my_call_str} ({datetime.now().strftime('%H:%M:%S')})>"

    def send_prompt(self):
        self.send_output(self.get_ts_prompt(), env_vars=False)

    def send_output(self, ret, env_vars=True):
        if not ret:
            return
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
        self._connection.send_data(ret)

    def _send_out_sidestop(self, cli_out: bytes):
        if not self._user_db_ent.cli_sidestop:
            self._connection.send_data(cli_out)
            self.change_cli_state(1)
            return
        tmp = cli_out.split(b'\r')
        out_lines = b'\r'.join(tmp[:self._user_db_ent.cli_sidestop])
        self._tx_buffer = b'\r'.join(tmp[self._user_db_ent.cli_sidestop:])
        if not self._tx_buffer:
            self._connection.send_data(cli_out)
            self.change_cli_state(1)
            return
        if self._ss_state == 0:
            out_lines += self._getTabStr_CLI('op_prompt_0').encode(self._encoding[0], self._encoding[1])
        elif self._ss_state == 1:
            out_lines += self._getTabStr_CLI('op_prompt_1').encode(self._encoding[0], self._encoding[1])
        self._connection.send_data(out_lines)
        self.change_cli_state(7)

    # TX-Abort-Stuff
    def _abort_send_out(self):
        prp = self._prp
        if hasattr(prp, 'cli_abort'):
            prp.cli_abort()

        self._connection.clear_tx_buff()
        self._tx_buffer = b''
        self._connection.send_data((f"\r\r # {self._getTabStr_CLI('aborted')} !\r"
                                    + self.get_ts_prompt()).encode(self._encoding[0], 'ignore'))

    def _check_abort_cmd(self):
        eol = find_eol(self._raw_input)
        if (self._raw_input.upper() == b'A' + eol and
            (self._connection.get_tx_buff_len
            or self._tx_buffer or self._connection.is_prp_opt_id_in_tx_buff(PRP_OPT_ESC_CLI))
        ):
            self._abort_send_out()
            self._last_line = b''
            return True
        return False

    #
    def change_cli_state(self, state: int):
        # print(f"CLI change state: {state} - {self._state_index}")
        self._state_index = state

    def _is_prefix(self):
        # Optimized by GROK (x.com) TODO Again
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
        line_w_cmd = b''
        for line in lines:
            if line.startswith(self.prefix):
                line_w_cmd = line
                break
        else:
            # If no non-empty lines found
            return False

        # Check if the input starts with the prefix
        if line_w_cmd.startswith(self.prefix):
            cmd_part = line_w_cmd[len(self.prefix):].split(b' ')
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

    def load_fm_file(self, filename: str):
        file_n = CFG_data_path + \
                 CFG_usertxt_path + \
                 self._stat_cfg_index_call + '/' + \
                 filename
        out = get_str_fm_file(file_n)
        if out:
            return zeilenumbruch_lines(out)
        return ''

    # Auto Baycom Login
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
                    self.send_output(self._sys_login.start(), env_vars=False)
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

    # Software ID
    def _get_own_identy_str(self):
        """ Normalen Station Identy STR bauen (SYSOP/NODE) """
        if not self.sw_id:
            # Kein CLI TYP
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
        return '{' + f"{self.sw_id}-{VER}-{flag}" + '}'

    def _set_user_db_software_id(self):
        if self._user_db_ent:
            self._user_db_ent.software_str = str(self.stat_identifier.id_str)
            self._user_db_ent.Software = str(self.stat_identifier.software) + '-' + str(self.stat_identifier.version)
            if not self._user_db_ent.TYP:
                self._user_db_ent.TYP = str(self.stat_identifier.typ)

    def _software_identifier(self):
        if self._stat_identifier_found:
            return True

        res = self._find_sw_identifier()
        if res and self.stat_identifier:
            self._stat_identifier_found = True

            if self.stat_identifier.knows_me is not None:
                if not self.stat_identifier.knows_me:
                    self._send_name_cmd_back()

            if self.stat_identifier.txt_encoding is not None:
                self._encoding = self.stat_identifier.txt_encoding, 'ignore'
                if self._user_db_ent:
                    self._user_db_ent.Encoding = self.stat_identifier.txt_encoding

            # FIXME: PRP-Remote Disabled
            #   self._init_popt_remote()
            return True

        return False

    def _find_sw_identifier(self):
        # print(f"find_stat_identifier self.stat_identifier: {self.stat_identifier}")
        if self.stat_identifier is None:
            # print(self._last_line + self._raw_input)
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
                    #logger.debug(f"stat_identifier found!: {temp_stat_identifier}")
                    return True
            return False
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
                        #logger.debug(f"stat_identifier found!: {temp_stat_identifier}")
                        return True
                    return True
        return False
    # Auto Name sharing #NAM#
    def _send_name_cmd_back(self):
        stat_cfg: dict = self._connection.get_stat_cfg
        name = stat_cfg.get('stat_parm_Name', '')
        if name:
            if self.stat_identifier is not None:
                if self.stat_identifier:
                    if self.stat_identifier.typ == 'SYSOP':
                        self.send_output(f'\r//N {name}\r', env_vars=False)
                    else:
                        self.send_output(f'\rN {name}\r', env_vars=False)
    ###################################
    # Init PoPT Remote (Monitor)
    def _init_popt_remote(self):
        """ Wenn Station Identy empfangen wurde """
        prp = self._prp
        if not hasattr(prp, 'init_prp_handshake'):
            logger.error("CLI: Attribute Error. Can't get PRP")
            return

        prp.init_prp_handshake(self.stat_identifier)

    # GUI
    def _gui_channel_status_change(self):
        if hasattr(self._gui, 'on_channel_status_change'):
            self._gui.on_channel_status_change()

    #########################################################
    # CMD exec
    def _find_cmd(self):
        if self._cmd:
            self._env_var_cmd = False
            inp_cmd = str(self._cmd.decode(self._encoding[0], 'ignore'))
            inp_cmd = inp_cmd.replace(' ', '')
            cmds    = self.get_allowed_cmds()
            treffer = []
            for cmd in cmds:
                if self._command_set[cmd][0]:
                    if inp_cmd == cmd[:self._command_set[cmd][0]]:
                        treffer = [cmd]
                        break
                if inp_cmd == cmd[:len(inp_cmd)]:
                    treffer.append(cmd)

            self._cmd = b''

            # == Keine Treffer
            if not treffer:
                return f"\r # {self._getTabStr_CLI('cmd_not_known')}\r"

            # == Mehrere Treffer
            if len(treffer) > 1:
                return (f"\r # {self._getTabStr_CLI('cmd_not_known')}"
                        f"\r # {(' '.join(treffer))} ?\r")

            cmd = treffer[0]

            # == Ist ausführbar?
            if not callable(self._command_set[cmd][1]):
                return ''

            # == Ausführen!
            ret = tuple(self._command_set[cmd])[1]()

            # == Cleanup
            self.new_last_line = b''

            # == Return
            if ret:
                # == Env Vars
                self._env_var_cmd = self._command_set[cmd][3]
                return ret
            return ''

        return ""

    def exec_cmd(self):
        if not self._last_line.endswith(b'\r'):
            self._last_line += b'\r'
        self._input = self._last_line + self._input
        if self._is_prefix():
            return self._find_cmd()
        # Message is for User ( Text , Chat )
        if self.prefix:
            return ''
        self._ss_state = 0  # Reset Side Stop State to default
        # CMD Input for No User Terminals ( Node ... )
        ret = self._find_cmd()
        if self._crone_state_index not in [100] and \
                self._state_index not in [2, 4, 8]:  # Not Quit| 8 = BBS send msg
            if self.skip_prompt:
                self.skip_prompt = False
            else:
                ret += self.get_ts_prompt()
        return ret

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
    # CMD
    def _cmd_connect(self, exclusive=False):
        self._decode_param()
        if not self._parameter:
            return f"\r {self._getTabStr_CLI('cmd_c_noCall')}\r"

        dest_call = str(self._parameter[0]).upper()
        if not validate_ax25Call(dest_call):
            return f"\r {self._getTabStr_CLI('cmd_c_badCall')}\r"

        port_id = -1
        vias = []
        port_tr = False
        if len(self._parameter) > 1:
            if self._parameter[-1].isdigit():
                port_tr = True
                try:
                    port_id = int(self._parameter[-1])
                    if port_id not in self._port_handler.get_all_ports().keys():
                        return f"\r {self._getTabStr_CLI('cmd_c_noPort')}\r"
                except ValueError:
                    return f"\r {self._getTabStr_CLI('cmd_c_badPort')}\r"

            via_params = self._parameter[1:-1] if port_tr else self._parameter[1:]
            vias = [call.upper() for call in via_params if validate_ax25Call(call.upper())]

        conn = self._port_handler.connection_manager.new_outgoing_connection(
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

    def _cmd_echo(self):  # Echo
        ret = ''
        for el in self._parameter:
            ret += el.decode(self._encoding[0], self._encoding[1]) + ' '
        self.skip_prompt = True
        return ret[:-1] + '\r'

    def _cmd_q(self):  # Quit
        conn_dauer = get_time_delta(self.time_start)
        ret = f"\r # {self._getTabStr_CLI('time_connected')}: {conn_dauer}\r\r"
        ret += self.load_fm_file(self._stat_cfg_index_call + '.btx') + '\r'
        self.send_output(ret, env_vars=True)
        self._crone_state_index = 100  # Quit State
        return ''

    def _cmd_lang(self):
        if not self._parameter:
            return f'\r # {self._getTabStr_CLI("cli_no_lang_param")}{" ".join(list(LANG_IND.keys()))}\r'
        self._decode_param()
        if self._parameter[0].upper() in LANG_IND.keys():
            self._cli_lang = int(LANG_IND.get(self._parameter[0].upper(), 1))
            self._connection.set_user_db_language(self._cli_lang)
            return f'\r # {self._getTabStr_CLI("cli_lang_set")}\r'
        return f'\r # {self._getTabStr_CLI("cli_no_lang_param")}{" ".join(list(LANG_IND.keys()))}\r'

    def _cmd_ch(self):
        if not self._parameter:
            return self._getTabStr_CLI('ch_cmd_param_error')
        if len(self._parameter) > 1:
            param = [self._parameter[0], b' '.join(self._parameter[1:])]
        else:
            param: b'' = self._parameter[0]
            param = param.split(b' ', maxsplit=1)
        if len(param) < 2:
            return self._getTabStr_CLI('ch_cmd_param_error')
        try:
            ch_id = int(param[0])
        except ValueError:
            return self._getTabStr_CLI('ch_cmd_param_error')

        all_conn = self._port_handler.get_all_connections()
        if ch_id not in all_conn:
            return self._getTabStr_CLI('ch_cmd_empty_ch')
        if ch_id == self._connection.ch_index:
            return self._getTabStr_CLI('ch_cmd_own_ch')

        to_conn = all_conn[ch_id]
        to_send = f'\rCH {self._connection.ch_index} ({self._connection.to_call_str}): '.encode('UTF-8', 'ignore')
        to_send += param[1] + b'\r'
        to_conn.send_data(to_send)
        return self._getTabStr_CLI('ch_cmd_send').format(ch_id, to_conn.to_call_str)

    def _cmd_umlaut(self):
        # print(self.parameter)
        if not self._parameter:
            return f"\r{self._getTabStr_CLI('cli_text_encoding_no_param')}: {self._encoding[0]}\r"
        res = find_decoding(self._parameter[0].replace(b'\r', b''))
        if not res:
            return f"\r{self._getTabStr_CLI('cli_text_encoding_error_not_found')}\r"
        self._encoding = res, self._encoding[1]
        if self._user_db_ent:
            self._user_db_ent.Encoding = str(res)
        return f"\r{self._getTabStr_CLI('cli_text_encoding_set')} {res}\r"

    def _cmd_bell(self):
        if not self._connection.noty_bell:
            self._connection.noty_bell = True
            msg = b' '.join(self._parameter)
            msg = msg.decode(self._encoding[0], self._encoding[1])
            self._port_handler.api.set_noty_bell_PH(self._connection.ch_index, msg)
            return f'\r # {self._getTabStr_CLI("cmd_bell")}\r'
        return f'\r # {self._getTabStr_CLI("cmd_bell_again")}\r'

    def _cmd_op(self):
        if not self._parameter:
            self._user_db_ent.cli_sidestop = 0
            ""
            return self._getTabStr_CLI('box_cmd_op1')
        try:
            self._user_db_ent.cli_sidestop = int(self._parameter[0])
        except ValueError:
            return self._getTabStr_CLI('box_cmd_op2')
        return self._getTabStr_CLI('box_cmd_op3').format(self._user_db_ent.cli_sidestop)

    def _cmd_conv(self):
        self.skip_prompt = True
        self._connection.enter_converse_cli()

    # RTT CMD
    def _cmd_rtt(self):
        """ Response executed in self._StrCommands """
        rtt_timer = str(datetime.now().strftime('%H:%M:%S.%f'))
        self.skip_prompt = True
        self.rtt_active  = True

        return f"//E #RTT#{rtt_timer[:-3]}\r"

    # PoPT Remote Monitor
    """
    def _cmd_set_gui_remote_mon(self):
        remote_monitor_conf = getNew_remote_mon_cfg()
        remote_monitor_conf['gui_mon']  = True
        remote_monitor_conf['mon_port'] = 0
        self._connection.set_remote_mon(remote_monitor_conf)
    """

    ##############################################
    def cli_exec(self, inp=b''):
        """ Exec on RX """
        self._raw_input = bytes(inp)
        ret = self._state_exec[self._state_index]()
        if ret:
            self.send_output(ret, env_vars=False)

    def cli_cron(self):
        """ Global Crone Tasks """
        if not self._connection.is_link:
            self.cli_state_crone()

    def cli_state_crone(self):
        """ State Crone Tasks """
        ret = self._cron_state_exec[self._crone_state_index]()
        if ret:
            self.send_output(ret, env_vars=False)

    def cli_update_monitor(self, ax25frame_conf:dict):
        pass

    ########################################################
    # == Helper
    def cli_conn_cleanup(self):
        # ====== APRS Chat
        self._aprs_chat_cmds.aprs_chat_cleanup()

    ########################################################
    # States
    def _s0(self):  # C-Text
        self._state_index = 1
        ret = self._get_own_identy_str() + '\r'
        ret += self._c_text
        ret += self._aprs_chat_cmds.aprs_cText_noty()
        if self.cli_name != CLI_TYP_SYSOP:
            ret += self.get_ts_prompt()
        self.send_output(ret, env_vars=True)
        return ''

    def _s1(self):
        # print("CMD-Handler S1")
        # if not self.stat_identifier:
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
        str_cmd_ret = self._StrCommands.exec_str_cmd(self._last_line + self._raw_input)
        if str_cmd_ret:
            self.send_output(str_cmd_ret, env_vars=False)
            self._last_line    = b''
            self.new_last_line = b''
            return ''
        ########################
        # Check Abort Cmd
        if self._check_abort_cmd():
            return ''
        self._input = self._raw_input               # TODO Cleanup this VAR mess
        self.send_output(self.exec_cmd(), self._env_var_cmd)
        self._last_line = self.new_last_line       # TODO Cleanup this VAR mess
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
            self._gui_channel_status_change()

            self.change_cli_state(1)
            return ''
        res = self._sys_login.step(inp)
        if not res:
            if self._sys_login.fail_counter > 1:
                del self._sys_login
                self._sys_login = None
                # print("Priv: Failed !")
                logger.warning("Priv: Failed !")
                self._gui_channel_status_change()

                self.change_cli_state(1)
            return ""
        if self._sys_login.attempt_count == self._sys_login.attempts:
            del self._sys_login
            self._sys_login = None
            # print("END")
            self.sysop_priv = True
            self._gui_channel_status_change()

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
            self._gui_channel_status_change()

            self.change_cli_state(1)
            return ''
        res = self._sys_login.step(inp)
        if not res:

            if self._sys_login.fail_counter > 20:
                del self._sys_login
                self._sys_login = None
                # print("Priv: Failed !")
                logger.warning(self._logTag + "Priv: Failed !")
                self._gui_channel_status_change()

                self.change_cli_state(1)

            # print("----")
            # self._sys_login.attempts += 1
            return ""
        if self._sys_login.attempt_count == self._sys_login.attempts:
            del self._sys_login
            self._sys_login = None
            # print("END")
            self.sysop_priv = True
            self._gui_channel_status_change()

            self.change_cli_state(1)
        return res

    def _s7(self):
        """ Side Stop / Paging"""
        if not self._raw_input:
            return
        if self._check_abort_cmd():
            self.change_cli_state(1)
            return
        if not self._tx_buffer:
            logger.warning(self._logTag + f"CLI: _s7: No tx_buffer but in S7 !!")
            self.change_cli_state(1)
            return
        if not self._user_db_ent.cli_sidestop:
            logger.warning(self._logTag + f"CLI: _s7: No UserOpt but in S7 !!")
            self.change_cli_state(1)
            return
        eol = find_eol(self._raw_input)
        if self._raw_input in eol:
            self._send_out_sidestop(self._tx_buffer)
            return
        if self._ss_state == 0:
            if self._raw_input.upper() == b'A' + eol:
                self._tx_buffer = bytearray()
                self.send_prompt()
                self.change_cli_state(1)
                return
            if self._raw_input.upper() == b'O' + eol:
                self._connection.send_data(bytearray(self._tx_buffer))
                self._tx_buffer = bytearray()
                self.change_cli_state(1)
                return
        if self._ss_state == 1:
            if self._raw_input.upper() == b'A' + eol:
                self._tx_buffer = bytearray()
                self.send_prompt()
                self.change_cli_state(1)
                return

            if self._raw_input.upper().startswith(b'R'):
                self._tx_buffer = bytearray()
                self.change_cli_state(1)
                self._last_line = b''
                self._input = self._raw_input
                self.send_output(self.exec_cmd(), env_vars=False)
                self._last_line = self.new_last_line
                return

    ########################################################
    # Crone States (called fm tasker)
    @staticmethod
    def _cron_s0():
        """ Dummy for doing nothing """
        return ''

    def _cron_s_quit(self):
        # self._connection: AX25Conn
        if self._connection.is_tx_buff_empty:
            if self._connection.l3_state_id not in [0, 1, 4]:
                self._connection.change_l3_state(4)

