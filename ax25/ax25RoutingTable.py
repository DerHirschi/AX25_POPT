"""By Grok3-AI"""
import time
from cfg.logger_config import logger

class RoutingTable:
    """
    Globale Routingtabelle zur Analyse von NET/ROM- und INP-Daten (Layer-3).
    Speichert Knoten und Verbindungen mit port-spezifischen Metriken.
    Für Analysezwecke optimiert, aber erweiterbar für Layer-4.
    """
    def __init__(self):
        self.table = {
            'nodes': {},       # Knoten: Callsign -> Informationen
            'connections': {}  # Verbindungen: (from_call, to_call) -> Liste von Einträgen
        }
        self.max_history = 100  # Maximale Anzahl gespeicherter Frames pro Knoten

    def update(self, ax25frame_cfg: dict):
        """
        Aktualisiert die Tabelle mit dekodierten Daten.
        """
        netRom_cfg = ax25frame_cfg.get('netrom_cfg', {})
        if not netRom_cfg:
            return
        current_time    = time.time()
        port_id         = ax25frame_cfg.get('port_id', -1)
        digi_path       = ax25frame_cfg.get('digi_path', [])

        # UI-Frames (NET/ROM Nachbarinformationen)
        if 'node_call' in netRom_cfg:
            node_call = netRom_cfg['node_call']
            if node_call not in self.table['nodes']:
                self.table['nodes'][node_call] = {
                    'alias': netRom_cfg.get('node_id', ''),
                    'ip': netRom_cfg.get('ip', ''),
                    'protocol': 'NET/ROM',
                    'ports': {port_id: {'digi_path': digi_path, 'last_seen': current_time}},
                    'first_seen': current_time,
                    'last_seen': current_time,
                    'info_history': [netRom_cfg]
                }
            else:
                node = self.table['nodes'][node_call]
                node['alias'] = netRom_cfg.get('node_id', node['alias'])
                node['ip'] = netRom_cfg.get('ip', node['ip'])
                node['ports'][port_id] = {'digi_path': digi_path, 'last_seen': current_time}
                node['last_seen'] = current_time
                node['info_history'].append(netRom_cfg)
                if len(node['info_history']) > self.max_history:
                    node['info_history'] = node['info_history'][-self.max_history:]

            neighbors = netRom_cfg.get('node_nb_list', {})
            for neighbor in neighbors.values():
                nb_call = neighbor['best_neighbor_call']
                key = (node_call, nb_call)
                if key not in self.table['connections']:
                    self.table['connections'][key] = []
                self.table['connections'][key].append({
                    'type': 'neighbor',
                    'metrics': {
                        'quality': neighbor.get('qual', 0),
                        'rtt': ax25frame_cfg.get('rtt', 0),
                        'port_id': port_id,
                        'digi_path': digi_path
                    },
                    'timestamp': current_time
                })

        # I-Frames (INP Route Records)
        elif 'inp_route' in netRom_cfg:
            route = netRom_cfg['inp_route']
            for i, (node_call, hop_counter, marker) in enumerate(route):
                if node_call not in self.table['nodes']:
                    self.table['nodes'][node_call] = {
                        'alias': '',
                        'ip': '',
                        'protocol': 'INP',
                        'ports': {port_id: {'digi_path': digi_path, 'last_seen': current_time}},
                        'first_seen': current_time,
                        'last_seen': current_time,
                        'info_history': [netRom_cfg]
                    }
                else:
                    node = self.table['nodes'][node_call]
                    node['ports'][port_id] = {'digi_path': digi_path, 'last_seen': current_time}
                    node['last_seen'] = current_time
                    node['info_history'].append(netRom_cfg)
                    if len(node['info_history']) > self.max_history:
                        node['info_history'] = node['info_history'][-self.max_history:]

            for i in range(len(route) - 1):
                from_call = route[i][0]
                to_call = route[i + 1][0]
                hop_counter = route[i + 1][1]
                marker = route[i + 1][2]
                key = (from_call, to_call)
                if key not in self.table['connections']:
                    self.table['connections'][key] = []
                self.table['connections'][key].append({
                    'type': 'route',
                    'metrics': {
                        'hop_counter': hop_counter,
                        'marker': marker,
                        'ttl': netRom_cfg.get('time_to_live', 255),
                        'ci_id': f"{netRom_cfg.get('cir_index', 0):02x}/{netRom_cfg.get('cir_ID', 0):02x}",
                        'port_id': port_id,
                        'digi_path': digi_path
                    },
                    'timestamp': current_time
                })

        # RIF/RIP-Frames
        elif 'rif_data' in netRom_cfg:
            for rip in netRom_cfg['rif_data']:
                rif = rip['rif_data']
                call = rif.get('call', 'INVALID')
                if call == 'INVALID':
                    continue
                if call not in self.table['nodes']:
                    self.table['nodes'][call] = {
                        'alias': rif.get('alias', ''),
                        'ip': rif.get('ip', ''),
                        'protocol': 'RIF/RIP',
                        'ports': {port_id: {'digi_path': digi_path, 'last_seen': current_time}},
                        'first_seen': current_time,
                        'last_seen': current_time,
                        'info_history': [netRom_cfg]
                    }
                else:
                    node = self.table['nodes'][call]
                    node['alias'] = rif.get('alias', node['alias'])
                    node['ip'] = rif.get('ip', node['ip'])
                    node['ports'][port_id] = {'digi_path': digi_path, 'last_seen': current_time}
                    node['last_seen'] = current_time
                    node['info_history'].append(netRom_cfg)
                    if len(node['info_history']) > self.max_history:
                        node['info_history'] = node['info_history'][-self.max_history:]

                from_call = netRom_cfg.get('call_from', '')
                key = (from_call, call)
                if key not in self.table['connections']:
                    self.table['connections'][key] = []
                self.table['connections'][key].append({
                    'type': 'metric_update',
                    'metrics': {
                        'quality': rif.get('quality', 0),
                        'hop_counter': rif.get('hop_count', 0),
                        'rtt': rif.get('transport_time', 0),
                        'ttl': netRom_cfg.get('time_to_live', 255),
                        'port_id': port_id,
                        'digi_path': digi_path
                    },
                    'timestamp': current_time
                })

        logger.debug(f"Nodes: {len(self.table['nodes'])}, Connections: {len(self.table['connections'])}")

    def get_routes_for_de(self, de_call, max_routes=3, port_id=None):
        """
        Konvertiert Verbindungen in ein route_1, route_2, route_3-Format.
        Optional nach port_id filtern.
        """
        routes = []
        for (from_call, to_call), entries in self.table['connections'].items():
            if to_call == de_call:
                for entry in entries:
                    if port_id is None or entry['metrics']['port_id'] == port_id:
                        quality = entry['metrics'].get('quality', 0)
                        hop_counter = entry['metrics'].get('hop_counter', 0)
                        routes.append({
                            'route': [from_call, to_call],
                            'quality': quality,
                            'hop_counter': hop_counter
                        })
        routes = sorted(routes, key=lambda x: x['quality'], reverse=True)[:max_routes]
        result = {}
        for i, route in enumerate(routes, 1):
            result[f'route_{i}'] = route['route'] + [route['quality']] if route else []
        for i in range(1, max_routes + 1):
            if f'route_{i}' not in result:
                result[f'route_{i}'] = []
        return result

    def filter_by_port(self, port_id):
        """
        Gibt eine gefilterte Tabelle mit Daten für einen bestimmten Port zurück.
        """
        filtered = {'nodes': {}, 'connections': {}}
        for call, node in self.table['nodes'].items():
            if port_id in node['ports']:
                filtered['nodes'][call] = node.copy()
                filtered['nodes'][call]['ports'] = {port_id: node['ports'][port_id]}
        for key, entries in self.table['connections'].items():
            filtered_entries = [e for e in entries if e['metrics']['port_id'] == port_id]
            if filtered_entries:
                filtered['connections'][key] = filtered_entries
        return dict(filtered)

    def debug_out(self, port_id=None):
        """
        Gibt die Tabelle aus, optional gefiltert nach port_id.
        """
        table = self.filter_by_port(port_id) if port_id is not None else self.table
        print("------- Routing Table -------")
        print("Nodes:")
        for call, node in table['nodes'].items():
            print(f"-- {call}:")
            for key, value in node.items():
                if key == 'info_history':
                    print(f"- {key}: {len(value)} entries")
                elif key == 'ports':
                    print(f"- {key}: {list(value.keys())}")
                else:
                    print(f"- {key}: {value}")
        print("\nConnections:")
        for (from_call, to_call), entries in table['connections'].items():
            print(f"-- {from_call} -> {to_call}:")
            for entry in entries:
                print(f"- Type: {entry['type']}")
                print(f"  Metrics: {entry['metrics']}")
                print(f"  Timestamp: {entry['timestamp']}")
        print("----------------------------")