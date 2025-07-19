import tkinter as tk
from tkinter import ttk, Menu
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import DUALPORT_TX_MODE
from cfg.default_config import getNew_dualPort_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class DP_cfg_Tab(ttk.Frame):
    def __init__(self, root_win, dp_settings: dict):
        ttk.Frame.__init__(self, root_win)
        self.pack()
        ##################
        # Port
        port_frame = ttk.Frame(self)
        port_frame.pack(fill=tk.X, padx=5, pady=5)

        port_opt = list(PORT_HANDLER.ax25_ports.keys())
        self._prim_port_var = tk.StringVar(self)
        self._sec_port_var  = tk.StringVar(self)

        prim_port_frame = ttk.Frame(port_frame)
        prim_port_frame.pack(side=tk.LEFT, expand=True)
        prim_port_label = ttk.Label(prim_port_frame, text='Primary-Port: ')
        prim_port_label.pack(side=tk.LEFT)
        self._prim_port_var.set(str(dp_settings.get('primary_port_id', -1)))
        prim_port_opt = [self._prim_port_var.get()] + port_opt
        prim_port = ttk.OptionMenu(prim_port_frame, self._prim_port_var, *prim_port_opt)
        prim_port.pack(side=tk.LEFT)

        sec_port_frame = ttk.Frame(port_frame)
        sec_port_frame.pack(side=tk.LEFT, expand=True)
        sec_port_label = ttk.Label(sec_port_frame, text='Secondary-Port: ')
        sec_port_label.pack(side=tk.LEFT)
        self._sec_port_var.set(str(dp_settings.get('secondary_port_id', -1)))
        sec_port_opt = [self._sec_port_var.get()] + port_opt
        sec_port = ttk.OptionMenu(sec_port_frame, self._sec_port_var, *sec_port_opt)
        sec_port.pack(side=tk.LEFT)

        ##################
        # Options
        opt_frame = ttk.Frame(self)
        opt_frame.pack(fill=tk.Y, padx=5, pady=15, anchor=tk.W)

        self._tx_prim_var = tk.BooleanVar(self, value=bool(dp_settings.get('tx_primary', True)))
        tx_prim = ttk.Checkbutton(opt_frame, text='TX on primary Port', variable=self._tx_prim_var)
        tx_prim.pack(anchor=tk.W)

        self._tx_auto_var = tk.BooleanVar(self, value=bool(dp_settings.get('auto_tx', False)))
        tx_auto = ttk.Checkbutton(opt_frame, text='Auto TX-Port', variable=self._tx_auto_var)
        tx_auto.pack(anchor=tk.W, side=tk.LEFT)
        ################
        # Auto-TX Mode
        mode_opt = list(DUALPORT_TX_MODE.keys())
        self._tx_auto_mode_var = tk.StringVar(self)
        tx_auto_mode = ttk.Frame(opt_frame)
        tx_auto_mode.pack(padx=80)
        tx_auto_mode_label = ttk.Label(tx_auto_mode, text='Auto-TX Mode: ')
        tx_auto_mode_label.pack(side=tk.LEFT)
        self._tx_auto_mode_var.set(mode_opt[dp_settings.get('auto_tx_mode', 0)])
        mode_opt = [self._tx_auto_var.get()] + mode_opt
        tx_auto_mode = ttk.OptionMenu(tx_auto_mode, self._tx_auto_mode_var, *mode_opt)
        tx_auto_mode.pack(side=tk.LEFT)

    def get_cfg_fm_vars(self):
        prim_port = self._prim_port_var.get()
        sec_port = self._sec_port_var.get()
        if prim_port == sec_port:
            return {}
        if prim_port == -1 or sec_port == -1:
            return {}

        return dict(
            tx_primary=bool(self._tx_prim_var.get()),  # TX Primary/Secondary
            auto_tx=bool(self._tx_auto_var.get()),  # Auto TX
            auto_tx_mode=int(DUALPORT_TX_MODE.get(self._tx_auto_mode_var.get(), 0)),  # Auto TX Mode
            primary_port_id=int(prim_port),
            secondary_port_id=int(sec_port)
        )


class DualPortSettingsWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._lang = POPT_CFG.get_guiCFG_language()
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._root_win = root_win
        win_height = 330
        win_width = 600
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        self.title('DualPort-Settings')
        self._root_win.dualPort_settings_win = self
        ########################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ########################################
        new_btn_f = ttk.Frame(main_f)
        new_btn_f.pack(fill=tk.X)
        ttk.Button(new_btn_f,
                   text=self._getTabStr('new'),
                   command= lambda: self._new_dualPort_cfg()
                   ).pack(side=tk.LEFT, padx=10)
        tk.Button(new_btn_f,
                  text=self._getTabStr('delete'),
                  command=lambda :self._del_dualPort_cfg(),
                  bg='red',
                  relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                  highlightthickness=0,
                  ).pack(side=tk.RIGHT, anchor=tk.E, padx=10)
        ########################################
        self.tabControl = ttk.Notebook(main_f)
        self.tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=15)
        # Tab Vars
        self.tab_list: {int: DP_cfg_Tab} = {}

        all_dualPorts = POPT_CFG.get_dualPort_CFG()
        for port_id, dp_cfg in all_dualPorts.items():
            tab = DP_cfg_Tab(self.tabControl, dp_cfg, )
            self.tab_list[port_id] = tab
            port_lable_text = 'Port {}'.format(port_id)
            self.tabControl.add(tab, text=port_lable_text)

        ###########################################
        # BTN
        btn_frame = ttk.Frame(main_f, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=15)
        ok_btn = ttk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)

        save_btn = ttk.Button(btn_frame, text=self._getTabStr('save'), command=self._save_btn)
        save_btn.pack(side=tk.LEFT)

        abort_btn = ttk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

        self._init_menubar()

    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('new'), command= lambda: self._new_dualPort_cfg())
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('delete'),
                             command=lambda :self._del_dualPort_cfg())
        menubar.add_cascade(label="Dual-Port", menu=MenuVerb, underline=0)

    def _new_dualPort_cfg(self):
        new_cfg = getNew_dualPort_cfg()
        tab = DP_cfg_Tab(self.tabControl, new_cfg, )
        self.tab_list[-1] = tab
        port_lable_text = self._getTabStr('new')
        self.tabControl.add(tab, text=port_lable_text)

    def _del_dualPort_cfg(self):
        try:
            tab_ind = self.tabControl.index('current')
            ind_tab = self.tabControl.tab('current')
        except tk.TclError:
            pass
        else:
            ind_text = ind_tab['text']
            if ind_text == self._getTabStr('new'):
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
        POPT_CFG.save_MAIN_CFG_to_file()

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
