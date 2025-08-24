"""
PoPT GPIO Functions.
Pi GPIO 0-26

setup_gpio(pin)
set_gpio_dir(pin, False)  -  Fasle = Output | True = Input
set_gpio_val(pin, bool)
get_gpio_val(pin) -> bool / None
"""

import os

from cfg.constant import GPIO_PATH
from cfg.logger_config import logger
from fnc.os_fnc import is_linux, path_exists


def is_gpio_device():
    if not is_linux():
        return False
    return path_exists(GPIO_PATH)

def is_gpio_init(gpio: int):
    gpio_path = GPIO_PATH + f"/gpio{gpio}"
    return path_exists(gpio_path)

def close_gpio(gpio: int):
    if not is_gpio_device():
        logger.warning(f"GPIO: close_gpio No GPIO Device")
        return False
    if not is_gpio_init(gpio):
        return False
    os_cmd = f"echo {gpio} > {GPIO_PATH}/unexport"
    try:
        ret = os.system(os_cmd)
    except TypeError:
        logger.error(f"GPIO: close_gpio TypeError: {os_cmd}")
        return False
    if ret:
        logger.error(f"GPIO: close_gpio() 1 > {ret}")
        return False
    return True

def set_gpio_dir(gpio: int, gpio_dir_in: bool):
    if not is_gpio_device():
        logger.warning(f"GPIO: set_gpio_dir No GPIO Device")
        return False
    gpio_path = GPIO_PATH + f"/gpio{gpio}"
    if not path_exists(gpio_path):
        # Init nicht erfolgreich ? gpio Pfad wurde nicht angelegt vom OS
        logger.error(f"GPIO: set_gpio_dir() 2 > Path doesn't exists {gpio_path}")
        return False
    gpio_direction = {
        True: 'in',
        False: 'out',
    }.get(gpio_dir_in, 'out')
    os_cmd = f"echo {gpio_direction} > {gpio_path}/direction"
    try:
        ret = os.system(os_cmd)
    except TypeError:
        logger.error(f"GPIO: set_gpio_dir TypeError: {os_cmd}")
        return False
    if ret:
        logger.error(f"GPIO: set_gpio_dir() 3 > {ret}")
        return False
    return True

def setup_gpio(gpio: int):
    if not is_gpio_device():
        logger.warning(f"GPIO: setup_gpio No GPIO Device")
        return False
    if is_gpio_init(gpio):
        # Bereits aktiviert
        logger.warning(f"GPIO: setup_gpio() > {gpio} bereits initialisiert.")
        return True
    os_cmd = f"echo {gpio} > {GPIO_PATH}/export"
    try:
        ret = os.system(os_cmd)
    except TypeError:
        logger.error(f"GPIO: setup_gpio TypeError: {os_cmd}")
        return False
    if ret:
        logger.error(f"GPIO: setup_gpio() 1 > {ret}")
        return False
    gpio_path = GPIO_PATH + f"/gpio{gpio}"
    if not path_exists(gpio_path):
        # Init nicht erfolgreich ? gpio Pfad wurde nicht angelegt vom OS
        logger.error(f"GPIO: setup_gpio() 2 > Path doesn't exists {gpio_path}")
        return False
    return True

def get_gpio_dir(gpio: int):
    if not is_gpio_device():
        logger.warning(f"GPIO: get_gpio_dir No GPIO Device")
        return None
    if not is_gpio_init(gpio):
        logger.warning(f"GPIO: get_gpio_dir() 1 > GPIO {gpio} nicht initialisiert !")
        return None
    gpio_path = GPIO_PATH + f"/gpio{gpio}"
    os_cmd = f"cat {gpio_path}/direction"
    try:
        return os.popen(os_cmd).read()[:-1]
    except TypeError:
        logger.error(f"GPIO: get_gpio_dir TypeError: {os_cmd}")
        return None

def get_gpio_val(gpio: int):
    if not is_gpio_device():
        logger.warning(f"GPIO: get_gpio_val No GPIO Device")
        return None
    if not is_gpio_init(gpio):
        logger.warning(f"GPIO: get_gpio_val() 1 > GPIO {gpio} nicht initialisiert !")
        return None
    gpio_path = GPIO_PATH + f"/gpio{gpio}"
    os_cmd = f"cat {gpio_path}/value"
    try:
        ret = os.popen(os_cmd).read()
    except TypeError:
        logger.error(f"GPIO: get_gpio_val TypeError: {os_cmd}")
        return None
    try:
        return bool(int(ret))
    except ValueError:
        logger.error(f"GPIO: get_gpio_val ValueError os.popen: {ret}")
        return None

def set_gpio_val(gpio: int, value: bool):
    if not is_gpio_device():
        logger.warning(f"GPIO: set_gpio_val No GPIO Device")
        return False
    if not is_gpio_init(gpio):
        logger.warning(f"GPIO: set_gpio_val() 1 > GPIO {gpio} nicht initialisiert !")
        return False
    if get_gpio_dir(gpio) == 'in':
        logger.warning(f"GPIO: set_gpio_val() 1 > GPIO {gpio} ist nicht als Ausgang konfiguriert!")
        return False
    gpio_path = GPIO_PATH + f"/gpio{gpio}"
    os_cmd = f"echo {int(value)} > {gpio_path}/value"
    try:
        ret = os.system(os_cmd)
    except TypeError:
        logger.error(f"GPIO: set_gpio_val TypeError: {os_cmd}")
        return False
    if ret:
        logger.error(f"GPIO: set_gpio_val() 1 > {ret}")
        return False
    return True

"""
for pin in range(0, 27):
    set_gpio_val(pin, False)

for pin in range(0, 27):
    setup_gpio(pin)

for pin in range(0, 27):
    set_gpio_dir(pin, False)

for pin in range(0, 27):
    close_gpio(pin)
    
for pin in range(0, 27):
    is_gpio_init(pin)

klick = True
while True:
    try:
        for pin in range(1, 27):
            set_gpio_val(pin, klick)
    except KeyboardInterrupt:
        break
    time.sleep(0.5)
    klick = not klick
        
"""



