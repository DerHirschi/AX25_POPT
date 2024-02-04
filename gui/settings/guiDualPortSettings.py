import tkinter as tk
from tkinter import ttk, Menu
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import DUALPORT_TX_MODE
from cfg.default_config import getNew_dualPort_cfg
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE


class DP_cfg_Tab(tk.Frame):
    def __init__(self, root_win, dp_settings: dict):
        tk.Frame.__init__(self, root_win)
        self.pack()
        ##################
        # Port
        port_frame = tk.Frame(self)
        port_frame.pack(fill=tk.X, padx=5, pady=5)

        port_opt = list(PORT_HANDLER.ax25_ports.keys())
        self._prim_port_var = tk.StringVar(self, value=str(dp_settings.get('primary_port_id', -1)))
        self._sec_port_var = tk.StringVar(self, value=str(dp_settings.get('secondary_port_id', -1)))

        prim_port_frame = tk.Frame(port_frame)
        prim_port_frame.pack(side=tk.LEFT, expand=True)
        prim_port_label = tk.Label(prim_port_frame, text='Primary-Port: ')
        prim_port_label.pack(side=tk.LEFT)
        prim_port = tk.OptionMenu(prim_port_frame, self._prim_port_var, *port_opt)
        prim_port.pack(side=tk.LEFT)

        sec_port_frame = tk.Frame(port_frame)
        sec_port_frame.pack(side=tk.LEFT, expand=True)
        sec_port_label = tk.Label(sec_port_frame, text='Secondary-Port: ')
        sec_port_label.pack(side=tk.LEFT)
        sec_port = tk.OptionMenu(sec_port_frame, self._sec_port_var, *port_opt)
        sec_port.pack(side=tk.LEFT)

        ##################
        # Options
        opt_frame = tk.Frame(self)
        opt_frame.pack(fill=tk.Y, padx=5, pady=15, anchor=tk.W)

        self._tx_prim_var = tk.BooleanVar(self, value=bool(dp_settings.get('tx_primary', True)))
        tx_prim = tk.Checkbutton(opt_frame, text='TX on primary Port', variable=self._tx_prim_var)
        tx_prim.pack(anchor=tk.W)

        self._tx_auto_var = tk.BooleanVar(self, value=bool(dp_settings.get('auto_tx', False)))
        tx_auto = tk.Checkbutton(opt_frame, text='Auto TX-Port', variable=self._tx_auto_var)
        tx_auto.pack(anchor=tk.W, side=tk.LEFT)
        ################
        # Auto-TX Mode
        mode_opt = list(DUALPORT_TX_MODE.keys())
        self._tx_auto_mode_var = tk.StringVar(self, value=mode_opt[dp_settings.get('auto_tx_mode', 0)])
        tx_auto_mode = tk.Frame(opt_frame)
        tx_auto_mode.pack(padx=80)
        tx_auto_mode_label = tk.Label(tx_auto_mode, text='Auto-TX Mode: ')
        tx_auto_mode_label.pack(side=tk.LEFT)
        tx_auto_mode = tk.OptionMenu(tx_auto_mode, self._tx_auto_mode_var, *mode_opt)
        tx_auto_mode.pack(side=tk.LEFT)

    def get_cfg_fm_vars(self):
        prim_port = self._prim_port_var.get()
        sec_port = self._sec_port_var.get()
        if prim_port == sec_port:
            return {}
        if prim_port == -1 or sec_port == -1:
            return {}

        return dict(
            tx_primary=bool(self._tx_prim_var.get()),                               # TX Primary/Secondary
            auto_tx=bool(self._tx_auto_var.get()),                                  # Auto TX
            auto_tx_mode=int(DUALPORT_TX_MODE.get(self._tx_auto_mode_var.get(), 0)),     # Auto TX Mode
            primary_port_id=int(prim_port),
            secondary_port_id=int(sec_port)
        )


class DualPortSettingsWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._lang = root_win.language
        self._root_win = root_win
        self.win_height = 330
        self.win_width = 600
        self.style = root_win.style
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.title('DualPort-Settings')
        self._root_win.dualPort_settings_win = self

        self.tabControl = ttk.Notebook(self)
        self.tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=15)
        # Tab Vars
        self.tab_list: {int: DP_cfg_Tab} = {}

        all_dualPorts = POPT_CFG.get_dualPort_CFG()
        for port_id in all_dualPorts.keys():
            dp_cfg = all_dualPorts.get(port_id, {})
            if dp_cfg:
                tab = DP_cfg_Tab(self.tabControl, dp_cfg, )
                self.tab_list[port_id] = tab
                port_lable_text = 'Port {}'.format(port_id)
                self.tabControl.add(tab, text=port_lable_text)

        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=15)
        ok_btn = tk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_frame, text=STR_TABLE['save'][self._lang], command=self._save_btn)
        save_btn.pack(side=tk.LEFT)

        abort_btn = tk.Button(btn_frame, text=STR_TABLE['cancel'][self._lang], command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

        self._init_menubar()

    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=STR_TABLE['new'][self._lang], command=self._new_dualPort_cfg)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=STR_TABLE['delete'][self._lang],
                              command=self._del_dualPort_cfg
                              )
        menubar.add_cascade(label="Dual-Port", menu=MenuVerb, underline=0)

    def _new_dualPort_cfg(self, event=None):
        new_cfg = getNew_dualPort_cfg()
        tab = DP_cfg_Tab(self.tabControl, new_cfg, )
        self.tab_list[-1] = tab
        port_lable_text = STR_TABLE['new'][self._lang]
        self.tabControl.add(tab, text=port_lable_text)

    def _del_dualPort_cfg(self, event=None):
        try:
            tab_ind = self.tabControl.index('current')
            ind_tab = self.tabControl.tab('current')
        except tk.TclError:
            pass
        else:
            ind_text = ind_tab['text']
            if ind_text == STR_TABLE['new'][self._lang]:
                del self.tab_list[-1]
            else:
                ind = int(ind_text.replace('Port ', '')[0])
                del self.tab_list[ind]
            self.tabControl.forget(tab_ind)
            self._set_cfg_to_port()
            self._root_win.sysMsg_to_monitor('Info: Dual-Port gelöscht.')

    def _set_cfg_to_port(self):
        self._set_new_port_tab()
        new_cfg = {}
        for k in self.tab_list.keys():
            if k != -1:
                tab = self.tab_list[k]
                cfg = tab.get_cfg_fm_vars()
                if not any((
                        bool(cfg.get('primary_port_id', -1) == -1),
                        bool(cfg.get('secondary_port_id', -1) == -1),
                        bool(cfg.get('primary_port_id', -1) == cfg.get('secondary_port_id', -1))
                )):
                    prim_port_id = cfg.get('primary_port_id', -1)
                    if prim_port_id not in new_cfg.keys():
                        new_cfg[prim_port_id] = cfg

        POPT_CFG.set_dualPort_CFG(new_cfg)
        PORT_HANDLER.set_dualPort_fm_cfg()

    def _save_cfg(self):
        self._set_cfg_to_port()
        POPT_CFG.save_CFG_to_file()

    def _set_new_port_tab(self):
        if -1 not in self.tab_list.keys():
            return
        tab = self.tab_list[-1]
        cfg = tab.get_cfg_fm_vars()
        if not cfg:
            return
        if any((
            bool(cfg.get('primary_port_id', -1) == -1),
            bool(cfg.get('secondary_port_id', -1) == -1),
            bool(cfg.get('primary_port_id', -1) == cfg.get('secondary_port_id', -1))
        )):
            return
        all_dualPorts = PORT_HANDLER.get_all_dualPorts_primary()
        prim_port_id = cfg.get('primary_port_id', -1)
        if prim_port_id in all_dualPorts.keys():
            return
        del self.tab_list[-1]
        index = len(list(self.tab_list.keys()))
        self.tab_list[prim_port_id] = tab
        port_lable_text = 'Port {}'.format(prim_port_id)
        self.tabControl.tab(index, text=port_lable_text)

    def _ok_btn(self):
        self._set_cfg_to_port()
        self.destroy_win()

    def _save_btn(self):
        # self._set_cfg_to_port()
        # self.destroy_win()
        self._save_cfg()

    def _abort_btn(self):
        # self._set_cfg_to_port()
        self.destroy_win()

    def destroy_win(self):
        self._root_win.dualPort_settings_win = None
        self.destroy()
