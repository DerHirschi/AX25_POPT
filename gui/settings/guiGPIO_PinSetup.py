import tkinter as tk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab, lob_gen


class GPIO_pinSetup(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        win_width = 800
        win_height = 400
        # self.style = root_win.style
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
        # TODO self.title(get_strTab(str_key='settings', lang_index=self._lang))
        #####################################################
        self._root_win = root_win
        #####################################################
        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        ok_btn = tk.Button(btn_frame, text=' OK ', command=self._save_btn)
        ok_btn.pack(side=tk.LEFT)

        abort_btn = tk.Button(btn_frame, text=get_strTab(str_key='cancel', lang_index=self._lang), command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    ######################################################
    def _save_cfg(self):
        pass

    ######################################################
    def _save_btn(self):
        self._save_cfg()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        self._root_win.pin_setup_win = None
        self.destroy()