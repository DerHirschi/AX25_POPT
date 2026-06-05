import threading
import time

from ax25.ax25Error import AX25DeviceFAIL
from ax25.ax25_ports import AX25DeviceTAB
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab

class RxEchoVars(object):
    def __init__(self, port_id: int):
        self.port_id = port_id
        self.rx_ports: {int: [str]} = {}
        self.tx_ports: {int: [str]} = {}
        self.tx_buff = []

class PortManager:
    def __init__(self, popt_handler):
        logger.info("PortManager: Init")
        self._popt_handler  = popt_handler
        """ PoPT Ports """
        self.ax25_ports         = {}
        self.rx_echo            = {}
        self.rx_echo_on         = False
        self._glb_port_blocking = 1
        """ Thread Garbage Collector """
        self._thread_manager    = popt_handler.thread_manager

    #@property
    #def _is_running(self):
    #    return self._popt_handler.is_running
    # =================================
    # Init
    def init_port(self, port_id: int):
        logger.info("PortManager: Initialisiere Port: {}".format(port_id))
        if port_id in self.ax25_ports.keys():
            port = self.ax25_ports[port_id]
            if hasattr(port, 'ende'):
                if not port.ende:
                    logger.error('PortManager: Could not initialise Port {}. Port already in use'.format(port_id))
                    if hasattr(self._popt_handler, 'api'):
                        self._popt_handler.api.sysmsg_to_gui(get_strTab('port_in_use', POPT_CFG.get_guiCFG_language()).format(port_id))
                    return False
                del self.ax25_ports[port_id]
        ##########
        # Init CFG
        new_cfg = POPT_CFG.get_port_CFG_fm_id(port_id=port_id)
        if not new_cfg:
            logger.info(f'PortManager: Port {port_id} disabled.')
            return False
        if new_cfg.get('parm_PortTyp', '') not in AX25DeviceTAB.keys():
            logger.info(f'PortManager: Port {port_id} disabled.')
            return False
        #########################
        # Init Port/Device
        try:
            temp = AX25DeviceTAB[new_cfg.get('parm_PortTyp', '')](int(port_id), self._popt_handler)
        except AX25DeviceFAIL as e:
            if hasattr(self._popt_handler, 'api'):
                self._popt_handler.api.sysmsg_to_gui(get_strTab('port_not_init', POPT_CFG.get_guiCFG_language()).format(port_id))
            logger.error(f'PortManager: Could not initialise Port {port_id}. {e}')
            return False
        #####################################################
        # Start Port/Device Thread if TNC Multiport Master
        if temp.is_multi_ch_slave():
            """ TNC Multiport Slave """
            logger.info(f'PortManager: Port {port_id} is TNC Multiport Slave.')
        else:
            th_name = f"tasker_port-{port_id}"
            th = threading.Thread(target=temp.port_tasker, name=th_name)
            if not self._thread_manager.add_thread(th):
                logger.error(f'PortManager: Could not start Port-Tasker Thread {port_id} !')
                temp.close()
                return False
        ###########################################
        # Check
        if not temp.device_is_running:
            logger.error(f'PortManager: Could not initialise Port {port_id}. Device not running.')
            if hasattr(self._popt_handler, 'api'):
                self._popt_handler.api.sysmsg_to_gui(get_strTab('port_not_init', POPT_CFG.get_guiCFG_language()).format(port_id))
            temp.close()
            del temp
            return False
        ######################################
        # Gather all Ports in dict: ax25_ports
        self.ax25_ports[port_id]    = temp
        self.rx_echo[port_id]       = RxEchoVars(port_id) # TODO Cleanup / OPT
        """ Pipe Tool """
        self._popt_handler.pipe_manager.pipeTool_init_by_port(port_id)
        if hasattr(self._popt_handler, 'api'):
            self._popt_handler.api.sysmsg_to_gui(get_strTab('port_init', POPT_CFG.get_guiCFG_language()).format(port_id))
        logger.info(f"PortManager: Port {port_id} Typ: {new_cfg.get('parm_PortTyp', '')} erfolgreich initialisiert.")
        return True

    def reinit_port(self, port_id: int):
        thread_name = f"reinit_port-{port_id}"
        reinit_th = threading.Thread(target=self._reinit_port_th,
                                     args=(port_id, ),
                                     name=thread_name)
        if not self._thread_manager.add_thread(reinit_th):
            logger.error(
                f"PortManager: Reinit Port {port_id}. Can't start Reinit Thread")
            return
        self._popt_handler.api.set_diesel()

    def _reinit_port_th(self, port_id: int):
        if hasattr(self._popt_handler, 'api'):
            self._popt_handler.api.sysmsg_to_gui(get_strTab('port_reinit', POPT_CFG.get_guiCFG_language()).format(port_id))
        logger.info(f"PortManager: Reinit Port {port_id}")
        #self.disco_conn_fm_port(port_id)
        self.close_port(port_id)
        time.sleep(1)  # Cooldown for Device
        if not self.init_port(port_id=port_id):
            return
        try:
            port = self.ax25_ports[port_id]
            port.set_block_incoming_conn(0)
        except Exception as ex:
            logger.error(f"PortManager: Error Reinit port: {ex}")
        if hasattr(self._popt_handler, 'pipe_manager'):
            self._popt_handler.pipe_manager.pipeTool_init_by_port(port_id)
        ##########################
        # Pipe-Tool Init

    # =================================
    # Close
    def close_port(self, port_id: int):
        # self.sysmsg_to_gui(get_strTab('close_port', POPT_CFG.get_guiCFG_language()).format(port_id))
        # self.sysmsg_to_gui('Info: Versuche Port {} zu schließen.'.format(port_id))
        logger.info('PortManager: Versuche Port {} zu schließen.'.format(port_id))
        if port_id in list(self.rx_echo.keys()):
            del self.rx_echo[port_id]
        if port_id in list(self.ax25_ports.keys()):
            self._popt_handler.pipe_manager.close_pipes_by_port(port_id)
            port = self.ax25_ports[port_id]
            if port.connections:
                port.disco_all_conns()
                time.sleep(1)
            port.close()

            while not port.ende:
                logger.debug(f"PortManager: Warte auf Port {port_id}")
                time.sleep(0.5)
                port.close()

            if port_id in list(self.ax25_ports.keys()):
                del self.ax25_ports[port_id]
            # del port
        # self.sysmsg_to_gui(get_strTab('port_closed', POPT_CFG.get_guiCFG_language()).format(port_id))
        #self.sysmsg_to_gui('Info: Port {} erfolgreich geschlossen.'.format(port_id))
        logger.info('PortManager: Port {} erfolgreich geschlossen.'.format(port_id))

    def close_all_ports(self):
        for k in list(self.ax25_ports.keys()):
            logger.info(f"PortManager: Closing Port {k}")
            self._popt_handler.api.sysmsg_to_gui(f"Closing Port {k}")
            self.close_port(k)

    """
    def reinit_all_ports(self):
        self.sysmsg_to_gui(get_strTab('all_port_reinit', POPT_CFG.get_guiCFG_language()))
        logger.info("PortManager: Reinit all Ports")
        for port_id in list(self.ax25_ports.keys()):
            self.close_port(port_id=port_id)
        time.sleep(1)  # Cooldown for Device
        for port_id in range(MAX_PORTS):  # Max Ports
            self._init_port(port_id=port_id)
        ##########################
        # Pipe-Tool Init
        self.set_diesel()
    """
    """
    def set_kiss_param_all_ports(self):
        for port_id, port in self.ax25_ports.items():
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_id)
            if port_cfg.get('parm_kiss_is_on', True):
                # time.sleep(1)
                self._popt_handler.api.sysmsg_to_gui(get_strTab('send_kiss_parm', POPT_CFG.get_guiCFG_language()).format(port_id))
                try:
                    port.set_kiss_parm()
                except AX25DeviceFAIL as e:
                    logger.error(f"PortManager: set_kiss_parm() Port: {port_id} - {e}")
                    pass
    """

    # =================================
    # Connection Block
    def unblock_all_ports(self):
        for port_id, port in self.ax25_ports.items():
            if hasattr(port, 'set_block_incoming_conn'):
                port.set_block_incoming_conn(0)
        self._glb_port_blocking = 0

    def block_all_ports(self, state=0):
        # 0 = unblock incoming
        # 1 = ignore incoming
        # 2 = reject incoming
        # 3 = reject incoming with msg
        for port_id, port in self.ax25_ports.items():
            if hasattr(port, 'set_block_incoming_conn'):
                port.set_block_incoming_conn(state)
        self._glb_port_blocking = state

    def get_glb_port_blocking(self):
        return self._glb_port_blocking
    # =================================
    # Getta
    def get_all_ports(self):
        ret = {}
        for port_id, port in self.ax25_ports.items():
            if not port:
                continue
            prim_port = port.get_dualPort_primary()
            if prim_port:
                port = prim_port
                port_id = port.port_id
            if port_id not in ret.keys():
                ret[port_id] = port
        return ret

    def get_all_ports_f_cfg(self):
        return dict(self.ax25_ports)

    def get_port_by_id(self, port_id: int):
        return self.ax25_ports.get(port_id, None)

    def get_port_by_index(self, index: int):
        if index in self.ax25_ports.keys():
            port = self.ax25_ports[index]
            if not port.is_dualPort():
                return port
            else:
                return port.get_dualPort_primary()
        return None

    # == Multiport TNC
    def get_multi_ch_master_ports(self):
        ret = {}
        for port_id, port in self.ax25_ports.items():
            if hasattr(port, 'is_multi_ch_tnc') and hasattr(port, 'is_multi_ch_master'):
                if port.is_multi_ch_tnc() and port.is_multi_ch_master():
                    ret[port_id] = port
        return ret

    def is_multiport_slave(self, port_id: int):
        port = self.ax25_ports.get(port_id, None)
        if hasattr(port, 'is_multi_ch_slave'):
            return port.is_multi_ch_slave()
        return False

    # =================================
    # Dual Port
    def set_dualPort_fm_cfg(self):
        dualPort_cfg = POPT_CFG.get_dualPort_CFG()
        # print(f"dualPort CFG: {dualPort_cfg}")
        for port_id in self.ax25_ports.keys():
            self.ax25_ports[port_id].reset_dualPort()
        for k in dualPort_cfg.keys():
            cfg = dualPort_cfg.get(k, {})
            if cfg:
                prim_port_id = cfg.get('primary_port_id', -1)
                sec_port_id = cfg.get('secondary_port_id', -1)
                if not any((
                    bool(prim_port_id == -1),
                    bool(sec_port_id == -1),
                    bool(sec_port_id == prim_port_id),
                    bool(prim_port_id not in self.ax25_ports.keys()),
                    bool(sec_port_id not in self.ax25_ports.keys()),
                )):
                    self._set_dualPort_PH(cfg)

    def _set_dualPort_PH(self, conf: dict):
        if not conf:
            return False
        primary_port = self.ax25_ports.get(conf.get('primary_port_id', -1), None)
        secondary_port = self.ax25_ports.get(conf.get('secondary_port_id', -1), None)
        if not hasattr(secondary_port, 'set_dualPort'):
            return False
        if hasattr(primary_port, 'set_dualPort'):
            return primary_port.set_dualPort(conf, secondary_port)
        return False

    def get_all_dualPorts_primary(self):
        # Get all Primary Dual Ports
        ret = {}
        all_ports = self.get_all_ports()
        for port_id in list(all_ports.keys()):
            port = all_ports[port_id]
            if port:
                if port.is_dualPort_primary():
                    ret[port_id] = port
        return ret

    def get_dualPort_primary_PH(self, port_id):
        port = self.ax25_ports.get(port_id, None)
        if port:
            return port.get_dualPort_primary()
        return None

    # =================================
    # RX-ECHO Handling
    def rx_echo_input(self, ax_frame, receiving_port_id):
        """Opt by Grok3-AI"""
        from_call = ax_frame.from_call.call_str
        for target_port_id in self.rx_echo.keys():
            if target_port_id != receiving_port_id:
                rx_echo_var = self.rx_echo[target_port_id]
                if receiving_port_id in rx_echo_var.rx_ports:
                    callsign_list = rx_echo_var.rx_ports[receiving_port_id]
                    # print(callsign_list)
                    if not callsign_list or from_call in callsign_list:
                        logger.debug("PortManager: " +
                            f"RX-Echo: Forwarding frame from {from_call} on port {receiving_port_id} to port {target_port_id}")
                        rx_echo_var.tx_buff.append(ax_frame)

    ##################################
    # DIGI
    """
    def get_all_digiConn(self):
        ret = {}
        for port_id, port in self.ax25_ports.items():
            if port:
                all_digi_conn = port.get_digi_conn()
                for conn_key, conn in all_digi_conn.items():
                    if conn_key not in ret:
                        ret[conn_key] = conn
                    else:
                        # print(f"!! Digi-Connection {conn_key} on Port {port_id} has same UID: {conn.uid}")
                        logger.warning(f"!! Digi-Connection {conn_key} on Port {port_id} has same UID: {conn.uid}")
                        # conn.ch_index += 1
        return ret
    """
