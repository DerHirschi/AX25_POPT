import tkinter as tk
from tkinter import ttk

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.bbs_gui.bbs_settings.guiBBS_CC_Settings_add_rule import BBS_addRuleWinCC
from gui.bbs_gui.bbs_settings.guiBBS_CC_Settings_del_rule import BBS_delRuleWinCC


class BBSccSettings(tk.Frame):
    def __init__(self, tabctl, root_win):
        tk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._logTag    = 'BBS_CC_Settings: '
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict     = dict(self._root_win.get_root_pms_cfg())
        self._cc_tab: dict      = self._pms_cfg.get('cc_tab', {})
        ###################################
        # Vars
        self._sort_rev          = False
        self._last_sort_col     = {}
        self._tree_data         = []
        self._selected_items    = []
        ###########################################
        ###################################
        # GUI Stuff
        tk.Label(self, text='CC').pack(side=tk.TOP, expand=False)
        r_btn_fr    = tk.Frame(self, borderwidth=10)
        r_tab_frame = tk.Frame(self, borderwidth=10)

        r_btn_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        r_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # r2
        tk.Button(r_btn_fr,
                  text=self._getTabStr('new'),
                  command=lambda :self._add_rule_btn()
                  ).pack(side=tk.LEFT, fill=tk.X, expand=False)

        tk.Button(r_btn_fr,
                  text=self._getTabStr('delete'),
                  command=lambda :self._del_rule_btn()
                  ).pack(side=tk.RIGHT, expand=False)

        # Tree Time.
        col = (
            'c1',
            'c2',
        )
        tree_scrollbar = ttk.Scrollbar(r_tab_frame)

        self._cc_tree = ttk.Treeview(
            r_tab_frame,
            columns=col,
            show='headings',
            yscrollcommand=tree_scrollbar.set
        )
        self._cc_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tree_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self._cc_tree.heading('c1', text=self._getTabStr('to'),  command=lambda: self._sort_entry('c1', self._cc_tree))
        self._cc_tree.heading('c2', text='CC', command=lambda: self._sort_entry('c2', self._cc_tree))
        self._cc_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO,  width=200)
        self._cc_tree.column("c2", anchor=tk.CENTER, stretch=tk.YES, width=400)

        self._cc_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select())
        self._update_tree()

    ####################################
    def _update_tree(self):
        self._format_tree_data()
        for i in self._cc_tree.get_children():
            self._cc_tree.delete(i)
        for ret_ent in self._tree_data:
            self._cc_tree.insert('', tk.END, values=ret_ent)

    def _format_tree_data(self):
        self._tree_data = []
        # for el in [getNew_BBS_REJ_cfg()]:
        if type(self._cc_tab) != dict:
            logger.error(self._logTag + f"_format_tree_data()> cc_tab wrong Data: {self._cc_tab}")
            return
        for org_call, cc_list in self._cc_tab.items():
            ent = [org_call, ", ".join(cc_list)]
            self._tree_data.append(ent)

    def _tree_select(self):
        self._selected_items = []
        for selected_item in self._cc_tree.selection():
            item = self._cc_tree.item(selected_item)['values']
            self._selected_items.append(item)

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
        BBS_addRuleWinCC(self._root_win)

    def _del_rule_btn(self):
        if not self._selected_items:
            return
        try:
            selected = self._selected_items[-1][0]
        except IndexError:
            return
        if hasattr(self._root_win.add_win, 'lift'):
            self._root_win.add_win.lift()
            return

        if self._root_win.add_win is not None:
            return
        BBS_delRuleWinCC(self._root_win, selected)

    ####################################
    def update_win(self):
        self._cc_tab: dict = self._pms_cfg.get('cc_tab', {})
        self._update_tree()