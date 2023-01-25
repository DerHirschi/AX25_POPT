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
        self.rx_buf = ax25_frame
        self.tx_buf: [AX25Frame] = []
        """ Port Variablen"""
        self.vs = 0
        self.vr = 0
        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        self.n2 = 1
        self.zustand_tab = {
            S1Frei.index: S1Frei,
            S5InfoReady.index: S5InfoReady
        }
        self.zustand_exec = self.zustand_tab[1](self)
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
        self.rx_buf = ax25_frame
        self.zustand_exec.rx(ax25_frame=ax25_frame)

    def handle_tx(self, ax25_frame: AX25Frame):
        self.zustand_exec.tx(ax25_frame=ax25_frame)

    def build_tx_frame(self):
        frame = AX25Frame()
        frame.to_call = self.rx_buf.from_call
        frame.from_call = self.rx_buf.to_call
        frame.via_calls = self.rx_buf.via_calls
        if frame.via_calls:
            frame.via_calls.reverse()
        frame.set_stop_bit()
        frame.ctl_byte.pf = self.rx_buf.ctl_byte.pf
        return frame

    def send_UA(self):
        pac = self.build_tx_frame()
        pac.ctl_byte.UAcByte()
        pac.encode()
        self.tx_buf.append(pac)

    def send_DM(self):
        pac = self.build_tx_frame()
        pac.ctl_byte.DMcByte()
        pac.encode()
        self.tx_buf.append(pac)


class DefaultStat(object):
    index = 0

    def __init__(self, ax25_conn: AX25Conn):
        self.ax25conn = ax25_conn
        self.flag = {
            0: '',
            1: 'FREI',
            5: 'Info.-Übertrag.',
        }[self.index]

    def change_state(self, zustand_id=1):
        self.ax25conn.zustand_exec = self.ax25conn.zustand_tab[zustand_id](self.ax25conn)

    def rx(self, ax25_frame: AX25Frame):
        pass

    def tx(self, ax25_frame: AX25Frame):
        pass

    def crone(self):
        pass


class S1Frei(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    DM            | DM    |       | DM    |        | DM     |         | UA,S5 3)| DM 4)
    """
    index = 1

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag == 'SABM':
            self.ax25conn.send_UA()
            self.change_state(5)
            print('UA')
        elif ax25_frame.ctl_byte.pf and flag in ['RR', 'REJ', 'SREJ', 'RNR']:
            self.ax25conn.send_DM()
            print('DM')


class S5InfoReady(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    RR    | I/RR 1)| RR   | I/- 2)| RR    | I      | RR,S9  | S9      | UA      | UA,S1
    """
    index = 5

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag == 'SABM':
            self.ax25conn.send_UA()
            print('UA')
        elif flag == 'DISC':
            self.ax25conn.send_UA()
            self.change_state(1)
            print('DISC')

