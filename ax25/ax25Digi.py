import time
from ax25.ax25Connection import AX25Conn
from cfg.logger_config import logger


class AX25DigiConnection:
    def __init__(self, digi_conf: dict):
        self._conf_max_buff = digi_conf.get('max_buff', 10)
        self._conf_max_n2 = digi_conf.get('max_n2', 5)
        self._conf_short_via = digi_conf.get('short_via_calls', True)
        self._conf_UI_short_via = digi_conf.get('UI_short_via', True)
        self._conf_last_rx_fail = digi_conf.get('last_rx_fail_sec', 20)
        self._conf_digi_ssid_port = digi_conf.get('digi_ssid_port', True)
        self._conf_digi_auto_port = digi_conf.get('digi_auto_port', True)
        self._ax25_conf = digi_conf.get('ax25_conf', {})
        self._digi_call = digi_conf.get('digi_call', '')
        self._digi_ssid = digi_conf.get('digi_ssid', 0)
        self._rx_conn_uid = self._ax25_conf.get('uid', '')
        self._tx_conn_uid = ''
        self._rx_port = digi_conf.get('rx_port', None)
        self._tx_port = None
        self._rx_conn = None
        self._tx_conn = None
        self._port_handler = None
        if self._rx_port:
            self._port_handler = self._rx_port.port_get_PH()

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
            logger.error("DIGI INIT Error !")
            self._state_0_error()
            """
            print(f"_ax25_conf: {self._ax25_conf}")
            print(f"_digi_call: {self._digi_call}")
            print(f"_rx_port: {self._rx_port}")
            print(f"_port_handler: {self._port_handler}")
            """

    def _init_digi_conn(self, ax25_frame):
        # print("!!!! _init_digi_conn !!!!")
        logger.debug("!!!! _init_digi_conn !!!!")
        logger.debug(ax25_frame.get_frame_conf())
        """
        try:
            self._rx_conn = AX25Conn(ax25_frame, port=self._rx_port)
        except AX25ConnectionERROR:
            print("!!!! _init_digi_conn ERROR!!!!")
            logger.debug("!!!! _init_digi_conn ERROR!!!!")
            self._state_0_error()
            return
        """
        self._rx_conn = AX25Conn(ax25_frame, port=self._rx_port)
        self._rx_conn.cli.change_cli_state(5)
        self._rx_conn.is_link_remote = False
        self._rx_conn.cli_remote = False
        self._rx_conn.is_digi = True
        self._rx_conn.my_call_str = str(self._digi_call)
        self._rx_conn.digi_call = str(self._digi_call)
        self._rx_conn_uid = str(self._rx_conn.uid)
        self._rx_conn.set_station_cfg()
        """
        try:
            self._rx_conn.set_station_cfg()
        except AX25ConnectionERROR:
            self._state_0_error()
            return
        """
        if self._rx_conn_uid in self._rx_port.connections.keys():
            logger.warning("ERROR DIGI - Connection -  self._rx_conn_uid in self._rx_port.connections ")
            self._state_0_error()
            return
        if self._conf_short_via:
            ax25_frame.short_via_calls(self._digi_call)
        if self._conf_digi_auto_port:
            tx_port_id = -1
        else:
            tx_port_id = int(self._rx_port.port_id)

        if self._conf_digi_ssid_port:
            tx_port_id = int(self._digi_ssid)

        # print(f"DIGI INIT: axConf: {ax25_frame_conf}")
        tx_conn = self._port_handler.new_outgoing_connection(
            dest_call=self._ax25_conf.get('to_call_str', ''),
            own_call=self._ax25_conf.get('from_call_str', ''),
            via_calls=self._ax25_conf.get('via_calls_str', []),  # Auto lookup in MH if not exclusive Mode
            port_id=tx_port_id,                                  # -1 Auto lookup in MH list
            exclusive=True,                                      # True = no lookup in MH list
            is_service=True
        )
        if not tx_conn[0]:
            logger.error(f"Digi-Error _init_digi_conn: {tx_conn[1]}")
            self._state_0_error()
            return
        self._tx_conn = tx_conn[0]
        if not self._tx_conn.new_digi_connection(self._rx_conn):
            logger.error("Digi-Error: not self._tx_conn.new_digi_connection(self._rx_conn)")
            self._state_0_error()
            return
        self._tx_conn.is_link_remote = True
        self._tx_conn.cli_remote = False
        self._tx_conn.is_digi = True
        self._tx_conn.my_call_str = str(self._digi_call)
        # self._tx_conn.digi_call = self._digi_call
        self._tx_conn.set_station_cfg()
        """
        try:
            self._tx_conn.set_station_cfg()
        except AX25ConnectionERROR:
            self._state_0_error()
            return
        """

        self._tx_conn_uid = self._tx_conn.uid
        self._tx_port = self._tx_conn.own_port

        logger.debug(f"LinkConn : {self._port_handler.link_connections.items()}")
        logger.debug(f"LinkConn : txConns: {self._tx_port.connections}")
        logger.debug(f"LinkConn : txConn UID: {self._tx_conn.uid}")
        logger.debug(f"LinkConn : rxConns: {self._rx_port.connections}")
        logger.debug(f"LinkConn : rxConn UID: {self._rx_conn.uid}")
        self._state = 2

    def add_rx_conn_cron(self):
        if not self._rx_conn:
            self._state_0_error()
            return
        if self._link_connections():
            if self._rx_conn_uid in self._tx_port.connections:
                logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                logger.debug(f"_tx_port.connections: {self._tx_port.connections}")
                logger.debug(f"RX-UID: {self._rx_conn.uid}")
                logger.debug(f"RX-UID: {self._rx_conn_uid}")
                logger.debug(f"TX-UID: {self._tx_conn.uid}")
                logger.debug(f"TX-UID: {self._tx_conn_uid}")
                logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                # self._tx_port.connections[str(self._tx_conn_uid)] = self._tx_conn
                self._state_0_error()
                return
            self._rx_port.connections[str(self._rx_conn_uid)] = self._rx_conn
            self._port_handler.insert_new_connection_PH(self._rx_conn, is_service=True)
            self._state = 3

            logger.debug(f"LinkConn Accept: {self._port_handler.link_connections.items()}")
            logger.debug(f"RX-State: {self._rx_conn.get_state()}")
            logger.debug(f"TX-State: {self._tx_conn.get_state()}")

            return
        self._state_0_error()

    def _link_connections(self):
        if not self._rx_conn or not self._tx_conn:
            self._state_0_error()
            logger.error('Digi-Conn_link Error: No tx or rx conn')
            return

        if self._rx_conn.new_digi_connection(self._tx_conn):
            logger.debug('Digi-Accept')
            return True
        return False

    def _state_0_error(self, ax25_frame=None):
        logger.error(f"Digi-Error: STATE: {self._state}")
        self._state = 0
        self._disco_tx_conn()
        self._disco_rx_conn()

    def _state_1_rx(self, ax25_frame):
        if ax25_frame.ctl_byte.flag == 'SABM':
            if not self._tx_conn_uid:
                self._init_digi_conn(ax25_frame)
            else:
                logger.error('Digi-SABM-RX ERROR')
                self._state_0_error()
                # self.crone() # # SABM TX
        elif ax25_frame.ctl_byte.flag == 'DISC':
            # self._abort_digi_conn(ax25_frame)
            logger.debug('DIGI S! DISC RX')
            if self.is_done():
                # self._rx_port.add_frame_to_digiBuff(ax25_frame)
                self._digi_fallback(ax25_frame)
            else:
                # print('DIGI ABORT')
                self._abort_digi_conn(ax25_frame)
        else:
            # MAYBE Fallback to simple Digi Mode ?
            logger.warning(f'DIGI Not Known Frame: {ax25_frame.ctl_byte.flag}')
            self._digi_fallback(ax25_frame)
            self._state_0_error()

    def _state_2(self, ax25_frame=None):
        if ax25_frame.ctl_byte.flag == 'SABM':
            # print('DIGI INIT SABM RX')
            self._last_rx = time.time()
            if self._check_txConn_state():
                """ IF AXIP is Faster than other Port """
                # TODO Bad solution
                # self._rx_conn.LINK_Connection = self._tx_conn
                # self.add_rx_conn_cron()
                self._tx_conn.accept_digi_connection()
                self._rx_conn.zustand_exec.change_state(5)
                self._state = 3

        elif ax25_frame.ctl_byte.flag == 'DISC':
            self._abort_digi_conn(ax25_frame)
            logger.debug('DIGI INIT DISC RX ')

    def _state_3(self, ax25_frame=None):
        if ax25_frame:
            if self._rx_conn:
                self._rx_conn.handle_rx(ax25_frame=ax25_frame)
        if self.is_done():
            self._port_handler.delete_digi_conn(self._rx_conn_uid)

    def is_done(self):
        if all((not self._rx_conn, not self._tx_conn)):
            return True
        if self._rx_conn:
            if self._rx_conn.get_state():
                return False
        if self._tx_conn:
            if self._tx_conn.get_state():
                return False
        return True

    def _is_running(self):
        if any((not self._rx_conn, not self._tx_conn)):
            return False
        if self._rx_conn:
            if self._rx_conn.get_state() < 5:
                return False
        if self._tx_conn:
            if self._tx_conn.get_state() < 5:
                return False
        return True

    def _disco_tx_conn(self):
        if self._tx_conn:
            if self._tx_conn.get_state():
                if self._tx_conn.is_buffer_empty():
                    self._tx_conn.conn_disco()

    def _disco_rx_conn(self):
        if self._rx_conn:
            if self._rx_conn.get_state():
                if self._rx_conn.is_buffer_empty():
                    self._rx_conn.conn_disco()

    def _UI_digi(self, ax25_frame):
        if self._conf_UI_short_via:
            ax25_frame.short_via_calls(self._digi_call)
        if self._conf_digi_auto_port:
            tx_port_id = -1
        else:
            tx_port_id = self._rx_port.port_id

        if self._conf_digi_ssid_port:
            tx_port_id = self._digi_ssid

        port = self._port_handler.get_port_by_id(tx_port_id)
        if not port:
            logger.warning(f"UI-DIGI ERROR: No Port: {tx_port_id} - DIGI: {self._digi_call} - SSID: {self._digi_ssid}")
            print(f"UI-DIGI ERROR: No Port: {tx_port_id} - DIGI: {self._digi_call} - SSID: {self._digi_ssid}")
            return
        port.add_frame_to_digiBuff(ax25_frame)

    def _digi_fallback(self, ax25_frame):
        print('DIGI Fallback')
        logger.debug('DIGI Fallback')
        # self._rx_port.add_frame_to_digiBuff(ax25_frame)
        self._UI_digi(ax25_frame)

    def digi_rx_handle(self, ax25_frame):
        if ax25_frame.ctl_byte.flag == 'UI':
            self._UI_digi(ax25_frame)
            return
        state_exec = self._state_tab.get(self._state, None)
        if not callable(state_exec):
            self._state_0_error()
            logger.error(f"DIGI-RX ERROR: not callable(state_exec) - STATE: {self._state}")
            print(f"DIGI-RX ERROR: not callable(state_exec) - STATE: {self._state}")
            return
        state_exec(ax25_frame=ax25_frame)

    def _abort_digi_conn(self, ax25_frame=None):
        logger.debug(f"DIGI ABORT: {self._rx_conn_uid}")
        if ax25_frame and self._rx_conn:
            self._rx_conn.handle_rx(ax25_frame=ax25_frame)
        self._disco_tx_conn()
        del self._rx_conn
        self._rx_conn = None
        self._state = 3

    ################################################
    # Crone Tasks
    def digi_crone(self):
        """ !! called fm Port Tasker LOOP !! """
        if self._state == 2:
            self._check_last_SABM()
            return
        if self._state == 3:
            if self._is_running():
                self._check_RNR()
                self._check_RNR_reset()

    def _check_last_SABM(self):
        if self._state != 2:
            return False
        if time.time() - self._last_rx > self._conf_last_rx_fail:
            logger.debug(f'DIGI _check_last_SABM: ABORT')
            self._abort_digi_conn()

    def _check_RNR_reset(self):
        if not self._check_buffer_limit_RxConn():
            self._unset_TxConn_RNR()
        if not self._check_buffer_limit_TxConn():
            self._unset_RxConn_RNR()

    def _check_RNR(self):
        if self._check_buffer_limit_RxConn():
            self._set_TxConn_RNR()
        if self._check_buffer_limit_TxConn():
            self._set_RxConn_RNR()

    def _set_TxConn_RNR(self):
        if not self._tx_conn:
            logger.error("Digi-Error: _set_TxConn_RNR")
            print("Digi-Error: _set_TxConn_RNR")
            self._state_0_error()
            return
        if self._tx_conn.is_RNR:
            return
        self._tx_conn.set_RNR()

    def _unset_TxConn_RNR(self):
        if not self._tx_conn:
            logger.error("Digi-Error: _unset_TxConn_RNR")
            print("Digi-Error: _unset_TxConn_RNR")
            self._state_0_error()
            return
        if not self._tx_conn.is_RNR:
            return
        self._tx_conn.unset_RNR()

    def _set_RxConn_RNR(self):
        if not self._rx_conn:
            logger.error("Digi-Error: _set_RxConn_RNR")
            print("Digi-Error: _set_RxConn_RNR")
            self._state_0_error()
            return
        if self._rx_conn.is_RNR:
            return
        self._rx_conn.set_RNR()

    def _unset_RxConn_RNR(self):
        if not self._rx_conn:
            logger.error("Digi-Error: _unset_RxConn_RNR")
            print("Digi-Error: _unset_RxConn_RNR")
            self._state_0_error()
            return
        if not self._rx_conn.is_RNR:
            return
        self._rx_conn.unset_RNR()

    def _check_buffer_limit_RxConn(self):
        if all((
            not self._conf_max_buff,
            not self._conf_max_n2
        )):
            return False
        if self._conf_max_n2:
            if self._rx_conn.n2 > self._conf_max_n2:
                return True
        if not self._conf_max_buff:
            return False
        if len(self._rx_conn.tx_buf_rawData) > self._conf_max_buff:
            return True
        return False

    def _check_buffer_limit_TxConn(self):
        if all((
            not self._conf_max_buff,
            not self._conf_max_n2
        )):
            return False
        if self._conf_max_n2:
            if self._tx_conn.n2 > self._conf_max_n2:
                return True
        if not self._conf_max_buff:
            return False
        if len(self._tx_conn.tx_buf_rawData) > self._conf_max_buff:
            return True
        return False

    def get_state(self):
        return self._state

    def _check_txConn_state(self):
        if not self._tx_conn:
            logger.debug('DIGI._check_txConn_state : no txConn')
            self._state_0_error()
        txConn_state = self._tx_conn.get_state()
        if txConn_state != 2:
            if txConn_state < 5:
                logger.debug('DIGI._check_txConn_state : txConn STATE ERROR')
                self._state_0_error()
                return False
            return True
        return False

