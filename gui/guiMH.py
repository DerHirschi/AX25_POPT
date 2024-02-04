import logging
import tkinter as tk
from tkinter import ttk, Menu, messagebox

from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25Statistics import MyHeard
from cfg.constant import CFG_TR_DX_ALARM_BG_CLR
from cfg.string_tab import STR_TABLE
from fnc.str_fnc import conv_time_DE_str

logger = logging.getLogger(__name__)


class MHWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        self._lang = root_win.language
        self.title("MyHEARD")
        self.style = self._root_win.style
        self.geometry(f"1250x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close_me)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        ###################################
        # Vars
        self._mh = PORT_HANDLER.get_MH()
        self._rev_ent = False
        # self._alarm_active_var = self._root_win.setting_dx_alarm
        self._alarm_newCall_var = tk.BooleanVar(self)
        self._alarm_seenSince_var = tk.StringVar(self)
        self._alarm_distance_var = tk.StringVar(self)
        # self._tracer_active_var = tk.BooleanVar(self)
        self._tracer_duration_var = tk.StringVar(self)
        self._alarm_ports = []
        _ports = list(PORT_HANDLER.get_all_ports().keys())
        for _por_id in _ports:
            self._alarm_ports.append(tk.BooleanVar(self))
        self._get_vars()
        # ############################### Columns ############################
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=50)
        self.grid_rowconfigure(1, weight=0, minsize=25)
        self.grid_rowconfigure(2, weight=0, minsize=25)
        self.grid_rowconfigure(3, weight=1)
        # ###################### DX Alarm Settings ######################
        # ALARM
        lower_frame = tk.Frame(self)
        lower_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
        frame_11_label = tk.Frame(lower_frame)
        frame_11_label.pack(side=tk.TOP)
        tk.Label(frame_11_label, text='DX-Alarm Setting').pack()
        ###
        # activ Checkbox
        frame_21_active = tk.Frame(lower_frame)
        frame_21_active.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)

        tk.Label(frame_21_active, text='Activate ').pack(side=tk.LEFT, )
        tk.Checkbutton(frame_21_active,
                       variable=self._root_win.setting_dx_alarm,
                       # command=self._chk_alarm_active
                       ).pack(side=tk.LEFT, )

        # New Call in List Checkbox
        frame_21_newCall = tk.Frame(lower_frame)
        frame_21_newCall.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)

        tk.Label(frame_21_newCall, text='new Call ').pack(side=tk.LEFT, )
        tk.Checkbutton(frame_21_newCall,
                       variable=self._alarm_newCall_var,
                       command=self._set_alarm_newCall
                       ).pack(side=tk.LEFT, )

        # Alarm seen since Days
        frame_21_seen = tk.Frame(lower_frame)
        frame_21_seen.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)

        tk.Label(frame_21_seen, text='seen since (Days) (0 = off)').pack(side=tk.LEFT, )
        tk.Spinbox(frame_21_seen,
                   from_=0,
                   to=365,
                   increment=1,
                   width=4,
                   textvariable=self._alarm_seenSince_var,
                   command=self._set_alarm_last_seen
                   ).pack(side=tk.LEFT, )

        # Alarm Distance
        frame_21_distance = tk.Frame(lower_frame)
        frame_21_distance.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)

        tk.Label(frame_21_distance, text='Distance (0 = off)').pack(side=tk.LEFT, )
        tk.Spinbox(frame_21_distance,
                   from_=0,
                   to=20000,
                   increment=1,
                   width=6,
                   textvariable=self._alarm_distance_var,
                   command=self._set_alarm_distance
                   ).pack(side=tk.LEFT, )

        # ###################### Ports ############################
        lower_frame_ports = tk.Frame(self)
        lower_frame_ports.grid(row=1, column=0, columnspan=2, sticky='nsew')
        frame_13_label = tk.Frame(lower_frame_ports)
        frame_13_label.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        tk.Label(frame_13_label, text='Ports: ').pack(side=tk.LEFT, )
        _i = 0
        for _port_id in _ports:
            _frame = tk.Frame(lower_frame_ports)
            _frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=7)
            _text = f'{_port_id}'
            tk.Label(_frame, text=_text, width=3).pack(side=tk.LEFT, padx=1)
            tk.Checkbutton(_frame,
                           variable=self._alarm_ports[_i],
                           command=self._set_alarm_ports,
                           ).pack(side=tk.LEFT, padx=1)
            _i += 1
        # ###################### Auto Tracer ######################
        # Tracer
        auto_tracer_state = {
            True: 'disabled',
            False: 'normal'
        }.get(self._root_win.get_tracer(), 'disabled')
        lower_frame_tracer = tk.Frame(self)
        lower_frame_tracer.grid(row=2, column=0, columnspan=2, sticky='nsew')
        frame_12_label = tk.Frame(lower_frame_tracer)
        frame_12_label.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        tk.Label(frame_12_label, text='Auto APRS-Tracer: ').pack(side=tk.LEFT, )
        ###
        # activ Checkbox
        frame_22_active = tk.Frame(lower_frame_tracer)
        frame_22_active.pack(side=tk.LEFT, fill=tk.BOTH, )

        tk.Label(frame_22_active, text='Activate ').pack(side=tk.LEFT, )
        tk.Checkbutton(frame_22_active,
                       variable=self._root_win.setting_auto_tracer,
                       command=self._root_win.set_auto_tracer,
                       state=auto_tracer_state
                       ).pack(side=tk.LEFT, )
        # duration
        frame_22_duration = tk.Frame(lower_frame_tracer)
        frame_22_duration.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)

        tk.Label(frame_22_duration, text='Duration (min) ').pack(side=tk.LEFT, )
        tk.Spinbox(frame_22_duration,
                   from_=5,
                   to=1440,
                   increment=5,
                   width=5,
                   textvariable=self._tracer_duration_var,
                   state=auto_tracer_state,
                   command=self._set_auto_tracer,
                   ).pack(side=tk.LEFT, )

        ##########################################################################################
        # TREE
        columns = (
            'mh_last_seen',
            'mh_first_seen',
            'mh_port',
            'mh_call',
            'mh_loc',
            'mh_dist',
            'mh_nPackets',
            'mh_REJ',
            'mh_route',
            'mh_last_ip',
            'mh_ip_fail'
        )
        self._tree = ttk.Treeview(self, columns=columns, show='headings')
        self._tree.grid(row=3, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=3, column=1, sticky='ns')

        self._tree.heading('mh_last_seen', text='Letzte Paket', command=lambda: self._sort_entry('last'))
        self._tree.heading('mh_first_seen', text='Erste Paket', command=lambda: self._sort_entry('first'))
        self._tree.heading('mh_port', text='Port', command=lambda: self._sort_entry('port'))
        self._tree.heading('mh_call', text='Call', command=lambda: self._sort_entry('call'))
        self._tree.heading('mh_loc', text='LOC', command=lambda: self._sort_entry('loc'))
        self._tree.heading('mh_dist', text='km', command=lambda: self._sort_entry('dist'))
        self._tree.heading('mh_nPackets', text='Packets', command=lambda: self._sort_entry('pack'))
        self._tree.heading('mh_REJ', text='REJs', command=lambda: self._sort_entry('rej'))
        self._tree.heading('mh_route', text='Route', command=lambda: self._sort_entry('route'))
        self._tree.heading('mh_last_ip', text='AXIP', command=lambda: self._sort_entry('axip'))
        self._tree.heading('mh_ip_fail', text='Fail', command=lambda: self._sort_entry('axipfail'))
        self._tree.column("mh_last_seen", anchor=tk.W, stretch=tk.YES, width=180)
        self._tree.column("mh_first_seen", anchor=tk.W, stretch=tk.YES, width=180)
        self._tree.column("mh_call", anchor=tk.W, stretch=tk.YES, width=120)
        self._tree.column("mh_loc", anchor=tk.W, stretch=tk.YES, width=100)
        self._tree.column("mh_dist", anchor=tk.W, stretch=tk.YES, width=70)
        self._tree.column("mh_port", anchor=tk.W, stretch=tk.NO, width=80)
        self._tree.column("mh_nPackets", anchor=tk.W, stretch=tk.NO, width=80)
        self._tree.column("mh_REJ", anchor=tk.W, stretch=tk.NO, width=55)
        self._tree.column("mh_ip_fail", anchor=tk.W, stretch=tk.NO, width=50)
        self._tree.tag_configure("dx_alarm", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)

        self._root_win.mh_window = self
        self._tree_data = []
        self._update_mh()
        self._init_menubar()
        self._tree.bind('<<TreeviewSelect>>', self.entry_selected)

    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=STR_TABLE['del_all'][self._lang], command=self._reset_mh_list)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=STR_TABLE['delete_dx_history'][self._lang], command=self._reset_dx_history)
        menubar.add_cascade(label='MyHeard', menu=MenuVerb, underline=0)

    def _get_vars(self):
        # self._alarm_active_var.set(bool())
        self._alarm_newCall_var.set(bool(self._mh.parm_new_call_alarm))
        self._alarm_seenSince_var.set(str(self._mh.parm_lastseen_alarm))
        self._alarm_distance_var.set(str(self._mh.parm_distance_alarm))
        # self._tracer_active_var.set(bool(self._root_win.setting_auto_tracer.get()))
        self._tracer_duration_var.set(str(self._root_win.get_auto_tracer_duration()))
        _i = 0
        for _var in self._alarm_ports:
            if _i in self._mh.parm_alarm_ports:
                _var.set(True)
            else:
                _var.set(False)
            _i += 1

    def _set_alarm_ports(self, event=None):
        _i = 0
        for _var in self._alarm_ports:
            if _var.get():
                if _i not in self._mh.parm_alarm_ports:
                    self._mh.parm_alarm_ports.append(int(_i))
            else:
                if _i in self._mh.parm_alarm_ports:
                    self._mh.parm_alarm_ports.remove(int(_i))
            _i += 1

    def _set_alarm_distance(self, event=None):
        _var = self._alarm_distance_var.get()
        try:
            _var = int(_var)
        except ValueError:
            return
        self._mh.parm_distance_alarm = _var

    def _set_alarm_last_seen(self, event=None):
        _var = self._alarm_seenSince_var.get()
        try:
            _var = int(_var)
        except ValueError:
            return
        self._mh.parm_lastseen_alarm = _var

    def _set_alarm_newCall(self, event=None):
        self._mh.parm_new_call_alarm = bool(self._alarm_newCall_var.get())

    def _set_auto_tracer(self, event=None):
        _dur = self._tracer_duration_var.get()
        try:
            _dur = int(_dur)
        except ValueError:
            return
        self._root_win.set_auto_tracer_duration(_dur)

    def entry_selected(self, event):
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[3]
            vias = record[8]
            port = record[2]
            if type(port) is str:
                port = int(port.split(' ')[0])
            # print(port)
            if vias:
                call = f'{call} {vias}'
            if not self._root_win.new_conn_win:
                self._root_win.open_new_conn_win()
            if self._root_win.new_conn_win:
                self._root_win.new_conn_win.preset_ent(call, port)
            self._close_me()

    def _update_mh(self):
        self._init_tree_data()
        self._update_tree()

    def _init_tree_data(self):
        self._sort_entry('last')

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)

        for ret_ent in self._tree_data:
            if ret_ent[1]:
                self._tree.insert('', tk.END, values=ret_ent[0], tags=('dx_alarm',))
            else:
                self._tree.insert('', tk.END, values=ret_ent[0], )

    def _sort_entry(self, flag: str):
        sort_date = self._mh.get_sort_mh_entry(flag_str=flag, reverse=self._rev_ent)
        if self._rev_ent:
            self._rev_ent = False
        else:
            self._rev_ent = True
        self._format_tree_ent(sort_date)
        self._update_tree()

    def _format_tree_ent(self, mh_list):
        self._tree_data = []
        for k in mh_list:
            ent: MyHeard
            ent = mh_list[k]
            if ent.axip_add[1]:
                axip_str = '{} - {}'.format(ent.axip_add[0], ent.axip_add[1])
            else:
                axip_str = ''
            dx_alarm = False
            if ent.own_call in list(self._mh.dx_alarm_hist):
                dx_alarm = True

            self._tree_data.append(((
                f'{conv_time_DE_str(ent.last_seen)}',
                f'{conv_time_DE_str(ent.first_seen)}',
                f'{ent.port_id} {ent.port}',
                f'{ent.own_call}',
                f'{ent.locator}',
                f'{ent.distance}',
                f'{ent.pac_n}',
                f'{ent.rej_n}',
                ' '.join(ent.route),
                f'{axip_str}',
                f'{ent.axip_fail}',
            ), dx_alarm))

    def _reset_mh_list(self):
        self.lower()
        if messagebox.askokcancel(title=STR_TABLE.get('msg_box_mh_delete', ('', '', ''))[self._lang],
                                  message=STR_TABLE.get('msg_box_mh_delete_msg', ('', '', ''))[self._lang]):
            mh = PORT_HANDLER.get_MH()
            mh.reset_mainMH()
            self._update_mh()
        self.lift()

    def _reset_dx_history(self):
        self.lower()
        if messagebox.askokcancel(title=STR_TABLE.get('msg_box_mh_delete', ('', '', ''))[self._lang],
                                  message=STR_TABLE.get('msg_box_mh_delete_msg', ('', '', ''))[self._lang]):
            mh = PORT_HANDLER.get_MH()
            mh.reset_dxHistory()
        self.lift()

    def __del__(self):
        self._root_win.mh_window = None
        # self.destroy()

    def _close_me(self):
        self._mh.reset_dx_alarm_his()
        self._root_win.mh_window = None
        self.destroy()
