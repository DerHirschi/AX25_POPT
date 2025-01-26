import time

from cfg.default_config import getNew_gpio_pin_cfg, getNew_gpio_fnc_cfg_dxAlarm
from poptGPIO.gpio_fnc import is_gpio_device, set_gpio_dir, setup_gpio, set_gpio_val, close_gpio, get_gpio_val
from poptGPIO.pinctl_fnc import is_pinctrl_device, set_pinctrl_dir, set_pinctrl_val, get_pinctrl_val
from cfg.logger_config import logger
from poptGPIO.poptGPIO_fnc import GPIO_DXAlarm


class poptGPIO_main:
    def __init__(self, portHandler):
        self._logTag = 'poptGPIO: '
        logger.info(self._logTag + "Init")
        self._portHandler = portHandler
        self._is_pinctrl = is_pinctrl_device()
        if not any((self._is_pinctrl, is_gpio_device())):
            logger.warning(self._logTag + f"No GPIO Device found !")
            logger.warning(self._logTag + "Init failed !")
            raise IOError('No GPIO Device found !')

        self._gpio_conf = {}
        ##### DEV !!!!!!!! #############################
        for pin in range(10, 17):
            pin_name, pin_cfg = getNew_gpio_pin_cfg(pin)
            test_fnc_cfg: dict = getNew_gpio_fnc_cfg_dxAlarm()
            pin_cfg['function_cfg'] = test_fnc_cfg
            self._gpio_conf[pin_name] = pin_cfg
        ##################################
        self._pin_cfg = {}
        self._init_fm_conf()
        ##################################
        self._FNC_TAB = dict(
            dx_alarm=GPIO_DXAlarm,
        )
        self._gpio_tasks = {}
        self._init_tasker_fm_conf()

        logger.info(self._logTag + "Init done..")

    def _init_fm_conf(self):
        logger.info(self._logTag + "Init Pins fm Config..")
        for att_name, value in self._gpio_conf.items():
            if att_name.startswith('pin_'):
                if not self._setup_pin(value):
                    logger.error(self._logTag + "Init Pins fm Config")
                    logger.error(self._logTag + f"pinctrl: {self._is_pinctrl}")
                    logger.error(self._logTag + f"{att_name} > {value}")
                    continue
                time.sleep(0.05)
                self._pin_cfg[att_name] = value
                logger.info(self._logTag + f"{att_name} init successful!  pinctrl: {self._is_pinctrl}")
        logger.info(self._logTag + "Init Pins fm Config.. Done !")

    def _init_tasker_fm_conf(self):
        logger.info(self._logTag + "Init Tasker fm Config..")
        for pin_name, pin_cfg in self._pin_cfg.items():
            pin_fnc_cfg: dict = pin_cfg.get('function_cfg', {})
            pin_fnc_name = pin_fnc_cfg.get('task_name', '')
            pin_fnc = self._FNC_TAB.get(pin_fnc_name, None)
            if pin_fnc is not None:
                try:
                    self._gpio_tasks[pin_name] = pin_fnc(gpio=self, pin_cfg=pin_cfg)
                except AttributeError as e:
                    logger.error(self._logTag + f"{e}")
                    continue
        logger.info(self._logTag + "Init Tasker fm Config..Done !")

    #####################################################################
    def gpio_tasker(self):
        """ Called fm PortHandler 0.5 sec """
        for pin_name, pin_fnc in dict(self._gpio_tasks).items():
            if hasattr(pin_fnc, 'gpioFNC_get_e_state'):
                if pin_fnc.gpioFNC_get_e_state():
                    del self._gpio_tasks[pin_name]
                    continue
            else:
                del self._gpio_tasks[pin_name]
                continue
            if hasattr(pin_fnc, 'gpioFNC_tasker'):
                pin_fnc.gpioFNC_tasker()
            else:
                del self._gpio_tasks[pin_name]
                continue

    #####################################################################
    def _setup_pin(self, pin_conf: dict):
        pin = pin_conf.get('pin', 0)
        if not pin:
            logger.error(self._logTag + "_setup_pin: No Pin (Pin = 0)")
            return False
        if self._is_pinctrl:
            return self._setup_pinctrl_pin(pin_conf)
        return self._setup_gpio_pin(pin_conf)

    def _setup_pinctrl_pin(self, pin_conf: dict):
        pin = pin_conf.get('pin', 0)
        pin_dir_in = pin_conf.get('pin_dir_in', False)
        value = pin_conf.get('value', True)
        res = set_pinctrl_dir(pin, pin_dir_in)
        time.sleep(0.05)
        if not res:
            logger.error(self._logTag + f"_setup_pinctrl_pin: {res}")
            return False
        if value is not None and not pin_dir_in:
            if not pin_conf.get('polarity_high', 1):
                value = bool(not value)
            return set_pinctrl_val(pin, value=value)
        return True

    def _setup_gpio_pin(self, pin_conf: dict):
        pin = pin_conf.get('pin', 0)
        pin_dir_in = pin_conf.get('pin_dir_in', False)
        value = pin_conf.get('value', True)
        res = setup_gpio(pin)
        if not res:
            logger.error(self._logTag + f"_setup_gpio_pin, setup_gpio(): {res}")
            return False
        res = set_gpio_dir(pin, pin_dir_in)
        time.sleep(0.05)
        if not res:
            logger.error(self._logTag + f"_setup_gpio_pin, set_gpio_dir(): {res}")
            return False

        if value is not None and not pin_dir_in:
            if not pin_conf.get('polarity_high', 1):
                value = bool(not value)
            return set_gpio_val(pin, value=value)
        return True

    #####################################################################
    def get_pin_val(self, pin_id: int):
        pin_name = f"pin_{pin_id}"
        if pin_name not in self._pin_cfg:
            logger.error(self._logTag + f"{pin_name} not in Config")
            raise IOError(f"{pin_name} not in Config")
        pin_conf = self._pin_cfg.get(pin_name, {})
        if self._is_pinctrl:
            ret = get_pinctrl_val(pin_id)
            time.sleep(0.03)
            if ret is None:
                return None
            if not pin_conf.get('polarity_high', 1):
                return not ret
            return ret
        ret = get_gpio_val(pin_id)
        time.sleep(0.03)
        if ret is None:
            return None
        if not pin_conf.get('polarity_high', 1):
            return not ret
        return ret

    def set_pin_val(self, pin_id: int, val: bool):
        pin_name = f"pin_{pin_id}"
        if pin_name not in self._pin_cfg:
            logger.error(self._logTag + f"{pin_name} not in Config")
            raise IOError(f"{pin_name} not in Config")
        pin_conf = self._pin_cfg.get(pin_name, {})
        if self._is_pinctrl:
            if not pin_conf.get('polarity_high', 1):
                val = bool(not val)
            return set_pinctrl_val(gpio=pin_id, value=val)
        if not pin_conf.get('polarity_high', 1):
            val = bool(not val)
        ret = set_gpio_val(gpio=pin_id, value=val)
        time.sleep(0.03)
        return ret

    #####################################################################
    def is_pinctrl(self):
        return bool(self._is_pinctrl)

    def get_gpioPH(self):
        return self._portHandler

    #####################################################################
    def close_gpio_pins(self):
        logger.info(self._logTag + "CLosing GPIO")
        if self._is_pinctrl:
            logger.info(self._logTag + f"CLosing GPIO done ! pinctrl: {self._is_pinctrl}")
            return True
        for pin_name, pin_conf in self._gpio_conf.items():
            pin = pin_conf.get('pin', 0)
            if not pin:
                continue
            res = close_gpio(pin)
            if not res:
                logger.error(self._logTag + f"CLosing GPIO - pin:{pin}: {res}")
                continue
            logger.info(self._logTag + f"CLosing GPIO - pin:{pin}: done!")

        logger.info(self._logTag + "CLosing GPIO done !")
        return True
