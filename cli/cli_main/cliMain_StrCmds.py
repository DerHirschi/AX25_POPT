from datetime import datetime, timedelta

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cli.cli_modulBase import CliModulBase


class CliStrCommands(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

        self._str_cmd_exec = {
            b'#REQUESTNAME:':   self._str_cmd_req_name,
            b'#NAM#':           self._cliMain.user_db_cmds.cmd_set_name,
            b'#QTH#':           self._cliMain.user_db_cmds.cmd_set_qth,
            b'#LOC#':           self._cliMain.user_db_cmds.cmd_set_loc,
            b'#RTT#':           self._str_cmd_recv_rtt,
        }

    # =========================================
    # API
    def exec_str_cmd(self, inp_lines: bytes):
        inp_lines = inp_lines.replace(b'\n', b'\r')
        inp_lines = inp_lines.split(b'\r')
        ret = ''
        for li in inp_lines:
            for str_cmd, cmd_fnc in self._str_cmd_exec.items():
                if li.startswith(str_cmd):
                    self._cliMain.set_parameter([li[len(str_cmd):]])
                    ret = cmd_fnc()
                    return ret
        self._cliMain.new_last_line = inp_lines[-1]
        return ret

    # =========================================
    # CMDS
    def _str_cmd_req_name(self):
        stat_cfg: dict = self._connection.get_stat_cfg
        name = stat_cfg.get('stat_parm_Name', '')
        qth = POPT_CFG.get_guiCFG_qth()
        # qth = self._connection.stat_cfg.stat_parm_QTH
        loc = POPT_CFG.get_guiCFG_locator()
        # loc = self._connection.stat_cfg.stat_parm_LOC
        if name:
            name = f'\r#NAM# {name}\r'
        if qth:
            qth = f'\r#QTH# {qth}\r'
        if loc:
            if hasattr(self._stat_identifier, 'software'):
                if 'PoPT' == self._stat_identifier.software:
                    loc = f'\r#LOC# {loc}\r'
            else:
                try:
                    loc = f'\r#LOC# {loc[:6]}\r'
                except IndexError:
                    loc = ''
        tmp = self._parameter[0]
        cmd_dict = {
            b'+++#': name + qth + loc,
            b'++-#': name + qth,
            b'+--#': name,
            b'+-+#': name + loc,
            b'--+#': loc,
            b'-++#': qth + loc,
        }
        req_name = '-'
        req_qth = '-'
        req_loc = '-'
        if self._user_db_ent:
            if not self._user_db_ent.Name:
                req_name = '+'
            if not self._user_db_ent.QTH:
                req_qth = '+'
            if not self._user_db_ent.LOC:
                req_loc = '+'
        req_str = req_name + req_qth + req_loc
        if '+' in req_str:
            req_str = '\r#REQUESTNAME:' + req_str + '#\r'
        else:
            req_str = ''
        if tmp in cmd_dict.keys():
            return cmd_dict[tmp] + req_str
        return ''

    def _str_cmd_recv_rtt(self):
        self._cliMain.skip_prompt = False
        if not self._cliMain.rtt_active:
            return ''
        self._cliMain.rtt_active = False
        try:
            timer_val   = self._parameter[0].decode(self._get_encoding()[0], 'ignore')
            dt_sent = datetime.strptime(timer_val + "000", '%H:%M:%S.%f')
            dt_recv = datetime.now()

            dt_sent_same_day = datetime.combine(dt_recv.date(), dt_sent.time())
            dt_recv_same_day = dt_recv
            # 4. Tagesüberlauf prüfen: wenn empfangen < gesendet → +1 Tag
            if dt_recv_same_day < dt_sent_same_day:
                dt_recv_same_day += timedelta(days=1)

            # 5. Differenz berechnen
            time_d = dt_recv_same_day - dt_sent_same_day
            total_seconds = time_d.total_seconds()
            # 6. In MM:SS.mmm umwandeln
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            milliseconds = int((total_seconds - int(total_seconds)) * 1000)

            str_to_snd = '\r'
            str_to_snd += self._getTabStr_CLI('cmd_rtt_1')
            if minutes:
                str_to_snd += f"{minutes:02d} {self._getTabStr_CLI('minutes')} - "

            str_to_snd += f"{seconds:02d}.{milliseconds:01d} {self._getTabStr_CLI('seconds')}"
            self._cliMain.skip_prompt = False
            str_to_snd += '\r\r'
            if self._cliMain.service_cli:
                return str_to_snd + self._get_ts_prompt()
            return str_to_snd

        except Exception as ex:
            logger.warning(self._logTag + f"RTT parse error: {ex}")
            if self._cliMain.service_cli:
                return ' # Error\r\r' + self._get_ts_prompt()
            return ' # Error\r\r'
