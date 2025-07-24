import tkinter as tk
from tkinter import ttk
from cfg.constant import VER
from cfg.logger_config import logger


class About(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self.main_cl = main_win
        self.style = main_win.style
        self.win_height = 200
        self.win_width = 700
        self.title("Über")
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.main_cl.main_win.winfo_x()}+"
                      f"{self.main_cl.main_win.winfo_y()}")
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
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
                          # height=1,
                          width=6,
                          command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)

        x = 40
        y = 20
        txt1 = '(P)ython (o)ther (P)acket (T)erminal {}'.format(VER)
        label = ttk.Label(main_f, text=txt1)
        #font1 = label.cget('font')
        #font1 = (font1[0], 13)
        #label.configure(font=font1)
        label.place(x=x, y=y)
        x = 40
        y = 45
        txt1 = 'by MD2SAW'
        label = ttk.Label(main_f, text=txt1)
        label.place(x=x, y=y)
        x = 40
        y = 70
        txt1 = 'Mit Unterstützung der CB-Funk PR-Community'
        label = ttk.Label(main_f, text=txt1)
        label.place(x=x, y=y)
        x = 40
        y = 110
        txt1 = 'GitHub:  https://github.com/DerHirschi/AX25_POPT'
        label = ttk.Label(main_f, text=txt1)
        label.place(x=x, y=y)

    def destroy_win(self):
        self.destroy()
        self.main_cl.settings_win = None

    def tasker(self):
        pass
