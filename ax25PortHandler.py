import socket
from ax25dec_enc import AX25Frame
import monitor

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


class DevDirewolf(object):
    def __init__(self):
        self.dw_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.address = ('192.168.178.152', 8001)
        self.monitor = monitor.Monitor()
        self.connections = {
            # 'addrss_str_id': ConnObj
        }
        try:
            self.dw_sock.connect(self.address)
            self.dw_sock.settimeout(1.0)
            print(self.dw_sock.gettimeout())
        except (OSError, ConnectionRefusedError, ConnectionError) as e:
            pass
            logger.error('Error. Cant connect to Direwolf {}'.format(self.address))
            logger.error('{}'.format(e))

    def run_loop(self):
        while True:
            try:
                buf = self.dw_sock.recv(333)
                logger.debug('Inp Buf> {}'.format(buf))
            except socket.timeout:
                break

            if buf:  # RX ############
                # TODO self.set_t0()
                e = None
                ax25frame = AX25Frame()
                try:
                    ax25frame.decode(buf)
                except IndexError as e:
                    logger.error('DW.decoding: {}'.format(e))
                ############################
                # Monitor
                if e is None:
                    self.monitor.frame_inp(ax25frame, 'DW')
                # decode_inp = ax.decode_ax25_frame(b)
                # if dekiss_inp:
                # self.handle_rx(dekiss_inp)
                ############################
                # Monitor TODO Better Monitor
                # logger.info(dekiss_inp[1])
                ############################
                # MH List and Statistics
                #mh.mh_inp(dekiss_inp, self.port_id)
                self.timer_T0 = 0
            else:
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
