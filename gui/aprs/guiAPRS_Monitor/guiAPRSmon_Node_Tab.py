from datetime import datetime
from tkinter import ttk
import tkinter as tk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSmonNodeTree(ttk.Frame):
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
        h_frame = ttk.Frame(self)
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
        self.node_tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.node_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.node_tree.yview)
        self.node_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self.node_tree.heading('#0', text='Symbol')
        self.node_tree.heading('node_id', text="ID", command=lambda: self._sort_entry('node_id', self.node_tree))
        self.node_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self.node_tree))
        self.node_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self.node_tree))
        self.node_tree.heading('path', text="Path", command=lambda: self._sort_entry('path', self.node_tree))
        self.node_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self.node_tree))
        self.node_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self.node_tree))
        self.node_tree.heading('m_cap', text="MSG capable", command=lambda: self._sort_entry('m_cap', self.node_tree))
        self.node_tree.heading('rx_time', text=self._getTabStr('date_time'),
                               command=lambda: self._sort_entry('rx_time', self.node_tree))

        self.node_tree.column('#0', anchor='w', stretch=False, width=50)
        self.node_tree.column("node_id", anchor='w', stretch=False, width=80)
        self.node_tree.column("port", anchor='w', stretch=False, width=60)
        self.node_tree.column("via", anchor='w', stretch=False, width=80)
        self.node_tree.column("path", anchor='w', stretch=True, width=80)
        self.node_tree.column("loc", anchor='w', stretch=False, width=90)
        self.node_tree.column("dist", anchor='w', stretch=False, width=50)
        self.node_tree.column("m_cap", anchor='w', stretch=False, width=80)
        self.node_tree.column("rx_time", anchor='w', stretch=False, width=80)
        # self._node_tree.bind('<<TreeviewSelect>>', self._node_entry_selected)

    #############################################################
    def node_tree_init(self):
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
            self._aprsMon_root.add_to_tree(tree_data, tree=self.node_tree, replace_ent=True)
            c += 1
        self._node_count_label_var.set(self._set_node_c(c))

    def node_tree_update(self, node_tab_ent: dict, object_ent: dict):
        node_id     = node_tab_ent.get('node_id', '')
        port_filter = self._port_filter_var.get()
        port = node_tab_ent.get('port_id', '')

        if port_filter and port_filter != port:
            items = list(self.node_tree.get_children())
            self._node_count_label_var.set(self._set_node_c(len(items)))
            return
        selected_node_ids = []
        for selected_item in self.node_tree.selection():
            selected_node_ids.append(self.node_tree.set(selected_item, 'node_id'))

        items = list(self.node_tree.get_children())
        list_len = len(items)
        """
        for index, item in enumerate(items):
            if self._node_tree.set(item, 'node_id') == node_id:
                self._node_tree.delete(item)
                break
        """
        auto_scroll = list_len == len(list(self.node_tree.get_children()))
        tree_data = self._get_treedata_fm_node_tab(node_tab_ent)
        if tree_data:
            self._aprsMon_root.add_to_tree(tree_data, tree=self.node_tree, add_to_end=False, auto_scroll=auto_scroll, replace_ent=True)

        items = list(self.node_tree.get_children())
        self._node_count_label_var.set(self._set_node_c(len(items)))
        if node_id in selected_node_ids:
            for item in self.node_tree.get_children():
                if self.node_tree.set(item, 'node_id') == node_id:
                    self.node_tree.selection_add(item)
                    break

        if object_ent:
            self._aprsMon_root.obj_tree_update(object_ent)

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
                node_tab_ent.get('rx_time', datetime.now()).strftime('%H:%M:%S'),
                node_tab_ent.get('symbol', ('', '')),
        )

    def node_entry_selected(self):
        self._call_filter_list = []
        for selected_item in self.node_tree.selection():
            item = self.node_tree.item(selected_item)
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
            self._aprsMon_root.text_widget.delete(0.0, 'end')
            self._aprsMon_root.init_ais_mon(init_tree=False)

    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """

        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))
