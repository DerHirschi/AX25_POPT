from ax25dec_enc import AX25Frame
from datetime import datetime

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def get_call_str(call, ssid=0):
    if ssid:
        return call + '-' + str(ssid)
    else:
        return call


class Monitor(object):
    """
    CB24: fm DX0SAW to APDW17 ctl UI pid=F0(Text) len 100 20:24:38
    CB24: fm DX0SAW to MD2SAW via DNX527 CB0SAW ctl I00^ pid=F0(Text) len 86 01:44:27

    """
    def __init__(self):
        self.out_buf = []

    def frame_inp(self, axframe: AX25Frame, port_name='DW'):
        from_call = get_call_str(axframe.from_call.call, axframe.from_call.ssid)
        to_call = get_call_str(axframe.to_call.call, axframe.to_call.ssid)
        via_calls = []
        for stat in axframe.via_calls:
            # stat: Call
            call_str = get_call_str(stat.call, stat.ssid)
            if stat.c_bit:
                call_str += '*'
            via_calls.append(call_str)
        out_str = '{}-{}: {} to {}'.format(port_name, hex(axframe.kiss[-1]), from_call, to_call)
        if via_calls:
            out_str += ' via'
            for st in via_calls:
                out_str += ' {}'.format(st)
        if axframe.ctl_byte.cmd:
            out_str += ' cmd'
        else:
            out_str += ' rpt'
        out_str += ' ({}) {}'.format(axframe.ctl_byte.hex, axframe.ctl_byte.mon_str)
        out_str += ' pid={}({})'.format(hex(axframe.pid_byte.hex), axframe.pid_byte.flag)
        if axframe.data_len:
            out_str += ' len {}'.format(axframe.data_len)
        now = datetime.now()  # current date and time
        # out_str += ' {}'.format(now.strftime('%d/%m/%Y %H:%M:%S'))
        out_str += ' {}\n'.format(now.strftime('%H:%M:%S'))
        if axframe.data:
            data = axframe.data.decode('UTF-8', 'ignore')
            data = data.replace('\r', '\n').replace('\r\n', '\n').replace('\n\r', '\n')
            while len(data) > 100:
                out_str += data[:100] + '\n'
                data = data[100:]
            out_str += data + '\n'

        logger.info(out_str)
        self.out_buf.append(out_str)
