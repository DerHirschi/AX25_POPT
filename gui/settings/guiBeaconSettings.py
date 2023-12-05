import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk as ttk
from tkinter import scrolledtext
from ax25.ax25Beacon import Beacon
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import GUI_DISABLED_CLR
from fnc.str_fnc import tk_filter_bad_chars
from cfg.string_tab import STR_TABLE


class BeaconTab:
    def __init__(self, root, tabclt: ttk.Notebook, beacon: Beacon):
        self._tab_clt = tabclt
        self._root = root
        self._lang = self._root.lang
        self.style = root.style
        self.own_tab = ttk.Frame(self._tab_clt)
        self.beacon = beacon
        # height = root.win_height
        # width = root.win_width
        #################
        # Von
        call_x = 10
        call_y = 20
        call_label = tk.Label(self.own_tab, text=f"{STR_TABLE['from'][self._lang]}:")
        call_label.place(x=call_x, y=call_y)
        self.from_select_var = tk.StringVar(self.own_tab)
        self.from_opt = dict(PORT_HANDLER.ax25_stations_settings)
        self.from_select_var.set(beacon.from_call)  # default value
        opt = list(self.from_opt.keys())
        if not opt:
            opt = ['NOCALL']
        from_call = tk.OptionMenu(self.own_tab, self.from_select_var, *opt, command=self._cmd_fm_call_set)
        from_call.configure(width=8, height=1)
        from_call.place(x=call_x + 55, y=call_y - 5)

        #################
        #################
        # An
        call_x = 220
        call_y = 20
        call_label = tk.Label(self.own_tab, text=f"{STR_TABLE['to'][self._lang]}:")
        call_label.place(x=call_x, y=call_y)
        self.call = tk.Entry(self.own_tab, width=9)
        self.call.place(x=call_x + 35, y=call_y)
        self.call.insert(tk.END, beacon.to_call)
        #################
        # VIA
        call_x = 370
        call_y = 20
        call_label = tk.Label(self.own_tab, text='VIA:')
        call_label.place(x=call_x, y=call_y)
        self.via = tk.Entry(self.own_tab, width=35)
        self.via.place(x=call_x + 40, y=call_y)
        self.via.insert(tk.END, beacon.via_calls)
        #################
        #################
        # CTL or RPT
        call_x = 750
        call_y = 20
        self.aprs_check_var = tk.IntVar(self.own_tab)
        self.aprs_check = tk.Checkbutton(self.own_tab,
                                         text='CTL/RPT',
                                         variable=self.aprs_check_var)
        self.aprs_check.var = self.aprs_check_var
        if self.beacon.aprs:
            self.aprs_check.select()
            self.aprs_check_var.set(1)
        self.aprs_check.place(x=call_x + 55, y=call_y)
        #################
        # Poll
        call_x = 750
        call_y = 55
        self.pool_check_var = tk.IntVar(self.own_tab)
        self.pool_check = tk.Checkbutton(self.own_tab,
                                         text='Poll',
                                         variable=self.pool_check_var)
        self.pool_check.var = self.pool_check_var
        if self.beacon.pool:
            self.pool_check.select()
            self.pool_check_var.set(1)
        self.pool_check.place(x=call_x + 55, y=call_y)
        #################
        #################
        # Port
        call_x = 10
        call_y = 55
        call_label = tk.Label(self.own_tab, text=f"{STR_TABLE['port'][self._lang]}:")
        call_label.place(x=call_x, y=call_y)
        self.port_select_var = tk.StringVar(self.own_tab)
        self.port_opt = PORT_HANDLER.get_all_ports()
        self.port_select_var.set(str(self.beacon.port_id))  # default value
        opt = list(self.port_opt.keys())
        if not opt:
            opt = ['0']

        port = tk.OptionMenu(self.own_tab, self.port_select_var, *opt, command=self._root.change_port)
        port.configure(width=8, height=1)
        port.place(x=call_x + 55, y=call_y - 5)
        #################
        #################
        # Intervall
        call_x = 220
        call_y = 55
        call_label = tk.Label(self.own_tab, text=f"{STR_TABLE['intervall'][self._lang]} (min):")
        call_label.place(x=call_x, y=call_y)
        self.interv = tk.Entry(self.own_tab, width=4)
        self.interv.place(x=call_x + 135, y=call_y)
        self.interv.insert(tk.END, str(self.beacon.repeat_time))
        #################
        # Versatz
        call_x = 420
        call_y = 55
        move_label = tk.Label(self.own_tab, text=f"{STR_TABLE['versatz'][self._lang]} (sek):")
        move_label.place(x=call_x, y=call_y)
        self.move = tk.Entry(self.own_tab, width=5)
        self.move.place(x=call_x + 135, y=call_y)
        self.move.insert(tk.END, str(self.beacon.move_time))
        #################
        #################
        # Active Checkbox
        call_x = 750
        call_y = 90
        self.active_check_var = tk.IntVar(self.own_tab)
        self.active_check = tk.Checkbutton(self.own_tab,
                                           text=STR_TABLE['active'][self._lang],
                                           variable=self.active_check_var,
                                           command=self._cmd_be_enabled)
        self.active_check.var = self.active_check_var
        self.active_check.place(x=call_x + 55, y=call_y)
        if self.beacon.is_enabled:
            self.active_check_var.set(1)
            self.active_check.select()

        ########################
        # Typ TEXT/MH/File bla .. .
        call_x = 750
        call_y = 125
        tk.Label(self.own_tab, text='Typ: ').place(x=call_x + 68, y=call_y)
        _options = ["Text", "File", "MH"]
        self.beacon_type_var = tk.StringVar(self.own_tab)
        self.beacon_type_var.set(self.beacon.typ)
        self.beacon_type = tk.OptionMenu(self.own_tab,
                                         self.beacon_type_var,
                                         command=self._cmd_be_change_typ,
                                         *_options
                                         )
        self.beacon_type.place(x=call_x + 125, y=call_y)

        ###################################################################
        #################
        #################
        # Minutes Selector
        call_x = 10
        call_y = 90
        minutes_sel_lable = tk.Label(self.own_tab, text=f"{STR_TABLE['minutes'][self._lang]}:")
        minutes_sel_lable.place(x=call_x, y=call_y)
        self.minutes_sel = []
        tr = False
        for minute in range(12):
            text = minute * 5
            minutes_sel_var = tk.BooleanVar(self.own_tab)
            minutes_sel = tk.Checkbutton(self.own_tab,
                                         text=str(text),
                                         variable=minutes_sel_var,
                                         command=self._check_hour_minutes_cmd)
            minutes_sel.configure(state='disabled')  # TODO
            minutes_sel.var = minutes_sel_var
            minutes_sel.place(x=call_x + 75 + (55 * minute), y=call_y)
            self.minutes_sel.append((minutes_sel_var, minutes_sel))
            if self.beacon.minutes[minute]:
                minutes_sel_var.set(True)
                minutes_sel.select()
                tr = True
        #########################
        # Disable Intervall Ent
        if tr:
            self.interv.configure(state='disabled')

        #################
        # Std Selector
        call_x = 10
        call_y = 122
        std_sel_lable = tk.Label(self.own_tab, text=f"{STR_TABLE['hours'][self._lang]}:")
        std_sel_lable.place(x=call_x, y=call_y)
        self.std_sel = []
        for std in range(24):
            text = std
            std_var = tk.BooleanVar(self.own_tab)
            std_sel = tk.Checkbutton(self.own_tab,
                                     text=str(text),
                                     variable=std_var,
                                     command=self._check_hour_minutes_cmd)
            # command=self.cmd_be_enabled)
            std_sel.var = std_var
            if self.beacon.hours[std]:
                std_var.set(True)
                std_sel.select()
                # tr = True
            if std > 11:
                std = std - 12
                std_sel.place(x=call_x + 75 + (55 * std), y=call_y + 21)
            else:
                std_sel.place(x=call_x + 75 + (55 * std), y=call_y)
            self.std_sel.append((std_var, std_sel))

        #################
        # Tag Selector
        call_x = 10
        call_y = 173
        tag_sel_lable = tk.Label(self.own_tab, text=f"{STR_TABLE['day'][self._lang]}:")
        tag_sel_lable.place(x=call_x, y=call_y)
        self.tag_sel = []
        for tag in list(self.beacon.week_days.keys()):
            ind = list(self.beacon.week_days.keys()).index(tag)
            sel_var = tk.BooleanVar(self.own_tab)
            sel = tk.Checkbutton(self.own_tab,
                                 text=tag,
                                 variable=sel_var,
                                 command=self._check_day_cmd)

            # command=self.cmd_be_enabled)
            sel.var = sel_var
            sel.place(x=call_x + 75 + (65 * ind), y=call_y)
            self.tag_sel.append((sel_var, sel))
            if self.beacon.week_days[tag]:
                sel_var.set(True)
                sel.select()
        #################
        # Monat Selector
        call_x = 10
        call_y = 205
        tag_sel_lable = tk.Label(self.own_tab, text=f"{STR_TABLE['month'][self._lang]}:")
        tag_sel_lable.place(x=call_x, y=call_y)
        self.monat_sel = []
        for monat in range(12):
            # text = ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO'][tag]
            sel_var = tk.BooleanVar(self.own_tab)
            sel = tk.Checkbutton(self.own_tab,
                                 text=str(monat + 1),
                                 variable=sel_var,
                                 command=self._check_month_cmd)
            # command=self.cmd_be_enabled)
            sel.var = sel_var
            sel.place(x=call_x + 75 + (55 * monat), y=call_y)
            self.monat_sel.append((sel_var, sel))
            if self.beacon.month[monat]:
                sel_var.set(True)
                sel.select()

        #################
        # Beacon Text
        call_x = 10
        call_y = 235
        # call_y = 100
        self.b_text_ent = tk.scrolledtext.ScrolledText(self.own_tab, font=("Courier", 12))
        # self.b_text_ent.configure(width=83, height=15)
        self.b_text_ent.configure(width=82, height=8)
        self.b_text_ent.place(x=call_x, y=call_y)
        self.b_text_ent.insert(tk.END, self.beacon.text)

        #################
        # Aus Datei
        call_x = 10
        call_y = self._root.win_height - 180
        # call_y = 100
        call_label = tk.Label(self.own_tab, text=f"{STR_TABLE['text_fm_file'][self._lang]}:")
        call_label.place(x=call_x, y=call_y)
        self.be_txt_filename_var = tk.StringVar(self.own_tab)
        self.be_txt_filename = tk.Entry(self.own_tab, textvariable=self.be_txt_filename_var, width=50)
        self.be_txt_filename.bind("<KeyRelease>", self._on_key_press_filename_ent)
        self._b_text_bg_color = self.b_text_ent.cget('background')
        if self.beacon.text_filename:
            self.be_txt_filename_var.set(self.beacon.text_filename)
            self.b_text_ent.configure(state='disabled', background='#b1b1b3')
        self.be_txt_filename.place(x=call_x + 140, y=call_y)
        be_txt_openfile_btn = tk.Button(self.own_tab, text='Datei', command=self._select_files)
        be_txt_openfile_btn.place(x=call_x + 710, y=call_y - 2)

        self._cmd_be_change_typ()

    def _cmd_be_enabled(self):
        self.beacon.is_enabled = bool(self.active_check_var.get())

    def _cmd_fm_call_set(self, event):
        self.beacon.set_from_call(self.from_select_var.get())
        _label_txt = '{} {}'.format(self.port_select_var.get(), self.from_select_var.get())
        self._root.tabControl.tab(self._root.tab_list.index(self), text=_label_txt)
        self._root.change_port(None)

    def _on_key_press_filename_ent(self, event):
        # print(event)
        filenames = self.be_txt_filename_var.get()
        if filenames:
            self.beacon.text_filename = filenames

            if self.beacon.set_text_fm_file():
                self.b_text_ent.configure(state='normal', background=GUI_DISABLED_CLR)
                self.b_text_ent.delete('1.0', tk.END)
                self.b_text_ent.insert(tk.END, tk_filter_bad_chars(self.beacon.text))
                self.b_text_ent.configure(state='disabled')
            else:
                self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)
                # self.be_txt_filename_var.set('')
                self.beacon.text_filename = ''
        else:
            # self.be_txt_filename_var.set('')
            self.beacon.text_filename = ''
            self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)

    def _select_files(self):
        self._root.attributes("-topmost", False)
        # self.root.lower
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='data/',
            filetypes=filetypes)

        if filenames:
            self.be_txt_filename_var.set(filenames[0])
            self.beacon.text_filename = filenames[0]
            if self.beacon.set_text_fm_file():
                self.b_text_ent.configure(state='normal', background=GUI_DISABLED_CLR)
                self.b_text_ent.delete('1.0', tk.END)
                self.b_text_ent.insert(tk.END, tk_filter_bad_chars(self.beacon.text))
                self.b_text_ent.configure(state='disabled')
            else:
                self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)
                self.be_txt_filename_var.set('')
                self.beacon.text_filename = ''
        else:
            self.be_txt_filename_var.set('')
            self.beacon.text_filename = ''
            self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)

    def _check_day_cmd(self):
        # self.tag_sel.append((sel_var, sel))
        for selector in self.tag_sel:
            var = selector[0].get()
            tag = selector[1].cget('text')
            self.beacon.week_days[tag] = var

    def _check_month_cmd(self):
        # self.tag_sel.append((sel_var, sel))
        for k in list(self.beacon.month.keys()):
            selector = self.monat_sel[k]
            var = selector[0].get()
            self.beacon.month[k] = var

    def _check_hour_minutes_cmd(self):
        # self.tag_sel.append((sel_var, sel))
        tr = False
        for k in list(self.beacon.hours.keys()):
            selector = self.std_sel[k]
            var = selector[0].get()
            self.beacon.hours[k] = var
            """
            if var:
                tr = True
            """
        for k in list(self.beacon.minutes.keys()):
            selector = self.minutes_sel[k]
            var = selector[0].get()
            self.beacon.minutes[k] = var
            if var:
                tr = True
        if tr:
            self.interv.configure(state='disabled')
        else:
            self.interv.configure(state='normal')

    def _cmd_be_change_typ(self, event=None):
        if self.beacon_type_var.get() == "Text":
            self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)
            self.be_txt_filename.configure(state='disabled', background=GUI_DISABLED_CLR)
        elif self.beacon_type_var.get() == "File":
            self.b_text_ent.configure(state='disabled', background=GUI_DISABLED_CLR)
            self.be_txt_filename.configure(state='normal', background=self._b_text_bg_color)
        # elif self.beacon_type_var.get() == "MH":
        else:
            self.b_text_ent.configure(state='disabled', background=GUI_DISABLED_CLR)
            self.be_txt_filename.configure(state='disabled', background=GUI_DISABLED_CLR)


class BeaconSettings(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self._main_cl = main_win
        self.lang = self._main_cl.language
        main_win.settings_win = self
        self.win_height = 600
        self.win_width = 1060
        self.style = main_win.style
        self.title(STR_TABLE['beacon_settings'][self.lang])
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._main_cl.main_win.winfo_x()}+"
                      f"{self._main_cl.main_win.winfo_y()}")
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
        # self.port_handler = main_win.ax25_port_handler
        # self.all_beacons: {int: {str: [Beacon]}} = self.port_handler.beacons
        ##########################
        # OK, Save, Cancel
        tk.Button(self,
                  text=STR_TABLE['OK'][self.lang],
                  # font=("TkFixedFont", 15),
                  # bg="green",
                  height=1,
                  width=6,
                  command=self._ok_btn_cmd).place(x=20, y=self.win_height - 50)

        tk.Button(self,
                  text=STR_TABLE['save'][self.lang],
                  # font=("TkFixedFont", 15),
                  # bg="green",
                  height=1,
                  width=7,
                  command=self._save_btn_cmd).place(x=110, y=self.win_height - 50)

        tk.Button(self,
                  text=STR_TABLE['cancel'][self.lang],
                  # font=("TkFixedFont", 15),
                  # bg="green",
                  height=1,
                  width=8,
                  command=self._destroy_win).place(x=self.win_width - 120, y=self.win_height - 50)

        ####################################
        # New Station, Del Station Buttons
        tk.Button(self,
                  text=STR_TABLE['new_beacon'][self.lang],
                  # font=("TkFixedFont", 15),
                  # bg="green",
                  height=1,
                  width=10,
                  command=self._new_beacon_btn_cmd).place(x=20, y=self.win_height - 590)
        tk.Button(self,
                  text=STR_TABLE['delete'][self.lang],
                  # font=("TkFixedFont", 15),
                  bg="red3",
                  height=1,
                  width=10,
                  command=self._del_beacon_btn_cmd).place(x=self.win_width - 141, y=self.win_height - 590)

        ############################################
        self.tabControl = ttk.Notebook(self, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self.win_height - 550)
        self.tab_list: [ttk.Frame] = []
        # Tab Frames
        for port_id in PORT_HANDLER.beacons.keys():
            for stat_call in PORT_HANDLER.beacons[port_id]:
                for _beacon in PORT_HANDLER.beacons[port_id][stat_call]:
                    _beacon: Beacon
                    _label_txt = '{} {} {}'.format(len(self.tab_list), _beacon.from_call, port_id)
                    _tab = BeaconTab(self, self.tabControl, _beacon)
                    self.tabControl.add(_tab.own_tab, text=_label_txt)
                    self.tab_list.append(_tab)

    def _set_vars(self):
        for _tab in self.tab_list:
            _tab.beacon.set_from_call(_tab.from_select_var.get())
            _tab.beacon.set_to_call(_tab.call.get())
            if _tab.beacon.from_call != 'NOCALL' and \
                    _tab.beacon.to_call != 'NOCALL':
                _tab.beacon.set_via_calls(_tab.via.get())
                _tab.beacon.aprs = bool(_tab.aprs_check_var.get())
                _tab.beacon.pool = bool(_tab.pool_check_var.get())
                _tab.beacon.is_enabled = bool(_tab.active_check_var.get())
                _tab.beacon.port_id = int(_tab.port_select_var.get())
                _tab.beacon.repeat_time = float(_tab.interv.get())
                _tab.beacon.move_time = int(_tab.move.get())
                _tab.beacon.text = _tab.b_text_ent.get(0.0, tk.END)[:-1]
                _tab.beacon.typ = _tab.beacon_type_var.get()
                _port_id = _tab.beacon.port_id
                _stat_call = _tab.beacon.from_call
                _label_txt = '{} {}'.format(_port_id, _stat_call)
                self.tabControl.tab(self.tab_list.index(_tab), text=_label_txt)
                if _port_id in PORT_HANDLER.beacons.keys():
                    if _stat_call in PORT_HANDLER.beacons[_port_id].keys():
                        """ Should never get to this condition """
                        _tmp: [] = PORT_HANDLER.beacons[_port_id][_stat_call]
                        if _tab.beacon not in _tmp:
                            PORT_HANDLER.beacons[_port_id][_stat_call].append(_tab.beacon)
                    else:
                        PORT_HANDLER.beacons[_port_id][_stat_call] = [_tab.beacon]
                else:
                    PORT_HANDLER.beacons[_port_id] = {_stat_call: [_tab.beacon]}

    def _re_init_beacons(self):
        for _tab in self.tab_list:
            _tab.beacon.re_init()

    def _save_btn_cmd(self):
        self._set_vars()
        PORT_HANDLER.save_all_port_cfgs()
        self._main_cl.msg_to_monitor('Info: Baken Settings wurden gespeichert..')
        self._main_cl.msg_to_monitor('Lob: Gute Entscheidung! Bake bake Kuchen.')

    def _ok_btn_cmd(self):
        self._set_vars()
        self._re_init_beacons()
        self._main_cl.msg_to_monitor('Info: Baken Settings wurden gespeichert..')
        self._main_cl.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self._destroy_win()

    def _new_beacon_btn_cmd(self):
        # ax25_frame: AX25Frame, port_id: int, repeat_time: int, move_time: int, aprs_stuff: bool = False
        _beacon = Beacon()
        _label_txt = '{} {} {}'.format(len(self.tab_list), _beacon.from_call, _beacon.port_id)
        _tab = BeaconTab(self, self.tabControl, _beacon)
        self.tabControl.add(_tab.own_tab, text=_label_txt)
        self.tabControl.select(len(self.tab_list))
        self.tab_list.append(_tab)

    def _del_beacon_btn_cmd(self):
        try:
            ind = self.tabControl.index('current')
        except tk.TclError:
            pass
        else:
            tab: BeaconTab = self.tab_list[ind]
            beacon = tab.beacon
            for k in list(PORT_HANDLER.beacons.keys()):
                for kk in list(PORT_HANDLER.beacons[k].keys()):
                    if beacon in list(PORT_HANDLER.beacons[k][kk]):
                        PORT_HANDLER.beacons[k][kk].remove(beacon)
                        break
            del self.tab_list[ind]
            self.tabControl.forget(ind)

    def change_port(self, event):
        _ind = self.tabControl.index('current')
        _tab: BeaconTab = self.tab_list[_ind]
        _beacon = _tab.beacon
        for k in list(PORT_HANDLER.beacons.keys()):
            for kk in list(PORT_HANDLER.beacons[k].keys()):
                if _beacon in list(PORT_HANDLER.beacons[k][kk]):
                    PORT_HANDLER.beacons[k][kk].remove(_beacon)
                    break
        self._set_vars()

    def _destroy_win(self):
        self._main_cl.settings_win = None
        self.destroy()

    def tasker(self):
        pass
