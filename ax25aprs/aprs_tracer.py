import time
from collections import deque

from ax25.ax25_util.ax25Statistics import get_dx_tx_alarm_his_pack
from ax25aprs.aprs_dec import get_last_digi_fm_path, parse_aprs_fm_aprsframe
from ax25aprs.aprs_constant import APRS_SW_ID, APRS_TRACER_COMMENT
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.loc_fnc import decimal_degrees_to_aprs


class APRSTracer:
    def __init__(self, aprs_main, port_handler):
        logger.info("APRS-Tracer: Init")
        self._aprs_main     = aprs_main
        self._port_handler  = port_handler

        self._ais_cfg   = POPT_CFG.get_CFG_aprs_ais()
        # Packet Pool
        self._be_tracer_traced_packets  = self._ais_cfg.get('be_tracer_traced_packets', {})
        self.be_tracer_alarm_hist       = self._ais_cfg.get('be_tracer_alarm_hist', {})
        # Control vars
        # self._be_tracer_is_alarm = False
        self._be_tracer_tx_trace_packet = ''
        self._be_tracer_tx_rtt          = time.time()
        self._be_tracer_interval_timer  = time.time()
        """ Load CFGs and Init (Login to APRS-Server) """
        self.be_tracer_active       = self._ais_cfg.get('be_tracer_active', False)
        self.be_auto_tracer_active  = self._ais_cfg.get('be_auto_tracer_active', False)
        self._be_auto_tracer_timer  = 0

        self._get_userDB = lambda : self._port_handler.get_userDB()

    # ==========
    def reinit(self):
        self._ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        #self._be_tracer_traced_packets = self._ais_cfg.get('be_tracer_traced_packets', {})
        #self.be_tracer_alarm_hist      = self._ais_cfg.get('be_tracer_alarm_hist', {})

        self._be_tracer_tx_trace_packet = ''
        self._be_tracer_tx_rtt          = time.time()
        self._be_tracer_interval_timer  = time.time()

    def save_param(self):
        logger.info("APRS-Tracer: Save Conf")
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        ais_cfg['be_tracer_active']         = bool(self.be_tracer_active)
        ais_cfg['be_tracer_traced_packets'] = dict(self._be_tracer_traced_packets)
        ais_cfg['be_tracer_alarm_hist']     = dict(self.be_tracer_alarm_hist)
        ais_cfg['be_auto_tracer_duration']  = int(self._ais_cfg['be_auto_tracer_duration'])
        POPT_CFG.set_CFG_aprs_ais(ais_cfg)

    # ==========
    def aprs_tracer_tasker(self):
        # Send Tracer Beacon in intervall
        # self._update_gui_icon()
        if self.be_tracer_active:
            if time.time() > self._be_tracer_interval_timer:
                # print("TRACER TASKER")
                self.tracer_sendit()
                return
        if self.be_auto_tracer_active:
            if not self._ais_cfg.get('be_auto_tracer_duration', 60):
                return
            if time.time() > self._be_auto_tracer_timer:
                return
            if time.time() > self._be_tracer_interval_timer:
                self.tracer_sendit()
                return
    # ==========

    def _tracer_build_msg(self):
        # !5251.12N\01109.78E-27.235MHz P.ython o.ther P.acket T.erminal (PoPT)
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        lat, lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)
        coordinate = decimal_degrees_to_aprs(lat, lon)
        rtt_timer = time.time()
        self._be_tracer_tx_rtt = rtt_timer
        return f'={coordinate[0]}/{coordinate[1]}%{APRS_TRACER_COMMENT} #{self._aprs_main.ais_loc}#{rtt_timer}#'
        # _aprs_msg = _aprs_msg.replace('`', '')

    def _tracer_build_pack(self):
        port_id         = int(self._ais_cfg.get('be_tracer_port', 0))
        station_call    = str(self._ais_cfg.get('be_tracer_station', 'NOCALL'))
        wide_c = self._ais_cfg.get('be_tracer_wide', 1)
        wide = f'WIDE{wide_c}-{wide_c}'
        path = ','.join(list(self._ais_cfg.get('be_tracer_via', [])) + [wide])
        # dest = APRS_SW_ID
        if station_call not in self._port_handler.get_stat_calls_fm_port(port_id):
            return {}
        add_str = f'{station_call}>{APRS_SW_ID},{path}:'
        msg = self._tracer_build_msg()
        aprs_raw = add_str + msg
        aprs_pack = parse_aprs_fm_aprsframe(aprs_raw)
        if not aprs_pack:
            return {}
        aprs_pack['port_id'] = str(port_id)
        aprs_pack['raw_message_text'] = msg
        return aprs_pack

    def tracer_sendit(self):
        if self._ais_cfg.get('be_tracer_station', 'NOCALL') != 'NOCALL':
            pack = self._tracer_build_pack()
            if pack.get('raw_message_text', '') and pack.get('comment', ''):
                self._be_tracer_tx_trace_packet = pack.get('comment', '')
                self._aprs_main.send_APRS_as_UI(pack)
                self._tracer_reset_timer()
                # print(self._tracer_build_msg())

    def _tracer_reset_timer(self):
        self._be_tracer_interval_timer = time.time() + (60 * self._ais_cfg.get('be_tracer_interval', 5))

    def tracer_reset_auto_timer(self, ext_timer=None):
        if ext_timer is None:
            self._be_auto_tracer_timer = time.time() + (self._ais_cfg.get('be_auto_tracer_duration', 60) * 60)
        else:
            self._be_auto_tracer_timer = ext_timer + (self._ais_cfg.get('be_auto_tracer_duration', 60) * 60)

    def tracer_get_last_send(self):
        return time.time() - (self._be_tracer_interval_timer - (60 * self._ais_cfg.get('be_tracer_interval', 5)))

    def tracer_msg_rx(self, pack):
        if pack.get("from", '') != self._ais_cfg.get('be_tracer_station', 'NOCALL'):
            return False
        if pack.get("comment", '') != self._be_tracer_tx_trace_packet:
            return False
        # print(f'Tracer RX: {pack}')
        # print(f'Tracer RX path: {pack["path"]}')
        return self._tracer_add_traced_packet(pack)

    def _tracer_get_rtt_fm_pack(self, pack):
        if not pack.get('comment', False):
            return 0
        rtt_str = str(pack['comment'])
        rtt_str = rtt_str.replace(f'{APRS_TRACER_COMMENT} #{self._aprs_main.ais_loc}#', '')
        rtt_str = rtt_str[:-1]
        try:
            return float(rtt_str)
        except ValueError:
            return 0

    def _tracer_add_traced_packet(self, pack):
        k = pack.get('path', [])
        if not k:
            return False
        k = str(k)
        pack_rtt = self._tracer_get_rtt_fm_pack(pack)
        if not pack_rtt:
            return False
        pack['rtt'] = time.time() - pack_rtt
        # pack['rx_time'] = datetime.now()
        path = pack.get('path', [])
        call = pack.get('via', '')
        if not call and path:
            call = get_last_digi_fm_path(pack)
        if call:
            pack['call'] = str(call)

            loc = ''
            dist = 0
            user_db = self._get_userDB()
            user_db_ent = user_db.get_entry(call_str=call, add_new=True)
            if user_db_ent:
                loc = user_db_ent.LOC
                dist = user_db_ent.Distance
            pack['distance'] = dist
            pack['locator'] = loc
            pack['tr_alarm'] = self._tracer_check_alarm(pack)
            if k in self._be_tracer_traced_packets.keys():
                self._be_tracer_traced_packets[k].append(pack)
            else:
                self._be_tracer_traced_packets[k] = deque([pack], maxlen=100)
            # print(f'Tracer RX dict: {self.be_tracer_traced_packets}')
            # self._tracer_check_alarm(pack)
            # self._tracer_update_gui()
            return True
        return False

    def _tracer_check_alarm(self, pack):
        if not self._ais_cfg.get('be_tracer_alarm_active', False):
            return False
        dist = pack.get('distance', 0)
        if dist >= self._ais_cfg.get('be_tracer_alarm_range', 50):
            # self._be_tracer_is_alarm = True
            if self._port_handler:
                self._port_handler.set_tracerAlarm(True)
            self._tracer_add_alarm_hist(pack)
            return True
        return False

    def _tracer_add_alarm_hist(self, aprs_pack):
        via = ''
        if aprs_pack.get('via', ''):
            if aprs_pack.get('path', []):
                via = get_last_digi_fm_path(aprs_pack)
        else:
            via_list = []
            for _digi in aprs_pack.get('path', []):
                if '*' == _digi[-1]:
                    via_list.append(str(_digi))
            if len(via_list) > 1:
                via = via_list[-2]

        hist_struc = get_dx_tx_alarm_his_pack(
            port_id=aprs_pack.get('port_id', -1),
            call_str=aprs_pack.get('call', ''),
            via=via,
            path=aprs_pack.get('path', []),
            locator=aprs_pack.get('locator', ''),
            distance=aprs_pack.get('distance', -1),
            typ='TRACE',
        )
        self.be_tracer_alarm_hist[str(hist_struc['key'])] = dict(hist_struc)

    def tracer_traces_get(self):
        return self._be_tracer_traced_packets

    def tracer_traces_delete(self):
        self._be_tracer_traced_packets = {}

    def tracer_auto_tracer_set(self, state=None):
        if self.be_tracer_active:
            self.be_auto_tracer_active = False
            return False
        if state is None:
            self.be_auto_tracer_active = not self.be_auto_tracer_active
            self.tracer_reset_auto_timer()
            return bool(self.be_auto_tracer_active)
        self._be_auto_tracer_timer = 0
        self.be_auto_tracer_active = state
        return bool(self.be_auto_tracer_active)

    def tracer_auto_tracer_duration_set(self, dur: int):
        self._ais_cfg['be_auto_tracer_duration'] = dur
        self.save_param()

    def tracer_auto_tracer_get_active_timer(self):
        return self._be_auto_tracer_timer

    def tracer_auto_tracer_get_active(self):
        return self.be_auto_tracer_active

    def tracer_tracer_get_active(self):
        return self.be_tracer_active

