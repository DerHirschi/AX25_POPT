"""
    Layer 3 ??
    AX.25 Packet Handlink
"""
from ax25dec_enc import AX25Frame, Call
import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

MYCALL_call = 'MD5SAW'
MYCALL_ssid = 0
MYCALL_str = 0


class AX25L3Conn(object):
    def __init__(self, ax25_frame: AX25Frame):
        self.ax25_frame = ax25_frame
        self.own_call = ax25_frame.to_call
        self.dest_call = ax25_frame.from_call
        self.via_call = ax25_frame.via_calls

        self.address_str_id = ''    # Unique ID for Connection
        self.vs = 0
        self.vr = 0

        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        self.n2 = 1


class DefaultPORTConfig(AX25L3Conn):
    pass


class MD5SAW(AX25L3Conn):
    pass
