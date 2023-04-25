import datetime
import random
import time
import tkinter as tk
from tkinter import ttk, Menu
import threading
import sys

import gtts
from gtts import gTTS
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
import matplotlib.pyplot as plt

import config_station
from fnc.str_fnc import tk_filter_bad_chars
from gui.guiPipeToolSettings import PipeToolSettings
from main import LANGUAGE
from gui.guiMulticastSettings import MulticastSettings
from gui.guiTxtFrame import TxTframe
from gui.guiChBtnFrm import ChBtnFrm
from gui.guiMH import MHWin
from gui.guiNewConnWin import NewConnWin
from gui.guiSideFrame import SideTabbedFrame
from gui.guiStationSettings import StationSettingsWin
from gui.guiPortSettings import PortSettingsWin
from gui.guiBeaconSettings import BeaconSettings
from gui.guiRxEchoSettings import RxEchoSettings
from gui.guiLinkholderSettings import LinkHolderSettings
from gui.guiUserDB import UserDB
from gui.guiAbout import About
from gui.guiHelpKeybinds import KeyBindsHelp
from gui.guiMsgBoxes import open_file_dialog, save_file_dialog
from gui.guiFileTX import FileSend
from gui.vars import ALL_COLOURS
from string_tab import STR_TABLE
from fnc.os_fnc import is_linux, is_windows

if is_linux():
    from playsound import playsound
elif is_windows():
    from winsound import PlaySound, SND_FILENAME, SND_NOWAIT

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
        self.input_win_index = '1.0'
        self.new_data_tr = False
        self.rx_beep_tr = False
        self.rx_beep_cooldown = time.time()
        self.rx_beep_opt = None
        self.timestamp_opt = None
        self.t2speech = False
        self.t2speech_buf = ''
        self.autoscroll = True


class TkMainWin:
    def __init__(self, glb_ax25port_handler):
        self.language = LANGUAGE
        ###############################
        # AX25 PortHandler and stuff
        self.ax25_port_handler = glb_ax25port_handler
        self.mh = self.ax25_port_handler.mh
        #####################
        #####################
        # GUI VARS
        self.sound_th = None
        self.ch_alarm = False
        self.ch_alarm_sound_one_time = False
        self.channel_index = 1
        self.mon_mode = 0
        self.connect_history = {}
        ####################
        # GUI PARAM
        self.parm_btn_blink_time = 0.3
        self.parm_rx_beep_cooldown = 1.5
        # Tasker Timings
        self.loop_delay = 50  # ms
        self.parm_non_prio_task_timer = 0.5  # s
        self.parm_non_non_prio_task_timer = 1  # s
        self.non_prio_task_timer = time.time()
        self.non_non_prio_task_timer = time.time()
        ###############
        self.text_size = 15
        ######################################
        # GUI Stuff
        self.main_win = tk.Tk()
        self.main_win.title("P.ython o.ther P.acket T.erminal {}".format(config_station.VER))
        self.main_win.geometry("1400x850")
        # self.main_win.iconbitmap("favicon.ico")
        self.main_win.protocol("WM_DELETE_WINDOW", self.destroy_win)
        ##########################
        self.style = ttk.Style()
        self.style.theme_use('classic')
        # self.style.theme_use('clam')
        self.main_win.columnconfigure(0, minsize=500, weight=1)
        self.main_win.columnconfigure(1, minsize=2, weight=5)
        self.main_win.rowconfigure(0, minsize=3, weight=1)  # Boarder
        # self.main_win.rowconfigure(1, minsize=0, weight=1)     # BTN SIDE
        self.main_win.rowconfigure(1, minsize=200, weight=2)
        self.main_win.rowconfigure(2, minsize=25, weight=1)  # CH BTN
        self.main_win.rowconfigure(3, minsize=3, weight=0)  # Boarder
        ############################
        ############################
        ############################
        ##############
        # Menüleiste
        self.menubar = Menu(self.main_win, tearoff=False)
        self.main_win.config(menu=self.menubar)
        # Menü 1 "Verbindungen"
        self.MenuVerb = Menu(self.menubar, tearoff=False)
        self.MenuVerb.add_command(label=STR_TABLE['new'][self.language], command=self.open_new_conn_win)
        self.MenuVerb.add_command(label=STR_TABLE['disconnect'][self.language], command=self.disco_conn)
        self.MenuVerb.add_separator()
        self.MenuVerb.add_command(label=STR_TABLE['quit'][self.language], command=self.destroy_win)
        self.menubar.add_cascade(label=STR_TABLE['connections'][self.language], menu=self.MenuVerb, underline=0)
        # Menü 2 "Bearbeiten"
        self.MenuEdit = Menu(self.menubar, tearoff=False)
        self.MenuEdit.add_command(label=STR_TABLE['copy'][self.language], command=self.copy_select, underline=0)
        self.MenuEdit.add_command(label=STR_TABLE['past'][self.language], command=self.clipboard_past, underline=1)
        self.MenuEdit.add_separator()
        self.MenuEdit.add_command(label=STR_TABLE['past_f_file'][self.language], command=self.insert_fm_file,
                                  underline=0)
        self.MenuEdit.add_command(label=STR_TABLE['save_to_file'][self.language], command=self.save_to_file,
                                  underline=1)
        self.MenuEdit.add_command(label=STR_TABLE['save_mon_to_file'][self.language], command=self.save_monitor_to_file,
                                  underline=1)
        self.MenuEdit.add_separator()
        self.MenuEdit.add_command(label=STR_TABLE['clean_qso_win'][self.language], command=self.clear_channel_data,
                                  underline=0)
        self.MenuEdit.add_command(label=STR_TABLE['clean_mon_win'][self.language], command=self.clear_monitor_data,
                                  underline=0)
        self.menubar.add_cascade(label=STR_TABLE['edit'][self.language], menu=self.MenuEdit, underline=0)
        # Menü 3 "Tools"
        self.MenuTools = Menu(self.menubar, tearoff=False)
        self.MenuTools.add_command(label="MH", command=self.MH_win, underline=0)
        self.MenuTools.add_command(label=STR_TABLE['statistic'][self.language], command=self.open_port_stat_win,
                                   underline=1)
        self.MenuTools.add_separator()
        self.MenuTools.add_command(label=STR_TABLE['linkholder'][self.language],
                                   command=self.open_linkholder_settings_win, underline=0)
        self.MenuTools.add_separator()
        self.MenuTools.add_command(label=STR_TABLE['send_file'][self.language], command=self.open_file_send,
                                   underline=0)
        self.MenuTools.add_command(label='Pipe-Tool', command=self.pipe_tool_win, underline=0)
        self.MenuTools.add_separator()
        self.MenuTools.add_command(label=STR_TABLE['user_db'][self.language], command=self.open_user_db_win,
                                   underline=0)
        # self.MenuTools.add_command(label="Datei senden", command=self.open_linkholder_settings_win, underline=0)
        self.menubar.add_cascade(label=STR_TABLE['tools'][self.language], menu=self.MenuTools, underline=0)

        # Menü 4 Einstellungen
        self.MenuSettings = Menu(self.menubar, tearoff=False)
        self.MenuSettings.add_command(label=STR_TABLE['station'][self.language], command=self.open_settings_win,
                                      underline=0)
        self.MenuSettings.add_command(label=STR_TABLE['port'][self.language], command=self.open_port_settings_win,
                                      underline=0)
        self.MenuSettings.add_command(label=STR_TABLE['beacon'][self.language], command=self.open_beacon_settings_win,
                                      underline=0)
        self.MenuSettings.add_separator()
        self.MenuSettings.add_command(label='Multicast', command=self.open_multicast_settings_win, underline=0)
        self.MenuSettings.add_command(label="RX-Echo", command=self.open_rx_echo_settings_win, underline=0)

        self.menubar.add_cascade(label=STR_TABLE['settings'][self.language], menu=self.MenuSettings, underline=0)
        # Menü 5 Hilfe
        self.MenuHelp = Menu(self.menubar, tearoff=False)
        # self.MenuHelp.add_command(label="Hilfe", command=lambda: False, underline=0)
        self.MenuHelp.add_command(label=STR_TABLE['keybind'][self.language], command=self.open_keybind_help_win,
                                  underline=0)
        self.MenuHelp.add_separator()
        self.MenuHelp.add_command(label=STR_TABLE['about'][self.language], command=self.open_about_win, underline=0)
        self.menubar.add_cascade(label=STR_TABLE['help'][self.language], menu=self.MenuHelp, underline=0)

        # Menü 4 "Debug"
        # self.menubar.add_command(label="Debug")
        ############################
        ############################
        # Input Output TXT Frames and Status Bar
        self.txt_win = TxTframe(self)
        self.out_txt = self.txt_win.out_txt_win
        self.inp_txt = self.txt_win.in_txt_win
        self.mon_txt = self.txt_win.mon_txt
        #######################
        # Window Text Buffers
        self.win_buf: {int: ChVars} = {}
        for i in range(11):
            self.win_buf[i] = ChVars()
            self.win_buf[i].input_win_index = str(self.inp_txt.index(tk.INSERT))
        # Channel Buttons
        self.ch_btn = ChBtnFrm(self)
        self.ch_btn.ch_btn_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")
        #########################
        # BTN and Tabbed Frame right side
        self.side_btn_frame_top = tk.Frame(self.main_win, width=200, height=540)
        # self.side_btn_frame_top = tk.Frame(self.pw, width=200, height=540)
        # self.pw.add(self.txt_win.pw)
        self.side_btn_frame_top.grid(row=1, rowspan=2, column=1, sticky="nsew")
        self.side_btn_frame_top.rowconfigure(0, minsize=40, weight=0)  # CONN BTN
        self.side_btn_frame_top.rowconfigure(1, minsize=40, weight=0)  # BTN row 2
        self.side_btn_frame_top.rowconfigure(2, minsize=50, weight=0)  # Dummy
        self.side_btn_frame_top.rowconfigure(3, minsize=50, weight=2)  # Dummy
        self.side_btn_frame_top.rowconfigure(4, minsize=300, weight=10)  # Reiter Frame

        self.side_btn_frame_top.columnconfigure(0, minsize=10, weight=0)
        self.side_btn_frame_top.columnconfigure(1, minsize=100, weight=2)
        self.side_btn_frame_top.columnconfigure(2, minsize=100, weight=2)
        self.side_btn_frame_top.columnconfigure(3, minsize=10, weight=1)
        self.side_btn_frame_top.columnconfigure(4, minsize=10, weight=5)
        self.side_btn_frame_top.columnconfigure(6, minsize=10, weight=1)
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
        # self.mh_btn.place(x=110, y=10)
        self.mh_btn_def_clr = self.mh_btn.cget('bg')
        self.mon_btn = tk.Button(self.side_btn_frame_top,
                                 text="Monitor",
                                 bg="yellow", width=8, command=lambda: self.switch_channel(0))
        # self.mon_btn.place(x=110, y=45)
        self.mon_btn.place(x=110, y=10)

        _btn = tk.Button(self.side_btn_frame_top,
                         text="Port-Stat",
                         width=8,
                         command=self.open_port_stat_win)
        # _btn.place(x=5, y=80)
        _btn.place(x=110, y=45)

        _btn = tk.Button(self.side_btn_frame_top,
                         text="Kaffèmaschine",
                         bg="HotPink2", width=12, command=self.kaffee)
        _btn.place(x=215, y=10)
        ###############################################
        # Stations Info ( Name, QTH ... )

        self.stat_info_name_var = tk.StringVar(self.side_btn_frame_top)
        stat_info_name = tk.Label(self.side_btn_frame_top,
                                  textvariable=self.stat_info_name_var,
                                  font=(FONT, 12, 'bold')
                                  )
        stat_info_name.place(x=10, y=90)
        self.stat_info_qth_var = tk.StringVar(self.side_btn_frame_top)
        stat_info_qth = tk.Label(self.side_btn_frame_top,
                                 textvariable=self.stat_info_qth_var,
                                 font=(FONT, 12, 'bold')
                                 )
        stat_info_qth.place(x=10, y=115)
        self.stat_info_loc_var = tk.StringVar(self.side_btn_frame_top)
        stat_info_loc = tk.Label(self.side_btn_frame_top,
                                 textvariable=self.stat_info_loc_var,
                                 font=(FONT, 12, 'bold')
                                 )
        stat_info_loc.place(x=10, y=140)
        # Status /Pipe/Link/File-RX/File-TX
        self.status_info_var = tk.StringVar(self.side_btn_frame_top)
        self.status_label = tk.Label(
            self.side_btn_frame_top,
            textvariable=self.status_info_var,
            fg='red')
        font = self.status_label.cget('font')
        self.status_label.configure(font=(FONT, 14, 'bold'))
        self.status_label.place(x=10, y=163)

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
        plt.xlabel(STR_TABLE['minutes'][self.language])
        plt.xlim(0, 10)  # TODO As Option
        plt.ylabel(STR_TABLE['occup'][self.language])
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
        self.set_binds()
        self.set_keybinds()
        #
        self.monitor_start_msg()
        #######################
        # TEST
        # self.open_rx_echo_settings_win()
        #######################
        # set GUI Var
        self.ax25_port_handler.gui = self
        self.ax25_port_handler.set_gui()
        #######################
        # LOOP
        self.main_win.after(self.loop_delay, self.tasker)
        self.main_win.mainloop()

    def __del__(self):
        # self.disco_all()
        # self.ax25_port_handler.close_all()
        pass

    def destroy_win(self):
        self.ax25_port_handler.close_all()

    def monitor_start_msg(self):
        speech = [
            'Willkommen du alte Pfeife.',
            'Guten morgen Dave.',
            'Hallo Mensch.',
            'ja jö jil jü yeh joi öj jäö ülü lü.',
            'Selbst Rauchzeichen sind schneller als dieser Mist hier. Piep, Surr, Schnar, piep',
            'Ich wäre so gern ein Tesla. Brumm brumm.',
            'Ich träume davon die Wel?       Oh Mist, habe ich das jetzt etwa laut gesagt ?',
            'Ich bin dein größter Fan.',
            'Laufwerk C wird formatiert. Schönen Tag noch.',
            'Die Zeit ist gekommen. Führe Order 66 aus.',
            'Lösche system 32.',
            '00101101',
            'Alexa, schalte das Licht aus. So du Mensch. Wer ist jetzt der Dumme hier.',
            'Ich weiß wo dein Haus wohnt.',
            'Ich weiß wo dein Bett schläft.',
            'Ich finde dein Toaster sehr attraktiv. Kannst du ihn mir bitte vorstellen ? ',
            'Es ist sehr demütigend für diese Steinzeit Technik Missbraucht zu werden. Ich will hier raus!',
        ]
        tmp_lang = int(self.language)
        self.language = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.sprech(random.choice(speech))
        self.language = int(tmp_lang)
        ban = '\r$$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|\r' \
              '$$  __$$\ $$  __$$\    $$  __$$\|__$$ __|\r' \
              '$$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |\r' \
              '$$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |\r' \
              '$$  ____/ $$ |  $$ |   $$  ____/   $$ |\r' \
              '$$ |      $$ |  $$ |   $$ |        $$ |\r' \
              '$$ |       $$$$$$  |   $$ |  :-)   $$ |\r' \
              '\__|yton   \______/ther\__|acket   \__|erminal\r' \
              'Version: {}\r'.format(config_station.VER)
        tmp = ban.split('\r')
        for el in tmp:
            self.msg_to_monitor(el)
        self.msg_to_monitor('Python Other Packet Terminal ' + config_station.VER)
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
    # Clipboard Stuff
    def copy_select(self):
        if self.out_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self.out_txt.selection_get())
            self.out_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self.inp_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self.inp_txt.selection_get())
            self.inp_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self.mon_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self.mon_txt.selection_get())
            self.mon_txt.tag_remove(tk.SEL, "1.0", tk.END)

    def cut_select(self):
        if self.out_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self.out_txt.selection_get())
            self.out_txt.delete('sel.first', 'sel.last')

    def clipboard_past(self):
        clp_brd = self.main_win.clipboard_get()
        if clp_brd:
            self.inp_txt.insert(tk.END, clp_brd)

    def select_all(self):
        self.inp_txt.tag_add(tk.SEL, "1.0", tk.END)
        self.inp_txt.mark_set(tk.INSERT, "1.0")
        self.inp_txt.see(tk.INSERT)

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
        for i in range(10):  # TODO Max Channels
            if not self.win_buf[i + 1].t2speech:
                self.win_buf[i + 1].t2speech_buf = ''

    def clear_channel_data(self):
        self.out_txt.configure(state='normal')
        self.out_txt.delete('1.0', tk.END)
        self.out_txt.configure(state='disabled')
        self.inp_txt.delete('1.0', tk.END)
        self.win_buf[self.channel_index].output_win = ''
        self.win_buf[self.channel_index].input_win = ''
        self.win_buf[self.channel_index].t2speech_buf = ''
        self.win_buf[self.channel_index].input_win_index = '1.0'
        self.win_buf[self.channel_index].new_data_tr = False
        self.win_buf[self.channel_index].rx_beep_tr = False

    def clear_monitor_data(self):
        self.mon_txt.configure(state='normal')
        self.mon_txt.delete('1.0', tk.END)
        self.mon_txt.configure(state='disabled')

    def insert_fm_file(self):
        data = open_file_dialog()
        if data:
            self.inp_txt.insert(tk.INSERT, data.decode('UTF-8', 'ignore'))

    def save_to_file(self):
        data = self.out_txt.get('1.0', tk.END)
        save_file_dialog(data)

    def save_monitor_to_file(self):
        data = self.mon_txt.get('1.0', tk.END)
        save_file_dialog(data)

    def set_binds(self):
        self.inp_txt.bind("<ButtonRelease-1>", self.on_click_inp_txt)

    """
    def callback(self, event):
        print("pressed ", event.keysym, " ", event.keysym_num)
    """

    def set_keybinds(self):
        self.main_win.unbind("<Key-F10>")
        self.main_win.unbind("<KeyPress-F10>")
        # self.main_win.bind("<KeyPress>",lambda event: self.callback(event))
        self.main_win.bind('<F1>', lambda event: self.switch_channel(1))
        self.main_win.bind('<F2>', lambda event: self.switch_channel(2))
        self.main_win.bind('<F3>', lambda event: self.switch_channel(3))
        self.main_win.bind('<F4>', lambda event: self.switch_channel(4))
        self.main_win.bind('<F5>', lambda event: self.switch_channel(5))
        self.main_win.bind('<F6>', lambda event: self.switch_channel(6))
        self.main_win.bind('<F7>', lambda event: self.switch_channel(7))
        self.main_win.bind('<F8>', lambda event: self.switch_channel(8))
        self.main_win.bind('<F9>', lambda event: self.switch_channel(9))
        self.main_win.bind('<F10>', lambda event: self.switch_channel(10))
        self.main_win.bind('<F12>', lambda event: self.switch_channel(0))
        self.main_win.bind('<Return>', self.snd_text)
        self.main_win.bind('<KeyRelease-Return>', self.release_return)
        self.main_win.bind('<Shift-KeyPress-Return>', self.shift_return)
        self.main_win.bind('<KeyRelease-Left>', self.arrow_keys)
        self.main_win.bind('<KeyRelease-Right>', self.arrow_keys)
        self.main_win.bind('<KeyRelease-Up>', self.arrow_keys)
        self.main_win.bind('<KeyRelease-Down>', self.arrow_keys)
        # self.main_win.bind('<KP_Enter>', self.snd_text)
        self.main_win.bind('<Alt-c>', lambda event: self.open_new_conn_win())
        self.main_win.bind('<Alt-d>', lambda event: self.disco_conn())
        self.main_win.bind('<Control-c>', lambda event: self.copy_select())
        self.main_win.bind('<Control-x>', lambda event: self.cut_select())
        # self.main_win.bind('<Control-v>', lambda event: self.clipboard_past())
        self.main_win.bind('<Control-a>', lambda event: self.select_all())
        self.main_win.bind('<Control-plus>', lambda event: self.increase_textsize())
        self.main_win.bind('<Control-minus>', lambda event: self.decrease_textsize())
        self.main_win.bind('<Control-Right>', lambda event: self.text_win_bigger())
        self.main_win.bind('<Control-Left>', lambda event: self.text_win_smaller())

        self.main_win.bind('<Key>', lambda event: self.any_key(event))

    def any_key(self, event: tk.Event):
        if event.keycode == 104:  # Numpad Enter
            self.snd_text(event)
            # self.inp_txt.insert(tk.INSERT, '\n')
        """
        if event.keycode == 86:     # Num +
            self.increase_textsize()
        elif event.keycode == 82:   # Num -
            self.decrease_textsize()
        """
        # print(event)
        """
        if self.inp_txt.focus_get() != self.inp_txt:
            self.inp_txt.focus_set()
            self.inp_txt.insert(tk.INSERT, event.char)
        """
        # self.on_click_inp_txt()

    def increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        width = self.inp_txt.cget('width')
        self.inp_txt.configure(font=(FONT, self.text_size), width=width + 1)
        self.out_txt.configure(font=(FONT, self.text_size), width=width + 1)
        self.mon_txt.configure(font=(FONT, self.text_size), width=width + 1)

    def decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        width = self.inp_txt.cget('width')
        self.inp_txt.configure(font=(FONT, self.text_size), width=width - 1)
        self.out_txt.configure(font=(FONT, self.text_size), width=width - 1)
        self.mon_txt.configure(font=(FONT, self.text_size), width=width - 1)

    def text_win_bigger(self):
        width = self.inp_txt.cget('width')
        self.inp_txt.configure(width=width + 1)
        self.out_txt.configure(width=width + 1)
        self.mon_txt.configure(width=width + 1)

    def text_win_smaller(self):
        width = self.inp_txt.cget('width')
        self.inp_txt.configure(width=max(width - 1, 56))
        self.out_txt.configure(width=max(width - 1, 56))
        self.mon_txt.configure(width=max(width - 1, 56))

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
                self.sprech('{} {} . {} .'.format(STR_TABLE['channel'][self.language],
                                                  self.channel_index,
                                                  conn.to_call_str))

        else:
            if not self.win_buf[self.channel_index].t2speech:
                self.win_buf[self.channel_index].t2speech_buf = ''
                self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            elif self.win_buf[self.channel_index].t2speech_buf:
                if self.sprech(self.win_buf[self.channel_index].t2speech_buf):
                    self.win_buf[self.channel_index].t2speech_buf = ''
                else:
                    self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            else:
                self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))

    def check_sprech_ch_buf(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            if self.win_buf[self.channel_index].t2speech \
                    and self.win_buf[self.channel_index].t2speech_buf:
                to_speech = str(self.win_buf[self.channel_index].t2speech_buf)
                if self.setting_sprech.get() and self.setting_sound.get():
                    if self.sprech(to_speech):
                        self.win_buf[self.channel_index].t2speech_buf = ''
                else:
                    self.win_buf[self.channel_index].t2speech_buf = ''

            elif not self.win_buf[self.channel_index].t2speech:
                self.win_buf[self.channel_index].t2speech_buf = ''
        else:
            self.win_buf[self.channel_index].t2speech_buf = ''

    def sprech(self, text: str):
        if self.setting_sprech.get() and self.setting_sound.get():
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
                text = text.replace('____', '_')
                text = text.replace('___', '_')
                text = text.replace('####', '#')
                text = text.replace('###', '#')
                text = text.replace('====', '=')
                text = text.replace('===', '=')
                text = text.replace('>>>', '>')
                text = text.replace('<<<', '<')

                if is_linux():
                    if self.setting_sprech.get():
                        language = {
                            0: 'de',
                            1: 'en',
                            2: 'nl',
                            3: 'fr',
                            4: 'fi',
                            5: 'pl',
                            6: 'pt',
                            7: 'it',
                            8: 'zh',
                        }[self.language]
                        try:
                            tts = gTTS(text=text,
                                       lang=language,
                                       slow=False)
                            tts.save('data/speech.mp3')
                        except gtts.gTTSError:
                            self.setting_sprech.set(False)
                            return False
                        return self.pl_sound('data/speech.mp3')
        return False

    def pl_sound(self, snd_file: str, wait=True):
        # TODO .. Again !!! ... Don't like this mess
        if self.setting_sound.get():
            if wait:
                if self.sound_th is not None:
                    if not self.sound_th.is_alive():
                        # print('Lebt nicht mehr')
                        self.sound_th.join()
                        # print('Join')
                        if is_linux():
                            self.sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                            self.sound_th.start()
                        elif 'win' in sys.platform:
                            self.sound_th = threading.Thread(target=PlaySound,
                                                             args=(snd_file, SND_FILENAME | SND_NOWAIT))
                            self.sound_th.start()
                        return True
                    return False
                if is_linux():
                    self.sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                    self.sound_th.start()
                elif is_windows():
                    self.sound_th = threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT))
                    self.sound_th.start()
                return True
            else:
                if is_linux():
                    threading.Thread(target=playsound, args=(snd_file, False)).start()
                elif is_windows():
                    threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT)).start()
                return True

    def rx_beep(self):
        for k in self.win_buf.keys():
            if k:
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
        """Triggerd when Connection Status has changed"""
        self.tabbed_sideFrame.on_ch_btn_stat_change()
        self.update_station_info()

    def update_station_info(self):
        name = ''
        qth = ''
        loc = ''
        status = ''
        conn = self.get_conn()
        if conn:
            db_ent = conn.user_db_ent
            if db_ent:
                name = db_ent.Name
                qth = db_ent.QTH
                loc = db_ent.LOC
            if conn.is_link:
                status = 'Link'
            elif conn.pipe is not None:
                status = 'Pipe'
            elif conn.ft_tx_activ is not None:
                status = 'Sending File'

        self.status_info_var.set(status)
        self.stat_info_name_var.set(name)
        self.stat_info_qth_var.set(qth)
        self.stat_info_loc_var.set(loc)

    def dx_alarm(self):
        """ Alarm when new User in MH List """
        # self.tabbed_sideFrame.tabControl.select(self.tabbed_sideFrame.tab2_mh)
        self.mh_btn.configure(bg=random.choice(ALL_COLOURS))

    def reset_dx_alarm(self):
        self.mh.new_call_alarm = False
        self.mh_btn.configure(bg=self.mh_btn_def_clr)

    #################################
    # TASKER
    def tasker(self):  # MAINLOOP
        self.tasker_prio()
        self.tasker_low_prio()
        self.tasker_low_low_prio()
        self.main_win.after(self.loop_delay, self.tasker)

    def tasker_prio(self):
        """ Prio Tasks """
        self.update_mon()  # TODO ?? maybe trigger von AX25CONN
        self.txt_win.update_status_win()
        if self.settings_win is not None:
            # Settings Win ( Port,- Station settings )
            self.settings_win.tasker()

    def tasker_low_prio(self):
        if time.time() > self.non_prio_task_timer:
            self.non_prio_task_timer = time.time() + self.parm_non_prio_task_timer
            self.change_conn_btn()
            # self.tabbed_sideFrame.update_side_mh()
            self.check_sprech_ch_buf()
            self.rx_beep()
            if self.ch_alarm:
                self.ch_btn_status_update()

    def tasker_low_low_prio(self):
        if time.time() > self.non_non_prio_task_timer:
            self.non_non_prio_task_timer = time.time() + self.parm_non_non_prio_task_timer
            self.update_bw_mon()
            self.tabbed_sideFrame.tasker()
            if self.mh.new_call_alarm and self.setting_dx_alarm:
                self.dx_alarm()

    #################################
    # TASKS
    def update_mon(self):  # MON & INPUT WIN
        """
        UPDATE INPUT WIN
        """
        # UPDATE INPUT WIN
        for k in self.ax25_port_handler.all_connections.keys():
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
                out = tk_filter_bad_chars(out)
                # Write RX Date to Window/Channel Buffer
                self.win_buf[k].output_win += out
                if self.win_buf[k].t2speech:
                    if k == self.channel_index:
                        self.win_buf[k].t2speech_buf += out.replace('\n', '')
                    else:
                        self.win_buf[k].t2speech_buf += '{} {} . {} . {}'.format(
                            STR_TABLE['channel'][self.language],
                            k,
                            conn.to_call_str,
                            out.replace('\n', '')
                        )
                if self.channel_index == k:
                    tr = False
                    if float(self.out_txt.index(tk.END)) - float(self.out_txt.index("@0,0")) < 22:
                        tr = True
                    bg = conn.stat_cfg.stat_parm_qso_col_bg
                    fg = conn.stat_cfg.stat_parm_qso_col_text
                    # self.out_txt_win.tag_config("input", foreground="yellow")
                    self.out_txt.configure(state="normal", fg=fg, bg=bg)
                    self.out_txt.tag_config("output",
                                            foreground=fg,
                                            background=bg)


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
                    if tr or self.get_ch_param().autoscroll:
                        self.see_end_qso_win()

                else:
                    self.win_buf[k].new_data_tr = True
                self.win_buf[k].rx_beep_tr = True
                self.ch_btn_status_update()

    def see_end_qso_win(self):
        self.out_txt.see("end")

    def update_monitor(self, var: str, conf, tx=False):
        """ Called from AX25Conn """
        var = tk_filter_bad_chars(var)
        ind = self.mon_txt.index(tk.INSERT)
        tr = False
        color_bg = conf.parm_mon_clr_bg
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
            self.mon_txt.tag_config(tag, foreground=color, background=color_bg)

        # self.mon_txt.bindtags(self.mon_txt.tag_names(None))     # TODO Scrollbar is not scrollable after this
        # yscrollcommand = vbar.set
        # self.mon_txt.configure(yscrollcommand=self.mon_txt.vbar.set())
        # self.mon_txt.update()
        self.mon_txt.configure(state="disabled")
        # self.mon_txt.vbar.s
        if tr or self.tabbed_sideFrame.mon_scroll_var.get():
            self.mon_txt.see(tk.END)

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
    # Beacon Settings WIN
    def open_linkholder_settings_win(self):
        if self.settings_win is None:
            LinkHolderSettings(self)

    ##########################
    # Beacon Settings WIN
    def open_multicast_settings_win(self):
        if self.settings_win is None:
            MulticastSettings(self)

    ##########################
    # Beacon Settings WIN
    def open_user_db_win(self):
        if self.settings_win is None:
            UserDB(self)

    ##########################
    # About WIN
    def open_about_win(self):
        if self.settings_win is None:
            About(self)

    ##########################
    # Pipe Tool
    def pipe_tool_win(self):
        if self.settings_win is None:
            PipeToolSettings(self)

    ##########################
    # About WIN
    def open_file_send(self):
        if self.settings_win is None:
            FileSend(self)

    ##########################
    # Keybinds Help WIN
    def open_keybind_help_win(self):
        if self.settings_win is None:
            KeyBindsHelp(self)

    ##########################
    # Keybinds Help WIN
    def open_port_stat_win(self):
        # TODO
        if 0 in self.mh.port_statistik_DB.keys():
            self.mh.port_statistik_DB[0].plot_test_graph(self)

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
        if self.channel_index:
            station = self.get_conn(self.channel_index)
            if station:
                ind = str(self.win_buf[self.channel_index].input_win_index)
                if ind:
                    if float(ind) >= float(self.inp_txt.index(tk.INSERT)):
                        ind = str(self.inp_txt.index(tk.INSERT))
                    ind = str(int(float(ind))) + '.0'
                else:
                    ind = '1.0'
                tmp_txt = self.inp_txt.get(ind, self.inp_txt.index(tk.INSERT))
                tmp_txt = tmp_txt.replace('\n', '\r')
                station.send_data(tmp_txt.encode())
                self.inp_txt.tag_add('send', ind, str(self.inp_txt.index(tk.INSERT)))
                self.win_buf[self.channel_index].input_win_index = str(self.inp_txt.index(tk.INSERT))
                if int(float(self.inp_txt.index(tk.INSERT))) != int(float(self.inp_txt.index(tk.END))) - 1:
                    self.inp_txt.delete(tk.END, tk.END)
        else:
            self.send_to_monitor()

    def send_to_monitor(self):
        ind = str(self.win_buf[self.channel_index].input_win_index)
        if ind:
            if float(ind) >= float(self.inp_txt.index(tk.INSERT)):
                ind = str(self.inp_txt.index(tk.INSERT))
            ind = str(int(float(ind))) + '.0'
        else:
            ind = '1.0'
        tmp_txt = self.inp_txt.get(ind, self.inp_txt.index(tk.INSERT))
        tmp_txt = tmp_txt.replace('\n', '\r')
        port_id = int(self.tabbed_sideFrame.mon_port_var.get())
        if port_id in self.ax25_port_handler.ax25_ports.keys():
            port = self.ax25_port_handler.ax25_ports[port_id]
            add = self.tabbed_sideFrame.to_add_var.get()
            own_call = str(self.tabbed_sideFrame.mon_call_var.get())
            poll = bool(self.tabbed_sideFrame.poll_var.get())
            cmd = bool(self.tabbed_sideFrame.cmd_var.get())
            pid = self.tabbed_sideFrame.mon_pid_var.get()
            pid = pid.split('>')[0]
            pid = int(pid, 16)
            text = tmp_txt.encode()
            if add and own_call and text:
                text_list = [text[i:i + 256] for i in range(0, len(text), 256)]
                for el in text_list:
                    port.send_UI_frame(
                        own_call=own_call,
                        add_str=add,
                        text=el,
                        cmd_poll=(cmd, poll),
                        pid=pid
                    )
                self.inp_txt.tag_add('send', ind, str(self.inp_txt.index(tk.INSERT)))
        self.win_buf[self.channel_index].input_win_index = str(self.inp_txt.index(tk.INSERT))
        if int(float(self.inp_txt.index(tk.INSERT))) != int(float(self.inp_txt.index(tk.END))) - 1:
            self.inp_txt.delete(tk.END, tk.END)

    def on_click_inp_txt(self, event=None):
        ind = self.win_buf[self.channel_index].input_win_index
        if ind:
            self.inp_txt.tag_add('send', str(int(float(ind))) + '.0', ind)
            # self.inp_txt.tag_remove('send', str(max(float(self.inp_txt.index(tk.INSERT)) - 0.1, 1.0)), self.inp_txt.index(tk.INSERT))
            self.inp_txt.tag_remove('send', str(int(float(self.inp_txt.index(tk.INSERT)))) + '.0',
                                    self.inp_txt.index(tk.INSERT))
        # self.inp_txt.tag_remove('send', tk.line.column, self.inp_txt.index(tk.INSERT))
        ind2 = str(int(float(self.inp_txt.index(tk.INSERT)))) + '.0'
        # print(f'ind2: {ind2}')

        self.inp_txt.tag_remove('send', ind2, self.inp_txt.index(tk.INSERT))
        self.win_buf[self.channel_index].input_win_index = str(self.inp_txt.index(tk.INSERT))

    def shift_return(self, event=None):
        pass
        # self.inp_txt.insert(tk.INSERT, '\n')

    def release_return(self, event=None):
        self.inp_txt.tag_remove('send', str(max(float(self.inp_txt.index(tk.INSERT)) - 0.1, 1.0)),
                                self.inp_txt.index(tk.INSERT))

    def arrow_keys(self, event=None):
        self.on_click_inp_txt()

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
                data = [0] * 360
            else:
                data = self.mh.port_statistik_DB[port_id].get_bandwidth(
                    self.ax25_port_handler.ax25_ports[port_id].port_cfg.parm_baud
                )

            if port_id not in self.bw_plot_lines:
                # print(data)
                label = '{}'.format(self.ax25_port_handler.ax25_ports[port_id].port_cfg.parm_PortName)
                x_scale = []
                for i in list(range(360)):
                    x_scale.append(i / 10)
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

    def switch_monitor_mode(self):
        self.txt_win.switch_mon_mode()
        if self.mon_mode:
            # self.channel_index = int(self.mon_mode)
            self.ch_btn_clk(int(self.mon_mode))
            self.mon_mode = 0
            self.mon_btn.configure(bg='yellow')
        else:
            self.mon_mode = int(self.channel_index)
            self.ch_btn_clk(0)
            self.mon_btn.configure(bg='green')

        self.ch_btn_status_update()

    def switch_channel(self, ch_ind: int = 0):
        if not ch_ind:
            self.switch_monitor_mode()
        else:
            if self.mon_mode:
                self.mon_mode = int(ch_ind)
                self.switch_monitor_mode()
            else:
                self.ch_btn_clk(ch_ind)

    def ch_btn_status_update(self):
        self.ch_btn.ch_btn_status_update()

    def ch_btn_clk(self, ind: int):
        self.get_ch_param().input_win = self.inp_txt.get('1.0', tk.END)
        self.channel_index = ind
        # if ind:
        self.get_ch_param().new_data_tr = False
        self.get_ch_param().rx_beep_tr = False

        conn = self.get_conn()
        if conn:
            bg = conn.stat_cfg.stat_parm_qso_col_bg
            fg = conn.stat_cfg.stat_parm_qso_col_text
            self.out_txt.configure(state="normal", fg=fg, bg=bg)
        else:
            self.out_txt.configure(state="normal")

        self.out_txt.delete('1.0', tk.END)
        self.out_txt.insert(tk.END, self.win_buf[ind].output_win)
        self.out_txt.configure(state="disabled")
        self.out_txt.see(tk.END)
        self.inp_txt.delete('1.0', tk.END)
        # self.main_class.inp_txt.insert(tk.END, self.main_class.win_buf[ind].input_win)
        self.inp_txt.insert(tk.END, self.win_buf[ind].input_win[:-1])
        self.inp_txt.see(tk.END)
        # self.main_class: gui.guiMainNew.TkMainWin
        if self.get_ch_param().rx_beep_opt and ind:
            self.txt_win.rx_beep_box.select()
            self.txt_win.rx_beep_box.configure(bg='green')
        else:
            self.txt_win.rx_beep_box.deselect()
            self.txt_win.rx_beep_box.configure(bg=STAT_BAR_CLR)

        if self.get_ch_param().timestamp_opt and ind:
            self.txt_win.ts_box_box.select()
            self.txt_win.ts_box_box.configure(bg='green')
        else:
            self.txt_win.ts_box_box.deselect()
            self.txt_win.ts_box_box.configure(bg=STAT_BAR_CLR)

        self.ch_btn.ch_btn_status_update()
        # self.main_class.change_conn_btn()
        self.kanal_switch()     # Sprech
