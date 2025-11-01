from cli.cliMain import DefaultCLI


class NodeCLI(DefaultCLI):
    cli_name = 'NODE'  # DON'T CHANGE !
    service_cli = True
    prefix = b''
    sw_id = 'PoPTNode'
    can_sidestop = True
    new_aprs_msg_noty = True

    # Extra CMDs for this CLI

    def init(self):
        self._commands_cfg  = ['QUIT',
                               'BYE',
                               # NODE
                               'ECHO',
                               'CONNECT',
                               'C!',
                               'CH',
                               'CONV',
                               'PORT',
                               'MH',
                               'LMH',
                               'AXIP',
                               'DXLIST',
                               'LCSTATUS',
                               'CSTAT',
                               'RTT',
                               # APRS
                               'ATR',
                               'WX',
                               # User Info
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
                               #'LB',
                               #'LN',
                               #'LM',
                               #'R',
                               #'KM',
                               # CLI OPT
                               'OP',
                               'LANG',
                               'UMLAUT',
                               #
                               'VERSION',
                               'POPT',
                               'HELP',
                               '?']


    def _s2(self):
        return self._cmd_q()

    def _baycom_auto_login(self):
        return False
