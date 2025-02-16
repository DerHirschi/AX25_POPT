from datetime import datetime

from cfg.constant import BBS_SW_ID, NO_REMOTE_STATION_TYPE
from cfg.logger_config import logger
from cli.cliMain import DefaultCLI
from fnc.str_fnc import get_strTab


class BoxCLI(DefaultCLI):
    cli_name = 'BOX'  # DON'T CHANGE !
    service_cli = True
    # _c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    # bye_text = '73 ...\r'
    # prompt = 'PoPT-NODE>'
    prefix = b''
    sw_id = BBS_SW_ID
    can_sidestop = True
    new_mail_noty = True

    # Extra CMDs for this CLI

    def init(self):

        self._commands_cfg = ['QUIT',
                              'BYE',


                              'LCSTATUS',
                              ## APRS
                              # 'ATR',
                              'WX',
                              ## User Info
                              'BELL',
                              'INFO',
                              'LINFO',
                              'NEWS',
                              # UserDB
                              'USER',
                              'NAME',
                              'QTH',
                              'LOC',
                              'ZIP',
                              'PRMAIL',
                              'EMAIL',
                              'WEB',
                              # BOX
                              'LB',
                              'LN',
                              'LM',
                              'R',
                              'KM',
                              # CLI OPT
                              'OP',
                              'LANG',
                              'UMLAUT',
                              #
                              'VERSION',
                              'POPT',
                              'HELP',
                              '?']
    ###########################################################
    def _s0(self):  # C-Text
        bbs = self._port_handler.get_bbs()
        if any((
                not hasattr(bbs, 'get_new_pn_count_by_call'),
                not hasattr(bbs, 'get_pms_cfg'),
        )):
            logger.error(self._logTag + "_s0: No BBS !!")
            self.change_cli_state(2)
            return "\r\r # BBS Error !! \r\r"

        ret = bbs.pms_flag.decode('ASCII', 'ignore') + '\r'
        pms_cfg: dict = bbs.get_pms_cfg()
        self.change_cli_state(1)
        if any((
                self._user_db_ent.TYP in NO_REMOTE_STATION_TYPE,
                self._connection.bbs_connection,
                self._to_call in pms_cfg.get('home_bbs_cfg', {}).keys()
        )):
            logger.debug(self._logTag + "No CLI-CMD Mode. No C-Text")
            return ret + self.get_ts_prompt()

        ret += self._c_text
        new_mail = bbs.get_new_pn_count_by_call(self._to_call)
        if new_mail:
            ret += get_strTab('box_new_mail_ctext', self._cli_lang).format(new_mail)

        return ret + self.get_ts_prompt()

    def _s1(self):
        bbs = self._port_handler.get_bbs()
        if any((
                not hasattr(bbs, 'get_new_pn_count_by_call'),
                not hasattr(bbs, 'get_pms_cfg'),
        )):
            logger.error(self._logTag + "_s1: No BBS !!")
            self.change_cli_state(2)
            return "\r\r # BBS Error !! \r\r"
        # print("CMD-Handler S1")
        if not self.stat_identifier:
            self._software_identifier()
        ########################
        if self._connection.bbs_connection:
            return
        pms_cfg: dict = bbs.get_pms_cfg()
        if self._to_call in pms_cfg.get('home_bbs_cfg', {}).keys():
            self._connection.bbsFwd_start()
        if any((
                self.stat_identifier.typ in ['BBS', 'NODE'],
                self._user_db_ent.TYP in NO_REMOTE_STATION_TYPE,
        )):
            return
        ########################
        # Check String Commands
        if not self._exec_str_cmd():
            self._input = self._raw_input
            self._send_output(self._exec_cmd())
        self._last_line = self._new_last_line
        return ''

    def _s2(self):
        return self._cmd_q()
    ########################################################################

    def get_ts_prompt(self):
        return f"\r({datetime.now().strftime('%H:%M:%S')}) {self._my_call_str}>\r"
    ########################################################################
    def _baycom_auto_login(self):
        return False
