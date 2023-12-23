import logging
import tkinter as tk
from tkinter import ttk

from UserDB.UserDBmain import USER_DB
from fnc.str_fnc import conv_time_DE_str

logger = logging.getLogger(__name__)


class UserDBtreeview(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root = root_win
        # self.user_db = USER_DB
        ###################################
        # Vars
        self.rev_ent = False
        # self.mh_win = tk.Tk()
        self.title("User-DB")
        self.style = self.root.style
        # self.geometry("1250x700")
        self.geometry(f"1090x"
                      f"700+"
                      f"{self.root.main_win.winfo_x()}+"
                      f"{self.root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)
        ##########################################################################################
        # TREE
        columns = (
            'uDB_call',
            'uDB_sysop',
            'uDB_typ',
            'uDB_loc',
            'uDB_dist',
            'uDB_qth',
            'uDB_land',
            'uDB_lastseen',
        )
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.grid(row=0, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.tree.heading('uDB_call', text='Call', command=lambda: self.sort_entry('call'))
        self.tree.heading('uDB_sysop', text='Sysop', command=lambda: self.sort_entry('sysop'))
        self.tree.heading('uDB_typ', text='Typ', command=lambda: self.sort_entry('typ'))
        self.tree.heading('uDB_loc', text='Locator', command=lambda: self.sort_entry('loc'))
        self.tree.heading('uDB_dist', text='Distance', command=lambda: self.sort_entry('dist'))
        self.tree.heading('uDB_qth', text='QTH', command=lambda: self.sort_entry('qth'))
        self.tree.heading('uDB_land', text='Land', command=lambda: self.sort_entry('land'))
        self.tree.heading('uDB_lastseen', text='Last Conn', command=lambda: self.sort_entry('last_seen'))

        self.tree.column("uDB_call", anchor=tk.W, stretch=tk.NO, width=130)
        self.tree.column("uDB_sysop", anchor=tk.W, stretch=tk.NO, width=130)
        self.tree.column("uDB_typ", anchor=tk.W, stretch=tk.NO, width=150)
        self.tree.column("uDB_loc", anchor=tk.W, stretch=tk.NO, width=100)
        self.tree.column("uDB_dist", anchor=tk.W, stretch=tk.NO, width=90)
        self.tree.column("uDB_qth", anchor=tk.W, stretch=tk.YES, width=190)
        self.tree.column("uDB_land", anchor=tk.W, stretch=tk.NO, width=60)
        self.tree.column("uDB_lastseen", anchor=tk.W, stretch=tk.NO, width=190)
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)

        self.tree_data = []
        self.root.userDB_tree_win = self
        self.init_tree_data()
        self.update_tree()
        self.tree.bind('<<TreeviewSelect>>', self.entry_selected)

    def init_tree_data(self):
        self.sort_entry('call')

    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ret_ent in self.tree_data:
            self.tree.insert('', tk.END, values=ret_ent)

    def entry_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            _key = record[0]

            self.root.open_user_db_win(ent_key=_key)

    def sort_entry(self, flag: str):
        sort_date = USER_DB.get_sort_entr(flag_str=flag, reverse=self.rev_ent)
        if self.rev_ent:
            self.rev_ent = False
        else:
            self.rev_ent = True
        self.format_tree_ent(sort_date)
        self.update_tree()

    def format_tree_ent(self, data):
        self.tree_data = []
        for k in data:
            ent = data[k]

            self.tree_data.append((
                f'{ent.call_str}',
                f'{ent.Sysop_Call}',
                f'{ent.TYP}',
                f'{ent.LOC}',
                f'{round(ent.Distance)}',
                f'{ent.QTH}',
                f'{ent.Land}',
                f'{conv_time_DE_str(ent.last_seen)}',

            ))

    def close(self):
        self.root.userDB_tree_win = None
        self.destroy()

    def __del__(self):
        self.root.userDB_tree_win = None
        # self.destroy()

