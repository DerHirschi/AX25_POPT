import tkinter as tk
from tkinter import ttk

from cfg.constant import GPIO_RANGE
from cfg.default_config import getNew_gpio_pin_cfg
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class GPIO_pinSetup(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        win_width = 600
        win_height = 400
        # self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.attributes("-topmost", True)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._lang = POPT_CFG.get_guiCFG_language()
        # TODO self.title(get_strTab(str_key='settings', lang_index=self._lang))
        #####################################################
        self._root_win = root_win
        self._gpio = root_win.get_gpio()
        ###############
        self._pin_fnc_opt = dict(
            dx_alarm=self._setup_dxalarm,
            conn_alarm=self._setup_connalarm,
        )
        self._pol_opt = dict(
            normal=True,
            inverted=False
        )
        ###############
        self._pin_id_var = tk.StringVar(self, value=str(1))
        self._pin_fnc_var = tk.StringVar(self)
        self._blink_var = tk.StringVar(self, value=str(1))
        self._hold_var = tk.StringVar(self, value=str(0))
        self._pol_var = tk.StringVar(self, value='normal')

        self._init_lable_var = tk.StringVar(self, value='! Not initialised !')
        self._dir_lable_var = tk.StringVar(self, value='Direction Input: n.a')
        self._val_lable_var = tk.StringVar(self, value='Value: n.a')
        self._pol_lable_var = tk.StringVar(self, value='Polarity: n.a')
        #####################################################
        upper_frame = tk.Frame(self)
        upper_frame.pack(expand=False, fill=tk.X)
        # Pin Sel
        pin_opt_frame = tk.Frame(upper_frame)
        pin_opt_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(pin_opt_frame, text='PIN: ').pack(side=tk.LEFT, padx=5)
        min_pin = GPIO_RANGE[0]
        max_pin = GPIO_RANGE[1]
        pin_selector = tk.Spinbox(pin_opt_frame,
                                  from_=min_pin,
                                  to=max_pin,
                                  increment=1,
                                  width=3,
                                  textvariable=self._pin_id_var,
                                  # command=self._set_max_frame,
                                  state='normal')

        pin_selector.pack(side=tk.LEFT, padx=10)
        # Init Btn
        setup_btn = tk.Button(
            upper_frame,
            text='Setup',
            command=self._setup_pin_btn
        )
        setup_btn.pack(side=tk.LEFT, padx=70,)
        ###########################################
        # Parameter Frame
        param_frame = tk.Frame(self)
        param_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        ####
        param_frame_l = tk.Frame(param_frame)
        param_frame_l.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side=tk.LEFT)
        #
        ttk.Separator(param_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, expand=True)
        #
        param_frame_r = tk.Frame(param_frame, )
        param_frame_r.pack(expand=True, fill=tk.BOTH, padx=5, pady=10, side=tk.LEFT)
        ###########################################
        # param_frame_l
        ## FNC
        fnc_sel_frame = tk.Frame(param_frame_l)
        fnc_sel_frame.pack(fill=tk.X, pady=15)
        tk.Label(fnc_sel_frame, text='Function: ').pack(side=tk.LEFT, padx=5)
        fnc_selector = tk.OptionMenu(
            fnc_sel_frame,
            self._pin_fnc_var,
            *self._pin_fnc_opt.keys(),
            # command=
        )
        fnc_selector.pack(side=tk.LEFT, padx=5)

        ############ Blink
        blink_t_frame = tk.Frame(param_frame_l)
        blink_t_frame.pack(fill=tk.X, pady=10)
        tk.Label(blink_t_frame, text='Blink Timer s').pack(side=tk.LEFT, padx=5)
        opt = range(1,11)
        blink_sel = tk.OptionMenu(blink_t_frame, self._blink_var, *opt)
        blink_sel.pack(side=tk.LEFT, padx=5)

        ############ Hold
        hold_t_frame = tk.Frame(param_frame_l)
        hold_t_frame.pack(fill=tk.X, pady=10)
        tk.Label(hold_t_frame, text='Hold Timer s').pack(side=tk.LEFT, padx=5)
        opt = range(1, 600)
        hold_sel = tk.OptionMenu(hold_t_frame, self._hold_var, *opt)
        hold_sel.pack(side=tk.LEFT, padx=5)

        ############ POL
        pol_t_frame = tk.Frame(param_frame_l)
        pol_t_frame.pack(fill=tk.X, pady=10)
        tk.Label(pol_t_frame, text='Polarity').pack(side=tk.LEFT, padx=5)

        opt = self._pol_opt.keys()
        pol_sel = tk.OptionMenu(pol_t_frame, self._pol_var, *opt)
        pol_sel.pack(side=tk.LEFT, padx=5)

        ###########################################
        # param_frame_r
        lable_frame_1 = tk.Frame(param_frame_r)
        lable_frame_2 = tk.Frame(param_frame_r)
        lable_frame_3 = tk.Frame(param_frame_r)
        lable_frame_4 = tk.Frame(param_frame_r)
        lable_frame_1.pack(fill=tk.X)
        lable_frame_2.pack(fill=tk.X)
        lable_frame_3.pack(fill=tk.X)
        lable_frame_4.pack(fill=tk.X)

        tk.Label(lable_frame_1, textvariable=self._init_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)
        tk.Label(lable_frame_2, textvariable=self._dir_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)
        tk.Label(lable_frame_3, textvariable=self._val_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)
        tk.Label(lable_frame_4, textvariable=self._pol_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)

        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        ok_btn = tk.Button(btn_frame, text=' OK ', command=self._save_btn)
        ok_btn.pack(side=tk.LEFT)

        abort_btn = tk.Button(btn_frame, text=get_strTab(str_key='cancel', lang_index=self._lang), command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    ######################################################
    def _setup_pin_btn(self):
        try:
            pin_id = int(self._pin_id_var.get())
        except ValueError:
            return
        pin_cfg = self._gpio.get_pin_conf()
        
        if f"pin_{pin_id}" in pin_cfg:
            self._update_lable_fm_cfg(pin_cfg.get(f"pin_{pin_id}", {}))
            return
        pin_cfg = getNew_gpio_pin_cfg(pin_id)
        self._setup_pin(pin_cfg[1])
        """
        pin_fnc = self._pin_fnc_var.get()
        if pin_fnc not in self._pin_fnc_opt.keys():
            return
        pin_cfg = getNew_gpio_pin_cfg(pin_id)
        setup_fnc = self._pin_fnc_opt[pin_fnc]
        ret = setup_fnc(pin_id=pin_id)
        """

    def _setup_pin(self, pin_cfg: dict):
        if not pin_cfg:
            self._reset_pin_lable()
            return
        ret = self._gpio.add_pin(pin_conf=pin_cfg)
        if not ret:
            self._reset_pin_lable()
            return

        pin_id = pin_cfg.get('pin', 0)
        try:
            pin_val = self._gpio.get_pin_val(pin_id=pin_id)
        except IOError:
            pin_val = None
        pin_pol = pin_cfg.get('polarity_high', '')
        pin_dir = pin_cfg.get('pin_dir_in', '')
        pin_fnc_name = pin_cfg.get('function_cfg', {}).get('task_name', '')
        if pin_val is None:
            self._reset_pin_lable()
            return
        self._pin_fnc_var.set(value=pin_fnc_name)
        self._init_lable_var.set(value='Init OK')

        self._dir_lable_var.set(value=f'Direction Input: {pin_dir}')
        self._val_lable_var.set(value=f'Value: {pin_val}')
        pol_str = 'n.a.'
        for opt_str, val in self._pol_opt.items():
            if val == bool(pin_pol):
                pol_str = val
                break
        self._pol_lable_var.set(value=f'Polarity: {pol_str}')

    def _setup_dxalarm(self, pin_id: int):
        pass

    def _setup_connalarm(self, pin_id: int):
        pass

    def _update_lable_fm_cfg(self, pin_cfg: dict):
        if not pin_cfg:
            self._reset_pin_lable()
            return
        pin_id = pin_cfg.get('pin', 0)
        try:
            pin_val = self._gpio.get_pin_val(pin_id=pin_id)
        except IOError:
            pin_val = None
        pin_pol = pin_cfg.get('polarity_high', '')
        pin_dir = pin_cfg.get('pin_dir_in', '')
        pin_fnc_name = pin_cfg.get('function_cfg', {}).get('task_name', '')
        if pin_val is None:
            self._reset_pin_lable()
            return
        self._pin_fnc_var.set(value=pin_fnc_name)
        self._init_lable_var.set(value='Init OK')

        self._dir_lable_var.set(value=f'Direction Input: {pin_dir}')
        self._val_lable_var.set(value=f'Value: {pin_val}')
        pol_str = 'n.a.'
        for opt_str, val in self._pol_opt.items():
            if val == bool(pin_pol):
                pol_str = val
                break
        self._pol_lable_var.set(value=f'Polarity: {pol_str}')

    ######################################################
    def _reset_pin_lable(self):
        self._init_lable_var.set(value='! Not initialised !')
        self._dir_lable_var.set(value='Direction Input: n.a')
        self._val_lable_var.set(value='Value: n.a')
        self._pol_lable_var.set(value='Polarity: n.a')
        self._pin_fnc_var.set(value='')

    ######################################################
    def _save_cfg(self):
        pass

    ######################################################
    def _save_btn(self):
        self._save_cfg()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        self._root_win.pin_setup_win = None
        self.destroy()