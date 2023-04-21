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
        self.user_db = root.ax25_port_handler.user_db
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

        del_bt = tk.Button(self,
                          text=STR_TABLE['delete'][self.lang],
                          # font=("TkFixedFont", 15),
                          bg="red",
                          height=1,
                          width=6,
                          command=self.del_btn_cmd
                           )
        del_bt.place(x=10, y=10)

        self.grid_columnconfigure(0, weight=0, minsize=15)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1, minsize=400)
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
        self.tree.bind('<<TreeviewSelect>>', self.select_entry)
        self.tree.column("#0", width=0, minwidth=0)
        self.tree.column("call", anchor='w', stretch=tk.NO, width=150)
        self.db_ent = False
        ents = sorted(list(self.user_db.db.keys()))
        for ret_ent in ents:
            self.tree.insert('', tk.END, values=ret_ent)
        if ents:
            self.db_ent = self.user_db.get_entry(ents[0])

        # self.tree.bind('<<TreeviewSelect>>', self.entry_selected)
        #################################################
        # Entry
        # Name
        _x = 200
        _y = 50
        tk.Label(self, text='Name: ').place(x=_x, y=_y)
        self.name_var = tk.StringVar(self)
        self.name_ent = tk.Entry(self,
                                 textvariable=self.name_var,
                                 width=22)
        self.name_ent.place(x=_x + 80, y=_y)
        # Name
        _x = 555
        _y = 50
        tk.Label(self, text='Typ: ').place(x=_x, y=_y)
        self.typ_var = tk.StringVar(self)
        opt = [
            'SYSOP',
            'NODE',
            'BBS',
            'CONVERS',
            'OTHER',
        ]
        self.typ_var.set('SYSOP')
        self.typ_ent = tk.OptionMenu(self, self.typ_var, *opt)
        self.typ_ent.place(x=_x + 80, y=_y - 2)
        # QTH
        _x = 200
        _y = 80
        tk.Label(self, text='QTH: ').place(x=_x, y=_y)
        self.qth_var = tk.StringVar(self)
        self.qth_ent = tk.Entry(self,
                                textvariable=self.qth_var,
                                width=22)
        self.qth_ent.place(x=_x + 80, y=_y)
        # LOC
        _x = 555
        _y = 80
        tk.Label(self, text='LOC: ').place(x=_x, y=_y)
        self.loc_var = tk.StringVar(self)
        self.loc_ent = tk.Entry(self,
                                textvariable=self.loc_var,
                                width=7)
        self.loc_ent.place(x=_x + 80, y=_y)
        # ZIP
        _x = 200
        _y = 110
        tk.Label(self, text='ZIP: ').place(x=_x, y=_y)
        self.zip_var = tk.StringVar(self)
        self.zip_ent = tk.Entry(self,
                                textvariable=self.zip_var,
                                width=10)
        self.zip_ent.place(x=_x + 80, y=_y)
        # LAND
        _x = 555
        _y = 110
        tk.Label(self, text='LAND: ').place(x=_x, y=_y)
        self.land_var = tk.StringVar(self)
        self.land_ent = tk.Entry(self,
                                 textvariable=self.land_var,
                                 width=8)
        self.land_ent.place(x=_x + 80, y=_y)

        # PR-MAIL
        _x = 200
        _y = 140
        tk.Label(self, text='PR-MAIL: ').place(x=_x, y=_y)
        self.prmail_var = tk.StringVar(self)
        self.prmail_ent = tk.Entry(self,
                                   textvariable=self.prmail_var,
                                   width=32)
        self.prmail_ent.place(x=_x + 80, y=_y)
        # E-MAIL
        _x = 200
        _y = 170
        tk.Label(self, text='E-MAIL: ').place(x=_x, y=_y)
        self.email_var = tk.StringVar(self)
        self.email_ent = tk.Entry(self,
                                  textvariable=self.email_var,
                                  width=32)
        self.email_ent.place(x=_x + 80, y=_y)
        # HTTP
        _x = 200
        _y = 200
        tk.Label(self, text='WEB: ').place(x=_x, y=_y)
        self.http_var = tk.StringVar(self)
        self.http_ent = tk.Entry(self,
                                 textvariable=self.http_var,
                                 width=32)
        self.http_ent.place(x=_x + 80, y=_y)

        # CLI LANGUAGE
        _x = 200
        _y = 400
        tk.Label(self, text='Sprache: ').place(x=_x, y=_y)
        self.lang_var = tk.StringVar(self)
        lang_opt = [
            'DEUTSCH',
            'ENGLSCH',
            'NIEDERLÄNDISCH',
            'FRANZÖSISCH',
            'FINLAND',
            'POLNISCH',
            'PORTUGIESISCH',
            'ITALIENISCH',
        ]
        self.lang_var.set('DEUTSCH')
        self.lang_ent = tk.OptionMenu(self, self.lang_var, *lang_opt)
        self.lang_ent.place(x=_x + 80, y=_y - 2)
        self.set_var_to_ent()

    def select_entry(self, event=None):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values'][0]
            self.db_ent = self.user_db.get_entry(record)
            self.set_var_to_ent()
            break

    def set_var_to_ent(self):
        if self.db_ent:
            self.name_var.set(self.db_ent.Name)
            self.qth_var.set(self.db_ent.QTH)
            self.loc_var.set(self.db_ent.LOC)
            self.prmail_var.set(self.db_ent.PRmail)
            self.email_var.set(self.db_ent.Email)
            self.http_var.set(self.db_ent.HTTP)
            self.zip_var.set(self.db_ent.ZIP)
            self.land_var.set(self.db_ent.Land)
            self.typ_var.set(self.db_ent.TYP)

    def save_btn_cmd(self):
        if self.db_ent:
            self.db_ent.Name = self.name_var.get()
            self.db_ent.QTH = self.qth_var.get()
            self.db_ent.LOC = self.loc_var.get()
            self.db_ent.PRmail = self.prmail_var.get()
            self.db_ent.Email = self.email_var.get()
            self.db_ent.HTTP = self.http_var.get()
            self.db_ent.ZIP = self.zip_var.get()
            self.db_ent.Land = self.land_var.get()
            self.db_ent.TYP = self.typ_var.get()

    def ok_btn_cmd(self):
        self.root.msg_to_monitor('Info: Baken Settings wurden gespeichert..')
        self.root.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self.destroy_win()

    def del_btn_cmd(self):
        del self.user_db.db[self.db_ent.call_str]
        ents = sorted(list(self.user_db.db.keys()))
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ret_ent in ents:
            self.tree.insert('', tk.END, values=ret_ent)
        if ents:
            self.db_ent = self.user_db.get_entry(ents[0])

    def destroy_win(self):
        self.destroy()
        self.root.settings_win = None

    def tasker(self):
        pass
