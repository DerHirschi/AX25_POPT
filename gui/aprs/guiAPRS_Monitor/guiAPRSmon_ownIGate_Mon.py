from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSmonIGateMonTree(ttk.Frame):
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
        # =================
        self._port_filter_var = self._aprsMon_root.port_filter_var
        # =================
        columns = (
            'node_id',
            'port',
            'txport',
            'dir',
            'via',
            'rx_time',
            'comment',
        )
        self.own_igate_tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.own_igate_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.own_igate_tree.yview)
        self.own_igate_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self.own_igate_tree.heading('#0', text='Symbol')
        self.own_igate_tree.heading('node_id', text="ID", command=lambda: self._sort_entry('node_id', self.own_igate_tree))
        self.own_igate_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self.own_igate_tree))
        self.own_igate_tree.heading('txport', text="TX-Port", command=lambda: self._sort_entry('txport', self.own_igate_tree))
        self.own_igate_tree.heading('dir', text="Direction", command=lambda: self._sort_entry('via', self.own_igate_tree))
        self.own_igate_tree.heading('via', text="VIA", command=lambda: self._sort_entry('via', self.own_igate_tree))
        self.own_igate_tree.heading('rx_time', text=self._getTabStr('date_time'),
                                    command=lambda: self._sort_entry('rx_time', self.own_igate_tree))
        self.own_igate_tree.heading('comment', text="Data", command=lambda: self._sort_entry('comment', self.own_igate_tree))

        self.own_igate_tree.column('#0', anchor='w', stretch=False, width=50)
        self.own_igate_tree.column("node_id", anchor='w', stretch=False, width=80)
        self.own_igate_tree.column("port", anchor='w', stretch=False, width=60)
        self.own_igate_tree.column("txport", anchor='w', stretch=False, width=60)
        self.own_igate_tree.column("dir", anchor='w', stretch=False, width=80)
        self.own_igate_tree.column("via", anchor='w', stretch=False, width=80)
        self.own_igate_tree.column("rx_time", anchor='w', stretch=False, width=80)
        self.own_igate_tree.column("comment", anchor='w', stretch=True, width=80)


    #############################################################
    def update_tree(self):
        """Treeview mit I-Gate Monitor Daten füllen"""
        if not self._ais_obj:
            return

        mon_buf = self._ais_obj.get_igate_mon()
        if not mon_buf:
            return

        # aktuellen Inhalt löschen
        for item in self.own_igate_tree.get_children():
            self.own_igate_tree.delete(item)

        port_filter = self._port_filter_var.get() if self._port_filter_var else None

        for pack in reversed(mon_buf):
            port_id = str(pack.get('port_id', ''))

            # Port Filter
            if port_filter and port_filter != 'ALL':
                if port_id != str(port_filter):
                    continue

            node_id = pack.get('from', '')
            port    = port_id
            txport  = pack.get('tx_port', '')
            dire    = pack.get('dir', '')
            via     = pack.get('via', '') or ','.join(pack.get('path', []))

            rx_time = pack.get('rx_time', '')
            if rx_time:
                rx_time = rx_time.strftime('%d.%m.%y %H:%M:%S')

            comment = pack.get('raw_message_text', '') or pack.get('comment', '')

            symbol = self._aprsMon_root.get_symbol_fm_node_tab(node_id)

            """
            self.own_igate_tree.insert(
                '',
                'end',
                text=symbol,
                values=(node_id, port, txport, via, rx_time, comment)
            )
            """

            self._aprsMon_root.add_to_tree(
                tree_data=(node_id, port, txport, dire, via, rx_time, comment, symbol),
                tree=self.own_igate_tree,
                add_to_end=False,
                auto_scroll=False,
                replace_ent=False)


    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """

        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))