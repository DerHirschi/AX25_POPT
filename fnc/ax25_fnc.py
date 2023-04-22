def reverse_uid(inp=''):
    inp = inp.split(':')
    addr, via, ret = inp[:2], inp[2:], ''
    addr.reverse()
    via.reverse()
    for el in addr:
        ret += el + ':'
    for el in via:
        ret += el + ':'
    return ret[:-1]


def get_call_wo_ssid(call: str):
    ind = call.find('-')
    if ind != -1:
        return call[:ind]
    else:
        return call


def get_call_str(call: str, ssid=0):
    if ssid:
        return call + '-' + str(ssid)
    else:
        return call


def call_tuple_fm_call_str(call_str: str):
    """
    Separates Call from SSID
    :param call_str:
    :return: tuple(str: call, int: ssid)
    """
    call_str = call_str.replace('\r', '').replace('\n', '').replace(' ', '')
    ind = call_str.find('-')
    if ind != -1:
        if call_str[ind + 1:].isdigit():
            return call_str[:ind].upper(), int(call_str[ind + 1:])
        else:
            return call_str.upper(), 0
    else:
        return call_str.upper(), 0


def validate_call(call_str: str):
    call_str = call_str.replace(' ', '').replace('\r', '').replace('\n', '')
    call_str = call_str.upper()
    call_tuple = call_tuple_fm_call_str(call_str)
    if 6 < len(call_tuple[0]) < 3:
        if not all(c.isnumeric() or c.isalpha() for c in call_tuple[0]):
            return False
    if 0 > call_tuple[1] > 15:
        return False
    return call_str
