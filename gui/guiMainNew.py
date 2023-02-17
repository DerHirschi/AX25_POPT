import time
import tkinter as tk
from tkinter import ttk, Menu, OptionMenu
import logging
import threading
from playsound import playsound

# import config_station
from gui.guiTxtFrame import TxTframe
from gui.guiChBtnFrm import ChBtnFrm
from gui.guiMH import MHWin
from main import VER, AX25PortHandler, AX25Frame, Call
from ax25.ax25Connection import AX25Conn

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)

LOOP_DELAY = 50  # ms
TEXT_SIZE = 15
TEXT_SIZE_STATUS = 11
FONT = "Courier"
TXT_BACKGROUND_CLR = 'black'
TXT_OUT_CLR = 'red'
TXT_INP_CLR = 'yellow'
TXT_INP_CURSOR_CLR = 'white'
TXT_MON_CLR = 'green'
TXT_MON_TX_CLR = 'medium violet red'
STAT_BAR_CLR = 'grey60'


def pl_sound(snd_file: str):
    threading.Thread(target=playsound, args=(snd_file,)).start()


class ChVars:
    output_win = ''
    input_win = ''
    new_data_tr = False
    rx_beep_tr = False
    rx_beep_cooldown = time.time()
    rx_beep_opt = None
    timestamp_opt = None


class TkMainWin:
    def __init__(self, port_handler: AX25PortHandler):
        ###############################
        # AX25 PortHandler and stuff
        self.ax25_port_handler: AX25PortHandler = port_handler
        # Default Port 0
        self.ax25_port_index = 0
        self.ax25_ports = self.ax25_port_handler.ax25_ports[self.ax25_port_index]
        cfg = self.ax25_ports[1]    # TODO
        # Globals
        self.mh = cfg.glb_mh
        self.own_call = cfg.parm_StationCalls  # TODO Select Ports for Calls

        #######################
        # Window Text Buffers
        self.win_buf: {int: ChVars} = {}
        for i in range(10):
            self.win_buf[i + 1] = ChVars()
        #####################
        #####################
        # GUI VARS
        self.ch_alarm = False
        self.ch_alarm_sound_one_time = False
        self.channel_index = 1
        ####################
        # GUI PARAM
        self.parm_btn_blink_time = 0.3
        self.parm_rx_beep_cooldown = 0.5
        ###############
        self.text_size = int(TEXT_SIZE)
        ######################################
        # GUI Stuff
        self.main_win = tk.Tk()
        self.main_win.title("P.ython o.ther P.acket T.erminal {}".format(VER))
        self.main_win.geometry("1400x850")
        ##########################
        self.style = ttk.Style()
        self.style.theme_use('classic')
        # self.style.theme_use('clam')
        self.main_win.columnconfigure(0, minsize=500, weight=1)
        self.main_win.columnconfigure(1, minsize=2, weight=5)
        self.main_win.rowconfigure(0, minsize=3, weight=1)     # Boarder
        self.main_win.rowconfigure(1, minsize=40, weight=1)     # BTN SIDE
        self.main_win.rowconfigure(2, minsize=200, weight=2)
        self.main_win.rowconfigure(3, minsize=25, weight=1)    # CH BTN
        self.main_win.rowconfigure(4, minsize=3, weight=1)    # Boarder

        ############################

        ############################
        ############################
        ##############
        # Menüleiste
        self.menubar = Menu(self.main_win)
        self.main_win.config(menu=self.menubar)
        # Menü 1 "Verbindungen"
        self.MenuVerb = Menu(self.menubar)
        self.MenuVerb.add_command(label="Neu", command=self.open_new_conn_win)
        self.MenuVerb.add_command(label="Disconnect", command=self.disco_conn)
        self.MenuVerb.add_command(label="Quit", command=self.main_win.quit)
        self.menubar.add_cascade(label="Verbindungen", menu=self.MenuVerb)
        # Menü 2 "MH"
        self.menubar.add_command(label="MH", command=self.MH_win)
        # Menü 3 "Tools"
        self.MenuTools = Menu(self.menubar)
        self.menubar.add_cascade(label="Tools", menu=self.MenuTools)
        # Menü 4 "Debug"
        # self.menubar.add_command(label="Debug")
        ############################
        ############################
        ############################

        # Input Output TXT Frames and Status Bar
        self.txt_win = TxTframe(self)
        self.out_txt = self.txt_win.out_txt_win
        self.inp_txt = self.txt_win.in_txt_win
        self.mon_txt = self.txt_win.mon_txt
        # Channel Buttons
        self.ch_btn = ChBtnFrm(self)
        self.ch_btn.ch_btn_frame.grid(row=3, column=0, columnspan=1, sticky="nsew")
        ############################
        # Conn BTN upper Side
        self.btn_frame = tk.Frame(self.main_win, width=500, height=30)
        self.btn_frame.grid(row=1, column=0, columnspan=1, sticky="nsew")
        self.btn_frame.rowconfigure(0, minsize=10, weight=1)

        self.btn_frame.columnconfigure(0, minsize=5, weight=0)
        self.btn_frame.columnconfigure(1, minsize=5, weight=0)
        self.btn_frame.columnconfigure(2, minsize=5, weight=0)
        self.btn_frame.columnconfigure(3, minsize=5, weight=0)

        self.btn_frame.columnconfigure(4, minsize=500, weight=1)

        self.conn_btn = tk.Button(self.btn_frame, text="New Conn", bg="green", height=5, width=5, command=self.open_new_conn_win)
        self.conn_btn.grid(row=0, column=0, sticky="nsew")
        self.disco_btn = tk.Button(self.btn_frame, text="Disconnect", bg="red", height=5, width=5, command=self.disco_conn)
        self.disco_btn.grid(row=0, column=1, sticky="nsew")
        #########################
        # Check Boxes Right Side
        self.side_btn_frame_top = tk.Frame(self.main_win, width=200, height=540)
        self.side_btn_frame_top.grid(row=1, rowspan=2, column=1, sticky="nsew")
        self.side_btn_frame_top.rowconfigure(0, minsize=40, weight=0)    # CONN BTN
        self.side_btn_frame_top.rowconfigure(1, minsize=200, weight=0)    #
        self.side_btn_frame_top.rowconfigure(2, minsize=300, weight=1)    # Reiter Frame

        self.side_btn_frame_top.columnconfigure(0, minsize=10, weight=0)
        self.side_btn_frame_top.columnconfigure(1, minsize=30, weight=0)
        self.side_btn_frame_top.columnconfigure(2, minsize=10, weight=0)
        self.side_btn_frame_top.columnconfigure(3, minsize=30, weight=0)
        self.side_btn_frame_top.columnconfigure(4, minsize=10, weight=1)
        self.side_btn_frame_top.columnconfigure(6, minsize=10, weight=10)
        self.mh_btn = tk.Button(self.side_btn_frame_top,
                                text="MH",
                                bg="yellow", width=10, command=self.MH_win)
        self.mh_btn.grid(row=0, column=1, sticky="nsew")
        self.btn2 = tk.Button(self.side_btn_frame_top,
                              text="Dummy",
                              bg="yellow", width=10)
        self.btn2.grid(row=0, column=3, sticky="nsew")
        """
        self.side_chkbox_frame = tk.Frame(self.side_btn_frame_top, width=200, height=300)
        self.side_chkbox_frame.grid(row=2, column=0, columnspan=5, sticky="nsew")
        self.side_chkbox_frame.columnconfigure(0, minsize=70, weight=0)
        self.time_stamp_tr = tk.IntVar()

        Checkbutton(self.side_chkbox_frame,
                    text="Time-Stamp",
                    borderwidth=0,
                    variable=self.time_stamp_tr,
                    ).grid(row=0, column=0, sticky="nsew")
        """
        self.tab_side_frame = tk.Frame(self.side_btn_frame_top, width=300, height=400)
        self.tab_side_frame.grid(row=2, column=0, columnspan=6, sticky="nsew")
        self.tabControl = ttk.Notebook(self.tab_side_frame, height=300, width=500)
        #self.tabControl.grid(row=3, column=0, columnspan=5, sticky="nsew")

        tab1 = ttk.Frame(self.tabControl)
        self.tab2_mh = ttk.Frame(self.tabControl)
        tab3 = ttk.Frame(self.tabControl)
        tab4 = ttk.Frame(self.tabControl)

        self.tabControl.add(tab1, text='Station')
        self.tabControl.add(self.tab2_mh, text='MH')
        self.tabControl.add(tab3, text='Ports')
        self.tabControl.add(tab4, text='Settings')
        self.tabControl.pack(expand=0, fill="both")
        self.tabControl.select(self.tab2_mh)
        ttk.Label(tab1,
                  text="TEST").grid(column = 0,
                               row = 0,
                               padx = 30,
                               pady = 30)
        self.tab2_mh.columnconfigure(0, minsize=85, weight=10)
        self.tab2_mh.columnconfigure(1, minsize=100, weight=9)
        self.tab2_mh.columnconfigure(2, minsize=50, weight=8)
        self.tab2_mh.columnconfigure(3, minsize=50, weight=8)
        self.tab2_mh.columnconfigure(4, minsize=50, weight=9)
        tk.Label(self.tab2_mh, text="Zeit", width=85).grid(row=0, column=0)
        tk.Label(self.tab2_mh, text="Call", width=100).grid(row=0, column=1)
        tk.Label(self.tab2_mh, text="PACK", width=50).grid(row=0, column=2)
        tk.Label(self.tab2_mh, text="REJ", width=50).grid(row=0, column=3)
        tk.Label(self.tab2_mh, text="Route", width=50).grid(row=0, column=4)
        self.side_mh: {int: [tk.Entry, tk.Entry, tk.Entry, tk.Entry, tk.Entry]} = {}
        for row in range(9):
            a = tk.Entry(self.tab2_mh, width=85)
            b = tk.Entry(self.tab2_mh, width=80)
            # b = tk.Button(self.tab2_mh, width=100)
            c = tk.Entry(self.tab2_mh, width=20)
            d = tk.Entry(self.tab2_mh, width=20)
            e = tk.Entry(self.tab2_mh, width=100)
            a.grid(row=row + 1, column=0)
            b.grid(row=row + 1, column=1)
            c.grid(row=row + 1, column=2)
            d.grid(row=row + 1, column=3)
            e.grid(row=row + 1, column=4)
            self.side_mh[row + 1] = [a, b, c, d, e]
        self.update_side_mh()
        ############################
        # Windows
        self.new_conn_win = None
        ###########################
        # Init
        # set GUI Var
        self.ax25_port_handler.set_gui(self)
        # set Ch Btn Color
        self.ch_btn_status_update()
        # set KEY BINDS
        self.set_keybinds()
        #######################
        # LOOP
        self.main_win.after(LOOP_DELAY, self.tasker)
        self.main_win.mainloop()

    ##########################
    # no WIN FNC
    def get_conn(self, con_ind: int):
        if con_ind in self.ax25_port_handler.all_connections.keys():
            ret = self.ax25_port_handler.all_connections[con_ind]
            return ret
        return False

    def get_ch_param(self):
        return self.win_buf[self.channel_index]

    def ch_btn_status_update(self):
        self.ch_btn.ch_btn_status_update()

    def set_keybinds(self):
        self.main_win.bind('<F1>', lambda event: self.ch_btn.ch_btn_clk(1))
        self.main_win.bind('<F2>', lambda event: self.ch_btn.ch_btn_clk(2))
        self.main_win.bind('<F3>', lambda event: self.ch_btn.ch_btn_clk(3))
        self.main_win.bind('<F4>', lambda event: self.ch_btn.ch_btn_clk(4))
        self.main_win.bind('<F5>', lambda event: self.ch_btn.ch_btn_clk(5))
        self.main_win.bind('<F6>', lambda event: self.ch_btn.ch_btn_clk(6))
        self.main_win.bind('<F7>', lambda event: self.ch_btn.ch_btn_clk(7))
        self.main_win.bind('<F8>', lambda event: self.ch_btn.ch_btn_clk(8))
        self.main_win.bind('<F9>', lambda event: self.ch_btn.ch_btn_clk(9))
        self.main_win.bind('<F10>', lambda event: self.ch_btn.ch_btn_clk(10))
        self.main_win.bind('<Return>', self.snd_text)
        # self.main_win.bind('<KP_Enter>', self.snd_text)
        self.main_win.bind('<Alt-c>', lambda event: self.open_new_conn_win())
        self.main_win.bind('<Alt-d>', lambda event: self.disco_conn())
        self.main_win.bind('<Control-plus>', lambda event: self.increase_textsize())
        self.main_win.bind('<Control-minus>', lambda event: self.decrease_textsize())

        self.main_win.bind('<Key>', lambda event: self.any_key(event))

    def any_key(self, event: tk.Event):
        if event.keycode == 104:  # Numpad Enter
            self.snd_text(event)
            self.inp_txt.insert(tk.END, '\n')
        """
        if event.keycode == 86:     # Num +
            self.increase_textsize()
        elif event.keycode == 82:   # Num -
            self.decrease_textsize()
        """
        print(event)
        if self.inp_txt.focus_get() != self.inp_txt:
            self.inp_txt.focus_set()
            self.inp_txt.insert(tk.END, event.char)

    def increase_textsize(self):
        self.text_size += 1
        self.inp_txt.configure(font=(FONT, self.text_size))
        self.out_txt.configure(font=(FONT, self.text_size))
        self.mon_txt.configure(font=(FONT, self.text_size))

    def decrease_textsize(self):
        self.text_size -= 1
        self.inp_txt.configure(font=(FONT, self.text_size))
        self.out_txt.configure(font=(FONT, self.text_size))
        self.mon_txt.configure(font=(FONT, self.text_size))

    def rx_beep(self):
        for k in self.win_buf.keys():
            temp: ChVars = self.win_buf[k]
            if temp.rx_beep_cooldown < time.time():
                temp.rx_beep_cooldown = time.time() + self.parm_rx_beep_cooldown
                tr = temp.rx_beep_opt
                if tr is not None:
                    tr = temp.rx_beep_opt
                    if tr:
                        if temp.rx_beep_tr:
                            temp.rx_beep_tr = False
                            pl_sound('data/sound/rx_beep.wav')

    def new_conn_snd(self):
        pl_sound('data/sound/conn_alarm.wav')

    def disco_snd(self):
        pl_sound('data/sound/disco_alarm.wav')
    # no WIN FNC
    ##########################

    def tasker(self):  # MAINLOOP

        self.update_mon()   # TODO trigger von AX25CONN

        self.txt_win.update_status_win()
        """
        if self.debug_win is not None:
            self.debug_win: DEBUGwin
            if self.debug_win.is_running:
                self.debug_win.tasker()
            else:
                self.debug_win = None
        """
        ###############
        # Set CH Buttons
        if self.ch_alarm:
            self.ch_btn_status_update()
        rx_beep_check = self.txt_win.rx_beep_var.get()
        if rx_beep_check:
            self.txt_win.rx_beep_box.configure(bg='green', activebackground='green')
        else:
            self.txt_win.rx_beep_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.get_ch_param().rx_beep_opt = rx_beep_check
        self.rx_beep()

        ts_check = self.txt_win.ts_box_var.get()
        if ts_check:
            self.txt_win.ts_box_box.configure(bg='green', activebackground='green')
        else:
            self.txt_win.ts_box_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.get_ch_param().timestamp_opt = ts_check

        # print(float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")))
        self.update_side_mh()
        # Loop back
        self.main_win.after(LOOP_DELAY, self.tasker)

    def update_mon(self):  # MON & INPUT WIN
        """
        Main Win
        # Debug WIN
        """
        # UPDATE INPUT WIN
        if self.ax25_port_handler.all_connections.keys():
            for k in self.ax25_port_handler.all_connections.keys():
                # if self.channel_index == k:
                # conn: AX25Conn
                conn = self.get_conn(k)
                if conn.rx_buf_rawData:
                    if not conn.my_digi_call:
                        out = str(conn.rx_buf_rawData.decode('UTF-8', 'ignore')) \
                            .replace('\r', '\n') \
                            .replace('\r\n', '\n') \
                            .replace('\n\r', '\n')
                        conn.rx_buf_rawData = b''
                        # Write RX Date to Window/Channel Buffer
                        self.win_buf[k].output_win += out
                        if self.channel_index == k:
                            tr = False
                            if float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")) < 22:
                                tr = True
                            self.out_txt.configure(state="normal")
                            self.out_txt.insert('end', out)
                            self.out_txt.configure(state="disabled")
                            if tr:
                                self.out_txt.see("end")
                        else:
                            self.win_buf[k].new_data_tr = True
                        self.win_buf[k].rx_beep_tr = True
                        self.ch_btn_status_update()

    def update_monitor(self, var: str, conf, tx=False):
        """ Called from AX25Conn """
        ind = self.mon_txt.index(tk.INSERT)
        tr = False
        if float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")) < 22:
            tr = True
        self.mon_txt.configure(state="normal")
        self.mon_txt.insert(tk.END, var)
        self.mon_txt.configure(state="disabled")
        if tx:
            ind2 = self.mon_txt.index(tk.INSERT)
            self.mon_txt.tag_add("tx{}".format(conf.parm_PortNr), ind, ind2)
            self.mon_txt.tag_config("tx{}".format(conf.parm_PortNr), foreground=conf.parm_mon_clr_tx)

        else:
            ind2 = self.mon_txt.index(tk.INSERT)
            self.mon_txt.tag_add("rx{}".format(conf.parm_PortNr), ind, ind2)
            self.mon_txt.tag_config("rx{}".format(conf.parm_PortNr), foreground=conf.parm_mon_clr_rx)

        if tr:
            self.mon_txt.see(tk.END)
        # self.update_side_mh()

    def update_side_mh(self):
        mh_ent = self.mh.output_sort_entr(8)
        c = 1
        for el in mh_ent:
            self.side_mh[c][0].delete(0, tk.END)
            self.side_mh[c][0].insert(0, el.last_seen.split(' ')[1])
            self.side_mh[c][1].delete(0, tk.END)
            self.side_mh[c][1].insert(0, el.own_call)
            # self.side_mh[c][1].configure(text=el.own_call)
            self.side_mh[c][2].delete(0, tk.END)
            self.side_mh[c][2].insert(0, el.pac_n)
            self.side_mh[c][3].delete(0, tk.END)
            self.side_mh[c][3].insert(0, el.rej_n)
            c += 1

    ##########################
    # New Connection WIN
    def open_new_conn_win(self):
        # TODO
        if self.new_conn_win is None:
            self.new_conn_win = tk.Tk()
            self.new_conn_win.title("New Connection")
            self.new_conn_win.geometry("600x185")
            self.new_conn_win.protocol("WM_DELETE_WINDOW", self.destroy_new_conn_win)
            self.new_conn_win.resizable(False,False)
            self.new_conn_win.columnconfigure(0, minsize=20, weight=1)
            self.new_conn_win.columnconfigure(1, minsize=100, weight=1)
            self.new_conn_win.columnconfigure(2, minsize=50, weight=5)
            self.new_conn_win.columnconfigure(3, minsize=120, weight=1)
            self.new_conn_win.columnconfigure(4, minsize=20, weight=1)
            self.new_conn_win.rowconfigure(0, minsize=38, weight=3)
            self.new_conn_win.rowconfigure(1, minsize=5, weight=5)
            self.new_conn_win.rowconfigure(2, minsize=35, weight=3)
            self.new_conn_win.rowconfigure(3, minsize=5, weight=1)
            self.new_conn_win.rowconfigure(4, minsize=40, weight=3)
            self.new_conn_win.rowconfigure(5, minsize=40, weight=1)
            options = [
                "Port-0",
                "Port-1",
                "Port-2",
                "Port-3",
            ]

            # datatype of menu text
            port = tk.StringVar()
            port.set("Port-0")

            # Create Dropdown menu
            drop = OptionMenu(self.new_conn_win, port, *options)
            drop.configure(bg='grey80', foreground='black', width=50, height=5, direction='above')

            drop.grid(row=1, column=1, columnspan=1, sticky="nsew")
            call_txt_inp = tk.Text(self.new_conn_win, background='grey80', foreground='black', font=("TkFixedFont", 12),
                                   height=5)
            call_txt_inp.grid(row=1, column=3, columnspan=1, sticky="nsew")

            conn_btn = tk.Button(self.new_conn_win,
                                 text="Los", bg="green",
                                 command=lambda: self.process_new_conn_win(call_txt_inp, port))
            conn_btn.grid(row=4, column=1, sticky="nsew")
            call_txt_inp.focus_set()
            ##############
            # KEY BINDS
            self.new_conn_win.bind('<Return>', lambda event: self.process_new_conn_win(call_txt_inp, port))
            self.new_conn_win.bind('<KP_Enter>', lambda event: self.process_new_conn_win(call_txt_inp, port))
            self.new_conn_win.bind('<Escape>', lambda event: self.destroy_new_conn_win())

    def process_new_conn_win(self, call_txt: tk.Text, port: tk.StringVar):
        txt_win = call_txt
        call = txt_win.get('0.0', tk.END)
        call = call.split('\r')[0]
        call = call.split('\n')[0]
        call = call.split(' ')
        via = []
        if len(call) > 1:
            via = call[1:]
        call = call[0]
        call = call.replace(' ', '')
        print(str(call))
        print(len(call))
        port = port.get()
        if port:
            self.ax25_port_index = int(port.replace('Port-', ''))
        else:
            self.ax25_port_index = 0
        print(str(port))
        print(str(self.ax25_port_index))
        call = call.split('-')
        if 6 >= len(call[0]) > 1:

            ax_frame = AX25Frame()
            ax_frame.from_call.call = self.ax25_port_handler.ax25_ports[self.ax25_port_index][0].my_stations[0]  # TODO select outgoing call
            # ax_frame.from_call.call = self.own_call[0]  # TODO select outgoing call
            ax_frame.to_call.call = call[0].upper()
            if len(call) > 1:
                if call[1].isdigit():
                    ax_frame.to_call.ssid = int(call[1])
            # via1 = Call()
            # via1.call = 'DNX527'
            ax_frame.via_calls = []
            for c in via:
                new_c = Call()
                new_c.call_str = c.upper()
                ax_frame.via_calls.append(new_c)

            ax_frame.ctl_byte.SABMcByte()
            conn = self.ax25_port_handler.ax25_ports[self.ax25_port_index][0].new_connection(ax25_frame=ax_frame)
            if conn:
                # conn: AX25Conn
                self.ax25_port_handler.insert_conn2all_conn_var(new_conn=conn, ind=self.channel_index)
            else:
                self.out_txt.insert(tk.END, '\n*** Busy. No free SSID available.\n\n')
            self.destroy_new_conn_win()
            self.ch_btn_status_update()

    def destroy_new_conn_win(self):
        self.new_conn_win.destroy()
        self.new_conn_win = None

    # New Connection WIN ENDE
    ##########################

    # ##############
    # DISCO
    def disco_conn(self):
        station: AX25Conn = self.get_conn(self.channel_index)
        if station:
            if station.zustand_exec.stat_index:
                tr = False
                if station.zustand_exec.stat_index in [2, 4]:
                    tr = True
                station.zustand_exec.change_state(4)
                # station.set_new_state()
                station.zustand_exec.tx(None)
                if tr:
                    station.n2 = 100

    # DISCO ENDE
    # ##############
    ###################
    # SEND TEXT OUT
    def snd_text(self, event: tk.Event):
        station: AX25Conn = self.get_conn(self.channel_index)

        if station:
            ind = str(float(self.inp_txt.index(tk.INSERT)) - 1)
            tmp_txt = self.inp_txt.get(ind, self.inp_txt.index(tk.INSERT))
            tmp_txt = tmp_txt.replace('\n', '').replace('\r', '')
            # Send it to Connection/Station TX Buffer
            station.tx_buf_rawData += (tmp_txt + '\r').encode()
            ind = self.out_txt.index(tk.INSERT)
            tmp_txt += '\n'
            # Insert in OutScreen Window
            self.out_txt.configure(state="normal")
            self.out_txt.insert(tk.END, tmp_txt)
            self.out_txt.configure(state="disabled")
            # Insert in Buffer for Channel switching
            self.win_buf[self.channel_index].output_win += tmp_txt

            ind2 = self.out_txt.index(tk.INSERT)
            self.out_txt.tag_add("input", ind, ind2)
            # configuring a tag called start
            self.out_txt.tag_config("input", foreground="yellow")

    # SEND TEXT OUT
    ###################
    # MH WIN
    def MH_win(self):
        """MH WIN"""
        MHWin(self.mh)

    # MH WIN ENDE