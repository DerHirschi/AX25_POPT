import tkinter as tk
from tkinter import ttk
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE


class DIGI_cfg_Tab(tk.Frame):
    def __init__(self, root_win, digi_settings: dict):
        tk.Frame.__init__(self, root_win)
        self.pack()
        ##################
        # Vars
        self._digi_enabled = tk.BooleanVar(self, value=digi_settings.get('digi_enabled', False))
        self._managed_digi = tk.BooleanVar(self, value=digi_settings.get('managed_digi', False))
        # Managed-DIGI Parameter #######################################################
        self._digi_ssid_port = tk.BooleanVar(self, value=digi_settings.get('digi_ssid_port', True))
        # OR
        self._digi_auto_port = tk.BooleanVar(self, value=digi_settings.get('digi_auto_port', True))

        self._short_via_calls = tk.BooleanVar(self, value=digi_settings.get('short_via_calls', True))
        self._UI_short_via_calls = tk.BooleanVar(self, value=digi_settings.get('UI_short_via', False))
        self._max_buff = tk.StringVar(self, value=str(digi_settings.get('max_buff', 10)))
        self._max_n2 = tk.StringVar(self, value=str(digi_settings.get('max_n2', 4)))
        self._last_rx_fail_sec = tk.StringVar(self, value=str(digi_settings.get('last_rx_fail_sec', 60)))

        ##################
        # DIGI enbaled
        opt_frame_0 = tk.Frame(self)
        opt_frame_0.pack(fill=tk.X)
        digi_chk = tk.Checkbutton(opt_frame_0,
                                          text='DIGI',
                                          variable=self._digi_enabled,
                                          command=self._set_l3_digi_entry_state)
        digi_chk.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        ##################
        # Managed DIGI
        self._managed_digi_chk = tk.Checkbutton(opt_frame_0,
                                          text='L3-DIGI',
                                          variable=self._managed_digi,
                                          command=self._set_l3_digi_entry_state)
        self._managed_digi_chk.pack(side=tk.LEFT, padx=5, pady=5)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5, expand=False)
        ##################################################################
        opt_frame_1 = tk.Frame(self)
        opt_frame_1.pack(fill=tk.X)
        ##################
        self._ssid_port_ent = tk.Checkbutton(opt_frame_1,
                                             text='SSID=PORT',
                                             variable=self._digi_ssid_port,
                                             command=self._set_port_entry_state)
        self._ssid_port_ent.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self._auto_port_ent = tk.Checkbutton(opt_frame_1,
                                             text='AutoPort fm MH',
                                             variable=self._digi_auto_port,
                                             command=self._set_port_entry_state)
        self._auto_port_ent.pack(side=tk.LEFT, padx=20)
        ##################################################################
        opt_frame_2 = tk.Frame(self)
        opt_frame_2.pack(fill=tk.X)
        ##################
        self._short_via_ent = tk.Checkbutton(opt_frame_2,
                                             text='Short VIAs ',
                                             variable=self._short_via_calls)
        self._short_via_ent.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.W)
        self._UI_short_via_ent = tk.Checkbutton(opt_frame_2,
                                                text='UI-Frames Short VIAs',
                                                variable=self._UI_short_via_calls)
        self._UI_short_via_ent.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.W)
        ##################################################################
        opt_frame_3 = tk.Frame(self)
        opt_frame_3.pack(fill=tk.X, padx=5, pady=5)
        ##################
        tk.Label(opt_frame_3, text='MAX Buffer till RNR: ').pack(side=tk.LEFT, padx=5)
        self._max_buff_ent = tk.Spinbox(opt_frame_3,
                                        textvariable=self._max_buff,
                                        from_=0,
                                        to=10000,
                                        increment=100,
                                        width=5)
        self._max_buff_ent.pack(side=tk.LEFT, padx=10)
        tk.Label(opt_frame_3, text='Bytes').pack(side=tk.LEFT, padx=5)
        ##################################################################
        opt_frame_4 = tk.Frame(self)
        opt_frame_4.pack(fill=tk.X, padx=5, pady=5)
        ##################
        tk.Label(opt_frame_4, text='MAX N2 till RNR: ').pack(side=tk.LEFT, padx=5)
        self._max_n2_ent = tk.Spinbox(opt_frame_4,
                                      textvariable=self._max_n2,
                                      from_=0,
                                      to=15,
                                      increment=1,
                                      width=3)
        self._max_n2_ent.pack(side=tk.LEFT, padx=10)
        ##################################################################
        opt_frame_5 = tk.Frame(self)
        opt_frame_5.pack(fill=tk.X, padx=5, pady=5)
        ##################
        tk.Label(opt_frame_5, text='last SABM RX Fail').pack(side=tk.LEFT, padx=5)
        self._max_SABM_ent = tk.Spinbox(opt_frame_5,
                                        textvariable=self._last_rx_fail_sec,
                                        from_=10,
                                        to=200,
                                        increment=10,
                                        width=4)
        self._max_SABM_ent.pack(side=tk.LEFT, padx=10)
        tk.Label(opt_frame_5, text='Sec').pack(side=tk.LEFT, padx=5)
        ###################################################################
        ###################################################################
        ###################################################################
        self._init_entry_state()

    def _init_entry_state(self):
        self._set_l3_digi_entry_state()

    def _set_l3_digi_entry_state(self, event=None):
        if not self._digi_enabled.get():
            self._managed_digi_chk.configure(state='disabled')
            self._short_via_ent.configure(state='disabled')
            self._UI_short_via_ent.configure(state='disabled')
            self._max_buff_ent.configure(state='disabled')
            self._max_n2_ent.configure(state='disabled')
            self._max_SABM_ent.configure(state='disabled')
            self._ssid_port_ent.configure(state='disabled')
            self._auto_port_ent.configure(state='disabled')
            return
        self._managed_digi_chk.configure(state='normal')
        if self._managed_digi.get():
            self._short_via_ent.configure(state='normal')
            self._UI_short_via_ent.configure(state='normal')
            self._max_buff_ent.configure(state='normal')
            self._max_n2_ent.configure(state='normal')
            self._max_SABM_ent.configure(state='normal')
        else:
            self._short_via_ent.configure(state='disabled')
            self._UI_short_via_ent.configure(state='disabled')
            self._max_buff_ent.configure(state='disabled')
            self._max_n2_ent.configure(state='disabled')
            self._max_SABM_ent.configure(state='disabled')
        self._set_port_entry_state()

    def _set_port_entry_state(self, event=None):
        if not self._managed_digi.get():
            self._ssid_port_ent.configure(state='disabled')
            self._auto_port_ent.configure(state='disabled')
            return
        if self._digi_ssid_port.get():
            self._digi_auto_port.set(False)
            self._auto_port_ent.configure(state='disabled')
        else:
            self._auto_port_ent.configure(state='normal')

        if self._digi_auto_port.get():
            self._digi_ssid_port.set(False)
            self._ssid_port_ent.configure(state='disabled')
        else:
            self._ssid_port_ent.configure(state='normal')

    def get_cfg_fm_vars(self):
        ret = POPT_CFG.get_digi_default_CFG()
        ret['digi_enabled'] = bool(self._digi_enabled.get())
        ret['managed_digi'] = bool(self._managed_digi.get())
        # Managed-DIGI Parameter ###############################################################################
        ret['short_via_calls'] = bool(self._short_via_calls.get())  # Short VIA Call in AX25 Address
        ret['UI_short_via'] = bool(self._UI_short_via_calls.get())  # UI-Frames: Short VIA Call in AX25 Address
        ret['max_buff'] = int(self._max_buff.get())  # bytes till RNR
        ret['max_n2'] = int(self._max_n2.get())  # N2 till RNR
        ret['last_rx_fail_sec'] = int(self._last_rx_fail_sec.get())  # sec fail when no SABM and Init state
        ret['digi_ssid_port'] = bool(self._digi_ssid_port.get())  # DIGI SSID = TX-Port
        ret['digi_auto_port'] = bool(self._digi_auto_port.get())  # Get TX-Port fm MH-List
        return dict(ret)


class DIGI_SettingsWin(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        self._lang = POPT_CFG.get_guiCFG_language()
        #####################################################################
        # PORT_HANDLER.update_digi_setting()
        #####################################################################

        tabControl = ttk.Notebook(self)
        tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=15)
        # Tab Vars
        self._tab_list: {int: DIGI_cfg_Tab} = {}

        all_DIGIs = POPT_CFG.get_digi_CFG()
        for digi_call, digi_cfg in all_DIGIs.items():
            tab = DIGI_cfg_Tab(tabControl, digi_cfg, )
            self._tab_list[digi_call] = tab
            port_lable_text = f'{digi_call}'
            tabControl.add(tab, text=port_lable_text)

    def _set_cfg_to_port(self):
        all_DIGIs = POPT_CFG.get_digi_CFG()
        new_cfg = {}
        for digi_call, digi_cfg in all_DIGIs.items():
            if digi_call in self._tab_list:
                new_cfg[digi_call] = self._tab_list[digi_call].get_cfg_fm_vars()
        POPT_CFG.set_digi_CFG(new_cfg)

    def _save_cfg(self):
        self._set_cfg_to_port()
        POPT_CFG.save_MAIN_CFG_to_file()

    @staticmethod
    def _get_config():
        return dict(POPT_CFG.get_digi_CFG())

    def save_config(self):
        old_cfg = self._get_config()
        self._save_cfg()
        if old_cfg == self._get_config():
            return False
        self._set_cfg_to_port()
        return False