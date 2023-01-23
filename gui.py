import tkinter as tk

LOOP_DELAY = 300        # ms
TEXT_SIZE = 12


class TkMainWin:
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Simple Text Editor")
        self.win.geometry("700x600")
        self.win.columnconfigure(2, minsize=200, weight=1)

        self.inp_txt = tk.Text(self.win, background='black', foreground='yellow', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(0, minsize=150, weight=1)
        self.inp_txt.grid(row=0, column=1, sticky="nsew")

        self.out_txt = tk.Text(self.win, background='black', foreground='red', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(1, minsize=300, weight=1)
        self.out_txt.grid(row=1, column=1, sticky="nsew")

        self.mon_txt = tk.Text(self.win, background='black', foreground='green', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(2, minsize=300, weight=1)
        self.mon_txt.grid(row=2, column=1, sticky="nsew")

        self.win.after(LOOP_DELAY, self.tasker)
        self.win.mainloop()

    def tasker(self):
        # print(self.inp_txt.get("1.0", tk.END))
        # self.win.rowconfigure(1, minsize=300 + self.n, weight=1)
        self.win.after(LOOP_DELAY, self.tasker)


if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        print("Ende")
