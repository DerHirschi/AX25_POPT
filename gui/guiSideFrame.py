import tkinter as tk
from tkinter import ttk, Checkbutton

import main


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

        tab1_connection = ttk.Frame(self.tabControl)
        self.tab2_mh = ttk.Frame(self.tabControl)
        tab3 = ttk.Frame(self.tabControl)
        self.tab4_settings = ttk.Frame(self.tabControl)
        self.tab5_ch_links = ttk.Frame(self.tabControl)

        self.tabControl.add(tab1_connection, text='Station')
        self.tabControl.add(self.tab2_mh, text='MH')
        self.tabControl.add(tab3, text='Ports')
        self.tabControl.add(self.tab4_settings, text='Settings')
        self.tabControl.add(self.tab5_ch_links, text='CH-Echo')
        self.tabControl.pack(expand=0, fill="both")
        self.tabControl.select(self.tab2_mh)
        parm_y = 20
        m_f_label = tk.Label(tab1_connection, text='Max Pac:')
        self.max_frame_var = tk.StringVar()
        self.max_frame_var.set('1')
        self.max_frame = tk.Spinbox(tab1_connection,
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
        p_l_label = tk.Label(tab1_connection, text='Pac Len:')
        self.pac_len_var = tk.IntVar(tab1_connection)
        self.pac_len_var.set(128)
        self.pac_len = tk.ttk.Combobox(tab1_connection,
                                       width=4,
                                       textvariable=self.pac_len_var,
                                       values=list(range(1, 257)),
                                       state='disabled')
        self.pac_len.bind("<<ComboboxSelected>>", self.set_pac_len)
        p_l_label.place(x=10, y=parm_y)
        self.pac_len.place(x=10 + 80, y=parm_y)
        # RNR Checkbutton
        parm_y = 90
        self.rnr_var = tk.BooleanVar(tab1_connection)

        self.rnr = tk.Checkbutton(tab1_connection,
                                  text='RNR',
                                  variable=self.rnr_var,
                                  command=self.chk_rnr)
        self.rnr.place(x=10 , y=parm_y)
        # MH ##########################
        self.tab2_mh.columnconfigure(0, minsize=85, weight=10)
        self.tab2_mh.columnconfigure(1, minsize=100, weight=9)
        self.tab2_mh.columnconfigure(2, minsize=50, weight=8)
        self.tab2_mh.columnconfigure(3, minsize=50, weight=8)
        self.tab2_mh.columnconfigure(4, minsize=50, weight=9)
        tk.Label(self.tab2_mh, text="Zeit", width=85).grid(row=0, column=0)
        tk.Label(self.tab2_mh, text="Call", width=100).grid(row=0, column=1)
        tk.Label(self.tab2_mh, text="PACK", width=50).grid(row=0, column=2)
        tk.Label(self.tab2_mh, text="REJ", width=50).grid(row=0, column=3)
        tk.Label(self.tab2_mh, text="Route", width=50).grid(row=0, column=4)
        self.side_mh: {int: [tk.Entry, tk.Entry, tk.Entry, tk.Entry, tk.Entry]} = {}
        for row in range(9):
            a = tk.Entry(self.tab2_mh, width=85)
            b = tk.Entry(self.tab2_mh, width=80)
            # b = tk.Button(self.tab2_mh, width=100)
            c = tk.Entry(self.tab2_mh, width=20)
            d = tk.Entry(self.tab2_mh, width=20)
            e = tk.Entry(self.tab2_mh, width=100)
            a.grid(row=row + 1, column=0)
            b.grid(row=row + 1, column=1)
            c.grid(row=row + 1, column=2)
            d.grid(row=row + 1, column=3)
            e.grid(row=row + 1, column=4)
            self.side_mh[row + 1] = [a, b, c, d, e]
        self.update_side_mh()

        # Settings ##########################
        # Global Sound
        self.sound_on = tk.IntVar()
        Checkbutton(self.tab4_settings,
                    text="Sound",
                    variable=self.sound_on,
                    ).place(x=10, y=10)
        self.sound_on.set(1)
        # Global Sound
        self.bake_on = tk.BooleanVar()
        Checkbutton(self.tab4_settings,
                    text="Baken",
                    variable=self.bake_on,
                    ).place(x=10, y=35)
        self.bake_on.set(True)
        # RX ECHO
        self.rx_echo_on = tk.BooleanVar()
        _chk_btn = Checkbutton(self.tab4_settings,
                    text="RX-Echo",
                    variable=self.rx_echo_on,
                    )
        _chk_btn.place(x=10, y=60)

        self.bake_on.set(False)
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


    def tester(self, event):
        print("TEST")

    def chk_rnr(self):
        conn = self.main_win.get_conn()
        if conn:
            if self.rnr_var.get():
                conn.set_RNR()
            else:
                conn.unset_RNR()

    def tasker(self):
        self.update_side_mh()
        self.update_ch_echo()

    def update_side_mh(self):
        mh_ent = self.mh.output_sort_entr(8)
        c = 1
        for el in mh_ent:
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
            c += 1

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
        else:
            self.max_frame.configure(state='disabled')
            self.pac_len.configure(state='disabled')
            self.rnr_var.set(False)
            self.rnr.deselect()
            self.rnr.configure(state='disabled')

        self.update_ch_echo()

    def set_max_frame(self):
        conn = self.main_win.get_conn()
        if conn:
            conn.parm_MaxFrame = int(self.max_frame_var.get())

    def set_pac_len(self, event):
        conn = self.main_win.get_conn()
        if conn:
            conn.parm_PacLen = min(max(self.pac_len_var.get(), 1), 256)
