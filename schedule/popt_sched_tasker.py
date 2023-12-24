import time

from cfg.popt_config import POPT_CFG
from schedule.tasks.AutoConnTask import AutoConnTask
from schedule.popt_sched import PoPTSchedule
from schedule.tasks.BeaconTask import BeaconTask


class PoPTSchedule_Tasker:
    def __init__(self, port_handler):
        self._port_handler = port_handler
        self._scheduled_tasks = {
            'PMS': self.start_AutoConnTask,
            'BEACON': self.start_BeaconTask,
        }
        self._scheduled_tasks_q = []
        self.auto_connections = {}      # [AutoConnTask()]
        self._task_timer_1sec = time.time() + 1
        self._init_beacon_tasks()

    def tasker(self):
        """ 0.5 Sek called fm Porthandler Loop """
        self._05_sec_tasker()
        self._1_sec_tasker()

    def _05_sec_tasker(self):
        self._AutoConn_tasker()     # TODO move to Porthandler Loop

    def _1_sec_tasker(self):
        if time.time() > self._task_timer_1sec:
            self._scheduler_task()
            self._task_timer_1sec = time.time() + 1

    #################################
    # scheduled Tasks
    #
    def _scheduler_task(self):
        for task in self._scheduled_tasks_q:
            task_fnc = self._scheduled_tasks.get(task[1].get('task_typ', ''), None)
            if callable(task_fnc):
                task_fnc(task[1], task[0])

    ####################################
    # Auto Connection Tasker
    def start_AutoConnTask(self, conf, sched_conf=None):
        if self._is_AutoConn_maxConn(conf):
            return None
        k = conf.get('dest_call', '')
        if not k:
            return None
        if k in self.auto_connections.keys():
            return None
        if sched_conf:
            if not sched_conf.is_schedule():
                return None
        autoConn = AutoConnTask(self._port_handler, conf)
        if autoConn.state_id and not autoConn.e:
            self.auto_connections[k] = autoConn
            return autoConn
        del autoConn
        return None

    def _AutoConn_tasker(self):
        for k in list(self.auto_connections.keys()):
            # print(f"AutoConn state_id: {self.auto_connections[k].state_id}")
            if self.auto_connections[k].state_id:
                self.auto_connections[k].crone()
            else:
                del self.auto_connections[k]

    def _is_AutoConn_maxConn(self, autoconn_cfg):
        max_conn = autoconn_cfg.get('max_conn', 0)
        if not max_conn:
            return False
        conn_k = autoconn_cfg.get('dest_call', '')
        n_conn = list(self.auto_connections.keys()).count(conn_k)
        if n_conn >= max_conn:
            return True
        return False

    ####################################
    # Beacon Tasker
    def reinit_beacon_tasks(self):
        self.del_scheduler_Task_by_Typ('BEACON')
        self._init_beacon_tasks()
                
    def _init_beacon_tasks(self):
        beacons_cfg = POPT_CFG.get_Beacon_tasks()
        for beacon in beacons_cfg:
            sched_cfg = beacon.get('scheduler_cfg', None)
            if sched_cfg:
                self.insert_scheduler_Task(sched_cfg, beacon)

    def start_BeaconTask(self, conf, sched_conf=None):
        is_glb_beacon = POPT_CFG.get_guiPARM_main('gui_cfg_beacon')
        if not is_glb_beacon:
            return None
        if not conf.get('is_enabled', False):
            return None
        if conf.get('own_call', 'NOCALL') == 'NOCALL':
            return None
        if not conf.get('dest_call', ''):
            return None
        if sched_conf:
            if not sched_conf.is_schedule():
                return None
        beacon = BeaconTask(self._port_handler, conf)
        beacon.send_it()

    ####################################
    # Scheduler Q
    def insert_scheduler_Task(self, sched_cfg, conf: dict):
        """
        :param conf: {}  # PMS
            'task_typ': 'PMS',
            'max_conn': 0,
            'port_id': 0,
            'own_call': 'MDBLA1',
            'dest_call': 'MDBLA2',
            'via_calls': ['MDBLA5', 'MDBLA8'],
            'axip_add': ('', 0),

            conf = {}   # BEACON
            'task_typ': 'BEACON',
            'max_conn': 0,
            'port_id': 0,
            'own_call': 'MDBLA1',
            'dest_call': 'MDBLA2',
            'via_calls': ['MDBLA5', 'MDBLA8'],
            'text': b'TEST',
            'cmd_poll': (False, False),
            'pid': 0xF0

        """
        poptSched = PoPTSchedule(sched_cfg)
        self._scheduled_tasks_q.append(
            (poptSched, conf)
        )

    def del_scheduler_Task(self, conf):
        """
        :param conf: {}
            'task_typ': 'PMS',
            'max_conn': 0,
            'port_id': 0,
            'own_call': 'MDBLA1',
            'dest_call': 'MDBLA2',
            'via_calls': ['MDBLA5', 'MDBLA8'],
            'axip_add': ('', 0),

        """

        for task in list(self._scheduled_tasks_q):
            if task[1] == conf:
                self._scheduled_tasks_q.remove(task)
                return
    
    def del_scheduler_Task_by_Typ(self, typ: str):
        if not typ:
            return
        for task in list(self._scheduled_tasks_q):
            if task[1]['task_typ'] == typ:
                self._scheduled_tasks_q.remove(task)

    def start_scheduler_Task_manual(self, conf):
        """
        :param conf: {}
            'task_typ': 'PMS',
            'max_conn': 0,
            'port_id': 0,
            'own_call': 'MDBLA1',
            'dest_call': 'MDBLA2',
            'via_calls': ['MDBLA5', 'MDBLA8'],
            'axip_add': ('', 0),

        """

        for task in list(self._scheduled_tasks_q):
            if task[1] == conf:
                task[0].manual_trigger()
                self.start_AutoConnTask(task[1])
