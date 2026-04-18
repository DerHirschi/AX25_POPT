import threading
import time
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.one_wire_fnc import is_1wire_device, get_1wire_temperature


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
        """ Thread Garbage Collector """
        self._thread_gc: list  = popt_handler.thread_gc
        """"""
        self._is_running   = popt_handler.is_running
        """"""
        self._tasker_th    = threading.Thread(target=self._tasker)
        self._update_1wire_th: threading.Thread or None  = None  # 1Wire Thread
        """"""
        #
        self._1wire_timer      = time.time() + 10  # + 10 Sec, give some time to Init the rest
        self._task_timer_05sec = time.time() + 0.5
        self._task_timer_1sec  = time.time() + 1
        self._task_timer_2sec  = time.time() + 2
        self._task_timer_5sec  = time.time() + 5
        if not gui_app:
            self._init_PH_tasker()



    def _init_PH_tasker(self):
        threading.Thread(target=self._tasker).start()

    def _tasker(self):
        while self._is_running:
            self.tasker_gui_th()
            if not self._is_running:
                return
            time.sleep(0.25)

    def tasker_gui_th(self):
        if not self._is_running:
            return False
        # TODO Tasker-Q
        # ret = any((self._5sec_task(),  ret))
        task_pr = self._prio_task()
        task_05 = self._05sec_task()
        task_10 = self._1sec_task()
        task_20 = self._2sec_task()

        return task_pr or task_05 or task_10 or task_20

    def _prio_task(self):
        """ 0.1 Sec (Mainloop Speed) """
        task_01 = self._bbs().tasker()          # bbs.tasker-q
        task_02 = self._gpio_tasker_q()         # gpio.tasker-q
        task_03 = self._sound().sound_tasker()  # tasker-q

        return task_01 or task_02 or task_03

    def _05sec_task(self):
        """ 0.5 Sec """
        if time.time() > self._task_timer_05sec:
            self._Sched_task()
            self._aprs_task()
            self._gpio_task()
            self._popt_handler.pipe_manager.pipeTool_task()
            self._task_timer_05sec = time.time() + 0.5
            return True
        return False

    def _1sec_task(self):
        """ 1 Sec """
        if time.time() > self._task_timer_1sec:
            self._port_watchdog_task()
            self._mh_task()         # #################
            self._tasker_1wire()
            self._popt_handler.update_remote_monitor_task()
            self._task_timer_1sec = time.time() + 1
            return True
        return False

    def _2sec_task(self):
        """ 2 Sec """
        if time.time() > self._task_timer_2sec:
            self._bbs().main_cron()
            self._task_timer_2sec = time.time() + 2
            return True
        return False

    def _5sec_task(self):
        """ 5 Sec """
        if time.time() > self._task_timer_5sec:
            # self._update_remote_monitor_batch_task()
            self._task_timer_5sec = time.time() + 5
            return True
        return False

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
        if self._update_1wire_th is None:
            self._oneWire_thread_run()
            return
        if self._update_1wire_th.is_alive():
            return
        self._oneWire_thread_run()
        return

    def _oneWire_thread_run(self):
        self._1wire_timer = time.time() + POPT_CFG.get_1wire_loop_timer()
        self._update_1wire_th = threading.Thread(target=self._oneWire_task)
        self._thread_gc.append(self._update_1wire_th)
        self._update_1wire_th.start()

    @staticmethod
    def _oneWire_task():
        if not is_1wire_device():
            return
        sensor_cfg = POPT_CFG.get_1wire_sensor_cfg()
        if not sensor_cfg:
            return
        for textVar, sens_cfg in sensor_cfg.items():
            sens_cfg: dict
            sens_id = sens_cfg.get('device_path', '')
            if not sens_id:
                continue
            try:
                sens_cfg['device_value'] = str(get_1wire_temperature(sens_id)[0])
            except IndexError:
                logger.warning(f"PH: _oneWire_task IndexError: {textVar}")
                logger.warning(f"PH: _oneWire_task IndexError: {sens_cfg}")
                continue
        # POPT_CFG.set_1wire_sensor_cfg(dict(sensor_cfg))
