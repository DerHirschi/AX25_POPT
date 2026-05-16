import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import get_list_fm_viaStr
from fnc.str_fnc import get_strTab


class APRStracerSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style          = root_win.style
        self.style_name     = root_win.style_name
        self._root_win      = root_win
        self._popt_handler  = root_win.popt_handler
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        #self._aprs_icon_tab = root_win.guiIcon.get_aprs_icon_tab_32()
        # ====================================
        ais_cfg            = POPT_CFG.get_CFG_aprs_ais()
        # ====================================
        self._be_port_var = tk.StringVar(self, value=str(ais_cfg.get('be_tracer_port', 0)))
        self._be_wide_var = tk.StringVar(self, value=str(ais_cfg.get('be_tracer_wide', 1)))
        self._be_stat_var = tk.StringVar(self, value=ais_cfg.get('be_tracer_station', 'NOCALL'))
        path = ' '.join(ais_cfg.get('be_tracer_via', []))
        self._be_via_var         = tk.StringVar(self,  value=path)
        self._be_interval_var    = tk.StringVar(self,  value=str(ais_cfg.get('be_tracer_interval', 5)))
        self._be_active_var      = tk.BooleanVar(self, value=ais_cfg.get('be_tracer_active', False))
        self._alarm_active_var   = tk.BooleanVar(self, value=ais_cfg.get('be_tracer_alarm_active', False))
        self._alarm_distance_var = tk.StringVar(self,  value=str(ais_cfg.get('be_tracer_alarm_range', 50)))
        # ====================================
        l_frame = ttk.Frame(self)
        r_frame = ttk.LabelFrame(self, text=f"Beacon {self._getTabStr('settings')}")
        l_frame.pack(side='left', padx=10, pady=10, fill='x', anchor='n')
        r_frame.pack(side='left', padx=10, pady=10, fill='x', anchor='n')
        # ====================================
        # l_frame
        # == Port
        port_f = ttk.Frame(l_frame)
        port_f.pack(padx=5, pady=5, anchor='w')
        options = list(self._popt_handler.get_all_ports().keys())
        if not options:
            options = [0]
        ttk.Label(port_f, text='Port ').pack(side='left', padx=5)
        options = [self._be_port_var.get()] + options
        ttk.OptionMenu(port_f, self._be_port_var, *options,).pack(side='left')

        # == Call
        call_f = ttk.Frame(l_frame)
        call_f.pack(padx=5, pady=5, anchor='w')
        options = self._popt_handler.api.get_stat_calls_fm_port(ais_cfg.get('be_tracer_port', 0))

        ttk.Label(call_f, text='Station ').pack(side='left', padx=5)
        self._be_stat_opt = ttk.Combobox(call_f,
                                         width=10,
                                         textvariable=self._be_stat_var,
                                         values=options)
        self._be_stat_opt.pack(side='left')

        # == via
        via_f = ttk.Frame(l_frame)
        via_f.pack(padx=5, pady=5, anchor='w')
        ttk.Label(via_f, text='via ').pack(side='left', padx=5)
        ttk.Entry(via_f, textvariable=self._be_via_var, width=25).pack(side='left')

        # ====================================
        # r_frame
        # == WIDE
        wide_f = ttk.Frame(r_frame)
        wide_f.pack(padx=5, pady=5, anchor='w')
        ttk.Label(wide_f, text='via WIDE ').pack(side='left', padx=5)
        ttk.Spinbox(wide_f,
                    from_=1,
                    to=7,
                    increment=1,
                    width=3,
                    textvariable=self._be_wide_var,
                    # command=self.change_settings
                    ).pack(side='left')

        # == Interval
        interval_f = ttk.Frame(r_frame)
        interval_f.pack(padx=5, pady=5, anchor='w')
        ttk.Label(interval_f, text='Interval ').pack(side='left', padx=5)
        ttk.Spinbox(interval_f,
                    from_=1,
                    to=60,
                    increment=1,
                    width=3,
                    textvariable=self._be_interval_var,
                    # command=self.change_settings
                    ).pack(side='left')

        # == Active
        activ_f = ttk.Frame(r_frame)
        activ_f.pack(padx=5, pady=5, anchor='w')
        ttk.Label(activ_f, text='Activate ').pack(side='left', padx=5)
        ttk.Checkbutton(activ_f,
                        variable=self._be_active_var,
                        command=self._chk_active
                        ).pack(side='left', )

    def _chk_active(self, event=None):
        self.save_config()
        aprs_main = self._popt_handler.get_aprs_ais()
        aprs_main.set_be_tracer_active(self._be_active_var.get())
        # self._root_win.set_tracer_icon()

    def save_config(self):
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        ais_cfg['be_tracer_port']           = int(self._be_port_var.get())
        ais_cfg['be_tracer_station']        = self._be_stat_var.get()
        ais_cfg['be_tracer_wide']           = self._be_wide_var.get()
        path = get_list_fm_viaStr(self._be_via_var.get())
        ais_cfg['be_tracer_via']            = list(path)
        ais_cfg['be_tracer_interval']       = int(self._be_interval_var.get())
        ais_cfg['be_tracer_active']         = self._be_active_var.get()
        ais_cfg['be_tracer_alarm_active']   = bool(self._alarm_active_var.get())
        ais_cfg['be_tracer_alarm_range']    = int(self._alarm_distance_var.get())

        POPT_CFG.set_CFG_aprs_ais(ais_cfg)