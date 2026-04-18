from cfg.popt_config import POPT_CFG


class CoreAPI:
    """ Zentrale API für GPIO/MQTT/... """
    def __init__(self, popt_handler):
        self._popt_handler = popt_handler
        """"""
        self._mh                = lambda : popt_handler.get_MH()
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

