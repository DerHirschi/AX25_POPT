import threading
import time

from cfg.constant import GUI_TASKER_NOT_BURN_DELAY, GUI_TASKER_Q_RUNTIME, GUI_TASKER_TIME_D_UNTIL_BURN, \
    GUI_TASKER_BURN_DELAY
from cfg.logger_config import logger
from classes.CLbuffers import ListBuffer
from sound.popt_sound import SOUND


class GuiTasker:
    def __init__(self, gui_root_cl):
        self._logTag = 'GUI-Tasker: '
        logger.debug(self._logTag + 'Init')
        # ================================
        self._gui_root     = gui_root_cl
        self._gui_main_win = gui_root_cl.main_win
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        # ================================
        self._Alarm_Frame  = gui_root_cl.Alarm_Frame
        # ================================
        self.quit               = False
        self._init_state        = 0
        # ================================
        # GC
        self._thread_gc = ListBuffer()  # Thread Garbage colletor
        self._win_gc    = ListBuffer()  # ttk.Frame GC
        # ================================
        # GUI PARAM
        # self._parm_rx_beep_cooldown             = 2  # s
        # ================================
        # Tasker
        self._parm_non_prio_task_timer          = 0.25  # s
        self._parm_non_non_prio_task_timer      = 1  # s
        self._parm_non_non_non_prio_task_timer  = 5  # s
        self._non_prio_task_timer               = time.time()
        self._non_non_prio_task_timer           = time.time()
        self._non_non_non_prio_task_timer       = time.time()
        self._tasker_q_timer                    = time.time()
        self._win_gc_task_timer                 = time.time() + 1
        # ================================
        # Tasker Q
        self._get_tasker_q_can_run = lambda start_time, run_time: bool(run_time > time.time() - start_time)
        self._tasker_q      = ListBuffer()
        self._tasker_q_prio = ListBuffer()
        # ================================
        # 0.25 Sec Flip
        self._flip025 = True
        # ================================
        # Main Loop
        #self._gui_main_win.after(GUI_TASKER_NOT_BURN_DELAY, self._tasker)
        # ================================

    # ================================
    def tasker(self):  # MAINLOOP
        timer_overall    = time.time()
        self._win_gc_tasker()
        if self.quit:
            if self._tasker_quit():
                return
            self._tasker_queue(timer_overall)

        else:
            self._tasker_prio()                     # Port-Handler Tasker, ..., ...
            task_0_25     = self._tasker_025_sec()  # 0.25 & 0.5 Sec(flip flop)
            task_1_00     = self._tasker_1_sec()    # 1.00 Sec
            update_needed = task_0_25 or task_1_00
            # Nur wenn vorherige Tasks nicht ausgeführt wurden
            if not update_needed:
                update_needed = self._tasker_5_sec()    # 5.00 Sec

            # Tasker-Q
            tasker_q = self._tasker_queue(timer_overall)

            # Nur wenn vorherige Tasks ausgeführt wurden
            if update_needed or tasker_q:
                self._gui_main_win.update_idletasks()

        t_delta      = time.time() - timer_overall
        if t_delta > GUI_TASKER_TIME_D_UNTIL_BURN:
            logger.warning(self._logTag + "Tasker Overload: !!")
            logger.warning(self._logTag + f"  - Loop needs {round(t_delta, 2)}s to process !!")
            self._gui_main_win.after(GUI_TASKER_BURN_DELAY,     self.tasker)
        else:
            self._gui_main_win.after(GUI_TASKER_NOT_BURN_DELAY, self.tasker)

    def _tasker_quit(self):
        if not self._popt_handler.get_ph_end():
            return False
        #if self._tasker_q:
        #    logger.info('GUI: Still jobs in _tasker_q')
        #    return False
        th_name = []
        for gc_thread in self._thread_gc.buffer_get:
            if hasattr(gc_thread, 'is_alive'):
                if gc_thread.is_alive():
                    th_name.append(gc_thread.name)
        if th_name:
            logger.info(self._logTag + f'Waiting for {len(th_name)} Threads ! Please Wait ...')
            for thname in th_name:
                logger.debug(self._logTag + f"  - Waiting for Thread: {thname}")
            return False
        self._gui_main_win.quit()
        try:
            self._gui_main_win.destroy()
            logger.info(self._logTag + 'Closing GUI: Done')
        except Exception as ex:
            logger.warning(ex)
        return True


    def _tasker_queue(self, start_time: time.time):
        if self._tasker_q_prio.is_empty and self._tasker_q.is_empty:
            return False
        # ===== PRIO
        while (not self._tasker_q_prio.is_empty and
               self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME)):
            task, arg = self._tasker_q_prio.buffer_read
            if callable(task):
                if arg is None:
                    task()
                else:
                    task(arg)

        if self.quit:
            return True

        # ===== Non Prio
        while (not self._tasker_q.is_empty and
               self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME)):
                task, arg = self._tasker_q.buffer_read
                if callable(task):
                    if arg is None:
                        task()
                    else:
                        task(arg)
        return True

    def _tasker_prio(self):
        """ Prio Tasks every Irritation """
        tasker_ret = False
        """ PoPT-Core Tasker """
        if hasattr(self._popt_handler, 'popt_core_task'):
            timer = time.time()
            self._popt_handler.popt_core_task()
            t_delta = time.time() - timer
            if t_delta > GUI_TASKER_TIME_D_UNTIL_BURN:
                logger.warning(f"PH-Tasker Overload: Loop needs {round(t_delta, 2)}s to process !!")

        """ Toplevel Win Tasker """
        task        = self._gui_root.toplevel_manager.tasker_prio()
        tasker_ret  = task or tasker_ret
        task_01     = self._monitor_task()
        tasker_ret  = tasker_ret or task_01
        return tasker_ret

    def _tasker_025_sec(self):
        """ 0.25 Sec """
        if time.time() > self._non_prio_task_timer:
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            #####################
            task_02 = self._gui_root.qso_frame.update_qso_win()
            task_03 = self._SideFrame_tasker()
            task_04 = self._gui_root.AX25StatusBar.update_status_bar()
            """ Toplevel Win Tasker """
            task_05 = self._gui_root.toplevel_manager.tasker_025_sec()
            """ Alarm Icon Frame Tasker """
            task_06 = self._AlarmIcon_tasker()
            ret = (task_02 or
                   task_03 or
                   task_04 or
                   task_05 or
                   task_06
                   )

            #if self._flip025:
            #    task_05_01 = self._AlarmIcon_tasker05()
            #    ret = task_05_01 or ret
            #####################
            self._flip025 = not self._flip025
            return ret
        return False

    def _tasker_1_sec(self):
        """ 1 Sec """
        if time.time() > self._non_non_prio_task_timer:
            #####################
            self.add_tasker_q(self._gui_root.ConnStatusBar.update_stat_info_conn_timer)
            self.add_tasker_q(self._gui_root.update_ft_info)
            self.add_tasker_q(self._check_port_blocking_task)
            self.add_tasker_q(self._gui_root.chBtn_frame.tasker)
            """ Toplevel Win Tasker """
            self.add_tasker_q(self._gui_root.toplevel_manager.tasker_1_sec)
            # APRS - MSG Spooler
            self.add_tasker_q(self._gui_root.toplevel_manager.update_aprs_spooler_task)

            if SOUND.master_sound_on:
                # TODO Sound Task
                # self._gui_root.rx_beep_sound()
                self.add_tasker_q(self._gui_root.rx_beep_sound)
                if SOUND.master_sprech_on:
                    self.add_tasker_q(self._gui_root.check_sprech_ch_buf)
                    # self._gui_root.check_sprech_ch_buf()

            #####################
            self._non_non_prio_task_timer = time.time() + self._parm_non_non_prio_task_timer
            return True
        return False

    def _tasker_5_sec(self):
        """ 5 Sec """
        if time.time() > self._non_non_non_prio_task_timer:
            if self._init_state < 2:
                self._init_state += 1
                if self._init_state == 2:
                    self.add_tasker_q(self._gui_root.reset_diesel_task)

            #####################
            self.add_tasker_q(self._gui_root.BwPlot.update_bw_mon)
            """ Toplevel Win Tasker """
            self.add_tasker_q(self._gui_root.toplevel_manager.tasker_5_sec)
            #####################
            self._non_non_non_prio_task_timer = time.time() + self._parm_non_non_non_prio_task_timer
            return True
        return False

    # END TASKER
    ######################################################################
    def add_tasker_q(self, fnc, arg=None, prio=True):
        if prio:
            if (fnc, None) in self._tasker_q_prio.buffer_get:
                return
            self._tasker_q_prio.buffer_write(
                (fnc, arg)
            )
        else:
            if (fnc, None) in self._tasker_q.buffer_get:
                return
            self._tasker_q.buffer_write(
                (fnc, arg)
            )

    def add_thread_gc(self, thread: threading.Thread):
        self._thread_gc.buffer_write(thread)

    def add_win_gc(self, trash_win):
        self._win_gc.buffer_write(trash_win)

    def _win_gc_tasker(self):
        if time.time() < self._win_gc_task_timer:
            return
        for trash_win in self._win_gc.buffer_get:
            if hasattr(trash_win, 'is_destroyed'):
                if trash_win.is_destroyed:
                    if hasattr(trash_win, 'all_dead'):
                        if trash_win.all_dead():
                            self._win_gc.buffer_remove(trash_win)
                            del trash_win
                            continue
            if hasattr(trash_win, 'tasker'):
                trash_win.tasker()
        self._win_gc_task_timer = time.time() + 1

    ######################################################################
    def _AlarmIcon_tasker(self):
        if not hasattr(self._Alarm_Frame, 'statusbar_tasker'):
            return False
        self._Alarm_Frame.statusbar_tasker()
        return True


    def _SideFrame_tasker(self):
        if self._flip025:
            return (
                self._gui_root.tabbed_sideFrame.tasker() or
                self._gui_root.tabbed_sideFrame.on_ch_stat_change()
            )

        return (
            self._gui_root.tabbed_sideFrame2.tasker() or
            self._gui_root.tabbed_sideFrame2.on_ch_stat_change()
        )

    def _check_port_blocking_task(self):
        if hasattr(self._popt_handler, 'port_manager'):
            if hasattr(self._popt_handler.port_manager, 'get_glb_port_blocking'):
                if not self._popt_handler.port_manager.get_glb_port_blocking():
                    self._Alarm_Frame.set_PortBlocking(set_on=False)
                else:
                    self._Alarm_Frame.set_PortBlocking(set_on=True)

    ######################################################################
    def _monitor_task(self):
        mon_buff = self._popt_handler.get_monitor_data()
        if not mon_buff:
            return False
        new_mon_buff = []
        for axframe_conf in mon_buff:
            port_id = axframe_conf.get('port', -1)

            self._gui_root.mon_tree_frame.mon_pack_buff.append(dict(axframe_conf))
            if port_id not in self._gui_root.mon_port_on_vars:
                logger.error(self._logTag +
                    f"_monitor_task: port_id ({port_id}) not in mon_port_on_vars({self._gui_root.mon_port_on_vars.keys()})")
                continue
            if not self._gui_root.mon_port_on_vars[port_id].get():
                continue
            new_mon_buff.append(axframe_conf)

        """ Monitor Tree """
        self._gui_root.monitor_tree_update(new_mon_buff)
        """ Monitor """
        self.add_tasker_q(self._gui_root.monFrame.monitor_q_task,
                           new_mon_buff,
                           False)
        return True

    ######################################################################
    # Q-Tasks
    ######################################################################


