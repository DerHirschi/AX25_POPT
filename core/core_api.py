from cfg.popt_config import POPT_CFG


class CoreAPI:
    """ Zentrale API für GPIO/MQTT/... """
    def __init__(self, popt_handler):
        self._popt_handler = popt_handler
        """"""
        self._gui               = lambda : popt_handler.get_gui()
        self._mh                = lambda : popt_handler.get_MH()
        self._aprs              = lambda : popt_handler.get_aprs_ais()
        self._gpio              = lambda : popt_handler.get_GPIO()
        self._port_manager      = popt_handler.port_manager
        self._get_macast_server = lambda : popt_handler.get_mcast_server()
        # self._scheduled_tasker  = lambda : popt_handler.get_scheduled_tasker()

    # ===============================================
    def get_stat_calls_fm_port(self, port_id=0):
        if port_id not in self._popt_handler.port_manager.ax25_ports.keys():
            return []
        return POPT_CFG.get_stationCalls_fm_port(port_id)

    # ===============================================
    def send_UI(self, conf: dict):
        port_id = conf.get('port_id', 0)
        ax25_ports = self._port_manager.get_all_ports()
        if port_id not in ax25_ports:
            return False
        if not all((
                conf.get('own_call', ''),
                conf.get('add_str', ''),
                conf.get('text', b'')
        )):
            return False
        mcast_server = self._get_macast_server()
        if hasattr(mcast_server, 'get_mcast_port_id'):
            if port_id == mcast_server.get_mcast_port_id():
                mcast_server.send_UI_to_all(conf)
                return True
        ax25_ports[port_id].send_UI_frame(
            own_call=conf.get('own_call', ''),
            add_str=conf.get('add_str', ''),
            text=conf.get('text', b'')[:256],
            cmd_poll=conf.get('cmd_poll', (False, False)),
            pid=conf.get('pid', 0xF0),
        )
        return True

    # ===============================================
    def sysmsg_to_gui(self, msg: str = ''):
        #if self._gui and self.is_running:
        if hasattr(self._gui(), 'sysMsg_to_monitor'):
            self._gui().sysMsg_to_monitor(msg)

    # ===============================================
    def set_dxAlarm(self, set_alarm=True):
        if set_alarm:
            aprs_obj = self._aprs()
            if all((aprs_obj, self._mh())):
                aprs_obj.tracer_reset_auto_timer(self._mh().last_dx_alarm)

            if self._gui():
                self._gui().dx_alarm()
        else:
            if self._mh():
                self._mh().dx_alarm_trigger = False
            if self._gui():
                self._gui().reset_dx_alarm()

    def get_dxAlarm(self):
        if hasattr(self._mh(), 'dx_alarm_trigger'):
            return self._mh().dx_alarm_trigger
        return False
    # ===============================================
    def set_aprsMailAlarm_PH(self, set_alarm=True):
        if self._gui():
            if set_alarm:
                self._gui().set_aprsMail_alarm()
            else:
                self._gui().reset_aprsMail_alarm()

        if hasattr(self._gpio(), 'set_aprs_alarm'):
            self._gpio().set_aprs_alarm(set_alarm)

    def set_pmsMailAlarm(self, set_alarm=True):
        if self._gui():
            if set_alarm:
                self._gui().pmsMail_alarm()
            else:
                self._gui().reset_pmsMail_alarm()

        if hasattr(self._gpio(), 'set_pms_alarm'):
            self._gpio().set_pms_alarm(set_alarm)

    def set_pmsFwdAlarm(self, set_alarm=True):
        if self._gui():
            if set_alarm:
                self._gui().pmsFwd_alarm()
            else:
                self._gui().reset_pmsFwd_alarm()

    def set_tracerAlarm(self, set_alarm=True):
        if self._gui():
            if set_alarm:
                self._gui().tracer_alarm()
            else:
                self._gui().reset_tracer_alarm()

    def set_diesel(self, set_alarm=True):
        if self._gui():
            if set_alarm:
                self._gui().set_diesel()
            else:
                self._gui().reset_diesel()

    # ===============================================
    def set_noty_bell_PH(self, ch_id, msg=''):
        if self._gui():
            self._gui().set_noty_bell(ch_id, msg)

        if hasattr(self._gpio(), 'set_sysop_alarm'):
            self._gpio().set_sysop_alarm(True)

    def reset_noty_bell_PH(self):
        all_conn = self._popt_handler.get_all_connections()
        for ch in all_conn.keys():
            conn = all_conn[ch]
            if conn:
                if conn.noty_bell:
                    return

        if hasattr(self._gui(), 'reset_noty_bell_alarm'):
            self._gui().reset_noty_bell_alarm()

        if hasattr(self._gpio(), 'set_sysop_alarm'):
            self._gpio().set_sysop_alarm(False)

