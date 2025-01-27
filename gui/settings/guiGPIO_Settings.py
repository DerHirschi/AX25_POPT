import tkinter as tk
from tkinter import ttk

from cfg.constant import GPIO_RANGE
from cfg.popt_config import POPT_CFG
from gui.settings.guiGPIO_PinSetup import GPIO_pinSetup
from poptGPIO.gpio_fnc import is_gpio_init, get_gpio_dir, get_gpio_val, is_gpio_device
from poptGPIO.pinctl_fnc import is_pinctrl_device, get_pinctrl_dir, get_pinctrl_val


class GPIOSettings(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        ################################
        # self._lang = POPT_CFG.get_guiCFG_language()
        ################################
        self._gpio = None
        if hasattr(root_win, 'get_GPIOfmPH'):
            self._gpio = root_win.get_GPIOfmPH()
        self._rev_ent = False
        self.pin_setup_win = None
        ################################
        upper_frame = tk.Frame(self)
        upper_frame.pack(fill=tk.X)
        ################################
        global_opt_frame = tk.Frame(upper_frame)
        global_opt_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        tk.Button(global_opt_frame, text='Update', command=self._update_data_fm_cfg).pack(side=tk.LEFT, pady=15, padx=15)
        tk.Button(global_opt_frame, text='Pin Setup', command=self._open_pin_setup).pack(side=tk.LEFT, padx=15)
        ################################
        ################################
        lower_frame = tk.Frame(self)
        lower_frame.pack(fill=tk.BOTH, expand=True)
        ##########################################################################################
        # TREE
        columns = (
            # 'pin_id',
            'gpio_id',
            'gpio_dir',
            'gpio_pol',
            'gpio_initval',
            'gpio_val',
            'gpio_fnc',
            # 'sens_val_f',
        )
        self._tree = ttk.Treeview(lower_frame, columns=columns, show='headings')
        # self._tree.heading('pin_id', text='TextVAR', command=lambda: self._sort_entry('str_var'))
        self._tree.heading('gpio_id', text='GPIO ID', command=lambda: self._sort_entry('gpio_id'))
        self._tree.heading('gpio_dir', text='INPUT', command=lambda: self._sort_entry('gpio_dir'))
        self._tree.heading('gpio_pol', text='Polarity', command=lambda: self._sort_entry('gpio_pol'))
        self._tree.heading('gpio_initval', text='Init-Value', command=lambda: self._sort_entry('gpio_initval'))
        self._tree.heading('gpio_val', text='Value', command=lambda: self._sort_entry('gpio_val'))
        self._tree.heading('gpio_fnc', text='FNC', command=lambda: self._sort_entry('gpio_fnc'))
        # self._tree.column("str_var", anchor=tk.W, stretch=tk.YES, width=100)
        self._tree.column("gpio_id", anchor=tk.W, stretch=tk.NO, width=100)
        self._tree.column("gpio_dir", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self._tree.column("gpio_pol", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self._tree.column("gpio_initval", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self._tree.column("gpio_val", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self._tree.column("gpio_fnc", anchor=tk.CENTER, stretch=tk.YES, width=140)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(lower_frame, orient=tk.VERTICAL, command=self._tree.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._gpio_conf = POPT_CFG.get_gpio_cfg()
        ##### DEV !!!!!!!! #############################
        """
        for pin in range(10, 17):
            pin_name, pin_cfg = getNew_gpio_pin_cfg(pin)
            test_fnc_cfg: dict = getNew_gpio_fnc_cfg_dxAlarm()
            pin_cfg['function_cfg'] = test_fnc_cfg
            self._gpio_conf[pin_name] = pin_cfg
        """

        self._update_data_fm_cfg()

    def _sort_entry(self, col):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(self._tree.set(k, col), k) for k in self._tree.get_children('')]
        tmp.sort(reverse=self._rev_ent)
        self._rev_ent = not self._rev_ent
        for index, (val, k) in enumerate(tmp):
            self._tree.move(k, '', int(index))

    def _update_data_fm_cfg(self, event=None):
        for i in self._tree.get_children():
            self._tree.delete(i)

        if self._gpio is None:
            return

        for pin_name, pin_conf in self._gpio_conf.items():
            pin_id = int(pin_conf.get('pin', 0))
            pin_dir_in = bool(pin_conf.get('pin_dir_in', False))
            polarity_high = bool(pin_conf.get('polarity_high', 1))
            init_value = bool(pin_conf.get('value', False))
            function_cfg = dict(pin_conf.get('function_cfg', {}))
            task_name = str(function_cfg.get('task_name', ''))
            gpio_val = '!Init!'
            if is_pinctrl_device():
                gpio_val = get_pinctrl_val(pin_id)
            elif is_gpio_device():
                if is_gpio_init(pin_id):
                    gpio_val = get_gpio_val(pin_id)
            val = (pin_id,
                   pin_dir_in,
                   polarity_high,
                   init_value,
                   gpio_val,
                   task_name)
            self._tree.insert('', tk.END, values=val, )



    def _open_pin_setup(self):
        if self.pin_setup_win is None:
            self.pin_setup_win = GPIO_pinSetup(self)


    def save_config(self):
        return False

