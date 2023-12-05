import tkinter as tk
from tkinter import ttk

from cfg.constant import WEEK_DAYS_GE
from schedule.popt_sched import getNew_schedule_config


# from string_tab import STR_TABLE


class PoPT_Set_Scheduler(tk.Toplevel):
    def __init__(self, root_win, sel_frames=None):
        """
        ROOT WIN VARS needed:
        self.schedule_config = getNew_schedule_config()
        self.schedule_win = None
        Func needed/triggered when closed:
        self.scheduler_config_save_task()

        :returns to self._root_win.schedule_config on call self._set_vars_to_conf()
        :param root_win:
        # :param schedule_conf:   getNew_schedule_config()
        :param sel_frames:      ['min', 'h', 'wd', 'm', 'md']
        """
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        self._root_win.schedule_win = self
        # self._lang = root_win.language
        ##############
        # DEV
        """
        schedule_conf = build_schedule_config(intervall=5, move_time=20,
                                              minutes={10: True, 50: True},
                                              hours={1: True, 5: True},
                                              week_days={'MO': True, 'DO': True},
                                              month={1: True, 6: True},
                                              month_day={11: True, 16: True},
                                              set_interval=False)
        """
        ###################################
        # Vars
        if not self._root_win.schedule_config:
            self._root_win.schedule_config = getNew_schedule_config()
        self.schedule_config = self._root_win.schedule_config
        self._select_vars = {}
        self._min_sel = {}
        self._interval_var = tk.StringVar(self, value='0')
        self._offset_var = tk.StringVar(self, value='0')
        if not self.schedule_config:
            self.schedule_config = dict(getNew_schedule_config())
        if not sel_frames:
            sel_frames = ['min', 'h', 'wd', 'm', 'md']
            # sel_frames = ['wd', 'm', 'md']
        ###################################
        # self.title(STR_TABLE['msg_center'][self._lang])
        self.title('Scheduler-Set')
        # self.style = self._root_win.style
        self.geometry(f"800x"
                      f"600+"
                      f"{self._root_win.winfo_x()}+"
                      f"{self._root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        ###################################
        l_frame = tk.Frame(self, borderwidth=20, width=150)
        r_frame = tk.Frame(self, borderwidth=20)
        l_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, expand=False)
        r_frame.pack(side=tk.LEFT, expand=False, anchor='n')
        ###################################
        # L
        intervall_frame = tk.Frame(l_frame, borderwidth=5, height=30)
        btn_frame = tk.Frame(l_frame, borderwidth=5, height=40)
        intervall_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        self._init_interval_frame(intervall_frame)
        self._init_btn_frame(btn_frame)

        # RIGHT

        if 'min' in sel_frames:
            min_frame = tk.Frame(r_frame, borderwidth=5)
            min_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
            ttk.Separator(r_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X, expand=False)

            tk.Label(min_frame, text='Minuten').pack(side=tk.TOP, fill=tk.X, expand=False)
            self._init_select_frames(min_frame,
                                     [(x - 1) * 5 for x in range(1, 13)],
                                     'minutes'
                                     )
        if 'h' in sel_frames:
            h_frame = tk.Frame(r_frame, borderwidth=5)
            h_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
            ttk.Separator(r_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X, expand=False)

            tk.Label(h_frame, text='Stunden').pack(side=tk.TOP, fill=tk.X, expand=False)
            self._init_select_frames(h_frame,
                                     list(range(24)),
                                     'hours'
                                     )
        if 'wd' in sel_frames:
            weekDay_frame = tk.Frame(r_frame, borderwidth=5)
            weekDay_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
            ttk.Separator(r_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X, expand=False)

            tk.Label(weekDay_frame, text='Wochentage').pack(side=tk.TOP, fill=tk.X, expand=False)
            self._init_select_frames(weekDay_frame,
                                     WEEK_DAYS_GE,
                                     'week_days'
                                     )

        if 'm' in sel_frames:
            month_frame = tk.Frame(r_frame, borderwidth=5)
            month_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
            ttk.Separator(r_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X, expand=False)

            tk.Label(month_frame, text='Monate').pack(side=tk.TOP, fill=tk.X, expand=False)
            self._init_select_frames(month_frame,
                                     list(range(1, 13)),
                                     'month'
                                     )

        if 'md' in sel_frames:
            monthDay_frame = tk.Frame(r_frame, borderwidth=5)
            monthDay_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
            ttk.Separator(r_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X, expand=False)

            tk.Label(monthDay_frame, text='Monats Tage').pack(side=tk.TOP, fill=tk.X, expand=False)
            self._init_select_frames(monthDay_frame,
                                     list(range(1, 32)),
                                     'month_day'
                                     )

        self._set_vars_fm_conf()
        self._state_min_frame()

    def _init_interval_frame(self, frame: tk.Frame):
        tk.Label(frame, text='Intervall').pack(side=tk.TOP, fill=tk.X, expand=True)
        f1 = tk.Frame(frame, borderwidth=3)
        f2 = tk.Frame(frame, borderwidth=3)
        f1.pack(side=tk.TOP, expand=False, anchor='w')
        f2.pack(side=tk.TOP, expand=False, anchor='w')
        tk.Label(f1, text='Intervall (min): ', width=15).pack(side=tk.LEFT, expand=False)
        tk.Spinbox(f1,
                   from_=0,
                   to=1440,
                   increment=1,
                   textvariable=self._interval_var,
                   width=5,
                   command=self._state_min_frame
                   ).pack(side=tk.LEFT, expand=False)
        tk.Label(f2, text='Versatz (sek): ', width=15).pack(side=tk.LEFT, expand=False)
        tk.Spinbox(f2,
                   from_=0,
                   to=59,
                   increment=1,
                   textvariable=self._offset_var,
                   width=3
                   ).pack(side=tk.LEFT, expand=False)

    def _init_btn_frame(self, frame: tk.Frame):
        tk.Button(frame,
                  text='Ok',
                  command=self._ok
                  ).pack(side=tk.LEFT, expand=False)
        tk.Button(frame,
                  text='Abbrechen',
                  command=self._close
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(frame,
                  text='RESET',
                  command=self._reset_all_selVars
                  ).pack(side=tk.RIGHT, expand=False)

    def _init_select_frames(self, frame: tk.Frame, sel_list: list, var_k):
        """
        :param frame: tk.Frame
        :param sel_list: list
        :return: var_dict: dict
        """
        var_dict = {}
        el_c = 0
        intern_frame = tk.Frame(frame)
        intern_frame.pack(side=tk.LEFT, expand=False)
        tk.Button(intern_frame,
                  text='Reset',
                  command=lambda: self._reset_selVars(var_k)
                  ).pack(side=tk.TOP, expand=False)
        for el in sel_list:
            if not el_c:
                intern_frame = tk.Frame(frame)
                intern_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
            if intern_frame:
                var = tk.BooleanVar(self)
                var_dict[el] = var
                text = str(el).ljust(3)
                chk_btn = tk.Checkbutton(intern_frame, text=text, variable=var, width=2)
                chk_btn.pack(side=tk.LEFT)

                if var_k == 'minutes':
                    self._min_sel[el] = chk_btn
                el_c = (el_c + 1) % 7
        self._select_vars[var_k] = var_dict

    def _set_vars_fm_conf(self):
        for k in self._select_vars.keys():
            for kk in self._select_vars[k]:
                if self.schedule_config.get(k, {}).get(kk, False):
                    self._select_vars[k][kk].set(True)
        self._interval_var.set(value=self.schedule_config["repeat_min"])
        self._offset_var.set(value=self.schedule_config["move"])

    def _set_vars_to_conf(self):
        # Todo: Testen
        # Don't like this solution..
        for k in self._select_vars.keys():
            for kk in self._select_vars[k]:
                if self._select_vars[k][kk].get():
                    if not self.schedule_config.get(k, None):
                        self.schedule_config[k] = {}
                    self.schedule_config[k][kk] = True
        self.schedule_config["repeat_min"] = int(self._interval_var.get())
        self.schedule_config["move"] = int(self._offset_var.get())
        self._root_win.schedule_config = dict(self.schedule_config)

    def _state_min_frame(self, event=None):
        if int(self._interval_var.get()):
            self._disable_min_sel()
        else:
            self._enable_min_sel()

    def _disable_min_sel(self):
        for k in self._min_sel.keys():
            if self._min_sel[k].cget('state') == 'normal':
                self._min_sel[k].configure(state='disabled')

    def _enable_min_sel(self):
        for k in self._min_sel.keys():
            if self._min_sel[k].cget('state') == 'disabled':
                self._min_sel[k].configure(state='normal')

    def _reset_selVars(self, var_k):
        sel_vars = self._select_vars.get(var_k, {})
        for k in sel_vars.keys():
            sel_vars[k].set(False)

    def _reset_all_selVars(self):
        for k in self._select_vars.keys():
            for kk in self._select_vars[k].keys():
                self._select_vars[k][kk].set(False)
        self._interval_var.set(value='0')
        self._offset_var.set(value='0')
        self._state_min_frame()

    def _ok(self):
        self._set_vars_to_conf()
        if self._root_win.scheduler_config_save_task:
            self._root_win.scheduler_config_save_task()
        self._close()

    def _close(self):
        self._root_win.schedule_win = None
        self.destroy()

