from ax25.ax25_util.ax25monitor import cli_monitor_frame_inp
from cfg.logger_config import logger
from classes.CLbuffers import LockedDict, ListBuffer



class CliMonitorManager:
    def __init__(self):
        self._log_tag = "CLI-Mon-Manager: "
        # ==================
        self._subscriber = LockedDict()
        self._mon_buffer = ListBuffer()

    # ==============================================
    # Tasker called fm PoPT-Core
    def tasker(self):
        if not self._subscriber or self._mon_buffer.is_empty:
            return

        while not self._mon_buffer.is_empty:
            packet = self._mon_buffer.buffer_read
            port_id   = packet.get('port', -1)
            from_call = packet.get('from_call_str', "")
            to_call   = packet.get('to_call_str', "")
            via_calls = packet.get('via_calls_str', [])
            for uid, data in dict(self._subscriber).items():
                connection, mon_cfg = data
                cfg_port  = mon_cfg.get('port_ids', [])
                cfg_calls = mon_cfg.get('filter_calls', [])
                cfg_excl  = mon_cfg.get('filter_exclude', False)
                #cfg_own   = mon_cfg.get('filter_own', True)
                if cfg_port and port_id not in cfg_port:
                    continue
                if cfg_calls:
                    if cfg_excl:
                        if from_call in cfg_calls:
                            continue
                        if to_call in cfg_calls:
                            continue
                        tr = False
                        for via_call in via_calls:
                            if via_call in cfg_calls:
                                tr = True
                                break
                        if tr:
                            continue
                    else:
                        tr = False
                        for via_call in via_calls:
                            if via_call in cfg_calls:
                                tr = True
                                break
                        if (from_call not in cfg_calls
                                and to_call not in cfg_calls
                                and not tr):
                            continue
                # ==================
                # Own Packet Filter TODO

                # ==================
                # Send it !!


                try:
                    encoding = connection.cli.cli_encoding
                    flag = f"{'TX' if packet.get('tx', True) else 'RX'}:{port_id}"
                    mon_str = cli_monitor_frame_inp(packet, dict(
                        port_name=flag,
                        distance=True,
                        decoding=encoding[0],
                    ))
                    connection.cli.send_output(mon_str, env_vars=False)
                except AttributeError:
                    logger.warning(self._log_tag + "tasker - AttributeError connection.cli.send_output")
                    if not self.del_subscriber(connection):
                        logger.warning(self._log_tag + "tasker - can't del subscriber")
                        del self._subscriber[uid]
                        logger.info(self._log_tag + "tasker - subscriber deleted by tasker")

    # ==============================================
    # Monitor Buffer
    def add_mon_to_buffer(self, ax25frame_conf: dict):
        if not self._subscriber:
            return
        self._mon_buffer.buffer_write(dict(ax25frame_conf))


    # ==============================================
    # Subscriber / Members / Connections
    def add_subscriber(self, connection, mon_cfg: dict):

        if not hasattr(connection, "uid"):
            logger.error(self._log_tag + "add_subscriber - AttributeError connection.uid")
            return False

        uid = connection.uid

        if uid in self._subscriber:
            logger.warning(self._log_tag + f"add_subscriber - uid({uid}) already in self._subscriber")

        self._subscriber[uid] = connection, mon_cfg
        return True

    def del_subscriber(self, connection):
        if not hasattr(connection, "uid"):
            logger.error(self._log_tag + "del_subscriber - AttributeError connection.uid")
            return False

        uid = connection.uid
        if uid not in self._subscriber:
            logger.warning(self._log_tag + f"del_subscriber - uid({uid}) not in self._subscriber")
            return False

        del self._subscriber[uid]
        return True

    # ==============================================

