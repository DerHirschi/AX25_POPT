import random
import threading
import tkinter as tk
from tkinter.ttk import *
from tkinter import scrolledtext, Label, Menu
import logging
from playsound import playsound

from main import VER, AX25PortHandler
from ax25.ax25Port import KissTCP, AX25Conn, AX25Frame, Call
from gui.guiMH import MHWin
from gui.guiDebug import DEBUGwin
from ax25.ax25Statistics import *

LOOP_DELAY = 50  # ms
TEXT_SIZE = 15
TEXT_SIZE_STATUS = 11
FONT = "Courier"

TEST_TIME_RNG = (0, 60)
TEST_DATA_RNG = (2, 1000)
TEST_OUT0 = b''
TEST_OUT1 = b''
TEST_RUN = False
TEST_FAIL_cnt = 0
TEST_cnt_0 = 0
TEST_cnt_1 = 0
next_run = time.time()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)


class TkMainWin:
    def __init__(self, port_handler):
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
        # TESTING DEBUGGING
        self.axtest_port = self.ax25_ports[0]  # TODO Port Management

        #######################
        # Window Text Buffers
        self.win_buf: {int: [str, str, bool, bool]} = {}
        #  {CH: [Input, Output, NewData, OneTimeAlarm]}
        for i in range(9):
            self.win_buf[i + 1] = ['', '', False, False]
        ###############################################
        #####################
        # GUI VARS
        self.ch_alarm = False
        self.ch_alarm_sound_one_time = False
        self.ch_btn_blink_timer = time.time()
        ####################
        # GUI PARAM
        self.btn_parm_blink_time = 0.4
        # TKINTER
        self.win = tk.Tk()

        self.debug_win = None
        self.new_conn_win = None
        self.channel_index = 1

        self.win.title("P.ython o.ther P.acket T.erminal {}".format(VER))
        self.win.geometry("1400x850")
        self.win.columnconfigure(1, minsize=550, weight=1)
        self.win.columnconfigure(2, minsize=150, weight=1)
        self.win.rowconfigure(0, minsize=150, weight=1)
        self.win.rowconfigure(1, minsize=20, weight=1)
        self.win.rowconfigure(2, minsize=400, weight=1)
        self.win.rowconfigure(3, minsize=30, weight=1)
        self.win.rowconfigure(4, minsize=250, weight=1)
        ##############
        # KEY BINDS
        self.win.bind('<Return>', self.snd_text)

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
        ###################
        # Vorschreibfenster
        self.inp_txt = scrolledtext.ScrolledText(self.win,
                                                 background='black',
                                                 foreground='yellow',
                                                 font=(FONT, TEXT_SIZE),
                                                 insertbackground='white')
        self.inp_txt.grid(row=0, column=1, sticky="nsew")
        #################
        # Staus Bar
        self.status_frame = tk.Frame(self.win, width=550, height=20)
        self.status_frame.grid(row=1, column=1, sticky="nsew")
        self.status_frame.columnconfigure(1, minsize=70, weight=2)  # Name
        self.status_frame.columnconfigure(2, minsize=50, weight=2)  # Status
        self.status_frame.columnconfigure(3, minsize=70, weight=2)  # unACK
        self.status_frame.columnconfigure(4, minsize=70, weight=2)  # VS VR
        self.status_frame.columnconfigure(5, minsize=50, weight=2)  # N2
        self.status_frame.columnconfigure(6, minsize=70, weight=2)  # T1
        self.status_frame.columnconfigure(7, minsize=70, weight=2)  # T3
        self.status_frame.columnconfigure(8, minsize=50, weight=1)  # RX Beep


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

        ############
        # Ausgabe
        self.out_txt = scrolledtext.ScrolledText(self.win, background='black',
                                                 foreground='red',
                                                 font=(FONT, TEXT_SIZE))
        # self.out_txt.configure(state="disabled")
        self.out_txt.grid(row=2, column=1, sticky="nsew")
        ##############
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
        self.ch_btn_frame.grid(row=3, column=1, sticky="nsew")
        self.ch_button1 = tk.Button(self.ch_btn_frame, text=" 1 ", bg="red", command=lambda: self.ch_btn_clk(1))
        self.ch_button2 = tk.Button(self.ch_btn_frame, text=" 2 ", bg="red", command=lambda: self.ch_btn_clk(2))
        self.ch_button3 = tk.Button(self.ch_btn_frame, text=" 3 ", bg="red", command=lambda: self.ch_btn_clk(3))
        self.ch_button4 = tk.Button(self.ch_btn_frame, text=" 4 ", bg="red", command=lambda: self.ch_btn_clk(4))
        self.ch_button5 = tk.Button(self.ch_btn_frame, text=" 5 ", bg="red", command=lambda: self.ch_btn_clk(5))
        self.ch_button6 = tk.Button(self.ch_btn_frame, text=" 6 ", bg="red", command=lambda: self.ch_btn_clk(6))
        self.ch_button7 = tk.Button(self.ch_btn_frame, text=" 7 ", bg="red", command=lambda: self.ch_btn_clk(7))
        self.ch_button8 = tk.Button(self.ch_btn_frame, text=" 8 ", bg="red", command=lambda: self.ch_btn_clk(8))
        self.ch_button9 = tk.Button(self.ch_btn_frame, text=" 9 ", bg="red", command=lambda: self.ch_btn_clk(9))
        self.ch_button10 = tk.Button(self.ch_btn_frame, text=" 10 ", bg="red", command=lambda: self.ch_btn_clk(10))
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
        self.con_btn_dict = {
            1: self.ch_button1,
            2: self.ch_button2,
            3: self.ch_button3,
            4: self.ch_button4,
            5: self.ch_button5,
            6: self.ch_button6,
            7: self.ch_button7,
            8: self.ch_button8,
            9: self.ch_button9,
            10: self.ch_button10,
        }
        ##############
        # Monitor
        self.mon_txt = scrolledtext.ScrolledText(self.win, background='black',
                                                 foreground='green',
                                                 font=(FONT, TEXT_SIZE))
        # self.mon_txt.configure(state="disabled")
        self.mon_txt.grid(row=4, column=1, columnspan=2, sticky="nsew")
        #######################
        #######################
        # SeitenLabel ( TEST )
        self.side_frame = tk.Frame(self.win, width=500, height=30)
        self.side_frame.rowconfigure(0, minsize=60, weight=1)
        self.side_frame.rowconfigure(1, minsize=440, weight=1)
        self.side_frame.grid(row=0, column=2, rowspan=4, sticky="nsew")
        # Seiten Buttons Frame
        self.side_btn_frame = tk.Frame(self.side_frame, width=500, height=30)
        self.side_btn_frame.rowconfigure(0, minsize=60, weight=1)
        self.side_btn_frame.rowconfigure(1, minsize=440, weight=1)
        self.side_btn_frame.columnconfigure(0, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(1, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(2, minsize=100, weight=1)
        self.side_btn_frame.columnconfigure(3, minsize=100, weight=1)
        self.side_btn_frame.grid(row=0, column=0, sticky="nsew")
        self.side_btn_frame.rowconfigure(0, minsize=30, weight=1)
        self.side_btn_frame.rowconfigure(1, minsize=30, weight=1)
        # New Conncetion
        self.conn_btn = tk.Button(self.side_btn_frame, text="New Conn", bg="green", command=self.open_new_conn_win)
        self.conn_btn.grid(row=0, column=0, sticky="nsew")
        self.disco_btn = tk.Button(self.side_btn_frame, text="Disconnect", bg="red", command=self.disco_conn)
        self.disco_btn.grid(row=0, column=1, sticky="nsew")
        self.test_btn = tk.Button(self.side_btn_frame, text="TestCon", bg="yellow", command=self.start_new_conn)
        self.test_btn.grid(row=1, column=0, sticky="nsew")
        self.test_btn1 = tk.Button(self.side_btn_frame, text="TestData", bg="yellow", command=self.run_test)
        self.test_btn1.grid(row=1, column=1, sticky="nsew")

        self.test_lable = Label(self.side_frame, text="", font=("Arial", 15))
        self.test_lable.grid(row=1, column=0)
        # self.test_lable1 = Label(self.side_frame, text="1\n2\n3\n4\n5\n6\n7\n8\n", font=("Arial", 15))
        # self.test_lable1.grid(row=1, column=0)

        self.ax25_port_handler.set_gui(self)
        self.ch_btn_status_update()
        #######################
        # LOOP
        self.win.after(LOOP_DELAY, self.tasker)
        self.win.mainloop()

    def __del__(self):
        pass
        # self.mh.save_mh_data()
        # del self.mh
        # .lock.release()
        # self.ax25_ports_th.join()

        # del self.axtest_port

    """
    def run(self):
        #######################
        # LOOP
        self.win.after(LOOP_DELAY, self.tasker)
        self.win.mainloop()

    """

    def ch_btn_status_update(self):
        # TODO Again !!
        ch_alarm = False
        if self.ax25_port_handler.all_connections.keys():
            for i in list(self.con_btn_dict.keys()):
                if i in self.ax25_port_handler.all_connections.keys():
                    if not self.ax25_port_handler.all_connections[i].is_link or \
                            not self.ax25_port_handler.all_connections[i].my_digi_call:
                        if i == self.channel_index:
                            self.con_btn_dict[i].configure(bg='green2')
                        else:
                            if self.win_buf[i][2]:
                                ch_alarm = True
                                self.ch_btn_alarm(self.con_btn_dict[i])
                            else:
                                self.con_btn_dict[i].configure(bg='green4')
                    else:
                        if i == self.channel_index:
                            self.con_btn_dict[i].configure(bg='red2')
                        else:
                            self.con_btn_dict[i].configure(bg='red4')
                else:
                    if i == self.channel_index:
                        self.con_btn_dict[i].configure(bg='red2')
                    else:
                        self.con_btn_dict[i].configure(bg='red4')

        else:
            for i in list(self.con_btn_dict.keys()):
                if i == self.channel_index:
                    self.con_btn_dict[i].configure(bg='red2')
                else:
                    self.con_btn_dict[i].configure(bg='red4')
        self.ch_alarm = ch_alarm

    def ch_btn_clk(self, ind: int):
        self.win_buf[self.channel_index][0] = self.inp_txt.get('1.0', tk.END)
        self.channel_index = ind
        self.win_buf[self.channel_index][2] = False
        self.win_buf[self.channel_index][3] = False
        self.out_txt.configure(state="normal")
        self.out_txt.delete('1.0', tk.END)
        self.out_txt.insert(tk.END, self.win_buf[ind][1])
        self.out_txt.configure(state="disabled")
        self.inp_txt.delete('1.0', tk.END)
        self.inp_txt.insert(tk.END, self.win_buf[ind][0])
        # self.inp_txt.configure(state="disabled")
        self.out_txt.see(tk.END)
        self.inp_txt.see(tk.END)
        self.ch_btn_status_update()

    def ch_btn_alarm(self, btn: tk.Button):
        if self.ch_btn_blink_timer < time.time():
            COLORS = ['gainsboro', 'old lace',
                      'linen', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
                      'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
                      'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
                      'light slate gray', 'gray', 'light gray', 'midnight blue', 'navy', 'cornflower blue',
                      'dark slate blue',
                      'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue', 'blue',
                      'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
                      'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
                      'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green',
                      'dark olive green',
                      'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
                      'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
                      'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
                      'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
                      'indian red', 'saddle brown', 'sandy brown',
                      'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
                      'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
                      'pale violet red', 'maroon', 'medium violet red', 'violet red',
                      'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
                      'thistle',
                      'AntiqueWhite3', 'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2',
                      'PeachPuff3', 'PeachPuff4',
                      'LemonChiffon2', 'LemonChiffon3', 'LemonChiffon4', 'cornsilk2', 'cornsilk3',
                      'cornsilk4', 'ivory2', 'ivory3', 'ivory4', 'honeydew2', 'honeydew3', 'honeydew4',
                      'LavenderBlush2', 'LavenderBlush3', 'LavenderBlush4', 'MistyRose2', 'MistyRose3',
                      'MistyRose4', 'azure2', 'azure3', 'azure4', 'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
                      'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
                      'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
                      'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
                      'SkyBlue1', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4', 'LightSkyBlue1', 'LightSkyBlue2',
                      'LightSkyBlue3', 'LightSkyBlue4', 'Slategray1', 'Slategray2', 'Slategray3',
                      'Slategray4', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
                      'LightSteelBlue4', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4',
                      'LightCyan2', 'LightCyan3', 'LightCyan4', 'PaleTurquoise1', 'PaleTurquoise2',
                      'PaleTurquoise3', 'PaleTurquoise4', 'CadetBlue1', 'CadetBlue2', 'CadetBlue3',
                      'CadetBlue4', 'turquoise1', 'turquoise2', 'turquoise3', 'turquoise4', 'cyan2', 'cyan3',
                      'cyan4', 'DarkSlategray1', 'DarkSlategray2', 'DarkSlategray3', 'DarkSlategray4',
                      'aquamarine2', 'aquamarine4', 'DarkSeaGreen1', 'DarkSeaGreen2', 'DarkSeaGreen3',
                      'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
                      'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
                      'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
                      'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
                      'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
                      'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
                      'LightYellow2', 'LightYellow3', 'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
                      'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
                      'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
                      'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
                      'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4', 'burlywood1',
                      'burlywood2', 'burlywood3', 'burlywood4', 'wheat1', 'wheat2', 'wheat3', 'wheat4', 'tan1',
                      'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
                      'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
                      'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
                      'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
                      'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
                      'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
                      'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink1', 'pink2', 'pink3', 'pink4',
                      'LightPink1', 'LightPink2', 'LightPink3', 'LightPink4', 'PaleVioletRed1',
                      'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
                      'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
                      'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4', 'plum1',
                      'plum2', 'plum3', 'plum4', 'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
                      'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
                      'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
                      'MediumPurple3', 'MediumPurple4', 'thistle1', 'thistle2', 'thistle3', 'thistle4',
                      ]
            clr = random.choice(COLORS)
            btn.configure(bg=clr)
            self.ch_btn_blink_timer = time.time() + self.btn_parm_blink_time

    def tasker(self):  # MAINLOOP
        # logger.debug(self.axtest_port.connections.keys())

        self.update_mon()   # TODO trigger von AX25CONN

        self.update_status_win()
        if self.debug_win is not None:
            self.debug_win: DEBUGwin
            if self.debug_win.is_running:
                self.debug_win.tasker()
            else:
                self.debug_win = None
        # DEBUGGING ###
        # self.tx_rx_check_rand_data()    # TEST Funktion !!!
        ###############
        # Set CH Buttons
        if self.ch_alarm:
            self.ch_btn_status_update()
        self.rx_beep()
        # Loop back
        self.win.after(LOOP_DELAY, self.tasker)

    def rx_beep(self):
        tr = self.rx_beep_option.get()
        if tr:
            for k in self.win_buf.keys():
                if self.win_buf[k][3]:
                    self.win_buf[k][3] = False
                    snd = threading.Thread(target=playsound, args=('data/sound/bell_o.wav', ))  # TODO File in CFG
                    snd.start()

    ##########################
    # no WIN FNC
    def get_conn(self, con_ind: int):
        if con_ind in self.ax25_port_handler.all_connections.keys():
            ret: AX25Conn = self.ax25_port_handler.all_connections[con_ind]
            return ret
        return False

    # no WIN FNC
    ##########################

    ##############
    # TEST FNC
    def run_test(self):
        global TEST_RUN, TEST_OUT0, TEST_OUT1, next_run
        if TEST_RUN:
            TEST_RUN = False
            self.test_btn1.configure(bg='yellow', text="TestData")
        else:
            TEST_OUT0 = b''
            TEST_OUT1 = b''
            next_run = time.time()
            TEST_RUN = True
            self.test_btn1.configure(bg='green', text="Läuft")

    def tx_rx_check_rand_data(self):
        global next_run, TEST_OUT0, TEST_OUT1, TEST_RUN, TEST_FAIL_cnt, TEST_cnt_0, TEST_cnt_1
        if len(list(self.axtest_port.connections.keys())) > 1 and TEST_RUN:
            # Snd Data ..
            if time.time() > next_run:
                next_run = random.randrange(TEST_TIME_RNG[0], TEST_TIME_RNG[1]) + time.time()
                rand_data = ''.join('{}'.format(x) for x in range(random.randrange(TEST_DATA_RNG[0], TEST_DATA_RNG[1])))
                rand_data = rand_data.encode()
                ran_stat = random.randrange(2)
                if ran_stat:
                    con: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[1]]

                    if not con.tx_buf_rawData:
                        TEST_OUT1 += rand_data
                        con.tx_buf_rawData += rand_data

                else:

                    con: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[0]]
                    if not con.tx_buf_rawData:
                        TEST_OUT0 += rand_data
                        con.tx_buf_rawData += rand_data
            # CHeck
            conn0: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[0]]
            if conn0.rx_buf_rawData_2:
                inp0 = bytes(conn0.rx_buf_rawData_2)
                conn0.rx_buf_rawData_2 = b''  # TODO !!!! Could lost some Packets cause Threading
                try:
                    ind0 = TEST_OUT1.index(inp0)
                    if ind0 != 0:
                        logger.error("!!!!!!! TEST ERROR STAT 1 to 0 ... ABFOLGE !!!!\n ind0: {}\n".format(ind0))
                        raise IndexError
                except ValueError:
                    TEST_cnt_1 -= 1
                except IndexError:
                    logger.error("!!!!!!! TEST ERROR STAT 1 to 0")
                    # TEST_RUN = False
                    TEST_FAIL_cnt += 1
                    TEST_cnt_1 -= 1
                    if TEST_FAIL_cnt > 10:
                        TEST_RUN = False
                    self.test_btn1.configure(bg='red', text="FAIL!!")
                TEST_OUT1 = TEST_OUT1[len(inp0):]
                TEST_cnt_1 += 1

            conn1: AX25Conn = self.axtest_port.connections[list(self.axtest_port.connections.keys())[1]]
            if conn1.rx_buf_rawData_2:
                inp1 = bytes(conn1.rx_buf_rawData_2)
                conn1.rx_buf_rawData_2 = b''  # TODO !!!! Could lost some Packets cause Threading
                try:
                    ind1 = TEST_OUT0.index(inp1)
                    if ind1 != 0:
                        logger.error("!!!!!!! TEST ERROR STAT 0 to 1 ... ABFOLGE !!!!\n ind1: {}\n".format(ind1))
                        raise IndexError
                except ValueError:
                    TEST_cnt_0 -= 1
                except IndexError:
                    logger.error("!!!!!!! TEST ERROR STAT 0 to 1")
                    # TEST_RUN = False
                    TEST_FAIL_cnt += 1
                    TEST_cnt_0 -= 1
                    if TEST_FAIL_cnt > 10:
                        TEST_RUN = False
                    self.test_btn1.configure(bg='red', text="FAIL!!")
                TEST_OUT0 = TEST_OUT0[len(inp1):]
                TEST_cnt_0 += 1

    def start_new_conn(self):
        ax_frame = AX25Frame()
        ax_frame.from_call.call = 'MD6TES'
        ax_frame.to_call.call = 'CB0SAW'
        via1 = Call()
        via1.call = 'DNX527'
        ax_frame.via_calls = [via1]
        ax_frame.ctl_byte.SABMcByte()

        # ax_frame.encode()
        if self.axtest_port.new_connection(ax25_frame=ax_frame):
            self.test_btn.configure(bg='green')

    # TEST fnc ENDE
    #############
    #################
    # Main Win
    # - Main Win & Debug Win

    def update_mon(self):  # MON & INPUT WIN
        """
        Main Win
        # Debug WIN
        """
        # UPDATE INPUT WIN
        if self.ax25_port_handler.all_connections.keys():
            for k in self.ax25_port_handler.all_connections.keys():
                # if self.channel_index == k:
                conn: AX25Conn
                conn = self.get_conn(k)
                if conn.rx_buf_rawData:
                    if not conn.my_digi_call:
                        out = str(conn.rx_buf_rawData.decode('UTF-8', 'ignore')) \
                            .replace('\r', '\n') \
                            .replace('\r\n', '\n') \
                            .replace('\n\r', '\n')
                        conn.rx_buf_rawData = b''
                        # Write RX Date to Window/Channel Buffer
                        self.win_buf[k][1] += out
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
                            self.win_buf[k][2] = True
                        self.win_buf[k][3] = True
                        self.ch_btn_status_update()
        # UPDATE MONITOR
        """
        if self.axtest_port.monitor.out_buf:
            self.mon_txt.configure(state="normal")
            el: str
            for el in self.axtest_port.monitor.out_buf:
                temp = el.split(': ')
                temp = temp[1].split(' to')
                if temp[0] in self.axtest_port.station_cfg.parm_StationCalls:
                    # self.mon_txt.configure(foreground='yellow')
                    self.mon_txt.tag_configure("red", foreground="red")

                    # apply the tag "red"
                    self.mon_txt.tag_add("red", tk.END)
                self.mon_txt.insert("end", el)
                # Autoscroll if Scrollbar near end
                if float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")) < 25:
                    self.mon_txt.see("end")
            self.mon_txt.configure(state="disabled")
        """
        # self.axtest_port.monitor.out_buf = []

    # - Main Win & Debug Win
    def update_status_win(self, window=None):
        """
        Main Win
        Debug WIN
        """
        text = ''
        station = self.get_conn(self.channel_index)
        if station:
            dest_call = station.ax25_out_frame.to_call.call_str
            via_calls = ''
            for via in station.ax25_out_frame.via_calls:
                via: Call
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

            text = '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   '{}\n' \
                   'RES: {} - END: {} - @0,0: {}\n' \
                   'NR: {} - NS: {}\n' \
                   'T1: {}\nT2: {}\nT3 {}\n' \
                   'noACK: {}\n' \
                   'old2Send: {}\n' \
                   '2Send: {}\n' \
                   'SendRaw: {}\n' \
                   'MyDigiCall: {}\n' \
                .format(
                dest_call,
                via_calls,
                list(self.ax25_port_handler.all_connections.keys()),
                uid,
                float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index("@0,0")),
                float(self.mon_txt.index(tk.END)),
                float(self.mon_txt.index("@0,0")),
                nr, ns,
                t1, t2, t3,
                noACK_buf,
                send_buf_len,
                len_tx2snd_buf,
                len_txraw_buf,
                digi_call
            )

        else:
            self.status_name.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_status.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_unack.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_vs.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_n2.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_t1.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
            self.status_t3.configure(text="", font=("Arial", TEXT_SIZE_STATUS), bg='grey80')
        if window is None:
            self.test_lable.config(text=text)  # Debug LABEL
        else:
            window.config(text=text)  # Debug LABEL

    # Main Win ENDE
    #################
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
            self.new_conn_win.columnconfigure(0, minsize=50, weight=2)
            self.new_conn_win.columnconfigure(1, minsize=150, weight=1)
            self.new_conn_win.columnconfigure(2, minsize=150, weight=1)
            self.new_conn_win.columnconfigure(3, minsize=50, weight=1)
            self.new_conn_win.rowconfigure(0, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(1, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(2, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(3, minsize=30, weight=1)
            self.new_conn_win.rowconfigure(4, minsize=50, weight=1)
            self.new_conn_win.rowconfigure(5, minsize=50, weight=1)

            call_txt_inp = tk.Text(self.new_conn_win, background='grey80', foreground='black', font=("TkFixedFont", 12))
            call_txt_inp.grid(row=1, column=2, columnspan=1, sticky="nsew")

            conn_btn = tk.Button(self.new_conn_win,
                                 text="Los", bg="green",
                                 command=lambda: self.process_new_conn_win(call_txt_inp))
            conn_btn.grid(row=5, column=1, sticky="nsew")

    def process_new_conn_win(self, call_txt: tk.Text):
        txt_win = call_txt
        call = txt_win.get('@0,0', tk.END)
        call = call.split('\r')[0]
        call = call.split('\n')[0]
        call = call.replace(' ', '')
        print(str(call))
        print(len(call))
        for i in call:
            print(i.encode())
        if len(call) <= 6:

            call = call.upper()
            ax_frame = AX25Frame()
            ax_frame.from_call.call = self.axtest_port.my_stations[0]  # TODO select outgoing call
            # ax_frame.from_call.call = self.own_call[0]  # TODO select outgoing call
            ax_frame.to_call.call = call
            # via1 = Call()
            # via1.call = 'DNX527'
            ax_frame.via_calls = []
            ax_frame.ctl_byte.SABMcByte()
            conn = self.axtest_port.new_connection(ax25_frame=ax_frame)
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
            station.zustand_exec.change_state(4)
            # station.set_new_state()
            station.zustand_exec.tx(None)

    # DISCO ENDE
    # ##############

    ###################
    # SEND TEXT OUT
    def snd_text(self, event: tk.Event):
        station = self.get_conn(self.channel_index)

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
            self.win_buf[self.channel_index][1] += tmp_txt

            ind2 = self.out_txt.index(tk.INSERT)
            self.out_txt.tag_add("input", ind, ind2)
            # configuring a tag called start
            self.out_txt.tag_config("input", foreground="yellow")

    # SEND TEXT OUT
    ###################
    ##############
    # MH WIN
    def MH_win(self):
        """MH WIN"""
        MHWin(self.axtest_port.MYHEARD)

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


"""
if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        pass
    print("Ende")
    # MYHEARD.save_mh_data()
"""
