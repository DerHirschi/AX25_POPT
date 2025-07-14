import json
import lzma
import threading
import time
#from sys import stdout

import meshtastic
from meshtastic import tcp_interface, serial_interface
from meshtastic.protobuf import portnums_pb2
from pubsub import pub

from cfg.constant import PARAM_MAX_MON_WIDTH
from cfg.logger_config import logger
from fnc.lzhuf import LZHUF_Comp
from fnc.str_fnc import get_timestamp

MESH_DEVICE_CFG = dict(
    modem_ip            = "192.168.1.160",
    modem_serail_add    = "", #"/dev/ttyACM0",                 # /dev/ttyUSB0
    ax25_mesh_chID      = 2,                  # Meshtastic CH-ID für DL_Convers Kanal
)
NODE_INFO_FILE = 'data/meshtastic_nodeInfo.json'

class MeshDevice:
    def __init__(self):
        logger.info("Init")
        logger.info(f"Lade Node-Info-Tab aus {NODE_INFO_FILE}")
        self._node_info_tab = {}
        self._load_node_tab()
        self._cfg           = MESH_DEVICE_CFG
        self._serial_mode   = True if self._cfg.get('modem_serail_add', '') else False

        self._old_q         = {}
        self._old_q_stat    = None
        self._my_metrics    = None
        self._my_node_tab   = ''
        self._nodelist_file_timer = time.time()


        # TX ACK Msg's
        self._tx_buff       = []  # (to_id, msg)
        self._pending_acks  = {}  # Speichert requestId -> (to_id, message) für Ack-Zuordnung
        self._nacks         = []
        self._tx_thread     = None
        # RX
        self._monitor_buff: list[tuple[bool, str]]  = []
        self._ax25_rx_buff: list[bytes]             = []
        self._ax25_tx_buff: list[bytes]             = []

        self._main_thread   = threading.Thread(target=self._run_loop)
        self.is_runnig      = True
        self._interface     = None
        self._connect_to_device()

    @staticmethod
    def _on_connection_established(interface, topic=pub.AUTO_TOPIC):
        logger.info(f"Verbindung hergestellt")

    def _on_connection_lost(self, interface, topic=pub.AUTO_TOPIC):
        if not self.is_runnig:
            return
        logger.warning(f"Verbindung verloren, versuche Neuverbindung...")
        self._reconnect()

    def _run_loop(self):
        # Callback für empfangene Pakete registrieren
        logger.info("Starte Main Loop")
        while self.is_runnig:
            if self.is_runnig:
                try:
                    if self._interface is None:
                        logger.warning(f"Keine Verbindung, versuche Neuverbindung...")
                        self._reconnect()
                        continue

                    self._ax25_tx_spooler()

                    #self._mesh_tx_spooler()
                    #if not self._serial_mode:
                    #    self._interface.sendHeartbeat()

                    #print(self._interface.isConnected)
                    """
                    interfaces self._old_q != self._interface.queue:
                        logger.debug(f"Q       : {self._interface.queue.keys()}")
                        logger.debug(f"Q-Len   : {len(self._interface.queue)}")
                        self._old_q = dict(self._interface.queue)
                    interfaces self._interface.queueStatus:
                        interfaces self._interface.queueStatus != self._old_q_stat:
                            logger.debug(f"Q-Status: {self._interface.queueStatus}")
                            self._old_q_stat = self._interface.queueStatus
                    """
                    """
                    my_metrics = self._interface.getMyNodeInfo().get('deviceMetrics', {})
                    if self._my_metrics != my_metrics:
                        self._my_metrics = dict(my_metrics)
                        logger.debug(f"N-Info: {self._my_metrics}")
                    """
                    #self._nodelist_to_file()
                    time.sleep(1)

                except (BrokenPipeError, ConnectionError, OSError) as e:
                    logger.error(f"Verbindungsfehler in run_receiver: {e}")
                    self._reconnect()
                except Exception as e:
                    logger.error(f"Fehler in run_receiver: {e}")
                    # print(f"Fehler in run_receiver: {e}")

    def _connect_to_device(self):
        """Versucht, eine Verbindung zum Meshtastic-Gerät herzustellen."""
        if self._main_thread.is_alive():
            logger.error("Mainthread is alive!!")
            self.is_runnig = False
            time.sleep(2)
            if self._main_thread.is_alive():
                logger.error("Mainthread is still alive!!")
                self.close_interface()
                raise ConnectionError
        try:
            if not self._serial_mode:
                modem_ip = self._cfg.get('modem_ip', '')
                if not modem_ip:
                    logger.error("Config Error: keine Modem IP gesetzt.")
                    raise AttributeError("Config Error: keine Modem IP gesetzt.")
                logger.info(f"Verbinde mit Meshtastic-Gerät an {modem_ip}...")
                self._interface = meshtastic.tcp_interface.TCPInterface(modem_ip, )
                logger.info("Verbindung erfolgreich hergestellt.")
            else:
                modem_address = self._cfg.get('modem_serail_add', '')
                if not modem_address:
                    logger.error("Config Error: keine Modem Adresse gesetzt.")
                    raise AttributeError("Config Error: keine Modem Adresse gesetzt.")
                logger.info(f"Verbinde mit Meshtastic-Gerät an {modem_address}...")
                self._interface = meshtastic.serial_interface.SerialInterface(modem_address, )
                logger.info("Verbindung erfolgreich hergestellt.")

            try:
                #self._mesh_recv_thread = threading.Thread(target=self._run_loop)
                #self._mesh_recv_thread.start()
                self._main_thread.start()

            except Exception as e:
                logger.error(f"Fehler beim Starten des Mesh-Receivers: {e}")
                self.close_interface()
                raise e

            # Knoteninformationen ausgeben
            my_node_info        = self._interface.getMyNodeInfo()
            self._my_node_id    = my_node_info.get('user', {}).get('id', 'UNKNOWN')
            logger.info(f"Listener gestartet. Warte auf eingehende Pakete (Knoten: {self._my_node_id})...")
            self._update_node_tab()
            pub.subscribe(self._on_connection_lost, "meshtastic.connection.lost")
            pub.subscribe(self._on_connection_established, "meshtastic.connection.established")
            pub.subscribe(self._process_packet, "meshtastic.receive")

            #print(self._interface.nodes[list(self._interface.nodes.keys())[140]])
            # print(self._interface.nodes[list(self._interface.nodes.keys())[139]])
            #print(len(self._interface.nodes))
            #print(self._interface.nodes)
            #print(self._interface.getNode('24'))


        except Exception as e:
            logger.error(f"Fehler beim Verbindungsaufbau: {e}")
            self._interface = None
            raise e

    def _reconnect(self):
        """Versucht, die Verbindung zum Meshtastic-Gerät neu herzustellen."""
        logger.info(f"Versuche, Verbindung neu herzustellen...")
        try:
            if self._interface:
                if self._tx_thread:
                    n = 0
                    while self._tx_thread.is_alive():
                        logger.info(f"Warte auf TX-Thread...")
                        time.sleep(1)
                        n += 1
                        if n > 10:
                            logger.error(f"TX-Thread lässt sich nicht schließen")
                            break

                try:
                    self._interface.close()
                    n = 0
                    while self._main_thread.is_alive():
                        logger.info(f"Warte auf Main-Thread...")
                        time.sleep(1)
                        n += 1
                        if n > 10:
                            logger.error(f"Main-Thread lässt sich nicht schließen")
                            break
                except Exception as e:
                    logger.warning(f"Fehler beim Schließen der alten Verbindung: {e}")
            self._interface = None
            time.sleep(2)  # Warte kurz vor dem Neuverbinden
            self._connect_to_device()
            return True
        except Exception as e:
            logger.error(f"Neuverbindung fehlgeschlagen: {e}")
            return False

    def close_interface(self):
        logger.info("Schließe Meshtastic-Verbindung...")
        self.is_runnig = False
        time.sleep(1)
        if self._interface:
            if self._tx_thread:
                while self._tx_thread.is_alive():
                    logger.info(f"Warte auf TX-Thread...")
                    time.sleep(1)
            try:
                self._interface.close()
            except Exception as e:
                logger.error(f"Fehler beim Schließen der Meshtastic-Verbindung: {e}")
            self._interface = None
        logger.info(f"Speichere Node-Info-Tab in {NODE_INFO_FILE}")
        self._save_node_tab()

    ###############################
    # Node Tab
    def _load_node_tab(self):
        try:
            with open(NODE_INFO_FILE, "r", encoding="utf-8") as file:
                self._node_info_tab = json.load(file)
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Node-Tab: {e}")

    def _save_node_tab(self):
        with open(NODE_INFO_FILE, "w", encoding="utf-8") as file:
            json.dump(self._node_info_tab, file, ensure_ascii=False, indent=4)

    def _update_node_tab(self):
        logger.info(f"Update Node-Info-Tab aus Meshtastic-Modem Daten")
        dev_node_tab: dict = self._interface.nodes
        for k, ent in dev_node_tab.items():
            if k in self._node_info_tab:
                self._node_info_tab[k].update(dict(ent.get('user', {})))
            else:
                self._node_info_tab[k] = dict(ent.get('user', {}))

    def _nodelist_to_file(self):
        if time.time() < self._nodelist_file_timer:
            return
        self._nodelist_file_timer = time.time() + 30
        try:
            my_node_tab = self._interface.showNodes()
        except Exception as e:
            logger.error(f":{e}")
            raise e
        if my_node_tab != self._my_node_tab:
            try:
                with open("../node_list.txt", 'w') as file:
                    file.write(my_node_tab)
                    file.close()
            except Exception as e:
                logger.error(f":{e}")
            self._my_node_tab = my_node_tab

    def get_shortName(self, user_id):
        return self._node_info_tab.get(user_id, {}).get('shortName', '')

    def get_hops(self, user_id):
        return self._node_info_tab.get(user_id, {}).get('hops', '-')

    def get_myID(self):
        return self._my_node_id
    ###############################
    #
    def _process_packet(self, packet, interface):
        """Verarbeitet und gibt empfangene Pakete aus."""
        # print(packet)
        try:
            decoded = packet.get("decoded", {})
            portnum = decoded.get("portnum", "UNKNOWN")
            #print(packet)
            if portnum == "TEXT_MESSAGE_APP":
                self._process_text_msg_app(packet)
            elif portnum == "ROUTING_APP":
                self._process_routing_app(packet)
            elif portnum == "NODEINFO_APP":
                self._process_node_info_app(packet)
            #else:
            #    logger.debug(f"Ignoriere Port: {portnum}")
            self._process_hop_info(packet)

            # if hasattr(self._main_handler, 'recv_mon_fm_mesh'):
            self._recv_mon_fm_mesh(packet)


        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten: {e}")

    def _process_text_msg_app(self, packet):
        # print("TExt MSG")
        decoded     = packet.get("decoded", {})
        payload     = decoded.get("payload", b"")
        channel     = packet.get("channel", -1)
        from_id     = packet.get("fromId", packet.get("from", "UNKNOWN"))
        to_id       = packet.get("toId", packet.get("to", "UNKNOWN"))
        if channel == self._cfg.get('ax25_mesh_chID', 999):
            # Verwende shortName aus NODE_INFO_TAB, falls verfügbar
            # message = payload.decode("utf-8", errors="ignore")
            sender  = self._node_info_tab.get(from_id, {}).get('shortName', from_id)
            # formatted_message = f"{sender}: {message}"
            logger.debug(f"Textnachricht von {sender}: {payload.hex()[:10]}...")
            logger.debug(f"Payload: {payload.hex()}")
            # Nachricht an Telnet-Server senden
            self._process_data_packet(packet)
        else:
            if to_id != self._my_node_id:
                logger.debug(f"Paket nicht für eigene Node. > {to_id}")
                return
            # Private Message
            self._process_data_packet(packet)
            """
            if hasattr(self._main_handler, 'recv_msg_fm_mesh'):
                logger.debug(f"Paket für eigene Node. > {to_id}")
                self._main_handler.recv_msg_fm_mesh(from_id, payload)
            """

    def _process_routing_app(self, packet):
        decoded     = packet.get("decoded", {})
        from_id     = packet.get("fromId", packet.get("from", "UNKNOWN"))
        sender      = self._node_info_tab.get(from_id, {}).get('shortName', from_id)
        request_id  = decoded.get("requestId", 0)
        error       = decoded.get("routing", {}).get("errorReason", "UNKNOWN")
        is_ack      = decoded.get("ack", False) or (packet.get("priority") == "ACK" and error == "NONE")
        is_nak      = decoded.get("nak", False) or (error != "NONE" and error != "UNKNOWN")

        if request_id and is_ack:
            logger.info(f"Ack empfangen von {sender} für requestId {request_id}")
            # print(f"Ack empfangen von {sender} für requestId {request_id}")
            # Entferne ausstehendes Ack aus der Warteschlange
            if request_id in self._pending_acks:
                to_id, message = self._pending_acks.pop(request_id)
                logger.info(f"Bestätigtes Paket an {to_id}: {message[:10]}..., requestId {request_id}")
                #print(f"Bestätigtes Paket an {to_id}: {message}")
        elif request_id and is_nak:
            if request_id in self._pending_acks:
                self._nacks.append(request_id)
                logger.warning(
                    f"Nak empfangen von {sender} für requestId {request_id}, Fehler: {error}")
                #print(f"Nak empfangen von {sender} für requestId {request_id}, Fehler: {error}, dec: {decoded}")
                # self._pending_acks.pop(request_id)
        """
        else:
            print(f"req_id: {request_id} - is_ack: {is_ack} - isNack: {is_nak}")
            print(f"dec: {decoded} ")
            logger.debug(f"Unbekannte ROUTING_APP-Nachricht: {packet}")
        """

    def _process_node_info_app(self, packet):
        # NODEINFO_APP-Paket verarbeiten
        #from_id         = packet.get("fromId", packet.get("from", "UNKNOWN"))
        decoded         = packet.get("decoded", {})
        # node_num        = packet.get("from", 0)
        user            = decoded.get("user", {})
        node_id         = user.get("id", "N/A")
        long_name       = user.get("longName", "N/A")
        short_name      = user.get("shortName", "N/A")
        hardware_model  = user.get("hardwareModel", "N/A")
        role            = user.get("role", "N/A")
        macaddr         = user.get("macaddr", "")
        publicKey       = user.get("publicKey", "N/A")

        node_info_ent = dict(
            id=node_id,
            longName=long_name,
            shortName=short_name,
            hwModel=hardware_model,
            role=role,
            macaddr=macaddr,
            publicKey=publicKey,
        )

        if node_id in self._node_info_tab:
            self._node_info_tab[node_id].update(node_info_ent)
        else:
            self._node_info_tab[node_id] = node_info_ent

        """
        print(
            f"Knoteninfo von {from_id}:\n"
            f"                ID={node_id}\n"
            f"                LongName={long_name}\n"
            f"                ShortName={short_name}\n"
            f"                Hardware={hardware_model}\n"
            f"                Rolle={role}\n"
            f"                MAC={macaddr}\n"
            f"                publicKey={publicKey}\n"
        )
        """
        """

        logger.debug(
            f"\nKnoteninfo von {from_id}:\n"
            f"                ID={node_id}\n"
            f"                LongName={long_name}\n"
            f"                ShortName={short_name}\n"
            f"                Hardware={hardware_model}\n"
            f"                Rolle={role}\n"
            f"                MAC={macaddr}\n"
            f"                publicKey={publicKey}\n"
        )
        """

    def _process_hop_info(self, packet):
        node_id  = packet.get("fromId", "")
        hopStart = packet.get("hopStart", -1)
        hopLimit = packet.get("hopLimit", -1)
        if any((hopLimit < 0, hopStart < 0)):
            return
        if node_id not in self._node_info_tab:
            return
        self._node_info_tab[node_id]['hops'] = hopStart - hopLimit
        """
        for node_id, node_infos in self._node_info_tab.items():
            interfaces node_infos.get('hops', None) is None:
                continue
            print(f"Node: {self._node_info_tab[node_id]['shortName']}, Hops: {node_infos.get('hops', 'N/A')}")
        """
    ###########################
    #
    def _process_data_packet(self, packet: dict):
        decoded = packet.get("decoded", {})
        payload = decoded.get("payload", b"")
        #channel = packet.get("channel", -1)
        #from_id = packet.get("fromId", packet.get("from", "UNKNOWN"))
        #sender  = self._node_info_tab.get(from_id, {}).get('shortName', from_id)
        """
        try:
            # de_lzhuf = self._decomp_lzhuf(payload)
            de_lzma  = self._decomp_lzma(payload)
        except Exception as e:
            logger.error("Mesh-process_data_packet: Error decomp Packet.")
            logger.error(e)
            return
        """

        self._ax25_rx_buff.append(payload)

    #############################
    # De/Compressing
    @staticmethod
    def _decomp_lzhuf(compressed_data: bytes):
        logTag       = "_decomp_lzhuf> "
        lzhuf        = LZHUF_Comp()
        decompressed = lzhuf.decode(compressed_data)

        compressed_size     = len(compressed_data)
        decompressed_size   = len(decompressed)
        compression_ratio   = decompressed_size / compressed_size
        logger.info(logTag + f"Komprimierte:   {compressed_size} Bytes")
        logger.info(logTag + f"Dekomprimierte: {decompressed_size} Bytes")
        logger.info(logTag + f"Rate:           {compression_ratio:.2f}:1")

        return decompressed

    @staticmethod
    def _comp_lzhuf(data: bytes):
        logTag = "_comp_lzhuf> "
        logger.info(logTag + f"Komprimierte:  lzhuf")
        lzhuf  = LZHUF_Comp()
        compressed = lzhuf.decode(data)

        compressed_size   = len(compressed)
        decompressed_size = len(data)
        compression_ratio = decompressed_size / compressed_size
        logger.info(logTag + f"Komprimierte:   {compressed_size} Bytes")
        logger.info(logTag + f"Dekomprimierte: {decompressed_size} Bytes")
        logger.info(logTag + f"Rate:           {compression_ratio:.2f}:1")

        return compressed

    @staticmethod
    def _decomp_lzma(compressed_data: bytes):
        logTag       = "_decomp_lzma> "
        decompressed = lzma.decompress(compressed_data)

        compressed_size     = len(compressed_data)
        decompressed_size   = len(decompressed)
        compression_ratio   = decompressed_size / compressed_size
        logger.info(logTag + f"Komprimierte:   {compressed_size} Bytes")
        logger.info(logTag + f"Dekomprimierte: {decompressed_size} Bytes")
        logger.info(logTag + f"Rate:           {compression_ratio:.2f}:1")

        return decompressed

    @staticmethod
    def _comp_lzma(data: bytes):
        logTag = "_comp_lzma> "
        logger.info(logTag + f"Komprimierte:  lzma")
        compressed = lzma.compress(data, preset=9)

        compressed_size   = len(compressed)
        decompressed_size = len(data)
        compression_ratio = decompressed_size / compressed_size
        logger.info(logTag + f"Komprimierte:   {compressed_size} Bytes")
        logger.info(logTag + f"Dekomprimierte: {decompressed_size} Bytes")
        logger.info(logTag + f"Rate:           {compression_ratio:.2f}:1")

        return compressed

    """
    def _recv_msg_fm_mesh(self, from_id: str, payload: bytes):
        shortName = self.get_shortName(from_id)
        logger.debug(f"Mesh Nachricht von {shortName}({from_id}): {payload[:10]}...")
        # out = f"{shortName}({from_id}) > {payload.decode('UTF-8', 'ignore')}"
        #out = payload.decode('UTF-8', 'ignore')
        #out = out.replace('\r', '\n')
        #out = zeilenumbruch_lines(out, max_zeichen=100)
        #out = tk_filter_bad_chars(out)
    """


    def _recv_mon_fm_mesh(self, packet: dict):
        logger.debug(f"Recv Packet: {packet.keys()}")
        # logger.debug(f"Recv Packet: {packet}")
        channel         = packet.get("channel", -1)
        from_id         = packet.get("fromId", packet.get("from", "UNKNOWN"))
        to_id           = packet.get("toId", packet.get("to", "UNKNOWN"))
        relay_node      = packet.get("relayNode", 0)
        decoded         = packet.get("decoded", {})
        portnum         = decoded.get("portnum", "UNKNOWN")
        payload         = decoded.get("payload", b"").decode('UTF-8', 'ignore')
        position        = decoded.get("position", {})
        user            = decoded.get("user", {})
        telemetry       = decoded.get("telemetry", {})
        dev_metrics     = telemetry.get('deviceMetrics', {})
        # env_metrics     = telemetry.get('environment_metrics', {}) if telemetry.get('environment_metrics', {}) else telemetry.get('environmentMetrics', {})
        env_metrics     = telemetry.get('environmentMetrics', {})
        pow_metrics     = telemetry.get('powerMetrics', {})
        local_stats     = telemetry.get('localStats', {})
        #node_id         = user.get("id", "N/A")
        #long_name       = user.get("longName", "N/A")
        #short_name      = user.get("shortName", "N/A")
        #hardware_model  = user.get("hardwareModel", "N/A")
        #role            = user.get("role", "N/A")
        #macaddr         = user.get("macaddr", "")
        #publicKey       = user.get("publicKey", "N/A")
        request_id  = decoded.get("requestId", 0)
        error       = decoded.get("routing", {}).get("errorReason", "UNKNOWN")
        is_ack      = decoded.get("ack", False) or (packet.get("priority") == "ACK" and error == "NONE")
        is_nak      = decoded.get("nak", False) or (error != "NONE" and error != "UNKNOWN")
        #print(f"is_ack: {is_ack}, error: {decoded.get('routing', {}).get('errorReason', 'UNKNOWN')}, priority: {packet.get('priority')}")

        shortName_from  = self.get_shortName(from_id)
        shortName_to    = self.get_shortName(to_id) if to_id != '^all' else 'ALL'
        shortName_from  = shortName_from if shortName_from else from_id
        shortName_to    = shortName_to   if shortName_to   else to_id
        hops_from       = self.get_hops(from_id)
        hops_to         = self.get_hops(to_id)

        # Header
        mon_str = (f"{get_timestamp()}: {f'{shortName_from}({hops_from})'.ljust(7)}>"
                   f"{f'{shortName_to}'.rjust(4)}{f'({hops_to})' if shortName_to != 'ALL' else '   '}")
        print(f"relay_node: {relay_node}")
        #print(f"pack.keys(): {packet.keys()}")
        #print(f"pack: {packet}")
        if relay_node:
            mon_str += f" via {relay_node}"
        mon_str += f": [{portnum}]"
        if channel != -1:
            mon_str += f"({channel})"
        if any((is_ack, is_nak)):
            mon_str += f" {'ACK' if is_ack else 'NACK'}"
            if is_nak:
                mon_str += f"({error})"
            mon_str += f"[{request_id}]"
        mon_str += "\n"
        # Payload
        if portnum == 'TEXT_MESSAGE_APP':
            if payload:
                mon_str += "┌──┴─▶ Payload▽\n"
                payload_lines = payload.split('\n')
                while '' in payload_lines:
                    payload_lines.remove('')
                l_i = len(payload_lines)
                for line in payload_lines:
                    while len(line) > PARAM_MAX_MON_WIDTH:
                        mon_str += f"├►{str(line[:PARAM_MAX_MON_WIDTH])}\n"
                        line = line[PARAM_MAX_MON_WIDTH:]
                    l_i -= 1
                    if line:
                        if not l_i:
                            mon_str += f"└►{str(line)}"
                        else:
                            mon_str += f"├►{str(line)}\n"
        elif portnum == 'TELEMETRY_APP':
            if any((dev_metrics,
                    env_metrics,
                    pow_metrics,
                    local_stats)):
                if dev_metrics:
                    mon_str += "┌──┴─▶ Device-Metrics▽\n"
                    tmp = dev_metrics
                elif env_metrics:
                    mon_str += "┌──┴─▶ Environment-Metrics▽\n"
                    tmp = env_metrics
                elif pow_metrics:
                    mon_str += "┌──┴─▶ Power-Metrics▽\n"
                    tmp = pow_metrics
                elif local_stats:
                    mon_str += "┌──┴─▶ Local-Stats▽\n"
                    tmp = local_stats
                else:
                    tmp = {}

                l_i = len(tmp.keys())
                for k, param in tmp.items():
                    l_i -= 1
                    if not l_i:
                        mon_str += f"└► {str(k).ljust(19)}: {param}"
                    else:
                        mon_str += f"├► {str(k).ljust(19)}: {param}\n"
            else:
                print(f"Unbekanntes TELEMETRY_APP Paket")
                print(telemetry)
        elif portnum == 'POSITION_APP' and position:
            mon_str += "┌──┴─▶ Position▽\n"
            l_i = len(position.keys())
            for k, param in position.items():
                l_i -= 1
                if k == 'raw':
                    continue
                if not l_i:
                    mon_str += f"└► {str(k).ljust(19)}: {param}"
                else:
                    mon_str += f"├► {str(k).ljust(19)}: {param}\n"
        elif portnum == 'NODEINFO_APP' and user:
            mon_str += "┌──┴─▶ Node-Info▽\n"
            l_i = len(user.keys()) - 1
            for k, param in user.items():
                l_i -= 1
                if k in ('raw', 'publicKey'):
                    continue
                if not l_i:
                    mon_str += f"└► {str(k).ljust(19)}: {param}"
                else:
                    mon_str += f"├► {str(k).ljust(19)}: {param}\n"

        if not mon_str.endswith('\n'):
            mon_str += "\n"
        if from_id != self.get_myID():
            rx = True
            # self._process_mh(from_id)
        else:
            rx = False
        self._monitor_buff.append((rx, mon_str))

    ###########################
    # TX
    # UnProto
    def _send_packet(self, data: bytes):
        # 232 Bytes len
        # comp_data_lzhuf = self._comp_lzhuf(data)
        # comp_data_lzma  = self._comp_lzma(data)
        comp_data_lzma = data
        if len(comp_data_lzma) > 232:
            logger.error(f"MeshDevice.send_packet()> Packet to big: {len(comp_data_lzma)} Bytes > 232")
            return
        try:
            # self._interface.sendText(
            self._interface.sendData(
                data=comp_data_lzma,
                portNum=portnums_pb2.PortNum.TEXT_MESSAGE_APP,
                channelIndex=self._cfg.get('ax25_mesh_chID', 999),
                destinationId="!ffffffff"  # Broadcast an alle Knoten
            )
            logger.debug(f"Nachricht gesendet an Kanal {self._cfg.get('ax25_mesh_chID', 999)}: {len(comp_data_lzma)} Bytes")
        except (BrokenPipeError, ConnectionError, OSError) as e:
            logger.error(f"Verbindungsfehler beim Senden der Nachricht: {e}")
            self._reconnect()
            # raise e
        except Exception as e:
            logger.error(f"Fehler beim Senden der Nachricht: {e}")
            self.close_interface()
            raise e

    def _ax25_tx_spooler(self):
        if not self._ax25_tx_buff:
            return
        if self._tx_thread:
            if self._tx_thread.is_alive():
                logger.info("TX Thread Lock.. Bussy TX")
                return
        logger.info("Starte TX Thread")
        logger.debug(f"len _ax25_tx_buff: {len(self._ax25_tx_buff)}")
        self._tx_thread     = threading.Thread(target=self._send_packet, args=(self._ax25_tx_buff[0], ))
        self._tx_thread.start()
        self._ax25_tx_buff  = self._ax25_tx_buff[1:]
        # self._mesh_device.send_packet_to(msg, to_id=to_id)
    #############################
    # Proto
    def _send_packet_to(self, message: bytes, to_id: str, ack=True, re_send=True):
        # 220 Bytes len
        try:

            # Sende Nachricht mit wantAck=True
            hops   = self._node_info_tab.get(to_id, {}).get('hops', None)
            if hops is not None:
                hops += 1
                hops = min(hops, 7)
            packet = self._interface.sendData(
                data=message,
                destinationId=to_id,
                portNum=portnums_pb2.PortNum.TEXT_MESSAGE_APP,
                wantAck=ack,
                hopLimit=hops
                # wantResponse=wantResponse,
                # onResponse=onResponse,
                # channelIndex=channelIndex,
            )

            logger.debug(f"Nachricht gesendet an {to_id}: {message}, requestId: {packet.id}")
            # print(f"Nachricht gesendet an {to_id}: {message}, requestId: {packet.id}")
            if ack:
                # Speichere requestId für spätere Zuordnung
                self._pending_acks[packet.id] = (to_id, message)
                logger.debug(f"Warte auf Ack von {to_id} (Timeout: 60s)...")
                is_ack = self._waitForAckNak(packet.id, timeout=60)
                if is_ack:
                    logger.info(f"Ack erfolgreich empfangen von {to_id} (waitForAckNak), requestId: {packet.id}")
                    # print(f"Ack erfolgreich empfangen von {to_id} (waitForAckNak)")
                    self._pending_acks.pop(packet.id, None)  # Entferne, falls bereits verarbeitet
                    return True
                else:
                    logger.warning(f"Kein Ack empfangen (Nak oder Timeout) von {to_id}, requestId: {packet.id}")
                    # print(f"Kein Ack empfangen (Nak oder Timeout) von {to_id}")
                    if re_send:
                        logger.info(f"Versuche Paket erneut zu senden. {to_id}, requestId: {packet.id}")
                        self._pending_acks.pop(packet.id, None)  # Entferne, falls bereits verarbeitet
                        return self._send_packet_to(message, to_id, re_send=False)
                    return False
            return True
        except (BrokenPipeError, ConnectionError, OSError) as e:
            logger.error(f"Verbindungsfehler beim Senden der Nachricht: {e}")
            self._reconnect()
            raise e
        except Exception as e:
            logger.error(f"Fehler beim Senden der Nachricht: {e}")
            raise e

    def add_to_tx_buff(self, to_id: str, message: bytes):
        self._tx_buff.append((
            to_id,
            message
        ))

    def _mesh_tx_spooler(self):
        if not self._tx_buff:
            return
        if self._tx_thread:
            if self._tx_thread.is_alive():
                print("TX Thread Lock")
                return
        to_id, msg    = self._tx_buff[0]
        self._tx_buff = self._tx_buff[1:]
        self._tx_thread = threading.Thread(target=self._send_packet_to, args=(msg, to_id))
        self._tx_thread.start()
        # self._mesh_device.send_packet_to(msg, to_id=to_id)

    def _waitForAckNak(self, packet_id, timeout=30):
        tick = 0
        while (tick < timeout) and packet_id in self._pending_acks and self.is_runnig:
            if packet_id in self._nacks:
                self._nacks.remove(packet_id)
                return False
            time.sleep(1)
            tick += 1
        return not packet_id in self._pending_acks

    ################################
    # AX25 Buffer
    def get_ax25_packet_fm_buff(self):
        if not self._ax25_rx_buff:
            return b''
        ret_pack = self._ax25_rx_buff[0]
        self._ax25_rx_buff = self._ax25_rx_buff[1:]
        return ret_pack

    def send_ax25_packet(self, ax25_packet: bytes):
        if ax25_packet in self._ax25_tx_buff:
            logger.warning("Paket ist bereits im TX-Buffer und noch nicht gesendet.. Überspringe..")
            return
        self._ax25_tx_buff.append(ax25_packet)

