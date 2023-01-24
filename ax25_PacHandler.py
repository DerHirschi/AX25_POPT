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


class AX25L3Conn(object):
    def __init__(self):
        self.ax25_frame: AX25Frame
        self.own_call = Call()
        self.dest_call = Call()
        self.via_call = []
        self.call_obj = Call()

        self.address_str_id = ''    # Unique ID for Connection
        self.vs = 0
        self.vr = 0

        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        self.n2 = 1

