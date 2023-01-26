"""
    Layer 3 ??
    AX.25 Packet Handlink
"""
import time
from ax25dec_enc import AX25Frame, reverse_uid
from config_station import DefaultStationConfig
from cli import *

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def count_modulo(inp: int):
    return (inp + 1) % 8


class AX25Conn(object):
    def __init__(self, ax25_frame: AX25Frame, cfg: DefaultStationConfig, rx=True):
        self.rx = rx
        self.ax25_out_frame = AX25Frame()   # Predefined AX25 Frame for Output
        if rx:
            self.ax25_out_frame.addr_uid = reverse_uid(ax25_frame.addr_uid)   # Unique ID for Connection
            self.ax25_out_frame.to_call = ax25_frame.from_call
            self.ax25_out_frame.from_call = ax25_frame.to_call
            self.ax25_out_frame.via_calls = ax25_frame.via_calls
            self.ax25_out_frame.ctl_byte.pf = ax25_frame.ctl_byte.pf
            if self.ax25_out_frame.via_calls:
                self.ax25_out_frame.via_calls.reverse()
            self.ax25_out_frame.set_stop_bit()
        else:
            self.ax25_out_frame.addr_uid = reverse_uid(ax25_frame.addr_uid)  # Unique ID for Connection
            self.ax25_out_frame.to_call = ax25_frame.to_call
            self.ax25_out_frame.from_call = ax25_frame.from_call
            self.ax25_out_frame.via_calls = ax25_frame.via_calls
            ax25_frame.encode()     # Set Stop-Bits and H-Bits while encoding
            if self.ax25_out_frame.addr_uid != ax25_frame.addr_uid:
                logger.warning('Connection UID is different after encoding Packet !!')
                self.ax25_out_frame.addr_uid = ax25_frame.addr_uid  # Unique ID for Connection

        self.rx_buf = ax25_frame                # Buffers for last Frame !?!
        self.tx_buf_2send: [AX25Frame] = []     # Buffer for Sending. Will be processed in ax25PortHandler
        self.tx_buf_unACK: [AX25Frame] = []     # Buffer for UNACK I-Frames
        """
        # Buffer for UNACK I-Frames
        self.tx_buf_unACK: {
            0: AX25Frame,
            1: AX25Frame,
            2: AX25Frame,
            3: AX25Frame,
            4: AX25Frame,
            5: AX25Frame,
            6: AX25Frame,
            7: AX25Frame,
        } = {}  
        """
        self.tx_buf_rawData: b'' = b''          # Buffer for TX RAW Data that will be packed in a Frame
        """ Port Variablen"""
        self.vs = 0     # Sendefolgenummer     / N(S) gleich V(S)
        self.vr = 0     # Empfangsfolgezählers / N(R) gleich V(R)
        self.t0 = 0
        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        self.n2 = 0
        self.zustand_tab = {
            DefaultStat.stat_index: DefaultStat,
            S1Frei.stat_index: S1Frei,
            S5Ready.stat_index: S5Ready
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
        """ Port Parameter ENDE """
        """ CLI Parameter """
        self.cli = DefaultCLI()
        """ CLI Parameter ENDE """
        self.calc_T2 = self.parm_T2 / (self.parm_baud / 100)
        # Initial-Round-Trip-Time (Auto Parm) (bei DAMA wird T2*2 genommen)/NO DAMA YET
        self.calc_IRTT = (self.parm_T2 + self.parm_TXD) * 2

        if self.rx:
            self.handle_rx(ax25_frame)
        else:
            self.handle_tx(ax25_frame)

    def handle_rx(self, ax25_frame: AX25Frame):
        if ax25_frame.is_digipeated:
            self.rx_buf = ax25_frame
            self.zustand_exec.rx(ax25_frame=ax25_frame)

    def handle_tx(self, ax25_frame: AX25Frame):
        self.zustand_exec.tx(ax25_frame=ax25_frame)

    def exec_cron(self):
        """ DefaultStat.cron() """
        self.zustand_exec.cron()

    def exec_cli(self, inp=b''):
        """ CLI Processing like send C-Text ... """
        self.tx_buf_rawData += self.cli.cli_exec(inp)

    def init_new_ax25frame(self):
        pac = AX25Frame()
        pac.from_call = self.ax25_out_frame.from_call
        pac.to_call = self.ax25_out_frame.to_call
        pac.via_calls = self.ax25_out_frame.via_calls
        pac.addr_uid = self.ax25_out_frame.addr_uid
        self.ax25_out_frame = pac

    def send_UA(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.UAcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_DM(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.DMcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_I(self, pf_bit=False):
        """
        :param pf_bit: bool
        True if RX a REJ Packet
        """
        if self.tx_buf_rawData:         # Double Check, just in case
            self.init_new_ax25frame()
            pac = self.ax25_out_frame
            # pac = self.ax25_out_frame           # Get predefined Packet Structure
            pac.ctl_byte.pf = pf_bit            # Poll/Final Bit / True if REJ is received
            pac.ctl_byte.nr = int(self.vr)      # Receive PAC Counter
            pac.ctl_byte.ns = int(self.vs)      # Send PAC Counter
            pac.ctl_byte.IcByte()               # Set C-Byte
            pac.pid_byte.text()                 # Set PID-Byte to TEXT
            # PAYLOAD !!
            pac_len = min(self.parm_PacLen, len(self.tx_buf_rawData))
            pac.data = self.tx_buf_rawData[:pac_len]
            self.tx_buf_rawData = self.tx_buf_rawData[pac_len:]
            pac.encode()                        # Encoding the shit
            self.tx_buf_unACK.append(pac)       # Keep Packet until ACK/RR
            self.tx_buf_2send.append(pac)
            self.vs = count_modulo(self.vs)     # Increment VS Modulo 8


class DefaultStat(object):
    stat_index = 0  # ENDE

    def __init__(self, ax25_conn: AX25Conn):
        self.ax25conn = ax25_conn
        self.flag = {
            0: 'ENDE',          # If Stat 0 than Delete Connection
            1: 'FREI',          # Init State
            5: 'BEREIT',
        }[self.stat_index]

    def change_state(self, zustand_id=1):
        self.ax25conn.zustand_exec = self.ax25conn.zustand_tab[zustand_id](self.ax25conn)

    def rx(self, ax25_frame: AX25Frame):
        pass

    def tx(self, ax25_frame: AX25Frame):
        pass

    def cron(self):
        pass


class S1Frei(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    DM            | DM    |       | DM    |        | DM     |         | UA,S5 3)| DM 4)
    """
    stat_index = 1  # FREI

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag == 'SABM':
            # Handle Incoming Connection
            self.ax25conn.send_UA()
            self.change_state(5)
            # Process CLI ( C-Text and so on )
            self.ax25conn.exec_cli()
        elif ax25_frame.ctl_byte.pf and flag in ['I', 'RR', 'REJ', 'SREJ', 'RNR', 'DISC']:
            self.ax25conn.send_DM()
            self.change_state(0)


class S5Ready(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    RR    | I/RR 1)| RR   | I/- 2)| RR    | I      | RR,S9  | S9      | UA      | UA,S1
    """
    stat_index = 5  # BEREIT

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag == 'SABM':
            self.ax25conn.send_UA()
        elif flag == 'DISC':
            self.ax25conn.send_UA()
            self.change_state(0)

    def cron(self):
        # Check if data in ax25conn.tx_buf_rawData
        if self.ax25conn.tx_buf_rawData:
            while len(self.ax25conn.tx_buf_unACK) < self.ax25conn.parm_MaxFrame\
                    and self.ax25conn.tx_buf_rawData:
                self.ax25conn.send_I(False)

