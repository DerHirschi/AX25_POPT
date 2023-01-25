"""
    Layer 3 ??
    AX.25 Packet Handlink
"""
from ax25dec_enc import AX25Frame, reverse_uid, DecodingERROR, EncodingERROR
from config_station import DefaultStationConfig

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class AX25Conn(object):
    def __init__(self, ax25_frame: AX25Frame, cfg: DefaultStationConfig, rx=True):
        print("AX25CONN")
        self.rx = rx
        if rx:
            self.address_str_id = ax25_frame.addr_uid               # Unique ID for Connection
        else:
            ax25_frame.encode()                                 # Make sure outgoing Packet is encoded
            self.address_str_id = reverse_uid(ax25_frame.addr_uid)  # Unique ID for Connection
        self.my_call = ax25_frame.to_call
        self.to_call = ax25_frame.from_call
        self.via_calls = ax25_frame.via_calls
        # self.rx_buf: [AX25Frame] = []
        self.tx_buf: [AX25Frame] = []
        """ Port Variablen"""
        self.vs = 0
        self.vr = 0
        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        self.n2 = 1
        self.zustand_tab = {
            self.S1Frei.index: self.S1Frei
        }
        self.zustand_exec = self.zustand_tab[1]()
        """ Port Parameter """
        self.parm_PacLen = cfg.parm_PacLen      # Max Pac len
        self.parm_MaxFrame = cfg.parm_MaxFrame  # Max (I) Frames
        self.parm_TXD = cfg.parm_TXD            # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
        self.parm_T0 = cfg.parm_T0              # T0 (Response Delay Timer) activated if data come in to prev resp to early
        self.parm_T2 = cfg.parm_T2              # T2 (Response Delay Timer) Default: 2888 / (parm_baud / 100)
        self.parm_T3 = cfg.parm_T3              # T3 (Inactive Link Timer)
        self.parm_N2 = cfg.parm_N2              # Max Try   Default 20
        self.parm_baud = cfg.parm_baud          # Baud for calculating Timer
        self.calc_T2 = self.parm_T2 / (self.parm_baud / 100)
        # Initial-Round-Trip-Time (Auto Parm) (bei DAMA wird T2*2 genommen)/NO DAMA YET
        self.parm_IRTT = (self.parm_T2 + self.parm_TXD) * 2

        if self.rx:
            self.handle_rx(ax25_frame)
        else:
            self.handle_tx(ax25_frame)

    def handle_rx(self, ax25_frame: AX25Frame):
        self.zustand_exec.rx(ax25_frame=ax25_frame)

    def handle_tx(self, ax25_frame: AX25Frame):
        self.zustand_exec.tx(ax25_frame=ax25_frame)

    class DefaultStat(object):
        flag = 'FREI'
        index = 0

        def rx(self, ax25_frame: AX25Frame):
            pass

        def tx(self, ax25_frame: AX25Frame):
            pass

    class S1Frei(DefaultStat):
        """
        I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
        DM            | DM    |       | DM    |        | DM     |         | UA,S5 3)| DM 4)
        """
        flag = 'FREI'
        index = 1

        def rx(self, ax25_frame: AX25Frame):
            flag = ax25_frame.ctl_byte.flag
            if flag == 'SABM':
                # Send UA

                print('UA')
            elif ax25_frame.ctl_byte.pf and flag in ['RR', 'REJ', 'SREJ', 'RNR']:
                # Send DM and Del me
                print('DM')

