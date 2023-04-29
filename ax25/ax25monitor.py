from ax25.ax25dec_enc import AX25Frame
from datetime import datetime

import logging
# Enable logging
"""
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
"""
logger = logging.getLogger(__name__)


def get_call_str(call, ssid=0):
    if ssid:
        return call + '-' + str(ssid)
    else:
        return call


class Monitor(object):  # TODO: Static
    """
    CB24: fm DX0SAW to APDW17 ctl UI pid=F0(Text) len 100 20:24:38
    CB24: fm DX0SAW to MD2SAW via DNX527 CB0SAW ctl I00^ pid=F0(Text) len 86 01:44:27

    """
    def __init__(self):
        self.out_buf = []

    def frame_inp(self, ax25_frame: AX25Frame, port_name='DW'):
        from_call = get_call_str(ax25_frame.from_call.call, ax25_frame.from_call.ssid)
        to_call = get_call_str(ax25_frame.to_call.call, ax25_frame.to_call.ssid)
        via_calls = []
        for stat in ax25_frame.via_calls:
            # stat: Call
            call_str = get_call_str(stat.call, stat.ssid)
            if stat.c_bit:
                call_str += '*'
            via_calls.append(call_str)

        out_str = '{} {}: {} to {}'.format(port_name, datetime.now().strftime('%H:%M:%S'), from_call, to_call)
        if via_calls:
            out_str += ' via'
            for st in via_calls:
                out_str += ' {}'.format(st)
        if ax25_frame.ctl_byte.cmd:
            out_str += ' cmd'
        else:
            out_str += ' rpt'
        out_str += ' ({}) {}'.format(ax25_frame.ctl_byte.hex, ax25_frame.ctl_byte.mon_str)
        if int(ax25_frame.pid_byte.hex):
            out_str += ' pid={}({})'.format(hex(ax25_frame.pid_byte.hex), ax25_frame.pid_byte.flag)
        if ax25_frame.data_len:
            out_str += ' len {}\n'.format(ax25_frame.data_len)
        else:
            out_str += '\n'
        # now = datetime.now()  # current date and time
        # out_str += ' {}'.format(now.strftime('%d/%m/%Y %H:%M:%S'))
        # out_str += ' {}\n'.format(now.strftime('%H:%M:%S'))
        if ax25_frame.data:
            data = ax25_frame.data.decode('UTF-8', 'ignore')
            data = data.replace('\r', '\n').replace('\r\n', '\n').replace('\n\r', '\n')
            data = data.split('\n')
            for da in data:
                while len(da) > 100:
                    out_str += da[:100] + '\n'
                    da = da[100:]
                if da:
                    if da[-1] != '\n' or da[-1] != '\r':
                        out_str += da + '\n'
        logger.debug(out_str)
        self.out_buf.append(out_str)
        return out_str
