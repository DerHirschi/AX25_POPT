import threading
import time

from cfg.constant import GUI_TASKER_TIME_D_UNTIL_BURN
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.one_wire_fnc import oneWire_task, is_1wire_device


class PoPTCoreTasker:
    def __init__(self, popt_handler, gui_app=True):
        logger.info("Core-Tasker: Init")
        self._popt_handler     = popt_handler
        self._gpio             = lambda : popt_handler.get_GPIO()
        self._mh               = lambda : popt_handler.get_MH()
        self._bbs              = lambda : popt_handler.get_bbs()
        self._aprs_ais         = lambda : popt_handler.get_aprs_ais()
        self._sound            = lambda : popt_handler.get_sound_modul()
        self._scheduled_tasker = lambda : popt_handler.get_scheduled_tasker()
        self._thread_manager   = lambda : popt_handler.get_thread_manager()
        """"""
        self._is_running   = popt_handler.is_running
        """"""
        self._tasker_th:       threading.Thread or None = None  # Non GUI Main Thread
        """"""
        self._1wire_timer       = time.time() + 10  # + 10 Sec, give some time to Init the rest
        self._task_timer_05sec  = time.time() + 0.5
        self._task_timer_1sec   = time.time() + 1
        self._task_timer_2sec   = time.time() + 2
        self._task_timer_30sec  = time.time() + 30
        """"""
        if not gui_app:
            self._init_PH_tasker()
        """"""
        self._tasker_q = []

    # ===================================
    # No GUI Loop/Thread
    def _init_PH_tasker(self):
        self._tasker_th    = threading.Thread(target=self._tasker)
        self._tasker_th.start()

    def _tasker(self):
        while self._is_running:
            self.popt_core_task()
            if not self._is_running:
                return
            time.sleep(0.25)

    # ===================================
    # Main Tasker
    def popt_core_task(self):
        if not self._is_running:
            self._tasker_q = []
            return
        if len(self._tasker_q) > 15:
            logger.warning("Core-Tasker: self._tasker_q > 15 !!")
        start_timer = time.time()
        self._prio_task()
        self._05sec_task()
        self._1sec_task()
        self._2sec_task()
        self._30sec_task()
        t_delta = time.time() - start_timer
        n   = 0
        fnc = None
        while self._tasker_q and t_delta < GUI_TASKER_TIME_D_UNTIL_BURN:
            fnc = self._tasker_q.pop()
            if callable(fnc):
                fnc()
            n += 1
            t_delta = time.time() - start_timer

        if t_delta > GUI_TASKER_TIME_D_UNTIL_BURN:
            logger.warning(f"Core-Tasker: Overload: Loop needs {round(t_delta, 2)}s to process !!")
            if hasattr(fnc, '__name__'):
                logger.warning(f"   -Last Task: {fnc.__name__}")
            logger.warning(f"   -{n} Tasks done.")
            logger.warning(f"   -{len(self._tasker_q)} Tasks still in Q.")

    # ===================================
    def _prio_task(self):
        """ 0.1 Sec (Mainloop Speed) """
        self._add_task_to_q(self._bbs().tasker)           # bbs.tasker-q
        self._add_task_to_q(self._gpio_tasker_q)          # tasker-q
        self._add_task_to_q(self._sound().sound_tasker)   # tasker-q (Threads)


    def _05sec_task(self):
        """ 0.5 Sec """
        if time.time() > self._task_timer_05sec:
            """"""
            self._add_task_to_q(self._Sched_task)
            self._add_task_to_q(self._aprs_task)
            self._add_task_to_q(self._popt_handler.pipe_manager.pipeTool_task)
            self._add_task_to_q(self._gpio_task)
            """"""
            self._task_timer_05sec = time.time() + 0.5
            return True
        return False

    def _1sec_task(self):
        """ 1 Sec """
        if time.time() > self._task_timer_1sec:
            """"""
            self._add_task_to_q(self._port_watchdog_task)
            self._add_task_to_q(self._mh_task)
            self._add_task_to_q(self._tasker_1wire)
            self._add_task_to_q(self._popt_handler.update_remote_monitor_task)
            """"""
            self._task_timer_1sec = time.time() + 1
            return True
        return False

    def _2sec_task(self):
        """ 2 Sec """
        if time.time() > self._task_timer_2sec:
            """"""
            self._add_task_to_q(self._bbs().main_cron)
            """"""
            self._task_timer_2sec = time.time() + 2
            return True
        return False

    def _30sec_task(self):
        """ 30 Sec """
        if time.time() > self._task_timer_30sec:
            # self._update_remote_monitor_batch_task()
            """"""
            self._add_task_to_q(self._thread_manager().thread_GC_cleanup_task)
            """"""
            self._task_timer_30sec = time.time() + 30
            return True
        return False

    # ===================================
    # Tasker Q
    def _add_task_to_q(self, fnc):
        if fnc in self._tasker_q:
            if hasattr(fnc, '__name__'):
                logger.warning(f"Core-Tasker: Task '{fnc.__name__}' already in Q")
                return
            logger.warning(f"Core-Tasker: Task '{fnc}' already in Q")
            return
        self._tasker_q.append(fnc)

    #######################################################################
    # Port Watchdog
    def _port_watchdog_task(self):
        for port_id, port in dict(self._popt_handler.get_all_ports()).items():
            if hasattr(port, 'get_watchdog_timer'):
                wd_timer = time.time() - port.get_watchdog_timer()
                if wd_timer > 10:
                    if hasattr(port, 'reset_watchdog_timer'):
                        port.reset_watchdog_timer()
                    logger.warning("=================Port-Watch-Dog====================")
                    logger.warning(f"Port : {port_id}")
                    logger.warning(f"timer: {round(wd_timer)} s")
                    #logger.info(f"Try to reinit Port {port_id}")
                    #threading.Thread(target=self.reinit_port, args=(port_id, )).start()

    #######################################################################
    # Scheduled Tasks
    def _Sched_task(self):
        if hasattr(self._scheduled_tasker(), 'tasker'):
            # Scheduler & AutoConn Tasker
            self._scheduled_tasker().tasker()
    #######################################################################
    # APRS
    def _aprs_task(self):
        if hasattr(self._aprs_ais(), 'task'):
            return self._aprs_ais().task()
        return False
    #######################################################################
    # MH
    def _mh_task(self):
        return self._mh().mh_task()

    #######################################################################
    # GPIO
    def _gpio_task(self):
        if hasattr(self._gpio(), 'gpio_tasker'):
            self._gpio().gpio_tasker()
            return
        return

    def _gpio_tasker_q(self):
        if hasattr(self._gpio(), 'gpio_tasker_q'):
            return self._gpio().gpio_tasker_q()
        return False

    ##############################################################
    # 1Wire TextVars
    def _tasker_1wire(self):
        if time.time() < self._1wire_timer:
            return
        if not is_1wire_device():
            self._1wire_timer = time.time() + 600
            return
        sensor_cfg = POPT_CFG.get_1wire_sensor_cfg()
        if not sensor_cfg:
            self._1wire_timer = time.time() + 30
            return
        th_name = "oneWire_task"
        if not self._thread_manager().is_alive_thread(th_name):
            update_1wire_th = threading.Thread(target=oneWire_task, name=th_name)
            self._thread_manager().add_thread(update_1wire_th)
            self._1wire_timer = time.time() + POPT_CFG.get_1wire_loop_timer()

