import time
import tkinter as tk
from tkinter import ttk, scrolledtext, Label, Checkbutton

from constant import ENCODINGS, STATION_TYPS

# from gui.guiMainNew import TkMainWin

#LOOP_DELAY = 50  # ms
#TEXT_SIZE = 15
FONT = "Courier"
TXT_BACKGROUND_CLR = 'black'
TXT_OUT_CLR = 'red'
TXT_INP_CLR = 'yellow'
TXT_INP_CURSOR_CLR = 'white'
TXT_MON_CLR = 'green'
STAT_BAR_CLR = 'grey60'
STAT_BAR_TXT_CLR = 'black'
TEXT_SIZE_STATUS = 11
FONT_STAT_BAR = 'Arial'


class TxTframe:
    def __init__(self, main_win):

        self.pw = ttk.PanedWindow(orient=tk.VERTICAL)
        self.main_class = main_win
        self.text_size = main_win.text_size
        self.mon_txt_height = 0
        self.out_txt_height = 0
        self.inp_txt_height = 0
        # self.mon_btn: tk.Button = main_win.mon_btn
        ###################
        # Input Win
        self.status_frame = tk.Frame(self.pw, width=500, height=320, bd=0, borderwidth=0, bg=STAT_BAR_CLR)
        # self.status_frame.grid(row=1, column=1, sticky="nsew")
        self.status_frame.pack(side=tk.BOTTOM, expand=0)

        self.status_frame.columnconfigure(1, minsize=60, weight=2)  # Name
        self.status_frame.columnconfigure(2, minsize=40, weight=3)  # Status
        self.status_frame.columnconfigure(3, minsize=40, weight=4)  # unACK
        self.status_frame.columnconfigure(4, minsize=40, weight=4)  # VS VR
        self.status_frame.columnconfigure(5, minsize=20, weight=5)  # N2
        self.status_frame.columnconfigure(6, minsize=20, weight=5)  # T1
        self.status_frame.columnconfigure(7, minsize=20, weight=5)  # T1
        self.status_frame.columnconfigure(8, minsize=20, weight=5)  # T2
        self.status_frame.columnconfigure(9, minsize=20, weight=5)  # T3
        self.status_frame.columnconfigure(10, minsize=50, weight=1)  # RX Beep
        self.status_frame.columnconfigure(11, minsize=20, weight=1)  # TimeStamp
        self.status_frame.rowconfigure(0, weight=1)  # Stat
        self.status_frame.rowconfigure(1, minsize=20, weight=0)  # Out

        self.in_txt_win = scrolledtext.ScrolledText(self.status_frame,
                                                    background=TXT_BACKGROUND_CLR,
                                                    foreground=TXT_INP_CLR,
                                                    font=(FONT, self.text_size),
                                                    insertbackground=TXT_INP_CURSOR_CLR,
                                                    height=100, bd=0,)
        self.in_txt_win.tag_config("send", foreground="green2")

        # self.in_txt_win.insert(tk.END, "Inp")
        self.in_txt_win.grid(row=0, column=0, columnspan=12, sticky="nsew")
        ##############
        # Status Frame
        self.status_name = Label(self.status_frame, text="", font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                 foreground=STAT_BAR_TXT_CLR,
                                 bg=STAT_BAR_CLR)
        self.status_name.grid(row=1, column=1, sticky="nsew")

        self.status_status = Label(self.status_frame, text="",
                                   font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                   bg=STAT_BAR_CLR,
                                   foreground=STAT_BAR_TXT_CLR)
        self.status_status.grid(row=1, column=2, sticky="nsew")

        self.status_unack = Label(self.status_frame, text="",
                                  foreground=STAT_BAR_TXT_CLR,
                                  font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                  bg=STAT_BAR_CLR)
        self.status_unack.grid(row=1, column=3, sticky="nsew")

        self.status_vs = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_vs.grid(row=1, column=4, sticky="nsew")

        self.status_n2 = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_n2.grid(row=1, column=7, sticky="nsew")

        self.status_t1 = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_t1.grid(row=1, column=8, sticky="nsew")
        # PARM T2
        self.status_t2 = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_t2.grid(row=1, column=5, sticky="nsew")
        # RTT
        self.status_rtt = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_rtt.grid(row=1, column=6, sticky="nsew")

        self.status_t3 = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_t3.grid(row=1, column=9, sticky="nsew")
        # Checkbox RX-BEEP
        self.rx_beep_var = tk.IntVar()
        self.rx_beep_box = Checkbutton(self.status_frame,
                                       text="RX-BEEP",
                                       bg=STAT_BAR_CLR,
                                       activebackground=STAT_BAR_CLR,
                                       borderwidth=0,
                                       onvalue=1, offvalue=0,
                                       foreground=STAT_BAR_TXT_CLR,
                                       variable=self.rx_beep_var,
                                       command=self.chk_rx_beep
                                       )
        self.rx_beep_box.grid(row=1, column=10, sticky="nsew")
        # Checkbox RX-BEEP
        self.ts_box_var = tk.IntVar()
        self.ts_box_box = Checkbutton(self.status_frame,
                                      text="T-S",
                                      bg=STAT_BAR_CLR,
                                      borderwidth=0,
                                      activebackground = STAT_BAR_CLR,
                                      onvalue=1, offvalue=0,
                                      foreground=STAT_BAR_TXT_CLR,
                                      variable=self.ts_box_var,
                                      command=self.chk_timestamp
                                      )
        self.ts_box_box.grid(row=1, column=11, sticky="nsew")
        self.status_frame.pack(side=tk.BOTTOM)

        ####################
        # Output
        self.out_frame = tk.Frame(self.pw, width=500, height=320, bd=0, borderwidth=0, )
        self.out_frame.pack(side=tk.BOTTOM, expand=0)
        self.out_frame.rowconfigure(0, weight=1)
        self.out_frame.rowconfigure(1, minsize=10, weight=0)
        self.stat_info_bar = tk.Frame(self.out_frame, height=10, bd=0, borderwidth=0, )
        """
        self.out_frame.columnconfigure(0, minsize=3, weight=0)  # Spacer
        self.out_frame.columnconfigure(1, minsize=80, weight=2)  # Name
        self.out_frame.columnconfigure(2, minsize=60, weight=3)  # QTH
        self.out_frame.columnconfigure(3, minsize=20, weight=4)  # LOC
        self.out_frame.columnconfigure(4, minsize=20, weight=5)  # Typ
        self.out_frame.columnconfigure(5, minsize=80, weight=4)  # Software
        self.out_frame.columnconfigure(6, minsize=28, weight=4)  # Status (PIPE/FT)
        self.out_frame.columnconfigure(7, minsize=30, weight=4)  # Conn Timer
        self.out_frame.columnconfigure(8, minsize=30, weight=4)  # Text Encoding
        self.out_frame.columnconfigure(9, minsize=3, weight=0)  # Spacer
        """

        self.stat_info_bar.columnconfigure(0, minsize=3, weight=0)  # Spacer
        self.stat_info_bar.columnconfigure(1, minsize=80, weight=2)  # Name
        self.stat_info_bar.columnconfigure(2, minsize=60, weight=3)  # QTH
        self.stat_info_bar.columnconfigure(3, minsize=20, weight=4)  # LOC
        self.stat_info_bar.columnconfigure(4, minsize=20, weight=5)  # Typ
        self.stat_info_bar.columnconfigure(5, minsize=80, weight=4)  # Software
        self.stat_info_bar.columnconfigure(6, minsize=28, weight=4)  # Status (PIPE/FT)
        self.stat_info_bar.columnconfigure(7, minsize=30, weight=4)  # Conn Timer
        self.stat_info_bar.columnconfigure(8, minsize=30, weight=4)  # Text Encoding
        self.stat_info_bar.columnconfigure(9, minsize=3, weight=0)  # Spacer

        self.out_txt_win = scrolledtext.ScrolledText(self.out_frame,
                                                     background=TXT_BACKGROUND_CLR,
                                                     foreground=TXT_OUT_CLR,
                                                     font=(FONT, self.text_size),
                                                     height=100,
                                                     bd=0,
                                                     borderwidth=0,
                                                     state="disabled")
        self.out_txt_win.tag_config("input", foreground="yellow")
        # self.out_txt_win.grid(row=0, column=0, columnspan=10, sticky="nsew")
        self.out_txt_win.grid(row=0, column=0,  sticky="nsew")
        self.stat_info_bar.grid(row=1, column=0,  sticky="nsew")
        # Stat INFO (Name,QTH usw)
        self.stat_info_name_var = tk.StringVar(self.stat_info_bar)
        self.stat_info_qth_var = tk.StringVar(self.stat_info_bar)
        self.stat_info_loc_var = tk.StringVar(self.stat_info_bar)
        self.stat_info_typ_var = tk.StringVar(self.stat_info_bar)
        self.stat_info_sw_var = tk.StringVar(self.stat_info_bar)
        self.stat_info_timer_var = tk.StringVar(self.stat_info_bar)
        self.stat_info_encoding_var = tk.StringVar(self.stat_info_bar)
        self.stat_info_status_var = tk.StringVar(self.stat_info_bar)
        size = 1
        name_label = tk.Label(self.stat_info_bar,
                 textvariable=self.stat_info_name_var,
                 # bg=STAT_BAR_CLR,
                 height=1,
                 borderwidth=0,
                 # border=0,
                 fg=STAT_BAR_TXT_CLR,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size, 'bold' )
                 )
        name_label.grid(row=1, column=1, sticky="nsew")
        name_label.bind('<Button-1>', self.main_class.open_user_db_win)
        qth_label = tk.Label(self.stat_info_bar,
                 textvariable=self.stat_info_qth_var,
                 bg=STAT_BAR_CLR,
                 fg=STAT_BAR_TXT_CLR,
                             height=1,
                             borderwidth=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size)
                 )
        qth_label.bind('<Button-1>', self.main_class.open_user_db_win)
        qth_label.grid(row=1, column=2, sticky="nsew")
        loc_label = tk.Label(self.stat_info_bar,
                 textvariable=self.stat_info_loc_var,
                 bg=STAT_BAR_CLR,
                 fg=STAT_BAR_TXT_CLR,
                             height=1,
                             borderwidth=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size)
                 )
        loc_label.bind('<Button-1>', self.main_class.open_user_db_win)
        loc_label.grid(row=1, column=3, sticky="nsew")

        opt = list(STATION_TYPS)
        stat_typ = tk.OptionMenu(
            self.stat_info_bar,
            self.stat_info_typ_var,
            *opt,
            command=self.set_stat_typ
        )
        stat_typ.configure(
            background="#0ed8c3",
            fg=STAT_BAR_TXT_CLR,
            width=10,
            height=1,
            borderwidth=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size,)
        )
        stat_typ.grid(row=1, column=4, sticky="nsew")

        tk.Label(self.stat_info_bar,
                 textvariable=self.stat_info_sw_var,
                 width=20,
                 bg="#ffd444",
                 # fg="red3",
                 height=1,
                 borderwidth=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size )
                 ).grid(row=1, column=5, sticky="nsew")

        status_label = tk.Label(self.stat_info_bar,
                 textvariable=self.stat_info_status_var,
                 bg=STAT_BAR_CLR,
                 fg="red3",
                                height=1,
                                borderwidth=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size, )
                 )
        status_label.grid(row=1, column=6, sticky="nsew")
        status_label.bind('<Button-1>', self.main_class.do_priv)

        tk.Label(self.stat_info_bar,
                 textvariable=self.stat_info_timer_var,
                 width=10,
                 height=1,
                 borderwidth=0,
                 # bg="steel blue",
                 # fg="red3",
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size,)
                 ).grid(row=1, column=7, sticky="nsew")
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            self.stat_info_bar,
            self.stat_info_encoding_var,
            *opt,
            command=self.change_txt_encoding
        )
        txt_encoding_ent.configure(
            background="steel blue",
            height=1,
            width=8,
            borderwidth=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size,)
        )
        txt_encoding_ent.grid(row=1, column=8, sticky="nsew")
        #############
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.pw,
                                                 background=TXT_BACKGROUND_CLR,
                                                 foreground=TXT_MON_CLR,
                                                 font=(FONT, self.text_size),
                                                 height=100, bd=0, borderwidth=0, state="disabled")

        # self.mon_txt.pack(side=tk.BOTTOM)

        # paned window

        self.pw.add(self.status_frame, weight=1)
        # self.pw.paneconfig(self.status_frame, height=40)
        self.pw.add(self.out_frame, weight=1)

        self.pw.add(self.mon_txt, weight=1)

        # place the panedwindow on the root window
        self.pw.pack(fill=tk.BOTH, expand=False)
        self.pw.grid(row=1, column=0, sticky="nsew")

    def update_status_win(self):
        """
        Main Win
        Debug WIN
        """
        station = self.main_class.get_conn(self.main_class.channel_index)
        if station:
            from_call = station.ax25_out_frame.from_call.call_str
            via_calls = ''
            for via in station.ax25_out_frame.via_calls:
                # via: Call
                via_calls += via.call_str + ' '
            status = station.zustand_tab[station.zustand_exec.stat_index][1]
            # uid = station.ax25_out_frame.addr_uid
            n2 = station.n2
            t1 = max(0, int(station.t1 - time.time()))
            #t2 = max(0, int(station.t2 - time.time()))
            t3 = max(0, int(station.t3 - time.time()))
            vr, vs = station.vr, station.vs
            # nr, ns = station.rx_buf_last_frame.ctl_byte.nr, station.rx_buf_last_frame.ctl_byte.ns
            # noACK_buf = str(list(station.tx_buf_unACK.keys()))[1:-1]
            parm_T2 = int(station.parm_T2 * 1000)
            rtt = station.RTT_Timer.rtt_last
            rtt_avg = station.RTT_Timer.rtt_average
            if station.own_port.port_cfg.parm_T2_auto:
                rtt_auto = 'A'
            else:
                rtt_auto = ''

                # send_buf_len = int(station.debugvar_len_out_buf)
            # len_tx2snd_buf = len(station.tx_buf_2send)
            # len_txraw_buf = len(station.tx_buf_rawData)
            # digi_call = station.my_digi_call
            self.status_name.configure(text=from_call)
            status_bg = {
                'ENDE': 'red',              # 0
                'FREI': 'orange',           # 1
                'AUFBAU': 'CadetBlue1',     # 2
                'FRMR': 'red',              # 3
                'ABBAU': 'OrangeRed',       # 4
                'BEREIT': 'green',          # 5
                'REJ': 'yellow',            # 6
                'FINAL': 'LightYellow',     # 7
                'RNR': 'PeachPuff4',        # 8
                'DEST-RNR': 'PeachPuff2',   # 9
                'BOTH-RNR': 'PeachPuff3',   # 10
                'RNR-F': 'LightYellow',     # 11
                'DEST-RNR-F': 'LightYellow',     # 12
                'BOTH-RNR-F': 'LightYellow',     # 13
                'RNR-REJ': 'light sky blue',              # 14
                'DEST-RNR-REJ': 'sky blue',    # 15
                'BOTH-RNR-REJ': 'deep sky blue',    # 16
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
                self.status_n2.configure(bg=STAT_BAR_CLR)
            self.status_n2.configure(text='N2: {}'.format(n2))
            self.status_t1.configure(text='T1: {}'.format(t1))
            self.status_t2.configure(text='T2: {}{}'.format(parm_T2, rtt_auto))
            self.status_rtt.configure(text='RTT: {:.1f}/{:.1f}'.format(rtt, rtt_avg))
            self.status_t3.configure(text='T3: {}'.format(t3))

        else:
            self.status_name.configure(text="", bg=STAT_BAR_CLR)
            self.status_status.configure(text="", bg=STAT_BAR_CLR)
            self.status_unack.configure(text="", bg=STAT_BAR_CLR)
            self.status_vs.configure(text="", bg=STAT_BAR_CLR)
            self.status_n2.configure(text="", bg=STAT_BAR_CLR)
            self.status_t1.configure(text="", bg=STAT_BAR_CLR)
            self.status_t2.configure(text="", bg=STAT_BAR_CLR)
            self.status_t3.configure(text="", bg=STAT_BAR_CLR)
            self.status_rtt.configure(text="", bg=STAT_BAR_CLR)

    def switch_mon_mode(self):
        # TODO Save Stretched Positions
        if self.main_class.mon_mode:
            try:
                self.pw.remove(self.status_frame)
                self.pw.remove(self.mon_txt)
            except tk.TclError:
                pass
            self.pw.configure(height=800)
            self.pw.add(self.status_frame, weight=1)
            self.pw.add(self.out_frame, weight=1)
            self.pw.add(self.mon_txt, weight=1)
            """
            self.status_frame.configure(height=self.inp_txt_height)
            self.out_txt_win.configure(height=self.out_txt_height)
            self.mon_txt.configure(height=self.mon_txt_height)
            """
            self.status_frame.configure(height=10)
            self.out_txt_win.configure(height=10)
            self.mon_txt.configure(height=10)
        else:
            self.mon_txt_height = self.mon_txt.cget('height')
            self.out_txt_height = self.out_txt_win.cget('height')
            self.inp_txt_height = self.status_frame.cget('height')
            # pw_height = self.pw.cget('height')
            self.pw.remove(self.out_frame)
            self.pw.configure(height=800)
            self.status_frame.configure(height=1)
            # self.mon_txt.configure(height=500)

    def chk_rx_beep(self):
        rx_beep_check = self.rx_beep_var.get()
        if rx_beep_check:
            self.rx_beep_box.configure(bg='green', activebackground='green')
        else:
            self.rx_beep_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.main_class.get_ch_param().rx_beep_opt = rx_beep_check

    def chk_timestamp(self):
        ts_check = self.ts_box_var.get()
        if ts_check:
            self.ts_box_box.configure(bg='green', activebackground='green')
        else:
            self.ts_box_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.main_class.get_ch_param().timestamp_opt = ts_check

    def set_stat_typ(self, event=None):
        conn = self.main_class.get_conn()
        if conn:
            db_ent = conn.user_db_ent
            if db_ent:
                db_ent.TYP = self.stat_info_typ_var.get()
        else:
            self.stat_info_typ_var.set('-----')

    def change_txt_encoding(self, event=None, enc=''):
        conn = self.main_class.get_conn()
        if conn:
            db_ent = conn.user_db_ent
            if db_ent:
                if not enc:
                    enc = self.stat_info_encoding_var.get()
                db_ent.Encoding = enc
        else:
            self.stat_info_encoding_var.set('')
