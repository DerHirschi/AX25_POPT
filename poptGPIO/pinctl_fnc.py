import os
from cfg.logger_config import logger
LOGGER_TAG = 'PINCTRL: '

def is_pinctrl_device():
    os_cmd = 'pinctrl > /dev/null 2>& 1'
    try:
        ret = os.system(os_cmd)
    except TypeError:
        return False
    if ret:
        return False
    return True

def set_pinctrl_dir(gpio: int, gpio_dir_in: bool):
    if not is_pinctrl_device():
        logger.warning(LOGGER_TAG + f"set_pinctrl_dir No PINCTRL Device")
        return False
    gpio_direction = {
        True: 'ip',
        False: 'op',
    }.get(gpio_dir_in, 'op')

    os_cmd = f"pinctrl set {gpio} {gpio_direction}"
    try:
        ret = os.system(os_cmd)
    except TypeError:
        return False
    if ret:
        return False
    return True

def set_pinctrl_val(gpio: int, value: bool):
    if not is_pinctrl_device():
        # logger.warning(LOGGER_TAG + f"set_pinctrl_val No PINCTRL Device")
        return False
    # TODO Check Direction
    gpio_direction = {True: 'dh', False: 'dl', }.get(value, 'dl')
    os_cmd = f"pinctrl set {gpio} {gpio_direction}"
    try:
        ret = os.system(os_cmd)
    except TypeError:
        return False
    if ret:
        return False
    return True


def get_pinctrl_pin_info(gpio: int):
    if not is_pinctrl_device():
        # logger.warning(LOGGER_TAG + f"set_pinctrl_val No PINCTRL Device")
        return None
    os_cmd = f"pinctrl get {gpio}"
    try:
        ret = os.popen(os_cmd).read()
    except TypeError:
        return None
    if not ret:
        return None
    tmp = ret.split(':')
    try:
        tmp_gpio = int(tmp[0])
    except (IndexError, ValueError):
        return None
    if tmp_gpio != gpio:
        return None
    try:
        tmp_dir, tmp_val = tmp[1].split('|')
    except ValueError:
        return None
    tmp_val = tmp_val.split('//')[0][1:-1]
    tmp_opt = tmp_dir[-3:-1]
    tmp_dir = tmp_dir[1:3]

    pin_dir = { 'ip': 'in', 'op': 'out'}.get(tmp_dir, None)
    pin_val = { 'hi': True, 'lo': False}.get(tmp_val, None)
    if any((pin_dir is None, pin_val is None)):
        logger.error(LOGGER_TAG + f"get_pinctrl_pin_info() - val: {pin_val}, dir: {pin_dir}, os_cmf: {os_cmd}")
        return None
    return pin_val, pin_dir, tmp_opt

def get_pinctrl_val(gpio: int):
    if not is_pinctrl_device():
        logger.warning(LOGGER_TAG + "get_pinctrl_val No GPIO Device")
        return None
    tmp = get_pinctrl_pin_info(gpio)
    if tmp is None:
        return None
    return bool(tmp[0])

def get_pinctrl_dir(gpio: int):
    if not is_pinctrl_device():
        logger.warning(LOGGER_TAG + "get_pinctrl_dir No GPIO Device")
        return None
    tmp = get_pinctrl_pin_info(gpio)
    if tmp is None:
        return None
    return str(tmp[1])

