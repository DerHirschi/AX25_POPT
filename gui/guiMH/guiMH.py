import gc
import random

import tkinter as tk
from tkinter import ttk, Menu, messagebox
from ax25.ax25Statistics import MyHeard
from cfg.constant import CFG_TR_DX_ALARM_BG_CLR
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import conv_time_DE_str, get_strTab
from gui.MapView.tkMapView_override import SafeTkinterMapView
from gui.guiMH.guiAPRS_be_tracer import BeaconTracer
from gui.guiMH.gui_ConnPath_plot import ConnPathsPlot


class MHWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_win    = root_win
        self._getTabStr   = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.title("MyHEARD")
        self.style = root_win.style
        self.geometry(f"1100x"
                      f"700+"
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
        ###################################
        # Vars
        self._rev_ent               = False
        self._tree_data             = []
        self._alarm_tree_data       = []
        self._alarm_newCall_var     = tk.BooleanVar(self)
        self._alarm_seenSince_var   = tk.StringVar(self)
        self._alarm_distance_var    = tk.StringVar(self)
        self._tracer_duration_var   = tk.StringVar(self)
        self._alarm_ports           = []
        self._markers               = {}  # {call: {'marker': MarkerObj, 'lat': float, 'lon': float}}
        self._paths                 = []  # Liste von Path-Objekten für Verbindungslinien
        self._quit                  = False
        self.is_destroyed           = False
        ports = list(POPT_CFG.get_port_CFGs().keys())
        for _por_id in ports:
            self._alarm_ports.append(tk.BooleanVar(self))
        self._get_vars()
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
        self._tabclt = ttk.Notebook(up_frame)
        self._tabclt.pack(fill='both', expand=True)
        mh_frame = ttk.Frame(self._tabclt)
        hi_frame = ttk.Frame(self._tabclt)
        tr_frame = ttk.Frame(self._tabclt)
        mh_frame.pack(fill='both', expand=True)
        hi_frame.pack(fill='both', expand=True)
        tr_frame.pack(fill='both', expand=True)
        self._tabclt.add(mh_frame, text='MH')
        self._tabclt.add(hi_frame, text='DX-Alarm')
        self._tabclt.add(tr_frame, text='APRS-Tracer')

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
        # ###################### Auto Tracer ######################
        # Tracer
        auto_tracer_state = {
            True: 'disabled',
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
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        lat, lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)

        # Setze die anfängliche Position und Zoom-Level (z. B. Europa)
        self._map_widget.set_position(lat, lon)
        self._map_widget.set_zoom(6)
        #############################################################################
        # ###################### M-Graph ##########################################
        # map2_frame
        self._mh_graph = ConnPathsPlot(map1_frame, self)

        ###############################################
        self._init_menubar()
        self._root_win.mh_window = self
        self._update_mh()
        self._update_dx_his()

    ##########################
    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('del_all'), command=self._reset_mh_list)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('delete_dx_history'), command=self._reset_dx_history)
        menubar.add_cascade(label='MyHeard', menu=MenuVerb, underline=0)

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
        if hasattr(self._map_widget, 'tasker'):
            return self._map_widget.tasker()
        return False

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
    def _update_dx_his(self):
        self._format_alarm_tree_data()
        self._update_alarm_tree()
        # self._update_map()

    def _update_alarm_tree(self):
        for i in self._alarm_tree.get_children():
            self._alarm_tree.delete(i)

        for ret_ent in self._alarm_tree_data:
            self._alarm_tree.insert('', 'end', values=ret_ent[0], )

    def _format_alarm_tree_data(self):
        self._alarm_tree_data = []
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
        his_keys.reverse()
        for k in his_keys:
            ent = dx_alarm_his.get(k, {})
            call = ent.get('call_str', '')
            port = ent.get('port_id', -1)
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
        self._init_tree_data()
        self._update_tree()
        self._update_map()

    def _init_tree_data(self):
        self._sort_entry('last')

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
        self._update_tree()

    def _format_tree_ent(self, mh_list):
        self._tree_data = []
        mh = self.get_mh()

        for k in mh_list:
            ent: MyHeard
            ent = mh_list[k]
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

    ##########################
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

    ##########################
    def _reset_mh_list(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_mh_delete'),
                                  message=self._getTabStr('msg_box_mh_delete_msg'), parent=self):
            mh = self.get_mh()
            mh.reset_mainMH()
            self._update_mh()

    def _reset_dx_history(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_mh_delete'),
                                  message=self._getTabStr('msg_box_mh_delete_msg'), parent=self):
            mh = self.get_mh()
            mh.reset_dxHistory()
            self._update_mh()

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