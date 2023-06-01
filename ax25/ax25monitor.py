from datetime import datetime
import logging

from ax25aprs.aprs_dec import format_aprs_f_monitor
from fnc.ax25_fnc import get_call_str

logger = logging.getLogger(__name__)


def monitor_frame_inp(ax25_frame, port_cfg):
    port_name = port_cfg.parm_PortName
    from_call = get_call_str(ax25_frame.from_call.call, ax25_frame.from_call.ssid)
    to_call = get_call_str(ax25_frame.to_call.call, ax25_frame.to_call.ssid)
    via_calls = [get_call_str(stat.call, stat.ssid) + '*' if stat.c_bit else get_call_str(stat.call, stat.ssid) for
                 stat in ax25_frame.via_calls]

    out_str = '{} {}: {} to {}'.format(port_name, datetime.now().strftime('%H:%M:%S'), from_call, to_call)
    out_str += ' via ' + ' '.join(via_calls) if via_calls else ''
    out_str += ' cmd' if ax25_frame.ctl_byte.cmd else ' rpt'
    out_str += ' ({}) {}'.format(ax25_frame.ctl_byte.hex, ax25_frame.ctl_byte.mon_str)
    out_str += ' pid={}({})'.format(hex(ax25_frame.pid_byte.hex), ax25_frame.pid_byte.flag) if int(
        ax25_frame.pid_byte.hex) else ''
    out_str += ' len {}\n'.format(ax25_frame.data_len) if ax25_frame.data_len else '\n'

    if ax25_frame.data:
        try:
            data = ax25_frame.data.decode('ASCII')
        except UnicodeDecodeError:
            data = f'<BIN> {len(ax25_frame.data)} Bytes'
        data = data.replace('\r\n', '\n').replace('\n\r', '\n').replace('\r', '\n')
        data = data.split('\n')
        for da in data:
            while len(da) > 80:
                out_str += da[:80] + '\n'
                da = da[80:]
            if da:
                if da[-1] != '\n' or da[-1] != '\r':
                    out_str += da + '\n'

        if ax25_frame.ctl_byte.flag == 'UI':
            out_str += format_aprs_f_monitor(ax25_frame, own_locator='JO52NU')
    return out_str


