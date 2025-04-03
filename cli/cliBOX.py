from datetime import datetime

from bbs.bbs_Error import bbsInitError
from bbs.bbs_constant import GET_MSG_STRUC, EOM
from bbs.bbs_fnc import find_eol
from cfg.constant import BBS_SW_ID, NO_REMOTE_STATION_TYPE
from cfg.logger_config import logger, BBS_LOG
from cli.StringVARS import replace_StringVARS
from cli.cliMain import DefaultCLI
from fnc.ax25_fnc import validate_ax25Call
from fnc.str_fnc import get_strTab, zeilenumbruch


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
        self._send_msg_state    = 0

    def init(self):
        self._command_set.update({
            # BOX
            'LB': (2, self._cmd_box_lb, self._getTabStr('cmd_lb')),

            'LN': (2, self._cmd_box_ln, self._getTabStr('cmd_ln')),
            'LM': (2, self._cmd_box_lm, self._getTabStr('cmd_lm')),
            'R':  (1, self._cmd_box_r,  self._getTabStr('cmd_r')),
            'SP': (2, self._cmd_box_sp, self._getTabStr('cmd_sp')),
            'SB': (2, self._cmd_box_sb, self._getTabStr('cmd_sb')),
            'KM': (2, self._cmd_box_km, self._getTabStr('cmd_km')),
            'K':  (1, self._cmd_box_k,  self._getTabStr('cmd_k')),
        })
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

        })

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

        ret = bbs.bbs_id_flag.decode('ASCII', 'ignore') + '\r'
        pms_cfg: dict = bbs.get_pms_cfg()
        self.change_cli_state(1)
        if any((
                self._user_db_ent.TYP in NO_REMOTE_STATION_TYPE,
                self._connection.bbs_connection,
                self._to_call in pms_cfg.get('fwd_bbs_cfg', {}).keys()
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
        if self._to_call in pms_cfg.get('fwd_bbs_cfg', {}).keys():
            self._connection.bbsFwd_start()
        if hasattr(self.stat_identifier, 'typ'):
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
        if self._ss_state == 0:
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
        if self._ss_state == 1:
            if self._raw_input in [b'a\r', b'A\r', b'a\n', b'A\n']:
                self._tx_buffer = b''
                self.send_prompt()
                self.change_cli_state(1)
                return

            if self._raw_input.startswith(b'r') or self._raw_input.startswith(b'R'):
                self._tx_buffer = b''
                self.change_cli_state(1)
                self._last_line = b''
                self._input = self._raw_input
                self._send_output(self._exec_cmd())
                self._last_line = self._new_last_line
                return

    def _s8(self):
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
                self._send_output(self._getTabStr('box_cmd_sp_abort_msg').format(self._out_msg.get('receiver', )))
                self._out_msg = GET_MSG_STRUC()
                return
            self._input = eol.join(lines[1:])

            self._out_msg.update(dict(subject=subject))
            # Text eingeben ... (Ende mit /EX oder Ctrl-Z) :
            self._send_output(self._getTabStr('box_cmd_sp_enter_msg'))
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
                self._send_output("\r # Error !! Please contact Sysop !!\r\r" + self.get_ts_prompt())
                return False

            ret = self._bbs.add_cli_msg_to_fwd_by_id(mid)
            if ret is None:
                logger.error(self._logTag + "_s8: ret is None")
                BBS_LOG.error(self._logTag + "_s8: ret is None")
                self._out_msg = GET_MSG_STRUC()
                self._send_msg_state = 0
                self.change_cli_state(1)
                self._send_output("\r # Error !! Please contact Sysop !!\r\r" + self.get_ts_prompt())
                return False
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
            self._send_output(ret_text)

            self._out_msg = GET_MSG_STRUC()
            self._send_msg_state = 0
            self.change_cli_state(1)
            return

        self._send_msg_state = 0
        self.change_cli_state(1)

    ##############################################
    #
    def _send_output(self, ret, env_vars=True):
        if ret:
            if self._state_index in [8]:
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
    def _cmd_box_lb(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_bl_msg_tabCLI'):
            logger.error("CLI: _cmd_box_lb: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"
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
        msg_list = list(bbs.get_bl_msg_tabCLI())
        msg_list.reverse()
        for el in msg_list:
            flag = 'B'
            # if el[7]:
            #     flag += 'N'
            el = list(el)
            el.append(flag)
            ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
        return ret + '\r'

    def _cmd_box_ln(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_pn_msg_tab_by_call'):
            logger.error("CLI: _cmd_box_lm: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"
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
        msg_list = list(bbs.get_pn_msg_tab_by_call(self._to_call))
        msg_list.reverse()
        for el in msg_list:
            flag = 'P'
            if el[7]:
                flag += 'N'
                el = list(el)
                el.append(flag)
                ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
        return ret + '\r'

    def _cmd_box_lm(self):
        bbs = self._port_handler.get_bbs()
        if not hasattr(bbs, 'get_pn_msg_tab_by_call'):
            logger.error("CLI: _cmd_box_lm: No BBS available")
            return "\r # Error: No Mail-Box available !\r\r"
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
        msg_list = list(bbs.get_pn_msg_tab_by_call(self._to_call))
        msg_list.reverse()
        for el in msg_list:
            flag = 'P'
            if el[7]:
                flag += 'N'
            el = list(el)
            el.append(flag)
            ret += BOX_MAIL_TAB_DATA(el)[:79] + '\r'
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
        if not hasattr(bbs, 'get_pn_msg_tab_by_call'):
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
        except (TypeError, ValueError) as e:
            logger.error(self._logTag + f"_fnc_box_r: raw_msg: {raw_msg}")
            logger.error(self._logTag + f"{e}")
            return self._getTabStr('box_msg_error')
        stat = str(typ)
        if new:
            stat += 'N'
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
