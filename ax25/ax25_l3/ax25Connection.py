"""
    PoPT - AX25 L3 Connection
    AX.25 PROT Packet Handling
"""
import time
from datetime import datetime

from ax25.ax25_l3.ax25_L3_StateTab import AX25L3_STATE_TAB, S1Frei, S2Aufbau
from ax25.ax25_l3.ax25RTT import RTT
from cfg.constant import TAG_QSO_PRP_STATUS_RX, TAG_QSO_PRP_STATUS_TX, CLI_TYP_PIPE, CLI_TYP_NO_CLI, CLI_TYP_TASK_FWD
from classes.CLbuffers import ByteArrayBuffer, ListBuffer
from cli.cli_frontends.cliConv import ConverseCLI
from cli import CLI_OPT, NoneCLI
from ax25.ax25_util.ax25UI_Pipe import AX25Pipe
from ax25.ax25_l2.ax25dec_enc import AX25Frame
from cfg.default_config import getNew_pipe_cfg, getNew_station_cfg
from cfg.logger_config import logger, LOG_BOOK
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import reverse_uid
from fnc.str_fnc import conv_time_DE_str
from prp import init_prpAX25L3
from ax25.ax25_ft.ax25FileTransfer import FileTransport, ft_rx_header_lookup
from fnc.loc_fnc import locator_distance
from sound.popt_sound import SOUND


class AX25Conn:
    def __init__(self, ax25_frame, port, rx=True):
        """ AX25 L3 Connection """
        """ Global Stuff """
        self.own_port           = port
        self._popt_handler      = port.port_get_PH()
        self._userDB            = self._popt_handler.userDB
        """ Port Config Parameter """
        self.port_id: int       = self.own_port.port_id
        self._port_cfg :dict    = POPT_CFG.get_port_CFG_fm_id(self.port_id)

        self.port_name: str     = self._port_cfg.get('parm_PortName', '')
        self.parm_PacLen        = self._port_cfg.get('parm_PacLen', 160)  # Max Pac len
        self.parm_MaxFrame      = self._port_cfg.get('parm_MaxFrame', 3)  # Max (I) Frames
        self.parm_MaxFrameAuto  = self._port_cfg.get('parm_MaxFrameAuto', True)  # Max (I) Frames
        self._parm_TXD          = self._port_cfg.get('parm_TXD', 400)  # TX Delay for RTT Calculation !! Need to be high on AXIP for T1 calculation
        #self._parm_Kiss_TXD     = 0
        #self._parm_Kiss_Tail    = 0
        #if self.own_port.tnc_protocol.is_enabled:
        self._parm_Kiss_TXD     = self._port_cfg.get('parm_kiss_TXD', 35)
        self._parm_Kiss_Tail    = self._port_cfg.get('parm_kiss_Tail', 15)
        self._parm_T2           = int(self._port_cfg.get('parm_T2', 2888))  # T2 (Response Delay Timer) Default: 2888 / (parm_baud / 100)
        self._parm_T3           = self._port_cfg.get('parm_T3', 180)  # T3 (Inactive Link Timer)
        self.parm_N2            = self._port_cfg.get('parm_N2', 20)  # Max Try   Default 20
        self._parm_baud         = self._port_cfg.get('parm_baud', 1200)  # Baud for calculating Timer
        """ Config new Connection Address """
        #####################################
        ax25_conf = ax25_frame.get_frame_conf()
        self.axip_add = tuple(ax25_conf.get('axip_add', ()))
        if rx:
            self._incoming_conn     = True
            self.uid                = str(reverse_uid(ax25_conf.get('uid', '')))  # Unique ID for Connection
            self.to_call_str_add    = str(ax25_conf.get('from_call_str', ''))
            self.to_call_str        = str(ax25_conf.get('from_call_str', ''))
            self.my_call_str_add    = str(ax25_conf.get('to_call_str', ''))
            self.my_call_str        = str(ax25_conf.get('to_call_str', ''))
            self.my_call            = str(ax25_conf.get('to_call', ''))
            self.via_calls          = list(ax25_conf.get('via_calls_str', []))
            self.via_calls.reverse()
        else:
            self._incoming_conn     = False
            self.uid                = str(ax25_conf.get('uid', ''))  # Unique ID for Connection
            self.to_call_str_add    = str(ax25_conf.get('to_call_str', ''))
            self.to_call_str        = str(ax25_conf.get('to_call_str', ''))
            self.my_call_str_add    = str(ax25_conf.get('from_call_str', ''))
            self.my_call_str        = str(ax25_conf.get('from_call_str', ''))
            self.my_call            = str(ax25_conf.get('from_call', ''))
            self.via_calls          = list(ax25_conf.get('via_calls_str', []))
        """ GUI Stuff """
        self.ch_index: int = 0
        self._my_locator = POPT_CFG.get_guiCFG_locator()
        """ Station CFG Parameter """
        self._stat_cfg      = {}
        self._my_call_alias = ''
        self._to_call_alias = ''
        """ IO Buffer AX25 Packet Handling """
        self.tx_buf_ctl   = []     # Buffer for CTL (S) Frame to send on next Cycle
        self.tx_buf_2send = []     # Buffer for Sending. Will be processed in ax25PortHandler
        self.tx_buf_unACK = {}     # Buffer for UNACK I-Frames
        self.rx_buf_last_data = bytearray()     # Buffers for last Frame
        """ TX Buffer for PRP """
        """ IO Buffer For GUI / CLI """
        self.tx_buf_rawData:ByteArrayBuffer = ByteArrayBuffer()     # Buffer for TX RAW Data that is not packed yet into a Frame

        self._is_tx_buffer     = lambda : (self._prp_remote.is_tx_buffer() or
                                           not self.tx_buf_rawData.is_empty)
        # RX
        self.rx_buf_rawData    = bytearray()  # Buffer RX QSO for AutoConnTask
        self.rx_tx_buf_guiData = ListBuffer() # Buffer for GUI QSO Window ('TX', data), ('RX', data)
        """ DIGI / Link to other Connection for Auto processing """
        self.LINK_Connection    = None
        self.LINK_rx_buff       = ByteArrayBuffer()
        self.is_link            = False
        self.is_link_remote     = False
        self.digi_call          = ''
        self.is_digi            = False
        """ PoPT Remote Protocol (PRP) """
        # self._prp_remote = PRPremote(self._port_handler, self)
        self._prp_remote        = init_prpAX25L3(self._popt_handler, self)

        """ Port Variablen"""
        # TODO Private / Clean Up / OPT
        self.vs  = 0   # Sendefolgenummer     / N(S) = V(R)  TX
        self.vr  = 0   # Empfangsfolgezählers / N(S) = V(R)  TX
        self._nr = -1  # Empfangsfolge Gegenstation / ACK
        self._ns = -1  # Sendefolge Gegenstation / ACK
        self._frame_payload = bytearray()  # Payload of received Frame
        self.t1  = 0   # ACK
        self.t2  = 0   # Respond Delay
        self.t3  = 0   # Connection Hold
        self.n2  = 0   # Fail Counter / No Response Counter
        self._await_disco = False
        """ S-Packet / CTL Vars"""
        self.REJ_is_set: bool = False
        self.is_RNR: bool     = False
        """ Max Frame Auto """
        self._MaxFrameCFG       = 0
        self._autoMaxFrameScore = 0
        self._is_resented       = False
        """ Timer Calculation & other Data for Statistics """
        self.IRTT = 0
        self.calc_irtt()
        self.RTT_Timer = RTT(self)
        self.tx_byte_count = 0
        self.rx_byte_count = 0
        self.tx_pack_count = 0
        self.rx_pack_count = 0
        """ Connection Start Time """
        self.time_start = datetime.now()
        """ File Transfer Stuff """
        self.ft_queue = []
        self.ft_obj   = None
        """ Pipe-Tool """
        self.pipe     = None
        """ BBS Control """
        self.bbs_connection = None
        """ Link Holder / Not related to Link Connection Stuff """
        self.link_holder_on: bool = False
        self.link_holder_interval: int = 30  # Minutes
        self.link_holder_timer = time.time()
        self.link_holder_text: str = '\r'
        """ User DB Entry """
        self.user_db_ent    = self._userDB.get_entry(self.to_call_str)
        self._encoding      = 'CP437'     # 'UTF-8'
        self.cli_language   = 0
        self.last_connect   = None
        if hasattr(self.user_db_ent, 'Language'):
            if self.user_db_ent.Language == -1:
                self.user_db_ent.Language = int(POPT_CFG.get_guiCFG_language())
            self.cli_language = self.user_db_ent.Language
        if hasattr(self.user_db_ent, 'last_conn'):
            self.last_connect = self.user_db_ent.last_conn
        if hasattr(self.user_db_ent, 'Encoding'):
            self._encoding = self.user_db_ent.Encoding
        self.set_distance()
        #self._set_user_db_ent()
        self.set_station_cfg()  # Station Individual Parameter
        """ CLI CFG """
        self.cli_remote     = True
        self.noty_bell      = False
        self.cli = NoneCLI(self)
        self.cli_type = ''
        """ Pipe CFG """
        pipe_cfg = POPT_CFG.get_pipe_CFG_fm_UID(call=str(self.my_call_str),
                                                port_id=-1)
        if not all((pipe_cfg,
                   pipe_cfg.get('pipe_parm_Proto', False))):
            """ Init CLI """
            self._init_cli()
            if hasattr(self.user_db_ent, 'sys_pw_autologin'):
                if not self.user_db_ent.sys_pw_autologin and not rx:
                    self.cli.change_cli_state(state=1)
                elif self.user_db_ent.sys_pw_autologin and not rx:
                    self.cli.change_cli_state(state=6)
            else:
                if not rx:
                    self.cli.change_cli_state(state=1)
        else:
            """ Init Pipe """
            if not self.set_pipe(pipe_cfg):
                self._await_disco = True
        """ Init State Tab """
        if rx:
            self.set_T1()
            self.set_T3()
            self._l3_state_exec = S1Frei(self)
            self.handle_rx(ax25_frame)
        else:
            # self.t2 = time.time() + 5
            self._l3_state_exec = S2Aufbau(self)
            # self.cli.change_cli_state(state=1)

    ########################
    # AX25 L3 State CTL
    def change_l3_state(self, state_id: int):
        self._l3_state_exec = AX25L3_STATE_TAB[state_id][0](self)

    @property
    def l3_state_id(self):
        return self._l3_state_exec.stat_index

    ########################
    # INIT
    def set_station_cfg(self):
        stat_cfg = POPT_CFG.get_stat_CFG_fm_call(self.my_call_str)
        if not stat_cfg:
            stat_cfg = POPT_CFG.get_stat_CFG_fm_call(self.my_call)

        self._stat_cfg = stat_cfg
        self._set_packet_param()

        """
        if self.my_call_str in self._port_handler.ax25_stations_settings.keys():
            self._stat_cfg = self._port_handler.ax25_stations_settings[self.my_call_str]
        else:
            for call in list(self._port_handler.ax25_stations_settings.keys()):
                if self.my_call in call:
                    if self.my_call in self._port_handler.ax25_stations_settings.keys():
                        self._stat_cfg = self._port_handler.ax25_stations_settings[self.my_call]
                        break
        self._set_packet_param()
        """
        return True

    def _set_user_db_ent(self):
        self.user_db_ent = self._userDB.get_entry(self.to_call_str)
        if self.user_db_ent is None:
            return
        self.user_db_ent.Connects += 1
        self.last_connect = self.user_db_ent.last_conn
        self.user_db_ent.last_conn = conv_time_DE_str()
        self._encoding    = self.user_db_ent.Encoding
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
        if self._stat_cfg.get('stat_parm_PacLen', 0):
            self.parm_PacLen = int(self._stat_cfg.get('stat_parm_PacLen', 0))
        else:
            self.parm_PacLen = int(self._port_cfg.get('parm_PacLen', 160))

        if self._stat_cfg.get('stat_parm_MaxFrame', 0):
            self.parm_MaxFrame = int(self._stat_cfg.get('stat_parm_MaxFrame', 0))
        else:
            self.parm_MaxFrame = int(self._port_cfg.get('parm_MaxFrame', 3))

        # self.user_db_ent = USER_DB.get_entry(self.to_call_str)

        if self.user_db_ent:
            if int(self.user_db_ent.pac_len):
                self.parm_PacLen = int(self.user_db_ent.pac_len)
            if int(self.user_db_ent.max_pac):
                self.parm_MaxFrame = int(self.user_db_ent.max_pac)

    ###################################################################
    # Converse Interconnect
    def enter_converse_cli(self):
        self.cli = ConverseCLI(self)
        #self.cli_type = str(self.cli.cli_name)

    # ========= TX
    def send_data(self,
                  data: bytes,
                  gui_echo=True,
                  file_trans=False,
                  use_prp=False # TODO  use_prp=True / disabled
                  ):
        """
        Normale Daten von CLI oder GUI(QSO)
        :param data:        bytes = Daten
        :param gui_echo:    bool = TX-Echo an GUI zurück
        :param file_trans:  bool = Ist Filetransfer (Daten sind für Dateiübertragung)
        :param use_prp:     bool = PRP nutzen, wenn es Sinn macht (Daten komprimiert werden können)
        :return: bool
        """
        if self._await_disco:
            return False
        if self.ft_obj is not None and not file_trans:
            return False
        if not data:
            return False
        if not isinstance(data, (bytes, bytearray)):
            logger.error(f"Incorrect Datatype: data({type(data)}) should be bytes or bytearray")
            return False
        self._link_holder_reset()
        # Send via PRP CLI-ESC
        if use_prp:
            # Version Check & CLI-ESC enabled & is sendet compressed?
            if self._prp_remote.prp_tx_esc_cli(data):
                if gui_echo:
                    no_eol = False if not data.endswith(b'\n') and not data.endswith(b'\r') else True
                    # PRP Status Msg an QSO Fenster senden
                    self.send_gui_QSO_PRPstatus(
                        data=self._prp_remote.get_cli_esc_sender_status(),
                        tx=True,
                        no_eol=no_eol)
                    # TX Echo senden
                    self._send_gui_QSO_tx(data)

                return True

        self.tx_buf_rawData.buffer_write(data)
        # TX Echo senden
        if gui_echo:
            self._send_gui_QSO_tx(data)
        return True


    def _get_payload_fm_tx_buffer(self):
        """ TX-Buffer / PRP-Buffer / PRP-Prio-Buffer """
        ######################################
        # PRP TX Buffer !!                   #
        data     = self._prp_remote.prp_tx_buffer.get_payload_fm_tx_buffer(int(self.parm_PacLen))
        data_len = len(data)
        #################################################
        # Normal TX Buffer                              #
        if data_len < self.parm_PacLen:                 #
            if not self.tx_buf_rawData.is_empty:
                pac_len = int(self.parm_PacLen) - data_len  #
                data   += self.tx_buf_rawData.buffer_read(pac_len)

        #################################################
        return data

    # ========= RX
    def handle_rx(self, ax25_frame):
        """
        self.zustand_exec.state_rx_handle >
        self.zustand_exec._rx_I           >
        self.prozess_I_frame              >
        self._recv_data
        """
        self._nr = int(ax25_frame.ctl_byte.nr)
        self._ns = int(ax25_frame.ctl_byte.ns)
        self._frame_payload = bytearray(ax25_frame.payload)
        self._l3_state_exec.state_rx_handle(ax25_frame=ax25_frame)
        self.set_T3()

    def process_I_frame(self):
        self.set_T2()
        if self._ns == self.vr:
            self.vr = (self.vr + 1) % 8     # Modulo 8
            self._process_recv_data(bytearray(self._frame_payload))
            self._frame_payload = bytearray()
            self.delUNACK()  # ACKs verarbeiten
            return True
        else:
            # Duplikat oder außerhalb Fenster → stillschweigend ignorieren
            return False

    def _process_recv_data(self, data: bytearray):
        """ Called fm self.process_I_frame() """
        # Statistic
        self.rx_byte_count += len(data)
        self.rx_pack_count += 1
        """ Link/Node-DIGI """
        if self.is_link:
            self.LINK_rx_buff.buffer_write(data)
            self.exec_cli(data)
            return
        """  Pipe-Tool """
        if self._pipe_rx(data):
            return
        """ BBS/PMS-FWD """
        if self._bbsFwd_rx(data):
            return
        """ FT """
        self._ft_check_incoming_ft(data)
        if self._ft_handle_rx(data):
            self.rx_buf_last_data = bytearray()
            return
        """ Remote Monitor """
        data = self._prp_rx(data)
        if not data:
            self.rx_buf_last_data = data
            return
        self._send_gui_QSO_rx(data)
        """ Station ( RE/DISC/Connect ) Sting Detection """
        self._set_dest_call_fm_data_inp(data)
        """ Save last Frame """
        self.rx_buf_last_data = data
        self.rx_buf_rawData  += data    # TODO Need better solution. Just for BBS-FWD-INIT
        """ CLI """
        self.exec_cli(data)
        return

    #############################
    # I/O Buffer Helper
    def clear_tx_buff(self):
        self.tx_buf_rawData.buffer_clear()
        #self._tx_buf_prio_Rest = bytearray()
        #self._tx_buf_prio_Q: list[bytes] = []

    #############################
    # AX25 Frame Buffer Handling
    def delUNACK(self):
        if ((self._nr - 1) % 8) in self.tx_buf_unACK.keys():
            self._del_unACK_buf()
            if not self.tx_buf_unACK:
                if not self._is_resented:
                    self._set_autoMaxFrameScore(True)
                self._is_resented = False
                self.set_T1(stop=True)
                self.set_T2(stop=True)
                return True
            self.set_T1()
        return False

    def _del_unACK_buf(self):
        if self._nr == -1:  # Check if right Packet
            return
        for i in list(self.tx_buf_unACK.keys()):
            if i == self._nr:
                break
            del self.tx_buf_unACK[i]
            # RTT
            self.RTT_Timer.rtt_rx(i)

    def resend_unACK_buf(self, max_pac=None):
        if not self.tx_buf_unACK:
            return

        if max_pac is None:
            max_pac = self.parm_MaxFrame

        index_list = list(self.tx_buf_unACK.keys())
        for i in range(min(max_pac, len(index_list))):
            pac = self.tx_buf_unACK[index_list[i]]
            pac.ctl_byte.nr = self.vr
            self.tx_buf_2send.append(pac)

        self.set_T1()
        # Auto Max-Frame
        self._set_autoMaxFrameScore(False)
        self._is_resented = True

    #############################
    # GUI I/O
    def _send_gui_QSO_tx(self, data: bytes):
        """ to QSO (TX-Echo)"""
        if self.ft_obj or self.pipe:
            return
        self.rx_tx_buf_guiData.buffer_write(
            ('TX', data)
        )


    def _send_gui_QSO_rx(self, data: bytes):
        """ to QSO (RX Date to QSO)"""
        if self.ft_obj or self.pipe:
            return
        self.rx_tx_buf_guiData.buffer_write(
            ('RX', data)
        )

    def _send_gui_QSO_sysMsg(self, data: str):
        """ Sys Msg to QSO with Timestamp """
        self.rx_tx_buf_guiData.buffer_write(
            ('SYS', data)
        )

    def send_sys_Msg_to_gui(self, data: str):
        """ to QSO Connect Status (Link Setup, Disconnected, ...)"""
        if not data:
            return

        lb_msg = f"CH {int(self.ch_index)} - {str(self.my_call_str)}: - {str(self.uid)} - Port: {int(self.port_id)}"
        LOG_BOOK.info(lb_msg)
        LOG_BOOK.info(f"CH {int(self.ch_index)} - {str(self.my_call_str)}: {data}")

        self._send_gui_QSO_sysMsg(data)

    def send_gui_QSO_PRPstatus(self, data: str, tx: bool, no_eol=False):
        """ PRP Status Msg to QSO  """
        if tx:
            tag = TAG_QSO_PRP_STATUS_TX
        else:
            tag = TAG_QSO_PRP_STATUS_RX

        if no_eol:
            data = '\n' + data
        self.rx_tx_buf_guiData.buffer_write(
            (tag, data)
        )

    #############################
    # Crone
    def exec_cron(self):
        """ DefaultStat.cron() """
        ###############################################
        """  DIGI / BBS / FT / CLI /LH Funktion """
        self._app_cron()
        """ Zustandstabelle Crone """
        self._l3_state_exec.cron()
        if self.l3_state_id == 0:
            self.conn_cleanup()
            return
        if self.l3_state_id == 1:
            if not self.tx_buf_ctl:
                self.change_l3_state(0)
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
            self._prp_cron()
            self._link_holder_cron()
        return True

    #############################
    # CLI Stuff
    def _init_cli(self):
        del self.cli
        cli_key = self._stat_cfg.get('stat_parm_cli', getNew_station_cfg().get('stat_parm_cli', CLI_TYP_NO_CLI))
        self.cli_type = str(cli_key)
        self.cli = CLI_OPT.get(cli_key, NoneCLI)(self)
        """
        cmds = []
        for k, cli in CLI_OPT.items():
            test_cli = cli(self)
            test_cli.init()
            cli_cmds = test_cli.get_cmds()
            for el in cli_cmds:
                if el not in cmds:
                    cmds.append(el)
            logger.debug(f"{k} : {cli_cmds}")

        logger.debug(f"All CLI CMDs : {sorted(cmds)}")
        """

    def _reinit_cli(self):
        if self.cli_type == CLI_TYP_TASK_FWD:
            #self.bbsFwd_init()
            return
        if self.pipe:
            return
        self._init_cli()
        if hasattr(self.user_db_ent, 'sys_pw_autologin'):
            if self.user_db_ent.sys_pw_autologin :
                self.cli.change_cli_state(state=6)
                return
        self.cli.change_cli_state(state=1)

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

    ##########################################################
    # PoPT Remote Protocol (PRP)
    def _prp_rx(self, data: bytes):
        """ Empfangene Daten durch PRP Decoder schieben und Rest zurück """
        # Sende Daten an PRP Decoder und erhalte Rest(nicht PRP Daten)
        rest_data_for_cli  = self._prp_remote.prp_rx(data)

        return rest_data_for_cli

    # == PRP - Remote Monitor I/O- PoPT Remote Protocol (PRP)
    def remote_monitor_update_tx(self, ax25frame_conf: dict):
        """
        Called fm port_handler.update_monitor()
        Sendet ax25-Frames für Remote Monitor an PRP
        """
        self._prp_remote.remote_monitor_update(ax25frame_conf)

    # == Remote Mon
    """
    def prp_del_rem_mon_buff(self, opt_id):
        # PRP Remote Mon & Disco
        if opt_id is None:
            # == Disco
            self._wait_tx_buf_prp_lock('_clear_tx_buff_prp')
            self._tx_buf_prp_Q: list[tuple[int, bytes]] = []
            self._tx_buf_prp_lock = False
        else:
            # == Remote Monitor
            self._wait_tx_buf_prp_lock('_clear_tx_buff_prp')
            self._tx_buf_prp_Q = [(id_, data) for id_, data in self._tx_buf_prp_Q if id_ < 20 or id_ == PRP_OPT_PRP_BATCH]
            self._tx_buf_prp_lock = False
        self._clear_tx_buff_prp_rest(opt_id)
    """

    # == PRP CLI-ESC
    """
    def prp_del_frame_buff_cli_esc(self, opt_id):
        self._clear_tx_buff_prp(opt_id)
        self._clear_tx_buff_prp_rest(opt_id)
    """

    # == Tasker (loop)
    def _prp_cron(self):
        """ Tasker(loop) für PRP """
        if hasattr(self._prp_remote, 'tasker'):
            self._prp_remote.tasker()
            return True
        return False

    ##########################################################
    # BBS_FWD Stuff
    def bbsFwd_init(self):
        if self.bbs_connection:
            return False
        bbs = self._popt_handler.get_bbs()
        if bbs is None:
            logger.error("PMS: bbs is None")
            return False
        self.bbs_connection = bbs.init_tx_fwd(self)
        if self.bbs_connection is None:
            logger.error("PMS: bbs_connection is None")
            return False
        return True

    def bbsFwd_start_reverse(self):
        if self.cli.stat_identifier is None:
            logger.error("PMS: cli.stat_identifier is None")
            return False
        if self.cli.stat_identifier.typ != 'BBS':
            logger.error("PMS: cli.stat_identifier.typ != 'BBS'")
            return False
        if self.cli.stat_identifier.e:
            logger.error("PMS: cli.stat_identifier.e")
            logger.error(f"{self.cli.stat_identifier.typ}")
            return False
        bbs = self._popt_handler.get_bbs()
        if bbs is None:
            logger.error("PMS: _bbs is None")
            return False
        self.bbs_connection = bbs.init_rev_fwd_conn(self)
        if self.bbs_connection is None:
            logger.error("PMS: bbs_connection is None")
            return False
        # print("Done: bbsFwd_start_reverse")
        return True

    def bbsFwd_start(self):
        """
        if self.cli.stat_identifier is None:
            logger.error("PMS: cli.stat_identifier is None")
            return False
        if self.cli.stat_identifier.typ != 'BBS':
            logger.error("PMS: cli.stat_identifier.typ != 'BBS'")
            return False
        if self.cli.stat_identifier.e:
            logger.error("PMS: cli.stat_identifier.e")
            logger.error(f"{self.cli.stat_identifier.typ}")
            return False
        """
        bbs = self._popt_handler.get_bbs()
        if bbs is None:
            logger.error("BBS: _bbs is None")
            return False
        if self.bbs_connection:
            logger.warning("BBS: bbs_connection not None. Manual Rev FWD Triggered ?")
            return False
        """
        if self.cli_type == "Task: FWD":
            logger.debug("BBS: Task Connection, no FWD Init needed.")
            return False
        """
        self.bbs_connection = bbs.init_fwd_conn(self)
        if self.bbs_connection is None:
            logger.error("BBS: bbs_connection is None")
            return False
        logger.debug("BBS: Done: bbsFwd start")
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
        if not hasattr(self.pipe, 'handle_rx_rawdata') and \
                not hasattr(self.pipe, 'is_error'):
            return False

        if self.pipe.is_error():
            logger.error(f"Pipe Error ({self.uid}): Disconnecting fm {self.to_call_str}")
            pipe_data = self.pipe.get_tx_data()
            if pipe_data:
                self.send_data(pipe_data)
            self.conn_disco()
        if self.pipe.handle_rx_rawdata(raw_data):
            return True
        return True

    def set_pipe(self, pipe_cfg=None):
        self.cli      = NoneCLI(self)
        self.cli_type = CLI_TYP_PIPE
        if not pipe_cfg:
            pipe_cfg = POPT_CFG.get_pipe_CFG().get(f'{self.own_port.port_id}-{self.my_call_str}', getNew_pipe_cfg())
        # print(f"Set Pipe: {pipe_cfg}")
        try:
            pipe = AX25Pipe(
                connection=self,
                pipe_cfg=pipe_cfg
            )
        except Exception as ex:
            logger.error("Conn: Pipe Error (AX25Conn-set_pipe())")
            logger.error(ex)
            return False
        if pipe_cfg.get('pipe_parm_PacLen', 0):
            self.parm_PacLen = pipe_cfg.get('pipe_parm_PacLen', self.parm_PacLen)
        if pipe_cfg.get('pipe_parm_MaxFrame', 0):
            self.parm_MaxFrame = pipe_cfg.get('pipe_parm_MaxFrame', self.parm_MaxFrame)
        if not self.own_port.add_pipe(pipe=pipe):
            logger.error("Conn: Port no Pipe")
            return False
        self.pipe       = pipe
        return True

    def _del_pipe(self):
        if self.pipe:
            self.own_port.del_pipe(self.pipe)
            if hasattr(self.pipe, 'close_pipe'):
                self.pipe.close_pipe()
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
                self._send_gui_QSO_rx(self.ft_obj.ft_rx_buf)
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
            #print(f"ft_resetRNR: conn_uid {conn_uid}")
            #print(f"ft_resetRNR: rev conn_uid {reverse_uid(conn_uid)}")
            #print(f"ft_resetRNR: self.uid {self.uid}")
            if conn_uid != self.uid and reverse_uid(conn_uid) != self.uid:
                #print(f"ft_resetRNR:SET! ")
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
                self.tx_buf_rawData.buffer_write(self.link_holder_text.encode(self._encoding, 'ignore'))

    ###############################
    # LINKS Linked/DIGI Connections
    def _link_crone(self):
        if self.is_link and self.LINK_Connection is not None:
            self.LINK_Connection.tx_buf_rawData.buffer_write(self.LINK_rx_buff.buffer_flush())
            self.tx_buf_rawData.buffer_write(self.LINK_Connection.LINK_rx_buff.buffer_flush())
            return True
        return False

    def new_link_connection(self, conn):
        if conn is None:
            return False
        if conn.uid in self._popt_handler.connection_manager.link_connections.keys():
            conn.change_l3_state(4)
            conn.zustand_exec.tx()
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
            print("LC 1")
            self._popt_handler.connection_manager.link_connections[str(conn.uid)] = conn, ''
        else:
            print("LC 2")
            self._popt_handler.connection_manager.link_connections[str(conn.uid)] = conn, conn.my_call_str

        self.LINK_Connection = conn
        self.is_link = True
        #   self.cli = cli.cliMain.NoneCLI(self)  # Disable CLI
        return True

    def new_digi_connection(self, conn):
        print(f"Conn newDIGIConn: UID: {conn.uid}")
        logger.debug(f"Conn newDIGIConn: UID: {conn.uid}")
        if conn is None:
            print("Conn ERROR: newDIGIConn: not conn")
            logger.error("Conn ERROR: newDIGIConn: not conn")
            return False
        if self.uid in list(self._popt_handler.connection_manager.link_connections.keys()):
            self.change_l3_state(4)
            self._l3_state_exec.tx()
            logger.error("Conn ERROR: newDIGIConn: self.uid in self._port_handler.connection_manager.link_connections")
            logger.error(f"{self.uid} - {self._popt_handler.connection_manager.link_connections.keys()}")
            return False
        self.digi_call = str(conn.digi_call)
        self._popt_handler.connection_manager.link_connections[str(self.uid)] = self, str(conn.digi_call)
        # self._port_handler.link_connections[str(reverse_uid(self.uid))] = conn, str(conn.digi_call)

        self.LINK_Connection = conn
        conn.LINK_Connection = self
        self.is_link = True
        ###############################
        # Del Digi Conn
        # self.own_port.delete_digi_conn(conn.uid)
        # conn.own_port.delete_digi_conn(self.uid)


        #   self.cli = cli.cliMain.NoneCLI(self)  # Disable CLI
        # print("new_digi TX CONN ")
        return True

    def link_disco(self, reconnect=True):
        # logger.debug(f'LINK DISCO')
        if self.is_link and self.LINK_Connection is not None:
            # logger.debug(f'LINK DISCO : ownUID: {self.uid} - LinkUID: {self.LINK_Connection.uid}')
            # logger.debug(f'LINK DISCO : digiCall: {self.digi_call} - is_digi: {self.is_digi}')
            # logger.debug(f'LINK DISCO : is_link_remote: {self.is_link_remote} - reconn: {reconnect}')
            if self.LINK_Connection.l3_state_id in [1, 2]:
                # self.LINK_Connection.n2 = 100
                self.LINK_Connection.set_T1(stop=True)
                self.LINK_Connection.change_l3_state(0)
                self.del_link()
            else:

                if not self.is_link_remote:
                    # logger.debug("LINK DISCO Remote")
                    self.LINK_Connection.conn_disco()
                    # self.LINK_Connection.zustand_exec.tx(None)
                else:
                    self._popt_handler.connection_manager.del_link(self.LINK_Connection.uid)
                    # print(self.l3_state_id)
                    # if self.l3_state_id not in [0, 1]:
                    # if reconnect and not self.digi_call:
                    if self.is_digi:
                        # logger.debug("DIGI DISCO Remote")
                        self.LINK_Connection.conn_disco()
                    elif reconnect and self.is_link_remote and not self.is_digi:
                        # logger.debug('ReConn')
                        if all((hasattr(self.LINK_Connection, 'send_sys_Msg_to_gui'),
                           hasattr(self.LINK_Connection, 'my_call_str'))):
                            # TODO ?? Why to LINKCONN GUI ?  CHANNEL ?
                            self.LINK_Connection.send_sys_Msg_to_gui(f'*** Reconnected to {self.LINK_Connection.my_call_str}')
                            self.send_to_link(f'\r*** Reconnected to {self.LINK_Connection.my_call_str}\r'.encode('ASCII', 'ignore'))
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
        if not all((inp, self.is_link)):
            return
        self.LINK_Connection.tx_buf_rawData.buffer_write(inp)

    def del_link(self):
        """ Called in State.link_cleanup() """
        if self.LINK_Connection is not None:
            # print(f'LINK CLEANUP link_connections K : {self._port_handler.link_connections.keys()}')
            self.LINK_Connection = None
            self.is_link = False
        self._popt_handler.connection_manager.del_link(self.uid)

    def _link_cleanup(self):
        # self.link_disco()
        self.del_link()
        # self._port_handler.del_link(self.uid)

    # ##############
    # DISCO
    def conn_disco(self):
        """ 2'nd time called = HardDisco """
        if self.l3_state_id:
            self._del_pipe()
            self._bbsFwd_disc()  # TODO return "is_"self.bbs_connection
            self.set_T1(stop=True)
            # self.zustand_exec.tx(None)
            if self.l3_state_id in [2, 4] or self._await_disco:
                logger.debug('End Conn')
                self.send_DISC_ctlBuf()
                self._l3_state_exec.S1_end_connection()
            else:
                if not self.is_tx_buff_empty:
                    self._await_disco = True
                    # logger.debug("DISCO and buff not NULL !!")
                    """
                    print(f"DISCO and buff not NULL !! tx_buf_rawData: {self.tx_buf_rawData}")
                    print(f"DISCO and buff not NULL !! tx_buf_2send: {self.tx_buf_2send}")
                    print(f"DISCO and buff not NULL !! tx_buf_unACK: {self.tx_buf_unACK}")
                    """
                else:
                    self.change_l3_state(4)

    def _wait_for_disco(self):
        if self.is_tx_buff_empty:
            self._await_disco = False
            self.change_l3_state(4)

    def conn_cleanup(self):
        # logger.debug(f"conn_cleanup: {self.uid}\n"
        #       f"state: {self.l3_state_id}\n")
        # self.bbsFwd_disc()
        self.cli.cli_conn_cleanup()
        if self.tx_buf_ctl:
            #logger.debug(f'NO CLeanup: {self.uid}: tx_buf_ctl')
            return
        if not self.rx_tx_buf_guiData.is_empty:
            #logger.debug(f'NO CLeanup: {self.uid}: rx_tx_buf_guiData')
            return
        self._link_cleanup()
        self._bbsFwd_disc()
        self.own_port.del_connections(conn=self)
        self._popt_handler.connection_manager.end_connection(self)   # Doppelt ..
        # TODO def is_conn_cleanup(self) -> return"

    def end_connection(self, reconn=True):
        logger.debug(f"end_connection: {self.uid}")
        self._del_pipe()
        self._bbsFwd_disc()
        self.ft_queue = []
        if self.ft_obj:
            self.ft_obj.ft_abort()
        self.ft_obj = None
        self.link_disco(reconnect=reconn)
        self.set_T1()
        self.vr  = 0
        self.vs  = 0
        self._nr = -1

    """
    def reset_conn(self):
        # TODO .. Not Used anymore .. Delete ..
        # self._del_pipe()
        self._bbsFwd_disc()
        self.ft_queue = []
        if self.ft_obj:
            self.ft_obj.ft_abort()
        self.ft_obj = None
        # self.link_disco(reconnect=reconn)
        self.set_T1()
        self.vr = 0
        self.vs = 0
        self._port_handler.reset_connection(connection=self) # TODO .. Not Used anymore .. Delete ..
    """
    """
    def is_disco(self):
        if self.l3_state_id in [0, 1]:
            return True
        return False
    """

    def is_incoming_connection(self):
        return True if self.l3_state_id == 1 else False

    ######################################################################
    # Timer usw
    # RNR
    def set_RNR(self):
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
            }.get(self.l3_state_id, None)
            if new_state:
                self.change_l3_state(new_state)

    def unset_RNR(self):
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
            }.get(self.l3_state_id, None)
            if new_state:
                self.change_l3_state(new_state)

    # ====== Mr.T
    def set_T1(self, stop=False):
        if stop:
            self.n2 = 0
            self.t1 = 0
            return
        # self.calc_irtt()
        n2   = int(self.n2)
        srtt = float(self._get_rtt())
        # if not self._port_cfg.get('parm_T2_auto', True):

        if n2 > 3:
            self.t1 = float(((srtt * (n2 + 4))  / 1000) + time.time())
        else:
            self.t1 = float(((srtt * 3)         / 1000) + time.time())
        """
        if self.t1 > 0:
            print('t1 > {}'.format(self.t1 - time.time()))
        """

    # T2
    def set_T2auto(self, t2_auto=True):
        self._port_cfg['parm_T2_auto'] = bool(t2_auto)
        self.calc_irtt()

    def set_T2var(self, t2: int):
        self._port_cfg['parm_T2'] = min(max(int(t2), 10), 5000)
        self.calc_irtt()

    def set_T2(self, stop=False, link_remote=False):
        """
        if self._port_cfg.get('parm_full_duplex', False):
            self.t2 = 0
            return
        """
        if stop:
            self.t2 = 0
            return
        self.t2 = float(self._parm_T2 + time.time())
        if self.is_link and not link_remote:
            if self.own_port == self.LINK_Connection.own_port:
                self.LINK_Connection.set_T2(link_remote=True)

    # T3
    def set_T3(self, stop=False):
        if stop:
            self.t3 = 0
        else:
            self.t3 = float(self._parm_T3 + time.time())

    # ====== N2 Fail-Handling
    def handle_N2_fail(self):
        to_qso_win = f'\n*** Failed to connect to {self.to_call_str} > ' \
                     f'Port {self.own_port.port_id}\n'
        user_db_ent = self._userDB.get_entry(self.to_call_str, add_new=False)
        if user_db_ent:
            if user_db_ent.Name:
                to_qso_win = f'*** Failed to connect to {self.to_call_str} - ' \
                             f'({user_db_ent.Name}) > Port {self.own_port.port_id}'
        self.send_to_link(to_qso_win.encode('ASCII', 'ignore'))
        self.send_sys_Msg_to_gui(to_qso_win)
        self.send_DISC_ctlBuf()

    # ====== RTT Calc
    def _get_rtt(self):
        auto = False  # TODO
        self.calc_irtt()
        if auto:
            return self.RTT_Timer.get_rtt_avrg() * 1000
        else:
            return self.IRTT

    def calc_irtt(self):
        header_len      = 16 + len(self.via_calls) * 7
        init_t2: float  = (((self.parm_PacLen + header_len) * 8) / self._parm_baud) * 1000
        #pac_len         = 256
        #init_t2: float  = (((pac_len + header_len) * 8) / self._parm_baud) * 1000
        irit = (init_t2 +
                #self._parm_TXD + # Pseudo TXD
                (self._parm_Kiss_TXD * 10) +
                (self._parm_Kiss_Tail * 10)
                )
        if self._port_cfg.get('parm_T2_auto', True):
            self._parm_T2   = float(irit / 1000)
        else:
            self._parm_T2   = float(self._port_cfg.get('parm_T2', 2888)) / 1000

        if self.via_calls:
            hops = (len(self.via_calls) + 1) * 2
            self.IRTT: float = max((irit * hops), 50)  # TODO seems not right!!!!!!!!!!!!!!!!!!!!
        else:
            self.IRTT: float = max((irit * 2), 50)     # TODO seems not right!!!!!!!!!!!!!!!!!!!!

        # print(f"IRIT    : {self.IRTT}")
        # print(f"parm_T2 : {self._parm_T2}")
        """
        self.IRTT = max(self.IRTT, 10)  # TODO seems not right!!!!!!!!!!!!!!!!!!!!
        self.IRTT       = irit * 2
        """

        # print('parm_T2: {}'.format(self.parm_T2))
        # print('IRTT: {}'.format(self.IRTT))

    # ====== Auto Max Frame
    def _set_autoMaxFrameScore(self, in_decrement: bool):
        """
        :param in_decrement: True = increment, False = decrement
        :return:
        """
        if not self.parm_MaxFrameAuto:
            return
        if not self._MaxFrameCFG:
            self._MaxFrameCFG = int(self.parm_MaxFrame)
        if in_decrement:
             self._autoMaxFrameScore += 1
             #logger.debug(f"autoMaxFrameScore increment: {self._autoMaxFrameScore}")
        else:
             self._autoMaxFrameScore -= 1
             #logger.debug(f"autoMaxFrameScore decrement: {self._autoMaxFrameScore}")

        if self._autoMaxFrameScore < 0:
            self._autoMaxFrameScore = 0
            self.parm_MaxFrame = max(1,
                                     (self.parm_MaxFrame - 1)
                                     )
            return
        if self._autoMaxFrameScore > 1:
            self._autoMaxFrameScore = 0
            self.parm_MaxFrame = min(self._MaxFrameCFG,
                                     (self.parm_MaxFrame + 1)
                                     )
            return

    ##################################
    # Build AX25 Frames
    # ====== AX25 Max Pac
    def build_I_fm_raw_buf(self):
        if self.tx_buf_unACK or not self._is_tx_buffer():
            return
        while (len(self.tx_buf_unACK) < self.parm_MaxFrame and
               self._is_tx_buffer()):
            self._send_I(False)

    # ====== AX25 Frames
    def _get_new_ax25frame(self):
        return AX25Frame(dict(
            uid=str(self.uid),
            from_call_str=str(self.my_call_str_add),
            to_call_str=str(self.to_call_str_add),
            via_calls=list(self.via_calls),
            axip_add=tuple(self.axip_add),
            digi_call=str(self.digi_call)
        ))

    def _send_I(self, pf_bit=False):
        """
        :param pf_bit: bool
        True if RX a REJ Packet
        """
        #####################################################################
        # AX25Frame Init                        #
        new_axFrame = self._get_new_ax25frame() # Get preseted AX25Frame
        new_axFrame.ctl_byte.pf = bool(pf_bit)  # Poll/Final Bit / True if REJ is received
        new_axFrame.ctl_byte.nr = self.vr       # Receive PAC Counter OBJ (keeping vr updated)
        new_axFrame.ctl_byte.ns = int(self.vs)  # Send PAC Counter
        new_axFrame.ctl_byte.IcByte()           # Set C-Byte
        new_axFrame.pid_byte.text()             # Set PID-Byte to TEXT
        #####################################################################
        # PAYLOAD !!                            #
        data = self._get_payload_fm_tx_buffer() # Get Data fm TX-Buffer / PRP-Buffer / PRP-Prio-Buffer
        #####################################################################
        # Put Payload into ax25 Frame           #
        new_axFrame.payload = bytes(data)       # Put payload into AX25-Frame
        data_len            = len(data)         # Keep data length for RTT
        #####################################################################
        self.tx_buf_unACK[int(self.vs)] = new_axFrame # Keep Packet until ACK/RR
        self.tx_buf_2send.append(new_axFrame)         # ax25 Frame Buffer
        #####################################################################
        # RTT                                                       #
        self.RTT_Timer.set_rtt_timer(int(self.vs), int(data_len))   #
        #####################################################################
        # !!! COUNT VS !!!                    # AX25 L3 Flow-CTRL
        self.vs = (int(self.vs) + 1) % 8      # Increment VS Modulo 8
        self.set_T1()                         # Re/Set T1
        #####################################################################
        # Statistics                          #
        self.tx_byte_count += int(data_len)   # Byte Counter
        self.tx_pack_count += 1               # Packet Counter

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

    ######################################
    # New Connection Handling
    def accept_connection(self):
        self._set_user_db_ent()
        self._popt_handler.connection_manager.accept_new_connection(self)
        if self.LINK_Connection:
            self.LINK_Connection.cli.change_cli_state(5)
            logger.debug(f"Conn {self.uid}: accept_digi_connection is LINK")
            # if self.digi_call in self._port_cfg.parm_Digi_calls:
            if POPT_CFG.get_digi_is_enabled(self.digi_call):
                logger.debug(f"Conn {self.uid}: accept_digi_connection")
                if self.accept_digi_connection():
                    logger.debug(f"Conn {self.uid}: accept_digi_connection True")
                    self.is_digi = True
                    return

            self.send_to_link(
                f'\r*** Connected to {self.to_call_str}\r'.encode('ASCII', 'ignore')
            )

    def accept_digi_connection(self):
        logger.debug(f'DIGI Conn accept..  {self.uid}  ?')
        if not self.LINK_Connection:
            logger.debug(f'DIGI Conn accept: No LINK_Connection {self.uid}')
            logger.debug(f'DIGI Conn accept: No LINK_Connection {self.LINK_Connection}')

            return False
        digi_uid = str(self.LINK_Connection.uid)
        digi_uid = reverse_uid(digi_uid)
        link_conn_port = self.LINK_Connection.own_port
        digi_accept: bool = link_conn_port.accept_digi_conn(digi_uid)
        return digi_accept

    def insert_new_connection(self):
        """ Insert connection for handling """
        is_service = self._is_service_connection
        self._popt_handler.connection_manager.insert_new_connection_PH(new_conn=self, is_service=is_service)

    # ======= Interconnect Lookup
    def _set_dest_call_fm_data_inp(self, raw_data: b''):
        # TODO AGAIN !!
        data = self.rx_buf_last_data + raw_data
        # tmp_raw = bytes(raw_data)
        if b'\r' not in data:
            return False
        data = data.split(b'\r')[:-1]
        for line in data:
            # tmp_raw = tmp_raw.replace(line + b'\r', b'')
            if not any((line.lower().startswith(b'*** connected to '),
                    line.lower().startswith(b'*** reconnected to '))):
                continue
            tmp_line = line.decode('ASCII', 'ignore')
            tmp_data = tmp_line.split(' to ')[-1]
            # tmp_data = tmp_data.decode('ASCII', 'ignore')
            # TODO Conn/reconn fnc
            if ':' in tmp_data:
                tmp_call = tmp_data.split(':')
                self.to_call_str = tmp_call[1].replace(' ', '')
                self._to_call_alias = tmp_call[0].replace(' ', '')
            else:
                self.to_call_str = tmp_data.replace(' ', '')
                self._to_call_alias = ''
            self.tx_byte_count  = 0
            self.rx_byte_count  = 0
            self.rx_buf_rawData = bytearray()
            self._set_user_db_ent()
            #self._set_packet_param()
            self._reinit_cli()
            lb_msg = f"CH {int(self.ch_index)} - {str(self.my_call_str)}: - {str(self.uid)} - Port: {int(self.port_id)}"
            lb_msg_1 = f"CH {int(self.ch_index)} - {str(self.my_call_str)}: {str(tmp_line)}"
            LOG_BOOK.info(lb_msg)
            LOG_BOOK.info(lb_msg_1)
            gui = self._popt_handler.get_gui()

            if hasattr(gui, 'add_LivePath_plot') and hasattr(gui, 'on_channel_status_change'):
                # TODO
                speech = ' '.join(self.to_call_str.replace('-', ' '))
                SOUND.sprech(speech)

                gui.add_LivePath_plot(node=str(self.to_call_str),
                                      port_id=int(self.port_id),
                                            ch_id=int(self.ch_index))
                gui.on_channel_status_change()
            # Maybe it's better to look at the whole string (include last frame)?
            return True
        return False

    ##############################################
    # Gettaa
    @property
    def _is_service_connection(self):
        return self.cli.service_cli

    @property
    def get_stat_cfg(self):
        return dict(self._stat_cfg)

    @property
    def get_port_cfg(self):
        return dict(self._port_cfg)

    @property
    def get_param_T2(self):
        """ called fm GUI """
        return float(self._parm_T2)

    @property
    def get_PacLen(self):
        return self.parm_PacLen

    @property
    def get_MaxPac(self):
        return self.parm_MaxFrame

    @property
    def prp(self):
        return self._prp_remote

    """
    def can_send_next_prp_batch(self):
        # Prüfen ob prp-tx-buffer noch voll ist 
        return (
                not bool(self._tx_buf_prp_Q)      and
                not bool(self._tx_buf_prp_prio_Q) and
                bool(len(self._tx_buf_prp_Rest) < (self.parm_PacLen * self.parm_MaxFrame))
                )
    """

    def is_prp_opt_id_in_tx_buff(self, opt_id: int):
        return self._prp_remote.is_prp_opt_id_in_tx_buff(opt_id)

    @property
    def is_incoming_conn(self):
        return bool(self._incoming_conn)

    # ========= I/O Buffers
    @property
    def get_tx_buff_len(self):
        return self.tx_buf_rawData.length

    @property
    def get_unACK_buff_len(self):
        return len(self.tx_buf_unACK)

    @property
    def get_tx_buff(self):
        return self.tx_buf_rawData.buffer_get

    @property
    def is_tx_buff_empty(self):
        return not self.tx_buf_unACK and not self._is_tx_buffer()

