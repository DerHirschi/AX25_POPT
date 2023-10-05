from datetime import datetime

from fnc.str_fnc import conv_time_for_key


def get_dx_tx_alarm_his_pack(
        port_id: int,
        call_str: str,
        via: str,
        path: list,
        locator: str,
        distance: float,
        typ: str,
):
    _now = datetime.now()
    return {
        'ts': _now,
        'port_id': port_id,
        'call_str': call_str,
        'via': via,
        'path': path,
        'loc': locator,
        'dist': distance,
        'typ': typ,
        'key': f"{conv_time_for_key(_now)}{call_str}",

    }


def get_bandwidth_struct():
    _struct = {}
    for _h in range(24):
        for _m in range(60):
            for _s in range(6):
                _ts_str = f'{str(_h).zfill(2)}:{str(_m).zfill(2)}:{_s}'
                _struct[_ts_str] = 0
    return _struct


def get_port_stat_struct():
    struct_hour = {}
    for key in [
        'N_pack',
        'I',
        'SABM',
        'DM',
        'DISC',
        'REJ',
        'RR',
        'RNR',
        'UI',
        'FRMR',
        'DATA_W_HEADER',
        'DATA'
    ]:
        struct_hour[key] = {minute: 0 for minute in range(60)}
    return struct_hour


def init_day_dic():

    ret = {}
    for hour in range(24):
        ret[hour] = get_port_stat_struct()
    return ret
