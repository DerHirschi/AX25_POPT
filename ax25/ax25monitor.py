from ax25.ax25NetRom import NetRom_decode_UI_mon, NetRom_decode_I_mon
from cfg.logger_config import logger
# from ax25.ax25NetRom import NetRom_decode_I
from ax25aprs.aprs_dec import format_aprs_f_monitor
from cfg.constant import ENCODINGS, PARAM_MAX_MON_WIDTH
from UserDB.UserDBmain import USER_DB
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import try_decode


def monitor_frame_inp(ax25_frame_conf: dict, mon_cfg: dict):
    """
    mon_cfg     = {
        "port_name": '',
        "distance" : False,
        "aprs_dec" : False,
        "nr_dec"   : False,
        "hex_out"  : False,
        "decoding" : 'Auto',
    }
    """

    port_name    = mon_cfg.get('port_name', '')
    dec_distance = mon_cfg.get('distance' , True)
    dec_aprs     = mon_cfg.get('aprs_dec' , True)
    dec_nr       = mon_cfg.get('nr_dec'   , True)
    hex_out      = mon_cfg.get('hex_out'  , True)
    decoding     = mon_cfg.get('decoding' , 'Auto')

    # port_name   = port_cfg.get('parm_PortName', '')
    own_loc     = POPT_CFG.get_guiCFG_locator()

    hex_str     = ''
    aprs_data   = ''
    ctl_flag    = ax25_frame_conf.get('ctl_flag', '')
    ctl_cmd     = ax25_frame_conf.get('ctl_cmd', '')
    ctl_hex     = ax25_frame_conf.get('ctl_hex', '')
    ctl_mon_str = ax25_frame_conf.get('ctl_mon_str', '')
    pid_flag    = ax25_frame_conf.get('pid_flag', '')
    pid_hex     = ax25_frame_conf.get('pid_hex', '')
    from_call   = ax25_frame_conf.get('from_call_str', '')
    to_call     = ax25_frame_conf.get('to_call_str', '')
    rx_time     = ax25_frame_conf.get('rx_time')
    payload_len = ax25_frame_conf.get('payload_len', 0)
    payload     = ax25_frame_conf.get('payload', b'')
    netrom_cfg  = ax25_frame_conf.get('netrom_cfg', {})
    # APRS
    if ctl_flag == 'UI' and dec_aprs:
        aprs_data = format_aprs_f_monitor(ax25_frame_conf, own_locator=own_loc)
    # Distance
    if dec_distance:
        from_call_d = round(USER_DB.get_distance(from_call))
        if from_call_d:
            from_call += f"({from_call_d} km)"
        to_call_d = round(USER_DB.get_distance(to_call))
        if to_call_d:
            to_call += f"({to_call_d} km)"

    via_calls = []
    for call_str, c_bit in ax25_frame_conf.get('via_calls_str_c_bit', []):
        if dec_distance:
            dist = round(USER_DB.get_distance(call_str))
            dist = f"({dist} km)" if dist else ''
        else:
            dist = ''
        via_calls.append(call_str + '*' + dist) if c_bit else via_calls.append(call_str + dist)

    ############################
    out_str = f"{port_name} {rx_time.strftime('%H:%M:%S')}: {from_call} to {to_call}"
    out_str += ' via ' + ' '.join(via_calls) if via_calls else ''
    out_str += ' cmd' if ctl_cmd else ' rpt'
    # out_str += f' ({ax25_frame.ctl_byte.hex}) {ax25_frame.ctl_byte.mon_str}'
    out_str += f' {ctl_mon_str}'
    out_str += f'\n   ├─▶ ctl={ctl_hex} pid={pid_hex}({pid_flag})'\
        if int(pid_hex, 16) else ''
    out_str += ' len={}\n'.format(payload_len) if payload_len else '\n'
    # Hex
    if hex_out:
        try:
            hex_str = ax25_frame_conf.get('ax25_raw', b'').hex()
        except Exception as e:
            logger.error(f"ax25monitor.py> decoding to hex Error: {e}")
    if hex_str:
        out_str += "┌──┴─▶ HEX:\n"
        while len(hex_str) > PARAM_MAX_MON_WIDTH:
            out_str += f"├►{str(hex_str[:PARAM_MAX_MON_WIDTH])}\n"
            hex_str = hex_str[PARAM_MAX_MON_WIDTH:]
        if hex_str:
            if not out_str.endswith('\n'):
                out_str += '\n'
        if any((netrom_cfg,
                payload)):
            if hex_str:
                out_str += f"├►{str(hex_str)}\n"
            out_str +=  "└──┐\n"
        else:
            if hex_str:
                out_str += f"└►{str(hex_str)}\n"



    # NetRom
    if netrom_cfg and dec_nr:  # Net-Rom
        if ctl_flag == 'UI':
            data = NetRom_decode_UI_mon(netrom_cfg=netrom_cfg)
            out_str += data
            if not out_str.endswith('\n'):
                out_str += '\n'
            return out_str

        if ctl_flag == 'I' and pid_hex == '0xcf':
            data    = NetRom_decode_I_mon(netrom_cfg)
            out_str += data
            if not out_str.endswith('\n'):
                out_str += '\n'
            return out_str

    if payload:
        if type(payload) is bytes:
            if netrom_cfg:
                payload = f'NET/ROM: <BIN> {payload_len} Bytes'
                decoding = ''
            elif decoding == 'Auto':
                payload = try_decode(payload)
            else:
                if decoding in ENCODINGS:
                    try:
                        payload = payload.decode(decoding)
                    except UnicodeDecodeError:
                        decoding = 'UnicodeDecodeError'
                        payload = f'<BIN> {payload_len} Bytes'
            out_str += f"┌──┴─▶ Payload ({decoding}):\n" if decoding else "┌──┴─▶Payload:\n"

            payload       = payload.replace('\r', '\n')
            payload_lines = payload.split('\n')
            while '' in payload_lines:
                payload_lines.remove('')
            l_i = len(payload_lines)
            for line in payload_lines:
                while len(line) > PARAM_MAX_MON_WIDTH:
                    out_str += f"├►{str(line[:PARAM_MAX_MON_WIDTH])}\n"
                    line = line[PARAM_MAX_MON_WIDTH:]
                l_i -= 1
                if line:
                    if not l_i and not aprs_data:
                        out_str += f"└►{str(line)}\n"
                    else:
                        out_str += f"├►{str(line)}\n"
            if aprs_data:
                out_str += "└──┐\n"

    if not out_str.endswith('\n'):
        out_str += '\n'
    if dec_aprs and aprs_data:
        out_str += aprs_data
        if not out_str.endswith('\n'):
            out_str += '\n'
    return out_str


