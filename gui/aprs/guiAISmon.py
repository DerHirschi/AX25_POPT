import datetime
import time
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from ax25.ax25InitPorts import PORT_HANDLER
from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from cfg.constant import FONT, APRS_INET_PORT_ID
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import build_aprs_icon_tab
from fnc.str_fnc import tk_filter_bad_chars, get_strTab


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
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
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
        self._ais_obj               = PORT_HANDLER.get_aprs_ais()
        self._aprs_icon_tab         = root_win.get_aprs_icon_tab_16()
        self._call_filter_list      = []
        self._sort_rev              = False
        ####
        self._tasker_q_timer        = time.time()
        self._tasker_q              = []
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
        self._tree = ttk.Treeview(pack_list_f, columns=columns, show='tree headings')
        self._tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(pack_list_f, orient='vertical', command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._tree.heading('#0',      text='Symbol')
        self._tree.heading('from',    text=self._getTabStr('from'),      command=lambda: self._sort_entry('from', self._tree))
        self._tree.heading('to',      text=self._getTabStr('to'),        command=lambda: self._sort_entry('to', self._tree))
        self._tree.heading('port',    text="Port",                       command=lambda: self._sort_entry('port', self._tree))
        self._tree.heading('via',     text='VIA',                        command=lambda: self._sort_entry('via', self._tree))
        self._tree.heading('path',    text='Path',                       command=lambda: self._sort_entry('path', self._tree))
        self._tree.heading('loc',     text='Locator',                    command=lambda: self._sort_entry('loc', self._tree))
        self._tree.heading('typ',     text='Typ',                        command=lambda: self._sort_entry('typ', self._tree))
        self._tree.heading('rx_time', text=self._getTabStr('date_time'), command=lambda: self._sort_entry('rx_time', self._tree))
        self._tree.heading('comment', text=self._getTabStr('message'),   command=lambda: self._sort_entry('comment', self._tree))
        self._tree.heading('raw',     text='RAW',                        command=lambda: self._sort_entry('raw', self._tree))
        self._tree.column('#0',       anchor='w', stretch=False, width=50)
        self._tree.column("from",     anchor='w', stretch=False, width=80)
        self._tree.column("to",       anchor='w', stretch=False, width=80)
        self._tree.column("port",     anchor='w', stretch=False, width=60)
        self._tree.column("via",      anchor='w', stretch=False, width=80)
        self._tree.column("path",     anchor='w', stretch=False, width=200)
        self._tree.column("loc",      anchor='w', stretch=False, width=120)
        self._tree.column("typ",      anchor='w', stretch=False, width=100)
        self._tree.column("rx_time",  anchor='w', stretch=False, width=70)
        self._tree.column("comment",  anchor='w', stretch=True,  width=20)
        self._tree.column("raw",      anchor='w', stretch=True,  width=20)
        ##############################################
        # Frame für den rechten Bereich
        left_frame  = ttk.Frame(mon_f)
        l1_frame    = ttk.Frame(mon_f)
        l2_frame    = ttk.Frame(mon_f)

        left_frame.pack( padx=5, pady=5, fill='both', expand=True)
        l1_frame   .pack(padx=5,         fill='x',    expand=True)
        l2_frame   .pack(padx=5,         fill='x',    expand=True)

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
        """
        ttk.Checkbutton(l1_frame   ,
                       variable=self._new_user_var,
                       text="UserDB      ",
                       command=self._chk_new_user
                       ).pack(side='left', padx=2)
        """
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
        self._node_tree.bind('<<TreeviewSelect>>', self._node_entry_selected)

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


        if self._ais_obj is not None:
            self._call_filter_list.append(self._ais_obj.ais_call)
            self._call_filter_calls_var.set(self._ais_obj.ais_call)
            self._ais_obj.ais_mon_gui = self
            """
            for port_id in self._ais_aprs_stations.keys():
                if self._ais_aprs_stations[port_id].aprs_parm_call:
                    self._ais_aprs_stat_calls.append(
                        self._ais_aprs_stations[port_id].aprs_parm_call
                    )
            """
        root_win.aprs_mon_win = self
        self._init_ais_mon()
        self._node_tree_init()
        self._obj_tree_init()

    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        if tree == self._tree:
            return
        if True:
            """Disabled"""
            return
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))


    """
    def _update_tree(self):
        self._del_tree()
        for ret_ent in self._tree_data:
            self._add_to_tree(tree_data=ret_ent)

    """
    @staticmethod
    def _del_tree(tree):
        for i in tree.get_children():
            tree.delete(i)

    def _add_to_tree(self, tree_data: tuple, tree, add_to_end=True, auto_scroll=True):
        is_scrolled_to_top = tree.yview()[0] == 0.0
        image = self._aprs_icon_tab.get(tree_data[-1], None)
        if add_to_end:
            index = 'end'
        else:
            index = 0

        if image:
            tree.image_ref = image
            tree.insert('', index, values=tree_data[:-1], image=image)
        else:
            tree.insert('', index, values=tree_data[:-1])

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

    """
    def _add_treedata(self, tree_data: tuple):
        self._tree_data = [tree_data] + self._tree_data
        self._tree_data = self._tree_data[:9001] # Over 9000 !!
     """

    #############################################################
    # Obj Tree
    def _obj_tree_init(self):
        if not hasattr(self._ais_obj, 'get_obj_tab'):
            return
        obj_tab: dict = self._ais_obj.get_obj_tab()
        port_filter   = self._port_filter_var.get()
        for node_id, ent in obj_tab.items():
            port = ent.get('port_id', '')
            if port_filter and port_filter != port:
                continue
            tree_data = self._get_treedata_fm_obj_tab(ent)
            if not tree_data:
                continue
            self._add_to_tree(tree_data, tree=self._obj_tree)

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

        items = list(self._obj_tree.get_children())
        list_len = len(items)
        for index, item in enumerate(items):
            if self._obj_tree.set(item, 'node_id') == node_id:
                self._obj_tree.delete(item)
                break

        auto_scroll = list_len == len(list(self._obj_tree.get_children()))
        tree_data = self._get_treedata_fm_obj_tab(object_ent)
        if tree_data:
            self._add_to_tree(tree_data, tree=self._obj_tree, add_to_end=False, auto_scroll=auto_scroll)

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
        for node_id, ent in node_tab.items():
            port = ent.get('port_id', '')
            if port_filter and port_filter != port:
                continue
            tree_data = self._get_treedata_fm_node_tab(ent)
            if not tree_data:
                continue
            self._add_to_tree(tree_data, tree=self._node_tree)
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
        for index, item in enumerate(items):
            if self._node_tree.set(item, 'node_id') == node_id:
                self._node_tree.delete(item)
                break

        auto_scroll = list_len == len(list(self._node_tree.get_children()))
        tree_data = self._get_treedata_fm_node_tab(node_tab_ent)
        if tree_data:
            self._add_to_tree(tree_data, tree=self._node_tree, add_to_end=False, auto_scroll=auto_scroll)

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

    def _node_entry_selected(self, event=None):
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
                self._call_filter.set(True)
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
        for index, item in enumerate(items):
            if self._wx_tree.set(item, 'node_id') == node_id:
                self._wx_tree.delete(item)
                break

        auto_scroll = list_len == len(list(self._wx_tree.get_children()))
        tree_data   = self._get_treedata_fm_wx_pack(aprs_pack)
        if tree_data:
            self._add_to_tree(tree_data, tree=self._wx_tree, add_to_end=False, auto_scroll=auto_scroll)

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
            aprs_pack.get('addresse', '') if aprs_pack.get('addresse', '') else aprs_pack.get('to', ''),
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
            self._add_to_tree(tree_data, tree=self._msg_tree, add_to_end=False, auto_scroll=True)

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
            self._add_to_tree(tree_data, tree=self._bl_tree, add_to_end=False, auto_scroll=True)

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
        # self._tree_data = []
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
                    self._add_to_tree(tree_data=tree_data, tree=self._tree, add_to_end=False)
                if el.get('weather', {}):
                    wx_tree_data = self._get_treedata_fm_wx_pack(el)
                    if wx_tree_data:
                        self._add_to_tree(tree_data=wx_tree_data, tree=self._wx_tree, add_to_end=False)
                elif el.get('format', '') == 'message':
                    msg_tree_data = self._get_treedata_fm_msg_pack(el)
                    if msg_tree_data:
                        self._add_to_tree(tree_data=msg_tree_data, tree=self._msg_tree, add_to_end=False)
                elif el.get('format', '') == 'bulletin':
                    bl_tree_data = self._get_treedata_fm_bl_pack(el)
                    if bl_tree_data:
                        self._add_to_tree(tree_data=bl_tree_data, tree=self._bl_tree, add_to_end=False)
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

    ###########################################################
    def tasker(self):
        if not self._tasker_q:
            return False
        if time.time() < self._tasker_q_timer:
            return False
        self._tasker_q_timer = time.time() + 0.1
        n = 10
        """
        if len(self._tasker_q) > 10:
            logger.warning(f"len(self._tasker_q) > 10: {len(self._tasker_q)}")
            logger.warning(f"self._tasker_q: {self._tasker_q}")
        """
        while self._tasker_q and n:
            task, arg = self._tasker_q[0]
            self._tasker_q = self._tasker_q[1:]
            if task == 'pack_to_mon':
                self._pack_to_mon_task(arg)
            elif task == 'update_node_tab':
                self._update_node_tab_task(arg)
            n -= 1
        return True

    def _add_tasker_q(self, fnc: str, arg):
        if (fnc, None) in self._tasker_q:
            return
        self._tasker_q.append((fnc, arg))

    def pack_to_mon(self, pack):
        self._add_tasker_q("pack_to_mon", pack)

    def _pack_to_mon_task(self, pack):
        port_filter = self._port_filter_var.get()
        if port_filter and port_filter != pack.get('port_id', ''):
            return
        tr = False
        tree_data = self._get_treedata_fm_pack(pack)
        #self._add_treedata(tree_data)
        self._add_to_tree(tree_data, tree=self._tree , add_to_end=False)
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

    def update_node_tab(self, node_tab_ent: dict, object_ent: dict):
        self._add_tasker_q("update_node_tab", (node_tab_ent, object_ent))

    def _update_node_tab_task(self, arg: tuple):
        node_tab_ent, object_ent = arg
        self._node_tree_update(node_tab_ent, object_ent)

    #######################################
    def set_ais_obj(self):
        self._ais_obj = PORT_HANDLER.get_aprs_ais()

    def _get_symbol_fm_node_tab(self, node_id: str):
        if hasattr(self._ais_obj, 'get_symbol_fm_node_tab'):
            return self._ais_obj.get_symbol_fm_node_tab(node_id)
        return '', ''

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
            self._call_filter_list.append(self._ais_obj.ais_call)

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
        self._del_tree(tree=self._tree)
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
        self._del_tree(tree=self._tree)
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
            self._del_tree(tree=self._tree)
            self._del_tree(tree=self._node_tree)
            self._del_tree(tree=self._obj_tree)
            self._del_tree(tree=self._wx_tree)

    def _scroll_to_end(self):
        if self._autoscroll_var.get():
            self._text_widget.see(tk.END)

    def _destroy_win(self):
        # self.tasker = lambda: 0
        self._ais_obj.ais_mon_gui  = None
        self._root_cl.aprs_mon_win = None
        # self._ais_obj.ais_rx_buff = self._tmp_buffer + self._ais_obj.ais_rx_buff
        self.destroy()
