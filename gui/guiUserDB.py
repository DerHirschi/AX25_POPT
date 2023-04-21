import tkinter as tk
from tkinter import ttk
from string_tab import STR_TABLE


class UserDB(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self)
        self.root = root
        self.lang = self.root.language
        root.settings_win = self
        self.win_height = 600
        self.win_width = 1060
        self.style = root.style
        self.title(STR_TABLE['user_db'][self.lang])
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root.main_win.winfo_x()}+"
                      f"{self.root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        self.lift()
        # self.attributes("-topmost", True)
        ###############
        # VARS
        self.user_db = root.ax25_port_handler.user_db.db
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text=STR_TABLE['OK'][self.lang],
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)

        save_bt = tk.Button(self,
                            text=STR_TABLE['save'][self.lang],
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)

        cancel_bt = tk.Button(self,
                              text=STR_TABLE['cancel'][self.lang],
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        self.grid_columnconfigure(0, weight=0, minsize=15)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1 , minsize=400)
        self.grid_rowconfigure(0, weight=0, minsize=50)

        columns = (
            'call',
        )
        self.tree = ttk.Treeview(self, columns=columns, show='tree', height=20)

        self.tree.grid(row=1, column=1, sticky='nw')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky='wns')
        """
        self.tree.heading('call',
                          text='Call',
                          # command=lambda: self.sort_entry('last')
                          )
        """
        self.tree.column("#0", width=0, minwidth=0)
        self.tree.column("call", anchor='w', stretch=tk.NO, width=150)
        for ret_ent in list(self.user_db.keys()):
            self.tree.insert('', tk.END, values=ret_ent)

        # self.tree.bind('<<TreeviewSelect>>', self.entry_selected)

    def save_btn_cmd(self):
        pass

    def ok_btn_cmd(self):
        self.root.msg_to_monitor('Info: Baken Settings wurden gespeichert..')
        self.root.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.root.settings_win = None

    def tasker(self):
        pass
