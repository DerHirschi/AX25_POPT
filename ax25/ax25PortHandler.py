import socket
import threading
import time

from ax25.ax25dec_enc import AX25Frame, DecodingERROR, Call, reverse_uid
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
        self.is_smart_digi = self.stat_cfg.parm_isSmartDigi
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
        """ Crapy Code :-( TODO Cleanup """
        # Monitor
        self.monitor.frame_inp(ax25_frame, self.portname)
        # MH List and Statistics
        self.MYHEARD.mh_inp(ax25_frame, self.portname)
        # Existing Connections
        uid = str(ax25_frame.addr_uid)
        print("KEY:{} - {} -{}".format(ax25_frame.addr_uid, uid, self.connections.keys()))
        if uid in self.connections.keys():
            # Connection already established
            if ax25_frame.is_digipeated:
                self.connections[uid].set_T2()
                self.connections[uid].handle_rx(ax25_frame=ax25_frame)
            else:
                print("ELSE")
                my_digi_call = self.connections[uid].my_digi_call
                if my_digi_call:
                    if ax25_frame.digi_check_and_encode(call=my_digi_call, h_bit_enc=False):
                        if uid in self.connections.keys():
                            self.connections[uid].set_T2()
                            print("KEY:{} - {} -{}".format(ax25_frame.addr_uid, uid, self.connections.keys()))
                            self.connections[uid].handle_rx(ax25_frame=ax25_frame)
        # DIGI / LINK Connection
        elif reverse_uid(uid) in self.connections.keys():
            print("ELSE REV")
            uid = reverse_uid(uid)
            my_digi_call = self.connections[uid].my_digi_call
            if my_digi_call:
                if ax25_frame.digi_check_and_encode(call=my_digi_call, h_bit_enc=False):
                    if uid in self.connections.keys():
                        self.connections[uid].set_T2()
                        print("KEY:{} - {} -{}".format(ax25_frame.addr_uid, uid, self.connections.keys()))
                        self.connections[uid].handle_rx(ax25_frame=ax25_frame)

        # New Incoming Connection Request
        elif ax25_frame.to_call.call_str in self.my_stations\
                and ax25_frame.is_digipeated:
            cfg = self.stat_cfg()
            self.connections[str(ax25_frame.addr_uid)] = AX25Conn(ax25_frame, cfg)
            self.connections[ax25_frame.addr_uid].set_T2()
            self.connections[ax25_frame.addr_uid].handle_rx(ax25_frame=ax25_frame)
        # DIGI
        elif self.is_stupid_digi or self.is_smart_digi:
            for my_call in self.my_stations:
                if self.is_stupid_digi:
                    # Simple "Stupid" DIGI
                    if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=True):
                        self.digi_buf.append(ax25_frame)
                else:
                    if ax25_frame.ctl_byte.flag == 'UI':
                        if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=True):
                            self.digi_buf.append(ax25_frame)
                    else:
                        # New "Smart" Digi / Link Request
                        if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=False):
                            print("NEW DIGI CONN")
                            # "Smart" DIGI
                            cfg = self.stat_cfg()
                            # Incoming REQ
                            conn_in = AX25Conn(ax25_frame, cfg)
                            conn_in.my_digi_call = my_call
                            conn_in.set_T2()
                            conn_in.handle_rx(ax25_frame=ax25_frame)
                            self.connections[str(ax25_frame.addr_uid)] = conn_in
                            if conn_in.zustand_exec.stat_index == 5:    # Accept ( Incoming SABM )
                                # Init Outgoing Connection
                                ax25_frame.short_via_calls(call=my_call)
                                ax25_frame.encode()
                                conn_out = AX25Conn(ax25_frame, cfg, rx=False)
                                conn_out_uid = conn_out.ax25_out_frame.addr_uid
                                conn_out.my_digi_call = my_call
                                conn_out.DIGI_Connection = conn_in
                                conn_in.DIGI_Connection = conn_out
                                conn_in.tx_buf_rawData = conn_out.rx_buf_rawData
                                conn_out.tx_buf_rawData = conn_in.rx_buf_rawData
                                conn_out.zustand_exec.__init__(conn_out)
                                conn_in.zustand_exec.__init__(conn_in)  # Reinit
                                self.connections[str(conn_out_uid)] = conn_out



    def tx_pac_handler(self):
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            if time.time() > conn.t2:
                snd_buf = list(conn.tx_buf_ctl) + list(conn.tx_buf_2send)
                conn.tx_buf_ctl = []
                conn.tx_buf_2send = []
                conn.REJ_is_set = False
                # self.connections[k].tx_buf_2send = []
                el: AX25Frame
                for el in snd_buf:
                    if conn.my_digi_call:
                        # print(conn.my_digi_call)
                        el.digi_check_and_encode(call=conn.my_digi_call, h_bit_enc=True)
                        el.encode(digi=True)    # Why encoding again ?? But it works.
                    else:
                        el.encode()

                    out = (bytes.fromhex('c000') + bytes(el.hexstr) + bytes.fromhex('c0'))
                    self.dw_sock.sendall(out)   # TODO try:
                    # self.connections[k].tx_buf_2send = self.connections[k].tx_buf_2send[1:]
                    # Monitor
                    self.monitor.frame_inp(el, self.portname)
        # DIGI
        fr: AX25Frame
        for fr in self.digi_buf:
            out = (bytes.fromhex('c000') + fr.hexstr + bytes.fromhex('c0'))
            self.dw_sock.sendall(out)  # TODO try:
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
                logger.debug('Inp Buf> {}'.format(buf))
            except socket.timeout:
                break

            if buf:  # RX ############
                self.set_TXD()
                ax25frame = AX25Frame()
                e = None
                try:
                    # Decoding
                    ax25frame.decode(buf)
                except DecodingERROR as e:
                    logger.error('{}.decoding: {}'.format(self.portname, e))
                    break
                if e is None and ax25frame.validate():
                    # ######### RX #############
                    # Handling
                    self.rx_pac_handler(ax25frame)
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

