import logging
import tkinter as tk
from tkinter import scrolledtext, Label, Menu
from ax25.ax25Statistics import MyHeard

logger = logging.getLogger(__name__)
"""
LOOP_DELAY = 10        # ms
TEXT_SIZE = 12
"""


class MHWin:
    def __init__(self, mh):
        self.mh = mh
        self.win = tk.Tk()
        self.win.title("MHEARD")
        self.win.geometry("820x600")
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.menubar = Menu(self.win)
        self.win.config(menu=self.menubar)
        self.menubar.add_command(label="Quit", command=self.close)
        tk.Label(self.win, text="Zeit").grid(row=1, column=0)
        tk.Label(self.win, text="Call").grid(row=1, column=1)
        tk.Label(self.win, text="Packets").grid(row=1, column=2)
        tk.Label(self.win, text="REJ s").grid(row=1, column=3)
        tk.Label(self.win, text="Route").grid(row=1, column=4)
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
            e1 = tk.Entry(self.win)
            a1.grid(row=ind, column=0)
            b1.grid(row=ind, column=1)
            c1.grid(row=ind, column=2)
            d1.grid(row=ind, column=3)
            e1.grid(row=ind, column=4)
            a1.insert(0, ent.last_seen)
            b1.insert(0, ent.own_call)
            c1.insert(0, ent.pac_n)
            d1.insert(0, ent.rej_n)
            ind += 1

    def __del__(self):
        if self.win is not None:
            self.win.destroy()
            self.win = None

    def close(self):
        self.win.destroy()
        self.win = None
