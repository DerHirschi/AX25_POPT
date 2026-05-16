from cfg.constant import VER
from cli.cli_modulBase import CliModulBase
from fnc.os_fnc import is_macos, is_linux, is_windows


class CliCmdInfos(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

    # ================================================
    # POPT
    @staticmethod
    def cmd_popt_banner():
        ret = '\r$$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|\r' \
              '$$  __$$\ $$  __$$\    $$  __$$\|__$$ __|\r' \
              '$$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |\r' \
              '$$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |\r' \
              '$$  ____/ $$ |  $$ |   $$  ____/   $$ |\r' \
              '$$ |      $$ |  $$ |   $$ |        $$ |\r' \
              '$$ |       $$$$$$  |   $$ |        $$ |\r' \
              '\__|yton   \______/ther\__|acket   \__|erminal\r\r' \
              f'Version: {VER}'
        if is_macos():
            ret += ' - MacOS'
        elif is_linux():
            ret += ' - Linux'
        elif is_windows():
            ret += ' - Windows'
        ret += '\r\r'
        return ret

    # ================================================
    # VER
    @staticmethod
    def cmd_ver():
        ret = '\r-= P.yton o.ther P.acket T.erminal =-\r' \
              f'-= Version: {VER}'
        if is_macos():
            ret += ' - MacOS'
        elif is_linux():
            ret += ' - Linux'
        elif is_windows():
            ret += ' - Windows'
        ret += '\r\r'
        return ret

    # ================================================
    # INFO
    def cmd_i(self):
        ret = self._cliMain.load_fm_file(self._cliMain.stat_cfg_index_call + '.itx')
        return ret.replace('\n', '\r')
    # ================================================
    # LINFO
    def cmd_li(self):
        ret = self._cliMain.load_fm_file(self._cliMain.stat_cfg_index_call + '.litx')
        return ret.replace('\n', '\r')
    # ================================================
    # NEWS
    def cmd_news(self):
        ret = self._cliMain.load_fm_file(self._cliMain.stat_cfg_index_call + '.atx')
        return ret.replace('\n', '\r')

