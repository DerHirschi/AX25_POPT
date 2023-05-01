import sys
import tkinter
import tkinter as tk
from tkinter import ttk, Checkbutton

from fnc.str_fnc import get_kb_str_fm_bytes
from string_tab import STR_TABLE
from ax25.ax25dec_enc import PIDByte
from fnc.os_fnc import is_linux


# import main


class SideTabbedFrame:
    def __init__(self, main_cl):
        self.main_win = main_cl
        self.lang = self.main_win.language
        self.mh = main_cl.mh
        self.style = self.main_win.style
        self.ch_index = self.main_win.channel_index
        self.all_connections = self.main_win.ax25_port_handler.all_connections
        self.side_btn_frame_top = self.main_win.side_btn_frame_top
        self.tab_side_frame = tk.Frame(
            self.side_btn_frame_top,
            # width=300,
            height=400
        )
        self.tab_side_frame.grid(row=4, column=0, columnspan=6, pady=10, sticky="nsew")
        self.tabControl = ttk.Notebook(
            self.tab_side_frame,
            height=300,
            # width=500
        )

        tab1_kanal = ttk.Frame(self.tabControl)
        # self.tab1_1_RTT = ttk.Frame(self.tabControl)
        self.tab2_mh = tk.Frame(self.tabControl)
        # self.tab2_mh.bind("<Button-1>", self.reset_dx_alarm)
        self.tab2_mh_def_bg_clr = self.tab2_mh.cget('bg')
        self.tab4_settings = ttk.Frame(self.tabControl)
        self.tab5_ch_links = ttk.Frame(self.tabControl)  # TODO
        self.tab6_monitor = ttk.Frame(self.tabControl)

        self.tabControl.add(tab1_kanal, text='Kanal')
        self.tabControl.add(self.tab2_mh, text='MH')
        # tab3 = ttk.Frame(self.tabControl)                         # TODO
        # self.tabControl.add(tab3, text='Ports')                   # TODO
        self.tabControl.add(self.tab4_settings, text='Global')
        self.tabControl.add(self.tab6_monitor, text='Monitor')

        # self.tabControl.add(self.tab5_ch_links, text='CH-Echo')   # TODO
        self.tabControl.pack(expand=0, fill="both")
        self.tabControl.select(self.tab2_mh)
        ################################################
        # Kanal
        parm_y = 20
        m_f_label = tk.Label(tab1_kanal, text='Max Pac:')
        self.max_frame_var = tk.StringVar()
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
        self.t2.bind("<<ComboboxSelected>>", self.set_t2)
        _label.place(x=10, y=parm_y)
        self.t2.place(x=50, y=parm_y)

        self.t2_auto_var = tk.BooleanVar(tab1_kanal)
        self.t2_auto = tk.Checkbutton(tab1_kanal,
                                      text='T2-Auto',
                                      variable=self.t2_auto_var,
                                      state='disabled',
                                      command=self.chk_t2auto
                                      )
        self.t2_auto.place(x=10, y=parm_y + 35)

        # RNR Checkbutton
        parm_y = 150
        self.rnr_var = tk.BooleanVar(tab1_kanal)

        self.rnr = tk.Checkbutton(tab1_kanal,
                                  text='RNR',
                                  variable=self.rnr_var,
                                  command=self.chk_rnr)
        self.rnr.place(x=10, y=parm_y)
        # Sprech
        parm_y = 200
        self.t2speech_var = tk.BooleanVar(tab1_kanal)

        self.t2speech = tk.Checkbutton(tab1_kanal,
                                       text='Sprachausgabe',
                                       variable=self.t2speech_var,
                                       command=self.chk_t2speech)
        self.t2speech.place(x=10, y=parm_y)
        self.t2speech_var.set(self.main_win.get_ch_param().t2speech)
        # Autoscroll
        parm_y = 225
        self.autoscroll_var = tk.BooleanVar(tab1_kanal)

        self.autoscroll = tk.Checkbutton(tab1_kanal,
                                         text='Autoscroll',
                                         variable=self.autoscroll_var,
                                         command=self.chk_autoscroll
                                         )
        self.autoscroll.place(x=10, y=parm_y)
        self.autoscroll_var.set(self.main_win.get_ch_param().autoscroll)

        # Link Holder
        parm_y = 175
        self.link_holder_var = tk.BooleanVar(tab1_kanal)
        self.link_holder = tk.Checkbutton(tab1_kanal,
                                          text='Linkhalter',
                                          variable=self.link_holder_var,
                                          command=self.chk_link_holder
                                          )
        self.link_holder.place(x=10, y=parm_y)

        clear_ch_data_btn = tk.Button(tab1_kanal,
                                      text='Säubern',
                                      command=self.main_win.clear_channel_data
                                      )
        clear_ch_data_btn.place(x=140, y=135)

        link_holder_settings_btn = tk.Button(tab1_kanal,
                                             text='Linkhalter',
                                             command=self.main_win.open_linkholder_settings_win
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
        # Progress bar
        # progress = tk.ttk.Progressbar(tab1_kanal, orient=tk.HORIZONTAL, length=150, mode='determinate')
        # progress.place(x=300, y=30)
        # progress['value'] = 60
        # TX Buffer
        _x = 290
        _y = 20
        self.tx_buff_var = tk.StringVar(tab1_kanal)
        self.tx_buff_lable = tk.Label(tab1_kanal, textvariable=self.tx_buff_var)
        self.tx_buff_var.set('')
        self.tx_buff_lable.place(x=_x, y=_y)
        # TX Gesamt
        _x = 290
        _y = 45
        self.tx_count_var = tk.StringVar(tab1_kanal)
        self.tx_count_lable = tk.Label(tab1_kanal, textvariable=self.tx_count_var)
        self.tx_count_var.set('')
        self.tx_count_lable.place(x=_x, y=_y)
        # RX Gesamt
        _x = 290
        _y = 70
        self.rx_count_var = tk.StringVar(tab1_kanal)
        self.rx_count_lable = tk.Label(tab1_kanal, textvariable=self.rx_count_var)
        self.rx_count_var.set('')
        self.rx_count_lable.place(x=_x, y=_y)

        ######################
        ttk.Separator(tab1_kanal, orient=tk.HORIZONTAL).place(x=281, y=110, relheight=0.6, relwidth=0.9)
        #####################
        # Status /Pipe/Link/File-RX/File-TX
        self.status_label_var = tk.StringVar(tab1_kanal)
        self.status_label = tk.Label(tab1_kanal, fg='red', textvariable=self.status_label_var)
        font = self.status_label.cget('font')
        self.status_label.configure(font=(font[0], 12))
        self.status_label.place(x=290, y=120)

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
        self.update_side_mh()
        self.tree.bind('<<TreeviewSelect>>', self.entry_selected)

        # Settings ##########################
        # Global Sound
        self.sound_on = tk.BooleanVar()
        Checkbutton(self.tab4_settings,
                    text="Sound",
                    variable=self.sound_on,
                    ).place(x=10, y=10)
        # self.sound_on.set(True)
        # Global Sprech
        self.sprech_on = tk.BooleanVar()
        sprech_btn = Checkbutton(self.tab4_settings,
                                 text="Sprachausgabe",
                                 variable=self.sprech_on,
                                 command=self.chk_sprech_on
                                 )
        sprech_btn.place(x=10, y=35)
        if is_linux():
            self.sprech_on.set(True)
        else:
            self.sprech_on.set(False)
            sprech_btn.configure(state='disabled')

        # Global Bake
        self.bake_on = tk.BooleanVar()
        Checkbutton(self.tab4_settings,
                    text="Baken",
                    variable=self.bake_on,
                    ).place(x=10, y=60)
        # self.bake_on.set(True)
        # DX Alarm  > dx_alarm_on
        self.dx_alarm_on = tk.BooleanVar()
        _chk_btn = Checkbutton(self.tab4_settings,
                               text="DX-Alarm",
                               variable=self.dx_alarm_on,
                               command=self.chk_dx_alarm,
                               # state='disabled'
                               )
        _chk_btn.place(x=10, y=85)

        # RX ECHO
        self.rx_echo_on = tk.BooleanVar()
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
        tk.Label(self.tab6_monitor, text=f"{STR_TABLE['to'][self.lang]}:").place(x=_x, y=_y)
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
        tk.Label(self.tab6_monitor, text=f"{STR_TABLE['port'][self.lang]}:").place(x=_x, y=_y)
        self.mon_port_var = tk.StringVar(self.tab6_monitor)
        self.mon_port_var.set('0')
        _vals = ['0']
        if self.main_win.ax25_port_handler.ax25_ports.keys():
            _vals = [str(x) for x in list(self.main_win.ax25_port_handler.ax25_ports.keys())]
        self.mon_port_ent = tk.ttk.Combobox(self.tab6_monitor,
                                            width=4,
                                            textvariable=self.mon_port_var,
                                            values=_vals,
                                            )
        self.mon_port_ent.place(x=_x + 50, y=_y)
        self.mon_port_ent.bind("<<ComboboxSelected>>", self.chk_mon_port)
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
                                             text=STR_TABLE['scrolling'][self.lang])
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
        # RX-Filter
        """
        _x = 10
        _y = 105
        self.rx_filter_var = tk.StringVar(self.tab6_monitor)
        tk.Label(self.tab6_monitor, text=f"{STR_TABLE['filter'][self.lang]}:").place(x=_x, y=_y)
        self.rx_filter_ent = tk.Entry(self.tab6_monitor, textvariable=self.rx_filter_var)
        self.rx_filter_ent.place(x=_x + 50, y=_y)
        """

        ##################
        # Tasker
        self.tasker_dict = {
            0: self.update_rtt,
            1: self.update_side_mh,
            # 5: self.update_ch_echo,
        }

        self.chk_mon_port()
        self.update_ch_echo()

    def reset_dx_alarm(self, event=None):
        self.main_win.reset_dx_alarm()
        # self.tab2_mh.configure(bg=self.tab2_mh_def_bg_clr)

    def update_ch_echo(self):
        # TODO AGAIN !!
        _tab = self.tab5_ch_links
        akt_ch_id = self.main_win.channel_index
        _var = tk.BooleanVar(_tab)
        for ch_id in list(self.ch_echo_vars.keys()):
            if ch_id not in list(self.all_connections.keys()):
                self.ch_echo_vars[ch_id][1].destroy()
                del self.ch_echo_vars[ch_id]
        for ch_id in list(self.all_connections.keys()):
            conn = self.all_connections[ch_id]
            if ch_id not in self.ch_echo_vars.keys():
                chk_bt_var = tk.IntVar()
                chk_bt = tk.Checkbutton(_tab,
                                        text=conn.to_call_str,
                                        variable=chk_bt_var,
                                        onvalue=int(ch_id),
                                        offvalue=0,
                                        command=self.chk_ch_echo
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

    def chk_ch_echo(self):
        # self.main_win.channel_index
        for ch_id in list(self.ch_echo_vars.keys()):
            _vars = self.ch_echo_vars[ch_id]
            if ch_id != self.main_win.channel_index:
                if _vars[0].get() and self.ch_echo_vars[self.main_win.channel_index][0].get():
                    self.all_connections[ch_id].ch_echo.append(self.all_connections[self.main_win.channel_index])
                    self.all_connections[self.main_win.channel_index].ch_echo.append(self.all_connections[ch_id])
                else:
                    if self.all_connections[self.main_win.channel_index] in self.all_connections[ch_id].ch_echo:
                        self.all_connections[ch_id].ch_echo.remove(self.all_connections[self.main_win.channel_index])

                    if self.all_connections[ch_id] in self.all_connections[self.main_win.channel_index].ch_echo:
                        self.all_connections[self.main_win.channel_index].ch_echo.remove(self.all_connections[ch_id])

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

    def chk_dx_alarm(self):
        self.main_win.setting_dx_alarm = self.dx_alarm_on.get()

    def chk_rnr(self):
        conn = self.main_win.get_conn()
        if conn:
            if self.rnr_var.get():
                conn.set_RNR()
            else:
                conn.unset_RNR()

    def chk_link_holder(self):
        conn = self.main_win.get_conn()
        if conn:
            if self.link_holder_var.get():
                conn.link_holder_on = True
                conn.link_holder_timer = 0
            else:
                conn.link_holder_on = False

    def chk_t2auto(self):
        conn = self.main_win.get_conn()
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

    def chk_sprech_on(self):
        if self.sprech_on.get():
            self.t2speech.configure(state='normal')
        else:
            self.t2speech.configure(state='disabled')
        self.main_win.set_var_to_all_ch_param()

    def chk_mon_port(self, event=None):
        vals = []
        port_id = int(self.mon_port_var.get())
        if port_id in self.main_win.ax25_port_handler.ax25_ports.keys():
            vals = self.main_win.ax25_port_handler.ax25_ports[port_id].my_stations
        if vals:
            self.mon_call_var.set(vals[0])
        self.mon_call_ent.configure(values=vals)

    def update_mon_port_id(self):
        if self.main_win.ax25_port_handler.ax25_ports.keys():
            _vals = [str(x) for x in list(self.main_win.ax25_port_handler.ax25_ports.keys())]
            self.mon_call_ent.configure(values=_vals)

    def set_t2(self, event):
        conn = self.main_win.get_conn()
        if conn:
            conn.cfg.parm_T2 = min(max(int(self.t2_var.get()), 500), 3000)
            conn.calc_irtt()

    def tasker(self):
        try:    # TODO Need correct prozedur to end the whole shit
            ind = self.tabControl.index(self.tabControl.select())
        except tkinter.TclError:
            pass
        else:
            if ind in self.tasker_dict.keys():
                self.tasker_dict[ind]()

    def entry_selected(self, event):
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
            self.main_win.open_new_conn_win()
            self.main_win.new_conn_win.call_txt_inp.insert(tk.END, call)
            self.main_win.new_conn_win.set_port_index(port)

    def format_tree_ent(self):
        self.tree_data = []
        for k in self.last_mh_ent:
            # ent: MyHeard
            ent = k
            route = ent.route

            self.tree_data.append((
                f"{ent.last_seen.split(' ')[1]}",
                f'{ent.own_call}',
                f'{ent.port_id} {ent.port}',
                f'{ent.pac_n}',
                ' '.join(route),
            ))

    def update_rtt(self):
        best = ''
        worst = ''
        avg = ''
        last = ''
        status_text = ''
        tx_buff = 'TX-Buffer: --- kb'
        tx_count = 'TX: --- kb'
        rx_count = 'RX: --- kb'
        station = self.main_win.get_conn(self.main_win.channel_index)
        if station:
            if station.RTT_Timer.rtt_best == 999.0:
                best = "Best: -1"
            else:
                best = "Best: {:.1f}".format(station.RTT_Timer.rtt_best)
            worst = "Worst: {:.1f}".format(station.RTT_Timer.rtt_worst)
            avg = "AVG: {:.1f}".format(station.RTT_Timer.rtt_average)
            last = "Last: {:.1f}".format(station.RTT_Timer.rtt_last)
            tx_buff = 'TX-Buffer: ' + get_kb_str_fm_bytes(len(station.tx_buf_rawData))
            tx_count = 'TX: ' + get_kb_str_fm_bytes(station.tx_byte_count)
            rx_count = 'RX: ' + get_kb_str_fm_bytes(station.rx_byte_count)
            if station.is_link:
                status_text = 'Link'
            elif station.pipe is not None:
                status_text = 'Pipe'
            elif station.ft_tx_activ is not None:
                status_text = 'Sending File'
        self.status_label_var.set(status_text)
        self.rtt_best.configure(text=best)
        self.rtt_worst.configure(text=worst)
        self.rtt_avg.configure(text=avg)
        self.rtt_last.configure(text=last)
        self.tx_buff_var.set(tx_buff)
        self.tx_count_var.set(tx_count)
        self.rx_count_var.set(rx_count)

    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ret_ent in self.tree_data:
            self.tree.insert('', tk.END, values=ret_ent)

    def update_side_mh(self):
        mh_ent = list(self.mh.output_sort_entr(8))
        if mh_ent != self.last_mh_ent:
            self.last_mh_ent = mh_ent
            self.format_tree_ent()
            self.update_tree()

    def on_ch_btn_stat_change(self):
        conn = self.main_win.get_conn()
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

        self.t2speech_var.set(self.main_win.get_ch_param().t2speech)
        self.update_ch_echo()

    def set_max_frame(self):
        conn = self.main_win.get_conn()
        if conn:
            conn.parm_MaxFrame = int(self.max_frame_var.get())

    def set_pac_len(self, event):
        conn = self.main_win.get_conn()
        if conn:
            conn.parm_PacLen = min(max(self.pac_len_var.get(), 1), 256)
            conn.calc_irtt()
            self.t2_var.set(str(conn.parm_T2 * 1000))

    def chk_t2speech(self):
        self.main_win.get_ch_param().t2speech = bool(self.t2speech_var.get())

    def chk_autoscroll(self):
        self.main_win.get_ch_param().autoscroll = bool(self.autoscroll_var.get())
        if bool(self.autoscroll_var.get()):
            self.main_win.see_end_qso_win()
