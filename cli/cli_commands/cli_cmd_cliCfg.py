from cfg.constant import LANG_IND
from cli.cli_modulBase import CliModulBase
from fnc.str_fnc import find_decoding


class CliCmdCliCFG(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)


    # ==== Paging (OP)
    def cmd_op(self):
        if not self._parameter:
            self._user_db_ent.cli_sidestop = 0
            ""
            return self._getTabStr_CLI('box_cmd_op1')
        try:
            self._user_db_ent.cli_sidestop = int(self._parameter[0])
        except ValueError:
            return self._getTabStr_CLI('box_cmd_op2')
        return self._getTabStr_CLI('box_cmd_op3').format(self._user_db_ent.cli_sidestop)

    # ==== CLI Language (LANG)
    def cmd_lang(self):
        if not self._parameter:
            return (f'\r # {self._getTabStr_CLI("cli_no_lang_param")}'
                    f'\r # {" ".join(list(LANG_IND.keys()))}\r\r')
        self._decode_param()
        if self._parameter[0].upper() in LANG_IND.keys():
            self._cli_lang = int(LANG_IND.get(self._parameter[0].upper(), 1))
            self._connection.set_user_db_language(self._cli_lang)
            return f'\r # {self._getTabStr_CLI("cli_lang_set")}\r'
        return (f'\r # {self._getTabStr_CLI("cli_no_lang_param")}'
                f'\r # {" ".join(list(LANG_IND.keys()))}\r\r')

    # ==== Umlaute / Encoder Erkennung (UM)
    def cmd_umlaut(self):
        # print(self.parameter)
        if not self._parameter:
            return f"\r{self._getTabStr_CLI('cli_text_encoding_no_param')}: {self._encoding[0]}\r"
        res = find_decoding(self._parameter[0].replace(b'\r', b''))
        if not res:
            return f"\r{self._getTabStr_CLI('cli_text_encoding_error_not_found')}\r"
        self._cliMain.set_cli_encoding((res, self._cliMain.cli_encoding[1]))
        if self._user_db_ent:
            self._user_db_ent.Encoding = str(res)
        return f"\r{self._getTabStr_CLI('cli_text_encoding_set')} {res}\r"

