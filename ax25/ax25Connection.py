"""
    Layer 3 ??
    AX.25 Packet Handlink
"""
import time

from ax25.ax25dec_enc import AX25Frame, reverse_uid
from config_station import DefaultPortConfig, NoneCLI

import logging


logger = logging.getLogger(__name__)


def count_modulo(inp: int):
    return (inp + 1) % 8


class AX25Conn(object):
    def __init__(self, ax25_frame: AX25Frame, cfg: DefaultPortConfig, port, rx=True):
        ###############
        # DEBUG
        self.debugvar_len_out_buf = 0
        ###############
        ############
        # GLOBALS
        # glb_mh = None
        self.own_port = port
        self.prt_hndl = self.own_port.port_handler
        """
        if cfg.glb_port_handler is None:
            logger.error("No Port Handler found !!!")
            # TODO Maybe Settings to choose run with Porthandler or not
            self.is_prt_hndl = False
            raise ConnectionError
        else:
            
            self.prt_hndl = cfg.glb_port_handler
            self.is_prt_hndl = True
        """
        self.ch_index: int = 0
        self.gui = self.prt_hndl.gui
        if self.gui is None:
            self.is_gui = False
        else:
            self.ch_index = self.gui.channel_index
            self.is_gui = True
        # AX25 Frame for Connection Initialisation.
        self.ax25_out_frame = AX25Frame()   # Predefined AX25 Frame for Output
        """ Config new Connection Address """
        self.ax25_out_frame.axip_add = ax25_frame.axip_add
        self.axip_add = self.ax25_out_frame.axip_add
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
                self.ax25_out_frame.addr_uid = ax25_frame.addr_uid  # Unique ID for Connection
        self.my_call_obj = self.ax25_out_frame.from_call
        self.my_call_str = self.my_call_obj.call
        print('self.axip_add')
        print(self.axip_add)
        """ S-Packet / CTL Vars"""
        self.REJ_is_set: bool = False
        """ IO Buffer Packet For Handling """
        self.tx_buf_ctl: [AX25Frame] = []           # Buffer for CTL ( S ) Frame to send on next Cycle
        self.tx_buf_2send: [AX25Frame] = []         # Buffer for Sending. Will be processed in ax25PortHandler
        self.tx_buf_unACK: {int: AX25Frame} = {}    # Buffer for UNACK I-Frames
        self.rx_buf_last_frame = ax25_frame         # Buffers for last Frame !?!
        """ IO Buffer For GUI / CLI """
        self.tx_buf_rawData: b'' = b''          # Buffer for TX RAW Data that will be packed into a Frame
        self.rx_buf_rawData: b'' = b''          # Received Data for GUI
        self.rx_buf_monitor: [str] = []         # Received Data Monitor String
        self.rx_buf_rawData_2: b'' = b''        # Received Data TEST Script
        """ Port Variablen"""
        self.vs = 0  # Sendefolgenummer     / N(S) = V(R)  TX
        self.vr = 0  # Empfangsfolgezählers / N(S) = V(R)  TX
        self.t1 = 0  # ACK
        self.t2 = 0  # Respond Delay
        self.t3 = 0  # Connection Hold
        self.n2 = 0  # Fail Counter / No Response Counter
        """ Port Config Parameter """
        self.cfg = cfg
        self.parm_PacLen = cfg.parm_PacLen  # Max Pac len
        self.parm_MaxFrame = cfg.parm_MaxFrame  # Max (I) Frames
        self.parm_TXD = cfg.parm_TXD    # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
        self.parm_T2 = cfg.parm_T2      # T2 (Response Delay Timer) Default: 2888 / (parm_baud / 100)
        self.parm_T3 = cfg.parm_T3      # T3 (Inactive Link Timer)
        self.parm_N2 = cfg.parm_N2      # Max Try   Default 20
        self.parm_baud = cfg.parm_baud  # Baud for calculating Timer
        """ Zustandstabelle / Statechart """
        self.zustand_tab = {
            0: (DefaultStat, 'ENDE'),
            1: (S1Frei, 'FREI'),
            2: (S2Aufbau, 'AUFBAU'),
            4: (S4Abbau, 'ABBAU'),
            5: (S5Ready, 'BEREIT'),
            6: (S6sendREJ, 'REJ'),
            7: (S7WaitForFinal, 'FINAL'),
        }
        """ MH for CLI """
        # self.mh = cfg.parm_mh
        # self.cli = NoneCLI(self)
        """ Station Individual Parameter """
        if self.my_call_obj.call_str in cfg.parm_StationCalls:
            self.parm_PacLen = cfg.parm_stat_PacLen[self.my_call_obj.call_str]      # Max Pac len
            self.parm_MaxFrame = cfg.parm_stat_MaxFrame[self.my_call_obj.call_str]  # Max Pac
            """ Init CLI """
            for stat in cfg.parm_Stations:
                if self.my_call_obj.call_str in stat.stat_parm_Call:
                    self.cli = cfg.parm_cli[self.my_call_obj.call_str](self, stat)
                    break

            # print(cfg.parm_Stations)
            # print(cfg.parm_cli[self.my_call_obj.call_str].c_text)
        else:
            self.cli = NoneCLI(self)
        """ DIGI / Link to other Connection for Auto processing """
        self.DIGI_Connection: AX25Conn
        self.is_link = False
        self.my_digi_call = ''
        """ Timer Calculation """
        self.parm_T2 = float(self.parm_T2 / self.parm_baud)  # TODO Berechnen nach Paktegröße
        # Initial-Round-Trip-Time (Auto Parm) (bei DAMA wird T2*2 genommen)/NO DAMA YET
        self.calc_IRTT = (self.parm_T2 + self.parm_TXD / 10) * 2
        if rx:
            self.zustand_exec = S1Frei(self)
        else:
            self.zustand_exec = S2Aufbau(self)
            self.cli.change_cli_state(1)
            # self.prt_hndl.insert_conn2all_conn_var(new_conn=self)
            self.set_T3()

    def __del__(self):
        """
        if hasattr(self, 'DIGI_Connection'):
            self.DIGI_Connection: AX25Conn
            self.DIGI_Connection.zustand_exec.change_state(4)
        """
        """
        if self.is_prt_hndl:
            self.prt_hndl.del_conn2all_conn_var(conn=self)
        """
        """
        if self.is_gui:
            self.gui.ch_btn_status()
        """
        del self.ax25_out_frame
        del self.cli
        del self.zustand_exec

    ####################
    # Zustand EXECs
    def handle_rx(self, ax25_frame: AX25Frame):
        # if hasattr(self, 'DIGI_Connection'):
        self.rx_buf_last_frame = ax25_frame
        self.zustand_exec.rx(ax25_frame=ax25_frame)
        self.set_T3()

    def handle_tx(self, ax25_frame: AX25Frame):
        self.zustand_exec.tx(ax25_frame=ax25_frame)

    def exec_cron(self):
        """ DefaultStat.cron() """
        self.cli.cli_cron()
        self.zustand_exec.cron()

    # Zustand EXECs ENDE
    #######################

    def link_connection(self, conn):
        self.DIGI_Connection: AX25Conn = conn
        self.is_link = True

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
        nr = int(self.rx_buf_last_frame.ctl_byte.nr)
        if nr != -1:  # Check if right Packet
            for i in list(self.tx_buf_unACK.keys()):
                if i == nr:
                    break
                del self.tx_buf_unACK[i]
                # print("DELunACK - DEL!!: {}".format(i))

    def resend_unACK_buf(self, max_pac=None):  # TODO Testing
        if max_pac is None:
            max_pac = self.parm_MaxFrame
        index_list = list(self.tx_buf_unACK.keys())
        for i in range(min(max_pac, len(index_list))):
            pac: AX25Frame = self.tx_buf_unACK[index_list[i]]
            # print("VR - PAC: {}".format(pac.ctl_byte.nr))
            # print("VR - VR Station: {}".format(self.vr))
            pac.ctl_byte.nr = self.vr
            self.tx_buf_2send.append(pac)

    def exec_cli(self, inp=b''):
        """ CLI Processing like sending C-Text ... """
        # self.tx_buf_rawData += self.cli.cli_exec(inp)
        self.cli.cli_exec(inp)

    def cron_cli(self):
        """ CLI Processing like sending C-Text ... """
        # self.tx_buf_rawData += self.cli.cli_exec(inp)
        self.cli.cli_cron()

    def init_new_ax25frame(self):
        pac = AX25Frame()
        pac.from_call = self.ax25_out_frame.from_call
        pac.to_call = self.ax25_out_frame.to_call
        pac.via_calls = self.ax25_out_frame.via_calls
        pac.addr_uid = self.ax25_out_frame.addr_uid
        pac.axip_add = self.ax25_out_frame.axip_add
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
            self.ax25_out_frame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
            self.ax25_out_frame.ctl_byte.nr = self.vr  # Receive PAC Counter
            self.ax25_out_frame.ctl_byte.ns = int(self.vs)  # Send PAC Counter
            self.ax25_out_frame.ctl_byte.IcByte()  # Set C-Byte
            self.ax25_out_frame.pid_byte.text()  # Set PID-Byte to TEXT
            # PAYLOAD !!
            pac_len = min(self.parm_PacLen, len(self.tx_buf_rawData))
            self.ax25_out_frame.data = self.tx_buf_rawData[:pac_len]
            self.tx_buf_rawData = self.tx_buf_rawData[pac_len:]
            self.tx_buf_unACK[int(self.vs)] = self.ax25_out_frame  # Keep Packet until ACK/RR
            self.tx_buf_2send.append(self.ax25_out_frame)
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
        pac.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        pac.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        pac.ctl_byte.nr = self.vr  # Receive PAC Counter
        self.ax25_out_frame.ctl_byte.RRcByte()
        if not self.REJ_is_set:
            self.tx_buf_ctl = [self.ax25_out_frame]

    def send_REJ(self, pf_bit=False, cmd_bit=False):
        self.init_new_ax25frame()
        pac = self.ax25_out_frame
        pac.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        pac.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        pac.ctl_byte.nr = self.vr  # Receive PAC Counter
        self.ax25_out_frame.ctl_byte.REJcByte()
        self.tx_buf_ctl = [self.ax25_out_frame]
        self.REJ_is_set = True


class DefaultStat(object):
    stat_index = 0  # ENDE Verbindung wird gelöscht...

    def __init__(self, ax25_conn: AX25Conn):
        self.ax25conn = ax25_conn
        if hasattr(self.ax25conn, 'DIGI_Connection'):
            self.digi_conn: AX25Conn = self.ax25conn.DIGI_Connection
        else:
            self.digi_conn = None

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
        pass

    def change_state(self, zustand_id=1):
        self.ax25conn.zustand_exec = self.ax25conn.zustand_tab[zustand_id][0](self.ax25conn)
        if self.ax25conn.is_gui:
            self.ax25conn.gui.ch_btn_status_update()

    def rx(self, ax25_frame: AX25Frame):
        pass

    def tx(self, ax25_frame: AX25Frame):
        pass

    def state_cron(self):
        pass

    def cron(self):
        """Global Cron"""
        ########################################
        # DIGI / LINK Connection / Node Funktion
        if self.digi_conn is not None:
            # Handle Connection End
            if self.digi_conn.zustand_exec.stat_index in [0, 1, 4]:
                if self.stat_index not in [0, 1, 4]:
                    self.change_state(4)
            if self.stat_index in [0, 1, 4]:
                if self.digi_conn.zustand_exec.stat_index not in [0, 1, 4]:
                    self.digi_conn.zustand_exec.change_state(4)
            else:
                # Handle RX/TX Buffer Sharing
                self.digi_conn: AX25Conn
                if self.ax25conn.rx_buf_rawData:
                    self.digi_conn.tx_buf_rawData += bytes(self.ax25conn.rx_buf_rawData)
                    self.ax25conn.rx_buf_rawData = b''
                if self.digi_conn.rx_buf_rawData:
                    self.ax25conn.tx_buf_rawData += bytes(self.digi_conn.rx_buf_rawData)
                    self.digi_conn.rx_buf_rawData = b''
        # CLEANUP
        if self.ax25conn.n2 == 100 and not self.ax25conn.tx_buf_2send:
            self.change_state(0)
            self.ax25conn.prt_hndl.del_conn2all_conn_var(self.ax25conn)
        ###########
        # DEBUGGING
        self.ax25conn.debugvar_len_out_buf = len(self.ax25conn.tx_buf_2send)
        ###########
        # TODO Connection Timeout
        self.state_cron()  # State Cronex


class S1Frei(DefaultStat):  # INIT RX
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
            self.ax25conn.rx_buf_rawData = '*** Connect from {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.n2 = 0
            self.change_state(5)
            # if self.ax25conn.is_prt_hndl:
            self.ax25conn.prt_hndl.insert_conn2all_conn_var(new_conn=self.ax25conn)
            if self.ax25conn.is_gui:
                self.ax25conn.gui.new_conn_snd()
            self.ax25conn.exec_cli()  # Process CLI ( C-Text and so on )
        elif ax25_frame.ctl_byte.pf and flag in ['I', 'RR', 'REJ', 'SREJ', 'RNR', 'DISC', 'FRMR']:
            self.ax25conn.send_DM()
            self.ax25conn.set_T1(stop=True)
            self.ax25conn.set_T2(stop=True)
            self.ax25conn.n2 = 100
        else:
            self.change_state(0)


class S2Aufbau(DefaultStat):    # INIT TX
    stat_index = 2  # AUFBAU Verbindung Aufbau

    def tx(self, ax25_frame: AX25Frame = None):
        ax25_frame = self.ax25conn.ax25_out_frame
        if time.time() > self.ax25conn.t1 \
                and time.time() > self.ax25conn.t3:
            if self.digi_conn is None:
                self.ax25conn.rx_buf_rawData = '\n*** Try connect to {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.send_SABM()
            self.ax25conn.set_T1()
            self.ax25conn.set_T3()
            # if self.ax25conn.is_prt_hndl:
            self.ax25conn.prt_hndl.insert_conn2all_conn_var(new_conn=self.ax25conn)

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag in ['UA', 'SABM']:
            if self.digi_conn is None:
                self.ax25conn.rx_buf_rawData = '\n*** Connected to {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.tx_buf_2send = []  # Clean Send Buffer.
            self.ax25conn.tx_buf_rawData = b''  # Clean Send Buffer.
            self.ax25conn.n2 = 0
            self.change_state(5)
            if self.ax25conn.is_gui:
                self.ax25conn.gui.new_conn_snd()
            """
            if flag == 'SABM':
                self.ax25conn.exec_cli()
            """
        elif flag in ['DM', 'DISC']:
            if self.digi_conn is None:
                self.ax25conn.rx_buf_rawData = '\n*** Busy from {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.n2 = 100
            self.change_state(0)
            # if self.ax25conn.is_prt_hndl:
            self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)

    def state_cron(self):
        if time.time() > self.ax25conn.t1:
            if not self.ax25conn.n2:
                if self.digi_conn is None:
                    self.ax25conn.rx_buf_rawData = '\n*** Try connect to {}\n'.format(
                        self.ax25conn.ax25_out_frame.to_call.call_str).encode()
            if self.ax25conn.n2 < self.ax25conn.parm_N2:
                # self.change_state(2)
                self.ax25conn.send_SABM()
                self.ax25conn.n2 += 1
                self.ax25conn.set_T1()
            else:
                if self.digi_conn is None:
                    self.ax25conn.rx_buf_rawData = '\n*** Failed connect to {}\n'.format(
                        self.ax25conn.ax25_out_frame.to_call.call_str).encode()
                self.ax25conn.send_DISC()
                self.ax25conn.n2 = 100
                self.change_state(1)
                # if self.ax25conn.is_prt_hndl:
                self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)


class S4Abbau(DefaultStat):
    stat_index = 4  # ABBAU

    def tx(self, ax25_frame: AX25Frame):
        self.ax25conn.n2 = 0
        self.ax25conn.tx_buf_rawData = b''
        self.ax25conn.tx_buf_2send = []
        self.ax25conn.tx_buf_unACK = {}
        self.ax25conn.send_DISC()
        self.ax25conn.set_T1()
        # self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)  # TODO if Hard DISCO

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag in ['UA', 'DM']:
            if self.digi_conn is None:
                self.ax25conn.rx_buf_rawData = '\n*** Disconnected from {}\n'.format(ax25_frame.to_call.call_str).encode()
            self.ax25conn.set_T1()  # Prevent sending another Packet
            self.change_state(0)
            # if self.ax25conn.is_prt_hndl:
            self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)
        elif flag in ['SABM'] or \
                (flag in ['RR', 'REJ', 'I', 'RNR'] and ax25_frame.ctl_byte.pf):
            self.ax25conn.send_DM()
            self.ax25conn.n2 = 100
            self.change_state(1)
            # if self.ax25conn.is_prt_hndl:
            self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)
        elif flag == 'DISC':
            self.ax25conn.send_UA()
            self.ax25conn.n2 = 100
            self.change_state(1)
            # if self.ax25conn.is_prt_hndl:
            self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)

    def state_cron(self):
        if time.time() > self.ax25conn.t1:
            if self.ax25conn.n2 < self.ax25conn.parm_N2:
                # self.change_state(2)
                self.ax25conn.send_DISC()
                self.ax25conn.n2 += 1
                self.ax25conn.set_T1()
            else:
                if self.digi_conn is None:
                    self.ax25conn.rx_buf_rawData = '\n*** Disconnected from {}\n'.format(
                        self.ax25conn.ax25_out_frame.to_call.call_str).encode()
                # self.ax25conn.send_DISC()
                self.change_state(0)
                # if self.ax25conn.is_prt_hndl:
                self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)


class S5Ready(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    RR    | I/RR 1)| RR   | I/- 2)| RR    | I      | RR,S9  | S9      | UA      | UA,S1
    """
    stat_index = 5  # BEREIT

    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        c_byte = ax25_frame.ctl_byte
        cmd = c_byte.cmd
        pf = c_byte.pf
        ns = c_byte.ns
        nr = c_byte.nr
        if flag == 'SABM':
            self.ax25conn.send_UA()
        elif flag == 'DISC':
            self.ax25conn.send_UA()
            self.ax25conn.n2 = 100
            self.change_state(1)
            # if self.ax25conn.is_prt_hndl:
            self.ax25conn.prt_hndl.del_conn2all_conn_var(conn=self.ax25conn)
        elif flag == 'RR':
            if ((nr - 1) % 8) in self.ax25conn.tx_buf_unACK.keys():
                self.ax25conn.del_unACK_buf()
                self.ax25conn.n2 = 0
                if self.ax25conn.tx_buf_unACK:
                    self.ax25conn.set_T2()
                else:
                    self.ax25conn.set_T1(stop=True)
            if cmd:
                self.ax25conn.send_RR(pf_bit=pf, cmd_bit=False)
            if self.stat_index == 7 and pf:  # Warte auf Final
                self.ax25conn.n2 = 0
                self.ax25conn.set_T1(stop=True)
                self.change_state(5)
            elif pf:
                self.ax25conn.send_RR(pf_bit=pf, cmd_bit=False)
        elif flag == 'REJ':
            self.ax25conn.n2 = 0
            # print(" !!!!! RX REJ !!!! ")
            # print("ownVR: {}     recNR: {}".format(self.ax25conn.vr, nr))
            # print("ownVS: {}     recNS: {}".format(self.ax25conn.vs, ns))
            if ((nr - 1) % 8) in self.ax25conn.tx_buf_unACK.keys():
                # print(" !!!!! DEL unACK !!!! ")
                self.ax25conn.del_unACK_buf()
            if self.stat_index == 7 and pf:
                self.ax25conn.set_T1(stop=True)
                self.change_state(5)
            elif pf:
                self.ax25conn.send_RR(pf_bit=pf, cmd_bit=False)
            else:
                # Maybe all ? or Automode ?
                self.ax25conn.resend_unACK_buf()
                self.ax25conn.set_T1()
        elif flag == 'I':
            self.ax25conn.set_T2()
            if ((nr - 1) % 8) in self.ax25conn.tx_buf_unACK.keys():
                self.ax25conn.del_unACK_buf()
                self.ax25conn.n2 = 0

            if ns == self.ax25conn.vr:  # !!!! Korrekt
                # Process correct I-Frame
                self.ax25conn.n2 = 0
                self.ax25conn.vr = count_modulo(int(self.ax25conn.vr))
                self.ax25conn.rx_buf_rawData += ax25_frame.data
                # CLI
                self.ax25conn.exec_cli(ax25_frame.data)
                # Debug Data Buffer
                self.ax25conn.rx_buf_rawData_2 += ax25_frame.data
                if self.stat_index == 7 and pf:
                    self.ax25conn.set_T1(stop=True)
                    self.ax25conn.send_RR(pf_bit=False, cmd_bit=False)
                    self.change_state(5)
                elif pf:
                    self.ax25conn.send_RR(pf_bit=True, cmd_bit=False)
                elif not self.ax25conn.tx_buf_unACK and \
                        not self.ax25conn.tx_buf_2send and \
                        not self.ax25conn.tx_buf_rawData:
                    self.ax25conn.send_RR(pf_bit=False, cmd_bit=False)
                    self.ax25conn.set_T1(stop=True)
                if self.stat_index == 6:  # return from REJ_state
                    self.change_state(5)

            else:  # !!!! Korrekt
                if self.stat_index in [5, 9]:
                    # REJ
                    """
                    print(" !!!!! TX REJ !!!! ")
                    print("ownVR: {}     recNR: {}".format(self.ax25conn.vr, nr))
                    print("ownVS: {}     recNS: {}".format(self.ax25conn.vs, ns))
                    """
                    if self.stat_index == 5:

                        if ns + 1 == self.ax25conn.vr:  # When Packet already is received
                            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
                            self.change_state(7)  # go into FINAL_state
                        else:

                            self.ax25conn.send_REJ(pf_bit=pf, cmd_bit=False)
                            self.change_state(6)  # go into REF_state
                        self.ax25conn.set_T1()
                    elif self.stat_index == 9:
                        self.change_state(15)  # go into "REJ ausgesandt u. Gegenstelle nicht bereit."
                elif self.stat_index in [10, 14]:
                    # TODO RNR
                    pass

    def tx(self, ax25_frame: AX25Frame):
        if time.time() > self.ax25conn.t1:
            if self.ax25conn.tx_buf_rawData:
                self.ax25conn.build_I_fm_raw_buf()

    def state_cron(self):
        # T1 Abgelaufen
        if time.time() > self.ax25conn.t2:
            if time.time() > self.ax25conn.t1:
                # Nach 5 Versuchen
                if self.ax25conn.n2:
                    if self.ax25conn.n2 > 5:
                        # BULLSHIT ?
                        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
                        self.ax25conn.set_T1()
                        self.change_state(7)  # S7 Warten auf Final
                    else:
                        if self.ax25conn.tx_buf_unACK:
                            # Nach 2 Versuchen nur noch einzelne Pakete senden
                            if self.ax25conn.n2 > 1:
                                self.ax25conn.resend_unACK_buf(1)
                                self.ax25conn.n2 += 1
                                self.ax25conn.set_T1()
                            else:
                                self.ax25conn.resend_unACK_buf()
                                self.ax25conn.n2 += 1
                                self.ax25conn.set_T1()
                                # Und neue Pakete gleich mit senden...
                                if self.ax25conn.tx_buf_rawData and not self.ax25conn.tx_buf_unACK:
                                    self.ax25conn.build_I_fm_raw_buf()

                else:
                    if self.ax25conn.tx_buf_unACK:
                        self.ax25conn.resend_unACK_buf()
                        self.ax25conn.n2 += 1
                        self.ax25conn.set_T1()
                    if self.ax25conn.tx_buf_rawData and not self.ax25conn.tx_buf_unACK:
                        self.ax25conn.build_I_fm_raw_buf()
                        self.ax25conn.set_T1()
        # T3 Abgelaufen
        if time.time() > self.ax25conn.t3 \
                and time.time() > self.ax25conn.t1:
            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self.ax25conn.set_T1()
            self.change_state(7)  # S7 Warten auf Final


class S6sendREJ(S5Ready):
    """Copy of S5Ready"""
    stat_index = 6  # REJ ausgesandt

    def tx(self, ax25_frame: AX25Frame):
        pass

    def state_cron(self):
        # T1 Abgelaufen
        if time.time() > self.ax25conn.t1 or \
                time.time() > self.ax25conn.t3:
            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self.ax25conn.n2 += 1
            self.ax25conn.set_T1()
            self.change_state(7)  # S7 Warten auf Final
        # TODO if n2 > parm_N2


class S7WaitForFinal(S5Ready):
    stat_index = 7  # Warten auf Final
    """
    def rx(self, ax25_frame: AX25Frame):
        flag = ax25_frame.ctl_byte.flag
        if flag == 'RR':
            c_byte = ax25_frame.ctl_byte
            pf = c_byte.pf
            nr = c_byte.nr
            if ((nr - 1) % 8) in self.ax25conn.tx_buf_unACK.keys():
                self.ax25conn.del_unACK_buf()
            if pf:
                self.ax25conn.set_T1(stop=True)
                self.ax25conn.n2 = 0
                self.change_state(5)
            else:
                # Unexpected
                logger.error("Unexpected RR Frame Received in S7. No Final")
                print(" !!!!! Unexpected RR - S7!!!! ")
                print("ownVR: {}     recNR: {}".format(self.ax25conn.vr, nr))
    """

    def state_cron(self):
        # T1 Abgelaufen
        if time.time() > self.ax25conn.t1:
            self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
            self.ax25conn.n2 += 1
            self.ax25conn.set_T1()
        # TODO if n2 > parm_N2
