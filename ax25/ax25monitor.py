from datetime import datetime
# import logging

from ax25aprs.aprs_dec import format_aprs_f_monitor
from fnc.ax25_fnc import get_call_str
from UserDB.UserDBmain import USER_DB

# logger = logging.getLogger(__name__)


def monitor_frame_inp(ax25_frame, port_cfg):
    port_name = port_cfg.parm_PortName
    aprs_loc = port_cfg.parm_aprs_station.get('aprs_parm_loc', '')
    aprs_data = ''
    if ax25_frame.ctl_byte.flag == 'UI':
        aprs_data = format_aprs_f_monitor(ax25_frame, own_locator=aprs_loc)

    from_call = get_call_str(ax25_frame.from_call.call, ax25_frame.from_call.ssid)
    from_call_d = round(USER_DB.get_distance(from_call))
    if from_call_d:
        from_call += f"({from_call_d} km)"
    to_call = get_call_str(ax25_frame.to_call.call, ax25_frame.to_call.ssid)
    to_call_d = round(USER_DB.get_distance(to_call))
    if to_call_d:
        to_call += f"({to_call_d} km)"
    """
    via_calls = [get_call_str(stat.call, stat.ssid) + '*' if stat.c_bit else get_call_str(stat.call, stat.ssid) for
                 stat in ax25_frame.via_calls]
    """
    via_calls = []
    for stat in ax25_frame.via_calls:
        dist = round(USER_DB.get_distance(get_call_str(stat.call, stat.ssid)))
        if dist:
            dist = f"({dist} km)"
        else:
            dist = ''
        if stat.c_bit:
            via_calls.append(get_call_str(stat.call, stat.ssid) + '*' + dist)
        else:
            via_calls.append(get_call_str(stat.call, stat.ssid) + dist)

    out_str = f"{port_name} {datetime.now().strftime('%H:%M:%S')}: {from_call} to {to_call}"
    out_str += ' via ' + ' '.join(via_calls) if via_calls else ''
    out_str += ' cmd' if ax25_frame.ctl_byte.cmd else ' rpt'
    # out_str += f' ({ax25_frame.ctl_byte.hex}) {ax25_frame.ctl_byte.mon_str}'
    out_str += f' {ax25_frame.ctl_byte.mon_str}'
    out_str += f'\n   ├──────▶: ctl={ax25_frame.ctl_byte.hex} pid={hex(ax25_frame.pid_byte.hex)}({ax25_frame.pid_byte.flag})'\
        if int(ax25_frame.pid_byte.hex) else ''
    out_str += ' len={}\n'.format(ax25_frame.data_len) if ax25_frame.data_len else '\n'

    if ax25_frame.data:
        data = ax25_frame.data
        if type(ax25_frame.data) == bytes:
            try:
                data = ax25_frame.data.decode('ASCII')
            except UnicodeDecodeError:
                data = f'<BIN> {len(ax25_frame.data)} Bytes'
        else:
            print(f"Monitor decode Data == STR: {data} - {ax25_frame.from_call.call_str} - {ax25_frame.ctl_byte.flag}")
        data = data.replace('\r\n', '\n').replace('\n\r', '\n').replace('\r', '\n')
        data = data.split('\n')
        for da in data:
            while len(da) > 80:
                out_str += da[:80] + '\n'
                da = da[80:]
            if da:
                if da[-1] != '\n' or da[-1] != '\r':
                    out_str += da + '\n'

        # if ax25_frame.ctl_byte.flag == 'UI':
        # out_str += aprs_data
    return out_str, aprs_data


