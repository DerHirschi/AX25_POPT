import tkinter as tk
from tkinter import scrolledtext, Label, Menu
from ax25.ax25PortHandler import AX25Conn


class DEBUGwin:
    def __init__(self, conn: AX25Conn):
        self.connection = conn
        self.win = tk.Tk()
        self.win.title("DEBUGGING")
        self.win.geometry("1200x800")
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.win.columnconfigure(0, minsize=500, weight=2)
        self.win.columnconfigure(1, minsize=200, weight=1)
        self.win.rowconfigure(0, minsize=300, weight=1)
        self.win.rowconfigure(1, minsize=150, weight=1)

    def __del__(self):
        if self.win is not None:
            self.win.destroy()
            self.win = None

    def close(self):
        self.win.destroy()
        self.win = None
