import datetime
import time

from ax25.ax25_ports.ax25Port_Classes import RxBuf
from ax25.ax25_util.ax25UI_Pipe import AX25Pipe

from ax25.ax25_l3.ax25Digi import AX25DigiConnection
from ax25.ax25_l3.ax25Connection import AX25Conn
from ax25.ax25_l2.ax25dec_enc import AX25Frame, bytearray2hexstr
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger, LOG_BOOK
from fnc.ax25_fnc import reverse_uid, is_digipeated_pre_digi
from ax25.ax25Error import AX25EncodingERROR, AX25DecodingERROR, AX25DeviceERROR, AX25DeviceFAIL


class AX25Port(object):
    def __init__(self, port_id: int, port_handler):
        self._logTag = f"Port {port_id}: "
        #self.port_w_dog = time.time()   # Debuging
        self._port_handler              = port_handler
        self._loop_watchdog             = time.time()
        self._loop_is_running           = self._port_handler.is_running
        self.ende                       = False
        self.device                     = None
        self.device_is_running          = False
        ############
        self._tnc_emu_connection        = None
        self._tnc_emu_client_address    = None
        ############
        # CONFIG
        self._port_cfg = dict(POPT_CFG.get_port_CFG_fm_id(port_id))
        if not self._port_cfg:
            logger.error(f"{self._logTag}No Config !!!")
            raise AX25DeviceFAIL(self)

        self._port_param    = self._port_cfg.get('parm_PortParm', ('', 0))
        self.portname       = self._port_cfg.get('parm_PortName', '')
        self.port_typ       = self._port_cfg.get('parm_PortTyp', '')
        self.port_id        = self._port_cfg.get('parm_PortNr', -1)
        # self._my_stations = port_cfg.get('parm_StationCalls', [])
        # self.parm_TXD = port_cfg.get('parm_TXD', 400)
        self._TXD = time.time()
        # CONFIG ENDE
        #############
        """ KISS / AGWPE - TNC Protocol """
        """
        if self.port_id == 4:
            self.tnc_protocol   = AGWPEHandler(self._port_cfg)
        else:
            self.tnc_protocol   = Kiss(self._port_cfg)
        """
        self.tnc_protocol = None
        """ DIGI """
        # self.digi_calls = self._port_cfg.parm_Digi_calls
        self._parm_digi_TXD = self._port_cfg.get('parm_TXD', 400) * 4  # TODO add to Settings GUI
        self._digi_TXD      = time.time()
        self._digi_buf      = []         # RX/TX
        """ """
        self._digi_connections  = {}
        self._unProto_buf       = []           # TX
        self.pipes              = {}
        self.connections        = {}
        #############
        # VARS
        self._mh            = self._port_handler.get_MH()
        #############
        """ Dual Port """
        self.dualPort_primaryPort   = None
        self.dualPort_secondaryPort = None
        self.dualPort_lastRX        = b''  # Prim
        self.dualPort_echoFilter    = []   # Prim
        self.dualPort_cfg           = {}
        self.dualPort_monitor_buf   = []
        """ MCast Server """
        self._mcast_server          = None
        """ Block incoming Connections """
        # Blocking incoming connection until PoPT Init is Done...
        self._block_incoming_conn   = 1     # 0 = no_blocking, 1 = ignore, 2 = reject, 3 = reject w msg.
        ##############
        # AXIP VARs
        # self.axip_anti_spam = {}
        """
        try:
            self.init()
        except AX25DeviceFAIL:
            # raise AX25DeviceFAIL(self)  # TODO in PortINIT
            AX25DeviceFAIL(self)
        """

        # ██████████████████████████████████████████████████████████████
        # ███ LOGGING BEI INIT █████████████████████████████████████████
        # ██████████████████████████████████████████████████████████████
        logger.info("═" * 60)
        logger.info(f"Port INITIALISIERT - Port {self.port_id}")
        logger.info(f"  Typ:          {self.port_typ}")
        logger.info(f"  Port-Name:    {self.portname}")
        logger.info(f"  Parameter:    {self._port_cfg.get('parm_PortParm', None)}")
        logger.info(f"  KISS Enabled: {self._port_cfg.get('parm_kiss_is_on', True)}")
        logger.info(f"  TXD:    {self._port_cfg.get('parm_kiss_TXD', 35)}")
        logger.info(f"  Pers:   {self._port_cfg.get('parm_kiss_Pers', 160)}")
        logger.info(f"  Slot:   {self._port_cfg.get('parm_kiss_Slot', 30)}")
        logger.info(f"  Tail:   {self._port_cfg.get('parm_kiss_Tail', 15)}")
        logger.info(f"  Duplex: {self._port_cfg.get('parm_kiss_F_Duplex', 0)}")
        logger.info("═" * 60)


    def init(self):
        pass


    def set_kiss_parm(self):
        pass

    def close_device(self):
        pass

    def close(self):
        # self.disco_all_conns()
        # if self._port_cfg.get('parm_axip_Multicast', False):
        if self._mcast_server:
            self._mcast_server.del_mcast_port()
            self._mcast_server = None
        self._loop_is_running = False
        self.close_device()
        # if self.device is not None:
        # self.device.close()

    def _rx(self):
        return RxBuf()

    def tx(self, frame):
        if self._tx_dualPort_handler(frame):
            return
        """
        if self._port_cfg.get('parm_full_duplex', False):
            # print('FD')
            if self._tx_th:
                if self._tx_th.is_alive():
                    # print('FD alive')
                    return
            self._tx_th = threading.Thread(target=self.tx_out, args=(frame, ))
            self._tx_th.start()
            return
        """
        self._tx_out(frame)

    def _tx_out(self, frame):
        setattr(frame, 'rx_time', datetime.datetime.now())
        # frame.rx_time = datetime.datetime.now()
        self._update_monitor(ax25frame=frame, tx=True)
        self._dualPort_monitor_input(ax25frame=frame, tx=True)
        try:
            self._tx_device(frame)
        except (AX25DeviceERROR, AX25DeviceFAIL):
            logger.error(f"Error: tx_device() Port: {self.port_id}")
            self.close()

    def _tx_device(self, frame):
        pass

    def tx_multicast(self, frame):
        pass

    def _set_TXD(self):
        """ Internal TXD. Not Kiss TXD """
        self._TXD = time.time() + self._port_cfg.get('parm_TXD', 400) / 1000

    def _set_digi_TXD(self):
        """ Internal TXD. Not Kiss TXD """
        self._digi_TXD = time.time() + self._parm_digi_TXD / 1000

    ###################################################
    # RX Stuff
    def rx_handler(self, ax25_frame):
        """ Main RX-Handler """
        # print(ax25_frame.get_frame_conf())
        self._reset_ft_wait_timer(ax25_frame)
        # Monitor / MH / Port-Statistic
        # self._gui_monitor(ax25frame=ax25_frame, tx=False)
        isUI = False
        if ax25_frame.ctl_byte.flag == 'UI':
            self._rx_UI_handler(ax25_frame=ax25_frame)  # just APRS-IGATE
            isUI = True
        if not ax25_frame.is_digipeated and ax25_frame.via_calls:
            if not isUI:
                if self._rx_link_handler(ax25_frame=ax25_frame):
                    # Link Connection Handler
                    return True
            if self._rx_digi_handler(ax25_frame=ax25_frame):
                # DIGI
                return True
        elif ax25_frame.is_digipeated:
            if not isUI:
                if self._rx_conn_handler(ax25_frame=ax25_frame):
                    # Connections
                    return True
                if self._rx_new_conn_handler(ax25_frame=ax25_frame):
                    # New Connections
                    return True
            if self._rx_pipe_handler(ax25_frame=ax25_frame):
                # Pipe
                return True
        return False

    def _rx_link_handler(self, ax25_frame):
        ax25_frame_conf = dict(ax25_frame.get_frame_conf())
        uid = str(ax25_frame_conf.get('uid', ''))
        """
        if reverse_uid(str(uid)) in self._port_handler.link_connections.keys():
            logger.debug(f"Port rx_link_handler reverse_uid: UID: {uid}")
            logger.debug(f"Port rx_link_handler reverse_uid: FRAME ctl: {ax25_frame.ctl_byte.flag}")
            return False
        """
        if uid in self._port_handler.connection_manager.link_connections.keys():
            # logger.debug(self._logTag + f"Link-Conn RX: {uid}")
            conn = self._port_handler.connection_manager.link_connections[uid][0]
            link_call = str(self._port_handler.connection_manager.link_connections[uid][1])
            """
            logger.debug(self._logTag + f"Link-Conn RX link_call: {link_call}")
            logger.debug(self._logTag + f"Link-Conn RX is_link_remote: {conn.is_link_remote}")
            logger.debug(self._logTag + f"Link-Conn RX digi_call: {conn.digi_call}")
            logger.debug(self._logTag + f"Link-Conn RX my_call_str: {conn.my_call_str}")
            logger.debug(self._logTag + f"Link-Conn RX self._port_handler.link_connections: {self._port_handler.link_connections}")
            logger.debug(self._logTag + f"Link-Conn RX ++: {ax25_frame_conf}")
            """
            if link_call:
                # if link_call != ax25_frame.via_calls[-1].call_str:
                #     return False

                # for call in ax25_frame.via_calls:
                # if not ax25_frame.digi_check_and_encode(call=link_call, h_bit_enc=False):
                if not is_digipeated_pre_digi(ax25_frame_conf, link_call):
                    logger.debug(self._logTag + f"Link-Conn RX No DIGI chk --: {ax25_frame_conf}")
                    return False
                # if call.call_str == link_call:
                # logger.debug(self._logTag + f"Link-Conn RX --: {ax25_frame_conf}")
                conn.handle_rx(ax25_frame=ax25_frame)
                return True
                # if ax25_frame.digi_check_and_encode(call=link_call, h_bit_enc=True):
            # conn.handle_rx(ax25_frame=ax25_frame)
            # return True
        return False

    def _rx_pipe_handler(self, ax25_frame):
        uid = ax25_frame.get_frame_conf().get('uid', '')
        # logger.debug(uid)
        # logger.debug(self.pipes.keys())
        if uid not in self.pipes.keys():
            # logger.debug('UI-Pipe: No UID')
            return False
        if self.pipes[uid].get_pipe_connection() is not None:
            # logger.debug('UI-Pipe: connection')
            return False
        # logger.debug('UI-Pipe: OK')
        self.pipes[uid].handle_rx(ax25_frame=ax25_frame)
        return True

    def _rx_UI_handler(self, ax25_frame):
        # print(f"Port RX UI Handler - aprs_ais: {self.aprs_stat.aprs_ais}")
        ax25_frame_conf = ax25_frame.get_frame_conf()
        """
        netrom_cfg = ax25_frame_conf.get('netrom_cfg', {})
        if netrom_cfg:     # Net-Rom
            rTable = self.port_get_PH().get_RoutingTable()
            if rTable is None:
                return True
            ax25_frame_conf['port_id'] = int(self.port_id)
            # rTable.NetRom_UI_rx(ax25_frame_conf)
            # NetRom_decode_UI(ax25_frame_conf)
            return True
        """
        aprs_ais = self._port_handler.get_aprs_ais()
        if hasattr(aprs_ais, 'aprs_ax25frame_rx'):
            aprs_ais.aprs_ax25frame_rx(
                port_id=self.port_id,
                ax25frame_conf=ax25_frame_conf
            )
            return False
        return False

    def _rx_conn_handler(self, ax25_frame):
        uid = str(ax25_frame.addr_uid)
        if uid in self.connections.keys():
            self.connections[uid].handle_rx(ax25_frame=ax25_frame)
            return True
        return False

    def _rx_new_conn_handler(self, ax25_frame):
        # New Incoming Connection
        if ax25_frame.to_call.call_str in POPT_CFG.get_stationCalls_fm_port(self.port_id):
            block_list  = POPT_CFG.get_block_list_by_id(self.port_id)
            block_state = block_list.get(ax25_frame.from_call.call, 0)
            gui = self._port_handler.get_gui()
            if block_state == 1:
                LOG_BOOK.info(f"*** Connection ignored (Block List)! Port: {self.port_id}, Call: {ax25_frame.from_call.call}")
                if hasattr(gui, 'set_port_block_warning'):
                    gui.set_port_block_warning()
                return True
            elif block_state == 2:
                LOG_BOOK.info(f"*** Connection rejected (Block List)! Port: {self.port_id}, Call: {ax25_frame.from_call.call}")
                if hasattr(gui, 'set_port_block_warning'):
                    gui.set_port_block_warning()
                self.send_DM_frame(ax25_frame_cfg=ax25_frame.get_frame_conf())
                return True
            uid = str(ax25_frame.addr_uid)
            if uid not in self.connections.keys():
                if not self._block_incoming_conn:
                    self.connections[uid] = AX25Conn(ax25_frame, port=self)
                    return True
                elif self._block_incoming_conn == 1:    # Ignore incoming Conn
                    LOG_BOOK.info(
                        f"*** Connection ignored (Global)! Port: {self.port_id}, Call: {ax25_frame.from_call.call}")
                    if hasattr(gui, 'set_port_block_warning'):
                        gui.set_port_block_warning()
                    return True
                elif self._block_incoming_conn == 2:    # Reject incoming Conn
                    LOG_BOOK.info(
                        f"*** Connection rejected (Global)! Port: {self.port_id}, Call: {ax25_frame.from_call.call}")
                    if hasattr(gui, 'set_port_block_warning'):
                        gui.set_port_block_warning()
                    self.send_DM_frame(ax25_frame_cfg=ax25_frame.get_frame_conf())
                    return True
        return False

    ########################################################
    # DIGI
    def _rx_digi_handler(self, ax25_frame):
        if not POPT_CFG.get_digi_CFG():
            return False
        return self._rx_managed_digi(ax25_frame)

    def _rx_simple_digi(self, ax25_frame):
        for call in ax25_frame.via_calls:
            # digi_conf = dict(POPT_CFG.get_digi_CFG_for_Call(call.call_str))
            # if call.call_str in self.digi_calls:
            if POPT_CFG.get_digi_is_enabled(call.call_str):
                if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
                    self._digi_buf.append(ax25_frame)
                    logger.debug(f"Simple DIGI: {ax25_frame.get_frame_conf()}")
                    # self.set_digi_TXD()
                    return True
        return False

    def _rx_managed_digi(self, ax25_frame):
        self._cleanup_digi_conn()
        # get_digi_CFG
        digi_conf = dict(POPT_CFG.get_digi_CFG())
        ax25_conf = dict(ax25_frame.get_frame_conf())
        uid = ax25_conf.get('uid', '')
        if not uid:
            return False


        for call in ax25_frame.via_calls:
            if call.call not in digi_conf.keys():
                continue
            tmp_cfg = dict(digi_conf.get(call.call, {}))
            if not tmp_cfg.get('digi_enabled', False):
                continue
            # if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
            if is_digipeated_pre_digi(ax25_conf=dict(ax25_conf), call=str(call.call_str)):
                if tmp_cfg.get('managed_digi', False):
                    if uid not in self._digi_connections.keys():
                        if self._block_incoming_conn:
                            LOG_BOOK.info(
                                f"*** DIGI ignored (Global)! Port: {self.port_id}, Call: {ax25_frame.from_call.call}")
                            gui = self._port_handler.get_gui()
                            if hasattr(gui, 'set_port_block_warning'):
                                gui.set_port_block_warning()
                            return True
                        tmp_cfg.update(dict(
                            rx_port=self,
                            digi_call=str(call.call_str),
                            digi_ssid=int(call.ssid),       # As Port-ID
                            ax25_conf=dict(ax25_conf)
                        ))
                        if ax25_frame.ctl_byte.flag == 'UI':
                            logger.debug(self._logTag + "_rx_managed_digi NewUI")
                            AX25DigiConnection(tmp_cfg).digi_rx_handle(ax25_frame)
                            return True
                        # New Digi Conn
                        if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
                            logger.debug(self._logTag + f" NewDigiConn: tmp_cfg {tmp_cfg}")
                            logger.debug(self._logTag + f" NewDigiConn: digi_conn {self._digi_connections.keys()}")
                            logger.debug(self._logTag + f" NewDigiConn: conn {self.connections.keys()}")
                            logger.debug(self._logTag + f" NewDigiConn: ax25_conf {ax25_conf}")
                            digi_conn = AX25DigiConnection(dict(tmp_cfg))
                            digi_conn.digi_rx_handle(ax25_frame)
                            self._digi_connections[uid] = digi_conn

                            return True
                        logger.error(self._logTag + f" NewDigiConn: not ax25_frame.digi_check_and_encode")
                        logger.error(self._logTag + f" NewDigiConn: tmp_cfg {tmp_cfg}")
                        logger.error(self._logTag + f" NewDigiConn: digi_conn {self._digi_connections.keys()}")
                        logger.error(self._logTag + f" NewDigiConn: conn {self.connections.keys()}")
                        logger.error(self._logTag + f" NewDigiConn: ax25_conf {ax25_conf}")
                        return True

                    if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
                        logger.debug(self._logTag + f" DigiConn: tmp_cfg {tmp_cfg}")
                        logger.debug(self._logTag + f" DigiConn: digi_conn {self._digi_connections.keys()}")
                        logger.debug(self._logTag + f" DigiConn: conn {self.connections.keys()}")
                        logger.debug(self._logTag + f" DigiConn: ax25_conf {ax25_conf}")
                        self._digi_connections[uid].digi_rx_handle(ax25_frame)
                        return True

                    #logger.debug(self._logTag + f" DigiConn: not ax25_frame.digi_check_and_encode")
                    #logger.debug(self._logTag + f" DigiConn: tmp_cfg {tmp_cfg}")
                    #logger.debug(self._logTag + f" DigiConn: digi_conn {self._digi_connections.keys()}")
                    #logger.debug(self._logTag + f" DigiConn: conn {self.connections.keys()}")
                    #logger.debug(self._logTag + f" DigiConn: ax25_conf {ax25_conf}")
                    return True

                if ax25_conf.get('uid', '') not in self._digi_connections.keys():
                    # logger.debug(self._logTag + f" S-Digi: digi_check_and_encode {ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True)}")
                    if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
                        if self._block_incoming_conn:
                            LOG_BOOK.info(
                                f"*** DIGI ignored (Global)! Port: {self.port_id}, Call: {ax25_frame.from_call.call}")
                            gui = self._port_handler.get_gui()
                            if hasattr(gui, 'set_port_block_warning'):
                                gui.set_port_block_warning()
                            return True
                        logger.debug(self._logTag + f" S-Digi: tmp_cfg {tmp_cfg}")
                        logger.debug(self._logTag + f" S-Digi: digi_conn {self._digi_connections.keys()}")
                        logger.debug(self._logTag + f" S-Digi: conn {self.connections.keys()}")
                        logger.debug(self._logTag + f" S-Digi: ax25_conf {ax25_conf}")
                        self.add_frame_to_digiBuff(ax25_frame)
                        return True
                    #logger.debug(self._logTag + f" S-Digi: not ax25_frame.digi_check_and_encode")
                    #logger.debug(self._logTag + f" S-Digi: tmp_cfg {tmp_cfg}")
                    #logger.debug(self._logTag + f" S-Digi: digi_conn {self._digi_connections.keys()}")
                    #logger.debug(self._logTag + f" S-Digi: conn {self.connections.keys()}")
                    #logger.debug(self._logTag + f" S-Digi: ax25_conf {ax25_conf}")
                    return True
            return False
        return False

    def add_digi_conn(self, digi_connection):
        tx_uid = str(digi_connection.get_tx_uid())
        if tx_uid in self._digi_connections:
            logger.error(self._logTag + f"add_digi_conn - uid in _digi_connections")
            logger.error(self._logTag + f"self._digi_connections {self._digi_connections}")
            logger.error(self._logTag + f"rx_uid  {tx_uid}")
            return False
        logger.debug(self._logTag + f"add_digi_conn +++ tx_uid  {tx_uid}")
        self._digi_connections[tx_uid] = digi_connection
        return True

    def accept_digi_conn(self, uid: str):
        """
        if uid in self._digi_connections.keys():
            logger.debug(f'Port: accept_digi_conn: {uid}')
            return self._digi_connections[uid].add_rx_conn_cron()
        """
        uid = reverse_uid(uid)
        if uid in self._digi_connections.keys():
            logger.debug(f'Port: accept_digi_conn reverse: {uid}')
            return self._digi_connections[uid].add_rx_conn_cron()

        logger.error('Port: accept_digi_conn: UID ERROR')
        logger.error(f'Port: accept_digi_conn uid: {uid}')
        logger.error(f'Port: accept_digi_conn keys: {self._digi_connections.keys()}')
        return False
        # return True

    def delete_digi_conn(self, uid: str):
        if uid in self._digi_connections.keys():
            # print(f"DIGI-Conn DEL: {uid}")
            del self._digi_connections[uid]

    def _cleanup_digi_conn(self):
        for uid, digi_conn in list(self._digi_connections.items()):
            # print(f"DIGI-CONn: {uid}")
            # digi_conn.debug_out()
            if digi_conn.is_done():
                # print(f"DIGI-CONN Cleanup {uid}")
                self.delete_digi_conn(uid)

    def _digi_task(self):
        self._cleanup_digi_conn()
        for uid, digi_conn in list(self._digi_connections.items()):
            # print(f"DIGI-CONN TASK: {uid}")
            if digi_conn:
                digi_conn.digi_crone()

    def get_digi_conn(self):
        return self._digi_connections

    def add_frame_to_digiBuff(self, ax25frame):
        # print(f"Add DIGI-BUFF: {ax25frame}")
        self._digi_buf.append(ax25frame)

    #################################################
    # Routing Tab
    """
    def _update_routingTab(self, ax25_conf: dict):
        if not ax25_conf.get('netrom_cfg', {}):
            return
        if not hasattr(self._port_handler, 'get_RoutingTable'):
            logger.error(f'Port {self.port_id}: port_handler AttributeError (get_RoutingTable)')
            return
        rTab = self._port_handler.get_RoutingTable()
        if hasattr(rTab, 'update'):
            rTab.update(ax25_conf)
        # rTab.debug_out()
        return
    """
    #################################################
    def _process_rx_buf(self, buf):
        self._set_TXD()
        self._set_digi_TXD()
        ax25frame = AX25Frame()
        try:
            ax25frame.decode_ax25frame(buf.raw_data)
        except AX25DecodingERROR:
            logger.warning("-------------------------------------------------------------------")
            logger.warning(f'Port {self.port_id}: decoding: ')
            logger.warning(f'Port {self.port_id}: org {buf.raw_data}')
            logger.warning(f'Port {self.port_id}: hex {bytearray2hexstr(buf.raw_data)}')
            logger.warning(f'Port {self.port_id}: kiss-org {buf.kiss_frame}')
            logger.warning(f'Port {self.port_id}: kiss-hex {bytearray2hexstr(buf.kiss_frame)}')
            logger.warning("-------------------------------------------------------------------")
            return
        ax25frame.axip_add          = buf.axip_add
        ax25frame_conf              = ax25frame.get_frame_conf()
        ax25frame_conf['port_id']   = int(self.port_id)     # TODO using port_id fm this cfg
        # self._update_routingTab(ax25frame_conf)
        if not self._rx_dualPort_handler(ax25_frame=ax25frame):
            self._update_monitor(ax25frame=ax25frame, tx=False)
            self._mh_input(ax25frame_conf, tx=False)
            if hasattr(self._mcast_server, 'mcast_update_member_ip'):
                self._mcast_server.mcast_update_member_ip(ax25frame=ax25frame)
            self.rx_handler(ax25frame)
            if hasattr(self._mcast_server, 'mcast_rx'):
                self._mcast_server.mcast_rx(ax25frame=ax25frame)
        self._rx_echo(ax25_frame=ax25frame)


    def _rx_dualPort_handler(self, ax25_frame):
        if not self.dualPort_cfg:
            return False
        if not all((self.dualPort_primaryPort, self.dualPort_secondaryPort)):
            return False
        frame_raw = bytes(ax25_frame.data_bytes)
        # DualPort Echo Filter
        if frame_raw in self.dualPort_primaryPort.dualPort_echoFilter:
            return True
        # DualPort lastRX Filter
        if frame_raw == self.dualPort_primaryPort.dualPort_lastRX:
            self.dualPort_primaryPort.dualPort_lastRX = b''
            # DualPort Monitor
            self._dualPort_monitor_input(ax25frame=ax25_frame, tx=False, double=True)
            # MH / Port-Statistic
            ax25frame_conf = ax25_frame.get_frame_conf()
            self._mh_input(ax25frame_conf, tx=False)
            return True
        self.dualPort_primaryPort.dualPort_lastRX = frame_raw
        # Monitor
        self._update_monitor(ax25frame=ax25_frame, tx=False)
        # DualPort Monitor
        self._dualPort_monitor_input(ax25frame=ax25_frame, tx=False)
        # MH / Port-Statistic
        ax25frame_conf = ax25_frame.get_frame_conf()
        self._mh_input(ax25frame_conf, tx=False)
        self.dualPort_primaryPort.rx_handler(ax25_frame)
        return True

    ###################################################
    # TX Stuff
    def _tx_dualPort_handler(self, frame):
        if not self.check_dualPort():
            return False
        tx_port = self.get_dualPort_txPort(frame.to_call.call_str)
        tx_port._tx_out(frame)
        self.dualPort_echoFilter.append(bytes(frame.data_bytes))
        self.dualPort_echoFilter = self.dualPort_echoFilter[-7:]
        return True

    def _tx_handler(self):
        """ Main TX-Handler """
        """All Connections"""
        if self._tx_connection_buf():
            return True
        """Pipe-Tool"""
        if self._tx_pipe_buf():
            return True
        """UI Frame Buffer Like Beacons"""
        if self._tx_UI_buf():
            return True
        """DIGI"""
        if self._tx_digi_buf():
            return True
        """RX-Echo"""
        if self._tx_rxecho_buf():
            return True
        return False

    def _tx_connection_buf(self):
        for conn_id, conn in self.connections.items():
            if time.time() < conn.t2:
                continue
            snd_buf = list(conn.tx_buf_ctl) + list(conn.tx_buf_2send)
            if not snd_buf:
                continue
            # TODO Buffer handling in ax25Conn
            conn.tx_buf_ctl = []
            conn.tx_buf_2send = []
            conn.REJ_is_set = False
            for el in snd_buf:
                # if el.digi_call and conn.is_link:
                try:
                    if conn.digi_call:
                        # TODO Just check for digi_call while encoding
                        # print(conn.digi_call)
                        el.digi_check_and_encode(call=conn.digi_call, h_bit_enc=True)
                    else:
                        el.encode_ax25frame()
                except Exception as ex:
                    logger.error(ex)
                    continue
                try:
                    self.tx(frame=el)
                except AX25DeviceFAIL as e:
                    raise e
            return True # CHECKME !!! Just one connection at fnc-call ??
        return False

    def _tx_pipe_buf(self):
        tr = False
        for uid in self.pipes.keys():
            pipe = self.pipes[uid]
            # pipe.tx_crone()
            for frame in pipe.tx_frame_buf:
                try:
                    self.tx(frame=frame)
                    tr = True
                except AX25DeviceFAIL as e:
                    raise e
            pipe.tx_frame_buf = []
        return tr

    def _tx_UI_buf(self):
        tr = False
        for fr in self._unProto_buf:
            try:
                self.tx(frame=fr)
                tr = True
            except AX25DeviceFAIL as e:
                raise e
            # Monitor
            # self._gui_monitor(ax25frame=fr, tx=True)
        self._unProto_buf = []
        return tr

    def _tx_digi_buf(self):
        tr = False
        if time.time() > self._digi_TXD:
            for fr in self._digi_buf:
                try:
                    self.tx(frame=fr)
                    tr = True
                except AX25DeviceFAIL as e:
                    raise e
                # Monitor
                # self._gui_monitor(ax25frame=fr, tx=True)
            self._digi_buf = []
        return tr

    def _tx_rxecho_buf(self):
        tr = False
        # RX-Echo
        if self.port_id in self._port_handler.port_manager.rx_echo.keys():
            for fr in self._port_handler.port_manager.rx_echo[self.port_id].tx_buff:
                try:
                    self.tx(frame=fr)
                    tr = True
                except AX25DeviceFAIL as e:
                    raise e
                except AX25EncodingERROR:
                    logger.error('Encoding Error: ! MSG to short !')
                # Monitor
                # self._gui_monitor(ax25frame=fr, tx=True)
            self._port_handler.port_manager.rx_echo[self.port_id].tx_buff = []
        return tr

    def _rx_echo(self, ax25_frame):
        if self._port_handler.port_manager.rx_echo_on:
            self._port_handler.port_manager.rx_echo_input(ax_frame=ax25_frame, receiving_port_id=self.port_id)

    ##########################################################
    # DualPort
    def reset_dualPort(self):
        """ Called fm PortHandler """
        if self.dualPort_secondaryPort:
            self.dualPort_secondaryPort.dualPort_cfg = {}
            self.dualPort_secondaryPort.dualPort_primaryPort = None
            self.dualPort_secondaryPort.dualPort_secondaryPort = None
        self.dualPort_cfg = {}
        self.dualPort_primaryPort = None
        self.dualPort_secondaryPort = None

    def set_dualPort(self, conf: dict, secondary_port):
        """ Called fm PortHandler """
        if not all((conf, secondary_port)):
            return False
        """
        if any((self.dualPort_primaryPort, self.dualPort_secondaryPort)):
            return False
        """
        del self.dualPort_primaryPort
        del self.dualPort_secondaryPort
        self.dualPort_primaryPort = None
        self.dualPort_secondaryPort = None
        secondary_port.dualPort_cfg = conf
        secondary_port.dualPort_primaryPort = self
        secondary_port.dualPort_secondaryPort = secondary_port
        self.dualPort_cfg = secondary_port.dualPort_cfg
        self.dualPort_primaryPort = self
        self.dualPort_secondaryPort = secondary_port
        return True

    def is_dualPort(self):
        """ Called fm PortHandler """
        if self.dualPort_cfg:
            return self.check_dualPort()
        return False

    def is_dualPort_primary(self):
        """ Called fm PortHandler """
        if self.check_dualPort():
            return bool(self.dualPort_primaryPort == self)
        return False

    def get_dualPort_primary(self):
        """ Called fm PortHandler """
        if self.check_dualPort():
            return self.dualPort_primaryPort
        return None

    def check_dualPort(self):
        if self.dualPort_cfg:
            if not all((self.dualPort_primaryPort, self.dualPort_secondaryPort)):
                self.reset_dualPort()
                return False
            return True
        if any((self.dualPort_primaryPort, self.dualPort_secondaryPort)):
            self.reset_dualPort()
        return False

    def get_dualPort_txPort(self, call=''):
        if not self.check_dualPort():
            return self
        if not self.dualPort_cfg.get('auto_tx', False):
            if self.dualPort_cfg.get('tx_primary', True):
                return self.dualPort_primaryPort
            return self.dualPort_secondaryPort
        port_id = self.dualPort_primaryPort.port_id
        last_port_id = {
            0: self._mh.get_dualPort_firstRX(call, port_id),
            1: self._mh.get_dualPort_lastRX(call, port_id),
        }.get(self.dualPort_cfg.get('auto_tx_mode', 0), None)
        # last_port_id = self._mh.get_dualPort_lastRX(call, port_id)
        if last_port_id is None:
            return self.dualPort_primaryPort
        if last_port_id == self.dualPort_secondaryPort.port_id:
            return self.dualPort_secondaryPort
        return self.dualPort_primaryPort

    def _dualPort_monitor_input(self, ax25frame, tx: bool, double=False):
        if not self.check_dualPort():
            return
        data = dict(
            tx=bool(tx),
            ax25frame=ax25frame.get_frame_conf(),
            frame_rawData=bytes(ax25frame.data_bytes)
        )
        if not double:
            self._dualPort_monitor_insert(data)
            return
        self._dualPort_monitor_update(data)

    def _dualPort_monitor_update(self, data: dict):
        if not self.dualPort_primaryPort.dualPort_monitor_buf:
            self._dualPort_monitor_insert(data)
            return
        temp_data = self.dualPort_primaryPort.dualPort_monitor_buf[-1]
        is_prim = self.is_dualPort_primary()
        self_port_index = int(not is_prim)
        sec_port_index = int(is_prim)
        if temp_data[self_port_index]:
            self._dualPort_monitor_insert(data)
            return
        if not temp_data[sec_port_index]:
            self._dualPort_monitor_insert(data)
            return
        if temp_data[sec_port_index]['frame_rawData'] != data['frame_rawData']:
            self._dualPort_monitor_insert(data)
            return
        temp_data[self_port_index] = data

    def _dualPort_monitor_insert(self, data: dict):
        if self.is_dualPort_primary():
            self.dualPort_primaryPort.dualPort_monitor_buf.append(
                [data, {}]
            )
        else:
            self.dualPort_primaryPort.dualPort_monitor_buf.append(
                [{}, data]
            )
        self.dualPort_primaryPort.dualPort_monitor_buf = self.dualPort_primaryPort.dualPort_monitor_buf[-10000:]

    ############################################################
    # Pipe-Tool
    """
    def build_new_pipe(self,
                       own_call='',
                       add_str='',
                       cmd_pf=(False, False),
                       pid=0xf0
                       ):
        if not add_str:
            return False
        if not own_call:
            return False
        pipe = AX25Pipe(
            port_id=self.port_id,
            own_call=own_call,
            address_str=add_str,
            cmd_pf=cmd_pf,
            pid=pid
        )
        if pipe.uid not in self.pipes.keys():
            self.pipes[str(pipe.uid)] = pipe
            return True
        return False
    """

    def add_pipe(self, pipe_cfg=None, pipe=None):
        if pipe is None and not pipe_cfg:
            return None
        if pipe is None:
            try:
                pipe = AX25Pipe(pipe_cfg=pipe_cfg)
            except AttributeError:
                logger.error(f"Port {self.port_id}: AttributeError while adding AX25Pipe")
                return None
            except Exception as ex:
                logger.error(f"Port {self.port_id}: Error while adding AX25Pipe")
                logger.error(ex)
                return None
        self.pipes[pipe.get_pipe_uid()] = pipe
        return pipe

    def del_pipe(self, pipe):
        if not pipe:
            return False
        if pipe.get_pipe_uid() in self.pipes.keys():
            # self.port_handler.del_pipe_PH(pipe.uid)
            self.pipes[pipe.get_pipe_uid()] = None
            del self.pipes[pipe.get_pipe_uid()]
            return True
        return False

    ############################################################
    # L3 Connection
    def build_new_connection(self,
                             own_call: str,
                             dest_call: str,
                             via_calls: list,
                             axip_add: (str, int) = ('', 0),
                             link_conn=None,
                             # digi_conn=None
                             ):

        if link_conn:
            if link_conn.port_id:
                digi_call = f'{link_conn.my_call}-{link_conn.port_id}'
            else:
                digi_call = link_conn.my_call_str
            via_calls = [digi_call] + via_calls

        if link_conn and not via_calls:
            return False
        ax_frame = AX25Frame(dict(
            from_call_str=str(own_call),
            to_call_str=str(dest_call),
            via_calls=list(via_calls),
            axip_add=tuple(axip_add),
        ))

        conn = self.new_connection(ax25_frame=ax_frame)
        if not conn:
            return False
        if link_conn:
            conn.is_link_remote = True
            if conn.new_link_connection(link_conn):
                if link_conn.new_link_connection(conn):
                    return conn
            return False
        return conn

    def new_connection(self, ax25_frame):
        """ New Outgoing Connection """
        ax25_frame.ctl_byte.SABMcByte()
        try:
            ax25_frame.encode_ax25frame()  # TODO Not using full encoding to get UID
        except AX25EncodingERROR as e:
            logger.warning(f"Port {self.port_id}: new_connection ERROR {e}")
            logger.warning(f"Port {self.port_id}: new_connection destCall {ax25_frame.to_call}")
            logger.warning(f"Port {self.port_id}: new_connection via_calls {ax25_frame.via_calls}")
            return False

        while True:
            if ax25_frame.addr_uid not in self.connections.keys() and \
                    reverse_uid(ax25_frame.addr_uid) not in self.connections.keys() and \
                    (ax25_frame.from_call.call_str != ax25_frame.to_call.call_str):
                break

            logger.warning(f"Port {self.port_id}: Same UID !! {ax25_frame.addr_uid}")
            ax25_frame.from_call.call_str = ''
            ax25_frame.from_call.ssid += 1
            try:
                ax25_frame.from_call.enc_call()
            except AX25EncodingERROR:
                return False
            if ax25_frame.from_call.ssid > 15:
                logger.warning("Port {}: Same UID - No free SSID !! uid: {} - SSID: {}".format(self.port_id, ax25_frame.addr_uid, ax25_frame.from_call.ssid))
                return False
            try:
                ax25_frame.encode_ax25frame()  # TODO Not using full encoding to get UID
            except AX25EncodingERROR:
                logger.error("AX25EncodingError: AX25Port Nr:({}): new_connection()".format(self.port_id))
                raise AX25EncodingERROR(self)
        # try:
        #     conn = AX25Conn(ax25_frame, rx=False, port=self)
        # except AX25ConnectionERROR:
        #     return False
        conn = AX25Conn(ax25_frame, rx=False, port=self)
        # conn.digi_call = digi_call
        # conn.cli.change_cli_state(1)
        self.connections[ax25_frame.addr_uid] = conn
        return conn

    def del_connections(self, conn):
        self._port_handler.connection_manager.del_link(conn.uid)
        if conn.uid in self.pipes.keys():
            del self.pipes[conn.uid]
        for conn_uid in list(self.connections.keys()):
            if conn == self.connections[conn_uid]:
                del self.connections[conn_uid]
                return

    def disco_all_conns(self):
        for uid, conn in dict(self.connections).items():
            conn: AX25Conn
            conn.conn_disco()
            conn.conn_disco()   # Force Disco
        n = 0
        while self.connections and n < 10:
            time.sleep(0.5)
            n += 1
            if n > 9:
                # Make sure that loop is ending in any case
                logger.warning(f"Port {self.port_id}: Station Disco while Port closing failed.")
                break

    ####################################################################
    # L2 AX25 Frame
    def send_UI_frame(self,
                      own_call,
                      add_str: str,
                      text: bytes,
                      cmd_poll=(False, False),
                      pid=0xF0,
                      axip_add=None,
                      digi=False
                      ):
        if not own_call:
            logger.error("send_UI_frame: No own_call!")
            return False
        if not add_str:
            logger.error("send_UI_frame: No add_str!")
            return False
        if not text:
            logger.error("send_UI_frame: No text/payload!")
            return False
        tmp = add_str.upper().split(' ')
        dest_call = tmp[0].replace(' ', '')
        via_calls = []
        if len(tmp) > 1:
            via_calls = tmp[1:]
        if not axip_add:
            if via_calls:
                axip_add = self._mh.get_AXIP_fm_DB_MH(call_str=via_calls[0])
            else:
                axip_add = self._mh.get_AXIP_fm_DB_MH(call_str=dest_call)

        frame = AX25Frame(
            dict(
                from_call_str=str(own_call),
                to_call_str=str(dest_call),
                via_calls=list(via_calls),
                axip_add=tuple(axip_add),
            )
        )
        frame.ctl_byte.UIcByte()
        if pid in frame.pid_byte.pac_types.keys():
            frame.pid_byte.pac_types[pid]()
        else:
            frame.pid_byte.text()
        frame.ctl_byte.cmd, frame.ctl_byte.pf = cmd_poll
        frame.payload = text
        frame.from_call.call_str = own_call
        frame.to_call.call_str = dest_call
        try:
            frame.encode_ax25frame(digi=digi)
        except AX25EncodingERROR:
            return False
        else:
            self._unProto_buf.append(frame)
            return True

    def send_DM_frame(self, ax25_frame_cfg: dict):
        vias = list(ax25_frame_cfg.get('via_calls_str', []))
        vias.reverse()
        frame = AX25Frame(
            dict(
                from_call_str=str(ax25_frame_cfg.get('to_call_str', '')),
                to_call_str=str(ax25_frame_cfg.get('from_call_str', '')),
                via_calls=vias,
                axip_add=tuple(ax25_frame_cfg.get('axip_add', ('', 0))),
            )
        )
        frame.ctl_byte.DMcByte()

        #frame.ctl_byte.cmd, frame.ctl_byte.pf = False, False
        #frame.from_call.call_str = own_call
        #frame.to_call.call_str = dest_call
        try:
            frame.encode_ax25frame()
        except AX25EncodingERROR:
            return False
        else:
            self._unProto_buf.append(frame)
            return True

    #################################################
    #
    def _reset_ft_wait_timer(self, ax25_frame):
        if ax25_frame.ctl_byte.flag in ['I', 'SABM', 'DM', 'DISC', 'REJ', 'UA', 'UI']:
            for uid, conn in self.connections.items():
                conn.ft_reset_timer(ax25_frame.addr_uid)

    def _update_monitor(self, ax25frame, tx: bool = True):
        axframe_conf = ax25frame.get_frame_conf()
        axframe_conf['tx'] = bool(tx)
        axframe_conf['port'] = int(self.port_id)
        axframe_conf['port_conf'] = dict(self._port_cfg)
        self._port_handler.update_monitor(ax25frame_conf=axframe_conf)

    def _mh_input(self, ax25frame_conf, tx: bool):
        # MH / Port-Statistic
        primary_port_id = self.dualPort_cfg.get('primary_port_id', -1)
        self._mh.mh_input(ax25frame_conf, self.port_id, tx=tx, primary_port_id=primary_port_id)

    ###################################################
    # Tasker
    def port_tasker(self):
        """ Main Loop """
        #while self._loop_is_running:
        self._port_loop()
        # time.sleep(0.03)
        # print(f"Loop Ends Port: {self.port_id}")
        logger.info(f"Port {self.port_id}: Loop End")
        self.close()
        self.device = None
        self.ende = True

    def _port_loop(self):
        while self._loop_is_running:
            self._loop_watchdog = time.time()
            try:
                buf: RxBuf = self._rx()
                if buf and buf.raw_data:
                    self._process_rx_buf(buf)
            except (AX25DeviceERROR, AX25DeviceFAIL):
                break
            # Port Tasker
            self._task_Port()
            if time.time() > self._TXD:
                self._tx_handler()
            time.sleep(0.001)

    ##########################################################
    # Port/Connection Tasker
    def _task_Port(self):
        """ Execute Port related Cronjob like Beacon sending"""
        self._task_connections()
        self._digi_task()

    def _task_connections(self):
        """ Execute Cronjob on all Connections"""
        for uid, conn in dict(self.connections).items():
            if hasattr(conn, 'exec_cron'):
                conn.exec_cron()
    #########################################
    #
    def port_get_PH(self):
        return self._port_handler

    def port_get_port_cfg(self):
        return dict(self._port_cfg)

    ################################
    # Watchdog
    def get_watchdog_timer(self):
        return self._loop_watchdog

    def reset_watchdog_timer(self):
        self._loop_watchdog = time.time()

    ################################
    # Port Ctrl
    def set_block_incoming_conn(self, state=0):
        self._block_incoming_conn = state

    def get_block_incoming_conn(self):
        return self._block_incoming_conn
