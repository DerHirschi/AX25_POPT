import tkinter as tk
from tkinter import ttk

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class KeyBindsHelp(tk.Toplevel):
    def __init__(self, main_win):
        self._lang = POPT_CFG.get_guiCFG_language()
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self.main_cl    = main_win
        self.style      = main_win.style
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.win_height = 280
        self.win_width  = 600
        self.title(self._getTabStr('key_title'))
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.main_cl.main_win.winfo_x()}+"
                      f"{self.main_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ##########################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ##########################
        # OK
        ok_bt = ttk.Button(main_f,
                          text="Ok",
                          width=6,
                          command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)

        ttk.Label(main_f, text=self._getTabStr('key_esc')).place(x=50, y=10)
        ttk.Label(main_f, text=self._getTabStr('key_altc')).place(x=50, y=30)
        ttk.Label(main_f, text=self._getTabStr('key_altd')).place(x=50, y=50)
        ttk.Label(main_f, text=self._getTabStr('key_f')).place(x=50, y=70)
        ttk.Label(main_f, text=self._getTabStr('key_f12')).place(x=50, y=90)
        ttk.Label(main_f, text=self._getTabStr('key_strgplus')).place(x=50, y=110)
        ttk.Label(main_f, text=self._getTabStr('key_strgminus')).place(x=50, y=130)
        ttk.Label(main_f, text=self._getTabStr('key_shiftf')).place(x=50, y=150)
        # tk.Label(self, text='STRG + Pfeil(Links) > Textfenster verkleinern').place(x=50, y=150)
        # tk.Label(self, text='STRG + Pfeil(Rechts) > Textfenster vergrößern').place(x=50, y=170)

    def destroy_win(self):
        self.destroy()
        self.main_cl.settings_win = None

    def tasker(self):
        pass
