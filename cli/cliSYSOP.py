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
