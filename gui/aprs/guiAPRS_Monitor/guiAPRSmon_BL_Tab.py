from datetime import datetime
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSmonBLTree(ttk.Frame):
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
            'to',
            'port',
            'via',
            'path',
            'loc',
            'dist',
            'rx_time',
            'comment',
        )
        self.bl_tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.bl_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.bl_tree.yview)
        self.bl_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self.bl_tree.heading('#0', text='Symbol')
        self.bl_tree.heading('node_id', text="BL ID",
                             command=lambda: self._sort_entry('node_id', self.bl_tree))
        self.bl_tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry('to', self.bl_tree))
        self.bl_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self.bl_tree))
        self.bl_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self.bl_tree))
        self.bl_tree.heading('path', text="Path", command=lambda: self._sort_entry('path', self.bl_tree))
        self.bl_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self.bl_tree))
        self.bl_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self.bl_tree))
        self.bl_tree.heading('rx_time', text=self._getTabStr('date_time'),
                             command=lambda: self._sort_entry('rx_time', self.bl_tree))
        self.bl_tree.heading('comment', text="Msg", command=lambda: self._sort_entry('comment', self.bl_tree))

        self.bl_tree.column('#0', anchor='w', stretch=False, width=50)
        self.bl_tree.column("node_id", anchor='w', stretch=False, width=80)
        self.bl_tree.column("to", anchor='w', stretch=False, width=80)
        self.bl_tree.column("port", anchor='w', stretch=False, width=60)
        self.bl_tree.column("via", anchor='w', stretch=False, width=80)
        self.bl_tree.column("path", anchor='w', stretch=False, width=200)
        self.bl_tree.column("loc", anchor='w', stretch=False, width=90)
        self.bl_tree.column("dist", anchor='w', stretch=False, width=50)
        self.bl_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self.bl_tree.column("comment", anchor='w', stretch=True, width=80)

    #############################################################
    def get_treedata_fm_bl_pack(self, aprs_pack: dict):
        symbol   =  self._aprsMon_root.get_symbol_fm_node_tab(aprs_pack.get('from', ''))
        msg_text = aprs_pack.get('message_text', '')
        return (
            aprs_pack.get('from', ''),
            aprs_pack.get('msgNo', ''),
            aprs_pack.get('port_id', ''),
            aprs_pack.get('via', ''),
            '>'.join(aprs_pack.get('path', [])),
            aprs_pack.get('locator', ''),
            round(aprs_pack.get('distance', -1)),
            aprs_pack.get('rx_time', datetime.now()).strftime('%H:%M:%S'),
            msg_text,
            symbol,
        )

    def bl_tree_update(self, aprs_pack: dict):
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
        for selected_item in self.bl_tree.selection():
            selected_node_ids.append(self.bl_tree.set(selected_item, 'node_id'))

        tree_data = self.get_treedata_fm_bl_pack(aprs_pack)
        if tree_data:
            self._aprsMon_root.add_to_tree(tree_data, tree=self.bl_tree, add_to_end=False, auto_scroll=True, replace_ent=False)

        if node_id in selected_node_ids:
            for item in self.bl_tree.get_children():
                if self.bl_tree.set(item, 'node_id') == node_id:
                    self.bl_tree.selection_add(item)
                    break


    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """

        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))


