import datetime
import gc
import time
import random
import tkinter as tk

from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from cfg.constant import FONT, APRS_MAX_TREE_ITEMS
from ax25aprs.aprs_constant import APRS_INET_PORT_ID
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import delete_tree
from fnc.str_fnc import tk_filter_bad_chars, get_strTab
from gui.MapView.tkMapView_override import SafeTkinterMapView
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_BL_Tab import APRSmonBLTree
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_DIGI_Tab import APRSmonDIGIMonTree
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_IGate_Tab import IGateTab
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_Msg_Tab import APRSmonMSGTree
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_Node_Tab import APRSmonNodeTree
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_Obj_Tab import APRSmonObjTree
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_Pack_Tab import APRSmonPackTree
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_WX_Tab import APRSmonWXTree
from gui.aprs.guiAPRS_Monitor.guiAPRSmon_ownIGate_Mon import APRSmonIGateMonTree
from gui.aprs.guiAPRS_SMS_frame import APRSChatFrame


class AISmonitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_cl       = root_win
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._text_size     = int(self._root_cl.text_size)
        self._win_height    = 600
        self._win_width     = 1200
        # self.style = self._root_cl.style
        self.title(self._getTabStr('aprs_mon'))
        self.geometry(f"{self._win_width}x"
                      f"{self._win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        # self.resizable(False, False)
        self.lift()
        ##############################################
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        self._own_lat, self._own_lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)
        self._popt_handler           = root_win.get_PH_mainGUI()
        self._ais_obj                = self._popt_handler.get_aprs_ais()
        self._aprs_icon_tab_16       = root_win.guiIcon.get_aprs_icon_tab_16()
        self._aprs_icon_tab_24       = root_win.guiIcon.get_aprs_icon_tab_24()
        self.call_filter_list        = []
        ####
        self._tasker_q               = []
        self._tasker_q_prio          = []
        self._10_sec_task_timer      = time.time() + 10
        ####
        self._marker_timeout         = 30  # Minuten, bis Marker gelöscht wird (anpassen nach Bedarf)
        self._markers                = {}  # {call: {'marker': MarkerObj, 'lat': float, 'lon': float}}
        self._paths                  = []  # Liste von Path-Objekten für Verbindungslinien
        self._current_path           = None
        # Map View Thread Ctrl.
        self._quit                   = False
        self.is_destroyed            = False
        ##############################################
        self._autoscroll_var        = tk.BooleanVar(self, value=True)
        self._call_filter           = tk.BooleanVar(self, value=False)
        self.call_filter_calls_var  = tk.StringVar(self)
        self.port_filter_var        = tk.StringVar(self,  value='')
        ##############################################
        main_f = ttk.Frame(self)
        main_f.pack(fill='both', expand=True)
        ##############################################
        pw      = ttk.PanedWindow(main_f, orient='horizontal')
        pw.pack(fill='both', expand=True)
        tree_f  = ttk.Frame(pw)
        mon_f   = ttk.Frame(pw)
        pw.add(tree_f, weight=1)
        pw.add(mon_f,  weight=1)
        ##############################################
        tab = ttk.Notebook(tree_f)
        tab.pack(fill='both', expand=True)
        ##############################################
        igate_list_f = ttk.Frame(tab)
        self._pack_tree_cl  = APRSmonPackTree(tab, self)
        self._igate_tab     = IGateTab(self, igate_list_f)
        self._node_tree_cl  = APRSmonNodeTree(tab, self, self._popt_handler)
        self._obj_tree_cl   = APRSmonObjTree(tab, self, self._popt_handler)
        self._wx_tree_cl    = APRSmonWXTree(  tab, self)
        self._msg_tree_cl   = APRSmonMSGTree( tab, self)
        self._bl_tree_cl    = APRSmonBLTree(  tab, self)
        self._igate_mon_cl  = APRSmonIGateMonTree(tab, self, self._popt_handler)
        self._digi_mon_cl   = APRSmonDIGIMonTree(tab, self, self._popt_handler)
        igate_list_f.pack(fill='both', expand=True)
        ##############################################
        tab.add(self._node_tree_cl, text="Node-List")
        tab.add(igate_list_f,       text="IGate Status")
        tab.add(self._obj_tree_cl,  text="Objects")
        tab.add(self._wx_tree_cl,   text="WX")
        tab.add(self._msg_tree_cl,  text="Msg")
        tab.add(self._bl_tree_cl,   text="Bulletin")
        tab.add(self._pack_tree_cl, text="Packet-Monitor")
        tab.add(self._igate_mon_cl, text="IGate-Monitor")
        tab.add(self._digi_mon_cl,  text="DIGI-Monitor")
        ##############################################
        ttk.Label(tree_f, text='Port-Filter:').pack(side='left', anchor='w', padx=10)
        opt = [
                  "",
                  "",
                  APRS_INET_PORT_ID,
              ] + [str(el) for el in list(POPT_CFG.get_port_CFGs().keys())]
        port_filter_m = ttk.OptionMenu(tree_f,
                                       self.port_filter_var,
                                       *opt,
                                       command=lambda e: self._chk_port_filter())
        port_filter_m.pack(side='left', padx=0)
        ##############################################
        # Frame für den linken Bereich
        ##############################################
        # PW für den rechten Bereich
        tab2 = ttk.Notebook(mon_f)
        tab2.pack(fill='both', expand=True)
        ##############################################
        mon_tab_f = ttk.Frame(tab2)
        map_tab_f = ttk.Frame(tab2)
        sms_tab_f = APRSChatFrame(tab2, self._popt_handler)

        mon_tab_f.pack(fill='both', expand=True)
        map_tab_f.pack(fill='both', expand=True)
        sms_tab_f.pack(fill='both', expand=True)

        tab2.add(mon_tab_f, text="Monitor")
        tab2.add(map_tab_f, text="Map")
        tab2.add(sms_tab_f, text="SMS")
        ##############################################
        # Monitor
        left_frame  = ttk.Frame(mon_tab_f)
        l1_frame    = ttk.Frame(mon_tab_f)
        l2_frame    = ttk.Frame(mon_tab_f)

        left_frame.pack( padx=5, pady=5, fill='both', expand=True)
        l1_frame   .pack(padx=5,         fill='x',    expand=False)
        l2_frame   .pack(padx=5,         fill='x',    expand=False)

        self.text_widget = ScrolledText(left_frame,
                                        background='black',
                                        foreground='green',
                                        width=85
                                        )
        self.text_widget.configure(font=(FONT, self._text_size))
        self.text_widget.pack(fill='both', expand=True)

        # Frame für den rechten Bereich
        ttk.Checkbutton(l1_frame   ,
                       variable=self._autoscroll_var,
                       text="Autoscroll  ",
                       command=self._scroll_to_end).pack(side='left', padx=2)

        ttk.Checkbutton(l1_frame   ,
                       variable=self._call_filter,
                       text="Call-Filter  ",
                       command=self._chk_call_filter
                       ).pack(side='left', padx=2)

        ttk.Label(l2_frame   , text="Call-Filter:").pack(side='left', padx=2)
        ttk.Entry(l2_frame,
                  textvariable=self.call_filter_calls_var,
                  width=20
                  ).pack(side='left', padx=2)
        ##########
        ttk.Button(l2_frame,
                   text="Reset",
                   command=self._reset_filter
                   ).pack(side='left', padx=50)

        ttk.Button(l2_frame   ,
                  text=self._getTabStr('delete'),
                  command=self._del_buffer
                  ).pack(side='left', padx=10)
        ##############################################
        # MAP
        f1 = ttk.Frame(map_tab_f)
        f2 = ttk.Frame(map_tab_f)

        f1.pack(padx=5, pady=5, fill='both', expand=True)
        f2.pack(padx=5,         fill='x',    expand=False)
        ##############################################
        # Erstelle das Map-Widget
        self._map_widget = SafeTkinterMapView(root_win=self, master=f1, corner_radius=0)
        self._map_widget.pack(fill="both", expand=True)

        # Setze die anfängliche Position und Zoom-Level (z. B. Europa)
        self._map_widget.set_position(self._own_lat, self._own_lon)  # Paris als Startpunkt
        self._map_widget.set_zoom(8)
        # self._map_widget.bind("<<MapViewZoom>>", self._on_zoom_change)
        ########################################################
        # f2
        ttk.Button(f2,
                   text='Reset Map',
                   command=lambda : self._clear_map_markers()
        ).pack(anchor='w', padx=20)
        ########################################################

        ########################################################
        self.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())
        ########################################################
        self._bl_tree_cl.bl_tree.bind(    '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._bl_tree_cl.bl_tree))
        self._msg_tree_cl.msg_tree.bind(  '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._msg_tree_cl.msg_tree))
        self._obj_tree_cl.obj_tree.bind(  '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._obj_tree_cl.obj_tree))
        self._pack_tree_cl.mon_tree.bind( '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._pack_tree_cl.mon_tree))
        self._node_tree_cl.node_tree.bind('<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._node_tree_cl.node_tree))

        if self._ais_obj is not None:
            own_call = POPT_CFG.get_CFG_aprs_ais().get('ais_call', '')
            if own_call:
                self.call_filter_list.append(own_call)
                self.call_filter_calls_var.set(own_call)

        #self._node_tree_init()
        self._node_tree_cl.node_tree_init()
        self._obj_tree_cl.obj_tree_init()
        self._igate_tab.init_tree()
        self.init_ais_mon()
        self._igate_mon_cl.init_tree()
        self._digi_mon_cl.init_tree()
        sms_tab_f.update_aprs_msg_frame()
        root_win.toplevel_manager.aprs_mon_win = self


    #############################################################
    def add_to_tree(self, tree_data: tuple, tree, add_to_end=True, auto_scroll=True, replace_ent=False, prio=True):
        self._add_tasker_q("_add_to_tree", (tree_data, tree, add_to_end, auto_scroll, replace_ent), prio=prio)

    def _add_to_tree_task(self, tree_data: tuple, tree, add_to_end=True, auto_scroll=True, replace_ent=False):
        is_scrolled_to_top = tree.yview()[0] == 0.0
        image              = self._aprs_icon_tab_16.get(tree_data[-1], None)
        if replace_ent:
            items = list(tree.get_children())
            for index, item in enumerate(items):
                if tree.set(item, 'node_id') == tree_data[0]:
                    tree.delete(item)
                    break

        if add_to_end:
            index = 'end'
        else:
            index = 0

        tree_data_f = [tk_filter_bad_chars(el) if type(el) == str else el for el in tree_data[:-1]]

        try:
            if image:
                tree.image_ref = image
                tree.insert('', index, values=tree_data_f, image=image)
            else:
                tree.insert('', index, values=tree_data_f)
        except tk.TclError as ex:
            logger.warning("TCL Error in AISmonitor add_to_tree")
            logger.warning(ex)
            return

        tree_items = tree.get_children()
        if len(tree_items) > APRS_MAX_TREE_ITEMS:
            for item in tree_items[APRS_MAX_TREE_ITEMS:]:
                tree.delete(item)

        if not is_scrolled_to_top and not add_to_end and auto_scroll :
            try:
                tree.yview_scroll(1, "units")
            except tk.TclError:
                pass
            except Exception as e:
                null = e
                # logger.warning(e)
                pass

    @staticmethod
    def _get_treedata_fm_pack(aprs_pack: dict):
        text = aprs_pack.get('text', '')
        if not text and aprs_pack.get('comment', ''):
            text = aprs_pack.get('comment', '')
        if not text and aprs_pack.get('status', ''):
            text = aprs_pack.get('status', '')

        msg_typ = aprs_pack.get('format', '')
        if aprs_pack.get('subpacket', ''):
            msg_typ = 'subpacket'
        if aprs_pack.get('weather', ''):
            msg_typ = 'weather'
        return (
                aprs_pack.get('from', ''),
                aprs_pack.get('to', ''),
                aprs_pack.get('port_id', ''),
                aprs_pack.get('via', ''),
                '>'.join(aprs_pack.get('path', [])),
                f"{aprs_pack.get('locator', '')}({round(aprs_pack.get('distance', -1))} km)",
                msg_typ,
                aprs_pack.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
                text,
                aprs_pack.get('raw', ''),
                (aprs_pack.get('symbol_table', ''), aprs_pack.get('symbol', ''))
            )

    #############################################################
    # IGate Tree
    def igate_tree_update(self, pack: dict):
        self._igate_mon_cl.igate_tree_update(pack)

    #############################################################
    # DIGI Tree
    def digi_tree_update(self, pack: dict):
        self._digi_mon_cl.digi_tree_update(pack)

    #############################################################
    # Obj Tree
    def obj_tree_update(self, object_ent: dict):
        self._obj_tree_cl.obj_tree_update(object_ent)

    #############################################################
    def init_ais_mon(self, init_tree=True):
        if not self._ais_obj:
            self.text_widget.insert(tk.END, "*** ERROR: No AIS found ***")
            logger.error("*** ERROR: No AIS found ***")
            return
        tr              = False
        call_filter_var = self._call_filter.get()
        port_filter     = self.port_filter_var.get()
        for el in list(self._ais_obj.ais_rx_buff):
            if not el:
                continue
            el: dict
            # Tree
            if port_filter and port_filter != el.get('port_id', ''):
                continue
            if init_tree:
                tree_data = self._get_treedata_fm_pack(el)
                if tree_data:
                    self.add_to_tree(tree_data=tree_data,
                                      tree=self._pack_tree_cl.mon_tree,
                                      add_to_end=False,
                                      replace_ent=False,
                                      prio=False)
                if el.get('weather', {}):
                    wx_tree_data = self._wx_tree_cl.get_treedata_fm_wx_pack(el)
                    if wx_tree_data:
                        self.add_to_tree(tree_data=wx_tree_data,
                                          tree=self._wx_tree_cl.wx_tree,
                                          add_to_end=False,
                                          replace_ent=True)
                elif el.get('format', '') == 'message':
                    msg_tree_data = self._msg_tree_cl.get_treedata_fm_msg_pack(el)
                    if msg_tree_data:
                        self.add_to_tree(tree_data=msg_tree_data,
                                          tree=self._msg_tree_cl.msg_tree,
                                          add_to_end=False,
                                          replace_ent=False)
                elif el.get('format', '') == 'bulletin':
                    bl_tree_data = self._bl_tree_cl.get_treedata_fm_bl_pack(el)
                    if bl_tree_data:
                        self.add_to_tree(tree_data=bl_tree_data,
                                          tree=self._bl_tree_cl.bl_tree,
                                          add_to_end=False,
                                          replace_ent=False)
            # self._add_treedata(tree_data)
            # Monitor

            if call_filter_var:
                if el.get('from', '') in self.call_filter_list:
                    tr = True
                    tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc)
                    self.text_widget.insert(tk.END, tmp)
            else:
                tr = True
                tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc)
                self.text_widget.insert(tk.END, tmp)
        if tr:
            self._scroll_to_end()

        #print(f"e_t Total: {time.time() - tt} s")
        #print(f"buf_len  : {buf_len} ")

    ###########################################################
    def tasker(self):
        if self._quit:
            self._check_threads_and_destroy()
            return True
        ret = False
        if time.time() > self._10_sec_task_timer:
            self._10_sec_task_timer = time.time() + 10
            self._check_map_timeouts()
            ret = True

        if hasattr(self._map_widget, 'tasker'):
            ret = self._map_widget.tasker()

        if not self._tasker_q and not self._tasker_q_prio:
            return ret

        tasker_n = 20

        while any((self._tasker_q_prio, self._tasker_q)) and tasker_n:
            if self._tasker_q_prio:
                task, arg = self._tasker_q_prio[0]
                self._tasker_q_prio = self._tasker_q_prio[1:]
            elif self._tasker_q:
                task, arg = self._tasker_q[0]
                self._tasker_q = self._tasker_q[1:]
            else:
                break
            if task == 'pack_to_mon':
                self._pack_to_mon_task(arg)
            elif task == 'update_node_tab':
                self._update_node_tab_task(arg)
            elif task == '_add_to_tree':
                tree_data, tree, add_to_end, auto_scroll, replace_ent = arg
                self._add_to_tree_task(tree_data, tree, add_to_end, auto_scroll, replace_ent)
            elif task == 'update_igate_tab':
                self._update_igate_tab_task(arg)
            tasker_n -= 1

        return True

    def _add_tasker_q(self, fnc: str, arg, prio=True):
        if prio:
            if (fnc, None) in self._tasker_q_prio:
                return
            self._tasker_q_prio.append(
                (fnc, arg)
            )
        else:
            if (fnc, None) in self._tasker_q:
                return
            self._tasker_q.append(
                (fnc, arg)
            )

    def pack_to_mon(self, pack):
        self._add_tasker_q("pack_to_mon", pack)

    def _pack_to_mon_task(self, pack):
        port_filter = self.port_filter_var.get()
        if port_filter and port_filter != pack.get('port_id', ''):
            return
        tr = False
        tree_data = self._get_treedata_fm_pack(pack)
        #self._add_treedata(tree_data)
        self.add_to_tree(tree_data, tree=self._pack_tree_cl.mon_tree, add_to_end=False, replace_ent=False, prio=False)
        if self._call_filter.get():
            if pack['from'] in self.call_filter_list:
                tr = True
                tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc)
                tmp = tk_filter_bad_chars(tmp)
                self.text_widget.insert(tk.END, tmp)
                self._wx_tree_cl.wx_tree_update(pack)
                self._msg_tree_cl.msg_tree_update(pack)
                self._bl_tree_cl.bl_tree_update(pack)
        else:
            tr = True
            tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc)
            tmp = tk_filter_bad_chars(tmp)
            self.text_widget.insert(tk.END, tmp)
            self._wx_tree_cl.wx_tree_update(pack)
            self._msg_tree_cl.msg_tree_update(pack)
            self._bl_tree_cl.bl_tree_update(pack)
        if tr:
            self._scroll_to_end()

        # Marker aktualisieren/hinzufügen
        if 'latitude' in pack and 'longitude' in pack:
            lat, lon = pack.get('latitude', 0.0), pack.get('longitude', 0.0)
            if lat is not None:
                node_id = pack.get('from', '')
                if pack.get('format', '') == 'object':
                    node_id = pack.get('name', node_id)
                symbol_table = pack.get('symbol_table', '/')
                symbol = pack.get('symbol', ' ')
                last_update = pack.get('rx_time', datetime.datetime.now())
                #comment = pack.get('comment', '') or pack.get('status', '') or pack.get('message_text', '')
                self._update_marker(node_id, lat, lon, symbol_table, symbol, last_update)

    def update_node_tab(self, node_tab_ent: dict, object_ent: dict):
        self._add_tasker_q("update_node_tab", (node_tab_ent, object_ent))

    def _update_node_tab_task(self, arg: tuple):
        node_tab_ent, object_ent = arg
        self._node_tree_cl.node_tree_update(node_tab_ent, object_ent)

    def update_igate_tab(self, call: str):
        self._add_tasker_q("update_igate_tab", call)

    def _update_igate_tab_task(self, call: str):
        if hasattr(self, '_igate_tab'):
            self._igate_tab.update_tree(call)

    #######################################
    # MAP
    def _get_station_icon(self, call: str):
        default_icon    = self._aprs_icon_tab_24.get(('\\', 'X'), None)
        user_db         = self._get_userDB()

        if not hasattr(user_db, 'get_typ'):
            logger.error("not hasattr(user_db, 'get_typ')")
            return default_icon
        symbol   = self.get_symbol_fm_node_tab(call) # ('', '')
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
            self._map_widget.set_zoom(8)

        # Bestimme Indizes je nach Treeview
        if tree == self._node_tree_cl.node_tree:
            self._node_tree_cl.node_entry_selected()
        call_index = 0  # node_id
        call = values[call_index].strip()
        if not call:
            return

        user_db = self._get_userDB()
        if not user_db:
            return

        target_lat, target_lon, target_loc = user_db.get_location(call)
        if not target_lat and not target_lon:
            return  # Position unbekannt

        # Linie zeichnen
        path_coords = [(self._own_lat, self._own_lon), (target_lat, target_lon)]
        self._current_path = self._map_widget.set_path(path_coords, color="blue", width=2)

        # Marker für eigene Position sicherstellen
        if 'Own' not in self._markers:
            #own_icon = self._get_station_icon('')  # Default Icon, da kein Call
            own_marker = self._map_widget.set_marker(self._own_lat, self._own_lon, text="My Station",)
            self._markers['Own'] = {
                'marker': own_marker,
                'lat': self._own_lat,
                'lon': self._own_lon,
                'last_update': datetime.datetime.now()
            }

        # Marker für Zielstation sicherstellen
        if call not in self._markers:
            target_icon = self._get_station_icon(call)
            target_marker = self._map_widget.set_marker(target_lat, target_lon, text=call, icon=target_icon)
            self._markers[call] = {
                'marker': target_marker,
                'lat': target_lat,
                'lon': target_lon,
                'last_update': datetime.datetime.now()
            }

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
    #######################################
    def _update_marker(self, node_id, lat, lon, symbol_table, symbol, last_update):
        if not node_id or lat is None or lon is None:
            return
        # Kleiner Random-Offset hinzufügen, wenn neu
        if node_id not in self._markers:
            offset_range = 0.0001  # Ca. 10-11 Meter, anpassen nach Bedarf
            lat += random.uniform(-offset_range, offset_range)
            lon += random.uniform(-offset_range, offset_range)
        else:
            # Bei Update die offsette Position beibehalten
            old_data = self._markers[node_id]
            lat = old_data['lat']
            lon = old_data['lon']

        icon = self._aprs_icon_tab_24.get((symbol_table, symbol), None)
        text = node_id
        #if comment:
        #    text += f" ({tk_filter_bad_chars(comment)})"
        if node_id in self._markers:
            old_data = self._markers[node_id]
            marker = old_data['marker']
            if old_data['lat'] != lat or old_data['lon'] != lon:
                marker.set_position(lat, lon)
                old_data['lat'] = lat
                old_data['lon'] = lon
            old_data['last_update'] = last_update
        else:
            marker = self._map_widget.set_marker(lat, lon, text=text, icon=icon)
            self._markers[node_id] = {
                'marker': marker,
                'lat': lat,
                'lon': lon,
                'last_update': last_update
            }

    def _check_map_timeouts(self):
        now = datetime.datetime.now()
        to_delete = []
        for node_id, data in list(self._markers.items()):
            if (now - data['last_update']).total_seconds() / 60 > self._marker_timeout:
                data['marker'].delete()
                to_delete.append(node_id)
        for d in to_delete:
            del self._markers[d]

    def _clear_map_markers(self):
        """Löscht alle Marker von der Karte und leert das _markers Dictionary."""
        for node_id, data in list(self._markers.items()):
            data['marker'].delete()
            del self._markers[node_id]

    #######################################
    def set_ais_obj(self):
        self._ais_obj = self._popt_handler.get_aprs_ais()

    def get_symbol_fm_node_tab(self, node_id: str):
        if hasattr(self._ais_obj, 'get_symbol_fm_node_tab'):
            return self._ais_obj.get_symbol_fm_node_tab(node_id)
        return '', ''

    """
    def _get_pos_fm_node_tab(self, node_id: str):
        if hasattr(self._ais_obj, 'get_pos_fm_node_tab'):
            return self._ais_obj.get_pos_fm_node_tab(node_id)
        return 0, 0
    """

    def _get_userDB(self):
        try:
            port_handler = self._root_cl.get_PH_mainGUI()
            return port_handler.get_userDB()
        except Exception as ex:
            logger.error(ex)
            return None

    #######################################

    def _increase_textsize(self):
        self._text_size += 1
        self._text_size = max(self._text_size, 3)
        self.text_widget.configure(font=(FONT, self._text_size))

    def _decrease_textsize(self):
        self._text_size -= 1
        self._text_size = max(self._text_size, 3)
        self.text_widget.configure(font=(FONT, self._text_size))

    def _chk_call_filter(self):
        self.call_filter_list = []
        if self._ais_obj is not None:
            own_call = POPT_CFG.get_CFG_aprs_ais().get('ais_call', '')
            if own_call:
                self.call_filter_list.append(own_call)

        calls = self.call_filter_calls_var.get()
        calls = calls.split(' ')
        tmp = []
        for el in list(calls):
            if el:
                tmp.append(el.upper())
        calls = tmp
        self.call_filter_list = self.call_filter_list + calls

    def _chk_port_filter(self):
        self.text_widget.delete(0.0, tk.END)
        delete_tree(tree=self._pack_tree_cl.mon_tree)
        delete_tree(tree=self._node_tree_cl.node_tree)
        delete_tree(tree=self._obj_tree_cl.obj_tree)
        delete_tree(tree=self._wx_tree_cl.wx_tree)
        self.init_ais_mon()
        self._node_tree_cl.node_tree_init()
        self._obj_tree_cl.obj_tree_init()

    def _reset_filter(self):
        self.call_filter_list = []
        self._call_filter.set(False)
        self.call_filter_calls_var.set('')
        self.text_widget.delete(0.0, tk.END)
        delete_tree(tree=self._pack_tree_cl.mon_tree)
        delete_tree(tree=self._node_tree_cl.node_tree)
        delete_tree(tree=self._obj_tree_cl.obj_tree)
        delete_tree(tree=self._wx_tree_cl.wx_tree)
        delete_tree(tree=self._igate_mon_cl.own_igate_tree)
        delete_tree(tree=self._digi_mon_cl.digi_tree)
        self.init_ais_mon()
        self._node_tree_cl.node_tree_init()
        self._obj_tree_cl.obj_tree_init()
        self._igate_mon_cl.init_tree()
        self._digi_mon_cl.init_tree()

    def _del_buffer(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'),
                                  parent=self):
            if hasattr(self._ais_obj, 'del_ais_rx_buff'):
                self._ais_obj.del_ais_rx_buff()
            self.text_widget.delete(0.0, tk.END)
            delete_tree(tree=self._pack_tree_cl.mon_tree)
            delete_tree(tree=self._node_tree_cl.node_tree)
            delete_tree(tree=self._obj_tree_cl.obj_tree)
            delete_tree(tree=self._wx_tree_cl.wx_tree)

    def _scroll_to_end(self):
        if self._autoscroll_var.get():
            self.text_widget.see(tk.END)

    #####################################################
    def _add_thread_gc(self, thread):
        if hasattr(self._root_cl, 'add_thread_gc'):
            self._root_cl.add_thread_gc(thread)

    def destroy_win(self):
        self._close_me()

    def destroy(self):
        self.destroy_win()

    def _close_me(self):
        if self._quit:
            return

        # Threads stoppen signalisieren
        self._map_widget.running = False
        self._map_widget.image_load_queue_tasks = []
        self._map_widget.image_load_queue_results = []
        for thread in self._map_widget.get_threads():
            self._add_thread_gc(thread)
        self._root_cl.toplevel_manager.aprs_mon_win = None
        self._root_cl.add_win_gc(self)
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

            self.destroy()
            self.is_destroyed = True

    def all_dead(self):
        map_threads = self._map_widget.get_threads()
        return all(not thread.is_alive() for thread in map_threads)

    # ==========================================
    def get_ais_obj(self):
        return self._ais_obj