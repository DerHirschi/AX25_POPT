from datetime import datetime
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSmonMSGTree(ttk.Frame):
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
        self.msg_tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.msg_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.msg_tree.yview)
        self.msg_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self.msg_tree.heading('#0', text='Symbol')
        self.msg_tree.heading('node_id', text=self._getTabStr('from'),
                              command=lambda: self._sort_entry('node_id', self.msg_tree))
        self.msg_tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry('to', self.msg_tree))
        self.msg_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self.msg_tree))
        self.msg_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self.msg_tree))
        self.msg_tree.heading('path', text="Path", command=lambda: self._sort_entry('path', self.msg_tree))
        self.msg_tree.heading('loc', text="Locator", command=lambda: self._sort_entry('loc', self.msg_tree))
        self.msg_tree.heading('dist', text="km", command=lambda: self._sort_entry('dist', self.msg_tree))
        self.msg_tree.heading('rx_time', text=self._getTabStr('date_time'),
                              command=lambda: self._sort_entry('rx_time', self.msg_tree))
        self.msg_tree.heading('comment', text="Msg", command=lambda: self._sort_entry('comment', self.msg_tree))

        self.msg_tree.column('#0', anchor='w', stretch=False, width=50)
        self.msg_tree.column("node_id", anchor='w', stretch=False, width=80)
        self.msg_tree.column("to", anchor='w', stretch=False, width=80)
        self.msg_tree.column("port", anchor='w', stretch=False, width=60)
        self.msg_tree.column("via", anchor='w', stretch=False, width=80)
        self.msg_tree.column("path", anchor='w', stretch=False, width=200)
        self.msg_tree.column("loc", anchor='w', stretch=False, width=90)
        self.msg_tree.column("dist", anchor='w', stretch=False, width=50)
        self.msg_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self.msg_tree.column("comment", anchor='w', stretch=True, width=80)

    #############################################################
    def get_treedata_fm_msg_pack(self, aprs_pack: dict):
        symbol  =  self._aprsMon_root.get_symbol_fm_node_tab(aprs_pack.get('from', ''))
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
            aprs_pack.get('rx_time', datetime.now()).strftime('%H:%M:%S'),
            msg_text,
            symbol,
        )

    def msg_tree_update(self, aprs_pack: dict):
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
        for selected_item in self.msg_tree.selection():
            selected_node_ids.append(self.msg_tree.set(selected_item, 'node_id'))

        tree_data   = self.get_treedata_fm_msg_pack(aprs_pack)
        if tree_data:
            self._aprsMon_root.add_to_tree(tree_data, tree=self.msg_tree, add_to_end=False, auto_scroll=True, replace_ent=False)

        if node_id in selected_node_ids:
            for item in self.msg_tree.get_children():
                if self.msg_tree.set(item, 'node_id') == node_id:
                    self.msg_tree.selection_add(item)
                    break


    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """

        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))


