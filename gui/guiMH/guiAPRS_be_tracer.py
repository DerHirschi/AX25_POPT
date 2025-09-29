import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import CFG_TR_DX_ALARM_BG_CLR
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import get_list_fm_viaStr
from fnc.str_fnc import get_strTab


class BeaconTracer(ttk.Frame):
    def __init__(self, root_frame, root_win):
        ttk.Frame.__init__(self, root_frame)
        self.pack(fill='both', expand=True)
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ##############################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ##############################################
        upper_frame = ttk.Frame(main_f)  # Setting
        # upper_frame2 = tk.Frame(self)  # Setting
        middle_frame = ttk.Frame(main_f)  # Tree
        lower_frame = ttk.Frame(main_f)  # Selected Info
        upper_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10)
        # upper_frame2.pack(side=tk.TOP, fill=tk.BOTH, pady=10)
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10, expand=True)
        lower_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10)

        ##########################
        # Upper Frame ( Settings )
        frame_1_label = ttk.Frame(upper_frame)
        frame_1_label.pack(side=tk.TOP)
        ttk.Label(frame_1_label, text='Beacon Setting').pack()

        frame_2 = ttk.Frame(upper_frame)
        frame_2.pack(side=tk.TOP, fill=tk.BOTH)
        frame_2_port = ttk.Frame(upper_frame)
        frame_2_port.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

        # Port
        self._be_port_var = tk.StringVar(self)
        options = list(PORT_HANDLER.get_all_ports().keys())
        if len(options) > PORT_HANDLER.get_aprs_ais().be_tracer_port:
            self._be_port_var.set(options[PORT_HANDLER.get_aprs_ais().be_tracer_port])
        if not options:
            options = [0]
        ttk.Label(frame_2_port, text='Port ').pack(side=tk.LEFT, padx=5)
        options = [self._be_port_var.get()] + options
        ttk.OptionMenu(frame_2_port, self._be_port_var, *options, command=self._chk_port).pack(side=tk.LEFT, )

        # Station / Call
        frame_2_stat = ttk.Frame(upper_frame)
        frame_2_stat.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        self._be_stat_var = tk.StringVar(self)
        # options = list(PORT_HANDLER.ge)
        options = PORT_HANDLER.get_stat_calls_fm_port(PORT_HANDLER.get_aprs_ais().be_tracer_port)

        self._be_stat_var.set(PORT_HANDLER.get_aprs_ais().be_tracer_station)
        ttk.Label(frame_2_stat, text='Station ').pack(side=tk.LEFT, )
        self._be_stat_opt = ttk.Combobox(frame_2_stat,
                                            width=10,
                                            textvariable=self._be_stat_var,
                                            values=options)
        self._be_stat_opt.pack(side=tk.LEFT, )

        # VIA
        frame_2_via = ttk.Frame(upper_frame)
        frame_2_via.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        self._be_via_var = tk.StringVar(self)
        path = ' '.join(PORT_HANDLER.get_aprs_ais().be_tracer_via)
        self._be_via_var.set(path)
        ttk.Label(frame_2_via, text='via ').pack(side=tk.LEFT, )
        ttk.Entry(frame_2_via, textvariable=self._be_via_var, width=25).pack(side=tk.LEFT, )

        # WIDE
        frame_2_wide = ttk.Frame(upper_frame)
        frame_2_wide.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        self._be_wide_var = tk.StringVar(self)

        self._be_wide_var.set(str(PORT_HANDLER.get_aprs_ais().be_tracer_wide))
        ttk.Label(frame_2_wide, text='via WIDE ').pack(side=tk.LEFT, )
        ttk.Spinbox(frame_2_wide,
                   from_=1,
                   to=7,
                   increment=1,
                   width=3,
                   textvariable=self._be_wide_var,
                   # command=self.change_settings
                   ).pack(side=tk.LEFT, )

        # Interval
        frame_2_interval = ttk.Frame(upper_frame)
        frame_2_interval.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        self._be_interval_var = tk.StringVar(self)

        self._be_interval_var.set(str(PORT_HANDLER.get_aprs_ais().be_tracer_interval))
        ttk.Label(frame_2_interval, text='Interval ').pack(side=tk.LEFT, )
        ttk.Spinbox(frame_2_interval,
                   from_=1,
                   to=60,
                   increment=1,
                   width=3,
                   textvariable=self._be_interval_var,
                   # command=self.change_settings
                   ).pack(side=tk.LEFT, )

        # activ Checkbox
        frame_2_active = ttk.Frame(upper_frame)
        frame_2_active.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        self._be_active_var = tk.BooleanVar(self)
        self._be_active_var.set(PORT_HANDLER.get_aprs_ais().be_tracer_active)
        ttk.Label(frame_2_active, text='Activate ').pack(side=tk.LEFT, )
        ttk.Checkbutton(frame_2_active,
                       variable=self._be_active_var,
                       command=self._chk_active
                       ).pack(side=tk.LEFT, )

        # Save Button

        ttk.Button(
            upper_frame,
            text='SAVE',
            command=self._save_btn
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=20)

        # Send Button

        ttk.Button(
            upper_frame,
            text='SEND',
            command=self._send_btn
        ).pack(side=tk.LEFT, fill=tk.BOTH, padx=20)
        # ALARM
        frame_11_label = ttk.Frame(lower_frame)
        frame_11_label.pack(side=tk.TOP)
        ttk.Label(frame_11_label, text='Alarm Setting').pack()
        ###
        # activ Checkbox
        frame_21_active = ttk.Frame(lower_frame)
        frame_21_active.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        self._alarm_active_var = tk.BooleanVar(self)
        self._alarm_active_var.set(PORT_HANDLER.get_aprs_ais().be_tracer_alarm_active)
        ttk.Label(frame_21_active, text='Activate ').pack(side=tk.LEFT, )
        ttk.Checkbutton(frame_21_active,
                       variable=self._alarm_active_var,
                       command=self._chk_alarm_active
                       ).pack(side=tk.LEFT, )

        # Alarm Distance
        frame_21_distance = ttk.Frame(lower_frame)
        frame_21_distance.pack(side=tk.LEFT, fill=tk.BOTH, padx=30)
        self._alarm_distance_var = tk.StringVar(self)

        self._alarm_distance_var.set(str(PORT_HANDLER.get_aprs_ais().be_tracer_alarm_range))
        ttk.Label(frame_21_distance, text='Distance ').pack(side=tk.LEFT, )
        ttk.Spinbox(frame_21_distance,
                   from_=1,
                   to=20000,
                   increment=1,
                   width=6,
                   textvariable=self._alarm_distance_var,
                   command=self._set_alarm_distance
                   ).pack(side=tk.LEFT, )

        ##########################
        # Middle Frame ( Treeview )
        tree_Frame = ttk.Frame(middle_frame)
        tree_Frame.pack(fill=tk.BOTH, expand=True)
        tree_Frame.grid_rowconfigure(0, weight=1)
        tree_Frame.grid_columnconfigure(0, weight=1)
        self._tree_data = []
        columns = (
            'rx_time',
            'call',
            'port',
            'path',
            'rtt',
            'locator',
            'distance',
        )
        self._tree = ttk.Treeview(tree_Frame, columns=columns, show='headings')
        self._tree.grid(row=0, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_Frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self._tree.heading('rx_time', text='RX-TIME', )
        self._tree.heading('call', text='CALL', )
        self._tree.heading('port', text='Port', )
        self._tree.heading('path', text='Path', )
        self._tree.heading('rtt', text='RTT', )
        self._tree.heading('locator', text='LOC', )
        self._tree.heading('distance', text='Distance', )
        self._tree.column("rx_time", anchor=tk.CENTER, stretch=tk.YES, width=100)
        self._tree.column("call", anchor=tk.CENTER, stretch=tk.YES, width=90)
        self._tree.column("port", anchor=tk.CENTER, stretch=tk.YES, width=60)
        self._tree.column("path", anchor=tk.CENTER, stretch=tk.YES, width=180)
        self._tree.column("rtt", anchor=tk.CENTER, stretch=tk.YES, width=60)
        self._tree.column("locator", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("distance", anchor=tk.CENTER, stretch=tk.YES, width=80)
        ##########################
        # Lower Frame ( Infos )

        ##########################
        # self._chk_port()
        self._update_tree_data()

    def _update_tree_data(self):
        self._format_tree_data()
        self._update_tree()

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        self._tree.tag_configure("tr_alarm", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        for ret_ent in self._tree_data:
            if ret_ent[1]:
                self._tree.insert('', tk.END, values=ret_ent[0], tags=('tr_alarm',))
            else:
                self._tree.insert('', tk.END, values=ret_ent[0], )

    def _format_tree_data(self):
        traces: dict = PORT_HANDLER.get_aprs_ais().tracer_traces_get()
        self._tree_data = []
        tr_keys = list(traces.keys())
        tr_keys.reverse()
        for k in tr_keys:
            pack = traces[k][-1]
            rx_time = pack.get('rx_time', '')
            if rx_time:
                rx_time = rx_time.strftime('%d/%m/%y %H:%M:%S')
            path = pack.get('path', [])
            call = pack.get('call', '')
            if call:
                path = ', '.join(path)
                port_id = pack.get('port_id', -1)
                rtt = pack.get('rtt', 0)
                loc = pack.get('locator', '')
                dist = pack.get('distance', 0)

                self._tree_data.append(((
                    rx_time,
                    call,
                    port_id,
                    path,
                    f'{rtt:.2f}',
                    loc,
                    dist,
                ), pack.get('tr_alarm', False)))
                pack['tr_alarm'] = False

    def _save_btn(self):
        self._save_vars()
        self._save_to_cfg()

    def _save_vars(self):
        PORT_HANDLER.get_aprs_ais().be_tracer_port = int(self._be_port_var.get())
        PORT_HANDLER.get_aprs_ais().be_tracer_station = self._be_stat_var.get()
        PORT_HANDLER.get_aprs_ais().be_tracer_wide = self._be_wide_var.get()
        path = get_list_fm_viaStr(self._be_via_var.get())
        PORT_HANDLER.get_aprs_ais().be_tracer_via = list(path)
        PORT_HANDLER.get_aprs_ais().be_tracer_interval = int(self._be_interval_var.get())
        PORT_HANDLER.get_aprs_ais().be_tracer_active = self._be_active_var.get()
        PORT_HANDLER.get_aprs_ais().be_tracer_alarm_active = bool(self._alarm_active_var.get())
        PORT_HANDLER.get_aprs_ais().be_tracer_alarm_range = int(self._alarm_distance_var.get())

    @staticmethod
    def _save_to_cfg():
        PORT_HANDLER.get_aprs_ais().save_conf_to_file()

    def _send_btn(self):
        self._save_vars()
        PORT_HANDLER.get_aprs_ais().tracer_sendit()

    def _chk_alarm_active(self, event=None):
        PORT_HANDLER.get_aprs_ais().be_tracer_alarm_active = bool(self._alarm_active_var.get())

    def _set_alarm_distance(self, event=None):
        PORT_HANDLER.get_aprs_ais().be_tracer_alarm_range = int(self._alarm_distance_var.get())

    def _chk_port(self, event=None):
        try:
            port_id = int(self._be_port_var.get())
        except ValueError:
            pass
        else:
            vals = PORT_HANDLER.get_stat_calls_fm_port(port_id)
            if vals:
                self._be_stat_var.set(vals[0])
            self._be_stat_opt.configure(values=vals)
            self._save_vars()

    def _chk_active(self, event=None):
        # FIXME
        self._save_vars()
        self._root_win.set_tracer_fm_aprs()
        # self._root_win.set_tracer_icon()

    def delete_all_data(self):
        PORT_HANDLER.get_aprs_ais().tracer_traces_delete()
        self._update_tree_data()

    def get_tracer_tree(self):
        return self._tree
