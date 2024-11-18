import datetime
import socket
import serial
import time
import crcmod

from ax25.ax25UI_Pipe import AX25Pipe

crc_x25 = crcmod.predefined.mkCrcFun('x-25')

from ax25.ax25Digi import AX25DigiConnection
from ax25.ax25Kiss import Kiss
from ax25.ax25Connection import AX25Conn
# from ax25.ax25NetRom import NetRom_decode_UI
from ax25.ax25dec_enc import AX25Frame, bytearray2hexstr
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.ax25_fnc import reverse_uid
from ax25.ax25Error import AX25EncodingERROR, AX25DecodingERROR, AX25DeviceERROR, AX25DeviceFAIL
from fnc.os_fnc import is_linux
from fnc.socket_fnc import get_ip_by_hostname

if is_linux():
    import termios



class RxBuf:
    axip_add = '', 0
    raw_data = b''
    kiss = b''


class AX25Port(object):
    def __init__(self, port_cfg, port_handler):
        # super(AX25Port, self).__init__()
        self.ende = False
        self.device_is_running = False
        self.loop_is_running = port_handler.is_running

        ############
        # CONFIG
        self.port_cfg = dict(port_cfg)
        self.port_handler = port_handler
        self.kiss = Kiss(port_cfg)
        self.port_param = port_cfg.get('parm_PortParm', ('', 0))
        self.portname = port_cfg.get('parm_PortName', '')
        self.port_typ = port_cfg.get('parm_PortTyp', '')
        self.port_id = port_cfg.get('parm_PortNr', -1)
        self.my_stations = port_cfg.get('parm_StationCalls', [])
        # self.parm_TXD = port_cfg.get('parm_TXD', 400)
        self._TXD = time.time()
        # CONFIG ENDE
        #############
        """ DIGI """
        # self.digi_calls = self.port_cfg.parm_Digi_calls
        self._parm_digi_TXD = port_cfg.get('parm_TXD', 400) * 4  # TODO add to Settings GUI
        self._digi_TXD = time.time()
        self._digi_buf = []         # RX/TX
        """ """
        self._digi_connections = {}
        self._UI_buf = []           # TX
        self.pipes = {}
        self.connections = {}
        #############
        # VARS
        self.monitor_out = True
        self.device = None
        self._mh = port_handler.get_MH()
        #############
        """ Dual Port """
        self.dualPort_primaryPort = None
        self.dualPort_secondaryPort = None
        self.dualPort_lastRX = b''  # Prim
        self.dualPort_echoFilter = []  # Prim
        self.dualPort_cfg = {}
        self.dualPort_monitor_buf = []
        ##############
        # AXIP VARs
        self.own_ipAddr = ''
        # self.axip_anti_spam = {}
        try:
            self.init()
        except AX25DeviceFAIL:
            # raise AX25DeviceFAIL(self)  # TODO in PortINIT
            AX25DeviceFAIL(self)

    def init(self):
        pass

    def __del__(self):
        self.close()
        # self.loop_is_running = False

    def set_kiss_parm(self):
        pass

    def close_device(self):
        pass

    def close(self):
        # TODO Del all conn's and Port cfg .. etc ..

        """
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            # Try to send a Disc
            conn.zustand_exec.change_state(4)
            conn.zustand_exec.tx(None)
        time.sleep(1)
        """
        self.loop_is_running = False
        self.close_device()
        # if self.device is not None:
        # self.device.close()

    def rx(self):
        return RxBuf()

    def tx(self, frame):
        if self._tx_dualPort_handler(frame):
            return
        self.tx_out(frame)

    def tx_out(self, frame):
        setattr(frame, 'rx_time', datetime.datetime.now())
        # frame.rx_time = datetime.datetime.now()
        self._gui_monitor(ax25frame=frame, tx=True)
        self._dualPort_monitor_input(ax25frame=frame, tx=True)
        try:
            self.tx_device(frame)
        except AX25DeviceERROR:
            logger.error(f"Error: tx_device() Port: {self.port_id}")
            self.close()

    def tx_device(self, frame):
        pass

    def tx_multicast(self, frame):
        pass

    def set_TXD(self):
        """ Internal TXD. Not Kiss TXD """
        self._TXD = time.time() + self.port_cfg.get('parm_TXD', 400) / 1000

    def set_digi_TXD(self):
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
        if reverse_uid(ax25_frame.addr_uid) in self.port_handler.link_connections.keys():
            print(f"Port rx_link_handler reverse_uid: UID: {ax25_frame.addr_uid}")
            print(f"Port rx_link_handler reverse_uid: FRAME ctl: {ax25_frame.ctl_byte.flag}")
            return False
        if ax25_frame.addr_uid in self.port_handler.link_connections.keys():
            # print(f"Link-Conn RX: {ax25_frame.addr_uid}")
            conn = self.port_handler.link_connections[ax25_frame.addr_uid][0]
            link_call = self.port_handler.link_connections[ax25_frame.addr_uid][1]
            if link_call:
                if ax25_frame.digi_check_and_encode(call=link_call, h_bit_enc=True):
                    conn.handle_rx(ax25_frame=ax25_frame)
                    return True
            conn.handle_rx(ax25_frame=ax25_frame)
            return True
        return False

    def _rx_pipe_handler(self, ax25_frame):
        uid = ax25_frame.get_frame_conf().get('uid', '')
        # logger.debug(uid)
        # logger.debug(self.pipes.keys())
        if uid not in self.pipes.keys():
            # logger.debug('UI-Pipe: No UID')
            return False
        if self.pipes[uid].get_pipe_connection() is not None:
            logger.debug('UI-Pipe: connection')
            return False
        logger.debug('UI-Pipe: OK')
        self.pipes[uid].handle_rx(ax25_frame=ax25_frame)
        return True

    def _rx_UI_handler(self, ax25_frame):
        # print(f"Port RX UI Handler - aprs_ais: {self.aprs_stat.aprs_ais}")
        ax25_frame_conf = ax25_frame.get_frame_conf()
        """
        netrom_cfg = ax25_frame_conf.get('netrom_cfg', {})
        if netrom_cfg:     # Net-Rom
            rTable = self.port_handler.get_RoutingTable()
            if rTable is None:
                return True
            ax25_frame_conf['port_id'] = int(self.port_id)
            rTable.NetRom_UI_rx(ax25_frame_conf)
            # NetRom_decode_UI(ax25_frame_conf)
            return True
        """
        aprs_ais = self.port_handler.get_aprs_ais()
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
        if ax25_frame.to_call.call_str in self.my_stations:
            uid = str(ax25_frame.addr_uid)
            if uid not in self.connections.keys():
                self.connections[uid] = AX25Conn(ax25_frame, port=self)
                # try:
                #     self.connections[uid] = AX25Conn(ax25_frame, port=self)
                # except AX25ConnectionERROR:
                #     return False
                # self.connections[uid].handle_rx(ax25_frame=ax25_frame)
                return True
        return False

    ########################################################
    # DIGI
    def _rx_digi_handler(self, ax25_frame):
        if not POPT_CFG.get_digi_CFG():
            return False
        # if ax25_frame.ctl_byte.flag == 'UI':
        #     return self._rx_simple_digi(ax25_frame)
        # if self.is_smart_digi:
        return self._rx_managed_digi(ax25_frame)

    def _rx_simple_digi(self, ax25_frame):
        for call in ax25_frame.via_calls:
            # digi_conf = dict(POPT_CFG.get_digi_CFG_for_Call(call.call_str))
            # if call.call_str in self.digi_calls:
            if POPT_CFG.get_digi_is_enabled(call.call_str):
                if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
                    self._digi_buf.append(ax25_frame)
                    # self.set_digi_TXD()
                    return True
        return False

    def _rx_managed_digi(self, ax25_frame):
        self._cleanup_digi_conn()
        for call in ax25_frame.via_calls:
            digi_conf = dict(POPT_CFG.get_digi_CFG_for_Call(call.call_str))
            if digi_conf.get('digi_enabled', False):
                if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
                    if digi_conf.get('managed_digi', False):
                        if ax25_frame.addr_uid not in self._digi_connections.keys():
                            ax25_conf = ax25_frame.get_frame_conf()
                            digi_conf.update(dict(
                                    rx_port=self,
                                    digi_call=str(call.call_str),
                                    digi_ssid=int(call.ssid),
                                    ax25_conf=ax25_conf
                                ))
                            # print(digi_conf)
                            if ax25_frame.ctl_byte.flag == 'UI':
                                AX25DigiConnection(digi_conf).digi_rx_handle(ax25_frame)
                                return

                            self._digi_connections[str(ax25_frame.addr_uid)] = AX25DigiConnection(digi_conf)
                        self._digi_connections[str(ax25_frame.addr_uid)].digi_rx_handle(ax25_frame)
                        return True
                    self.add_frame_to_digiBuff(ax25_frame)
                    return True
                return False
        return False

    def accept_digi_conn(self, uid: str):
        if uid not in self._digi_connections.keys():
            print('accept_digi_conn: UID ERROR')
            print(f'accept_digi_conn uid: {uid}')
            print(f'accept_digi_conn keys: {self._digi_connections.keys()}')
            return False
        self._digi_connections[uid].add_rx_conn_cron()
        return True

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
            digi_conn.digi_crone()

    def get_digi_conn(self):
        return self._digi_connections

    def add_frame_to_digiBuff(self, ax25frame):
        # print(f"Add DIGI-BUFF: {ax25frame}")
        self._digi_buf.append(ax25frame)

    #################################################

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
        self._gui_monitor(ax25frame=ax25_frame, tx=False)
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
        tx_port.tx_out(frame)
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
        tr = False
        for k in self.connections.keys():
            conn = self.connections[k]
            if time.time() > conn.t2 and not tr:
                snd_buf = list(conn.tx_buf_ctl) + list(conn.tx_buf_2send)
                conn.tx_buf_ctl = []
                conn.tx_buf_2send = []
                conn.REJ_is_set = False
                for el in snd_buf:
                    # if el.digi_call and conn.is_link:
                    if conn.digi_call:
                        # TODO Just check for digi_call while encoding
                        print(conn.digi_call)
                        el.digi_check_and_encode(call=conn.digi_call, h_bit_enc=True)
                    else:
                        el.encode_ax25frame()
                    try:
                        self.tx(frame=el)
                        tr = True
                    except AX25DeviceFAIL as e:
                        raise e
                    # Monitor
                    # self._gui_monitor(ax25frame=el, tx=True)
            else:
                tr = True
        return tr

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
        for fr in self._UI_buf:
            try:
                self.tx(frame=fr)
                tr = True
            except AX25DeviceFAIL as e:
                raise e
            # Monitor
            # self._gui_monitor(ax25frame=fr, tx=True)
        self._UI_buf = []
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
        if self.port_id in self.port_handler.rx_echo.keys():
            for fr in self.port_handler.rx_echo[self.port_id].tx_buff:
                try:
                    self.tx(frame=fr)
                    tr = True
                except AX25DeviceFAIL as e:
                    raise e
                except AX25EncodingERROR:
                    logger.error('Encoding Error: ! MSG to short !')
                # Monitor
                # self._gui_monitor(ax25frame=fr, tx=True)
            self.port_handler.rx_echo[self.port_id].tx_buff = []
        return tr

    def _rx_echo(self, ax25_frame):
        if self.port_handler.rx_echo_on:
            self.port_handler.rx_echo_input(ax_frame=ax25_frame, port_id=self.port_id)

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
            return False
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

    ##########################################################
    # Port/Connection Tasker
    def _task_Port(self):
        """ Execute Port related Cronjob like Beacon sending"""
        self._task_connections()
        self._digi_task()

    def _task_connections(self):
        """ Execute Cronjob on all Connections"""
        for k in list(self.connections.keys()):
            conn = self.connections.get(k, None)
            if conn:
                conn.exec_cron()

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
            return False
        print("port add_pipe")
        if pipe is None:
            pipe = AX25Pipe(pipe_cfg=pipe_cfg)
        print(pipe.get_pipe_uid())
        self.pipes[pipe.get_pipe_uid()] = pipe
        return True

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
                             via_calls: [str],
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
        """ 
        if own_call not in self.my_stations and not link_conn:
            return False
        """
        if link_conn and not via_calls:
            return False
        ax_frame = AX25Frame(dict(
            from_call_str=str(own_call),
            to_call_str=str(dest_call),
            via_calls=list(via_calls),
            axip_add=tuple(axip_add),
        ))
        """
        ax_frame.from_call.call_str = own_call
        ax_frame.to_call.call_str = dest_call
        ax_frame.via_calls = list(via_calls_fm_str(' '.join(via_calls)))
        ax_frame.axip_add = axip_add
        """

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
            logger.warning(f"new_connection ERROR {e}")
            print(f"new_connection ERROR {e}")
            print(f"new_connection destCall {ax25_frame.to_call}")
            logger.warning(f"new_connection destCall {ax25_frame.to_call}")
            print(f"new_connection via_calls {ax25_frame.via_calls}")
            logger.warning(f"new_connection via_calls {ax25_frame.via_calls}")
            return False

        while True:
            if ax25_frame.addr_uid not in self.connections.keys() and \
                    reverse_uid(ax25_frame.addr_uid) not in self.connections.keys() and \
                    (ax25_frame.from_call.call_str != ax25_frame.to_call.call_str):
                break

            print("Same UID !! {}".format(ax25_frame.addr_uid))
            logger.warning("Same UID !! {}".format(ax25_frame.addr_uid))
            ax25_frame.from_call.call_str = ''
            ax25_frame.from_call.ssid += 1
            try:
                ax25_frame.from_call.enc_call()
            except AX25EncodingERROR:
                return False
            if ax25_frame.from_call.ssid > 15:
                print("Same UID - No free SSID !! uid: {} - SSID: {}".format(ax25_frame.addr_uid, ax25_frame.from_call.ssid))
                logger.warning("Same UID - No free SSID !! uid: {} - SSID: {}".format(ax25_frame.addr_uid, ax25_frame.from_call.ssid))
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
        self.port_handler.del_link(conn.uid)
        if conn.uid in self.pipes.keys():
            del self.pipes[conn.uid]
        for conn_uid in list(self.connections.keys()):
            if conn == self.connections[conn_uid]:
                del self.connections[conn_uid]
                return

    ####################################################################
    # L2 AX25 Frame
    def send_UI_frame(self,
                      own_call,
                      add_str: str,
                      text: bytes,
                      cmd_poll=(False, False),
                      pid=0xF0
                      ):
        if not own_call:
            return False
        if not add_str:
            return False
        if not text:
            return False
        tmp = add_str.upper().split(' ')
        dest_call = tmp[0].replace(' ', '')
        via_calls = []
        if len(tmp) > 1:
            via_calls = tmp[1:]
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
            frame.encode_ax25frame()
        except AX25EncodingERROR:
            return False
        else:
            self._UI_buf.append(frame)
            return True

    def _reset_ft_wait_timer(self, ax25_frame):
        if ax25_frame.ctl_byte.flag in ['I', 'SABM', 'DM', 'DISC', 'REJ', 'UA', 'UI']:
            for k in self.connections.keys():
                self.connections[k].ft_reset_timer(ax25_frame.addr_uid)

    def _gui_monitor(self, ax25frame, tx: bool = True):
        if self.monitor_out:
            port_cfg = self.port_cfg
            self.port_handler.update_monitor(
                # monitor_frame_inp(ax25frame, self.port_cfg),
                ax25frame,
                port_conf=port_cfg,
                tx=tx)

    def _mh_input(self, ax25frame_conf, tx: bool):
        # MH / Port-Statistic
        primary_port_id = self.dualPort_cfg.get('primary_port_id', -1)
        self._mh.mh_input(ax25frame_conf, self.port_id, tx=tx, primary_port_id=primary_port_id)

    def port_tasker(self):
        """ Main Loop """
        while self.loop_is_running:
            self._tasks()
            # time.sleep(0.03)
        print(f"Loop Ends Port: {self.port_id}")
        logger.info(f"Loop Ends Port: {self.port_id}")
        self.close()
        self.device = None
        self.ende = True

    def _tasks(self):
        while self.loop_is_running:
            try:
                ##############################################
                buf: RxBuf = self.rx()
                ##############################################
            except AX25DeviceERROR:
                # print(e)
                # time.sleep(0.05)
                # self.close()
                break
            if not self.loop_is_running:
                # self.close()
                break
            if buf is None:
                time.sleep(0.05)
                break
            if not buf.raw_data:  # RX ############
                time.sleep(0.05)
                break
            self.set_TXD()
            self.set_digi_TXD()
            ax25frame = AX25Frame()
            try:
                # Decoding
                ax25frame.decode_ax25frame(buf.raw_data)
            except AX25DecodingERROR:
                logger.error('Port:{} decoding: '.format(self.portname))
                logger.error('{}: org {}'.format(self.portname, buf.raw_data))
                logger.error('{}: hex {}'.format(self.portname, bytearray2hexstr(buf.raw_data)))
                break
            if ax25frame.validate():
                ax25frame.axip_add = buf.axip_add
                # ax25frame.rx_time = datetime.datetime.now()
                # setattr(ax25frame, 'rx_time', datetime.datetime.now())
                # ######### RX #############
                if not self._rx_dualPort_handler(ax25_frame=ax25frame):
                    # Monitor
                    self._gui_monitor(ax25frame=ax25frame, tx=False)
                    # MH / Port-Statistic
                    ax25frame_conf = ax25frame.get_frame_conf()
                    self._mh_input(ax25frame_conf, tx=False)
                    self.rx_handler(ax25frame)

                # RX-ECHO
                self._rx_echo(ax25_frame=ax25frame)
                # AXIP-Multicast
                if self.port_cfg.get('parm_axip_Multicast', False):
                    self.tx_multicast(frame=ax25frame)

            if self.port_cfg.get('parm_full_duplex', False):
                break

        if self.loop_is_running:
            #############################################
            # Crone
            self._task_Port()
            # if time.time() > self.TXD or self.port_cfg.parm_full_duplex:
            if time.time() > self._TXD:
                # ######### TX #############
                self._tx_handler()


class KissTCP(AX25Port):
    def init(self):
        if self.loop_is_running:
            print("KISS TCP INIT")
            logger.info("KISS TCP INIT")
            sock_timeout = 0.2
            # self.kiss = b'\x00'
            self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            try:
                self.device.settimeout(sock_timeout)
                self.device.connect(self.port_param)
                self.device_is_running = True

            except (OSError, ConnectionRefusedError, ConnectionError) as e:
                logger.error('Error. Cant connect to KISS TCP Device {}'.format(self.port_param))
                logger.error('{}'.format(e))
                # self.device.shutdown(socket.SHUT_RDWR)
                # self.device.close()
                self.close_device()
                raise AX25DeviceFAIL

            else:
                if self.kiss.is_enabled:
                    # self.device.sendall(self.kiss.device_kiss_start_1())
                    try:
                        self.device.sendall(self.kiss.device_jhost())
                        # print(self.device.recv(999))
                    except BrokenPipeError as e:
                        print('{}'.format(e))
                        logger.error('{}'.format(e))
                        # self.device.shutdown(socket.SHUT_RDWR)
                        # self.device.close()
                        self.close_device()
                    else:
                        self.set_kiss_parm()

    def __del__(self):
        # self.device.shutdown(socket.SHUT_RDWR)
        self.close_device()

    def close_device(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                # Deactivate KISS Mode on TNC
                """
                if self.kiss.is_enabled:
                    self.device.sendall(self.kiss.device_kiss_end())
                """

                self.device.shutdown(socket.SHUT_RDWR)
                self.device.close()
            except (OSError, ConnectionRefusedError, ConnectionError, AttributeError):
                pass
            finally:
                self.device_is_running = False
                if self.device is not None:
                    self.device.close()
                print("KISS TCP FINALLY")

    def set_kiss_parm(self):
        if self.kiss.is_enabled and self.device is not None and self.device_is_running:
            self.device.sendall(self.kiss.set_all_parameter())

    def rx(self):
        try:
            recv_buff = self.device.recv(999)
        except socket.timeout as e:
            # self.device.close()
            # raise AX25DeviceERROR(e, self)
            # raise AX25DeviceERROR
            return None
        except OSError as e:
            raise AX25DeviceERROR(e, self)
        ret = RxBuf()

        if recv_buff:
            de_kiss_fr = self.kiss.de_kiss(recv_buff)
            if de_kiss_fr:
                ret.raw_data = de_kiss_fr
                return ret
        else:
            return ret

    def tx_device(self, frame):
        try:
            self.device.sendall(self.kiss.kiss(frame.data_bytes))
            # self.device.sendall(b'\xC0' + b'\x00' + frame.bytes + b'\xC0')
        except (OSError, ConnectionRefusedError, ConnectionError, socket.timeout) as e:
            logger.error('Error. Cant send Packet to KISS TCP Device. Try Reinit Device {}'.format(self.port_param))
            logger.error('{}'.format(e))
            try:
                self.init()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                raise AX25DeviceFAIL
        # else:
        #     self._mh.bw_mon_inp(frame, self.port_id)

        ############################################


class KISSSerial(AX25Port):

    def init(self):
        if self.loop_is_running:
            print("KISS Serial INIT")
            logger.info("KISS Serial INIT")
            # self.kiss = b'\x00'
            try:
                self.device = serial.Serial(self.port_param[0], self.port_param[1], timeout=0.2)
                self.device_is_running = True
            except (FileNotFoundError, serial.serialutil.SerialException) as e:
                print('Error. Cant connect to KISS Serial Device {}'.format(self.port_param))
                logger.error('Error. Cant connect to KISS Serial Device {}'.format(self.port_param))
                logger.error('{}'.format(e))
                print('{}'.format(e))
                self.close_device()
                raise AX25DeviceFAIL
            else:
                if self.kiss.is_enabled:
                    tnc_banner = self.device.readall().decode('UTF-8', 'ignore')
                    logger.info(f"TNC-Banner: {tnc_banner}")
                    print(f"TNC-Banner: {tnc_banner}")
                    # self.device.flush()
                    self.device.write(self.kiss.device_kiss_start_1())
                    self.device.readall()
                    # print(self.device.read())
                    # self.device.write(self.kiss.device_jhost())
                    # self.device.write(b'\xc0\x10\x0c\xc0')
                    self.set_kiss_parm()

    def __del__(self):
        self.close_device()

    def _reinit(self):
        self._close_dev()
        try:
            self.init()
        except AX25DeviceFAIL:
            raise AX25DeviceFAIL

    def close_device(self):
        self.loop_is_running = False
        self._close_dev()

    def _close_dev(self):
        # self.loop_is_running = False
        if self.device is not None:
            try:
                # Deactivate KISS Mode on TNC
                if self.kiss.is_enabled:
                    self.device.write(self.kiss.device_kiss_end())
                if is_linux():
                    try:
                        self.device.flush()
                    except termios.error:
                        pass
                else:
                    self.device.flush()
                self.device.close()
                # self.device_is_running = False
            except (FileNotFoundError, serial.serialutil.SerialException, OSError, TypeError):
                pass
            self.device_is_running = False

    def set_kiss_parm(self):
        if self.kiss.is_enabled and self.device is not None:
            try:
                self.device.write(self.kiss.set_all_parameter())
            except serial.portNotOpenError:
                self.device_is_running = False
                self.close_device()

    def rx(self):
        recv_buff = b''
        while self.loop_is_running and self.device_is_running:
            try:
                recv_buff += self.device.read()

            except serial.SerialException:
                # There is no new data from serial port
                return RxBuf()
            except TypeError as e:
                logger.warning('Serial Device Error {}'.format(e))
                try:
                    # self.init()
                    self._reinit()
                except AX25DeviceFAIL:
                    self.close_device()
                    logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                    raise AX25DeviceERROR
            else:
                ret = RxBuf()
                if recv_buff:
                    de_kiss_fr = self.kiss.de_kiss(recv_buff)
                    if de_kiss_fr:  # TODO !!!! flush buffer ?
                        ret.raw_data = de_kiss_fr
                        return ret
                else:
                    return ret

    def tx_device(self, frame):
        if self.device is None:
            try:
                # self.init()
                self._reinit()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                self.close_device()
                raise AX25DeviceERROR
        if self.device is None:
            logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
            self.close_device()
            raise AX25DeviceERROR

        try:
            self.device.write(self.kiss.kiss(frame.data_bytes))
        except (FileNotFoundError, serial.serialutil.SerialException) as e:
            logger.warning(
                'Error. Cant send Packet to KISS Serial Device. Try Reinit Device {}'.format(self.port_param))
            logger.warning('{}'.format(e))
            try:
                # self.init()
                self._reinit()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                self.close_device()
                raise AX25DeviceERROR
        # else:
        #     self._mh.bw_mon_inp(frame, self.port_id)


class AXIP(AX25Port):

    def init(self):
        if self.loop_is_running:
            print("AXIP Client INIT")
            logger.info("AXIP Client INIT")
            if not self.port_param[0]:
                hostname = socket.gethostname()
                self.port_param = socket.gethostbyname(hostname), self.port_param[1]
            self.own_ipAddr = self.port_param[0]
            logger.info('AXIP bind on IP: {}'.format(self.own_ipAddr))
            sock_timeout = 0.01

            self.device = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            # self.device.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.device.settimeout(sock_timeout)
            try:
                self.device.bind(self.port_param)
                self.device_is_running = True
            except OSError as e:
                logger.error('AXIP 2 {}'.format(e))
                # self.device.shutdown(socket.SHUT_RDWR)
                self.device.close()
                self.device_is_running = False
                raise AX25DeviceFAIL

    def __del__(self):
        # self.device.shutdown(socket.SHUT_RDWR)
        self.close_device()

    def close_device(self):
        self.loop_is_running = False
        if self.device is not None:
            try:
                print("Try Close AXIP")
                self.device.close()
            except (socket.error, AttributeError) as e:
                print(f"Try Close AXIP except: {e}")
            finally:
                self.device_is_running = False
                if self.device is not None:
                    self.device.close()
                print("AXIP FINALLY")

    def rx(self):
        try:
            udp_recv = self.device.recvfrom(800)
            # self.device.settimeout(0.1)
        # except socket.error:
        # raise AX25DeviceERROR
        except OSError:
            return RxBuf()
        else:
            recv_buff = udp_recv[0]
            to_call_ip_addr = udp_recv[1]
            ###################################
            # CRC
            crc = recv_buff[-2:]
            crc = int(bytearray2hexstr(crc[::-1]), 16)
            pack = recv_buff[:-2]
            calc_crc = crc_x25(pack)
            ret = RxBuf()
            ret.axip_add = to_call_ip_addr
            if calc_crc == crc:
                ret.raw_data = pack
                ret.kiss = b''
            return ret

    def tx_device(self, frame, no_multicast=False):
        if frame.axip_add != ('', 0):
            axip_add = get_ip_by_hostname(frame.axip_add[0])
            if axip_add:
                frame.axip_add = (axip_add, int(frame.axip_add[1]))
            ###################################
            # CRC
            calc_crc = crc_x25(frame.data_bytes)
            calc_crc = bytes.fromhex(hex(calc_crc)[2:].zfill(4))[::-1]
            ###################################
            try:
                self.device.sendto(frame.data_bytes + calc_crc, frame.axip_add)
                # self.device.settimeout(0.1)
            except (ConnectionRefusedError, ConnectionError, socket.timeout, socket.error) as e:
                print('Error. Cant send Packet to AXIP Device. Try Reinit Device {}'.format(frame.axip_add))
                logger.warning('Error. Cant send Packet to AXIP Device. Try Reinit Device {}'.format(frame.axip_add))
                print('{}'.format(e))
                logger.warning('{}'.format(e))
                try:
                    self.init()
                except AX25DeviceFAIL:
                    logger.error('Error. Reinit AXIP Failed !! {}'.format(self.port_param))
                    raise AX25DeviceFAIL
            except OSError:
                pass
            except TypeError as e:
                logger.error(f"TypeError AXIP Dev !!! \n {e}")
                print(f"TypeError AXIP Dev !!! \n {e}")
                logger.error(frame.axip_add)
                print(frame.axip_add)
                logger.error(frame.data_bytes + calc_crc)
                print(frame.data_bytes + calc_crc)
            # else:
            #     self._mh.bw_mon_inp(frame, self.port_id)

        if self.port_cfg.get('parm_axip_Multicast', False) and not no_multicast:
            self.tx_multicast(frame=frame)

    def tx_multicast(self, frame):
        for axip_add in self.port_handler.multicast_ip_s:
            if axip_add != frame.axip_add:
                frame.axip_add = axip_add
                # TODO Failed IP
                try:
                    self.tx_device(frame, no_multicast=True)
                except (ConnectionRefusedError, ConnectionError, socket.timeout):
                    self._mh.mh_ip_failed(axip_add, self.port_id)
                except (OSError, socket.error) as e:
                    logger.error(
                        'Error. Cant send Packet to AXIP Device MULTICAST {}'.format(frame.axip_add))
                    logger.error('{}'.format(e))

    """
    def clean_anti_spam(self):
        for k in list(self.axip_anti_spam.keys()):
            if self.axip_anti_spam[k][1] < time.time():
                del self.axip_anti_spam[k]
    """
AX25DeviceTAB = {
            'KISSTCP': KissTCP,
            'KISSSER': KISSSerial,
            'AXIP': AXIP,
        }