import tkinter as tk
from datetime import datetime
from tkinter import ttk, Checkbutton, TclError, messagebox

from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25dec_enc import PIDByte
from cfg.constant import CFG_TR_DX_ALARM_BG_CLR, ENCODINGS
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
from fnc.os_fnc import is_linux
from fnc.str_fnc import conv_time_DE_str, get_time_delta, get_kb_str_fm_bytes
from sound.popt_sound import SOUND


class SideTabbedFrame:  # TODO
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
        # _tab_side_frame.grid(row=3, column=0, columnspan=6, pady=10, sticky="nsew")
        _tab_side_frame.pack(fill=tk.X, expand=True, pady=5)
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
        tab_connects = tk.Frame(self._tabControl)
        tab2_mh = tk.Frame(self._tabControl)
        tab4_settings = ttk.Frame(self._tabControl)
        # self.tab5_ch_links = ttk.Frame(self._tabControl)  # TODO
        tab6_monitor = ttk.Frame(self._tabControl)
        tab7_tracer = ttk.Frame(self._tabControl)

        self._tabControl.add(tab1_kanal, text='Kanal')
        # tab3 = ttk.Frame(self._tabControl)                         # TODO
        # self._tabControl.add(tab3, text='Ports')                   # TODO
        self._tabControl.add(tab4_settings, text='Global')
        self._tabControl.add(tab_connects, text='Connects')
        self._tabControl.add(tab6_monitor, text='Monitor')
        self._tabControl.add(tab2_mh, text='MH')
        self._tabControl.add(tab7_tracer, text='Tracer')

        # self._tabControl.add(self.tab5_ch_links, text='CH-Echo')   # TODO
        self._tabControl.pack(expand=1, fill="both")
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
        x = 290
        y = 20
        self._conn_durration_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._conn_durration_var).place(x=x, y=y)
        self._conn_durration_var.set('--:--:--')
        #### conn_durration_var
        # TX Buffer
        x = 290
        y = 45
        self._tx_buff_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._tx_buff_var).place(x=x, y=y)
        self._tx_buff_var.set('')
        # TX Gesamt
        x = 290
        y = 70
        self._tx_count_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._tx_count_var).place(x=x, y=y)
        self._tx_count_var.set('')
        # RX Gesamt
        x = 290
        y = 95
        self._rx_count_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self._rx_count_var).place(x=x, y=y)
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
        x = 300
        y = 170
        self.ft_progress = tk.ttk.Progressbar(tab1_kanal,
                                              orient=tk.HORIZONTAL,
                                              length=150,
                                              mode='determinate',
                                              )
        self.ft_progress.place(x=x, y=y)
        self.ft_progress.bind('<Button-1>', self._main_win.open_ft_manager)
        self.ft_progress['value'] = 0
        self.ft_progress_var = tk.StringVar(tab1_kanal)
        self.ft_size_var = tk.StringVar(tab1_kanal)
        self.ft_duration_var = tk.StringVar(tab1_kanal)
        self.ft_bps_var = tk.StringVar(tab1_kanal)
        self.ft_next_tx_var = tk.StringVar(tab1_kanal)
        tk.Label(tab1_kanal, textvariable=self.ft_progress_var).place(x=x + 160, y=y)
        tk.Label(tab1_kanal, textvariable=self.ft_size_var).place(x=x, y=y + 25)
        tk.Label(tab1_kanal, textvariable=self.ft_duration_var).place(x=x, y=y + 50)
        tk.Label(tab1_kanal, textvariable=self.ft_bps_var).place(x=x, y=y + 75)
        tk.Label(tab1_kanal, textvariable=self.ft_next_tx_var).place(x=x + 160, y=y + 75)
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
                  text="Statistik",
                  command=self._open_PortStat
                  ).pack(side=tk.LEFT, padx=50)

        #############################################################################
        # Global Settings ################################
        # Global Sound
        Checkbutton(tab4_settings,
                    text="Sound",
                    variable=self._main_win.setting_sound,
                    command=self._chk_sound
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
        auto_tracer_state = {
            True: 'disabled',
            False: 'normal'
        }.get(self._main_win.get_tracer(), 'disabled')
        self._autotracer_chk_btn = Checkbutton(tab4_settings,
                                               text="Auto-Tracer",
                                               variable=self._main_win.setting_auto_tracer,
                                               command=self._chk_auto_tracer,
                                               state=auto_tracer_state
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
        self.to_add_var = tk.StringVar(tab6_monitor)
        tk.Label(tab6_monitor, text=f"{STR_TABLE['to'][self._lang]}:").place(x=x, y=y)
        tk.Entry(tab6_monitor, textvariable=self.to_add_var).place(x=x + 40, y=y)

        # CMD/RPT
        x = 10
        y = 80
        self.cmd_var = tk.BooleanVar(tab6_monitor)
        tk.Checkbutton(tab6_monitor,
                       variable=self.cmd_var,
                       text='CMD/RPT').place(x=x, y=y)

        # Poll
        x = 10
        y = 105
        self.poll_var = tk.BooleanVar(tab6_monitor)
        tk.Checkbutton(tab6_monitor,
                       variable=self.poll_var,
                       text='Poll').place(x=x, y=y)

        # Port
        x = 40
        y = 140
        tk.Label(tab6_monitor, text=f"{STR_TABLE['port'][self._lang]}:").place(x=x, y=y)
        self.mon_port_var = tk.StringVar(tab6_monitor)
        self.mon_port_var.set('0')
        vals = ['0']
        if PORT_HANDLER.get_all_ports().keys():
            vals = [str(x) for x in list(PORT_HANDLER.get_all_ports().keys())]
        mon_port_ent = tk.ttk.Combobox(tab6_monitor,
                                       width=4,
                                       textvariable=self.mon_port_var,
                                       values=vals,
                                       )
        mon_port_ent.place(x=x + 50, y=y)
        mon_port_ent.bind("<<ComboboxSelected>>", self._chk_mon_port)
        # Calls
        x = 40
        y = 175
        self.mon_call_var = tk.StringVar(tab6_monitor)
        # vals = []
        # if self.main_win.ax25_port_handler.ax25_ports.keys():
        #     _vals = [str(x) for x in list(self.main_win.ax25_port_handler.ax25_ports.keys())]
        self.mon_call_ent = tk.ttk.Combobox(tab6_monitor,
                                            width=9,
                                            textvariable=self.mon_call_var,
                                            values=[],
                                            )
        self.mon_call_ent.place(x=x, y=y)

        # Auto Scrolling
        x = 10
        y = 210
        self.mon_scroll_var = tk.BooleanVar(tab6_monitor)
        tk.Checkbutton(tab6_monitor,
                       variable=self.mon_scroll_var,
                       text=STR_TABLE['scrolling'][self._lang]).place(x=x, y=y)

        # Monitor APRS Decoding Output
        x = 10
        y = 235
        self.mon_aprs_var = tk.BooleanVar(tab6_monitor)
        self.mon_aprs_var.set(True)
        tk.Checkbutton(tab6_monitor,
                       variable=self.mon_aprs_var,
                       text='APRS-Decoding').place(x=x, y=y)

        # Monitor Decoding
        tk.Label(tab6_monitor, text='Decoding:').place(x=40, y=265)
        # self.mon_decoding_var.set(True)
        dec_val = ['Auto'] + list(ENCODINGS)
        tk.ttk.Combobox(tab6_monitor,
                        width=9,
                        textvariable=self._main_win.setting_mon_encoding,
                        values=dec_val,
                        ).place(x=135, y=265)

        # PID

        self.mon_pid_var = tk.StringVar(tab6_monitor)
        tk.Label(tab6_monitor, text='PID:').place(x=10, y=45)
        pid = PIDByte()  # TODO CONST PIDByte().pac_types
        pac_types = dict(pid.pac_types)
        vals = []
        for x in list(pac_types.keys()):
            pid.pac_types[int(x)]()
            vals.append(f"{str(hex(int(x))).upper()}>{pid.flag}")
        tk.ttk.Combobox(tab6_monitor,
                        width=20,
                        values=vals,
                        textvariable=self.mon_pid_var).place(x=50, y=45)
        self.mon_pid_var.set(vals[0])
        # self.pac_len.bind("<<ComboboxSelected>>", self.set_pac_len)
        # Monitor RX-Filter Ports
        self._mon_port_on_vars = {}
        all_ports = PORT_HANDLER.ax25_ports
        for port_id in all_ports:
            self._mon_port_on_vars[port_id] = tk.BooleanVar(tab6_monitor)
            x = 170
            y = 80 + (25 * port_id)
            tk.Checkbutton(tab6_monitor,
                           text=f"Port {port_id}",
                           variable=self._mon_port_on_vars[port_id],
                           command=self._chk_mon_port_filter
                           ).place(x=x, y=y)
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
        #################################
        self._init_connects_tab(tab_connects)
        ##################
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

    def _init_connects_tab(self, root_frame):
        # TREE
        root_frame.rowconfigure(0, minsize=100, weight=1)
        root_frame.rowconfigure(1, minsize=50, weight=0)
        root_frame.columnconfigure(0, minsize=150, weight=1)
        root_frame.columnconfigure(1, minsize=150, weight=1)

        columns = (
            'channel',
            'call',
            'own_call',
            'port',
            'typ',
            'dauer',
        )

        self._connects_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
        self._connects_tree.grid(row=0, column=0, columnspan=2, sticky='nsew')

        self._connects_tree.heading('channel', text='CH')
        self._connects_tree.heading('call', text='To')
        self._connects_tree.heading('own_call', text='Station')
        self._connects_tree.heading('port', text='Port')
        self._connects_tree.heading('typ', text='Typ')
        self._connects_tree.heading('dauer', text='Time')
        self._connects_tree.column("channel", anchor=tk.W, stretch=tk.NO, width=50)
        self._connects_tree.column("call", anchor=tk.W, stretch=tk.NO, width=115)
        self._connects_tree.column("own_call", anchor=tk.CENTER, stretch=tk.NO, width=115)
        self._connects_tree.column("port", anchor=tk.W, stretch=tk.NO, width=61)
        self._connects_tree.column("typ", anchor=tk.W, stretch=tk.NO, width=155)
        self._connects_tree.column("dauer", anchor=tk.W, stretch=tk.YES, width=110)
        # self._connects_tree.tag_configure("dx_alarm", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')

        self._connects_tree_data = []
        # self._last_mh_ent = []
        # self._update_side_mh()
        self._connects_tree.bind('<<TreeviewSelect>>', self._connects_entry_selected)

        btn_frame = tk.Frame(root_frame)
        btn_frame.grid(row=1, column=0)
        tk.Button(btn_frame,
                  text=STR_TABLE['disconnect_all'][self._lang],
                  command=self._disoc_all
                  ).pack(side=tk.LEFT, padx=50)
        """

        tk.Button(btn_frame,
                  text="Statistik",
                  command=self._open_PortStat
                  ).pack(side=tk.LEFT, padx=50)
        """

    def _set_rx_echo(self, event=None):
        PORT_HANDLER.rx_echo_on = bool(self._main_win.setting_rx_echo.get())
        self._main_win.set_rxEcho_icon(self._main_win.setting_rx_echo.get())

    def set_auto_tracer_state(self):
        bool_state = self._main_win.get_tracer() or not self._main_win.get_dx_alarm()
        state = {
            True: 'disabled',
            False: 'normal'
        }.get(bool_state, 'disabled')
        self._autotracer_chk_btn.configure(state=state)

    def _chk_sound(self):
        if self._main_win.setting_sound.get():
            SOUND.master_sound_on = True
        else:
            SOUND.master_sound_on = False

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
        self._main_win.set_tracer_icon()

    def _chk_beacon(self):
        POPT_CFG.set_guiPARM_main({
            'gui_cfg_beacon': bool(self._main_win.setting_bake.get())
        })
        self._main_win.set_Beacon_icon(self._main_win.setting_bake.get())

    def _chk_auto_tracer(self):
        self._main_win.set_auto_tracer()
        self._main_win.set_tracer_icon()

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
            SOUND.master_sprech_on = True
            self.t2speech.configure(state='normal')
        else:
            SOUND.master_sprech_on = False
            self.t2speech.configure(state='disabled')
        self._main_win.set_var_to_all_ch_param()

    def _chk_mon_port(self, event=None):
        port_id = int(self.mon_port_var.get())
        vals = PORT_HANDLER.get_stat_calls_fm_port(port_id)
        if vals:
            self.mon_call_var.set(vals[0])
        self.mon_call_ent.configure(values=vals)

    def _chk_mon_port_filter(self):
        all_ports = PORT_HANDLER.ax25_ports
        for port_id in all_ports:
            all_ports[port_id].monitor_out = self._mon_port_on_vars[port_id].get()

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
                port = int(port.split('-')[0])

            if vias:
                call = f'{call} {vias}'
            if not self._main_win.new_conn_win:
                self._main_win.open_new_conn_win()
            if self._main_win.new_conn_win:
                self._main_win.new_conn_win.preset_ent(call, port)

    def _connects_entry_selected(self, event=None):
        for selected_item in self._connects_tree.selection():
            item = self._connects_tree.item(selected_item)
            record = item['values']
            # show a message
            ch_id = int(record[0])
            self._main_win.switch_channel(ch_id)

    def _trace_entry_selected(self, event=None):
        pass
        # self._main_win.open_be_tracer_win()

    @staticmethod
    def _tracer_send():
        PORT_HANDLER.get_aprs_ais().tracer_sendit()

    # MH

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
    # Connects
    def _update_connects(self):
        connects = PORT_HANDLER.get_all_connections(with_null=True)
        for i in self._connects_tree.get_children():
            self._connects_tree.delete(i)
        ch_list = list(connects.keys())
        ch_list.sort()
        for ch_id in ch_list:
            conn = connects[ch_id]
            timer = datetime.now() - conn.time_start
            timer = str(timer).split('.')[0]
            typ = conn.cli_type
            if conn.is_link:
                if hasattr(conn.LINK_Connection, 'to_call_str'):
                    typ = f'Link {conn.LINK_Connection.to_call_str}'
                else:
                    typ = 'Link'
            if conn.pipe:
                typ = 'Pipe'
            ent = [
                conn.ch_index,
                conn.to_call_str,
                conn.my_call_str,
                conn.port_id,
                typ,
                timer,
            ]
            self._connects_tree.insert('', tk.END, values=ent, )

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
                     f'{ent.port}',
                     f'{ent.pac_n}',
                     ' '.join(route),
                 ), dx_alarm)
            )

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

    def _disoc_all(self):
        if messagebox.askokcancel(title=STR_TABLE.get('disconnect_all', ('', '', ''))[self._lang],
                                  message=STR_TABLE.get('disconnect_all_ask', ('', '', ''))[self._lang]):
            PORT_HANDLER.disco_all_Conn()

