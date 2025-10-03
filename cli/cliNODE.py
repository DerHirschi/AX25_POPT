from cli.cliMain import DefaultCLI


class NodeCLI(DefaultCLI):
    cli_name = 'NODE'  # DON'T CHANGE !
    service_cli = True
    # _c_text = '-= Test C-TEXT 2=-\r\r'  # Can overwrite in config
    # bye_text = '73 ...\r'
    # prompt = 'PoPT-NODE>'
    prefix = b''
    sw_id = 'PoPTNode'
    can_sidestop = True
    new_mail_noty = True

    # Extra CMDs for this CLI

    def init(self):
        self._commands_cfg  = ['QUIT',
                               'BYE',
                               # NODE
                               'ECHO',
                               'CONNECT',
                               'C!',
                               'CH',
                               'PORT',
                               'MH',
                               'LMH',
                               'AXIP',
                               'DXLIST',
                               'LCSTATUS',
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
                               'CONV',
                               '?']


    def _s2(self):
        return self._cmd_q()

    def _baycom_auto_login(self):
        return False
