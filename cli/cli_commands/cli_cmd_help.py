from cli.cli_modulBase import CliModulBase


class CliCmdHelp(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

    # ===========================================
    def cmd_help(self):
        # ret = f"\r   < {self._getTabStr('help')} >\r"
        ret = ("\r"
              f"=== {self._getTabStr_CLI('help')} ===\r"
               "--------------------------------------------------\r")
        for k in sorted(list(self._cliMain.get_allowed_cmds())):
            if self._cliMain.command_set[k][2]:
                ret += ' {}{:10} = {}\r'.format(self._cliMain.prefix.decode('UTF-8', 'ignore'),
                                                k,
                                                self._cliMain.command_set[k][2])
        ret += '\r'
        return ret

    def cmd_shelp(self):
        ret = '\r # '
        c = 0
        cmds = list(self._cliMain.get_allowed_cmds())
        cmds.sort()
        for k in cmds:
            ret += (k + ' ')
            if len(ret) - c > 60:
                ret += '\r # '
                c += 60
        ret += '\r\r'
        return ret
