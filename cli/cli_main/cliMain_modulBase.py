from fnc.str_fnc import get_strTab


class CliModulBase:
    def __init__(self, cli_main):
        self._cliMain = cli_main
        # ================================
        self._logTag = f"CLI-{cli_main.cli_name}: "
        # ================================
        self._connection    = cli_main.connection
        self._own_port      = cli_main.own_port
        self._port_handler  = cli_main.popt_handler
        self._user_db       = cli_main.userDB
        self._user_db_ent   = cli_main.userDB_ent
        self._cli_lang      = cli_main.cli_lang
        # ================================
        self._my_call_str   = self._connection.my_call_str
        self._to_call_str   = self._connection.to_call_str
        self._to_call       = self._connection.to_call_str.split('-')[0]
        # ================================
        self._get_encoding  = lambda : cli_main.cli_encoding
        self._getTabStr_CLI = lambda str_k: get_strTab(str_k, self._cli_lang)
        # ================================
        self._stat_identifier_str = ''

    @property
    def _parameter(self):
        return self._cliMain.parameter

    @property
    def _stat_identifier(self):
        return self._cliMain.stat_identifier

    def _get_ts_prompt(self):
        return self._cliMain.get_ts_prompt()



