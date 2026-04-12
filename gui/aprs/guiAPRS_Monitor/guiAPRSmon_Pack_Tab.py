from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class APRSmonPackTree(ttk.Frame):
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
        self.mon_tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.mon_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.mon_tree.yview)
        self.mon_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self.mon_tree.heading('#0', text='Symbol')
        self.mon_tree.heading('from', text=self._getTabStr('from'),
                              command=lambda: self._sort_entry('from', self.mon_tree))
        self.mon_tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry('to', self.mon_tree))
        self.mon_tree.heading('port', text="Port", command=lambda: self._sort_entry('port', self.mon_tree))
        self.mon_tree.heading('via', text='VIA', command=lambda: self._sort_entry('via', self.mon_tree))
        self.mon_tree.heading('path', text='Path', command=lambda: self._sort_entry('path', self.mon_tree))
        self.mon_tree.heading('loc', text='Locator', command=lambda: self._sort_entry('loc', self.mon_tree))
        self.mon_tree.heading('typ', text='Typ', command=lambda: self._sort_entry('typ', self.mon_tree))
        self.mon_tree.heading('rx_time', text=self._getTabStr('date_time'),
                              command=lambda: self._sort_entry('rx_time', self.mon_tree))
        self.mon_tree.heading('comment', text=self._getTabStr('message'),
                              command=lambda: self._sort_entry('comment', self.mon_tree))
        self.mon_tree.heading('raw', text='RAW', command=lambda: self._sort_entry('raw', self.mon_tree))
        self.mon_tree.column('#0', anchor='w', stretch=False, width=50)
        self.mon_tree.column("from", anchor='w', stretch=False, width=80)
        self.mon_tree.column("to", anchor='w', stretch=False, width=80)
        self.mon_tree.column("port", anchor='w', stretch=False, width=60)
        self.mon_tree.column("via", anchor='w', stretch=False, width=80)
        self.mon_tree.column("path", anchor='w', stretch=False, width=200)
        self.mon_tree.column("loc", anchor='w', stretch=False, width=120)
        self.mon_tree.column("typ", anchor='w', stretch=False, width=100)
        self.mon_tree.column("rx_time", anchor='w', stretch=False, width=70)
        self.mon_tree.column("comment", anchor='w', stretch=True, width=20)
        self.mon_tree.column("raw", anchor='w', stretch=True, width=20)

    #############################################################

    #############################################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        if True:
            """Disabled"""
            return
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))