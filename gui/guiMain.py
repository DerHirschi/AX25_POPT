import datetime
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
from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25monitor import monitor_frame_inp
from cfg.popt_config import POPT_CFG
from fnc.cfg_fnc import cleanup_obj_to_dict, set_obj_att_fm_dict
from fnc.str_fnc import tk_filter_bad_chars, try_decode, get_time_delta, format_number, conv_timestamp_delta, \
    get_kb_str_fm_bytes, conv_time_DE_str
from gui.aprs.guiAISmon import AISmonitor
from gui.aprs.guiAPRS_Settings import APRSSettingsWin
from gui.aprs.guiAPRS_be_tracer import BeaconTracer
from gui.aprs.guiAPRS_pn_msg import APRS_msg_SYS_PN
from gui.aprs.guiAPRS_wx_tree import WXWin
from gui.pms.guiBBS_APRS_MSGcenter import MSG_Center
from gui.pms.guiBBS_PMS_Settings import PMS_Settings
from gui.plots.guiBBS_fwdPath_Plot import FwdGraph
from gui.pms.guiBBS_fwd_q import BBS_fwd_Q
from gui.pms.guiBBS_newMSG import BBS_newMSG
from gui.ft.guiFT_Manager import FileTransferManager
from gui.guiLocatorCalc import LocatorCalculator
from gui.settings.guiPipeToolSettings import PipeToolSettings
from gui.plots.guiPlotPort import PlotWindow
from gui.guiPriv import PrivilegWin

from gui.UserDB.guiUserDBoverview import UserDBtreeview
from gui.settings.guiMulticastSettings import MulticastSettings
from gui.guiMH import MHWin
from gui.guiNewConnWin import NewConnWin
from gui.settings.guiStationSettings import StationSettingsWin
from gui.settings.guiPortSettings import PortSettingsWin
from gui.settings.guiBeaconSettings import BeaconSettings
from gui.settings.guiRxEchoSettings import RxEchoSettings
from gui.settings.guiLinkholderSettings import LinkHolderSettings
from gui.UserDB.guiUserDB import UserDB
from gui.guiAbout import About
from gui.guiHelpKeybinds import KeyBindsHelp
from gui.guiMsgBoxes import open_file_dialog, save_file_dialog
from gui.ft.guiFileTX import FileSend
from cfg.constant import LANGUAGE, FONT, POPT_BANNER, WELCOME_SPEECH, VER, CFG_clr_sys_msg, STATION_TYPS, \
    ENCODINGS, TEXT_SIZE_STATUS, TXT_BACKGROUND_CLR, TXT_OUT_CLR, TXT_INP_CLR, TXT_INP_CURSOR_CLR, TXT_MON_CLR, \
    STAT_BAR_CLR, STAT_BAR_TXT_CLR, FONT_STAT_BAR, STATUS_BG, PARAM_MAX_MON_LEN, CFG_sound_RX_BEEP, CFG_sound_CONN, \
    CFG_sound_DICO, CFG_TR_DX_ALARM_BG_CLR
from cfg.string_tab import STR_TABLE
from fnc.os_fnc import is_linux, is_windows, get_root_dir
from fnc.gui_fnc import get_all_tags, set_all_tags, generate_random_hex_color, set_new_tags, cleanup_tags

if is_linux():
    from playsound import playsound
elif is_windows():
    from winsound import PlaySound, SND_FILENAME, SND_NOWAIT
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt


class ChVars(object):
    output_win = ''
    input_win = ''
    output_win_tags = {}
    input_win_tags = {}
    new_tags = []
    last_tag_name = 'NOCALL'
    input_win_index = '1.0'
    input_win_cursor_index = tk.INSERT
    new_data_tr = False
    rx_beep_tr = False
    rx_beep_cooldown = time.time()
    rx_beep_opt = False
    timestamp_opt = False
    t2speech = False
    t2speech_buf = ''
    autoscroll = True

    # self.hex_output = True


class SideTabbedFrame:  # TODO: WTF
    def __init__(self, main_cl):
        self._main_win = main_cl
        self._lang = int(main_cl.language)
        self.style = main_cl.style
        self.ch_index = main_cl.channel_index
        self._mh = self._main_win.mh
        self._ch_is_disc = False
        _tab_side_frame = tk.Frame(
            main_cl.get_side_frame(),  # TODO: WTF
            # width=300,
            height=400
        )
        _tab_side_frame.grid(row=3, column=0, columnspan=6, pady=10, sticky="nsew")
        """
        s = ttk.Style()
        s.theme_use('default')
        s.configure('TNotebook.Tab', background="green3")
        s.map("TNotebook", background=[("selected", "green3")])
        """
        self._tabControl = ttk.Notebook(
            _tab_side_frame,
            height=300,
            # width=500
        )

        tab1_kanal = ttk.Frame(self._tabControl)
        tab2_mh = tk.Frame(self._tabControl)
        tab4_settings = ttk.Frame(self._tabControl)
        # self.tab5_ch_links = ttk.Frame(self._tabControl)  # TODO
        tab6_monitor = ttk.Frame(self._tabControl)
        tab7_tracer = ttk.Frame(self._tabControl)

        self._tabControl.add(tab1_kanal, text='Kanal')
        # tab3 = ttk.Frame(self._tabControl)                         # TODO
        # self._tabControl.add(tab3, text='Ports')                   # TODO
        self._tabControl.add(tab4_settings, text='Global')
        self._tabControl.add(tab6_monitor, text='Monitor')
        self._tabControl.add(tab2_mh, text='MH')
        self._tabControl.add(tab7_tracer, text='Tracer')

        # self._tabControl.add(self.tab5_ch_links, text='CH-Echo')   # TODO
        self._tabControl.pack(expand=0, fill="both")
        self._tabControl.select(tab2_mh)
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
                                    command=self._set_max_frame,
                                    state='disabled')
        m_f_label.place(x=10, y=parm_y)
        self.max_frame.place(x=10 + 80, y=parm_y)
        parm_y = 55
        p_l_label = tk.Label(tab1_kanal, text='Pac Len:')
        self.pac_len_var = tk.IntVar(tab1_kanal)
        self.pac_len_var.set(128)
        vals = []
        for i in range(256):
            vals.append(str(i + 1))
        self.pac_len = tk.ttk.Combobox(tab1_kanal,
                                       width=4,
                                       textvariable=self.pac_len_var,
                                       values=vals,
                                       state='disabled')
        self.pac_len.bind("<<ComboboxSelected>>", self._set_pac_len)
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
        self._rnr_var = tk.BooleanVar(tab1_kanal)

        self._rnr = tk.Checkbutton(tab1_kanal,
                                   text='RNR',
                                   variable=self._rnr_var,
                                   command=self._chk_rnr)
        self._rnr.place(x=10, y=parm_y)
        # Sprech
        parm_y = 200
        self.t2speech_var = tk.BooleanVar(tab1_kanal)

        self.t2speech = tk.Checkbutton(tab1_kanal,
                                       text='Sprachausgabe',
                                       variable=self.t2speech_var,
                                       command=self._chk_t2speech)
        self.t2speech.place(x=10, y=parm_y)
        self.t2speech_var.set(self._main_win.get_ch_var().t2speech)
        # Autoscroll
        parm_y = 225
        self.autoscroll_var = tk.BooleanVar(tab1_kanal)

        self.autoscroll = tk.Checkbutton(tab1_kanal,
                                         text='Autoscroll',
                                         variable=self.autoscroll_var,
                                         command=self._chk_autoscroll
                                         )
        self.autoscroll.place(x=10, y=parm_y)
        self.autoscroll_var.set(self._main_win.get_ch_var().autoscroll)

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
                                      command=self._main_win.clear_channel_vars
                                      )
        clear_ch_data_btn.place(x=140, y=135)

        link_holder_settings_btn = tk.Button(tab1_kanal,
                                             text='Linkhalter',
                                             command=self._main_win.open_link_holder_sett
                                             )
        link_holder_settings_btn.place(x=140, y=165)
        # RTT
        self._rtt_worst_var = tk.StringVar(tab1_kanal)
        self._rtt_avg_var = tk.StringVar(tab1_kanal)
        self._rtt_last_var = tk.StringVar(tab1_kanal)
        self._rtt_best_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._rtt_best_var).place(x=170, y=10)
        tk.Label(tab1_kanal, textvariable=self._rtt_worst_var).place(x=170, y=35)
        tk.Label(tab1_kanal, textvariable=self._rtt_avg_var).place(x=170, y=60)
        tk.Label(tab1_kanal, textvariable=self._rtt_last_var).place(x=170, y=85)

        ##########################################
        # Kanal Rechts / Status / FT
        ttk.Separator(tab1_kanal, orient='vertical').place(x=280, rely=0.05, relheight=0.9, relwidth=0.6)
        ##########################################

        # Conn Dauer
        _x = 290
        _y = 20
        self._conn_durration_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._conn_durration_var).place(x=_x, y=_y)
        self._conn_durration_var.set('--:--:--')
        #### conn_durration_var
        # TX Buffer
        _x = 290
        _y = 45
        self._tx_buff_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._tx_buff_var).place(x=_x, y=_y)
        self._tx_buff_var.set('')
        # TX Gesamt
        _x = 290
        _y = 70
        self._tx_count_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._tx_count_var).place(x=_x, y=_y)
        self._tx_count_var.set('')
        # RX Gesamt
        _x = 290
        _y = 95
        self._rx_count_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._rx_count_var).place(x=_x, y=_y)
        self._rx_count_var.set('')

        # Status /Pipe/Link/File-RX/File-TX
        self._status_label_var = tk.StringVar(tab1_kanal)
        status_label = tk.Label(tab1_kanal, fg='red', textvariable=self._status_label_var)
        font = status_label.cget('font')
        status_label.configure(font=(font[0], 12))
        status_label.place(x=290, y=120)
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
        tk.Label(tab1_kanal, textvariable=self.ft_size_var).place(x=_x, y=_y + 25)
        tk.Label(tab1_kanal, textvariable=self.ft_duration_var).place(x=_x, y=_y + 50)
        tk.Label(tab1_kanal, textvariable=self.ft_bps_var).place(x=_x, y=_y + 75)
        tk.Label(tab1_kanal, textvariable=self.ft_next_tx_var).place(x=_x + 160, y=_y + 75)
        # self.ft_progress_var.set(f"--- %")
        # self.ft_size_var.set(f"Size: 10.000,0 / 20.00,0 kb")
        # self.ft_duration_var.set(f"Time: 00:00:00 / 00:00:00")
        # self.ft_bps_var.set(f"BPS: 100.000")
        #######################################################################
        # MH ##########################
        # TREE
        tab2_mh.rowconfigure(0, minsize=100, weight=1)
        tab2_mh.rowconfigure(1, minsize=50, weight=0)
        tab2_mh.columnconfigure(0, minsize=150, weight=1)
        tab2_mh.columnconfigure(1, minsize=150, weight=1)

        columns = (
            'mh_last_seen',
            'mh_call',
            'mh_dist',
            'mh_port',
            'mh_nPackets',
            'mh_route',
        )

        self._tree = ttk.Treeview(tab2_mh, columns=columns, show='headings')
        self._tree.grid(row=0, column=0, columnspan=2, sticky='nsew')

        self._tree.heading('mh_last_seen', text='Zeit')
        self._tree.heading('mh_call', text='Call')
        self._tree.heading('mh_dist', text='km')
        self._tree.heading('mh_port', text='Port')
        self._tree.heading('mh_nPackets', text='PACK')
        self._tree.heading('mh_route', text='Route')
        self._tree.column("mh_last_seen", anchor=tk.W, stretch=tk.NO, width=85)
        self._tree.column("mh_call", anchor=tk.W, stretch=tk.NO, width=105)
        self._tree.column("mh_dist", anchor=tk.CENTER, stretch=tk.NO, width=70)
        self._tree.column("mh_port", anchor=tk.W, stretch=tk.NO, width=61)
        self._tree.column("mh_nPackets", anchor=tk.W, stretch=tk.NO, width=60)
        self._tree.column("mh_route", anchor=tk.W, stretch=tk.YES, width=180)
        self._tree.tag_configure("dx_alarm", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')

        self._tree_data = []
        self._last_mh_ent = []
        # self._update_side_mh()
        self._tree.bind('<<TreeviewSelect>>', self._entry_selected)

        btn_frame = tk.Frame(tab2_mh)
        btn_frame.grid(row=1, column=0)
        tk.Button(btn_frame,
                  text="MH",
                  command=self._open_mh
                  ).pack(side=tk.LEFT, padx=50)
        tk.Button(btn_frame,
                  text="Statistic",
                  command=self._open_PortStat
                  ).pack(side=tk.LEFT, padx=50)

        #############################################################################
        # Global Settings ################################
        # Global Sound
        Checkbutton(tab4_settings,
                    text="Sound",
                    variable=self._main_win.setting_sound,
                    ).place(x=10, y=10)
        # Global Sprech
        sprech_btn = Checkbutton(tab4_settings,
                                 text="Sprachausgabe",
                                 variable=self._main_win.setting_sprech,
                                 command=self._chk_sprech_on
                                 )
        sprech_btn.place(x=10, y=35)
        if not is_linux():
            sprech_btn.configure(state='disabled')
        # Global Bake
        Checkbutton(tab4_settings,
                    text="Baken",
                    variable=self._main_win.setting_bake,
                    command=self._chk_beacon,
                    ).place(x=10, y=60)
        # DX Alarm  > dx_alarm_on
        Checkbutton(tab4_settings,
                    text="Tracer",
                    variable=self._main_win.setting_tracer,
                    command=self._chk_tracer,
                    # state='disabled'
                    ).place(x=10, y=85)
        _auto_tracer_state = {
            True: 'disabled',
            False: 'normal'
        }.get(self._main_win.get_tracer(), 'disabled')
        self._autotracer_chk_btn = Checkbutton(tab4_settings,
                                               text="Auto-Tracer",
                                               variable=self._main_win.setting_auto_tracer,
                                               command=self._chk_auto_tracer,
                                               state=_auto_tracer_state
                                               )
        self._autotracer_chk_btn.place(x=10, y=110)
        Checkbutton(tab4_settings,
                    text="DX-Alarm",
                    variable=self._main_win.setting_dx_alarm,
                    command=self._main_win.set_dx_alarm,
                    # state='disabled'
                    ).place(x=10, y=135)
        # RX ECHO
        Checkbutton(tab4_settings,
                    text="RX-Echo",
                    variable=self._main_win.setting_rx_echo,
                    ).place(x=10, y=160)
        ############
        # CH ECHO
        self._chk_btn_default_clr = self._autotracer_chk_btn.cget('bg')
        self._ch_echo_vars = {}
        #################
        ###################################################################################
        # Monitor Frame
        # Address
        _x = 10
        _y = 10
        self.to_add_var = tk.StringVar(tab6_monitor)
        tk.Label(tab6_monitor, text=f"{STR_TABLE['to'][self._lang]}:").place(x=_x, y=_y)
        tk.Entry(tab6_monitor, textvariable=self.to_add_var).place(x=_x + 40, y=_y)

        # CMD/RPT
        _x = 10
        _y = 80
        self.cmd_var = tk.BooleanVar(tab6_monitor)
        tk.Checkbutton(tab6_monitor,
                       variable=self.cmd_var,
                       text='CMD/RPT').place(x=_x, y=_y)

        # Poll
        _x = 10
        _y = 105
        self.poll_var = tk.BooleanVar(tab6_monitor)
        tk.Checkbutton(tab6_monitor,
                       variable=self.poll_var,
                       text='Poll').place(x=_x, y=_y)

        # Port
        _x = 40
        _y = 140
        tk.Label(tab6_monitor, text=f"{STR_TABLE['port'][self._lang]}:").place(x=_x, y=_y)
        self.mon_port_var = tk.StringVar(tab6_monitor)
        self.mon_port_var.set('0')
        _vals = ['0']
        if PORT_HANDLER.get_all_ports().keys():
            _vals = [str(x) for x in list(PORT_HANDLER.get_all_ports().keys())]
        mon_port_ent = tk.ttk.Combobox(tab6_monitor,
                                       width=4,
                                       textvariable=self.mon_port_var,
                                       values=_vals,
                                       )
        mon_port_ent.place(x=_x + 50, y=_y)
        mon_port_ent.bind("<<ComboboxSelected>>", self._chk_mon_port)
        # Calls
        _x = 40
        _y = 175
        self.mon_call_var = tk.StringVar(tab6_monitor)
        _vals = []
        # if self.main_win.ax25_port_handler.ax25_ports.keys():
        #     _vals = [str(x) for x in list(self.main_win.ax25_port_handler.ax25_ports.keys())]
        self.mon_call_ent = tk.ttk.Combobox(tab6_monitor,
                                            width=9,
                                            textvariable=self.mon_call_var,
                                            values=_vals,
                                            )
        self.mon_call_ent.place(x=_x, y=_y)

        # Auto Scrolling
        _x = 10
        _y = 210
        self.mon_scroll_var = tk.BooleanVar(tab6_monitor)
        tk.Checkbutton(tab6_monitor,
                       variable=self.mon_scroll_var,
                       text=STR_TABLE['scrolling'][self._lang]).place(x=_x, y=_y)

        # Monitor APRS Decoding Output
        _x = 10
        _y = 235
        self.mon_aprs_var = tk.BooleanVar(tab6_monitor)
        self.mon_aprs_var.set(True)
        tk.Checkbutton(tab6_monitor,
                       variable=self.mon_aprs_var,
                       text='APRS-Decoding').place(x=_x, y=_y)

        # PID
        _x = 10
        _y = 45
        self.mon_pid_var = tk.StringVar(tab6_monitor)
        tk.Label(tab6_monitor, text='PID:').place(x=_x, y=_y)
        pid = PIDByte()  # TODO CONST PIDByte().pac_types
        pac_types = dict(pid.pac_types)
        _vals = []
        for x in list(pac_types.keys()):
            pid.pac_types[int(x)]()
            _vals.append(f"{str(hex(int(x))).upper()}>{pid.flag}")
        tk.ttk.Combobox(tab6_monitor,
                        width=20,
                        values=_vals,
                        textvariable=self.mon_pid_var).place(x=_x + 40, y=_y)
        self.mon_pid_var.set(_vals[0])
        # self.pac_len.bind("<<ComboboxSelected>>", self.set_pac_len)
        # Monitor RX-Filter Ports
        self._mon_port_on_vars = {}
        all_ports = PORT_HANDLER.get_all_ports()
        for port_id in all_ports:
            self._mon_port_on_vars[port_id] = tk.BooleanVar(tab6_monitor)
            _x = 170
            _y = 80 + (25 * port_id)
            tk.Checkbutton(tab6_monitor,
                           text=f"Port {port_id}",
                           variable=self._mon_port_on_vars[port_id],
                           command=self._chk_mon_port_filter
                           ).place(x=_x, y=_y)
            self._mon_port_on_vars[port_id].set(all_ports[port_id].monitor_out)
        ######################################################################################
        # TRACER
        # TREE
        tab7_tracer.columnconfigure(0, minsize=150, weight=1)
        tab7_tracer.columnconfigure(1, minsize=150, weight=1)
        tab7_tracer.rowconfigure(0, minsize=100, weight=1)
        tab7_tracer.rowconfigure(1, minsize=50, weight=0)

        tracer_columns = (
            'rx_time',
            'call',
            'port',
            'distance',
            'path',
        )

        self._trace_tree = ttk.Treeview(tab7_tracer, columns=tracer_columns, show='headings')
        self._trace_tree.grid(row=0, column=0, columnspan=2, sticky='nsew')

        self._trace_tree.heading('rx_time', text='Zeit')
        self._trace_tree.heading('call', text='Call')
        self._trace_tree.heading('port', text='Port')
        self._trace_tree.heading('distance', text='km')
        self._trace_tree.heading('path', text='Path')
        self._trace_tree.column("rx_time", anchor=tk.CENTER, stretch=tk.YES, width=90)
        self._trace_tree.column("call", stretch=tk.YES, width=80)
        self._trace_tree.column("port", anchor=tk.CENTER, stretch=tk.NO, width=60)
        self._trace_tree.column("distance", stretch=tk.NO, width=70)
        self._trace_tree.column("path", anchor=tk.CENTER, stretch=tk.YES, width=180)
        self._trace_tree.bind('<<TreeviewSelect>>', self._trace_entry_selected)

        self._trace_tree_data = []
        self._trace_tree_data_old = {}
        self._update_side_trace()
        btn_frame = tk.Frame(tab7_tracer)
        btn_frame.grid(row=1, column=0)
        tk.Button(btn_frame,
                  text="SEND",
                  command=self._tracer_send
                  ).pack(side=tk.LEFT, padx=50)
        tk.Button(btn_frame,
                  text="Tracer",
                  command=self._open_tracer
                  ).pack(side=tk.LEFT, padx=50)

        # tk.Button(tab7_tracer, text="SEND").grid(row=1, column=1, padx=10)

        ##################
        # Tasker
        self._tasker_dict = {
            0: self._update_rtt,
            3: self._update_side_mh,
            4: self._update_side_trace,
        }

        self._chk_mon_port()
        # self._update_ch_echo()
        self._update_side_mh()
        self._update_side_trace()

    """
    def _init_tab_style(self):
        s = ttk.Style()
        s.theme_use('default')
        s.configure('TNotebook.Tab', background="green3")
        s.map("TNotebook", background=[("selected", "green3")])
    """

    def set_auto_tracer_state(self):
        _bool_state = self._main_win.get_tracer() or not self._main_win.get_dx_alarm()
        _state = {
            True: 'disabled',
            False: 'normal'
        }.get(_bool_state, 'disabled')
        self._autotracer_chk_btn.configure(state=_state)

    """
    def _update_ch_echo(self):
        # TODO AGAIN !!
        _tab = self.tab5_ch_links
        akt_ch_id = self._main_win.channel_index
        _var = tk.BooleanVar(_tab)
        for ch_id in list(self._ch_echo_vars.keys()):
            if ch_id not in list(PORT_HANDLER.get_all_connections().keys()):
                self._ch_echo_vars[ch_id][1].destroy()
                del self._ch_echo_vars[ch_id]
        for ch_id in list(PORT_HANDLER.get_all_connections().keys()):
            conn = PORT_HANDLER.get_all_connections()[ch_id]
            if ch_id not in self._ch_echo_vars.keys():
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
                self._ch_echo_vars[ch_id] = tmp
            else:
                self._ch_echo_vars[ch_id][1].configure(state='normal')
                self._ch_echo_vars[ch_id][1].configure(text=conn.to_call_str)
            if ch_id != akt_ch_id:
                self._ch_echo_vars[ch_id][1].configure(state='normal')
            else:
                self._ch_echo_vars[ch_id][1].configure(state='disabled')
            if akt_ch_id in self._ch_echo_vars.keys():
                if self._ch_echo_vars[ch_id][0].get() and self._ch_echo_vars[akt_ch_id][0].get():
                    self._ch_echo_vars[ch_id][1].configure(bg='green1')
                    self._ch_echo_vars[akt_ch_id][1].configure(bg='green1')
                else:
                    self._ch_echo_vars[ch_id][1].configure(bg=self._chk_btn_default_clr)
                    self._ch_echo_vars[akt_ch_id][1].configure(bg=self._chk_btn_default_clr)

        # self.sound_on.set(1)
    """
    """ 
    def _chk_ch_echo(self):
        # self.main_win.channel_index
        for ch_id in list(self._ch_echo_vars.keys()):
            _vars = self._ch_echo_vars[ch_id]
            if ch_id != self._main_win.channel_index:
                if _vars[0].get() and self._ch_echo_vars[self._main_win.channel_index][0].get():
                    PORT_HANDLER.get_all_connections()[ch_id].ch_echo.append(
                        PORT_HANDLER.get_all_connections()[self._main_win.channel_index])
                    PORT_HANDLER.get_all_connections()[self._main_win.channel_index].ch_echo.append(
                        PORT_HANDLER.get_all_connections()[ch_id])
                else:
                    if PORT_HANDLER.get_all_connections()[self._main_win.channel_index] in \
                            PORT_HANDLER.get_all_connections()[ch_id].ch_echo:
                        PORT_HANDLER.get_all_connections()[ch_id].ch_echo.remove(
                            PORT_HANDLER.get_all_connections()[self._main_win.channel_index])

                    if PORT_HANDLER.get_all_connections()[ch_id] in PORT_HANDLER.get_all_connections()[
                        self._main_win.channel_index].ch_echo:
                        PORT_HANDLER.get_all_connections()[self._main_win.channel_index].ch_echo.remove(
                            PORT_HANDLER.get_all_connections()[ch_id])
        
          
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

    """
    def _chk_dx_alarm(self):
        self._main_win.setting_dx_alarm = self.dx_alarm_on.get()
    """

    def _chk_tracer(self):
        self._main_win.set_tracer()

    def _chk_beacon(self):
        POPT_CFG.set_guiPARM_main({
            'gui_cfg_beacon': bool(self._main_win.setting_bake.get())
        })

    def _chk_auto_tracer(self):
        self._main_win.set_auto_tracer()

    def _chk_rnr(self):
        conn = self._main_win.get_conn()
        if conn is not None:
            if self._rnr_var.get():
                conn.set_RNR()
            else:
                conn.unset_RNR()

    def _chk_link_holder(self):
        conn = self._main_win.get_conn()
        if conn is not None:
            if self.link_holder_var.get():
                conn.link_holder_on = True
                conn.link_holder_timer = 0
            else:
                conn.link_holder_on = False
            self._main_win.on_channel_status_change()

    def _chk_t2auto(self):
        _conn = self._main_win.get_conn()
        if _conn is not None:
            if self.t2_auto_var.get():
                _conn.own_port.port_cfg.parm_T2_auto = True
                _conn.calc_irtt()
                self.t2_var.set(str(_conn.parm_T2 * 1000))
                self.t2.configure(state='disabled')
            else:
                _conn.own_port.port_cfg.parm_T2_auto = False
                self.t2.configure(state='normal')
            _conn.calc_irtt()

    def _chk_sprech_on(self):

        if self._main_win.setting_sprech.get():
            self.t2speech.configure(state='normal')
        else:
            self.t2speech.configure(state='disabled')
        self._main_win.set_var_to_all_ch_param()

    def _chk_mon_port(self, event=None):
        port_id = int(self.mon_port_var.get())
        vals = PORT_HANDLER.get_stat_calls_fm_port(port_id)
        if vals:
            self.mon_call_var.set(vals[0])
        self.mon_call_ent.configure(values=vals)

    def _chk_mon_port_filter(self):
        _all_ports = PORT_HANDLER.get_all_ports()
        for port_id in _all_ports:
            _all_ports[port_id].monitor_out = self._mon_port_on_vars[port_id].get()

    def update_mon_port_id(self):
        if PORT_HANDLER.get_all_ports().keys():
            _vals = [str(x) for x in list(PORT_HANDLER.get_all_ports().keys())]
            self.mon_call_ent.configure(values=_vals)

    def _set_t2(self, event):
        conn = self._main_win.get_conn()
        if conn is not None:
            conn.cfg.parm_T2 = min(max(int(self.t2_var.get()), 500), 3000)
            conn.calc_irtt()

    def tasker(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except TclError:
            pass
        else:
            if ind in self._tasker_dict.keys():
                self._tasker_dict[ind]()

    def _entry_selected(self, event):
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[1]
            vias = record[5]
            port = record[3]
            if type(port) is str:
                port = int(port.split(' ')[0])

            if vias:
                call = f'{call} {vias}'
            if not self._main_win.new_conn_win:
                self._main_win.open_new_conn_win()
            if self._main_win.new_conn_win:
                self._main_win.new_conn_win.preset_ent(call, port)

    def _trace_entry_selected(self, event=None):
        pass
        # self._main_win.open_be_tracer_win()

    @staticmethod
    def _tracer_send():
        PORT_HANDLER.get_aprs_ais().tracer_sendit()

    # MH
    def _format_tree_ent(self):
        self._tree_data = []
        for k in self._last_mh_ent:
            # ent: MyHeard
            ent = k
            route = ent.route
            dx_alarm = False
            if ent.own_call in list(self._mh.dx_alarm_hist):
                dx_alarm = True
            self._tree_data.append(
                ((
                     f"{conv_time_DE_str(ent.last_seen).split(' ')[1]}",
                     f'{ent.own_call}',
                     f'{ent.distance}',
                     f'{ent.port_id}',
                     f'{ent.pac_n}',
                     ' '.join(route),
                 ), dx_alarm)
            )

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
        _station = self._main_win.get_conn(self._main_win.channel_index)
        if _station is not None:
            if _station.RTT_Timer.rtt_best == 999.0:
                best = "Best: -1"
            else:
                best = "Best: {:.1f}".format(_station.RTT_Timer.rtt_best)
            worst = "Worst: {:.1f}".format(_station.RTT_Timer.rtt_worst)
            avg = "AVG: {:.1f}".format(_station.RTT_Timer.rtt_average)
            last = "Last: {:.1f}".format(_station.RTT_Timer.rtt_last)
            duration = f"{STR_TABLE['time_connected'][self._lang]}: {get_time_delta(_station.time_start)}"
            tx_buff = 'TX-Buffer: ' + get_kb_str_fm_bytes(len(_station.tx_buf_rawData))
            tx_count = 'TX: ' + get_kb_str_fm_bytes(_station.tx_byte_count)
            rx_count = 'RX: ' + get_kb_str_fm_bytes(_station.rx_byte_count)
            if _station.is_link:
                status_text = 'Link'
            elif _station.pipe is not None:
                status_text = 'Pipe'
            elif _station.ft_obj is not None:
                if _station.ft_obj.dir == 'TX':
                    status_text = 'Sending File'
                else:
                    status_text = 'Receiving File'
        if duration != self._conn_durration_var.get():
            self._status_label_var.set(status_text)
            self._rtt_best_var.set(best)
            self._rtt_worst_var.set(worst)
            self._rtt_avg_var.set(avg)
            self._rtt_last_var.set(last)
            self._conn_durration_var.set(duration)
            self._tx_buff_var.set(tx_buff)
            self._tx_count_var.set(tx_count)
            self._rx_count_var.set(rx_count)

    ##########################################################
    # MH
    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            if ret_ent[1] and self._mh.dx_alarm_trigger:
                self._tree.insert('', tk.END, values=ret_ent[0], tags=('dx_alarm',))
            else:
                self._tree.insert('', tk.END, values=ret_ent[0], )

    def _update_side_mh(self):
        mh_ent = list(self._mh.output_sort_entr(10))
        if mh_ent != self._last_mh_ent:
            self._last_mh_ent = mh_ent
            self._format_tree_ent()
            self._update_tree()

    def reset_dx_alarm(self):
        mh_ent = list(self._mh.output_sort_entr(10))
        self._last_mh_ent = mh_ent
        self._format_tree_ent()
        self._update_tree()

    ############################################################
    # Tracer
    def _update_side_trace(self):
        self._format_trace_tree_data()
        # self._update_trace_tree()

    def _format_trace_tree_data(self):
        traces = dict(PORT_HANDLER.get_aprs_ais().tracer_traces_get())
        if self._trace_tree_data_old != len(str(traces)):
            self._trace_tree_data_old = len(str(traces))
            self._trace_tree_data = []
            for k in traces.keys():
                pack = traces[k][-1]
                rx_time = pack.get('rx_time', '')
                if rx_time:
                    rx_time = rx_time.strftime('%H:%M:%S')
                path = pack.get('path', [])
                call = pack.get('call', '')
                if call:
                    path = ', '.join(path)
                    port_id = pack.get('port_id', -1)
                    # rtt = pack.get('rtt', 0)
                    # loc = pack.get('locator', '')
                    dist = pack.get('distance', 0)

                    self._trace_tree_data.append((
                        rx_time,
                        call,
                        port_id,
                        dist,
                        path,
                    ))
            self._update_trace_tree()

    def _update_trace_tree(self):
        for i in self._trace_tree.get_children():
            self._trace_tree.delete(i)
        for ret_ent in self._trace_tree_data:
            self._trace_tree.insert('', tk.END, values=ret_ent)

    def on_ch_stat_change(self):
        _conn = self._main_win.get_conn()
        if _conn is not None:
            if self._ch_is_disc:
                self._ch_is_disc = False
                self.max_frame.configure(state='normal')
                self.pac_len.configure(state='normal')
                self._rnr.configure(state='normal')
                self.link_holder.configure(state='normal')
                self.t2_auto.configure(state='normal')

            self.max_frame_var.set(str(_conn.parm_MaxFrame))
            self.pac_len_var.set(_conn.parm_PacLen)
            self._rnr_var.set(_conn.is_RNR)
            self.link_holder_var.set(_conn.link_holder_on)
            self._tx_buff_var.set('TX-Buffer: ' + get_kb_str_fm_bytes(len(_conn.tx_buf_rawData)))
            if _conn.own_port.port_cfg.parm_T2_auto:  # FIXME var parm_T2_auto to connection
                if not self.t2_auto_var.get():
                    self.t2_var.set(str(_conn.parm_T2 * 1000))
                    self.t2.configure(state='disabled')
            else:
                if self.t2_auto_var.get():
                    self.t2.configure(state='normal')
                    self.t2_var.set(str(_conn.parm_T2 * 1000))
            self.t2_auto_var.set(_conn.own_port.port_cfg.parm_T2_auto)

        else:
            if not self._ch_is_disc:
                self._ch_is_disc = True
                self.max_frame.configure(state='disabled')
                self.pac_len.configure(state='disabled')
                self._rnr_var.set(False)
                # self.rnr.deselect()
                self._rnr.configure(state='disabled')
                self.t2_auto_var.set(False)
                # self.t2_auto.deselect()
                self.t2_auto.configure(state='disabled')
                self.t2.configure(state='disabled')
                self.link_holder_var.set(False)
                self.link_holder.configure(state='disabled')
                self._tx_buff_var.set('TX-Buffer: --- kb')
                self._tx_count_var.set('TX: --- kb')
                self._rx_count_var.set('RX: --- kb')

        self.t2speech_var.set(self._main_win.get_ch_var().t2speech)
        # self._update_ch_echo()

    def _set_max_frame(self):
        conn = self._main_win.get_conn()
        if conn is not None:
            conn.parm_MaxFrame = int(self.max_frame_var.get())

    def _set_pac_len(self, event):
        conn = self._main_win.get_conn()
        if conn is not None:
            conn.parm_PacLen = min(max(self.pac_len_var.get(), 1), 256)
            conn.calc_irtt()
            self.t2_var.set(str(conn.parm_T2 * 1000))

    def _chk_t2speech(self):
        self._main_win.get_ch_var().t2speech = bool(self.t2speech_var.get())

    def _chk_autoscroll(self):
        self._main_win.get_ch_var().autoscroll = bool(self.autoscroll_var.get())
        if bool(self.autoscroll_var.get()):
            self._main_win.see_end_qso_win()

    def _open_tracer(self):
        self._main_win.open_be_tracer_win()

    def _open_mh(self):
        self._main_win.open_MH_win()

    def _open_PortStat(self):
        self._main_win.open_window('PortStat')


class PoPT_GUI_Main:
    def __init__(self):
        ######################################
        # GUI Stuff
        self.main_win = tk.Tk()
        self.main_win.title(f"P.ython o.ther P.acket T.erminal {VER}")
        self.main_win.geometry("1400x850")  # TODO to/fm CFG
        try:
            self.main_win.iconbitmap("favicon.ico")
        except TclError:
            pass
        self.main_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
        ##########################
        self.style = ttk.Style()
        # self.style.theme_use('classic')
        # self.style.theme_use('clam')
        ######################################
        # Init Vars
        # self.language = POPT_CFG.get_guiCFG_language()
        self.mh = PORT_HANDLER.get_MH()
        self.language = LANGUAGE
        self.text_size = POPT_CFG.load_guiPARM_main().get('gui_parm_text_size', 13)
        ###############################
        self._root_dir = get_root_dir()
        self._root_dir = self._root_dir.replace('/', '//')
        #####################
        # GUI VARS
        self.connect_history = POPT_CFG.load_guiPARM_main().get('gui_parm_connect_history', {})
        # GLb Setting Vars
        self.setting_sound = tk.BooleanVar(self.main_win)
        self.setting_sprech = tk.BooleanVar(self.main_win)
        self.setting_bake = tk.BooleanVar(self.main_win)
        self.setting_rx_echo = tk.BooleanVar(self.main_win)
        self.setting_tracer = tk.BooleanVar(self.main_win)
        self.setting_auto_tracer = tk.BooleanVar(self.main_win)
        self.setting_dx_alarm = tk.BooleanVar(self.main_win)
        ###################
        # Status Frame Vars
        self._status_name_var = tk.StringVar(self.main_win)
        self._status_status_var = tk.StringVar(self.main_win)
        self._status_unack_var = tk.StringVar(self.main_win)
        self._status_vs_var = tk.StringVar(self.main_win)
        self._status_n2_var = tk.StringVar(self.main_win)
        self._status_t1_var = tk.StringVar(self.main_win)
        self._status_t2_var = tk.StringVar(self.main_win)
        self._status_rtt_var = tk.StringVar(self.main_win)
        self._status_t3_var = tk.StringVar(self.main_win)
        self._rx_beep_var = tk.IntVar(self.main_win)
        self._ts_box_var = tk.IntVar(self.main_win)
        # Stat INFO (Name,QTH usw)
        self.stat_info_name_var = tk.StringVar(self.main_win)
        self.stat_info_qth_var = tk.StringVar(self.main_win)
        self.stat_info_loc_var = tk.StringVar(self.main_win)
        self.stat_info_typ_var = tk.StringVar(self.main_win)
        self.stat_info_sw_var = tk.StringVar(self.main_win)
        self.stat_info_timer_var = tk.StringVar(self.main_win)
        self.stat_info_encoding_var = tk.StringVar(self.main_win)
        self.stat_info_status_var = tk.StringVar(self.main_win)
        ##############
        # Controlling
        self._ch_alarm = False
        self.channel_index = 1
        self.mon_mode = 0
        self._sound_th = None
        self._is_closing = False
        ####################
        # GUI PARAM
        self._parm_btn_blink_time = 1  # s
        self._parm_rx_beep_cooldown = 2  # s
        # Tasker Timings
        self._loop_delay = 60  # ms
        self._parm_non_prio_task_timer = 0.25  # s
        self._parm_non_non_prio_task_timer = 1  # s
        self._parm_non_non_non_prio_task_timer = 5  # s
        self._parm_test_task_timer = 60  # 5        # s
        self._non_prio_task_timer = time.time()
        self._non_non_prio_task_timer = time.time()
        self._non_non_non_prio_task_timer = time.time()
        self._test_task_timer = time.time()
        ########################################
        ############################
        # Windows
        self.new_conn_win = None
        self.settings_win = None
        self.mh_window = None
        self.wx_window = None
        self.port_stat_win = None
        self.be_tracer_win = None
        self.locator_calc_window = None
        self.aprs_mon_win = None
        self.aprs_pn_msg_win = None
        self.userdb_win = None
        self.userDB_tree_win = None
        self.FileSend_win = None
        self.BBS_fwd_q_list = None
        self.MSG_Center_win = None
        self.newPMS_MSG_win = None
        self.fwd_Path_plot_win = None
        ####################################
        self._init_GUI_vars_fm_CFG()
        ####################################
        # Window Text Buffers & Channel Vars
        self._channel_vars = {}
        self._init_Channel_Vars()
        ######################################
        # ....
        main_pw = ttk.PanedWindow(self.main_win, orient=tk.HORIZONTAL)
        main_pw.pack(fill=tk.BOTH, expand=True)

        l_frame = tk.Frame(main_pw)
        self._r_frame = tk.Frame(main_pw)
        r_pack_frame = tk.Frame(self._r_frame)
        l_frame.pack(fill=tk.BOTH, expand=True)
        self._r_frame.pack(fill=tk.BOTH, expand=True)
        r_pack_frame.pack(fill=tk.BOTH, expand=True)
        main_pw.add(l_frame, weight=100)
        main_pw.add(self._r_frame, weight=1)

        r_pack_frame.rowconfigure(0, minsize=3, weight=1)  # Boarder
        r_pack_frame.rowconfigure(1, minsize=220, weight=2)
        r_pack_frame.rowconfigure(2, minsize=28, weight=1)  # CH BTN
        ###########################################
        # Channel Buttons
        self._ch_btn_blink_timer = time.time()
        self._con_btn_dict = {}
        ch_btn_frame = tk.Frame(l_frame)
        ch_btn_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, )
        self._init_ch_btn_frame(ch_btn_frame)
        ###########################################
        # Input Output TXT Frames and Status Bar
        self._pw = ttk.PanedWindow(l_frame, orient=tk.VERTICAL, )
        self._pw.pack(side=tk.BOTTOM, expand=1)
        # Input
        self._TXT_upper_frame = tk.Frame(self._pw, bd=0, borderwidth=0, bg=STAT_BAR_CLR)
        self._TXT_upper_frame.pack(side=tk.BOTTOM, expand=1)
        # QSO
        self._TXT_mid_frame = tk.Frame(self._pw, bd=0, borderwidth=0, )
        self._TXT_mid_frame.pack(side=tk.BOTTOM, expand=1)
        # Mon
        self._TXT_lower_frame = tk.Frame(self._pw, bd=0, borderwidth=0, )
        self._TXT_lower_frame.pack(side=tk.BOTTOM, expand=1)

        self._inp_txt = None
        self._out_txt = None
        self._mon_txt = None
        self._init_TXT_frame_up()
        self._init_TXT_frame_mid()
        self._init_TXT_frame_low()

        self._pw.add(self._TXT_upper_frame, weight=1)
        self._pw.add(self._TXT_mid_frame, weight=1)
        self._pw.add(self._TXT_lower_frame, weight=1)
        #########################
        #########################
        # Tabbed Frame right
        self._side_btn_frame_top = tk.Frame(r_pack_frame, )
        self._side_btn_frame_top.grid(row=1, rowspan=1, column=1, sticky="nsew")
        self._side_btn_frame_top.rowconfigure(0, minsize=40, weight=0)  # CONN BTN
        self._side_btn_frame_top.rowconfigure(1, minsize=40, weight=0)  # BTN row 2
        self._side_btn_frame_top.rowconfigure(2, minsize=1, weight=0)  # Dummy
        self._side_btn_frame_top.rowconfigure(3, minsize=300, weight=10)  # Reiter Frame

        self._side_btn_frame_top.columnconfigure(0, minsize=10, weight=0)
        self._side_btn_frame_top.columnconfigure(1, minsize=100, weight=2)
        self._side_btn_frame_top.columnconfigure(2, minsize=100, weight=2)
        ##############
        # GUI Buttons
        self._init_btn()
        ##############
        # Side Frame
        self.tabbed_sideFrame = SideTabbedFrame(self)
        ############################
        # Canvas Plot
        self._bw_plot_x_scale = []
        self._bw_plot_lines = {}
        self._init_bw_plot()
        ###########################
        # set KEY BINDS
        self._set_binds()
        self._set_keybinds()
        # Menubar
        self._init_menubar()
        # set Ch Btn Color
        self.ch_status_update()
        # Init Vars fm CFG
        self._init_PARM_vars()
        self._set_CFG()
        # Text Tags
        self._all_tag_calls = []
        self.set_text_tags()
        # .....
        self._update_qso_Vars()
        self._monitor_start_msg()
        #############################
        # set GUI Var to Port Handler
        PORT_HANDLER.set_gui(self)
        #######################
        # LOOP LOOP LOOP
        self.main_win.after(self._loop_delay, self._tasker)
        self.main_win.mainloop()

    ##############################################################
    def __del__(self):
        pass

    def _destroy_win(self):
        self.sysMsg_to_monitor("PoPT wird beendet.")
        logging.info('Closing GUI')
        self._is_closing = True
        logging.info('Closing GUI: Save GUI Vars & Parameter.')
        self._save_GUIvars()
        self._save_parameter()
        self._save_Channel_Vars()
        logging.info('Closing GUI: Closing Ports.')
        PORT_HANDLER.close_all_ports()

        logging.info('Closing GUI: Destroying all Sub-Windows')
        for wn in [
            self.settings_win,
            self.mh_window,
            self.wx_window,
            self.userdb_win,
            self.userDB_tree_win,
            self.aprs_mon_win,
            self.aprs_pn_msg_win,
            self.be_tracer_win,
            self.BBS_fwd_q_list,
            self.MSG_Center_win,
            self.newPMS_MSG_win,
            self.fwd_Path_plot_win,
        ]:
            if wn is not None:
                wn.destroy()
        self.main_win.update_idletasks()
        self._loop_delay = 800
        logging.info('Closing GUI: Done')

    def _save_GUIvars(self):
        #########################
        # GUI-Vars to cfg
        guiCfg = POPT_CFG.load_guiPARM_main()
        guiCfg['gui_lang'] = int(self.language)
        guiCfg['gui_cfg_sound'] = bool(self.setting_sound.get())
        guiCfg['gui_cfg_beacon'] = bool(self.setting_bake.get())
        guiCfg['gui_cfg_rx_echo'] = bool(self.setting_rx_echo.get())
        # guiCfg['gui_cfg_tracer'] = bool(self.setting_tracer.get())
        guiCfg['gui_cfg_tracer'] = False
        guiCfg['gui_cfg_auto_tracer'] = bool(self.setting_auto_tracer.get())
        guiCfg['gui_cfg_dx_alarm'] = bool(self.setting_dx_alarm.get())
        guiCfg['gui_cfg_sprech'] = bool(self.setting_sprech.get())
        POPT_CFG.save_guiPARM_main(guiCfg)

    def _save_parameter(self):
        #########################
        # Parameter to cfg
        guiCfg = POPT_CFG.load_guiPARM_main()
        guiCfg['gui_parm_new_call_alarm'] = bool(self.mh.parm_new_call_alarm)
        guiCfg['gui_parm_channel_index'] = int(self.channel_index)
        guiCfg['gui_parm_text_size'] = int(self.text_size)
        guiCfg['gui_parm_connect_history'] = dict(self.connect_history)
        POPT_CFG.save_guiPARM_main(guiCfg)

    def _save_Channel_Vars(self):
        current_ch_vars = self.get_ch_var(ch_index=self.channel_index)
        current_ch_vars.input_win = self._inp_txt.get('1.0', tk.END)
        current_ch_vars.input_win_tags = get_all_tags(self._inp_txt)
        current_ch_vars.output_win_tags = get_all_tags(self._out_txt)
        current_ch_vars.input_win_cursor_index = self._inp_txt.index(tk.INSERT)
        # guiCfg = POPT_CFG.load_guiCH_VARS()
        ch_vars = {}
        for ch_id in list(self._channel_vars.keys()):
            ch_vars[ch_id] = cleanup_obj_to_dict(self._channel_vars[ch_id])
            del ch_vars[ch_id]['t2speech_buf']
            del ch_vars[ch_id]['rx_beep_cooldown']
            del ch_vars[ch_id]['rx_beep_tr']
            del ch_vars[ch_id]['output_win_tags']
            del ch_vars[ch_id]['input_win_tags']
            ch_vars[ch_id]['output_win_tags'] = cleanup_tags(self._channel_vars[ch_id].output_win_tags)
            ch_vars[ch_id]['input_win_tags'] = cleanup_tags(self._channel_vars[ch_id].input_win_tags)
        POPT_CFG.save_guiCH_VARS(dict(ch_vars))
        # POPT_CFG.save_guiCH_VARS({})

    ####################
    # Init Stuff
    def _init_Channel_Vars(self):
        cfg_ch_vars = POPT_CFG.load_guiCH_VARS()
        for ch_id in list(cfg_ch_vars.keys()):
            self._channel_vars[ch_id] = set_obj_att_fm_dict(ChVars(), cfg_ch_vars[ch_id])

    def _init_GUI_vars_fm_CFG(self):
        #########################
        # GUI-Vars fm cfg
        self.language = POPT_CFG.get_guiCFG_language()
        guiCfg = POPT_CFG.load_guiPARM_main()
        self.setting_sound.set(guiCfg.get('gui_cfg_sound', False))
        self.setting_bake.set(guiCfg.get('gui_cfg_beacon', False))
        self.setting_rx_echo.set(guiCfg.get('gui_cfg_rx_echo', False))
        if is_linux():
            self.setting_sprech.set(guiCfg.get('gui_cfg_sprech', False))
        else:
            self.setting_sprech.set(False)
        self.setting_tracer.set(guiCfg.get('gui_cfg_tracer', False))
        self.setting_auto_tracer.set(guiCfg.get('gui_cfg_auto_tracer', False))
        self.setting_dx_alarm.set(guiCfg.get('gui_cfg_dx_alarm', True))

    def _init_PARM_vars(self):
        #########################
        # Parameter fm cfg
        # ## guiCfg = POPT_CFG.load_guiPARM_main()
        # PORT_HANDLER.get_MH().parm_new_call_alarm = guiCfg.get('gui_parm_new_call_alarm', False)
        # self.channel_index = guiCfg.get('gui_parm_channel_index', 1)
        # ## self.text_size = guiCfg.get('gui_parm_text_size', 13)
        # self.connect_history: {str: ConnHistory}
        # self._mon_buff: (
        #             ax25frame,
        #             conf,
        #             bool(tx)
        #         )
        pass

    def _set_CFG(self):
        self.set_tracer()
        self.set_auto_tracer()
        self.set_dx_alarm()

    def _init_bw_plot(self):
        for _i in list(range(60)):
            self._bw_plot_x_scale.append(_i / 6)
        """
        self._bw_fig = Figure(figsize=(8, 5), dpi=80)
        self._ax = self._bw_fig.add_subplot(111)
        """
        self._bw_fig, self._ax = plt.subplots()
        self._bw_fig.subplots_adjust(left=0.1, right=0.95, top=0.99, bottom=0.1)
        self._ax.axis([0, 10, 0, 100])  # TODO As Option
        self._bw_fig.set_facecolor('xkcd:light grey')
        self._ax.set_facecolor('#000000')
        self._ax.xaxis.label.set_color('black')
        self._ax.yaxis.label.set_color('black')
        self._ax.tick_params(axis='x', colors='black')
        self._ax.tick_params(axis='y', colors='black')
        self._ax.set_xlabel(STR_TABLE['minutes'][self.language])
        self._ax.set_ylabel(STR_TABLE['occup'][self.language])
        self._canvas = FigureCanvasTkAgg(self._bw_fig, master=self._r_frame)
        self._canvas.flush_events()
        self._canvas.draw()
        # self._canvas.get_tk_widget().grid(row=4, column=0, columnspan=7, sticky="nsew")
        self._canvas.get_tk_widget().pack(side=tk.TOP, expand=True)
        # self._canvas.get_tk_widget().config(cursor="none")
        self._bw_fig.canvas.flush_events()

    def _init_menubar(self):
        _menubar = Menu(self.main_win, tearoff=False)
        self.main_win.config(menu=_menubar)
        # Menü 1 "Verbindungen"
        _MenuVerb = Menu(_menubar, tearoff=False)
        _MenuVerb.add_command(label=STR_TABLE['new_conn'][self.language], command=self.open_new_conn_win)
        _MenuVerb.add_command(label=STR_TABLE['disconnect'][self.language], command=self._disco_conn)
        _MenuVerb.add_separator()
        _MenuVerb.add_command(label=STR_TABLE['disconnect_all'][self.language], command=self._disco_all)
        _MenuVerb.add_separator()
        _MenuVerb.add_command(label=STR_TABLE['quit'][self.language], command=self._destroy_win)
        _menubar.add_cascade(label=STR_TABLE['connections'][self.language], menu=_MenuVerb, underline=0)
        # Menü 2 "Bearbeiten"
        _MenuEdit = Menu(_menubar, tearoff=False)
        _MenuEdit.add_command(label=STR_TABLE['copy'][self.language], command=self._copy_select, underline=0)
        _MenuEdit.add_command(label=STR_TABLE['past'][self.language], command=self._clipboard_past, underline=1)
        _MenuEdit.add_separator()
        _MenuEdit.add_command(label=STR_TABLE['past_qso_f_file'][self.language], command=self._insert_fm_file,
                              underline=0)
        _MenuEdit.add_command(label=STR_TABLE['save_qso_to_file'][self.language], command=self._save_to_file,
                              underline=1)
        _MenuEdit.add_command(label=STR_TABLE['save_mon_to_file'][self.language], command=self._save_monitor_to_file,
                              underline=1)
        _MenuEdit.add_separator()
        _MenuEdit.add_command(label=STR_TABLE['clean_qso_win'][self.language], command=self.clear_channel_vars,
                              underline=0)
        _MenuEdit.add_command(label=STR_TABLE['clean_mon_win'][self.language], command=self._clear_monitor_data,
                              underline=0)

        _MenuEdit.add_separator()
        _MenuEdit.add_command(label=STR_TABLE['clean_all_qso_win'][self.language], command=self._clear_all_Channel_vars,
                              underline=0)
        _menubar.add_cascade(label=STR_TABLE['edit'][self.language], menu=_MenuEdit, underline=0)
        # Menü 3 "Tools"
        _MenuTools = Menu(_menubar, tearoff=False)
        _MenuTools.add_command(label="MH", command=self.open_MH_win, underline=0)
        _MenuTools.add_command(label=STR_TABLE['statistic'][self.language],
                               command=lambda: self.open_window('PortStat'),
                               underline=1)
        _MenuTools.add_separator()
        _MenuTools.add_command(label="User-DB Tree",
                               command=lambda: self.open_window('userDB_tree'),
                               underline=0)
        _MenuTools.add_command(label=STR_TABLE['user_db'][self.language],
                               command=lambda: self.open_user_db_win(),
                               underline=0)
        _MenuTools.add_separator()
        _MenuTools.add_command(label=STR_TABLE['locator_calc'][self.language],
                               command=lambda: self.open_window('locator_calc'),
                               underline=0)
        _MenuTools.add_separator()

        _MenuTools.add_command(label="FT-Manager",
                               command=lambda: self._open_settings_window('ft_manager'),
                               underline=0)
        _MenuTools.add_command(label=STR_TABLE['send_file'][self.language],
                               command=lambda: self.open_window('ft_send'),
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
        _MenuTools.add_separator()

        _MenuTools.add_command(label='Kaffèmaschine',
                               command=lambda: self._kaffee(),
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
        _MenuAPRS.add_command(label=STR_TABLE['aprs_mon'][self.language],
                              command=lambda: self.open_window('aprs_mon'),
                              underline=0)
        _MenuAPRS.add_command(label="Beacon Tracer", command=self.open_be_tracer_win,
                              underline=0)
        _MenuAPRS.add_separator()
        _MenuAPRS.add_command(label=STR_TABLE['wx_window'][self.language],
                              command=lambda: self.open_window('wx_win'),
                              underline=0)
        _MenuAPRS.add_command(label=STR_TABLE['pn_msg'][self.language],
                              command=lambda: self.open_window('aprs_msg'),
                              underline=0)
        _MenuAPRS.add_separator()
        _MenuAPRS.add_command(label=STR_TABLE['settings'][self.language],
                              command=lambda: self._open_settings_window('aprs_sett'),
                              underline=0)
        # MenuAPRS.add_separator()
        _menubar.add_cascade(label="APRS", menu=_MenuAPRS, underline=0)
        # BBS/PMS
        _MenuBBS = Menu(_menubar, tearoff=False)
        _MenuBBS.add_command(label=STR_TABLE['new_msg'][self.language],
                             command=lambda: self.open_window('pms_new_msg'),
                             underline=0)
        _MenuBBS.add_command(label=STR_TABLE['msg_center'][self.language],
                             command=lambda: self.open_window('pms_msg_center'),
                             underline=0)

        _MenuBBS.add_separator()
        _MenuBBS.add_command(label=STR_TABLE['fwd_list'][self.language],
                             command=lambda: self.open_window('pms_fwq_q'),
                             underline=0)
        _MenuBBS.add_command(label=STR_TABLE['fwd_path'][self.language],
                             command=lambda: self.open_window('fwdPath'),
                             underline=0)
        _MenuBBS.add_separator()
        _MenuBBS.add_command(label=STR_TABLE['start_fwd'][self.language],
                             command=self._do_pms_fwd,
                             underline=0)

        _MenuBBS.add_command(label=STR_TABLE['start_auto_fwd'][self.language],
                             command=self._do_pms_autoFWD,
                             underline=0)
        _MenuBBS.add_separator()
        _MenuBBS.add_command(label=STR_TABLE['settings'][self.language],
                             command=lambda: self._open_settings_window('pms_setting'),
                             underline=0)
        _menubar.add_cascade(label='PMS', menu=_MenuBBS, underline=0)

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

    def _init_btn(self):
        _btn_upper_frame = tk.Frame(self._side_btn_frame_top)
        _btn_lower_frame = tk.Frame(self._side_btn_frame_top)
        _btn_upper_frame.place(x=5, y=5)
        _btn_lower_frame.place(x=5, y=38)
        self._conn_btn = tk.Button(_btn_upper_frame,
                                   text="New Conn",
                                   bg="green",
                                   width=8,
                                   command=self.open_new_conn_win)
        # self._conn_btn.place(x=5, y=10)
        self._conn_btn.pack(side=tk.LEFT)

        self._mh_btn = tk.Button(_btn_lower_frame,
                                 text="MH",
                                 # bg="yellow",
                                 width=8,
                                 command=self.open_MH_win)

        # self._mh_btn.place(x=5, y=45)
        self._mh_btn.pack(side=tk.LEFT)
        self._mh_btn_def_clr = self._mh_btn.cget('bg')

        self._mon_btn = tk.Button(_btn_upper_frame,
                                  text="Monitor",
                                  bg="yellow", width=8, command=lambda: self.switch_channel(0))
        # self._mon_btn.place(x=110, y=10)
        self._mon_btn.pack(padx=2)

        self._tracer_btn = tk.Button(_btn_lower_frame,
                                     text="Tracer",
                                     width=8,
                                     command=self.open_be_tracer_win)  # .place(x=110, y=45)
        self._tracer_btn.pack(side=tk.LEFT, padx=2)
        self._tracer_btn_def_clr = self._tracer_btn.cget('bg')

    def _init_ch_btn_frame(self, root_frame):
        btn_font = ("fixedsys", 8,)
        ch_btn_frame = tk.Frame(root_frame, )
        ch_btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ch_btn_frame.columnconfigure(1, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(2, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(3, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(4, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(5, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(6, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(7, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(8, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(9, minsize=50, weight=1)
        ch_btn_frame.columnconfigure(10, minsize=50, weight=1)
        ch_1_var = tk.StringVar(self.main_win, value='1')
        ch_2_var = tk.StringVar(self.main_win, value='2')
        ch_3_var = tk.StringVar(self.main_win, value='3')
        ch_4_var = tk.StringVar(self.main_win, value='4')
        ch_5_var = tk.StringVar(self.main_win, value='5')
        ch_6_var = tk.StringVar(self.main_win, value='6')
        ch_7_var = tk.StringVar(self.main_win, value='7')
        ch_8_var = tk.StringVar(self.main_win, value='8')
        ch_9_var = tk.StringVar(self.main_win, value='9')
        ch_10_var = tk.StringVar(self.main_win, value='10')
        ch_button1 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_1_var, bg="red",
                               command=lambda: self.switch_channel(1))
        ch_button2 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_2_var, bg="red",
                               command=lambda: self.switch_channel(2))
        ch_button3 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_3_var, bg="red",
                               command=lambda: self.switch_channel(3))
        ch_button4 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_4_var, bg="red",
                               command=lambda: self.switch_channel(4))
        ch_button5 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_5_var, bg="red",
                               command=lambda: self.switch_channel(5))
        ch_button6 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_6_var, bg="red",
                               command=lambda: self.switch_channel(6))
        ch_button7 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_7_var, bg="red",
                               command=lambda: self.switch_channel(7))
        ch_button8 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_8_var, bg="red",
                               command=lambda: self.switch_channel(8))
        ch_button9 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_9_var, bg="red",
                               command=lambda: self.switch_channel(9))
        ch_button10 = tk.Button(ch_btn_frame, font=btn_font, textvariable=ch_10_var, bg="red",
                                command=lambda: self.switch_channel(10))
        ch_button1.grid(row=0, column=1, sticky="nsew")
        ch_button2.grid(row=0, column=2, sticky="nsew")
        ch_button3.grid(row=0, column=3, sticky="nsew")
        ch_button4.grid(row=0, column=4, sticky="nsew")
        ch_button5.grid(row=0, column=5, sticky="nsew")
        ch_button6.grid(row=0, column=6, sticky="nsew")
        ch_button7.grid(row=0, column=7, sticky="nsew")
        ch_button8.grid(row=0, column=8, sticky="nsew")
        ch_button9.grid(row=0, column=9, sticky="nsew")
        ch_button10.grid(row=0, column=10, sticky="nsew")
        self._con_btn_dict = {
            1: (ch_button1, ch_1_var),
            2: (ch_button2, ch_2_var),
            3: (ch_button3, ch_3_var),
            4: (ch_button4, ch_4_var),
            5: (ch_button5, ch_5_var),
            6: (ch_button6, ch_6_var),
            7: (ch_button7, ch_7_var),
            8: (ch_button8, ch_8_var),
            9: (ch_button9, ch_9_var),
            10: (ch_button10, ch_10_var),
        }

    def _init_TXT_frame_up(self):
        status_frame = tk.Frame(self._TXT_upper_frame, bd=0, borderwidth=0, bg=STAT_BAR_CLR)
        status_frame.pack(side=tk.BOTTOM, expand=1)

        status_frame.columnconfigure(1, minsize=60, weight=2)  # Name
        status_frame.columnconfigure(2, minsize=40, weight=3)  # Status
        status_frame.columnconfigure(3, minsize=40, weight=4)  # unACK
        status_frame.columnconfigure(4, minsize=40, weight=4)  # VS VR
        status_frame.columnconfigure(5, minsize=20, weight=5)  # N2
        status_frame.columnconfigure(6, minsize=20, weight=5)  # T1
        status_frame.columnconfigure(7, minsize=20, weight=5)  # T1
        status_frame.columnconfigure(8, minsize=20, weight=5)  # T2
        status_frame.columnconfigure(9, minsize=20, weight=5)  # T3
        status_frame.columnconfigure(10, minsize=50, weight=1)  # RX Beep
        status_frame.columnconfigure(11, minsize=20, weight=1)  # TimeStamp
        status_frame.columnconfigure(12, minsize=1, weight=0)  # TimeStamp
        status_frame.rowconfigure(0, weight=1)  # Stat
        status_frame.rowconfigure(1, minsize=20, weight=0)  # Out

        self._inp_txt = scrolledtext.ScrolledText(status_frame,
                                                  background=TXT_BACKGROUND_CLR,
                                                  foreground=TXT_INP_CLR,
                                                  font=(FONT, self.text_size),
                                                  insertbackground=TXT_INP_CURSOR_CLR,
                                                  height=100,
                                                  width=300,
                                                  bd=0,
                                                  )
        self._inp_txt.tag_config("send", foreground="green2")
        # self.in_txt_win.insert(tk.END, "Inp")
        self._inp_txt.grid(row=0, column=0, columnspan=13, sticky="nsew")
        ##############
        # Status Frame

        Label(status_frame,
              textvariable=self._status_name_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              foreground=STAT_BAR_TXT_CLR,
              bg=STAT_BAR_CLR
              ).grid(row=1, column=1, sticky="nsew")

        self._status_status = Label(status_frame,
                                    textvariable=self._status_status_var,
                                    font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                    bg=STAT_BAR_CLR,
                                    foreground=STAT_BAR_TXT_CLR
                                    )
        self._status_status.grid(row=1, column=2, sticky="nsew")

        self._status_unack = Label(status_frame,
                                   textvariable=self._status_unack_var,
                                   foreground=STAT_BAR_TXT_CLR,
                                   font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                   bg=STAT_BAR_CLR
                                   )
        self._status_unack.grid(row=1, column=3, sticky="nsew")

        Label(status_frame,
              textvariable=self._status_vs_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=STAT_BAR_CLR,
              foreground=STAT_BAR_TXT_CLR
              ).grid(row=1, column=4, sticky="nsew")

        self._status_n2 = Label(status_frame,
                                textvariable=self._status_n2_var,
                                font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                bg=STAT_BAR_CLR,
                                foreground=STAT_BAR_TXT_CLR
                                )
        self._status_n2.grid(row=1, column=7, sticky="nsew")

        Label(status_frame,
              textvariable=self._status_t1_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=STAT_BAR_CLR,
              foreground=STAT_BAR_TXT_CLR
              ).grid(row=1, column=8, sticky="nsew")
        # PARM T2
        Label(status_frame,
              textvariable=self._status_t2_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=STAT_BAR_CLR,
              foreground=STAT_BAR_TXT_CLR
              ).grid(row=1, column=5, sticky="nsew")
        # RTT
        Label(status_frame,
              textvariable=self._status_rtt_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=STAT_BAR_CLR,
              foreground=STAT_BAR_TXT_CLR
              ).grid(row=1, column=6, sticky="nsew")

        Label(status_frame,
              textvariable=self._status_t3_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=STAT_BAR_CLR,
              foreground=STAT_BAR_TXT_CLR
              ).grid(row=1, column=9, sticky="nsew")
        # Checkbox RX-BEEP
        self.rx_beep_box = Checkbutton(status_frame,
                                       text="RX-BEEP",
                                       bg=STAT_BAR_CLR,
                                       font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                       activebackground=STAT_BAR_CLR,
                                       borderwidth=0,
                                       onvalue=1, offvalue=0,
                                       foreground=STAT_BAR_TXT_CLR,
                                       variable=self._rx_beep_var,
                                       command=self._chk_rx_beep
                                       )
        self.rx_beep_box.grid(row=1, column=10, sticky="nsew")
        # TODO Checkbox Time Stamp
        self.ts_box_box = Checkbutton(status_frame,
                                      text="T-S",
                                      font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                      bg=STAT_BAR_CLR,
                                      borderwidth=0,
                                      activebackground=STAT_BAR_CLR,
                                      onvalue=1, offvalue=0,
                                      foreground=STAT_BAR_TXT_CLR,
                                      variable=self._ts_box_var,
                                      command=self._chk_timestamp,
                                      state='disabled'
                                      )
        self.ts_box_box.grid(row=1, column=11, sticky="nsew")

    def _init_TXT_frame_mid(self):
        self._TXT_mid_frame.rowconfigure(1, minsize=22, weight=1)
        self._TXT_mid_frame.rowconfigure(0, weight=1)
        self._TXT_mid_frame.columnconfigure(0, minsize=3, weight=0)  # Spacer
        self._TXT_mid_frame.columnconfigure(1, minsize=80, weight=2)  # Name
        self._TXT_mid_frame.columnconfigure(2, minsize=60, weight=3)  # QTH
        self._TXT_mid_frame.columnconfigure(3, minsize=20, weight=4)  # LOC
        self._TXT_mid_frame.columnconfigure(4, minsize=20, weight=5)  # Typ
        self._TXT_mid_frame.columnconfigure(5, minsize=80, weight=4)  # Software
        self._TXT_mid_frame.columnconfigure(6, minsize=28, weight=4)  # Status (PIPE/FT)
        self._TXT_mid_frame.columnconfigure(7, minsize=30, weight=4)  # Conn Timer
        self._TXT_mid_frame.columnconfigure(8, minsize=30, weight=4)  # Text Encoding
        self._TXT_mid_frame.columnconfigure(9, minsize=3, weight=0)  # Spacer
        self._out_txt = scrolledtext.ScrolledText(self._TXT_mid_frame,
                                                  background=TXT_BACKGROUND_CLR,
                                                  foreground=TXT_OUT_CLR,
                                                  font=(FONT, self.text_size),
                                                  height=100,
                                                  width=300,
                                                  bd=0,
                                                  borderwidth=0,
                                                  state="disabled",
                                                  )
        self._out_txt.tag_config("input", foreground="yellow")
        self._out_txt.grid(row=0, column=0, columnspan=10, sticky="nsew")

        name_label = tk.Label(self._TXT_mid_frame,
                              textvariable=self.stat_info_name_var,
                              # bg=STAT_BAR_CLR,
                              height=1,
                              borderwidth=0,
                              border=0,
                              fg=STAT_BAR_TXT_CLR,
                              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS, 'bold')
                              )
        name_label.grid(row=1, column=1, sticky="nsew")
        name_label.bind('<Button-1>', self.open_user_db_win)
        qth_label = tk.Label(self._TXT_mid_frame,
                             textvariable=self.stat_info_qth_var,
                             bg=STAT_BAR_CLR,
                             fg=STAT_BAR_TXT_CLR,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS)
                             )
        qth_label.bind('<Button-1>', self.open_user_db_win)
        qth_label.grid(row=1, column=2, sticky="nsew")
        loc_label = tk.Label(self._TXT_mid_frame,
                             textvariable=self.stat_info_loc_var,
                             bg=STAT_BAR_CLR,
                             fg=STAT_BAR_TXT_CLR,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS)
                             )
        loc_label.bind('<Button-1>', self.open_user_db_win)
        loc_label.grid(row=1, column=3, sticky="nsew")

        opt = list(STATION_TYPS)
        stat_typ = tk.OptionMenu(
            self._TXT_mid_frame,
            self.stat_info_typ_var,
            *opt,
            command=self._set_stat_typ
        )
        stat_typ.configure(
            background="#0ed8c3",
            fg=STAT_BAR_TXT_CLR,
            width=10,
            height=1,
            borderwidth=0,
            border=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,)
        )
        stat_typ.grid(row=1, column=4, sticky="nsew")

        tk.Label(self._TXT_mid_frame,
                 textvariable=self.stat_info_sw_var,
                 width=20,
                 bg="#ffd444",
                 # fg="red3",
                 height=1,
                 borderwidth=0,
                 border=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS)
                 ).grid(row=1, column=5, sticky="nsew")

        self.status_label = tk.Label(self._TXT_mid_frame,
                                     textvariable=self.stat_info_status_var,
                                     bg=STAT_BAR_CLR,
                                     fg="red3",
                                     height=1,
                                     borderwidth=0,
                                     border=0,
                                     font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,)
                                     )
        self.status_label.grid(row=1, column=6, sticky="nsew")
        self.status_label.bind('<Button-1>', self.do_priv)

        tk.Label(self._TXT_mid_frame,
                 textvariable=self.stat_info_timer_var,
                 width=10,
                 height=1,
                 borderwidth=0,
                 border=0,
                 # bg="steel blue",
                 # fg="red3",
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,)
                 ).grid(row=1, column=7, sticky="nsew")
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            self._TXT_mid_frame,
            self.stat_info_encoding_var,
            *opt,
            command=self._change_txt_encoding
        )
        txt_encoding_ent.configure(
            background="steel blue",
            height=1,
            width=8,
            borderwidth=0,
            border=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - 1,)
        )
        txt_encoding_ent.grid(row=1, column=8, sticky="nsew", )

    def _init_TXT_frame_low(self):
        self._mon_txt = scrolledtext.ScrolledText(self._TXT_lower_frame,
                                                  background=TXT_BACKGROUND_CLR,
                                                  foreground=TXT_MON_CLR,
                                                  font=(FONT, self.text_size),
                                                  height=100,
                                                  width=300,
                                                  bd=0,
                                                  borderwidth=0,
                                                  state="disabled",
                                                  )
        self._mon_txt.pack(side=tk.TOP)

    #######################################
    # Text Tags

    def set_text_tags(self):
        self._all_tag_calls = []
        all_stat_cfg = PORT_HANDLER.get_all_stat_cfg()
        for call in list(all_stat_cfg.keys()):
            stat_cfg = all_stat_cfg[call]
            tx_fg = stat_cfg.stat_parm_qso_col_text_tx
            tx_bg = stat_cfg.stat_parm_qso_col_bg

            rx_fg = stat_cfg.stat_parm_qso_col_text_rx

            tx_tag = 'TX-' + str(call)
            rx_tag = 'RX-' + str(call)
            self._all_tag_calls.append(str(call))

            self._out_txt.configure(state="normal")
            self._out_txt.tag_config(tx_tag,
                                     foreground=tx_fg,
                                     background=tx_bg,
                                     selectbackground=tx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._out_txt.tag_config(rx_tag,
                                     foreground=rx_fg,
                                     background=tx_bg,
                                     selectbackground=rx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._out_txt.tag_config('SYS-MSG',
                                     foreground='#fc7126',
                                     background='#000000',
                                     selectbackground='#fc7126',
                                     selectforeground='#000000',
                                     )
            self._out_txt.tag_config('TX-NOCALL',
                                     foreground='#ffffff',
                                     background='#000000',
                                     selectbackground='#ffffff',
                                     selectforeground='#000000',
                                     )
            self._out_txt.tag_config('RX-NOCALL',
                                     foreground='#000000',
                                     background='#ffffff',
                                     selectbackground='#000000',
                                     selectforeground='#ffffff',
                                     )
            self._out_txt.configure(state="disabled")

            self._mon_txt.configure(state="normal")

        # Monitor Tags
        all_port = PORT_HANDLER.get_all_ports()
        for port_id in all_port.keys():
            tag_tx = f"tx{port_id}"
            tag_rx = f"rx{port_id}"
            tx_fg = all_port[port_id].port_cfg.parm_mon_clr_tx
            tx_bg = all_port[port_id].port_cfg.parm_mon_clr_bg
            rx_fg = all_port[port_id].port_cfg.parm_mon_clr_rx
            self._mon_txt.tag_config(tag_tx, foreground=tx_fg,
                                     background=tx_bg,
                                     selectbackground=tx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._mon_txt.tag_config(tag_rx, foreground=rx_fg,
                                     background=tx_bg,
                                     selectbackground=rx_fg,
                                     selectforeground=tx_bg,
                                     )

        self._mon_txt.configure(state="disabled")

    #######################################
    # KEYBIND Stuff
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
        # self.main_win.bind('<Control-Right>', lambda event: self._text_win_bigger())
        # self.main_win.bind('<Control-Left>', lambda event: self._text_win_smaller())

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

    ##########################
    # Start Message in Monitor
    def _monitor_start_msg(self):
        # tmp_lang = int(self.language)
        # self.language = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.sprech(random.choice(WELCOME_SPEECH))
        # self.language = int(tmp_lang)
        ban = POPT_BANNER.format(VER)
        tmp = ban.split('\r')
        for el in tmp:
            self.sysMsg_to_monitor(el)
        self.sysMsg_to_monitor('Python Other Packet Terminal ' + VER)
        for stat in PORT_HANDLER.ax25_stations_settings.keys():
            self.sysMsg_to_monitor('Info: Stationsdaten {} erfolgreich geladen.'.format(stat))
        for port_k in PORT_HANDLER.get_all_ports().keys():
            msg = 'konnte nicht initialisiert werden!'
            if PORT_HANDLER.get_all_ports()[port_k].device_is_running:
                msg = 'erfolgreich initialisiert.'
            self.sysMsg_to_monitor('Info: Port {}: {} - {} {}'
                                   .format(port_k,
                                           PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortName,
                                           PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortTyp,
                                           msg
                                           ))
            self.sysMsg_to_monitor('Info: Port {}: Parameter: {} | {}'
                                   .format(port_k,
                                           PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortParm[0],
                                           PORT_HANDLER.get_all_ports()[port_k].port_cfg.parm_PortParm[1]
                                           ))

    # END Init Stuff
    ######################################################################

    ######################################################################
    # GUI Sizing/Formatting Stuff
    def _increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        self._inp_txt.configure(font=(FONT, self.text_size), )
        self._out_txt.configure(font=(FONT, self.text_size), )
        self._mon_txt.configure(font=(FONT, self.text_size), )

    def _decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self._inp_txt.configure(font=(FONT, self.text_size), )
        self._out_txt.configure(font=(FONT, self.text_size), )
        self._mon_txt.configure(font=(FONT, self.text_size), )

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
        try:
            clp_brd = self.main_win.clipboard_get()
        except tk.TclError:
            logging.warning("TclError Clipboard no STR")
            return

        if clp_brd:
            self._inp_txt.insert(tk.END, clp_brd)

    def _select_all(self):
        self._inp_txt.tag_add(tk.SEL, "1.0", tk.END)
        self._inp_txt.mark_set(tk.INSERT, "1.0")
        self._inp_txt.see(tk.INSERT)

    # END GUI Sizing/Formatting Stuff
    ######################################################################

    ######################################################################
    #
    def get_conn(self, con_ind: int = 0):
        # TODO Call just if necessary
        # TODO current Chanel.connection to var, prevent unnecessary calls
        if not con_ind:
            con_ind = self.channel_index
        all_conn = PORT_HANDLER.get_all_connections()
        if con_ind in all_conn.keys():
            ret = all_conn[con_ind]
            return ret
        return None

    def get_ch_var(self, ch_index=0):
        if ch_index:
            if ch_index not in self._channel_vars.keys():
                self._channel_vars[ch_index] = ChVars()
            return self._channel_vars[ch_index]

        if self.channel_index not in self._channel_vars.keys():
            self._channel_vars[self.channel_index] = ChVars()
        return self._channel_vars[self.channel_index]

    def set_var_to_all_ch_param(self):
        for ch_id in self._channel_vars.keys():
            ch_vars = self.get_ch_var(ch_index=ch_id)
            if not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''

    def clear_channel_vars(self):
        self._out_txt.configure(state='normal')
        self._out_txt.delete('1.0', tk.END)
        self._out_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]

        self._channel_vars[self.channel_index] = ChVars()
        self._update_qso_Vars()

    def _clear_all_Channel_vars(self):
        self._out_txt.configure(state='normal')
        self._out_txt.delete('1.0', tk.END)
        self._out_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]
        for ch_id in self._channel_vars.keys():
            self._channel_vars[ch_id] = ChVars()
        self._update_qso_Vars()

    def _clear_monitor_data(self):
        self._mon_txt.configure(state='normal')
        self._mon_txt.delete('1.0', tk.END)
        self._mon_txt.configure(state='disabled')

    def _insert_fm_file(self):
        _data = open_file_dialog()
        if _data:
            # TODO Maybe Channel Decoding ?  ?
            self._inp_txt.insert(tk.INSERT, try_decode(_data, ignore=True))

    def _save_to_file(self):
        data = self._out_txt.get('1.0', tk.END)
        save_file_dialog(data)

    def _save_monitor_to_file(self):
        data = self._mon_txt.get('1.0', tk.END)
        save_file_dialog(data)

    ######################################################################
    # Sound
    def _kanal_switch(self):
        """ Triggered on CH BTN Click """
        threading.Thread(target=self._kanal_switch_sprech_th).start()

    def _kanal_switch_sprech_th(self):
        conn = self.get_conn(self.channel_index)
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        if conn is not None:
            if ch_vars.t2speech \
                    and ch_vars.t2speech_buf:
                # to_speech = 'Kanal {} .'.format(self.channel_index)
                # to_speech += '{} .'.format(conn.to_call_str)
                to_speech = str(ch_vars.t2speech_buf)
                if self.sprech(to_speech):
                    ch_vars.t2speech_buf = ''

            else:
                ch_vars.t2speech_buf = ''
                self.sprech('{} {} . {} .'.format(STR_TABLE['channel'][self.language],
                                                  self.channel_index,
                                                  conn.to_call_str))

        else:
            if not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''
                self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            elif ch_vars.t2speech_buf:
                if self.sprech(ch_vars.t2speech_buf):
                    ch_vars.t2speech_buf = ''
                else:
                    self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            else:
                self.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))

    def _check_sprech_ch_buf(self):
        conn = self.get_conn(self.channel_index)
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        if conn is not None:
            if ch_vars.t2speech \
                    and ch_vars.t2speech_buf:
                to_speech = str(ch_vars.t2speech_buf)
                if self.setting_sprech.get() and self.setting_sound.get():
                    if self.sprech(to_speech):
                        ch_vars.t2speech_buf = ''
                else:
                    ch_vars.t2speech_buf = ''

            elif not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''
        else:
            ch_vars.t2speech_buf = ''

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
                        self._sound_th.join()
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
        for k in self._channel_vars.keys():
            if k:  # not int(0)    # TODO Service Ports
                ch_vars = self.get_ch_var(ch_index=k)
                if ch_vars.rx_beep_cooldown < time.time():
                    ch_vars.rx_beep_cooldown = time.time() + self._parm_rx_beep_cooldown
                    if ch_vars.rx_beep_opt:
                        if ch_vars.rx_beep_tr:
                            ch_vars.rx_beep_tr = False
                            self._sound_play(self._root_dir + CFG_sound_RX_BEEP, False)

    def new_conn_sound(self):
        self._sound_play(self._root_dir + CFG_sound_CONN, False)

    def disco_sound(self):
        """ fm PortHandler """
        self._sound_play(self._root_dir + CFG_sound_DICO, False)

    # Sound
    ######################################################################
    #
    ######################################################################

    def _dx_alarm(self):
        """ Alarm when new User in MH List """
        if self.setting_dx_alarm.get():
            _clr = generate_random_hex_color()
            if self._mh_btn.cget('bg') != _clr:
                self._mh_btn.configure(bg=_clr)
            _aprs_obj = PORT_HANDLER.get_aprs_ais()
            if _aprs_obj is not None:
                _aprs_obj.tracer_reset_auto_timer(self.mh.last_dx_alarm)

    def _tracer_alarm(self):
        """ Tracer Alarm """
        # self.tabbed_sideFrame.tabControl.select(self.tabbed_sideFrame.tab2_mh)
        _clr = generate_random_hex_color()
        if self._tracer_btn.cget('bg') != _clr:
            self._tracer_btn.configure(bg=_clr)

    def _reset_tracer_alarm(self):
        """ Tracer Alarm """
        PORT_HANDLER.get_aprs_ais().tracer_alarm_reset()
        if self._tracer_btn.cget('bg') != self._tracer_btn_def_clr:
            self._tracer_btn.configure(bg=self._tracer_btn_def_clr)

    def _reset_dx_alarm(self):
        self.mh.dx_alarm_trigger = False

        if self._mh_btn.cget('bg') != self._mh_btn_def_clr:
            self._mh_btn.configure(bg=self._mh_btn_def_clr)

    ######################################################################
    # TASKER
    def _tasker(self):  # MAINLOOP
        if self._is_closing:
            self._tasker_quit()
        else:
            # self._tasker_prio()
            if not self._tasker_05_sec():
                if not self._tasker_1_sec():
                    if not self._tasker_5_sec():
                        self.main_win.update_idletasks()
            # self._tasker_tester()
        self.main_win.after(self._loop_delay, self._tasker)

    @staticmethod
    def _tasker_quit():
        if PORT_HANDLER.check_all_ports_closed():
            PORT_HANDLER.close_gui()
            logging.info('Closing GUI: Done.')

    def _tasker_prio(self):
        """ Prio Tasks every Irritation flip flop """
        pass
        """
        if self._prio_task_flip:
            
        else:
           
        self._prio_task_flip = not self._prio_task_flip
        """

    def _tasker_05_sec(self):
        """ 0.5 Sec """
        if time.time() > self._non_prio_task_timer:
            #####################
            # self._aprs_task()
            self._monitor_task()
            self._update_qso_win()
            self._update_status_win()
            #####################
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            return True
        return False

    def _tasker_1_sec(self):
        """ 1 Sec """
        if time.time() > self._non_non_prio_task_timer:
            #####################
            self._update_stat_info_conn_timer()
            self._update_ft_info()
            self.tabbed_sideFrame.tasker()
            # if MH_LIST.new_call_alarm and self.setting_dx_alarm.get():
            if self._ch_alarm:
                self._ch_btn_status_update()
            if self.mh.dx_alarm_trigger:
                self._dx_alarm()
            if PORT_HANDLER.get_aprs_ais() is not None:
                if PORT_HANDLER.get_aprs_ais().tracer_is_alarm():
                    self._tracer_alarm()
            if self.settings_win is not None:
                self.settings_win.tasker()
            if self.setting_sound:
                # TODO Sound Task
                self._rx_beep_sound()
                if self.setting_sprech:
                    self._check_sprech_ch_buf()
            """
            if self.MSG_Center is not None:
                self.MSG_Center.tasker()
            """
            """
            if self.aprs_mon_win is not None:
                self.aprs_mon_win.tasker()
            """
            #####################
            self._non_non_prio_task_timer = time.time() + self._parm_non_non_prio_task_timer
            return True
        return False

    def _tasker_5_sec(self):
        """ 5 Sec """
        if time.time() > self._non_non_non_prio_task_timer:
            #####################
            self._update_bw_mon()
            self._aprs_wx_tree_task()
            #####################
            self._non_non_non_prio_task_timer = time.time() + self._parm_non_non_non_prio_task_timer
            return True
        return False

    def _tasker_tester(self):
        """ 5 Sec """
        if time.time() > self._test_task_timer:
            self._test_task_timer = time.time() + self._parm_test_task_timer
            #####################

    # END TASKER
    ######################################################################
    @staticmethod
    def _aprs_wx_tree_task():
        if PORT_HANDLER.get_aprs_ais() is not None:
            PORT_HANDLER.get_aprs_ais().aprs_wx_tree_task()

    ###############################################################
    # QSO WIN
    def _update_qso_win(self):
        all_conn = PORT_HANDLER.get_all_connections()
        all_conn_ch_index = list(all_conn.keys())
        tr = False
        for channel in all_conn_ch_index:
            conn = all_conn[channel]
            if conn:
                if self._update_qso(conn):
                    tr = True
        if tr:
            self.ch_status_update()

    def _update_qso(self, conn):
        channel = conn.ch_index
        if not conn:
            return False
        if conn.ft_obj:
            return False
        if 1 > channel > 10:
            # TODO Service Channels
            return False
        if conn.rx_tx_buf_guiData:
            self._update_qso_spooler(conn)
            return True
        return False

    def _update_qso_spooler(self, conn):
        gui_buf = list(conn.rx_tx_buf_guiData)
        conn.rx_tx_buf_guiData = list(conn.rx_tx_buf_guiData[len(gui_buf):])
        for qso_data in gui_buf:
            if qso_data[0] == 'TX':
                self._update_qso_tx(conn, qso_data[1])
            else:
                self._update_qso_rx(conn, qso_data[1])

    def _update_qso_tx(self, conn, data):
        txt_enc = 'UTF-8'
        if conn.user_db_ent:
            txt_enc = conn.user_db_ent.Encoding
        inp = data.decode(txt_enc, 'ignore').replace('\r', '\n')
        inp = tk_filter_bad_chars(inp)

        Ch_var = self.get_ch_var(ch_index=conn.ch_index)
        Ch_var.output_win += inp
        if conn.my_call_str in self._all_tag_calls:
            tag_name_tx = 'TX-' + str(conn.my_call_str)
            Ch_var.last_tag_name = str(conn.my_call_str)
        elif conn.my_call_obj.call in self._all_tag_calls:
            tag_name_tx = 'TX-' + str(conn.my_call_obj.call)
            Ch_var.last_tag_name = str(conn.my_call_str)
        else:
            tag_name_tx = 'TX-' + Ch_var.last_tag_name

        if self.channel_index == conn.ch_index:
            self._out_txt.configure(state="normal")
            ind = self._out_txt.index('end-1c')
            self._out_txt.insert('end', inp)
            ind2 = self._out_txt.index('end-1c')
            if tag_name_tx:
                self._out_txt.tag_add(tag_name_tx, ind, ind2)
            self._out_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            # TODO Autoscroll
            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
                self.see_end_qso_win()
        else:
            if tag_name_tx:
                Ch_var.new_tags.append(
                    (tag_name_tx, len(inp))
                )

    def _update_qso_rx(self, conn, data):
        txt_enc = 'UTF-8'
        if conn.user_db_ent:
            txt_enc = conn.user_db_ent.Encoding

        out = data.decode(txt_enc, 'ignore')
        out = out.replace('\r', '\n')
        out = tk_filter_bad_chars(out)

        # Write RX Date to Window/Channel Buffer
        Ch_var = self.get_ch_var(ch_index=conn.ch_index)
        Ch_var.output_win += out
        if conn.my_call_str in self._all_tag_calls:
            tag_name_rx = 'RX-' + str(conn.my_call_str)
            Ch_var.last_tag_name = str(conn.my_call_str)
        elif conn.my_call_obj.call in self._all_tag_calls:
            tag_name_rx = 'RX-' + str(conn.my_call_obj.call)
            Ch_var.last_tag_name = str(conn.my_call_str)
        else:
            tag_name_rx = 'RX-' + Ch_var.last_tag_name

        if self.channel_index == conn.ch_index:
            if Ch_var.t2speech:
                Ch_var.t2speech_buf += out.replace('\n', '')

            self._out_txt.configure(state="normal")
            # configuring a tag called start
            ind = self._out_txt.index('end-1c')
            self._out_txt.insert('end', out)
            ind2 = self._out_txt.index('end-1c')
            if tag_name_rx:
                self._out_txt.tag_add(tag_name_rx, ind, ind2)

            self._out_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            # TODO Autoscroll
            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
                self.see_end_qso_win()
        else:
            Ch_var.new_data_tr = True
            if Ch_var.t2speech:
                # TODO ?????????????????????????????????????????????
                Ch_var.t2speech_buf += '{} {} . {} . {}'.format(
                    STR_TABLE['channel'][self.language],
                    conn.ch_index,
                    conn.to_call_str,
                    out.replace('\n', '')
                )
            if tag_name_rx:
                Ch_var.new_tags.append(
                    (tag_name_rx, len(out))
                )
        Ch_var.rx_beep_tr = True

    def _update_qso_Vars(self):
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        ch_vars.new_data_tr = False
        ch_vars.rx_beep_tr = False

        self._out_txt.configure(state="normal")

        self._out_txt.delete('1.0', tk.END)
        self._out_txt.insert(tk.END, ch_vars.output_win)
        self._out_txt.configure(state="disabled")
        self._out_txt.see(tk.END)

        self._inp_txt.delete('1.0', tk.END)
        self._inp_txt.insert(tk.END, ch_vars.input_win[:-1])
        set_all_tags(self._inp_txt, ch_vars.input_win_tags)
        set_all_tags(self._out_txt, ch_vars.output_win_tags)
        set_new_tags(self._out_txt, ch_vars.new_tags)
        ch_vars.new_tags = []
        self._inp_txt.mark_set("insert", ch_vars.input_win_cursor_index)
        self._inp_txt.see(tk.END)

        # self.main_class: gui.guiMainNew.TkMainWin
        if ch_vars.rx_beep_opt and self.channel_index:
            self.rx_beep_box.select()
            self.rx_beep_box.configure(bg='green')
        else:
            self.rx_beep_box.deselect()
            self.rx_beep_box.configure(bg=STAT_BAR_CLR)

        if ch_vars.timestamp_opt and self.channel_index:
            self.ts_box_box.select()
            self.ts_box_box.configure(bg='green')
        else:
            self.ts_box_box.deselect()
            self.ts_box_box.configure(bg=STAT_BAR_CLR)

    def sysMsg_to_qso(self, data, ch_index):
        if not data:
            return
        if 1 > ch_index > 10:
            return False
        data = data.replace('\r', '')
        data = f"\n    <{conv_time_DE_str()}>\n" + data + '\n'
        data = tk_filter_bad_chars(data)
        ch_vars = self.get_ch_var(ch_index=ch_index)
        tag_name = 'SYS-MSG'
        ch_vars.output_win += data
        if self.channel_index == ch_index:
            tr = False
            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index("@0,0")) < 22:
                tr = True
            self._out_txt.configure(state="normal")

            ind = self._out_txt.index(tk.INSERT)
            self._out_txt.insert('end', data)
            ind2 = self._out_txt.index(tk.INSERT)
            self._out_txt.tag_add(tag_name, ind, ind2)
            self._out_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            if tr or self.get_ch_var().autoscroll:
                self.see_end_qso_win()

        else:
            ch_vars.new_tags.append(
                (tag_name, len(data))
            )
            ch_vars.new_data_tr = True
        ch_vars.rx_beep_tr = True
        self.ch_status_update()

    # END QSO WIN
    ###############################################################
    ###############################################################
    # Monitor WIN

    def sysMsg_to_monitor(self, var: str):
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

        self._see_end_mon_win()
        if 'Lob: ' in var:
            var = var.split('Lob: ')
            if len(var) > 1:
                self.sprech(var[1])

    """
    def update_monitor(self, ax25frame, port_conf, tx=False):
        # Called from AX25Conn 
        self._mon_buff.append((
            ax25frame,
            port_conf,
            bool(tx)
        ))
    """

    def _monitor_task(self):
        mon_buff = PORT_HANDLER.get_monitor_data()
        if mon_buff:
            tr = False
            self._mon_txt.configure(state="normal")
            for el in mon_buff:
                conf = el[1]
                port_id = conf.parm_PortNr
                tx = el[2]
                _mon_out = monitor_frame_inp(el[0], conf)
                if self.tabbed_sideFrame.mon_aprs_var.get():
                    _mon_str = _mon_out[0] + _mon_out[1]
                else:
                    _mon_str = _mon_out[0]
                _var = tk_filter_bad_chars(_mon_str)
                ind = self._mon_txt.index('end-1c')
                # TODO Autoscroll
                if float(self._mon_txt.index(tk.END)) - float(self._mon_txt.index(tk.INSERT)) < 15:
                    tr = True
                if tx:
                    tag = "tx{}".format(port_id)
                else:
                    tag = "rx{}".format(port_id)

                if tag in self._mon_txt.tag_names(None):
                    self._mon_txt.insert(tk.END, _var, tag)
                else:
                    self._mon_txt.insert(tk.END, _var)
                    ind2 = self._mon_txt.index('end-1c')
                    self._mon_txt.tag_add(tag, ind, ind2)
            cut_len = int(self._mon_txt.index('end-1c').split('.')[0]) - PARAM_MAX_MON_LEN + 1
            if cut_len > 0:
                self._mon_txt.delete('1.0', f"{cut_len}.0")
            self._mon_txt.configure(state="disabled", exportselection=True)
            if tr or self.tabbed_sideFrame.mon_scroll_var.get():
                self._see_end_mon_win()

    def see_end_qso_win(self):
        self._out_txt.see("end")

    def _see_end_mon_win(self):
        self._mon_txt.see("end")

    # END Monitor WIN
    ###############################################################
    ###############################################################
    # Open Toplevel Win

    def open_link_holder_sett(self):
        self._open_settings_window('l_holder')

    def open_ft_manager(self, event=None):
        self._open_settings_window('ft_manager')

    def _open_settings_window(self, win_key: str):
        if not win_key:
            return
        if self.settings_win:
            return
        settings_win = {
            'priv_win': PrivilegWin,  # Priv Win
            'keybinds': KeyBindsHelp,  # Keybinds Help WIN
            'about': About,  # About WIN
            'aprs_sett': APRSSettingsWin,  # APRS Settings
            'ft_manager': FileTransferManager,  # FT Manager
            'pipe_sett': PipeToolSettings,  # Pipe Tool
            # 'user_db': UserDB,  # UserDB
            'mcast_sett': MulticastSettings,  # Multicast Settings
            'l_holder': LinkHolderSettings,  # Linkholder
            'rx_echo_sett': RxEchoSettings,  # RX Echo
            'beacon_sett': BeaconSettings,  # Beacon Settings
            'port_sett': PortSettingsWin,  # Port Settings
            'stat_sett': StationSettingsWin,  # Stat Settings
            'pms_setting': PMS_Settings,  # PMS Settings
        }.get(win_key, '')
        if callable(settings_win):
            self.settings_win = settings_win(self)

    def open_window(self, win_key: str):
        # self._open_window('new_conn')
        if not win_key:
            return
        win_list = {
            'new_conn': (self.new_conn_win, NewConnWin),
            'wx_win': (self.wx_window, WXWin),
            'locator_calc': (self.locator_calc_window, LocatorCalculator),
            'aprs_mon': (self.aprs_mon_win, AISmonitor),
            'aprs_msg': (self.aprs_pn_msg_win, APRS_msg_SYS_PN),
            'pms_fwq_q': (self.BBS_fwd_q_list, BBS_fwd_Q),
            'pms_msg_center': (self.MSG_Center_win, MSG_Center),
            'pms_new_msg': (self.newPMS_MSG_win, BBS_newMSG),
            'userDB_tree': (self.userDB_tree_win, UserDBtreeview),
            'ft_send': (self.FileSend_win, FileSend),
            'PortStat': (self.port_stat_win, PlotWindow),
            'fwdPath': (self.fwd_Path_plot_win, FwdGraph),
            # TODO .......

        }.get(win_key, None)
        if not win_list:
            return
        if win_list[0]:
            if hasattr(win_list[0], 'lift'):
                win_list[0].lift()
            return
        if callable(win_list[1]):
            win_list[1](self)

    ##########################
    # UserDB
    def open_user_db_win(self, event=None, ent_key=''):
        if self.userdb_win is None:
            if not ent_key:
                _conn = self.get_conn()
                if _conn is not None:
                    ent_key = _conn.to_call_str
            self.userdb_win = UserDB(self, ent_key)

    ##########################
    # New Connection WIN
    def open_new_conn_win(self):
        self.open_window('new_conn')

    ######################
    # APRS Beacon Tracer
    def open_be_tracer_win(self):
        self._reset_tracer_alarm()
        if self.be_tracer_win is None:
            self.be_tracer_win = BeaconTracer(self)

    ###################
    # MH WIN
    def open_MH_win(self):
        """MH WIN"""
        self._reset_dx_alarm()  # TODO
        if self.mh_window is None:
            MHWin(self)
        self.tabbed_sideFrame.reset_dx_alarm()

    #######################################################
    def gui_set_distance(self):
        self._set_distance_fm_conn()

    def _set_distance_fm_conn(self):
        _conn = self.get_conn()
        if _conn is not None:
            _conn.set_distance()
            return True
        return False

    #######################################################################
    # DISCO
    def _disco_conn(self):
        conn = self.get_conn(self.channel_index)
        if conn is not None:
            conn.conn_disco()

    @staticmethod
    def _disco_all():
        PORT_HANDLER.disco_all_Conn()

    # DISCO ENDE
    #######################################################################
    #######################################################################
    # SEND TEXT OUT
    def _snd_text(self, event: tk.Event):
        if self.channel_index:
            station = self.get_conn(self.channel_index)
            if station:
                ch_vars = self.get_ch_var(ch_index=self.channel_index)
                ind = str(ch_vars.input_win_index)
                if ind:
                    if float(ind) >= float(self._inp_txt.index(tk.INSERT)):
                        ind = str(self._inp_txt.index(tk.INSERT))
                    ind = str(int(float(ind))) + '.0'
                else:
                    ind = '1.0'
                txt_enc = 'UTF-8'
                if station.user_db_ent:
                    txt_enc = station.user_db_ent.Encoding
                tmp_txt = self._inp_txt.get(ind, self._inp_txt.index(tk.INSERT))

                tmp_txt = tmp_txt.replace('\n', '\r')
                station.send_data(tmp_txt.encode(txt_enc, 'ignore'))

                self._inp_txt.tag_remove('send', ind, str(self._inp_txt.index(tk.INSERT)))
                self._inp_txt.tag_add('send', ind, str(self._inp_txt.index(tk.INSERT)))

                ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))

                if '.0' in self._inp_txt.index(tk.INSERT):
                    self._inp_txt.tag_remove('send', 'insert-1c', tk.INSERT)

        else:
            self._send_to_monitor()

    def _send_to_monitor(self):
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        ind = str(ch_vars.input_win_index)
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
        ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))
        if int(float(self._inp_txt.index(tk.INSERT))) != int(float(self._inp_txt.index(tk.END))) - 1:
            self._inp_txt.delete(tk.END, tk.END)

    def _on_click_inp_txt(self, event=None):
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        _ind = ch_vars.input_win_index
        if _ind:
            self._inp_txt.tag_add('send', str(int(float(_ind))) + '.0', _ind)
            # self.inp_txt.tag_remove('send', str(max(float(self.inp_txt.index(tk.INSERT)) - 0.1, 1.0)), self.inp_txt.index(tk.INSERT))
            self._inp_txt.tag_remove('send', str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0',
                                     self._inp_txt.index(tk.INSERT))
        # self.inp_txt.tag_remove('send', tk.line.column, self.inp_txt.index(tk.INSERT))
        _ind2 = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'

        self._inp_txt.tag_remove('send', _ind2, self._inp_txt.index(tk.INSERT))
        ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))

    # SEND TEXT OUT
    #######################################################################
    # BW Plot
    def _update_bw_mon(self):
        _tr = False
        for _port_id in list(PORT_HANDLER.ax25_ports.keys()):
            _data = self.mh.get_bandwidth(
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

    # END BW Plot
    #######################################################################

    def _kaffee(self):
        self.sysMsg_to_monitor('Hinweis: Hier gibt es nur Muckefuck !')
        self.sprech('Gluck gluck gluck blubber blubber')
        # PORT_HANDLER.db.aprsWX_get_data_f_wxTree()
        # self._do_bbs_fwd()
        # self.conn_task = AutoConnTask()

    @staticmethod
    def _do_pms_autoFWD():
        PORT_HANDLER.get_bbs().start_man_autoFwd()

    def _do_pms_fwd(self):
        conn = self.get_conn()
        if conn is not None:
            conn.bbsFwd_start_reverse()

    def do_priv(self, event=None, login_cmd=''):
        _conn = self.get_conn()
        if _conn is not None:
            if _conn.user_db_ent:
                if _conn.user_db_ent.sys_pw:
                    _conn.cli.start_baycom_login(login_cmd=login_cmd)
                else:
                    self._open_settings_window('priv_win')

    def _open_ft_manager(self, event=None):
        self._open_settings_window('ft_manager')

    def _switch_monitor_mode(self):
        self._switch_mon_mode()
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

    #####################################################################
    #
    def conn_btn_update(self):
        """
        Called fm:
        self._ch_btn_clk
        PORT_HANDLER.accept_new_connection
        PORT_HANDLER.end_connection
        """
        conn = self.get_conn(self.channel_index)
        if conn:
            if self._conn_btn.cget('bg') != "red":
                self._conn_btn.configure(bg="red", text="Disconnect", command=self._disco_conn)
        elif self._conn_btn.cget('bg') != "green":
            self._conn_btn.configure(text="New Conn", bg="green", command=self.open_new_conn_win)
        # !! Loop !! self._ch_btn_status_update()

    def ch_status_update(self):
        # TODO Call just if necessary
        """ Triggerd when Connection Status has changed """
        self._ch_btn_status_update()
        # self.change_conn_btn()
        # self._change_conn_btn()
        self.on_channel_status_change()

    def _ch_btn_clk(self, ind: int):
        old_ch_vars = self.get_ch_var(ch_index=int(self.channel_index))
        old_ch_vars.input_win = self._inp_txt.get('1.0', tk.END)
        old_ch_vars.input_win_tags = get_all_tags(self._inp_txt)
        old_ch_vars.output_win_tags = get_all_tags(self._out_txt)
        old_ch_vars.input_win_cursor_index = self._inp_txt.index(tk.INSERT)
        self.channel_index = ind
        self._update_qso_Vars()
        self.ch_status_update()
        self.conn_btn_update()
        self._kanal_switch()  # Sprech

    def _ch_btn_status_update(self):
        # TODO Call just if necessary
        # TODO not calling in Tasker Loop for Channel Alarm (change BTN Color)
        # self.main_class.on_channel_status_change()
        ch_alarm = False
        # if PORT_HANDLER.get_all_connections().keys():
        for i in list(self._con_btn_dict.keys()):
            all_conn = PORT_HANDLER.get_all_connections()
            if i in list(all_conn.keys()):
                btn_txt = all_conn[i].to_call_str
                is_link = all_conn[i].is_link
                is_pipe = all_conn[i].pipe
                if is_pipe is None:
                    is_pipe = False
                if is_link:
                    btn_txt = 'L>' + btn_txt
                elif is_pipe:
                    btn_txt = 'P>' + btn_txt
                if self._con_btn_dict[i][1].get() != btn_txt:
                    self._con_btn_dict[i][1].set(btn_txt)
                if i == self.channel_index:
                    if is_link:
                        if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue2':
                            self._con_btn_dict[i][0].configure(bg='SteelBlue2')
                    elif is_pipe:
                        if self._con_btn_dict[i][0].cget('bg') != 'cyan2':
                            self._con_btn_dict[i][0].configure(bg='cyan2')
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'green2':
                            self._con_btn_dict[i][0].configure(bg='green2')
                else:
                    if self.get_ch_new_data_tr(i):
                        if is_link:
                            if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue4':
                                self._con_btn_dict[i][0].configure(bg='SteelBlue4')
                            # ch_alarm = False
                        elif is_pipe:
                            if self._con_btn_dict[i][0].cget('bg') != 'cyan4':
                                self._con_btn_dict[i][0].configure(bg='cyan4')
                            # ch_alarm = False
                        else:
                            ch_alarm = True
                            self._ch_btn_alarm(self._con_btn_dict[i][0])
                    else:
                        if is_link:
                            # ch_alarm = False
                            if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue4':
                                self._con_btn_dict[i][0].configure(bg='SteelBlue4')
                        elif is_pipe:
                            if self._con_btn_dict[i][0].cget('bg') != 'cyan4':
                                self._con_btn_dict[i][0].configure(bg='cyan4')
                            # ch_alarm = False
                        else:
                            if self._con_btn_dict[i][0].cget('bg') != 'green4':
                                self._con_btn_dict[i][0].configure(bg='green4')
            else:
                if self._con_btn_dict[i][1].get() != str(i):
                    # self.con_btn_dict[i].configure(text=str(i))
                    self._con_btn_dict[i][1].set(str(i))

                if not self.get_ch_new_data_tr(i):
                    if i == self.channel_index:
                        if self._con_btn_dict[i][0].cget('bg') != 'red2':
                            self._con_btn_dict[i][0].configure(bg='red2')
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'red4':
                            self._con_btn_dict[i][0].configure(bg='red4')
                else:
                    if i != self.channel_index:
                        if self._con_btn_dict[i][0].cget('bg') != 'yellow':
                            self._con_btn_dict[i][0].configure(bg='yellow')

        if self._ch_btn_blink_timer < time.time():
            self._ch_btn_blink_timer = time.time() + self._parm_btn_blink_time
        self._ch_alarm = ch_alarm

    def _ch_btn_alarm(self, btn: tk.Button):
        if self._ch_btn_blink_timer < time.time():
            _clr = generate_random_hex_color()
            if btn.cget('bg') != _clr:
                btn.configure(bg=_clr)

    def on_channel_status_change(self):
        """ Triggerd when Connection Status has changed + additional Trigger"""
        self.tabbed_sideFrame.on_ch_stat_change()
        self.update_station_info()

    def _update_stat_info_conn_timer(self):
        conn = self.get_conn()
        if conn is not None:
            self.stat_info_timer_var.set(get_time_delta(conn.cli.time_start))
        else:
            if self.stat_info_timer_var.get() != '--:--:--':
                self.stat_info_timer_var.set('--:--:--')

    def update_station_info(self):
        name = '-------'
        qth = '-------'
        loc = '------'
        # _dist = 0
        _status = '-------'
        _typ = '-----'
        _sw = '---------'
        _enc = ''
        _conn = self.get_conn()
        if _conn is not None:
            _db_ent = _conn.user_db_ent
            if _db_ent:
                if _db_ent.Name:
                    name = _db_ent.Name
                if _db_ent.QTH:
                    qth = _db_ent.QTH
                if _db_ent.LOC:
                    loc = _db_ent.LOC
                if _db_ent.Distance:
                    loc += f" ({_db_ent.Distance} km)"
                if _db_ent.TYP:
                    _typ = _db_ent.TYP
                if _db_ent.Software:
                    _sw = _db_ent.Software
                _enc = _db_ent.Encoding
            if _conn.is_link:
                _status = 'LINK'
                if self.stat_info_status_var.get() != _status:
                    self.stat_info_status_var.set(_status)
                    self.status_label.bind('<Button-1>', )
            elif _conn.pipe is not None:
                _status = 'PIPE'
                if self.stat_info_status_var.get() != _status:
                    self.stat_info_status_var.set(_status)
                    self.status_label.bind('<Button-1>', )
            elif _conn.ft_obj is not None:
                _status = f'{_conn.ft_obj.dir} FILE'
                if self.stat_info_status_var.get() != _status:
                    self.stat_info_status_var.set(_status)
                    # self.status_label.bind('<Button-1>', lambda: self._open_settings_window('ft_manager'))
                    self.status_label.bind('<Button-1>', self._open_ft_manager)
            else:
                _status = ''
                if _conn.cli.sysop_priv:
                    _status += 'S'
                else:
                    _status += '-'
                if _conn.link_holder_on:
                    _status += 'L'
                else:
                    _status += '-'
                if _conn.is_RNR:
                    _status += 'R'
                else:
                    _status += '-'
                _status += '----'
                if self.stat_info_status_var.get() != _status:
                    self.stat_info_status_var.set(_status)
                    self.status_label.bind('<Button-1>', self.do_priv)
        elif self.stat_info_status_var.get() != _status:
            self.stat_info_status_var.set(_status)
            self.status_label.bind('<Button-1>', )
        """
        if _dist:
            loc += f" ({_dist} km)"
        """
        # if self.stat_info_status_var.get() != _status:
        #     self.stat_info_status_var.set(_status)
        if self.stat_info_name_var.get() != name:
            self.stat_info_name_var.set(name)
        if self.stat_info_qth_var.get() != qth:
            self.stat_info_qth_var.set(qth)
        if self.stat_info_loc_var.get() != loc:
            self.stat_info_loc_var.set(loc)
        if self.stat_info_typ_var.get() != _typ:
            self.stat_info_typ_var.set(_typ)
        if self.stat_info_sw_var.get() != _sw:
            self.stat_info_sw_var.set(_sw)
        if self.stat_info_encoding_var.get() != _enc:
            self.stat_info_encoding_var.set(_enc)

    def _update_ft_info(self):
        _prog_val = 0
        _prog_var = '---.- %'
        _size_var = 'Size: ---,- / ---,- kb'
        _dur_var = 'Time: --:--:-- / --:--:--'
        _bps_var = 'BPS: ---.---'
        _next_tx = 'TX in: --- s'
        _conn = self.get_conn()
        if _conn is not None:
            if _conn.ft_obj is not None:
                _ft_obj = _conn.ft_obj
                _percentage_completion, _data_len, _data_sendet, _time_spend, _time_remaining, _baud_rate = _ft_obj.get_ft_infos()
                _prog_val = _percentage_completion
                _prog_var = f"{_percentage_completion} %"
                _data_len = get_kb_str_fm_bytes(_data_len)
                _data_sendet = get_kb_str_fm_bytes(_data_sendet)
                _size_var = f'Size: {_data_sendet} / {_data_len}'
                _t_spend = conv_timestamp_delta(_time_spend)
                _t_remaining = conv_timestamp_delta(_time_remaining)
                _dur_var = f'Time: {_t_spend} / {_t_remaining}'
                _bps_var = f"BPS: {format_number(_baud_rate)}"
                if _ft_obj.param_wait:
                    _n_tx = _ft_obj.last_tx - time.time()
                    _next_tx = f'TX in: {max(round(_n_tx), 0)} s'

        if self.tabbed_sideFrame.ft_duration_var.get() != _dur_var:
            self.tabbed_sideFrame.ft_progress['value'] = _prog_val
            self.tabbed_sideFrame.ft_progress_var.set(_prog_var)
            self.tabbed_sideFrame.ft_size_var.set(_size_var)
            self.tabbed_sideFrame.ft_duration_var.set(_dur_var)
            self.tabbed_sideFrame.ft_bps_var.set(_bps_var)
            self.tabbed_sideFrame.ft_next_tx_var.set(_next_tx)

    #########################################
    # TxTframe FNCs
    def _update_status_win(self):
        station = self.get_conn(self.channel_index)
        if station is not None:
            from_call = str(station.ax25_out_frame.from_call.call_str)
            status = station.zustand_tab[station.get_state_index()][1]
            # uid = station.ax25_out_frame.addr_uid
            n2 = station.n2
            unAck = f"unACK: {len(station.tx_buf_unACK.keys())}"
            vs_vr = f"VS/VR: {station.vr}/{station.vs}"
            n2_text = f"N2: {n2}"
            t1_text = f"T1: {max(0, int(station.t1 - time.time()))}"
            rtt_text = 'RTT: {:.1f}/{:.1f}'.format(station.RTT_Timer.rtt_last, station.RTT_Timer.rtt_average)
            t3_text = f"T3: {max(0, int(station.t3 - time.time()))}"
            if station.own_port.port_cfg.parm_T2_auto:
                t2_text = f"T2: {int(station.parm_T2 * 1000)}A"
            else:
                t2_text = f"T2: {int(station.parm_T2 * 1000)}"
            if self._status_name_var.get() != from_call:
                self._status_name_var.set(from_call)
            if self._status_status_var.get() != status:
                status_bg = STATUS_BG[status]
                self._status_status_var.set(status)
                self._status_status.configure(bg=status_bg)
            if self._status_unack_var.get() != unAck:
                self._status_unack_var.set(unAck)
                if len(station.tx_buf_unACK.keys()):
                    if self._status_unack.cget('bg') != 'yellow':
                        self._status_unack.configure(bg='yellow')
                else:
                    if self._status_unack.cget('bg') != 'green':
                        self._status_unack.configure(bg='green')
            if self._status_vs_var.get() != vs_vr:
                self._status_vs_var.set(vs_vr)
            if self._status_n2_var.get() != n2_text:
                self._status_n2_var.set(n2_text)
                if n2 > 4:
                    if self._status_n2.cget('bg') != 'yellow':
                        self._status_n2.configure(bg='yellow')
                elif n2 > 10:
                    if self._status_n2.cget('bg') != 'orange':
                        self._status_n2.configure(bg='orange')
                else:
                    if self._status_n2.cget('bg') != STAT_BAR_CLR:
                        self._status_n2.configure(bg=STAT_BAR_CLR)
            if self._status_t1_var.get() != t1_text:
                self._status_t1_var.set(t1_text)
            if self._status_t2_var.get() != t2_text:
                self._status_t2_var.set(t2_text)
            if self._status_rtt_var.get() != rtt_text:
                self._status_rtt_var.set(rtt_text)
            if self._status_t3_var.get() != t3_text:
                self._status_t3_var.set(t3_text)

        else:
            if self._status_status.cget('bg') != STAT_BAR_CLR:
                # self.status_name.configure(text="", bg=STAT_BAR_CLR)
                self._status_name_var.set('')
                self._status_status.configure(bg=STAT_BAR_CLR)
                self._status_status_var.set('')
                self._status_unack.configure(bg=STAT_BAR_CLR)
                self._status_unack_var.set('')
                self._status_vs_var.set('')
                self._status_n2.configure(bg=STAT_BAR_CLR)
                self._status_n2_var.set('')
                self._status_t1_var.set('')
                self._status_t2_var.set('')
                self._status_t3_var.set('')
                self._status_rtt_var.set('')

    def _switch_mon_mode(self):
        # TODO Save Stretched Positions
        if self.mon_mode:
            try:
                self._pw.remove(self._TXT_upper_frame)
                self._pw.remove(self._TXT_lower_frame)
            except tk.TclError:
                pass
            self._pw.add(self._TXT_upper_frame, weight=1)
            self._pw.add(self._TXT_mid_frame, weight=1)
            self._pw.add(self._TXT_lower_frame, weight=1)
        else:
            self._pw.remove(self._TXT_mid_frame)

    def _chk_rx_beep(self):
        rx_beep_check = self._rx_beep_var.get()
        if rx_beep_check:
            if self.rx_beep_box.cget('bg') != 'green':
                self.rx_beep_box.configure(bg='green', activebackground='green')
        else:
            if self.rx_beep_box.cget('bg') != STAT_BAR_CLR:
                self.rx_beep_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.get_ch_var().rx_beep_opt = rx_beep_check

    def _chk_timestamp(self):
        ts_check = self._ts_box_var.get()
        if ts_check:
            if self.ts_box_box.cget('bg') != 'green':
                self.ts_box_box.configure(bg='green', activebackground='green')
        else:
            if self.ts_box_box.cget('bg') != STAT_BAR_CLR:
                self.ts_box_box.configure(bg=STAT_BAR_CLR, activebackground=STAT_BAR_CLR)
        self.get_ch_var().timestamp_opt = ts_check

    def _set_stat_typ(self, event=None):
        conn = self.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                db_ent.TYP = self.stat_info_typ_var.get()
        else:
            self.stat_info_typ_var.set('-----')

    def _change_txt_encoding(self, event=None, enc=''):
        conn = self.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                if not enc:
                    enc = self.stat_info_encoding_var.get()
                db_ent.Encoding = enc
        else:
            self.stat_info_encoding_var.set('')

    ##########################################
    #
    def get_free_channel(self, start_channel=1):
        for ch_id in range(start_channel, 11):
            if not self.get_conn(con_ind=ch_id):
                return ch_id

    def get_ch_new_data_tr(self, ch_id):
        return bool(self.get_ch_var(ch_index=ch_id).new_data_tr)

    def set_tracer(self, state=None):
        _ais_obj = PORT_HANDLER.get_aprs_ais()
        if _ais_obj is not None:
            _ais_obj.be_tracer_active = bool(self.setting_tracer.get())
        else:
            self.setting_tracer.set(False)
        self.set_auto_tracer()
        # FIXME
        self.tabbed_sideFrame.set_auto_tracer_state()

    @staticmethod
    def get_tracer():
        _ais_obj = PORT_HANDLER.get_aprs_ais()
        if _ais_obj is not None:
            return bool(_ais_obj.be_tracer_active)
        return False

    def set_tracer_fm_aprs(self):
        _ais_obj = PORT_HANDLER.get_aprs_ais()
        if _ais_obj is not None:
            self.setting_tracer.set(_ais_obj.be_tracer_active)
        else:
            self.setting_tracer.set(False)
        self.tabbed_sideFrame.set_auto_tracer_state()

    def set_auto_tracer(self, event=None):
        _ais_obj = PORT_HANDLER.get_aprs_ais()
        set_to = False
        if _ais_obj is not None:
            self.set_tracer_fm_aprs()
            if self.setting_tracer.get():
                set_to = False
            else:
                set_to = bool(self.setting_auto_tracer.get())
            _ais_obj.tracer_auto_tracer_set(set_to)
        self.setting_auto_tracer.set(set_to)
        self.tabbed_sideFrame.set_auto_tracer_state()

    @staticmethod
    def get_auto_tracer_duration():
        _ais_obj = PORT_HANDLER.get_aprs_ais()
        if _ais_obj is None:
            return 0
        return _ais_obj.be_auto_tracer_duration

    def set_auto_tracer_duration(self, dur):
        _ais_obj = PORT_HANDLER.get_aprs_ais()
        if _ais_obj is not None:
            if type(dur) is int:
                _ais_obj.tracer_auto_tracer_duration_set(dur)
                self.set_auto_tracer()

    def set_dx_alarm(self, event=None):
        _dx_alarm = bool(self.setting_dx_alarm.get())
        if not _dx_alarm:
            self.setting_auto_tracer.set(False)
        self.set_auto_tracer()

    def get_dx_alarm(self):
        return bool(self.setting_dx_alarm.get())

    def get_side_frame(self):
        return self._side_btn_frame_top
