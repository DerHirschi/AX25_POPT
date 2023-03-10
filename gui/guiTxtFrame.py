import time
import tkinter as tk
from tkinter import ttk, scrolledtext, Label, Checkbutton

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

        self.status_frame.columnconfigure(1, minsize=70, weight=2)  # Name
        self.status_frame.columnconfigure(2, minsize=50, weight=3)  # Status
        self.status_frame.columnconfigure(3, minsize=70, weight=4)  # unACK
        self.status_frame.columnconfigure(4, minsize=70, weight=4)  # VS VR
        self.status_frame.columnconfigure(5, minsize=50, weight=5)  # N2
        self.status_frame.columnconfigure(6, minsize=70, weight=5)  # T1
        self.status_frame.columnconfigure(7, minsize=70, weight=5)  # T3
        self.status_frame.columnconfigure(8, minsize=50, weight=1)  # RX Beep
        self.status_frame.columnconfigure(9, minsize=20, weight=1)  # TimeStamp
        self.status_frame.rowconfigure(0, weight=1)  # Stat
        self.status_frame.rowconfigure(1, minsize=20, weight=0)  # Out

        self.in_txt_win = scrolledtext.ScrolledText(self.status_frame,
                                                    background=TXT_BACKGROUND_CLR,
                                                    foreground=TXT_INP_CLR,
                                                    font=(FONT, self.text_size),
                                                    insertbackground=TXT_INP_CURSOR_CLR,
                                                    height=100, bd=0)
        # self.in_txt_win.insert(tk.END, "Inp")
        self.in_txt_win.grid(row=0, column=0, columnspan=10, sticky="nsew")
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
        self.status_n2.grid(row=1, column=5, sticky="nsew")

        self.status_t1 = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_t1.grid(row=1, column=6, sticky="nsew")
        self.status_t3 = Label(self.status_frame, text="",
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                               bg=STAT_BAR_CLR,
                               foreground=STAT_BAR_TXT_CLR)
        self.status_t3.grid(row=1, column=7, sticky="nsew")
        # Checkbox RX-BEEP
        self.rx_beep_var = tk.IntVar()
        self.rx_beep_box = Checkbutton(self.status_frame,
                                       text="RX-BEEP",
                                       bg=STAT_BAR_CLR,
                                       activebackground=STAT_BAR_CLR,
                                       borderwidth=0,
                                       onvalue=1, offvalue=0,
                                       foreground=STAT_BAR_TXT_CLR,
                                       variable=self.rx_beep_var
                                       )
        self.rx_beep_box.grid(row=1, column=8, sticky="nsew")
        # Checkbox RX-BEEP
        self.ts_box_var = tk.IntVar()
        self.ts_box_box = Checkbutton(self.status_frame,
                                      text="T-S",
                                      bg=STAT_BAR_CLR,
                                      borderwidth=0,
                                      activebackground = STAT_BAR_CLR,
                                      onvalue=1, offvalue=0,
                                      foreground=STAT_BAR_TXT_CLR,
                                      variable=self.ts_box_var
                                      )
        self.ts_box_box.grid(row=1, column=9, sticky="nsew")

        ####################
        # Output
        self.out_txt_win = scrolledtext.ScrolledText(self.pw, background=TXT_BACKGROUND_CLR,
                                                     foreground=TXT_OUT_CLR,
                                                     font=(FONT, self.text_size),
                                                     height=100, bd=0, borderwidth=0, state="disabled")

        self.out_txt_win.tag_config("input", foreground="yellow")
        self.out_txt_win.tag_config("output", foreground="red")
        # self.out_txt_win.bind(self.out_txt_win.tag(None))
        # self.out_txt_win.insert(tk.END, "OUT")
        # self.out_txt.pack(side=tk.TOP)

        self.status_frame.pack(side=tk.BOTTOM)

        #############
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.pw,
                                                 background=TXT_BACKGROUND_CLR,
                                                 foreground=TXT_MON_CLR,
                                                 font=(FONT, self.text_size),
                                                 height=100, bd=0, borderwidth=0, state="disabled")
        #self.mon_txt.unbind_all('<Button>')
        #self.mon_txt.unbind_all('<ButtonRelease>')
        # self.mon_txt.insert(tk.END, "MON")
        self.mon_txt.pack(side=tk.BOTTOM)
        # print(self.mon_txt.vbar.bind_all())
        # print(self.mon_txt.vbar.bindtags(None))
        #print(self.mon_txt.vbar.event_info())
        #print(self.mon_txt.event_info())
        # paned window

        self.pw.add(self.status_frame, weight=1)
        # self.pw.paneconfig(self.status_frame, height=40)
        self.pw.add(self.out_txt_win, weight=1)

        # self.pw.add(self.out_txt, weight=2)
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
            # t2 = max(0, int(station.t2 - time.time()))
            t3 = max(0, int(station.t3 - time.time()))
            vr, vs = station.vr, station.vs
            # nr, ns = station.rx_buf_last_frame.ctl_byte.nr, station.rx_buf_last_frame.ctl_byte.ns
            # noACK_buf = str(list(station.tx_buf_unACK.keys()))[1:-1]

            # send_buf_len = int(station.debugvar_len_out_buf)
            # len_tx2snd_buf = len(station.tx_buf_2send)
            # len_txraw_buf = len(station.tx_buf_rawData)
            # digi_call = station.my_digi_call
            self.status_name.configure(text=from_call)
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
                self.status_n2.configure(bg=STAT_BAR_CLR)
            self.status_n2.configure(text='N2: {}'.format(n2))
            self.status_t1.configure(text='T1: {}'.format(t1))
            self.status_t3.configure(text='T3: {}'.format(t3))

        else:
            self.status_name.configure(text="", bg=STAT_BAR_CLR)
            self.status_status.configure(text="", bg=STAT_BAR_CLR)
            self.status_unack.configure(text="", bg=STAT_BAR_CLR)
            self.status_vs.configure(text="", bg=STAT_BAR_CLR)
            self.status_n2.configure(text="", bg=STAT_BAR_CLR)
            self.status_t1.configure(text="", bg=STAT_BAR_CLR)
            self.status_t3.configure(text="", bg=STAT_BAR_CLR)

    def switch_mon_mode(self):
        # TODO Save Stretched Positions
        if self.main_class.mon_mode:
            self.main_class.mon_mode = False
            self.main_class.mon_btn.configure(bg='yellow')
            self.pw.remove(self.status_frame)
            self.pw.remove(self.mon_txt)
            self.pw.configure(height=800)

            self.pw.add(self.status_frame, weight=1)
            self.pw.add(self.out_txt_win, weight=1)
            self.pw.add(self.mon_txt, weight=1)

            #self.status_frame.configure(height=self.inp_txt_height)
            """
            self.status_frame.configure(height=self.inp_txt_height)
            self.out_txt_win.configure(height=self.out_txt_height)
            self.mon_txt.configure(height=self.mon_txt_height)
            """
            self.status_frame.configure(height=10)
            self.out_txt_win.configure(height=10)
            self.mon_txt.configure(height=10)
            """
            self.mon_txt.update()
            self.out_txt_win.update()
            self.status_frame.update()
            """
            self.main_class.ch_btn_status_update()

            #self.mon_txt.configure(height=self.mon_txt_height)
        else:
            self.main_class.mon_mode = True
            self.main_class.mon_btn.configure(bg='green')

            self.mon_txt_height = self.mon_txt.cget('height')
            self.out_txt_height = self.out_txt_win.cget('height')
            self.inp_txt_height = self.status_frame.cget('height')
            # pw_height = self.pw.cget('height')
            self.pw.remove(self.out_txt_win)
            self.pw.configure(height=800)
            self.status_frame.configure(height=1)
            self.main_class.ch_btn_status_update()
            # self.mon_txt.configure(height=500)

            """
            self.mon_txt.update()
            self.out_txt_win.update()
            self.status_frame.update()
            self.pw.update()
            """
