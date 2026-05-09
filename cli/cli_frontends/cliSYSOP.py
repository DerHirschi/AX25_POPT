from cfg.constant import CLI_TYP_SYSOP
from cli.cli_main.cliMain import DefaultCLI


class UserCLI(DefaultCLI):
    cli_name = CLI_TYP_SYSOP  # DON'T CHANGE !
    service_cli = False
    # _c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    # bye_text = '73 ...\r'
    # prompt = 'TEST-STATION-User-CLI>'
    prefix = b'//'
    sw_id = 'PoPT'
    can_sidestop = False
    new_aprs_msg_noty = False
    # Extra CMDs for this CLI

    def init(self):
        pass

    def _s2(self):
        return self._cmd_q()
