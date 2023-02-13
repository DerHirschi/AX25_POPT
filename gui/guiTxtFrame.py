import time
import tkinter as tk
from tkinter import ttk, scrolledtext, Label, Checkbutton

LOOP_DELAY = 50  # ms
TEXT_SIZE = 15
TEXT_SIZE_STATUS = 11
FONT = "Courier"
TXT_BACKGROUND_CLR = 'black'
TXT_OUT_CLR = 'red'
TXT_INP_CLR = 'yellow'
TXT_INP_CURSOR_CLR = 'white'
TXT_MON_CLR = 'green'


class TxTframe:
    def __init__(self, main_win):

        self.pw = ttk.PanedWindow(orient=tk.VERTICAL)
        self.main_class = main_win
        ###################
        # Output Win
        self.status_frame = tk.Frame(self.pw, width=550, height=320, bd=0, borderwidth=1)
        # self.status_frame.grid(row=1, column=1, sticky="nsew")
        self.status_frame.pack(side=tk.BOTTOM, expand=0)

        self.status_frame.columnconfigure(1, minsize=70, weight=2)  # Name
        self.status_frame.columnconfigure(2, minsize=50, weight=2)  # Status
        self.status_frame.columnconfigure(3, minsize=70, weight=2)  # unACK
        self.status_frame.columnconfigure(4, minsize=70, weight=2)  # VS VR
        self.status_frame.columnconfigure(5, minsize=50, weight=2)  # N2
        self.status_frame.columnconfigure(6, minsize=70, weight=2)  # T1
        self.status_frame.columnconfigure(7, minsize=70, weight=2)  # T3
        self.status_frame.columnconfigure(8, minsize=50, weight=1)  # RX Beep
        self.status_frame.rowconfigure(0, weight=1)  # Stat
        self.status_frame.rowconfigure(1, minsize=20, weight=0)  # Out

        self.in_txt_win = scrolledtext.ScrolledText(self.status_frame,
                                                    background=TXT_BACKGROUND_CLR,
                                                    foreground=TXT_INP_CLR,
                                                    font=(FONT, TEXT_SIZE),
                                                    insertbackground=TXT_INP_CURSOR_CLR,
                                                    height=100, bd=0)
        # self.in_txt_win.insert(tk.END, "Inp")
        self.in_txt_win.grid(row=0, column=0, columnspan=10, sticky="nsew")
        ##############
        # Status Frame
        self.status_name = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_name.grid(row=1, column=1, sticky="nsew")

        self.status_status = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_status.grid(row=1, column=2, sticky="nsew")

        self.status_unack = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_unack.grid(row=1, column=3, sticky="nsew")

        self.status_vs = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_vs.grid(row=1, column=4, sticky="nsew")

        self.status_n2 = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_n2.grid(row=1, column=5, sticky="nsew")

        self.status_t1 = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_t1.grid(row=1, column=6, sticky="nsew")
        self.status_t3 = Label(self.status_frame, text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_t3.grid(row=1, column=7, sticky="nsew")
        self.rx_beep_option = tk.IntVar()
        Checkbutton(self.status_frame, text="RX-BEEP", variable=self.rx_beep_option).grid(row=1, column=8,
                                                                                          sticky="nsew")
        ####################
        # Vorschreibfenster
        self.out_txt_win = scrolledtext.ScrolledText(self.pw, background=TXT_BACKGROUND_CLR,
                                                     foreground=TXT_OUT_CLR,
                                                     font=(FONT, TEXT_SIZE),
                                                     height=100, bd=0, borderwidth=1)

        # self.out_txt_win.insert(tk.END, "OUT")
        # self.out_txt.pack(side=tk.TOP)


        self.status_frame.pack(side=tk.BOTTOM)

        #############
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.pw,
                                                 background=TXT_BACKGROUND_CLR,
                                                 foreground=TXT_MON_CLR,
                                                 font=(FONT, TEXT_SIZE),
                                                 height=100, bd=0, borderwidth=1)
        # self.mon_txt.insert(tk.END, "MON")
        self.mon_txt.pack(side=tk.BOTTOM)
        # paned window

        self.pw.add(self.status_frame, weight=1)
        # self.pw.paneconfig(self.status_frame, height=40)
        self.pw.add(self.out_txt_win, weight=1)

        # self.pw.add(self.out_txt, weight=2)
        self.pw.add(self.mon_txt, weight=1)

        # place the panedwindow on the root window
        self.pw.pack(fill=tk.BOTH, expand=False)
        self.pw.grid(row=2, column=0, sticky="nsew")

    def update_status_win(self):
        """
        Main Win
        Debug WIN
        """
        text = ''
        station = self.main_class.get_conn(self.main_class.channel_index)
        if station:
            dest_call = station.ax25_out_frame.to_call.call_str
            via_calls = ''
            for via in station.ax25_out_frame.via_calls:
                # via: Call
                via_calls += via.call_str + ' '
            status = station.zustand_tab[station.zustand_exec.stat_index][1]
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
            digi_call = station.my_digi_call
            self.status_name.configure(text=dest_call)
            status_bg = {
                'ENDE': 'red',
                'FREI': 'orange',
                'AUFBAU': 'CadetBlue1',
                'ABBAU': 'OrangeRed',
                'BEREIT': 'green',
                'REJ': 'yellow',
                'FINAL': 'LightYellow',
            }[status]
            self.status_status.configure(text=status, bg=status_bg)
            if len(station.tx_buf_unACK.keys()):
                self.status_unack.configure(bg='yellow')
            else:
                self.status_unack.configure(bg='green')
            self.status_unack.configure(text='unACK: {}'.format(len(station.tx_buf_unACK.keys())))
            self.status_vs.configure(text='VS/VR: {}/{}'.format(vs, vr))
            if n2 > 4:
                self.status_n2.configure(bg='yellow')
            elif n2 > 10:
                self.status_n2.configure(bg='orange')
            else:
                self.status_n2.configure(bg='grey80')
            self.status_n2.configure(text='N2: {}'.format(n2))
            self.status_t1.configure(text='T1: {}'.format(t1))
            self.status_t3.configure(text='T3: {}'.format(t3))
            """
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
                   'SendRaw: {}\n' \
                   'TEST_OUT0: {}\n' \
                   'TEST_OUT1: {}\n' \
                   'Fail: {} - OK0: {} - OK1: {}'.format(
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
                    len_txraw_buf,
                    len(TEST_OUT0),
                    len(TEST_OUT1),
                    TEST_FAIL_cnt,
                    TEST_cnt_0,
                    TEST_cnt_1
                                    )
            """

        else:
            self.status_name.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_status.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_unack.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_vs.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_n2.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_t1.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_t3.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
