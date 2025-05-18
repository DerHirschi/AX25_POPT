import tkinter as tk
from tkinter import ttk

from cfg.default_config import getNew_BBS_REJ_cfg
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class BBS_addRuleWinHold(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win)
        self._logTag = "BBS_add_RH_RuleWin> "
        win_width = 970
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
            pass
        self.lift()
        ###############################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ###############################
        self._lang          = POPT_CFG.get_guiCFG_language()
        self._getTabStr     = lambda str_k: get_strTab(str_k, self._lang)
        self._root_win      = root_win
        self._root_win.add_win = self
        # self.title(f"Add Reject Hold")
        self.title(f"{self._getTabStr('new')} Reject/Hold")
        ##################################################
        self._RH_opt_var    = tk.StringVar(self, value='H')
        self._msg_typ_var   = tk.StringVar(self, value='B')
        self._from_var      = tk.StringVar(self)
        self._to_var        = tk.StringVar(self)
        self._via_var       = tk.StringVar(self)
        self._bid_var       = tk.StringVar(self)
        self._msg_len_var   = tk.StringVar(self)
        ##################################################
        m_frame  = ttk.Frame(main_f)
        m_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=7, pady=7)
        self._msg_typ_var.set('B')
        opt = [self._msg_typ_var.get()] + ['B', 'P']
        mopt_m = ttk.OptionMenu(m_frame, self._msg_typ_var, *opt)
        mopt_m.pack(side=tk.LEFT, padx=8)
        ######
        from_ent_f = ttk.Frame(m_frame)
        from_ent_f.pack(side=tk.LEFT, padx=4)
        ttk.Label(from_ent_f, text='From: ').pack(side=tk.LEFT)
        ttk.Entry(from_ent_f, textvariable=self._from_var, width=9).pack(side=tk.LEFT)
        ######
        from_ent_f = tk.Frame(m_frame)
        from_ent_f.pack(side=tk.LEFT, padx=4)
        ttk.Label(from_ent_f, text='Via: ').pack(side=tk.LEFT)
        ttk.Entry(from_ent_f, textvariable=self._via_var, width=9).pack(side=tk.LEFT)
        ######
        from_ent_f = ttk.Frame(m_frame)
        from_ent_f.pack(side=tk.LEFT, padx=4)
        ttk.Label(from_ent_f, text='To: ').pack(side=tk.LEFT)
        ttk.Entry(from_ent_f, textvariable=self._to_var, width=9).pack(side=tk.LEFT)
        ######
        from_ent_f = ttk.Frame(m_frame)
        from_ent_f.pack(side=tk.LEFT, padx=4)
        ttk.Label(from_ent_f, text='BID: ').pack(side=tk.LEFT)
        ttk.Entry(from_ent_f, textvariable=self._bid_var, width=9).pack(side=tk.LEFT)
        ######
        from_ent_f = ttk.Frame(m_frame)
        from_ent_f.pack(side=tk.LEFT, padx=4)
        ttk.Label(from_ent_f, text='MaxLen: ').pack(side=tk.LEFT)
        ttk.Entry(from_ent_f, textvariable=self._msg_len_var, width=9).pack(side=tk.LEFT)
        ##########
        self._RH_opt_var.set('H')
        opt = [self._RH_opt_var.get()] + ['R', 'H']
        ropt_m = ttk.OptionMenu(m_frame, self._RH_opt_var, *opt)
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
        rej_hold_ent = getNew_BBS_REJ_cfg()
        try:
            msg_len = int(self._msg_len_var.get())
        except ValueError:
            msg_len = 0
        msg_typ     = str(self._msg_typ_var.get()).upper().replace(' ', '')
        from_call   = str(self._from_var.get()).upper().replace(' ', '')
        via         = str(self._via_var.get()).upper().replace(' ', '')
        to_call     = str(self._to_var.get()).upper().replace(' ', '')
        bid         = str(self._bid_var.get()).upper().replace(' ', '')
        r_h         = str(self._RH_opt_var.get()).upper().replace(' ', '')
        if all((
            not from_call,
            not via,
            not to_call,
            not bid,
            not msg_len,
        )):
            return

        rej_hold_ent.update(
            dict(
                msg_typ=        msg_typ,
                from_call=      from_call,
                via=            via,
                to_call=        to_call,
                bid=            bid,
                msg_len=        msg_len,
                r_h=            r_h,
            )
        )
        pms_cfg: dict = self._root_win.get_root_pms_cfg()
        reject_tab = pms_cfg.get('reject_tab', [])
        if type(reject_tab) != list:
            reject_tab = list()
        if rej_hold_ent in reject_tab:
            return
        reject_tab.append(rej_hold_ent)
        # print(reject_tab)
        pms_cfg['reject_tab'] = reject_tab

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