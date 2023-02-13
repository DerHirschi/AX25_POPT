import tkinter as tk
from tkinter import ttk, Menu
import logging
import threading
import time
from playsound import playsound

from gui.guiTxtFrame import TxTframe
from gui.guiChBtnFrm import ChBtnFrm
from main import VER, AX25PortHandler

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
    snd = threading.Thread(target=playsound, args=(snd_file,))
    snd.start()


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
        self.ch_btn_blink_timer = time.time()
        self.channel_index = 1
        ####################
        # GUI PARAM
        self.btn_parm_blink_time = 0.4

        ######################################
        # GUI Stuff
        self.main_win = tk.Tk()
        self.main_win.title("P.ython o.ther P.acket T.erminal {}".format(VER))
        self.main_win.geometry("1400x850")
        # self.style = ttk.Style()
        # self.style.theme_use('classic')
        self.main_win.columnconfigure(0, minsize=500, weight=3)
        self.main_win.columnconfigure(1, minsize=200, weight=2)
        self.main_win.rowconfigure(0, minsize=3, weight=1)     # Boarder
        self.main_win.rowconfigure(1, minsize=40, weight=0)
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

        # self.debug_win = None
        # self.new_conn_win = None

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

