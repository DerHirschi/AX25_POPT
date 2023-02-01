import time
import tkinter as tk
from tkinter import scrolledtext, Label, Menu
from ax25.ax25PortHandler import AX25Conn
from ax25.ax25dec_enc import Call
LOOP_DELAY = 10


class DEBUGwin:
    def __init__(self, conn: {str: AX25Conn}):
        super(DEBUGwin, self).__init__()
        self.CONN_IND = 0
        self.is_running = True
        self.connections = conn
        self.win = tk.Tk()
        self.win.title("DEBUGGING")
        self.win.geometry("800x800")
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.win.columnconfigure(0, minsize=300, weight=1)
        # self.win.columnconfigure(1, minsize=200, weight=1)
        self.win.rowconfigure(0, minsize=200, weight=1)
        # self.win.rowconfigure(1, minsize=200, weight=1)

        self.stat_frm = Label(self.win, text="", font=("Arial", 15))
        self.stat_frm.grid(row=0, column=0)
        self.update_status_win()
        #######################
        # LOOP
        self.win.after(LOOP_DELAY, self.tasker)
        # self.win.mainloop()

    def __del__(self):
        if self.win is not None:
            self.win.destroy()
            self.win = None

    def close(self):
        self.win.destroy()
        self.is_running = False
        self.win = None

    def tasker(self):       # MAINLOOP
        if self.is_running:
            self.update_status_win()
        # self.update_status_win()
        # self.win.after(LOOP_DELAY, self.tasker)

    def update_status_win(self):
        """
        Main Win
        Debug WIN
        """
        text = ''
        if len(list(self.connections.keys())) > 1:
            station: AX25Conn
            station = self.connections[list(self.connections.keys())[1]]
            dest_call = station.ax25_out_frame.to_call.call_str
            via_calls = ''
            for via in station.ax25_out_frame.via_calls:
                via: Call
                via_calls += via.call_str + ' '
            status = station.zustand_tab[station.zustand_ind][1]
            uid = station.ax25_out_frame.addr_uid
            n2 = station.n2
            t1 = max(0, int(station.t1 - time.time()))
            t2 = max(0, int(station.t2 - time.time()))
            t3 = max(0, int(station.t3 - time.time()))
            vr, vs = station.vr, station.vs
            nr, ns = station.rx_buf_last_frame.ctl_byte.nr, station.rx_buf_last_frame.ctl_byte.ns
            noACK_buf = str(list(station.tx_buf_unACK.keys()))[1:-1]
            if station.debugvar_len_out_buf:
                station.debugvar_len_out_buf = 0
            send_buf_len = int(station.debugvar_len_out_buf)
            len_tx2snd_buf = len(station.tx_buf_2send)
            len_txraw_buf = len(station.tx_buf_rawData)

            text = '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   'VR: {} - VS: {} - N2: {}\n' \
                   'NR: {} - NS: {}\n' \
                   'T1: {}\nT2: {}\nT3 {}\n' \
                   'noACK: {}\n' \
                   'old2Send: {}\n' \
                   '2Send: {}\n' \
                   'SendRaw: {}\n'.format(
                    dest_call,
                    via_calls,
                    status,
                    uid,
                    vr, vs, n2,
                    nr, ns,
                    t1, t2, t3,
                    noACK_buf,
                    send_buf_len,
                    len_tx2snd_buf,
                    len_txraw_buf
                                         )

        self.stat_frm.config(text=text)  # Debug LABEL



