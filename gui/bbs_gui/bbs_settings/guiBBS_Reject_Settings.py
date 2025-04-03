import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.str_fnc import get_strTab
from gui.bbs_gui.bbs_settings.guiBBS_H_Settings_add_rule import BBS_addRuleWinHold


class BBSRejectSettings(tk.Frame):
    def __init__(self, tabctl, root_win):
        tk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._logTag    = 'BBSRejectSettings: '
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict     = dict(self._root_win.get_root_pms_cfg())
        self._rej_tab: list     = self._pms_cfg.get('reject_tab', [])
        ###################################
        # Vars
        self._sort_rev          = False
        self._last_sort_col     = {}
        self._tree_data         = []
        self._selected_items    = []
        ###########################################
        ###########################################
        # Local
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        add_btn = tk.Button(btn_frame,
                            text=self._getTabStr('new'),
                            command=lambda :self._add_rule_btn()
                            )
        del_btn = tk.Button(btn_frame,
                            text=self._getTabStr('delete'),
                            command=self._del_btn
                            )
        add_btn.pack(side=tk.LEFT, padx=30, pady=15)
        del_btn.pack(side=tk.LEFT, padx=30)
        ##########
        cfg_tree_frame = tk.Frame(self)
        cfg_tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=7, pady=10)
        col = (
            'c1',
            'c2',
            'c3',
            'c4',
            'c5',
            'c6',
            'c7',
        )
        tree_scrollbar = ttk.Scrollbar(cfg_tree_frame)

        self._rej_tree = ttk.Treeview(
            cfg_tree_frame,
            columns=col,
            show='headings',
            yscrollcommand=tree_scrollbar.set
        )
        self._rej_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tree_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self._rej_tree.heading('c1', text='Typ',   command=lambda: self._sort_entry('c1', self._rej_tree))
        self._rej_tree.heading('c2', text='From',  command=lambda: self._sort_entry('c2', self._rej_tree))
        self._rej_tree.heading('c3', text='Via',   command=lambda: self._sort_entry('c3', self._rej_tree))
        self._rej_tree.heading('c4', text='To',    command=lambda: self._sort_entry('c4', self._rej_tree))
        self._rej_tree.heading('c5', text='BID',   command=lambda: self._sort_entry('c5', self._rej_tree))
        self._rej_tree.heading('c6', text='MaxLg', command=lambda: self._sort_entry('c6', self._rej_tree))
        self._rej_tree.heading('c7', text='R/H',   command=lambda: self._sort_entry('c7', self._rej_tree))
        self._rej_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO,  width=60)
        self._rej_tree.column("c2", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._rej_tree.column("c3", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._rej_tree.column("c4", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._rej_tree.column("c5", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._rej_tree.column("c6", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._rej_tree.column("c7", anchor=tk.CENTER, stretch=tk.NO,  width=60)
        self._rej_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select())
        self._update_tree()

    ####################################
    def update_win(self):
        self._rej_tab: list = self._pms_cfg.get('reject_tab', [])
        self._update_tree()

    ####################################
    def _update_tree(self):
        self._format_tree_data()
        for i in self._rej_tree.get_children():
            self._rej_tree.delete(i)
        for ret_ent in self._tree_data:
            self._rej_tree.insert('', tk.END, values=ret_ent)

    def _format_tree_data(self):
        self._tree_data = []
        # for el in [getNew_BBS_REJ_cfg()]:
        if type(self._rej_tab) != list:
            return
        for el in self._rej_tab:
            ent = []
            for k, val in el.items():
                ent.append(val)
            self._tree_data.append(ent)

    ####################################
    def _tree_select(self):
        self._selected_items = []
        for selected_item in self._rej_tree.selection():
            item = self._rej_tree.item(selected_item)['values']
            self._selected_items.append(item)

    ####################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        self._last_sort_col[tree] = col
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    ####################################
    def _add_rule_btn(self):
        if hasattr(self._root_win.add_win, 'lift'):
            self._root_win.add_win.lift()
            return


        if self._root_win.add_win is not None:
            return
        BBS_addRuleWinHold(self._root_win)

    def _del_btn(self):
        need_update = False
        for el in self._selected_items:
            tmp = dict(
                msg_typ=        el[0],
                from_call=      el[1],
                via=            el[2],
                to_call=        el[3],
                bid=            el[4],
                msg_len=        el[5],
                r_h=            el[6],
            )
            if tmp not in self._rej_tab:
                logger.error(self._logTag + f'_del_btn() Entry not Found: {tmp}')
                continue
            need_update = True
            self._rej_tab.remove(tmp)

        if need_update:
            self.update_win()

