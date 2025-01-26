import tkinter as tk
from tkinter import ttk

from cfg.constant import GPIO_RANGE
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
        ################################
        upper_frame = tk.Frame(self)
        upper_frame.pack(fill=tk.X)
        ################################
        global_opt_frame = tk.Frame(upper_frame)
        global_opt_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        tk.Button(global_opt_frame, text='Update', command=self._update_data_fm_cfg).pack(pady=15, padx=15)
        ################################
        ################################
        lower_frame = tk.Frame(self)
        lower_frame.pack(fill=tk.BOTH, expand=True)
        ##########################################################################################
        # TREE
        columns = (
            'str_var',
            'gpio_id',
            'gpio_dir',
            'gpio_val',
            # 'sens_val_f',
        )
        self._tree = ttk.Treeview(lower_frame, columns=columns, show='headings')
        self._tree.heading('str_var', text='TextVAR', command=lambda: self._sort_entry('str_var'))
        self._tree.heading('gpio_id', text='GPIO ID', command=lambda: self._sort_entry('gpio_id'))
        self._tree.heading('gpio_dir', text='IN/OUT', command=lambda: self._sort_entry('gpio_dir'))
        self._tree.heading('gpio_val', text='Value', command=lambda: self._sort_entry('gpio_val'))
        self._tree.column("str_var", anchor=tk.W, stretch=tk.YES, width=100)
        self._tree.column("gpio_id", anchor=tk.W, stretch=tk.YES, width=100)
        self._tree.column("gpio_dir", anchor=tk.CENTER, stretch=tk.NO, width=100)
        self._tree.column("gpio_val", anchor=tk.CENTER, stretch=tk.NO, width=100)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(lower_frame, orient=tk.VERTICAL, command=self._tree.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._gpio_conf = dict(

            pin_10=dict(
                pin=10,
                pin_dir_in=False,
                value=None,  # True/False/None = no state set on init(pin setup)
                function='',
                function_cfg={},
            ),
            pin_11=dict(
                pin=11,
                pin_dir_in=False,
                value=True,  # True/False/None = no state set on init(pin setup)
                function='',
                function_cfg={},
            ),
            pin_12=dict(
                pin=12,
                pin_dir_in=False,
                value=True,  # True/False/None = no state set on init(pin setup)
                function='',
                function_cfg={},
            ),
            pin_13=dict(
                pin=13,
                pin_dir_in=False,
                value=True,  # True/False/None = no state set on init(pin setup)
                function='',
                function_cfg={},
            ),
        )

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
        # data = {}
        if self._gpio is None:
            return
        """
        pin_cfgs = {}
        for att_name, value in self._gpio_conf.items():
            if att_name.startswith('pin_') and type(value) == dict:
                pin_cfgs[att_name] = dict(value)
        """
        # if self._gpio.is_pinctrl:
        for gpio in range(GPIO_RANGE[0], GPIO_RANGE[1] + 1):
            gpio_dir = None
            gpio_val = None
            if is_pinctrl_device():
                gpio_dir = get_pinctrl_dir(gpio)
                gpio_val = get_pinctrl_val(gpio)
            elif is_gpio_device():
                if not is_gpio_init(gpio):
                    continue
                gpio_dir = get_gpio_dir(gpio)
                gpio_val = get_gpio_val(gpio)

            textVar = f"$gpio-{gpio}"
            val = (textVar,
                   int(gpio),
                   gpio_dir,
                   gpio_val)
            self._tree.insert('', tk.END, values=val, )
            """
            data[gpio] = dict(
                gpio_id=int(gpio),
                gpio_dir=str(gpio_dir),
                gpio_val=gpio_val,
            )
            """
            return


    def save_config(self):
        return False

