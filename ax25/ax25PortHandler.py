import copy
import socket
import threading
import time

from ax25.ax25dec_enc import AX25Frame, DecodingERROR, Call, reverse_uid
# from gui.guiMaín_old import MYHEARD
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
    def __init__(self, station_cfg):
        super(DevDirewolf, self).__init__()
        ############
        # CONFIG
        self.address = ('192.168.178.152', 8001)
        sock_timeout = 0.5
        # TODO: Set CFG from outer
        self.station_cfg = station_cfg
        self.portname = self.station_cfg.parm_PortName
        self.my_stations = self.station_cfg.parm_StationCalls
        self.is_stupid_digi = self.station_cfg.parm_is_StupidDigi
        self.is_smart_digi = self.station_cfg.parm_isSmartDigi
        self.parm_TXD = self.station_cfg.parm_TXD
        self.TXD = time.time()
        self.digi_buf: [AX25Frame] = []
        # CONFIG ENDE
        #############
        #############
        # VARS
        self.loop_is_running = False
        #############
        self.monitor = ax25monitor.Monitor()
        self.MYHEARD = self.station_cfg.parm_mh
        self.connections: {str: AX25Conn} = {}
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
        """ Not Happy with that Part . . :-( TODO Cleanup """
        # Monitor
        self.monitor.frame_inp(ax25_frame, self.portname)
        # MH List and Statistics
        self.MYHEARD.mh_inp(ax25_frame, self.portname)
        # Existing Connections
        uid = str(ax25_frame.addr_uid)
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

        # New Incoming Connection Request
        elif ax25_frame.to_call.call_str in self.my_stations \
                and ax25_frame.is_digipeated:
            cfg = self.station_cfg()
            self.connections[uid] = AX25Conn(ax25_frame, cfg)
            self.connections[uid].set_T2()
            self.connections[uid].handle_rx(ax25_frame=ax25_frame)
        # DIGI / LINK Connection
        elif reverse_uid(uid) in self.connections.keys():
            uid = reverse_uid(uid)
            my_digi_call = self.connections[uid].my_digi_call
            if my_digi_call:
                if ax25_frame.digi_check_and_encode(call=my_digi_call, h_bit_enc=False):
                    if uid in self.connections.keys():
                        self.connections[uid].set_T2()
                        self.connections[uid].handle_rx(ax25_frame=ax25_frame)

        # DIGI
        elif self.is_stupid_digi or self.is_smart_digi:
            for my_call in self.my_stations:
                # Simple "Stupid" DIGI
                if self.is_stupid_digi:
                    if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=True):
                        self.digi_buf.append(ax25_frame)
                else:
                    # DIGI UI Frames
                    if ax25_frame.ctl_byte.flag == 'UI':
                        if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=True):
                            self.digi_buf.append(ax25_frame)
                    else:
                        # New "Smart" Digi / Link Request
                        if ax25_frame.digi_check_and_encode(call=my_call, h_bit_enc=False):
                            print("NEW DIGI CONN")
                            # "Smart" DIGI
                            cfg = self.station_cfg()
                            # Incoming REQ
                            conn_in = AX25Conn(ax25_frame, cfg)
                            conn_in.my_digi_call = str(my_call)
                            conn_in.set_T2()
                            conn_in.handle_rx(ax25_frame=ax25_frame)
                            self.connections[uid] = conn_in
                            if conn_in.zustand_exec.stat_index == 5:  # Accept ( Incoming SABM )
                                # Init Outgoing Connection
                                print("CONN IN UID: {}".format(uid))
                                print("CONN IN MyCall: {}".format(conn_in.my_digi_call))
                                copy_ax25frame = copy.copy(ax25_frame)
                                copy_ax25frame.short_via_calls(call=my_call)
                                copy_ax25frame.encode()

                                while copy_ax25frame.addr_uid in self.connections.keys() or \
                                        reverse_uid(copy_ax25frame.addr_uid) in self.connections.keys():
                                    print("Same UID in Connections.. Try change SSID {}".format(copy_ax25frame.addr_uid))
                                    my_call = copy_ax25frame.increment_viacall_ssid(call=my_call)
                                    if my_call:
                                        copy_ax25frame.short_via_calls(call=my_call)
                                        print("New MyCall {}".format(my_call))
                                        copy_ax25frame.digi_check_and_encode(call=my_call, h_bit_enc=True)
                                        print("New UID  {}".format(copy_ax25frame.addr_uid))
                                        # copy_ax25frame.short_via_calls(call=my_call)
                                        # copy_ax25frame.encode(digi=True)
                                    else:
                                        conn_in.zustand_exec.change_state(4)
                                        break
                                if conn_in.zustand_exec.stat_index == 5:
                                    conn_out = AX25Conn(copy_ax25frame, cfg, rx=False)
                                    conn_out_uid = conn_out.ax25_out_frame.addr_uid
                                    conn_out.my_digi_call = str(my_call)
                                    print("CONN OUT UID: {}".format(conn_out_uid))
                                    print("CONN OUT MyCall: {}".format(conn_out.my_digi_call))
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
                        print("Send DIGI CALL: " + conn.my_digi_call)
                        el.set_check_h_bits(dec=False)
                        el.digi_check_and_encode(call=conn.my_digi_call, h_bit_enc=True)
                        el.encode(digi=True)  # Why encoding again ?? But it works.
                    else:
                        el.encode()

                    out = (bytes.fromhex('c000') + bytes(el.hexstr) + bytes.fromhex('c0'))
                    self.dw_sock.sendall(out)  # TODO try:
                    # self.connections[k].tx_buf_2send = self.connections[k].tx_buf_2send[1:]
                    # Monitor
                    self.monitor.frame_inp(el, 'DW-TX')
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
        cfg = self.station_cfg()
        # ax25_frame.addr_uid = reverse_uid(ax25_frame.addr_uid)
        conn = AX25Conn(ax25_frame, cfg, rx=False)
        conn.cli.change_cli_state(1)
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
