import tkinter as tk
from config_station import VER


class About(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self.main_cl = main_win
        self.style = main_win.style
        self.win_height = 200
        self.win_width = 700
        self.title("Über")
        self.geometry("{}x{}".format(self.win_width, self.win_height))
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

        _x = 40
        _y = 20
        _txt1 = '(P)ython (o)ther (P)acket (T)erminal {}'.format(VER)
        _label = tk.Label(self, text=_txt1)
        _font1 = _label.cget('font')
        _font1 = (_font1[0], 13)
        _label.configure(font=_font1)
        _label.place(x=_x, y=_y)
        _x = 40
        _y = 45
        _txt1 = 'by MD2SAW'
        _label = tk.Label(self, text=_txt1)
        _label.place(x=_x, y=_y)
        _x = 40
        _y = 70
        _txt1 = 'Mit Unterstützung der CB-Funk PR-Community'
        _label = tk.Label(self, text=_txt1)
        _label.place(x=_x, y=_y)
        _x = 40
        _y = 110
        _txt1 = 'GitHub:  https://github.com/DerHirschi/AX25_POPT'
        _label = tk.Label(self, text=_txt1)
        _label.place(x=_x, y=_y)

    def destroy_win(self):
        self.destroy()
        self.main_cl.settings_win = None
