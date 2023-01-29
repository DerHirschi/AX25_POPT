import time
import tkinter as tk
from tkinter import scrolledtext, Label, Menu, LEFT
import threading
import logging
from ax25.ax25PortHandler import DevDirewolf, MYHEARD, AX25Conn
from ax25.ax25dec_enc import Call
from gui.guiMH import MHWin
from gui.guiDebug import DEBUGwin


LOOP_DELAY = 10        # ms
TEXT_SIZE = 12

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)


class TkMainWin:
    def __init__(self):
        self.axtest_port = DevDirewolf()    # TODO
        self.axtest_port.run_once()
        self.ax25_ports_th = threading.Thread(target=self.ax25ports_th)
        self.ax25_ports_th.start()
        self.win = tk.Tk()
        # self.mh_win: MHWin
        self.debug_win = None       # TODO .. Class
        self.new_conn_win = None
        self.win.title("Py AX.25")
        self.win.geometry("1400x600")
        self.win.columnconfigure(1, minsize=500, weight=2)
        self.win.columnconfigure(2, minsize=200, weight=1)
        self.win.rowconfigure(0, minsize=150, weight=1)
        self.win.rowconfigure(1, minsize=300, weight=1)
        self.win.rowconfigure(2, minsize=30, weight=1)
        self.win.rowconfigure(3, minsize=300, weight=1)


        ##############
        # Menüleiste
        self.menubar = Menu(self.win)
        self.win.config(menu=self.menubar)
        # Menü 1 "Verbindungen"
        self.MenuVerb = Menu(self.menubar)
        self.MenuVerb.add_command(label="Neu", command=self.open_new_conn_win)
        self.MenuVerb.add_command(label="Quit", command=self.win.quit)
        self.menubar.add_cascade(label="Verbindungen", menu=self.MenuVerb)
        # Menü 2 "MH"
        # self.menubar.add_command(label="MH", command=self.MH_win)
        self.menubar.add_command(label="MH", command=self.MH_win)
        # Menü 3 "Tools"
        self.MenuTools = Menu(self.menubar)
        # self.MenuTools.add_command(label="Debug Tool", command=self.DEBUG_win)
        self.menubar.add_cascade(label="Tools", menu=self.MenuTools)
        # Menü 4 "Debug"
        self.menubar.add_command(label="Debug", command=self.DEBUG_win)
        ##############
        # Textfenster
        # Vorschreibfenster
        self.inp_txt = tk.Text(self.win, background='black', foreground='yellow', font=("TkFixedFont", TEXT_SIZE))
        self.inp_txt.grid(row=0, column=1, sticky="nsew")
        # Ausgabe
        self.out_txt = tk.Text(self.win, background='black', foreground='red', font=("TkFixedFont", TEXT_SIZE))
        self.out_txt.grid(row=1, column=1, sticky="nsew")
        # CH Buttons
        self.ch_btn_frame = tk.Frame(self.win, width=500, height=30)
        self.ch_btn_frame.columnconfigure(1, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(2, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(3, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(4, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(5, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(6, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(7, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(8, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(9, minsize=50, weight=1)
        self.ch_btn_frame.columnconfigure(10, minsize=50, weight=1)
        self.ch_btn_frame.grid(row=2, column=1, sticky="nsew")
        self.ch_button1 = tk.Button(self.ch_btn_frame, text=" 1 ", bg="green")
        self.ch_button2 = tk.Button(self.ch_btn_frame, text=" 2 ", bg="red")
        self.ch_button3 = tk.Button(self.ch_btn_frame, text=" 3 ", bg="red")
        self.ch_button4 = tk.Button(self.ch_btn_frame, text=" 4 ", bg="red")
        self.ch_button5 = tk.Button(self.ch_btn_frame, text=" 5 ", bg="red")
        self.ch_button6 = tk.Button(self.ch_btn_frame, text=" 6 ", bg="red")
        self.ch_button7 = tk.Button(self.ch_btn_frame, text=" 7 ", bg="red")
        self.ch_button8 = tk.Button(self.ch_btn_frame, text=" 8 ", bg="red")
        self.ch_button9 = tk.Button(self.ch_btn_frame, text=" 9 ", bg="red")
        self.ch_button10 = tk.Button(self.ch_btn_frame, text=" 10 ", bg="red")
        self.ch_button1.grid(row=1, column=1, sticky="nsew")
        self.ch_button2.grid(row=1, column=2, sticky="nsew")
        self.ch_button3.grid(row=1, column=3, sticky="nsew")
        self.ch_button4.grid(row=1, column=4, sticky="nsew")
        self.ch_button5.grid(row=1, column=5, sticky="nsew")
        self.ch_button6.grid(row=1, column=6, sticky="nsew")
        self.ch_button7.grid(row=1, column=7, sticky="nsew")
        self.ch_button8.grid(row=1, column=8, sticky="nsew")
        self.ch_button9.grid(row=1, column=9, sticky="nsew")
        self.ch_button10.grid(row=1, column=10, sticky="nsew")

        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.win, background='black', foreground='green', font=("TkFixedFont", TEXT_SIZE))
        # frame.grid(column=0, row=0, columnspan=3, rowspan=2)
        self.mon_txt.grid(row=3, column=1, columnspan=2, sticky="nsew")
        #######################
        # SeitenLabel ( TEST )
        self.side_frame = tk.Frame(self.win, width=500, height=30)
        self.side_frame.rowconfigure(0, minsize=100, weight=1)
        self.side_frame.rowconfigure(1, minsize=400, weight=1)
        self.side_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")
        # Seiten Buttons
        self.side_btn_frame = tk.Frame(self.side_frame, width=500, height=30)
        self.side_btn_frame.rowconfigure(0, minsize=100, weight=1)
        self.side_btn_frame.rowconfigure(1, minsize=400, weight=1)
        self.side_btn_frame.columnconfigure(0, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(1, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(2, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(3, minsize=100, weight=1)
        self.side_btn_frame.grid(row=0, column=0, sticky="nsew")
        self.side_btn_frame.rowconfigure(0, minsize=50, weight=1)
        self.side_btn_frame.rowconfigure(1, minsize=50, weight=1)
        # New Conncetion
        self.conn_btn = tk.Button(self.side_btn_frame, text="New Conn", bg="green", command=self.open_new_conn_win)
        self.conn_btn.grid(row=0, column=0, sticky="nsew")
        self.test_btn = tk.Button(self.side_btn_frame, text="Test", bg="yellow")
        self.test_btn.grid(row=1, column=0, sticky="nsew")
        self.test_btn1 = tk.Button(self.side_btn_frame, text="Test2", bg="red")
        self.test_btn1.grid(row=1, column=1, sticky="nsew")

        self.test_lable = Label(self.side_frame, text="1\n2\n3\n4\n5\n6\n7\n8\n", font=("Arial", 15))
        self.test_lable.grid(row=1, column=0)
        #self.test_lable1 = Label(self.side_frame, text="1\n2\n3\n4\n5\n6\n7\n8\n", font=("Arial", 15))
        #self.test_lable1.grid(row=1, column=0)

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
        if self.debug_win is not None:
            self.debug_win: DEBUGwin
            if self.debug_win.is_running:
                self.debug_win.tasker()
            else:
                # self.debug_win.close()
                self.debug_win = None
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
    # New Connection WIN
    def open_new_conn_win(self):
        # TODO
        if self.new_conn_win is None:
            self.new_conn_win = tk.Tk()
            self.new_conn_win.title("New Connection")
            self.new_conn_win.geometry("700x300")
            self.new_conn_win.protocol("WM_DELETE_WINDOW", self.destroy_new_conn_win)
            self.new_conn_win.columnconfigure(0, minsize=200, weight=2)
            self.new_conn_win.columnconfigure(1, minsize=200, weight=1)
            self.new_conn_win.columnconfigure(3, minsize=300, weight=1)
            self.new_conn_win.rowconfigure(0, minsize=100, weight=1)
            self.new_conn_win.rowconfigure(1, minsize=100, weight=1)
            self.new_conn_win.rowconfigure(2, minsize=50, weight=1)
            self.new_conn_win.rowconfigure(3, minsize=50, weight=1)

            call_txt_inp = tk.Text(self.win, background='black', foreground='yellow', font=("TkFixedFont", TEXT_SIZE))
            call_txt_inp.grid(row=0, column=1, sticky="nsew")

            conn_btn = tk.Button(self.new_conn_win, text="Los", bg="green", command=self.open_new_conn_win)
            conn_btn.grid(row=3, column=0, sticky="nsew")


    def destroy_new_conn_win(self):
        self.new_conn_win.destroy()
        self.new_conn_win = None

    # New Connection WIN
    # ##############

    ##############
    # MH WIN
    def MH_win(self):
        """MH WIN"""
        MHWin(MYHEARD)
    # MH WIN ENDE
    ##############

    ##############
    # DEBUG WIN
    def DEBUG_win(self):
        if self.debug_win is None:
            self.debug_win = DEBUGwin(self.axtest_port.connections)
        else:
            if not self.debug_win.is_running:
                self.debug_win = DEBUGwin(self.axtest_port.connections)

    # DEBUG WIN ENDE
    ##############


if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        pass
    print("Ende")
    MYHEARD.save_mh_data()
