from cli.cli_modulBase import CliModulBase


class CliCmdMonitor(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)
        self.short_help_str = "Monitor [port] +/- [CALL] [CALL] ..."
        # ======================
        self._CliMon_manager = self._popt_handler.CliMonManager
        self._mon_cfg        = dict(
            port_ids=[],
            filter_calls=[],        # Empty = All(unfiltered)
            filter_exclude=False,   # True  = -MD2SAW CB0SAW / False = +MD2SAW CB0SAW
            filter_own=True         # Filter own Traffic
        )
        self._is_running     = False

    def cmd_monitor(self):
        self._decode_param()
        self._clear_mon_conf()

        # ==== Stop
        if not self._parameter:
            if self._is_running:
                self._stop_monitor()
                return '\r # Monitor> OFF\r'
            return f'\r # {self.short_help_str}\r'

        # ==== Start
        if len(self._parameter) == 2:
            return self._getTabStr_CLI('box_parameter_error')+ '\r'

        # Port ID
        try:
            port_id = int(self._parameter[0].strip())
        except (ValueError, IndexError):
            return self._getTabStr_CLI('box_parameter_error') + '\r'

        if port_id not in self._popt_handler.port_manager.get_all_ports():
            return f" {self._getTabStr_CLI('cmd_c_noPort')}\r"

        self._mon_cfg['port_ids'] = [port_id]

        if len(self._parameter) == 1:
            return self._start_monitor()

        # Exclude/Include (+/-)
        excl_filter = {
            '+': False,
            '-': True,
        }.get(self._parameter[1].strip(), None)
        if excl_filter is None:
            return self._getTabStr_CLI('box_parameter_error') + '\r'

        # Calls
        call_filter = [str(x).upper().strip() for x in self._parameter[2:]]
        if not call_filter:
            return self._getTabStr_CLI('box_parameter_error') + '\r'

        self._mon_cfg['filter_exclude'] = excl_filter
        self._mon_cfg['filter_calls']   = call_filter
        return self._start_monitor()

    #=======================
    def cleanup(self):
        self._stop_monitor()

    #=======================
    def _clear_mon_conf(self):
        self._mon_cfg = dict(
            port_ids=[],
            filter_calls=[],  # Empty = All(unfiltered)
            filter_exclude=False,  # True  = -MD2SAW CB0SAW / False = +MD2SAW CB0SAW
            filter_own=True  # Filter own Traffic
        )

    #=======================
    def _start_monitor(self):
        # Stop APRS Chat
        self._cliMain.AprsChat.aprs_chat_quit()
        # Stop if running
        if self._is_running:
            self._stop_monitor()

        if not self._CliMon_manager.add_subscriber(self._connection, self._mon_cfg):
            return "\r # Error CLI-Monitor\r"
        self._is_running = True
        try:
            port = self._mon_cfg['port_ids'][0]
        except IndexError:
            port = 'ERROR'

        call_f = self._mon_cfg['filter_calls']
        excl_f = {True: '-', False: '+'}.get(self._mon_cfg['filter_exclude'], True)
        if not call_f:
            return f'\r  # Monitor> Port={port}\r'

        return f"\r  # Monitor> Port={port}  {excl_f}{' '.join(call_f)}\r"

    def _stop_monitor(self):
        self._CliMon_manager.del_subscriber(self._connection)
        self._is_running = False
        self._cliMain.clear_tx_buffer()

