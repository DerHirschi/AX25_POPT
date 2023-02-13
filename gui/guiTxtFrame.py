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
    def __init__(self):

        self.pw = ttk.PanedWindow(orient=tk.VERTICAL)
        ###################
        # Output Win
        self.out_txt_win = scrolledtext.ScrolledText(self.pw,
                                                     background=TXT_BACKGROUND_CLR,
                                                     foreground=TXT_OUT_CLR,
                                                     font=(FONT, TEXT_SIZE),
                                                     height=100)
        self.out_txt_win.insert(tk.END, "Out")
        self.out_txt_win.pack(side=tk.TOP)

        ##############
        # Status Frame
        self.status_frame = tk.Frame(self.pw, width=550, height=320, bd=0)
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
        self.status_frame.rowconfigure(0, minsize=20, weight=0)  # Stat
        self.status_frame.rowconfigure(1, weight=1)  # Out

        self.status_name = Label(self.status_frame, text="name", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_name.grid(row=0, column=1, sticky="nsew")
        #self.status_name.pack(side=tk.LEFT, orient=tk.HORIZONTAL)

        self.status_status = Label(self.status_frame, text="stat", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_status.grid(row=0, column=2, sticky="nsew")
        #self.status_status.pack(side=tk.LEFT, orient=tk.HORIZONTAL)

        self.status_unack = Label(self.status_frame, text="unack", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_unack.grid(row=0, column=3, sticky="nsew")
        #self.status_unack.pack(side=tk.LEFT, orient=tk.HORIZONTAL)

        self.status_vs = Label(self.status_frame, text="vs", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_vs.grid(row=0, column=4, sticky="nsew")
        #self.status_vs.pack(side=tk.LEFT, orient=tk.HORIZONTAL)
        self.status_n2 = Label(self.status_frame, text="n2", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_n2.grid(row=0, column=5, sticky="nsew")
        self.status_t1 = Label(self.status_frame, text="t1", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_t1.grid(row=0, column=6, sticky="nsew")
        self.status_t3 = Label(self.status_frame, text="t3", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        self.status_t3.grid(row=0, column=7, sticky="nsew")
        self.rx_beep_option = tk.IntVar()
        Checkbutton(self.status_frame, text="RX-BEEP", variable=self.rx_beep_option).grid(row=0, column=8,
                                                                                          sticky="nsew")
        ####################
        # Vorschreibfenster
        self.inp_txt_win = scrolledtext.ScrolledText(self.status_frame, background=TXT_BACKGROUND_CLR,
                                                     foreground=TXT_INP_CLR,
                                                     font=(FONT, TEXT_SIZE),
                                                     insertbackground=TXT_INP_CURSOR_CLR,
                                                     height=100)

        self.inp_txt_win.insert(tk.END, "INP")
        # self.out_txt.pack(side=tk.TOP)
        self.inp_txt_win.grid(row=1, column=0, columnspan=9, sticky="nsew")

        self.status_frame.pack(side=tk.BOTTOM)

        #############
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.pw,
                                                 background=TXT_BACKGROUND_CLR,
                                                 foreground=TXT_MON_CLR,
                                                 font=(FONT, TEXT_SIZE), height=100)
        self.mon_txt.insert(tk.END, "MON")
        self.mon_txt.pack(side=tk.BOTTOM)
        # paned window

        self.pw.add(self.out_txt_win, weight=1)
        self.pw.add(self.status_frame, weight=1)
        # self.pw.paneconfig(self.status_frame, height=40)

        # self.pw.add(self.out_txt, weight=2)
        self.pw.add(self.mon_txt, weight=1)

        # place the panedwindow on the root window
        self.pw.pack(fill=tk.BOTH, expand=False)
        self.pw.grid(row=1, column=0, sticky="nsew")
