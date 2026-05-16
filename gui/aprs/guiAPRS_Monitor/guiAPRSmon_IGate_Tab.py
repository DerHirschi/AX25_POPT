from tkinter import ttk

class IGateTab:
    def __init__(self, ais_mon, parent_frame):
        self._ais_mon = ais_mon
        self._ais_obj = ais_mon.get_ais_obj()

        self._port_filter_var = ais_mon.port_filter_var
        self._sort_rev = False

        # =========================
        columns = (
            'node_id',
            'call',
            'software',
            'msg_cnt',
            'pkt_cnt',
            'rf_cnt',
            'upl_cnt',
            'dnl_cnt',
            'last_rx',
        )

        self._tree = ttk.Treeview(parent_frame, columns=columns, show='tree headings')
        self._tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(parent_frame, orient='vertical', command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        # =========================
        self._tree.heading('#0', text='IGate')
        self._tree.heading('node_id')
        self._tree.heading('call', text="Call", command=lambda: self._sort_entry('call', self._tree))
        self._tree.heading('software', text="Software", command=lambda: self._sort_entry('software', self._tree))
        self._tree.heading('msg_cnt', text="MSG", command=lambda: self._sort_entry('msg_cnt', self._tree))
        self._tree.heading('pkt_cnt', text="PKT", command=lambda: self._sort_entry('pkt_cnt', self._tree))
        self._tree.heading('rf_cnt', text="RF", command=lambda: self._sort_entry('rf_cnt', self._tree))
        self._tree.heading('upl_cnt', text="UP", command=lambda: self._sort_entry('upl_cnt', self._tree))
        self._tree.heading('dnl_cnt', text="DN", command=lambda: self._sort_entry('dnl_cnt', self._tree))
        self._tree.heading('last_rx', text="Last RX", command=lambda: self._sort_entry('last_rx', self._tree))

        # =========================
        self._tree.column('#0', width=50, stretch=False)
        self._tree.column('node_id', width=0, stretch=False)
        self._tree.column('call', width=100, stretch=False)
        self._tree.column('software', width=200, stretch=True)
        self._tree.column('msg_cnt', width=70, stretch=False)
        self._tree.column('pkt_cnt', width=70, stretch=False)
        self._tree.column('rf_cnt', width=70, stretch=False)
        self._tree.column('upl_cnt', width=80, stretch=False)
        self._tree.column('dnl_cnt', width=80, stretch=False)
        self._tree.column('last_rx', width=80, stretch=False)

    # ==========================================================
    def init_tree(self):
        if not hasattr(self._ais_obj, 'get_igates_tab'):
            return

        ig_tab = self._ais_obj.get_igates_tab()

        for call, ent in dict(ig_tab).items():
            tree_data = self._format_tree_data(call, ent)
            if tree_data:
                self._ais_mon.add_to_tree(
                    tree_data,
                    tree=self._tree,
                    replace_ent=True,
                    prio=False
                )

    # ==========================================================
    def update_tree(self, call: str):
        if not hasattr(self._ais_obj, 'get_igates_tab'):
            return

        ig_tab = self._ais_obj.get_igates_tab()
        ent = ig_tab.get(call, {})
        if not ent:
            return

        tree_data = self._format_tree_data(call, ent)
        if tree_data:
            self._ais_mon.add_to_tree(
                tree_data,
                tree=self._tree,
                add_to_end=False,
                replace_ent=True,
                prio=False
            )

    # ==========================================================
    @staticmethod
    def _format_tree_data(call: str, ent: dict):
        if not call:
            return ()

        last = ent.get('last', {})
        data = last.get('data', {})

        return (

            call,
            call,
            ent.get('software', ''),
            data.get('MSG_CNT', 0),
            data.get('PKT_CNT', 0),
            data.get('RF_CNT', 0),
            data.get('UPL_CNT', 0),
            data.get('DNL_CNT', 0),
            last.get('rx_time', '').strftime('%H:%M:%S') if last.get('rx_time') else '',
            ('\\', 'I')  # eigenes IGate Symbol
        )

    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """

        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

