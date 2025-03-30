import tkinter as tk
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE

class KeyBindsHelp(tk.Toplevel):
    def __init__(self, main_win):
        self._lang = POPT_CFG.get_guiCFG_language()
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self.main_cl = main_win
        self.style = main_win.style
        self.win_height = 280
        self.win_width = 600
        self.title(STR_TABLE['key_title'][self._lang])
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
            pass
        self.lift()
        ##########################
        # OK
        ok_bt = tk.Button(self,
                          text="Ok",
                          height=1,
                          width=6,
                          command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)

        tk.Label(self, text=STR_TABLE['key_esc'][self._lang]).place(x=50, y=10)
        tk.Label(self, text=STR_TABLE['key_altc'][self._lang]).place(x=50, y=30)
        tk.Label(self, text=STR_TABLE['key_altd'][self._lang]).place(x=50, y=50)
        tk.Label(self, text=STR_TABLE['key_f'][self._lang]).place(x=50, y=70)
        tk.Label(self, text=STR_TABLE['key_f12'][self._lang]).place(x=50, y=90)
        tk.Label(self, text=STR_TABLE['key_strgplus'][self._lang]).place(x=50, y=110)
        tk.Label(self, text=STR_TABLE['key_strgminus'][self._lang]).place(x=50, y=130)
        tk.Label(self, text=STR_TABLE['key_shiftf'][self._lang]).place(x=50, y=150)
        # tk.Label(self, text='STRG + Pfeil(Links) > Textfenster verkleinern').place(x=50, y=150)
        # tk.Label(self, text='STRG + Pfeil(Rechts) > Textfenster vergrößern').place(x=50, y=170)

    def destroy_win(self):
        self.destroy()
        self.main_cl.settings_win = None

    def tasker(self):
        pass
