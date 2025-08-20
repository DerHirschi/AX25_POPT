import threading
import traceback

from cfg.constant import SERVICE_CH_START, TASK_TYP_FWD
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
            dest_call=  self._conf.get('dest_call'),
            own_call=   self._conf.get('own_call'),
            via_calls=  self._conf.get('via_calls'),          # Auto lookup in MH if not exclusive Mode
            port_id=    self._conf.get('port_id', -1),        # -1 Auto lookup in MH list
            axip_add=   self._conf.get('axip_add', ('', 0)),  # AXIP Adress
            exclusive=  True,                                 # True = no lookup in MH list
            link_conn=  None,                                 # Linked Connection AX25Conn
            channel=    SERVICE_CH_START,                     # GUI Channel
        )
        # print(self.connection)
        self._connection        = None
        self.e                  = False
        self._state_exec        = None
        self.state_id           = 1
        self._state_tab = {
            TASK_TYP_FWD: {
                0: self._end_connection,
                1: self._PMS_fwd_init,
                4: self._PMS_wait_rev_fwd_ended,
            }
        }.get(self._conf.get('task_typ', ''), {})
        if not self._state_tab:
            self.e = True
            logger.error(f"Error ConnTask no state_tab Typ: {self._conf}")
            self._set_state_exec(0)
        if not connection[0]:
            self.e = True
            logger.error(f"Error ConnTask connection: {connection[1]}")
            self._set_state_exec(0)
        else:
            self._connection = connection[0]
            logger.debug("ConnTask connection: Start")
            self._set_state_exec(1)
            self._exec_state_tab()

    def crone(self):
        try:
            if self.e:
                self._ConnTask_ende()
            if not self._is_connected():
                self._ConnTask_ende()
                return False
            self._exec_state_tab()
            return True
        except Exception as ex:
            logger.error(
                f"Fehler in AutoConnTask crone: {ex}, Thread: {threading.current_thread().name}")
            traceback.print_exc()
            raise ex

    def _set_state_exec(self, state_id):
        if self._state_tab:
            logger.debug(f"AutoConn State change: {self.state_id} > {state_id}")
            self.state_id    = state_id
            self._state_exec = self._state_tab[self.state_id]

    def _exec_state_tab(self):
        if self._state_exec:
            self._state_exec()

    def _is_connected(self):
        if self.e:
            return False
        if not self._connection:
            self.e = True
            return False
        state_index = self._connection.get_state()
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

    def _end_connection(self):
        # 0
        if not self._connection:
            return
        if not self._connection.is_buffer_empty():
            return
        self._connection.conn_disco()

    ###############################################
    # PMS
    def _PMS_fwd_init(self):
        # 1
        self._connection.cli      = NoneCLI(self._connection)
        self._connection.cli_type = f"Task: {self._conf.get('task_typ', '-')}"
        if self._connection.bbsFwd_init():
            self._set_state_exec(4)
        else:
            logger.error("_PMS_fwd_init > bbsFwd_init")
            self._set_state_exec(0)

    def _PMS_wait_rev_fwd_ended(self):
        # 4
        if not hasattr(self._connection, 'bbs_connection') or\
            not hasattr(self._connection, 'tx_buf_rawData'):
            self._ConnTask_ende()
            return
        if self._connection.bbs_connection:
            return
        if self._connection.tx_buf_rawData:
            return
        if self._connection:
            self._end_connection()
        else:
            self._ConnTask_ende()

    ##########################################
    #
