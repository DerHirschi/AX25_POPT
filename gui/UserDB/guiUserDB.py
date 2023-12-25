import tkinter as tk
from tkinter import ttk
from datetime import datetime

from UserDB.UserDBmain import USER_DB
from cfg.constant import ENCODINGS, STATION_TYPS
from fnc.str_fnc import conv_time_DE_str
from cfg.string_tab import STR_TABLE
from gui.guiMsgBoxes import AskMsg


class UserDB(tk.Toplevel):
    def __init__(self, root, ent_key=''):
        tk.Toplevel.__init__(self)
        self._root_win = root
        self.lang = self._root_win.language
        self.win_height = 600
        self.win_width = 1060
        self.style = root.style
        self.title(STR_TABLE['user_db'][self.lang])
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        # self.attributes("-topmost", True)
        ###############
        # VARS
        # self.user_db = root.ax25_port_handler.user_db
        self._user_db = USER_DB
        self._db_ent = None
        self._call_label_var = tk.StringVar(self)
        self._name_var = tk.StringVar(self)
        self._typ_var = tk.StringVar(self, value='SYSOP')
        self._sysop_var = tk.StringVar(self, value='SYSOP')
        self._qth_var = tk.StringVar(self)
        self._loc_var = tk.StringVar(self)
        self._zip_var = tk.StringVar(self)
        self._land_var = tk.StringVar(self)
        self._encoding_var = tk.StringVar(self, value='UTF-8')
        self._software_var = tk.StringVar(self)
        self._prmail_var = tk.StringVar(self)
        self._email_var = tk.StringVar(self)
        self._http_var = tk.StringVar(self)
        self._lang_var = tk.StringVar(self)
        self._conn_count_var = tk.StringVar(self)
        self._dist_var = tk.StringVar(self)
        self._last_conn_var = tk.StringVar(self)
        self._last_edit_var = tk.StringVar(self)
        self._max_pac_var = tk.StringVar(self, value='0')
        self._pac_len_var = tk.StringVar(self, value='0')
        self._axip_add_var = tk.StringVar(self, value='')
        self._axip_port_var = tk.StringVar(self, value='0')
        self._fake_attempts_var = tk.StringVar(self, value='5')
        self._fill_char_var = tk.StringVar(self, value='80')
        self._login_cmd_var = tk.StringVar(self, value='SYS')
        self._stations_node_var = tk.StringVar(self)
        self._stations_bbs_var = tk.StringVar(self)
        self._stations_other_var = tk.StringVar(self)
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text=STR_TABLE['OK'][self.lang],
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self._ok_btn_cmd)

        save_bt = tk.Button(self,
                            text=STR_TABLE['save'][self.lang],
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self._save_btn_cmd)

        cancel_bt = tk.Button(self,
                              text=STR_TABLE['cancel'][self.lang],
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self._destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        del_bt = tk.Button(self,
                           text=STR_TABLE['delete'][self.lang],
                           # font=("TkFixedFont", 15),
                           bg="red",
                           height=1,
                           width=6,
                           command=self._del_btn_cmd
                           )
        del_bt.place(x=10, y=10)

        self.grid_columnconfigure(0, weight=0, minsize=15)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1, minsize=400)
        self.grid_rowconfigure(0, weight=0, minsize=50)

        self._tree = ttk.Treeview(self, columns=('call',), show='tree', height=20)
        self._tree.grid(row=1, column=1, sticky='nw')
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky='wns')

        self._tree.bind('<<TreeviewSelect>>', self._select_entry)
        self._tree.column("#0", width=0, minwidth=0)
        self._tree.column("call", anchor='w', stretch=tk.NO, width=150)

        ents = sorted(list(self._user_db.db.keys()))
        for ret_ent in ents:
            self._tree.insert('', tk.END, values=ret_ent)
        ##################################
        # Selected Call Label
        tk.Label(self,
                 textvariable=self._call_label_var,
                 font=("Courier", 14, 'bold')
                 ).place(x=int(self.win_width / 2), y=10)
        ##################################
        # tabs
        tabControl = ttk.Notebook(self, height=self.win_height - 150, width=self.win_width - 220)
        tabControl.place(x=200, y=50)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)
        tab4 = ttk.Frame(tabControl)
        tabControl.add(tab1, text=STR_TABLE['main_page'][self.lang])
        tabControl.add(tab2, text=STR_TABLE['settings'][self.lang])
        tabControl.add(tab3, text=STR_TABLE['passwords'][self.lang])
        tabControl.add(tab4, text=STR_TABLE['stations'][self.lang])
        # self.tree.bind('<<TreeviewSelect>>', self.entry_selected)
        #################################################
        # Entry
        # Name
        _x = 10
        _y = 20
        tk.Label(tab1, text='Name: ').place(x=_x, y=_y)
        name_ent = tk.Entry(tab1,
                            textvariable=self._name_var,
                            width=22)
        name_ent.place(x=_x + 80, y=_y)
        # Typ
        _x = 375
        _y = 20
        tk.Label(tab1, text='Typ: ').place(x=_x, y=_y)
        opt = STATION_TYPS
        typ_ent = tk.OptionMenu(tab1, self._typ_var, *opt)
        typ_ent.place(x=_x + 80, y=_y - 2)
        # SYSOP
        _x = 625
        _y = 20
        tk.Label(tab1, text='Sysop: ').place(x=_x, y=_y)
        opt = sorted(self._user_db.get_keys_by_typ(typ='SYSOP'))
        if not opt:
            opt = ['']
        self._sysop_ent = tk.OptionMenu(tab1,
                                        self._sysop_var,
                                        *opt,
                                        # command=lambda event: self.on_select_sysop(event)
                                        )
        # self.sysop_ent.bind()
        self._sysop_ent.place(x=_x + 100, y=_y - 2)

        # QTH
        _x = 10
        _y = 50
        tk.Label(tab1, text='QTH: ').place(x=_x, y=_y)
        qth_ent = tk.Entry(tab1,
                           textvariable=self._qth_var,
                           width=22)
        qth_ent.place(x=_x + 80, y=_y)
        # LOC
        _x = 375
        _y = 50
        tk.Label(tab1, text='LOC: ').place(x=_x, y=_y)
        loc_ent = tk.Entry(tab1,
                           textvariable=self._loc_var,
                           width=7)
        loc_ent.place(x=_x + 80, y=_y)
        # ZIP
        _x = 10
        _y = 80
        tk.Label(tab1, text='ZIP: ').place(x=_x, y=_y)
        zip_ent = tk.Entry(tab1,
                           textvariable=self._zip_var,
                           width=10)
        zip_ent.place(x=_x + 80, y=_y)
        # LAND
        _x = 375
        _y = 80
        tk.Label(tab1, text='LAND: ').place(x=_x, y=_y)
        land_ent = tk.Entry(tab1,
                            textvariable=self._land_var,
                            width=8)
        land_ent.place(x=_x + 80, y=_y)
        # Ecoding
        _x = 455
        _y = 110
        tk.Label(tab1, text=f"{STR_TABLE['txt_decoding'][self.lang]}: ").place(x=_x, y=_y)
        opt = list(ENCODINGS)
        encoding_ent = tk.OptionMenu(tab1, self._encoding_var, *opt)
        encoding_ent.place(x=_x + 185, y=_y - 2)
        # Software
        _x = 455
        _y = 140
        tk.Label(tab1, textvariable=self._software_var).place(x=_x, y=_y)

        # PR-MAIL
        _x = 10
        _y = 110
        tk.Label(tab1, text='PR-MAIL: ').place(x=_x, y=_y)
        prmail_ent = tk.Entry(tab1,
                              textvariable=self._prmail_var,
                              width=32)
        prmail_ent.place(x=_x + 80, y=_y)
        # E-MAIL
        _x = 10
        _y = 140
        tk.Label(tab1, text='E-MAIL: ').place(x=_x, y=_y)
        email_ent = tk.Entry(tab1,
                             textvariable=self._email_var,
                             width=32)
        email_ent.place(x=_x + 80, y=_y)
        # HTTP
        _x = 10
        _y = 170
        tk.Label(tab1, text='WEB: ').place(x=_x, y=_y)
        http_ent = tk.Entry(tab1,
                            textvariable=self._http_var,
                            width=32)
        http_ent.place(x=_x + 80, y=_y)

        # Stat Infos / Bemerkungen
        _x = 10
        _y = 200
        tk.Label(tab1, text='Infos: ').place(x=_x, y=_y)
        # self.info_var = tk.StringVar(self)
        self._info_ent = tk.Text(tab1,
                                 width=65,
                                 height=9
                                 )
        self._info_ent.place(x=_x + 80, y=_y)

        # CLI LANGUAGE   # TODO
        _x = 10
        _y = 400
        tk.Label(tab1, text='Sprache: ').place(x=_x, y=_y)
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
        self._lang_var.set('DEUTSCH')
        lang_ent = tk.OptionMenu(tab1, self._lang_var, *lang_opt)
        lang_ent.configure(state='disabled')  # TODO
        lang_ent.place(x=_x + 80, y=_y - 2)

        # Connection Counter
        tk.Label(tab1, text='Connections: ').place(x=240, y=393)
        tk.Label(tab1, textvariable=self._conn_count_var).place(x=357, y=393)
        # Distance
        tk.Label(tab1, text='Distance: ').place(x=240, y=417)
        tk.Label(tab1, textvariable=self._dist_var).place(x=357, y=417)

        # Last Connection
        tk.Label(tab1, text='Last Conn: ').place(x=460, y=393)
        tk.Label(tab1, textvariable=self._last_conn_var).place(x=560, y=393)
        # Last Edit
        tk.Label(tab1, text='Last Edit: ').place(x=460, y=417)
        tk.Label(tab1, textvariable=self._last_edit_var).place(x=560, y=417)
        # self.last_conn_var.set('2023-05-08 13:12:12')

        #######################
        # TAB2
        # C-TEXT
        _x = 10
        _y = 10
        tk.Label(tab2, text='C-Text: ').place(x=_x, y=_y)
        # self.info_var = tk.StringVar(self)
        self._ctext_ent = tk.Text(tab2,
                                  width=80,
                                  height=12
                                  )
        self._ctext_ent.place(x=_x, y=_y + 30)

        # Max-PAc
        _x = 10
        _y = 300
        tk.Label(tab2, text='Max-Pac: ').place(x=_x, y=_y)
        max_pac_opt = list(range(8))
        max_pac_ent = tk.OptionMenu(tab2,
                                    self._max_pac_var,
                                    *max_pac_opt
                                    )
        max_pac_ent.place(x=_x + 85, y=_y - 2)
        # Pac-Len
        _x = 200
        _y = 300
        tk.Label(tab2, text='Pac-Len: ').place(x=_x, y=_y)
        # max_pac_opt = list(range(8))
        pac_len_ent = tk.Spinbox(tab2,
                                 textvariable=self._pac_len_var,
                                 from_=0,
                                 to=256,
                                 increment=10,
                                 width=4
                                 )
        pac_len_ent.place(x=_x + 85, y=_y - 2)

        # AXIP-ADD
        _x = 10
        _y = 340
        tk.Label(tab2, text='AXIP-Address: ').place(x=_x, y=_y)
        axip_add_ent = tk.Entry(tab2,
                                textvariable=self._axip_add_var,
                                width=40
                                )
        axip_add_ent.place(x=_x + 130, y=_y - 2)

        # AXIP-Port
        _x = 10
        _y = 380
        tk.Label(tab2, text='AXIP-Port: ').place(x=_x, y=_y)
        axip_port_ent = tk.Entry(tab2,
                                 textvariable=self._axip_port_var,
                                 width=6
                                 )
        axip_port_ent.place(x=_x + 130, y=_y - 2)

        #######################
        # TAB3
        # Passwörter
        # Sys-PW
        _x = 20
        _y = 20
        tk.Label(tab3, text=STR_TABLE['syspassword'][self.lang]).place(x=_x, y=_y)
        # self.sys_password_var = tk.StringVar(self)
        self._sys_password_ent = tk.Text(tab3,
                                         height=5,
                                         width=80)
        _x = 15
        _y = 60
        self._sys_password_ent.place(x=_x, y=_y)
        # Fake-Attempts inclusive real attempt
        _x = 20
        _y = 200
        tk.Label(tab3, text=STR_TABLE['trys'][self.lang]).place(x=_x, y=_y)

        # max_pac_opt = list(range(8))
        fake_attempts_ent = tk.Spinbox(tab3,
                                       textvariable=self._fake_attempts_var,
                                       from_=1,
                                       to=10,
                                       increment=1,
                                       width=3
                                       )
        fake_attempts_ent.place(x=_x + 140, y=_y - 2)
        # Fill Chars
        _x = 300
        _y = 200
        tk.Label(tab3, text=STR_TABLE['fillchars'][self.lang]).place(x=_x, y=_y)

        # max_pac_opt = list(range(8))
        fill_chars_ent = tk.Spinbox(tab3,
                                    textvariable=self._fill_char_var,
                                    from_=0,
                                    to=120,
                                    increment=10,
                                    width=4
                                    )
        fill_chars_ent.place(x=_x + 140, y=_y - 2)
        # Login CMD
        _x = 20
        _y = 240
        tk.Label(tab3, text=STR_TABLE['login_cmd'][self.lang]).place(x=_x, y=_y)

        tk.Entry(tab3, textvariable=self._login_cmd_var, width=20).place(x=_x + 170, y=_y)
        #######################
        # TAB4
        # Stationen
        # NODES
        _x = 20
        _y = 20
        tk.Label(tab4, textvariable=self._stations_node_var).place(x=_x, y=_y)
        # self.stations_node_var.set('NODES: ')
        # BBS
        _x = 20
        _y = 60
        tk.Label(tab4, textvariable=self._stations_bbs_var).place(x=_x, y=_y)
        # self.stations_bbs_var.set('BBS: ')
        # Other
        _x = 20
        _y = 100
        tk.Label(tab4, textvariable=self._stations_other_var).place(x=_x, y=_y)
        # self.stations_other_var.set('OTHER: ')

        if not ent_key:
            self._select_entry_fm_ch_id()
        else:
            self._select_entry_fm_key(ent_key)
        root.userdb_win = self

    def _select_entry(self, event=None):
        self._save_vars()
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values'][0]
            self._db_ent = self._user_db.get_entry(record)
            self._set_var_to_ent()
            break

    def _select_entry_fm_ch_id(self):
        conn = self._root_win.get_conn()
        if conn is not None:
            self._db_ent = conn.user_db_ent
            self._set_var_to_ent()

    def _select_entry_fm_key(self, key: str):
        if key in self._user_db.db.keys():
            self._db_ent = self._user_db.db[key]
            self._set_var_to_ent()

    def _on_select_sysop(self, event=None):
        if self._db_ent is not None:
            msg = AskMsg(titel=f'Einträge ergänzen?', message=f"Einträge vom Sysop ergänzen ?")
            # self.settings_win.lift()
            if msg:
                sysop_key = self._sysop_var.get()
                if sysop_key in self._user_db.db.keys():
                    self._user_db.update_var_fm_dbentry(fm_key=sysop_key, to_key=self._db_ent.call_str)
                    self._set_var_to_ent()

    def _set_var_to_ent(self):
        if self._db_ent is not None:
            self._call_label_var.set(self._db_ent.call_str)
            self._name_var.set(self._db_ent.Name)
            self._qth_var.set(self._db_ent.QTH)
            self._loc_var.set(self._db_ent.LOC)
            self._dist_var.set(f"{round(self._db_ent.Distance, 1)} km")
            self._prmail_var.set(self._db_ent.PRmail)
            self._email_var.set(self._db_ent.Email)
            self._http_var.set(self._db_ent.HTTP)
            self._encoding_var.set(self._db_ent.Encoding)
            self._software_var.set(self._db_ent.Software)
            self._zip_var.set(self._db_ent.ZIP)
            self._land_var.set(self._db_ent.Land)
            self._typ_var.set(self._db_ent.TYP)

            self._pac_len_var.set(str(self._db_ent.pac_len))
            self._max_pac_var.set(str(self._db_ent.max_pac))
            """self.last_edit_var.set(
                f"{self.db_ent.last_edit.date()} - "
                f"{self.db_ent.last_edit.time().hour}:"
                f"{self.db_ent.last_edit.time().minute}"
            )"""
            self._last_edit_var.set(conv_time_DE_str(self._db_ent.last_edit))
            self._last_conn_var.set(conv_time_DE_str(self._db_ent.last_seen))
            self._conn_count_var.set(str(self._db_ent.Connects))

            self._info_ent.delete(0.0, tk.END)
            self._info_ent.insert(tk.INSERT, self._db_ent.Info)

            self._ctext_ent.delete(0.0, tk.END)
            self._ctext_ent.insert(tk.INSERT, self._db_ent.CText)

            # self.sys_password_ent.delete(0.0, tk.END)
            self._sys_password_ent.delete(0.0, tk.END)
            self._sys_password_ent.insert(tk.INSERT, str(self._db_ent.sys_pw))
            self._fake_attempts_var.set(str(self._db_ent.sys_pw_parm[0]))
            self._fill_char_var.set(str(self._db_ent.sys_pw_parm[1]))
            if len(self._db_ent.sys_pw_parm) == 2:
                self._db_ent.sys_pw_parm.append('SYS')
            self._login_cmd_var.set(str(self._db_ent.sys_pw_parm[2]))
            axip = self._db_ent.AXIP
            if not axip:
                axip = '', 0
            self._axip_add_var.set(axip[0])
            self._axip_port_var.set(axip[1])
            self._update_sysop_opt()
            self._update_stations()

    def _sysop_opt_remove(self):
        self._sysop_var.set('')  # remove default selection only, not the full list
        self._sysop_ent['menu'].delete(0, 'end')  # remove full list

    def _update_sysop_opt(self):
        self._sysop_opt_remove()  # remove all options

        if self._db_ent.TYP == 'SYSOP':
            self._sysop_var.set('')
            self._sysop_ent.configure(state='disabled')

        else:
            self._sysop_ent.configure(state='normal')
            self._sysop_var.set(self._db_ent.Sysop_Call)
            # print(f"Sysop_ca: {self._db_ent.Sysop_Call}")
            self._sysop_ent.setvar(self._db_ent.Sysop_Call)

            for opt in sorted(self._user_db.get_keys_by_typ(typ='SYSOP')):
                self._sysop_ent['menu'].add_command(label=opt, command=tk._setit(self._sysop_var, opt))

    def _update_stations(self):
        sysop_key = ''
        if self._db_ent is not None:
            if self._db_ent.TYP == 'SYSOP':
                sysop_key = self._db_ent.call_str
            else:
                sysop_key = self._db_ent.Sysop_Call

        node_str = 'NODES: '
        bbs_str = 'BBS: '
        other_str = 'OTHER: '

        if sysop_key:
            stat_dict = self._user_db.get_keys_by_sysop(sysop=sysop_key)
            node_calls = stat_dict['NODE']
            bbs_calls = stat_dict['BBS']
            other_calls = []
            for k in stat_dict.keys():
                if k not in ['NODE', 'BBS']:
                    for call in stat_dict[k]:
                        other_calls.append(call)
            node_str = node_str + ' '.join(node_calls)
            bbs_str = bbs_str + ' '.join(bbs_calls)
            other_str = other_str + ' '.join(other_calls)

        self._stations_node_var.set(node_str)
        self._stations_bbs_var.set(bbs_str)
        self._stations_other_var.set(other_str)

    def _save_btn_cmd(self):
        self._save_vars()
        self._user_db.save_data()
        self._select_entry()
        self._root_win.update_station_info()
        if self._db_ent is None:
            return
        self._root_win.sysMsg_to_monitor(f'Info: User Daten für {self._db_ent.call_str} wurden gespeichert..')

    def _save_vars(self):
        if self._db_ent is not None:
            self._db_ent.Name = str(self._name_var.get())
            self._db_ent.QTH = str(self._qth_var.get())
            self._db_ent.LOC = str(self._loc_var.get())

            self._db_ent.PRmail = str(self._prmail_var.get())
            self._db_ent.Email = str(self._email_var.get())
            self._db_ent.HTTP = str(self._http_var.get())
            self._db_ent.Encoding = str(self._encoding_var.get())
            self._db_ent.ZIP = str(self._zip_var.get())
            self._db_ent.Land = str(self._land_var.get())

            self._db_ent.pac_len = int(self._pac_len_var.get())
            self._db_ent.max_pac = int(self._max_pac_var.get())
            self._db_ent.CText = str(self._ctext_ent.get(0.0, tk.END)[:-1])
            self._db_ent.Info = str(self._info_ent.get(0.0, tk.END)[:-1])

            self._db_ent.sys_pw = str(self._sys_password_ent.get(0.0, tk.END)[:-1])
            self._db_ent.sys_pw_parm = [
                int(self._fake_attempts_var.get()),
                int(self._fill_char_var.get()),
                str(self._login_cmd_var.get()),
            ]

            self._db_ent.last_edit = datetime.now()
            self._db_ent.TYP = str(self._typ_var.get())
            if self._db_ent.TYP == 'SYSOP':
                self._db_ent.Sysop_Call = ''
            else:
                tmp = str(self._sysop_var.get())
                if tmp != self._db_ent.Sysop_Call:
                    self._db_ent.Sysop_Call = tmp
                    self._on_select_sysop()
            axip_add = self._axip_add_var.get()
            axip_add = axip_add.replace(' ', '')
            axip_port = self._axip_port_var.get()
            try:
                axip_port = int(axip_port)
            except ValueError:
                axip_port = 0
            self._db_ent.AXIP = (
                axip_add,
                axip_port
            )
        self._root_win.gui_set_distance()

    def _clean_ent(self):
        self._db_ent = None
        self._call_label_var.set('')
        self._name_var.set('')
        self._qth_var.set('')
        self._loc_var.set('')
        self._dist_var.set('')
        self._prmail_var.set('')
        self._email_var.set('')
        self._http_var.set('')
        self._encoding_var.set('')
        self._software_var.set('')
        self._zip_var.set('')
        self._land_var.set('')
        self._typ_var.set('')

        self._pac_len_var.set(str(0))
        self._max_pac_var.set(str(0))

        self._last_edit_var.set('')
        self._last_conn_var.set('')
        self._conn_count_var.set(str(0))

        self._info_ent.delete(0.0, tk.END)
        self._ctext_ent.delete(0.0, tk.END)

        # self.sys_password_ent.delete(0.0, tk.END)
        self._sys_password_ent.delete(0.0, tk.END)
        self._fake_attempts_var.set(str(0))
        self._fill_char_var.set(str(0))

        self._login_cmd_var.set('')

    def _ok_btn_cmd(self):
        self._save_vars()
        self._root_win.sysMsg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self._destroy_win()

    def _del_btn_cmd(self):
        if self._db_ent is not None:
            msg = AskMsg(titel=f'lösche {self._db_ent.call_str} !', message=f"{self._db_ent.call_str} löschen ?")
            # self.settings_win.lift()
            if msg:
                self._user_db.del_entry(str(self._db_ent.call_str))
                ents = sorted(list(self._user_db.db.keys()))
                for i in self._tree.get_children():
                    self._tree.delete(i)
                for ret_ent in ents:
                    self._tree.insert('', tk.END, values=ret_ent)
                if ents:
                    self._db_ent = self._user_db.get_entry(ents[0])
                self._clean_ent()

    def _destroy_win(self):
        self._root_win.userdb_win = None
        self.destroy()

    def tasker(self):
        pass
