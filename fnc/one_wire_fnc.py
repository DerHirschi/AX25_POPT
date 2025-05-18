from cfg.constant import ONE_WIRE_PATH
from fnc.file_fnc import get_str_fm_file
from fnc.os_fnc import is_linux, path_exists


def is_1wire_device():
    if not is_linux():
        return False
    return path_exists(ONE_WIRE_PATH)

def get_all_1wire_paths():
    wire_dev = get_str_fm_file(ONE_WIRE_PATH + '/w1_master_slaves').split('\n')[:-1]
    if not wire_dev:
        return []
    return wire_dev

def get_max_1wire():
    try:
        return int(get_str_fm_file(ONE_WIRE_PATH + '/w1_master_max_slave_count').split('\n')[0])
    except (ValueError, IndexError, AttributeError, TypeError):
        return 0

def get_1wire_timeout():
    try:
        return int(get_str_fm_file(ONE_WIRE_PATH + '/w1_master_timeout').split('\n')[0])
    except (ValueError, IndexError, AttributeError, TypeError):
        return 0


def get_1wire_temperature(device_path: str):
    if not is_1wire_device():
        return ()
    try:
        tempData = int(get_str_fm_file(f'{ONE_WIRE_PATH}/{device_path}/temperature').split('\n')[0])
    except (ValueError, IndexError, AttributeError, TypeError):
        return ()

    """Source: https://st-page.de/2018/01/20/tutorial-raspberry-pi-temperaturmessung-mit-ds18b20/"""
    tempCelsius = round(float(tempData) / 1000, 1)
    # tempKelvin = 273 + float(tempData) / 1000
    tempFahrenheit = round(float(tempData) / 1000 * 9.0 / 5.0 + 32.0, 1)
    return float(tempCelsius), float(tempFahrenheit)

