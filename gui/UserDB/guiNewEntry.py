import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import validate_ax25Call
from fnc.str_fnc import get_strTab


class GUINewUserEntry(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        win_width = 380
        win_height = 110
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.attributes("-topmost", True)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._lang = POPT_CFG.get_guiCFG_language()
        self.title(get_strTab(str_key='userdb_newUser', lang_index=self._lang))
        ################################################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ################################################################
        self._root_win = root_win
        self._ent_var = tk.StringVar(self, value='')

        frame1 = ttk.Frame(main_f)
        frame1.pack(expand=False, fill=tk.X, padx=30, pady=10)
        self._call_ent = ttk.Entry(frame1, textvariable=self._ent_var, width=10)
        self._call_ent.pack(expand=False, fill=tk.X)
        ###########################################
        # BTN
        btn_frame = ttk.Frame(main_f, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        ok_btn = ttk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)

        abort_btn = ttk.Button(btn_frame, text=get_strTab(str_key='cancel', lang_index=self._lang),
                              command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    def _ok_btn(self):
        inp = self._ent_var.get().upper()
        if not validate_ax25Call(inp):
            self._call_ent.focus()
            return
        user_db = self._root_win.get_UserDB()
        db_ent = user_db.get_entry(inp, add_new=True)
        if db_ent is None:
            self._call_ent.focus()
            return
        self._root_win.set_newUser_ent(db_entry=db_ent)
        self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        self._root_win.NewUser_ent_win = None
        self.destroy()