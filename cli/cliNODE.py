from cfg.constant import CLI_TYP_NODE
from cli.cliMain import DefaultCLI


class NodeCLI(DefaultCLI):
    cli_name = CLI_TYP_NODE  # DON'T CHANGE !
    service_cli = True
    prefix = b''
    sw_id = 'PoPTNode'
    can_sidestop = True
    new_aprs_msg_noty = True

    # Extra CMDs for this CLI

    def init(self):
        pass

    def _s2(self):
        return self._cmd_q()

    def _baycom_auto_login(self):
        return False
