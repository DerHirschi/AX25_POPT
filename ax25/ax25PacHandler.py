"""
    Layer 3 ??
    AX.25 Packet Handlink
"""
import time
from ax25.ax25dec_enc import AX25Frame, reverse_uid
from config_station import DefaultStationConfig
from cli.cli import *

import logging
"""
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
"""
logger = logging.getLogger(__name__)


def count_modulo(inp: int):
    return (inp + 1) % 8


class AX25Conn(object):
    def __init__(self, ax25_frame: AX25Frame, cfg: DefaultStationConfig, rx=True):
        ###############
        # DEBUG
        self.debugvar_len_out_buf = 0
        ###############
        self.rx = rx
        self.ax25_out_frame = AX25Frame()  # Predefined AX25 Frame for Output
        if rx:
            self.ax25_out_frame.addr_uid = str(reverse_uid(ax25_frame.addr_uid))  # Unique ID for Connection
            self.ax25_out_frame.to_call = ax25_frame.from_call
            self.ax25_out_frame.from_call = ax25_frame.to_call
            self.ax25_out_frame.via_calls = list(ax25_frame.via_calls)
            self.ax25_out_frame.ctl_byte.pf = ax25_frame.ctl_byte.pf
            if self.ax25_out_frame.via_calls:
                self.ax25_out_frame.via_calls.reverse()
            self.ax25_out_frame.set_stop_bit()
        else:
            self.ax25_out_frame.addr_uid = ax25_frame.addr_uid  # Unique ID for Connection
            self.ax25_out_frame.to_call = ax25_frame.to_call
            self.ax25_out_frame.from_call = ax25_frame.from_call
            self.ax25_out_frame.via_calls = ax25_frame.via_calls
            ax25_frame.encode()  # Set Stop-Bits and H-Bits while encoding
            if self.ax25_out_frame.addr_uid != ax25_frame.addr_uid:
                logger.warning('Connection UID is different after encoding Packet !!')
                self.ax25_out_frame.addr_uid = ax25_frame.addr_uid  # Unique ID for Connection

        self.rx_buf_last_frame = ax25_frame  # Buffers for last Frame !?!
        self.tx_buf_2send: [AX25Frame] = []  # Buffer for Sending. Will be processed in ax25PortHandler
        # self.tx_buf_unACK: [AX25Frame] = []   # Buffer for UNACK I-Frames
        self.tx_buf_unACK: {int: AX25Frame} = {}  # Buffer for UNACK I-Frames
        self.tx_buf_rawData: b'' = b''  # Buffer for TX RAW Data that will be packed in a Frame
        self.rx_buf_rawData: b'' = b''  # Received Data for GUI
        """ Port Variablen"""
        self.vs = 0  # Sendefolgenummer     / N(S) gleich V(R)
        self.vr = 0  # Empfangsfolgezählers / N(S) gleich V(R)
        self.t0 = 0
        self.t1 = 0  # ACK
        self.t2 = 0  # Respond Delay
        self.t3 = 0  # Connection Hold
        self.n2 = 0
        """ Zustandstabelle / State  chart"""
        self.zustand_tab = {
            0: (DefaultStat, 'ENDE'),
            1: (S1Frei, 'FREI'),
            2: (S2Aufbau, 'AUFBAU'),
            4: (S4Abbau, 'ABBAU'),
            5: (S5Ready, 'BEREIT'),
            6: (S6sendREJ, 'REJ'),
            7: (S7WaitForFinal, 'FINAL'),
        }
        if self.rx:
            self.zustand_ind = 1
        else:
            self.zustand_ind = 2
        self.zustand_exec = self.zustand_tab[self.zustand_ind][0](self)
        """ Port Parameter """
        self.parm_PacLen = cfg.parm_PacLen  # Max Pac len
        self.parm_MaxFrame = cfg.parm_MaxFrame  # Max (I) Frames
        self.parm_TXD = cfg.parm_TXD  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
        self.parm_T0 = cfg.parm_T0  # T0 (Response Delay Timer) activated if data come in to prev resp to early
        self.parm_T2 = cfg.parm_T2  # T2 (Response Delay Timer) Default: 2888 / (parm_baud / 100)
        self.parm_T3 = cfg.parm_T3  # T3 (Inactive Link Timer)
        self.parm_N2 = cfg.parm_N2  # Max Try   Default 20
        self.parm_baud = cfg.parm_baud  # Baud for calculating Timer
        """ Port Parameter ENDE """
        """ CLI Parameter """
        self.cli = DefaultCLI()
        """ CLI Parameter ENDE """
        self.calc_T2 = self.parm_T2 / (self.parm_baud / 100)
        # Initial-Round-Trip-Time (Auto Parm) (bei DAMA wird T2*2 genommen)/NO DAMA YET
        self.calc_IRTT = (self.parm_T2 + self.parm_TXD) * 2
        """
        if self.rx:
            self.zustand_exec = S1Frei(self)
            # self.handle_rx(ax25_frame)
        else:
            self.zustand_exec = S2Aufbau(self)
            self.set_T3()
            # self.zustand_exec = S2Aufbau(self)
            # self.handle_tx(ax25_frame)
        """

    def __del__(self):
        del self.zustand_exec

    ####################
    # Zustand EXECs
    def handle_rx(self, ax25_frame: AX25Frame):
        # print( vars(self.zustand_exec).keys())
        self.set_new_state()
        self.rx_buf_last_frame = ax25_frame
        self.zustand_exec.rx(ax25_frame=ax25_frame)
        self.set_T3()

    def handle_tx(self, ax25_frame: AX25Frame):
        self.set_new_state()
        self.zustand_exec.tx(ax25_frame=ax25_frame)
        # self.set_T3()

    def exec_cron(self):
        """ DefaultStat.cron() """
        self.set_new_state()
        self.zustand_exec.cron()
    # Zustand EXECs ENDE
    #######################
    # Zustand Handling

    def change_state(self, zustand=1):
        del self.zustand_exec
        self.zustand_ind = zustand
        logger.error("ZUSTAND CHANGE - State: {}".format(zustand))
        # DONE: TESTING: TODO !!!! Init zustand_exec after del zustand_exec !!! Risk of Bug
        # self.zustand_exec = self.zustand_tab[zustand](self)

    def set_new_state(self):
        self.zustand_exec = self.zustand_tab[self.zustand_ind][0](self)
    # Zustand Handling ENDE
    #######################

    def set_T1(self, stop=False):
        if stop:
            self.n2 = 0
            self.t1 = 0
        else:
            n2 = int(self.n2)
            srtt = float(self.calc_IRTT)
            if self.ax25_out_frame.via_calls:
                srtt = int((len(self.ax25_out_frame.via_calls) * 2 + 1) * srtt)
            if n2 > 3:
                self.t1 = float(((srtt * (n2 + 4)) / 100) + time.time())
            else:
                self.t1 = float(((srtt * 3) / 100) + time.time())

    def set_T2(self, stop=False):
        if stop:
            self.t2 = 0
        else:
            self.t2 = float(self.parm_T2 + time.time())

    def set_T3(self, stop=False):
        if stop:
            self.t3 = 0
        else:
            self.t3 = float(self.parm_T3 + time.time())

    def del_unACK_buf(self):
        # vs = int(self.vs)
        vr = int(self.rx_buf_last_frame.ctl_byte.nr)
        if vr != -1:    # Check if right Packet
            vr = (vr - 1) % 8
            index_list = list(self.tx_buf_unACK.keys())
            """
            print("DELunACK ------------------------------")
            print("DELunACK - vr: {}".format(vr))
            print("DELunACK - tx_buf_unACK: {}".format(index_list))
            """
            for i in range(8):
                ind = (vr - i) % 8
                print("DELunACK - ind: {}".format(ind))
                if ind in index_list:
                    del self.tx_buf_unACK[ind]
                    print("DELunACK - DEL!!: {}".format(ind))
                else:
                    break

    def resend_unACK_buf(self, max_pac=None):  # TODO Testing
        vs = int(self.vs)
        if max_pac is None:
            max_pac = self.parm_MaxFrame
        index_list = list(self.tx_buf_unACK.keys())
        start_i = None
        for i in range(8):
            if (vs - 1) % 8 not in index_list:
                break
            else:
                start_i = (vs - 1) % 8
        """
        print("unACK Resender ------------------------------")
        print("unACK Resender - max_pac: {}".format(max_pac))
        print("unACK Resender - self.tx_buf_unACK.k: {}".format(index_list))
        print("unACK Resender - start_i: {}".format(start_i))
        """
        if start_i is not None:
            for i in range(min(max_pac, len(index_list))):
                print("unACK Resender - loop: {}".format(i))

                if i + start_i in index_list:
                    self.tx_buf_2send.append(self.tx_buf_unACK[i + start_i])
                else:
                    logger.error("unACK Resender.. unACK_buf: {}\nind: {}".format(
                        self.tx_buf_unACK.keys(),
                        start_i + i
                    ))
        else:
            logger.error("unACK Resender.. unACK_buf: {}\n NONE".format(
                self.tx_buf_unACK.keys()
            ))

    def exec_cli(self, inp=b''):
        """ CLI Processing like sending C-Text ... """
        self.tx_buf_rawData += self.cli.cli_exec(inp)

    def init_new_ax25frame(self):
        pac = AX25Frame()
        pac.from_call = self.ax25_out_frame.from_call
        pac.to_call = self.ax25_out_frame.to_call
        pac.via_calls = self.ax25_out_frame.via_calls
        pac.addr_uid = self.ax25_out_frame.addr_uid
        self.ax25_out_frame = pac

    def build_I_fm_raw_buf(self):
        if self.tx_buf_rawData:
            while len(self.tx_buf_unACK) < self.parm_MaxFrame \
                    and self.tx_buf_rawData:
                self.send_I(False)

    def send_I(self, pf_bit=False):
        """
        :param pf_bit: bool
        True if RX a REJ Packet
        """
        if self.tx_buf_rawData:  # Double Check, just in case
            self.init_new_ax25frame()
            pac = self.ax25_out_frame  # Get predefined Packet Structure
            # pac = self.ax25_out_frame
            self.ax25_out_frame.ctl_byte.pf = pf_bit  # Poll/Final Bit / True if REJ is received
            # TODO !!! Testen ob VR in tx_buf_unACK geupdated wird !!!
            self.ax25_out_frame.ctl_byte.nr = self.vr  # Receive PAC Counter
            # TODO !!! Testen ob VR in tx_buf_unACK geupdated wird !!!
            self.ax25_out_frame.ctl_byte.ns = int(self.vs)  # Send PAC Counter
            self.ax25_out_frame.ctl_byte.IcByte()  # Set C-Byte
            self.ax25_out_frame.pid_byte.text()  # Set PID-Byte to TEXT
            # PAYLOAD !!
            pac_len = min(self.parm_PacLen, len(self.tx_buf_rawData))
            self.ax25_out_frame.data = self.tx_buf_rawData[:pac_len]
            self.tx_buf_rawData = self.tx_buf_rawData[pac_len:]
            self.ax25_out_frame.encode()  # Encoding the shit
            # self.tx_buf_unACK.append(pac)         # Keep Packet until ACK/RR
            pac = self.ax25_out_frame
            self.tx_buf_unACK[int(self.vs)] = pac  # Keep Packet until ACK/RR
            self.tx_buf_2send.append(pac)
            # !!! COUNT VS !!!
            self.vs = count_modulo(int(self.vs))  # Increment VS Modulo 8
            self.set_T1()  # Re/Set T1

    def send_UA(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.UAcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)
        self.set_T3()

    def send_DM(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.DMcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_DISC(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.DISCcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_SABM(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.SABMcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_RR(self, pf_bit=False, cmd_bit=False):
        self.init_new_ax25frame()
        pac = self.ax25_out_frame
        pac.ctl_byte.cmd = cmd_bit  # Command / Respond Bit
        pac.ctl_byte.pf = pf_bit   # Poll/Final Bit / True if REJ is received
        pac.ctl_byte.nr = self.vr  # Receive PAC Counter
        self.ax25_out_frame.ctl_byte.RRcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_REJ(self, pf_bit=False, cmd_bit=False):
        self.init_new_ax25frame()
        pac = self.ax25_out_frame
        pac.ctl_byte.cmd = cmd_bit      # Command / Respond Bit
        pac.ctl_byte.pf = pf_bit        # Poll/Final Bit / True if REJ is received
        pac.ctl_byte.nr = self.vr    # Receive PAC Counter
        self.ax25_out_frame.ctl_byte.REJcByte()
        self.ax25_out_frame.encode()
        self.tx_buf_2send.append(self.ax25_out_frame)


class DefaultStat(object):
    stat_index = 0  # ENDE Verbindung wird gelöscht...

    def __init__(self, ax25_conn: AX25Conn):
        # logger.error("ZUSTAND - INIT - State: {}".format(self.stat_index))
        self.ax25conn = ax25_conn
        """
        self.flag = {
            0: 'ENDE',      # If Stat 0 than Delete Connection
            1: 'FREI',      # Init State RX
            2: 'AUFBAU',    # Init State TX
            # 3: 'RÜCKWEISUNG',
            4: 'ABBAU',
            5: 'BEREIT',
            6: 'REJ AUSGESANDT',
            7: 'WARTE AUF FINAL',
        }[self.stat_index]
        """
    def __del__(self):
        # Change stat to 0 And disc
        # logger.error("ZUSTAND - DEL - State: {}".format(self.stat_index))
        pass

    def change_state(self, zustand_id=1):
        """
        del self.ax25conn.zustand_exec
        new_z = self.ax25conn.zustand_tab[zustand_id]
        new_z(self.ax25conn)
        self.ax25conn.zustand_exec = new_z
        """
        logger.error("ZUSTAND CHANGE - State: {}".format(zustand_id))
        self.ax25conn.change_state(zustand=zustand_id)

    def rx(self, ax25_frame: AX25Frame):
        pass

    def tx(self, ax25_frame: AX25Frame):
        pass

    def state_cron(self):
        pass

    def cron(self):
        """Global Cron"""
        self.state_cron()       # State Crone
        ###########
        # DEBUGGING
        self.ax25conn.debugvar_len_out_buf = len(self.ax25conn.tx_buf_2send)
        ###########
        # TODO Connection Timeout


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
            self.ax25conn.rx_buf_rawData = '** Connect from {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.change_state(5)
            # Process CLI ( C-Text and so on )
            self.ax25conn.exec_cli()
        elif ax25_frame.ctl_byte.pf and flag in ['I', 'RR', 'REJ', 'SREJ', 'RNR', 'DISC', 'FRMR']:
            self.ax25conn.send_DM()
            self.change_state(0)


class S2Aufbau(DefaultStat):
    stat_index = 2  # AUFBAU Verbindung Aufbau

    def tx(self, ax25_frame: AX25Frame):
        if time.time() > self.ax25conn.t1\
         and time.time() > self.ax25conn.t3:
            self.ax25conn.rx_buf_rawData = '\n*** Try connect to {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.send_SABM()
            self.ax25conn.set_T1()
            self.ax25conn.set_T3()

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag == 'UA':
            self.ax25conn.rx_buf_rawData = '\n*** Connected to {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.tx_buf_2send = []    # Clean Send Buffer.
            self.ax25conn.tx_buf_rawData = b''    # Clean Send Buffer.
            self.ax25conn.n2 = 0
            self.change_state(5)
        elif flag == 'DM':
            self.ax25conn.rx_buf_rawData = '\n*** Busy from {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.change_state(0)

    def state_cron(self):
        if time.time() > self.ax25conn.t1:
            if not self.ax25conn.n2:
                self.ax25conn.rx_buf_rawData = '\n*** Try connect to {}\n'.format(self.ax25conn.ax25_out_frame.to_call.call_str).encode()
            if self.ax25conn.n2 < self.ax25conn.parm_N2:
                # self.change_state(2)
                self.ax25conn.send_SABM()
                self.ax25conn.n2 += 1
                self.ax25conn.set_T1()
            else:
                self.ax25conn.rx_buf_rawData = '\n*** Failed connect to {}\n'.format(self.ax25conn.ax25_out_frame.to_call.call_str).encode()
                self.ax25conn.send_DISC()
                self.change_state(0)


class S4Abbau(DefaultStat):
    stat_index = 4  # ABBAU

    def tx(self, ax25_frame: AX25Frame):
        self.ax25conn.tx_buf_rawData = b''
        self.ax25conn.tx_buf_2send = []
        self.ax25conn.tx_buf_unACK = {}
        self.ax25conn.send_DISC()
        self.ax25conn.set_T1()
        self.ax25conn.set_T3()

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag in ['UA', 'DM']:
            self.ax25conn.rx_buf_rawData = '\n*** Disconnected from {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.set_T1()      # Prevent sending another Packet
            self.ax25conn.set_T3()      # Prevent sending another Packet
            self.change_state(0)

    def state_cron(self):
        if time.time() > self.ax25conn.t1\
                or time.time() > self.ax25conn.t3:
            if self.ax25conn.n2 < self.ax25conn.parm_N2:
                # self.change_state(2)
                self.ax25conn.send_DISC()
                self.ax25conn.n2 += 1
                self.ax25conn.set_T1()
                self.ax25conn.set_T3()
            else:
                self.ax25conn.rx_buf_rawData = '\n*** Disconnected from {}\n'.format(
                    self.ax25conn.ax25_out_frame.to_call.call_str).encode()
                # self.ax25conn.send_DISC()
                self.change_state(0)


class S5Ready(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    RR    | I/RR 1)| RR   | I/- 2)| RR    | I      | RR,S9  | S9      | UA      | UA,S1
    """
    # MD2SAW to MD6TES via CB0SAW* DX0SAW* cmd (0x31) RR1+  >> After T3/2 ?
    """
    DW 02:27:28: DX0SAW to MD2SAW via CB0SAW cmd (0x91) RR4+
    DW 02:27:28: MD2SAW to DX0SAW via CB0SAW* rpt (0xb1) RR5+
    """
    stat_index = 5  # BEREIT

    def rx(self, ax25_frame: AX25Frame):
        self.ax25conn.set_T1(stop=True)
        flag = ax25_frame.ctl_byte.flag
        c_byte = ax25_frame.ctl_byte
        cmd = c_byte.cmd
        pf = c_byte.pf
        ns = c_byte.ns
        nr = c_byte.nr
        # TESTING: self.ax25conn.send_DM()
        if flag == 'SABM':
            self.ax25conn.send_UA()
        elif flag == 'DISC':
            self.ax25conn.send_UA()
            self.change_state(0)
        elif flag == 'RR':
            self.ax25conn.del_unACK_buf()
            if self.ax25conn.vs == nr:
                if cmd:
                    self.ax25conn.send_RR(pf_bit=pf, cmd_bit=False)
            else:
                # TODO FRMR
                print(" !!!! FRMR RR !!!! ")
                print("ownVR: {}     recNR: {}".format(self.ax25conn.vr, nr))
                print("ownVS: {}     recNS: {}".format(self.ax25conn.vs, ns))
        elif flag == 'REJ':
            # TODO !!!!!!!!!!!!
            pass
        elif flag == 'I':
            """
            vr = # Empfangsfolgezählers / N(R) gleich V(R)
            vS = # Empfangsfolgezählers / N(S) gleich V(S)
            """
            if nr != self.ax25conn.vs:
                # TODO FRMR S3
                print(" !!!! FRMR I !!!! ")
                print("ownVR: {}     recNR: {}".format(self.ax25conn.vr, nr))
                print("ownVS: {}     recNS: {}".format(self.ax25conn.vs, ns))
            else:
                self.ax25conn.del_unACK_buf()
                if ns == self.ax25conn.vr:  # Korrekt
                    # Proces correct I-Frame
                    self.ax25conn.vr = count_modulo(int(self.ax25conn.vr))
                    self.ax25conn.rx_buf_rawData += ax25_frame.data
                    if cmd:
                        self.ax25conn.send_RR(pf_bit=pf, cmd_bit=False)
                    elif not self.ax25conn.tx_buf_unACK:
                        self.ax25conn.send_RR(pf_bit=pf, cmd_bit=False)
                    if self.stat_index == 6:    # return from REJ_state
                        self.change_state(5)
                else:
                    if self.stat_index in [5, 9]:
                        # REJ
                        print(" !!!!! TX REJ !!!! ")
                        print("ownVR: {}     recNR: {}".format(self.ax25conn.vr, nr))
                        print("ownVS: {}     recNS: {}".format(self.ax25conn.vs, ns))
                        self.ax25conn.send_REJ(pf_bit=False, cmd_bit=False)
                        if self.stat_index == 5:
                            self.change_state(6)    # go into REF_state
                        elif self.stat_index == 9:
                            self.change_state(15)   # go into "REJ ausgesandt u. Gegenstelle nicht bereit"
                    elif self.stat_index in [10, 14]:
                        # TODO RNR
                        pass

    def tx(self, ax25_frame: AX25Frame):
        if time.time() > self.ax25conn.t1:
            if self.ax25conn.tx_buf_rawData:
                self.ax25conn.build_I_fm_raw_buf()

    def state_cron(self):
        # T1 Abgelaufen
        if time.time() > self.ax25conn.t1:
            # Nach 5 Versuchen
            if self.ax25conn.n2 > 5:
                self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
                self.ax25conn.set_T1()
                self.change_state(7)    # S7 Warten auf Final
            else:
                if self.ax25conn.tx_buf_unACK:
                    # Nach 2 Versuchen nur noch einzelne Pakete senden
                    if self.ax25conn.n2 > 1:
                        self.ax25conn.resend_unACK_buf(1)
                    else:
                        self.ax25conn.resend_unACK_buf()
                        # Und neue Pakete gleich mit senden...
                        if self.ax25conn.tx_buf_rawData:
                            self.ax25conn.build_I_fm_raw_buf()
                    self.ax25conn.n2 += 1
                    self.ax25conn.set_T1()
        if self.ax25conn.tx_buf_rawData \
                and time.time() > self.ax25conn.t1:
            self.ax25conn.build_I_fm_raw_buf()
            self.ax25conn.set_T3()
        # T3 Abgelaufen
        elif time.time() > self.ax25conn.t3\
                and time.time() > self.ax25conn.t1:
            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self.ax25conn.set_T1()
            self.change_state(7)        # S7 Warten auf Final


class S6sendREJ(S5Ready):
    """Copy of S5Ready"""
    stat_index = 6  # REJ ausgesandt

    def tx(self, ax25_frame: AX25Frame):
        pass

    def state_cron(self):
        # T1 Abgelaufen
        if time.time() > self.ax25conn.t1:
            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self.ax25conn.n2 += 1
            self.ax25conn.set_T1()
            self.change_state(7)  # S7 Warten auf Final
        elif time.time() > self.ax25conn.t3:
            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self.ax25conn.n2 += 1
            self.ax25conn.set_T1()
            self.change_state(7)  # S7 Warten auf Final


class S7WaitForFinal(DefaultStat):
    stat_index = 7  # Warten auf Final

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag == 'RR':
            c_byte = ax25_frame.ctl_byte
            pf = c_byte.pf
            nr = c_byte.nr
            if self.ax25conn.vs == nr:
                self.ax25conn.del_unACK_buf()
                if pf:
                    self.ax25conn.set_T1(stop=True)
                    self.ax25conn.n2 = 0
                    self.change_state(5)
            else:
                # TODO FRMR
                print(" !!!!! FRMR RR - S7!!!! ")
                print("ownVR: {}     recNR: {}".format(self.ax25conn.vr, nr))

    def state_cron(self):
        # T1 Abgelaufen
        if time.time() > self.ax25conn.t1:
            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self.ax25conn.n2 += 1
            self.ax25conn.set_T1()

