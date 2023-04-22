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

        ##################################
        # tabs
        self.tabControl = ttk.Notebook(self, height=self.win_height - 150, width=self.win_width - 220)
        self.tabControl.place(x=200, y=50)
        tab1 = ttk.Frame(self.tabControl)
        tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(tab1, text=STR_TABLE['main_page'][self.lang])
        self.tabControl.add(tab2, text=STR_TABLE['settings'][self.lang])
        # self.tree.bind('<<TreeviewSelect>>', self.entry_selected)
        #################################################
        # Entry
        # Name
        _x = 10
        _y = 20
        tk.Label(tab1, text='Name: ').place(x=_x, y=_y)
        self.name_var = tk.StringVar(self)
        self.name_ent = tk.Entry(tab1,
                                 textvariable=self.name_var,
                                 width=22)
        self.name_ent.place(x=_x + 80, y=_y)
        # Name
        _x = 375
        _y = 20
        tk.Label(tab1, text='Typ: ').place(x=_x, y=_y)
        self.typ_var = tk.StringVar(self)
        opt = [
            'SYSOP',
            'NODE',
            'BBS',
            'CONVERS',
            'OTHER',
        ]
        self.typ_var.set('SYSOP')
        self.typ_ent = tk.OptionMenu(tab1, self.typ_var, *opt)
        self.typ_ent.place(x=_x + 80, y=_y - 2)
        # QTH
        _x = 10
        _y = 50
        tk.Label(tab1, text='QTH: ').place(x=_x, y=_y)
        self.qth_var = tk.StringVar(self)
        self.qth_ent = tk.Entry(tab1,
                                textvariable=self.qth_var,
                                width=22)
        self.qth_ent.place(x=_x + 80, y=_y)
        # LOC
        _x = 375
        _y = 50
        tk.Label(tab1, text='LOC: ').place(x=_x, y=_y)
        self.loc_var = tk.StringVar(self)
        self.loc_ent = tk.Entry(tab1,
                                textvariable=self.loc_var,
                                width=7)
        self.loc_ent.place(x=_x + 80, y=_y)
        # ZIP
        _x = 10
        _y = 80
        tk.Label(tab1, text='ZIP: ').place(x=_x, y=_y)
        self.zip_var = tk.StringVar(self)
        self.zip_ent = tk.Entry(tab1,
                                textvariable=self.zip_var,
                                width=10)
        self.zip_ent.place(x=_x + 80, y=_y)
        # LAND
        _x = 375
        _y = 80
        tk.Label(tab1, text='LAND: ').place(x=_x, y=_y)
        self.land_var = tk.StringVar(self)
        self.land_ent = tk.Entry(tab1,
                                 textvariable=self.land_var,
                                 width=8)
        self.land_ent.place(x=_x + 80, y=_y)

        # PR-MAIL
        _x = 10
        _y = 110
        tk.Label(tab1, text='PR-MAIL: ').place(x=_x, y=_y)
        self.prmail_var = tk.StringVar(self)
        self.prmail_ent = tk.Entry(tab1,
                                   textvariable=self.prmail_var,
                                   width=32)
        self.prmail_ent.place(x=_x + 80, y=_y)
        # E-MAIL
        _x = 10
        _y = 140
        tk.Label(tab1, text='E-MAIL: ').place(x=_x, y=_y)
        self.email_var = tk.StringVar(self)
        self.email_ent = tk.Entry(tab1,
                                  textvariable=self.email_var,
                                  width=32)
        self.email_ent.place(x=_x + 80, y=_y)
        # HTTP
        _x = 10
        _y = 170
        tk.Label(tab1, text='WEB: ').place(x=_x, y=_y)
        self.http_var = tk.StringVar(self)
        self.http_ent = tk.Entry(tab1,
                                 textvariable=self.http_var,
                                 width=32)
        self.http_ent.place(x=_x + 80, y=_y)
        # Stat Infos / Bemerkungen
        _x = 10
        _y = 200
        tk.Label(tab1, text='Infos: ').place(x=_x, y=_y)
        # self.info_var = tk.StringVar(self)
        self.info_ent = tk.Text(tab1,
                                width=65,
                                height=9
                                )
        self.info_ent.place(x=_x + 80, y=_y)

        # CLI LANGUAGE
        _x = 10
        _y = 400
        tk.Label(tab1, text='Sprache: ').place(x=_x, y=_y)
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
        self.lang_ent = tk.OptionMenu(tab1, self.lang_var, *lang_opt)
        self.lang_ent.place(x=_x + 80, y=_y - 2)
        #######################
        # TAB2
        # C-TEXT
        _x = 10
        _y = 10
        tk.Label(tab2, text='C-Text: ').place(x=_x, y=_y)
        # self.info_var = tk.StringVar(self)
        self.ctext_ent = tk.Text(tab2,
                                 width=80,
                                 height=12
                                 )
        self.ctext_ent.place(x=_x, y=_y + 30)

        # Max-PAc
        _x = 10
        _y = 300
        tk.Label(tab2, text='Max-Pac: ').place(x=_x, y=_y)
        self.max_pac_var = tk.StringVar(self)
        self.max_pac_var.set('0')
        max_pac_opt = list(range(8))
        self.max_pac_ent = tk.OptionMenu(tab2,
                                         self.max_pac_var,
                                         *max_pac_opt
                                         )
        self.max_pac_ent.place(x=_x + 85, y=_y - 2)
        # Pac-Len
        _x = 200
        _y = 300
        tk.Label(tab2, text='Pac-Len: ').place(x=_x, y=_y)
        self.pac_len_var = tk.StringVar(self)
        self.pac_len_var.set('0')
        # max_pac_opt = list(range(8))
        self.pac_len_ent = tk.Spinbox(tab2,
                                      textvariable=self.pac_len_var,
                                      from_=0,
                                      to=256,
                                      increment=10,
                                      width=4
                                      )
        self.pac_len_ent.place(x=_x + 85, y=_y - 2)

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

            self.info_ent.delete(0.0, tk.END)
            self.info_ent.insert(tk.INSERT, self.db_ent.Info)

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
            self.db_ent.Info = self.info_ent.get(0.0, tk.END)[:-1]
        self.user_db.save_data()

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
