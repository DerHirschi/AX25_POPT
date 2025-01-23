from poptGPIO.gpio_fnc import is_gpio_device
from poptGPIO.pinctl_fnc import is_pinctrl_device
from cfg.logger_config import logger

class poptGPIO_main:
    def __init__(self):
        self._log_tag = 'poptGPIO: '
        logger.info(self._log_tag + "Init")
        self._is_pinctrl = is_pinctrl_device()
        is_gpio_dev = is_gpio_device()
        if not all((self._is_pinctrl, is_gpio_dev)):
            logger.warning(self._log_tag + f"No GPIO Device found !")
            logger.warning(self._log_tag + "Init failed !")
            raise IOError('No GPIO Device found !')

        logger.info(self._log_tag + "Init done..")


test = poptGPIO_main()
