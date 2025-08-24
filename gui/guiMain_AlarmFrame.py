import time
import tkinter as tk

from ax25.ax25InitPorts import PORT_HANDLER


class AlarmIconFrame(tk.Frame):
    def __init__(self, root, main_gui):
        tk.Frame.__init__(self, root, bg='#313336', height=15, width=50)
        self.pack(fill='x', pady=5, expand=False)

        self._diesel_label = tk.Label(self, text='➿',
                                      font=('', 12,),
                                      # state='disabled',
                                      background='#313336',
                                      foreground='orange')
        self._diesel_label.pack(side='left', padx=5)

        self._block_in_conn = tk.Label(self, text='⛝',
                                  font=('', 13),
                                  state='disabled',
                                  background='#313336',
                                  foreground='#fa2020')
        self._block_in_conn.pack(side='left', padx=3)
        self._block_in_conn.bind('<Button-1>', lambda event: main_gui.open_BlockList_win())

        self._mh_label = tk.Label(self, text='⊛',
                                  font=('', 14),
                                  state='disabled',
                                  background='#313336',
                                  foreground='#18e002')
        self._mh_label.pack(side='left', padx=3)
        self._mh_label.bind('<Button-1>', lambda event: main_gui.open_MH_win())

        self._tracer_label = tk.Label(self, text='☈',
                                      font=('', 11),
                                      background='#313336',
                                      state='disabled',
                                      foreground='#18e002')
        self._tracer_label.pack(side='left', padx=3)
        self._tracer_label.bind('<Button-1>', lambda event: main_gui.open_be_tracer_win())

        self._beacon_label = tk.Label(self, text='⨀',
                                      font=('', 9),
                                      background='#313336',
                                      state='disabled',
                                      foreground='#18e002')
        self._beacon_label.pack(side='left', padx=3)

        self._rxEcho_label = tk.Label(self, text='⤨',
                                      font=('', 14),
                                      background='#313336',
                                      state='disabled',
                                      foreground='#18e002')
        self._rxEcho_label.pack(side='left', padx=3)

        self._pms_fwd_label = tk.Label(self, text='✉⇄',
                                       font=('', 15,),
                                       background='#313336',
                                       state='disabled',
                                       foreground='#18e002')
        self._pms_fwd_label.pack(side='left', padx=3)
        self._pms_fwd_label.bind('<Button-1>', lambda event: main_gui.open_window('pms_fwq_q'))

        self._pms_mail_label = tk.Label(self, text='✉',
                                        font=('', 15,),
                                        background='#313336',
                                        state='disabled',
                                        foreground='#18e002')
        self._pms_mail_label.pack(side='left', padx=3)
        self._pms_mail_label.bind('<Button-1>', lambda event: main_gui.open_window('pms_msg_center'))


        self._aprs_mail_label = tk.Label(self, text='Ⓐ✉',
                                         font=('', 15,),
                                         background='#313336',
                                         state='disabled',
                                         foreground='#18e002')
        self._aprs_mail_label.pack(side='left', padx=3)
        self._aprs_mail_label.bind('<Button-1>', lambda event: main_gui.open_window('aprs_msg'))

        self._bell_label = tk.Label(self, text='☎',
                                    font=('', 11,),
                                    background='#313336',
                                    state='disabled',
                                    foreground='#18e002')
        self._bell_label.pack(side='left', padx=3)

        ##############################
        # Tasker
        self._alarm_labels = {
            'diesel':       self._diesel_label,
            'block_conn':   self._block_in_conn,
            'dx':           self._mh_label,
            'tracer':       self._tracer_label,
            'beacon':       self._beacon_label,
            'rxecho':       self._rxEcho_label,
            'aprsmail':     self._aprs_mail_label,
            'pmsmail':      self._pms_mail_label,
            'pmsfwd':       self._pms_fwd_label,
            'bell':         self._bell_label,
        }
        self._05_blink = {}
        self._1_blink  = {}
        for k in self._alarm_labels.keys():
            self._05_blink[k] = 0
            self._1_blink[k]  = 0

        ##############################
        # States
        self._glb_port_blocking = False

    def AlarmIcon_tasker05(self):
        for k in list(self._05_blink.keys()):
            if self._05_blink[k]:
                if self._05_blink[k] > 0:
                    self._05_blink[k] -= 1
                if k in self._alarm_labels.keys():
                    if self._alarm_labels[k].cget('state') == 'disabled':
                        self._alarm_labels[k].configure(state='normal')
                    else:
                        self._alarm_labels[k].configure(state='disabled')

    def AlarmIcon_tasker1(self):
        for k in list(self._1_blink.keys()):
            if self._1_blink[k]:
                if self._1_blink[k] > 0:
                    self._1_blink[k] -= 1
                if k in self._alarm_labels.keys():
                    if self._alarm_labels[k].cget('state') == 'disabled':
                        self._alarm_labels[k].configure(state='normal')
                    else:
                        self._alarm_labels[k].configure(state='disabled')
        self._TracerIcon_tasker()

    def _add_blink_task(self, alarm_k: str, blink_n: int, sec05=True):
        if not blink_n:
            return
        if sec05:
            self._05_blink[alarm_k] += blink_n
        else:
            self._1_blink[alarm_k] += blink_n

    def _is_blink_task(self, alarm_k):
        task_05 = self._05_blink.get(alarm_k, 0)
        task_1  = self._1_blink.get(alarm_k, 0)
        if any((task_05, task_1)):
            return True
        return False

    def _remove_blink_task(self, alarm_k: str, sec05=True):
        if sec05:
            if self._05_blink[alarm_k]:
                self._05_blink[alarm_k] = 0
        else:
            if self._1_blink[alarm_k]:
                self._1_blink[alarm_k] = 0
        """
        if label.cget('state') == 'normal':
            label.configure(state='disabled')
        """

    ###################################
    #
    def set_PortBlocking(self, set_on=True, blinking=True):
        if set_on:
            if self._glb_port_blocking:
                return
            if self._block_in_conn.cget('foreground') != '#fa2020':
                self._block_in_conn.configure(foreground='#fa2020')
            if blinking:
                self._add_blink_task('block_conn', -1, sec05=True)
            elif self._block_in_conn.cget('state') == 'disabled':
                self._add_blink_task('block_conn', 3, sec05=True)
            elif self._block_in_conn.cget('state') == 'normal':
                self._add_blink_task('block_conn', 2, sec05=True)
            self._glb_port_blocking = True
        elif not set_on:
            if not self._glb_port_blocking:
                return
            self._remove_blink_task('block_conn', sec05=True)
            if self._block_in_conn.cget('state') == 'normal':
                self._add_blink_task('block_conn', 1, sec05=True)
            self._glb_port_blocking = False
            #else:
            #    self._add_blink_task('block_conn', 2, sec05=True)

    def set_PortBlocking_warning(self):
        if self._glb_port_blocking:
            return
        if self._1_blink['block_conn']:
            return
        if self._block_in_conn.cget('foreground') != '#ecf70f':
            self._block_in_conn.configure(foreground='#ecf70f')

        if self._block_in_conn.cget('state') == 'disabled':
            self._add_blink_task('block_conn', 4, sec05=False)
        else:
            self._add_blink_task('block_conn', 5, sec05=False)


    def set_dxAlarm(self, alarm_set=True):
        if alarm_set:
            """
            if self._mh_label.cget('foreground') != '#18e002':
                self._mh_label.configure(foreground='#18e002')
            """
            self._add_blink_task('dx', -1, sec05=False)
        else:
            """
            if self._mh_label.cget('foreground') != '#f0d402':
                self._mh_label.configure(foreground='#f0d402')
            """
            self._remove_blink_task('dx', sec05=False)

    def set_dxAlarm_active(self, alarm_set=True):
        self.set_dxAlarm(False)
        if alarm_set:
            """
            if self._mh_label.cget('foreground') != '#f0d402':
                self._mh_label.configure(foreground='#f0d402')
            """
            if self._mh_label.cget('state') == 'disabled':
                self._add_blink_task('dx', 3, sec05=True)
            return
        if self._mh_label.cget('state') == 'normal':
            self._add_blink_task('dx', 3, sec05=True)
        return

    def set_Bell_alarm(self, alarm_set=True):
        if alarm_set:
            self._add_blink_task('bell', -1, sec05=False)
        else:
            self._remove_blink_task('bell', sec05=False)

    def set_Bell_active(self, alarm_set=True):
        if alarm_set:
            if self._bell_label.cget('state') == 'disabled':
                self._add_blink_task('bell', 3, sec05=True)
            return
        if self._bell_label.cget('state') == 'normal':
            self._add_blink_task('bell', 3, sec05=True)
        return

    def set_aprsMail_alarm(self, alarm_set=True):
        if alarm_set:
            if self._aprs_mail_label.cget('state') == 'disabled':
                bl = 3
            else:
                bl = 2
        else:
            if self._aprs_mail_label.cget('state') == 'normal':
                bl = 3
            else:
                bl = 2

        self._add_blink_task('aprsmail', bl, sec05=True)

    def set_tracerAlarm(self, alarm_set=True):
        if alarm_set:
            self._add_blink_task('tracer', -1, sec05=False)
        else:
            self._remove_blink_task('tracer', sec05=False)

    def set_pmsMailAlarm(self, alarm_set=True):
        if alarm_set:
            self._add_blink_task('pmsmail', -1, sec05=False)
        else:
            self._remove_blink_task('pmsmail', sec05=False)
            if self._pms_mail_label.cget('state') == 'normal':
                self._pms_mail_label.configure(state='disabled')

    def set_diesel(self, alarm_set=True):
        if alarm_set:
            if self._diesel_label.cget('state') == 'disabled':
                self._diesel_label.configure(state='normal')
        else:
            if self._diesel_label.cget('state') == 'normal':
                self._diesel_label.configure(state='disabled')

    def set_pms_fwd_alarm(self, alarm_set=True):

        if alarm_set:
            if self._pms_fwd_label.cget('state') == 'disabled':
                bl = 3
            else:
                bl = 2
        else:
            if self._pms_fwd_label.cget('state') == 'normal':
                bl = 3
            else:
                bl = 2

        self._add_blink_task('pmsfwd', bl, sec05=True)

    def set_beacon_icon(self, alarm_set=True):
        if alarm_set:
            if self._beacon_label.cget('state') == 'disabled':
                bl = 3
            else:
                bl = 2
        else:
            if self._beacon_label.cget('state') == 'normal':
                bl = 3
            else:
                bl = 2
        self._add_blink_task('beacon', bl, sec05=True)

    def set_rxEcho_icon(self, alarm_set=True):
        if alarm_set:
            if self._rxEcho_label.cget('state') == 'disabled':
                bl = 3
            else:
                bl = 2
        else:
            if self._rxEcho_label.cget('state') == 'normal':
                bl = 3
            else:
                bl = 2

        self._add_blink_task('rxecho', bl, sec05=True)

    def _TracerIcon_tasker(self):
        """  """
        tracer  = PORT_HANDLER.get_aprs_ais()
        alarm_k = 'tracer'
        if not tracer:
            if self._tracer_label.cget('state') == 'normal':
                if not self._is_blink_task(alarm_k):
                    # self._tracer_label.configure(state='disabled')
                    self._add_blink_task(alarm_k, 3, sec05=True)
            return
        at_active = tracer.tracer_auto_tracer_get_active()
        t_active  = tracer.tracer_tracer_get_active()
        if not t_active and not at_active:
            if self._tracer_label.cget('state') == 'normal':
                if not self._is_blink_task(alarm_k):
                    # self._tracer_label.configure(state='disabled')
                    self._add_blink_task(alarm_k, 3, sec05=True)
            return
        bl = 0
        if not at_active:
            if self._tracer_label.cget('foreground') != '#18e002':
                self._tracer_label.configure(foreground='#18e002')
                bl = 2
            if self._tracer_label.cget('state') == 'disabled':
                if not self._is_blink_task(alarm_k):
                    # self._tracer_label.configure(state='disabled')
                    bl = 3
            self._add_blink_task(alarm_k, bl, sec05=True)
            return
        at_timer = tracer.tracer_auto_tracer_get_active_timer()
        if at_timer < time.time():
            if self._tracer_label.cget('foreground') != '#f0d402':
                self._tracer_label.configure(foreground='#f0d402')
                bl = 2
            if self._tracer_label.cget('state') == 'disabled':
                if not self._is_blink_task(alarm_k):
                    # self._tracer_label.configure(state='disabled')
                    bl = 3
            self._add_blink_task(alarm_k, bl, sec05=True)
            return
        if self._tracer_label.cget('foreground') != '#03cefc':
            self._tracer_label.configure(foreground='#03cefc')
            bl = 2
        if self._tracer_label.cget('state') == 'disabled':
            if not self._is_blink_task(alarm_k):
                # self._tracer_label.configure(state='disabled')
                bl = 3
        self._add_blink_task(alarm_k, bl, sec05=True)
        return
