import tkinter as tk
from tkinter import ttk

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class BBS_addRuleWinCC(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win)
        self._logTag = "BBS_add_CC_RuleWin> "
        win_width = 500
        win_height = 120
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
        ###########################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ###########################
        self._lang          = POPT_CFG.get_guiCFG_language()
        self._getTabStr     = lambda str_k: get_strTab(str_k, self._lang)
        self._root_win      = root_win
        self._root_win.add_win = self
        self.title(f"{self._getTabStr('new')} CC")
        ##################################################
        self._cc_tab: dict  = self._root_win.get_root_pms_cfg().get('cc_tab', {})
        ##################################################
        self._origin_var    = tk.StringVar(self, value='')
        self._cc_var        = tk.StringVar(self, value='')

        ##################################################
        m_frame = ttk.Frame(main_f)
        m_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=15, pady=7)
        com_box = ttk.Combobox(m_frame, textvariable=self._origin_var, width=20)
        com_box['values'] = list(self._cc_tab.keys())
        com_box.pack(side=tk.LEFT)
        #
        cc_entry = ttk.Entry(m_frame, textvariable=self._cc_var, width=20)
        cc_entry.pack(side=tk.LEFT, padx=12)

        ###########################################
        # BTN
        btn_frame = ttk.Frame(main_f)
        btn_frame.pack(expand=True, fill=tk.X, padx=10, pady=10)
        save_btn  = ttk.Button(btn_frame, text=self._getTabStr('save'),   command=self._save_btn)
        abort_btn = ttk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        save_btn.pack( side=tk.LEFT)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    def _save_btn(self):
        org = self._origin_var.get().upper()
        cc  = self._cc_var.get().upper()
        cc_list = self._cc_tab.get(org, [])
        if cc not in cc_list:
            cc_list.append(cc)
            self._cc_tab[org] = cc_list

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