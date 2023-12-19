import time

from schedule.tasks.AutoConnTask import AutoConnTask
from schedule.popt_sched import PoPTSchedule


class PoPTSchedule_Tasker:
    def __init__(self, port_handler):
        self._port_handler = port_handler
        self._scheduled_tasks_q = []
        self._scheduled_tasks = {
            'PMS': self.start_AutoConnTask,
            'BEACON': self.start_BeaconTask,
        }
        self.auto_connections = {}      # [AutoConnTask()]
        self._task_timer_1sec = time.time() + 1

    def tasker(self):
        """ 0.5 Sek called fm Porthandler Loop """
        self._05_sec_tasker()
        self._1_sec_tasker()

    def _05_sec_tasker(self):
        self._AutoConn_tasker()

    def _1_sec_tasker(self):
        if time.time() > self._task_timer_1sec:
            self._scheduler_task()
            self._task_timer_1sec = time.time() + 1

    #################################
    # scheduled Tasks
    #
    def _scheduler_task(self):
        for task in self._scheduled_tasks_q:
            if task[0].is_schedule():
                if not self._is_AutoConn_maxConn(task[1]):
                    task_fnc = self._scheduled_tasks.get(task[1].get('task_typ', ''), None)
                    if callable(task_fnc):
                        task_fnc(task[1])

    ####################################
    # Auto Connection Tasker
    def start_AutoConnTask(self, conf):
        k = conf.get('dest_call', '')
        if not k:
            return None
        if k in self.auto_connections.keys():
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
                print(f"AutoConn remove: {self.auto_connections[k]}")
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
    def start_BeaconTask(self):
        pass

    ####################################
    def insert_scheduler_Task(self, sched_cfg, conf):
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
        poptSched = PoPTSchedule(sched_cfg)
        self._scheduled_tasks_q.append(
            (poptSched, conf)
        )
        print('New Task')

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
                print('Del Task')
                return

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
