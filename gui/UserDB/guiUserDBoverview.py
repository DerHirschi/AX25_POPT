import tkinter as tk
from tkinter import ttk

from UserDB.UserDBmain import USER_DB
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import conv_time_DE_str, get_strTab
from gui.guiMsgBoxes import AskMsg
from gui.guiRightClick_Menu import ContextMenu


class UserDBtreeview(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self.root       = root_win
        self._user_db   = USER_DB
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # Vars
        self.title("User-DB")
        self.style = self.root.style
        # self.geometry("1250x700")
        self.geometry(f"1250x"
                      f"700+"
                      f"{self.root.main_win.winfo_x()}+"
                      f"{self.root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ############################################################
        self._sort_flag         = ''
        self._rev_ent           = False
        self._selected          = []
        self._tree_data         = []
        self._data              = {}
        self._key_is_pressed    = False
        ############################################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ##########################################################################################
        # TREE
        tree_f = ttk.Frame(main_f)
        tree_f.pack(fill=tk.BOTH, expand=True)
        columns = (
            'uDB_call',
            'uDB_sysop',
            'uDB_typ',
            'uDB_loc',
            'uDB_dist',
            'uDB_qth',
            'uDB_land',
            'uDB_lastconn',
            # 'uDB_lastseen', # TODO Get from MH
        )
        self._tree = ttk.Treeview(tree_f, columns=columns, show='headings')
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_f, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self._tree.heading('uDB_call', text='Call', command=lambda: self._sort_entry('call'))
        self._tree.heading('uDB_sysop', text='Sysop', command=lambda: self._sort_entry('sysop'))
        self._tree.heading('uDB_typ', text='Typ', command=lambda: self._sort_entry('typ'))
        self._tree.heading('uDB_loc', text='Locator', command=lambda: self._sort_entry('loc'))
        self._tree.heading('uDB_dist', text='Distance', command=lambda: self._sort_entry('dist'))
        self._tree.heading('uDB_qth', text='QTH', command=lambda: self._sort_entry('qth'))
        self._tree.heading('uDB_land', text='Land', command=lambda: self._sort_entry('land'))
        self._tree.heading('uDB_lastconn', text='Last Conn', command=lambda: self._sort_entry('last_conn'))
        # self.tree.heading('uDB_lastseen', text='Last seen', command=lambda: self.sort_entry('last_seen')) # TODO Get from MH

        self._tree.column("uDB_call", anchor=tk.W, stretch=tk.NO, width=130)
        self._tree.column("uDB_sysop", anchor=tk.W, stretch=tk.NO, width=130)
        self._tree.column("uDB_typ", anchor=tk.W, stretch=tk.NO, width=150)
        self._tree.column("uDB_loc", anchor=tk.W, stretch=tk.NO, width=100)
        self._tree.column("uDB_dist", anchor=tk.W, stretch=tk.NO, width=90)
        self._tree.column("uDB_qth", anchor=tk.W, stretch=tk.YES, width=190)
        self._tree.column("uDB_land", anchor=tk.W, stretch=tk.NO, width=60)
        self._tree.column("uDB_lastconn", anchor=tk.W, stretch=tk.NO, width=190)
        # self.tree.column("uDB_lastseen", anchor=tk.W, stretch=tk.NO, width=190) # TODO Get from MH
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)

        self.root.userDB_tree_win = self
        self._init_tree_data()
        self._update_tree()
        self.bind('<Key>', lambda event: self._on_key_press(event))
        self.bind('<KeyRelease>', lambda event: self._on_key_release(event))
        self._tree.bind('<<TreeviewSelect>>', self._entry_selected)
        self._init_RClick_menu()

    def _init_RClick_menu(self):
        txt_men = ContextMenu(self._tree)
        txt_men.add_item(self._getTabStr('delete_selected'), self._del_menu_cmd)

    def _init_tree_data(self):
        self._sort_entry('call')

    def _update_tree(self):
        self._format_tree_ent()

        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            self._tree.insert('', tk.END, values=ret_ent)

    def _on_key_press(self, event: tk.Event):
        self._key_is_pressed = True

    def _on_key_release(self, event: tk.Event):
        self._key_is_pressed = False

    def _entry_selected(self, event: tk.Event):
        r_key = ''
        self._selected = []
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values']
            # show a message
            r_key = record[0]
            self._selected.append(record[0])
        if self._key_is_pressed or not r_key:
            return
        self.root.open_user_db_win(ent_key=r_key)

    def _sort_entry(self, flag: str):
        self._sort_flag = flag
        self._data = self._user_db.get_sort_entr(flag_str=self._sort_flag, reverse=self._rev_ent)
        if self._rev_ent:
            self._rev_ent = False
        else:
            self._rev_ent = True
        self._update_tree()

    def _update_entry(self):
        self._data = self._user_db.get_sort_entr(flag_str=self._sort_flag, reverse=self._rev_ent)
        self._update_tree()

    def _format_tree_ent(self):
        self._tree_data = []
        for k, ent in self._data.items():
            distance = round(ent.Distance)
            self._tree_data.append((
                f'{ent.call_str}',
                f'{ent.Sysop_Call}',
                f'{ent.TYP}',
                f'{ent.LOC}',
                f"{'n/a' if distance < 0 else distance}",
                f'{ent.QTH}',
                f'{ent.Land}',
                f"{'' if ent.last_conn is None else conv_time_DE_str(ent.last_conn)}",
                # f'{conv_time_DE_str(ent.last_seen)}',   # TODO Get from MH

            ))

    def _del_menu_cmd(self):
        if not self._selected:
            return
        msg = AskMsg(
            titel=self._getTabStr('userdb_del_hint2_1').format(len(self._selected)),
            message=self._getTabStr('userdb_del_hint2_2').format(len(self._selected)),
            parent_win=self)
        if not msg:
            return

        for sel_ent in self._selected:
            self._user_db.del_entry(str(sel_ent))
        self._update_entry()

    def close(self):
        self.root.userDB_tree_win = None
        self.destroy()

    def __del__(self):
        self.root.userDB_tree_win = None
        # self.destroy()

