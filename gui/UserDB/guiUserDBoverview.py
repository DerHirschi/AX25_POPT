import gc
import random
import tkinter as tk
from tkinter import ttk

from UserDB.UserDBmain import Client
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import conv_time_DE_str, get_strTab
from gui.MapView.tkMapView_override import SafeTkinterMapView
from gui.guiMsgBoxes import AskMsg
from gui.guiRightClick_Menu import ContextMenu


class UserDBtreeview(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_win              = root_win
        self._getTabStr             = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._aprs_icon_tab_24      = root_win.get_aprs_icon_tab_24()
        self._aprs_icon_tab_16      = root_win.get_aprs_icon_tab_16()
        ###################################
        # Vars
        self.title("User-DB")
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1200x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ############################################################
        self._sort_flag         = ''
        self._rev_ent           = False
        self._selected          = []
        self._tree_data         = []
        self._data              = {}
        self._key_is_pressed    = False
        #
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        self._own_lat, self._own_lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)
        self._markers       = {}  # {call: {'marker': MarkerObj, 'lat': float, 'lon': float}}
        self._paths         = []  # Liste von Path-Objekten für Verbindungslinien
        self._current_path  = None
        # MapView Thread Ctrl.
        self._quit        = False
        self.is_destroyed = False
        ############################################################
        main_f = ttk.Frame(self)
        main_f.pack(fill='both', expand=True)
        ##########################################################################################
        self._main_pw = ttk.Panedwindow(main_f, orient='vertical')
        self._main_pw.pack(fill='both', expand=True)
        tree_f = ttk.Frame(self._main_pw)
        map_f  = ttk.Frame(self._main_pw)
        tree_f.pack(fill='both', expand=True)
        map_f.pack( fill='both', expand=True)

        self._main_pw.add(tree_f, weight=0)
        self._main_pw.add(map_f, weight=1)
        ##########################################################################################
        # TREE
        columns = (
            'uDB_call',
            'uDB_sysop',
            'uDB_typ',
            'uDB_loc',
            'uDB_dist',
            'uDB_qth',
            'uDB_land',
            'uDB_lastconn',
            # 'uDB_lastseen', # TODO Get from MH
        )
        self._tree = ttk.Treeview(tree_f, columns=columns, show='tree headings')
        self._tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_f, orient='vertical', command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._tree.heading('uDB_call', text='Call', command=lambda: self._sort_entry('call'))
        self._tree.heading('uDB_sysop', text='Sysop', command=lambda: self._sort_entry('sysop'))
        self._tree.heading('uDB_typ', text='Typ', command=lambda: self._sort_entry('typ'))
        self._tree.heading('uDB_loc', text='Locator', command=lambda: self._sort_entry('loc'))
        self._tree.heading('uDB_dist', text='Distance', command=lambda: self._sort_entry('dist'))
        self._tree.heading('uDB_qth', text='QTH', command=lambda: self._sort_entry('qth'))
        self._tree.heading('uDB_land', text='Land', command=lambda: self._sort_entry('land'))
        self._tree.heading('uDB_lastconn', text='Last Conn', command=lambda: self._sort_entry('last_conn'))
        # self.tree.heading('uDB_lastseen', text='Last seen', command=lambda: self.sort_entry('last_seen')) # TODO Get from MH

        self._tree.column('#0', anchor='w', stretch=False, width=45)
        self._tree.column("uDB_call", anchor='w', stretch=tk.NO, width=130)
        self._tree.column("uDB_sysop", anchor='w', stretch=tk.NO, width=130)
        self._tree.column("uDB_typ", anchor='w', stretch=tk.NO, width=150)
        self._tree.column("uDB_loc", anchor='w', stretch=tk.NO, width=100)
        self._tree.column("uDB_dist", anchor='w', stretch=tk.NO, width=90)
        self._tree.column("uDB_qth", anchor='w', stretch=tk.YES, width=190)
        self._tree.column("uDB_land", anchor='w', stretch=tk.NO, width=60)
        self._tree.column("uDB_lastconn", anchor='w', stretch=tk.NO, width=190)
        # self.tree.column("uDB_lastseen", anchor='w', stretch=tk.NO, width=190) # TODO Get from MH
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)
        ##########################################################################################
        # MAP
        self._map_widget = SafeTkinterMapView(root_win=self, master=map_f, corner_radius=0)
        self._map_widget.pack(fill="both", expand=True)
        ais_cfg  = POPT_CFG.get_CFG_aprs_ais()
        lat, lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)

        # Setze die anfängliche Position und Zoom-Level (z. B. Europa)
        self._map_widget.set_position(lat, lon)
        self._map_widget.set_zoom(6)
        ##########################################################################################
        self._root_win.userDB_tree_win = self
        self._init_tree_data()
        self._update_tree()
        self._update_map()
        self.bind('<Key>', lambda event: self._on_key_press(event))
        self.bind('<KeyRelease>', lambda event: self._on_key_release(event))
        #self._tree.bind('<<TreeviewSelect>>', self._entry_selected)
        self._tree.bind('<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._tree))
        self._init_RClick_menu()

    #####################################################
    def _init_RClick_menu(self):
        txt_men = ContextMenu(self._tree)
        txt_men.add_item(self._getTabStr('show_in_userDB'), self._open_main_UserDB)
        txt_men.add_separator()
        txt_men.add_item(self._getTabStr('delete_selected'), self._del_menu_cmd)

    #####################################################
    def tasker(self):
        if self._quit:
            self._check_threads_and_destroy()
            return True
        if hasattr(self._map_widget, 'tasker'):
            return self._map_widget.tasker()
        return False

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
        #own_lat, own_lon = POPT_CFG.get_CFG_aprs_ais().get('ais_lat', 0.0), POPT_CFG.get_CFG_aprs_ais().get('ais_lon', 0.0)
        user_db = self._get_userDB()
        user_database: dict = user_db.get_database()
        if not hasattr(user_db, 'get_location'):
            logger.error("not hasattr(user_db, 'get_location')")
            return

        for call, ent in user_database.items():
            ent: Client
            if ent.call_str in self._markers:
                continue
            lat, lon, loc = user_db.get_location(ent.call_str)
            if not lat and not lon:
                continue

            offset_range = 0.0002  # Ca. 10-11 Meter, anpassen nach Bedarf
            lat += random.uniform(-offset_range, offset_range)
            lon += random.uniform(-offset_range, offset_range)
            icon = self._get_station_icon(ent.call_str)
            # Marker für die Station setzen
            marker = self._map_widget.set_marker(lat, lon, text=ent.call_str, icon=icon)
            self._markers[ent.call_str] = {'marker': marker, 'lat': lat, 'lon': lon}

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
        self._entry_selected(event)
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
        call_index = 0      # mh_call
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
    #####################################################
    def _init_tree_data(self):
        self._sort_entry('call')

    def _update_tree(self):
        self._format_tree_ent()

        for i in self._tree.get_children():
            self._tree.delete(i)

        ais = self._root_win.get_AIS_mainGUI()


        for ret_ent in self._tree_data:
            call   = ret_ent[0]
            symbol = ais.get_symbol_fm_node_tab(call)
            image  = self._aprs_icon_tab_16.get(symbol, None)
            if image:
                self._tree.insert('', 'end', values=ret_ent, image=image)
            else:
                self._tree.insert('', 'end', values=ret_ent)

    def _on_key_press(self, event: tk.Event):
        self._key_is_pressed = True

    def _on_key_release(self, event: tk.Event):
        self._key_is_pressed = False

    def _entry_selected(self, event: tk.Event):
        #r_key = ''
        self._selected = []
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values']
            # show a message
            #r_key = record[0]
            self._selected.append(record[0])
        #if self._key_is_pressed or not r_key:
        #    return
        #self._root_win.open_user_db_win(ent_key=r_key)

    def _open_main_UserDB(self, event=None):
        if not self._selected:
            return
        if self._key_is_pressed:
            return
        selected = self._selected[-1]
        self._root_win.open_user_db_win(ent_key=selected)


    def _sort_entry(self, flag: str):
        userDB = self._get_userDB()
        self._sort_flag = flag
        self._data = userDB.get_sort_entr(flag_str=self._sort_flag, reverse=self._rev_ent)
        if self._rev_ent:
            self._rev_ent = False
        else:
            self._rev_ent = True
        self._update_tree()

    def _update_entry(self):
        userDB = self._get_userDB()
        self._data = userDB.get_sort_entr(flag_str=self._sort_flag, reverse=self._rev_ent)
        self._update_tree()

    def _format_tree_ent(self):
        self._tree_data = []
        for k, ent in self._data.items():
            distance = round(ent.Distance)
            self._tree_data.append((
                f'{ent.call_str}',
                f'{ent.Sysop_Call}',
                f'{ent.TYP}',
                f'{ent.LOC}',
                f"{'n/a' if distance < 0 else distance}",
                f'{ent.QTH}',
                f'{ent.Land}',
                f"{'' if ent.last_conn is None else conv_time_DE_str(ent.last_conn)}",
                # f'{conv_time_DE_str(ent.last_seen)}',   # TODO Get from MH

            ))

    def _del_menu_cmd(self):
        if not self._selected:
            return
        if self._key_is_pressed:
            return
        msg = AskMsg(
            titel=self._getTabStr('userdb_del_hint2_1').format(len(self._selected)),
            message=self._getTabStr('userdb_del_hint2_2').format(len(self._selected)),
            parent_win=self)
        if not msg:
            return
        userDB = self._get_userDB()
        for sel_ent in self._selected:
            userDB.del_entry(str(sel_ent))
        self._update_entry()
    ##########################
    def _get_mh(self):
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

    #################################################
    def _add_thread_gc(self, thread):
        if hasattr(self._root_win, 'add_thread_gc'):
            self._root_win.add_thread_gc(thread)

    def _close_me(self):
        if self._quit:
            return
        self._clear_map()

        # Threads stoppen signalisieren
        self._map_widget.running = False
        self._map_widget.image_load_queue_tasks = []
        self._map_widget.image_load_queue_results = []
        for thread in self._map_widget.get_threads():
            self._add_thread_gc(thread)
        self._root_win.userDB_tree_win = None
        self._root_win.add_win_gc(self)
        # Fenster/Frame unsichtbar machen, statt direkt zu zerstören
        self._quit = True
        self.withdraw()  # Macht das gesamte Toplevel unsichtbar (alternativ: self._map_pw.pack_forget() für nur den Map-Bereich)
        # Starte asynchrones Polling, um auf Threads zu warten
        self._check_threads_and_destroy()

    def _check_threads_and_destroy(self):
        map_threads = self._map_widget.get_threads()
        all_dead    = all(not thread.is_alive() for thread in map_threads)

        if all_dead:
            # Alle Threads sind tot – jetzt safe zerstören
            self._map_widget.clean_cache()
            gc.collect()
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

