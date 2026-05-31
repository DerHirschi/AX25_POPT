from cli.cli_modulBase import CliModulBase


class CliCmdMonitor(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)
        # ======================
        self._CliMon_manager = self._popt_handler.CliMonManager
        self._is_running = False

    def cmd_monitor(self):
        self._decode_param()
        print(self._parameter)
        if not self._is_running:
            self._start_monitor()
            self._is_running = True
            return
        self._is_running = False
        self._stop_monitor()

    #=======================
    def cleanup(self):
        self._stop_monitor()

    #=======================
    def _start_monitor(self):
        self._cliMain.AprsChat.aprs_chat_quit()
        mon_cfg = dict(
            port_ids=[0],
            filter_calls=[],  # Empty = All(unfiltered)
            filter_exclude=False,  # True  = -MD2SAW CB0SAW / False = +MD2SAW CB0SAW
            filter_own=True  # Filter own Traffic
        )
        self._CliMon_manager.add_subscriber(self._connection, mon_cfg)

    def _stop_monitor(self):
        self._CliMon_manager.del_subscriber(self._connection)
