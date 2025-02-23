import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
# from cfg.logger_config import logger

class BBS_fwd_Q(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        self._bbs_obj = PORT_HANDLER.get_bbs()
        # self._ais_obj.wx_tree_gui = self
        ###################################
        # Vars
        self._rev_ent = False

        self._lang = POPT_CFG.get_guiCFG_language()
        self.title(STR_TABLE['fwd_list'][self._lang])
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1000x"
                      f"300+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        # ############################### Columns ############################
        # _frame = tk.Frame(self, background='red')
        # _frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # _frame.columnconfigure(0, weight=1, minsize=1000)
        # _frame.columnconfigure(1, weight=0, minsize=150)
        # _frame.rowconfigure(0, weight=0)
        # tk.Label(_frame, text='sags').grid(row=0, column=1)
        ##########################################################################################
        # TREE
        tree_frame = tk.Frame(self, )
        tree_frame.rowconfigure(0, weight=1, )
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        btn_frame = tk.Frame(self, width=150)
        btn_frame.rowconfigure(0, weight=1, )
        btn_frame.rowconfigure(1, weight=1, )
        btn_frame.rowconfigure(2, weight=1, )
        btn_frame.columnconfigure(0, weight=1, minsize=150)
        btn_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        tk.Button(btn_frame,
                  text="FWD Starten",
                  command=self._do_fwd
                  ).grid(row=0, column=0)
        columns = (
            'BID',
            'from',
            'to',
            'fwd_bbs_call',
            'type',
            'sub',
            'size',
        )

        self._tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self._tree.grid(row=0, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self._tree.heading('BID', text='BID', command=lambda: self._sort_entry('BID'))
        self._tree.heading('from', text='From', command=lambda: self._sort_entry('from'))
        self._tree.heading('to', text='To', command=lambda: self._sort_entry('to'))
        self._tree.heading('fwd_bbs_call', text='To BBS', command=lambda: self._sort_entry('fwd_bbs_call'))
        self._tree.heading('type', text='Type', command=lambda: self._sort_entry('type'))
        self._tree.heading('sub', text='Subject', command=lambda: self._sort_entry('sub'))
        self._tree.heading('size', text='Size', command=lambda: self._sort_entry('size'))
        self._tree.column("BID", anchor=tk.CENTER, stretch=tk.YES, width=100)
        self._tree.column("from", anchor=tk.CENTER, stretch=tk.YES, width=190)
        self._tree.column("to", anchor=tk.CENTER, stretch=tk.YES, width=190)
        self._tree.column("fwd_bbs_call", anchor=tk.CENTER, stretch=tk.YES, width=90)
        self._tree.column("type", anchor=tk.CENTER, stretch=tk.YES, width=60)
        self._tree.column("sub", anchor=tk.CENTER, stretch=tk.YES, width=150)
        self._tree.column("size", anchor=tk.CENTER, stretch=tk.YES, width=60)

        self._tree_data = []
        self._data = []
        self._root_win.BBS_fwd_q_list = self
        self.init_tree_data()
        # self._tree.bind('<<TreeviewSelect>>', self._entry_selected)

    def init_tree_data(self):
        self._get_data()
        self._format_tree_data()
        self._update_tree()

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            self._tree.insert('', tk.END, values=ret_ent)

    def _get_data(self):
        self._data = list(self._bbs_obj.get_active_fwd_q_tab())

    def _format_tree_data(self):
        self._tree_data = []
        for el in self._data:
            from_call = f"{el[1]}@{el[2]}"
            to_call = f"{el[3]}@{el[4]}"
            self._tree_data.append((
                f'{el[0]}',
                f'{from_call}',
                f'{to_call}',
                f'{el[5]}',  # to BBS
                f'{el[6]}',  # typ
                f'{el[7]}',  # sub
                f'{el[8]}',  # size
            ))

    def _sort_entry(self, col):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(self._tree.set(k, col), k) for k in self._tree.get_children('')]
        tmp.sort(reverse=self._rev_ent)
        self._rev_ent = not self._rev_ent
        for index, (val, k) in enumerate(tmp):
            self._tree.move(k, '', int(index))

    def _do_fwd(self):
        self._bbs_obj.start_man_autoFwd()

    def _close(self):
        self._bbs_obj = None
        self._root_win.BBS_fwd_q_list = None
        self.destroy()
