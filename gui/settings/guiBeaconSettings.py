import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk as ttk
from tkinter import scrolledtext
# from ax25.ax25Beacon import Beacon
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import GUI_DISABLED_CLR
from cfg.default_config import getNew_BEACON_cfg
from cfg.popt_config import POPT_CFG
from fnc.file_fnc import get_bin_fm_file
from fnc.str_fnc import tk_filter_bad_chars
from cfg.string_tab import STR_TABLE
from schedule.popt_sched import getNew_schedule_config


class BeaconTab:
    def __init__(self, root, tabclt: ttk.Notebook, beacon: dict):
        self._tab_clt = tabclt
        self._root = root
        self._lang = self._root.lang
        self.style = root.style
        self.own_tab = ttk.Frame(self._tab_clt)
        self.beacon: dict = beacon
        sched = beacon.get('scheduler_cfg', dict(getNew_schedule_config()))
        self.sched = sched
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
        self.from_select_var.set(beacon.get('own_call', 'NOCALL'))  # default value
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
        self.call.insert(tk.END, beacon.get('dest_call', 'BEACON'))
        #################
        # VIA
        call_x = 370
        call_y = 20
        call_label = tk.Label(self.own_tab, text='VIA:')
        call_label.place(x=call_x, y=call_y)
        self.via = tk.Entry(self.own_tab, width=35)
        self.via.place(x=call_x + 40, y=call_y)
        vias = ' '.join(beacon.get('via_calls', []))
        self.via.insert(tk.END, vias)
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
        if beacon.get('cmd_poll', (False, False))[0]:
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
        if beacon.get('cmd_poll', (False, False))[1]:
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
        self.port_select_var.set(str(beacon.get('port_id', 0)))  # default value
        opt = list(PORT_HANDLER.get_all_ports().keys())
        if not opt:
            opt = ['0']

        port = tk.OptionMenu(self.own_tab,
                             self.port_select_var,
                             *opt,
                             )
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
        self.interv.insert(tk.END, str(sched.get('repeat_min')))
        #################
        # Versatz
        call_x = 420
        call_y = 55
        move_label = tk.Label(self.own_tab, text=f"{STR_TABLE['versatz'][self._lang]} (sek):")
        move_label.place(x=call_x, y=call_y)
        self.move = tk.Entry(self.own_tab, width=5)
        self.move.place(x=call_x + 135, y=call_y)
        self.move.insert(tk.END, str(sched.get('move')))
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
        if beacon.get('is_enabled', False):
            self.active_check_var.set(1)
            self.active_check.select()

        ########################
        # Typ TEXT/MH/File bla .. .
        call_x = 750
        call_y = 125
        tk.Label(self.own_tab, text='Typ: ').place(x=call_x + 68, y=call_y)
        _options = ["Text", "File", "MH"]
        self.beacon_type_var = tk.StringVar(self.own_tab)
        self.beacon_type_var.set(beacon.get('typ', 'Text'))
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
        self._minutes_sel = {}
        tr = False
        for minute in range(12):
            text = minute * 5
            minutes_sel_var = tk.BooleanVar(self.own_tab)
            minutes_sel = tk.Checkbutton(self.own_tab,
                                         text=str(text),
                                         variable=minutes_sel_var,
                                         command=lambda: self._check_minutes_cmd(minute))
            # minutes_sel.configure(state='disabled')  # TODO
            minutes_sel.var = minutes_sel_var
            minutes_sel.place(x=call_x + 75 + (55 * minute), y=call_y)
            self._minutes_sel[minute] = minutes_sel_var
            if minute in sched.get('minutes', {}).keys():
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
        self._std_sel = {}
        for std in range(24):
            text = std
            std_var = tk.BooleanVar(self.own_tab)
            std_sel = tk.Checkbutton(self.own_tab,
                                     text=str(text),
                                     variable=std_var,
                                     command=lambda: self._check_hour_cmd(std))
            # command=self.cmd_be_enabled)
            std_sel.var = std_var
            if std in sched.get('hours', {}).keys():
                std_var.set(True)
                std_sel.select()
                # tr = True
            if std > 11:
                std = std - 12
                std_sel.place(x=call_x + 75 + (55 * std), y=call_y + 21)
            else:
                std_sel.place(x=call_x + 75 + (55 * std), y=call_y)
            self._std_sel[std] = std_var

        #################
        # Tag Selector
        call_x = 10
        call_y = 173
        tag_sel_lable = tk.Label(self.own_tab, text=f"{STR_TABLE['day'][self._lang]}:")
        tag_sel_lable.place(x=call_x, y=call_y)
        self.tag_sel = {}
        ind = 1
        for tag in ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']:
            sel_var = tk.BooleanVar(self.own_tab)
            sel = tk.Checkbutton(self.own_tab,
                                 text=tag,
                                 variable=sel_var,
                                 command=lambda: self._check_day_cmd(tag))

            # command=self.cmd_be_enabled)
            sel.var = sel_var
            sel.place(x=call_x + 75 + (65 * ind), y=call_y)
            self.tag_sel[tag] = sel_var
            if sched.get('week_days', {}).get(tag, False):
                sel_var.set(True)
                sel.select()
            ind += 1
        #################
        # Monat Selector
        call_x = 10
        call_y = 205
        tag_sel_lable = tk.Label(self.own_tab, text=f"{STR_TABLE['month'][self._lang]}:")
        tag_sel_lable.place(x=call_x, y=call_y)
        self._monat_sel = {}
        for monat in list(range(1, 13)):
            sel_var = tk.BooleanVar(self.own_tab)
            sel = tk.Checkbutton(self.own_tab,
                                 text=str(monat),
                                 variable=sel_var,
                                 command=lambda: self._check_month_cmd(monat))
            # command=self.cmd_be_enabled)
            sel.var = sel_var
            sel.place(x=call_x + 75 + (55 * (monat - 1)), y=call_y)
            self._monat_sel[monat] = sel_var
            if sched.get('month', {}).get(monat, False):
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
        self.b_text_ent.insert(tk.END, beacon.get('text', ''))

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
        self.be_txt_filename_var.set(beacon.get('text_filename', ''))
        self.be_txt_filename.place(x=call_x + 140, y=call_y)
        be_txt_openfile_btn = tk.Button(self.own_tab, text='Datei', command=self._select_files)
        be_txt_openfile_btn.place(x=call_x + 710, y=call_y - 2)

        self._cmd_be_change_typ()

    def _cmd_be_enabled(self):
        self.beacon['is_enabled'] = bool(self.active_check_var.get())

    def _cmd_fm_call_set(self, event):
        self.beacon['own_call'] = str(self.from_select_var.get())
        _label_txt = '{} {}'.format(self.port_select_var.get(), self.from_select_var.get())
        self._root.tabControl.tab(self._root.tab_list.index(self), text=_label_txt)
        # self._root.change_port(None)

    def _on_key_press_filename_ent(self, event):
        # print(event)
        filename = self.be_txt_filename_var.get()
        if filename:
            self.beacon['text_filename'] = filename
            bin_text = get_bin_fm_file(filename)
            if bin_text:
                self.beacon['text'] = bin_text.decode('utf-8', 'ignore')
                self.b_text_ent.configure(state='normal', background=GUI_DISABLED_CLR)
                self.b_text_ent.delete('1.0', tk.END)
                self.b_text_ent.insert(tk.END, tk_filter_bad_chars(self.beacon['text']))
                self.b_text_ent.configure(state='disabled')
            else:
                self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)
                # self.be_txt_filename_var.set('')
                self.beacon['text_filename'] = ''
        else:
            # self.be_txt_filename_var.set('')
            self.beacon['text_filename'] = ''
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
            self.beacon['text_filename'] = filenames[0]
            bin_text = get_bin_fm_file(filenames[0])
            if bin_text:
                self.beacon['text'] = str(bin_text.decode('utf-8', 'ignore'))[:256]
                self.b_text_ent.configure(state='normal', background=GUI_DISABLED_CLR)
                self.b_text_ent.delete('1.0', tk.END)
                self.b_text_ent.insert(tk.END, tk_filter_bad_chars(self.beacon['text']))
                self.b_text_ent.configure(state='disabled')
            else:
                self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)
                self.be_txt_filename_var.set('')
                self.beacon['text_filename'] = ''
        else:
            self.be_txt_filename_var.set('')
            self.beacon['text_filename'] = ''
            self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)

    def _check_day_cmd(self, tag):
        week_days = self.sched.get('week_days', {})
        var = self.tag_sel.get(tag, None)
        if not var:
            return
        var = var.get()
        week_days[tag] = bool(var)
        self.sched['week_days'] = week_days

    def _check_month_cmd(self, monat: int):
        month = self.sched.get('month', {})
        var = self._monat_sel.get(monat, None)
        if not var:
            return
        var = var.get()
        month[monat] = bool(var)
        self.sched['month'] = month

    def _check_minutes_cmd(self, minute: int):
        minutes = self.sched.get('minutes', {})
        var = self._monat_sel.get(minute, None)
        if not var:
            return
        var = var.get()
        minutes[minute] = bool(var)
        self.sched['minutes'] = minutes
        self._disable_intervall()

    def _check_hour_cmd(self, hour: int):
        hours = self.sched.get('hours', {})
        var = self._monat_sel.get(hour, None)
        if not var:
            return
        var = var.get()
        hours[hour] = bool(var)
        self.sched['hours'] = hours
        self._disable_intervall()

    def _disable_intervall(self):
        hours = self.sched.get('hours', {})
        minutes = self.sched.get('minutes', {})

        for k in hours:
            if hours[k]:
                self.interv.configure(state='disabled')
                return
        for k in minutes:
            if minutes[k]:
                self.interv.configure(state='disabled')
                return
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
        for beacon in POPT_CFG.get_Beacon_tasks():
            port_id = beacon.get('port_id', 0)
            own_call = beacon.get('own_call', '')
            if own_call:
                label_txt = '{} {}'.format(own_call, port_id)
                tab = BeaconTab(self, self.tabControl, beacon)
                self.tabControl.add(tab.own_tab, text=label_txt)
                self.tab_list.append(tab)

    def _set_vars(self):
        beacon_tasks = []
        for tab in self.tab_list:
            tab.beacon['own_call'] = tab.from_select_var.get()
            tab.beacon['dest_call'] = tab.call.get()
            if tab.beacon['own_call'] != 'NOCALL':
                vias = tab.via.get().split(' ')
                # vias.remove(' ')
                tab.beacon['via_calls'] = vias
                cmd_rpt = bool(tab.aprs_check_var.get())
                poll = bool(tab.pool_check_var.get())
                tab.beacon['cmd_poll'] = (cmd_rpt, poll)
                # tab.beacon['is_enabled'] = bool(tab.active_check_var.get())
                tab.beacon['port_id'] = int(tab.port_select_var.get())
                tab.beacon['scheduler_cfg']['repeat_min'] = float(tab.interv.get())
                tab.beacon['scheduler_cfg']['move'] = int(tab.move.get())
                tab.beacon['text'] = tab.b_text_ent.get(0.0, tk.END)[:-1]
                tab.beacon['text_filename'] = str(tab.be_txt_filename_var.get())
                tab.beacon['typ'] = tab.beacon_type_var.get()
                _port_id = tab.beacon['port_id']
                _stat_call = tab.beacon['own_call']
                _label_txt = f'{_stat_call} {_port_id}'
                self.tabControl.tab(self.tab_list.index(tab), text=_label_txt)
                beacon_tasks.append(dict(tab.beacon))

        POPT_CFG.set_Beacon_tasks(beacon_tasks)

    @staticmethod
    def _re_init_beacons():
        PORT_HANDLER.reinit_beacon_task()

    def _save_btn_cmd(self):
        self._set_vars()
        POPT_CFG.save_CFG_to_file()
        self._main_cl.msg_to_monitor('Info: Baken Settings wurden gespeichert..')

    def _ok_btn_cmd(self):
        self._set_vars()
        self._re_init_beacons()
        self._main_cl.msg_to_monitor('Info: Baken Settings wurden gespeichert..')
        self._main_cl.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self._destroy_win()

    def _new_beacon_btn_cmd(self):
        # ax25_frame: AX25Frame, port_id: int, repeat_time: int, move_time: int, aprs_stuff: bool = False
        beacon = getNew_BEACON_cfg()
        own_call = beacon.get('own_call', 'NOCALL')
        port_id = beacon.get('port_id', 0)
        _label_txt = '{} {} {}'.format(len(self.tab_list), own_call, port_id)
        _tab = BeaconTab(self, self.tabControl, beacon)
        self.tabControl.add(_tab.own_tab, text=_label_txt)
        self.tabControl.select(len(self.tab_list))
        self.tab_list.append(_tab)

    def _del_beacon_btn_cmd(self):
        try:
            ind = self.tabControl.index('current')
        except tk.TclError:
            pass
        else:
            del self.tab_list[ind]
            self.tabControl.forget(ind)

    def _destroy_win(self):
        self._main_cl.settings_win = None
        self.destroy()

    def tasker(self):
        pass
