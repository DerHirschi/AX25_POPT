import socket
import serial
import threading
import time
import crcmod

from ax25.ax25Kiss import Kiss
from ax25.ax25Connection import AX25Conn
from ax25.ax25Statistics import MH_LIST
from ax25.ax25UI_Pipe import AX25Pipe
from ax25.ax25dec_enc import AX25Frame, bytearray2hexstr, via_calls_fm_str
from fnc.ax25_fnc import reverse_uid
from ax25.ax25Error import AX25EncodingERROR, AX25DecodingERROR, AX25DeviceERROR, AX25DeviceFAIL, logger
from fnc.os_fnc import is_linux
from fnc.socket_fnc import get_ip_by_hostname
if is_linux():
    import termios

crc_x25 = crcmod.predefined.mkCrcFun('x-25')


class RxBuf:
    axip_add = '', 0
    raw_data = b''
    kiss = b''


class AX25Port(threading.Thread):
    def __init__(self, port_cfg, port_handler):
        super(AX25Port, self).__init__()
        self.ende = False
        self.device_is_running = False
        self.loop_is_running = port_handler.is_running
        self.deb_port_vars = {}

        """ self.ax25_port_handler will be set in AX25PortInit """
        # self.ax25_ports: {int: AX25Port}    # TODO Check if needed
        ############
        # CONFIG
        self.port_cfg = port_cfg
        self.port_handler = port_handler
        self.beacons = self.port_handler.beacons
        self.kiss = Kiss(self.port_cfg)
        self.port_param = self.port_cfg.parm_PortParm
        self.portname = self.port_cfg.parm_PortName
        self.port_typ = self.port_cfg.parm_PortTyp
        self.port_id = self.port_cfg.parm_PortNr
        self.my_stations = self.port_cfg.parm_StationCalls
        self.parm_TXD = self.port_cfg.parm_TXD
        self.TXD = time.time()
        """ DIGI """
        self.stupid_digi_calls = self.port_cfg.parm_StupidDigi_calls
        self.is_smart_digi = self.port_cfg.parm_isSmartDigi
        self.parm_digi_TXD = self.parm_TXD * 4  # TODO add to Settings GUI
        self.digi_TXD = time.time()
        self.digi_buf: [AX25Frame] = []
        self.UI_buf: [AX25Frame] = []
        self.connections: {str: AX25Conn} = {}
        self.pipes: {str: AX25Pipe} = {}
        """ APRS Stuff """
        self.aprs_stat = self.port_cfg.parm_aprs_station
        # self.aprs_ais = PORT_HANDLER.get_aprs_ais()
        # CONFIG ENDE
        #############
        #############
        # VARS
        # self.monitor = ax25monitor.Monitor()
        self.monitor_out = True
        self.gui = None
        self.device = None
        ##############
        # AXIP VARs
        self.own_ipAddr = ''
        # self.axip_anti_spam = {}
        try:
            self.init()
        except AX25DeviceFAIL as e:
            raise e

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

    def tx(self, frame: AX25Frame):
        pass

    def tx_multicast(self, frame: AX25Frame):
        pass

    def set_TXD(self):
        """ Internal TXD. Not Kiss TXD """
        self.TXD = time.time() + self.parm_TXD / 1000

    def set_digi_TXD(self):
        """ Internal TXD. Not Kiss TXD """
        self.digi_TXD = time.time() + self.parm_digi_TXD / 1000

    def rx_handler(self, ax25_frame: AX25Frame):
        """ Main RX-Handler """
        self.reset_ft_wait_timer(ax25_frame)
        if ax25_frame.ctl_byte.flag == 'UI':
            self.rx_UI_handler(ax25_frame=ax25_frame)
        if not ax25_frame.is_digipeated and ax25_frame.via_calls:
            if self.rx_link_handler(ax25_frame=ax25_frame):
                # Link Connection Handler
                return True
            if self.rx_simple_digi_handler(ax25_frame=ax25_frame):
                # Simple DIGI
                return True
        elif ax25_frame.is_digipeated:
            if self.rx_conn_handler(ax25_frame=ax25_frame):
                # Connections
                return True
            if self.rx_pipe_handler(ax25_frame=ax25_frame):
                # Pipe
                return True
            if self.rx_new_conn_handler(ax25_frame=ax25_frame):
                # New Connections
                return True
        return False

    def rx_link_handler(self, ax25_frame: AX25Frame):
        if ax25_frame.addr_uid in self.port_handler.link_connections.keys():
            conn = self.port_handler.link_connections[ax25_frame.addr_uid][0]
            link_call = self.port_handler.link_connections[ax25_frame.addr_uid][1]
            if link_call:
                if ax25_frame.digi_check_and_encode(call=link_call, h_bit_enc=True):
                    conn.handle_rx(ax25_frame=ax25_frame)
                    return True
            conn.handle_rx(ax25_frame=ax25_frame)
            return True
        return False

    def rx_pipe_handler(self, ax25_frame: AX25Frame):
        uid = str(ax25_frame.addr_uid)
        if uid in self.pipes.keys():
            self.pipes[uid].handle_rx(ax25_frame=ax25_frame)
            return True
        return False

    def rx_UI_handler(self, ax25_frame: AX25Frame):
        # print(f"Port RX UI Handler - aprs_ais: {self.aprs_stat.aprs_ais}")
        if self.port_handler.get_aprs_ais() is not None:
            self.port_handler.get_aprs_ais().aprs_ax25frame_rx(
                port_id=self.port_id,
                ax25_frame=ax25_frame
            )
            return True
        return False

    def rx_conn_handler(self, ax25_frame: AX25Frame):
        if ax25_frame.ctl_byte.flag == 'UI':
            return False
        uid = str(ax25_frame.addr_uid)
        if uid in self.connections.keys():
            self.connections[uid].handle_rx(ax25_frame=ax25_frame)
            return True
        return False

    def rx_new_conn_handler(self, ax25_frame: AX25Frame):
        if ax25_frame.ctl_byte.flag == 'UI':
            return False
        # New Incoming Connection
        if ax25_frame.to_call.call_str in self.my_stations:
            uid = str(ax25_frame.addr_uid)
            self.connections[uid] = AX25Conn(ax25_frame, cfg=self.port_cfg, port=self)
            # self.connections[uid].handle_rx(ax25_frame=ax25_frame)
            return True
        return False

    def rx_simple_digi_handler(self, ax25_frame: AX25Frame):
        for call in ax25_frame.via_calls:
            if call.call_str in self.stupid_digi_calls:
                if ax25_frame.digi_check_and_encode(call=call.call_str, h_bit_enc=True):
                    self.digi_buf.append(ax25_frame)
                    # self.set_digi_TXD()
                    return True
        return False

    def tx_handler(self):
        """ Main TX-Handler """
        """All Connections"""
        if self.tx_connection_buf():
            return True
        """Pipe-Tool"""
        if self.tx_pipe_buf():
            return True
        """UI Frame Buffer Like Beacons"""
        if self.tx_UI_buf():
            return True
        """DIGI"""
        if self.tx_digi_buf():
            return True
        """RX-Echo"""
        if self.tx_rxecho_buf():
            return True
        return False

    def tx_connection_buf(self):
        tr = False
        for k in self.connections.keys():
            conn: AX25Conn = self.connections[k]
            if time.time() > conn.t2 and not tr:
                snd_buf = list(conn.tx_buf_ctl) + list(conn.tx_buf_2send)
                conn.tx_buf_ctl = []
                conn.tx_buf_2send = []
                conn.REJ_is_set = False
                el: AX25Frame
                for el in snd_buf:
                    if el.digi_call and conn.is_link:
                        # TODO Just check for digi_call while encoding
                        el.digi_check_and_encode(call=el.digi_call, h_bit_enc=True)
                    else:
                        el.encode_ax25frame()
                    try:
                        self.tx(frame=el)
                        tr = True
                    except AX25DeviceFAIL as e:
                        raise e
                    # Monitor
                    self.gui_monitor(ax25frame=el, tx=True)
            else:
                tr = True
        return tr

    def tx_pipe_buf(self):
        pipe: AX25Pipe
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
                # Monitor
                self.gui_monitor(ax25frame=frame, tx=True)
            pipe.tx_frame_buf = []
        return tr

    def tx_UI_buf(self):
        tr = False
        fr: AX25Frame
        for fr in self.UI_buf:
            try:
                self.tx(frame=fr)
                tr = True
            except AX25DeviceFAIL as e:
                raise e
            # Monitor
            self.gui_monitor(ax25frame=fr, tx=True)
        self.UI_buf = []
        return tr

    def tx_digi_buf(self):
        tr = False
        if time.time() > self.digi_TXD:
            fr: AX25Frame
            for fr in self.digi_buf:
                try:
                    self.tx(frame=fr)
                    tr = True
                except AX25DeviceFAIL as e:
                    raise e
                # Monitor
                self.gui_monitor(ax25frame=fr, tx=True)
            self.digi_buf = []
        return tr

    def tx_rxecho_buf(self):
        tr = False
        # RX-Echo
        fr: AX25Frame
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
                self.gui_monitor(ax25frame=fr, tx=True)

            self.port_handler.rx_echo[self.port_id].tx_buff = []
        return tr

    def rx_echo(self, ax25_frame: AX25Frame):
        if self.gui is not None:
            if self.gui.setting_rx_echo.get():
                self.port_handler.rx_echo_input(ax_frame=ax25_frame, port_id=self.port_id)

    def cron_port_handler(self):
        """ Execute Port related Cronjob like Beacon sending"""
        self.cron_pac_handler()
        self.cron_pipes()
        self.cron_send_beacons()

    def cron_pipes(self):
        for uid in self.pipes.keys():
            self.pipes[uid].cron_exec()

    def cron_pac_handler(self):
        """ Execute Cronjob on all Connections"""
        for _k in list(self.connections.keys()):
            # if _k in self.connections.keys():
            try:    # TODO Not happy. When no more Errors delete this shit.
                self.connections[_k].exec_cron()
            except KeyError:
                logger.error(f"KeyError cron_pac_handler(): {_k}")
                print(f"KeyError cron_pac_handler(): {_k}")
                print(f"KeyError cron_pac_handler()keys:: {list(self.connections.keys())}")

    def cron_send_beacons(self):
        tr = True
        if self.gui is not None:
            if not self.gui.setting_bake.get():
                tr = False
        if tr:
            # if self.port_id in self.beacons.keys():
            beacon_tasks = self.beacons.get(self.port_id, {})
            for k in beacon_tasks.keys():
                beacon_list = beacon_tasks[k]
                # beacon: Beacon
                for beacon in beacon_list:
                    if beacon.is_enabled:
                        send_it = beacon.crone()
                        ip_fm_mh = MH_LIST.mh_get_last_ip(beacon.to_call, self.port_cfg.parm_axip_fail)
                        beacon.axip_add = ip_fm_mh
                        if self.port_typ == 'AXIP' and not self.port_cfg.parm_axip_Multicast:
                            if ip_fm_mh == ('', 0):
                                send_it = False
                        if send_it:
                            _beacon_ax25frame = beacon.encode_beacon()
                            if _beacon_ax25frame:
                                self.UI_buf.append(_beacon_ax25frame)

    def build_new_pipe(self,
                       own_call,
                       add_str,
                       cmd_pf=(False, False),
                       pid=0xf0
                       ):
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

    def del_pipe(self, pipe: AX25Pipe):
        if pipe.uid in self.pipes.keys():
            del self.pipes[pipe.uid]
            return True
        return False

    def build_new_connection(self,
                             own_call: str,
                             dest_call: str,
                             via_calls: [str],
                             axip_add: (str, int) = ('', 0),
                             link_conn=None,
                             ):

        if link_conn is None:
            link_conn = False
        if own_call not in self.my_stations and not link_conn:
            return False
        if link_conn and not via_calls:
            return False
        ax_frame = AX25Frame()
        ax_frame.from_call.call_str = own_call
        ax_frame.to_call.call_str = dest_call
        ax_frame.via_calls = list(via_calls_fm_str(' '.join(via_calls)))
        ax_frame.axip_add = axip_add

        conn = self.new_connection(ax25_frame=ax_frame)
        if not conn:
            return False
        if link_conn:
            conn.is_link_remote = True
            if conn.link_connection(link_conn):
                if link_conn.link_connection(conn):
                    return conn
            return False
        return conn

    def new_connection(self, ax25_frame: AX25Frame):
        """ New Outgoing Connection """
        ax25_frame.ctl_byte.SABMcByte()
        ax25_frame.encode_ax25frame()  # TODO Not using full encoding to get UID
        """
        while ax25_frame.addr_uid in self.connections.keys() or \
                reverse_uid(ax25_frame.addr_uid) in self.connections.keys():
        """
        while True:
            if ax25_frame.addr_uid not in self.connections.keys() and \
                    reverse_uid(ax25_frame.addr_uid) not in self.connections.keys():
                break
            if ax25_frame.addr_uid in self.connections.keys():
                if self.connections[ax25_frame.addr_uid].zustand_exec.stat_index in [0, 1]:
                    break
            if reverse_uid(ax25_frame.addr_uid) in self.connections.keys():
                if self.connections[reverse_uid(ax25_frame.addr_uid)].zustand_exec.stat_index in [0, 1]:
                    break

            logger.debug("Same UID !! {}".format(ax25_frame.addr_uid))
            ax25_frame.from_call.call_str = ''
            ax25_frame.from_call.ssid += 1
            try:
                ax25_frame.from_call.enc_call()
            except AX25EncodingERROR:
                return False
            if ax25_frame.from_call.ssid > 15:
                return False
            try:
                ax25_frame.encode_ax25frame()  # TODO Not using full encoding to get UID
            except AX25EncodingERROR:
                logger.error("AX25EncodingError: AX25Port Nr:({}): new_connection()".format(self.port_id))
                raise AX25EncodingERROR(self)
        conn = AX25Conn(ax25_frame, self.port_cfg, rx=False, port=self)
        # conn.cli.change_cli_state(1)
        self.connections[ax25_frame.addr_uid] = conn
        return conn

    def del_connections(self, conn: AX25Conn):
        logger.debug(f"del_connections: {conn.uid}\n"
              f"state: {conn.zustand_exec.stat_index}\n"
              f"conn.keys: {self.connections.keys()}\n")
        self.port_handler.del_link(conn.uid)
        if conn.uid in self.pipes.keys():
            del self.pipes[conn.uid]
        if conn.uid in self.connections.keys():
            del self.connections[conn.uid]
        if reverse_uid(conn.uid) in self.connections.keys():
            del self.connections[reverse_uid(conn.uid)]

    def send_UI_frame(self,
                      own_call,
                      add_str: str,
                      text: bytes,
                      cmd_poll=(False, False),
                      pid=0xF0
                      ):
        tmp = add_str.split(' ')
        dest_call = tmp[0].replace(' ', '')
        frame = AX25Frame()

        if len(tmp) > 1:
            vias = tmp[1:]
            frame.via_calls = list(via_calls_fm_str(' '.join(vias)))

        frame.ctl_byte.UIcByte()
        frame.ctl_byte.cmd, frame.ctl_byte.pf = cmd_poll
        if pid in frame.pid_byte.pac_types.keys():
            frame.pid_byte.pac_types[pid]()
        else:
            frame.pid_byte.text()
        frame.data = text
        frame.axip_add = MH_LIST.mh_get_last_ip(call_str=dest_call)
        frame.from_call.call_str = own_call
        frame.to_call.call_str = dest_call
        try:
            frame.encode_ax25frame()
        except AX25EncodingERROR:
            return False
        else:
            self.UI_buf.append(frame)
            return True

    def reset_ft_wait_timer(self, ax25_frame: AX25Frame):
        if ax25_frame.ctl_byte.flag in ['I', 'SABM', 'DM', 'DISC', 'REJ', 'UA', 'UI']:
            for k in self.connections.keys():
                self.connections[k].ft_reset_timer(ax25_frame.addr_uid)

    def gui_monitor(self, ax25frame: AX25Frame,  tx: bool = True):
        if self.monitor_out:
            if self.gui is not None:
                self.gui.update_monitor(
                    # monitor_frame_inp(ax25frame, self.port_cfg),
                    ax25frame,
                    conf=self.port_cfg,
                    tx=tx)

    def run(self):
        while self.loop_is_running:

            self.tasks()
        # time.sleep(0.05)
        print(f"Loop Ends Port: {self.port_id}")
        logger.info(f"Loop Ends Port: {self.port_id}")
        self.close()
        self.device = None
        self.ende = True

    def tasks(self):
        while self.loop_is_running:
            try:
                ##############################################
                buf: RxBuf = self.rx()
                ##############################################
            except AX25DeviceERROR:
                # time.sleep(0.1)
                break
            if not self.loop_is_running:
                break
            if buf is None:
                # buf = RxBuf()
                break
            if not buf.raw_data:  # RX ############
                time.sleep(0.05)
                break
            self.set_TXD()
            self.set_digi_TXD()
            ax25frame = AX25Frame()
            ax25frame.axip_add = buf.axip_add
            try:
                # Decoding
                ax25frame.decode_ax25frame(buf.raw_data)
            except AX25DecodingERROR:
                logger.error('Port:{} decoding: '.format(self.portname))
                logger.error('{}: org {}'.format(self.portname, buf.raw_data))
                logger.error('{}: hex {}'.format(self.portname, bytearray2hexstr(buf.raw_data)))
                break
            if ax25frame.validate():
                # ######### RX #############
                # MH List and Statistics
                MH_LIST.mh_inp(ax25frame, self.portname, self.port_id)
                # Monitor
                self.gui_monitor(ax25frame=ax25frame, tx=False)
                # Handling
                self.rx_handler(ax25frame)
                # RX-ECHO
                self.rx_echo(ax25_frame=ax25frame)
                # AXIP-Multicast
                if self.port_cfg.parm_axip_Multicast:
                    self.tx_multicast(frame=ax25frame)
            if self.port_cfg.parm_full_duplex:
                break

        if self.loop_is_running:
            if time.time() > self.TXD or self.port_cfg.parm_full_duplex:
                #############################################
                # Crone
                self.cron_port_handler()
                # ######### TX #############
                self.tx_handler()


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
                # ?? TODO DNS support ??
                self.device.connect(self.port_param)
                self.device_is_running = True

            except (OSError, ConnectionRefusedError, ConnectionError) as e:
                logger.error('Error. Cant connect to KISS TCP Device {}'.format(self.port_param))
                logger.error('{}'.format(e))
                # self.device.shutdown(socket.SHUT_RDWR)
                self.device.close()
                # raise AX25DeviceFAIL

            else:
                if self.kiss.is_enabled:
                    # self.device.sendall(self.kiss.device_kiss_start_1())
                    self.device.sendall(self.kiss.device_jhost())
                    # print(self.device.recv(999))
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
        if self.kiss.is_enabled and self.device is not None:
            self.device.sendall(self.kiss.set_all_parameter())

    def rx(self):
        try:
            recv_buff = self.device.recv(999)
        except socket.timeout:
            # self.device.close()
            raise AX25DeviceERROR
        except OSError:
            raise AX25DeviceERROR
        ret = RxBuf()

        if recv_buff:
            de_kiss_fr = self.kiss.de_kiss(recv_buff)
            if de_kiss_fr:
                ret.raw_data = de_kiss_fr
                return ret
        else:
            return ret

    def tx(self, frame: AX25Frame):
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
        else:
            MH_LIST.bw_mon_inp(frame, self.port_id)

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
        self.init()

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
                    logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                    raise AX25DeviceFAIL
            else:
                ret = RxBuf()
                if recv_buff:
                    de_kiss_fr = self.kiss.de_kiss(recv_buff)
                    if de_kiss_fr:  # TODO !!!! flush buffer ?
                        ret.raw_data = de_kiss_fr
                        return ret
                else:
                    return ret

    def tx(self, frame: AX25Frame):
        if self.device is None:
            try:
                # self.init()
                self._reinit()
            except AX25DeviceFAIL:
                logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
                self.close_device()
                # raise AX25DeviceFAIL
                return
        if self.device is None:
            logger.error('Error. Reinit Failed !! {}'.format(self.port_param))
            self.close_device()
            # raise AX25DeviceFAIL
            return

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
                raise AX25DeviceFAIL
        else:
            MH_LIST.bw_mon_inp(frame, self.port_id)


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
                # raise AX25DeviceFAIL

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

    def tx(self, frame: AX25Frame, no_multicast=False):
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
            else:
                MH_LIST.bw_mon_inp(frame, self.port_id)

        if self.port_cfg.parm_axip_Multicast and not no_multicast:
            self.tx_multicast(frame=frame)

    def tx_multicast(self, frame: AX25Frame):
        for axip_add in self.port_handler.multicast_ip_s:
            if axip_add != frame.axip_add:
                frame.axip_add = axip_add
                try:
                    self.tx(frame, no_multicast=True)
                except (ConnectionRefusedError, ConnectionError, socket.timeout):
                    MH_LIST.mh_ip_failed(axip_add)
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
