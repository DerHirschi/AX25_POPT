from ax25.ax25_ports.ax25Port_Classes import RxBuf
from cfg.constant import MULTI_CH_TNC_DEV
from cfg.logger_config import logger
from classes.CLbuffers import LockedDict


class MultiChannelTNC:
    def __init__(self, ax25port, popt_handler):
        self._my_port       = ax25port
        self._popt_handler  = popt_handler
        self._port_cfg      = self._my_port.port_get_port_cfg()
        # =============================
        port_id              = self._my_port.port_id
        self.tnc_channel     = self._my_port.tnc_channel
        self.is_multi_ch_tnc = self._port_cfg.get('parm_kiss_multi_ch', False)
        self._logTag         = f"Port {port_id}-MultiCH({self.tnc_channel}): "

        # =============================
        self._multi_ch_slave_ports = LockedDict()
        self.multi_ch_master_port  = None
        self.is_multi_ch_tnc       = (self.is_multi_ch_tnc and
                                self._my_port.port_typ in MULTI_CH_TNC_DEV)
        self.is_multi_ch_slave     = (self.is_multi_ch_tnc and
                                  self._port_cfg.get('parm_kiss_multi_master', -1) != -1)


    # =========================================
    # Init
    def init_multi_channel_tnc(self):
        multi_ch_master_id = self._port_cfg.get('parm_kiss_multi_master', -1)
        if multi_ch_master_id != self._my_port.port_id and multi_ch_master_id != -1:
            """ Init Slave Port """
            master_port = self._popt_handler.get_port_by_index(multi_ch_master_id)
            if not hasattr(master_port, 'device_is_running'):
                return False
            if not master_port.device_is_running or master_port.ende:
                return False
            self.multi_ch_master_port       = master_port
            self._my_port.device_is_running = master_port.device_is_running
            self._my_port.device            = master_port.device
            self.multi_ch_master_port.multi_ch_tnc.init_multi_channel_slave(self.tnc_channel, self._my_port)
            if self._port_cfg.get('parm_set_kiss_param', True):
                self._my_port.set_kiss_parm()
            return True
        return False

    def init_multi_channel_slave(self, tnc_channel: int, slave_port):
        if tnc_channel in self._multi_ch_slave_ports:
            logger.error(self._logTag + f"init_multi_channel_slave Channel ({tnc_channel}) already in multi_ch_slave_ports")
            return
        if tnc_channel == self.tnc_channel:
            logger.error(self._logTag + f"init_multi_channel_slave Slave Channel ({tnc_channel}) is same as Master Channel!")
            return
        if not slave_port.device_is_running or slave_port.ende:
            logger.error(self._logTag + f"init_multi_channel_slave Slave Channel ({tnc_channel}) is not running")
            return
        self._multi_ch_slave_ports[tnc_channel] = slave_port



    # =========================================
    # Tasker
    def multi_ch_slave_tasks(self):
        """ Master Port calls all M-Ch Tasks """
        if not self.is_multi_ch_tnc or self.is_multi_ch_slave:
            return
        for port_id, slave_port in self._multi_ch_slave_ports.items():
            if hasattr(slave_port, 'task_multi_ch_slave'):
                slave_port.task_multi_ch_slave()
                continue
            logger.warning(self._logTag + f"Tasker: AttributeError for Slave Port {port_id} !")
            logger.warning(self._logTag + f"Tasker: Slave Port {port_id} will be disabled...")
            self.remove_slave_port(port_id)
    # =========================================
    # TX
    def multi_ch_tx(self, ax25frame):
        if not self.is_multi_ch_slave:
            return False
        if not hasattr(self.multi_ch_master_port, 'tx_out'):
            logger.error(self._logTag + f"Master Port (TNC-Ch: {self.tnc_channel})not available")
            return True
        self.multi_ch_master_port.tx_out(ax25frame, self.tnc_channel)
        return True
    
    # =========================================
    # RX
    def multi_ch_rx(self, rx_buffer: RxBuf):
        if not self.is_multi_ch_slave:
            return False
        tnc_ch     = rx_buffer.tnc_channel
        slave_port = self._multi_ch_slave_ports.get(tnc_ch, None)
        if hasattr(slave_port, 'multi_ch_process_rx_buf'):
            slave_port.multi_ch_process_rx_buf(rx_buffer)
            return True
        logger.error(self._logTag + f"Slave Port (TNC-Ch: {tnc_ch}) not available")
        return True
    
    # =========================================
    # Slave Port Management
    def remove_slave_port(self, port_id: int):
        if port_id not in self._multi_ch_slave_ports:
            logger.warning(self._logTag + f"Can't remove Slave Port ({port_id}). Not in _multi_ch_slave_ports.")
            return
        del self._multi_ch_slave_ports[port_id]

    # =========================================
    # Close
    def multi_ch_close_master(self):
        """ Called fm Slave Port.close() """
        if not self.is_multi_ch_slave:
            return
        if hasattr(self.multi_ch_master_port, 'remove_slave_port'):
            self.multi_ch_master_port.remove_slave_port(self._my_port.port_id)
            return
        logger.error(self._logTag + f"Close Master Port AttributeError")

    def multi_ch_close_slaves(self):
        """ Called fm Master Port.close() """
        if self.is_multi_ch_slave:
            return False

        for port_id, slave_port in dict(self._multi_ch_slave_ports).items():
            if hasattr(slave_port, 'close'):
                slave_port.close()
                logger.info(self._logTag + f"Close Slave Port ({port_id}), done.")
                if port_id in self._multi_ch_slave_ports:
                    logger.warning(self._logTag + f"Slave Port ({port_id}) still in Slave Tab.")
                continue
            logger.warning(self._logTag + f"Close Slave Port ({port_id}) AttributeError")
        return True
