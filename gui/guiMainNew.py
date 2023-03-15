import datetime
import time
import tkinter as tk
from tkinter import ttk, Menu
import logging
import threading
import sys

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
from config_station import VER

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
        self.ch_alarm = False
        self.ch_alarm_sound_one_time = False
        self.channel_index = 1
        self.mon_mode = False
        self.non_prio_task_timer = time.time()
        ####################
        # GUI PARAM
        self.parm_btn_blink_time = 0.3
        self.parm_rx_beep_cooldown = 1.5
        self.parm_non_prio_task_timer = 0.5
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
        #self.main_win.rowconfigure(1, minsize=0, weight=1)     # BTN SIDE
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
        # self.MenuHelp.add_command(label="Über", command=lambda: False, underline=0)
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
                                bg="yellow", width=8, command=self.MH_win)

        self.mh_btn.place(x=5, y=45)
        self.mon_btn = tk.Button(self.side_btn_frame_top,
                              text="Monitor",
                              bg="yellow", width=8, command=self.txt_win.switch_mon_mode)
        self.mon_btn.place(x=110, y=45)

        self.tabbed_sideFrame = SideTabbedFrame(self)
        self.setting_sound = self.tabbed_sideFrame.sound_on
        self.setting_bake = self.tabbed_sideFrame.bake_on
        self.setting_rx_echo = self.tabbed_sideFrame.rx_echo_on
        ############################
        # Windows
        self.new_conn_win = None
        self.settings_win = None
        ###########################
        # Init
        # set GUI Var
        self.ax25_port_handler.set_gui(self)
        # set Ch Btn Color
        self.ch_btn_status_update()
        # set KEY BINDS
        self.set_keybinds()
        ####
        # TEST
        # self.open_rx_echo_settings_win()
        # print(self.mon_txt.vbar.bindtags(None))
        #######################
        # LOOP
        self.monitor_start_msg()
        self.main_win.after(LOOP_DELAY, self.tasker)
        self.main_win.mainloop()

    def __del__(self):
        # self.disco_all()
        # self.ax25_port_handler.close_all()
        pass

    def destroy_win(self):
        self.ax25_port_handler.close_all()
        self.main_win.quit()
        # self.main_class.settings_win = None

    def monitor_start_msg(self):
        ban = '\r$$$$$$$\   $$$$$$\     $$$$$$$\ $$$$$$$$|\r' \
              '$$  __$$\ $$  __$$\    $$  __$$\|__$$ __|\r' \
              '$$ |  $$ |$$ /  $$ |   $$ |  $$ |  $$ |\r' \
              '$$$$$$$  |$$ |  $$ |   $$$$$$$  |  $$ |\r' \
              '$$  ____/ $$ |  $$ |   $$  ____/   $$ |\r' \
              '$$ |      $$ |  $$ |   $$ |        $$ |\r' \
              '$$ |       $$$$$$  |   $$ |        $$ |\r' \
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
        # print(event)
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

    def change_conn_btn(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            self.conn_btn.configure(bg="red", text="Disconnect", command=self.disco_conn)
        else:
            self.conn_btn.configure(text="New Conn", bg="green", command=self.open_new_conn_win)

    ###############
    # Sound
    def pl_sound(self, snd_file: str):
        if self.setting_sound.get():
            if 'linux' in sys.platform:
                threading.Thread(target=playsound, args=(snd_file,)).start()
            elif 'win' in sys.platform:
                threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT)).start()

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
                            self.pl_sound('data/sound/rx_beep.wav')

    def new_conn_snd(self):
        self.pl_sound('data/sound/conn_alarm.wav')

    def disco_snd(self):
        self.pl_sound('data/sound/disco_alarm.wav')
    # Sound Ende
    #################
    # no WIN FNC
    ##########################

    def on_channel_status_change(self):
        """Triggerd when Connection Status has change"""
        self.tabbed_sideFrame.update_stat_settings()

    def tasker(self):  # MAINLOOP
        ########################################
        # Check Boxes ( RX-BEEP and TimeStamp )
        rx_beep_check = self.txt_win.rx_beep_var.get()
        if rx_beep_check:
            self.txt_win.rx_beep_box.configure(bg='green', activebackground='green')
        else:
            self.txt_win.rx_beep_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.get_ch_param().rx_beep_opt = rx_beep_check
        ts_check = self.txt_win.ts_box_var.get()
        if ts_check:
            self.txt_win.ts_box_box.configure(bg='green', activebackground='green')
        else:
            self.txt_win.ts_box_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.get_ch_param().timestamp_opt = ts_check
        #############################################
        # Settings Win ( Port,- Station settings )
        if self.settings_win is not None:
            self.settings_win.tasker()
        #####################
        # Prio TASKS ########
        self.update_mon()  # TODO trigger von AX25CONN
        self.txt_win.update_status_win()
        if self.ch_alarm:
            self.ch_btn_status_update()
        ######################
        # Non Prio ###########
        if time.time() > self.non_prio_task_timer:
            self.non_prio_task_timer = time.time() + self.parm_non_prio_task_timer
            self.change_conn_btn()
            self.tabbed_sideFrame.update_side_mh()
            self.rx_beep()
        # Loop back
        self.main_win.after(LOOP_DELAY, self.tasker)
    """
    def cli_echo(self, data: str, channel_index: int):
        print(type(data))
        print(data + ' <GUI> ' + str(channel_index))
        # CLI Echo . Called from CLI
        # Write RX Date to Window/Channel Buffer
        if channel_index and self.get_conn(channel_index):
            self.win_buf[channel_index].output_win += data
            if self.channel_index == channel_index:
                tr = False
                if float(self.out_txt.index(tk.END)) - float(self.out_txt.index("@0,0")) < 22:
                    tr = True
                self.out_txt.configure(state="normal")
                self.out_txt.insert('end', data)
                self.out_txt.configure(state="disabled")
                if tr:
                    self.out_txt.see("end")
            else:
                self.win_buf[channel_index].new_data_tr = True
            self.win_buf[channel_index].rx_beep_tr = True
            self.ch_btn_status_update()
    """
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
                    if not conn.my_digi_call:
                        inp = str(conn.tx_buf_guiData.decode('UTF-8', 'ignore')) \
                            .replace('\r', '\n') \
                            .replace('\r\n', '\n') \
                            .replace('\n\r', '\n')
                        conn.tx_buf_guiData = b''
                        # Write RX Date to Window/Channel Buffer
                        self.win_buf[k].output_win += inp
                        out = str(conn.rx_buf_rawData.decode('UTF-8', 'ignore')) \
                            .replace('\r', '\n') \
                            .replace('\r\n', '\n') \
                            .replace('\n\r', '\n')
                        conn.rx_buf_rawData = b''
                        # Write RX Date to Window/Channel Buffer
                        self.win_buf[k].output_win += out

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

    # ##############
    # DISCO
    def disco_conn(self):
        station = self.get_conn(self.channel_index)
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

    def disco_all(self):
        for ch_id in range(1,11):
            station = self.get_conn(ch_id)
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
        station = self.get_conn(self.channel_index)

        if station:
            ind = str(float(self.inp_txt.index(tk.INSERT)) - 1)
            tmp_txt = self.inp_txt.get(ind, self.inp_txt.index(tk.INSERT))
            tmp_txt = tmp_txt.replace('\n', '').replace('\r', '')
            # Send it to Connection/Station TX Buffer
            station.tx_buf_rawData += (tmp_txt + '\r').encode()
            """
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
            """
            # configuring a tag called start


    # SEND TEXT OUT
    ###################
    # MH WIN
    def MH_win(self):
        """MH WIN"""
        MHWin(self.mh)

