from cli.cliMain import DefaultCLI


class UserCLI(DefaultCLI):
    cli_name = 'USER'  # DON'T CHANGE !
    service_cli = False
    # _c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    # bye_text = '73 ...\r'
    # prompt = 'TEST-STATION-User-CLI>'
    prefix = b'//'
    sw_id = 'PoPT'
    can_sidestop = False
    new_mail_noty = True
    # Extra CMDs for this CLI

    def init(self):
        """
        self._cmd_exec_ext = {}
        self._cron_state_exec_ext = {}
        self._state_exec_ext = {
            2: self.s2
        }
        """

    def _s2(self):
        return self._cmd_q()
