"""
    Layer 3
    AX.25 PROT Packet Handling
"""
import time
from datetime import datetime

import cli.cliMain
from ax25.ax25UI_Pipe import AX25Pipe
from cfg import config_station
from UserDB.UserDBmain import USER_DB
from ax25.ax25dec_enc import AX25Frame
from cfg.default_config import getNew_pipe_cfg
# from cfg.constant import NO_REMOTE_STATION_TYPE
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import reverse_uid
from ax25.ax25FileTransfer import FileTransport, ft_rx_header_lookup
from fnc.loc_fnc import locator_distance
from sound.popt_sound import SOUND


def count_modulo(inp: int):
    return (inp + 1) % 8


class RTT:
    # TODO
    def __init__(self, connection):
        self._conn = connection
        self._act_paclen = self._conn.parm_PacLen
        self.rtt_dict: {int: float} = {}
        self.rtt_best = 999.0
        self.rtt_worst = 0.0
        self.rtt_average = float(self._conn.IRTT / 1000) / 2
        self.rtt_last = 0.0
        self.rtt_single_timer = 0.0
        for i in range(8):
            self.rtt_dict[i] = {
                'timer': 0.0,
                'paclen': int(self._act_paclen),
                'rtt': self.rtt_average
            }
        # self.rtt_single_list = [float(self.rtt_average)]*4
        self.rtt_single_list = []

    def get_rtt_avrg(self):
        self._calc_rtt_vars()
        if self.rtt_best == 999:
            return self.rtt_average
        else:
            return (self.rtt_average + self.rtt_best) / 2

    def set_rtt_timer(self, vs: int, paclen: int):
        self.rtt_dict[vs]['timer'] = time.time()
        self.rtt_dict[vs]['paclen'] = paclen
        # print('set {}'.format(self.rtt_dict))

    def set_rtt_single_timer(self):
        self.rtt_single_timer = time.time()

    def rtt_single_rx(self, stop=False):
        if stop:
            self.rtt_single_timer = 0.0
        if self.rtt_single_timer:
            # rtt = float(((time.time() - self.rtt_single_timer) / 2) / 16) * self.act_paclen
            rtt = (time.time() - self.rtt_single_timer) * 1.3
            self.rtt_single_list[0] = rtt
            self.rtt_single_list = self.rtt_single_list[1:] + [self.rtt_single_list[0]]
            self.rtt_single_timer = 0.0
        # print("RTT-S: {}".format(self.rtt_single_list))

    def rtt_rx(self, vs: int):
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


class AX25Conn:
    def __init__(self, ax25_frame, port, rx=True):
        """ AX25 Connection class """
        # TODO: Cleanup
        """ Global Stuff """
        self.own_port = port
        self._port_handler = port.port_handler
        """ GUI Stuff"""
        self.ch_index: int = 0
        self.port_id: int = self.own_port.port_id
        self.port_name: str = self.own_port.portname
        self._gui = self._port_handler.get_gui()
        # self.ChVars = None
        """ Config new Connection Address """
        #####################################
        ax25_conf = ax25_frame.get_frame_conf()
        self.axip_add = tuple(ax25_conf.get('axip_add', ()))
        if rx:
            # TODO Clean up !!!
            self.uid = str(reverse_uid(ax25_conf.get('uid', '')))  # Unique ID for Connection
            self.to_call_str = str(ax25_conf.get('from_call_str', ''))
            self.my_call_str = str(ax25_conf.get('to_call_str', ''))
            self.my_call = str(ax25_conf.get('to_call', ''))
            self.via_calls = list(ax25_conf.get('via_calls_str', []))
            self.via_calls.reverse()
        else:
            self.uid = str(ax25_conf.get('uid', ''))  # Unique ID for Connection
            self.to_call_str = str(ax25_conf.get('to_call_str', ''))
            self.my_call_str = str(ax25_conf.get('from_call_str', ''))
            self.my_call = str(ax25_conf.get('from_call', ''))
            self.via_calls = list(ax25_conf.get('via_calls_str', []))

        """ IO Buffer Packet For Handling """
        self.tx_buf_ctl = []           # Buffer for CTL (S) Frame to send on next Cycle
        self.tx_buf_2send = []         # Buffer for Sending. Will be processed in ax25PortHandler
        self.tx_buf_unACK = {}                  # Buffer for UNACK I-Frames
        self._rx_buf_last_frame = ax25_frame    # Buffers for last Frame !?!
        self.rx_buf_last_data = b''             # Buffers for last Frame !?!
        """ IO Buffer For GUI / CLI """
        self.tx_buf_rawData = b''           # Buffer for TX RAW Data that is not packed yet into a Frame
        self.rx_tx_buf_guiData = []         # Buffer for GUI QSO Window ('TX', data), ('RX', data)
        """ DIGI / Link to other Connection for Auto processing """
        self.LINK_Connection = None
        self.LINK_rx_buff = b''
        self.is_link = False
        self.is_link_remote = False
        self.digi_call = ''
        self.is_digi = False
        """ Connection Conf """
        """
        self.conf = dict(
            uid=self.uid,
            from_call_str=self.my_call_str,
            to_call_str=self.to_call_str,
            via_calls=self.via_calls,
            axip_add=self.axip_add,
            digi_call=self.digi_call,
            node_conf=dict(
                digi_max_buff=10,  # bytes till RNR
                digi_max_n2=4,  # N2 till RNR
            ),
        )
        """
        """ Port Variablen"""
        # TODO Private / Clean Up / OPT
        self.vs = 0  # Sendefolgenummer     / N(S) = V(R)  TX
        self.vr = 0  # Empfangsfolgezählers / N(S) = V(R)  TX
        self.t1 = 0  # ACK
        self.t2 = 0  # Respond Delay
        self.t3 = 0  # Connection Hold
        self.n2 = 0  # Fail Counter / No Response Counter
        self._await_disco = False
        """ Port Config Parameter """
        self.port_cfg = self.own_port.port_cfg
        self.parm_PacLen = self.port_cfg.parm_PacLen  # Max Pac len
        self.parm_MaxFrame = self.port_cfg.parm_MaxFrame  # Max (I) Frames
        self.parm_TXD = self.port_cfg.parm_TXD  # TX Delay for RTT Calculation  !! Need to be high on AXIP for T1 calculation
        self.parm_Kiss_TXD = 0
        self.parm_Kiss_Tail = 0
        if self.own_port.kiss.is_enabled:
            self.parm_Kiss_TXD = self.own_port.port_cfg.parm_kiss_TXD
            self.parm_Kiss_Tail = self.own_port.port_cfg.parm_kiss_Tail
        self.parm_T2 = int(self.port_cfg.parm_T2)  # T2 (Response Delay Timer) Default: 2888 / (parm_baud / 100)
        self.parm_T3 = self.port_cfg.parm_T3  # T3 (Inactive Link Timer)
        self.parm_N2 = self.port_cfg.parm_N2  # Max Try   Default 20
        self.parm_baud = self.port_cfg.parm_baud  # Baud for calculating Timer
        """ Timer Calculation & other Data for Statistics"""
        self.IRTT = 0
        # self.RTT = 0
        self.calc_irtt()
        self.RTT_Timer = RTT(self)
        self.tx_byte_count = 0
        self.rx_byte_count = 0
        """ Connection Start Time """
        self.time_start = datetime.now()
        """ Zustandstabelle / States """
        # TODO Cleanup  CONST zustand_tab
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
        """ BBS Control """
        self.bbs_connection = None
        """ Link Holder / Not related to Link Connection Stuff """
        self.link_holder_on: bool = False
        self.link_holder_interval: int = 30  # Minutes
        self.link_holder_timer = time.time()
        self.link_holder_text: str = '\r'
        """ Encoding """
        self._encoding = 'CP437'     # 'UTF-8'
        """ Station CFG Parameter """
        self.stat_cfg = config_station.DefaultStation()
        self._my_call_alias = ''
        self._to_call_alias = ''
        # self._my_locator = self.stat_cfg.stat_parm_LOC
        self._my_locator = self._gui.own_loc
        """ User DB Entry """
        self.user_db_ent = None
        self.cli_remote = True
        self.cli_language = 0
        self.last_connect = None
        self._set_user_db_ent()
        """ Station Individual Parameter """
        self.set_station_cfg()
        """ CLI CFG """
        self.noty_bell = False
        self.cli = cli.cliMain.NoneCLI(self)
        self.cli_type = ''
        """ Pipe CFG """
        pipe_cfg = POPT_CFG.get_pipe_CFG_fm_UID(call=str(self.my_call_str),
                                                port_id=int(self.own_port.port_id))
        if not all((pipe_cfg,
                   pipe_cfg.get('pipe_parm_Proto', False))):
            """ Init CLI """
            self._init_cli()
            if not rx:
                self.cli.change_cli_state(state=1)
        else:
            """ Init Pipe """
            self.set_pipe(pipe_cfg)
        """ Init State Tab """
        if rx:
            self.set_T1()
            self.set_T3()
            self.zustand_exec = S1Frei(self)
            self.handle_rx(ax25_frame)
        else:
            # self.t2 = time.time() + 5
            self.zustand_exec = S2Aufbau(self)
            # self.cli.change_cli_state(state=1)

    def __del__(self):
        pass

    ##################
    # CLI INIT
    def _init_cli(self):
        # TODO
        if self.stat_cfg.stat_parm_Call in self.port_cfg.parm_cli.keys():
            del self.cli
            # self.cli = self.cfg.parm_cli[self.stat_cfg.stat_parm_Call](self)
            # print(f"CLI INIT : {self.cfg.parm_cli[self.stat_cfg.stat_parm_Call]}")
            self.cli = cli.cliMain.CLI_OPT[self.port_cfg.parm_cli[self.stat_cfg.stat_parm_Call].get('cli_typ', 'NO-CLI')](self)
            self.cli_type = self.cli.cli_name
            # print(f"CLI INIT typ: {self.cli.cli_name}")
            self.cli.build_prompt()
        """
        else:
            self.cli = cli.cli.NoneCLI(self)
        """

    def _reinit_cli(self):
        # print(f"CLI RE-INIT: {self.uid}")
        if not self.pipe:
            self._init_cli()
            self.cli.change_cli_state(state=1)

    def set_station_cfg(self):  # TODO New Station CFG
        if self.my_call_str in self._port_handler.ax25_stations_settings.keys():
            self.stat_cfg = self._port_handler.ax25_stations_settings[self.my_call_str]
        else:
            for call in list(self._port_handler.ax25_stations_settings.keys()):
                if self.my_call in call:
                    if self.my_call in self._port_handler.ax25_stations_settings.keys():
                        self.stat_cfg = self._port_handler.ax25_stations_settings[self.my_call]
                        break
        self._set_packet_param()

    ####################
    # Zustand EXECs
    def handle_rx(self, ax25_frame):
        self._rx_buf_last_frame = ax25_frame
        self.zustand_exec.state_rx_handle(ax25_frame=ax25_frame)
        """
        if ax25_frame.payload:
            self.rx_buf_last_data = ax25_frame.payload
        """
        self.set_T3()

    def handle_tx(self, ax25_frame):
        """ Not used... TX is handled by cron """
        self.zustand_exec.tx(ax25_frame=ax25_frame)

    def send_data(self, data, file_trans=False):
        if self.ft_obj is not None and not file_trans:
            return False
        if data:
            if type(data) is bytes:
                self._link_holder_reset()
                self.tx_buf_rawData += data
                return True
        return False

    def _recv_data(self, data: b'', file_trans=False):
        # Statistic
        self.rx_byte_count += len(data)
        """ Link/Node-DIGI """
        if self.is_link:
            self.LINK_rx_buff += data
            self.exec_cli(data)
            return
        """  Pipe-Tool """
        if self._pipe_rx(data):
            return
        """ FT """
        self._ft_check_incoming_ft(data)
        if self._ft_handle_rx(data):
            return
        """ BBS/PMS-FWD"""
        if self._bbsFwd_rx(data):
            return
        self._send_gui_QSObuf_rx(data)
        """ Station ( RE/DISC/Connect ) Sting Detection """
        self._set_dest_call_fm_data_inp(data)
        """ CLI """
        self.exec_cli(data)
        self.rx_buf_last_data = data
        return

    def exec_cron(self):
        """ DefaultStat.cron() """
        ###############################################
        """  DIGI / BBS / FT / CLI /LH Funktion """
        self._app_cron()
        """ Zustandstabelle Crone """
        self.zustand_exec.cron()
        if self.zustand_exec.stat_index == 0:
            self.conn_cleanup()
            return
        if self.zustand_exec.stat_index == 1:
            if not self.tx_buf_ctl:
                self.zustand_exec.stat_index = 0
            return
        if self._await_disco:
            self._wait_for_disco()
            return

    def _app_cron(self):
        if self._link_crone():   # DIGI / LINK Connection / Node Funktion
            return True
        if self._ft_cron():
            return True
        if self._bbsFwd_cron():
            return True
        if self._cron_cli():
            self._link_holder_cron()
        return True

    #############################
    # BBS_FWD Stuff
    def bbsFwd_start_reverse(self):
        if self.cli.stat_identifier is None:
            print("E: cli.stat_identifier is None")
            return False
        if self.cli.stat_identifier.typ != 'BBS':
            print("E: cli.stat_identifier.typ != 'BBS'")
            return False
        if self.cli.stat_identifier.e:
            print("E: cli.stat_identifier.e")
            print(f"{self.cli.stat_identifier.typ}")
            return False
        bbs = self._port_handler.get_bbs()
        if bbs is None:
            print("E: _bbs is None")
            return False
        self.bbs_connection = bbs.init_fwd_conn(self)
        if self.bbs_connection is None:
            print("E: bbs_connection is None")
            return False
        # print("Done: bbsFwd_start_reverse")
        return True

    def _bbsFwd_cron(self):
        if self.bbs_connection is None:
            return False
        self.bbs_connection.connection_cron()
        return True

    def _bbsFwd_rx(self, data):
        if self.bbs_connection is None:
            return False
        return self.bbs_connection.connection_rx(data)
        # return True

    def _bbsFwd_disc(self):
        if self.bbs_connection is None:
            return False
        self.bbs_connection.end_conn()
        return True

    #############################
    # Proto PIPE
    def _pipe_rx(self, raw_data: b''):
        if self.pipe is None:
            return False
        self.pipe.handle_rx_rawdata(raw_data)
        return True

    def set_pipe(self, pipe_cfg=None):
        if not pipe_cfg:
            pipe_cfg = POPT_CFG.get_pipe_CFG().get(f'{self.own_port.port_id}-{self.my_call_str}', getNew_pipe_cfg())

        try:
            pipe = AX25Pipe(
                connection=self,
                pipe_cfg=pipe_cfg
            )
        except AttributeError:
            # print("Pipe Error (AX25Conn-set_pipe())")
            return False
        if pipe_cfg.get('pipe_parm_PacLen', 0):
            self.parm_PacLen = pipe_cfg.get('pipe_parm_PacLen', self.parm_PacLen)
        if pipe_cfg.get('pipe_parm_MaxFrame', 0):
            self.parm_MaxFrame = pipe_cfg.get('pipe_parm_MaxFrame', self.parm_MaxFrame)
        if not self.own_port.add_pipe(pipe=pipe):
            # print("Port no Pipe")
            return False
        self.cli = cli.cliMain.NoneCLI(self)
        self.cli_type = ''
        self.pipe = pipe

    def _del_pipe(self):
        if self.pipe:
            self.own_port.del_pipe(self.pipe)
            self.pipe = None
            # self._reinit_cli()
            return True
        return False

    def del_pipe_fm_conn(self):
        if self._del_pipe():
            self._reinit_cli()

    ########################################
    # File Transfer
    def _ft_check_incoming_ft(self, data):
        if self.ft_obj is None:
            ret = ft_rx_header_lookup(data=data, last_pack=self.rx_buf_last_data)
            if ret:
                self.ft_obj = ret
                self.ft_obj.connection = self

    def _ft_handle_rx(self, data: b''):
        if self.ft_obj is None:
            return False
        return self.ft_obj.ft_rx(data)

    def _ft_cron(self):
        if self._ft_queue_handling():
            # if self._gui is not None:
            #     self._gui.on_channel_status_change()
            return self.ft_obj.ft_crone()
        return False

    def _ft_queue_handling(self):
        if self.ft_obj is not None:
            self.ft_obj: FileTransport
            # if self.ft_obj.pause:
            #     return False
            if self.ft_obj.done:
                # print(f"FT Done - rest: {self.ft_obj.ft_rx_buf}")
                # self.rx_buf_rawData += bytes(self.ft_obj.ft_rx_buf)
                self._send_gui_QSObuf_rx(self.ft_obj.ft_rx_buf)
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
    def _link_holder_reset(self):
        if self.link_holder_on:
            self.link_holder_timer = time.time() + (self.link_holder_interval * 60)

    def _link_holder_cron(self):
        if self.link_holder_on:
            if self.link_holder_timer < time.time():
                self.link_holder_timer = time.time() + (self.link_holder_interval * 60)
                self.tx_buf_rawData += self.link_holder_text.encode(self._encoding, 'ignore')

    ###############################
    # LINKS Linked/DIGI Connections
    def _link_crone(self):
        if self.is_link and self.LINK_Connection is not None:
            self.LINK_Connection.tx_buf_rawData += bytes(self.LINK_rx_buff)
            self.LINK_rx_buff = b''
            self.tx_buf_rawData += bytes(self.LINK_Connection.LINK_rx_buff)
            self.LINK_Connection.LINK_rx_buff = b''
            return True
        return False

    def new_link_connection(self, conn):
        if conn is None:
            return False
        if conn.uid in self._port_handler.link_connections.keys():
            conn.zustand_exec.change_state(4)
            conn.zustand_exec.tx(None)
            return False
        if self.is_link_remote:
            self.my_call_str = str(conn.my_call_str)
            if conn.port_id:
                digi_call = f'{conn.my_call}-{conn.port_id}'
            else:
                digi_call = str(conn.my_call_str)
            self.my_call_str = digi_call
            # self.ax25_out_frame.digi_call = str(conn.my_call_str)
            self.digi_call = digi_call
            self._port_handler.link_connections[str(conn.uid)] = conn, ''
        else:
            self._port_handler.link_connections[str(conn.uid)] = conn, self.my_call_str

        self.LINK_Connection = conn
        self.is_link = True
        #   self.cli = cli.cliMain.NoneCLI(self)  # Disable CLI
        return True

    def new_digi_connection(self, conn):
        print(f"Conn newDIGIConn: UID: {conn.uid}")
        if conn is None:
            print("Conn ERROR: newDIGIConn: not conn")
            return False
        if self.uid in self._port_handler.link_connections.keys():
            self.zustand_exec.change_state(4)
            self.zustand_exec.tx(None)
            print("Conn ERROR: newDIGIConn: self.uid in self._port_handler.link_connections")
            return False
        self.digi_call = str(conn.digi_call)
        self._port_handler.link_connections[str(self.uid)] = self, conn.digi_call

        self.LINK_Connection = conn
        self.is_link = True
        #   self.cli = cli.cliMain.NoneCLI(self)  # Disable CLI
        # print("new_digi TX CONN ")
        return True

    def link_disco(self, reconnect=True):
        print(f'LINK DISCO')
        if self.is_link and self.LINK_Connection is not None:
            print(f'LINK DISCO : ownUID: {self.uid} - LinkUID: {self.LINK_Connection.uid}')
            print(f'LINK DISCO : digiCall: {self.digi_call} - is_digi: {self.is_digi}')
            print(f'LINK DISCO : is_link_remote: {self.is_link_remote} - reconn: {reconnect}')
            if self.LINK_Connection.zustand_exec.stat_index in [1, 2]:
                # self.LINK_Connection.n2 = 100
                self.LINK_Connection.set_T1(stop=True)
                self.LINK_Connection.zustand_exec.change_state(0)
                self.del_link()
            else:

                if not self.is_link_remote:
                    print("LINK DISCO Remote")
                    self.LINK_Connection.conn_disco()
                    # self.LINK_Connection.zustand_exec.tx(None)
                else:
                    self._port_handler.del_link(self.LINK_Connection.uid)
                    # print(self.zustand_exec.stat_index)
                    # if self.zustand_exec.stat_index not in [0, 1]:
                    # if reconnect and not self.digi_call:
                    if self.is_digi:
                        print("DIGI DISCO Remote")
                        self.LINK_Connection.conn_disco()
                    elif reconnect and self.is_link_remote and not self.is_digi:
                        print('ReConn')
                        self.LINK_Connection.send_sys_Msg_to_gui(f'*** Reconnected to {self.my_call_str}')
                        self.send_to_link(f'\r*** Reconnected to {self.my_call_str}\r'.encode('ASCII', 'ignore'))
                        """
                        if self.digi_call:
                            print("Link Disco ----")
                            self.LINK_Connection.conn_disco()
                        else:
                            self.LINK_Connection.cli.change_cli_state(state=1)
                            self.LINK_Connection.cli.send_prompt()
                        """
                        self.LINK_Connection.cli.change_cli_state(state=1)
                        self.LINK_Connection.cli.send_prompt()
                    self.LINK_Connection.del_link()

    def send_to_link(self, inp: b''):
        if inp:
            if self.is_link:
                self.LINK_Connection.tx_buf_rawData += inp

    def del_link(self):
        """ Called in State.link_cleanup() """
        if self.LINK_Connection is not None:
            # print(f'LINK CLEANUP link_connections K : {self._port_handler.link_connections.keys()}')
            self.LINK_Connection = None
            self.is_link = False
        self._port_handler.del_link(self.uid)

    def _link_cleanup(self):
        # self.link_disco()
        self.del_link()
        # self._port_handler.del_link(self.uid)

    # ##############
    # DISCO
    def conn_disco(self):
        """ 2'nd time called = HardDisco """
        if self.zustand_exec.stat_index:
            self._del_pipe()
            self._bbsFwd_disc()  # TODO return "is_"self.bbs_connection
            self.set_T1(stop=True)
            # self.zustand_exec.tx(None)
            if self.zustand_exec.stat_index in [2, 4] or self._await_disco:
                self.send_DISC_ctlBuf()
                self.zustand_exec.S1_end_connection()
            else:
                if not self.is_buffer_empty():
                    self._await_disco = True
                    print("DISCO and buff not NULL !!")
                    """
                    print(f"DISCO and buff not NULL !! tx_buf_rawData: {self.tx_buf_rawData}")
                    print(f"DISCO and buff not NULL !! tx_buf_2send: {self.tx_buf_2send}")
                    print(f"DISCO and buff not NULL !! tx_buf_unACK: {self.tx_buf_unACK}")
                    """
                else:

                    self.zustand_exec.change_state(4)

    def is_buffer_empty(self):
        return not bool(self.tx_buf_rawData or self.tx_buf_2send or self.tx_buf_unACK)

    def _wait_for_disco(self):
        if self.tx_buf_rawData or self.tx_buf_2send or self.tx_buf_unACK:
            return
        self._await_disco = False
        self.zustand_exec.change_state(4)

    def conn_cleanup(self):
        print(f"conn_cleanup: {self.uid}\n"
              f"state: {self.zustand_exec.stat_index}\n")
        # self.bbsFwd_disc()
        if self.tx_buf_ctl:
            return
        if self.rx_tx_buf_guiData:
            return
        self._link_cleanup()
        self.own_port.del_connections(conn=self)
        self._port_handler.end_connection(self)   # Doppelt ..
        # TODO def is_conn_cleanup(self) -> return"

    def end_connection(self, reconn=True):
        print(f"end_connection: {self.uid}")
        self._del_pipe()
        self.ft_queue = []
        if self.ft_obj:
            self.ft_obj.ft_abort()
        self.ft_obj = None
        self.link_disco(reconnect=reconn)
        self.set_T1()
        self.vr = 0
        self.vs = 0

    def is_dico(self):
        if not self.zustand_exec:
            return True
        if not self.zustand_exec.stat_index:
            return True
        if self.zustand_exec.stat_index in [0, 1]:
            return True
        return False

    def is_incoming_connection(self):
        if self.zustand_exec.stat_index == 1:
            return True
        return False

    ###############################################
    # Timer usw
    def set_RNR(self, link_remote=False):
        if not self.is_RNR:
            self.send_RNR()
            self.set_T1(stop=True)
            self.set_T3()
            self.is_RNR = True

            new_state = {
                5: 8,
                6: 14,
                7: 11,
                9: 10,
                12: 13,
                15: 16
            }.get(self.zustand_exec.stat_index, None)
            if new_state:
                self.zustand_exec.change_state(new_state)

    def unset_RNR(self, link_remote=False):
        if self.is_RNR:
            self.is_RNR = False
            self.send_RR()
            self.set_T1()
            # self.set_T3(stop=True)

            new_state = {
                8: 5,
                10: 9,
                11: 7,
                13: 12,
                14: 6,
                16: 15
            }.get(self.zustand_exec.stat_index, None)
            if new_state:
                self.zustand_exec.change_state(new_state)

    def _send_gui_QSObuf_tx(self, data):
        if self.ft_obj:
            return
        if self.pipe:
            return
        self.rx_tx_buf_guiData.append(
            ('TX', data)
        )

    def _send_gui_QSObuf_rx(self, data):
        if self.ft_obj:
            return
        if self.pipe:
            return
        self.rx_tx_buf_guiData.append(
            ('RX', data)
        )

    def _set_dest_call_fm_data_inp(self, raw_data: b''):
        # TODO AGAIN !!
        data = self.rx_buf_last_data + raw_data
        if b'\r' not in data:
            return
        data = data.split(b'\r')[:-1]
        for line in data:
            if line.lower().startswith(b'*** connected to ') or\
                    line.lower().startswith(b'*** reconnected to '):
                tmp_data = line.split(b' to ')[-1]
                tmp_data = tmp_data.decode('ASCII', 'ignore')
                # TODO Conn/reconn fnc
                if ':' in tmp_data:
                    tmp_call = tmp_data.split(':')
                    self.to_call_str = tmp_call[1].replace(' ', '')
                    self._to_call_alias = tmp_call[0].replace(' ', '')
                else:
                    self.to_call_str = tmp_data.replace(' ', '')
                    self._to_call_alias = ''
                self.tx_byte_count = 0
                self.rx_byte_count = 0
                self._set_user_db_ent()
                self._set_packet_param()
                self._reinit_cli()

                if self._gui:
                    # TODO
                    speech = ' '.join(self.to_call_str.replace('-', ' '))
                    SOUND.sprech(speech)
                    self._gui.on_channel_status_change()
                # Maybe it's better to look at the whole string (include last frame)?
                return
        return

    def _set_user_db_ent(self):
        self.user_db_ent = USER_DB.get_entry(self.to_call_str)
        if self.user_db_ent:
            self.user_db_ent.Connects += 1  # TODO Count just when connected
            self.last_connect = self.user_db_ent.last_seen
            self.user_db_ent.last_seen = datetime.now()
            self._encoding = self.user_db_ent.Encoding
            if self.user_db_ent.Language == -1:
                self.user_db_ent.Language = int(POPT_CFG.get_guiCFG_language())
            self.cli_language = self.user_db_ent.Language
            self.set_distance()
            # TODO disable CLI for node ect.
            """
            if self.user_db_ent.TYP in NO_REMOTE_STATION_TYPE:
                self.cli_remote = False
            else:
                self.cli_remote = True
            """

    def set_user_db_language(self, lang_ind: int):
        self.user_db_ent.Language = int(lang_ind)
        self.cli_language = int(lang_ind)

    def set_distance(self):
        if self.user_db_ent:
            if self._my_locator and self.user_db_ent.LOC:
                self.user_db_ent.Distance = locator_distance(self._my_locator, self.user_db_ent.LOC)

    def _set_packet_param(self):
        self.parm_PacLen = self.port_cfg.parm_PacLen  # Max Pac len
        self.parm_MaxFrame = self.port_cfg.parm_MaxFrame  # Max (I) Frames
        self.user_db_ent = USER_DB.get_entry(self.to_call_str)
        stat_call = self.stat_cfg.stat_parm_Call

        if self.user_db_ent:
            if int(self.user_db_ent.pac_len):
                self.parm_PacLen = int(self.user_db_ent.pac_len)
            elif stat_call != config_station.DefaultStation.stat_parm_Call:
                if stat_call in self.port_cfg.parm_stat_PacLen.keys():
                    if self.port_cfg.parm_stat_PacLen[stat_call]:  # If 0 then default port param
                        self.parm_PacLen = self.port_cfg.parm_stat_PacLen[stat_call]  # Max Pac len

            if int(self.user_db_ent.max_pac):
                self.parm_MaxFrame = int(self.user_db_ent.max_pac)
            elif stat_call != config_station.DefaultStation.stat_parm_Call:
                if stat_call in self.port_cfg.parm_stat_MaxFrame.keys():
                    if self.port_cfg.parm_stat_MaxFrame[stat_call]:  # If 0 then default port param
                        self.parm_MaxFrame = self.port_cfg.parm_stat_MaxFrame[stat_call]  # Max Pac

        else:
            # TODO
            stat_call = self.stat_cfg.stat_parm_Call
            if stat_call != config_station.DefaultStation.stat_parm_Call:
                if stat_call in self.port_cfg.parm_stat_PacLen.keys():
                    if self.port_cfg.parm_stat_PacLen[stat_call]:  # If 0 then default port param
                        self.parm_PacLen = self.port_cfg.parm_stat_PacLen[stat_call]  # Max Pac len
                if stat_call in self.port_cfg.parm_stat_MaxFrame.keys():
                    if self.port_cfg.parm_stat_MaxFrame[stat_call]:  # If 0 then default port param
                        self.parm_MaxFrame = self.port_cfg.parm_stat_MaxFrame[stat_call]  # Max Pac

    def _get_rtt(self):
        auto = False  # TODO
        self.calc_irtt()
        if auto:
            return self.RTT_Timer.get_rtt_avrg() * 1000
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
            self.parm_T2 = int(self.port_cfg.parm_T2) / 1000
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
            srtt = float(self._get_rtt())
            if not self.own_port.port_cfg.parm_T2_auto:
                if self.via_calls:
                    srtt = int((len(self.via_calls) * 2 + 1) * srtt)
            if n2 > 3:
                self.t1 = float(((srtt * (n2 + 4)) / 1000) + time.time())
            else:
                self.t1 = float(((srtt * 3) / 1000) + time.time())
        """
        if self.t1 > 0:
            print('t1 > {}'.format(self.t1 - time.time()))
        """

    def set_T2(self, stop=False, link_remote=False):
        if self.port_cfg.parm_full_duplex:
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

    def prozess_I_frame(self):
        self.set_T2()
        self.set_T1(stop=True)
        self.n2 = 0
        self.delUNACK()
        if self.zustand_exec.ns == self.vr:  # !!!! Korrekt
            # Process correct I-Frame
            self.vr = count_modulo(int(self.vr))
            self._recv_data(bytes(self.zustand_exec.frame.payload))
            return True
        else:
            return False

    def delUNACK(self):
        if ((self.zustand_exec.nr - 1) % 8) in self.tx_buf_unACK.keys():
            self._del_unACK_buf()
            return True
        return False

    def _del_unACK_buf(self):
        nr = int(self._rx_buf_last_frame.ctl_byte.nr)
        if nr != -1:  # Check if right Packet
            for i in list(self.tx_buf_unACK.keys()):
                if i == nr:
                    break
                del self.tx_buf_unACK[i]
                # RTT
                self.RTT_Timer.rtt_rx(i)

    def resend_unACK_buf(self, max_pac=None):
        if max_pac is None:
            max_pac = self.parm_MaxFrame
        index_list = list(self.tx_buf_unACK.keys())
        for i in range(min(max_pac, len(index_list))):
            pac = self.tx_buf_unACK[index_list[i]]
            pac.ctl_byte.nr = self.vr
            self.tx_buf_2send.append(pac)

    def exec_cli(self, inp=b''):
        """ CLI Processing like sending C-Text ... """
        if self.ft_obj:
            return False
        # if self.is_link:
        #     return False
        if self.pipe:
            return False
        if not self.cli_remote:
            return False
        self.cli.cli_exec(inp)
        return True

    def _cron_cli(self):
        """ CLI Processing like sending C-Text ... """
        if self.ft_obj is not None:
            return False
        if self.is_link:
            return False
        if self.pipe is not None:
            return False
        self.cli.cli_cron()
        return True

    def _get_new_ax25frame(self):
        pac = AX25Frame(dict(
            uid=str(self.uid),
            from_call_str=str(self.my_call_str),
            to_call_str=str(self.to_call_str),
            via_calls=list(self.via_calls),
            axip_add=tuple(self.axip_add),
            digi_call=str(self.digi_call)
        ))
        return pac

    def build_I_fm_raw_buf(self):
        if self.tx_buf_rawData:
            while len(self.tx_buf_unACK) < self.parm_MaxFrame \
                    and self.tx_buf_rawData:
                self._send_I(False)

    def _send_I(self, pf_bit=False):
        """
        :param pf_bit: bool
        True if RX a REJ Packet
        """
        # A bit of Mess TODO Try to Cleanup
        if self.tx_buf_rawData:  # Double Check, just in case
            new_axFrame = self._get_new_ax25frame()
            new_axFrame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
            new_axFrame.ctl_byte.nr = self.vr  # Receive PAC Counter
            new_axFrame.ctl_byte.ns = int(self.vs)  # Send PAC Counter
            new_axFrame.ctl_byte.IcByte()  # Set C-Byte
            new_axFrame.pid_byte.text()  # Set PID-Byte to TEXT
            # PAYLOAD !!
            pac_len = min(self.parm_PacLen, len(self.tx_buf_rawData))
            new_axFrame.payload = self.tx_buf_rawData[:pac_len]
            self._send_gui_QSObuf_tx(self.tx_buf_rawData[:pac_len])
            #####################################################################
            self.tx_buf_rawData = self.tx_buf_rawData[pac_len:]
            self.tx_buf_unACK[int(self.vs)] = new_axFrame       # Keep Packet until ACK/RR
            self.tx_buf_2send.append(new_axFrame)
            # RTT
            self.RTT_Timer.set_rtt_timer(int(self.vs), int(pac_len))
            # !!! COUNT VS !!!
            self.vs = count_modulo(int(self.vs))  # Increment VS Modulo 8
            self.set_T1()  # Re/Set T1
            # Statistics
            self.tx_byte_count += int(pac_len)

    def send_UA(self):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.UAcByte()
        self.tx_buf_ctl.append(new_axFrame)
        self.set_T3()

    def send_DM(self):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.DMcByte()
        self.tx_buf_ctl.append(new_axFrame)

    def send_DISC(self):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.DISCcByte()
        self.tx_buf_2send.append(new_axFrame)

    def send_DISC_ctlBuf(self):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.DISCcByte()
        self.tx_buf_ctl.append(new_axFrame)

    def send_SABM(self):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.SABMcByte()
        self.tx_buf_2send.append(new_axFrame)

    def send_RR(self, pf_bit=False, cmd_bit=False):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        new_axFrame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        new_axFrame.ctl_byte.nr = self.vr  # Receive PAC Counter
        new_axFrame.ctl_byte.RRcByte()
        if not self.REJ_is_set:
            self.tx_buf_ctl = [new_axFrame]

    def send_REJ(self, pf_bit=False, cmd_bit=False):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        new_axFrame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        new_axFrame.ctl_byte.nr = self.vr  # Receive PAC Counter
        new_axFrame.ctl_byte.REJcByte()
        self.tx_buf_ctl = [new_axFrame]
        self.REJ_is_set = True

    def send_RNR(self, pf_bit=False, cmd_bit=False):
        new_axFrame = self._get_new_ax25frame()
        new_axFrame.ctl_byte.cmd = bool(cmd_bit)  # Command / Respond Bit
        new_axFrame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        new_axFrame.ctl_byte.nr = self.vr  # Receive PAC Counter
        new_axFrame.ctl_byte.RNRcByte()
        self.tx_buf_ctl = [new_axFrame]
        # ??? if not self.REJ_is_set:
        # self.REJ_is_set = True

    def get_state_index(self):
        return self.zustand_exec.stat_index

    def send_sys_Msg_to_gui(self, data):
        if not data:
            return
        gui = self._port_handler.get_gui()
        if not gui:
            return
        gui.sysMsg_to_qso(data, self.ch_index)

    def accept_connection(self):
        self._port_handler.accept_new_connection(self)
        if self.LINK_Connection:
            self.LINK_Connection.cli.change_cli_state(5)
            if self.digi_call in self.port_cfg.parm_Digi_calls:
                if self.accept_digi_connection():
                    self.is_digi = True
                    return
                """
                print(f"Accept Conn UID: {self.uid}")
                print(f"Accept Conn digi_call: {self.digi_call}")
                print(f"Accept Conn parm_Digi_calls: {self.port_cfg.parm_Digi_calls}")
                """
            self.send_to_link(
                f'\r*** Connected to {self.to_call_str}\r'.encode('ASCII', 'ignore')
            )

    def accept_digi_connection(self):
        print(f'DIGI Conn accept..  {self.uid}  ?')
        if not self.LINK_Connection:
            print(f'DIGI Conn accept: No LINK_Connection {self.uid}')
            print(f'DIGI Conn accept: No LINK_Connection {self.LINK_Connection}')

            return False
        digi_uid = self.LINK_Connection.uid
        digi_uid = reverse_uid(digi_uid)
        link_conn_port = self.LINK_Connection.own_port
        return link_conn_port.accept_digi_conn(digi_uid)

    def insert_new_connection(self):
        """ Insert connection for handling """
        is_service = self._is_service_connection()
        self._port_handler.insert_new_connection_PH(new_conn=self, is_service=is_service)

    def _is_service_connection(self):
        return self.cli.service_cli

    def get_state(self):
        return self.zustand_exec.stat_index

    def get_port_handler_CONN(self):
        return self._port_handler

###########################################################################
###########################################################################
###########################################################################
class DefaultStat(object):
    stat_index = 0  # ENDE Verbindung wird gelöscht...

    def __init__(self, ax25_conn):
        self._ax25conn = ax25_conn
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
        self._ax25conn.zustand_exec = self._ax25conn.zustand_tab[zustand_id][0](self._ax25conn)
        """
        if self.ax25conn.port_handler.gui is not None:
            # if self.ax25conn.is_gui:
            self.ax25conn.port_handler.gui.ch_status_update()
        """
    def state_rx_handle(self, ax25_frame):
        self.frame = ax25_frame
        self.nr = self.frame.ctl_byte.nr
        self.ns = self.frame.ctl_byte.ns
        self.pf = self.frame.ctl_byte.pf
        self.cmd = self.frame.ctl_byte.cmd
        {
            'SABM': self._rx_SABM,
            'DISC': self._rx_DISC,
            'UA': self._rx_UA,
            'DM': self._rx_DM,
            'RR': self._rx_RR,
            'RNR': self._rx_RNR,
            'REJ': self._rx_REJ,
            'I': self._rx_I,
            'FRMR': self._rx_FRMR,
            'UI': self._rx_UI,
        }[self.frame.ctl_byte.flag]()

    def _rx_SABM(self):
        self._cleanup()

    def _rx_UI(self):
        pass

    def _rx_DISC(self):
        """UA, wenn der DISC-Block ohne Poll empfangen wurde."""
        if self.cmd:
            self._ax25conn.send_UA()
        elif not self.pf:
            self._ax25conn.send_UA()
        self.S1_end_connection()

    def _rx_UA(self):
        if self.stat_index:
            self._ax25conn.send_SABM()
            self._ax25conn.set_T1()
            self.change_state(2)

    def _rx_DM(self):
        if self.stat_index:
            self._ax25conn.send_SABM()
            self._ax25conn.set_T1()
            self.change_state(2)

    def _rx_RR(self):
        pass

    def _rx_RNR(self):
        pass

    def _rx_REJ(self):
        pass

    def _rx_I(self):
        if self.stat_index:
            # self._ax25conn.set_T1(stop=True)
            self._prozess_I_frame()

    def _rx_FRMR(self):
        if self.stat_index:
            self._ax25conn.send_DISC()
            self._ax25conn.set_T1()
            self.change_state(4)

    def tx(self, ax25_frame):
        pass

    def _send_to_link(self, inp: b''):
        self._ax25conn.send_to_link(inp)

    def _state_cron(self):
        pass

    def cron(self):
        """Global Cron"""
        # TODO Move up
        ###########
        # TODO Connection Timeout
        # if self.stat_index:
        if self._ax25conn.n2 > self._ax25conn.parm_N2:
            self._n2_fail()
        else:
            if time.time() > self._ax25conn.t1:
                self._t1_fail()
            if time.time() > self._ax25conn.t3:
                self._t3_fail()
        self._state_cron()  # State Cronex
        """
        if self.stat_index == 0:
            self.cleanup()
        """

    def _cleanup(self):
        # print('STATE 0 Cleanup')
        self._ax25conn.conn_cleanup()

    def S1_end_connection(self, reconn=True):
        self.change_state(1)
        self._ax25conn.end_connection(reconn)

    def S0_end_connection(self):
        self.change_state(0)
        self._cleanup()

    def _t1_fail(self):
        pass
        # self.cleanup()

    def _t3_fail(self):
        self._cleanup()

    def _n2_fail(self):
        self._cleanup()

    def _reject(self):
        self._ax25conn.send_DM()
        self.S1_end_connection()

    def _prozess_I_frame(self):
        return self._ax25conn.prozess_I_frame()

    def _delUNACK(self):
        return self._ax25conn.delUNACK()


class S1Frei(DefaultStat):  # INIT RX
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    DM            | DM    |       | DM    |        | DM     |         | UA,S5 3)| DM 4)
    """
    stat_index = 1  # FREI

    def _rx_SABM(self):
        self._ax25conn.insert_new_connection()
        self._ax25conn.accept_connection()
        self._ax25conn.send_UA()
        self.change_state(5)
        self._ax25conn.n2 = 0
        self._ax25conn.set_T1(stop=True)
        self._ax25conn.set_T3()
        self._ax25conn.exec_cli()  # Process CLI ( C-Text and so on )
        # Handle Incoming Connection

    def _rx_DISC(self):
        self._reject()
        """
        self.ax25conn.send_DM()
        self.change_state(4)
        """

    def _rx_UA(self):
        self.change_state(0)
        self._ax25conn.set_T1(stop=True)

    def _rx_DM(self):
        self.change_state(0)
        self._ax25conn.set_T1(stop=True)

    def _rx_RR(self):
        if self.pf:
            self._reject()
        """
        self.change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_RNR(self):
        if self.pf:
            self._reject()
        """
        self.change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_REJ(self):
        if self.pf:
            self._reject()
        """
        self.change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_I(self):
        if self.pf:
            self._reject()
        """
        self.change_state(0)
        self._ax25conn.set_T1(stop=True)
        """

    def _rx_FRMR(self):
        self.change_state(4)

    def _t1_fail(self):
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        """
        if self.ax25conn.is_link_remote:
            parm_n2 = self.ax25conn.parm_N2
        else:
            parm_n2 = 3
        """
        parm_n2 = 3
        if self._ax25conn.n2 > parm_n2:
            # print("S1 t1 FAIL > N2")
            self.change_state(0)

    def _t3_fail(self):
        # print("S1 t3 FAIL")
        self.change_state(0)


class S2Aufbau(DefaultStat):  # INIT TX
    stat_index = 2  # AUFBAU Verbindung Aufbau

    def tx(self, ax25_frame = None):
        """ NOT USED... CLEANUP !!!"""
        pass

    def _rx_SABM(self):
        self._accept()

    def _rx_DISC(self):
        self._reject()

    def _rx_UA(self):
        self._accept()

    def _rx_DM(self):
        self._reject()

    def _rx_FRMR(self):
        pass

    def _rx_I(self):
        pass

    def _accept(self):
        # print("S2 - ACCEPT")
        self._ax25conn.tx_buf_2send = []  # Clean Send Buffer.
        self._ax25conn.tx_buf_rawData = b''  # Clean Send Buffer.
        self._ax25conn.n2 = 0
        self._ax25conn.accept_connection()
        self.change_state(5)

    def _reject(self):
        self._ax25conn.send_sys_Msg_to_gui(f'*** Busy from {self._ax25conn.to_call_str}')
        self._ax25conn.send_to_link(f'*** Busy from {self._ax25conn.to_call_str}'.encode('ASCII', 'ignore'))
        self.S1_end_connection(reconn=False)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        if self._ax25conn.n2 < self._ax25conn.parm_N2:
            self._ax25conn.send_SABM()
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        to_qso_win = f'\n*** Failed to connect to {self._ax25conn.to_call_str} > ' \
                     f'Port {self._ax25conn.own_port.port_id}\n'
        user_db_ent = USER_DB.get_entry(self._ax25conn.to_call_str, add_new=False)
        if user_db_ent:
            if user_db_ent.Name:
                to_qso_win = f'*** Failed to connect to {self._ax25conn.to_call_str} - ' \
                             f'({user_db_ent.Name}) > Port {self._ax25conn.own_port.port_id}'
        self._ax25conn.send_to_link(to_qso_win.encode('ASCII', 'ignore'))
        self._ax25conn.send_sys_Msg_to_gui(to_qso_win)
        self._ax25conn.send_DISC_ctlBuf()
        self.S1_end_connection(reconn=False)


class S3sendFRMR(DefaultStat):
    stat_index = 3  # Blockrückruf

    def _rx_UA(self):
        pass

    def _rx_DM(self):
        pass

    def _rx_RR(self):
        pass

    def _rx_RNR(self):
        pass

    def _rx_REJ(self):
        pass

    def _rx_I(self):
        pass

    def _t1_fail(self):
        pass
        # Send FRMR

    def _t3_fail(self):
        pass
        # Send FRMR

    def _n2_fail(self):
        # self.ax25conn.send_SABM()
        self.S1_end_connection()


class S4Abbau(DefaultStat):
    stat_index = 4  # ABBAU

    def tx(self, ax25_frame):
        self._ax25conn.n2 = 0
        self._ax25conn.tx_buf_rawData = b''
        self._ax25conn.tx_buf_2send = []
        self._ax25conn.tx_buf_unACK = {}
        self._ax25conn.send_DISC()
        self._ax25conn.set_T1()

    def _rx_UA(self):
        self.end_conn()

    def _rx_DM(self):
        self.end_conn()

    def _rx_SABM(self):
        self._reject()

    def _rx_RR(self):
        pass
        """
        if self.pf:
            self.reject()
        """

    def _rx_REJ(self):
        pass
        """
        if self.pf:
            self.reject()
        """

    def _rx_I(self):
        pass
        """
        if self.pf:
            self.reject()
        """

    def _rx_RNR(self):
        pass
        """
        if self.pf:
            self.reject()
         """

    def end_conn(self):
        self.S1_end_connection()
        self._ax25conn.n2 = 100

    def _state_cron(self):
        pass

    def _t1_fail(self):
        # self.change_state(2)
        self._ax25conn.send_DISC()
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self.S1_end_connection()


class S5Ready(DefaultStat):
    """
    I mit |I ohne |RR mit |RR ohne|REJ mit|REJ ohne|RNR mit | RNR ohne| SABM    | DISC
    RR    | I/RR 1)| RR   | I/- 2)| RR    | I      | RR,S9  | S9      | UA      | UA,S1
    """
    stat_index = 5  # BEREIT

    def _rx_SABM(self):
        self._ax25conn.send_UA()

    def _rx_UA(self):
        pass

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        if self._delUNACK():
            self._ax25conn.set_T1(stop=True)
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)
            self._ax25conn.set_T2(stop=True)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)
            # self.ax25conn.set_T2(stop=True)
        else:
            # Maybe all ? or Automode ?
            self._ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self._ax25conn.set_T1()

    def _rx_I(self):
        if not self._prozess_I_frame():
            self._ax25conn.send_REJ(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1()
            self.change_state(6)  # go into REJ_state
        else:
            if self.pf:
                self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            elif not self._ax25conn.tx_buf_unACK and \
                    not self._ax25conn.tx_buf_2send and \
                    not self._ax25conn.tx_buf_rawData:
                self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(9)

    def tx(self, ax25_frame):
        if time.time() > self._ax25conn.t1:
            if self._ax25conn.tx_buf_rawData:
                self._ax25conn.build_I_fm_raw_buf()

    def _state_cron(self):
        pass

    def _t1_fail(self):
        # TODO Move up
        if time.time() > self._ax25conn.t2:
            # Nach 5 Versuchen
            if self._ax25conn.n2:
                if self._ax25conn.n2 > 4:
                    # BULLSHIT ?
                    self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
                    self._ax25conn.set_T1()
                    self.change_state(7)  # S7 Warten auf Final
                    # self.rtt_timer.set_rtt_single_timer()
                else:
                    if self._ax25conn.tx_buf_unACK:
                        self._ax25conn.resend_unACK_buf(1)
                        self._ax25conn.n2 += 1
                        self._ax25conn.set_T1()
            else:
                if self._ax25conn.tx_buf_unACK:
                    self._ax25conn.resend_unACK_buf()
                    self._ax25conn.n2 += 1
                    self._ax25conn.set_T1()

                if self._ax25conn.tx_buf_rawData and not self._ax25conn.tx_buf_unACK:
                    self._ax25conn.build_I_fm_raw_buf()
                    self._ax25conn.set_T1()

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(7)  # S7 Warten auf Final
        # self.rtt_timer.set_rtt_single_timer()


# class S6sendREJ(S5Ready):
class S6sendREJ(DefaultStat):
    """"""
    stat_index = 6  # REJ ausgesandt

    def tx(self, ax25_frame):
        pass

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(5)

    def _rx_I(self):
        if self._prozess_I_frame():
            if self.pf:
                self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            elif not self._ax25conn.tx_buf_unACK and \
                    not self._ax25conn.tx_buf_2send and \
                    not self._ax25conn.tx_buf_rawData:
                self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(5)

    def _rx_REJ(self):

        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            # Maybe all ? or Automode ?
            self._ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self._ax25conn.set_T1()

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1()
            self._ax25conn.set_T2(stop=True)

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(15)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(7)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(7)  # S7 Warten auf Final

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self.change_state(2)


class S7WaitForFinal(DefaultStat):
    stat_index = 7  # Warten auf Final

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(5)
        # self.rtt_timer.rtt_single_rx(stop=True)

    def _rx_I(self):
        if self._prozess_I_frame():
            # self.change_state(5)
            if self.pf:
                self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            elif not self._ax25conn.tx_buf_unACK and \
                    not self._ax25conn.tx_buf_2send and \
                    not self._ax25conn.tx_buf_rawData:
                self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=True)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # Maybe all ? or Automode ?
        self._ax25conn.resend_unACK_buf(1)
        # self.ax25conn.set_T1()    ?????????
        self._ax25conn.set_T1()
        if self.pf:
            # self.rtt_timer.rtt_single_rx()
            self._ax25conn.set_T1(stop=True)
            self._ax25conn.set_T2(stop=True)
            self.change_state(5)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()

        if self.pf:
            # self.rtt_timer.rtt_single_rx()
            self._ax25conn.set_T1(stop=True)
            self._ax25conn.set_T2(stop=True)
            self.change_state(5)

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            # self.rtt_timer.rtt_single_rx()
            self._ax25conn.set_T1(stop=True)
            self._ax25conn.set_T2(stop=True)
            self.change_state(9)
        else:
            self.change_state(12)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self.change_state(2)


class S8SelfNotReady(DefaultStat):
    stat_index = 8  # nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T2(stop=True)
            self._ax25conn.set_T1(stop=True)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self._ax25conn.set_T1()

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(10)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        if time.time() > self._ax25conn.t2:
            # Nach 5 Versuchen
            if self._ax25conn.n2:
                if self._ax25conn.n2 > 4:
                    # BULLSHIT ?
                    self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
                    self._ax25conn.set_T1()
                    self.change_state(11)  # S7 Warten auf Final
                    # self.rtt_timer.set_rtt_single_timer()
                else:
                    if self._ax25conn.tx_buf_unACK:
                        self._ax25conn.resend_unACK_buf(1)
                        self._ax25conn.n2 += 1
                        self._ax25conn.set_T1()
            else:
                if self._ax25conn.tx_buf_unACK:
                    self._ax25conn.resend_unACK_buf()
                    self._ax25conn.n2 += 1
                    self._ax25conn.set_T1()

                if self._ax25conn.tx_buf_rawData and not self._ax25conn.tx_buf_unACK:
                    self._ax25conn.build_I_fm_raw_buf()
                    self._ax25conn.set_T1()

    def _t3_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final
        # self.rtt_timer.set_rtt_single_timer()

    def _n2_fail(self):
        pass


class S9DestNotReady(DefaultStat):
    stat_index = 9  # Gegenstelle nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(5)

    def _rx_I(self):
        if self._prozess_I_frame():
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            self._ax25conn.send_REJ(pf_bit=self.pf, cmd_bit=False)
            self.change_state(15)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self._ax25conn.set_T1(stop=True)

        self.change_state(5)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(5)

    def _rx_RNR(self):
        # self.change_state(10)
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def _t1_fail(self):
        pass
        """
        self.ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final
        """

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final

    def _n2_fail(self):
        pass


class S10BothNotReady(DefaultStat):
    stat_index = 10  # Beide Seiten nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

        self.change_state(8)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(8)

    def _rx_RNR(self):
        # self.change_state(10)
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _t1_fail(self):
        pass
        """
        self.ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self.ax25conn.n2 += 1
        self.ax25conn.set_T1()
        self.change_state(13)  # S7 Warten auf Final
        """

    def _t3_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(13)  # S7 Warten auf Final

    def _n2_fail(self):
        pass


class S11SelfNotReadyFinal(DefaultStat):
    stat_index = 11  # Selber nicht bereit und auf Final warten

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        # if self.pf or self.cmd:
        self._delUNACK()

        if self.cmd:
            self._ax25conn.send_RNR(pf_bit=True, cmd_bit=False)
            self._ax25conn.set_T1()
        elif self.pf:
            self._ax25conn.set_T1(stop=True)
            self.change_state(8)
            # self.rtt_timer.rtt_single_rx()

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(8)  # ???
            # self.rtt_timer.rtt_single_rx()  # ???
        else:
            self._ax25conn.resend_unACK_buf(1)
            self._ax25conn.set_T1()
            # self.ax25conn.set_T1(stop=True)

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf and not self.cmd:
            # self.rtt_timer.rtt_single_rx()
            self.change_state(10)
        elif self.cmd:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(13)
        else:
            self.change_state(13)
        # self.rtt_timer.rtt_single_rx(stop=True)

    def _state_cron(self):
        pass

    def _t1_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self.change_state(2)


class S12DestNotReadyFinal(DefaultStat):
    stat_index = 12  # Gegenstelle nicht bereit und auf Final warten

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(5)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()

        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.set_T1(stop=True)
            self.change_state(5)
        else:
            self.change_state(7)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        self._ax25conn.resend_unACK_buf(1)
        self._ax25conn.set_T1()
        if self.pf:
            self.change_state(5)
            # self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.change_state(7)

    def _rx_RNR(self):
        # self.change_state(10)
        self._delUNACK()
        if self.pf:
            self.change_state(9)
            # self.ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self.change_state(2)


class S13BothNotReadyFinal(DefaultStat):
    stat_index = 13  # Beide Seiten nicht bereit und auf Final warten

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self.change_state(8)
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)
        else:
            self.change_state(11)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self.change_state(8)
        else:
            self._ax25conn.resend_unACK_buf(1)
            self._ax25conn.set_T1()
            self.change_state(11)

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self.change_state(11)

    def _t1_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()

    def _t3_fail(self):
        pass

    def _n2_fail(self):
        self._ax25conn.send_SABM()
        self.change_state(2)


class S14sendREJselfNotReady(DefaultStat):  # TODO  /  / Testing
    stat_index = 14  # REJ ausgesandt u. Selbst nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(8)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self._ax25conn.set_T1()

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(16)

    def _t1_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RNR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def _n2_fail(self):
        pass


class S15sendREJdestNotReady(DefaultStat):  # TODO  /  / Testing
    stat_index = 15  # REJ ausgesandt u. Gegenstelle nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(5)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        self.change_state(9)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

        self.change_state(6)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self._ax25conn.set_T1()
        self.change_state(6)

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RR(pf_bit=self.pf, cmd_bit=False)

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(12)  # S7 Warten auf Final

    def _n2_fail(self):
        pass


class S16sendREJbothNotReady(DefaultStat):  # TODO  / / Testing
    stat_index = 16  # REJ ausgesandt u. beide Seiten nicht bereit

    def _rx_SABM(self):
        self._ax25conn.send_UA()
        self.change_state(5)

    def _rx_I(self):
        self._prozess_I_frame()
        self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _rx_RR(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        # if self.pf or self.cmd:
        if self.cmd:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
            self._ax25conn.set_T1(stop=True)

        self.change_state(14)

    def _rx_REJ(self):
        self._ax25conn.n2 = 0
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)
        else:
            self._ax25conn.resend_unACK_buf(1)
            # self.ax25conn.set_T1()    ?????????
            self._ax25conn.set_T1()
        self.change_state(14)

    def _rx_RNR(self):
        self._delUNACK()
        if self.pf:
            self._ax25conn.send_RNR(pf_bit=self.pf, cmd_bit=False)

    def _t1_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def _t3_fail(self):
        self._ax25conn.send_RR(pf_bit=True, cmd_bit=True)
        self._ax25conn.n2 += 1
        self._ax25conn.set_T1()
        self.change_state(11)  # S7 Warten auf Final

    def _n2_fail(self):
        pass
