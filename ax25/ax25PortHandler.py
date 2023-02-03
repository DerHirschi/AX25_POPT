import socket
import threading
import time

from ax25.ax25dec_enc import AX25Frame, DecodingERROR, Call
from ax25.ax25Statistics import MH
from ax25.ax25PacHandler import AX25Conn
from config_station import MD5TESTstationCFG

import ax25.ax25monitor as ax25monitor

import logging
# Enable logging
"""
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
"""
logger = logging.getLogger(__name__)


class DevDirewolf(threading.Thread):
    def __init__(self):
        super(DevDirewolf, self).__init__()
        ############
        # CONFIG
        self.address = ('192.168.178.152', 8001)
        sock_timeout = 0.5
        # TODO: Set CFG from outer
        self.stat_cfg = MD5TESTstationCFG
        self.portname = self.stat_cfg.parm_PortName
        self.my_stations = self.stat_cfg.parm_StationCalls
        self.is_stupid_digi = self.stat_cfg.parm_is_StupidDigi
        self.is_digi = self.stat_cfg.parm_isDigi
        self.parm_TXD = self.stat_cfg.parm_TXD
        self.TXD = time.time()
        self.digi_buf: [AX25Frame] = []
        # CONFIG ENDE
        #############
        #############
        # VARS
        self.loop_is_running = False
        #############
        self.monitor = ax25monitor.Monitor()
        self.MYHEARD = MH()
        self.connections: {str: AX25Conn} = {}
        # AX25Conn(AX25Frame(), self.stat_cfg)      # Just do onetime Init
        self.dw_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            self.dw_sock.connect(self.address)
            self.dw_sock.settimeout(sock_timeout)
        except (OSError, ConnectionRefusedError, ConnectionError) as e:
            logger.error('Error. Cant connect to Direwolf {}'.format(self.address))
            logger.error('{}'.format(e))
            raise e

    def __del__(self):
        self.dw_sock.close()

    def set_TXD(self):
        self.TXD = time.time() + self.parm_TXD / 1000

    def rx_pac_handler(self, ax25_frame: AX25Frame):
        self.set_TXD()
        # Monitor
        self.monitor.frame_inp(ax25_frame, self.portname)
        # MH List and Statistics
        self.MYHEARD.mh_inp(ax25_frame, self.portname)
        for_digi = False
        if self.is_stupid_digi:
            for my_call in self.my_stations:
                if ax25_frame.is_for_digi(call=my_call, h_bit=True):
                    self.digi_buf.append(ax25_frame)
                    print("DIGI ....")
                    for_digi = True

        if ax25_frame.is_digipeated and not for_digi:
            # print(self.connections.keys())
            if ax25_frame.addr_uid in self.connections.keys():
                # Connection already established
                self.connections[ax25_frame.addr_uid].set_T2()      # TODO Extra Receive Timer T0
                self.connections[ax25_frame.addr_uid].handle_rx(ax25_frame=ax25_frame)
            else:   # Check MYStation Calls with SSID or Check incoming call without SSID
                if ax25_frame.to_call.call_str in self.my_stations:
                    cfg = self.stat_cfg()
                    self.connections[ax25_frame.addr_uid] = AX25Conn(ax25_frame, cfg)
                    self.connections[ax25_frame.addr_uid].set_T2()  # TODO Extra Receive Timer T0
                    self.connections[ax25_frame.addr_uid].handle_rx(ax25_frame=ax25_frame)

    def tx_pac_handler(self):
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            if time.time() > conn.t2:
                snd_buf = list(conn.tx_buf_ctl) + list(conn.tx_buf_2send)
                conn.tx_buf_ctl = []
                conn.REJ_is_set = False
                # self.connections[k].tx_buf_2send = []
                el: AX25Frame
                for el in snd_buf:
                    el.encode()
                    out = (bytes.fromhex('c000') + el.hexstr + bytes.fromhex('c0'))
                    self.dw_sock.sendall(out)   # TODO try:
                    self.connections[k].tx_buf_2send = self.connections[k].tx_buf_2send[1:]
                    # Monitor
                    self.monitor.frame_inp(el, self.portname)
        # DIGI
        fr: AX25Frame
        for fr in self.digi_buf:
            out = (bytes.fromhex('c000') + fr.hexstr + bytes.fromhex('c0'))
            self.dw_sock.sendall(out)  # TODO try:
            print("DIGI TX --")
            # Monitor
            self.monitor.frame_inp(fr, self.portname)
        self.digi_buf = []
        self.del_connections()

    def cron_pac_handler(self):
        """ Ecexute Cronjob on all Connections"""
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            conn.exec_cron()

    def new_connection(self, ax25_frame: AX25Frame):
        cfg = self.stat_cfg()
        # ax25_frame.addr_uid = reverse_uid(ax25_frame.addr_uid)
        conn = AX25Conn(ax25_frame, cfg, rx=False)
        self.connections[ax25_frame.addr_uid] = conn
        # self.tx_pac_handler()

    def del_connections(self):
        del_k = []
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            # S0 ENDE
            if not conn.zustand_exec.stat_index:
                # And empty Buffer ?? S0 should be enough
                del_k.append(k)
        for el in del_k:
            del self.connections[el]

    def run(self):
        if not self.loop_is_running:
            self.loop_is_running = True
            while self.loop_is_running:
                self.run_once()

    def run_once(self):
        while True:
            try:
                # buf = self.dw_sock.recv(333)
                buf = self.dw_sock.recv(400)
                """
                while b:
                    buf += b
                    b = self.dw_sock.recv(333)
                """
                logger.debug('Inp Buf> {}'.format(buf))
            except socket.timeout:
                break

            if buf:  # RX ############
                ax25frame = AX25Frame()
                e = None
                try:
                    # Decoding
                    ax25frame.decode(buf)
                except DecodingERROR as e:
                    logger.error('{}}.decoding: {}'.format(self.portname, e))
                    break
                if e is None and ax25frame.validate():
                    # ######### RX #############
                    # Handling
                    self.rx_pac_handler(ax25frame)
                    ############################
                # self.timer_T0 = 0
            else:
                break
        if time.time() > self.TXD:
            #############################################
            # Crone
            self.cron_pac_handler()
            # ######### TX #############
            # TX
            self.tx_pac_handler()

        ############################

        ############################
        # Cleanup
        # self.del_connections()

