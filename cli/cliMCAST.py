from cfg.logger_config import logger
from cli.cliMain import DefaultCLI
from fnc.socket_fnc import get_ip_by_hostname


class MCastCLI(DefaultCLI):
    cli_name = 'MCAST'  # DON'T CHANGE !
    service_cli = True
    prefix = b''
    sw_id = 'PoPTMCast'
    can_sidestop = True
    new_mail_noty = False

    # Extra CMDs for this CLI

    def init(self):
        # NO USER-DB Ctext
        self._c_text = self._load_fm_file(self._stat_cfg_index_call + '.ctx')
        self._c_text = self._c_text.replace('\n', '\r')
        # Standard Commands ( GLOBAL )
        self._command_set.update( {
            # CMD: (needed lookup len(cmd), cmd_fnc, HElp-Str)
            # MCAST ######################################################
            'CH':       (2, self._cmd_mcast_move_channel, self._getTabStr('cmd_help_mcast_move_ch'),     False),
            'CHLIST':   (3, self._cmd_mcast_channels, self._getTabStr('cmd_help_mcast_channels'),        False),
            'CHINFO':   (3, self._cmd_mcast_channel_info, self._getTabStr('cmd_help_mcast_ch_info'),     False),
            'SETAXIP':  (5, self._cmd_mcast_set_member_axip, self._getTabStr('cmd_help_mcast_set_axip'), False),
            ##############################################################
        })
        self._commands_cfg = ['QUIT',
                              'BYE',
                              ## MCAST
                              'CH',
                              'CHLIST',
                              'CHINFO',
                              'SETAXIP',
                              ## NODE
                              # 'ECHO',
                              # 'CONNECT',
                              # 'C!',
                              # 'PORT',
                              # 'MH',
                              # 'LMH',
                              # 'AXIP',
                              # 'DXLIST',
                              # 'LCSTATUS',
                              ## APRS
                              # 'ATR',
                              # 'WX',
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
                              # 'LB',
                              # 'LN',
                              # 'LM',
                              # 'R',
                              # 'KM',
                              # CLI OPT
                              'OP',
                              'LANG',
                              'UMLAUT',
                              #
                              'VERSION',
                              'POPT',
                              'HELP',
                              '?']
        self._state_exec = {
            0: self._s0,  # C-Text
            1: self._s1,  # Cmd Handler
            2: self._state_error,  #
            3: self._state_error,  #
            4: self._state_error,  #
            5: self._state_error,  #
            6: self._state_error,  #
            7: self._s7,  # Box Side Stop / Paging | Wait for input
        }

    def _state_error(self):
        logger.error(f"CLI: McastCLI: State Error: State {self._state_index}")
        self.change_cli_state(1
                              )
    ###############################################
    def _baycom_auto_login(self):
        return False
    ###############################################

    def cli_exec(self, inp=b''):
        self._raw_input = bytes(inp)
        ret = self._state_exec[self._state_index]()
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
        out =  self._send_sw_id()
        out += self._c_text
        out += f"\r{self._cmd_mcast_channels()}"
        out += f"\r # {self._register_mcast_member()}\r" # TODO Extra CMD etc.
        out += self.get_ts_prompt()
        self._send_output(out, env_vars=True)
        return ''

    def _s1(self):
        self._software_identifier()
        ########################
        # Check String Commands
        if not self._exec_str_cmd():
            self._input = self._raw_input
            self._send_output(self._exec_cmd(), self._env_var_cmd)
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
