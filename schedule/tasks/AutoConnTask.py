from cfg.constant import SERVICE_CH_START
from cfg.logger_config import logger
from cli import NoneCLI


class AutoConnTask:
    def __init__(self, port_handler, conf: dict):
        """
        self._conf = {
            'task_typ': 'PMS',
            'port_id': 0,
            'own_call': 'MD2SAW',
            'dest_call': 'DBO527',
            'via_calls': ['DNX527-1'],
            # 'axip_add': ('192.168.178.160', 8093),
            'silent_conn': True,
        }
        """
        self._conf = conf
        connection = port_handler.new_outgoing_connection(
            dest_call=self._conf.get('dest_call'),
            own_call=self._conf.get('own_call'),
            via_calls=self._conf.get('via_calls'),          # Auto lookup in MH if not exclusive Mode
            port_id=self._conf.get('port_id', -1),          # -1 Auto lookup in MH list
            axip_add=self._conf.get('axip_add', ('', 0)),   # AXIP Adress
            exclusive=True,                                 # True = no lookup in MH list
            link_conn=None,                                 # Linked Connection AX25Conn
            channel=SERVICE_CH_START,                       # GUI Channel
        )
        # print(self.connection)
        self.connection = None
        self.conn_state = None
        self.dest_station_id = None
        self.e = None
        self._state_exec = None
        self.state_id = 1
        self._state_tab = {
            'PMS': {
                0: self._end_connection,
                1: self._PMS_send_fwd_cmd,
                2: self._PMS_is_last_chars_in_rxbuff,
                3: self._PMS_start_rev_fwd,
                4: self._PMS_wait_rev_fwd_ended,
            }
        }.get(self._conf.get('task_typ', ''), {})
        if not self._state_tab:
            self.e = True
            # print(f"Error ConnTask no state_tab Typ: {self._conf}")
            logger.error(f"Error ConnTask no state_tab Typ: {self._conf}")
            self._set_state_exec(0)
        if not connection[0]:
            self.e = True
            # print(f"Error ConnTask connection: {connection[1]}")
            logger.error(f"Error ConnTask connection: {connection[1]}")
            self._set_state_exec(0)
        else:
            self.connection = connection[0]
            self.connection.cli = NoneCLI(self.connection)
            self.connection.cli_type = f"Task: {self._conf.get('task_typ', '-')}"
            # self.dest_station_id = self.connection.cli.stat_identifier
            self._set_state_exec(1)

    def crone(self):
        if self.e:
            self._ConnTask_ende()
            return False
        if not self._is_connected():
            self._ConnTask_ende()
            return False
        self._exec_state_tab()
        return True

    def _set_state_exec(self, state_id):
        if self._state_tab:
            self.state_id = state_id
            self._state_exec = self._state_tab[self.state_id]

    def _exec_state_tab(self):
        if self._state_exec:
            self._state_exec()

    def _is_connected(self):
        if self.e:
            return False
        if not self.connection:
            self.e = True
            return False
        state_index = self.connection.get_state()
        if not state_index:
            self.e = True
            return False
        if state_index in [1, 3, 4]:
            return False
        return True

    def _ConnTask_ende(self):
        # print(f"ConnTask {self._conf.get('task_typ', '')} END")
        if self.state_id:
            self._set_state_exec(0)
        # if self.connection:
        #     self._end_connection()

    def _end_connection(self):
        # 0
        if self.connection:
            self.connection.conn_disco()
            self.connection = None
        self._set_state_exec(0)
        self._ConnTask_ende()

    ###############################################
    # PMS
    def _PMS_send_fwd_cmd(self):
        # 1
        if self.connection.cli.stat_identifier:
            if self.connection.cli.stat_identifier.typ != 'BBS':
                self._set_state_exec(0)
                return
            rev_cmd = self.connection.cli.stat_identifier.bbs_rev_fwd_cmd
            if rev_cmd:
                self.connection.send_data(rev_cmd)
            self._set_state_exec(2)
            return

        self._set_state_exec(0)

    def _PMS_is_last_chars_in_rxbuff(self):
        # 2
        if self.connection.rx_buf_last_data.endswith(b'>\r'):
            self._set_state_exec(3)

    def _PMS_start_rev_fwd(self):
        # 3
        """
        if self.connection.bbs_connection:
            self._set_state_exec(4)
            return
        """
        # TODO if connection.rx:
        if self.connection.bbsFwd_start_reverse():
            self._set_state_exec(4)
        else:
            self._set_state_exec(0)

    def _PMS_wait_rev_fwd_ended(self):
        # 4
        if not self.connection.bbs_connection:
            # self._set_state_exec(0)
            if self.connection:
                # self._set_state_exec(0)
                self._end_connection()
            else:
                self._ConnTask_ende()

    ##########################################
    #
