import time
import tkinter as tk
from tkinter import scrolledtext, Label, Menu, Scrollbar, RIGHT, Y
import threading
from ax25PortHandler import DevDirewolf, MYHEARD, AX25Conn
from ax25dec_enc import Call
from ax25Statistics import MyHeard

LOOP_DELAY = 10        # ms
TEXT_SIZE = 12


class TkMainWin:
    def __init__(self):
        self.axtest_port = DevDirewolf()
        self.axtest_port.run_once()
        self.ax25_ports_th = threading.Thread(target=self.ax25ports_th)
        self.win = tk.Tk()
        self.mh_win = None          # TODO .. Class
        self.debug_win = None       # TODO .. Class
        self.win.title("Py AX.25")
        self.win.geometry("1400x600")
        self.win.columnconfigure(1, minsize=500, weight=2)
        self.win.columnconfigure(2, minsize=200, weight=1)
        ##############
        # Menüleiste
        self.menubar = Menu(self.win)
        self.win.config(menu=self.menubar)
        # Menü 1 "Verbindungen"
        self.MenuVerb = Menu(self.menubar)
        self.MenuVerb.add_command(label="Quit", command=self.win.quit)
        self.menubar.add_cascade(label="Verbindungen", menu=self.MenuVerb)
        # Menü 2 "MH"
        self.menubar.add_command(label="MH", command=self.MH_win)
        # Menü 3 "Tools"
        self.MenuTools = Menu(self.menubar)
        self.MenuTools.add_command(label="Debug Tool", command=self.DEBUG_win)
        self.menubar.add_cascade(label="Tools", menu=self.MenuTools)
        ##############
        # Textfenster
        # Vorschreibfenster
        self.inp_txt = tk.Text(self.win, background='black', foreground='yellow', font=("TkFixedFont", TEXT_SIZE))
        self.win.rowconfigure(0, minsize=150, weight=1)
        self.inp_txt.grid(row=0, column=1, sticky="nsew")
        # Ausgabe
        self.out_txt = tk.Text(self.win, background='black', foreground='red', font=("TkFixedFont", TEXT_SIZE))
        self.win.rowconfigure(1, minsize=300, weight=1)
        self.out_txt.grid(row=1, column=1, sticky="nsew")
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.win, background='black', foreground='green', font=("TkFixedFont", TEXT_SIZE))
        self.win.rowconfigure(2, minsize=300, weight=1)
        # frame.grid(column=0, row=0, columnspan=3, rowspan=2)
        self.mon_txt.grid(row=2, column=1, columnspan=2, sticky="nsew")
        #######################
        # SeitenLabel ( TEST )
        self.test_lable = Label(self.win, text="", font=("Arial", 15))
        self.test_lable.grid(row=1, column=2)

        #######################
        # LOOP
        self.win.after(LOOP_DELAY, self.tasker)
        self.win.mainloop()

    def tasker(self):       # MAINLOOP
        if not self.ax25_ports_th.is_alive():
            self.ax25_ports_th = threading.Thread(target=self.ax25ports_th)
            self.ax25_ports_th.start()
        self.update_mon()
        self.update_status_win()
        self.win.after(LOOP_DELAY, self.tasker)

    #################
    # Main Win
    # - Main Win & Debug Win
    def update_mon(self):
        """
        Main Win
        Debug WIN
        """
        if list(self.axtest_port.connections.keys()):
            k = list(self.axtest_port.connections.keys())[0]
            conn = self.axtest_port.connections[k]
            out = str(conn.rx_buf_rawData.decode('UTF-8', 'ignore')).replace('\r', '\n').replace('\r\n', '\n').replace('\n\r', '\n')
            conn.rx_buf_rawData = b''
            self.out_txt.insert(1.0, out)

        for el in self.axtest_port.monitor.out_buf:
            self.mon_txt.insert(1.0, el)

        self.axtest_port.monitor.out_buf = []

    # - Main Win & Debug Win
    def update_status_win(self, window=None):
        """
        Main Win
        Debug WIN
        """
        text = ''
        if list(self.axtest_port.connections.keys()):
            station: AX25Conn
            station = self.axtest_port.connections[list(self.axtest_port.connections.keys())[0]]
            dest_call = station.ax25_out_frame.to_call.call_str
            via_calls = ''
            for via in station.ax25_out_frame.via_calls:
                via: Call
                via_calls += via.call_str + ' '
            status = station.zustand_exec.flag
            n2 = station.n2
            t1 = max(0, int(station.t1 - time.time()))
            t2 = max(0, int(station.t2 - time.time()))
            t3 = max(0, int(station.t3 - time.time()))
            ns, vs = station.vr, station.vs
            noACK_buf = str(list(station.tx_buf_unACK.keys()))[1:-1]
            if station.debugvar_len_out_buf:
                station.debugvar_len_out_buf = 0
            send_buf_len = int(station.debugvar_len_out_buf)

            text = '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   'NS: {} - VS: {} - N2: {}\n' \
                   'T1: {}\nT2: {}\nT3 {}\n' \
                   'noACK: {}\n' \
                   'Send: {}'.format(
                    dest_call,
                    via_calls,
                    status,
                    ns, vs, n2,
                    t1, t2, t3,
                    noACK_buf,
                    send_buf_len
                                    )
        if window is None:
            self.test_lable.config(text=text)  # Debug LABEL
        else:
            window.config(text=text)  # Debug LABEL

    # Main Win ENDE
    #################
    def ax25ports_th(self):
        """Proces AX.25 Shit"""
        self.axtest_port.run_once()

    ##############
    # MH WIN
    def MH_win(self):
        """MH WIN"""
        if self.mh_win is None:
            self.mh_win = tk.Tk()
            self.mh_win.title("MHEARD")
            self.mh_win.geometry("820x600")
            self.mh_win.protocol("WM_DELETE_WINDOW", self.destroy_MH_win)

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

            menubar = Menu(self.mh_win)
            self.mh_win.config(menu=menubar)
            menubar.add_command(label="Quit", command=self.destroy_MH_win)

            tk.Label(self.mh_win, text="Zeit").grid(row=1, column=0)
            tk.Label(self.mh_win, text="Call").grid(row=1, column=1)
            tk.Label(self.mh_win, text="Packets").grid(row=1, column=2)
            tk.Label(self.mh_win, text="REJ s").grid(row=1, column=3)
            tk.Label(self.mh_win, text="Route").grid(row=1, column=4)
            ind = 2
            for k in MYHEARD.calls:
                ent: MyHeard
                ent = MYHEARD.calls[k]

                a1 = tk.Entry(self.mh_win)
                b1 = tk.Entry(self.mh_win)
                c1 = tk.Entry(self.mh_win, width=5)
                d1 = tk.Entry(self.mh_win, width=5)
                e1 = tk.Entry(self.mh_win)
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
        self.mh_win.destroy()
        self.mh_win = None
    # MH WIN ENDE
    ##############

    ##############
    # DEBUG WIN
    def DEBUG_win(self):
        self.debug_win = tk.Tk()
        self.debug_win.title("DEBUGGING")
        self.debug_win.geometry("1200x800")
        self.debug_win.protocol("WM_DELETE_WINDOW", self.destroy_DEBUG_win)
        self.debug_win.columnconfigure(0, minsize=500, weight=2)
        self.debug_win.columnconfigure(1, minsize=200, weight=1)
        self.debug_win.rowconfigure(0, minsize=300, weight=1)
        self.debug_win.rowconfigure(1, minsize=150, weight=1)

    def destroy_DEBUG_win(self):
        self.debug_win.destroy()
        self.debug_win = None
    # DEBUG WIN ENDE
    ##############

if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        pass
    print("Ende")
    MYHEARD.save_mh_data()
