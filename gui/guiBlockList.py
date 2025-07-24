import tkinter as tk
from tkinter import ttk

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.guiBlockList_add import BlockListADD


class BlockList(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._main      = main_win
        self.style      = self._main.style
        self.title('Black List')
        self.geometry(f"640x480+{self._main.main_win.winfo_x()}+{self._main.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.resizable(True, True)
        # self.attributes("-topmost", True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        #########################################
        # CFG
        self._block_list = POPT_CFG.get_block_list()
        ###################################
        # Vars
        self._sort_rev          = False
        self._last_sort_col     = {}
        self._tree_data         = []
        self._selected_items    = []
        self.add_win            = None
        ###########################################
        #
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side='top', fill='x', expand=False)
        add_btn = ttk.Button(btn_frame,
                             text=self._getTabStr('new'),
                             command=lambda: self._add_rule_btn()
                             )
        del_btn = ttk.Button(btn_frame,
                             text=self._getTabStr('delete'),
                             command=self._del_btn
                             )
        add_btn.pack(side='left', padx=30, pady=15)
        del_btn.pack(side='left', padx=30)

        ##########
        cfg_tree_frame = ttk.Frame(self)
        cfg_tree_frame.pack(side='top', fill='both', expand=True)
        col = (
            'c1',   # CALL
            'c2',   # Port
            'c3',   # State
        )
        tree_scrollbar = ttk.Scrollbar(cfg_tree_frame)

        self._tree = ttk.Treeview(
            cfg_tree_frame,
            columns=col,
            show='headings',
            yscrollcommand=tree_scrollbar.set
        )
        self._tree.pack(side='left', expand=True, fill='both')
        tree_scrollbar.pack(side='left', fill='y')

        self._tree.heading('c1', text='CALL', command=lambda: self._sort_entry('c1', self._tree))
        self._tree.heading('c2', text='Port', command=lambda: self._sort_entry('c2', self._tree))
        self._tree.heading('c3', text='State', command=lambda: self._sort_entry('c3', self._tree))
        self._tree.column("c1", anchor='center', stretch=tk.NO, width=60)
        self._tree.column("c2", anchor='center', stretch=tk.YES, width=120)
        self._tree.column("c3", anchor='center', stretch=tk.YES, width=120)
        self._tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select())
        self._update_tree()

    ####################################
    def _add_rule_btn(self):
        if hasattr(self.add_win, 'lift'):
            self.add_win.lift()
            return
        if self.add_win is not None:
            return
        self.add_win = BlockListADD(self)

    def _del_btn(self):
        need_update = False
        for el in self._selected_items:
            call, port, state = el
            if call not in self._block_list.get(port, {}):
                continue
            del self._block_list[port][call]
            need_update = True
        if need_update:
            self._update_tree()

    ####################################
    def update_tabs(self):
        self._update_tree()

    def _update_tree(self):
        self._format_tree_data()
        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            self._tree.insert('', 'end', values=ret_ent)

    def _format_tree_data(self):
        self._tree_data  = []
        self._block_list = POPT_CFG.get_block_list()
        for port, block_tab in self._block_list.items():
            for call, state in block_tab.items():
                if not state:
                    continue
                state_text = {
                    1: "ignored",
                    2: "rejected",
                }.get(state, '-')
                self._tree_data.append(
                    (
                        call, port, state_text
                    )
                )

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
    def _tree_select(self):
        self._selected_items = []
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)['values']
            self._selected_items.append(item)

    def _destroy_win(self):
        if hasattr(self.add_win, 'destroy_win'):
            self.add_win.destroy_win()
        self.destroy()
        self._main.block_list_win = None

    def close(self):
        self._destroy_win()