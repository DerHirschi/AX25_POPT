import sys
import tkinter as tk
from tkinter import ttk, Checkbutton


# import main


class SideTabbedFrame:
    def __init__(self, main_cl):
        self.main_win = main_cl
        self.mh = main_cl.mh
        self.style = self.main_win.style
        self.ch_index = self.main_win.channel_index
        self.all_connections = self.main_win.ax25_port_handler.all_connections
        self.side_btn_frame_top = self.main_win.side_btn_frame_top
        self.tab_side_frame = tk.Frame(self.side_btn_frame_top, width=300, height=400)
        self.tab_side_frame.grid(row=4, column=0, columnspan=6, pady=10, sticky="nsew")
        self.tabControl = ttk.Notebook(self.tab_side_frame, height=300, width=500)
        # self.tabControl.grid(row=3, column=0, columnspan=5, sticky="nsew")

        tab1_kanal = ttk.Frame(self.tabControl)
        self.tab2_mh = tk.Frame(self.tabControl)
        # self.tab2_mh.bind("<Button-1>", self.reset_dx_alarm)
        self.tab2_mh_def_bg_clr = self.tab2_mh.cget('bg')
        tab3 = ttk.Frame(self.tabControl)
        self.tab4_settings = ttk.Frame(self.tabControl)
        self.tab5_ch_links = ttk.Frame(self.tabControl)

        self.tabControl.add(tab1_kanal, text='Kanal')
        self.tabControl.add(self.tab2_mh, text='MH')
        self.tabControl.add(tab3, text='Ports')
        self.tabControl.add(self.tab4_settings, text='Global')
        self.tabControl.add(self.tab5_ch_links, text='CH-Echo')
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
        self.pac_len = tk.ttk.Combobox(tab1_kanal,
                                       width=4,
                                       textvariable=self.pac_len_var,
                                       values=list(range(1, 257)),
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
        self.tree.column("mh_route",  stretch=tk.YES, width=180)
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)

        self.tree_data = []
        self.last_mh_ent = []
        # self.init_tree_data()
        self.update_side_mh()
        self.tree.bind('<<TreeviewSelect>>', self.entry_selected)

        # Settings ##########################
        # Global Sound
        self.sound_on = tk.BooleanVar()
        Checkbutton(self.tab4_settings,
                    text="Sound",
                    variable=self.sound_on,
                    ).place(x=10, y=10)
        self.sound_on.set(True)
        # Global Sprech
        self.sprech_on = tk.BooleanVar()
        sprech_btn = Checkbutton(self.tab4_settings,
                                 text="Sprachausgabe",
                                 variable=self.sprech_on,
                                 command=self.chk_sprech_on
                                 )
        sprech_btn.place(x=10, y=35)
        if 'linux' in sys.platform:
            self.sprech_on.set(True)
        else:
            self.sprech_on.set(False)
            sprech_btn.configure(state='disabled')

        # Sprech
        parm_y = 175
        self.t2speech_var = tk.BooleanVar(tab1_kanal)

        self.t2speech = tk.Checkbutton(tab1_kanal,
                                       text='Sprachausgabe',
                                       variable=self.t2speech_var,
                                       command=self.chk_t2speech)
        self.t2speech.place(x=10, y=parm_y)
        self.t2speech_var.set(self.main_win.get_ch_param().t2speech)

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
        """
        self.dx_alarm_reset_btn = tk.Button(self.tab4_settings,
                                            text="Reset",
                                            command=lambda: self.reset_dx_alarm()
                                            )
        self.dx_alarm_reset_btn.place(x=150, y=85)
        """
        # RX ECHO
        self.rx_echo_on = tk.BooleanVar()
        _chk_btn = Checkbutton(self.tab4_settings,
                               text="RX-Echo",
                               variable=self.rx_echo_on,
                               )
        _chk_btn.place(x=10, y=115)

        """
        self.sound_on = tk.IntVar()
        Checkbutton(self.tab4_settings,
                    text="Test   ",
                    variable=self.sound_on,
                    ).grid(column=0,
                           row=1
                           )
        """
        ############
        # CH ECHO
        self.chk_btn_default_clr = _chk_btn.cget('bg')
        self.ch_echo_vars = {}
        self.update_ch_echo()
        #self.tabControl.s

    def reset_dx_alarm(self, event=None):
        self.main_win.reset_dx_alarm()
        # self.tab2_mh.configure(bg=self.tab2_mh_def_bg_clr)

    def update_ch_echo(self):
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

    def tester(self, event):
        print("TEST")

    def chk_rnr(self):
        conn = self.main_win.get_conn()
        if conn:
            if self.rnr_var.get():
                conn.set_RNR()
            else:
                conn.unset_RNR()

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

    def set_t2(self, event):
        conn = self.main_win.get_conn()
        if conn:
            conn.cfg.parm_T2 = min(max(int(self.t2_var.get()), 500), 3000)
            conn.calc_irtt()

    def tasker(self):
        if self.tabControl.index(self.tabControl.select()) == 1:
            self.update_side_mh()
        elif self.tabControl.index(self.tabControl.select()) == 4:
            self.update_ch_echo()

    """
    def open_new_conn_win(self, event, call: str):
        print(event)
        mh_ent = self.main_win.mh.mh_get_data_fm_call(call)
        print(call)
        if mh_ent:
            port = mh_ent.port_id
            vias = min(mh_ent.all_routes)
            if vias:
                call = f"{call} {' '.join(vias)}"
                self.main_win.open_new_conn_win()
                self.main_win.new_conn_win.call_txt_inp.insert(tk.END, call)
                self.main_win.new_conn_win.set_port_index(port)
    """

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

    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ret_ent in self.tree_data:
            self.tree.insert('', tk.END, values=ret_ent)

    def update_side_mh(self):
        mh_ent = self.mh.output_sort_entr(8)
        if mh_ent != self.last_mh_ent:
            self.last_mh_ent = list(self.mh.output_sort_entr(8))
            self.format_tree_ent()
            self.update_tree()
            """
            c = 1
            for el in mh_ent:
                self.side_mh[c][0].configure(state='normal')
                self.side_mh[c][1].configure(state='normal')
                self.side_mh[c][2].configure(state='normal')
                self.side_mh[c][3].configure(state='normal')
                self.side_mh[c][4].configure(state='normal')

                self.side_mh[c][0].bind('<Double-Button-1>', lambda event: self.open_new_conn_win(event, str(el.own_call)))
                self.side_mh[c][1].bind('<Double-Button-1>', lambda event: self.open_new_conn_win(event,str(el.own_call)))
                self.side_mh[c][2].bind('<Double-Button-1>', lambda event: self.open_new_conn_win(event,str(el.own_call)))
                self.side_mh[c][3].bind('<Double-Button-1>', lambda event: self.open_new_conn_win(event,str(el.own_call)))
                self.side_mh[c][4].bind('<Double-Button-1>', lambda event: self.open_new_conn_win(event,str(el.own_call)))

                self.side_mh[c][0].delete(0, tk.END)
                self.side_mh[c][0].insert(0, el.last_seen.split(' ')[1])
                self.side_mh[c][1].delete(0, tk.END)
                self.side_mh[c][1].insert(0, el.own_call)
                # self.side_mh[c][1].configure(text=el.own_call)
                self.side_mh[c][2].delete(0, tk.END)
                self.side_mh[c][2].insert(0, el.pac_n)
                self.side_mh[c][3].delete(0, tk.END)
                self.side_mh[c][3].insert(0, el.rej_n)
                self.side_mh[c][4].delete(0, tk.END)
                self.side_mh[c][4].insert(0, el.route)
                self.side_mh[c][0].configure(state='disabled')
                self.side_mh[c][1].configure(state='disabled')
                self.side_mh[c][2].configure(state='disabled')
                self.side_mh[c][3].configure(state='disabled')
                self.side_mh[c][4].configure(state='disabled')
                c += 1
            """

    def on_ch_btn_stat_change(self):
        conn = self.main_win.get_conn()
        if conn:
            self.max_frame.configure(state='normal')
            self.pac_len.configure(state='normal')
            self.max_frame_var.set(str(conn.parm_MaxFrame))
            self.pac_len_var.set(conn.parm_PacLen)
            self.rnr_var.set(conn.is_RNR)
            self.rnr.configure(state='normal')
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
