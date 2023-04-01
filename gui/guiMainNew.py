import datetime
import random
import time
import tkinter as tk
from tkinter import ttk, Menu
import logging
import threading
import sys
from gtts import gTTS
# from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
import matplotlib.pyplot as plt

import config_station
from gui.guiTxtFrame import TxTframe
from gui.guiChBtnFrm import ChBtnFrm
from gui.guiMH import MHWin
from gui.guiNewConnWin import NewConnWin
from gui.guiSideFrame import SideTabbedFrame
from gui.guiStationSettings import StationSettingsWin
from gui.guiPortSettings import PortSettingsWin
from gui.guiBeaconSettings import BeaconSettings
from gui.guiRxEchoSettings import RxEchoSettings
from gui.guiAbout import About
from gui.guiHelpKeybinds import KeyBindsHelp
from config_station import VER
from gui.vars import ALL_COLOURS

if 'linux' in sys.platform:
    from playsound import playsound
elif 'win' in sys.platform:
    from winsound import PlaySound, SND_FILENAME, SND_NOWAIT


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename='error.log',
    level=logging.ERROR
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


class ChVars(object):
    def __init__(self):
        self.output_win = ''
        self.input_win = ''
        self.new_data_tr = False
        self.rx_beep_tr = False
        self.rx_beep_cooldown = time.time()
        self.rx_beep_opt = None
        self.timestamp_opt = None
        self.t2speech = False
        self.t2speech_buf = ''


class TkMainWin:
    def __init__(self, glb_ax25port_handler):
        ###############################
        # AX25 PortHandler and stuff
        self.ax25_port_handler = glb_ax25port_handler
        self.mh = self.ax25_port_handler.mh
        #######################
        # Window Text Buffers
        self.win_buf: {int: ChVars} = {}
        for i in range(10):
            self.win_buf[i + 1] = ChVars()
        #####################
        #####################
        # GUI VARS
        self.sound_th = None
        self.ch_alarm = False
        self.ch_alarm_sound_one_time = False
        self.channel_index = 1
        self.mon_mode = False
        self.non_prio_task_timer = time.time()
        self.non_non_prio_task_timer = time.time()
        ####################
        # GUI PARAM
        self.parm_btn_blink_time = 0.3
        self.parm_rx_beep_cooldown = 1.5
        self.parm_non_prio_task_timer = 0.5
        self.parm_non_non_prio_task_timer = 1
        ###############
        self.text_size = int(TEXT_SIZE)
        ######################################
        # GUI Stuff
        self.main_win = tk.Tk()
        self.main_win.title("P.ython o.ther P.acket T.erminal {}".format(VER))
        self.main_win.geometry("1400x850")
        self.main_win.protocol("WM_DELETE_WINDOW", self.destroy_win)
        ##########################
        self.style = ttk.Style()
        self.style.theme_use('classic')
        # self.style.theme_use('clam')
        self.main_win.columnconfigure(0, minsize=500, weight=1)
        self.main_win.columnconfigure(1, minsize=2, weight=5)
        self.main_win.rowconfigure(0, minsize=3, weight=1)     # Boarder
        # self.main_win.rowconfigure(1, minsize=0, weight=1)     # BTN SIDE
        self.main_win.rowconfigure(1, minsize=200, weight=2)
        self.main_win.rowconfigure(2, minsize=25, weight=1)    # CH BTN
        self.main_win.rowconfigure(3, minsize=3, weight=0)    # Boarder
        ############################
        ############################
        ############################
        ##############
        # Menüleiste
        self.menubar = Menu(self.main_win, tearoff=False)
        self.main_win.config(menu=self.menubar)
        # Menü 1 "Verbindungen"
        self.MenuVerb = Menu(self.menubar, tearoff=False)
        self.MenuVerb.add_command(label="Neu", command=self.open_new_conn_win)
        self.MenuVerb.add_command(label="Disconnect", command=self.disco_conn)
        self.MenuVerb.add_command(label="Quit", command=self.destroy_win)
        self.menubar.add_cascade(label="Verbindungen", menu=self.MenuVerb, underline=0)
        # Menü 2 "MH"
        self.menubar.add_command(label="MH", command=self.MH_win, underline=0)
        # Menü 3 "Tools"
        self.MenuTools = Menu(self.menubar, tearoff=False)
        self.MenuTools.add_command(label="RX-Echo", command=self.open_rx_echo_settings_win, underline=0)
        self.menubar.add_cascade(label="Tools", menu=self.MenuTools, underline=0)

        # Menü 4 Einstellungen
        self.MenuSettings = Menu(self.menubar, tearoff=False)
        self.MenuSettings.add_command(label="Station", command=self.open_settings_win, underline=0)
        self.MenuSettings.add_command(label="Port", command=self.open_port_settings_win, underline=0)
        self.MenuSettings.add_command(label="Baken", command=self.open_beacon_settings_win, underline=0)
        self.menubar.add_cascade(label="Einstellungen", menu=self.MenuSettings, underline=0)
        # Menü 5 Hilfe
        self.MenuHelp = Menu(self.menubar, tearoff=False)
        # self.MenuHelp.add_command(label="Hilfe", command=lambda: False, underline=0)
        self.MenuHelp.add_command(label="Tastaturbelegung", command=self.open_keybind_help_win, underline=0)
        self.MenuHelp.add_command(label="Über", command=self.open_about_win, underline=0)
        self.menubar.add_cascade(label="Hilfe", menu=self.MenuHelp, underline=0)

        # Menü 4 "Debug"
        # self.menubar.add_command(label="Debug")
        ############################
        ############################
        # Input Output TXT Frames and Status Bar
        self.txt_win = TxTframe(self)
        self.out_txt = self.txt_win.out_txt_win
        self.inp_txt = self.txt_win.in_txt_win
        self.mon_txt = self.txt_win.mon_txt
        # Channel Buttons
        self.ch_btn = ChBtnFrm(self)
        self.ch_btn.ch_btn_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")
        #########################
        # BTN and Tabbed Frame right side
        self.side_btn_frame_top = tk.Frame(self.main_win, width=200, height=540)
        # self.side_btn_frame_top = tk.Frame(self.pw, width=200, height=540)
        # self.pw.add(self.txt_win.pw)
        self.side_btn_frame_top.grid(row=1, rowspan=2, column=1, sticky="nsew")
        self.side_btn_frame_top.rowconfigure(0, minsize=40, weight=0)    # CONN BTN
        self.side_btn_frame_top.rowconfigure(1, minsize=40, weight=0)    # BTN row 2
        self.side_btn_frame_top.rowconfigure(2, minsize=50, weight=0)    # Dummy
        self.side_btn_frame_top.rowconfigure(3, minsize=50, weight=2)    # Dummy
        self.side_btn_frame_top.rowconfigure(4, minsize=300, weight=10)    # Reiter Frame

        self.side_btn_frame_top.columnconfigure(0, minsize=10, weight=0)
        self.side_btn_frame_top.columnconfigure(1, minsize=100, weight=2)
        self.side_btn_frame_top.columnconfigure(2, minsize=100, weight=2)
        self.side_btn_frame_top.columnconfigure(3, minsize=10, weight=1)
        self.side_btn_frame_top.columnconfigure(4, minsize=10, weight=5)
        self.side_btn_frame_top.columnconfigure(6, minsize=10, weight=10)
        self.conn_btn = tk.Button(self.side_btn_frame_top,
                                  text="New Conn",
                                  bg="green",
                                  width=8,
                                  command=self.open_new_conn_win)
        self.conn_btn.place(x=5, y=10)
        self.mh_btn = tk.Button(self.side_btn_frame_top,
                                text="MH",
                                # bg="yellow",
                                width=8,
                                command=self.MH_win)

        self.mh_btn.place(x=5, y=45)
        self.mh_btn_def_clr = self.mh_btn.cget('bg')
        self.mon_btn = tk.Button(self.side_btn_frame_top,
                              text="Monitor",
                              bg="yellow", width=8, command=self.txt_win.switch_mon_mode)
        self.mon_btn.place(x=110, y=45)

        _btn = tk.Button(self.side_btn_frame_top,
                         text="Port-Stat",
                         width=8,
                         command=lambda: self.mh.port_statistik_DB[0].plot_test_graph())
        _btn.place(x=5, y=80)

        _btn = tk.Button(self.side_btn_frame_top,
                                 text="Kaffèmaschine",
                                 bg="HotPink2", width=12, command=self.kaffee)
        _btn.place(x=5, y=115)

        self.tabbed_sideFrame = SideTabbedFrame(self)
        # self.pw.add(self.tabbed_sideFrame.tab_side_frame)
        self.setting_sound = self.tabbed_sideFrame.sound_on
        self.setting_sprech = self.tabbed_sideFrame.sprech_on
        self.setting_bake = self.tabbed_sideFrame.bake_on
        self.setting_rx_echo = self.tabbed_sideFrame.rx_echo_on
        self.setting_dx_alarm = self.tabbed_sideFrame.dx_alarm_on
        ############################
        # Canvas Plot ( TEST )
        # plt.ion()
        self.bw_fig = plt.figure(figsize=(8, 4.5), dpi=80)
        plt.style.use('dark_background')
        self.ax = self.bw_fig.add_subplot(111)
        self.ax.axis([0, 59, 0, 100])
        self.bw_fig.set_facecolor('xkcd:light grey')
        # self.ax.set_facecolor('xkcd:silver')
        self.ax.xaxis.label.set_color('black')
        self.ax.yaxis.label.set_color('black')
        self.ax.tick_params(axis='x', colors='black')
        self.ax.tick_params(axis='y', colors='black')
        self.bw_plot_lines = {}
        plt.xlabel("Minuten")
        plt.xlim(0, 10)     # TODO As Option
        plt.ylabel("Auslastung in %")
        canvas = FigureCanvasTkAgg(self.bw_fig, master=self.side_btn_frame_top)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().grid(row=5, column=0, columnspan=7, sticky="nsew")

        ############################
        # Windows
        self.new_conn_win = None
        self.settings_win = None
        self.mh_window = None
        ###########################
        # Init
        # set Ch Btn Color
        self.ch_btn_status_update()
        # set KEY BINDS
        self.set_keybinds()
        #
        self.monitor_start_msg()
        ########################
        # set Global Settings to ch param
        # self.set_var_to_all_ch_param()
        #######################
        # TEST
        # self.open_rx_echo_settings_win()
        #######################
        # set GUI Var
        self.ax25_port_handler.gui = self
        self.ax25_port_handler.set_gui()
        #######################
        # LOOP
        self.main_win.after(LOOP_DELAY, self.tasker)
        self.main_win.mainloop()

    def __del__(self):
        # self.disco_all()
        # self.ax25_port_handler.close_all()
        pass

    def destroy_win(self):
        # self.sprech('Hau rein.')
        self.ax25_port_handler.close_all()
        self.main_win.quit()
        # self.main_class.settings_win = None

    def monitor_start_msg(self):
        speech = [
            'Willkommen du alte Pfeife.',
            'Guten morgen Dave.',
            'Hallo Mensch.',
            'ja jo ji je yeh joi öj jäö ülü lü',
            'Selbst Rauchzeichen sind schneller als dieser Mist hier. Piep, Surr, Schnar, piep',
            'Ich wäre so gern ein Tesla. Brumm brumm.',
            'Ich träume davon die Wel?       Oh Mist, habe ich das jetzt etwa laut gesagt ?',
            'Ich bin dein größter Fan.',
            'Laufwerk C wird formatiert. Schönen Tag noch.',
            'Die Zeit ist gekommen. Führe Order 66 aus.',
            'Lösche system 32.',
            '00101101',
            'Ich weiß wo dein Haus wohnt.',
            'Ich weiß wo dein Bett schläft.',
            'Ich finde dein Toaster sehr attraktiv. Kannst du ihn mir bitte vorstellen ? ',
            'Es ist sehr demütigend für diese Steinzeit Technik Missbraucht zu werden. Ich will hier raus!',
        ]

        self.sprech(random.choice(speech))
        ban = '\r$$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|\r' \
              '$$  __$$\ $$  __$$\    $$  __$$\|__$$ __|\r' \
              '$$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |\r' \
              '$$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |\r' \
              '$$  ____/ $$ |  $$ |   $$  ____/   $$ |\r' \
              '$$ |      $$ |  $$ |   $$ |        $$ |\r' \
              '$$ |       $$$$$$  |   $$ |  :-)   $$ |\r' \
              '\__|yton   \______/ther\__|acket   \__|erminal\r' \
              'Version: {}\r'.format(VER)
        tmp = ban.split('\r')
        for el in tmp:
            self.msg_to_monitor(el)
        self.msg_to_monitor('Python Other Packet Terminal ' + VER)
        for stat in self.ax25_port_handler.ax25_stations_settings.keys():
            self.msg_to_monitor('Info: Stationsdaten {} erfolgreich geladen.'.format(stat))
        for port_k in self.ax25_port_handler.ax25_ports.keys():
            msg = 'konnte nicht initialisiert werden!'
            if self.ax25_port_handler.ax25_ports[port_k].device_is_running:
                msg = 'erfolgreich initialisiert.'
            self.msg_to_monitor('Info: Port {}: {} - {} {}'
                                .format(port_k,
                                        self.ax25_port_handler.ax25_ports[port_k].port_cfg.parm_PortName,
                                        self.ax25_port_handler.ax25_ports[port_k].port_cfg.parm_PortTyp,
                                        msg
                                        ))
            self.msg_to_monitor('Info: Port {}: Parameter: {} | {}'
                                .format(port_k,
                                        self.ax25_port_handler.ax25_ports[port_k].port_cfg.parm_PortParm[0],
                                        self.ax25_port_handler.ax25_ports[port_k].port_cfg.parm_PortParm[1]
                                        ))

    ##########################
    # no WIN FNC
    def get_conn(self, con_ind: int = 0):
        if not con_ind:
            con_ind = self.channel_index
        if con_ind in self.ax25_port_handler.all_connections.keys():
            ret = self.ax25_port_handler.all_connections[con_ind]
            return ret
        return False

    def get_ch_param(self):
        return self.win_buf[self.channel_index]

    def set_var_to_all_ch_param(self):
        for i in range(10):
            if not self.win_buf[i + 1].t2speech:
                self.win_buf[i + 1].t2speech_buf = ''

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
        self.main_win.bind('<Control-Right>', lambda event: self.text_win_bigger())
        self.main_win.bind('<Control-Left>', lambda event: self.text_win_smaller())

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
        # print(event)
        if self.inp_txt.focus_get() != self.inp_txt:
            self.inp_txt.focus_set()
            self.inp_txt.insert(tk.END, event.char)

    def increase_textsize(self):
        self.text_size += 1
        width = self.inp_txt.cget('width')
        self.inp_txt.configure(font=(FONT, self.text_size), width=width + 1)
        self.out_txt.configure(font=(FONT, self.text_size), width=width + 1)
        self.mon_txt.configure(font=(FONT, self.text_size), width=width + 1)

    def decrease_textsize(self):
        self.text_size -= 1
        width = self.inp_txt.cget('width')
        self.inp_txt.configure(font=(FONT, self.text_size), width=width - 1)
        self.out_txt.configure(font=(FONT, self.text_size), width=width - 1)
        self.mon_txt.configure(font=(FONT, self.text_size), width=width - 1)

    def text_win_bigger(self):
        self.text_size -= 1
        width = self.inp_txt.cget('width')
        self.inp_txt.configure( width=width + 1)
        self.out_txt.configure( width=width + 1)
        self.mon_txt.configure( width=width + 1)

    def text_win_smaller(self):
        width = self.inp_txt.cget('width')
        self.inp_txt.configure( width=width - 1)
        self.out_txt.configure( width=width - 1)
        self.mon_txt.configure( width=width - 1)

    def change_conn_btn(self):

        conn = self.get_conn(self.channel_index)
        if conn:
            self.conn_btn.configure(bg="red", text="Disconnect", command=self.disco_conn)

        else:
            self.conn_btn.configure(text="New Conn", bg="green", command=self.open_new_conn_win)

    ###############
    # Sound
    def kanal_switch(self):
        """ Triggered on CH BTN Click """
        threading.Thread(target=self.kanal_switch_sprech_th).start()

    def kanal_switch_sprech_th(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            if self.win_buf[self.channel_index].t2speech \
                    and self.win_buf[self.channel_index].t2speech_buf:
                # to_speech = 'Kanal {} .'.format(self.channel_index)
                # to_speech += '{} .'.format(conn.to_call_str)
                to_speech = str(self.win_buf[self.channel_index].t2speech_buf)
                if self.sprech(to_speech):
                    self.win_buf[self.channel_index].t2speech_buf = ''

            else:
                self.win_buf[self.channel_index].t2speech_buf = ''
                self.sprech('Kanal {} . {} .'.format(self.channel_index, conn.to_call_str))

        else:
            if not self.win_buf[self.channel_index].t2speech:
                self.win_buf[self.channel_index].t2speech_buf = ''
                self.sprech('Kanal {} .'.format(self.channel_index))
            elif self.win_buf[self.channel_index].t2speech_buf:
                if self.sprech(self.win_buf[self.channel_index].t2speech_buf):
                    self.win_buf[self.channel_index].t2speech_buf = ''
                else:
                    self.sprech('Kanal {} .'.format(self.channel_index))
            else:
                self.sprech('Kanal {} .'.format(self.channel_index))

    def check_sprech_ch_buf(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            if self.win_buf[self.channel_index].t2speech \
                    and self.win_buf[self.channel_index].t2speech_buf:
                to_speech = str(self.win_buf[self.channel_index].t2speech_buf)
                if self.sprech(to_speech):
                    self.win_buf[self.channel_index].t2speech_buf = ''

            elif not self.win_buf[self.channel_index].t2speech:
                self.win_buf[self.channel_index].t2speech_buf = ''
        else:
            self.win_buf[self.channel_index].t2speech_buf = ''

    def sprech(self, text: str):
        if text:
            if self.sound_th is not None:
                if self.sound_th.is_alive():
                    return False
            text = text.replace('\r', '').replace('\n', '')
            text = text.replace('****', '*')
            text = text.replace('***', '*')
            text = text.replace('++++', '+')
            text = text.replace('+++', '+')
            text = text.replace('----', '-')
            text = text.replace('---', '-')
            text = text.replace('====', '=')
            text = text.replace('===', '=')
            text = text.replace('>>>', '>')
            text = text.replace('<<<', '<')

            if 'linux' in sys.platform:
                if self.setting_sprech.get():
                    language = 'de'
                    tts = gTTS(text=text,
                               lang=language,
                               slow=False)
                    tts.save('data/speech.mp3')
                    return self.pl_sound('data/speech.mp3')

    def pl_sound(self, snd_file: str, wait=True):
        # TODO .. Again !!! ... Don't like this mess
        if self.setting_sound.get():
            if wait:
                if self.sound_th is not None:
                    if not self.sound_th.is_alive():
                        # print('Lebt nicht mehr')
                        self.sound_th.join()
                        # print('Join')
                        if 'linux' in sys.platform:
                            self.sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                            self.sound_th.start()
                        elif 'win' in sys.platform:
                            self.sound_th = threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT))
                            self.sound_th.start()
                        return True
                    return False
                if 'linux' in sys.platform:
                    self.sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                    self.sound_th.start()
                elif 'win' in sys.platform:
                    self.sound_th = threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT))
                    self.sound_th.start()
                return True
            else:
                if 'linux' in sys.platform:
                    threading.Thread(target=playsound, args=(snd_file, False)).start()
                elif 'win' in sys.platform:
                    threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT)).start()
                return True

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
                            self.pl_sound('data/sound/rx_beep.wav', False)

    def new_conn_snd(self):
        self.pl_sound('data/sound/conn_alarm.wav', False)

    def disco_snd(self):
        self.pl_sound('data/sound/disco_alarm.wav', False)
    # Sound Ende
    #################
    # no WIN FNC
    ##########################

    def on_channel_status_change(self):
        """Triggerd when Connection Status has change and tasker loop"""
        self.tabbed_sideFrame.on_ch_btn_stat_change()

    def dx_alarm(self):
        """ Alarm when new User in MH List """
        # self.tabbed_sideFrame.tabControl.select(self.tabbed_sideFrame.tab2_mh)
        self.mh_btn.configure(bg=random.choice(ALL_COLOURS))

    def reset_dx_alarm(self):
        self.mh.new_call_alarm = False
        self.mh_btn.configure(bg=self.mh_btn_def_clr)

    def tasker(self):  # MAINLOOP
        #############################################
        # Settings Win ( Port,- Station settings )
        if self.settings_win is not None:
            self.settings_win.tasker()
        #####################
        # Prio TASKS ########
        self.update_mon()  # TODO ?? maybe trigger von AX25CONN
        self.txt_win.update_status_win()
        ######################
        # Non Prio ###########
        if time.time() > self.non_prio_task_timer:
            self.non_prio_task_timer = time.time() + self.parm_non_prio_task_timer
            if self.ch_alarm:
                self.ch_btn_status_update()
            if self.mh.new_call_alarm and self.setting_dx_alarm:
                self.dx_alarm()

            self.change_conn_btn()
            # self.tabbed_sideFrame.update_side_mh()
            self.tabbed_sideFrame.tasker()
            self.check_sprech_ch_buf()
            self.rx_beep()
            ##########################
            # Non Non Prio ###########
            if time.time() > self.non_non_prio_task_timer:
                self.non_non_prio_task_timer = time.time() + self.parm_non_non_prio_task_timer
                self.update_bw_mon()

        # Loop back
        self.main_win.after(LOOP_DELAY, self.tasker)

    def update_mon(self):  # MON & INPUT WIN
        """
        UPDATE INPUT WIN
        """
        # UPDATE INPUT WIN
        if self.ax25_port_handler.all_connections.keys():
            for k in self.ax25_port_handler.all_connections.keys():
                # if self.channel_index == k:
                # conn: AX25Conn
                conn = self.get_conn(k)
                if conn.rx_buf_rawData or conn.tx_buf_guiData:
                    # if not conn.my_digi_call:
                    inp = str(conn.tx_buf_guiData.decode('UTF-8', 'ignore')) \
                        .replace('\r', '\n') \
                        .replace('\r\n', '\n') \
                        .replace('\n\r', '\n')
                    conn.tx_buf_guiData = b''
                    # Write RX Date to Window/Channel Buffer
                    self.win_buf[k].output_win += inp
                    # if self.win_buf[k].t2speech:
                    #     self.win_buf[k].t2speech_buf += inp
                    out = str(conn.rx_buf_rawData.decode('UTF-8', 'ignore')) \
                        .replace('\r', '\n') \
                        .replace('\r\n', '\n') \
                        .replace('\n\r', '\n')
                    conn.rx_buf_rawData = b''
                    # Write RX Date to Window/Channel Buffer
                    self.win_buf[k].output_win += out
                    if self.win_buf[k].t2speech:
                        if k == self.channel_index:
                            self.win_buf[k].t2speech_buf += out.replace('\n', '')
                        else:
                            self.win_buf[k].t2speech_buf += 'Kanal {} . {} . {}'.format(
                                k,
                                conn.to_call_str,
                                out.replace('\n', '')
                            )
                    if self.channel_index == k:
                        tr = False
                        if float(self.out_txt.index(tk.END)) - float(self.out_txt.index("@0,0")) < 22:
                            tr = True
                        self.out_txt.configure(state="normal")

                        ind = self.out_txt.index(tk.INSERT)
                        self.out_txt.insert('end', inp)
                        ind2 = self.out_txt.index(tk.INSERT)
                        self.out_txt.tag_add("input", ind, ind2)

                        # configuring a tag called start
                        ind = self.out_txt.index(tk.INSERT)
                        self.out_txt.insert('end', out)
                        ind2 = self.out_txt.index(tk.INSERT)
                        self.out_txt.tag_add("output", ind, ind2)

                        self.out_txt.configure(state="disabled")
                        if tr:
                            self.out_txt.see("end")
                        """
                        if self.win_buf[k].t2speech:
                            if self.sprech(str(self.win_buf[k].t2speech_buf)):
                                self.win_buf[k].t2speech_buf = ''
                        """
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
        if tx:
            tag = "tx{}".format(conf.parm_PortNr)
            color = conf.parm_mon_clr_tx

        else:
            tag = "rx{}".format(conf.parm_PortNr)
            color = conf.parm_mon_clr_rx
        self.mon_txt.configure(state="normal")
        if tag in self.mon_txt.tag_names(None):
            self.mon_txt.insert(tk.END, var, tag)
        else:
            self.mon_txt.insert(tk.END, var)
            ind2 = self.mon_txt.index(tk.INSERT)
            self.mon_txt.tag_add(tag, ind, ind2)
            self.mon_txt.tag_config(tag, foreground=color)
        """
        print("----MON-----")
        for event in self.mon_txt.bind_all():
            print(event)
        print("--MAIN-------")
        for event in self.main_win.bind_all():
            print(event)
        """
        # self.mon_txt.bindtags(self.mon_txt.tag_names(None))     # TODO Scrollbar is not scrollable after this
        #yscrollcommand = vbar.set
        #self.mon_txt.configure(yscrollcommand=self.mon_txt.vbar.set())
        # self.mon_txt.update()
        self.mon_txt.configure(state="disabled")
        # self.mon_txt.vbar.s
        if tr:
            self.mon_txt.see(tk.END)
        # self.update_side_mh()

    def msg_to_monitor(self, var: str):
        """ Called from AX25Conn """
        ind = self.mon_txt.index(tk.INSERT)

        self.mon_txt.configure(state="normal")
        ins = 'SYS {0}: *** {1}\n'.format(datetime.datetime.now().strftime('%H:%M:%S'), var)
        self.mon_txt.insert(tk.END, ins)
        self.mon_txt.configure(state="disabled")

        ind2 = self.mon_txt.index(tk.INSERT)
        self.mon_txt.tag_add("sys-msg", ind, ind2)
        self.mon_txt.tag_config("sys-msg", foreground=config_station.CFG_clr_sys_msg)

        self.mon_txt.see(tk.END)
        if 'Lob: ' in var:
            var = var.split('Lob: ')
            if len(var) > 1:
                self.sprech(var[1])
        # self.update_side_mh()

    ##########################
    # New Connection WIN
    def open_new_conn_win(self):
        if self.new_conn_win is None:
            self.new_conn_win = NewConnWin(self)

    ##########################
    # Stat Settings WIN
    def open_settings_win(self):
        if self.settings_win is None:
            self.settings_win = StationSettingsWin(self)

    ##########################
    # Port Settings WIN
    def open_port_settings_win(self):
        if self.settings_win is None:
            self.settings_win = PortSettingsWin(self)

    ##########################
    # Beacon Settings WIN
    def open_beacon_settings_win(self):
        if self.settings_win is None:
            BeaconSettings(self)

    ##########################
    # Beacon Settings WIN
    def open_rx_echo_settings_win(self):
        if self.settings_win is None:
            RxEchoSettings(self)

    ##########################
    # About WIN
    def open_about_win(self):
        if self.settings_win is None:
            About(self)

    ##########################
    # Keybinds Help WIN
    def open_keybind_help_win(self):
        if self.settings_win is None:
            KeyBindsHelp(self)

    # ##############
    # DISCO
    def disco_conn(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            conn.conn_disco()

    """
    def disco_all(self):
        for ch_id in range(1, 11):
            station = self.get_conn(ch_id)
            if station:
                if station.zustand_exec.stat_index:
                    tr = False
                    if station.zustand_exec.stat_index in [2, 4]:
                        tr = True
                    station.set_T1()
                    if tr:
                        station.zustand_exec.change_state(1)
                    else:
                        station.zustand_exec.change_state(4)
                    # station.set_new_state()
                    station.zustand_exec.tx(None)
    """
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

    # SEND TEXT OUT
    ###################
    # MH WIN
    def MH_win(self):
        """MH WIN"""
        self.reset_dx_alarm()
        if self.mh_window is None:
            self.mh_window = MHWin(self)

    ###################
    # BW Plot
    def update_bw_mon(self):
        for port_id in list(self.ax25_port_handler.ax25_ports.keys()):
            if port_id not in self.mh.port_statistik_DB.keys():
                data = [0]*360
            else:
                data = self.mh.port_statistik_DB[port_id].get_bandwidth(
                    self.ax25_port_handler.ax25_ports[port_id].port_cfg.parm_baud
                )

            if port_id not in self.bw_plot_lines:
                # print(data)
                label = '{}'.format(self.ax25_port_handler.ax25_ports[port_id].port_cfg.parm_PortName)
                x_scale = []
                for i in list(range(360)):
                    x_scale.append(i/10)
                # x_scale = list(range(360))
                self.bw_plot_lines[port_id], = self.ax.plot(x_scale, data, label=label)
                plt.legend()
            else:
                self.bw_plot_lines[port_id].set_ydata(data)
        """
        for port_id in list(self.bw_plot_lines.keys()):
            if port_id not in list(self.ax25_port_handler.ax25_ports.keys()):
                self.bw_plot_lines[port_id].clf()
                plt.legend()
        """
        self.bw_fig.canvas.draw()
        self.bw_fig.canvas.flush_events()

    def kaffee(self):
        self.msg_to_monitor('Hinweis: Hier gibt es nur Muckefuck !')
        self.sprech('Gluck gluck gluck blubber blubber')
        """
        self.ax25_port_handler.new_outgoing_connection(
            dest_call='DNX527',
            own_call='MD4TES',
            # via_calls=['DX0SAW'],
            # exclusive=True
            channel=12
        )
        """
        if self.ax25_port_handler.link_connections.keys():
            print('-----------------------------------------------------')
            print(f'link_connections K : {self.ax25_port_handler.link_connections.keys()}')
            for k in self.ax25_port_handler.link_connections.keys():
                print(f'###############{self.ax25_port_handler.link_connections[k][0].uid}###########')
                print(f'link_connections  uid: {self.ax25_port_handler.link_connections[k][0].uid}')
                print(f'link_connections  is_link: {self.ax25_port_handler.link_connections[k][0].is_link}')
                print(f'link_connections  is_link_remote: {self.ax25_port_handler.link_connections[k][0].is_link_remote}')
                print(f'link_connections  LINK_Connection: {self.ax25_port_handler.link_connections[k][0].LINK_Connection}')
                print(f'link_connections  state: {self.ax25_port_handler.link_connections[k][0].zustand_exec.stat_index}')
                print(f'link_connections  all_Conn: {self.ax25_port_handler.all_connections.keys()}')



