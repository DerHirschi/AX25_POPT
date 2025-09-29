import tkinter as tk
from datetime import datetime
from tkinter import ttk, TclError, messagebox

from ax25.ax25dec_enc import PIDByte
from cfg.constant import CFG_TR_DX_ALARM_BG_CLR, ENCODINGS, COLOR_MAP
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.os_fnc import is_linux
from fnc.str_fnc import conv_time_DE_str, get_time_delta, get_kb_str_fm_bytes, get_strTab, conv_timestamp_delta
from sound.popt_sound import SOUND


class SideTabbedFrame:
    def __init__(self, main_cl, frame, plot_frame=None, path_frame=None):
        self._root_class        = main_cl
        self.style              = self._root_class.style
        self._conn_typ_icon_tab = self._root_class.get_conn_typ_icon_16()
        ##########################################
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._get_colorMap  = lambda: COLOR_MAP.get(self._root_class.style_name, ('black', '#d9d9d9'))
        ##########################################
        self._tabControl = ttk.Notebook(
            frame,
            height=300,
        )
        self._tabControl.bind('<<NotebookTabChanged>>', self.on_ch_stat_change)
        port_handler    = self._root_class.get_PH_mainGUI()
        ##########################################
        # Vars
        self._ch_is_disc  = True
        # M
        self._tree_data   = []
        self._last_mh_ent = []
        self._mh_iid_map  = {}  # Map: unique_key (z.B. call-port) -> Treeview IID
        # Tracer Tab
        self._trace_tree_data       = []
        self._trace_tree_data_old   = {}
        # Connect Tab
        self._connects_iid_map  = {}  # Map: ch_id -> Treeview IID
        # Connect History
        self._old_conn_hist_len = 0
        ##########################################
        # GUI Vars
        self._max_frame_var  = tk.StringVar( frame, value='1')
        self._pac_len_var    = tk.IntVar(    frame, value=128)
        self._t2_var         = tk.StringVar( frame, value='1700')
        self._t2_auto_var    = tk.BooleanVar(frame)
        self._rnr_var        = tk.BooleanVar(frame)
        self._t2speech_var   = tk.BooleanVar(frame, value=self._root_class.get_ch_var().t2speech)
        self._autoscroll_var = tk.BooleanVar(frame, value=self._root_class.get_ch_var().autoscroll)
        self._cliRemote_var  = tk.BooleanVar(frame, value=True)
        # RTT
        self._rtt_worst_var = tk.StringVar(frame)
        self._rtt_avg_var   = tk.StringVar(frame)
        self._rtt_last_var  = tk.StringVar(frame)
        self._rtt_best_var  = tk.StringVar(frame)
        #
        self._conn_duration_var = tk.StringVar(frame, value='--:--:--')
        self._tx_buff_var       = tk.StringVar(frame, value='')
        self._tx_count_var      = tk.StringVar(frame, value='')
        self._rx_count_var      = tk.StringVar(frame, value='')
        self._status_label_var  = tk.StringVar(frame, value='')

        ##########################################
        tab1_kanal      = ttk.Frame(self._tabControl)
        tab_connects    = ttk.Frame(self._tabControl)
        tab2_mh         = ttk.Frame(self._tabControl)
        tab4_settings   = ttk.Frame(self._tabControl)
        # self.tab5_ch_links = ttk.Frame(self._tabControl)  # TODO
        tab6_monitor    = ttk.Frame(self._tabControl)
        tab7_tracer     = ttk.Frame(self._tabControl)
        # self._path_plot = None
        ##############################################################
        self._tabControl.add(tab1_kanal, text=self._getTabStr('channel'))
        # self._tabControl.add(tab3, text='Ports')                   # TODO
        self._tabControl.add(tab4_settings, text='Global')
        self._tabControl.add(tab_connects,  text='Connects')
        self._tabControl.add(tab6_monitor,  text='Monitor')
        self._tabControl.add(tab2_mh,       text='MH')
        self._tabControl.add(tab7_tracer,   text='Tracer')
        if plot_frame:
            self._tabControl.add(plot_frame, text='BW-Plot')
        elif path_frame:
            # self._path_plot = LiveConnPath(self._tabControl)
            self._tabControl.add(path_frame, text='Pacman')

        self._tabControl.pack(expand=1, fill="both")
        ################################################
        # Kanal
        parm_y = 20
        m_f_label = ttk.Label(tab1_kanal, text='Max Pac:')
        self._max_frame = ttk.Spinbox(tab1_kanal,
                                     from_=1,
                                     to=7,
                                     increment=1,
                                     width=2,
                                     textvariable=self._max_frame_var,
                                     command=self._set_max_frame,
                                     state='disabled')
        m_f_label.place(x=10, y=parm_y)
        self._max_frame.place(x=10 + 80, y=parm_y)
        parm_y = 55
        p_l_label = ttk.Label(tab1_kanal, text='Pac Len:')
        vals = []
        for i in range(256):
            vals.append(str(i + 1))
        self._pac_len = ttk.Combobox(tab1_kanal,
                                       width=4,
                                       textvariable=self._pac_len_var,
                                       values=vals,
                                       state='disabled')
        self._pac_len.bind("<<ComboboxSelected>>", self._set_pac_len)
        p_l_label.place(x=10, y=parm_y)
        self._pac_len.place(x=10 + 80, y=parm_y)
        #################
        # t2 Auto Checkbutton
        parm_y = 90
        label = ttk.Label(tab1_kanal, text='T2:')

        val_list = [str(x) for x in range(0, 10)]

        for i in range(1, 500):
            # 10 - 5000
            val_list.append(str(i * 10))

        self._t2 = ttk.Combobox(tab1_kanal,
                               width=4,
                               textvariable=self._t2_var,
                               values=val_list,
                               state='disabled')
        self._t2.bind("<<ComboboxSelected>>", self._set_t2)
        label.place(x=10, y=parm_y)
        self._t2.place(x=50, y=parm_y)
        ####################
        self._t2_auto = ttk.Checkbutton(tab1_kanal,
                                       text='T2-Auto',
                                       variable=self._t2_auto_var,
                                       state='disabled',
                                       command=self._chk_t2auto
                                       )
        self._t2_auto.place(x=10, y=parm_y + 35)

        # RNR Checkbutton
        parm_y = 150

        self._rnr = ttk.Checkbutton(tab1_kanal,
                                   text='RNR',
                                   variable=self._rnr_var,
                                   state='disabled',
                                   command=self._chk_rnr)
        self._rnr.place(x=10, y=parm_y)
        # Sprech
        parm_y = 200

        self.t2speech = ttk.Checkbutton(tab1_kanal,
                                       text='Sprachausgabe',
                                       variable=self._t2speech_var,
                                       command=self._chk_t2speech)
        self.t2speech.place(x=10, y=parm_y)
        # Autoscroll
        parm_y = 225

        autoscroll = ttk.Checkbutton(tab1_kanal,
                                          text='Autoscroll',
                                          variable=self._autoscroll_var,
                                          command=self._chk_autoscroll
                                          )
        autoscroll.place(x=10, y=parm_y)

        # Remote /CLI Remote
        parm_y = 250

        self._cliRemote = ttk.Checkbutton(tab1_kanal,
                                         text='CLI/Remote',
                                         variable=self._cliRemote_var,
                                         state='disabled',
                                         command=self._chk_cliRemote
                                         )
        self._cliRemote.place(x=10, y=parm_y)

        # Link Holder
        parm_y = 175
        # self.link_holder_var = tk.BooleanVar(tab1_kanal)
        self._link_holder = ttk.Checkbutton(tab1_kanal,
                                            text=self._getTabStr('linkholder'),
                                            variable=self._root_class.link_holder_var,
                                            state='disabled',
                                            command=self._chk_link_holder
                                            )
        self._link_holder.place(x=10, y=parm_y)

        clear_ch_data_btn = ttk.Button(tab1_kanal,
                                      text=self._getTabStr('clean_qso'),
                                      command=self._root_class.clear_channel_vars
                                      )
        clear_ch_data_btn.place(x=140, y=135)

        link_holder_settings_btn = ttk.Button(tab1_kanal,
                                             text=self._getTabStr('linkholder'),
                                             command=self._root_class.open_link_holder_sett
                                             )
        link_holder_settings_btn.place(x=140, y=165)

        ttk.Label(tab1_kanal, textvariable=self._rtt_best_var).place(x=170, y=10)
        ttk.Label(tab1_kanal, textvariable=self._rtt_worst_var).place(x=170, y=35)
        ttk.Label(tab1_kanal, textvariable=self._rtt_avg_var).place(x=170, y=60)
        ttk.Label(tab1_kanal, textvariable=self._rtt_last_var).place(x=170, y=85)

        ##########################################
        # Kanal Rechts / Status / FT
        ttk.Separator(tab1_kanal, orient='vertical').place(x=280, rely=0.05, relheight=0.9, relwidth=0.6)
        ##########################################

        # Conn Dauer
        x = 290
        y = 20
        ttk.Label(tab1_kanal, textvariable=self._conn_duration_var).place(x=x, y=y)
        #### conn_durration_var
        # TX Buffer
        x = 290
        y = 45
        ttk.Label(tab1_kanal, textvariable=self._tx_buff_var).place(x=x, y=y)
        # TX Gesamt
        x = 290
        y = 70
        ttk.Label(tab1_kanal, textvariable=self._tx_count_var).place(x=x, y=y)
        # RX Gesamt
        x = 290
        y = 95
        ttk.Label(tab1_kanal, textvariable=self._rx_count_var).place(x=x, y=y)

        # Status /Pipe/Link/File-RX/File-TX
        bg = self._get_colorMap()[1]
        status_label = tk.Label(tab1_kanal,
                                fg='red',
                                bg=bg,
                                textvariable=self._status_label_var)
        font = status_label.cget('font')
        status_label.configure(font=(font[0], 12))
        status_label.place(x=290, y=120)
        ######################
        ttk.Separator(tab1_kanal, orient='horizontal').place(x=285, y=150, relheight=0.6, relwidth=0.9)
        #####################
        # Progress bar
        # tk.Label(tab1_kanal, text='File Transfer').place(x=380, y=160)
        x = 300
        y = 170
        self.ft_progress = ttk.Progressbar(tab1_kanal,
                                              orient='horizontal',
                                              length=150,
                                              mode='determinate',
                                              )
        self.ft_progress.place(x=x, y=y)
        self.ft_progress.bind('<Button-1>', self._root_class.open_ft_manager)
        self.ft_progress['value'] = 0

        ttk.Label(tab1_kanal, textvariable=self._root_class.ft_progress_var).place(x=x + 160, y=y)
        ttk.Label(tab1_kanal, textvariable=self._root_class.ft_size_var).place(x=x, y=y + 25)
        ttk.Label(tab1_kanal, textvariable=self._root_class.ft_duration_var).place(x=x, y=y + 50)
        ttk.Label(tab1_kanal, textvariable=self._root_class.ft_bps_var).place(x=x, y=y + 75)
        ttk.Label(tab1_kanal, textvariable=self._root_class.ft_next_tx_var).place(x=x + 160, y=y + 75)
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

        self._tree.heading('mh_last_seen', text='Time')
        self._tree.heading('mh_call', text='Call')
        self._tree.heading('mh_dist', text='km')
        self._tree.heading('mh_port', text='Port')
        self._tree.heading('mh_nPackets', text='PACK')
        self._tree.heading('mh_route', text='Route')
        self._tree.column("mh_last_seen",   anchor='w',      stretch=tk.NO, width=75)
        self._tree.column("mh_call",        anchor='w',      stretch=tk.NO, width=90)
        self._tree.column("mh_dist",        anchor='center', stretch=tk.NO, width=60)
        self._tree.column("mh_port",        anchor='center', stretch=tk.NO, width=50)
        self._tree.column("mh_nPackets",    anchor='w',      stretch=tk.NO, width=60)
        self._tree.column("mh_route",       anchor='w',      stretch=tk.YES, width=180)
        self._tree.tag_configure("dx_alarm", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')

        self._tree.bind('<<TreeviewSelect>>', self._entry_selected)

        btn_frame = ttk.Frame(tab2_mh)
        btn_frame.grid(row=1, column=0, columnspan=2)
        ttk.Button(btn_frame,
                  text="MH",
                  command=self._open_mh
                  ).pack(side='left', )

        ttk.Button(btn_frame,
                  # text="Statistik",
                  text=self._getTabStr('statistic'),
                  command=self._open_PortStat
                  ).pack(side='left', )

        #############################################################################
        # Global Settings ################################
        # Global Sound
        ttk.Checkbutton(tab4_settings,
                        text="Sound",
                        variable=self._root_class.setting_sound,
                        command=self._chk_sound
                        ).place(x=10, y=10)
        # Bell
        ttk.Checkbutton(tab4_settings,
                        text="Bell",
                        variable=self._root_class.setting_noty_bell,
                        command=self._root_class.set_noty_bell_active
                        ).place(x=150, y=10)
        # Global Sprech
        sprech_btn = ttk.Checkbutton(tab4_settings,
                                     text=self._getTabStr('sprech'),
                                     variable=self._root_class.setting_sprech,
                                     command=self._chk_sprech_on
                                     )
        sprech_btn.place(x=10, y=35)
        if not is_linux():
            sprech_btn.configure(state='disabled')
        # Global Bake
        ttk.Checkbutton(tab4_settings,
                        text=self._getTabStr('beacon'),
                        variable=self._root_class.setting_bake,
                        command=self._chk_beacon,
                        ).place(x=10, y=60)
        # DX Alarm  > dx_alarm_on
        ttk.Checkbutton(tab4_settings,
                        text="Tracer",
                        variable=self._root_class.setting_tracer,
                        command=self._chk_tracer,
                        # state='disabled'
                        ).place(x=10, y=85)
        auto_tracer_state = {
            True: 'disabled',
            False: 'normal'
        }.get(self._root_class.get_tracer(), 'disabled')
        self._autotracer_chk_btn = ttk.Checkbutton(tab4_settings,
                                                   text="Auto-Tracer",
                                                   variable=self._root_class.setting_auto_tracer,
                                                   command=self._chk_auto_tracer,
                                                   state=auto_tracer_state
                                                   )
        self._autotracer_chk_btn.place(x=10, y=110)
        ttk.Checkbutton(tab4_settings,
                        text="DX-Alarm",
                        variable=self._root_class.setting_dx_alarm,
                        command=self._root_class.set_dx_alarm,
                        # state='disabled'
                        ).place(x=10, y=135)
        # RX ECHO
        ttk.Checkbutton(tab4_settings,
                        text="RX-Echo",
                        variable=self._root_class.setting_rx_echo,
                        command=self._set_rx_echo
                        ).place(x=10, y=160)
        ############
        # CH ECHO
        # self._chk_btn_default_clr = self._autotracer_chk_btn.cget('bg')
        # self._ch_echo_vars = {}
        #################
        ###################################################################################
        # Monitor Frame
        # Address
        x = 10
        y = 10
        # self.to_add_var = tk.StringVar(tab6_monitor)
        ttk.Label(tab6_monitor, text=f"{self._getTabStr('to')}:").place(x=x, y=y)
        ttk.Entry(tab6_monitor, textvariable=self._root_class.mon_to_add_var).place(x=x + 40, y=y)

        # CMD/RPT
        x = 10
        y = 80
        # self.cmd_var = tk.BooleanVar(tab6_monitor)
        ttk.Checkbutton(tab6_monitor,
                        variable=self._root_class.mon_cmd_var,
                        text='CMD/RPT').place(x=x, y=y)

        # Poll
        x = 10
        y = 105
        # self.poll_var = tk.BooleanVar(tab6_monitor)
        ttk.Checkbutton(tab6_monitor,
                        variable=self._root_class.mon_poll_var,
                        text='Poll').place(x=x, y=y)

        # Port
        x = 40
        y = 140
        ttk.Label(tab6_monitor, text=f"{self._getTabStr('port')}:").place(x=x, y=y)
        # self.mon_port_var = tk.StringVar(tab6_monitor)
        # self._main_win.mon_port_var.set('0')
        vals = ['0']
        if port_handler.get_all_ports().keys():
            vals = [str(x) for x in list(port_handler.get_all_ports().keys())]
        mon_port_ent = ttk.Combobox(tab6_monitor,
                                    width=4,
                                    textvariable=self._root_class.mon_port_var,
                                    values=vals,
                                    )
        mon_port_ent.place(x=x + 50, y=y)
        mon_port_ent.bind("<<ComboboxSelected>>", self._chk_mon_port)
        # Calls
        x = 40
        y = 175
        # self.mon_call_var = tk.StringVar(tab6_monitor)
        # vals = []
        # if self.main_win.ax25_port_handler.ax25_ports.keys():
        #     _vals = [str(x) for x in list(self.main_win.ax25_port_handler.ax25_ports.keys())]
        self._mon_call_ent = ttk.Combobox(tab6_monitor,
                                          width=9,
                                          textvariable=self._root_class.mon_call_var,
                                          values=[],
                                          )
        self._mon_call_ent.place(x=x, y=y)

        # Auto Scrolling
        x = 10
        y = 210
        # self.mon_scroll_var = tk.BooleanVar(tab6_monitor)
        ttk.Checkbutton(tab6_monitor,
                        variable=self._root_class.mon_scroll_var,
                        text=self._getTabStr('scrolling')).place(x=x, y=y)

        # Monitor APRS Decoding Output
        x = 10
        y = 235
        # self.mon_aprs_var = tk.BooleanVar(tab6_monitor)
        # self.mon_aprs_var.set(True)
        ttk.Checkbutton(tab6_monitor,
                        variable=self._root_class.mon_dec_aprs_var,
                        text='APRS').place(x=x, y=y)
        # Monitor NetRom Decoding Output
        x = 10
        y = 260
        ttk.Checkbutton(tab6_monitor,
                        variable=self._root_class.mon_dec_nr_var,
                        text='NetRom').place(x=x, y=y)
        # Monitor Distance Decoding Output
        x = 10
        y = 285
        ttk.Checkbutton(tab6_monitor,
                        variable=self._root_class.mon_dec_dist_var,
                        text=self._getTabStr('distance')).place(x=x, y=y)
        # Monitor Distance Decoding Output
        x = 10
        y = 310
        ttk.Checkbutton(tab6_monitor,
                        variable=self._root_class.mon_dec_hex_var,
                        text='HEX').place(x=x, y=y)

        # Monitor Decoding
        ttk.Label(tab6_monitor, text='Decoding:').place(x=10, y=335)
        # self.mon_decoding_var.set(True)
        dec_val = ['Auto'] + list(ENCODINGS)
        ttk.Combobox(tab6_monitor,
                     width=9,
                     textvariable=self._root_class.setting_mon_encoding,
                     values=dec_val,
                     ).place(x=115, y=335)

        ##########################################################################
        # PID

        # self.mon_pid_var = tk.StringVar(tab6_monitor)
        ttk.Label(tab6_monitor, text='PID:').place(x=10, y=45)
        pid = PIDByte()  # TODO CONST PIDByte().pac_types
        pac_types = dict(pid.pac_types)
        vals = []
        for x in list(pac_types.keys()):
            pid.pac_types[int(x)]()
            vals.append(f"{str(hex(int(x))).upper()}>{pid.flag}")
        ttk.Combobox(tab6_monitor,
                     width=20,
                     values=vals,
                     textvariable=self._root_class.mon_pid_var).place(x=50, y=45)
        self._root_class.mon_pid_var.set(vals[0])
        # self.pac_len.bind("<<ComboboxSelected>>", self.set_pac_len)
        # Monitor RX-Filter Ports
        # self._mon_port_on_vars = {}
        all_ports = port_handler.ax25_ports
        i = 1
        for port_id in all_ports:
            # self._mon_port_on_vars[port_id] = tk.BooleanVar(tab6_monitor)
            x = 190
            y = 55 + (25 * i)
            ttk.Checkbutton(tab6_monitor,
                            text=f"Port {port_id}",
                            variable=self._root_class.mon_port_on_vars[port_id],
                            command=self._chk_mon_port_filter
                            ).place(x=x, y=y)
            i += 1
            # self._mon_port_on_vars[port_id].set(all_ports[port_id].monitor_out)

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

        self._trace_tree.heading('rx_time',     text='Time')
        self._trace_tree.heading('call',        text='Call')
        self._trace_tree.heading('port',        text='Port')
        self._trace_tree.heading('distance',    text='km')
        self._trace_tree.heading('path',        text='Path')
        self._trace_tree.column("rx_time",  anchor='center', stretch=tk.NO, width=75)
        self._trace_tree.column("call",                      stretch=tk.NO, width=90)
        self._trace_tree.column("port",     anchor='center', stretch=tk.NO, width=50)
        self._trace_tree.column("distance",                  stretch=tk.NO, width=60)
        self._trace_tree.column("path",     anchor='center', stretch=tk.YES, width=180)
        self._trace_tree.bind('<<TreeviewSelect>>', self._trace_entry_selected)

        btn_frame_tr = ttk.Frame(tab7_tracer)
        btn_frame_tr.grid(row=1, column=0, columnspan=2)
        ttk.Button(btn_frame_tr,
                  text="SEND",
                  command=self._tracer_send
                  ).pack(side='left')
        #ttk.Button(btn_frame_tr,
        #          text="Tracer",
        #          command=self._open_tracer
        #          ).pack(side='left', padx=20)
        """
        tk.Button(btn_frame_tr,
                  text=self._getTabStr('delete'),
                  command=self._delete_tracer
                  ).pack(side='left', padx=20)
        """
        #################################
        self._init_connects_tab(tab_connects)
        #################################
        # Tasker
        self._tasker_dict = {
            0: self._update_rtt,
            2: self._update_connects,
            4: self._update_side_mh,
            5: self._update_side_trace,
        }

        self._chk_mon_port()
        # self._update_ch_echo()
        self._update_side_mh()
        self._update_side_trace()

    def _init_connects_tab(self, root_frame: ttk.Frame):
        # TREE
        main_f = ttk.Frame(root_frame)
        main_f.pack(fill='both', expand=True)
        ######################################
        pw = ttk.Panedwindow(main_f, orient='vertical')
        pw.pack(fill='both', expand=True)
        ############
        cur_conn_tab_f = ttk.Frame(pw)
        his_conn_tab_f = ttk.Frame(pw)
        cur_conn_tab_f.pack(fill='both', expand=True)
        his_conn_tab_f.pack(fill='both', expand=True)
        ############
        pw.add(cur_conn_tab_f, weight=0)
        pw.add(his_conn_tab_f, weight=0)
        ######################################
        # Connected Tab
        columns = (
            'channel',
            'call',
            'own_call',
            'port',
            'typ',
            'dauer',
        )

        self._connects_tree = ttk.Treeview(cur_conn_tab_f, columns=columns, show='tree headings')

        self._connects_tree.heading('channel',  text='CH')
        self._connects_tree.heading('call',     text='To')
        self._connects_tree.heading('own_call', text='Station')
        self._connects_tree.heading('port',     text='Port')
        self._connects_tree.heading('typ',      text='Typ')
        self._connects_tree.heading('dauer',    text='Time')
        self._connects_tree.column("#0",        anchor='w',      stretch=tk.NO,  width=35)
        self._connects_tree.column("channel",   anchor='w',      stretch=tk.NO,  width=40)
        self._connects_tree.column("call",      anchor='w',      stretch=tk.NO,  width=90)
        self._connects_tree.column("own_call",  anchor='w',      stretch=tk.NO,  width=90)
        self._connects_tree.column("port",      anchor='center', stretch=tk.NO,  width=50)
        self._connects_tree.column("typ",       anchor='w',      stretch=tk.NO,  width=90)
        self._connects_tree.column("dauer",     anchor='w',      stretch=tk.YES, width=110)

        self._connects_tree.tag_configure("bell", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        self._connects_tree.bind('<<TreeviewSelect>>', self._connects_entry_selected)
        self._connects_tree.pack(fill='both', expand=True)
        ######################################
        # Connect History Tab
        columns = (
            'channel',
            'call',
            'own_call',
            'port',
            'dist',
            'typ',
            'dauer',
            'time',
        )

        self._conn_his_tab = ttk.Treeview(his_conn_tab_f, columns=columns, show='tree headings')

        self._conn_his_tab.heading('channel',   text='CH')
        self._conn_his_tab.heading('call',      text='To')
        self._conn_his_tab.heading('own_call',  text='Station')
        self._conn_his_tab.heading('port',      text='Port')
        self._conn_his_tab.heading('dist',       text='km')
        self._conn_his_tab.heading('typ',       text='Typ')
        self._conn_his_tab.heading('dauer',     text='Duration')
        self._conn_his_tab.heading('time',      text='Time')

        self._conn_his_tab.column("#0",         anchor='w',      stretch=tk.NO,  width=45)
        self._conn_his_tab.column("channel",    anchor='center', stretch=tk.NO,  width=40)
        self._conn_his_tab.column("call",       anchor='w',      stretch=tk.NO,  width=90)
        self._conn_his_tab.column("own_call",   anchor='w',      stretch=tk.NO,  width=90)
        self._conn_his_tab.column("port",       anchor='center', stretch=tk.NO,  width=50)
        self._conn_his_tab.column("dist",       anchor='w',      stretch=tk.NO,  width=50)
        self._conn_his_tab.column("typ",        anchor='w',      stretch=tk.NO,  width=110)
        self._conn_his_tab.column("dauer",      anchor='center', stretch=tk.NO,  width=90)
        self._conn_his_tab.column("time",       anchor='w',      stretch=tk.YES, width=110)

        #self._conn_his_tab.tag_configure("bell", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        #self._connects_tree.bind('<<TreeviewSelect>>', self._connects_entry_selected)
        self._conn_his_tab.pack(fill='both', expand=True)
        ######################################
        # Btn Frame
        btn_frame3 = ttk.Frame(main_f)
        btn_frame3.pack()
        ttk.Button(btn_frame3,
                  text=self._getTabStr('disconnect_all'),
                  command=self._disco_all
                  ).pack()


    def _set_rx_echo(self, event=None):
        port_handler = self._root_class.get_PH_mainGUI()
        port_handler.rx_echo_on = bool(self._root_class.setting_rx_echo.get())
        self._root_class.set_rxEcho_icon(self._root_class.setting_rx_echo.get())

    def set_auto_tracer_state(self):
        bool_state = self._root_class.get_tracer() or not self._root_class.get_dx_alarm()
        state = {
            True: 'disabled',
            False: 'normal'
        }.get(bool_state, 'disabled')
        self._autotracer_chk_btn.configure(state=state)

    def _chk_sound(self):
        if self._root_class.setting_sound.get():
            SOUND.master_sound_on = True
        else:
            SOUND.master_sound_on = False

    def _chk_tracer(self):
        self._root_class.set_tracer()

    def _chk_beacon(self):
        POPT_CFG.set_guiPARM_main({
            'gui_cfg_beacon': bool(self._root_class.setting_bake.get())
        })
        self._root_class.set_Beacon_icon(self._root_class.setting_bake.get())

    def _chk_auto_tracer(self):
        self._root_class.set_auto_tracer()

    def _chk_rnr(self):
        conn = self._root_class.get_conn()
        if conn is not None:
            if self._rnr_var.get():
                conn.set_RNR()
            else:
                conn.unset_RNR()

    def _chk_link_holder(self):
        conn = self._root_class.get_conn()
        if conn is not None:
            if self._root_class.link_holder_var.get():
                conn.link_holder_on = True
                conn.link_holder_timer = 0
            else:
                conn.link_holder_on = False
            self._root_class.on_channel_status_change()

    def _chk_cliRemote(self):
        conn = self._root_class.get_conn()
        if not conn:
            self._cliRemote_var.set(True)
            self._cliRemote.configure(state='disabled')
            return

        if self._cliRemote_var.get():
            conn.cli_remote = True
            return
        conn.cli_remote = False

    def _chk_t2auto(self):
        conn = self._root_class.get_conn()
        if conn is not None:
            if self._t2_auto_var.get():
                # conn.port_cfg['parm_T2_auto'] = True
                conn.set_T2auto(True)
                conn.calc_irtt()
                self._t2_var.set(str(conn.get_port_cfg().get('parm_T2', 500)))
                self._t2.configure(state='disabled')
            else:
                # conn.port_cfg['parm_T2_auto'] = False
                conn.set_T2auto(False)
                self._t2.configure(state='normal')
            conn.calc_irtt()

    def _chk_sprech_on(self):
        self._root_class.chk_master_sprech_on()

    def _chk_mon_port(self, event=None):
        port_handler = self._root_class.get_PH_mainGUI()
        port_id = int(self._root_class.mon_port_var.get())
        vals = port_handler.get_stat_calls_fm_port(port_id)
        if vals:
            self._root_class.mon_call_var.set(vals[0])
        self._mon_call_ent.configure(values=vals)

    def _chk_mon_port_filter(self):
        port_handler = self._root_class.get_PH_mainGUI()
        all_ports = port_handler.ax25_ports
        for port_id in all_ports:
            all_ports[port_id].monitor_out = self._root_class.mon_port_on_vars[port_id].get()

    def update_mon_port_id(self):
        port_handler = self._root_class.get_PH_mainGUI()
        if port_handler.get_all_ports().keys():
            vals = [str(x) for x in list(port_handler.get_all_ports().keys())]
            self._mon_call_ent.configure(values=vals)

    def _set_t2(self, event):
        conn = self._root_class.get_conn()
        if conn is not None:
            # conn.port_cfg['parm_T2'] = min(max(int(self.t2_var.get()), 500), 3000)
            try:
                conn.set_T2var(int(self._t2_var.get()))
            except ValueError:
                pass

    def tasker(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except TclError:
            return False
        else:
            if ind in self._tasker_dict.keys():
                self._tasker_dict[ind]()
                return True
        return False

    def _entry_selected(self, event):
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[1]
            vias = record[5]
            vias = vias.split(' ')
            vias.reverse()
            vias = ' '.join(vias)
            port = record[3]
            if type(port) is str:
                port = int(port.split('-')[0])

            if vias:
                call = f'{call} {vias}'
            if not self._root_class.new_conn_win:
                self._root_class.open_new_conn_win()
            if self._root_class.new_conn_win:
                self._root_class.new_conn_win.preset_ent(call, port)

    def _connects_entry_selected(self, event=None):
        selected_items = self._connects_tree.selection()
        if not selected_items:
            self._selected_ch_id = 0
            return
        item = self._connects_tree.item(selected_items[0])
        ch_id = int(item['values'][0])
        self._root_class.switch_channel(ch_id)

    def _trace_entry_selected(self, event=None):
        pass
        # self._main_win.open_be_tracer_win()

    def _tracer_send(self):
        port_handler = self._root_class.get_PH_mainGUI()
        port_handler.get_aprs_ais().tracer_sendit()

    # MH

    def _update_rtt(self):
        best = ''
        worst = ''
        avg = ''
        last = ''
        status_text = ''
        duration = f"{self._getTabStr('time_connected')}: --:--:--"
        tx_buff = 'TX-Buffer: --- kb'
        tx_count = 'TX: --- kb'
        rx_count = 'RX: --- kb'
        station = self._root_class.get_conn(self._root_class.channel_index)
        if station is not None:
            if station.RTT_Timer.rtt_best == 999.0:
                best = "Best: -1"
            else:
                best = "Best: {:.1f}".format(station.RTT_Timer.rtt_best)
            worst = "Worst: {:.1f}".format(station.RTT_Timer.rtt_worst)
            avg = "AVG: {:.1f}".format(station.RTT_Timer.rtt_average)
            last = "Last: {:.1f}".format(station.RTT_Timer.rtt_last)
            duration = f"{self._getTabStr('time_connected')}: {get_time_delta(station.time_start)}"
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
        if duration != self._conn_duration_var.get():
            self._status_label_var.set(status_text)
            self._rtt_best_var.set(best)
            self._rtt_worst_var.set(worst)
            self._rtt_avg_var.set(avg)
            self._rtt_last_var.set(last)
            self._conn_duration_var.set(duration)
            self._tx_buff_var.set(tx_buff)
            self._tx_count_var.set(tx_count)
            self._rx_count_var.set(rx_count)

    ##########################################################
    # Connects
    def _update_connects(self):
        self._update_conn_his()
        port_handler = self._root_class.get_PH_mainGUI()
        connects = port_handler.get_all_connections(with_null=True)
        current_chids = set(connects.keys())  # Set für schnelle Checks

        # Entferne Einträge, die nicht mehr existieren
        for ch_id in list(self._connects_iid_map.keys()):
            if ch_id not in current_chids:
                self._connects_tree.delete(self._connects_iid_map[ch_id])
                del self._connects_iid_map[ch_id]

        # Update oder füge neue Einträge hinzu (sortiert)
        ch_list = sorted(connects.keys())
        for ch_id in ch_list:
            conn  = connects[ch_id]
            timer = datetime.now() - conn.time_start
            timer = str(timer).split('.')[0]
            typ   = conn.cli_type
            bell  = conn.noty_bell
            is_digi = False
            if conn.is_link:
                is_digi = True
                if hasattr(conn.LINK_Connection, 'to_call_str'):
                    typ = f'DIGI {conn.LINK_Connection.to_call_str}'
                else:
                    typ = 'DIGI'
            if conn.pipe:
                typ = 'PIPE'
            ent = [
                int(conn.ch_index),
                str(conn.to_call_str),
                str(conn.my_call_str),
                int(conn.port_id),
                str(typ),
                timer,
            ]
            if is_digi:
                typ = 'DIGI'
            image = self._conn_typ_icon_tab.get(typ, None)
            tags  = ('bell',) if bell else ()

            if ch_id in self._connects_iid_map:
                # Bestehenden Eintrag aktualisieren (nur nötige Daten: typ, timer, aber für Konsistenz alle)
                iid = self._connects_iid_map[ch_id]
                if image:
                    self._connects_tree.item(iid, values=ent, tags=tags, image=image)
                else:
                    self._connects_tree.item(iid, values=ent, tags=tags)
            else:
                # Neuen Eintrag hinzufügen
                if image:
                    iid = self._connects_tree.insert('', 'end', values=ent, tags=tags, image=image)
                else:
                    iid = self._connects_tree.insert('', 'end', values=ent, tags=tags)

                self._connects_iid_map[ch_id] = iid

    def _update_conn_his(self):
        mh = self._get_mh()
        if not hasattr(mh, 'get_conn_hist'):
            return
        conn_history = mh.get_conn_hist()
        if len(conn_history) == self._old_conn_hist_len:
            return
        new_entries = conn_history[self._old_conn_hist_len:]
        for ent in new_entries:  # Reversed, um neueste zuerst einzufügen
            ent: dict
            typ = ent.get('typ', '')
            image_typ = str(typ)
            if 'DIGI' in image_typ:
                image_typ = 'DIGI'
            if ent.get('disco', False):
                image_typ += '-DISCO'
            else:
                image_typ += '-CONN'
            if ent.get('conn_incoming', False):
                image_typ += '-IN'
            else:
                image_typ += '-OUT'


            image = self._conn_typ_icon_tab.get(image_typ, None)
            tags = ()  # Optional: tags = ('disco',) if ent.disco else ()

            # Formatiere Dauer (dauer: Time)
            if ent.get('disco', False):
                duration_str = conv_timestamp_delta(ent.get('duration'))
            else:
                duration_str = "--:--:--"

            # Formatiere Startzeit (time: Duration)
            time_str = conv_time_DE_str(ent.get('time'))

            ent_values = (
                ent.get('ch_id', 0),           # channel
                ent.get('from_call' ,''),       # call (To)
                ent.get('own_call', ''),   # own_call (Station)
                ent.get('port_id', -1),    # port
                ent.get('distance', -1),    # Distance
                typ,  # typ
                duration_str,  # dauer (Time)
                time_str,  # time (Duration)
            )
            if image:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags, image=image)
            else:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags)

        self._old_conn_hist_len = len(conn_history)

    ################################################
    # MH
    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        mh = self._get_mh()
        for ret_ent in self._tree_data:
            if ret_ent[1] and mh.dx_alarm_trigger:
                self._tree.insert('', 'end', values=ret_ent[0], tags=('dx_alarm',))
            else:
                self._tree.insert('', 'end', values=ret_ent[0], )

    def _format_tree_ent(self):
        self._tree_data = []
        mh = self._get_mh()
        for k in self._last_mh_ent:
            # ent: MyHeard
            ent = k
            route = ent.route
            dx_alarm = mh.is_dx_alarm_f_call(ent.own_call)

            self._tree_data.append(
                ((
                     f"{conv_time_DE_str(ent.last_seen).split(' ')[1]}",
                     f'{ent.own_call}',
                     f'{ent.distance}',
                     f'{ent.port}',
                     f'{ent.pac_n}',
                     ' '.join(route),
                 ), dx_alarm)
            )

    def _update_side_mh(self):
        mh = self._get_mh()
        mh_ent = list(mh.output_sort_entr(20))
        if mh_ent != self._last_mh_ent:
            self._last_mh_ent = mh_ent
            self._format_tree_ent()
            self._update_tree()

    def reset_dx_alarm(self):
        mh = self._get_mh()
        mh_ent = list(mh.output_sort_entr(20))
        self._last_mh_ent = mh_ent
        self._format_tree_ent()
        self._update_tree()

    ############################################################
    # Tracer
    def _update_side_trace(self):
        self._format_trace_tree_data()
        # self._update_trace_tree()

    def _format_trace_tree_data(self):
        port_handler = self._root_class.get_PH_mainGUI()
        traces: dict = dict(port_handler.get_aprs_ais().tracer_traces_get())
        if self._trace_tree_data_old != len(str(traces)):
            self._trace_tree_data_old = len(str(traces))
            self._trace_tree_data = []
            for k in traces.keys():
                pack: dict = traces[k][-1]
                rx_time = pack.get('rx_time', datetime.now())
                delta = datetime.now() - rx_time
                if not delta.days:
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
            self._trace_tree.insert('', 'end', values=ret_ent)

    def on_ch_stat_change(self, event=None):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except TclError:
            return False
        else:
            if ind != 0:
                return False
        ret = False

        conn = self._root_class.get_conn()
        if conn:
            if self._ch_is_disc:
                self._ch_is_disc = False
                self._max_frame.configure(state='normal')
                self._pac_len.configure(state='normal')
                self._rnr.configure(state='normal')
                self._cliRemote.configure(state='normal')
                self._link_holder.configure(state='normal')
                self._t2_auto.configure(state='normal')

            self._max_frame_var.set(str(conn.parm_MaxFrame))
            self._pac_len_var.set(conn.parm_PacLen)
            self._rnr_var.set(conn.is_RNR)
            self._root_class.link_holder_var.set(conn.link_holder_on)
            self._cliRemote_var.set(conn.cli_remote)    # TODO CLI permissions
            self._tx_buff_var.set('TX-Buffer: ' + get_kb_str_fm_bytes(len(conn.tx_buf_rawData)))
            self._t2_var.set(str(conn.get_port_cfg().get('parm_T2', 500)))
            self._t2_auto_var.set(conn.get_port_cfg().get('parm_T2_auto', True))
            if self._t2_auto_var.get():
                self._t2.configure(state='disabled')
            else:
                self._t2.configure(state='normal')
            ret = True
        else:
            if not self._ch_is_disc:
                self._ch_is_disc = True
                self._max_frame.configure(state='disabled')
                self._pac_len.configure(state='disabled')
                self._rnr_var.set(False)
                # self.rnr.deselect()
                self._rnr.configure(state='disabled')
                self._t2_auto_var.set(False)
                # self.t2_auto.deselect()
                self._t2_auto.configure(state='disabled')
                self._t2.configure(state='disabled')
                self._root_class.link_holder_var.set(False)
                self._link_holder.configure(state='disabled')
                self._cliRemote.configure(state='disabled')
                self._tx_buff_var.set('TX-Buffer: --- kb')
                self._tx_count_var.set('TX: --- kb')
                self._rx_count_var.set('RX: --- kb')
                ret = True

        if self._t2speech_var.get() != self._root_class.get_ch_var().t2speech:
            self._t2speech_var.set(self._root_class.get_ch_var().t2speech)
            ret = True
        return ret
        # self._update_ch_echo()

    def _set_max_frame(self):
        conn = self._root_class.get_conn()
        if conn is not None:
            conn.parm_MaxFrame = int(self._max_frame_var.get())

    def _set_pac_len(self, event):
        conn = self._root_class.get_conn()
        if conn is not None:
            conn.parm_PacLen = min(max(self._pac_len_var.get(), 1), 256)
            conn.calc_irtt()
            self._t2_var.set(str(conn.get_port_cfg().get('parm_T2', 500)))

    def _chk_t2speech(self):
        self._root_class.get_ch_var().t2speech = bool(self._t2speech_var.get())

    def _chk_autoscroll(self):
        self._root_class.get_ch_var().autoscroll = bool(self._autoscroll_var.get())
        if bool(self._autoscroll_var.get()):
            self._root_class.see_end_qso_win()

    #def _open_tracer(self):
    #    self._main_win.open_be_tracer_win()
    """
    def _delete_tracer(self):
        pass
    """

    def _open_mh(self):
        self._root_class.open_MH_win()

    def _open_PortStat(self):
        self._root_class.open_window('PortStat')

    def _disco_all(self):
        if messagebox.askokcancel(title=self._getTabStr('disconnect_all'),
                                  message=self._getTabStr('disconnect_all_ask'), parent=self._root_class.main_win):
            port_handler = self._root_class.get_PH_mainGUI()
            port_handler.disco_all_Conn()

    def get_tab_index(self):
        try:
            return self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return None

    def set_tab_index(self, tab_id):
        if tab_id is None:
            return
        try:
            self._tabControl.select(tab_id)
        except tk.TclError:
            return

    def _get_mh(self):
        try:
            port_handler = self._root_class.get_PH_mainGUI()
            return port_handler.get_MH()
        except Exception as ex:
            logger.error(ex)
            return None