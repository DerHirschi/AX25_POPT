

class AX25Digi:
    def __init__(self):
        self._digi_call = ''
        self._rx_conn_uid = ''
        self._tx_conn_uid = ''
        self._rx_port = None
        self._tx_port = None
        self._rx_conn = None
        self._tx_conn = None

        self._rx_buff = b''
        self._tx_buff = b''

        self._state = 1             # 1 INIT, 2 Aufbau, ..., 5 Bereit
        self._state_tab = {
            1: self._state_1_rx,    # INIT
        }

    def _state_1_rx(self, ax25_frame):
        if ax25_frame.ctl_byte.flag == 'SABM':
            self._tx_port._digi_buf.append(ax25_frame)

    def digi_rx_handle(self, ax25_frame):
        state_exec = self._state_tab.get(self._state, None)
        if not callable(state_exec):
            return
        state_exec(ax25_frame=ax25_frame)

    def digi_crone(self):
        pass

