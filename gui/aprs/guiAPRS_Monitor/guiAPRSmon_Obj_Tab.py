from datetime import datetime
from tkinter import ttk
import tkinter as tk

from cfg.constant import APRS_MAX_TREE_ITEMS
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSmonObjTree(ttk.Frame):
    def __init__(self, parent, aprs_mon_root, port_handler):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        # =================
        self._aprsMon_root = aprs_mon_root
        self._port_handler = port_handler
        self._ais_obj      = port_handler.get_aprs_ais()
        # =================
        self._sort_rev     = False
        # =================
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._set_node_c   = lambda n: f"Total Nodes: {n}"
        # =================
        self._call_filter_list        = self._aprsMon_root.call_filter_list
        self._port_filter_var         = self._aprsMon_root.port_filter_var
        self._call_filter_calls_var   = self._aprsMon_root.call_filter_calls_var
        self._node_count_label_var    = tk.StringVar(self)
        # =================
        columns = (
            'node_id',
            'via',
            'port',
            'loc',
            'dist',
            'rx_time',
            'comment',
        )
        self.obj_tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.obj_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.obj_tree.yview)
        self.obj_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self.obj_tree.heading('#0', text='Symbol')
        self.obj_tree.heading('node_id', text="ID", command=lambda: self._sort_entry('node_id', self.obj_tree))
        self.obj_tree.heading('via', text="Reporter", command=lambda: self._sort_entry('via', self.obj_tree))
        self.obj_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self.obj_tree))
        self.obj_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self.obj_tree))
        self.obj_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self.obj_tree))
        self.obj_tree.heading('rx_time', text=self._getTabStr('date_time'),
                              command=lambda: self._sort_entry('rx_time', self.obj_tree))
        self.obj_tree.heading('comment', text="Comment", command=lambda: self._sort_entry('comment', self.obj_tree))

        self.obj_tree.column('#0', anchor='w', stretch=False, width=50)
        self.obj_tree.column("node_id", anchor='w', stretch=False, width=80)
        self.obj_tree.column("via", anchor='w', stretch=False, width=80)
        self.obj_tree.column("port", anchor='w', stretch=False, width=60)
        self.obj_tree.column("loc", anchor='w', stretch=False, width=90)
        self.obj_tree.column("dist", anchor='w', stretch=False, width=50)
        self.obj_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self.obj_tree.column("comment", anchor='w', stretch=True, width=80)



    #############################################################
    def obj_tree_init(self):
        if not hasattr(self._ais_obj, 'get_obj_tab'):
            return
        obj_tab: dict = self._ais_obj.get_obj_tab()
        port_filter = self._port_filter_var.get()
        n = APRS_MAX_TREE_ITEMS
        for node_id, ent in dict(obj_tab).items():
            port = ent.get('port_id', '')
            if port_filter and port_filter != port:
                continue
            tree_data = self._get_treedata_fm_obj_tab(ent)
            if not tree_data:
                continue
            self._aprsMon_root.add_to_tree(tree_data, tree=self.obj_tree, replace_ent=True, prio=False)
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
            obj_tab_ent.get('rx_time', datetime.now()).strftime('%H:%M:%S'),
            obj_tab_ent.get('comment', ''),
            obj_tab_ent.get('symbol', ('', '')),
        )

    def obj_tree_update(self, object_ent: dict):
        node_id = object_ent.get('node_id', '')
        port_filter = self._port_filter_var.get()
        port = object_ent.get('port_id', '')

        if port_filter and port_filter != port:
            return
        selected_node_ids = []
        for selected_item in self.obj_tree.selection():
            selected_node_ids.append(self.obj_tree.set(selected_item, 'node_id'))

        """
        items = list(self._obj_tree.get_children())
        list_len = len(items)
        for index, item in enumerate(items):
            if self._obj_tree.set(item, 'node_id') == node_id:
                self._obj_tree.delete(item)
                break
        """
        items = list(self.obj_tree.get_children())
        list_len = len(items)
        auto_scroll = list_len == len(list(self.obj_tree.get_children()))
        tree_data = self._get_treedata_fm_obj_tab(object_ent)
        if tree_data:
            self._aprsMon_root.add_to_tree(tree_data,
                             tree=self.obj_tree,
                             add_to_end=False,
                             auto_scroll=auto_scroll,
                             replace_ent=True,
                             prio=False)

        if node_id in selected_node_ids:
            for item in self.obj_tree.get_children():
                if self.obj_tree.set(item, 'node_id') == node_id:
                    self.obj_tree.selection_add(item)
                    break

    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """

        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))