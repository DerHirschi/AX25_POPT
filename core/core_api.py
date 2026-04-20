from cfg.popt_config import POPT_CFG


class CoreAPI:
    """ Zentrale API für GPIO/MQTT/... """
    def __init__(self, popt_handler):
        self._popt_handler = popt_handler
        """"""
        self._mh                = lambda : popt_handler.get_MH()
        self._port_manager      = popt_handler.port_manager
        self._get_macast_server = lambda : popt_handler.get_mcast_server()
        # self._scheduled_tasker  = lambda : popt_handler.get_scheduled_tasker()

    # ===============================================
    def get_dxAlarm(self):
        if hasattr(self._mh(), 'dx_alarm_trigger'):
            return self._mh().dx_alarm_trigger
        return False

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
