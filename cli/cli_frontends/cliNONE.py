from cfg.constant import CLI_TYP_NO_CLI
from cli.cli_main.cliMain import DefaultCLI


class NoneCLI(DefaultCLI):
    """ ? To Disable CLI / Remote ? """
    cli_name = CLI_TYP_NO_CLI  # DON'T CHANGE !
    service_cli = False
    # _c_text = ''
    # bye_text = ''
    prefix = b''
    can_sidestop = False
    new_aprs_msg_noty = False

    def init(self):
        # self._commands_cfg = []
        pass

    def cli_exec(self, inp=b''):

        self._raw_input += bytes(inp)
        #if self.stat_identifier is None:
        #    self._raw_input += bytes(inp)
        return self._software_identifier()


    def exec_cmd(self):
        return ''

    def cli_cron(self):
        pass

    def _baycom_auto_login(self):
        return False

