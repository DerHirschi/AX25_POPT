import socket
from ax25dec_enc import AX25Frame, DecodingERROR, EncodingERROR
from ax25Statistics import MH
from ax25PacHandler import AX25Conn
from config_station import MD5TESTstationCFG

import monitor

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)
MYHEARD = MH()
MONITOR = monitor.Monitor()


class DevDirewolf(object):
    def __init__(self):
        ############
        # CONFIG
        self.address = ('192.168.178.152', 8001)
        sock_timeout = 1.0
        # TODO: Set CFG from outer
        self.stat_cfg = MD5TESTstationCFG
        self.my_stations = self.stat_cfg.parm_StationCalls
        # AX25 Parm
        # self.parm_MaxFrame = self.stat_cfg.parm_MaxFrame
        # self.MaxFrame = 0
        # CONFIG ENDE
        #############
        #############
        # VARS
        # self.tx_buff_data: [b''] = []     # Abhängig von Max Frame
        # self.tx_buff_ctl: [b''] = []      # PRIO, nicht von Max Frame abhängig
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

    def rx_pac_handler(self, ax25_frame: AX25Frame):
        # Monitor
        self.monitor.frame_inp(ax25_frame, 'DW')
        # MH List and Statistics
        MYHEARD.mh_inp(ax25_frame, 'DW')
        if ax25_frame.addr_uid in self.connections.keys():
            # Connection already established
            conn: AX25Conn = self.connections[ax25_frame.addr_uid]
            conn.handle_rx(ax25_frame=ax25_frame)
        else:   # Check MYStation Calls with SSID or Check incoming call without SSID
            if ax25_frame.to_call.call_str in self.my_stations \
              or ax25_frame.to_call.call in self.my_stations:
                cfg = self.stat_cfg()
                self.connections[ax25_frame.addr_uid] = AX25Conn(ax25_frame, cfg)

    def tx_pac_handler(self):
        """
        self.fetch_tx_buffer()
        frame: b''
        for frame in self.tx_buff_ctl:
            out = (bytes.fromhex('c000') + frame + bytes.fromhex('c0'))
            self.dw_sock.sendall(out)
        for frame in self.tx_buff_data:
            out = (bytes.fromhex('c000') + frame + bytes.fromhex('c0'))
            self.dw_sock.sendall(out)
        """
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            el: AX25Frame
            for el in conn.tx_buf:
                out = (bytes.fromhex('c000') + el.hexstr + bytes.fromhex('c0'))
                self.dw_sock.sendall(out)
                # Monitor
                self.monitor.frame_inp(el, 'DW')
            self.connections[k].tx_buf = []
    """   
    def fetch_tx_buffer(self):
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            el: AX25Frame
            for el in conn.tx_buf:
                # if len(self.tx_buff_data) < self.stat_cfg.port_parm_MaxPac:
                if el.ctl_byte.flag in ['I', 'UI']:
                    if el.hexstr not in self.tx_buff_data:
                        self.tx_buff_data.append(el.hexstr)
                else:
                    if el.hexstr not in self.tx_buff_ctl:
                        self.tx_buff_ctl.append(el.hexstr)
            self.connections[k].tx_buf = []
    """
    def del_connections(self):
        del_k = []
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            # S1 Frei
            if conn.zustand_exec.index == 1:
                # And empty Buffer
                # if not conn.rx_buf and not conn.tx_buf:
                if not conn.tx_buf:
                    del_k.append(k)
        for el in del_k:
            del self.connections[el]

    def run_once(self):
        while True:
            buf = b''
            try:
                buf = self.dw_sock.recv(333)
                """
                while b:
                    buf += b
                    b = self.dw_sock.recv(333)
                """
                logger.debug('Inp Buf> {}'.format(buf))
            except socket.timeout:
                pass

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
                    self.rx_pac_handler(ax25frame)
                    ############################

                # self.timer_T0 = 0
            else:
                # ######### TX #############
                # Handling
                self.tx_pac_handler()
                ############################

                ############################
                # Cleanup
                self.del_connections()
                break
            #############################################
            # Crone
            # self.cron_main()
            # self.handle_tx()  # TX #############################################################
            """
            if self.tx_buffer:
                # monitor.debug_out(self.ax_conn)
                n = 0
                while self.tx_buffer and n < self.parm_MaxBufferTX:
                    enc = ax.encode_ax25_frame(self.tx_buffer[0][0])
                    mon = ax.decode_ax25_frame(bytes.fromhex(enc))
                    enc = bytes.fromhex('c000' + enc + 'c0')
                    self.dw_sock.sendall(enc)
                    ############################
                    # Monitor TODO Better Monitor
                    monitor.monitor(mon[1], self.port_id)
                    monitor.debug_out("Out> " + str(mon))
                    self.tx_buffer = self.tx_buffer[1:]
                    n += 1
            """

        # self.dw_sock.close()
