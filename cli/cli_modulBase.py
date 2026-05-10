from fnc.str_fnc import get_strTab


class CliModulBase:
    def __init__(self, cli_main):
        self._cliMain = cli_main
        # ================================
        self._logTag = f"CLI-{cli_main.cli_name}: "
        # ================================
        self._connection    = cli_main.connection
        self._own_port      = cli_main.own_port
        self._popt_handler  = cli_main.popt_handler
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

    @property
    def _raw_input(self):
        return self._cliMain.raw_input

    def _get_ts_prompt(self):
        return self._cliMain.get_ts_prompt()

    def _decode_param(self, defaults=None):
        if defaults is None:
            defaults = []
        if type(defaults) is not list:
            defaults = []
        tmp = []
        if not defaults:
            for el in self._parameter:
                tmp.append(el.decode(self._get_encoding()[0], 'ignore').replace('\r', ''))
        else:
            for el in defaults:
                if len(self._parameter) > len(tmp):
                    tmp_parm = self._parameter[len(tmp)].decode(self._get_encoding()[0], 'ignore').replace('\r', '')
                    try:
                        tmp_parm = type(el)(tmp_parm)
                    except ValueError:
                        tmp_parm = el
                else:
                    tmp_parm = el
                tmp.append(tmp_parm)
        self._cliMain.set_parameter(tmp)


