import random

from cfg.logger_config import logger
from cli.cli_main.BaycomLogin import get_baycom_pw
from cli.cli_modulBase import CliModulBase


class BaycomLoginServer(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)
        self._password = self._cliMain.rights_manager.get_auth_password(self._to_call_str)
        self._attempt_count = 0
        self._expected_res = ''
        self._is_auth   = False
        self._text_input = ''
        # ==========================
        self._old_cli_statt = 0
        self._own_state_id  = 50

    @property
    def is_auth(self):
        return self._is_auth

    # ========================================
    # CLI CMD API
    def cmd_baycomSrv_login(self):
        """Sendet eine Challenge an den Client, z.B. 'Enter password chars> 2 5 1 4 3'"""
        if not self._password:
            return "\r # Error: Login not allowed!\r\r"
        self._text_input = ''

        indices = [str(random.randint(1, len(self._password))) for _ in range(5)]
        random.shuffle(indices)
        challenge = ' '.join(indices)
        self._expected_res = get_baycom_pw(self._password, challenge)
        self._old_cli_statt = int(self._cliMain.state_index)
        self._cliMain.skip_prompt = True
        self._cliMain.change_cli_state(self._own_state_id)
        return f"Enter password chars> {challenge}\r"

    def cmd_baycomSrv_logout(self):
        if not self._is_auth:
            return ''
        self._attempt_count = 0
        self._is_auth = False
        logger.info(f"Auth[{self._my_call_str}]: {self._to_call_str} Logout.")
        return f"\r # Successfully logged out \r\r"

    # ========================================
    def _check_response(self):
        """Prüft die Antwort des Clients"""
        self._attempt_count += 1
        old_auth_state = bool(self._is_auth)
        self._is_auth  = bool(self._is_auth or self._expected_res in self._text_input)
        # ==== Logging
        if not old_auth_state and self._is_auth:
            logger.info(f"Auth[{self._my_call_str}]: {self._to_call_str} has granted SYS Privileges on this Station.")
        elif all((not old_auth_state, self._is_auth)):
            logger.warning(f"Auth[{self._my_call_str}]: {self._to_call_str} failed to get SYS Privileges (wrong Password). Attempt: {self._attempt_count}")

        self._text_input = ''

    # ==================================
    # CLI State
    def cli_state_baycom_auth_response(self):
        if not self._raw_input:
            self._cliMain.change_cli_state(self._old_cli_statt)
            return self._get_ts_prompt()

        raw_text: str = self._raw_input.decode(self._get_encoding()[0], 'ignore')
        self._text_input += raw_text
        if not raw_text.endswith('\r') and not raw_text.endswith('\n'):
            return ''

        self._text_input = self._text_input.replace('\n', '\r')
        inp_lines        = self._text_input.split('\r')
        self._text_input = inp_lines[0]

        self._check_response()

        self._cliMain.change_cli_state(self._old_cli_statt)

        rest_input = '\r'.join(inp_lines[1:]).encode(self._get_encoding()[0], 'ignore')
        if rest_input:
            self._cliMain.set_input(rest_input)
            return self._cliMain.exec_cmd()
        return self._get_ts_prompt()


