import time
import tkinter as tk

from ax25.ax25InitPorts import PORT_HANDLER


class AlarmIconFrame(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root, bg='#313336', height=15, width=50)
        self.pack(fill=tk.X, pady=5, expand=False)

        self._diesel_label = tk.Label(self, text='➿',
                                      font=(None, 12,),
                                      # state='disabled',
                                      background='#313336',
                                      foreground='orange')
        self._diesel_label.pack(side=tk.LEFT, padx=5)

        self._mh_label = tk.Label(self, text='⊛',
                                  font=(None, 14),
                                  state='disabled',
                                  background='#313336',
                                  foreground='#18e002')
        self._mh_label.pack(side=tk.LEFT, padx=3)

        self._tracer_label = tk.Label(self, text='⨂',
                                      font=(None, 9),
                                      background='#313336',
                                      state='disabled',
                                      foreground='#18e002')
        self._tracer_label.pack(side=tk.LEFT, padx=3)

        self._beacon_label = tk.Label(self, text='⨀',
                                      font=(None, 9),
                                      background='#313336',
                                      state='disabled',
                                      foreground='#18e002')
        self._beacon_label.pack(side=tk.LEFT, padx=3)

        self._rxEcho_label = tk.Label(self, text='⤨',
                                      font=(None, 14),
                                      background='#313336',
                                      state='disabled',
                                      foreground='#18e002')
        self._rxEcho_label.pack(side=tk.LEFT, padx=3)

        self._pms_mail_label = tk.Label(self, text='✉',
                                        font=(None, 15,),
                                        background='#313336',
                                        state='disabled',
                                        foreground='#18e002')
        self._pms_mail_label.pack(side=tk.LEFT, padx=3)

        self._pms_fwd_label = tk.Label(self, text='✉⇄',
                                       font=(None, 15,),
                                       background='#313336',
                                       state='disabled',
                                       foreground='#18e002')
        self._pms_fwd_label.pack(side=tk.LEFT, padx=3)

        self._05_blink = {
            'diesel': 0,
            'dx': 0,
            'tracer': 0,
            'beacon': 0,
            'rxecho': 0,
            'pmsmail': 0,
            'pmsfwd': 0,
        }
        self._1_blink = {
            'diesel': 0,
            'dx': 0,
            'tracer': 0,
            'beacon': 0,
            'rxecho': 0,
            'pmsmail': 0,
            'pmsfwd': 0,
        }

        self._alarm_labels = {
            'diesel': self._diesel_label,
            'dx': self._mh_label,
            'tracer': self._tracer_label,
            'beacon': self._beacon_label,
            'rxecho': self._rxEcho_label,
            'pmsmail': self._pms_mail_label,
            'pmsfwd': self._pms_fwd_label,
        }

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

    def add_blink_task(self, alarm_k: str, blink_n: int, sec05=True):
        if not blink_n:
            return
        if alarm_k not in self._alarm_labels.keys():
            return
        label = self._alarm_labels.get(alarm_k, None)
        if not label:
            return
        if sec05:
            if alarm_k not in self._05_blink.keys():
                return
            self._05_blink[alarm_k] += blink_n
        else:
            if alarm_k not in self._1_blink.keys():
                return
            self._1_blink[alarm_k] += blink_n

    def _is_blink_task(self, alarm_k):
        task_05 = self._05_blink.get(alarm_k, 0)
        task_1 = self._1_blink.get(alarm_k, 0)
        if any((task_05, task_1)):
            return True
        return False

    def remove_blink_task(self, alarm_k: str, sec05=True):
        label = self._alarm_labels.get(alarm_k, None)
        if not label:
            return
        if sec05:
            if alarm_k not in self._05_blink.keys():
                return
            self._05_blink[alarm_k] = 0
        else:
            if alarm_k not in self._1_blink.keys():
                return
            self._1_blink[alarm_k] = 0
        """
        if label.cget('state') == 'normal':
            label.configure(state='disabled')
        """

    def set_dxAlarm(self, alarm_set=True):
        if alarm_set:
            if self._mh_label.cget('foreground') != '#18e002':
                self._mh_label.configure(foreground='#18e002')
            self.add_blink_task('dx', -1, sec05=False)
        else:
            if self._mh_label.cget('foreground') != '#f0d402':
                self._mh_label.configure(foreground='#f0d402')
            self.remove_blink_task('dx', sec05=False)

    def set_dxAlarm_active(self, alarm_set=True):
        self.set_dxAlarm(False)
        if alarm_set:
            if self._mh_label.cget('foreground') != '#f0d402':
                self._mh_label.configure(foreground='#f0d402')
            if self._mh_label.cget('state') == 'disabled':
                self.add_blink_task('dx', 3, sec05=True)
            return
        if self._mh_label.cget('state') == 'normal':
            self.add_blink_task('dx', 3, sec05=True)
        return

    def set_tracerAlarm(self, alarm_set=True):
        if alarm_set:
            self.add_blink_task('tracer', -1, sec05=False)
        else:
            self.remove_blink_task('tracer', sec05=False)

    def set_pmsMailAlarm(self, alarm_set=True):
        if alarm_set:
            self.add_blink_task('pmsmail', -1, sec05=False)
        else:
            self.remove_blink_task('pmsmail', sec05=False)
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

        self.add_blink_task('pmsfwd', bl, sec05=True)

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
        self.add_blink_task('beacon', bl, sec05=True)

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

        self.add_blink_task('rxecho', bl, sec05=True)

    def _TracerIcon_tasker(self):
        """  """
        tracer = PORT_HANDLER.get_aprs_ais()
        alarm_k = 'tracer'
        if not tracer:
            if self._tracer_label.cget('state') == 'normal':
                if not self._is_blink_task(alarm_k):
                    # self._tracer_label.configure(state='disabled')
                    self.add_blink_task(alarm_k, 3, sec05=True)
            return
        at_active = tracer.tracer_auto_tracer_get_active()
        t_active = tracer.tracer_tracer_get_active()
        if not t_active and not at_active:
            if self._tracer_label.cget('state') == 'normal':
                if not self._is_blink_task(alarm_k):
                    # self._tracer_label.configure(state='disabled')
                    self.add_blink_task(alarm_k, 3, sec05=True)
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
            self.add_blink_task(alarm_k, bl, sec05=True)
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
            self.add_blink_task(alarm_k, bl, sec05=True)
            return
        if self._tracer_label.cget('foreground') != '#03cefc':
            self._tracer_label.configure(foreground='#03cefc')
            bl = 2
        if self._tracer_label.cget('state') == 'disabled':
            if not self._is_blink_task(alarm_k):
                # self._tracer_label.configure(state='disabled')
                bl = 3
        self.add_blink_task(alarm_k, bl, sec05=True)
        return
