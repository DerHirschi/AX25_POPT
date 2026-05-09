from datetime import timedelta, datetime

from cfg.constant import BOOL_ON_OFF
from cfg.popt_config import POPT_CFG
from cli.cli_modulBase import CliModulBase
from fnc.str_fnc import get_timedelta_CLIstr, get_timedelta_str_fm_sec


class CliCmdMyHeard(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)
        self._mh = self._popt_handler.get_MH()

    # ==============================
    # MH
    def cmd_mh(self):
        last_port_id = len(self._popt_handler.get_all_port_ids())
        if last_port_id > 20:
            max_ent = int(last_port_id)
        else:
            max_ent = 20
        self._decode_param(defaults=[
            max_ent,  # Entry's
            -1,  # Port
        ])

        parm = self._parameter[0]
        if parm < last_port_id:
            port = self._parameter[0]
            if self._parameter[1] == -1:
                parm = 20
            else:
                parm = self._parameter[1]
        else:
            port = self._parameter[1]
        ret = self._get_mh_out_cli(max_ent=parm, port_id=port)
        return ret + '\r'

    def _get_mh_out_cli(self, max_ent=20, port_id=-1):
        sort_list = self._mh.get_sort_mh_entry('last', False)
        if not sort_list:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r'
        out = ''
        c = 0
        max_c = 0

        for call in list(sort_list.keys()):
            if port_id == -1 or port_id == sort_list[call].port_id:
                max_c += 1
                if max_c > max_ent:
                    break
                time_delta_str = get_timedelta_CLIstr(sort_list[call].last_seen)
                call_str = sort_list[call].own_call
                if sort_list[call].route:
                    call_str += '*'
                out += f'{time_delta_str} P:{sort_list[call].port_id:2} {call_str:10}'.ljust(27, " ")

                c += 1
                if c == 2:  # Breite
                    c = 0
                    out += '\r'
        if not out:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r'
        return '\r' + out

    # ==============================
    # LMH
    def cmd_mhl(self):
        last_port_id = len(self._popt_handler.get_all_port_ids())
        if last_port_id > 10:
            max_ent = int(last_port_id)
        else:
            max_ent = 10
        self._decode_param(defaults=[
            max_ent,  # Entry's
            -1,  # Port
        ])

        parm = self._parameter[0]
        if parm < last_port_id:
            port = self._parameter[0]
            if self._parameter[1] == -1:
                parm = 10
            else:
                parm = self._parameter[1]
        else:
            port = self._parameter[1]

        ret = self._get_mh_long_out_cli(max_ent=parm, port_id=port)

        return ret + '\r'

    def _get_mh_long_out_cli(self, max_ent=10, port_id=-1):
        sort_list = self._mh.get_sort_mh_entry('last', False)
        if not sort_list:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r'
        out = ''
        max_c = 0
        """
        tp = 0
        tb = 0
        rj = 0
        """

        for call in list(sort_list.keys()):
            if port_id == -1 or port_id == sort_list[call].port_id:
                max_c += 1
                if max_c > max_ent:
                    break
                time_delta_str = get_timedelta_CLIstr(sort_list[call].last_seen)
                via = sort_list[call].route
                if via:
                    via = via[-1]
                else:
                    via = ''
                loc = ''
                dis = ''
                typ = ''
                userdb_ent = self._user_db.get_entry(sort_list[call].own_call, add_new=False)
                if userdb_ent:
                    loc = userdb_ent.LOC
                    if userdb_ent.Distance:
                        dis = str(userdb_ent.Distance)
                    typ = userdb_ent.TYP

                out += (f' {time_delta_str:9}{str(sort_list[call].port_id).ljust(5)}{sort_list[call].own_call:10}'
                        f'{via:10}{loc:9}{dis:10}{typ:7}{sort_list[call].pac_n}')

                out += '\r'
        if not out:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r'
        return "\r-----Time-Port-Call------via-------LOC------Dist(km)--Type---Packets\r" + out

    # ==============================
    # CHIST
    def cmd_chist(self):
        """Connection History der eigenen Station (letzte 30 Tage)"""
        mh = self._mh
        if not hasattr(mh, 'get_conn_hist'):
            return f"\r # {self._getTabStr_CLI('cli_no_data')}\r\r"

        # Nur abgeschlossene Verbindungen zu unserer eigenen Station
        own_call_base = self._my_call_str.split('-')[0].upper()
        conn_hist = mh.get_conn_hist()

        now = datetime.now()
        start_time = now - timedelta(days=30)

        entries = []
        for e in conn_hist:
            if not e.get('disco', False):
                continue
            if e.get('own_call', '').split('-')[0].upper() != own_call_base:
                continue
            if 'Task:' in e.get('typ', ''):
                continue
            ts = e.get('time', None)
            if not ts or ts < start_time:
                continue
            entries.append(e)

        # Sortierung: neueste zuerst
        entries.sort(key=lambda x: x.get('time', datetime.min), reverse=True)

        if not entries:
            return f"\r # {self._getTabStr_CLI('cli_no_data')}\r\r"

        out = "\r"
        out += f" Connection-History {own_call_base} – {self._getTabStr_CLI('last_30_days')} ({len(entries)} {self._getTabStr_CLI('connections')})\r"
        out += "─" * 71 + "\r"
        out += self._getTabStr_CLI('cmd_chist_tab')
        out += "────────── ──────── ──────  ───────── ────  ──────────────────────\r"

        for e in entries:
            ts = e.get('time')
            duration = e.get('duration', timedelta())
            dur_str = f"{duration.seconds // 60:02d}:{duration.seconds % 60:02d}"
            if duration.days:
                dur_str = f"{duration.days}d {dur_str}"

            from_call = e.get('from_call', '???')
            port = e.get('port_id', '')
            db_ent = self._user_db.get_entry(from_call, add_new=False)

            loc_dist = ""
            if db_ent:
                if db_ent.LOC:
                    loc_dist = db_ent.LOC.ljust(8)
                if db_ent.Distance != -1:
                    loc_dist += f"  / {db_ent.Distance} km"

            out += f"{ts.strftime('%d.%m.%Y')} {ts.strftime('%H:%M')}    {str(dur_str).ljust(6)}  {from_call.ljust(9)} {str(port).ljust(4)}  {loc_dist[:30]}\r"

        out += "─" * 79 + "\r"
        return out + "\r"

    # ==============================
    # AXIP
    def cmd_axip(self):
        parm = 10
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except ValueError:
                pass
        ret = self._get_axip_out_cli(max_ent=parm)

        return ret + '\r'

    def _get_axip_out_cli(self, max_ent=10):
        ent = self._mh.get_sort_mh_entry('last', reverse=False)
        dbl_ent = []
        if not ent:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r'
        max_c = 0
        out = '\r'
        # out += '\r                       < AXIP - Clients >\r\r'
        out += '-Call------IP:Port---------------------------Last------------\r'
        for k in ent.keys():
            if ent[k].own_call not in dbl_ent:
                dbl_ent.append(ent[k].own_call)
                axip_add = self._mh.get_AXIP_fm_DB_MH(ent[k].own_call)
                if axip_add[0]:
                    max_c += 1
                    if max_c > max_ent:
                        break
                    out += ' {:9} {:33} {:8}\r'.format(
                        ent[k].own_call,
                        axip_add[0] + ':' + str(axip_add[1]),
                        get_timedelta_CLIstr(ent[k].last_seen, r_just=False)
                    )
        return out

    # ==============================
    # DXLIST
    def cmd_dxlist(self):
        parm = 10
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except ValueError:
                pass
        ret = self._get_alarm_out_cli(max_ent=parm)

        return ret + '\r'

    def _get_alarm_out_cli(self, max_ent=10):
        alarm_his       = dict(self._mh.dx_alarm_perma_hist)
        aprs_main = self._popt_handler.get_aprs_ais()
        if hasattr(aprs_main, 'get_be_tracer_alarm_hist'):
            tracer_his = dict(aprs_main.get_be_tracer_alarm_hist())
            alarm_his.update(tracer_his)

        if not alarm_his:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r'
        out = '\r'
        out += "-----Time-Port---Call------via-------LOC------Dist(km)--Type---\r"
        max_c = 0
        key_list = list(alarm_his.keys())
        key_list.sort(reverse=True)
        for k in key_list:
            max_c += 1
            if max_c > max_ent:
                break
            ent = alarm_his.get(k,{})

            td_ent = ent.get('ts', None)
            time_delta_str = get_timedelta_CLIstr(td_ent) if td_ent is not None else 'n.a.'

            via     = ent.get('via', '')
            loc     = ent.get('loc', '')
            dis     = str(ent.get('dist', -1))
            typ     = ent.get('typ', '')
            port    = str(ent.get('port_id', -1))
            call    = ent.get('call_str', '')

            out += f' {time_delta_str} {port:6} {call:10}{via:10}{loc:9}{dis:10}{typ}\r'

        return out

    # ==============================
    # ATR
    def cmd_aprs_trace(self):
        """APRS Tracer"""
        aprs_ais = self._popt_handler.get_aprs_ais()
        if aprs_ais is None:
            return f'\r # {self._getTabStr_CLI("cli_no_tracer_data")}\r\r'
        parm = 10
        if self._parameter:
            try:
                parm = int(self._parameter[0])
            except ValueError:
                pass
        data = aprs_ais.tracer_traces_get()
        if not data:
            return f'\r # {self._getTabStr_CLI("cli_no_tracer_data")}\r\r'
        ais_cfg     = POPT_CFG.get_CFG_aprs_ais()
        intervall   = ais_cfg.get('be_tracer_interval', 5)
        active      = ais_cfg.get('be_tracer_active', 5)
        last_send   = aprs_ais.tracer_get_last_send()
        last_send   = get_timedelta_str_fm_sec(last_send, r_just=False)
        if not active:
            intervall_str = 'off'
        else:
            intervall_str = str(intervall)
        # out = '\r # APRS-Tracer Beacon\r\r'
        out = '\r'
        out += f"Tracer Port     : {ais_cfg.get('be_tracer_port', 0)}\r"
        out += f"Tracer Call     : {ais_cfg.get('be_tracer_station', 'NOCALL')}\r"
        out += f"Tracer WIDE Path: {ais_cfg.get('be_tracer_wide', 1)}\r"
        out += f'Tracer intervall: {intervall_str}\r'
        out += f"Auto Tracer     : {BOOL_ON_OFF.get(ais_cfg.get('be_auto_tracer_active', False), False).lower()}\r"
        # out += f'APRS-Server     : {constant.BOOL_ON_OFF.get(self._port_handler.aprs_ais., False).lower()}\r'
        out += f'Last Trace send : {last_send}\r\r'
        out += '-----Last-Port--Call------LOC-------------Path----------------------------------\r'
        max_c = 0
        for k in data:
            max_c += 1
            if max_c > parm:
                break
            ent = data[k][-1]
            td = get_timedelta_CLIstr(ent['rx_time'])
            # path = ', '.join(ent.get('path', []))
            loc = f'{ent.get("locator", "------")[:6]}({round(ent.get("distance", -1))}km)'
            call = ent.get('call', '')
            path_raw = ent.get('path', [])
            path = ''
            c = 0
            for _el in path_raw:
                path += f'{_el}> '
                c += 1
                if c == 3:
                    path += '\r' + ''.rjust(42, ' ')
                    c = 0

            out += f'{td.rjust(9):10}{ent.get("port_id", "-"):6}{call:10}{loc:16}'
            out += f'{path[:-2]}'
            out += '\r'

        return out + '\r'

