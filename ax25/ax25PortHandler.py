import socket

from ax25.ax25dec_enc import AX25Frame, DecodingERROR
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
MYHEARD = MH()
MONITOR = ax25monitor.Monitor()


class DevDirewolf(object):
    def __init__(self):
        ############
        # CONFIG
        self.address = ('192.168.178.152', 8001)
        sock_timeout = 0.5
        # TODO: Set CFG from outer
        self.stat_cfg = MD5TESTstationCFG
        self.my_stations = self.stat_cfg.parm_StationCalls
        # CONFIG ENDE
        #############
        #############
        # VARS
        self.loop_is_running = False
        #############
        self.monitor = MONITOR
        self.connections = {
            # 'addrss_str_id': AX25Conn
        }
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

    def rx_pac_handler(self, ax25_frame: AX25Frame):
        # Monitor
        self.monitor.frame_inp(ax25_frame, 'DW')
        # MH List and Statistics
        MYHEARD.mh_inp(ax25_frame, 'DW')
        if ax25_frame.is_digipeated:
            # print(self.connections.keys())
            if ax25_frame.addr_uid in self.connections.keys():
                # Connection already established
                conn: AX25Conn = self.connections[ax25_frame.addr_uid]
                conn.handle_rx(ax25_frame=ax25_frame)
            else:   # Check MYStation Calls with SSID or Check incoming call without SSID
                if ax25_frame.to_call.call_str in self.my_stations \
                  or ax25_frame.to_call.call in self.my_stations:
                    cfg = self.stat_cfg()
                    conn = AX25Conn(ax25_frame, cfg)
                    conn.handle_rx(ax25_frame=ax25_frame)
                    self.connections[ax25_frame.addr_uid] = conn

    def tx_pac_handler(self):
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            el: AX25Frame
            for el in conn.tx_buf_2send:
                out = (bytes.fromhex('c000') + el.hexstr + bytes.fromhex('c0'))
                self.dw_sock.sendall(out)   # TODO try:
                # Monitor
                self.monitor.frame_inp(el, 'DW')
            self.connections[k].tx_buf_2send = []

        self.del_connections()

    def cron_pac_handler(self):
        """ Ecexute Cronjob on all Connections"""
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            conn.exec_cron()

    def new_connection(self, ax25_frame: AX25Frame):
        cfg = self.stat_cfg()
        ax25_frame = ax25_frame
        # ax25_frame.addr_uid = reverse_uid(ax25_frame.addr_uid)
        conn = AX25Conn(ax25_frame, cfg, rx=False)
        self.connections[ax25_frame.addr_uid] = conn
        # self.tx_pac_handler()

    def del_connections(self):
        del_k = []
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            # S0 ENDE
            if conn.zustand_exec.stat_index == 0:
                # And empty Buffer ?? S0 should be enough
                if not conn.tx_buf_2send:
                    del_k.append(k)
        for el in del_k:
            del self.connections[el]

    def run_loop(self):
        if not self.loop_is_running:
            self.loop_is_running = True
            while self.loop_is_running:
                self.run_once()

    def run_once(self):
        while True:
            try:
                buf = self.dw_sock.recv(333)
                """
                while b:
                    buf += b
                    b = self.dw_sock.recv(333)
                """
                logger.debug('Inp Buf> {}'.format(buf))
            except socket.timeout:
                break

            if buf:  # RX ############
                # TODO self.set_t0()
                ax25frame = AX25Frame()
                e = None
                try:
                    # Decoding
                    ax25frame.decode(buf)
                except DecodingERROR as e:
                    logger.error('DW.decoding: {}'.format(e))
                    break
                if e is None and ax25frame.validate():
                    # ######### RX #############
                    # Handling
                    logger.debug("STARTE RX")
                    self.rx_pac_handler(ax25frame)
                    logger.debug("ENDE RX")
                    ############################
                # self.timer_T0 = 0
            else:
                break

        #############################################
        # Crone
        logger.debug("STARTE CRON")
        self.cron_pac_handler()
        logger.debug("STARTE CRON")
        # ######### TX #############
        # TX
        logger.debug("STARTE TX")
        self.tx_pac_handler()
        logger.debug("STARTE TX")

        ############################

        ############################
        # Cleanup
        # self.del_connections()

