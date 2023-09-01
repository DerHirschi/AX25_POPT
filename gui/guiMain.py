import datetime
import gc
import logging
import random
import time
import tkinter as tk
from tkinter import ttk, Menu, Checkbutton, TclError, scrolledtext, Label
import threading
import sys

import gtts
from gtts import gTTS

from ax25.ax25dec_enc import PIDByte
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25Statistics import MH_LIST
from ax25.ax25monitor import monitor_frame_inp

from fnc.str_fnc import tk_filter_bad_chars, try_decode, get_time_delta, format_number, conv_timestamp_delta, \
    get_kb_str_fm_bytes, conv_time_DE_str
from gui.guiAISmon import AISmonitor
from gui.guiAPRS_Settings import APRSSettingsWin
from gui.guiAPRS_pn_msg import APRS_msg_SYS_PN
from gui.guiFT_Manager import FileTransferManager
from gui.guiLocatorCalc import LocatorCalculator
from gui.guiPipeToolSettings import PipeToolSettings
from gui.guiPlotPort import PlotWindow
from gui.guiPriv import PrivilegWin

from gui.guiUserDBoverview import UserDBtreeview
from gui.guiMulticastSettings import MulticastSettings
from gui.guiChBtnFrm import ChBtnFrm
from gui.guiMH import MHWin
from gui.guiNewConnWin import NewConnWin
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
from constant import LANGUAGE, ALL_COLOURS, FONT, POPT_BANNER, WELCOME_SPEECH, VER, CFG_clr_sys_msg, STATION_TYPS, \
    ENCODINGS, TEXT_SIZE_STATUS, TXT_BACKGROUND_CLR, TXT_OUT_CLR, TXT_INP_CLR, TXT_INP_CURSOR_CLR, TXT_MON_CLR, \
    STAT_BAR_CLR, STAT_BAR_TXT_CLR, FONT_STAT_BAR
from string_tab import STR_TABLE
from fnc.os_fnc import is_linux, is_windows, get_root_dir
from fnc.gui_fnc import get_all_tags, set_all_tags

if is_linux():
    from playsound import playsound
elif is_windows():
    from winsound import PlaySound, SND_FILENAME, SND_NOWAIT


class ChVars(object):
    def __init__(self):
        self.output_win = ''
        self.output_win_tags = {}
        self.input_win = ''
        self.input_win_tags = {}
        self.input_win_index = '1.0'
        self.input_win_cursor_index = tk.INSERT
        self.new_data_tr = False
        self.rx_beep_tr = False
        self.rx_beep_cooldown = time.time()
        self.rx_beep_opt = None
        self.timestamp_opt = None
        self.t2speech = False
        self.t2speech_buf = ''
        self.autoscroll = True
        self.qso_tag_name = ''
        self.qso_tag_fg = ''
        self.qso_tag_bg = ''
        # self.hex_output = True


class SideTabbedFrame:
    def __init__(self, main_cl):
        self._main_win = main_cl
        self._lang = int(main_cl.language)
        self.style = main_cl.style
        self.ch_index = main_cl.channel_index

        self._tab_side_frame = tk.Frame(
            main_cl.get_side_frame(),
            # width=300,
            height=400
        )
        self._tab_side_frame.grid(row=4, column=0, columnspan=6, pady=10, sticky="nsew")
        self._tabControl = ttk.Notebook(
            self._tab_side_frame,
            height=300,
            # width=500
        )

        tab1_kanal = ttk.Frame(self._tabControl)
        # self.tab1_1_RTT = ttk.Frame(self._tabControl)
        self.tab2_mh = tk.Frame(self._tabControl)
        # self.tab2_mh.bind("<Button-1>", self.reset_dx_alarm)
        self.tab2_mh_def_bg_clr = self.tab2_mh.cget('bg')
        self.tab4_settings = ttk.Frame(self._tabControl)
        self.tab5_ch_links = ttk.Frame(self._tabControl)  # TODO
        self.tab6_monitor = ttk.Frame(self._tabControl)

        self._tabControl.add(tab1_kanal, text='Kanal')
        self._tabControl.add(self.tab2_mh, text='MH')
        # tab3 = ttk.Frame(self._tabControl)                         # TODO
        # self._tabControl.add(tab3, text='Ports')                   # TODO
        self._tabControl.add(self.tab4_settings, text='Global')
        self._tabControl.add(self.tab6_monitor, text='Monitor')

        # self._tabControl.add(self.tab5_ch_links, text='CH-Echo')   # TODO
        self._tabControl.pack(expand=0, fill="both")
        self._tabControl.select(self.tab2_mh)
        ################################################
        # Kanal
        parm_y = 20
        m_f_label = tk.Label(tab1_kanal, text='Max Pac:')
        self.max_frame_var = tk.StringVar(tab1_kanal)
        self.max_frame_var.set('1')
        self.max_frame = tk.Spinbox(tab1_kanal,
                                    from_=1,
                                    to=7,
                                    increment=1,
                                    width=2,
                                    textvariable=self.max_frame_var,
                                    command=self.set_max_frame,
                                    state='disabled')
        m_f_label.place(x=10, y=parm_y)
        self.max_frame.place(x=10 + 80, y=parm_y)
        parm_y = 55
        p_l_label = tk.Label(tab1_kanal, text='Pac Len:')
        self.pac_len_var = tk.IntVar(tab1_kanal)
        self.pac_len_var.set(128)
        vals = []
        for i in range(255):
            vals.append(str(i + 1))
        self.pac_len = tk.ttk.Combobox(tab1_kanal,
                                       width=4,
                                       textvariable=self.pac_len_var,
                                       values=vals,
                                       state='disabled')
        self.pac_len.bind("<<ComboboxSelected>>", self.set_pac_len)
        p_l_label.place(x=10, y=parm_y)
        self.pac_len.place(x=10 + 80, y=parm_y)
        # t2 Auto Checkbutton
        parm_y = 90
        _label = tk.Label(tab1_kanal, text='T2:')
        self.t2_var = tk.StringVar(tab1_kanal)
        self.t2_var.set(str(1700))
        val_list = []

        for i in range(10, 60):
            # 500 - 3000
            val_list.append(str(i * 50))

        self.t2 = tk.ttk.Combobox(tab1_kanal,
                                  width=4,
                                  textvariable=self.t2_var,
                                  values=val_list,
                                  state='disabled')
        self.t2.bind("<<ComboboxSelected>>", self._set_t2)
        _label.place(x=10, y=parm_y)
        self.t2.place(x=50, y=parm_y)

        self.t2_auto_var = tk.BooleanVar(tab1_kanal)
        self.t2_auto = tk.Checkbutton(tab1_kanal,
                                      text='T2-Auto',
                                      variable=self.t2_auto_var,
                                      state='disabled',
                                      command=self._chk_t2auto
                                      )
        self.t2_auto.place(x=10, y=parm_y + 35)

        # RNR Checkbutton
        parm_y = 150
        self.rnr_var = tk.BooleanVar(tab1_kanal)

        self.rnr = tk.Checkbutton(tab1_kanal,
                                  text='RNR',
                                  variable=self.rnr_var,
                                  command=self._chk_rnr)
        self.rnr.place(x=10, y=parm_y)
        # Sprech
        parm_y = 200
        self.t2speech_var = tk.BooleanVar(tab1_kanal)

        self.t2speech = tk.Checkbutton(tab1_kanal,
                                       text='Sprachausgabe',
                                       variable=self.t2speech_var,
                                       command=self.chk_t2speech)
        self.t2speech.place(x=10, y=parm_y)
        self.t2speech_var.set(self._main_win.get_ch_param().t2speech)
        # Autoscroll
        parm_y = 225
        self.autoscroll_var = tk.BooleanVar(tab1_kanal)

        self.autoscroll = tk.Checkbutton(tab1_kanal,
                                         text='Autoscroll',
                                         variable=self.autoscroll_var,
                                         command=self.chk_autoscroll
                                         )
        self.autoscroll.place(x=10, y=parm_y)
        self.autoscroll_var.set(self._main_win.get_ch_param().autoscroll)

        # Link Holder
        parm_y = 175
        self.link_holder_var = tk.BooleanVar(tab1_kanal)
        self.link_holder = tk.Checkbutton(tab1_kanal,
                                          text='Linkhalter',
                                          variable=self.link_holder_var,
                                          command=self._chk_link_holder
                                          )
        self.link_holder.place(x=10, y=parm_y)

        clear_ch_data_btn = tk.Button(tab1_kanal,
                                      text='Säubern',
                                      command=self._main_win.clear_channel_data
                                      )
        clear_ch_data_btn.place(x=140, y=135)

        link_holder_settings_btn = tk.Button(tab1_kanal,
                                             text='Linkhalter',
                                             command=self._main_win.open_link_holder_sett
                                             )
        link_holder_settings_btn.place(x=140, y=165)
        # RTT
        self.rtt_best = tk.Label(tab1_kanal, text='')
        self.rtt_worst = tk.Label(tab1_kanal, text='')
        self.rtt_avg = tk.Label(tab1_kanal, text='')
        self.rtt_last = tk.Label(tab1_kanal, text='')

        self.rtt_best.place(x=170, y=10)
        self.rtt_worst.place(x=170, y=35)
        self.rtt_avg.place(x=170, y=60)
        self.rtt_last.place(x=170, y=85)

        ##########################################
        # Kanal Rechts / Status / FT
        ttk.Separator(tab1_kanal, orient='vertical').place(x=280, rely=0.05, relheight=0.9, relwidth=0.6)
        ##########################################

        # Conn Dauer
        _x = 290
        _y = 20
        self.conn_durration_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self.conn_durration_var).place(x=_x, y=_y)
        self.conn_durration_var.set('--:--:--')
        #### conn_durration_var
        # TX Buffer
        _x = 290
        _y = 45
        self.tx_buff_var = tk.StringVar(tab1_kanal)
        self.tx_buff_lable = tk.Label(tab1_kanal, textvariable=self.tx_buff_var)
        self.tx_buff_var.set('')
        self.tx_buff_lable.place(x=_x, y=_y)
        # TX Gesamt
        _x = 290
        _y = 70
        self.tx_count_var = tk.StringVar(tab1_kanal)
        self.tx_count_lable = tk.Label(tab1_kanal, textvariable=self.tx_count_var)
        self.tx_count_var.set('')
        self.tx_count_lable.place(x=_x, y=_y)
        # RX Gesamt
        _x = 290
        _y = 95
        self.rx_count_var = tk.StringVar(tab1_kanal)
        self.rx_count_lable = tk.Label(tab1_kanal, textvariable=self.rx_count_var)
        self.rx_count_var.set('')
        self.rx_count_lable.place(x=_x, y=_y)

        # Status /Pipe/Link/File-RX/File-TX
        self.status_label_var = tk.StringVar(tab1_kanal)
        self.status_label = tk.Label(tab1_kanal, fg='red', textvariable=self.status_label_var)
        font = self.status_label.cget('font')
        self.status_label.configure(font=(font[0], 12))
        self.status_label.place(x=290, y=120)
        ######################
        ttk.Separator(tab1_kanal, orient=tk.HORIZONTAL).place(x=281, y=150, relheight=0.6, relwidth=0.9)
        #####################
        # Progress bar
        # tk.Label(tab1_kanal, text='File Transfer').place(x=380, y=160)
        _x = 300
        _y = 170
        self.ft_progress = tk.ttk.Progressbar(tab1_kanal,
                                              orient=tk.HORIZONTAL,
                                              length=150,
                                              mode='determinate',
                                              )
        self.ft_progress.place(x=_x, y=_y)
        self.ft_progress.bind('<Button-1>', self._main_win.open_ft_manager)
        self.ft_progress['value'] = 0
        self.ft_progress_var = tk.StringVar(tab1_kanal)
        self.ft_size_var = tk.StringVar(tab1_kanal)
        self.ft_duration_var = tk.StringVar(tab1_kanal)
        self.ft_bps_var = tk.StringVar(tab1_kanal)
        self.ft_next_tx_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self.ft_progress_var).place(x=_x + 160, y=_y)
        tk.Label(tab1_kanal, textvariable=self.ft_size_var).place(x=_x , y=_y + 25)
        tk.Label(tab1_kanal, textvariable=self.ft_duration_var).place(x=_x , y=_y + 50)
        tk.Label(tab1_kanal, textvariable=self.ft_bps_var).place(x=_x , y=_y + 75)
        tk.Label(tab1_kanal, textvariable=self.ft_next_tx_var).place(x=_x + 160, y=_y + 75)
        # self.ft_progress_var.set(f"--- %")
        # self.ft_size_var.set(f"Size: 10.000,0 / 20.00,0 kb")
        # self.ft_duration_var.set(f"Time: 00:00:00 / 00:00:00")
        # self.ft_bps_var.set(f"BPS: 100.000")
        ################################
        # MH ##########################
        # TREE
        self.tab2_mh.columnconfigure(0, minsize=300, weight=1)

        columns = (
            'mh_last_seen',
            'mh_call',
            'mh_port',
            'mh_nPackets',
            'mh_route',
        )

        self.tree = ttk.Treeview(self.tab2_mh, columns=columns, show='headings')
        self.tree.grid(row=0, column=0, sticky='nsew')

        self.tree.heading('mh_last_seen', text='Zeit')
        self.tree.heading('mh_call', text='Call')
        self.tree.heading('mh_port', text='Port')
        self.tree.heading('mh_nPackets', text='PACK')
        self.tree.heading('mh_route', text='Route')
        self.tree.column("mh_last_seen", anchor=tk.CENTER, stretch=tk.NO, width=90)
        self.tree.column("mh_call", stretch=tk.NO, width=100)
        self.tree.column("mh_port", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self.tree.column("mh_nPackets", anchor=tk.CENTER, stretch=tk.NO, width=60)
        self.tree.column("mh_route", stretch=tk.YES, width=180)

        self.tree_data = []
        self.last_mh_ent = []
        self._update_side_mh()
        self.tree.bind('<<TreeviewSelect>>', self._entry_selected)

        # Settings ##########################
        # Global Sound
        self.sound_on = tk.BooleanVar(self.tab4_settings)
        Checkbutton(self.tab4_settings,
                    text="Sound",
                    variable=self.sound_on,
                    ).place(x=10, y=10)
        # self.sound_on.set(True)
        # Global Sprech
        self.sprech_on = tk.BooleanVar(self.tab4_settings)
        sprech_btn = Checkbutton(self.tab4_settings,
                                 text="Sprachausgabe",
                                 variable=self.sprech_on,
                                 command=self._chk_sprech_on
                                 )
        sprech_btn.place(x=10, y=35)
        if is_linux():
            self.sprech_on.set(True)
        else:
            self.sprech_on.set(False)
            sprech_btn.configure(state='disabled')

        # Global Bake
        self.bake_on = tk.BooleanVar(self.tab4_settings)
        Checkbutton(self.tab4_settings,
                    text="Baken",
                    variable=self.bake_on,
                    ).place(x=10, y=60)
        self.bake_on.set(True)
        # self.bake_on.set(True)
        # DX Alarm  > dx_alarm_on
        self.dx_alarm_on = tk.BooleanVar(self.tab4_settings)
        _chk_btn = Checkbutton(self.tab4_settings,
                               text="DX-Alarm",
                               variable=self.dx_alarm_on,
                               command=self._chk_dx_alarm,
                               # state='disabled'
                               )
        _chk_btn.place(x=10, y=85)

        # RX ECHO
        self.rx_echo_on = tk.BooleanVar(self.tab4_settings)
        _chk_btn = Checkbutton(self.tab4_settings,
                               text="RX-Echo",
                               variable=self.rx_echo_on,
                               )
        _chk_btn.place(x=10, y=115)

        ############
        # CH ECHO
        self.chk_btn_default_clr = _chk_btn.cget('bg')
        self.ch_echo_vars = {}
        #################
        #################
        # Monitor Frame
        # Address
        _x = 10
        _y = 10
        self.to_add_var = tk.StringVar(self.tab6_monitor)
        tk.Label(self.tab6_monitor, text=f"{STR_TABLE['to'][self._lang]}:").place(x=_x, y=_y)
        self.to_add_ent = tk.Entry(self.tab6_monitor, textvariable=self.to_add_var)
        self.to_add_ent.place(x=_x + 40, y=_y)

        # CMD/RPT
        _x = 10
        _y = 80
        self.cmd_var = tk.BooleanVar(self.tab6_monitor)
        self.cmd_ent = tk.Checkbutton(self.tab6_monitor,
                                      variable=self.cmd_var,
                                      text='CMD/RPT')
        self.cmd_ent.place(x=_x, y=_y)

        # Poll
        _x = 10
        _y = 105
        self.poll_var = tk.BooleanVar(self.tab6_monitor)
        self.poll_ent = tk.Checkbutton(self.tab6_monitor,
                                       variable=self.poll_var,
                                       text='Poll')
        self.poll_ent.place(x=_x, y=_y)

        # Port
        _x = 40
        _y = 140
        tk.Label(self.tab6_monitor, text=f"{STR_TABLE['port'][self._lang]}:").place(x=_x, y=_y)
        self.mon_port_var = tk.StringVar(self.tab6_monitor)
        self.mon_port_var.set('0')
        _vals = ['0']
        if PORT_HANDLER.get_all_ports().keys():
            _vals = [str(x) for x in list(PORT_HANDLER.get_all_ports().keys())]
        self.mon_port_ent = tk.ttk.Combobox(self.tab6_monitor,
                                            width=4,
                                            textvariable=self.mon_port_var,
                                            values=_vals,
                                            )
        self.mon_port_ent.place(x=_x + 50, y=_y)
        self.mon_port_ent.bind("<<ComboboxSelected>>", self._chk_mon_port)
        # Calls
        _x = 40
        _y = 175
        self.mon_call_var = tk.StringVar(self.tab6_monitor)
        _vals = []
        # if self.main_win.ax25_port_handler.ax25_ports.keys():
        #     _vals = [str(x) for x in list(self.main_win.ax25_port_handler.ax25_ports.keys())]
        self.mon_call_ent = tk.ttk.Combobox(self.tab6_monitor,
                                            width=9,
                                            textvariable=self.mon_call_var,
                                            values=_vals,
                                            )
        self.mon_call_ent.place(x=_x, y=_y)

        # Auto Scrolling
        _x = 10
        _y = 210
        self.mon_scroll_var = tk.BooleanVar(self.tab6_monitor)
        self.mon_scroll_ent = tk.Checkbutton(self.tab6_monitor,
                                             variable=self.mon_scroll_var,
                                             text=STR_TABLE['scrolling'][self._lang])
        self.mon_scroll_ent.place(x=_x, y=_y)

        # PID
        _x = 10
        _y = 45
        self.mon_pid_var = tk.StringVar(self.tab6_monitor)
        tk.Label(self.tab6_monitor, text='PID:').place(x=_x, y=_y)
        pid = PIDByte()
        pac_types = dict(pid.pac_types)
        _vals = []
        for x in list(pac_types.keys()):
            pid.pac_types[int(x)]()
            _vals.append(f"{str(hex(x)).upper()}>{pid.flag}")
        self.mon_pid_ent = tk.ttk.Combobox(self.tab6_monitor,
                                           width=20,
                                           values=_vals,
                                           textvariable=self.mon_pid_var)
        self.mon_pid_var.set(_vals[0])
        self.mon_pid_ent.place(x=_x + 40, y=_y)
        # self.pac_len.bind("<<ComboboxSelected>>", self.set_pac_len)
        # Monitor RX-Filter Ports
        self.mon_port_on_vars = {}
        all_ports = PORT_HANDLER.get_all_ports()
        for port_id in all_ports:
            self.mon_port_on_vars[port_id] = tk.BooleanVar(self.tab6_monitor)
            _x = 170
            _y = 80 + (25 * port_id)
            tk.Checkbutton(self.tab6_monitor,
                           text=f"Port {port_id}",
                           variable=self.mon_port_on_vars[port_id],
                           command=self._chk_mon_port_filter
                           ).place(x=_x, y=_y)
            self.mon_port_on_vars[port_id].set(all_ports[port_id].monitor_out)

        ##################
        # Tasker
        self._tasker_dict = {
            0: self._update_rtt,
            1: self._update_side_mh,
            # 5: self.update_ch_echo,
        }

        self._chk_mon_port()
        self._update_ch_echo()

    """
    def reset_dx_alarm(self, event=None):
        self._main_win.reset_dx_alarm()
        # self.tab2_mh.configure(bg=self.tab2_mh_def_bg_clr)
    """

    def _update_ch_echo(self):

        # TODO AGAIN !!
        _tab = self.tab5_ch_links
        akt_ch_id = self._main_win.channel_index
        _var = tk.BooleanVar(_tab)
        for ch_id in list(self.ch_echo_vars.keys()):
            if ch_id not in list(PORT_HANDLER.get_all_connections().keys()):
                self.ch_echo_vars[ch_id][1].destroy()
                del self.ch_echo_vars[ch_id]
        for ch_id in list(PORT_HANDLER.get_all_connections().keys()):
            conn = PORT_HANDLER.get_all_connections()[ch_id]
            if ch_id not in self.ch_echo_vars.keys():
                chk_bt_var = tk.IntVar()
                chk_bt = tk.Checkbutton(_tab,
                                        text=conn.to_call_str,
                                        variable=chk_bt_var,
                                        onvalue=int(ch_id),
                                        offvalue=0,
                                        command=self._chk_ch_echo
                                        )
                chk_bt.place(x=10, y=10 + (28 * (ch_id - 1)))
                # _chk_bt.configure(state='disabled')
                tmp = chk_bt_var, chk_bt
                self.ch_echo_vars[ch_id] = tmp
            else:
                self.ch_echo_vars[ch_id][1].configure(state='normal')
                self.ch_echo_vars[ch_id][1].configure(text=conn.to_call_str)
            if ch_id != akt_ch_id:
                self.ch_echo_vars[ch_id][1].configure(state='normal')
            else:
                self.ch_echo_vars[ch_id][1].configure(state='disabled')
            if akt_ch_id in self.ch_echo_vars.keys():
                if self.ch_echo_vars[ch_id][0].get() and self.ch_echo_vars[akt_ch_id][0].get():
                    self.ch_echo_vars[ch_id][1].configure(bg='green1')
                    self.ch_echo_vars[akt_ch_id][1].configure(bg='green1')
                else:
                    self.ch_echo_vars[ch_id][1].configure(bg=self.chk_btn_default_clr)
                    self.ch_echo_vars[akt_ch_id][1].configure(bg=self.chk_btn_default_clr)

        # self.sound_on.set(1)

    def _chk_ch_echo(self):
        # self.main_win.channel_index
        for ch_id in list(self.ch_echo_vars.keys()):
            _vars = self.ch_echo_vars[ch_id]
            if ch_id != self._main_win.channel_index:
                if _vars[0].get() and self.ch_echo_vars[self._main_win.channel_index][0].get():
                    PORT_HANDLER.get_all_connections()[ch_id].ch_echo.append(PORT_HANDLER.get_all_connections()[self._main_win.channel_index])
                    PORT_HANDLER.get_all_connections()[self._main_win.channel_index].ch_echo.append(PORT_HANDLER.get_all_connections()[ch_id])
                else:
                    if PORT_HANDLER.get_all_connections()[self._main_win.channel_index] in PORT_HANDLER.get_all_connections()[ch_id].ch_echo:
                        PORT_HANDLER.get_all_connections()[ch_id].ch_echo.remove(PORT_HANDLER.get_all_connections()[self._main_win.channel_index])

                    if PORT_HANDLER.get_all_connections()[ch_id] in PORT_HANDLER.get_all_connections()[self._main_win.channel_index].ch_echo:
                        PORT_HANDLER.get_all_connections()[self._main_win.channel_index].ch_echo.remove(PORT_HANDLER.get_all_connections()[ch_id])

        """   
        for ch_id in list(self.ch_echo_vars.keys()):
            _vars = self.ch_echo_vars[ch_id]
            if _vars[0].get() and self.ch_echo_vars[self.main_win.channel_index][0].get():
                self.ch_echo_vars[ch_id][1].configure(bg='green1')
                # self.ch_echo_vars[self.main_win.channel_index][0].set(True)
                self.ch_echo_vars[self.main_win.channel_index][1].configure(bg='green1')

            else:
                self.ch_echo_vars[ch_id][1].configure(bg=self.chk_btn_default_clr)
                # self.ch_echo_vars[self.main_win.channel_index][0].set(False)
                self.ch_echo_vars[self.main_win.channel_index][1].configure(bg=self.chk_btn_default_clr)
        """

    def _chk_dx_alarm(self):
        self._main_win.setting_dx_alarm = self.dx_alarm_on.get()

    def _chk_rnr(self):
        conn = self._main_win.get_conn()
        if conn:
            if self.rnr_var.get():
                conn.set_RNR()
            else:
                conn.unset_RNR()

    def _chk_link_holder(self):
        conn = self._main_win.get_conn()
        if conn:
            if self.link_holder_var.get():
                conn.link_holder_on = True
                conn.link_holder_timer = 0
            else:
                conn.link_holder_on = False
            self._main_win.on_channel_status_change()

    def _chk_t2auto(self):
        conn = self._main_win.get_conn()
        if conn:
            if self.t2_auto_var.get():
                conn.own_port.port_cfg.parm_T2_auto = True
                conn.calc_irtt()
                self.t2_var.set(str(conn.parm_T2 * 1000))
                self.t2.configure(state='disabled')
            else:
                conn.own_port.port_cfg.parm_T2_auto = False
                self.t2.configure(state='normal')
            conn.calc_irtt()

    def _chk_sprech_on(self):
        if self.sprech_on.get():
            self.t2speech.configure(state='normal')
        else:
            self.t2speech.configure(state='disabled')
        self._main_win.set_var_to_all_ch_param()

    def _chk_mon_port(self, event=None):
        vals = []
        port_id = int(self.mon_port_var.get())
        if port_id in PORT_HANDLER.get_all_ports().keys():
            vals = PORT_HANDLER.get_all_ports()[port_id].my_stations
        if vals:
            self.mon_call_var.set(vals[0])
        self.mon_call_ent.configure(values=vals)

    def _chk_mon_port_filter(self):
        _all_ports = PORT_HANDLER.get_all_ports()
        for port_id in _all_ports:
            _all_ports[port_id].monitor_out = self.mon_port_on_vars[port_id].get()

    def update_mon_port_id(self):
        if PORT_HANDLER.get_all_ports().keys():
            _vals = [str(x) for x in list(PORT_HANDLER.get_all_ports().keys())]
            self.mon_call_ent.configure(values=_vals)

    def _set_t2(self, event):
        conn = self._main_win.get_conn()
        if conn:
            conn.cfg.parm_T2 = min(max(int(self.t2_var.get()), 500), 3000)
            conn.calc_irtt()

    def tasker(self):
        try:    # TODO Need correct prozedur to end the whole shit
            ind = self._tabControl.index(self._tabControl.select())
        except TclError:
            pass
        else:
            if ind in self._tasker_dict.keys():
                self._tasker_dict[ind]()

    def _entry_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[1]
            vias = record[4]
            port = record[2]
            port = int(port.split(' ')[0])
            if vias:
                call = f'{call} {vias}'
            self._main_win.open_new_conn_win()
            self._main_win.new_conn_win.call_txt_inp.insert(tk.END, call)
            self._main_win.new_conn_win.set_port_index(port)

    def _format_tree_ent(self):
        self.tree_data = []
        for k in self.last_mh_ent:
            # ent: MyHeard
            ent = k
            route = ent.route

            self.tree_data.append((
                f"{conv_time_DE_str(ent.last_seen).split(' ')[1]}",
                f'{ent.own_call}',
                f'{ent.port_id} {ent.port}',
                f'{ent.pac_n}',
                ' '.join(route),
            ))

    def _update_rtt(self):
        best = ''
        worst = ''
        avg = ''
        last = ''
        status_text = ''
        duration = f"{STR_TABLE['time_connected'][self._lang]}: --:--:--"
        tx_buff = 'TX-Buffer: --- kb'
        tx_count = 'TX: --- kb'
        rx_count = 'RX: --- kb'
        station = self._main_win.get_conn(self._main_win.channel_index)
        if station:
            if station.RTT_Timer.rtt_best == 999.0:
                best = "Best: -1"
            else:
                best = "Best: {:.1f}".format(station.RTT_Timer.rtt_best)
            worst = "Worst: {:.1f}".format(station.RTT_Timer.rtt_worst)
            avg = "AVG: {:.1f}".format(station.RTT_Timer.rtt_average)
            last = "Last: {:.1f}".format(station.RTT_Timer.rtt_last)
            duration = f"{STR_TABLE['time_connected'][self._lang]}: {get_time_delta(station.time_start)}"
            tx_buff = 'TX-Buffer: ' + get_kb_str_fm_bytes(len(station.tx_buf_rawData))
            tx_count = 'TX: ' + get_kb_str_fm_bytes(station.tx_byte_count)
            rx_count = 'RX: ' + get_kb_str_fm_bytes(station.rx_byte_count)
            if station.is_link:
                status_text = 'Link'
            elif station.pipe is not None:
                status_text = 'Pipe'
            elif station.ft_obj is not None:
                if station.ft_obj.dir == 'TX':
                    status_text = 'Sending File'
                else:
                    status_text = 'Receiving File'
        self.status_label_var.set(status_text)
        self.rtt_best.configure(text=best)
        self.rtt_worst.configure(text=worst)
        self.rtt_avg.configure(text=avg)
        self.rtt_last.configure(text=last)
        self.conn_durration_var.set(duration)
        self.tx_buff_var.set(tx_buff)
        self.tx_count_var.set(tx_count)
        self.rx_count_var.set(rx_count)

    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ret_ent in self.tree_data:
            self.tree.insert('', tk.END, values=ret_ent)

    def _update_side_mh(self):
        mh_ent = list(MH_LIST.output_sort_entr(8))
        if mh_ent != self.last_mh_ent:
            self.last_mh_ent = mh_ent
            self._format_tree_ent()
            self.update_tree()

    def on_ch_stat_change(self):
        conn = self._main_win.get_conn()
        if conn:
            self.max_frame.configure(state='normal')
            self.pac_len.configure(state='normal')
            self.max_frame_var.set(str(conn.parm_MaxFrame))
            self.pac_len_var.set(conn.parm_PacLen)
            self.rnr_var.set(conn.is_RNR)
            self.rnr.configure(state='normal')
            self.link_holder.configure(state='normal')
            if conn.link_holder_on:
                self.link_holder_var.set(True)
            else:
                self.link_holder_var.set(False)

            self.tx_buff_var.set('TX-Buffer: ' + get_kb_str_fm_bytes(len(conn.tx_buf_rawData)))

            if conn.is_RNR:
                self.rnr.select()
            else:
                self.rnr.deselect()
            self.t2_auto.configure(state='normal')
            if conn.own_port.port_cfg.parm_T2_auto:
                self.t2_auto_var.set(True)
                self.t2_auto.select()
                self.t2_var.set(str(conn.parm_T2 * 1000))
                self.t2.configure(state='disabled')
            else:
                self.t2_auto_var.set(False)
                self.t2_auto.deselect()
                self.t2.configure(state='normal')
                self.t2_var.set(str(conn.parm_T2 * 1000))

        else:
            self.max_frame.configure(state='disabled')
            self.pac_len.configure(state='disabled')
            self.rnr_var.set(False)
            self.rnr.deselect()
            self.rnr.configure(state='disabled')
            self.t2_auto_var.set(False)
            self.t2_auto.deselect()
            self.t2_auto.configure(state='disabled')
            self.t2.configure(state='disabled')
            self.link_holder_var.set(False)
            self.link_holder.configure(state='disabled')
            self.tx_buff_var.set('TX-Buffer: --- kb')
            self.tx_count_var.set('TX: --- kb')
            self.rx_count_var.set('RX: --- kb')

        self.t2speech_var.set(self._main_win.get_ch_param().t2speech)
        self._update_ch_echo()

    def set_max_frame(self):
        conn = self._main_win.get_conn()
        if conn:
            conn.parm_MaxFrame = int(self.max_frame_var.get())

    def set_pac_len(self, event):
        conn = self._main_win.get_conn()
        if conn:
            conn.parm_PacLen = min(max(self.pac_len_var.get(), 1), 256)
            conn.calc_irtt()
            self.t2_var.set(str(conn.parm_T2 * 1000))

    def chk_t2speech(self):
        self._main_win.get_ch_param().t2speech = bool(self.t2speech_var.get())

    def chk_autoscroll(self):
        self._main_win.get_ch_param().autoscroll = bool(self.autoscroll_var.get())
        if bool(self.autoscroll_var.get()):
            self._main_win.see_end_qso_win()


class TxTframe:
    def __init__(self, main_win):

        self.pw = ttk.PanedWindow(orient=tk.VERTICAL)
        self._main_class = main_win
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
                                                    height=100, bd=0, )
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
                                      activebackground =STAT_BAR_CLR,
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
        self.out_frame.rowconfigure(1, minsize=10, weight=0)
        self.out_frame.rowconfigure(0, weight=1)
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
        self.out_txt_win = scrolledtext.ScrolledText(self.out_frame,
                                                     background=TXT_BACKGROUND_CLR,
                                                     foreground=TXT_OUT_CLR,
                                                     font=(FONT, self.text_size),
                                                     height=100,
                                                     bd=0,
                                                     borderwidth=0,
                                                     state="disabled")
        self.out_txt_win.tag_config("input", foreground="yellow")
        self.out_txt_win.grid(row=0, column=0, columnspan=10, sticky="nsew")
        # Stat INFO (Name,QTH usw)
        self.stat_info_name_var = tk.StringVar(self.out_frame)
        self.stat_info_qth_var = tk.StringVar(self.out_frame)
        self.stat_info_loc_var = tk.StringVar(self.out_frame)
        self.stat_info_typ_var = tk.StringVar(self.out_frame)
        self.stat_info_sw_var = tk.StringVar(self.out_frame)
        self.stat_info_timer_var = tk.StringVar(self.out_frame)
        self.stat_info_encoding_var = tk.StringVar(self.out_frame)
        self.stat_info_status_var = tk.StringVar(self.out_frame)
        size = 1
        name_label = tk.Label(self.out_frame,
                              textvariable=self.stat_info_name_var,
                              # bg=STAT_BAR_CLR,
                              height=1,
                              borderwidth=0,
                              border=0,
                              fg=STAT_BAR_TXT_CLR,
                              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size, 'bold')
                              )
        name_label.grid(row=1, column=1, sticky="nsew")
        name_label.bind('<Button-1>', self._main_class.open_user_db)
        qth_label = tk.Label(self.out_frame,
                             textvariable=self.stat_info_qth_var,
                             bg=STAT_BAR_CLR,
                             fg=STAT_BAR_TXT_CLR,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size)
                             )
        qth_label.bind('<Button-1>', self._main_class.open_user_db)
        qth_label.grid(row=1, column=2, sticky="nsew")
        loc_label = tk.Label(self.out_frame,
                             textvariable=self.stat_info_loc_var,
                             bg=STAT_BAR_CLR,
                             fg=STAT_BAR_TXT_CLR,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size)
                             )
        loc_label.bind('<Button-1>', self._main_class.open_user_db)
        loc_label.grid(row=1, column=3, sticky="nsew")

        opt = list(STATION_TYPS)
        stat_typ = tk.OptionMenu(
            self.out_frame,
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
            border=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size,)
        )
        stat_typ.grid(row=1, column=4, sticky="nsew")

        tk.Label(self.out_frame,
                 textvariable=self.stat_info_sw_var,
                 width=20,
                 bg="#ffd444",
                 # fg="red3",
                 height=1,
                 borderwidth=0,
                 border=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size)
                 ).grid(row=1, column=5, sticky="nsew")

        self.status_label = tk.Label(self.out_frame,
                                     textvariable=self.stat_info_status_var,
                                     bg=STAT_BAR_CLR,
                                     fg="red3",
                                     height=1,
                                     borderwidth=0,
                                     border=0,
                                     font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size,)
                                     )
        self.status_label.grid(row=1, column=6, sticky="nsew")
        self.status_label.bind('<Button-1>', self._main_class.do_priv)

        tk.Label(self.out_frame,
                 textvariable=self.stat_info_timer_var,
                 width=10,
                 height=1,
                 borderwidth=0,
                 border=0,
                 # bg="steel blue",
                 # fg="red3",
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - size,)
                 ).grid(row=1, column=7, sticky="nsew")
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            self.out_frame,
            self.stat_info_encoding_var,
            *opt,
            command=self.change_txt_encoding
        )
        txt_encoding_ent.configure(
            background="steel blue",
            height=1,
            width=8,
            borderwidth=0,
            border=0,
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
        station = self._main_class.get_conn(self._main_class.channel_index)
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
        if self._main_class.mon_mode:
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
        self._main_class.get_ch_param().rx_beep_opt = rx_beep_check

    def chk_timestamp(self):
        ts_check = self.ts_box_var.get()
        if ts_check:
            self.ts_box_box.configure(bg='green', activebackground='green')
        else:
            self.ts_box_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self._main_class.get_ch_param().timestamp_opt = ts_check

    def set_stat_typ(self, event=None):
        conn = self._main_class.get_conn()
        if conn:
            db_ent = conn.user_db_ent
            if db_ent:
                db_ent.TYP = self.stat_info_typ_var.get()
        else:
            self.stat_info_typ_var.set('-----')

    def change_txt_encoding(self, event=None, enc=''):
        conn = self._main_class.get_conn()
        if conn:
            db_ent = conn.user_db_ent
            if db_ent:
                if not enc:
                    enc = self.stat_info_encoding_var.get()
                db_ent.Encoding = enc
        else:
            self.stat_info_encoding_var.set('')


class TkMainWin:
    # @profile
    # def __init__(self, glb_ax25port_handler):
    # def __init__(self, root_tk):
    def __init__(self):
        self.language = LANGUAGE
        ###############################
        # AX25 PortHandler and stuff
        # self.ax25_port_handler = PORT_HANDLER

        self._root_dir = get_root_dir()
        self._root_dir = self._root_dir.replace('/', '//')
        #####################
        #####################
        # GUI VARS
        self._sound_th = None
        self.ch_alarm = False
        self.ch_alarm_sound_one_time = False
        self.channel_index = 1
        self.mon_mode = 0
        self._mon_buff = []
        self.connect_history = {}
        ####################
        # GUI PARAM
        self.parm_btn_blink_time = 0.3
        self._parm_rx_beep_cooldown = 1.5
        # Tasker Timings
        self._loop_delay = 80  # ms
        self._parm_non_prio_task_timer = 0.5  # s
        self._parm_non_non_prio_task_timer = 1  # s
        self._parm_non_non_non_prio_task_timer = 5 # 5  # s
        self._parm_test_task_timer = 60 # 5  # s
        self._parm_bw_mon_reset_task_timer = 3600  # s
        # self._parm_bw_mon_reset_task_timer = 120    # s
        self._non_prio_task_timer = time.time()
        self._non_non_prio_task_timer = time.time()
        self._non_non_non_prio_task_timer = time.time()
        self._test_task_timer = time.time()
        ###############
        self.text_size = 15
        ######################################
        # GUI Stuff
        self.main_win = tk.Tk()
        # self.main_win = root_tk
        self.main_win.title("P.ython o.ther P.acket T.erminal {}".format(VER))
        self.main_win.geometry("1400x850")
        # self.main_win.iconbitmap("favicon.ico")
        self.main_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
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
        _menubar = Menu(self.main_win, tearoff=False)
        self.main_win.config(menu=_menubar)
        # Menü 1 "Verbindungen"
        _MenuVerb = Menu(_menubar, tearoff=False)
        _MenuVerb.add_command(label=STR_TABLE['new'][self.language], command=self.open_new_conn_win)
        _MenuVerb.add_command(label=STR_TABLE['disconnect'][self.language], command=self._disco_conn)
        _MenuVerb.add_separator()
        _MenuVerb.add_command(label=STR_TABLE['quit'][self.language], command=self._destroy_win)
        _menubar.add_cascade(label=STR_TABLE['connections'][self.language], menu=_MenuVerb, underline=0)
        # Menü 2 "Bearbeiten"
        _MenuEdit = Menu(_menubar, tearoff=False)
        _MenuEdit.add_command(label=STR_TABLE['copy'][self.language], command=self._copy_select, underline=0)
        _MenuEdit.add_command(label=STR_TABLE['past'][self.language], command=self._clipboard_past, underline=1)
        _MenuEdit.add_separator()
        _MenuEdit.add_command(label=STR_TABLE['past_f_file'][self.language], command=self._insert_fm_file,
                              underline=0)
        _MenuEdit.add_command(label=STR_TABLE['save_to_file'][self.language], command=self._save_to_file,
                              underline=1)
        _MenuEdit.add_command(label=STR_TABLE['save_mon_to_file'][self.language], command=self._save_monitor_to_file,
                              underline=1)
        _MenuEdit.add_separator()
        _MenuEdit.add_command(label=STR_TABLE['clean_qso_win'][self.language], command=self.clear_channel_data,
                              underline=0)
        _MenuEdit.add_command(label=STR_TABLE['clean_mon_win'][self.language], command=self._clear_monitor_data,
                              underline=0)
        _menubar.add_cascade(label=STR_TABLE['edit'][self.language], menu=_MenuEdit, underline=0)
        # Menü 3 "Tools"
        _MenuTools = Menu(_menubar, tearoff=False)
        _MenuTools.add_command(label="MH", command=self._MH_win, underline=0)
        _MenuTools.add_command(label=STR_TABLE['statistic'][self.language], command=self.open_port_stat_win,
                               underline=1)
        _MenuTools.add_separator()
        _MenuTools.add_command(label="User-DB Tree", command=self._UserDB_tree, underline=0)
        _MenuTools.add_command(label=STR_TABLE['user_db'][self.language],
                               command=lambda: self._open_settings_window('user_db'),
                               underline=0)
        _MenuTools.add_separator()
        _MenuTools.add_command(label=STR_TABLE['locator_calc'][self.language], command=self._locator_calc_win,
                               underline=0)
        _MenuTools.add_separator()

        _MenuTools.add_command(label="FT-Manager",
                               command=lambda: self._open_settings_window('ft_manager'),
                               underline=0)
        _MenuTools.add_command(label=STR_TABLE['send_file'][self.language],
                               command=lambda: self._open_settings_window('ft_send'),
                               underline=0)
        _MenuTools.add_separator()
        _MenuTools.add_command(label=STR_TABLE['linkholder'][self.language],
                               command=lambda: self._open_settings_window('l_holder'),
                               underline=0)
        _MenuTools.add_command(label='Pipe-Tool',
                               command=lambda: self._open_settings_window('pipe_sett'),
                               underline=0)
        _MenuTools.add_separator()

        _MenuTools.add_command(label='Priv',
                               command=lambda: self._open_settings_window('priv_win'),
                               underline=0)

        # MenuTools.add_command(label="Datei senden", command=self.open_linkholder_settings_win, underline=0)
        _menubar.add_cascade(label=STR_TABLE['tools'][self.language], menu=_MenuTools, underline=0)

        # Menü 4 Einstellungen
        _MenuSettings = Menu(_menubar, tearoff=False)
        _MenuSettings.add_command(label=STR_TABLE['station'][self.language],
                                  command=lambda: self._open_settings_window('stat_sett'),
                                  underline=0)
        _MenuSettings.add_command(label=STR_TABLE['port'][self.language],
                                  command=lambda: self._open_settings_window('port_sett'),
                                  underline=0)
        _MenuSettings.add_command(label=STR_TABLE['beacon'][self.language],
                                  command=lambda: self._open_settings_window('beacon_sett'),
                                  underline=0)
        _MenuSettings.add_command(label='APRS',
                                  command=lambda: self._open_settings_window('aprs_sett'),
                                  underline=0)

        _MenuSettings.add_separator()
        _MenuSettings.add_command(label='Multicast',
                                  command=lambda: self._open_settings_window('mcast_sett'),
                                  underline=0)
        _MenuSettings.add_command(label="RX-Echo",
                                  command=lambda: self._open_settings_window('rx_echo_sett'),
                                  underline=0)

        _menubar.add_cascade(label=STR_TABLE['settings'][self.language], menu=_MenuSettings, underline=0)
        # APRS Menu
        _MenuAPRS = Menu(_menubar, tearoff=False)
        _MenuAPRS.add_command(label=STR_TABLE['aprs_mon'][self.language], command=self._open_aismon_win,
                              underline=0)
        _MenuAPRS.add_command(label=STR_TABLE['pn_msg'][self.language], command=self._open_aprs_pn_msg_win,
                              underline=0)
        # MenuAPRS.add_separator()
        _menubar.add_cascade(label="APRS", menu=_MenuAPRS, underline=0)

        # Menü 5 Hilfe
        _MenuHelp = Menu(_menubar, tearoff=False)
        # MenuHelp.add_command(label="Hilfe", command=lambda: False, underline=0)
        _MenuHelp.add_command(label=STR_TABLE['keybind'][self.language],
                              command=lambda: self._open_settings_window('keybinds'),
                              underline=0)
        _MenuHelp.add_separator()
        _MenuHelp.add_command(label=STR_TABLE['about'][self.language],
                              command=lambda: self._open_settings_window('about'),
                              underline=0)
        _menubar.add_cascade(label=STR_TABLE['help'][self.language], menu=_MenuHelp, underline=0)

        # Menü 4 "Debug"
        # menubar.add_command(label="Debug")
        ############################
        ############################
        # Input Output TXT Frames and Status Bar
        self._txt_win = TxTframe(self)
        self._out_txt = self._txt_win.out_txt_win
        self._inp_txt = self._txt_win.in_txt_win
        self._mon_txt = self._txt_win.mon_txt
        #######################
        # Window Text Buffers
        self._win_buf: {int: ChVars} = {}
        for i in range(11):
            self._win_buf[i] = ChVars()
            self._win_buf[i].input_win_index = str(self._inp_txt.index(tk.INSERT))
        # Channel Buttons
        self._ch_btn = ChBtnFrm(self)
        self._ch_btn.ch_btn_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")
        #########################
        # BTN and Tabbed Frame right side
        self._side_btn_frame_top = tk.Frame(self.main_win, width=200, height=540)
        # self.side_btn_frame_top = tk.Frame(self.pw, width=200, height=540)
        # self.pw.add(self.txt_win.pw)
        self._side_btn_frame_top.grid(row=1, rowspan=2, column=1, sticky="nsew")
        self._side_btn_frame_top.rowconfigure(0, minsize=40, weight=0)  # CONN BTN
        self._side_btn_frame_top.rowconfigure(1, minsize=40, weight=0)  # BTN row 2
        self._side_btn_frame_top.rowconfigure(2, minsize=50, weight=0)  # Dummy
        self._side_btn_frame_top.rowconfigure(3, minsize=50, weight=2)  # Dummy
        self._side_btn_frame_top.rowconfigure(4, minsize=300, weight=10)  # Reiter Frame
        # self._side_btn_frame_top.rowconfigure(5, minsize=15, weight=1)  # Reiter Frame

        self._side_btn_frame_top.columnconfigure(0, minsize=10, weight=0)
        self._side_btn_frame_top.columnconfigure(1, minsize=100, weight=2)
        self._side_btn_frame_top.columnconfigure(2, minsize=100, weight=2)
        self._side_btn_frame_top.columnconfigure(3, minsize=10, weight=1)
        self._side_btn_frame_top.columnconfigure(4, minsize=10, weight=5)
        self._side_btn_frame_top.columnconfigure(6, minsize=10, weight=1)
        self._conn_btn = tk.Button(self._side_btn_frame_top,
                                   text="New Conn",
                                   bg="green",
                                   width=8,
                                   command=self.open_new_conn_win)
        self._conn_btn.place(x=5, y=10)

        self._mh_btn = tk.Button(self._side_btn_frame_top,
                                 text="MH",
                                 # bg="yellow",
                                 width=8,
                                 command=self._MH_win)

        self._mh_btn.place(x=5, y=45)
        # self.mh_btn.place(x=110, y=10)
        self.mh_btn_def_clr = self._mh_btn.cget('bg')
        self._mon_btn = tk.Button(self._side_btn_frame_top,
                                  text="Monitor",
                                  bg="yellow", width=8, command=lambda: self.switch_channel(0))
        # self.mon_btn.place(x=110, y=45)
        self._mon_btn.place(x=110, y=10)

        _btn = tk.Button(self._side_btn_frame_top,
                         text="Port-Stat",
                         width=8,
                         command=self.open_port_stat_win)
        # _btn.place(x=5, y=80)
        _btn.place(x=110, y=45)

        _btn = tk.Button(self._side_btn_frame_top,
                         text="Kaffèmaschine",
                         bg="HotPink2", width=12, command=self._kaffee)
        _btn.place(x=215, y=10)
        self.tabbed_sideFrame = SideTabbedFrame(self)
        # self.pw.add(self.tabbed_sideFrame.tab_side_frame)
        self.setting_sound = self.tabbed_sideFrame.sound_on
        self.setting_sprech = self.tabbed_sideFrame.sprech_on
        self.setting_bake = self.tabbed_sideFrame.bake_on
        self.setting_rx_echo = self.tabbed_sideFrame.rx_echo_on
        self.setting_dx_alarm = self.tabbed_sideFrame.dx_alarm_on
        ############################
        # Canvas Plot ( TEST )
        # ### BushFIX F*** Plot eating up memory ###
        """
        self._bw_plot_enabled_var = tk.BooleanVar(self._side_btn_frame_top)
        self._bw_plot_enabled_var.set(True)
        tk.Checkbutton(
            self._side_btn_frame_top,
            text=STR_TABLE['bw_plot_enable'][self.language],
            variable=self._bw_plot_enabled_var
        ).grid(row=5, column=0, columnspan=7, sticky="nsew")
        """

        # plt.ion()
        self._bw_fig = Figure(figsize=(8, 4.5), dpi=80)
        # plt.style.use('dark_background')
        self._ax = self._bw_fig.add_subplot(111)
        self._bw_fig.subplots_adjust(left=0.1, right=0.95, top=0.97, bottom=0.1)
        self._ax.axis([0, 10, 0, 60])
        self._bw_fig.set_facecolor('xkcd:light grey')
        self._ax.set_facecolor('#000000')
        # self.bw_fig.xlim(0, 10)  # TODO As Option
        self._ax.xaxis.label.set_color('black')
        self._ax.yaxis.label.set_color('black')
        self._ax.tick_params(axis='x', colors='black')
        self._ax.tick_params(axis='y', colors='black')
        self._ax.set_xlabel(STR_TABLE['minutes'][self.language])
        self._ax.set_ylabel(STR_TABLE['occup'][self.language])
        self._bw_plot_lines = {}
        # plt.xlabel(STR_TABLE['minutes'][self.language])
        # plt.xlim(0, 10)  # TODO As Option
        # plt.ylabel(STR_TABLE['occup'][self.language])
        self._canvas = FigureCanvasTkAgg(self._bw_fig, master=self._side_btn_frame_top)  # A tk.DrawingArea.
        self._canvas.flush_events()
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(row=5, column=0, columnspan=7, sticky="nsew")
        self._canvas.get_tk_widget().config(cursor="none")
        self._bw_fig.canvas.flush_events()

        self._bw_plot_x_scale = []
        for _i in list(range(60)):
            self._bw_plot_x_scale.append(_i / 6)
        self._bw_plot_lines = {}

        ############################
        # Windows
        self.new_conn_win = None
        self.settings_win = None
        self.mh_window = None
        self.port_stat_win = None
        self.locator_calc_window = None
        self.aprs_mon_win = None
        self.aprs_pn_msg_win = None
        self.userDB_tree_win = None
        ###########################
        # Init
        # set Ch Btn Color
        self.ch_status_update()
        # set KEY BINDS
        self._set_binds()
        self._set_keybinds()
        # .....
        self._monitor_start_msg()
        #######################
        # set GUI Vav
        PORT_HANDLER.set_gui(self)
        #######################
        # LOOP
        self.main_win.after(self._loop_delay, self._tasker)
        self.main_win.mainloop()

    def __del__(self):
        # self.disco_all()
        # self.ax25_port_handler.close_all()
        pass

    def _destroy_win(self):
        logging.info('Closing GUI.')
        self._close_port_stat_win()
        if self.settings_win is not None:
            self.settings_win.destroy()
        if self.mh_window is not None:
            self.mh_window.destroy()
        logging.info('Closing GUI: Closing Ports.')
        PORT_HANDLER.close_all()
        logging.info('Closing GUI: Done.')

    def _monitor_start_msg(self):

        # tmp_lang = int(self.language)
        # self.language = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.sprech(random.choice(WELCOME_SPEECH))
        # self.language = int(tmp_lang)
        ban = POPT_BANNER.format(VER)
        tmp = ban.split('\r')
        for el in tmp:
            self.msg_to_monitor(el)
        self.msg_to_monitor('Python Other Packet Terminal ' + VER)
        for stat in PORT_HANDLER.ax25_stations_settings.keys():
            self.msg_to_monitor('Info: Stationsdaten {} erfolgreich geladen.'.format(stat))
        for port_k in PORT_HANDLER.get_all_ports().keys():
            msg = 'konnte nicht initialisiert werden!'
            if PORT_HANDLER.get_all_ports()[port_k].device_is_running:
                msg = 'erfolgreich initialisiert.'
            self.msg_to_monitor('Info: Port {}: {} - {} {}'
                                .format(port_k,
                                        PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortName,
                                        PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortTyp,
                                        msg
                                        ))
            self.msg_to_monitor('Info: Port {}: Parameter: {} | {}'
                                .format(port_k,
                                        PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortParm[0],
                                        PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortParm[1]
                                        ))

    ##########################
    # Clipboard Stuff
    def _copy_select(self):
        if self._out_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._out_txt.selection_get())
            self._out_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._inp_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._inp_txt.selection_get())
            self._inp_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._mon_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._mon_txt.selection_get())
            self._mon_txt.tag_remove(tk.SEL, "1.0", tk.END)

    def _cut_select(self):
        if self._out_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._out_txt.selection_get())
            self._out_txt.delete('sel.first', 'sel.last')

    def _clipboard_past(self):
        clp_brd = self.main_win.clipboard_get()
        if clp_brd:
            self._inp_txt.insert(tk.END, clp_brd)

    def _select_all(self):
        self._inp_txt.tag_add(tk.SEL, "1.0", tk.END)
        self._inp_txt.mark_set(tk.INSERT, "1.0")
        self._inp_txt.see(tk.INSERT)

    ##########################
    # no WIN FNC
    def get_conn(self, con_ind: int = 0):
        if not con_ind:
            con_ind = self.channel_index
        if con_ind in PORT_HANDLER.get_all_connections().keys():
            ret = PORT_HANDLER.get_all_connections()[con_ind]
            return ret
        return False

    def get_ch_param(self, ch_index=0):
        if ch_index:
            return self._win_buf[ch_index]
        else:
            return self._win_buf[self.channel_index]

    def set_var_to_all_ch_param(self):
        for i in range(10):  # TODO Max Channels
            if not self._win_buf[i + 1].t2speech:
                self._win_buf[i + 1].t2speech_buf = ''

    def clear_channel_data(self):
        self._out_txt.configure(state='normal')
        self._out_txt.delete('1.0', tk.END)
        self._out_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        del self._win_buf[self.channel_index]
        self._win_buf[self.channel_index] = ChVars()

    def _clear_monitor_data(self):
        self._mon_txt.configure(state='normal')
        self._mon_txt.delete('1.0', tk.END)
        self._mon_txt.configure(state='disabled')

    def _insert_fm_file(self):
        data = open_file_dialog()
        if data:
            # TODO Maybe Channel Decoding ?  ?
            self._inp_txt.insert(tk.INSERT, try_decode(data, ignore=True))

    def _save_to_file(self):
        data = self._out_txt.get('1.0', tk.END)
        save_file_dialog(data)

    def _save_monitor_to_file(self):
        data = self._mon_txt.get('1.0', tk.END)
        save_file_dialog(data)

    def _set_binds(self):
        self._inp_txt.bind("<ButtonRelease-1>", self._on_click_inp_txt)

    def _set_keybinds(self):
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
        self.main_win.bind('<Return>', self._snd_text)
        self.main_win.bind('<KeyRelease-Return>', self._release_return)
        self.main_win.bind('<Shift-KeyPress-Return>', self._shift_return)
        self.main_win.bind('<KeyRelease-Left>', self._arrow_keys)
        self.main_win.bind('<KeyRelease-Right>', self._arrow_keys)
        self.main_win.bind('<KeyRelease-Up>', self._arrow_keys)
        self.main_win.bind('<KeyRelease-Down>', self._arrow_keys)
        # self.main_win.bind('<KP_Enter>', self.snd_text)
        self.main_win.bind('<Alt-c>', lambda event: self.open_new_conn_win())
        self.main_win.bind('<Escape>', lambda event: self.open_new_conn_win())
        self.main_win.bind('<Alt-d>', lambda event: self._disco_conn())
        self.main_win.bind('<Control-c>', lambda event: self._copy_select())
        self.main_win.bind('<Control-x>', lambda event: self._cut_select())
        # self.main_win.bind('<Control-v>', lambda event: self.clipboard_past())
        self.main_win.bind('<Control-a>', lambda event: self._select_all())
        self.main_win.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.main_win.bind('<Control-minus>', lambda event: self._decrease_textsize())
        self.main_win.bind('<Control-Right>', lambda event: self._text_win_bigger())
        self.main_win.bind('<Control-Left>', lambda event: self._text_win_smaller())

        self.main_win.bind('<Key>', lambda event: self._any_key(event))

    def _any_key(self, event: tk.Event):
        if event.keycode == 104:  # Numpad Enter
            self._snd_text(event)

    def _arrow_keys(self, event=None):
        self._on_click_inp_txt()

    def _shift_return(self, event=None):
        pass

    def _release_return(self, event=None):
        pass

    def _increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        width = self._inp_txt.cget('width')
        self._inp_txt.configure(font=(FONT, self.text_size), width=width + 1)
        self._out_txt.configure(font=(FONT, self.text_size), width=width + 1)
        self._mon_txt.configure(font=(FONT, self.text_size), width=width + 1)

    def _decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        width = self._inp_txt.cget('width')
        self._inp_txt.configure(font=(FONT, self.text_size), width=width - 1)
        self._out_txt.configure(font=(FONT, self.text_size), width=width - 1)
        self._mon_txt.configure(font=(FONT, self.text_size), width=width - 1)

    def _text_win_bigger(self):
        width = self._inp_txt.cget('width')
        self._inp_txt.configure(width=width + 1)
        self._out_txt.configure(width=width + 1)
        self._mon_txt.configure(width=width + 1)

    def _text_win_smaller(self):
        width = self._inp_txt.cget('width')
        self._inp_txt.configure(width=max(width - 1, 56))
        self._out_txt.configure(width=max(width - 1, 56))
        self._mon_txt.configure(width=max(width - 1, 56))

    def change_conn_btn(self):
        # TODO Nur triggern wenn ch_btn click | neue in conn | disco
        # TODO extra Funktionen für on_disco & on_newconn
        if self.get_conn(self.channel_index):
            if self._conn_btn.cget('bg') != "red":
                self._conn_btn.configure(bg="red", text="Disconnect", command=self._disco_conn)
        elif self._conn_btn.cget('bg') != "green":
            self._conn_btn.configure(text="New Conn", bg="green", command=self.open_new_conn_win)

    ###############
    # Sound
    def _kanal_switch(self):
        """ Triggered on CH BTN Click """
        threading.Thread(target=self._kanal_switch_sprech_th).start()

    def _kanal_switch_sprech_th(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            if self._win_buf[self.channel_index].t2speech \
                    and self._win_buf[self.channel_index].t2speech_buf:
                # to_speech = 'Kanal {} .'.format(self.channel_index)
                # to_speech += '{} .'.format(conn.to_call_str)
                to_speech = str(self._win_buf[self.channel_index].t2speech_buf)
                if self.sprech(to_speech):
                    self._win_buf[self.channel_index].t2speech_buf = ''

            else:
                self._win_buf[self.channel_index].t2speech_buf = ''
                self.sprech('{} {} . {} .'.format(STR_TABLE['channel'][self.language],
                                                  self.channel_index,
                                                  conn.to_call_str))

        else:
            if not self._win_buf[self.channel_index].t2speech:
                self._win_buf[self.channel_index].t2speech_buf = ''
                self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            elif self._win_buf[self.channel_index].t2speech_buf:
                if self.sprech(self._win_buf[self.channel_index].t2speech_buf):
                    self._win_buf[self.channel_index].t2speech_buf = ''
                else:
                    self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            else:
                self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))

    def _check_sprech_ch_buf(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            if self._win_buf[self.channel_index].t2speech \
                    and self._win_buf[self.channel_index].t2speech_buf:
                to_speech = str(self._win_buf[self.channel_index].t2speech_buf)
                if self.setting_sprech.get() and self.setting_sound.get():
                    if self.sprech(to_speech):
                        self._win_buf[self.channel_index].t2speech_buf = ''
                else:
                    self._win_buf[self.channel_index].t2speech_buf = ''

            elif not self._win_buf[self.channel_index].t2speech:
                self._win_buf[self.channel_index].t2speech_buf = ''
        else:
            self._win_buf[self.channel_index].t2speech_buf = ''

    def sprech(self, text: str):
        if self.setting_sprech.get() and self.setting_sound.get():
            if text:
                if self._sound_th is not None:
                    if self._sound_th.is_alive():
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
                            print("GTTS")
                            tts = gTTS(text=text,
                                       lang=language,
                                       slow=False)
                            tts.save('data/speech.mp3')
                        except gtts.gTTSError:
                            self.setting_sprech.set(False)
                            return False
                        return self._sound_play(self._root_dir + '//data//speech.mp3')
        return False

    def _sound_play(self, snd_file: str, wait=True):
        # TODO .. Again !!! ... Don't like this mess
        if self.setting_sound.get():
            if wait:
                if self._sound_th is not None:
                    if not self._sound_th.is_alive():
                        # print('Lebt nicht mehr')
                        self._sound_th.join()
                        # print('Join')
                        if is_linux():
                            self._sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                            self._sound_th.start()
                        elif 'win' in sys.platform:
                            self._sound_th = threading.Thread(target=PlaySound,
                                                              args=(snd_file, SND_FILENAME | SND_NOWAIT))
                            self._sound_th.start()
                        return True
                    return False
                if is_linux():
                    self._sound_th = threading.Thread(target=playsound, args=(snd_file, True))
                    self._sound_th.start()
                elif is_windows():
                    self._sound_th = threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT))
                    self._sound_th.start()
                return True
            else:
                if is_linux():
                    threading.Thread(target=playsound, args=(snd_file, True)).start()
                elif is_windows():
                    threading.Thread(target=PlaySound, args=(snd_file, SND_FILENAME | SND_NOWAIT)).start()
                return True

    def _rx_beep_sound(self):
        for k in self._win_buf.keys():
            if k:
                temp: ChVars = self._win_buf[k]
                if temp.rx_beep_cooldown < time.time():
                    temp.rx_beep_cooldown = time.time() + self._parm_rx_beep_cooldown
                    tr = temp.rx_beep_opt
                    if tr is not None:
                        tr = temp.rx_beep_opt
                        if tr:
                            if temp.rx_beep_tr:
                                temp.rx_beep_tr = False
                                self._sound_play(self._root_dir + '//data//sound//rx_beep.wav', False)

    def new_conn_sound(self):
        self._sound_play(self._root_dir + '//data//sound//conn_alarm.wav', False)

    def disco_sound(self):
        self._sound_play(self._root_dir + '//data//sound//disco_alarm.wav', False)

    # Sound Ende
    #################
    # no WIN FNC
    ##########################

    def _dx_alarm(self):
        """ Alarm when new User in MH List """
        # self.tabbed_sideFrame.tabControl.select(self.tabbed_sideFrame.tab2_mh)
        self._mh_btn.configure(bg=random.choice(ALL_COLOURS))

    def reset_dx_alarm(self):
        MH_LIST.new_call_alarm = False
        self._mh_btn.configure(bg=self.mh_btn_def_clr)

    #################################
    # TASKER
    def _tasker(self):  # MAINLOOP
        # self._tasker_prio()
        self._tasker_low_prio()
        self._tasker_low_low_prio()
        self._tasker_low_low_low_prio()
        # self._tasker_tester()
        self.main_win.after(self._loop_delay, self._tasker)

    def _tasker_prio(self):
        """ Prio Tasks """
        pass

    def _tasker_low_prio(self):
        if time.time() > self._non_prio_task_timer:
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            #####################
            self._aprs_task()
            self._monitor_task()
            self._update_qso_win()
            self._txt_win.update_status_win()
            self.change_conn_btn()
            if self.setting_sound:
                self._rx_beep_sound()
                if self.setting_sprech:
                    self._check_sprech_ch_buf()
            if self.ch_alarm:
                self.ch_status_update()

    def _tasker_low_low_prio(self):
        """ 1 Sec """
        if time.time() > self._non_non_prio_task_timer:
            self._non_non_prio_task_timer = time.time() + self._parm_non_non_prio_task_timer
            #####################
            self._update_stat_info_conn_timer()
            self._update_ft_info()
            self.tabbed_sideFrame.tasker()
            if MH_LIST.new_call_alarm and self.setting_dx_alarm:
                self._dx_alarm()
            if self.settings_win is not None:
                # ( FT-Manager )
                self.settings_win.tasker()
            """
            if self.aprs_mon_win is not None:
                self.aprs_mon_win.tasker()
            """

    def _tasker_low_low_low_prio(self):
        """ 5 Sec """
        if time.time() > self._non_non_non_prio_task_timer:
            self._non_non_non_prio_task_timer = time.time() + self._parm_non_non_non_prio_task_timer
            #####################
            self._update_bw_mon()

    def _tasker_tester(self):
        """ 5 Sec """
        if time.time() > self._test_task_timer:
            self._test_task_timer = time.time() + self._parm_test_task_timer
            #####################
            self._tester()

    #@profile(precision=4)
    def _tester(self):
        print(gc.garbage)

    @staticmethod
    def _aprs_task():
        if PORT_HANDLER.get_aprs_ais() is not None:
            PORT_HANDLER.get_aprs_ais().task()

    def get_side_frame(self):
        return self._side_btn_frame_top

    #################################
    # TASKS
    def _update_qso_win(self):  # INPUT WIN
        # UPDATE INPUT WIN
        for k in PORT_HANDLER.get_all_connections():
            conn = self.get_conn(k)
            if conn:
                if conn.ft_obj is None:
                    if conn.rx_buf_rawData or conn.tx_buf_guiData:
                        k = conn.ch_index
                        txt_enc = 'UTF-8'
                        if conn.user_db_ent:
                            txt_enc = conn.user_db_ent.Encoding

                        inp = bytes(conn.tx_buf_guiData)
                        conn.tx_buf_guiData = b''

                        inp_len = len(conn.rx_buf_rawData)
                        out = bytes(conn.rx_buf_rawData[:inp_len])
                        conn.rx_buf_rawData = conn.rx_buf_rawData[inp_len:]

                        # if self.win_buf[k].hex_output:
                        """
                        hex_out = out.hex()
                        hex_in = inp.hex()
                        """
                        inp = inp.decode(txt_enc, 'ignore').replace('\r', '\n')
                        # Write RX Date to Window/Channel Buffer

                        out = out.decode(txt_enc, 'ignore')
                        out = out.replace('\r\n', '\n') \
                            .replace('\n\r', '\n') \
                            .replace('\r', '\n')
                        # print(f"{out}\nhex: {hex_out}")
                        out = tk_filter_bad_chars(out)
                        """
                        if hex_out:
                            out = out + ' > ' + hex_out + '\n'
                        if hex_in:
                            inp = inp + ' >' + hex_in + '<\n'
                        """
                        # Write RX Date to Window/Channel Buffer
                        self._win_buf[k].output_win += inp
                        self._win_buf[k].output_win += out
                        if self._win_buf[k].t2speech:
                            if k == self.channel_index:
                                self._win_buf[k].t2speech_buf += out.replace('\n', '')
                            else:
                                self._win_buf[k].t2speech_buf += '{} {} . {} . {}'.format(
                                    STR_TABLE['channel'][self.language],
                                    k,
                                    conn.to_call_str,
                                    out.replace('\n', '')
                                )
                        if self.channel_index == k:
                            fg = conn.stat_cfg.stat_parm_qso_col_text
                            bg = conn.stat_cfg.stat_parm_qso_col_bg
                            tag_name_out = 'OUT-' + str(conn.my_call_str)
                            self.get_ch_param(ch_index=k).qso_tag_fg = fg
                            self.get_ch_param(ch_index=k).qso_tag_bg = bg
                            self.get_ch_param(ch_index=k).qso_tag_name = tag_name_out

                            tr = False
                            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index(tk.INSERT)) < 15:
                                tr = True

                            self._out_txt.configure(state="normal")

                            self._out_txt.tag_config(tag_name_out,
                                                     foreground=fg,
                                                     background=bg,
                                                     selectbackground=fg,
                                                     selectforeground=bg
                                                     )

                            ind = self._out_txt.index('end-1c')
                            self._out_txt.insert('end', inp)
                            ind2 = self._out_txt.index('end-1c')
                            self._out_txt.tag_add("input", ind, ind2)

                            # configuring a tag called start
                            ind = self._out_txt.index('end-1c')
                            self._out_txt.insert('end', out)
                            ind2 = self._out_txt.index('end-1c')
                            self._out_txt.tag_add(tag_name_out, ind, ind2)
                            self._out_txt.configure(state="disabled",
                                                    exportselection=1
                                                    )
                            if tr or self.get_ch_param().autoscroll:
                                self.see_end_qso_win()
                        else:
                            tag_name_out = 'OUT-' + str(conn.my_call_str)
                            self.get_ch_param(ch_index=k).qso_tag_fg = str(conn.stat_cfg.stat_parm_qso_col_text)
                            self.get_ch_param(ch_index=k).qso_tag_bg = str(conn.stat_cfg.stat_parm_qso_col_bg)
                            self.get_ch_param(ch_index=k).qso_tag_name = tag_name_out
                            if tag_name_out not in self._win_buf[k].output_win_tags.keys():
                                self._win_buf[k].output_win_tags[tag_name_out] = ()
                            old_tags = list(self._win_buf[k].output_win_tags[tag_name_out])
                            if old_tags:
                                old_tags = old_tags + ['end-1c']
                            else:
                                old_tags = ['1.0', 'end-1c']
                            self._win_buf[k].output_win_tags[tag_name_out] = old_tags
                            self._win_buf[k].new_data_tr = True
                        self._win_buf[k].rx_beep_tr = True
                        self.ch_status_update()

    def update_monitor(self, ax25frame, conf, tx=False):
        """ Called from AX25Conn """
        self._mon_buff.append((
            ax25frame,
            conf,
            bool(tx)
        ))

    def _monitor_task(self):
        if self._mon_buff:
            tmp_buff = list(self._mon_buff)
            self._mon_buff = []
            tr = False
            self._mon_txt.configure(state="normal")
            for el in tmp_buff:
                var = monitor_frame_inp(el[0], el[1])
                conf = el[1]
                tx = el[2]
                var = tk_filter_bad_chars(var)
                ind = self._mon_txt.index('end-1c')
                color_bg = conf.parm_mon_clr_bg
                if float(self._mon_txt.index(tk.END)) - float(self._mon_txt.index(tk.INSERT)) < 15:
                    tr = True
                if tx:
                    tag = "tx{}".format(conf.parm_PortNr)
                    color = conf.parm_mon_clr_tx
                else:
                    tag = "rx{}".format(conf.parm_PortNr)
                    color = conf.parm_mon_clr_rx

                if tag in self._mon_txt.tag_names(None):
                    self._mon_txt.insert(tk.END, var, tag)
                else:
                    self._mon_txt.insert(tk.END, var)
                    ind2 = self._mon_txt.index('end-1c')
                    self._mon_txt.tag_config(tag, foreground=color,
                                             background=color_bg,
                                             selectbackground=self._mon_txt.cget('selectbackground'),
                                             selectforeground=self._mon_txt.cget('selectforeground'),
                                             )
                    self._mon_txt.tag_add(tag, ind, ind2)
            self._mon_txt.configure(state="disabled", exportselection=1)
            if tr or self.tabbed_sideFrame.mon_scroll_var.get():
                self._mon_txt.see(tk.END)

    def see_end_qso_win(self):
        self._out_txt.see("end")

    def msg_to_monitor(self, var: str):
        # var += bytes.fromhex('15').decode('UTF-8')+'\n'
        """ Called from AX25Conn """
        ind = self._mon_txt.index(tk.INSERT)

        self._mon_txt.configure(state="normal")
        ins = 'SYS {0}: *** {1}\n'.format(datetime.datetime.now().strftime('%H:%M:%S'), var)
        self._mon_txt.insert(tk.END, ins)
        self._mon_txt.configure(state="disabled")

        ind2 = self._mon_txt.index(tk.INSERT)
        self._mon_txt.tag_add("sys-msg", ind, ind2)
        self._mon_txt.tag_config("sys-msg", foreground=CFG_clr_sys_msg)

        self._mon_txt.see(tk.END)
        if 'Lob: ' in var:
            var = var.split('Lob: ')
            if len(var) > 1:
                self.sprech(var[1])

    def open_link_holder_sett(self):
        self._open_settings_window('l_holder')

    def open_ft_manager(self, event=None):
        self._open_settings_window('ft_manager')

    def open_user_db(self, event=None):
        self._open_settings_window('user_db')

    def _open_settings_window(self, win_key: str):
        if self.settings_win is None:
            settings_win = {
                'priv_win': PrivilegWin,  # Priv Win
                'keybinds': KeyBindsHelp,  # Keybinds Help WIN
                'about': About,  # About WIN
                'aprs_sett': APRSSettingsWin,  # APRS Settings
                'ft_manager': FileTransferManager,  # FT Manager
                'ft_send': FileSend,  # FT TX
                'pipe_sett': PipeToolSettings,  # Pipe Tool
                'user_db': UserDB,  # UserDB
                'mcast_sett': MulticastSettings,  # Multicast Settings
                'l_holder': LinkHolderSettings,  # Linkholder
                'rx_echo_sett': RxEchoSettings,  # RX Echo
                'beacon_sett': BeaconSettings,  # Beacon Settings
                'port_sett': PortSettingsWin,  # Port Settings
                'stat_sett': StationSettingsWin,  # Stat Settings
            }.get(win_key, '')
            if settings_win:
                self.settings_win = settings_win(self)

    ##########################
    # New Connection WIN
    def open_new_conn_win(self):
        self._new_conn_win()

    def _new_conn_win(self):
        if self.new_conn_win is None:
            self.new_conn_win = NewConnWin(self)

    ##########################
    # Keybinds Help WIN
    def open_port_stat_win(self):
        if self.port_stat_win is None:
            self.port_stat_win = PlotWindow(self)
        else:
            self.port_stat_win.deiconify()

    def _close_port_stat_win(self):
        if self.port_stat_win is not None:
            self.port_stat_win.destroy_plot()
            del self.port_stat_win
            self.port_stat_win = None

    ###################
    # MH WIN
    def _MH_win(self):
        """MH WIN"""
        self.reset_dx_alarm()
        if self.mh_window is None:
            MHWin(self)

    ###################
    # MH WIN
    def _locator_calc_win(self):
        """ """
        if self.locator_calc_window is None:
            LocatorCalculator(self)

    ###################
    # MH WIN
    def _open_aismon_win(self):
        """ """
        if self.aprs_mon_win is None:
            AISmonitor(self)

    ###################
    # MH WIN
    def _open_aprs_pn_msg_win(self):
        """ """
        if self.aprs_pn_msg_win is None:
            APRS_msg_SYS_PN(self)

    ###################
    # User-DB TreeView WIN
    def _UserDB_tree(self):
        """MH WIN"""
        if self.userDB_tree_win is None:
            self.userDB_tree_win = UserDBtreeview(self)

    def gui_set_distance(self):
        conn = self.get_conn()
        if conn:
            conn.set_distance()

    # ##############
    # DISCO
    def _disco_conn(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            conn.conn_disco()

    # DISCO ENDE
    # ##############
    ###################
    # SEND TEXT OUT
    def _snd_text(self, event: tk.Event):
        if self.channel_index:
            _station = self.get_conn(self.channel_index)
            if _station:
                _ind = str(self._win_buf[self.channel_index].input_win_index)
                if _ind:
                    if float(_ind) >= float(self._inp_txt.index(tk.INSERT)):
                        _ind = str(self._inp_txt.index(tk.INSERT))
                    _ind = str(int(float(_ind))) + '.0'
                else:
                    _ind = '1.0'
                _txt_enc = 'UTF-8'
                if _station.user_db_ent:
                    _txt_enc = _station.user_db_ent.Encoding
                _tmp_txt = self._inp_txt.get(_ind, self._inp_txt.index(tk.INSERT))

                _tmp_txt = _tmp_txt.replace('\n', '\r')
                _station.send_data(_tmp_txt.encode(_txt_enc, 'ignore'))

                self._inp_txt.tag_remove('send', _ind, str(self._inp_txt.index(tk.INSERT)))
                self._inp_txt.tag_add('send', _ind, str(self._inp_txt.index(tk.INSERT)))

                self._win_buf[self.channel_index].input_win_index = str(self._inp_txt.index(tk.INSERT))

                if '.0' in self._inp_txt.index(tk.INSERT):
                    self._inp_txt.tag_remove('send', 'insert-1c', tk.INSERT)

        else:
            self._send_to_monitor()

    def _send_to_monitor(self):
        ind = str(self._win_buf[self.channel_index].input_win_index)
        if ind:
            if float(ind) >= float(self._inp_txt.index(tk.INSERT)):
                ind = str(self._inp_txt.index(tk.INSERT))
            ind = str(int(float(ind))) + '.0'
        else:
            ind = '1.0'
        tmp_txt = self._inp_txt.get(ind, self._inp_txt.index(tk.INSERT))
        tmp_txt = tmp_txt.replace('\n', '\r')
        port_id = int(self.tabbed_sideFrame.mon_port_var.get())
        if port_id in PORT_HANDLER.get_all_ports().keys():
            port = PORT_HANDLER.get_all_ports()[port_id]
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
                # self.inp_txt.tag_add('send', ind, str(self.inp_txt.index(tk.INSERT)))
        self._win_buf[self.channel_index].input_win_index = str(self._inp_txt.index(tk.INSERT))
        if int(float(self._inp_txt.index(tk.INSERT))) != int(float(self._inp_txt.index(tk.END))) - 1:
            self._inp_txt.delete(tk.END, tk.END)

    def send_to_qso(self, data, ch_index):
        data = data.replace('\r', '\n')
        data = tk_filter_bad_chars(data)
        _k = ch_index
        _bg = self.get_ch_param(ch_index).qso_tag_bg
        _fg = self.get_ch_param(ch_index).qso_tag_fg
        tag_name_out = self.get_ch_param(ch_index).qso_tag_name
        self._win_buf[_k].output_win += data
        if self.channel_index == _k:
            tr = False
            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index("@0,0")) < 22:
                tr = True

            self._out_txt.configure(state="normal")
            self._out_txt.tag_config(tag_name_out,
                                     foreground=_fg,
                                     background=_bg,
                                     selectbackground=_fg,
                                     selectforeground=_bg
                                     )

            # configuring a tag called start
            ind = self._out_txt.index(tk.INSERT)
            self._out_txt.insert('end', data)
            ind2 = self._out_txt.index(tk.INSERT)
            self._out_txt.tag_add(tag_name_out, ind, ind2)
            self._out_txt.configure(state="disabled",
                                    exportselection=1
                                    )
            if tr or self.get_ch_param().autoscroll:
                self.see_end_qso_win()

        else:
            if tag_name_out not in self._win_buf[_k].output_win_tags.keys():
                self._win_buf[_k].output_win_tags[tag_name_out] = ()
            old_tags = list(self._win_buf[_k].output_win_tags[tag_name_out])
            if old_tags:
                old_tags = old_tags[:-1] + [tk.INSERT]
            else:
                old_tags = ['1.0', tk.INSERT]
            self._win_buf[_k].output_win_tags[tag_name_out] = old_tags
            self._win_buf[_k].new_data_tr = True
        self._win_buf[_k].rx_beep_tr = True
        self.ch_status_update()

    def _on_click_inp_txt(self, event=None):
        _ind = self._win_buf[self.channel_index].input_win_index
        if _ind:
            self._inp_txt.tag_add('send', str(int(float(_ind))) + '.0', _ind)
            # self.inp_txt.tag_remove('send', str(max(float(self.inp_txt.index(tk.INSERT)) - 0.1, 1.0)), self.inp_txt.index(tk.INSERT))
            self._inp_txt.tag_remove('send', str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0',
                                     self._inp_txt.index(tk.INSERT))
        # self.inp_txt.tag_remove('send', tk.line.column, self.inp_txt.index(tk.INSERT))
        _ind2 = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'

        self._inp_txt.tag_remove('send', _ind2, self._inp_txt.index(tk.INSERT))
        self._win_buf[self.channel_index].input_win_index = str(self._inp_txt.index(tk.INSERT))

    # SEND TEXT OUT
    ###################
    # BW Plot
    def _update_bw_mon(self):
        _tr = False
        for _port_id in list(PORT_HANDLER.ax25_ports.keys()):
            _data = MH_LIST.get_bandwidth(
                _port_id,
                PORT_HANDLER.ax25_ports[_port_id].port_cfg.parm_baud,
            )
            _label = f'{PORT_HANDLER.ax25_ports[_port_id].port_cfg.parm_PortName}'
            if _port_id not in self._bw_plot_lines:
                self._bw_plot_lines[int(_port_id)], = self._ax.plot(self._bw_plot_x_scale, _data, label=_label)
                self._ax.legend()
                _tr = True
            else:
                if list(_data) != list(self._bw_plot_lines[int(_port_id)].get_data()[1]):
                    self._bw_plot_lines[int(_port_id)].set_ydata(_data)
                    _tr = True
        if _tr:
            self._draw_bw_plot()

    def _draw_bw_plot(self):
        self._bw_fig.canvas.draw()
        self._bw_fig.canvas.flush_events()
        self._canvas.flush_events()

    def _kaffee(self):
        self.msg_to_monitor('Hinweis: Hier gibt es nur Muckefuck !')
        self.sprech('Gluck gluck gluck blubber blubber')

    def do_priv(self, event=None, login_cmd=''):
        _conn = self.get_conn()
        if _conn:
            if _conn.user_db_ent:
                if _conn.user_db_ent.sys_pw:
                    _conn.cli.start_baycom_login(login_cmd=login_cmd)
                else:
                    self._open_settings_window('priv_win')

    def _switch_monitor_mode(self):
        self._txt_win.switch_mon_mode()
        if self.mon_mode:
            # self.channel_index = int(self.mon_mode)
            self._ch_btn_clk(int(self.mon_mode))
            self.mon_mode = 0
            self._mon_btn.configure(bg='yellow')
        else:
            self.mon_mode = int(self.channel_index)
            self._ch_btn_clk(0)
            self._mon_btn.configure(bg='green')

        self.ch_status_update()

    def switch_channel(self, ch_ind: int = 0):
        # Channel 0 = Monitor
        if not ch_ind:
            self._switch_monitor_mode()
        else:
            if self.mon_mode:
                self.mon_mode = int(ch_ind)
                self._switch_monitor_mode()
            else:
                self._ch_btn_clk(ch_ind)

    def ch_status_update(self):
        """Triggerd when Connection Status has changed"""
        self._ch_btn.ch_btn_status_update()
        # self.change_conn_btn()
        self.on_channel_status_change()

    def _ch_btn_clk(self, ind: int):
        self.get_ch_param().input_win = self._inp_txt.get('1.0', tk.END)
        # self.get_ch_param().input_win_tags = self.inp_txt.tag_ranges('send')
        self.get_ch_param().input_win_tags = get_all_tags(self._inp_txt)
        self.get_ch_param().output_win_tags = get_all_tags(self._out_txt)
        self.get_ch_param().input_win_cursor_index = self._inp_txt.index(tk.INSERT)

        self.channel_index = ind
        self.get_ch_param().new_data_tr = False
        self.get_ch_param().rx_beep_tr = False

        self._out_txt.configure(state="normal")

        self._out_txt.delete('1.0', tk.END)
        self._out_txt.insert(tk.END, self._win_buf[ind].output_win)
        self._out_txt.configure(state="disabled")
        self._out_txt.see(tk.END)

        self._inp_txt.delete('1.0', tk.END)
        self._inp_txt.insert(tk.END, self._win_buf[ind].input_win[:-1])
        set_all_tags(self._inp_txt, self.get_ch_param().input_win_tags)
        set_all_tags(self._out_txt, self.get_ch_param().output_win_tags)
        self._inp_txt.mark_set("insert", self.get_ch_param().input_win_cursor_index)
        self._inp_txt.see(tk.END)

        # self.main_class: gui.guiMainNew.TkMainWin
        if self.get_ch_param().rx_beep_opt and ind:
            self._txt_win.rx_beep_box.select()
            self._txt_win.rx_beep_box.configure(bg='green')
        else:
            self._txt_win.rx_beep_box.deselect()
            self._txt_win.rx_beep_box.configure(bg=STAT_BAR_CLR)

        if self.get_ch_param().timestamp_opt and ind:
            self._txt_win.ts_box_box.select()
            self._txt_win.ts_box_box.configure(bg='green')
        else:
            self._txt_win.ts_box_box.deselect()
            self._txt_win.ts_box_box.configure(bg=STAT_BAR_CLR)

        self.on_channel_status_change()
        self._ch_btn.ch_btn_status_update()
        self._kanal_switch()  # Sprech

    def on_channel_status_change(self):
        """Triggerd when Connection Status has changed"""
        self.tabbed_sideFrame.on_ch_stat_change()
        self.update_station_info()

    def _update_stat_info_conn_timer(self):
        _conn = self.get_conn()
        if _conn:
            self._txt_win.stat_info_timer_var.set(get_time_delta(_conn.cli.time_start))
        else:
            self._txt_win.stat_info_timer_var.set('--:--:--')

    def update_station_info(self):
        _name = '-------'
        _qth = '-------'
        _loc = '------'
        _dist = 0
        _status = '-------'
        _typ = '-----'
        _sw = '---------'
        _enc = ''
        _conn = self.get_conn()
        if _conn:
            _db_ent = _conn.user_db_ent
            if _db_ent:
                if _db_ent.Name:
                    _name = _db_ent.Name
                if _db_ent.QTH:
                    _qth = _db_ent.QTH
                if _db_ent.LOC:
                    _loc = _db_ent.LOC
                if _db_ent.Distance:
                    _dist = _db_ent.Distance
                if _db_ent.TYP:
                    _typ = _db_ent.TYP
                if _db_ent.Software:
                    _sw = _db_ent.Software
                _enc = _db_ent.Encoding
            if _conn.is_link:
                _status = 'LINK'
                self._txt_win.status_label.bind('<Button-1>', )
            elif _conn.pipe is not None:
                _status = 'PIPE'
                self._txt_win.status_label.bind('<Button-1>', )
            elif _conn.ft_obj is not None:
                _status = f'{_conn.ft_obj.dir} FILE'
                self._txt_win.status_label.bind('<Button-1>', lambda: self._open_settings_window('ft_manager'))
            else:
                self._txt_win.status_label.bind('<Button-1>', self.do_priv)
                _status = ['-'] * 7
                if _conn.is_RNR:
                    _status[2] = 'R'
                if _conn.link_holder_on:
                    _status[1] = 'L'
                if _conn.cli.sysop_priv:
                    _status[0] = 'S'
                _status = ''.join(_status)
        if _dist:
            _loc += f" ({_dist} km)"

        self._txt_win.stat_info_status_var.set(_status)
        self._txt_win.stat_info_name_var.set(_name)
        self._txt_win.stat_info_qth_var.set(_qth)
        self._txt_win.stat_info_loc_var.set(_loc)
        self._txt_win.stat_info_typ_var.set(_typ)
        self._txt_win.stat_info_sw_var.set(_sw)
        self._txt_win.stat_info_encoding_var.set(_enc)

    def _update_ft_info(self):
        prog_val = 0
        prog_var = '---.- %'
        size_var = 'Size: ---,- / ---,- kb'
        dur_var = 'Time: --:--:-- / --:--:--'
        bps_var = 'BPS: ---.---'
        next_tx = 'TX in: --- s'
        _conn = self.get_conn()
        if _conn:
            if _conn.ft_obj is not None:
                _ft_obj = _conn.ft_obj
                percentage_completion, data_len, data_sendet, time_spend, time_remaining, baud_rate = _ft_obj.get_ft_infos()
                prog_val = percentage_completion
                prog_var = f"{percentage_completion} %"
                data_len = get_kb_str_fm_bytes(data_len)
                data_sendet = get_kb_str_fm_bytes(data_sendet)
                size_var = f'Size: {data_sendet} / {data_len}'
                t_spend = conv_timestamp_delta(time_spend)
                t_remaining = conv_timestamp_delta(time_remaining)
                dur_var = f'Time: {t_spend} / {t_remaining}'
                bps_var = f"BPS: {format_number(baud_rate)}"
                if _ft_obj.param_wait:
                    n_tx = _ft_obj.last_tx - time.time()
                    next_tx = f'TX in: {max(round(n_tx), 0)} s'

        if self.tabbed_sideFrame.ft_duration_var.get() != dur_var:
            self.tabbed_sideFrame.ft_progress['value'] = prog_val
            self.tabbed_sideFrame.ft_progress_var.set(prog_var)
            self.tabbed_sideFrame.ft_size_var.set(size_var)
            self.tabbed_sideFrame.ft_duration_var.set(dur_var)
            self.tabbed_sideFrame.ft_bps_var.set(bps_var)
            self.tabbed_sideFrame.ft_next_tx_var.set(next_tx)

    def get_ch_new_data_tr(self, ch_id):
        return bool(self._win_buf[ch_id].new_data_tr)

"""
if __name__ == '__main__':
    logger.info(f"PoPT_{VER} start....")
    #############
    # INIT GUI
    # TODO: if setting_gui (running without GUI option):
    logger.info(f"Loading GUI.")
    root = tk.Tk()
    # gui.guiMain.TkMainWin()
    TkMainWin(root)
    root.mainloop()

    logger.info(f"PoPT_{VER} ENDE.")
    print('ENDE')

"""