import gc
import random
import time

import tkinter as tk
from datetime import datetime
from tkinter import ttk, Menu, messagebox
from ax25.ax25Statistics import MyHeard
from cfg.constant import CFG_TR_DX_ALARM_BG_CLR
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import conv_time_DE_str, get_strTab, conv_timestamp_delta
from gui.MapView.tkMapView_override import SafeTkinterMapView
from gui.guiMH.guiAPRS_be_tracer import BeaconTracer
from gui.guiMH.gui_ConnPath_plot import ConnPathsPlot


class MHWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_win    = root_win
        self._getTabStr   = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.title("MyHeard")
        self.style = root_win.style
        self.geometry(f"1100x"
                      f"650+"
                      f"{root_win.main_win.winfo_x()}+"
                      f"{root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close_me)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ###################################
        self._aprs_icon_tab_24      = root_win.get_aprs_icon_tab_24()
        self._conn_typ_icon_tab     = root_win.get_conn_typ_icon_16()
        ###################################
        # Vars
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        self._own_lat, self._own_lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)
        self._current_path           = None
        self._old_conn_hist_len      = 0
        self._old_alarm_his_len      = 0
        self._old_mh_data            = {}
        self._rev_ent                = False
        self._rev_conn_his           = False
        self._tree_data              = []
        self._alarm_tree_data        = []
        self._alarm_ports            = []
        self._markers                = {}  # {call: {'marker': MarkerObj, 'lat': float, 'lon': float}}
        self._paths                  = []  # Liste von Path-Objekten für Verbindungslinien
        self._tab_task_timer         = time.time() + 2
        # MapView Thread Ctrl.
        self._quit                   = False
        self.is_destroyed            = False
        ###################################
        # GUI Vars
        self._port_filter_var           = tk.StringVar(self, value='')
        # self._call_filter_var           = tk.StringVar(self, value='')
        self._alarm_newCall_var         = tk.BooleanVar(self)
        self._alarm_newCall_var         = tk.BooleanVar(self)
        self._alarm_seenSince_var       = tk.StringVar(self)
        self._alarm_distance_var        = tk.StringVar(self)
        self._tracer_duration_var       = tk.StringVar(self)
        ports = list(POPT_CFG.get_port_CFGs().keys())
        for _por_id in ports:
            self._alarm_ports.append(tk.BooleanVar(self))
        self._get_vars()
        # ###################### Filter ######################
        filter_f = ttk.Frame(self)
        filter_f.pack(fill='x', anchor='w')
        ####
        label_f = ttk.Frame(filter_f)
        label_f.pack(side='left', anchor='w', padx=5)
        ttk.Label(label_f, text='Filter: ').pack(side='left', anchor='w')
        #
        port_f = ttk.Frame(filter_f)
        port_f.pack(side='left', anchor='w', padx=20)
        ttk.Label(port_f, text='Port: ').pack(side='left', anchor='w', padx=5)
        opt = ['', ''] + list(POPT_CFG.get_port_CFGs().keys())
        ttk.OptionMenu(port_f,
                       self._port_filter_var,
                       *opt,
                       command=lambda e: self._on_port_filter_select()).pack(side='left', anchor='w')
        #
        #call_f = ttk.Frame(filter_f)
        #call_f.pack(side='left', anchor='w', padx=10)
        #ttk.Label(call_f, text='Call: ').pack(side='left', anchor='w', padx=5)
        #ttk.Entry(call_f, textvariable=self._call_filter_var, width=10).pack(side='left', anchor='w')

        # ###################### Notebook ######################
        self._main_pw = ttk.Panedwindow(self)
        self._main_pw.pack(fill='both', expand=True)

        up_frame  = ttk.Frame(self._main_pw)
        map_frame = ttk.Frame(self._main_pw)
        up_frame.pack(fill='both', expand=True)
        map_frame.pack(fill='both', expand=True)
        self._main_pw.add(up_frame,  weight=0)
        self._main_pw.add(map_frame, weight=1)
        #################
        # Map / Net-Graph
        self._map_pw = ttk.Panedwindow(map_frame, orient='horizontal')
        self._map_pw.pack(fill='both', expand=True)

        map1_frame = ttk.Frame(self._map_pw)
        map2_frame = ttk.Frame(self._map_pw)
        map1_frame.pack(fill='both', expand=True)
        map2_frame.pack(fill='both', expand=True)

        self._map_pw.add(map1_frame, weight=1)
        self._map_pw.add(map2_frame, weight=1)
        # ###################### Upper Frame Notebook ####################
        self._tabclt = ttk.Notebook(up_frame, height=300)
        self._tabclt.pack(fill='both', expand=True)

        mh_frame = ttk.Frame(self._tabclt)
        hi_frame = ttk.Frame(self._tabclt)
        tr_frame = ttk.Frame(self._tabclt)
        co_frame = ttk.Frame(self._tabclt)
        mh_frame.pack(fill='both', expand=True)
        hi_frame.pack(fill='both', expand=True)
        tr_frame.pack(fill='both', expand=True)
        co_frame.pack(fill='both', expand=True)

        self._tabclt.add(mh_frame, text='MH')
        self._tabclt.add(hi_frame, text='DX-Alarm')
        self._tabclt.add(tr_frame, text='APRS-Tracer')
        self._tabclt.add(co_frame, text='Connections')

        # ###################### DX Alarm Settings ######################
        # ALARM
        alarm_frame         = ttk.Frame(hi_frame)
        alarm_tree_frame    = ttk.Frame(hi_frame)
        alarm_frame.pack(     fill='x',    expand=False)
        alarm_tree_frame.pack(fill='both', expand=True)

        alarm_f1 = ttk.Frame(alarm_frame)
        alarm_f2 = ttk.Frame(alarm_frame)
        alarm_f3 = ttk.Frame(alarm_frame)
        alarm_f4 = ttk.Frame(alarm_frame)
        alarm_f1.pack(side='top', padx=30)
        alarm_f2.pack(side='top', fill='x', padx=30)
        alarm_f3.pack(side='top', fill='x', padx=30)
        alarm_f4.pack(side='top', fill='x', padx=30)

        ###########################
        # alarm_f1
        ttk.Label(alarm_f1, text='DX-Alarm Setting').pack()
        # alarm_f2
        a_f1 = ttk.Frame(alarm_f2)
        a_f1.pack(side='left')
        ttk.Label(a_f1, text='Activate ').pack(side='left', )
        ttk.Checkbutton(a_f1,
                        variable=self._root_win.setting_dx_alarm,
                        # command=self._chk_alarm_active
                        ).pack(side='left', )

        # New Call in List Checkbox
        a_f2 = ttk.Frame(alarm_f2)
        a_f2.pack(side='left')
        ttk.Label(a_f2, text='new Call ').pack(side='left', )
        ttk.Checkbutton(a_f2,
                        variable=self._alarm_newCall_var,
                        command=self._set_alarm_newCall
                        ).pack(side='left', )

        # Alarm seen since Days
        a_f3 = ttk.Frame(alarm_f2)
        a_f3.pack(side='left', padx=30)

        ttk.Label(a_f3, text='seen since (Days) (0 = off)').pack(side='left', )
        ttk.Spinbox(a_f3,
                    from_=0,
                    to=365,
                    increment=1,
                    width=4,
                    textvariable=self._alarm_seenSince_var,
                    command=self._set_alarm_last_seen
                    ).pack(side='left', )

        # Alarm Distance
        a_f4 = ttk.Frame(alarm_f2)
        a_f4.pack(side='left', padx=30)

        ttk.Label(a_f4, text='Distance (0 = off)').pack(side='left', )
        ttk.Spinbox(a_f4,
                    from_=0,
                    to=20000,
                    increment=1,
                    width=6,
                    textvariable=self._alarm_distance_var,
                    command=self._set_alarm_distance
                    ).pack(side='left', )

        # ###################### Ports ############################
        lower_frame_ports = ttk.Frame(alarm_f3)
        lower_frame_ports.pack(fill='x')

        frame_13_label = ttk.Frame(lower_frame_ports)
        frame_13_label.pack(side='left')
        ttk.Label(frame_13_label, text='Ports: ').pack(side='left', )
        i = 0
        for _port_id in ports:
            frame = ttk.Frame(lower_frame_ports)
            frame.pack(side='left', padx=7)
            text = f'{_port_id}'
            ttk.Label(frame, text=text, width=3).pack(side='left', padx=1)
            ttk.Checkbutton(frame,
                            variable=self._alarm_ports[i],
                            command=self._set_alarm_ports,
                            ).pack(side='left', padx=1)
            i += 1
        # ###################### Connection History ######################
        # co_frame
        columns = (
            'channel',
            'call',
            'own_call',
            'port',
            'dist',
            'loc',
            'typ',
            'via',
            'dauer',
            'time',
        )

        self._conn_his_tab = ttk.Treeview(co_frame, columns=columns, show='tree headings')

        self._conn_his_tab.heading('channel', text='CH', command=lambda: self._sort_conn_his('channel'))
        self._conn_his_tab.heading('call', text='To', command=lambda: self._sort_conn_his('call'))
        self._conn_his_tab.heading('own_call', text='Station', command=lambda: self._sort_conn_his('own_call'))
        self._conn_his_tab.heading('port', text='Port', command=lambda: self._sort_conn_his('port'))
        self._conn_his_tab.heading('dist', text='km', command=lambda: self._sort_conn_his('dist'))
        self._conn_his_tab.heading('loc', text='Locator', command=lambda: self._sort_conn_his('loc'))
        self._conn_his_tab.heading('typ', text='Typ', command=lambda: self._sort_conn_his('typ'))
        self._conn_his_tab.heading('via', text='VIA', command=lambda: self._sort_conn_his('via'))
        self._conn_his_tab.heading('dauer', text='Duration', command=lambda: self._sort_conn_his('dauer'))
        self._conn_his_tab.heading('time', text='Time', command=lambda: self._sort_conn_his('time'))

        self._conn_his_tab.column("#0", anchor='w', stretch=tk.NO, width=45)
        self._conn_his_tab.column("channel", anchor='center', stretch=tk.NO, width=40)
        self._conn_his_tab.column("call", anchor='w', stretch=tk.NO, width=90)
        self._conn_his_tab.column("own_call", anchor='w', stretch=tk.NO, width=90)
        self._conn_his_tab.column("port", anchor='center', stretch=tk.NO, width=50)
        self._conn_his_tab.column("dist", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("loc", anchor='w', stretch=tk.NO, width=100)
        self._conn_his_tab.column("typ", anchor='w', stretch=tk.NO, width=110)
        self._conn_his_tab.column("via", anchor='w', stretch=tk.YES, width=180)
        self._conn_his_tab.column("dauer", anchor='center', stretch=tk.NO, width=90)
        self._conn_his_tab.column("time", anchor='w', stretch=tk.NO, width=130)

        # self._conn_his_tab.tag_configure("bell", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        # self._connects_tree.bind('<<TreeviewSelect>>', self._connects_entry_selected)
        self._conn_his_tab.pack(fill='both', expand=True)
        # ###################### Auto Tracer ######################
        # Tracer
        auto_tracer_state = {
            True:  'disabled',
            False: 'normal'
        }.get(self._root_win.get_tracer(), 'disabled')
        lower_frame_tracer = ttk.Frame(alarm_f4)
        lower_frame_tracer.pack(fill='x')

        frame_12_label = ttk.Frame(lower_frame_tracer)
        frame_12_label.pack(side='left')
        ttk.Label(frame_12_label, text='Auto APRS-Tracer: ').pack(side='left', )
        ###
        # activ Checkbox
        frame_22_active = ttk.Frame(lower_frame_tracer)
        frame_22_active.pack(side='left')

        ttk.Label(frame_22_active, text='Activate ').pack(side='left')
        ttk.Checkbutton(frame_22_active,
                        variable=self._root_win.setting_auto_tracer,
                        command=self._root_win.set_auto_tracer,
                        state=auto_tracer_state
                        ).pack(side='left')
        # duration
        frame_22_duration = ttk.Frame(lower_frame_tracer)
        frame_22_duration.pack(side='left', padx=30)

        ttk.Label(frame_22_duration, text='Duration (min) ').pack(side='left')
        ttk.Spinbox(frame_22_duration,
                    from_=5,
                    to=1440,
                    increment=5,
                    width=5,
                    textvariable=self._tracer_duration_var,
                    state=auto_tracer_state,
                    command=self._set_auto_tracer,
                    ).pack(side='left')

        # #### DX Alarm TREE
        columns = (
            'mh_call',
            'mh_port',
            'mh_loc',
            'mh_dist',
            'mh_nPackets',
            'mh_route',
            'mh_first_seen',
            'mh_last_seen',
        )
        alarm_tree_f = ttk.Frame(alarm_tree_frame)
        alarm_tree_f.pack(fill='both', expand=True)
        self._alarm_tree = ttk.Treeview(alarm_tree_f, columns=columns, show='headings')
        self._alarm_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(alarm_tree_f, orient='vertical', command=self._alarm_tree.yview)
        self._alarm_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y', expand=False)

        self._alarm_tree.heading('mh_call',       text='Call',          command=lambda: self._sort_entry('call'))
        self._alarm_tree.heading('mh_port',       text='Port',          command=lambda: self._sort_entry('port'))
        self._alarm_tree.heading('mh_loc',        text='LOC',           command=lambda: self._sort_entry('loc'))
        self._alarm_tree.heading('mh_dist',       text='km',            command=lambda: self._sort_entry('dist'))
        self._alarm_tree.heading('mh_nPackets',   text='Packets',       command=lambda: self._sort_entry('pack'))
        self._alarm_tree.heading('mh_route',      text='Route',         command=lambda: self._sort_entry('route'))
        self._alarm_tree.heading('mh_first_seen', text='Erste Paket',   command=lambda: self._sort_entry('first'))
        self._alarm_tree.heading('mh_last_seen',  text='Letzte Paket',  command=lambda: self._sort_entry('last'))
        #self._tree.heading('mh_ip_fail', text='Fail', command=lambda: self._sort_entry('axipfail'))
        self._alarm_tree.column("mh_call",        anchor='w', stretch=tk.NO,  width=90)
        self._alarm_tree.column("mh_port",        anchor='w', stretch=tk.NO,  width=60)
        self._alarm_tree.column("mh_loc",         anchor='w', stretch=tk.NO,  width=80)
        self._alarm_tree.column("mh_dist",        anchor='w', stretch=tk.NO,  width=60)
        self._alarm_tree.column("mh_nPackets",    anchor='w', stretch=tk.NO,  width=80)
        self._alarm_tree.column("mh_route",       anchor='w', stretch=tk.YES, width=180)
        self._alarm_tree.column("mh_first_seen",  anchor='w', stretch=tk.NO,  width=140)
        self._alarm_tree.column("mh_last_seen",   anchor='w', stretch=tk.NO,  width=140)
        #self._tree.tag_configure("dx_alarm", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        #self._tree.bind('<<TreeviewSelect>>', self.entry_selected)

        # ###################### MH-TREE Frame ######################
        # mh_frame
        filter_frame  = ttk.Frame(mh_frame)
        tree_frame    = ttk.Frame(mh_frame)
        filter_frame.pack(fill='x',    expand=False)
        tree_frame.pack(  fill='both', expand=True)


        # #### MH-TREE

        columns = (
            'mh_call',
            'mh_port',
            'mh_loc',
            'mh_dist',
            'mh_nPackets',
            'mh_REJ',
            'mh_route',
            'mh_last_ip',
            'mh_ip_fail',
            'mh_first_seen',
            'mh_last_seen',
        )
        #tree_f = ttk.Frame(tree_frame)
        #tree_f.pack(fill='both', expand=True)
        self._tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self._tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y', expand=False)

        self._tree.heading('mh_call',       text='Call',            command=lambda: self._sort_entry('call'))
        self._tree.heading('mh_port',       text='Port',            command=lambda: self._sort_entry('port'))
        self._tree.heading('mh_loc',        text='LOC',             command=lambda: self._sort_entry('loc'))
        self._tree.heading('mh_dist',       text='km',              command=lambda: self._sort_entry('dist'))
        self._tree.heading('mh_nPackets',   text='Packets',         command=lambda: self._sort_entry('pack'))
        self._tree.heading('mh_REJ',        text='REJs',            command=lambda: self._sort_entry('rej'))
        self._tree.heading('mh_route',      text='Route',           command=lambda: self._sort_entry('route'))
        self._tree.heading('mh_last_ip',    text='AXIP',            command=lambda: self._sort_entry('axip'))
        self._tree.heading('mh_ip_fail',    text='Fail',            command=lambda: self._sort_entry('axipfail'))
        self._tree.heading('mh_first_seen', text='Erste Paket',     command=lambda: self._sort_entry('first'))
        self._tree.heading('mh_last_seen',  text='Letzte Paket',    command=lambda: self._sort_entry('last'))

        self._tree.column("mh_call",        anchor='w', stretch=tk.NO,  width=90)
        self._tree.column("mh_port",        anchor='w', stretch=tk.NO,  width=60)
        self._tree.column("mh_loc",         anchor='w', stretch=tk.NO,  width=80)
        self._tree.column("mh_dist",        anchor='w', stretch=tk.NO,  width=60)
        self._tree.column("mh_nPackets",    anchor='w', stretch=tk.NO,  width=80)
        self._tree.column("mh_REJ",         anchor='w', stretch=tk.NO,  width=55)
        self._tree.column("mh_route",       anchor='w', stretch=tk.YES, width=180)
        self._tree.column("mh_last_ip",     anchor='w', stretch=tk.YES, width=130)
        self._tree.column("mh_ip_fail",     anchor='w', stretch=tk.NO,  width=50)
        self._tree.column("mh_first_seen",  anchor='w', stretch=tk.NO,  width=140)
        self._tree.column("mh_last_seen",   anchor='w', stretch=tk.NO,  width=140)
        self._tree.tag_configure("dx_alarm", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        self._tree.bind('<<TreeviewSelect>>', self.entry_selected)
        # ###################### MH-TREE Frame ######################
        # tr_frame
        self._be_tracer = BeaconTracer(tr_frame, self)
        #############################################################################
        # ###################### MAP ################################################
        # map1_frame
        f1 = ttk.Frame(map2_frame)
        f2 = ttk.Frame(map2_frame)

        f1.pack(padx=5, pady=5, fill='both', expand=True)
        f2.pack(padx=5, fill='x', expand=False)

        # Erstelle das Map-Widget
        self._map_widget = SafeTkinterMapView(root_win=self, master=f1, corner_radius=0)
        self._map_widget.pack(fill="both", expand=True)
        ais_cfg  = POPT_CFG.get_CFG_aprs_ais()
        lat, lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)

        # Setze die anfängliche Position und Zoom-Level (z. B. Europa)
        self._map_widget.set_position(lat, lon)
        self._map_widget.set_zoom(6)
        #############################################################################
        # ###################### M-Graph ##########################################
        # map2_frame
        self._mh_graph = ConnPathsPlot(map1_frame, self)

        ###############################################
        # Bindings für TreeviewSelect hinzufügen (nach Erstellen der Treeviews)
        tracer_tree = self._be_tracer.get_tracer_tree()
        tracer_tree.bind(       '<<TreeviewSelect>>',   lambda e: self._draw_connection(e, tracer_tree))
        self._tree.bind(        '<<TreeviewSelect>>',   lambda e: self._draw_connection(e, self._tree))
        self._alarm_tree.bind(  '<<TreeviewSelect>>',   lambda e: self._draw_connection(e, self._alarm_tree))
        self._conn_his_tab.bind('<<TreeviewSelect>>',   lambda e: self._draw_connection(e, self._conn_his_tab))
        #################################
        self._init_menubar()
        #################################
        # Tasker
        self._tasker_dict = {
            #0: self._update_mh,
            #1: self._update_dx_his,
            3: self._update_conn_his,
        }
        #################################
        self._root_win.mh_window = self
        self._update_mh()
        self._update_dx_his()
        self._update_conn_his()


    ##########################
    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuMH = Menu(menubar, tearoff=False)
        MenuMH.add_command(label=self._getTabStr('delete_mh_history'), command=self._reset_mh_list)
        MenuMH.add_separator()

        MenuMH.add_command(label=self._getTabStr('delete_dx_history'), command=self._reset_dx_history)
        MenuMH.add_separator()

        MenuMH.add_command(label=self._getTabStr('delete_tracer_history'), command=self._reset_tracer_history)

        MenuMH.add_separator()
        MenuMH.add_command(label=self._getTabStr('delete_conn_history'), command=self._reset_conn_history)

        menubar.add_cascade(label='MyHeard', menu=MenuMH, underline=0)

    def _get_vars(self):
        mh = self.get_mh()
        self._alarm_newCall_var.set(bool(mh.parm_new_call_alarm))
        self._alarm_seenSince_var.set(str(mh.parm_lastseen_alarm))
        self._alarm_distance_var.set(str(mh.parm_distance_alarm))
        self._tracer_duration_var.set(str(self._root_win.get_auto_tracer_duration()))
        i = 0
        for var in self._alarm_ports:
            if i in mh.parm_alarm_ports:
                var.set(True)
            else:
                var.set(False)
            i += 1

    ##########################
    def tasker(self):
        if self._quit:
            self._check_threads_and_destroy()
            return True
        ret = False
        if hasattr(self._map_widget, 'tasker'):
            ret = self._map_widget.tasker()

        ret = any((self._tab_tasker(), ret))
        return ret

    def _tab_tasker(self):
        if time.time() < self._tab_task_timer:
            return False
        self._tab_task_timer = time.time() + 2
        try:
            ind = self._tabclt.index(self._tabclt.select())
        except tk.TclError:
            return False
        else:
            if ind in self._tasker_dict.keys():
                self._tasker_dict[ind]()
                return True
        return False

    def _on_port_filter_select(self):
        self._rev_ent = not self._rev_ent
        self._update_mh()
        self._update_dx_his(True)
        self._update_conn_his()

    ##########################
    def _set_alarm_ports(self, event=None):
        i = 0
        mh = self.get_mh()
        for var in self._alarm_ports:
            if var.get():
                if i not in mh.parm_alarm_ports:
                    mh.parm_alarm_ports.append(int(i))
            else:
                if i in mh.parm_alarm_ports:
                    mh.parm_alarm_ports.remove(int(i))
            i += 1

    def _set_alarm_distance(self, event=None):
        var = self._alarm_distance_var.get()
        try:
            var = int(var)
        except ValueError:
            return
        mh = self.get_mh()
        mh.parm_distance_alarm = var

    def _set_alarm_last_seen(self, event=None):
        var = self._alarm_seenSince_var.get()
        try:
            var = int(var)
        except ValueError:
            return
        mh = self.get_mh()
        mh.parm_lastseen_alarm = var

    def _set_alarm_newCall(self, event=None):
        mh = self.get_mh()
        mh.parm_new_call_alarm = bool(self._alarm_newCall_var.get())

    def _set_auto_tracer(self, event=None):
        dur = self._tracer_duration_var.get()
        try:
            dur = int(dur)
        except ValueError:
            return
        self._root_win.set_auto_tracer_duration(dur)

    ##########################
    # Connection History
    def _update_conn_his(self):
        mh = self.get_mh()
        if not hasattr(mh, 'get_conn_hist'):
            return
        conn_history = mh.get_conn_hist()
        if len(conn_history) == self._old_conn_hist_len:
            return
        new_entries = conn_history[self._old_conn_hist_len:]
        for ent in reversed(new_entries):  # Reversed, um neueste zuerst einzufügen
            ent: dict
            port = ent.get('port_id', -1)
            typ  = ent.get('typ', '')
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
                ent.get('ch_id', 0),        # channel
                ent.get('from_call' ,''),   # call (To)
                ent.get('own_call', ''),    # own_call (Station)
                port,     # port
                ent.get('distance', -1),    # Distance
                ent.get('locator', ''),
                typ,  # typ
                ' '.join(ent.get('via', [])),
                duration_str,  # dauer (Time)
                time_str,  # time (Duration)
            )
            if image:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags, image=image)
            else:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags)

        self._old_conn_hist_len = len(conn_history)

    def _sort_conn_his(self, flag: str):
        # Thanks Grok-AI
        # Alle Einträge aus dem Treeview holen
        items = [(self._conn_his_tab.set(k, flag), k) for k in self._conn_his_tab.get_children('')]

        # Sortierfunktion basierend auf Flag definieren
        def sort_key(item):
            value = item[0]
            if flag == 'channel':
                return int(value) if value else 0
            elif flag == 'port':
                return int(value) if value else -1
            elif flag == 'dist':
                return int(value) if value else -1
            elif flag == 'dauer':
                # Dauer als Sekunden umwandeln (z.B. "--:--:--" ignorieren, sonst HH:MM:SS)
                if value == "--:--:--":
                    return 0
                try:
                    h, m, s = map(int, value.split(':'))
                    return h * 3600 + m * 60 + s
                except ValueError:
                    return 0
            elif flag == 'time':
                # Deutsches Format parsen: DD.MM.YYYY HH:MM:SS
                try:
                    return datetime.strptime(value, '%d/%m/%y %H:%M:%S')
                except ValueError:
                    return datetime.min  # Ungültige Zeiten ans Ende sortieren
            else:
                # Für Strings: lexikographisch, leere Strings ans Ende
                return value if value else ''

        # Sortieren
        items.sort(key=sort_key, reverse=self._rev_conn_his)

        # Richtungswechsel für nächsten Klick
        self._rev_conn_his = not self._rev_conn_his

        # Einträge neu einfügen
        for index, (val, k) in enumerate(items):
            self._conn_his_tab.move(k, '', index)

    ##########################
    # DX History
    def _update_dx_his(self, force_update=False):
        self._format_alarm_tree_data(force_update)
        self._update_alarm_tree()
        # self._update_map()

    def _update_alarm_tree(self):
        for i in self._alarm_tree.get_children():
            self._alarm_tree.delete(i)

        for ret_ent in self._alarm_tree_data:
            self._alarm_tree.insert('', 'end', values=ret_ent[0], )

    def _format_alarm_tree_data(self, force_update: bool):
        mh = self.get_mh()
        if not hasattr(mh, 'get_dx_alarm_perma_his') or not hasattr(mh, 'mh_get_data_fm_call'):
            logger.error("Attribute Error: mh.get_dx_alarm_perma_his()")
            return
        dx_alarm_his = mh.get_dx_alarm_perma_his()
        """
          return {
        'ts': now,
        'port_id': port_id,
        'call_str': call_str,
        'via': via,
        'path': path,
        'loc': locator,
        'dist': distance,
        'typ': typ,
        'key': f"{conv_time_for_key(now)}{call_str}",
              """
        his_keys = list(dx_alarm_his.keys())
        if len(his_keys) == self._old_alarm_his_len and not force_update:
            return
        self._old_alarm_his_len = len(his_keys)
        his_keys.reverse()
        self._alarm_tree_data = []
        for k in his_keys:
            ent = dx_alarm_his.get(k, {})
            port = ent.get('port_id', -1)
            if self._port_filter_var.get() != str(port) and self._port_filter_var.get():
                continue
            call   = ent.get('call_str', '')
            mh_ent = mh.mh_get_data_fm_call(call, port)
            mh_ent: MyHeard
            pac_n       = 'n/a'
            first_seen  = 'n/a'
            last_seen   = 'n/a'
            if mh_ent:
                pac_n       = mh_ent.pac_n
                first_seen  = mh_ent.first_seen
                last_seen   = mh_ent.last_seen
            self._alarm_tree_data.append(((
                                        f"{call}",
                                        f"{port}",
                                        f"{ent.get('loc', '')}",
                                        f"{ent.get('dist', 'n/a')}",
                                        f"{pac_n}",
                                        f"{' '.join(ent.get('path', []))}",
                                        f'{conv_time_DE_str(first_seen)}',
                                        f'{conv_time_DE_str(last_seen)}',
                                    ), None))
    ##########################
    def entry_selected(self, event):
        pass
    """
    def entry_selected(self, event):
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[3]
            vias = record[8]
            vias = vias.split(' ')
            vias.reverse()
            vias = ' '.join(vias)
            port = record[2]
            if type(port) is str:
                port = int(port.split(' ')[0])
            if vias:
                call = f'{call} {vias}'
            if not self._root_win.new_conn_win:
                self._root_win.open_new_conn_win()
            if self._root_win.new_conn_win:
                self._root_win.new_conn_win.preset_ent(call, port)
            self._close_me()
    """
    def _update_mh(self):
        self._sort_entry('last')
        if self._tree_data == self._old_mh_data:
            return
        self._old_mh_data = dict(self._tree_data)
        self._update_tree()
        self._update_map()

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)

        for ret_ent in self._tree_data:
            if ret_ent[1]:
                self._tree.insert('', 'end', values=ret_ent[0], tags=('dx_alarm',))
            else:
                self._tree.insert('', 'end', values=ret_ent[0], )

    def _sort_entry(self, flag: str):
        mh = self.get_mh()
        sort_date = mh.get_sort_mh_entry(flag_str=flag, reverse=self._rev_ent)
        if self._rev_ent:
            self._rev_ent = False
        else:
            self._rev_ent = True
        self._format_tree_ent(sort_date)

    def _format_tree_ent(self, mh_list):
        self._tree_data = []
        mh = self.get_mh()

        for k in mh_list:
            ent: MyHeard
            ent = mh_list[k]
            if self._port_filter_var.get() != str(ent.port_id) and self._port_filter_var.get():
                continue
            if ent.axip_add[1]:
                axip_str = '{} - {}'.format(ent.axip_add[0], ent.axip_add[1])
            else:
                axip_str = ''
            dx_alarm = False
            if hasattr(mh, 'is_dx_alarm_f_call'):
                dx_alarm = mh.is_dx_alarm_f_call(ent.own_call)

            self._tree_data.append(((
                                        f'{ent.own_call}',
                                        f'{ent.port_id} {ent.port}',
                                        f'{ent.locator}',
                                        f'{ent.distance}',
                                        f'{ent.pac_n}',
                                        f'{ent.rej_n}',
                                        ' '.join(ent.route),
                                        f'{axip_str}',
                                        f'{ent.axip_fail}',
                                        f'{conv_time_DE_str(ent.first_seen)}',
                                        f'{conv_time_DE_str(ent.last_seen)}',
                                    ), dx_alarm))

    ######################################################
    # MAP
    def _get_station_icon(self, call: str):
        default_icon    = self._aprs_icon_tab_24.get(('\\', 'X'), None)
        ais             = self._get_aprs_ais()
        user_db         = self._get_userDB()
        if not hasattr(ais, 'get_symbol_fm_node_tab'):
            logger.error("not hasattr(ais, 'get_symbol_fm_node_tab')")
            return default_icon
        if not hasattr(user_db, 'get_typ'):
            logger.error("not hasattr(user_db, 'get_typ')")
            return default_icon
        symbol   = ais.get_symbol_fm_node_tab(call) # ('', '')
        stat_typ = user_db.get_typ(call)

        # Beispiel-Implementierung: Zuweisung basierend auf Stationstyp
        icon_map = {
            'BBS':   self._aprs_icon_tab_24.get('/B', default_icon),
            'NODE':  self._aprs_icon_tab_24.get('/r', default_icon),
            'SYSOP': self._aprs_icon_tab_24.get('/y', default_icon)
        }

        aprs_icon = self._aprs_icon_tab_24.get(symbol, default_icon)
        if aprs_icon:
            return aprs_icon
        if stat_typ:
            return icon_map.get(stat_typ, default_icon)
        return default_icon

    def _update_map(self):
        """Aktualisiert die Karte mit Stationen und deren Routen als Verbindungslinien."""
        self._clear_map()  # Vorherige Marker und Pfade löschen
        mh = self.get_mh()
        mh_list = mh.get_sort_mh_entry(flag_str='last', reverse=False)
        #own_lat, own_lon = POPT_CFG.get_CFG_aprs_ais().get('ais_lat', 0.0), POPT_CFG.get_CFG_aprs_ais().get('ais_lon', 0.0)
        user_db = self._get_userDB()
        if not hasattr(user_db, 'get_location'):
            logger.error("not hasattr(user_db, 'get_location')")
            return

        for call, ent in mh_list.items():
            if ent.own_call in self._markers:
                continue
            lat, lon, loc = user_db.get_location(ent.own_call)
            if not lat and not lon:
                continue
            if self._port_filter_var.get() != str(ent.port_id) and self._port_filter_var.get():
                continue
            offset_range = 0.0002  # Ca. 10-11 Meter, anpassen nach Bedarf
            lat += random.uniform(-offset_range, offset_range)
            lon += random.uniform(-offset_range, offset_range)
            icon = self._get_station_icon(ent.own_call)
            # Marker für die Station setzen
            marker = self._map_widget.set_marker(lat, lon, text=ent.own_call, icon=icon)
            self._markers[ent.own_call] = {'marker': marker, 'lat': lat, 'lon': lon}

            # Route zeichnen
            """
            route = ent.route
            if route:
                prev_coords = (own_lat, own_lon)  # Startpunkt ist eigene Position
                for via_call in route:
                    # Locator der Via-Station aus MyHeard-Tabelle holen

                    via_lat, via_lon, via_loc = user_db.get_location(via_call)
                    via_lat += random.uniform(-offset_range, offset_range)
                    via_lon += random.uniform(-offset_range, offset_range)
                    if via_lat or via_lon:
                        icon = self._get_station_icon(via_call)
                        # Marker für die Station setzen
                        if via_call not in self._markers:
                            marker = self._map_widget.set_marker(lat, lon, text=via_call, icon=icon)
                            self._markers[via_call] = {'marker': marker, 'lat': lat, 'lon': lon}

                        # Verbindungslinie zeichnen
                        path = self._map_widget.set_path([prev_coords, (via_lat, via_lon)],
                                                         width=2)
                        self._paths.append(path)
                        prev_coords = (via_lat, via_lon)

                # Linie zur Zielstation

                path = self._map_widget.set_path([prev_coords, (lat, lon)], width=2)
                self._paths.append(path)
            """

    def _clear_map(self):
        """Löscht alle Marker und Pfade von der Karte."""
        for call, data in list(self._markers.items()):
            data['marker'].delete()
            del self._markers[call]
        for path in self._paths:
            path.delete()
        self._paths.clear()

    def _draw_connection(self, event, tree):
        # By Grok-AK
        selected = tree.selection()

        if not selected:
            return

        item = tree.item(selected[0])
        values = item['values']
        if not values:
            return

        # Alten Pfad löschen, falls vorhanden
        if self._current_path:
            self._current_path.delete()
            self._current_path = None
            ais_cfg  = POPT_CFG.get_CFG_aprs_ais()
            lat, lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)
            self._map_widget.set_position(lat, lon)
            self._map_widget.set_zoom(6)

        # Bestimme Indizes je nach Treeview
        if tree in (self._tree, self._alarm_tree):
            call_index = 0  # mh_call
        elif tree == self._conn_his_tab:
            call_index = 1  # call (To)
        elif tree == self._be_tracer.get_tracer_tree():
            call_index = 1  # call (To)
        else:
            return

        call = values[call_index].strip()
        if not call:
            return

        user_db = self._get_userDB()
        if not user_db:
            return

        target_lat, target_lon, target_loc = user_db.get_location(call)
        if not target_lat or not target_lon:
            return  # Position unbekannt

        # Linie zeichnen
        path_coords = [(self._own_lat, self._own_lon), (target_lat, target_lon)]
        self._current_path = self._map_widget.set_path(path_coords, color="blue", width=2)

        # Marker für eigene Position sicherstellen
        if 'Own' not in self._markers:
            #own_icon = self._get_station_icon('')  # Default Icon, da kein Call
            own_marker = self._map_widget.set_marker(self._own_lat, self._own_lon, text="My Station",)
            self._markers['Own'] = {'marker': own_marker, 'lat': self._own_lat, 'lon': self._own_lon}

        # Marker für Zielstation sicherstellen
        if call not in self._markers:
            target_icon = self._get_station_icon(call)
            target_marker = self._map_widget.set_marker(target_lat, target_lon, text=call, icon=target_icon)
            self._markers[call] = {'marker': target_marker, 'lat': target_lat, 'lon': target_lon}

        # Karte anpassen: Bounding Box mit Padding
        min_lat = min(self._own_lat, target_lat)
        max_lat = max(self._own_lat, target_lat)
        min_lon = min(self._own_lon, target_lon)
        max_lon = max(self._own_lon, target_lon)

        delta_lat = max_lat - min_lat
        delta_lon = max_lon - min_lon
        padding = 0.1 * max(delta_lat, delta_lon, 0.01)  # Mindestpadding für nahe Punkte

        north_lat = max_lat + padding
        south_lat = min_lat - padding
        west_lon = min_lon - padding
        east_lon = max_lon + padding

        self._map_widget.fit_bounding_box((north_lat, west_lon), (south_lat, east_lon))
    ##########################
    @staticmethod
    def _delete_tree(tree: ttk.Treeview):
        for i in tree.get_children():
            tree.delete(i)


    def _reset_mh_list(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_mh_delete'),
                                  message=self._getTabStr('msg_box_mh_delete_msg'), parent=self):
            mh = self.get_mh()
            mh.reset_mainMH()
            self._old_mh_data = {}
            self._delete_tree(self._tree)
            self._update_mh()

    def _reset_dx_history(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'), parent=self):
            mh = self.get_mh()
            mh.reset_dxHistory()
            self._old_alarm_his_len = 0
            self._delete_tree(self._alarm_tree)
            self._update_dx_his()

    def _reset_conn_history(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'), parent=self):
            mh = self.get_mh()
            mh.reset_conn_hist()
            self._old_conn_hist_len = 0
            self._delete_tree(self._conn_his_tab)
            self._update_conn_his()

    def _reset_tracer_history(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'), parent=self):

            self._be_tracer.delete_all_data()

    ##########################
    """
    def get_MapView_cache(self):
        if hasattr(self._root_win, 'get_MapView_cache'):
            return self._root_win.get_MapView_cache()
        return {}

    def set_MapView_cache(self, cache: dict):
        if hasattr(self._root_win, 'set_MapView_cache'):
            self._root_win.set_MapView_cache(cache)
    """
    ##########################


    def get_mh(self):
        try:
            port_handler = self._root_win.get_PH_mainGUI()
            return port_handler.get_MH()
        except Exception as ex:
            logger.error(ex)
            return None

    def _get_aprs_ais(self):
        try:
            port_handler = self._root_win.get_PH_mainGUI()
            return port_handler.get_aprs_ais()
        except Exception as ex:
            logger.error(ex)
            return None

    def _get_userDB(self):
        try:
            port_handler = self._root_win.get_PH_mainGUI()
            return port_handler.get_userDB()
        except Exception as ex:
            logger.error(ex)
            return None
    ##########################
    def _add_thread_gc(self, thread):
        if hasattr(self._root_win, 'add_thread_gc'):
            self._root_win.add_thread_gc(thread)

    def _close_me(self):
        if self._quit:
            return
        mh = self.get_mh()
        mh.reset_dx_alarm_his()
        self._mh_graph.destroy_plot()
        self._clear_map()

        # Threads stoppen signalisieren
        self._map_widget.running = False
        self._map_widget.image_load_queue_tasks = []
        self._map_widget.image_load_queue_results = []
        for thread in self._map_widget.get_threads():
            self._add_thread_gc(thread)
        self._root_win.mh_window = None
        self._root_win.add_win_gc(self)
        # Fenster/Frame unsichtbar machen, statt direkt zu zerstören
        self._quit = True
        self.withdraw()  # Macht das gesamte Toplevel unsichtbar (alternativ: self._map_pw.pack_forget() für nur den Map-Bereich)
        # Starte asynchrones Polling, um auf Threads zu warten
        self._check_threads_and_destroy()

    def _check_threads_and_destroy(self):
        map_threads = self._map_widget.get_threads()
        all_dead = all(not thread.is_alive() for thread in map_threads)

        if all_dead:
            # Alle Threads sind tot – jetzt safe zerstören
            self._map_widget.clean_cache()
            gc.collect()
            self._map_pw.destroy()
            self._main_pw.destroy()

            self.destroy()
            self.is_destroyed = True

    def all_dead(self):
        map_threads = self._map_widget.get_threads()
        return all(not thread.is_alive() for thread in map_threads)

    def destroy_win(self):
        self._close_me()

    def destroy(self):
        self.destroy_win()