import tkinter as tk
from tkinter import ttk, Menu, OptionMenu
import logging
import threading
import time
from playsound import playsound

from gui.guiTxtFrame import TxTframe
from gui.guiChBtnFrm import ChBtnFrm
from main import VER, AX25PortHandler, AX25Conn, AX25Frame

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


def pl_sound(snd_file: str):
    threading.Thread(target=playsound, args=(snd_file,)).start()


class ChVars:
    output_win = ''
    input_win = ''
    new_data_tr = False
    rx_beep_tr = False


class TkMainWin:
    def __init__(self, port_handler: AX25PortHandler):
        ###############################
        # AX25 PortHandler and stuff
        self.ax25_port_handler: AX25PortHandler = port_handler
        # Default Port 0
        self.ax25_port_index = 0
        self.ax25_ports = self.ax25_port_handler.ax25_ports[self.ax25_port_index]
        cfg = self.ax25_ports[1]
        # Globals
        self.mh = cfg.glb_mh
        # TODO
        self.own_call = cfg.parm_StationCalls  # TODO Select Ports for Calls

        #######################
        # Window Text Buffers
        self.win_buf: {int: ChVars} = {}
        for i in range(9):
            self.win_buf[i + 1] = ChVars()
        #####################
        #####################
        # GUI VARS
        self.ch_alarm = False
        self.ch_alarm_sound_one_time = False
        self.channel_index = 1
        ####################
        # GUI PARAM
        self.btn_parm_blink_time = 0.4
        ######################################
        # GUI Stuff
        self.main_win = tk.Tk()
        self.main_win.title("P.ython o.ther P.acket T.erminal {}".format(VER))
        self.main_win.geometry("1400x850")
        ##############
        # KEY BINDS
        self.main_win.bind('<Return>', self.snd_text)
        # self.style = ttk.Style()
        # self.style.theme_use('classic')
        self.main_win.columnconfigure(0, minsize=500, weight=3)
        self.main_win.columnconfigure(1, minsize=200, weight=2)
        self.main_win.rowconfigure(0, minsize=3, weight=1)     # Boarder
        self.main_win.rowconfigure(1, minsize=40, weight=1)
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
        self.MenuVerb.add_command(label="Neu")
        self.MenuVerb.add_command(label="Quit", command=self.main_win.quit)
        self.menubar.add_cascade(label="Verbindungen", menu=self.MenuVerb)
        # Menü 2 "MH"
        self.menubar.add_command(label="MH")
        # Menü 3 "Tools"
        self.MenuTools = Menu(self.menubar)
        self.menubar.add_cascade(label="Tools", menu=self.MenuTools)
        # Menü 4 "Debug"
        self.menubar.add_command(label="Debug")
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

        self.btn_frame = tk.Frame(self.main_win, width=500, height=30)
        self.btn_frame.grid(row=1, column=0, columnspan=1, sticky="nsew")
        self.btn_frame.rowconfigure(0, minsize=15, weight=1)
        self.btn_frame.rowconfigure(1, minsize=15, weight=1)

        self.btn_frame.columnconfigure(0, minsize=10, weight=0)
        self.btn_frame.columnconfigure(1, minsize=10, weight=0)
        self.btn_frame.columnconfigure(2, minsize=10, weight=0)
        self.btn_frame.columnconfigure(3, minsize=10, weight=0)

        self.btn_frame.columnconfigure(4, minsize=500, weight=1)

        self.conn_btn = tk.Button(self.btn_frame, text="New Conn", bg="green", command=self.open_new_conn_win)
        self.conn_btn.grid(row=0, column=0, sticky="nsew")
        self.disco_btn = tk.Button(self.btn_frame, text="Disconnect", bg="red", command=self.disco_conn)
        self.disco_btn.grid(row=0, column=1, sticky="nsew")
        self.test_btn = tk.Button(self.btn_frame, text="DUMMY", bg="yellow")
        self.test_btn.grid(row=1, column=0, sticky="nsew")
        self.test_btn1 = tk.Button(self.btn_frame, text="DUMMY", bg="yellow")
        self.test_btn1.grid(row=1, column=1, sticky="nsew")

        ############################
        # self.debug_win = None
        self.new_conn_win = None

        # self.txt_win.init(self.main_win)
        # self.txt_win.grid(row=1, column=0, sticky="nsew")

        self.ax25_port_handler.set_gui(self)
        self.ch_btn_status_update()
        #######################
        # LOOP
        self.main_win.after(LOOP_DELAY, self.tasker)
        self.main_win.mainloop()

    def ch_btn_status_update(self):
        self.ch_btn.ch_btn_status_update()

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
        # DEBUGGING ###
        # self.tx_rx_check_rand_data()    # TEST Funktion !!!
        ###############
        # Set CH Buttons
        if self.ch_alarm:
            self.ch_btn_status_update()
        self.rx_beep()
        # Loop back
        self.main_win.after(LOOP_DELAY, self.tasker)

    def rx_beep(self):
        tr = self.txt_win.rx_beep_option.get()
        if tr:
            for k in self.win_buf.keys():
                if self.win_buf[k].rx_beep_tr:
                    self.win_buf[k].rx_beep_tr = False
                    pl_sound('data/sound/bell_o.wav')

    ##########################
    # no WIN FNC
    def get_conn(self, con_ind: int):
        if con_ind in self.ax25_port_handler.all_connections.keys():
            ret = self.ax25_port_handler.all_connections[con_ind]
            return ret
        return False

    # no WIN FNC
    ##########################
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
                            if float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")) < 13:
                                tr = True
                            # Save Incoming Data in Window Buffer fo Channel Switching
                            # self.win_buf[self.channel_index][1] += out
                            # Insert Data in Textbox
                            self.out_txt.configure(state="normal")
                            self.out_txt.insert('end', out)
                            self.out_txt.configure(state="disabled")
                            # print("ST: {} - END: {} - DIF: {}".format(self.mon_txt.index("@0,0"),  self.mon_txt.index(tk.END), float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0"))))
                            if tr:
                                self.out_txt.see("end")
                        else:
                            self.win_buf[k].new_data_tr = True
                        self.win_buf[k].rx_beep_tr = True
                        self.ch_btn_status_update()

    def update_monitor(self, var: str, tx=False):
        """ Called from AX25Conn """
        ind = self.mon_txt.index(tk.INSERT)

        tr = False
        if float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")) < 13:
            tr = True
        self.mon_txt.configure(state="normal")
        self.mon_txt.insert(tk.END, var)
        self.mon_txt.configure(state="disabled")
        if tr:
            self.mon_txt.see(tk.END)
        if tx:
            ind2 = self.mon_txt.index(tk.INSERT)
            self.mon_txt.tag_add("tx", ind, ind2)
            # configuring a tag called start
            self.mon_txt.tag_config("tx", foreground="medium violet red")

    ##########################
    # New Connection WIN
    def open_new_conn_win(self):
        # TODO
        if self.new_conn_win is None:
            self.new_conn_win = tk.Tk()
            self.new_conn_win.title("New Connection")
            self.new_conn_win.geometry("600x220")
            self.new_conn_win.protocol("WM_DELETE_WINDOW", self.destroy_new_conn_win)
            self.new_conn_win.columnconfigure(0, minsize=20, weight=2)
            self.new_conn_win.columnconfigure(1, minsize=100, weight=1)
            self.new_conn_win.columnconfigure(2, minsize=50, weight=1)
            self.new_conn_win.columnconfigure(3, minsize=120, weight=1)
            self.new_conn_win.columnconfigure(4, minsize=20, weight=1)
            self.new_conn_win.rowconfigure(0, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(1, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(2, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(3, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(4, minsize=50, weight=1)
            self.new_conn_win.rowconfigure(5, minsize=50, weight=1)
            options = [
                "",
                "Port-0",
                "Port-1",
                "Port-2"
            ]

            # datatype of menu text
            port = tk.StringVar()

            # initial menu text
            port.set("Port-0")

            # Create Dropdown menu
            drop = OptionMenu(self.new_conn_win, port, *options)
            drop.grid(row=1, column=1, columnspan=1, sticky="nsew")
            call_txt_inp = tk.Text(self.new_conn_win, background='grey80', foreground='black', font=("TkFixedFont", 12))
            call_txt_inp.grid(row=1, column=3, columnspan=1, sticky="nsew")

            conn_btn = tk.Button(self.new_conn_win,
                                 text="Los", bg="green",
                                 command=lambda: self.process_new_conn_win(call_txt_inp, port))
            conn_btn.grid(row=5, column=1, sticky="nsew")
            ##############
            # KEY BINDS
            self.new_conn_win.bind('<Return>', lambda event: self.process_new_conn_win(call_txt_inp, port))

    def process_new_conn_win(self, call_txt: tk.Text, port: tk.StringVar):
        txt_win = call_txt
        call = txt_win.get('@0,0', tk.END)
        call = call.split('\r')[0]
        call = call.split('\n')[0]
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

        if len(call) <= 6:

            call = call.upper()
            ax_frame = AX25Frame()
            ax_frame.from_call.call = self.ax25_port_handler.ax25_ports[self.ax25_port_index][0].my_stations[0]  # TODO select outgoing call
            # ax_frame.from_call.call = self.own_call[0]  # TODO select outgoing call
            ax_frame.to_call.call = call
            # via1 = Call()
            # via1.call = 'DNX527'
            ax_frame.via_calls = []
            ax_frame.ctl_byte.SABMcByte()
            conn = self.ax25_port_handler.ax25_ports[self.ax25_port_index][0].new_connection(ax25_frame=ax_frame)
            if conn:
                conn: AX25Conn
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
