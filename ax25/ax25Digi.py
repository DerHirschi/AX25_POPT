

class AX25DigiConnection:
    def __init__(self, digi_conf: dict):
        self._conf = digi_conf
        self._conf_max_buff = digi_conf.get('max_buff', 2000)
        self._conf_short_via = digi_conf.get('short_via_calls', True)
        self._ax25_conf = digi_conf.get('ax25_conf', {})
        self._digi_call = digi_conf.get('digi_call', '')
        self._rx_conn_uid = self._ax25_conf.get('uid', '')
        self._tx_conn_uid = ''
        self._rx_port = digi_conf.get('port', None)
        self._tx_port = None
        self._rx_conn = None
        self._tx_conn = None
        self._port_handler = None
        if self._rx_port:
            self._port_handler = self._rx_port.port_handler

        self._rx_buff = b''
        self._tx_buff = b''

        self._state = 1             # 1 INIT, 2 Aufbau, ..., 5 Bereit
        self._state_tab = {
            0: self._state_0_error,     # ERROR
            1: self._state_1_rx,        # INIT
        }
        if not all((
                self._ax25_conf,
                self._digi_call,
                self._rx_port,
                self._port_handler
        )):
            self._state = 0

    def _init_digi_conn(self, ax25_frame):
        if self._conf_short_via:
            ax25_frame.short_via_calls()
        self._port_handler.new_outgoing_connection(
            dest_call='',
            own_call='',
            via_calls=[],     # Auto lookup in MH if not exclusive Mode
            port_id=-1,         # -1 Auto lookup in MH list
            # axip_add=('', 0),   # AXIP Adress
            exclusive=False,    # True = no lookup in MH list
            link_conn=None,     # Linked Connection AX25Conn
            # channel=1,          # Channel/Connection Index = Channel-ID
            is_service=True
        )


    def _state_0_error(self, ax25_frame=None):
        pass

    def _state_1_rx(self, ax25_frame):
        if ax25_frame.ctl_byte.flag == 'SABM':
            if not self._tx_conn_uid:
                self._init_digi_conn(ax25_frame)
            # self._tx_port._digi_buf.append(ax25_frame)

    def digi_rx_handle(self, ax25_frame):

        state_exec = self._state_tab.get(self._state, None)
        if not callable(state_exec):
            return
        state_exec(ax25_frame=ax25_frame)

    def digi_crone(self):
        pass

