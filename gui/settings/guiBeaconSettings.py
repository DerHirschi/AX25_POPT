import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk as ttk
from tkinter import scrolledtext
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import GUI_DISABLED_CLR
from cfg.default_config import getNew_BEACON_cfg
from cfg.popt_config import POPT_CFG
from fnc.file_fnc import get_bin_fm_file
from fnc.str_fnc import tk_filter_bad_chars, zeilenumbruch
from cfg.string_tab import STR_TABLE
from schedule.guiPoPT_Scheduler import PoPT_Set_Scheduler
from schedule.popt_sched import getNew_schedule_config


class BeaconTab:
    def __init__(self, root, tabclt: ttk.Notebook, beacon: dict):
        self._need_reinit = False
        self._tab_clt = tabclt
        self._root = root
        self._lang = POPT_CFG.get_guiCFG_language()
        self.own_tab = ttk.Frame(self._tab_clt)
        self.beacon: dict = beacon
        self.schedule_config = self.beacon.get('scheduler_cfg', getNew_schedule_config())

        #################
        # Von
        call_x = 10
        call_y = 20
        call_label = tk.Label(self.own_tab, text=f"{STR_TABLE['from'][self._lang]}:")
        call_label.place(x=call_x, y=call_y)
        self.from_select_var = tk.StringVar(self.own_tab)
        # from_opt = dict(PORT_HANDLER.ax25_stations_settings)
        self.from_select_var.set(beacon.get('own_call', 'NOCALL'))  # default value
        opt = list(POPT_CFG.get_stat_CFG_keys())
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
        self.intervall_var = tk.StringVar(self.own_tab)
        self.intervall_var.set(str(int(self.schedule_config.get('repeat_min', 30))))
        self._interv = tk.Entry(self.own_tab, width=4, textvariable=self.intervall_var)
        self._interv.place(x=call_x + 135, y=call_y)
        self._interv.bind('<KeyRelease>', self._set_need_reinit)
        #################
        # Versatz
        call_x = 420
        call_y = 55
        move_label = tk.Label(self.own_tab, text=f"{STR_TABLE['versatz'][self._lang]} (sek):")
        move_label.place(x=call_x, y=call_y)
        self.move_var = tk.StringVar(self.own_tab)
        self.move_var.set(str(self.schedule_config.get('move', 0)))
        move = tk.Entry(self.own_tab, width=5, textvariable=self.move_var)
        move.place(x=call_x + 135, y=call_y)
        move.bind('<KeyRelease>', self._set_need_reinit)

        #################
        #################
        # Active Checkbox
        call_x = 750
        call_y = 90
        self.active_check_var = tk.IntVar(self.own_tab)
        active_check = tk.Checkbutton(self.own_tab,
                                      text=STR_TABLE['active'][self._lang],
                                      variable=self.active_check_var,
                                      command=self._cmd_be_enabled)
        active_check.var = self.active_check_var
        active_check.place(x=call_x + 55, y=call_y)
        if beacon.get('is_enabled', False):
            self.active_check_var.set(1)
            active_check.select()

        ########################
        # Typ TEXT/MH/File bla .. .
        call_x = 750
        call_y = 125
        tk.Label(self.own_tab, text='Typ: ').place(x=call_x + 68, y=call_y)
        _options = ["Text", "File", "MH"]
        self.beacon_type_var = tk.StringVar(self.own_tab)
        self.beacon_type_var.set(beacon.get('typ', 'Text'))
        tk.OptionMenu(self.own_tab,
                      self.beacon_type_var,
                      command=self._cmd_be_change_typ,
                      *_options
                      ).place(x=call_x + 125, y=call_y)

        ####################################################
        # Scheduler BTN
        call_x = 600
        call_y = 55
        tk.Button(self.own_tab,
                  text="Scheduler",
                  command=self._open_schedWin
                  ).place(x=call_x + 55, y=call_y)

        ###################################################################
        #################
        # Beacon Text
        call_x = 10
        call_y = 175
        # call_y = 100
        self.b_text_ent = tk.scrolledtext.ScrolledText(self.own_tab, font=("Courier", 12))
        # self.b_text_ent.configure(width=83, height=15)
        self.b_text_ent.configure(width=82, height=8)
        self.b_text_ent.place(x=call_x, y=call_y)
        self.b_text_ent.insert(tk.END, beacon.get('text', ''))
        self.b_text_ent.bind('<KeyRelease>', self._update_byte_c_var_bind)

        #################
        # Aus Datei
        call_x = 10
        call_y = self._root.win_height - 180
        # call_y = 100
        call_label = tk.Label(self.own_tab, text=f"{STR_TABLE['text_fm_file'][self._lang]}:")
        call_label.place(x=call_x, y=call_y)
        self.be_txt_filename_var = tk.StringVar(self.own_tab)
        self._be_txt_filename = tk.Entry(self.own_tab, textvariable=self.be_txt_filename_var, width=50)
        self._be_txt_filename.bind("<KeyRelease>", self._on_key_press_filename_ent)
        self._b_text_bg_color = self.b_text_ent.cget('background')
        self.be_txt_filename_var.set(beacon.get('text_filename', ''))
        self._be_txt_filename.place(x=call_x + 140, y=call_y)
        be_txt_openfile_btn = tk.Button(self.own_tab, text=STR_TABLE['file_1'][self._lang], command=self._select_files)
        be_txt_openfile_btn.place(x=call_x + 710, y=call_y - 2)
        #################
        # Byte Zähler
        call_x = 885
        call_y = self._root.win_height - 185
        self._byte_count_var = tk.StringVar(self.own_tab, '')
        tk.Label(self.own_tab,
                 textvariable=self._byte_count_var,
                 font=(None, 9),
                 ).place(x=call_x, y=call_y)
        self._update_byte_c_var_fm_text()
        self._cmd_be_change_typ()

    def _update_byte_c_var_fm_text(self):
        new_text = f"{len(self.beacon.get('text', ''))}/256 Bytes"
        self._byte_count_var.set(new_text)

    def _update_byte_c_var_bind(self, event=None):
        ind2 = str(int(float(self.b_text_ent.index(tk.INSERT)))) + '.0'
        text = zeilenumbruch(self.b_text_ent.get(ind2, self.b_text_ent.index(tk.INSERT)))
        self.b_text_ent.delete(ind2, self.b_text_ent.index(tk.INSERT))
        self.b_text_ent.insert(tk.INSERT, text)
        text = self.b_text_ent.get(0.0, tk.END)[:-1]
        t_len = len(text)
        if t_len > 256:
            ind = t_len - 256
            self.b_text_ent.delete(f'insert-{ind}c', tk.INSERT)
            text = self.b_text_ent.get(0.0, tk.END)[:-1]

        t_len = len(text)
        new_text = f"{t_len}/256 Bytes"
        self._byte_count_var.set(new_text)
        self._need_reinit = True

    def _cmd_be_enabled(self):
        self._need_reinit = True
        self.beacon['is_enabled'] = bool(self.active_check_var.get())

    def _cmd_fm_call_set(self, event):
        self.beacon['own_call'] = str(self.from_select_var.get())
        _label_txt = '{} {}'.format(self.port_select_var.get(), self.from_select_var.get())
        self._root.tabControl.tab(self._root.tab_list.index(self), text=_label_txt)
        # self._root.change_port(None)
        self._need_reinit = True

    def _on_key_press_filename_ent(self, event):
        # print(event)
        filename = self.be_txt_filename_var.get()
        if filename:
            self.beacon['text_filename'] = filename
            bin_text = get_bin_fm_file(filename)
            if bin_text:
                self.beacon['text'] = bin_text.decode('utf-8', 'ignore')[:256]
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
        self._need_reinit = True
        self._update_byte_c_var_fm_text()

    def _select_files(self):
        # self._root.attributes("-topmost", False)
        # self.root.lower
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='data/',
            filetypes=filetypes)
        # self._root.lift()
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
        self._update_byte_c_var_fm_text()

    def _disable_intervall(self):
        hours = self.schedule_config.get('hours', {})
        minutes = self.schedule_config.get('minutes', {})

        for k in hours:
            if hours[k]:
                self._interv.configure(state='disabled')
                return
        for k in minutes:
            if minutes[k]:
                self._interv.configure(state='disabled')
                return
        self._interv.configure(state='normal')

    def _cmd_be_change_typ(self, event=None):
        if self.beacon_type_var.get() == "Text":
            self.b_text_ent.configure(state='normal', background=self._b_text_bg_color)
            self._be_txt_filename.configure(state='disabled', background=GUI_DISABLED_CLR)
        elif self.beacon_type_var.get() == "File":
            self.b_text_ent.configure(state='disabled', background=GUI_DISABLED_CLR)
            self._be_txt_filename.configure(state='normal', background=self._b_text_bg_color)
        # elif self.beacon_type_var.get() == "MH":
        else:
            self.b_text_ent.configure(state='disabled', background=GUI_DISABLED_CLR)
            self._be_txt_filename.configure(state='disabled', background=GUI_DISABLED_CLR)

    def _open_schedWin(self):
        try:
            self.schedule_config['repeat_min'] = int(float(self.intervall_var.get()))
        except ValueError:
            pass
        try:
            self.schedule_config['move'] = int(float(self.move_var.get()))
        except ValueError:
            pass
        if not self._root.schedule_win:
            PoPT_Set_Scheduler(self)

    def scheduler_config_save_task(self):
        """ Task fm PoPT-Scheduler_win"""
        self.move_var.set(str(int(self.schedule_config.get('move', 0))))
        self.intervall_var.set(str(int(self.schedule_config.get('repeat_min', 30))))
        self._disable_intervall()
        self._need_reinit = True

    def _set_need_reinit(self, event=None):
        self._need_reinit = True

    def need_reinit(self):
        return self._need_reinit


class BeaconSettings(tk.Frame):
    def __init__(self, tabctl, main_win=None):
        tk.Frame.__init__(self, tabctl)
        self._need_reinit = False
        # self._main_cl = main_win
        self._lang = POPT_CFG.get_guiCFG_language()
        self.win_height = 540
        self.win_width = 1060

        self.schedule_win = None
        # self.attributes("-topmost", True)
        ###############
        # VARS
        # self.port_handler = main_win.ax25_port_handler
        # self.all_beacons: {int: {str: [Beacon]}} = self.port_handler.beacons
        ##########################
        ####################################
        # New Station, Del Station Buttons
        tk.Button(self,
                  text=STR_TABLE['new_beacon'][self._lang],
                  # font=("TkFixedFont", 15),
                  # bg="green",
                  height=1,
                  width=10,
                  command=self._new_beacon_btn_cmd).place(x=20, y=self.win_height - 530)
        tk.Button(self,
                  text=STR_TABLE['delete'][self._lang],
                  # font=("TkFixedFont", 15),
                  bg="red3",
                  height=1,
                  width=10,
                  command=self._del_beacon_btn_cmd).place(x=self.win_width - 141, y=self.win_height - 530)

        ############################################
        self.tabControl = ttk.Notebook(self, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=50)
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
            if tab.need_reinit():
                self._need_reinit = True
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
                try:
                    tab.beacon['scheduler_cfg']['repeat_min'] = float(tab.intervall_var.get())
                except ValueError:
                    pass
                try:
                    tab.beacon['scheduler_cfg']['move'] = int(tab.move_var.get())
                except ValueError:
                    pass
                tab.beacon['text'] = tab.b_text_ent.get(0.0, tk.END)[:-1]
                tab.beacon['text_filename'] = str(tab.be_txt_filename_var.get())
                tab.beacon['typ'] = tab.beacon_type_var.get()
                port_id = tab.beacon['port_id']
                stat_call = tab.beacon['own_call']
                label_txt = f'{stat_call} {port_id}'
                self.tabControl.tab(self.tab_list.index(tab), text=label_txt)
                beacon_tasks.append(dict(tab.beacon))
        POPT_CFG.set_Beacon_tasks(beacon_tasks)

    @staticmethod
    def _re_init_beacons():
        PORT_HANDLER.reinit_beacon_task()

    """
    def _save_btn_cmd(self):
        self._set_vars()
        POPT_CFG.save_MAIN_CFG_to_file()
        # self._main_cl.sysMsg_to_monitor('Info: Baken Settings wurden gespeichert..')

    def _ok_btn_cmd(self):
        self._set_vars()
        self._re_init_beacons()
        # self._main_cl.sysMsg_to_monitor('Info: Baken Settings wurden gespeichert..')
        # self._main_cl.sysMsg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self._destroy_win()
    """

    def _new_beacon_btn_cmd(self):
        # ax25_frame: AX25Frame, port_id: int, repeat_time: int, move_time: int, aprs_stuff: bool = False
        beacon = getNew_BEACON_cfg()
        own_call = beacon.get('own_call', 'NOCALL')
        port_id = beacon.get('port_id', 0)
        label_txt = '{} {} {}'.format(len(self.tab_list), own_call, port_id)
        tab = BeaconTab(self, self.tabControl, beacon)
        self.tabControl.add(tab.own_tab, text=label_txt)
        self.tabControl.select(len(self.tab_list))
        self.tab_list.append(tab)

    def _del_beacon_btn_cmd(self):
        try:
            ind = self.tabControl.index('current')
        except tk.TclError:
            pass
        else:
            del self.tab_list[ind]
            self.tabControl.forget(ind)

    def save_config(self):
        self._set_vars()
        POPT_CFG.save_MAIN_CFG_to_file()
        if self._need_reinit:
            self._re_init_beacons()
            self._need_reinit = False
            return True
        # self._main_cl.sysMsg_to_monitor('Info: Baken Settings wurden gespeichert..')
        return False
