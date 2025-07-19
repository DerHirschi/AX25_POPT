import tkinter as tk
from tkinter import ttk

from cfg.constant import GPIO_RANGE
from cfg.default_config import getNew_gpio_pin_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class GPIO_pinSetup(tk.Toplevel):
    def __init__(self, root_win, pin_id=1):
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
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        self._lang = POPT_CFG.get_guiCFG_language()
        self.title('GPIO')
        #####################################################
        self._root_win = root_win
        self._gpio = root_win.get_gpio()
        ###############
        self._gpio_cfg = POPT_CFG.get_gpio_cfg()
        self._pin_cfg = '', {}
        self._is_pin_init = False
        self._pin_fnc_opt = dict(
            dx_alarm=self._setup_output_pins,
            conn_alarm=self._setup_output_pins,
            pms_alarm=self._setup_output_pins,
            aprs_alarm=self._setup_output_pins,
            sysop_alarm=self._setup_output_pins,
        )
        self._output_task_names = []
        for el_k, el_fnc in self._pin_fnc_opt.items():
            if el_fnc.__name__ == '_setup_output_pins':
                self._output_task_names.append(str(el_k))

        self._pol_opt = dict(
            normal=True,
            inverted=False
        )
        ###############
        self._pin_id_var    = tk.StringVar(self, value=str(pin_id))
        self._pin_fnc_var   = tk.StringVar(self)
        self._blink_var     = tk.StringVar(self, value=str(1))
        self._hold_var      = tk.IntVar(self,    value=0)
        self._hold_off_var  = tk.BooleanVar(self,value=True)
        self._pol_var       = tk.StringVar(self, value='normal')

        self._init_lable_var = tk.StringVar(self,value='! Not initialised !')
        self._dir_lable_var = tk.StringVar(self, value='Direction Input: n.a')
        self._val_lable_var = tk.StringVar(self, value='Value: n.a')
        self._pol_lable_var = tk.StringVar(self, value='Polarity: n.a')
        #####################################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        #####################################################
        upper_frame = ttk.Frame(main_f)
        upper_frame.pack(expand=False, fill=tk.X)
        # Pin Sel
        pin_opt_frame = ttk.Frame(upper_frame)
        pin_opt_frame.pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Label(pin_opt_frame, text='PIN: ').pack(side=tk.LEFT, padx=5)
        min_pin = GPIO_RANGE[0]
        max_pin = GPIO_RANGE[1]
        pin_selector = ttk.Spinbox(pin_opt_frame,
                                  from_=min_pin,
                                  to=max_pin,
                                  increment=1,
                                  width=3,
                                  textvariable=self._pin_id_var,
                                  command=self._switch_pin_id,
                                  state='normal')

        pin_selector.pack(side=tk.LEFT, padx=10)
        # Init Btn

        setup_btn = ttk.Button(
            upper_frame,
            text='Setup',
            command=self.setup_pin_btn
        )
        setup_btn.pack(side=tk.LEFT, padx=70,)

        del_btn = ttk.Button(
            upper_frame,
            text=get_strTab('delete', self._lang),
            command=self._del_pin
        )
        del_btn.pack(side=tk.LEFT, )

        ###########################################
        # Parameter Frame
        param_frame = ttk.Frame(main_f)
        param_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        ####
        param_frame_l = ttk.Frame(param_frame)
        param_frame_l.pack(expand=True, fill=tk.BOTH, padx=10, pady=10, side=tk.LEFT)
        #
        ttk.Separator(param_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, expand=True)
        #
        param_frame_r = ttk.Frame(param_frame, )
        param_frame_r.pack(expand=True, fill=tk.BOTH, padx=5, pady=10, side=tk.LEFT)
        ###########################################
        # param_frame_l
        ## FNC
        fnc_sel_frame = ttk.Frame(param_frame_l)
        fnc_sel_frame.pack(fill=tk.X, pady=15)
        ttk.Label(fnc_sel_frame, text='Function: ').pack(side=tk.LEFT, padx=5)
        opt = [self._pin_fnc_var.get()] + list(self._pin_fnc_opt.keys())
        if not opt:
            opt = ['', '']
        fnc_selector = ttk.OptionMenu(
            fnc_sel_frame,
            self._pin_fnc_var,
            *opt,
            command=self._select_pin_fnc,
        )
        fnc_selector.pack(side=tk.LEFT, padx=5)

        ############ Blink
        blink_t_frame = ttk.Frame(param_frame_l)
        blink_t_frame.pack(fill=tk.X, pady=10)
        ttk.Label(blink_t_frame, text='Blink Timer s').pack(side=tk.LEFT, padx=5)
        self._blink_sel = ttk.Spinbox(blink_t_frame,
                                      textvariable=self._blink_var,
                                      from_=0,
                                      to=11,
                                      increment=1,
                                      width=3
                                      )
        self._blink_sel.pack(side=tk.LEFT, padx=5)
        self._blink_var.set('1')

        ############ Hold
        hold_t_frame = ttk.Frame(param_frame_l)
        hold_t_frame.pack(fill=tk.X, pady=10)
        ttk.Label(hold_t_frame, text='Hold Timer s').pack(side=tk.LEFT, padx=5)
        # opt = ['OFF'] + list(range(0, 600))
        # self._hold_sel = tk.OptionMenu(hold_t_frame, self._hold_var, *opt)
        self._hold_sel = ttk.Spinbox(hold_t_frame,
                                     from_=0,
                                     to=7200,
                                     increment=10,
                                     width=5,
                                     textvariable=self._hold_var,
                                     # command=self._set_max_frame,
                                     state='normal')

        self._hold_sel.pack(side=tk.LEFT, padx=5)

        self._hold_off_sel = ttk.Checkbutton(hold_t_frame, text='On/Off', variable=self._hold_off_var)
        self._hold_off_sel.pack(side=tk.LEFT, padx=15)

        ############ POL
        pol_t_frame = ttk.Frame(param_frame_l)
        pol_t_frame.pack(fill=tk.X, pady=10)
        ttk.Label(pol_t_frame, text='Polarity').pack(side=tk.LEFT, padx=5)

        opt = list(self._pol_opt.keys())
        self._pol_var.set('normal')
        opt = [self._pin_fnc_var.get()] + opt
        self._pol_sel = ttk.OptionMenu(pol_t_frame, self._pol_var, *opt)
        self._pol_sel.pack(side=tk.LEFT, padx=5)
        ###########################################
        # param_frame_r
        lable_frame_1 = ttk.Frame(param_frame_r)
        lable_frame_2 = ttk.Frame(param_frame_r)
        lable_frame_3 = ttk.Frame(param_frame_r)
        lable_frame_4 = ttk.Frame(param_frame_r)
        lable_frame_1.pack(fill=tk.X)
        lable_frame_2.pack(fill=tk.X)
        lable_frame_3.pack(fill=tk.X)
        lable_frame_4.pack(fill=tk.X)

        ttk.Label(lable_frame_1, textvariable=self._init_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)
        ttk.Label(lable_frame_2, textvariable=self._dir_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)
        ttk.Label(lable_frame_3, textvariable=self._val_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)
        ttk.Label(lable_frame_4, textvariable=self._pol_lable_var).pack(pady=5, fill=tk.X, side=tk.LEFT)

        ###########################################
        # BTN
        btn_frame = ttk.Frame(main_f, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        ok_btn = ttk.Button(btn_frame, text=' OK ', command=self._save_btn)
        ok_btn.pack(side=tk.LEFT)

        abort_btn = ttk.Button(btn_frame, text=get_strTab(str_key='cancel', lang_index=self._lang), command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    ######################################################
    def setup_pin_btn(self):
        try:
            pin_id = int(self._pin_id_var.get())
        except ValueError:
            return
        if not pin_id:
            return
        pin_name = f"pin_{pin_id}"
        if pin_name in self._gpio_cfg:

            self._pin_cfg = pin_name, dict(self._gpio_cfg[pin_name])
            self._update_lable_fm_cfg(self._pin_cfg[1])
            return
        self._pin_cfg = getNew_gpio_pin_cfg(pin_id)
        self._setup_pin(self._pin_cfg[1])
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
        ret = self._gpio.init_pin(pin_conf=pin_cfg)
        if not ret:
            self._reset_pin_lable()
            return
        self._update_lable_fm_cfg(pin_cfg)

    def _del_pin(self):
        pin_name, pin_cfg = self._pin_cfg
        gpio_cfg: dict = POPT_CFG.get_gpio_cfg()
        if pin_name in gpio_cfg:
            del gpio_cfg[pin_name]
            POPT_CFG.set_gpio_cfg(gpio_cfg)
            self._root_win.update_gpio_tree()
            self.destroy_win()

    #################################################################
    def _switch_pin_id(self):
        self._is_pin_init = False

        # self._setup_pin_btn()

    #################################################################
    def _select_pin_fnc(self, event=None):
        pin_fnc = self._pin_fnc_var.get()
        if pin_fnc not in self._pin_fnc_opt:
            return
        self._pin_fnc_opt[pin_fnc]()

    def _setup_output_pins(self):
        self._pol_sel.configure(state='normal')
        self._hold_sel.configure(state='normal')
        self._blink_sel.configure(state='normal')

    def _update_lable_fm_cfg(self, pin_cfg: dict):
        if not pin_cfg:
            self._reset_pin_lable()
            return
        pin_id = pin_cfg.get('pin', 0)
        try:
            pin_val = self._gpio.get_pin_val(pin_id=pin_id)
        except IOError:
            pin_val = None
        pin_pol = pin_cfg.get('polarity_high', 1)
        pin_dir = pin_cfg.get('pin_dir_in', '')
        blink = pin_cfg.get('blink', 1)
        hold = pin_cfg.get('hold_timer', 1)
        pin_fnc_name = pin_cfg.get('task_name', '')
        if pin_val is None:
            self._reset_pin_lable()
            return
        self._pin_fnc_var.set(value=pin_fnc_name)
        if pin_pol:
            self._pol_var.set('normal')
        else:
            self._pol_var.set('inverted')
        self._blink_var.set(str(blink))
        if hold is None:
            self._hold_off_var.set(False)
            self._hold_var.set(0)
        else:
            self._hold_off_var.set(True)
            self._hold_var.set(hold)
        self._init_lable_var.set(value='Init OK')
        self._is_pin_init = True
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
        if not self._is_pin_init:
            return False
        try:
            # pin_id = int(self._pin_id_var.get())
            blink_timer = int(self._blink_var.get())
            pin_fnc = self._pin_fnc_var.get()
        except ValueError:
            return False
        hold_timer = self._hold_var.get()
        hold_off = self._hold_off_var.get()
        if not hold_off:
            hold_timer = None
        else:
            try:
                hold_timer = int(hold_timer)
            except ValueError:
                return False
        if not pin_fnc:
            return False

        pol_high = dict(
            normal=1,
            inverted=0
        ).get(self._pol_var.get(), 1)
        pin_name, pin_cfg = self._pin_cfg
        if pin_fnc in self._output_task_names:
            pin_cfg['pin_dir_in'] = False
        else:
            pin_cfg['pin_dir_in'] = True
        pin_cfg['value'] = False
        pin_cfg['task_name'] = pin_fnc
        pin_cfg['blink'] = blink_timer
        pin_cfg['hold_timer'] = hold_timer
        pin_cfg['polarity_high'] = int(pol_high)
        gpio_cfg: dict = POPT_CFG.get_gpio_cfg()
        gpio_cfg[pin_name] = dict(pin_cfg)
        POPT_CFG.set_gpio_cfg(gpio_cfg)

    ######################################################
    def _save_btn(self):
        self._save_cfg()
        self._root_win.update_gpio_tree()
        self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        self._root_win.pin_setup_win = None
        self.destroy()

