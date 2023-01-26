import tkinter as tk
from tkinter import scrolledtext, Label, Menu, Scrollbar, RIGHT, Y
import threading
from ax25PortHandler import DevDirewolf, MYHEARD
from ax25Statistics import MyHeard

LOOP_DELAY = 200        # ms
TEXT_SIZE = 12


class TkMainWin:
    def __init__(self):
        self.axtest_port = DevDirewolf()
        self.axtest_port.run_once()
        self.mon_th = threading.Thread(target=self.monitor_th)
        self.win = tk.Tk()
        self.mhwin = None
        self.win.title("Py AX.25")
        self.win.geometry("1400x600")
        self.win.columnconfigure(1, minsize=500, weight=2)
        self.win.columnconfigure(2, minsize=200, weight=1)
        ##############
        # Menüleiste
        self.menubar = Menu(self.win)
        self.win.config(menu=self.menubar)
        self.Menu1 = Menu(self.menubar)
        # self.Menu2 = Menu(self.menubar)
        # self.Menu1.add_command(label="MH", command=self.MH_win)
        self.Menu1.add_command(label="Quit", command=self.win.quit)
        self.menubar.add_cascade(label="Optionen", menu=self.Menu1)
        self.menubar.add_command(label="MH", command=self.MH_win)
        ##############
        # Textfenster
        # Vorschreibfenster
        self.inp_txt = tk.Text(self.win, background='black', foreground='yellow', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(0, minsize=150, weight=1)
        self.inp_txt.grid(row=0, column=1, sticky="nsew")
        # Ausgabe
        self.out_txt = tk.Text(self.win, background='black', foreground='red', font=("Arial", TEXT_SIZE))
        self.win.rowconfigure(1, minsize=300, weight=1)
        self.out_txt.grid(row=1, column=1, sticky="nsew")
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.win, background='black', foreground='green', font=("TkFixedFont", TEXT_SIZE))
        self.win.rowconfigure(2, minsize=300, weight=1)
        # frame.grid(column=0, row=0, columnspan=3, rowspan=2)
        self.mon_txt.grid(row=2, column=1, columnspan=2, sticky="nsew")
        #######################
        # SeitenLabel ( TEST )
        self.test_lable = Label(self.win, text="", font=("Arial", 22))
        self.test_lable.grid(row=0, column=2)

        #######################
        # LOOP
        self.win.after(LOOP_DELAY, self.tasker)
        self.win.mainloop()

    def tasker(self):
        if not self.mon_th.is_alive():
            self.mon_th = threading.Thread(target=self.monitor_th)
            self.mon_th.start()

        self.win.after(LOOP_DELAY, self.tasker)

    def monitor_th(self):
        self.axtest_port.run_once()
        for el in self.axtest_port.monitor.out_buf:
            self.mon_txt.insert(1.0, el)
        if list(self.axtest_port.connections.keys()):
            self.test_lable.config(text=str(list(self.axtest_port.connections.keys())[0]).split(':')[0])  # TEST LABEL
        else:
            self.test_lable.config(text='')  # TEST LABEL

        self.axtest_port.monitor.out_buf = []


    def MH_win(self):
        if self.mhwin is None:
            self.mhwin = tk.Tk()
            self.mhwin.title("MHEARD")
            self.mhwin.geometry("820x600")
            self.mhwin.protocol("WM_DELETE_WINDOW", self.destroy_MH_win)

            #self.mhwin.grid_rowconfigure(0, weight=1)
            #self.mhwin.columnconfigure(0, weight=1)
            """
            frame_main = tk.Frame(self.mhwin, bg="gray", height=30)
            frame_main.config(width=800, height=25)
            frame_main.grid(sticky='nw')
            # Create a frame for the canvas with non-zero row&column weights
            frame_canvas = tk.Frame(frame_main, height=22)
            #frame_canvas.grid(row=0, column=0,  sticky='nw')
            frame_canvas.grid_rowconfigure(0, weight=1)
            frame_canvas.grid_columnconfigure(0, weight=1)
            # Set grid_propagate to False to allow 5-by-5 buttons resizing later
            frame_canvas.grid_propagate(False)

            # Add a canvas in that frame
            canvas = tk.Canvas(frame_main, bg="yellow", height=20)
            canvas.grid(row=0, column=5, sticky="nw")

            # Link a scrollbar to the canvas
            vsb = tk.Scrollbar(frame_main, orient="vertical", command=canvas.yview)
            vsb.grid(row=0, column=0, sticky='ns')
            canvas.configure(yscrollcommand=vsb.set)
            # Set the canvas scrolling region
            canvas.config(scrollregion=canvas.bbox("all"))
            # scrollbar = Scrollbar(self.mhwin)
            # scrollbar.pack(side=RIGHT, fill=Y)
            # frame_canvas.config(width=800, height=25)
            """

            menubar = Menu(self.mhwin)
            self.mhwin.config(menu=menubar)
            menubar.add_command(label="Quit", command=self.destroy_MH_win)

            tk.Label(self.mhwin, text="Zeit").grid(row=1, column=0)
            tk.Label(self.mhwin, text="Call").grid(row=1, column=1)
            tk.Label(self.mhwin, text="Packets").grid(row=1, column=2)
            tk.Label(self.mhwin, text="REJ s").grid(row=1, column=3)
            tk.Label(self.mhwin, text="Route").grid(row=1, column=4)
            ind = 2
            for k in MYHEARD.calls:
                ent: MyHeard
                ent = MYHEARD.calls[k]

                a1 = tk.Entry(self.mhwin)
                b1 = tk.Entry(self.mhwin)
                c1 = tk.Entry(self.mhwin, width=5)
                d1 = tk.Entry(self.mhwin, width=5)
                e1 = tk.Entry(self.mhwin)
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
            # self.mhwin.mainloop()

    def destroy_MH_win(self):
        self.mhwin.destroy()
        self.mhwin = None


if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        pass
    print("Ende")
    MYHEARD.save_mh_data()
