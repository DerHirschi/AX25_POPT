#from ax25.ax25NetRom import NetRom_decode_I, NetRom_decode_UI_mon
# import logging
# from ax25.ax25NetRom import NetRom_decode_I
from ax25aprs.aprs_dec import format_aprs_f_monitor
from cfg.constant import ENCODINGS
from UserDB.UserDBmain import USER_DB
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import try_decode


def monitor_frame_inp(ax25_frame_conf: dict, port_cfg, decoding='Auto'):
    port_name = port_cfg.parm_PortName
    guiCfg = POPT_CFG.load_guiPARM_main()
    own_loc = guiCfg.get('gui_cfg_locator', '')

    # own_loc = port_cfg.parm_aprs_station.get('aprs_parm_loc', '')
    aprs_data = ''
    ctl_flag = ax25_frame_conf.get('ctl_flag', '')
    ctl_cmd = ax25_frame_conf.get('ctl_cmd', '')
    ctl_hex = ax25_frame_conf.get('ctl_hex', '')
    ctl_mon_str = ax25_frame_conf.get('ctl_mon_str', '')
    pid_flag = ax25_frame_conf.get('pid_flag', '')
    pid_hex = ax25_frame_conf.get('pid_hex', '')
    from_call = ax25_frame_conf.get('from_call_str', '')
    to_call = ax25_frame_conf.get('to_call_str', '')
    rx_time = ax25_frame_conf.get('rx_time')
    payload_len = ax25_frame_conf.get('payload_len', 0)
    payload = ax25_frame_conf.get('payload', b'')
    # netrom_cfg = ax25_frame_conf.get('netrom_cfg', {})
    if ctl_flag == 'UI':
        aprs_data = format_aprs_f_monitor(ax25_frame_conf, own_locator=own_loc)

    from_call_d = round(USER_DB.get_distance(from_call))
    if from_call_d:
        from_call += f"({from_call_d} km)"
    to_call_d = round(USER_DB.get_distance(to_call))
    if to_call_d:
        to_call += f"({to_call_d} km)"

    via_calls = []
    for call_str, c_bit in ax25_frame_conf.get('via_calls_str_c_bit', []):
        dist = round(USER_DB.get_distance(call_str))
        if dist:
            dist = f"({dist} km)"
        else:
            dist = ''
        if c_bit:
            via_calls.append(call_str + '*' + dist)
        else:
            via_calls.append(call_str + dist)

    out_str = f"{port_name} {rx_time.strftime('%H:%M:%S')}: {from_call} to {to_call}"
    out_str += ' via ' + ' '.join(via_calls) if via_calls else ''
    out_str += ' cmd' if ctl_cmd else ' rpt'
    # out_str += f' ({ax25_frame.ctl_byte.hex}) {ax25_frame.ctl_byte.mon_str}'
    out_str += f' {ctl_mon_str}'
    out_str += f'\n   ├──────▶: ctl={ctl_hex} pid={pid_hex}({pid_flag})'\
        if int(pid_hex, 16) else ''
    out_str += ' len={}\n'.format(payload_len) if payload_len else '\n'
    # ======= Old NetRom
    """
    if netrom_cfg:  # Net-Rom
        if ctl_flag == 'UI':
            data = NetRom_decode_UI_mon(ax25_frame_conf)
            out_str += data
            return out_str, aprs_data
    """
    # ======= DEV Inp-NetRom/L3-NetRom TODO move decoding call to ax25ecn_dec
    """
    if ctl_flag == 'I' and pid_hex == '0xcf':
        data = NetRom_decode_I(payload)
        out_str += data
        return out_str, aprs_data
    """
    # if payload:
    if type(payload) is bytes:
        if decoding == 'Auto':
            payload = try_decode(payload)
        else:
            if decoding in ENCODINGS:
                try:
                    payload = payload.decode(decoding)
                except UnicodeDecodeError:
                    payload = f'<BIN> {payload_len} Bytes'
        """
        else:
            print(f"Monitor decode Data == STR: {payload} - {from_call} - {ctl_flag}")
        """
        payload = payload.replace('\r', '\n')
        payload_lines = payload.split('\n')
        for line in payload_lines:
            while len(line) > 100:
                out_str += str(line[:100]) + '\n'
                line = line[100:]
            if line:
                if line[-1] != '\n':
                    out_str += str(line) + '\n'

        # if ax25_frame.ctl_byte.flag == 'UI':
        # out_str += aprs_data
    return out_str, aprs_data


