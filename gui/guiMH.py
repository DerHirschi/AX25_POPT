import logging
import tkinter as tk
from tkinter import Menu
from ax25.ax25Statistics import MyHeard
# import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class MHWin:
    def __init__(self, glb_mh):
        self.mh = glb_mh
        self.win = tk.Tk()
        self.win.title("MHEARD")
        self.win.geometry("1250x700")
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.win.attributes("-topmost", True)
        self.menubar = Menu(self.win)
        self.win.config(menu=self.menubar)
        self.menubar.add_command(label="Quit", command=self.close)
        self.menubar.add_command(label="Port-Statistik", command=glb_mh.port_statistik_DB.plot_test_graph)
        tk.Label(self.win, text="Zeit").grid(row=1, column=0, padx=10)
        tk.Label(self.win, text="Call").grid(row=1, column=1)
        tk.Label(self.win, text="Packets").grid(row=1, column=2)
        tk.Label(self.win, text="REJ s").grid(row=1, column=3)
        tk.Label(self.win, text="Route").grid(row=1, column=4)
        tk.Label(self.win, text="AXIP").grid(row=1, column=5)

        self.update_mh()

    def update_mh(self):

        ind = 2
        for k in self.mh.calls:
            ent: MyHeard
            ent = self.mh.calls[k]

            a1 = tk.Entry(self.win)
            b1 = tk.Entry(self.win)
            c1 = tk.Entry(self.win, width=5)
            d1 = tk.Entry(self.win, width=5)
            e1 = tk.Entry(self.win, width=25)
            f1 = tk.Entry(self.win, width=20)
            a1.grid(row=ind, column=0, padx=10)
            b1.grid(row=ind, column=1)
            c1.grid(row=ind, column=2)
            d1.grid(row=ind, column=3)
            e1.grid(row=ind, column=4)
            f1.grid(row=ind, column=5)
            a1.insert(0, ent.last_seen)
            b1.insert(0, ent.own_call)
            c1.insert(0, ent.pac_n)
            d1.insert(0, ent.rej_n)
            e1.insert(0, ent.route)

            if ent.axip_add[1]:
                axip_str = '{} - {}'.format(ent.axip_add[0], ent.axip_add[1])
            else:
                axip_str = ''
            f1.insert(0, axip_str)
            ind += 1

    def __del__(self):
        if self.win is not None:
            self.win.destroy()
            self.win = None

    def close(self):
        self.win.destroy()
        self.win = None
