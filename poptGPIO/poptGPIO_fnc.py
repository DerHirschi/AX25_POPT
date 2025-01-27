import time
from cfg.logger_config import logger


class GPIO_DefaultFNC:
    def __init__(self, gpio, pin_cfg: dict):
        self._logTag = 'GPIO_DefaultFNC: '
        self._pin_cfg = pin_cfg
        self._gpio = gpio
        if not hasattr(self._gpio, 'get_gpioPH'):
            logger.error(self._logTag + "self._gpio can't find get_gpioPH()")
            raise AttributeError("self._gpio can't find get_gpioPH()")
        self._port_handler = self._gpio.get_gpioPH()
        #######################################
        self._pin_fnc_cfg = pin_cfg.get('function_cfg', {})
        self._pin = pin_cfg.get('pin', 0)
        self._task_timer = time.time()
        self._parm_task_timer = self._pin_fnc_cfg.get('task_timer', 0)
        self._cfg_blink = self._pin_fnc_cfg.get('blink', 0)
        self._cfg_hold = self._pin_fnc_cfg.get('hold_timer', 0)
        # self._cfg_pol = self._pin_fnc_cfg.get('polarity_high', 1)
        self._is_blink = bool(self._cfg_blink) and not bool(self._cfg_hold)
        self._hold_timer = time.time()
        self._hold_trigger = False, False
        self._e = False
        self._setup_gpio()

    def _setup_gpio(self):
        self._set_gpio_val(self._pin_cfg.get('value', False))

    def gpioFNC_tasker(self):
        if self._e:
            return
        if not self._parm_task_timer:
            self._gpioFNC_task()
            return
        if time.time() > self._task_timer:
            self._gpioFNC_task()
            self._task_timer = time.time() + self._parm_task_timer
            return
        return

    def _gpioFNC_task(self):
        pass

    def gpioFNC_get_e_state(self):
        return bool(self._e)


    def _get_gpio_val(self):
        if not hasattr(self._gpio, 'get_pin_val'):
            logger.error(self._logTag + "_get_gpio_val: AttributeError")
            self._e = True
            return None
        try:
            ret = self._gpio.get_pin_val(self._pin)
        except IOError as e:
            logger.error(self._logTag + e)
            self._e = True
            return None
        if ret is None:
            logger.error(self._logTag + f"_get_gpio_state: return None on pin {self._pin}")
            logger.error(self._logTag + f"pin_cfg: {self._pin_cfg}")
            logger.error(self._logTag + f"pin_fnc_cfg: {self._pin_fnc_cfg}")
            self._e = True
            return None
        return ret

    #########################################################
    def _set_gpio_val(self, val: bool):
        if not hasattr(self._gpio, 'set_pin_val'):
            logger.error(self._logTag + "_get_gpio_val: AttributeError")
            self._e = True
            return None
        try:
            ret = self._gpio.set_pin_val(self._pin, val)
        except IOError as e:
            logger.error(self._logTag + e)
            self._e = True
            return None
        if not ret:
            logger.error(self._logTag + f"_set_gpio_val: return is False on pin {self._pin}")
            logger.error(self._logTag + f"pin_cfg: {self._pin_cfg}")
            logger.error(self._logTag + f"pin_fnc_cfg: {self._pin_fnc_cfg}")
            self._e = True
            return None
        return True

    #########################################################
    def _set_blink_alarm(self, gpio_val: bool):
        if self._hold_timer > time.time():
            return
        self._set_gpio_val(not gpio_val)
        self._hold_timer = time.time() + self._cfg_blink

    def _set_hold_alarm(self, gpio_val: bool):
        if self._hold_trigger == (True, True):
            return
        if not self._cfg_hold and self._hold_trigger[0]:
            return
        if self._hold_timer > time.time():
            return
        self._set_gpio_val(not gpio_val)
        if self._hold_trigger == (False, False):
            self._hold_trigger = True, False
            self._hold_timer = time.time() + self._cfg_hold
            return
        self._hold_trigger = True, True


class GPIO_DXAlarm(GPIO_DefaultFNC):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'GPIO_DXAlarm: '

    def _gpioFNC_task(self):
        dx_alarm = self._get_dxAlarm_state()
        gpio_val = self._get_gpio_val()
        if any((gpio_val is None, self._e)):
            return

        if all((
                self._is_blink,
                dx_alarm,
        )):
            self._set_blink_alarm(gpio_val)
            return

        if all((
            not self._is_blink,
            self._cfg_hold is not None,
            dx_alarm
        )):
            self._set_hold_alarm(gpio_val)
            return
        if all((
            not self._is_blink,
            self._cfg_hold is not None,
            not dx_alarm
        )):
            self._hold_trigger = False, False

        if dx_alarm and not gpio_val:
            self._set_gpio_val(not gpio_val)
            return
        if not dx_alarm and gpio_val:
            self._set_gpio_val(not gpio_val)
            return

    #########################################################
    def _get_dxAlarm_state(self):
        return bool(self._port_handler.get_dxAlarm())

class GPIO_ConnAlarm(GPIO_DefaultFNC):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'GPIO_ConnAlarm: '

    def _gpioFNC_task(self):
        conn_state = self._get_conn_state()
        gpio_val = self._get_gpio_val()
        if any((gpio_val is None, self._e)):
            return

        if all((
                self._is_blink,
                conn_state,
        )):
            self._set_blink_alarm(gpio_val)
            return

        if all((
                not self._is_blink,
                self._cfg_hold is not None,
                conn_state
        )):
            self._set_hold_alarm(gpio_val)
            return
        if all((
            not self._is_blink,
            self._cfg_hold is not None,
            not conn_state
        )):
            self._hold_trigger = False, False

        if conn_state and not gpio_val:
            self._set_gpio_val(not gpio_val)
            return
        if not conn_state and gpio_val:
            self._set_gpio_val(not gpio_val)
            return

    def _get_conn_state(self):
        return bool(self._port_handler.get_all_connections())
