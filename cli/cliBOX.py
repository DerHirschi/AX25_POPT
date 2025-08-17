from datetime import datetime

from bbs.bbs_Error import bbsInitError
from bbs.bbs_constant import GET_MSG_STRUC, EOM
from cfg.constant import BBS_SW_ID, NO_REMOTE_STATION_TYPE, LANG_IND
from cfg.logger_config import logger, BBS_LOG
from cli.StringVARS import replace_StringVARS
from cli.cliMain import DefaultCLI
from fnc.ax25_fnc import validate_ax25Call
from fnc.str_fnc import zeilenumbruch, find_eol


class BoxCLI(DefaultCLI):
    cli_name      = 'BOX'  # DON'T CHANGE!
    service_cli   = True
    prefix        = b''
    sw_id         = BBS_SW_ID
    can_sidestop  = True
    new_mail_noty = True
    def __init__(self, connection):
        DefaultCLI.__init__(self, connection=connection)

        ##################################################
        # Box Stuff
        self._bbs               = self._port_handler.get_bbs()
        if not self._bbs:
            logger.error(self._logTag + f"__init__ no BBS: {self._bbs}")
            raise bbsInitError(f"BoxCLI no BBS: {self._bbs}")
        self._bbs_call          = self._bbs.get_pms_cfg().get('user', '')
        regio                   = self._bbs.get_pms_cfg().get('regio', '')
        if not self._bbs_call:
            logger.error(self._logTag + f"Config Error, no BBS Call set: {self._bbs_call}")
            BBS_LOG.error(self._logTag + f"Config Error, no BBS Call set: {self._bbs_call}")
            self._bbs = None
        if not regio:
            logger.error(self._logTag + f"Config Error, no BBS Regio set: {regio}")
            BBS_LOG.error(self._logTag + f"Config Error, no BBS Regio set: {regio}")
            self._bbs = None
        self._bbs_address       = f"{self._bbs_call}.{regio}"
        self._out_msg           = GET_MSG_STRUC()
        ##################################
        #
        self._send_msg_state    = 0
        self._s9_state          = 0

    def init(self):
        self._command_set.update({
            # BOX
            'LB': (2, self._cmd_box_lb,     self._getTabStr('cmd_lb'),      False),

            'LN': (2, self._cmd_box_ln,     self._getTabStr('cmd_ln'),      False),
            'LM': (2, self._cmd_box_lm,     self._getTabStr('cmd_lm'),      False),
            'LL': (2, self._cmd_box_ll,     self._getTabStr('cmd_ll'),      False),
            'L<': (2, self._cmd_box_l_from, self._getTabStr('cmd_l_from'),  False),
            'L>': (2, self._cmd_box_l_to,   self._getTabStr('cmd_l_to'),    False),
            'L@': (2, self._cmd_box_l_at,   self._getTabStr('cmd_l_at'),    False),
            'R':  (1, self._cmd_box_r,      self._getTabStr('cmd_r'),       False),
            'SP': (2, self._cmd_box_sp,     self._getTabStr('cmd_sp'),      False),
            'SB': (2, self._cmd_box_sb,     self._getTabStr('cmd_sb'),      False),
            'KM': (2, self._cmd_box_km,     self._getTabStr('cmd_km'),      False),
            'K':  (1, self._cmd_box_k,      self._getTabStr('cmd_k'),       False),
        })
        self._commands_cfg = ['QUIT',
                              'BYE',
                              'CH',
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
                              'LL',
                              'L<',
                              'L>',
                              'L@',
                              'R',
                              'SP',
                              'SB',
                              'KM',
                              'K',
                              # CLI OPT
                              'OP',
                              'LANG',
                              'UMLAUT',
                              #
                              'VERSION',
                              'POPT',
                              'HELP',
                              '?']

        self._state_exec.update({
            8: self._s8,  # Send Msg
            9: self._s9   # Unknown User
        })

    ###########################################################
    # States
    def _s0(self):  # C-Text
        bbs = self._port_handler.get_bbs()
        if any((
                not hasattr(bbs, 'get_new_pn_count_by_call'),
                not hasattr(bbs, 'get_pms_cfg'),
                not hasattr(bbs, 'send_sysop_msg'),
        )):
            logger.error(self._logTag + "_s0: No BBS !!")
            self.change_cli_state(2)
            return "\r\r # BBS Error !! \r\r"

        ret = bbs.bbs_id_flag.decode('ASCII', 'ignore') + '\r'
        pms_cfg: dict = bbs.get_pms_cfg()
        self.change_cli_state(1)
        if any((
                self._user_db_ent.TYP in NO_REMOTE_STATION_TYPE,
                self._connection.bbs_connection,
                self._to_call in pms_cfg.get('fwd_bbs_cfg', {}).keys()
        )):
            logger.debug(self._logTag + "No CLI-CMD Mode. No C-Text")
            # self._software_identifier()
            self._send_output(ret + self.get_ts_prompt(), env_vars=True)
            return ''

        ret += self._c_text

        # New User

        if self._user_db_ent.bbs_newUser:
            ret += self._getTabStr('bbs_new_user_reg0')
            for lang, k in LANG_IND.items():
                if self._cli_lang == k:
                    ret += f"{lang}*> {k}\r"
                else:
                    ret += f"{lang} > {k}\r"
            ret += '>'
            #ret += self._getTabStr('bbs_new_user_reg1')
            self._user_db_ent.bbs_newUser = False
            self.change_cli_state(9)
            self.can_sidestop = False
            self._send_output(ret, env_vars=True)
            self._bbs.send_sysop_msg(
                topic=self._getTabStr('bbs_new_user_sysopMsg_top'),
                msg=self._getTabStr('bbs_new_user_sysopMsg_msg').format(self._to_call,
                                                                        bbs.get_pms_cfg().get('user', ''),
                                                                        datetime.now().strftime('%d/%m/%y %H:%M:%S')
                                                                        )
            )
            return ''

        new_mail = bbs.get_new_pn_count_by_call(self._to_call)
        if new_mail:
            ret += self._getTabStr('box_new_mail_ctext').format(new_mail)

        if not self._user_db_ent.PRmail:
            ret += self._getTabStr('box_no_hbbs_address')
        self._send_output(ret + self.get_ts_prompt(), env_vars=True)

        return ''

    def _s1(self):
        """ Exec Cmds """
        bbs = self._port_handler.get_bbs()
        if any((
                not hasattr(bbs, 'get_new_pn_count_by_call'),
                not hasattr(bbs, 'get_pms_cfg'),
        )):
            logger.error(self._logTag + "_s1: No BBS !!")
            self.change_cli_state(2)
            self._crone_state_index = 100  # Quit State
            return "******* PoPT-BBS Error !! \r"
        # print("CMD-Handler S1")
        #if not self.stat_identifier:
        ########################
        if self._connection.bbs_connection:
            return ''
        pms_cfg: dict = bbs.get_pms_cfg()
        if self._to_call in pms_cfg.get('fwd_bbs_cfg', {}).keys():
            if self._connection.bbsFwd_start():
                return ''
            else:
                self._crone_state_index = 100  # Quit State
                return "******* PoPT-BBS Error !! \r"
        self.software_identifier()
        if hasattr(self.stat_identifier, 'typ'):
            if any((
                # Disabling Remote CMDs for non Sysop Stations
                    self.stat_identifier.typ in ['BBS', 'NODE'],
                    self._user_db_ent.TYP in NO_REMOTE_STATION_TYPE,
            )):
                return ''
        ########################
        # Check String Commands
        if not self._exec_str_cmd():
            if self._check_abort_cmd():
                return ''
            self._input = self._raw_input
            self._send_output(self._exec_cmd(), self._env_var_cmd)
        self._last_line = self._new_last_line
        return ''

    def _s2(self):
        """ Quit """
        return self._cmd_q()

    def _s8(self):
        """ Send Message """
        self._input += self._raw_input
        eol = find_eol(self._input)
        if self._send_msg_state == 0:
            # Save Subject Text
            lines = self._input.split(eol)
            subject = lines[0].decode('ASCII', 'ignore')[:79]
            if not subject:
                # Nachricht fuer {} anulliert.
                self._send_msg_state = 0
                self.change_cli_state(1)
                self._send_output(self._getTabStr('box_cmd_sp_abort_msg').format(self._out_msg.get('receiver', ) + self.get_ts_prompt()), env_vars=False)
                self._out_msg = GET_MSG_STRUC()
                return
            self._input = eol.join(lines[1:])

            self._out_msg.update(dict(subject=subject))
            # Text eingeben ... (Ende mit /EX oder Ctrl-Z) :
            self._send_output(self._getTabStr('box_cmd_sp_enter_msg'), env_vars=False)
            self._send_msg_state = 1
            return
        if self._send_msg_state == 1:
            # Save Msg Text
            msg_lines = self._input.split(eol)
            msg       = self._out_msg.get('msg', b'')
            """
            if all((not msg_lines[0], not msg)):
                # Nachricht fuer {} anulliert.
                self._send_msg_state = 0
                self.change_cli_state(1)
                self._send_output(self._getTabStr('box_cmd_sp_abort_msg').format(self._out_msg.get('receiver', )))
                self._out_msg = GET_MSG_STRUC()
                return
            """
            eom_found = False
            while msg_lines:
                line: bytes = msg_lines[0]
                msg_lines = msg_lines[1:]
                if msg_lines:
                    line += eol

                for eom in EOM:
                    if line == eom:
                        eom_found = True
                if eom_found:
                    self._send_msg_state = 2
                    break
                else:
                    msg += line

            self._input = eol.join(msg_lines)
            self._out_msg.update(dict(msg=msg))
            if self._send_msg_state == 1:
                return

        if self._send_msg_state == 2:
            # Send it / Save it
            # print(self._out_msg)
            # Save usw
            mid = self._bbs.new_msg(self._out_msg)
            if not mid:
                logger.error(self._logTag + "_s8: no mid")
                BBS_LOG.error(self._logTag + "_s8: no mid")
                self._out_msg = GET_MSG_STRUC()
                self._send_msg_state = 0
                self.change_cli_state(1)
                self._send_output("\r # Error !! Please contact Sysop !!\r\r" + self.get_ts_prompt(), env_vars=False)
                return

            ret = self._bbs.add_cli_msg_to_fwd_by_id(mid)
            if ret is None:
                logger.error(self._logTag + "_s8: ret is None")
                BBS_LOG.error(self._logTag + "_s8: ret is None")
                self._out_msg = GET_MSG_STRUC()
                self._send_msg_state = 0
                self.change_cli_state(1)
                self._send_output("\r # Error !! Please contact Sysop !!\r\r" + self.get_ts_prompt(), env_vars=False)
                return
            bid, fwd_bbs_list = ret
            # Ok. Nachricht an Adresse MD2SAW @ wird geforwardet
            # ueber: MD2BOX MD2SAW  Mid: 24221-MD2BBS  Bytes: 5
            if fwd_bbs_list:
                ret_text = self._getTabStr('box_cmd_sp_msg_accepted').format(
                    self._out_msg.get('receiver', ''),
                    self._out_msg.get('recipient_bbs', ''),
                    ' '.join(fwd_bbs_list),
                    bid,
                    len(self._out_msg.get('msg', b''))
                )
            else:
                ret_text = self._getTabStr('box_cmd_sp_msg_accepted_local').format(
                    self._out_msg.get('receiver', ''),
                    bid,
                    len(self._out_msg.get('msg', b''))
                )

            ret_text += self.get_ts_prompt()
            self._send_output(ret_text, env_vars=False)

            self._out_msg = GET_MSG_STRUC()
            self._send_msg_state = 0
            self.change_cli_state(1)
            return

        self._send_msg_state = 0
        self.change_cli_state(1)

    def _s9(self):
        """ New User """
        eol = find_eol(self._raw_input)
        if self._s9_state == 0:
            # Language
            if self._raw_input.endswith(eol):
                inp = self._raw_input.replace(eol, b'')
                if not inp:
                    ret = self._getTabStr('bbs_new_user_reg1')
                    if self._user_db_ent.Name:
                        ret += f" {self._user_db_ent.Name} ?\r"
                        ret += self._getTabStr('bbs_new_user_reg_confirm')
                    self._send_output(ret, env_vars=False)
                    self._s9_state = 1
                    return
                try:
                    lang_opt = int(inp.replace(b' ', b''))
                except ValueError:
                    ret = self._getTabStr('box_parameter_error')
                    ret += '\r'
                    ret += self._getTabStr('bbs_new_user_reg0')
                    for lang, k in LANG_IND.items():
                        if self._cli_lang == k:
                            ret += f"{lang}*> {k}\r"
                        else:
                            ret += f"{lang} > {k}\r"
                    ret += '>'
                    self._send_output(ret)
                    return
                if lang_opt not in LANG_IND.values():
                    ret = self._getTabStr('box_parameter_error')
                    ret += '\r'
                    ret += self._getTabStr('bbs_new_user_reg0')
                    for lang, k in LANG_IND.items():
                        if self._cli_lang == k:
                            ret += f"{lang}*> {k}\r"
                        else:
                            ret += f"{lang} > {k}\r"
                    ret += '>'
                    self._send_output(ret)
                    return
                self._connection.set_user_db_language(lang_opt)
            ret = self._getTabStr('bbs_new_user_reg1')
            if self._user_db_ent.Name:
                ret += f" {self._user_db_ent.Name} ?\r"
                ret += self._getTabStr('bbs_new_user_reg_confirm')
            self._send_output(ret, env_vars=False)

            self._s9_state   = 1
        elif self._s9_state == 1:
            # Name
            if self._raw_input == eol and self._user_db_ent.Name:
                pass
            elif self._raw_input.endswith(eol):
                name = self._raw_input.replace(eol, b'').decode(self._encoding[0], 'ignore')
                self._user_db_ent.Name = str(name)
            ret = 'QTH                :'
            if self._user_db_ent.QTH:
                ret += f" {self._user_db_ent.QTH} ?\r"
                ret += self._getTabStr('bbs_new_user_reg_confirm')
            self._send_output(ret)
            self._s9_state = 2
        elif self._s9_state == 2:
            if self._raw_input == eol and self._user_db_ent.QTH:
                pass
            elif self._raw_input.endswith(eol):
                qth = self._raw_input.replace(eol, b'').decode(self._encoding[0], 'ignore')
                self._user_db_ent.QTH = str(qth)
            ret = 'Locator            :'
            if self._user_db_ent.LOC:
                ret += f" {self._user_db_ent.LOC} ?\r"
                ret += self._getTabStr('bbs_new_user_reg_confirm')
            self._send_output(ret)
            self._s9_state   = 3
        elif self._s9_state == 3:
            if self._raw_input == eol and self._user_db_ent.LOC:
                pass
            if self._raw_input.endswith(eol):
                loc = self._raw_input.replace(eol, b'').decode(self._encoding[0], 'ignore').upper()
                self._user_db_ent.LOC = str(loc)
            if self._user_db_ent.PRmail:
                self._send_output(self._getTabStr('bbs_new_user_reg2_1').format(self._user_db_ent.PRmail.split('@')[-1]))
                self._s9_state = 41
            else:
                self._send_output(self._getTabStr('bbs_new_user_reg2_2'), env_vars=False)
                self._s9_state   = 4
        elif self._s9_state == 41:
            if self._raw_input.endswith(eol):
                anw = self._raw_input.replace(eol, b'').upper().replace(b' ', b'')
                if anw in [b'N']:
                    self._send_output(self._getTabStr('bbs_new_user_reg2_2'), env_vars=False)
                    self._s9_state = 4
                else:
                    ret = self._getTabStr('bbs_new_user_reg4').format(self._user_db_ent.Name,
                                                                      self._user_db_ent.PRmail,
                                                                      self._user_db_ent.QTH,
                                                                      self._user_db_ent.LOC,
                                                                      )
                    ret += self.get_ts_prompt()
                    self._send_output(ret, env_vars=True)
                    self._s9_state = 10
                    self.can_sidestop = True
                    self.change_cli_state(1)
        elif self._s9_state == 4:
            if self._raw_input.endswith(eol):
                anw = self._raw_input.replace(eol, b'').upper().replace(b' ', b'')
                if anw in [b'N']:
                    self._send_output(self._getTabStr('bbs_new_user_reg3'), env_vars=False)
                    self._s9_state = 5
                else:
                    pms_cfg  = self._bbs.get_pms_cfg()
                    bbs_call = pms_cfg.get('user', '')
                    regio    = pms_cfg.get('regio', '')
                    if not all((bbs_call, regio)):
                        BBS_LOG.error(self._logTag + f"S9-2: no bbs_call({bbs_call}) or regio({regio})")
                        self._send_output("\r # Error: BBS-Error !\r\r")
                    else:
                        self._user_db_ent.PRmail = f"{self._to_call}@{bbs_call}.{regio}"
                        ret = self._getTabStr('bbs_new_user_reg4').format(self._user_db_ent.Name,
                                                                          self._user_db_ent.PRmail,
                                                                          self._user_db_ent.QTH,
                                                                          self._user_db_ent.LOC,
                                                                          )
                        new_mail = self._bbs.get_new_pn_count_by_call(self._to_call)
                        if new_mail:
                            ret += self._getTabStr('box_new_mail_ctext').format(new_mail)
                        ret += self.get_ts_prompt()
                        self._send_output(ret, env_vars=True)
                    self._s9_state = 10
                    self.can_sidestop = True
                    self.change_cli_state(1)
        elif self._s9_state == 5:
            if self._raw_input.endswith(eol):
                PRmail = self._raw_input.replace(eol, b'').decode(self._encoding[0], 'ignore').upper()
                # TODO Mail Address check
                tmp = PRmail.split('.')
                bbs_call = tmp[0]
                db_ent = self._user_db.get_entry(bbs_call, add_new=False)
                if not db_ent:
                    self._user_db_ent.PRmail = str(PRmail)
                elif not db_ent.TYP:
                    # TODO Set ent to BBS and add Mail Address or Noty Sysop
                    self._user_db_ent.PRmail = str(PRmail)
                elif db_ent.TYP != 'BBS':
                    ret = self._getTabStr('bbs_new_user_error_hbbs_add').format(
                        bbs_call,
                        db_ent.TYP
                    )
                    ret += self._getTabStr('bbs_new_user_reg2_2')
                    self._send_output(ret)
                    self._s9_state = 4
                    return
                elif not db_ent.PRmail:
                    self._user_db_ent.PRmail = str(PRmail)
                else:
                    bbs_add = str(db_ent.PRmail).split('@')[-1]
                    self._user_db_ent.PRmail = f"{self._to_call}@{bbs_add}"


                ret = self._getTabStr('bbs_new_user_reg4').format(self._user_db_ent.Name,
                                                                              self._user_db_ent.PRmail,
                                                                              self._user_db_ent.QTH,
                                                                              self._user_db_ent.LOC,
                                                                              )
                new_mail = self._bbs.get_new_pn_count_by_call(self._to_call)
                if new_mail:
                    ret += self._getTabStr('box_new_mail_ctext').format(new_mail)
                ret += self.get_ts_prompt()
                self._send_output(ret, env_vars=True)
                self._s9_state = 10
                self.can_sidestop = True
                self.change_cli_state(1)
        else:
            BBS_LOG.error(self._logTag + f"S9-?: self._s9_state = {self._s9_state}")
            self._send_output("\r # Error: BBS-Error S9 !\r\r")
            self._s9_state = 10
            self.can_sidestop = True
            self.change_cli_state(1)


    ##############################################
    #
    def _send_output(self, ret, env_vars=False):
        if ret:
            if self._state_index in [8]:
                # Send Msg
                if type(ret) is str:
                    ret = ret.encode(self._encoding[0], self._encoding[1])
                    ret = ret.replace(b'\n', b'\r')
                self._connection.tx_buf_rawData += ret
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
                    self._user_db_ent.cli_sidestop,
            )):
                self._send_out_sidestop(ret)
                return
            self._connection.tx_buf_rawData += ret
    ##############################################
    # BOX
    def _cmd_box_l_from(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_bl_msg_tabCLI'):
            logger.error("CLI: _cmd_box_lb: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        self._decode_param(defaults=[''])
        if not self._parameter:
            return self._getTabStr('box_parameter_error')
        if not self._parameter[0]:
            return self._getTabStr('box_parameter_error')
        param    = self._parameter[0].upper()
        msg_list = bbs.get_l_from(param)

        if not msg_list:
            return f"{self._getTabStr('hint_no_mail_for').format(param)}\r"

        self._ss_state = 1
        ret = '\r'
        BOX_MAIL_TAB_HEADER = (self._getTabStr('box_lm_header') +
                               "===== ==== ====== ====== ====== ====== ====/==== ======\r")
        BOX_MAIL_TAB_DATA = lambda data: (f"{str(data[0]).ljust(5)} "
                                          f"{data[-1].ljust(4)} "
                                          f"{str(data[1]).ljust(6)} "
                                          f"{str(data[2]).ljust(6)}@{str(data[3].split('.')[0]).ljust(6)} "
                                          f"{str(data[4]).ljust(6)} "
                                          f"{''.join(data[5].split(' ')[0].split('-')[1:])}/{''.join(data[5].split(' ')[1].split(':')[:-1])} "
                                          f"{str(data[6])}"
                                          )
        ret += BOX_MAIL_TAB_HEADER
        for el in msg_list:
            try:
                ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
            except IndexError:
                pass
        return ret + '\r'

    def _cmd_box_l_to(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_bl_msg_tabCLI'):
            logger.error("CLI: _cmd_box_lb: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        self._decode_param(defaults=[''])
        if not self._parameter:
            return self._getTabStr('box_parameter_error')
        if not self._parameter[0]:
            return self._getTabStr('box_parameter_error')
        param    = self._parameter[0].upper()
        msg_list = bbs.get_l_to(param, self._to_call)

        if not msg_list:
            return f"{self._getTabStr('hint_no_mail_for').format(param)}\r"

        self._ss_state = 1
        ret = '\r'
        BOX_MAIL_TAB_HEADER = (self._getTabStr('box_lm_header') +
                               "===== ==== ====== ====== ====== ====== ====/==== ======\r")
        BOX_MAIL_TAB_DATA = lambda data: (f"{str(data[0]).ljust(5)} "
                                          f"{data[-1].ljust(4)} "
                                          f"{str(data[1]).ljust(6)} "
                                          f"{str(data[2]).ljust(6)}@{str(data[3].split('.')[0]).ljust(6)} "
                                          f"{str(data[4]).ljust(6)} "
                                          f"{''.join(data[5].split(' ')[0].split('-')[1:])}/{''.join(data[5].split(' ')[1].split(':')[:-1])} "
                                          f"{str(data[6])}"
                                          )
        ret += BOX_MAIL_TAB_HEADER

        for el in msg_list:
            flag = el[-1]
            # if el[7]:
            #     flag += 'N'
            el = list(el)
            el.append(flag)
            try:
                ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
            except IndexError:
                pass
        return ret + '\r'

    def _cmd_box_l_at(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_bl_msg_tabCLI'):
            logger.error("CLI: _cmd_box_lb: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        self._decode_param(defaults=[''])
        if not self._parameter:
            return self._getTabStr('box_parameter_error')
        if not self._parameter[0]:
            return self._getTabStr('box_parameter_error')
        param = self._parameter[0].upper()
        msg_list = bbs.get_l_at(param, self._to_call)

        if not msg_list:
            return f"{self._getTabStr('hint_no_mail_for').format(param)}\r"

        self._ss_state = 1
        ret = '\r'
        BOX_MAIL_TAB_HEADER = (self._getTabStr('box_lm_header') +
                               "===== ==== ====== ====== ====== ====== ====/==== ======\r")
        BOX_MAIL_TAB_DATA = lambda data: (f"{str(data[0]).ljust(5)} "
                                          f"{data[-1].ljust(4)} "
                                          f"{str(data[1]).ljust(6)} "
                                          f"{str(data[2]).ljust(6)}@{str(data[3].split('.')[0]).ljust(6)} "
                                          f"{str(data[4]).ljust(6)} "
                                          f"{''.join(data[5].split(' ')[0].split('-')[1:])}/{''.join(data[5].split(' ')[1].split(':')[:-1])} "
                                          f"{str(data[6])}"
                                          )
        ret += BOX_MAIL_TAB_HEADER

        for el in msg_list:
            flag = el[-1]
            # if el[7]:
            #     flag += 'N'
            el = list(el)
            el.append(flag)
            try:
                ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
            except IndexError:
                pass
        return ret + '\r'

    def _cmd_box_lb(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_bl_msg_tabCLI'):
            logger.error("CLI: _cmd_box_lb: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        msg_list = list(bbs.get_bl_msg_tabCLI())
        if not msg_list:
            return f"{self._getTabStr('hint_no_mail')}\r"

        self._ss_state = 1
        ret = '\r'
        BOX_MAIL_TAB_HEADER = (self._getTabStr('box_lm_header') +
                               "===== ==== ====== ====== ====== ====== ====/==== ======\r")
        BOX_MAIL_TAB_DATA = lambda data: (f"{str(data[0]).ljust(5)} "
                                          f"{data[-1].ljust(4)} "
                                          f"{str(data[1]).ljust(6)} "
                                          f"{str(data[2]).ljust(6)}@{str(data[3]).ljust(6)} "
                                          f"{str(data[4]).ljust(6)} "
                                          f"{''.join(data[5].split(' ')[0].split('-')[1:])}/{''.join(data[5].split(' ')[1].split(':')[:-1])} "
                                          f"{str(data[6])}"
                                          )
        ret += BOX_MAIL_TAB_HEADER
        msg_list.reverse()
        for el in msg_list:
            flag = 'B'
            # if el[7]:
            #     flag += 'N'
            el = list(el)
            el.append(flag)
            print(el)
            try:
                ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
            except IndexError:
                pass
        return ret + '\r'

    def _cmd_box_ln(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_pn_msg_tab_by_call'):
            logger.error("CLI: _cmd_box_lm: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        msg_list = list(bbs.get_pn_msg_tab_by_call(self._to_call))
        if not msg_list:
            return f"{self._getTabStr('hint_no_mail')}\r"
        self._ss_state = 1
        ret = '\r'
        BOX_MAIL_TAB_HEADER = (self._getTabStr('box_lm_header') +
                               "===== ==== ====== ====== ====== ====== ====/==== ======\r")
        BOX_MAIL_TAB_DATA = lambda data: (f"{str(data[0]).ljust(5)} "
                                          f"{data[-1].ljust(4)} "
                                          f"{str(data[1]).ljust(6)} "
                                          f"{str(data[2]).ljust(6)}@{str(data[3].split('.')[0]).ljust(6)} "
                                          f"{str(data[4]).ljust(6)} "
                                          f"{''.join(data[5].split(' ')[0].split('-')[1:])}/{''.join(data[5].split(' ')[1].split(':')[:-1])} "
                                          f"{str(data[6])}"
                                          )
        ret += BOX_MAIL_TAB_HEADER
        msg_list.reverse()
        for el in msg_list:
            flag = 'P'
            if el[7]:
                flag += 'N'
                el = list(el)
                el.append(flag)
                try:
                    ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
                except IndexError:
                    pass
        return ret + '\r'

    def _cmd_box_lm(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_pn_msg_tab_by_call'):
            logger.error("CLI: _cmd_box_lm: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        msg_list = list(bbs.get_pn_msg_tab_by_call(self._to_call))
        if not msg_list:
            return f"{self._getTabStr('hint_no_mail')}\r"
        self._ss_state = 1
        ret = '\r'
        BOX_MAIL_TAB_HEADER = (self._getTabStr('box_lm_header') +
                               "===== ==== ====== ====== ====== ====== ====/==== ======\r")
        BOX_MAIL_TAB_DATA = lambda data: (f"{str(data[0]).ljust(5)} "
                                          f"{data[-1].ljust(4)} "
                                          f"{str(data[1]).ljust(6)} "
                                          f"{str(data[2]).ljust(6)}@{str(data[3].split('.')[0]).ljust(6)} "
                                          f"{str(data[4]).ljust(6)} "
                                          f"{''.join(data[5].split(' ')[0].split('-')[1:])}/{''.join(data[5].split(' ')[1].split(':')[:-1])} "
                                          f"{str(data[6])}"
                                          )
        ret += BOX_MAIL_TAB_HEADER
        msg_list.reverse()
        for el in msg_list:
            flag = 'P'
            if el[7]:
                flag += 'N'
            el = list(el)
            el.append(flag)
            try:
                ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
            except IndexError:
                pass
        return ret + '\r'

    def _cmd_box_ll(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'del_pn_in_by_IDs'):
            logger.error(self._logTag + "_cmd_box_km: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        # self._parameter = self._parameter[0]
        self._decode_param(defaults=[-1])

        if not self._parameter:
            return self._getTabStr('box_parameter_error')
        msg_list = bbs.get_ll(self._parameter[0], self._to_call)
        if not msg_list:
            return f"{self._getTabStr('hint_no_mail')}\r"
        self._ss_state = 1
        ret = '\r'
        BOX_MAIL_TAB_HEADER = (self._getTabStr('box_lm_header') +
                               "===== ==== ====== ====== ====== ====== ====/==== ======\r")
        BOX_MAIL_TAB_DATA = lambda data: (f"{str(data[0]).ljust(5)} "
                                          f"{data[-1].ljust(4)} "
                                          f"{str(data[1]).ljust(6)} "
                                          f"{str(data[2]).ljust(6)}@{str(data[3].split('.')[0]).ljust(6)} "
                                          f"{str(data[4]).ljust(6)} "
                                          f"{''.join(data[5].split(' ')[0].split('-')[1:])}/{''.join(data[5].split(' ')[1].split(':')[:-1])} "
                                          f"{str(data[6])}"
                                          )
        ret += BOX_MAIL_TAB_HEADER
        for el in msg_list:
            flag = el[-1]
            if el[7]:
                flag += 'N'
            el = list(el)
            el.append(flag)
            try:
                ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
            except IndexError:
                pass
        return ret + '\r'


    def _cmd_box_km(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'del_old_pn_msg_by_call'):
            logger.error(self._logTag + "_cmd_box_km: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"
        ret = bbs.del_old_pn_msg_by_call(self._to_call)
        return self._getTabStr('box_msg_del').format(len(ret))

    def _cmd_box_k(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'del_pn_in_by_IDs'):
            logger.error(self._logTag + "_cmd_box_km: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"
        self._parameter = self._parameter[:5]
        default_types = [-1 for x in self._parameter]
        self._decode_param(defaults=default_types)

        ret = bbs.del_pn_in_by_IDs(self._parameter, self._to_call)
        if not ret:
            return self._getTabStr('box_parameter_error')
        ret = [str(x[0]) for x in ret]
        msg_id_str = ' '.join(ret)
        return self._getTabStr('box_msg_del_k').format(msg_id_str)

    def _cmd_box_r(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_pn_msg_by_id') or not hasattr(bbs, 'get_bl_msg_by_id') :
            logger.error(self._logTag + "_cmd_box_r: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"
        try:
            msg_id = int(self._parameter[0])
        except (ValueError, IndexError):
            return self._getTabStr('box_parameter_error')
        msg = bbs.get_pn_msg_by_id(msg_id=msg_id, call=self._to_call)
        if msg:
            return self._fnc_box_r(msg)
        msg = bbs.get_bl_msg_by_id(msg_id=msg_id)
        if msg:
            return self._fnc_box_r(msg)
        return self._getTabStr('box_r_no_msg_found').format(msg_id)

    def _fnc_box_r(self, raw_msg: list):
        try:
            msg_tpl = raw_msg[0]
        except IndexError as e:
            logger.error(self._logTag + f"_fnc_box_r: raw_msg: {raw_msg}")
            logger.error(self._logTag + f"{e}")
            return self._getTabStr('box_msg_error')
        try:
            MSGID, \
            BID, \
            from_call, \
            from_bbs, \
            to_call, \
            to_bbs, \
            size, \
            subject, \
            header, \
            msg, \
            path, \
            msg_time, \
            rx_time, \
            new, \
            flag, \
                typ = msg_tpl
        except Exception as e:
            logger.error(self._logTag + f"_fnc_box_r: raw_msg: {raw_msg}")
            logger.error(self._logTag + f"{e}")
            return self._getTabStr('box_msg_error')
        stat = str(typ)
        if new:
            stat += '/N'
        ret = '\r'
        ret += f"{str(self._getTabStr('from')).ljust(13)}: {from_call}@{from_bbs}\r"
        ret += f"{str(self._getTabStr('to')).ljust(13)}: {to_call}@{to_bbs}\r"
        ret += f"{'Typ/Status'.ljust(13)}: {stat}\r"
        ret += f"{str(self._getTabStr('date_time')).ljust(13)}: {msg_time}\r"
        ret += f"RX {str(self._getTabStr('date_time')).ljust(10)}: {rx_time[2:]}\r"
        ret += f"{'BID'.ljust(13)}: {BID}\r"
        ret += f"{str(self._getTabStr('message') + ' #').ljust(13)}: {MSGID}\r"
        ret += zeilenumbruch(f"{str(self._getTabStr('titel')).ljust(13)}: {subject}\r\r")
        ret += msg.decode(self._encoding[0], self._encoding[1])
        ret += self._getTabStr('box_msg_foter').format(
            MSGID, to_call, from_call, BID
        )
        if all((new, typ == 'P')):
            bbs = self._port_handler.get_bbs()
            if not hasattr(bbs, 'set_in_msg_notNew'):
                logger.error(self._logTag + "_fnc_box_r: No BBS available")
                return ret
            bbs.set_in_msg_notNew(bid=BID)
        return ret

    def _cmd_box_sp(self):
        self._decode_param(defaults=[''])
        if not self._parameter:
            return self._getTabStr('box_error_no_address')

        # if not hasattr(bbs, 'del_pn_in_by_IDs'):
        if not self._bbs:
            logger.error(self._logTag + "_cmd_box_sp: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"
        if not self._user_db:
            logger.error(self._logTag + "_cmd_box_sp: User-DB available")
            return "\r # Error: No User-DB available !\r\r"
        # print(self._parameter)
        parameter: str  = self._parameter[0]
        to_address      = parameter.replace(' ', '').split('@')
        call            = to_address[0].upper()
        try:
            bbs_addr  = to_address[1].upper()
            bbs_call  = bbs_addr.split('.')[0].upper()
        except IndexError:
            bbs_addr = ''
            bbs_call = ''

        if not validate_ax25Call(call):
            return f"\r # Error: Invalid Call > {call} !\r\r"
        if bbs_call and not validate_ax25Call(bbs_call):
            return f"\r # Error: Invalid BBS-Call > {bbs_call} !\r\r"

        self._input   = b''
        self._out_msg = GET_MSG_STRUC()
        self._out_msg.update(dict(
            message_type=   'P',
            sender=         str(self._to_call),
            sender_bbs=     str(self._bbs_address),
            receiver=       str(call),
            recipient_bbs=  str(bbs_addr),
        ))
        user_db_address = self._user_db.get_PRmail(call)
        if user_db_address and '@' in user_db_address:
            if self._bbs_call in user_db_address:
                # Local
                self.change_cli_state(8)
                ret = self._getTabStr('box_cmd_sp_local').format(user_db_address, call)
                return ret
            userdb_bbs_add = user_db_address.split('@')[1]
            self._out_msg.update(dict(recipient_bbs=userdb_bbs_add))
            self.change_cli_state(8)
            ret  = self._getTabStr('box_cmd_sp_routing_to').format(userdb_bbs_add, call)
            return ret
        userdb_bbs_add = self._user_db.get_PRmail(bbs_call)
        if '@' in userdb_bbs_add:
            userdb_bbs_add = userdb_bbs_add.split('@')[1]
        if userdb_bbs_add:
            self.change_cli_state(8)
            ret  = self._getTabStr('box_cmd_sp_routing_to').format(f"{call}@{userdb_bbs_add}", call)
            self._out_msg.update(dict(recipient_bbs=userdb_bbs_add))
            return ret
        if bbs_addr and not '.' in bbs_addr:
            ret = self._getTabStr('box_error_invalid_dist').format(bbs_addr)
            self._out_msg = GET_MSG_STRUC()
            return ret
        # Local
        self.change_cli_state(8)
        ret = self._getTabStr('box_cmd_sp_local').format(call)
        return ret

    def _cmd_box_sb(self):
        self._decode_param(defaults=[''])
        if not self._parameter:
            return self._getTabStr('box_error_no_address')

        # if not hasattr(bbs, 'del_pn_in_by_IDs'):
        if not self._bbs:
            logger.error(self._logTag + "_cmd_box_sb: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"

        parameter: str  = self._parameter[0]
        to_address      = parameter.replace(' ', '').split('@')
        call            = to_address[0].upper()
        try:
            bbs_addr  = to_address[1].upper()
            bbs_call  = bbs_addr.split('.')[0].upper()
        except IndexError:
            bbs_addr = ''
            bbs_call = ''

        if not validate_ax25Call(call):
            return f"\r # Error: Invalid Call > {call} !\r\r"
        if bbs_call and not validate_ax25Call(bbs_call):
            return f"\r # Error: Invalid BBS-Call > {bbs_call} !\r\r"

        self._input   = b''
        self._out_msg = GET_MSG_STRUC()
        self._out_msg.update(dict(
            message_type=   'B',
            sender=         str(self._to_call),
            sender_bbs=     str(self._bbs_address),
            receiver=       str(call),
            recipient_bbs=  str(bbs_addr),
        ))

        # Local
        self.change_cli_state(8)
        bbs_cfg = self._bbs.get_pms_cfg()
        local_theme = bbs_cfg.get('local_theme', [])
        local_dist  = bbs_cfg.get('local_dist',  [])
        if any((not bbs_addr, bbs_addr in local_dist, call in local_theme)):
            ret = self._getTabStr('box_cmd_sp_local').format(call)
        else:
            ret  = self._getTabStr('box_cmd_sp_routing_to').format(bbs_addr, call)
        return ret

    ########################################################################

    def get_ts_prompt(self):
        return f"\r({datetime.now().strftime('%H:%M:%S')}) {self._my_call_str}>\r"

    ########################################################################
    def _baycom_auto_login(self):
        return False
