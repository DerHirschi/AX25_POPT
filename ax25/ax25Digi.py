import time

from ax25.ax25Connection import AX25Conn


class AX25DigiConnection:
    def __init__(self, digi_conf: dict):
        self._conf = digi_conf
        self._conf_max_buff = digi_conf.get('max_buff', 2000)
        self._conf_short_via = digi_conf.get('short_via_calls', True)
        self._conf_last_rx_fail = self._conf.get('last_rx_fail_sec', 20)
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

        self._state = 1             # 1 INIT, 2 Aufbau, ..., 5 Bereit
        self._state_tab = {
            0: self._state_0_error,     # ERROR
            1: self._state_1_rx,        # INIT DIGI-CONN
            2: self._state_2,           # RX SABM and wait for DIGI-CONN (reset fail timer)
            3: self._state_3,           # Connection Established
        }
        self._last_rx = time.time()

        if not all((
                self._ax25_conf,
                self._digi_call,
                self._rx_port,
                self._port_handler
        )):
            self._state_0_error()
            print(f"_ax25_conf: {self._ax25_conf}")
            print(f"_digi_call: {self._digi_call}")
            print(f"_rx_port: {self._rx_port}")
            print(f"_port_handler: {self._port_handler}")

    def _init_digi_conn(self, ax25_frame):
        # ax25_conf = ax25_frame.get_frame_conf()
        self._rx_conn = AX25Conn(ax25_frame, cfg=self._rx_port.port_cfg, port=self._rx_port)
        self._rx_conn.cli.change_cli_state(5)
        self._rx_conn.cli_remote = False
        self._rx_conn.my_call_str = self._digi_call
        self._rx_conn.digi_call = self._digi_call
        if self._rx_conn_uid in self._rx_port.connections.keys():
            self._state_0_error()
            print("ERROR DIGI - Connection ")
            return
        if self._conf_short_via:
            ax25_frame.short_via_calls(self._digi_call)
        ax25_frame_conf = ax25_frame.get_frame_conf()
        tx_conn = self._port_handler.new_outgoing_connection(
            dest_call=self._ax25_conf.get('to_call_str', ''),
            own_call=self._ax25_conf.get('from_call_str', ''),
            via_calls=ax25_frame_conf.get('via_calls_str', []),  # Auto lookup in MH if not exclusive Mode
            port_id=self._rx_port.port_id,  # -1 Auto lookup in MH list
            # axip_add=('', 0),   # AXIP Adress
            exclusive=False,  # True = no lookup in MH list
            # digi_conn=self._rx_conn,  # Linked Connection AX25Conn
            # channel=1,          # Channel/Connection Index = Channel-ID
            is_service=True
        )
        if not tx_conn[0]:
            self._state_0_error()
            print(f"Digi-Error Init: {tx_conn[1]}")
            return
        self._tx_conn = tx_conn[0]
        self._tx_conn.is_link_remote = True
        self._tx_conn.cli_remote = False
        self._tx_conn.my_call_str = self._digi_call
        self._tx_conn.digi_call = self._digi_call
        if not self._tx_conn.new_digi_connection(self._rx_conn):
            self._state_0_error()
            print("Digi-Error _tx_conn.new_digi_connection")
        self._tx_conn_uid = self._tx_conn.uid
        self._tx_port = self._tx_conn.own_port
        print(f"LinkConn : {self._port_handler.link_connections.items()}")
        self._state = 2

    def add_rx_conn_cron(self):
        if not self._rx_conn:
            self._state_0_error()
            return
        if self._link_connections():
            self._rx_port.connections[str(self._rx_conn_uid)] = self._rx_conn
            self._port_handler.insert_new_connection_PH(self._rx_conn, is_service=True)
            self._state = 3
            print(f"LinkConn Accept: {self._port_handler.link_connections.items()}")
            print(f"RX-State: {self._rx_conn.zustand_exec.stat_index}")
            print(f"TX-State: {self._tx_conn.zustand_exec.stat_index}")
            return
        self._state_0_error()

    def _link_connections(self):
        if not self._rx_conn or not self._tx_conn:
            self._state_0_error()
            print('Digi-Conn_link Error: No tx or rx conn')
            return

        if self._rx_conn.new_digi_connection(self._tx_conn):
            print('Digi-Accept')
            return True
        return False

    def _state_0_error(self, ax25_frame=None):
        self._state = 0
        print(f"Digi-Error")
        self._disco_tx_conn()
        self._disco_rx_conn()

    def _state_1_rx(self, ax25_frame):
        if self._rx_conn:
            print(f"Digi: rx-conn: {self._rx_conn} - State: {self._rx_conn.zustand_exec.stat_index}")
        else:
            print(f"Digi: rx-conn: {self._rx_conn}")
        if ax25_frame.ctl_byte.flag == 'SABM':
            if not self._tx_conn_uid:
                self._init_digi_conn(ax25_frame)
            else:
                self._state_0_error()
                print('Digi-SABM-RX')
                # self.crone() # # SABM TX
        elif ax25_frame.ctl_byte.flag == 'DISC':
            self._abort_digi_conn(ax25_frame)
            print('DIGI S! DISC RX')
        else:
            self._state_0_error()
            # MAYBE Fallback to simple Digi Mode ?
            # self._tx_port._digi_buf.append(ax25_frame)

    def _state_2(self, ax25_frame=None):
        if ax25_frame.ctl_byte.flag == 'SABM':
            print('DIGI INIT SABM RX')
            self._last_rx = time.time()
        elif ax25_frame.ctl_byte.flag == 'DISC':
            self._abort_digi_conn(ax25_frame)
            print('DIGI INIT DISC RX')

    def _state_3(self, ax25_frame=None):
        if ax25_frame:
            print(f"DIGI S3: {ax25_frame.ctl_byte.flag}")
            if self._rx_conn:
                self._rx_conn.handle_rx(ax25_frame=ax25_frame)
            print(f"DIGI S3:----------------")
            if self._rx_conn:
                print(f"RX-State: {self._rx_conn.zustand_exec.stat_index}")
            if self._tx_conn:
                print(f"TX-State: {self._tx_conn.zustand_exec.stat_index}")
        if self.is_done():
            self._port_handler.delete_digi_conn(self._rx_conn_uid)

    def is_done(self):
        if all((not self._rx_conn, not self._tx_conn)):
            return True
        if self._rx_conn:
            if self._rx_conn.zustand_exec.stat_index:
                return False
        if self._tx_conn:
            if self._tx_conn.zustand_exec.stat_index:
                return False
        return True

    def _disco_tx_conn(self):
        if self._tx_conn:
            if self._tx_conn.zustand_exec.stat_index:
                self._tx_conn.conn_disco()

    def _disco_rx_conn(self):
        if self._rx_conn:
            if self._rx_conn.zustand_exec.stat_index:
                self._rx_conn.conn_disco()

    def digi_rx_handle(self, ax25_frame):
        state_exec = self._state_tab.get(self._state, None)
        if not callable(state_exec):
            self._state_0_error()
            return
        state_exec(ax25_frame=ax25_frame)

    def _check_last_SABM(self):
        if self._state != 2:
            return False
        if time.time() - self._last_rx > self._conf_last_rx_fail:
            print(f'DIGI _check_last_SABM: ABORT')
            self._abort_digi_conn()

    def _abort_digi_conn(self, ax25_frame=None):
        print(f"DIGI ABORT: {self._rx_conn_uid}")
        if ax25_frame and self._rx_conn:
            self._rx_conn.handle_rx(ax25_frame=ax25_frame)
        self._disco_tx_conn()
        del self._rx_conn
        self._rx_conn = None
        self._state = 3

    def digi_crone(self):
        self._check_last_SABM()
        # self.debug_out()

    def debug_out(self):
        print("DIGI-Debug")
        print(f"RX-CONN-Debug: {self._rx_conn}")
        if self._rx_conn:
            print(f"RX-State-Debug: {self._rx_conn.zustand_exec.stat_index}")
        print(f"TX-CONN-Debug: {self._tx_conn}")
        if self._tx_conn:
            print(f"TX-State-Debug: {self._tx_conn.zustand_exec.stat_index}")


