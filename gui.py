import tkinter as tk
from tkinter import scrolledtext
import threading
from ax25PortHandler import DevDirewolf

LOOP_DELAY = 200        # ms
TEXT_SIZE = 12


class TkMainWin:
    def __init__(self):
        self.axtest_port = DevDirewolf()
        self.axtest_port.run_loop()
        self.mon_th = threading.Thread(target=self.monitor_th)
        self.win = tk.Tk()
        self.win.title("Py AX.25")
        self.win.geometry("1400x600")
        self.win.columnconfigure(1, minsize=500, weight=2)
        self.win.columnconfigure(2, minsize=200, weight=1)

        self.inp_txt = tk.Text(self.win, background='black', foreground='yellow', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(0, minsize=150, weight=1)
        self.inp_txt.grid(row=0, column=1, sticky="nsew")

        self.out_txt = tk.Text(self.win, background='black', foreground='red', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(1, minsize=300, weight=1)
        self.out_txt.grid(row=1, column=1, sticky="nsew")

        self.mon_txt = scrolledtext.ScrolledText(self.win, background='black', foreground='green', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(2, minsize=300, weight=1)
        # frame.grid(column=0, row=0, columnspan=3, rowspan=2)
        self.mon_txt.grid(row=2, column=1, columnspan=2, sticky="nsew")

        self.win.after(LOOP_DELAY, self.tasker)
        self.win.mainloop()

    def tasker(self):
        # print(self.inp_txt.get("1.0", tk.END))
        # self.win.rowconfigure(1, minsize=300 + self.n, weight=1)
        if not self.mon_th.is_alive():
            self.mon_th = threading.Thread(target=self.monitor_th)
            self.mon_th.start()

        self.win.after(LOOP_DELAY, self.tasker)

    def monitor_th(self):
        self.axtest_port.run_loop()
        for el in self.axtest_port.monitor.out_buf:
            self.mon_txt.insert(1.0, el)
        self.axtest_port.monitor.out_buf = []



if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        print("Ende")
