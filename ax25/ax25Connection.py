"""
    Layer 3 ??
    AX.25 PROT Packet Handling
"""
import time
from datetime import datetime

import cli.cliMain
import config_station
from UserDB.UserDBmain import USER_DB
from ax25.ax25dec_enc import AX25Frame
from fnc.ax25_fnc import reverse_uid
from ax25.ax25FileTransfer import FileTransport, ft_rx_header_lookup
from fnc.loc_fnc import locator_distance


def count_modulo(inp: int):
    return (inp + 1) % 8


class RTT(object):
    def __init__(self, connection):
        self.conn = connection
        self.act_paclen = self.conn.parm_PacLen
        self.rtt_dict: {int: float} = {}
        self.rtt_best = 999.0
        self.rtt_worst = 0.0
        self.rtt_average = float(self.conn.IRTT / 1000) / 2
        self.rtt_last = 0.0
        self.rtt_single_timer = 0.0
        for i in range(8):
            self.rtt_dict[i] = {
                'timer': 0.0,
                'paclen': int(self.act_paclen),
                'rtt': self.rtt_average
            }
        # self.rtt_single_list = [float(self.rtt_average)]*4
        self.rtt_single_list = []

    def _get_rtt_avrg(self):
        self._calc_rtt_vars()
        if self.rtt_best == 999:
            return self.rtt_average
        else:
            return (self.rtt_average + self.rtt_best) / 2

    def _set_rtt_timer(self, vs: int, paclen: int):
        self.rtt_dict[vs]['timer'] = time.time()
        self.rtt_dict[vs]['paclen'] = paclen
        # print('set {}'.format(self.rtt_dict))

    def _set_rtt_single_timer(self):
        self.rtt_single_timer = time.time()

    def _rtt_single_rx(self, stop=False):
        if stop:
            self.rtt_single_timer = 0.0
        if self.rtt_single_timer:
            # rtt = float(((time.time() - self.rtt_single_timer) / 2) / 16) * self.act_paclen
            rtt = (time.time() - self.rtt_single_timer) * 1.3
            self.rtt_single_list[0] = rtt
            self.rtt_single_list = self.rtt_single_list[1:] + [self.rtt_single_list[0]]
            self.rtt_single_timer = 0.0
        # print("RTT-S: {}".format(self.rtt_single_list))

    def _rtt_rx(self, vs: int):
        # print('RX {}' .format(self.rtt_dict))
        timer = float(self.rtt_dict[vs]['timer'])
        if timer:
            self.rtt_dict[vs]['rtt'] = time.time() - timer
        self.rtt_last = float(self.rtt_dict[vs]['rtt'])
        self._calc_rtt_vars()
        # print('RX rtt_last {}'.format(self.rtt_last))
        # print('RX rtt_best {}'.format(self.rtt_best))
        # print('RX rtt_worst {}'.format(self.rtt_worst))
        # print('RX rtt_average {}'.format(self.rtt_average))
        return self.rtt_last

    def _calc_rtt_vars(self):
        # print('_________calc_rtt____________')
        self.rtt_best = min(self.rtt_last, self.rtt_best)
        self.rtt_worst = max(self.rtt_last, self.rtt_worst)
        tmp = list(self.rtt_single_list)
        # print("tmp: {}".format(tmp))
        for vs in self.rtt_dict.keys():
            if self.rtt_dict[vs]['rtt']:
                # tmp_len = self.rtt_dict[vs]['paclen'] + 16
                # rtt = float((self.rtt_dict[vs]['rtt'] / 2) / tmp_len) * self.act_paclen
                rtt = self.rtt_dict[vs]['rtt']
                # print("rtt: {}".format(tmp))
                tmp.append(rtt)
        self.rtt_average = sum(tmp) / len(tmp)

        # print("rtt_average: {}".format(self.rtt_average))
        # print('------------------------')


class AX25Conn(object):
    def __init__(self, ax25_frame: AX25Frame, cfg, port, rx=True):
        """ AX25 Connection class """
        """ Global Stuff """
        self.own_port = port
        self.port_handler = self.own_port.port_handler
        """ GUI Stuff"""
        self.ch_index: int = 0  # Set in insert_conn2all_conn_var()
        self.port_id: int = self.own_port.port_id
        self.port_name: str = self.own_port.portname
        self.gui = self.port_handler.gui
        # self.ChVars = None
        """ Ch-Echo"""
        self.ch_echo: [AX25Conn] = []
        """ Config new Connection Address """
        # AX25 Frame for Connection Initialisation.
        self.ax25_out_frame = AX25Frame()  # Predefined AX25 Frame for Output
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
            ax25_frame.encode_ax25frame()  # Set Stop-Bits and H-Bits while encoding
            if self.ax25_out_frame.addr_uid != ax25_frame.addr_uid:
                self.ax25_out_frame.addr_uid = ax25_frame.addr_uid  # Unique ID for Connection
        self.my_call_obj = self.ax25_out_frame.from_call
        self.my_call_str = self.my_call_obj.call_str
        self.my_call_alias = ''
        self.my_locator = ''
        self.to_call_str = str(self.ax25_out_frame.to_call.call_str)
        self.to_call_alias = ''
        self.uid = str(self.ax25_out_frame.addr_uid)
        self.stat_cfg = config_station.DefaultStation()
        if self.my_call_str in self.port_handler.ax25_stations_settings.keys():
            self.stat_cfg = self.port_handler.ax25_stations_settings[self.my_call_str]
        else:
            for call in list(self.port_handler.ax25_stations_settings.keys()):
                if self.my_call_obj.call in call:
                    if self.my_call_obj.call in self.port_handler.ax25_stations_settings.keys():
                        self.stat_cfg = self.port_handler.ax25_stations_settings[self.my_call_obj.call]
                        break
        self.my_locator = self.stat_cfg.stat_parm_LOC
        """ IO Buffer Packet For Handling """
        self.tx_buf_ctl: [AX25Frame] = []  # Buffer for CTL ( S ) Frame to send on next Cycle
        self.tx_buf_2send: [AX25Frame] = []  # Buffer for Sending. Will be processed in ax25PortHandler
        self.tx_buf_unACK: {int: AX25Frame} = {}  # Buffer for UNACK I-Frames
        self.rx_buf_last_frame = ax25_frame  # Buffers for last Frame !?!
        self.rx_buf_last_data = b''  # Buffers for last Frame !?!
        """ IO Buffer For GUI / CLI """
        self.tx_buf_rawData: b'' = b''  # Buffer for TX RAW Data that will be packed into a Frame
        self.tx_buf_guiData: b'' = b''  # Buffer for TX Echo in GUI
        self.rx_buf_rawData: b'' = b''  # Received Data for GUI
        """ DIGI / Link to other Connection for Auto processing """
        self.LINK_Connection = None
        self.LINK_rx_buff: b'' = b''
        self.is_link = False
        self.is_link_remote = False
        # self.rx_buf_rawData_2: b'' = b''        # Received Data TEST Script
        """ Port Variablen"""
        self.vs = 0  # Sendefolgenummer     / N(S) = V(R)  TX
        self.vr = 0  # Empfangsfolgezählers / N(S) = V(R)  TX
        self.t1 = 0  # ACK
        self.t2 = 0  # Respond Delay
        self.t3 = 0  # Connection Hold
        self.n2 = 0  # Fail Counter / No Response Counter
        """ Port Config Parameter """
        self.cfg = cfg
        self.parm_PacLen = self.cfg.parm_PacLen  # Max Pac len
        self.parm_MaxFrame = self.cfg.parm_MaxFrame  # Max (I) Frames
        self.parm_TXD = self.cfg.parm_TXD  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
        self.parm_Kiss_TXD = 0
        self.parm_Kiss_Tail = 0
        if self.own_port.kiss.is_enabled:
            self.parm_Kiss_TXD = self.own_port.port_cfg.parm_kiss_TXD
            self.parm_Kiss_Tail = self.own_port.port_cfg.parm_kiss_Tail
        self.parm_T2 = int(self.cfg.parm_T2)  # T2 (Response Delay Timer) Default: 2888 / (parm_baud / 100)
        self.parm_T3 = self.cfg.parm_T3  # T3 (Inactive Link Timer)
        self.parm_N2 = self.cfg.parm_N2  # Max Try   Default 20
        self.parm_baud = self.cfg.parm_baud  # Baud for calculating Timer
        """ Timer Calculation & other Data for Statistics"""
        self.IRTT = 0
        self.RTT = 0
        self.calc_irtt()
        self.RTT_Timer = RTT(self)
        self.tx_byte_count = 0
        self.rx_byte_count = 0
        """ Connection Start Time """
        self.time_start = datetime.now()
        """ Zustandstabelle / Statechart """
        self.zustand_tab = {
            0: (DefaultStat, 'ENDE'),
            1: (S1Frei, 'FREI'),
            2: (S2Aufbau, 'AUFBAU'),
            3: (S3sendFRMR, 'FRMR'),
            4: (S4Abbau, 'ABBAU'),
            5: (S5Ready, 'BEREIT'),
            6: (S6sendREJ, 'REJ'),
            7: (S7WaitForFinal, 'FINAL'),
            8: (S8SelfNotReady, 'RNR'),
            9: (S9DestNotReady, 'DEST-RNR'),
            10: (S10BothNotReady, 'BOTH-RNR'),
            11: (S11SelfNotReadyFinal, 'RNR-F'),
            12: (S12DestNotReadyFinal, 'DEST-RNR-F'),
            13: (S13BothNotReadyFinal, 'BOTH-RNR-F'),
            14: (S14sendREJselfNotReady, 'RNR-REJ'),
            15: (S15sendREJdestNotReady, 'DEST-RNR-REJ'),
            16: (S16sendREJbothNotReady, 'BOTH-RNR-REJ'),
        }
        """ S-Packet / CTL Vars"""
        self.REJ_is_set: bool = False
        self.is_RNR: bool = False
        """ File Transfer Stuff """
        self.ft_queue: [FileTransport] = []
        self.ft_obj = None
        """ Pipe-Tool """
        self.pipe = None
        """ Link Holder / Not related to Link Connection Stuff """
        self.link_holder_on: bool = False
        self.link_holder_interval: int = 30  # Minutes
        self.link_holder_timer = time.time()
        self.link_holder_text: str = '\r'
        """ Encoding """
        self.encoding = 'CP437'     # 'UTF-8'
        """ User DB Entry """
        self.user_db_ent = False
        self.cli_language = 0
        self.set_user_db_ent()
        """ Station Individual Parameter """
        self.set_packet_param()
        """ Init CLI """
        self.cli = cli.cliMain.NoneCLI(self)
        self.cli_type = ''
        if self.stat_cfg.stat_parm_pipe is None:
            self.init_cli()
            if not rx:
                self.cli.change_cli_state(state=1)
        else:
            """ Init Pipe """
            self.pipe = self.stat_cfg.stat_parm_pipe(
                port_id=self.own_port.port_id,
                own_call=self.my_call_str,
                address_str='NOCALL',
            )
            self.pipe.connection = self
            self.pipe.change_settings()
        """ Init State Tab """
        if rx:
            self.set_T1()
            self.set_T3()
            self.zustand_exec = S1Frei(self)
            self.handle_rx(ax25_frame)
        else:
            self.zustand_exec = S2Aufbau(self)
            # self.cli.change_cli_state(state=1)

    def __del__(self):
        del self.ax25_out_frame
        del self.zustand_exec

    ##################
    # CLI INIT
    def init_cli(self):
        if self.stat_cfg.stat_parm_Call in self.cfg.parm_cli.keys():
            del self.cli
            # self.cli = self.cfg.parm_cli[self.stat_cfg.stat_parm_Call](self)
            # print(f"CLI INIT : {self.cfg.parm_cli[self.stat_cfg.stat_parm_Call]}")
            self.cli = cli.cliMain.CLI_OPT[self.cfg.parm_cli[self.stat_cfg.stat_parm_Call]](self)
            self.cli_type = self.cli.cli_name
            # print(f"CLI INIT typ: {self.cli.cli_name}")
            self.cli.build_prompt()
        """
        else:
            self.cli = cli.cli.NoneCLI(self)
        """

    def reinit_cli(self):
        print("CLI RE-INIT")
        if self.stat_cfg.stat_parm_pipe is None:
            self.init_cli()
            self.cli.change_cli_state(state=1)

    ####################
    # Zustand EXECs
    def handle_rx(self, ax25_frame: AX25Frame):
        self.rx_buf_last_frame = ax25_frame
        self.zustand_exec.state_rx_handle(ax25_frame=ax25_frame)
        if ax25_frame.data:
            self.rx_buf_last_data = ax25_frame.data
        self.set_T3()

    def handle_tx(self, ax25_frame: AX25Frame):
        """ Not used... TX is handled by cron """
        self.zustand_exec.tx(ax25_frame=ax25_frame)

    def send_data(self, data, file_trans=False):
        if self.ft_obj is not None and not file_trans:
            return False
        if data:
            if type(data) == bytes:
                self.link_holder_reset()
                self.tx_buf_rawData += data
                return True
        return False

    def recv_data(self, data: b'', file_trans=False):
        self.vr = count_modulo(int(self.vr))
        # self.ch_echo_frm_rx(data)   # TODO
        # Statistic
        self.rx_byte_count += len(data)
        if self.is_link:
            self.LINK_rx_buff += data
            return
        # Pipe-Tool
        if self.pipe_rx(data):
            return
        self.ft_check_incoming_ft(data)
        if self.ft_handle_rx(data):
            return

        self.rx_buf_rawData += data
        # Station ( RE/DISC/Connect ) Sting Detection
        self.set_dest_call_fm_data_inp(data)
        # CLI
        self.exec_cli(data)
        return

    def send_gui_echo(self, data):
        if self.ft_obj is not None:
            return
        if self.pipe is not None:
            return
        self.tx_buf_guiData += data

    def set_dest_call_fm_data_inp(self, raw_data: b''):
        # TODO AGAIN !!
        if b'*** ' not in raw_data:
            return
        for _det_str in [
            b'*** connected to',
            b'*** reconnected to'
        ]:
            if _det_str in raw_data.lower():
                _index = raw_data.lower().index(_det_str) + len(_det_str)
                raw_data = raw_data.decode('ASCII', 'ignore')
                _tmp_call = raw_data[_index:]
                _tmp_call = _tmp_call.split('\r')
                _cut_str = _tmp_call[1:]
                if ':' in _tmp_call[0]:
                    _tmp_call = _tmp_call[0].split(':')
                    self.to_call_str = _tmp_call[1].replace(' ', '')
                    self.to_call_alias = _tmp_call[0].replace(' ', '')
                else:
                    self.to_call_str = _tmp_call[0].replace(' ', '')
                    self.to_call_alias = ''
                if self.gui is not None:
                    speech = ' '.join(self.to_call_str.replace('-', ' '))
                    self.gui.sprech(speech)
                self.tx_byte_count = 0
                self.rx_byte_count = 0
                self.set_user_db_ent()
                self.set_packet_param()
                self.reinit_cli()
                if self.gui is not None:
                    self.gui.on_channel_status_change()
                # Maybe it's better to look at the whole string (include last frame)?
                return
        return

    def set_user_db_ent(self):
        self.user_db_ent = USER_DB.get_entry(self.to_call_str)
        if self.user_db_ent:
            self.user_db_ent.Connects += 1  # TODO Count just when connected
            self.user_db_ent.last_seen = datetime.now()
            self.encoding = self.user_db_ent.Encoding
            if self.user_db_ent.Language == -1:
                if self.gui is None:
                    self.user_db_ent.Language = 0
                else:
                    self.user_db_ent.Language = int(self.gui.language)
            self.cli_language = self.user_db_ent.Language
            self.set_distance()

    def set_user_db_language(self, lang_ind: int):
        self.user_db_ent.Language = int(lang_ind)
        self.cli_language = int(lang_ind)

    def set_distance(self):
        if self.user_db_ent:
            if self.my_locator and self.user_db_ent.LOC:
                self.user_db_ent.Distance = locator_distance(self.my_locator, self.user_db_ent.LOC)

    def set_packet_param(self):
        self.parm_PacLen = self.cfg.parm_PacLen  # Max Pac len
        self.parm_MaxFrame = self.cfg.parm_MaxFrame  # Max (I) Frames
        self.user_db_ent = USER_DB.get_entry(self.to_call_str)
        stat_call = self.stat_cfg.stat_parm_Call

        if self.user_db_ent:
            if int(self.user_db_ent.pac_len):
                self.parm_PacLen = int(self.user_db_ent.pac_len)
            elif stat_call != config_station.DefaultStation.stat_parm_Call:
                if stat_call in self.cfg.parm_stat_PacLen.keys():
                    if self.cfg.parm_stat_PacLen[stat_call]:  # If 0 then default port param
                        self.parm_PacLen = self.cfg.parm_stat_PacLen[stat_call]  # Max Pac len

            if int(self.user_db_ent.max_pac):
                self.parm_MaxFrame = int(self.user_db_ent.max_pac)
            elif stat_call != config_station.DefaultStation.stat_parm_Call:
                if stat_call in self.cfg.parm_stat_MaxFrame.keys():
                    if self.cfg.parm_stat_MaxFrame[stat_call]:  # If 0 then default port param
                        self.parm_MaxFrame = self.cfg.parm_stat_MaxFrame[stat_call]  # Max Pac

        else:
            stat_call = self.stat_cfg.stat_parm_Call
            if stat_call != config_station.DefaultStation.stat_parm_Call:
                if stat_call in self.cfg.parm_stat_PacLen.keys():
                    if self.cfg.parm_stat_PacLen[stat_call]:  # If 0 then default port param
                        self.parm_PacLen = self.cfg.parm_stat_PacLen[stat_call]  # Max Pac len
                if stat_call in self.cfg.parm_stat_MaxFrame.keys():
                    if self.cfg.parm_stat_MaxFrame[stat_call]:  # If 0 then default port param
                        self.parm_MaxFrame = self.cfg.parm_stat_MaxFrame[stat_call]  # Max Pac

    def exec_cron(self):
        """ DefaultStat.cron() """
        # print(self.ch_index)
        if not self.pipe_crone():
            if not self.ft_cron():
                self.cli.cli_cron()
                self.link_holder_cron()
        self.zustand_exec.cron()
        ########################################
        # DIGI / LINK Connection / Node Funktion
        self.link_crone()
        if self.zustand_exec.stat_index == 0:
            self.conn_cleanup()

    #############################
    # Proto PIPE
    def pipe_crone(self):
        if self.pipe is None:
            return False
        self.pipe.crone_exec()
        return True

    def pipe_rx(self, raw_data: b''):
        if self.pipe is not None:
            self.pipe.handle_rx_rawdata(raw_data)
            return True
        return False

    def set_pipe(self, pipe):
        self.pipe = pipe
        if self.pipe.parm_pac_len:
            self.parm_PacLen = int(self.pipe.parm_pac_len)
        if self.pipe.parm_max_pac:
            self.parm_MaxFrame = int(self.pipe.parm_max_pac)

    ########################################
    # File Transfer
    def ft_check_incoming_ft(self, data):
        if self.ft_obj is None:
            ret = ft_rx_header_lookup(data=data, last_pack=self.rx_buf_last_data)
            if ret:
                self.ft_obj = ret
                self.ft_obj.connection = self

    def ft_handle_rx(self, data: b''):
        if self.ft_obj is None:
            return False
        return self.ft_obj.ft_rx(data)

    def ft_cron(self):
        if self.ft_queue_handling():
            if self.gui is not None:
                self.gui.on_channel_status_change()
            return self.ft_obj.ft_crone()
        return False

    def ft_queue_handling(self):
        if self.ft_obj is not None:
            self.ft_obj: FileTransport
            # if self.ft_obj.pause:
            #     return False
            if self.ft_obj.done:
                print(f"FT Done - rest: {self.ft_obj.ft_rx_buf}")
                self.rx_buf_rawData += bytes(self.ft_obj.ft_rx_buf)
                self.ft_obj = None
                if self.ft_queue:
                    self.ft_obj = self.ft_queue[0]
                    self.ft_queue = self.ft_queue[1:]
                    return True
                return False
            return True

        if self.ft_queue:
            self.ft_obj = self.ft_queue[0]
            self.ft_queue = self.ft_queue[1:]
            return True
        return False

    def ft_reset_timer(self, conn_uid: str):
        if self.ft_obj is not None:
            if conn_uid != self.uid and reverse_uid(conn_uid) != self.uid:
                self.ft_obj.ft_set_wait_timer()

    #######################
    # Link Holder
    def link_holder_reset(self):
        if self.link_holder_on:
            self.link_holder_timer = time.time() + (self.link_holder_interval * 60)

    def link_holder_cron(self):
        if self.link_holder_on:
            if self.link_holder_timer < time.time():
                self.link_holder_timer = time.time() + (self.link_holder_interval * 60)
                self.tx_buf_rawData += self.link_holder_text.encode(self.encoding, 'ignore')

    def set_RNR(self, link_remote=False):
        if not self.is_RNR:
            self.send_RNR()
            self.set_T1(stop=True)
            self.set_T3()
            self.is_RNR = True
            if self.zustand_exec.stat_index == 5:
                self.zustand_exec.change_state(8)
            elif self.zustand_exec.stat_index == 6:
                self.zustand_exec.change_state(14)
            elif self.zustand_exec.stat_index == 7:
                self.zustand_exec.change_state(11)
            elif self.zustand_exec.stat_index == 9:
                self.zustand_exec.change_state(10)
            elif self.zustand_exec.stat_index == 12:
                self.zustand_exec.change_state(13)
            elif self.zustand_exec.stat_index == 15:
                self.zustand_exec.change_state(16)
            """
            if self.LINK_Connection is not None and not link_remote:
                self.LINK_Connection.set_RNR(link_remote=True)
            """

    def unset_RNR(self, link_remote=False):
        if self.is_RNR:
            self.is_RNR = False
            self.send_RR()
            self.set_T1()
            # self.set_T3(stop=True)
            if self.zustand_exec.stat_index == 8:
                self.zustand_exec.change_state(5)
            elif self.zustand_exec.stat_index == 10:
                self.zustand_exec.change_state(9)
            elif self.zustand_exec.stat_index == 11:
                self.zustand_exec.change_state(7)
            elif self.zustand_exec.stat_index == 13:
                self.zustand_exec.change_state(12)
            elif self.zustand_exec.stat_index == 14:
                self.zustand_exec.change_state(6)
            elif self.zustand_exec.stat_index == 16:
                self.zustand_exec.change_state(15)
            """
            if self.LINK_Connection is not None and not link_remote:
                self.LINK_Connection.unset_RNR(link_remote=True)
            """

    # Zustand EXECs ENDE
    #######################

    #######################
    # LINKS Linked Connections
    def link_crone(self):
        if self.is_link and self.LINK_Connection is not None:
            self.LINK_Connection.tx_buf_rawData += bytes(self.LINK_rx_buff)
            self.LINK_rx_buff = b''
            self.tx_buf_rawData += bytes(self.LINK_Connection.LINK_rx_buff)
            self.LINK_Connection.LINK_rx_buff = b''

    def link_connection(self, conn):
        conn: AX25Conn
        if conn is None:
            return False
        if conn.uid in self.port_handler.link_connections.keys():
            conn.zustand_exec.change_state(4)
            conn.zustand_exec.tx(None)
            return False
        if self.is_link_remote:
            self.my_call_str = str(conn.my_call_str)
            self.ax25_out_frame.digi_call = str(conn.my_call_str)
            self.port_handler.link_connections[str(conn.uid)] = conn, ''
        else:
            self.port_handler.link_connections[str(conn.uid)] = conn, self.my_call_str

        self.LINK_Connection = conn
        self.is_link = True
        self.cli = cli.cliMain.NoneCLI(self)  # Disable CLI

        return True

    def link_disco(self):
        if self.is_link and self.LINK_Connection is not None:
            if self.LINK_Connection.zustand_exec.stat_index == 1:
                # self.LINK_Connection.n2 = 100
                self.LINK_Connection.set_T1(stop=True)
                self.LINK_Connection.zustand_exec.change_state(0)
            else:
                if not self.is_link_remote:
                    # print(f'LINK DISCO : {self.uid}')
                    self.LINK_Connection.zustand_exec.change_state(4)
                    self.LINK_Connection.zustand_exec.tx(None)
                else:
                    self.port_handler.del_link(self.LINK_Connection.uid)
                    self.LINK_Connection.tx_buf_rawData += '\r*** Reconnected to {}\r'.format(self.my_call_str).encode('ASCII', 'ignore')
                    self.LINK_Connection.del_link()
                    self.LINK_Connection.init_cli()
                    self.LINK_Connection.cli.change_cli_state(state=1)
                    self.LINK_Connection.cli.send_prompt()
                    # self.LINK_Connection.cli.build_prompt()

    def link_send_to(self, inp: b''):
        if inp:
            if self.is_link:
                self.LINK_Connection.tx_buf_rawData += inp

    def del_link(self):
        """ Called in State.link_cleanup() """
        if self.LINK_Connection is not None:
            # print(f'LINK CLEANUP link_connections K : {self.port_handler.link_connections.keys()}')
            self.LINK_Connection = None
            self.is_link = False
        self.port_handler.del_link(self.uid)

    def link_cleanup(self):
        # self.link_disco()
        self.del_link()
        # self.port_handler.del_link(self.uid)

    # ##############
    # DISCO
    def conn_disco(self):
        if self.zustand_exec.stat_index:
            self.set_T1(stop=True)
            self.zustand_exec.tx(None)
            if self.zustand_exec.stat_index in [2, 4]:
                self.zustand_exec.S1_end_connection()
            else:
                self.zustand_exec.change_state(4)

    def conn_cleanup(self):
        # print(f"conn_cleanup: {self.uid}\n"
        #       f"state: {self.zustand_exec.stat_index}\n")
        self.link_cleanup()
        self.port_handler.del_conn2all_conn_var(self)   # Doppelt ..
        self.own_port.del_connections(conn=self)

    def end_connection(self):
        # print(f"end_connection: {self.uid}")
        self.link_disco()
        #self.n2 = 1
        self.set_T1()
        self.vr = 0
        self.vs = 0
        self.init_cli()
        # self.zustand_exec.change_state(0)
        """ !!!!!!!!! """
        """
        c = 0
        while c < 5 and self.rx_buf_rawData:
            # TODO Not Happy
            time.sleep(0.1)
            c += 1
        """
        # self.ax25conn.link_cleanup()
        self.port_handler.del_conn2all_conn_var(self)

    ###############################################
    # Channel ECHO  # TODO Again !
    def ch_echo_add(self, ax25_connection):
        if ax25_connection not in self.ch_echo:
            self.ch_echo.append(ax25_connection)

    def ch_echo_del(self, ax25_connection):
        if ax25_connection in self.ch_echo:
            self.ch_echo.remove(ax25_connection)

    def ch_echo_frm_tx(self, inp: b''):
        if inp:
            tag = '\r<CH-ECHO> CH: '
            if tag.encode(self.encoding, 'ignore') not in inp:
                echo_str = '\r{}{} - {}>\r'.format(tag, self.ch_index, self.my_call_str)
                inp = echo_str.encode(self.encoding, 'ignore') + inp
                for conn in self.ch_echo:
                    if conn.ch_index != self.ch_index:
                        conn.tx_buf_rawData += inp

    def ch_echo_frm_rx(self, inp: b''):
        if inp:
            tag = '\r<CH-ECHO> CH: '
            if tag.encode(self.encoding, 'ignore') not in inp:
                echo_str = '\r{}{} - {}>\r'.format(tag, self.ch_index, self.to_call_str)
                inp = echo_str.encode(self.encoding, 'ignore') + inp
                for conn in self.ch_echo:
                    if conn.ch_index != self.ch_index:
                        conn.tx_buf_rawData += inp

    ###############################################
    ###############################################
    # Timer usw
    def get_rtt(self):
        auto = False  # TODO
        self.calc_irtt()
        if auto:
            return self.RTT_Timer._get_rtt_avrg() * 1000
        else:
            return self.IRTT

    def calc_irtt(self):
        if self.own_port.port_cfg.parm_T2_auto:
            init_t2: float = (((self.parm_PacLen + 16) * 8) / self.parm_baud) * 1000
            self.IRTT = (init_t2 +
                         self.parm_TXD +
                         (self.parm_Kiss_TXD * 10) +
                         (self.parm_Kiss_Tail * 10)
                         ) * 2
            # self.parm_T2 = (float(self.IRTT / 1000) / 2)
            # TXD    TAIL
            self.parm_T2 = float(init_t2 + 400 + 150) / 1000
        else:
            self.parm_T2 = int(self.cfg.parm_T2) / 1000
            self.IRTT = ((self.parm_T2 * 1000) +
                         self.parm_TXD +
                         (self.parm_Kiss_TXD * 10) +
                         (self.parm_Kiss_Tail * 10)
                         ) * 2
        # print('parm_T2: {}'.format(self.parm_T2))
        self.IRTT = max(self.IRTT, 300)  # TODO seems not right!!!!!!!!!!!!!!!!!!!!
        # print('IRTT: {}'.format(self.IRTT))

    def set_T1(self, stop=False):
        if stop:
            self.n2 = 0
            self.t1 = 0
        else:
            self.calc_irtt()
            n2 = int(self.n2)
            srtt = float(self.get_rtt())
            if not self.own_port.port_cfg.parm_T2_auto:
                if self.ax25_out_frame.via_calls:
                    srtt = int((len(self.ax25_out_frame.via_calls) * 2 + 1) * srtt)
            if n2 > 3:
                self.t1 = float(((srtt * (n2 + 4)) / 1000) + time.time())
            else:
                self.t1 = float(((srtt * 3) / 1000) + time.time())
        """
        if self.t1 > 0:
            print('t1 > {}'.format(self.t1 - time.time()))
        """

    def set_T2(self, stop=False, link_remote=False):
        if self.cfg.parm_full_duplex:
            self.t2 = 0
        else:
            if stop:
                self.t2 = 0
            else:
                self.t2 = float(self.parm_T2 + time.time())
                if self.is_link and not link_remote:
                    if self.own_port == self.LINK_Connection.own_port:
                        self.LINK_Connection.set_T2(link_remote=True)

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
                # RTT
                self.RTT_Timer._rtt_rx(i)

    def resend_unACK_buf(self, max_pac=None):
        if max_pac is None:
            max_pac = self.parm_MaxFrame
        index_list = list(self.tx_buf_unACK.keys())
        for i in range(min(max_pac, len(index_list))):
            pac: AX25Frame = self.tx_buf_unACK[index_list[i]]
            pac.ctl_byte.nr = self.vr
            self.tx_buf_2send.append(pac)

    def exec_cli(self, inp=b''):
        """ CLI Processing like sending C-Text ... """
        if self.ft_obj is not None:
            return False
        if self.is_link:
            return False
        if self.pipe is not None:
            return False
        self.cli.cli_exec(inp)
        return True

    def cron_cli(self):
        """ CLI Processing like sending C-Text ... """
        if self.ft_obj is not None:
            return False
        if self.is_link:
            return False
        if self.pipe is not None:
            return False
        self.cli.cli_cron()
        return True

    def init_new_ax25frame(self):
        pac = AX25Frame()
        pac.from_call = self.ax25_out_frame.from_call
        pac.to_call = self.ax25_out_frame.to_call
        pac.via_calls = list(self.ax25_out_frame.via_calls)
        pac.addr_uid = str(self.ax25_out_frame.addr_uid)
        pac.axip_add = tuple(self.ax25_out_frame.axip_add)
        pac.digi_call = str(self.ax25_out_frame.digi_call)  # Link Call
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
        # A bit of Mess TODO Try to Cleanup
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
            self.send_gui_echo(self.tx_buf_rawData[:pac_len])
            # self.tx_buf_guiData += self.tx_buf_rawData[:pac_len]  # GUI Echo
            self.ch_echo_frm_tx(self.tx_buf_rawData[:pac_len])  # CH ECHO
            self.tx_buf_rawData = self.tx_buf_rawData[pac_len:]
            self.tx_buf_unACK[int(self.vs)] = self.ax25_out_frame  # Keep Packet until ACK/RR
            self.tx_buf_2send.append(self.ax25_out_frame)
            # RTT
            self.RTT_Timer._set_rtt_timer(int(self.vs), int(pac_len))
            # !!! COUNT VS !!!
            self.vs = count_modulo(int(self.vs))  # Increment VS Modulo 8
            self.set_T1()  # Re/Set T1
            # Statistics
            self.tx_byte_count += int(pac_len)

    def send_UA(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.UAcByte()
        self.tx_buf_ctl.append(self.ax25_out_frame)
        self.set_T3()

    def send_DM(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.DMcByte()
        self.tx_buf_ctl.append(self.ax25_out_frame)

    def send_DISC(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.DISCcByte()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_SABM(self):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.SABMcByte()
        self.tx_buf_2send.append(self.ax25_out_frame)

    def send_RR(self, pf_bit=False, cmd_bit=False):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        self.ax25_out_frame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        self.ax25_out_frame.ctl_byte.nr = self.vr  # Receive PAC Counter
        self.ax25_out_frame.ctl_byte.RRcByte()
        if not self.REJ_is_set:
            self.tx_buf_ctl = [self.ax25_out_frame]

    def send_REJ(self, pf_bit=False, cmd_bit=False):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        self.ax25_out_frame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        self.ax25_out_frame.ctl_byte.nr = self.vr  # Receive PAC Counter
        self.ax25_out_frame.ctl_byte.REJcByte()
        self.tx_buf_ctl = [self.ax25_out_frame]
        self.REJ_is_set = True

    def send_RNR(self, pf_bit=False, cmd_bit=False):
        self.init_new_ax25frame()
        self.ax25_out_frame.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        self.ax25_out_frame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        self.ax25_out_frame.ctl_byte.nr = self.vr  # Receive PAC Counter
        self.ax25_out_frame.ctl_byte.RNRcByte()
        self.tx_buf_ctl = [self.ax25_out_frame]
        # ??? if not self.REJ_is_set:
        # self.REJ_is_set = True


class DefaultStat(object):
    stat_index = 0  # ENDE Verbindung wird gelöscht...

    def __init__(self, ax25_conn: AX25Conn):
        self.ax25conn = ax25_conn
        self.frame = None
        # Incoming Frame
        self.nr = 0
        self.ns = 0
        self.pf = False
        self.cmd = False

    def __del__(self):
        # Change stat to 0 And disc
        pass

    def change_state(self, zustand_id=1):
        self.ax25conn.zustand_exec = self.ax25conn.zustand_tab[zustand_id][0](self.ax25conn)
        if self.ax25conn.port_handler.gui is not None:
            # if self.ax25conn.is_gui:
            self.ax25conn.port_handler.gui.ch_status_update()

    def state_rx_handle(self, ax25_frame: AX25Frame):
        self.frame = ax25_frame
        self.nr = self.frame.ctl_byte.nr
        self.ns = self.frame.ctl_byte.ns
        self.pf = self.frame.ctl_byte.pf
        self.cmd = self.frame.ctl_byte.cmd
        {
            'SABM': self.rx_SABM,
            'DISC': self.rx_DISC,
            'UA': self.rx_UA,
            'DM': self.rx_DM,
            'RR': self.rx_RR,
            'RNR': self.rx_RNR,
            'REJ': self.rx_REJ,
            'I': self.rx_I,
            'FRMR': self.rx_FRMR,
            'UI': self.rx_UI,
        }[self.frame.ctl_byte.flag]()

    def rx_SABM(self):
        self.cleanup()

    def rx_UI(self):
        pass

    def rx_DISC(self):
        """UA, wenn der DISC-Block ohne Poll empfangen wurde."""
        if self.cmd:
            self.ax25conn.send_UA()
        elif not self.pf:
            self.ax25conn.send_UA()
        self.S1_end_connection()

    def rx_UA(self):
        if self.stat_index:
            self.ax25conn.send_SABM()
            self.ax25conn.set_T1()
            self.change_state(2)

    def rx_DM(self):
        if self.stat_index:
            self.ax25conn.send_SABM()
            self.ax25conn.set_T1()
            self.change_state(2)

    def rx_RR(self):
        pass

    def rx_RNR(self):
        pass

    def rx_REJ(self):
        pass

    def rx_I(self):
        if self.stat_index:
            self.ax25conn.set_T1(stop=True)
            self.prozess_I_frame()

    def rx_FRMR(self):
        if self.stat_index:
            self.ax25conn.send_DISC()
            self.ax25conn.set_T1()
            self.change_state(4)

    def tx(self, ax25_frame: AX25Frame):
        pass

    def send_to_link(self, inp: b''):
        self.ax25conn.link_send_to(inp)

    def state_cron(self):
        pass

    def cron(self):
        """Global Cron"""
        # TODO Move up
        ###########
        # TODO Connection Timeout
        # if self.stat_index:
        if self.ax25conn.n2 > self.ax25conn.parm_N2:
            self.n2_fail()
        else:
            if time.time() > self.ax25conn.t1:
                self.t1_fail()
            if time.time() > self.ax25conn.t3:
                self.t3_fail()
        self.state_cron()  # State Cronex
        """
        if self.stat_index == 0:
            self.cleanup()
        """

    def cleanup(self):
        # print('STATE 0 Cleanup')
        self.ax25conn.conn_cleanup()

    def S1_end_connection(self):
        self.change_state(1)
        self.ax25conn.end_connection()

    def t1_fail(self):
        pass
        # self.cleanup()

    def t3_fail(self):
        self.cleanup()

    def n2_fail(self):
        self.cleanup()

    def reject(self):
        self.ax25conn.send_DM()
        self.S1_end_connection()

    def prozess_I_frame(self):
        # TODO Move up
        self.ax25conn.set_T2()
        self.ax25conn.set_T1(stop=True)
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.ns == self.ax25conn.vr:  # !!!! Korrekt
            # Process correct I-Frame
            self.ax25conn.recv_data(bytes(self.frame.data))
            return True
        else:
            return False

    def delUNACK(self):
        # TODO Move up
        if ((self.nr - 1) % 8) in self.ax25conn.tx_buf_unACK.keys():
            self.ax25conn.del_unACK_buf()
            return True
        return False


class S1Frei(DefaultStat):  # INIT RX
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    DM            | DM    |       | DM    |        | DM     |         | UA,S5 3)| DM 4)
    """
    stat_index = 1  # FREI

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(5)
        self.ax25conn.n2 = 0
        self.ax25conn.set_T1(stop=True)
        self.ax25conn.set_T3()
        self.ax25conn.exec_cli()  # Process CLI ( C-Text and so on )
        self.ax25conn.port_handler.insert_conn2all_conn_var(new_conn=self.ax25conn)
        # Handle Incoming Connection
        if self.ax25conn.LINK_Connection is None:
            self.ax25conn.rx_buf_rawData = '*** Connect from {}\r'.format(self.ax25conn.to_call_str).encode('ASCII', 'ignore')
            if self.ax25conn.gui is not None:
                self.ax25conn.gui.new_conn_sound()
                speech = ' '.join(self.ax25conn.to_call_str.replace('-', ' '))
                self.ax25conn.gui.sprech(speech)

    def rx_DISC(self):
        self.reject()
        """
        self.ax25conn.send_DM()
        self.change_state(4)
        """

    def rx_UA(self):
        self.change_state(0)
        self.ax25conn.set_T1(stop=True)

    def rx_DM(self):
        self.change_state(0)
        self.ax25conn.set_T1(stop=True)
        # self.ax25conn.set_T1()

    def rx_RR(self):
        self.change_state(0)
        self.ax25conn.set_T1(stop=True)
        # else:
        #     self.change_state(0)

    def rx_RNR(self):
        self.change_state(0)
        self.ax25conn.set_T1(stop=True)
        # else:
        #     self.change_state(0)

    def rx_REJ(self):
        self.change_state(0)
        self.ax25conn.set_T1(stop=True)
        # else:
        #     self.change_state(0)

    def rx_I(self):
        self.change_state(0)
        self.ax25conn.set_T1(stop=True)
        # else:
        #     self.change_state(0)

    def rx_FRMR(self):
        self.change_state(4)

    def t1_fail(self):
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        """
        if self.ax25conn.is_link_remote:
            parm_n2 = self.ax25conn.parm_N2
        else:
            parm_n2 = 3
        """
        parm_n2 = 3
        if self.ax25conn.n2 > parm_n2:
            # print("S1 t1 FAIL > N2")
            self.change_state(0)

    def t3_fail(self):
        # print("S1 t3 FAIL")
        self.change_state(0)


class S2Aufbau(DefaultStat):  # INIT TX
    stat_index = 2  # AUFBAU Verbindung Aufbau

    def tx(self, ax25_frame: AX25Frame = None):
        """ NOT USED... CLEANUP !!!"""
        pass

    def rx_SABM(self):
        self.accept()

    def rx_DISC(self):
        self.reject()

    def rx_UA(self):
        self.accept()

    def rx_DM(self):
        self.reject()

    def rx_FRMR(self):
        pass

    def rx_I(self):
        pass

    def accept(self):
        # print("S2 - ACCEPT")
        if self.ax25conn.LINK_Connection is None:
            self.ax25conn.rx_buf_rawData = '\r*** Connected to {}\r'.format(self.ax25conn.to_call_str).encode('ASCII', 'ignore')
        else:
            self.send_to_link('\r*** Connected to {}\r'.format(self.ax25conn.to_call_str).encode('ASCII', 'ignore'))
        if self.ax25conn.gui is not None:
            speech = ' '.join(self.ax25conn.to_call_str.replace('-', ' '))
            self.ax25conn.gui.sprech(speech)
        self.ax25conn.tx_buf_2send = []  # Clean Send Buffer.
        self.ax25conn.tx_buf_rawData = b''  # Clean Send Buffer.
        self.ax25conn.n2 = 0
        self.change_state(5)
        if self.ax25conn.gui is not None:
            self.ax25conn.gui.new_conn_sound()

    def reject(self):
        self.ax25conn.rx_buf_rawData = '\r*** Busy from {}\r'.format(self.ax25conn.to_call_str).encode('ASCII', 'ignore')
        self.S1_end_connection()

    def state_cron(self):
        pass

    def t1_fail(self):
        # TODO ??? Move up to Conn ???
        if not self.ax25conn.n2:
            if self.ax25conn.LINK_Connection is None:
                to_qso_win = f'\r*** Try connect to {self.ax25conn.ax25_out_frame.to_call.call_str}' \

                user_db_ent = USER_DB.get_entry(self.ax25conn.ax25_out_frame.to_call.call_str, add_new=False)
                if user_db_ent:
                    if user_db_ent.Name:
                        to_qso_win += f' - ({user_db_ent.Name})'
                    if user_db_ent.Distance:
                        to_qso_win += f' - {round(user_db_ent.Distance)} km'
                to_qso_win += f' > Port {self.ax25conn.own_port.port_id}\r'
                self.ax25conn.rx_buf_rawData = to_qso_win.encode('UTF-8', 'ignore')
        self.ax25conn.send_SABM()
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()

    def t3_fail(self):
        pass

    def n2_fail(self):
        to_qso_win = f'\r*** Failed connect to {self.ax25conn.ax25_out_frame.to_call.call_str} > ' \
                     f'Port {self.ax25conn.own_port.port_id}\r'
        user_db_ent = USER_DB.get_entry(self.ax25conn.ax25_out_frame.to_call.call_str, add_new=False)
        if user_db_ent:
            if user_db_ent.Name:
                to_qso_win = f'\r*** Failed connect to {self.ax25conn.ax25_out_frame.to_call.call_str} - ' \
                             f'({user_db_ent.Name}) > Port {self.ax25conn.own_port.port_id}\r'

        self.ax25conn.rx_buf_rawData = to_qso_win.encode('UTF-8', 'ignore')
        self.ax25conn.send_DISC()
        self.S1_end_connection()


class S3sendFRMR(DefaultStat):
    stat_index = 3  # Blockrückruf

    def rx_UA(self):
        pass

    def rx_DM(self):
        pass

    def rx_RR(self):
        pass

    def rx_RNR(self):
        pass

    def rx_REJ(self):
        pass

    def rx_I(self):
        pass

    def t1_fail(self):
        pass
        # Send FRMR

    def t3_fail(self):
        pass
        # Send FRMR

    def n2_fail(self):
        # self.ax25conn.send_SABM()
        self.S1_end_connection()


class S4Abbau(DefaultStat):
    stat_index = 4  # ABBAU

    def tx(self, ax25_frame: AX25Frame):
        self.ax25conn.n2 = 0
        self.ax25conn.tx_buf_rawData = b''
        self.ax25conn.tx_buf_2send = []
        self.ax25conn.tx_buf_unACK = {}
        self.ax25conn.send_DISC()
        self.ax25conn.set_T1()

    def rx_UA(self):
        self.end_conn()

    def rx_DM(self):
        self.end_conn()

    def rx_SABM(self):
        self.reject()

    def rx_RR(self):
        pass
        """
        if self.pf:
            self.reject()
        """

    def rx_REJ(self):
        pass
        """
        if self.pf:
            self.reject()
        """

    def rx_I(self):
        pass
        """
        if self.pf:
            self.reject()
        """

    def rx_RNR(self):
        pass
        """
        if self.pf:
            self.reject()
         """

    def end_conn(self):
        self.S1_end_connection()
        self.ax25conn.n2 = 100

    def state_cron(self):
        pass

    def t1_fail(self):
        # self.change_state(2)
        self.ax25conn.send_DISC()
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()

    def t3_fail(self):
        pass

    def n2_fail(self):
        self.S1_end_connection()


class S5Ready(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    RR    | I/RR 1)| RR   | I/- 2)| RR    | I      | RR,S9  | S9      | UA      | UA,S1
    """
    stat_index = 5  # BEREIT

    def rx_SABM(self):
        self.ax25conn.send_UA()

    def rx_UA(self):
        pass

    def rx_RR(self):
        self.ax25conn.n2 = 0
        if self.delUNACK():
            self.ax25conn.set_T1(stop=True)
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1(stop=True)
            self.ax25conn.set_T2(stop=True)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1(stop=True)
            # self.ax25conn.set_T2(stop=True)
        else:
            # Maybe all ? or Automode ?
            self.ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self.ax25conn.set_T1()

    def rx_I(self):
        if not self.prozess_I_frame():
            self.ax25conn.send_REJ(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1()
            self.change_state(6)  # go into REJ_state
        else:
            if self.pf:
                self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            elif not self.ax25conn.tx_buf_unACK and \
                    not self.ax25conn.tx_buf_2send and \
                    not self.ax25conn.tx_buf_rawData:
                self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(9)

    def tx(self, ax25_frame: AX25Frame):
        if time.time() > self.ax25conn.t1:
            if self.ax25conn.tx_buf_rawData:
                self.ax25conn.build_I_fm_raw_buf()

    def state_cron(self):
        pass

    def t1_fail(self):
        # TODO Move up
        if time.time() > self.ax25conn.t2:
            # Nach 5 Versuchen
            if self.ax25conn.n2:
                if self.ax25conn.n2 > 4:
                    # BULLSHIT ?
                    self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
                    self.ax25conn.set_T1()
                    self.change_state(7)  # S7 Warten auf Final
                    # self.rtt_timer.set_rtt_single_timer()
                else:
                    if self.ax25conn.tx_buf_unACK:
                        self.ax25conn.resend_unACK_buf(1)
                        self.ax25conn.n2 += 1
                        self.ax25conn.set_T1()
            else:
                if self.ax25conn.tx_buf_unACK:
                    self.ax25conn.resend_unACK_buf()
                    self.ax25conn.n2 += 1
                    self.ax25conn.set_T1()

                if self.ax25conn.tx_buf_rawData and not self.ax25conn.tx_buf_unACK:
                    self.ax25conn.build_I_fm_raw_buf()
                    self.ax25conn.set_T1()

    def t3_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(7)  # S7 Warten auf Final
        # self.rtt_timer.set_rtt_single_timer()


# class S6sendREJ(S5Ready):
class S6sendREJ(DefaultStat):
    """"""
    stat_index = 6  # REJ ausgesandt

    def tx(self, ax25_frame: AX25Frame):
        pass

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(5)

    def rx_I(self):
        if self.prozess_I_frame():
            if self.pf:
                self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            elif not self.ax25conn.tx_buf_unACK and \
                    not self.ax25conn.tx_buf_2send and \
                    not self.ax25conn.tx_buf_rawData:
                self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(5)

    def rx_REJ(self):

        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            # Maybe all ? or Automode ?
            self.ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self.ax25conn.set_T1()

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1()
            self.ax25conn.set_T2(stop=True)

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(15)

    def state_cron(self):
        pass

    def t1_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(7)  # S7 Warten auf Final

    def t3_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(7)  # S7 Warten auf Final

    def n2_fail(self):
        self.ax25conn.send_SABM()
        self.change_state(2)


class S7WaitForFinal(DefaultStat):
    stat_index = 7  # Warten auf Final

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(5)
        # self.rtt_timer.rtt_single_rx(stop=True)

    def rx_I(self):
        if self.prozess_I_frame():
            # self.change_state(5)
            if self.pf:
                self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            elif not self.ax25conn.tx_buf_unACK and \
                    not self.ax25conn.tx_buf_2send and \
                    not self.ax25conn.tx_buf_rawData:
                self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=True)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # Maybe all ? or Automode ?
        self.ax25conn.resend_unACK_buf(1)
        # self.ax25conn.set_T1()    ?????????
        self.ax25conn.set_T1()
        if self.pf:
            # self.rtt_timer.rtt_single_rx()
            self.ax25conn.set_T1(stop=True)
            self.ax25conn.set_T2(stop=True)
            self.change_state(5)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()

        if self.pf:
            # self.rtt_timer.rtt_single_rx()
            self.ax25conn.set_T1(stop=True)
            self.ax25conn.set_T2(stop=True)
            self.change_state(5)

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            # self.rtt_timer.rtt_single_rx()
            self.ax25conn.set_T1(stop=True)
            self.ax25conn.set_T2(stop=True)
            self.change_state(9)
        else:
            self.change_state(12)

    def state_cron(self):
        pass

    def t1_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()

    def t3_fail(self):
        pass

    def n2_fail(self):
        self.ax25conn.send_SABM()
        self.change_state(2)


class S8SelfNotReady(DefaultStat):
    stat_index = 8  # nicht bereit

    def rx_SABM(self):
        self.ax25conn.send_UA()

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T2(stop=True)
            self.ax25conn.set_T1(stop=True)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self.ax25conn.set_T1()

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(10)

    def state_cron(self):
        pass

    def t1_fail(self):
        if time.time() > self.ax25conn.t2:
            # Nach 5 Versuchen
            if self.ax25conn.n2:
                if self.ax25conn.n2 > 4:
                    # BULLSHIT ?
                    self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
                    self.ax25conn.set_T1()
                    self.change_state(11)  # S7 Warten auf Final
                    # self.rtt_timer.set_rtt_single_timer()
                else:
                    if self.ax25conn.tx_buf_unACK:
                        self.ax25conn.resend_unACK_buf(1)
                        self.ax25conn.n2 += 1
                        self.ax25conn.set_T1()
            else:
                if self.ax25conn.tx_buf_unACK:
                    self.ax25conn.resend_unACK_buf()
                    self.ax25conn.n2 += 1
                    self.ax25conn.set_T1()

                if self.ax25conn.tx_buf_rawData and not self.ax25conn.tx_buf_unACK:
                    self.ax25conn.build_I_fm_raw_buf()
                    self.ax25conn.set_T1()

    def t3_fail(self):
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final
        # self.rtt_timer.set_rtt_single_timer()

    def n2_fail(self):
        pass


class S9DestNotReady(DefaultStat):
    stat_index = 9  # Gegenstelle nicht bereit

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(5)

    def rx_I(self):
        if self.prozess_I_frame():
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.ax25conn.send_REJ(pf_bit=self.pf, cmd_bit=False)
            self.change_state(15)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.ax25conn.set_T1(stop=True)

        self.change_state(5)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(5)

    def rx_RNR(self):
        # self.change_state(10)
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def t1_fail(self):
        pass
        """
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final
        """

    def t3_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final

    def n2_fail(self):
        pass


class S10BothNotReady(DefaultStat):
    stat_index = 10  # Beide Seiten nicht bereit

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(8)

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1(stop=True)

        self.change_state(8)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(8)

    def rx_RNR(self):
        # self.change_state(10)
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def t1_fail(self):
        pass
        """
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(13)  # S7 Warten auf Final
        """

    def t3_fail(self):
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(13)  # S7 Warten auf Final

    def n2_fail(self):
        pass


class S11SelfNotReadyFinal(DefaultStat):
    stat_index = 11  # Selber nicht bereit und auf Final warten

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(8)

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        # if self.pf or self.cmd:
        self.delUNACK()

        if self.cmd:
            self.ax25conn.send_RNR(pf_bit=True, cmd_bit=False)
            self.ax25conn.set_T1()
        elif self.pf:
            self.ax25conn.set_T1(stop=True)
            self.change_state(8)
            # self.rtt_timer.rtt_single_rx()

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(8)  # ???
            # self.rtt_timer.rtt_single_rx()  # ???
        else:
            self.ax25conn.resend_unACK_buf(1)
            self.ax25conn.set_T1()
            # self.ax25conn.set_T1(stop=True)

    def rx_RNR(self):
        self.delUNACK()
        if self.pf and not self.cmd:
            # self.rtt_timer.rtt_single_rx()
            self.change_state(10)
        elif self.cmd:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(13)
        else:
            self.change_state(13)
        # self.rtt_timer.rtt_single_rx(stop=True)

    def state_cron(self):
        pass

    def t1_fail(self):
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()

    def t3_fail(self):
        pass

    def n2_fail(self):
        self.ax25conn.send_SABM()
        self.change_state(2)


class S12DestNotReadyFinal(DefaultStat):
    stat_index = 12  # Gegenstelle nicht bereit und auf Final warten

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(5)

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()

        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.set_T1(stop=True)
            self.change_state(5)
        else:
            self.change_state(7)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        self.ax25conn.resend_unACK_buf(1)
        self.ax25conn.set_T1()
        if self.pf:
            self.change_state(5)
            # self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.change_state(7)

    def rx_RNR(self):
        # self.change_state(10)
        self.delUNACK()
        if self.pf:
            self.change_state(9)
            # self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def t1_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()

    def t3_fail(self):
        pass

    def n2_fail(self):
        self.ax25conn.send_SABM()
        self.change_state(2)


class S13BothNotReadyFinal(DefaultStat):
    stat_index = 13  # Beide Seiten nicht bereit und auf Final warten

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(8)

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.change_state(8)
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1(stop=True)
        else:
            self.change_state(11)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(8)
        else:
            self.ax25conn.resend_unACK_buf(1)
            self.ax25conn.set_T1()
            self.change_state(11)

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.change_state(11)

    def t1_fail(self):
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()

    def t3_fail(self):
        pass

    def n2_fail(self):
        self.ax25conn.send_SABM()
        self.change_state(2)


class S14sendREJselfNotReady(DefaultStat):  # TODO  /  / Testing
    stat_index = 14  # REJ ausgesandt u. Selbst nicht bereit

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(8)

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1(stop=True)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self.ax25conn.set_T1()

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(16)

    def t1_fail(self):
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def t3_fail(self):
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def n2_fail(self):
        pass


class S15sendREJdestNotReady(DefaultStat):  # TODO  /  / Testing
    stat_index = 15  # REJ ausgesandt u. Gegenstelle nicht bereit

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(5)

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(9)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1(stop=True)

        self.change_state(6)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self.ax25conn.set_T1()
        self.change_state(6)

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def t1_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final

    def t3_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final

    def n2_fail(self):
        pass


class S16sendREJbothNotReady(DefaultStat):  # TODO  / / Testing
    stat_index = 16  # REJ ausgesandt u. beide Seiten nicht bereit

    def rx_SABM(self):
        self.ax25conn.send_UA()
        self.change_state(5)

    def rx_I(self):
        self.prozess_I_frame()
        self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def rx_RR(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.ax25conn.set_T1(stop=True)

        self.change_state(14)

    def rx_REJ(self):
        self.ax25conn.n2 = 0
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self.ax25conn.set_T1()
        self.change_state(14)

    def rx_RNR(self):
        self.delUNACK()
        if self.pf:
            self.ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def t1_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def t3_fail(self):
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def n2_fail(self):
        pass
