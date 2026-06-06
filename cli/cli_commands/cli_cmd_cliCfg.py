from cfg.constant import LANG_IND, STATION_ID_ENCODING
from cli.cli_modulBase import CliModulBase
from fnc.str_fnc import find_decoding


class CliCmdCliCFG(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)


    # ==== Paging (OP)
    def cmd_op(self):
        if not self._parameter:
            self._user_db_ent.cli_sidestop = 0
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
            self._cliMain.set_cli_lang(int(LANG_IND.get(self._parameter[0].upper(), 1)))
            return f'\r # {self._getTabStr_CLI("cli_lang_set")}\r'
        return (f'\r # {self._getTabStr_CLI("cli_no_lang_param")}'
                f'\r # {" ".join(list(LANG_IND.keys()))}\r\r')

    # ==== Umlaute / Encoder Erkennung (UM)
    def cmd_umlaut(self):
        # print(self.parameter)
        if not self._parameter:
            return f"\r{self._getTabStr_CLI('cli_text_encoding_no_param')}: {self._cliMain.cli_encoding[0]}\r"
        res = find_decoding(self._parameter[0].replace(b'\r', b''))
        if not res:
            return f"\r{self._getTabStr_CLI('cli_text_encoding_error_not_found')}\r"
        self._cliMain.set_cli_encoding((res, self._cliMain.cli_encoding[1]))
        if self._user_db_ent:
            self._user_db_ent.Encoding = str(res)
        return f"\r{self._getTabStr_CLI('cli_text_encoding_set')} {res}\r"

    # ==== Encoder Erkennung (ENCODER)
    def cmd_enc(self):
        self._decode_param()
        if not self._parameter:
            ret_str = ("\r"
                       f" # {self._getTabStr_CLI('cli_text_encoding_cmd_help')}\r"
                       f" # {self._getTabStr_CLI('cli_text_encoding_current')}: {self._cliMain.cli_encoding[0]}\r"
                        " #\r")

            for k, enc_val in STATION_ID_ENCODING.items():
                if enc_val == self._cliMain.cli_encoding[0]:
                    fill_char = '=>'
                else:
                    fill_char = '= '
                ret_str += f" # {str(k).ljust(2)} {fill_char} {enc_val}\r"
            return ret_str
        try:
            enc_id = int(str(self._parameter[0]).strip())
        except ValueError:
            return self._getTabStr_CLI('box_parameter_error') + '\r'

        encoder_val = STATION_ID_ENCODING.get(enc_id, "")
        if not encoder_val:
            return self._getTabStr_CLI('box_parameter_error') + '\r'

        self._cliMain.set_cli_encoding((encoder_val, self._cliMain.cli_encoding[1]))
        if self._user_db_ent:
            self._user_db_ent.Encoding = str(encoder_val)
        return f"\r{self._getTabStr_CLI('cli_text_encoding_set')} {encoder_val}\r"

