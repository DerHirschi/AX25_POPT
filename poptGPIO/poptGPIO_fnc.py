import time
from cfg.logger_config import logger


class GPIO_DefaultFNC_OUT:
    def __init__(self, gpio, pin_cfg: dict):
        self._logTag = 'GPIO_DefaultFNC_OUT: '
        self._pin_cfg = pin_cfg
        self._gpio = gpio
        if not hasattr(self._gpio, 'get_gpioPH'):
            logger.error(self._logTag + "self._gpio can't find get_gpioPH()")
            raise AttributeError("self._gpio can't find get_gpioPH()")
        self._port_handler = self._gpio.get_gpioPH()
        #######################################
        # self._pin_fnc_cfg = pin_cfg.get('function_cfg', {})
        self._pin = pin_cfg.get('pin', 0)
        self._task_timer = time.time()
        self._parm_task_timer = self._pin_cfg.get('task_timer', 0)
        self._cfg_blink = self._pin_cfg.get('blink', 0)
        self._cfg_hold = self._pin_cfg.get('hold_timer', 0)
        # self._cfg_pol = self._pin_cfg.get('polarity_high', 1)
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
        state_var = self._get_state_var()
        gpio_val  = self._get_gpio_val()
        if any((gpio_val is None, self._e)):
            return

        if all((
                self._is_blink,
                state_var,
        )):
            self._set_blink_alarm(gpio_val)
            return

        if all((
                not self._is_blink,
                self._cfg_hold is not None,
                state_var
        )):
            self._set_hold_alarm(gpio_val)
            return
        if all((
                not self._is_blink,
                self._cfg_hold is not None,
                not state_var
        )):
            self._hold_trigger = False, False

        if state_var and not gpio_val:
            self._set_gpio_val(not gpio_val)
            return
        if not state_var and gpio_val:
            self._set_gpio_val(not gpio_val)
            return

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
            # logger.error(self._logTag + f"pin_fnc_cfg: {self._pin_fnc_cfg}")
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
            # logger.error(self._logTag + f"pin_fnc_cfg: {self._pin_fnc_cfg}")
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

    def _get_state_var(self):
        return

#############################################################
# Custom CLI CMD
"""
class GPIO_CUSTOM_CLI_CMD(GPIO_DefaultFNC_OUT):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC_OUT.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'Custom CLI-CMD: '
"""
#############################################################
# DX-Alarm
class GPIO_DXAlarmOUT(GPIO_DefaultFNC_OUT):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC_OUT.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'GPIO_DXAlarm: '

    #########################################################
    def _get_state_var(self):
        return bool(self._port_handler.get_dxAlarm())

#############################################################
# Connection-Alarm
class GPIO_ConnAlarmOUT(GPIO_DefaultFNC_OUT):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC_OUT.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'GPIO_ConnAlarm: '

    def _get_state_var(self):
        return bool(self._port_handler.get_all_connections())

#############################################################
# PMS-Alarm (New Mail)
class GPIO_PMSAlarmOUT(GPIO_DefaultFNC_OUT):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC_OUT.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'GPIO_PMSAlarm: '

    def _get_state_var(self):
        if not hasattr(self._gpio, 'get_pms_alarm'):
            self._e = True
            return False
        return bool(self._gpio.get_pms_alarm())

#############################################################
# APRS-Alarm (New Private-Mail)
class GPIO_APRS_PMAlarmOUT(GPIO_DefaultFNC_OUT):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC_OUT.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'GPIO_APRS_PMAlarm: '

    def _get_state_var(self):
        if not hasattr(self._gpio, 'get_aprs_alarm'):
            self._e = True
            return False
        return bool(self._gpio.get_aprs_alarm())

#############################################################
# SYSOP-Alarm //BELL
class GPIO_SYSOP_AlarmOUT(GPIO_DefaultFNC_OUT):
    def __init__(self, gpio, pin_cfg: dict):
        GPIO_DefaultFNC_OUT.__init__(self, gpio=gpio, pin_cfg=pin_cfg)
        self._logTag = 'GPIO_SYSOP_Alarm: '

    def _get_state_var(self):
        if not hasattr(self._gpio, 'get_sysop_alarm'):
            self._e = True
            return False
        return bool(self._gpio.get_sysop_alarm())

#############################################################
# INPUT
"""
class GPIO_DefaultFNC_IN:
    def __init__(self, gpio, pin_cfg: dict):
        self._logTag = 'GPIO_DefaultFNC_IN: '
        self._pin_cfg = pin_cfg
        self._gpio = gpio
        if not hasattr(self._gpio, 'get_gpioPH'):
            logger.error(self._logTag + "self._gpio can't find get_gpioPH()")
            raise AttributeError("self._gpio can't find get_gpioPH()")
        self._port_handler = self._gpio.get_gpioPH()
        #######################################
        # self._pin_fnc_cfg = pin_cfg.get('function_cfg', {})
        self._pin = pin_cfg.get('pin', 0)
        self._task_timer = time.time()
        self._parm_task_timer = self._pin_cfg.get('task_timer', 0)
        # self._cfg_blink = self._pin_cfg.get('blink', 0)
        # self._cfg_hold = self._pin_cfg.get('hold_timer', 0)
        # self._is_blink = bool(self._cfg_blink) and not bool(self._cfg_hold)
        # self._hold_timer = time.time()
        # self._hold_trigger = False, False
        self._e = False

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
            # logger.error(self._logTag + f"pin_fnc_cfg: {self._pin_fnc_cfg}")
            self._e = True
            return None
        return ret
"""
