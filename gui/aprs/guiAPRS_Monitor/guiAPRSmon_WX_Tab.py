from datetime import datetime
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSmonWXTree(ttk.Frame):
    def __init__(self, parent, aprs_mon_root):
        super().__init__(parent)
        self.pack(fill='both', expand=True)
        # =================
        self._aprsMon_root = aprs_mon_root
        # =================
        self._sort_rev     = False
        # =================
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # =================
        self._port_filter_var         = self._aprsMon_root.port_filter_var
        # =================
        columns = (
            'node_id',
            'port',
            'via',
            'loc',
            'dist',
            'rx_time',
            'comment',
        )
        self.wx_tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.wx_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.wx_tree.yview)
        self.wx_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self.wx_tree.heading('#0', text='Symbol')
        self.wx_tree.heading('node_id', text="ID", command=lambda: self._sort_entry('node_id', self.wx_tree))
        self.wx_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self.wx_tree))
        self.wx_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self.wx_tree))
        self.wx_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self.wx_tree))
        self.wx_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self.wx_tree))
        self.wx_tree.heading('rx_time', text=self._getTabStr('date_time'),
                             command=lambda: self._sort_entry('rx_time', self.wx_tree))
        self.wx_tree.heading('comment', text="Data", command=lambda: self._sort_entry('comment', self.wx_tree))

        self.wx_tree.column('#0', anchor='w', stretch=False, width=50)
        self.wx_tree.column("node_id", anchor='w', stretch=False, width=80)
        self.wx_tree.column("port", anchor='w', stretch=False, width=60)
        self.wx_tree.column("via", anchor='w', stretch=False, width=80)
        self.wx_tree.column("loc", anchor='w', stretch=False, width=90)
        self.wx_tree.column("dist", anchor='w', stretch=False, width=50)
        self.wx_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self.wx_tree.column("comment", anchor='w', stretch=True, width=80)


    #############################################################
    def get_treedata_fm_wx_pack(self, aprs_pack: dict):
        wx_data = ' - '.join([f"{k}: {val}" for k, val in aprs_pack.get('weather', {}).items()])
        symbol  =  self._aprsMon_root.get_symbol_fm_node_tab(aprs_pack.get('from', ''))
        return (
            aprs_pack.get('from', ''),
            aprs_pack.get('port_id', ''),
            aprs_pack.get('via', ''),
            aprs_pack.get('locator', ''),
            round(aprs_pack.get('distance', -1)),
            aprs_pack.get('rx_time', datetime.now()).strftime('%H:%M:%S'),
            wx_data,
            symbol,
        )

    def wx_tree_update(self, aprs_pack: dict):
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
        for selected_item in self.wx_tree.selection():
            selected_node_ids.append(self.wx_tree.set(selected_item, 'node_id'))

        items    = list(self.wx_tree.get_children())
        list_len = len(items)
        """
        for index, item in enumerate(items):
            if self._wx_tree.set(item, 'node_id') == node_id:
                self._wx_tree.delete(item)
                break
        """

        auto_scroll = list_len == len(list(self.wx_tree.get_children()))
        tree_data   = self.get_treedata_fm_wx_pack(aprs_pack)
        if tree_data:
            self._aprsMon_root.add_to_tree(tree_data, tree=self.wx_tree, add_to_end=False, auto_scroll=auto_scroll, replace_ent=True)

        if node_id in selected_node_ids:
            for item in self.wx_tree.get_children():
                if self.wx_tree.set(item, 'node_id') == node_id:
                    self.wx_tree.selection_add(item)
                    break

    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """

        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))