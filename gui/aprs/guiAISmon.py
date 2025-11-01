import datetime
import gc
import time
import random
import tkinter as tk

from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from ax25.ax25InitPorts import PORT_HANDLER
from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from cfg.constant import FONT, APRS_INET_PORT_ID, APRS_MAX_TREE_ITEMS
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import tk_filter_bad_chars, get_strTab
from gui.MapView.tkMapView_override import SafeTkinterMapView


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
        self._ais_obj                = PORT_HANDLER.get_aprs_ais()
        self._aprs_icon_tab_16       = root_win.get_aprs_icon_tab_16()
        self._aprs_icon_tab_24       = root_win.get_aprs_icon_tab_24()
        self._call_filter_list       = []
        self._sort_rev               = False
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
        self._set_node_c = lambda n: f"Total Nodes: {n}"
        ##############################################
        self._autoscroll_var        = tk.BooleanVar(self, value=True)
        self._call_filter           = tk.BooleanVar(self, value=False)
        self._call_filter_calls_var = tk.StringVar(self)
        self._port_filter_var       = tk.StringVar(self,  value='')
        self._node_count_label_var  = tk.StringVar(self,  value=self._set_node_c(0))
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
        pack_list_f = ttk.Frame(tab)
        node_list_f = ttk.Frame(tab)
        obj_list_f  = ttk.Frame(tab)
        wx_list_f   = ttk.Frame(tab)
        msg_list_f  = ttk.Frame(tab)
        bl_list_f   = ttk.Frame(tab)
        pack_list_f.pack(fill='both', expand=True)
        node_list_f.pack(fill='both', expand=True)
        obj_list_f.pack( fill='both', expand=True)
        wx_list_f.pack(  fill='both', expand=True)
        msg_list_f.pack( fill='both', expand=True)
        bl_list_f.pack(  fill='both', expand=True)
        ##############################################
        tab.add(node_list_f, text="Node-List")
        tab.add(obj_list_f,  text="Objects")
        tab.add(wx_list_f,   text="WX")
        tab.add(msg_list_f,  text="Msg")
        tab.add(bl_list_f,   text="Bulletin")
        tab.add(pack_list_f, text="Packet-Monitor")
        ##############################################
        ttk.Label(tree_f, text='Port-Filter:').pack(side='left', anchor='w', padx=10)
        opt = [
                  "",
                  "",
                  APRS_INET_PORT_ID,
              ] + [str(el) for el in list(POPT_CFG.get_port_CFGs().keys())]
        port_filter_m = ttk.OptionMenu(tree_f,
                                       self._port_filter_var,
                                       *opt,
                                       command=lambda e: self._chk_port_filter())
        port_filter_m.pack(side='left', padx=0)
        ##############################################
        # Frame für den linken Bereich
        columns = (
            'from',
            'to',
            'port',
            'via',
            'path',
            'loc',
            'typ',
            'rx_time',
            'comment',
            'raw',
        )
        self._mon_tree = ttk.Treeview(pack_list_f, columns=columns, show='tree headings')
        self._mon_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(pack_list_f, orient='vertical', command=self._mon_tree.yview)
        self._mon_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._mon_tree.heading('#0', text='Symbol')
        self._mon_tree.heading('from', text=self._getTabStr('from'), command=lambda: self._sort_entry('from', self._mon_tree))
        self._mon_tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry('to', self._mon_tree))
        self._mon_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self._mon_tree))
        self._mon_tree.heading('via', text='VIA', command=lambda: self._sort_entry('via', self._mon_tree))
        self._mon_tree.heading('path', text='Path', command=lambda: self._sort_entry('path', self._mon_tree))
        self._mon_tree.heading('loc', text='Locator', command=lambda: self._sort_entry('loc', self._mon_tree))
        self._mon_tree.heading('typ', text='Typ', command=lambda: self._sort_entry('typ', self._mon_tree))
        self._mon_tree.heading('rx_time', text=self._getTabStr('date_time'), command=lambda: self._sort_entry('rx_time', self._mon_tree))
        self._mon_tree.heading('comment', text=self._getTabStr('message'), command=lambda: self._sort_entry('comment', self._mon_tree))
        self._mon_tree.heading('raw', text='RAW', command=lambda: self._sort_entry('raw', self._mon_tree))
        self._mon_tree.column('#0', anchor='w', stretch=False, width=50)
        self._mon_tree.column("from", anchor='w', stretch=False, width=80)
        self._mon_tree.column("to", anchor='w', stretch=False, width=80)
        self._mon_tree.column("port", anchor='w', stretch=False, width=60)
        self._mon_tree.column("via", anchor='w', stretch=False, width=80)
        self._mon_tree.column("path", anchor='w', stretch=False, width=200)
        self._mon_tree.column("loc", anchor='w', stretch=False, width=120)
        self._mon_tree.column("typ", anchor='w', stretch=False, width=100)
        self._mon_tree.column("rx_time", anchor='w', stretch=False, width=70)
        self._mon_tree.column("comment", anchor='w', stretch=True, width=20)
        self._mon_tree.column("raw", anchor='w', stretch=True, width=20)
        ##############################################
        # PW für den rechten Bereich
        tab2 = ttk.Notebook(mon_f)
        tab2.pack(fill='both', expand=True)
        ##############################################
        mon_tab_f = ttk.Frame(tab2)
        map_tab_f = ttk.Frame(tab2)

        mon_tab_f.pack(fill='both', expand=True)
        map_tab_f.pack(fill='both', expand=True)

        tab2.add(mon_tab_f, text="Monitor")
        tab2.add(map_tab_f, text="Map")
        ##############################################
        # Monitor
        left_frame  = ttk.Frame(mon_tab_f)
        l1_frame    = ttk.Frame(mon_tab_f)
        l2_frame    = ttk.Frame(mon_tab_f)

        left_frame.pack( padx=5, pady=5, fill='both', expand=True)
        l1_frame   .pack(padx=5,         fill='x',    expand=False)
        l2_frame   .pack(padx=5,         fill='x',    expand=False)

        self._text_widget = ScrolledText(left_frame,
                                         background='black',
                                         foreground='green',
                                         width=85
                                         )
        self._text_widget.configure(font=(FONT, self._text_size))
        self._text_widget.pack(fill='both', expand=True)

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
        ttk.Entry(l2_frame   ,
                 textvariable=self._call_filter_calls_var,
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
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        lat, lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)

        # Setze die anfängliche Position und Zoom-Level (z. B. Europa)
        self._map_widget.set_position(lat, lon)  # Paris als Startpunkt
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
        # Node-List
        h_frame = ttk.Frame(node_list_f)
        h_frame.pack(fill='x', expand=False)
        ttk.Label(h_frame, textvariable=self._node_count_label_var).pack(side='left', anchor='w', padx=10)
        #
        columns = (
            'node_id',
            'port',
            'via',
            'path',
            'loc',
            'dist',
            'm_cap',
            'rx_time',
        )
        self._node_tree = ttk.Treeview(node_list_f, columns=columns, show='tree headings')
        self._node_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(node_list_f, orient='vertical', command=self._node_tree.yview)
        self._node_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._node_tree.heading('#0',       text='Symbol')
        self._node_tree.heading('node_id',  text="ID", command=lambda: self._sort_entry('node_id', self._node_tree))
        self._node_tree.heading('port',     text="Port", command=lambda: self._sort_entry('port', self._node_tree))
        self._node_tree.heading('via',      text="VIA", command=lambda: self._sort_entry('via', self._node_tree))
        self._node_tree.heading('path',     text="Path", command=lambda: self._sort_entry('path', self._node_tree))
        self._node_tree.heading('loc',      text="Locator", command=lambda: self._sort_entry('loc', self._node_tree))
        self._node_tree.heading('dist',     text="km", command=lambda: self._sort_entry('dist', self._node_tree))
        self._node_tree.heading('m_cap',    text="MSG capable", command=lambda: self._sort_entry('m_cap', self._node_tree))
        self._node_tree.heading('rx_time',  text=self._getTabStr('date_time'), command=lambda: self._sort_entry('rx_time', self._node_tree))

        self._node_tree.column('#0',       anchor='w', stretch=False, width=50)
        self._node_tree.column("node_id",  anchor='w', stretch=False, width=80)
        self._node_tree.column("port",     anchor='w', stretch=False, width=60)
        self._node_tree.column("via",      anchor='w', stretch=False, width=80)
        self._node_tree.column("path",     anchor='w', stretch=True,  width=80)
        self._node_tree.column("loc",      anchor='w', stretch=False, width=90)
        self._node_tree.column("dist",     anchor='w', stretch=False, width=50)
        self._node_tree.column("m_cap",    anchor='w', stretch=False, width=80)
        self._node_tree.column("rx_time",  anchor='w', stretch=False, width=80)
        #self._node_tree.bind('<<TreeviewSelect>>', self._node_entry_selected)

        ########################################################
        columns = (
            'node_id',
            'via',
            'port',
            'loc',
            'dist',
            'rx_time',
            'comment',
        )
        self._obj_tree = ttk.Treeview(obj_list_f, columns=columns, show='tree headings')
        self._obj_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(obj_list_f, orient='vertical', command=self._obj_tree.yview)
        self._obj_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._obj_tree.heading('#0', text='Symbol')
        self._obj_tree.heading('node_id', text="ID", command=lambda: self._sort_entry('node_id', self._obj_tree))
        self._obj_tree.heading('via', text="Reporter", command=lambda: self._sort_entry('via', self._obj_tree))
        self._obj_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self._obj_tree))
        self._obj_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self._obj_tree))
        self._obj_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self._obj_tree))
        self._obj_tree.heading('rx_time', text=self._getTabStr('date_time'),
                                command=lambda: self._sort_entry('rx_time', self._obj_tree))
        self._obj_tree.heading('comment', text="Comment", command=lambda: self._sort_entry('comment', self._obj_tree))

        self._obj_tree.column('#0', anchor='w', stretch=False, width=50)
        self._obj_tree.column("node_id", anchor='w', stretch=False, width=80)
        self._obj_tree.column("via", anchor='w', stretch=False, width=80)
        self._obj_tree.column("port", anchor='w', stretch=False, width=60)
        self._obj_tree.column("loc", anchor='w', stretch=False, width=90)
        self._obj_tree.column("dist", anchor='w', stretch=False, width=50)
        self._obj_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self._obj_tree.column("comment", anchor='w', stretch=True, width=80)
        ########################################################
        # WX
        columns = (
            'node_id',
            'port',
            'via',
            'loc',
            'dist',
            'rx_time',
            'comment',
        )
        self._wx_tree = ttk.Treeview(wx_list_f, columns=columns, show='tree headings')
        self._wx_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(wx_list_f, orient='vertical', command=self._wx_tree.yview)
        self._wx_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._wx_tree.heading('#0', text='Symbol')
        self._wx_tree.heading('node_id', text="ID", command=lambda: self._sort_entry('node_id', self._wx_tree))
        self._wx_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self._wx_tree))
        self._wx_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self._wx_tree))
        self._wx_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self._wx_tree))
        self._wx_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self._wx_tree))
        self._wx_tree.heading('rx_time', text=self._getTabStr('date_time'),
                               command=lambda: self._sort_entry('rx_time', self._wx_tree))
        self._wx_tree.heading('comment', text="Data", command=lambda: self._sort_entry('comment', self._wx_tree))

        self._wx_tree.column('#0', anchor='w', stretch=False, width=50)
        self._wx_tree.column("node_id", anchor='w', stretch=False, width=80)
        self._wx_tree.column("port", anchor='w', stretch=False, width=60)
        self._wx_tree.column("via", anchor='w', stretch=False, width=80)
        self._wx_tree.column("loc", anchor='w', stretch=False, width=90)
        self._wx_tree.column("dist", anchor='w', stretch=False, width=50)
        self._wx_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self._wx_tree.column("comment", anchor='w', stretch=True, width=80)
        ########################################################
        # P MSG
        columns = (
            'node_id',
            'to',
            'port',
            'via',
            'path',
            'loc',
            'dist',
            'rx_time',
            'comment',
        )
        self._msg_tree = ttk.Treeview(msg_list_f, columns=columns, show='tree headings')
        self._msg_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(msg_list_f, orient='vertical', command=self._msg_tree.yview)
        self._msg_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._msg_tree.heading('#0', text='Symbol')
        self._msg_tree.heading('node_id', text=self._getTabStr('from'), command=lambda: self._sort_entry('node_id', self._msg_tree))
        self._msg_tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry('to', self._msg_tree))
        self._msg_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self._msg_tree))
        self._msg_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self._msg_tree))
        self._msg_tree.heading('path', text="Path", command=lambda: self._sort_entry('path', self._msg_tree))
        self._msg_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self._msg_tree))
        self._msg_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self._msg_tree))
        self._msg_tree.heading('rx_time', text=self._getTabStr('date_time'),
                               command=lambda: self._sort_entry('rx_time', self._msg_tree))
        self._msg_tree.heading('comment', text="Msg", command=lambda: self._sort_entry('comment', self._msg_tree))

        self._msg_tree.column('#0', anchor='w', stretch=False, width=50)
        self._msg_tree.column("node_id", anchor='w', stretch=False, width=80)
        self._msg_tree.column("to", anchor='w', stretch=False, width=80)
        self._msg_tree.column("port", anchor='w', stretch=False, width=60)
        self._msg_tree.column("via", anchor='w', stretch=False, width=80)
        self._msg_tree.column("path", anchor='w', stretch=False, width=200)
        self._msg_tree.column("loc", anchor='w', stretch=False, width=90)
        self._msg_tree.column("dist", anchor='w', stretch=False, width=50)
        self._msg_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self._msg_tree.column("comment", anchor='w', stretch=True, width=80)
        ########################################################
        # Bulletin
        columns = (
            'node_id',
            'to',
            'port',
            'via',
            'path',
            'loc',
            'dist',
            'rx_time',
            'comment',
        )
        self._bl_tree = ttk.Treeview(bl_list_f, columns=columns, show='tree headings')
        self._bl_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(bl_list_f, orient='vertical', command=self._bl_tree.yview)
        self._bl_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._bl_tree.heading('#0', text='Symbol')
        self._bl_tree.heading('node_id', text="BL ID",
                               command=lambda: self._sort_entry('node_id', self._bl_tree))
        self._bl_tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry('to', self._bl_tree))
        self._bl_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self._bl_tree))
        self._bl_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self._bl_tree))
        self._bl_tree.heading('path', text="Path", command=lambda: self._sort_entry('path', self._bl_tree))
        self._bl_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self._bl_tree))
        self._bl_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self._bl_tree))
        self._bl_tree.heading('rx_time', text=self._getTabStr('date_time'),
                               command=lambda: self._sort_entry('rx_time', self._bl_tree))
        self._bl_tree.heading('comment', text="Msg", command=lambda: self._sort_entry('comment', self._bl_tree))

        self._bl_tree.column('#0', anchor='w', stretch=False, width=50)
        self._bl_tree.column("node_id", anchor='w', stretch=False, width=80)
        self._bl_tree.column("to", anchor='w', stretch=False, width=80)
        self._bl_tree.column("port", anchor='w', stretch=False, width=60)
        self._bl_tree.column("via", anchor='w', stretch=False, width=80)
        self._bl_tree.column("path", anchor='w', stretch=False, width=200)
        self._bl_tree.column("loc", anchor='w', stretch=False, width=90)
        self._bl_tree.column("dist", anchor='w', stretch=False, width=50)
        self._bl_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self._bl_tree.column("comment", anchor='w', stretch=True, width=80)
        ########################################################
        self.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())
        ########################################################
        self._bl_tree.bind(  '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._bl_tree))
        self._msg_tree.bind( '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._msg_tree))
        self._obj_tree.bind( '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._obj_tree))
        self._mon_tree.bind( '<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._mon_tree))
        self._node_tree.bind('<<TreeviewSelect>>', lambda e: self._draw_connection(e, self._node_tree))

        if self._ais_obj is not None:
            own_call = POPT_CFG.get_CFG_aprs_ais().get('ais_call', '')
            if own_call:
                self._call_filter_list.append(own_call)
                self._call_filter_calls_var.set(own_call)

        self._node_tree_init()
        self._obj_tree_init()
        self._init_ais_mon()
        root_win.aprs_mon_win = self


    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        if tree == self._mon_tree:
            return
        if True:
            """Disabled"""
            return
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    @staticmethod
    def _del_tree(tree):
        for i in tree.get_children():
            tree.delete(i)


    def _add_to_tree(self, tree_data: tuple, tree, add_to_end=True, auto_scroll=True, replace_ent=False, prio=True):
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
    # Obj Tree
    def _obj_tree_init(self):
        if not hasattr(self._ais_obj, 'get_obj_tab'):
            return
        obj_tab: dict = self._ais_obj.get_obj_tab()
        port_filter   = self._port_filter_var.get()
        n = APRS_MAX_TREE_ITEMS
        for node_id, ent in dict(obj_tab).items():
            port = ent.get('port_id', '')
            if port_filter and port_filter != port:
                continue
            tree_data = self._get_treedata_fm_obj_tab(ent)
            if not tree_data:
                continue
            self._add_to_tree(tree_data, tree=self._obj_tree, replace_ent=True, prio=False)
            n -= 1
            if not n:
                break

    @staticmethod
    def _get_treedata_fm_obj_tab(obj_tab_ent: dict):
        node_id = obj_tab_ent.get('node_id', '')
        if not node_id:
            return ()
        return (
            obj_tab_ent.get('node_id', ''),
            obj_tab_ent.get('reporter', ''),
            obj_tab_ent.get('port_id', ''),
            obj_tab_ent.get('locator', ''),
            round(obj_tab_ent.get('distance', -1)),
            obj_tab_ent.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
            obj_tab_ent.get('comment', ''),
            obj_tab_ent.get('symbol', ('', '')),
        )

    def _obj_tree_update(self, object_ent: dict):
        node_id     = object_ent.get('node_id', '')
        port_filter = self._port_filter_var.get()
        port = object_ent.get('port_id', '')

        if port_filter and port_filter != port:
            return
        selected_node_ids = []
        for selected_item in self._obj_tree.selection():
            selected_node_ids.append(self._obj_tree.set(selected_item, 'node_id'))

        """
        items = list(self._obj_tree.get_children())
        list_len = len(items)
        for index, item in enumerate(items):
            if self._obj_tree.set(item, 'node_id') == node_id:
                self._obj_tree.delete(item)
                break
        """
        items = list(self._obj_tree.get_children())
        list_len = len(items)
        auto_scroll = list_len == len(list(self._obj_tree.get_children()))
        tree_data = self._get_treedata_fm_obj_tab(object_ent)
        if tree_data:
            self._add_to_tree(tree_data,
                              tree=self._obj_tree,
                              add_to_end=False,
                              auto_scroll=auto_scroll,
                              replace_ent=True,
                              prio=False)

        if node_id in selected_node_ids:
            for item in self._obj_tree.get_children():
                if self._obj_tree.set(item, 'node_id') == node_id:
                    self._obj_tree.selection_add(item)
                    break
    #############################################################
    # Node Tree
    def _node_tree_init(self):
        if not hasattr(self._ais_obj, 'get_node_tab'):
            return
        node_tab: dict = self._ais_obj.get_node_tab()
        port_filter = self._port_filter_var.get()
        c = 0
        for node_id, ent in dict(node_tab).items():
            port = ent.get('port_id', '')
            if port_filter and port_filter != port:
                continue
            tree_data = self._get_treedata_fm_node_tab(ent)
            if not tree_data:
                continue
            self._add_to_tree(tree_data, tree=self._node_tree, replace_ent=True)
            c += 1
        self._node_count_label_var.set(self._set_node_c(c))

    def _node_tree_update(self, node_tab_ent: dict, object_ent: dict):
        node_id     = node_tab_ent.get('node_id', '')
        port_filter = self._port_filter_var.get()
        port = node_tab_ent.get('port_id', '')

        if port_filter and port_filter != port:
            items = list(self._node_tree.get_children())
            self._node_count_label_var.set(self._set_node_c(len(items)))
            return
        selected_node_ids = []
        for selected_item in self._node_tree.selection():
            selected_node_ids.append(self._node_tree.set(selected_item, 'node_id'))

        items = list(self._node_tree.get_children())
        list_len = len(items)
        """
        for index, item in enumerate(items):
            if self._node_tree.set(item, 'node_id') == node_id:
                self._node_tree.delete(item)
                break
        """
        auto_scroll = list_len == len(list(self._node_tree.get_children()))
        tree_data = self._get_treedata_fm_node_tab(node_tab_ent)
        if tree_data:
            self._add_to_tree(tree_data, tree=self._node_tree, add_to_end=False, auto_scroll=auto_scroll, replace_ent=True)

        items = list(self._node_tree.get_children())
        self._node_count_label_var.set(self._set_node_c(len(items)))
        if node_id in selected_node_ids:
            for item in self._node_tree.get_children():
                if self._node_tree.set(item, 'node_id') == node_id:
                    self._node_tree.selection_add(item)
                    break

        if object_ent:
            self._obj_tree_update(object_ent)

    @staticmethod
    def _get_treedata_fm_node_tab(node_tab_ent: dict):
        node_id = node_tab_ent.get('node_id', '')
        if not node_id:
            return ()
        return (
                node_tab_ent.get('node_id', ''),
                node_tab_ent.get('port_id', ''),
                node_tab_ent.get('via', ''),
                '>'.join(node_tab_ent.get('path', [])),
                node_tab_ent.get('locator', ''),
                round(node_tab_ent.get('distance', -1)),
                node_tab_ent.get('message_capable', False),
                node_tab_ent.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
                node_tab_ent.get('symbol', ('', '')),
        )

    def _node_entry_selected(self):
        self._call_filter_list = []
        for selected_item in self._node_tree.selection():
            item = self._node_tree.item(selected_item)
            node_id = item['values'][0]
            self._call_filter_list.append(node_id)

        if self._call_filter_list:
            old_call_filter = list(self._call_filter_calls_var.get(). split(' '))
            old_call_filter.sort()
            new_call_filter = list(self._call_filter_list)
            new_call_filter.sort()
            if old_call_filter != new_call_filter:
                #self._call_filter.set(True)
                self._call_filter_calls_var.set(' '.join(new_call_filter))
            self._text_widget.delete(0.0, 'end')
            self._init_ais_mon(init_tree=False)

    #############################################################
    # WX Tree (init in _init_ais_mon)
    def _get_treedata_fm_wx_pack(self, aprs_pack: dict):
        wx_data = ' - '.join([f"{k}: {val}" for k, val in aprs_pack.get('weather', {}).items()])
        symbol  =  self._get_symbol_fm_node_tab(aprs_pack.get('from', ''))
        return (
            aprs_pack.get('from', ''),
            aprs_pack.get('port_id', ''),
            aprs_pack.get('via', ''),
            aprs_pack.get('locator', ''),
            round(aprs_pack.get('distance', -1)),
            aprs_pack.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
            wx_data,
            symbol,
        )

    def _wx_tree_update(self, aprs_pack: dict):
        if not aprs_pack.get('weather', {}):
            return
        node_id = aprs_pack.get('from', '')
        if not node_id:
            return
        port_filter = self._port_filter_var.get()
        port = aprs_pack.get('port_id', '')

        if port_filter and port_filter != port:
            return
        selected_node_ids = []
        for selected_item in self._wx_tree.selection():
            selected_node_ids.append(self._wx_tree.set(selected_item, 'node_id'))

        items    = list(self._wx_tree.get_children())
        list_len = len(items)
        """
        for index, item in enumerate(items):
            if self._wx_tree.set(item, 'node_id') == node_id:
                self._wx_tree.delete(item)
                break
        """

        auto_scroll = list_len == len(list(self._wx_tree.get_children()))
        tree_data   = self._get_treedata_fm_wx_pack(aprs_pack)
        if tree_data:
            self._add_to_tree(tree_data, tree=self._wx_tree, add_to_end=False, auto_scroll=auto_scroll, replace_ent=True)

        if node_id in selected_node_ids:
            for item in self._wx_tree.get_children():
                if self._wx_tree.set(item, 'node_id') == node_id:
                    self._wx_tree.selection_add(item)
                    break

    #############################################################
    # MSG Tree (init in _init_ais_mon)
    def _get_treedata_fm_msg_pack(self, aprs_pack: dict):
        symbol  =  self._get_symbol_fm_node_tab(aprs_pack.get('from', ''))
        msg_text = aprs_pack.get('message_text', '')
        if not msg_text and aprs_pack.get('response', ''):
            msg_text = f"{aprs_pack.get('response', '')} {aprs_pack.get('msgNo', '')}"
        return (
            aprs_pack.get('from', ''),
            aprs_pack.get('address', '') if aprs_pack.get('address', '') else aprs_pack.get('to', ''),
            aprs_pack.get('port_id', ''),
            aprs_pack.get('via', ''),
            '>'.join(aprs_pack.get('path', [])),
            aprs_pack.get('locator', ''),
            round(aprs_pack.get('distance', -1)),
            aprs_pack.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
            msg_text,
            symbol,
        )

    def _msg_tree_update(self, aprs_pack: dict):
        if aprs_pack.get('format', '') != 'message':
            return
        node_id = aprs_pack.get('from', '')
        if not node_id:
            return
        port_filter = self._port_filter_var.get()
        port = aprs_pack.get('port_id', '')

        if port_filter and port_filter != port:
            return
        selected_node_ids = []
        for selected_item in self._msg_tree.selection():
            selected_node_ids.append(self._msg_tree.set(selected_item, 'node_id'))

        tree_data   = self._get_treedata_fm_msg_pack(aprs_pack)
        if tree_data:
            self._add_to_tree(tree_data, tree=self._msg_tree, add_to_end=False, auto_scroll=True, replace_ent=False)

        if node_id in selected_node_ids:
            for item in self._msg_tree.get_children():
                if self._msg_tree.set(item, 'node_id') == node_id:
                    self._msg_tree.selection_add(item)
                    break

    #############################################################
    # BL Tree (init in _init_ais_mon)
    def _get_treedata_fm_bl_pack(self, aprs_pack: dict):
        symbol   =  self._get_symbol_fm_node_tab(aprs_pack.get('from', ''))
        msg_text = aprs_pack.get('message_text', '')
        return (
            aprs_pack.get('from', ''),
            aprs_pack.get('msgNo', ''),
            aprs_pack.get('port_id', ''),
            aprs_pack.get('via', ''),
            '>'.join(aprs_pack.get('path', [])),
            aprs_pack.get('locator', ''),
            round(aprs_pack.get('distance', -1)),
            aprs_pack.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
            msg_text,
            symbol,
        )

    def _bl_tree_update(self, aprs_pack: dict):
        if aprs_pack.get('format', '') != 'bulletin':
            return
        node_id = aprs_pack.get('from', '')
        if not node_id:
            return
        port_filter = self._port_filter_var.get()
        port = aprs_pack.get('port_id', '')

        if port_filter and port_filter != port:
            return
        selected_node_ids = []
        for selected_item in self._bl_tree.selection():
            selected_node_ids.append(self._bl_tree.set(selected_item, 'node_id'))

        tree_data = self._get_treedata_fm_bl_pack(aprs_pack)
        if tree_data:
            self._add_to_tree(tree_data, tree=self._bl_tree, add_to_end=False, auto_scroll=True, replace_ent=False)

        if node_id in selected_node_ids:
            for item in self._bl_tree.get_children():
                if self._bl_tree.set(item, 'node_id') == node_id:
                    self._bl_tree.selection_add(item)
                    break

    #############################################################
    def _init_ais_mon(self, init_tree=True):
        if not self._ais_obj:
            self._text_widget.insert(tk.END, "*** ERROR: No AIS found ***")
            logger.error("*** ERROR: No AIS found ***")
            return
        tr              = False
        call_filter_var = self._call_filter.get()
        port_filter     = self._port_filter_var.get()
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
                    self._add_to_tree(tree_data=tree_data,
                                      tree=self._mon_tree,
                                      add_to_end=False,
                                      replace_ent=False,
                                      prio=False)
                if el.get('weather', {}):
                    wx_tree_data = self._get_treedata_fm_wx_pack(el)
                    if wx_tree_data:
                        self._add_to_tree(tree_data=wx_tree_data,
                                          tree=self._wx_tree,
                                          add_to_end=False,
                                          replace_ent=True)
                elif el.get('format', '') == 'message':
                    msg_tree_data = self._get_treedata_fm_msg_pack(el)
                    if msg_tree_data:
                        self._add_to_tree(tree_data=msg_tree_data,
                                          tree=self._msg_tree,
                                          add_to_end=False,
                                          replace_ent=False)
                elif el.get('format', '') == 'bulletin':
                    bl_tree_data = self._get_treedata_fm_bl_pack(el)
                    if bl_tree_data:
                        self._add_to_tree(tree_data=bl_tree_data,
                                          tree=self._bl_tree,
                                          add_to_end=False,
                                          replace_ent=False)
            # self._add_treedata(tree_data)
            # Monitor

            if call_filter_var:
                if el.get('from', '') in self._call_filter_list:
                    tr = True
                    tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc)
                    self._text_widget.insert(tk.END, tmp)
            else:
                tr = True
                tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc)
                self._text_widget.insert(tk.END, tmp)
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
        port_filter = self._port_filter_var.get()
        if port_filter and port_filter != pack.get('port_id', ''):
            return
        tr = False
        tree_data = self._get_treedata_fm_pack(pack)
        #self._add_treedata(tree_data)
        self._add_to_tree(tree_data, tree=self._mon_tree, add_to_end=False, replace_ent=False, prio=False)
        if self._call_filter.get():
            if pack['from'] in self._call_filter_list:
                tr = True
                tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc)
                tmp = tk_filter_bad_chars(tmp)
                self._text_widget.insert(tk.END, tmp)
                self._wx_tree_update(pack)
                self._msg_tree_update(pack)
                self._bl_tree_update(pack)
        else:
            tr = True
            tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc)
            tmp = tk_filter_bad_chars(tmp)
            self._text_widget.insert(tk.END, tmp)
            self._wx_tree_update(pack)
            self._msg_tree_update(pack)
            self._bl_tree_update(pack)
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
        self._node_tree_update(node_tab_ent, object_ent)

    #######################################
    # MAP
    def _get_station_icon(self, call: str):
        default_icon    = self._aprs_icon_tab_24.get(('\\', 'X'), None)
        user_db         = self._get_userDB()

        if not hasattr(user_db, 'get_typ'):
            logger.error("not hasattr(user_db, 'get_typ')")
            return default_icon
        symbol   = self._get_symbol_fm_node_tab(call) # ('', '')
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
        if tree == self._node_tree:
            self._node_entry_selected()
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
    ##########################

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
        self._ais_obj = PORT_HANDLER.get_aprs_ais()

    def _get_symbol_fm_node_tab(self, node_id: str):
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
        self._text_widget.configure(font=(FONT, self._text_size))

    def _decrease_textsize(self):
        self._text_size -= 1
        self._text_size = max(self._text_size, 3)
        self._text_widget.configure(font=(FONT, self._text_size))

    def _chk_call_filter(self):
        self._call_filter_list = []
        if self._ais_obj is not None:
            own_call = POPT_CFG.get_CFG_aprs_ais().get('ais_call', '')
            if own_call:
                self._call_filter_list.append(own_call)

        calls = self._call_filter_calls_var.get()
        calls = calls.split(' ')
        tmp = []
        for el in list(calls):
            if el:
                tmp.append(el.upper())
        calls = tmp
        self._call_filter_list = self._call_filter_list + calls

    def _chk_port_filter(self):
        self._text_widget.delete(0.0, tk.END)
        self._del_tree(tree=self._mon_tree)
        self._del_tree(tree=self._node_tree)
        self._del_tree(tree=self._obj_tree)
        self._del_tree(tree=self._wx_tree)
        self._init_ais_mon()
        self._node_tree_init()
        self._obj_tree_init()

    def _reset_filter(self):
        self._call_filter_list = []
        self._call_filter.set(False)
        self._call_filter_calls_var.set('')
        self._text_widget.delete(0.0, tk.END)
        self._del_tree(tree=self._mon_tree)
        self._del_tree(tree=self._node_tree)
        self._del_tree(tree=self._obj_tree)
        self._del_tree(tree=self._wx_tree)
        self._init_ais_mon()
        self._node_tree_init()
        self._obj_tree_init()

    def _del_buffer(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'),
                                  parent=self):
            if hasattr(self._ais_obj, 'del_ais_rx_buff'):
                self._ais_obj.del_ais_rx_buff()
            self._text_widget.delete(0.0, tk.END)
            self._del_tree(tree=self._mon_tree)
            self._del_tree(tree=self._node_tree)
            self._del_tree(tree=self._obj_tree)
            self._del_tree(tree=self._wx_tree)

    def _scroll_to_end(self):
        if self._autoscroll_var.get():
            self._text_widget.see(tk.END)

    """
    def _destroy_win(self):
        # self.tasker = lambda: 0
        self._map_widget.running   = False
        #while self._map_widget.pre_cache_thread.is_alive():
        #    print('wait')
        #    time.sleep(0.04)
        #self._map_widget.delete_all_path()
        #self._map_widget.delete_all_marker()
        #self._map_widget.delete_all_polygon()
        self._map_widget.destroy()
        #self._map_widget = None
        self._root_cl.aprs_mon_win = None
        # self._ais_obj.ais_rx_buff = self._tmp_buffer + self._ais_obj.ais_rx_buff
        self.destroy()
    """
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
        self._root_cl.aprs_mon_win = None
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
