from collections import defaultdict
from datetime import datetime, timedelta

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cli.cli_modulBase import CliModulBase
from fnc.ascii_graph import generate_ascii_graph
from fnc.ax25_fnc import validate_ax25Call
from fnc.str_fnc import get_timedelta_CLIstr, convert_str_to_datetime


class CliCmdStatistics(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main=cli_main)

    # ==============================
    # BWSTAT
    def cmd_bwstat(self):
        mh = self._popt_handler.get_MH()
        if not mh:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r\r'

        out = f"\r {self._getTabStr_CLI('cmd_bwstat_1')}\r"
        total_bw = []
        port_bw  = {}
        port_cfg = dict(POPT_CFG.get_port_CFGs())
        port_ids = list(port_cfg.keys())

        # KORREKTUR: port_bw richtig befüllen
        for k in port_ids:
            bw_list = mh.get_bandwidth(k, baud=port_cfg.get(k, {}).get('parm_baud', 1200))
            port_bw[k] = bw_list[-60:]  # letzten 10 Minuten

        # Gesamtbandbreite
        for i in range(60):
            bw_sum = 0
            count = 0
            for p in port_ids:
                if p in port_bw and i < len(port_bw[p]):
                    bw_sum += port_bw[p][-(i+1)]
                    count += 1
            total_bw.append(bw_sum / count if count else 0)

        graph = generate_ascii_graph(
            [{'total': v} for v in reversed(total_bw[-60:])],
            self._getTabStr_CLI('cmd_bwstat_2'),
            datasets={'total': '█'},
            chart_type='bar',
            graph_height=8,
            graph_width=60,
            bar_mode=True,
            expand=False
        )
        out += graph

        # Einzelne Ports
        for k in port_ids:
            if k not in port_bw or not port_bw[k]:
                continue
            if not sum(port_bw[k]):
                out += f"\r\rPort {k}: {self._getTabStr_CLI('cli_no_data')}"
                continue
            out += '\r\r'
            graph = generate_ascii_graph(
                [{f'P{k}': v} for v in port_bw[k]],
                self._getTabStr_CLI('cmd_bwstat_3').format(k),
                datasets={f'P{k}': '█'},
                chart_type='bar',
                graph_height=8,
                graph_width=60,
                bar_mode=True,
                expand=False
            )
            out += graph

        return out + '\r\r'
    # ==============================
    # PSTAT
    def cmd_pstat(self):
        """ Port Statistiken (wie WX) """
        mh = self._popt_handler.get_MH()
        if not mh:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r\r'

        parm = 168  # Standard: letzte 168 Stunden (7 Tage)
        self._decode_param()
        if self._parameter:
            try:
                parm = int(self._parameter[0])
                if parm < 1:
                    parm = 1
                if parm > 168:  # max 7 Tage
                    parm = 168
            except ValueError:
                pass

        ret = self._get_pstat_cli_out(hours=parm)
        return ret + '\r'

    def _get_pstat_cli_out(self, hours=168):
        mh = self._popt_handler.get_MH()
        if not mh:
            return f'\r # {self._getTabStr_CLI("cli_no_data")}\r\r'

        port_cfg = dict(POPT_CFG.get_port_CFGs())
        now = datetime.now()
        start_time = now - timedelta(hours=hours)

        # EXAKTE INDIzes aus deinem Plot-Script (getestet & 100% korrekt!)
        TIME_IDX        = 1  # timestamt_dt
        N_PACK_IDX      = 3  # Gesamt-Pakete
        N_I_IDX         = 15  # I-Frames (Anzahl)
        N_UI_IDX        = 24  # UI-Frames (Anzahl)
        DATA_DOWN_IDX   = 27  # Payload ↓ (Bytes)
        DATA_UP_IDX     = 26  # Total ↑ (mit Header) → DATA_UP = Total - Payload
        N_REJ_IDX       = 19  # REJ

        # Header
        out = '\r'
        out += f" Port-{self._getTabStr_CLI('statistic')} – {hours} {self._getTabStr_CLI('hours')}\r"
        out += "─" * 79 + "\r"
        out += "Port    Packets  I-Frames  UI       Bytes RX  Bytes TX  REJ  Bandwidth(10m Avg)\r"
        out += "------- -------  --------  -------  --------  --------  ---  ------------------\r"
        total_pac = total_i = total_ui = total_data_down = total_data_up = total_rej = 0
        port_data_raw = {}  # für Graphen später speichern!

        for port_id in self._popt_handler.port_manager.ax25_ports.keys():
            port = self._popt_handler.port_manager.ax25_ports[port_id]
            port_name = str(port.portname)[:4].ljust(4)

            raw_data = mh.PortStat_get_data_by_port(port_id)
            if not raw_data:
                continue

            port_data_raw[port_id] = raw_data  # speichern für Graph!
            pac = i = ui = data_down = data_up = rej = 0

            for row in raw_data:
                try:
                    ts_str = row[TIME_IDX]
                    ts = convert_str_to_datetime(ts_str)
                    if ts < start_time:
                        continue

                    pac       += row[N_PACK_IDX]
                    i         += row[N_I_IDX]
                    ui        += row[N_UI_IDX]
                    data_down += row[DATA_DOWN_IDX]
                    data_up   += row[DATA_UP_IDX] - row[DATA_DOWN_IDX]
                    rej       += row[N_REJ_IDX]

                except (IndexError, ValueError, TypeError) as e:
                    logger.debug(f"PSTAT IndexError bei Port {port_id}: {e} | row: {row}")
                    continue

            total_pac       += pac
            total_i         += i
            total_ui        += ui
            total_data_down += data_down
            total_data_up   += data_up
            total_rej       += rej

            # Bandwidth (letzte 6 Samples = 1 Minute → 10s Avg)
            bw_data = mh.get_bandwidth(port_id, baud=port_cfg.get(port_id, {}).get('parm_baud', 1200))
            bw_avg = sum(bw_data) / len(bw_data) if bw_data else 0.0
            bw_str = f"{bw_avg:5.1f}%"

            out += (f"{port_id:2} {port_name} "
                    f"{pac:7}  {i:8}  {ui:7}  "
                    f" {data_down // 1024:6}k  "
                    f" {data_up // 1024:6}k  "
                    f"{rej:3}  {bw_str}\r")

        # Gesamtzeile
        out += "------- -------  --------  -------  --------  --------  ---  ------------------\r"
        out += (f"        {total_pac:7}  {total_i:8}  {total_ui:7}  "
                f" {total_data_down // 1024:6}k  "
                f" {total_data_up // 1024:6}k  "
                f"{total_rej:3}  Total\r")

        # Bandbreiten-Graph (immer, auch bei >24h)
        #out += '\r' + self._get_port_bw_cli_out()
        # ============================
        # 2. BALKEN-DIAGRAMME (NEU!)
        # ============================
        out += "\r\r" + "═" * 79 + "\r"
        out += f" {self._getTabStr_CLI('history')} (Bytes) – {hours} {self._getTabStr_CLI('hours')}\r"
        out += "═" * 79 + "\r\r"

        # --- Gesamt über alle Ports ---
        total_per_minute = defaultdict(int)
        for port_id, raw_data in port_data_raw.items():
            for row in raw_data:
                try:
                    ts_str = row[1]
                    ts = convert_str_to_datetime(ts_str)
                    if ts < start_time:
                        continue
                    minute_key = ts.strftime("%Y-%m-%d %H:%M")
                    total_per_minute[minute_key] += row[DATA_UP_IDX]  # DATA_W_HEADER
                except Exception as ex:
                    logger.warning(ex)
                    continue

        if total_per_minute:
            sorted_minutes = sorted(total_per_minute.items())
            #dates = [t[0].split(" ")[0] for t in sorted_minutes]
            #values = [t[1] for t in sorted_minutes]

            # Auf Stunden reduzieren (für Lesbarkeit)
            hourly = defaultdict(int)
            hourly_count = defaultdict(int)
            for (ts_str, bytes_val) in sorted_minutes:
                hour_key = ts_str[:13] + ":00"
                hourly[hour_key] += bytes_val
                hourly_count[hour_key] += 1

            graph_data = []
            labels = []
            for hk in sorted(hourly.keys()):
                avg_bytes = hourly[hk] // max(hourly_count[hk], 1)
                graph_data.append({"total": avg_bytes})
                labels.append(hk[11:13] + "h")

            graph = generate_ascii_graph(
                graph_data,
                f"{self._getTabStr_CLI('history')} (Bytes) (all Ports) – {hours}h",
                datasets={'total': '█'},
                chart_type='bar',
                graph_height=10,
                graph_width=min(len(graph_data), 78),
                bar_mode=True,
                expand=True
            )
            out += graph + "\r\r"

        # --- Einzelne Ports ---
        for port_id in sorted(port_data_raw.keys()):
            per_minute = defaultdict(int)
            raw_data = port_data_raw[port_id]

            for row in raw_data:
                try:
                    ts_str = row[1]
                    ts = convert_str_to_datetime(ts_str)
                    if ts < start_time:
                        continue
                    minute_key = ts.strftime("%Y-%m-%d %H:%M")
                    per_minute[minute_key] += row[DATA_UP_IDX]
                except Exception as ex:
                    logger.debug(ex)
                    continue

            if not per_minute:
                continue

            sorted_minutes = sorted(per_minute.items())
            hourly = defaultdict(int)
            hourly_count = defaultdict(int)
            for (ts_str, bytes_val) in sorted_minutes:
                hour_key = ts_str[:13] + ":00"
                hourly[hour_key] += bytes_val
                hourly_count[hour_key] += 1

            graph_data = []
            for hk in sorted(hourly.keys()):
                avg_bytes = hourly[hk] // max(hourly_count[hk], 1)
                graph_data.append({f"P{port_id}": avg_bytes})

            port_name = self._popt_handler.port_manager.ax25_ports[port_id].portname
            graph = generate_ascii_graph(
                graph_data,
                f"Port {port_id} – {port_name} – Bytes/min – {hours}h",
                datasets={f"P{port_id}": '█'},
                chart_type='bar',
                graph_height=8,
                graph_width=min(len(graph_data), 78),
                bar_mode=True,
                expand=True
            )
            out += graph + "\r\r"

        return out + '\r\r'

    # ==============================
    # WX
    def cmd_wx(self):
        """ WX Stations """
        aprs_ais = self._popt_handler.get_aprs_ais()
        if aprs_ais is None:
            return f'\r # {self._getTabStr_CLI("cli_no_wx_data")}\r\r'
        parm = 10
        ret = ''
        self._decode_param()
        if self._parameter:
            if self._parameter[0].isdigit():
                try:
                    parm = int(self._parameter[0])
                except ValueError:
                    pass
                ret = self._get_wx_cli_out(max_ent=parm)
            else:
                call = str(self._parameter[0]).upper()
                if validate_ax25Call(call):
                    le = parm
                    if len(self._parameter) == 2:
                        try:
                            le = int(self._parameter[1])
                        except ValueError:
                            pass
                    ret = self._get_wx_fm_call_cli_out(call=call, max_ent=le)
        else:
            ret = self._get_wx_cli_out(max_ent=parm)
        if not ret:
            return f'\r # {self._getTabStr_CLI("cli_no_wx_data")}\r\r'
        return ret + '\r'

    def _get_wx_fm_call_cli_out(self, call, max_ent=10):
        aprs_ais = self._popt_handler.get_aprs_ais()
        if not hasattr(aprs_ais, 'get_wx_data_f_call'):
            return f'\r # {self._getTabStr_CLI("cli_no_wx_data")}\r\r'
        data       = list(aprs_ais.get_wx_data_f_call(call))
        if not data:
            return ''
        data.reverse()
        data_len = len(data)
        max_c = 0
        loc = f'{data[0][12][:6]}({data[0][16]}km)'
        out = '\r'
        out += f'WX-Station: {call}\r'
        out += f'Locator   : {loc}\r'
        out += f'Comment   : {data[0][11]}\r'
        out += f'Datapoints: {data_len}\r\r'
        out += '-----Last-Port--Temp-Press---Hum-Lum-Rain(24h)-WindGust\r'
        time_range = 72
        init_time  = data[0][15].split(' ')[-1].split(':')[0]
        init_dict  = {}
        if data[0][5]:
            try:
                init_dict['temp'] = float(data[0][5])
            except ValueError:
                pass
        if  data[0][0]:
            try:
                init_dict['pres'] = float(data[0][0])
            except ValueError:
                pass
        if  data[0][1]:
            try:
                init_dict['hum'] = float(data[0][1])
            except ValueError:
                pass

        temp_graph_data = [init_dict]
        for el in data:
            time_st = el[15].split(' ')[-1].split(':')[0]
            if  str(time_st) != str(init_time):
                max_c += 1
                if max_c <= max_ent:
                    # td = get_timedelta_CLIstr(el[15].split(' ')[-1])
                    td = el[15].split(' ')[-1]
                    # pres = f'{el[0]:.2f}'
                    pres = f'{el[0]}'
                    # rain = f'{el[3]:.3f}'
                    rain = f'{el[3]}'
                    # out += f'{td.rjust(9):10}{"":6}'
                    out += f'{td.rjust(9):10}{el[-1]:6}'
                    out += f'{str(el[5]):5}'
                    out += f'{pres:7} '
                    out += f'{el[1]:3} '
                    out += f'{el[9]:3} '
                    out += f'{rain:9} '
                    # out += f'{el[7]:.3f}\r'
                    out += f'{el[7]}\r'


                temp_dict = {}
                if 'temp' in init_dict:
                    try:
                        temp_dict['temp'] = float(el[5])
                    except ValueError:
                        pass
                if 'pres' in init_dict:
                    try:
                        temp_dict['pres'] = float(el[0])
                    except ValueError:
                        pass
                if 'hum' in init_dict:
                    try:
                        temp_dict['hum'] = float(el[1])
                    except ValueError:
                        pass
                temp_graph_data.append(temp_dict)
                init_time = time_st
            if len(temp_graph_data) >= time_range :
                break

        if 'temp' in init_dict:
            datasets = {'temp': '+'}
            temp_graph = generate_ascii_graph(temp_graph_data,
                                         f"{self._getTabStr_CLI('temperature')}(C) - {call} - {time_range} {self._getTabStr_CLI('hours')}",
                                              datasets,
                                              chart_type='line',
                                              graph_height=12,
                                              graph_width=time_range,
                                              expand=True)
            out += '\r'
            out += '\r'
            out += temp_graph

        if 'pres' in init_dict:
            datasets = {'pres': '+'}
            press_graph = generate_ascii_graph(temp_graph_data,
                                              f"{self._getTabStr_CLI('wx_press')}(hPa) - {call} - {time_range} {self._getTabStr_CLI('hours')}",
                                               datasets,
                                               chart_type='line',
                                               graph_height=12,
                                               graph_width=time_range,
                                               expand=True)
            out += '\r'
            out += '\r'
            out += press_graph

        if 'hum' in init_dict:
            datasets = {'hum': '+'}
            hum_graph = generate_ascii_graph(temp_graph_data,
                                              f"{self._getTabStr_CLI('wx_hum')}(%) - {call} - {time_range} {self._getTabStr_CLI('hours')}",
                                             datasets,
                                             chart_type='line',
                                             graph_height=12,
                                             graph_width=time_range,
                                             expand=True)

            out += '\r'
            out += '\r'
            out += hum_graph

        out += '\r'
        return out

    def _get_wx_cli_out(self, max_ent=10):
        db = self._popt_handler.get_database()
        if not db:
            return ''

        # _data = self._port_handler.aprs_ais.get_wx_entry_sort_distance()
        data = db.aprsWX_get_data_f_CLItree(last_rx_days=3)
        if not data:
            return ''

        max_c = 0
        out = '\r-----Last-Port--Call------LOC-------------Temp-Press---Hum-Lum-Rain(24h)-\r'
        for el in data:
            max_c += 1
            if max_c > max_ent:
                break
            # _ent = self._port_handler.aprs_ais.aprs_wx_msg_pool[k][-1]
            td = get_timedelta_CLIstr(convert_str_to_datetime(el[0]))
            loc = f'{el[3].upper()[:6]}({int(el[4])}km)'
            pres = f'{el[5]}'
            rain = f'{el[7]}'
            out += f'{td.rjust(9):10}{el[2]:6}{el[1]:10}{loc:16}'
            out += f'{el[8]:5}'
            out += f'{pres:7} '
            out += f'{el[6]:3} '
            out += f'{el[9]:3} '
            out += f'{rain:6}\r'
        return out

    # ==============================
    # CSTAT
    def cmd_cstats(self):
        # By Grok-AI
        end_date   = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Verbindungshistorie abrufen (kompletter Datensatz)
        mh = self._popt_handler.get_MH()
        if not hasattr(mh, 'get_conn_hist'):
            return "\r # Error: Connection history not available !\r\r"

        conn_hist = mh.get_conn_hist()

        # Datenstruktur für die Statistik: days[date_obj][hour_int] = count
        days = defaultdict(lambda: defaultdict(int))
        total_duration = 0
        unique_users = set()
        total_connections = 0
        #killed_messages = 0  # Annahme: Keine gelöschten Nachrichten
        #read_messages = 0  # Annahme: Keine gelesenen Nachrichten

        # Alle Tage im Zeitraum generieren (für vollständige Tabelle, auch bei 0-Verbindungen)
        start_d  = start_date.date()
        end_d    = end_date.date()
        all_days = []
        current  = start_d
        while current <= end_d:
            all_days.append(current)
            current += timedelta(days=1)
        sorted_days = sorted(all_days)  # Sortiert nach Datum

        # Verbindungen analysieren und filtern
        for entry in conn_hist:
            if not entry.get('disco', False):  # Nur abgeschlossene Verbindungen
                continue
            if entry.get('own_call', '').split('-')[0] != self._my_call_str.split('-')[0]:  # Nur zur eigenen Station
                continue
            conn_time = entry.get('time', datetime.min)
            if not (start_date <= conn_time <= end_date):  # Filter nach Zeitraum
                continue
            duration = entry['duration'].total_seconds() / 60  # Dauer in Minuten
            user = entry['from_call']

            # Tag und Stunde extrahieren
            day_key  = conn_time.date()
            hour_key = conn_time.hour  # int

            # Zählen der Verbindungen pro Tag und Stunde
            days[day_key][hour_key] += 1
            total_duration += duration
            unique_users.add(user)
            total_connections += 1

        # Ausgabe generieren
        ret = '\r'
        ret += f"{f'For the period from {start_date.day}-{start_date.month} to {end_date.day}-{end_date.month}.':^79}\r\r"

        # Stundenüberschrift
        hours_header = ' '.join(f'{h:02d}' for h in range(24))
        ret += f"Da {hours_header} Totl\r"

        # Daten pro Tag (alle Tage im Zeitraum, auch mit 0)
        for day in sorted_days:
            day_str = day.strftime('%d')
            row = [days[day].get(h, 0) for h in range(24)]
            total = sum(row)
            row_str = ' '.join(f'{x if x > 0 else ".":>2}' for x in row)
            ret += f'{day_str} {row_str} {total:>4}\r'

        # Trennlinie (angepasst an 24 Stunden)
        sep_line = ' '.join(['--'] * 24) + ' ----'
        ret += sep_line + '\r'

        # Gesamtsummen pro Stunde (über alle Tage)
        hour_totals = [sum(days[d].get(h, 0) for d in sorted_days) for h in range(24)]
        total_all = sum(hour_totals)
        totals_str = ' '.join(f'{x:>2}' for x in hour_totals)  # >2 für Ausrichtung, " 0" oder " 3"
        ret += f"Tt {totals_str} {total_all:>4}\r"
        ret += '\r'

        # Zusätzliche Metriken
        total_minutes = int(total_duration)
        mean_time_per_conn = total_minutes / total_connections if total_connections > 0 else 0
        mean_time_per_user = total_minutes / len(unique_users) if unique_users else 0

        ret += f"{'Total time of connections':<36}: {total_minutes:>3} minutes, ({total_minutes // 60:>2} H {total_minutes % 60:>2} mn).\r"
        ret += f"{'Mean time per connection':<36}: {mean_time_per_conn:.1f} min/connection.\r"
        ret += f"{'Total time per user':<36}: {mean_time_per_user:.1f} min/user.\r"
        #ret += f"{'Number of killed messages':<36}: {killed_messages:>3}\r"
        #ret += f"{'Number of read messages':<36}: {read_messages:>3}\r"
        ret += f"{'Number of users':<36}: {len(unique_users)}\r"
        unique_users = list(unique_users)
        while len(unique_users) > 4:
            ret += f"{'Users':<36}: {' '.join(unique_users[:5]):>3}\r"
            unique_users = unique_users[5:]
        if unique_users:
            ret += f"{'Users':<36}: {' '.join(unique_users):>3}\r"

        return ret + '\r'

    # ==============================
