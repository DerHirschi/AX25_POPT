import threading
import tkinter as tk
from tkinter import ttk

from cfg.constant import ONE_WIRE_MAP, FONT
from cfg.default_config import getNew_1wire_device_cfg
from cfg.popt_config import POPT_CFG
from fnc.one_wire_fnc import is_1wire_device, get_all_1wire_paths, get_1wire_temperature, get_max_1wire


class OneWireSettings(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        ################################
        # self._lang = POPT_CFG.get_guiCFG_language()
        ################################
        self._rev_ent = False
        self._update_th = None
        self._sens_cfg: dict = dict(POPT_CFG.get_1wire_sensor_cfg())
        self._read_timer_var = tk.StringVar(self)
        self._read_timer_var.set(str(POPT_CFG.get_1wire_loop_timer()))

        self._max_sensor_label = lambda x: f"Max {x} Sensors"
        self._max_sensors = int(get_max_1wire())
        self._max_sensor_label_var = tk.StringVar(self, value=self._max_sensor_label(self._max_sensors))
        # self._metric_var = tk.StringVar(self, value='Metrisch') # NEEEEEEE
        ################################
        upper_frame = tk.Frame(self)
        upper_frame.pack(fill=tk.X)
        ################################
        global_opt_frame = tk.Frame(upper_frame)
        global_opt_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        #
        rt_opt_frame = tk.Frame(global_opt_frame)
        rt_opt_frame.pack(fill=tk.Y, padx=10, pady=10)
        tk.Label(rt_opt_frame, text='Sensor Read Timer in s:').pack(side=tk.LEFT, padx=15)
        opt = [x * 30 for x in range(1, 13)]
        read_timer_menu = tk.OptionMenu(rt_opt_frame, self._read_timer_var, *opt)
        read_timer_menu.pack(side=tk.LEFT, padx=5)
        #
        """
        metric_opt_frame = tk.Frame(global_opt_frame)
        metric_opt_frame.pack(fill=tk.Y, padx=10)
        tk.Label(metric_opt_frame, text='Sensor Read Timer in s:').pack(side=tk.LEFT, padx=15)
        opt = ['Metrisch', 'Imperiales']
        metric_menu = tk.OptionMenu(metric_opt_frame, self._metric_var, *opt)
        metric_menu.pack(side=tk.LEFT, padx=5)
        """
        #
        tk.Label(global_opt_frame, textvariable=self._max_sensor_label_var).pack()
        tk.Button(global_opt_frame, text='Update', command=self._update_sensors).pack(pady=15)
        ################################
        wire_frame = tk.Frame(upper_frame)
        wire_frame.pack(fill=tk.X, expand=True)
        #
        tk.Label(wire_frame, text=ONE_WIRE_MAP, font=(FONT, 9)).pack(pady=10)
        ################################
        ################################
        lower_frame = tk.Frame(self)
        lower_frame.pack(fill=tk.BOTH, expand=True)
        ##########################################################################################
        # TREE
        columns = (
            'str_var',
            'sens_id',
            'sens_val_c',
            # 'sens_val_f',
        )
        self._tree = ttk.Treeview(lower_frame, columns=columns, show='headings')
        self._tree.heading('str_var', text='TextVAR', command=lambda: self._sort_entry('str_var'))
        self._tree.heading('sens_id', text='Sensor ID', command=lambda: self._sort_entry('sens_id'))
        self._tree.heading('sens_val_c', text='Temp °C', command=lambda: self._sort_entry('sens_val_c'))
        # self._tree.heading('sens_val_f', text='Temp °F', command=lambda: self._sort_entry('sens_val_f'))
        self._tree.column("str_var", anchor=tk.W, stretch=tk.YES, width=100)
        self._tree.column("sens_id", anchor=tk.W, stretch=tk.YES, width=100)
        self._tree.column("sens_val_c", anchor=tk.CENTER, stretch=tk.NO, width=100)
        # self._tree.column("sens_val_f", anchor=tk.CENTER, stretch=tk.NO, width=100)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(lower_frame, orient=tk.VERTICAL, command=self._tree.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._update_sensors()

    def _sort_entry(self, col):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(self._tree.set(k, col), k) for k in self._tree.get_children('')]
        tmp.sort(reverse=self._rev_ent)
        self._rev_ent = not self._rev_ent
        for index, (val, k) in enumerate(tmp):
            self._tree.move(k, '', int(index))

    def _update_max_sensors(self):
        if not is_1wire_device():
            self._max_sensors = 0
            self._max_sensor_label_var.set(value=self._max_sensor_label('n/a'))
            return
        self._max_sensors = int(get_max_1wire())
        self._max_sensor_label_var.set(value=self._max_sensor_label(self._max_sensors))

    def _update_sensors(self, event=None):
        if self._update_th is None:
            self._update_th_run()
            return
        if self._update_th.is_alive():
            return
        self._update_th_run()
        return

    def _update_th_run(self):
        self._update_max_sensors()
        self._update_th = threading.Thread(target=self._update_sensors_th)
        self._update_th.start()

    def _update_sensors_th(self):
        if not is_1wire_device():
            self._reset_tree_data()
            return
        sensors_paths: list = get_all_1wire_paths()
        if not sensors_paths:
            self._reset_tree_data()
            return
        sens_data = {}
        for sens_id in sensors_paths:
            sens_data[sens_id]: str = str(get_1wire_temperature(sens_id)[0])
        sensors = list(sens_data.keys())
        # Update / Delete old Sensors
        for strVar, cfg in dict(self._sens_cfg).items():
            tmp_id = cfg.get('device_path', '')
            if tmp_id in sensors:
                cfg['device_value'] = sens_data.get(tmp_id, None)
                cfg['StringVar'] = str(strVar)
                sensors.remove(tmp_id)
            else:
                del self._sens_cfg[strVar]
        # Add New Sensors
        for sens_id in sensors:
            n = 1
            while f"$1wire-{n}" in self._sens_cfg:
                n += 1
                if n > self._max_sensors:
                    self._update_tree()
                    return
            strVar = f"$1wire-{n}"
            wire_cfg = getNew_1wire_device_cfg(sens_id)
            wire_cfg['device_value'] = sens_data.get(sens_id, None)
            wire_cfg['StringVar'] = str(strVar)
            self._sens_cfg[strVar] = wire_cfg

        self._update_tree()

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)

        for strVar, cfg in dict(self._sens_cfg).items():
            val = (strVar,
                   cfg.get('device_path', '---'),
                   cfg.get('device_value', 'n/a'))
            self._tree.insert('', tk.END, values=val, )


    def _reset_tree_data(self):
        self._sens_cfg = {}
        for i in self._tree.get_children():
            self._tree.delete(i)

    def save_config(self):
        old_sensor_cfg = POPT_CFG.get_1wire_sensor_cfg()
        old_timer_cfg = POPT_CFG.get_1wire_loop_timer()
        try:
            new_timer_cfg = max(30, int(self._read_timer_var.get()))
        except ValueError:
            new_timer_cfg = 60
        if all((
            old_sensor_cfg == dict(self._sens_cfg),
            old_timer_cfg == new_timer_cfg
        )):
            return False

        POPT_CFG.set_1wire_sensor_cfg(dict(self._sens_cfg))
        POPT_CFG.set_1wire_loop_timer(new_timer_cfg)
        return True
