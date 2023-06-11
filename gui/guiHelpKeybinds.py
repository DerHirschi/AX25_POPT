import tkinter as tk
from constant import VER


class KeyBindsHelp(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self.main_cl = main_win
        self.style = main_win.style
        self.win_height = 280
        self.win_width = 600
        self.title("Tastaturbelegung")
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.main_cl.main_win.winfo_x()}+"
                      f"{self.main_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        ##########################
        # OK
        ok_bt = tk.Button(self,
                          text="Ok",
                          height=1,
                          width=6,
                          command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)

        tk.Label(self, text='ESC > Neue Verbindung').place(x=50, y=10)
        tk.Label(self, text='ALT + C > Neue Verbindung').place(x=50, y=30)
        tk.Label(self, text='ALT + D > Disconnect').place(x=50, y=50)
        tk.Label(self, text='F1 - F10 > Kanal 1 - 10').place(x=50, y=70)
        tk.Label(self, text='F12 > Monitor').place(x=50, y=90)
        tk.Label(self, text='STRG + plus > Textgröße vergrößern').place(x=50, y=110)
        tk.Label(self, text='STRG + minus > Textgröße verkleinern').place(x=50, y=130)
        tk.Label(self, text='STRG + Pfeil(Links) > Textfenster verkleinern').place(x=50, y=150)
        tk.Label(self, text='STRG + Pfeil(Rechts) > Textfenster vergrößern').place(x=50, y=170)

    def destroy_win(self):
        self.destroy()
        self.main_cl.settings_win = None

    def tasker(self):
        pass
