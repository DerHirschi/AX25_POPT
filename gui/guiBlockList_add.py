import tkinter as tk
from tkinter import ttk

from cfg.default_config import getNew_BBS_REJ_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class BlockListADD(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win)
        win_width = 420
        win_height = 170
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ###############################
        main_f = ttk.Frame(self)
        main_f.pack(fill='both', expand=True)
        ###############################
        self._lang          = POPT_CFG.get_guiCFG_language()
        self._getTabStr     = lambda str_k: get_strTab(str_k, self._lang)
        self._root_win      = root_win
        # self._root_win.add_win = self
        # self.title(f"Add Reject Hold")
        self.title(self._getTabStr('userdb_newUser'))
        ##################################################
        self._port_var      = tk.StringVar(self, value='all')
        self._call_var      = tk.StringVar(self)
        self._block_opt_var = tk.StringVar(self, value='reject')

        ##################################################
        m_frame = ttk.Frame(main_f)
        m_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=7, pady=7)
        ##################################################
        call_ent_f = ttk.Frame(m_frame)
        call_ent_f.pack(side=tk.LEFT, padx=10)
        ttk.Label(call_ent_f, text='Call: ').pack(side=tk.LEFT)
        ttk.Entry(call_ent_f, textvariable=self._call_var, width=9).pack(side=tk.LEFT)
        ############################
        port_ent_f = ttk.Frame(m_frame)
        port_ent_f.pack(side=tk.LEFT, padx=10)
        self._port_var.set('all')
        opt = [self._port_var.get()] + list(POPT_CFG.get_port_CFGs().keys())
        ttk.Label(port_ent_f, text='Port: ').pack(side=tk.LEFT)
        mopt_m = ttk.OptionMenu(port_ent_f, self._port_var, *opt)
        mopt_m.pack(side=tk.LEFT, padx=2)

        ######
        opt_ent_f = ttk.Frame(m_frame)
        opt_ent_f.pack(side=tk.LEFT, padx=10)
        ttk.Label(opt_ent_f, text='Option: ').pack(side=tk.LEFT)
        self._block_opt_var.set('reject')
        opt = [self._block_opt_var.get()] + ['ignore']
        ropt_m = ttk.OptionMenu(opt_ent_f, self._block_opt_var, *opt)
        ropt_m.pack(side=tk.LEFT, padx=8)
        ###########################################
        # BTN
        btn_frame = ttk.Frame(main_f, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        save_btn  = ttk.Button(btn_frame, text=self._getTabStr('save'),   command=self._save_btn)
        abort_btn = ttk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        save_btn.pack( side=tk.LEFT)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    def _save_btn(self):
        port = self._port_var.get()
        call = self._call_var.get().upper()
        bopt = self._block_opt_var.get()
        if not call:
            return
        opt = {
            'ignore': 1,
            'reject': 2,
        }.get(bopt, 0)
        cfg = POPT_CFG.get_block_list()
        if port == 'all':
            for port in POPT_CFG.get_port_CFGs().keys():
                bl_tab = cfg.get(port, {})
                bl_tab[call] = opt
                cfg[port] = bl_tab
        else:
            bl_tab = cfg.get(int(port), {})
            bl_tab[call] = opt
            cfg[int(port)] = bl_tab
        POPT_CFG.set_block_list(cfg)
        if hasattr(self._root_win, 'update_tabs'):
            self._root_win.update_tabs()
        self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        if hasattr(self._root_win, 'lift'):
            self._root_win.lift()
        self._root_win.add_win = None
        self.destroy()