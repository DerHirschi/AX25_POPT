def reverse_uid(inp=''):
    inp = inp.split(':')
    addr, via = inp[:2], inp[2:]
    addr.reverse()
    via.reverse()
    return ':'.join(addr + via)


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
            return ''
    if 0 > call_tuple[1] > 15:
        return ''
    return call_str


def get_list_fm_viaStr(via_str: str):
    via_list = via_str.split(' ')
    vias = []
    for call in via_list:
        if call:
            tmp_call = validate_call(call)
            if tmp_call:
                vias.append(tmp_call)
            else:
                return []
    return vias


def build_ax25uid(from_call_str,
                  to_call_str,
                  via_calls: [] = None,
                  dec=True):
    if via_calls is None:
        via_calls = []
    if not all((from_call_str, to_call_str)):
        return ''
    ax25_uid = f'{from_call_str}:{to_call_str}'
    for call in via_calls:
        ax25_uid += f':{call}'
    if not dec:
        ax25_uid = reverse_uid(ax25_uid)

    return ax25_uid

def validate_ax25Call(call_str: str):
    """
    :return: bool
    """
    if not call_str:
        return False
    if '-' in call_str:
        call, ssid = call_str.split('-')
    else:
        call = call_str
        ssid = '0'
    # SSID
    try:
        ssid = int(ssid)
    except ValueError:
        return False

    if ssid > 15 or ssid < 0:
        print(f'Call validator ax25_fnc: SSID - {ssid}')
        return False
    # CALL
    if len(call) < 2 or len(call) > 6:    # Calls like CQ or ID
        print(f'Call validator ax25_fnc: Call length - {call}')
        return False

    for c in call:
        if not any((c.isupper(), c.isdigit())):
            print(f'Call validator ax25_fnc: CAll-Format - {call} -')
            return False
    return True