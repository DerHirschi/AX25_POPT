"""
With the help of Grok3-AI
"""
from cfg.constant import PARAM_MAX_MON_WIDTH
from fnc.str_fnc import find_eol
from cfg.logger_config import logger
from collections import defaultdict

# ======================== Exception's ==========================================
class NetRomDecodingERROR(Exception):
    def __init__(self, ax25_frame_conf: dict, e_text=''):
        payload = ax25_frame_conf.get('payload', b'')
        node_call = ax25_frame_conf.get('from_call_str', '')
        out_str = f"NetRomDecodingERROR: {e_text}\n"
        out_str += f"node_call: {node_call}\n"
        out_str += f"payload: {payload.hex()}\n"
        out_str += f"payload length: {len(payload)}\n"
        logger.error(out_str)

# ======================== Fragment Buffer ======================================
class FragmentBuffer:
    def __init__(self):
        # Dictionary to store fragments: key is (cir_index, cir_ID, tx_seq), value is list of bytes
        self.fragments = defaultdict(list)

    def add_fragment(self, cir_index: int, cir_ID: int, tx_seq: int, data: bytes, more_follows: bool) -> bytes:
        """Add a fragment to the buffer and return complete data if ready."""
        key = (cir_index, cir_ID, tx_seq)
        self.fragments[key].append((data, more_follows))

        # Check if all fragments are complete (no more_follows flag in the last fragment)
        fragments = self.fragments[key]
        if fragments and not fragments[-1][1]:  # Last fragment has more_follows = False
            # Combine all fragments
            combined_data = b''.join(frag[0] for frag in fragments)
            # Clear the buffer for this key
            del self.fragments[key]
            return combined_data
        return b''

    def clear(self):
        """Clear all fragments."""
        self.fragments.clear()

# Global fragment buffer
fragment_buffer = FragmentBuffer()

# ======================== Helper Functions =====================================
def decode_ax25call(inp: bytes):
    if len(inp) != 7:
        logger.error(f"Invalid AX.25 call length: {len(inp)}, payload: {inp.hex()}")
        return "INVALID", 0
    call = ''
    for c in inp[:-1]:
        char = chr(int(c) >> 1)
        # Anpassung: Erlaube alle ASCII-Zeichen, die TNN akzeptiert, und ignoriere Steuerzeichen
        if not (char.isalnum() or char in ' -'):  # Erweitert um Bindestrich und Leerzeichen
            logger.warning(f"Non-alphanumeric character in AX.25 call: {char}, payload: {inp.hex()}")
            call += '?'  # Ersetze ungültige Zeichen durch '?'
        else:
            call += char
    call = call.strip().upper()
    if len(call) < 2 or len(call) > 6:  # Typical callsign length
        logger.error(f"Invalid callsign length: {call}, payload: {inp.hex()}")
        return "INVALID", 0
    try:
        ssid = (inp[-1] >> 1) & 0x0F  # SSID from bits 4-7
        status = inp[-1]  # Full status byte (e.g., 0x1f = 31)
    except IndexError:
        logger.error(f"Invalid SSID byte in AX.25 call, payload: {inp.hex()}")
        return "INVALID", 0
    if ssid > 15:
        logger.error(f"Invalid SSID: {ssid}, payload: {inp.hex()}")
        return "INVALID", 0
    callsign = f"{call}-{ssid}" if ssid else call
    return callsign, status

def decode_opcode(opcode_byte: int) -> dict:
    try:
        choke_flag = (opcode_byte & 0b10000000) >> 7
        nak_flag = (opcode_byte & 0b01000000) >> 6
        more_follows_flag = (opcode_byte & 0b00100000) >> 5
        reserved_flag = (opcode_byte & 0b00010000) >> 4
        opcode_value = opcode_byte & 0b00001111

        # Anpassung: Opcode 0x00 umbenannt zu 'INP Route Record'
        opcode_names = {
            0x00: 'INP Route Record',  # INP-spezifische Nachricht, z. B. Route Record für die Dokumentation der Paketroute
            0x01: 'conn rqst',
            0x02: 'conn ack',
            0x03: 'disc rqst',
            0x04: 'disc ack',
            0x05: 'info',
            0x06: 'info ack',
            0x07: 'pid chg'
        }
        opcode_str = opcode_names.get(opcode_value, f'unknown({hex(opcode_value)})')

        return {
            'Choke': choke_flag,
            'NAK': nak_flag,
            'More-Follows': more_follows_flag,
            'Reserved': reserved_flag,
            'Opcode-Value': opcode_value,
            'Opcode-Str': opcode_str,
        }
    except Exception as e:
        logger.error(f"Failed to decode opcode: {str(e)}")
        return {
            'Choke': 0,
            'NAK': 0,
            'More-Follows': 0,
            'Reserved': 0,
            'Opcode-Value': 0,
            'Opcode-Str': 'error',
        }

# ======================== UI Decoding ==========================================
def NetRom_decode_UI(ax25_frame_conf: dict):
    payload = ax25_frame_conf.get('payload', b'')
    node_call = ax25_frame_conf.get('from_call_str', '')
    if not payload or not node_call:
        raise NetRomDecodingERROR(ax25_frame_conf, 'No Payload or NodeCall')
    if len(payload) < 7:
        raise NetRomDecodingERROR(ax25_frame_conf, 'Payload < 7')
    if int(payload[0]) != 0xFF:
        raise NetRomDecodingERROR(ax25_frame_conf, f'NetRom UI no valid Sig {hex(payload[0])} should be 0xFF')
    id_of_sending_node = payload[1:7].decode('ASCII', 'ignore')
    dest_frames = payload[7:]
    tmp = []
    while dest_frames:
        tmp.append(dest_frames[:21])
        dest_frames = dest_frames[21:]

    dec_neighbor_frames = {}
    for el in tmp:
        dest_call = decode_ax25call(el[:7])[0]
        if dest_call and dest_call != "INVALID":
            dest_id = el[7:13].decode('ASCII', 'ignore')
            best_neighbor_call = decode_ax25call(el[13:20])[0]
            if best_neighbor_call and best_neighbor_call != "INVALID":
                qual = int(el[-1])
                dec_neighbor_frames[dest_call] = \
                    dict(
                        dest_call=dest_call,
                        dest_id=dest_id,
                        best_neighbor_call=best_neighbor_call,
                        qual=qual
                    )
    netrom_UI_cfg = dict(
        node_call=str(node_call),
        node_id=str(id_of_sending_node),
        node_nb_list=dec_neighbor_frames,
    )
    return netrom_UI_cfg

def NetRom_decode_UI_mon(netrom_cfg: dict):
    call_of_sending_node = netrom_cfg.get('node_call', '')
    id_of_sending_node = netrom_cfg.get('node_id', '')
    node_nb_list = netrom_cfg.get('node_nb_list', {})

    monitor_str = f"┌──┴─▶ NET/ROM Routing▽ {id_of_sending_node}:{call_of_sending_node}\n"
    monitor_str += "├►Neighbors - Alias  - BestNeighbor - BestQual\n"
    i = len(node_nb_list.keys())
    for de, item in node_nb_list.items():
        de_id = item.get('dest_id', '')
        best_nb = item.get('best_neighbor_call', '')
        qaul = item.get('qual', '')
        i -= 1
        if i:
            monitor_str += f"├►{de.ljust(9)} - {de_id.ljust(6)} - {best_nb.ljust(12)} - {qaul}\n"
        else:
            monitor_str += f"└►{de.ljust(9)} - {de_id.ljust(6)} - {best_nb.ljust(12)} - {qaul}\n"
    return monitor_str

# ======================== I-Frame Decoding =====================================
def decode_INP_DHLC(ax25_payload: bytes) -> dict:
    if len(ax25_payload) < 20:
        raise NetRomDecodingERROR({'payload': ax25_payload}, "Payload too short for NET/ROM decoding")

    # Network Header (15 bytes)
    networkHeader = ax25_payload[:15]
    call_from = decode_ax25call(networkHeader[:7])[0]
    call_to = decode_ax25call(networkHeader[7:14])[0]
    time_to_live = networkHeader[-1]

    # Transport Header (5 bytes)
    transportHeader = ax25_payload[15:20]
    cir_index = transportHeader[0]
    cir_ID = transportHeader[1]
    tx_seq = transportHeader[2]
    rx_seq = transportHeader[3]
    op_code = transportHeader[4]
    dec_opt = decode_opcode(op_code)

    # Validate Circuit Index (max 256 circuits, based on TNN NUMCIR)
    if cir_index >= 256:
        raise NetRomDecodingERROR({'payload': ax25_payload}, f"Invalid Circuit Index: {cir_index}")

    # Initialize decoded data
    decoded_data = {
        'call_from': call_from,
        'call_to': call_to,
        'time_to_live': time_to_live,
        'cir_index': cir_index,
        'cir_ID': cir_ID,
        'tx_seq': tx_seq,
        'rx_seq': rx_seq,
        'op_code': op_code,
        'dec_opt': dec_opt,
        'information': b'',
        'window_size': 0,
        'user_callsign': '',
        'timeout': 0,
        'your_cir_index': 0,
        'your_cir_ID': 0,
        'my_cir_index': 0,
        'my_cir_ID': 0,
        'choke': 0,
        'inp_capable': False,
        'flags': [],
        'is_rif': False,
        'is_l3local': False,
        'uplink_node': '',
        'via_list': [],
        'pid': 0,
        'is_fragmented': False,
        'inp_route': [],  # List of tuples: (callsign, status, hop_counter, marker)
        'inp_marker': b'',
        'raw_data': ''
    }

    # Check for RIF format if INP capable
    if call_to == 'L3RTT' and len(ax25_payload) > 20 and ax25_payload[20] == 0xFF:
        decoded_data['information'] = ax25_payload[20:]
        decoded_data['is_rif'] = True
        return decoded_data

    # Opcode-specific decoding
    payload_offset = 20
    opcode_value = dec_opt['Opcode-Value']
    more_follows = dec_opt['More-Follows']

    if opcode_value == 0x01:  # Connect Request
        if len(ax25_payload) < 35:
            raise NetRomDecodingERROR({'payload': ax25_payload}, "Payload too short for Connect Request")
        decoded_data['window_size'] = ax25_payload[20] & 0x7F
        decoded_data['user_callsign'] = decode_ax25call(ax25_payload[21:28])[0]
        origin_node = decode_ax25call(ax25_payload[28:35])[0]
        decoded_data['user_callsign'] += f"@{origin_node}"
        payload_offset = 35
        if len(ax25_payload) >= 42:
            uplink_node = decode_ax25call(ax25_payload[35:42])[0]
            if uplink_node != "INVALID":
                decoded_data['uplink_node'] = uplink_node
                payload_offset = 42
                via_list = []
                while payload_offset + 7 <= len(ax25_payload):
                    via_call = decode_ax25call(ax25_payload[payload_offset:payload_offset + 7])[0]
                    if via_call == "INVALID":
                        break
                    via_list.append(via_call)
                    payload_offset += 7
                decoded_data['via_list'] = via_list
        if len(ax25_payload) >= payload_offset + 2:
            decoded_data['timeout'] = int.from_bytes(ax25_payload[payload_offset:payload_offset + 2], byteorder='big')
            payload_offset += 2
        if call_to == call_from:
            decoded_data['is_l3local'] = True

    elif opcode_value == 0x02:  # Connect Acknowledge
        if len(ax25_payload) < 25:
            raise NetRomDecodingERROR({'payload': ax25_payload}, "Payload too short for Connect Acknowledge")
        decoded_data['your_cir_index'] = ax25_payload[20]
        decoded_data['your_cir_ID'] = ax25_payload[21]
        decoded_data['my_cir_index'] = ax25_payload[22]
        decoded_data['my_cir_ID'] = ax25_payload[23]
        decoded_data['window_size'] = ax25_payload[24]
        decoded_data['choke'] = dec_opt['Choke']
        payload_offset = 25
        if call_to == call_from:
            decoded_data['is_l3local'] = True

    elif opcode_value == 0x03:  # Disconnect Request
        pass

    elif opcode_value == 0x04:  # Disconnect Acknowledge
        pass

    elif opcode_value == 0x05:  # Information
        information = ax25_payload[payload_offset:]
        decoded_data['information'] = information
        if call_to == 'L3RTT':
            if b'$N' in information:
                decoded_data['inp_capable'] = True
                parts = information.split(b'$N')
                decoded_data['information'] = parts[0].rstrip()
                decoded_data['flags'] = [flag.decode('ASCII', 'ignore') for flag in parts[1].split(b'$') if flag.strip() and all(32 <= ord(c) <= 127 for c in flag.decode('ASCII', 'ignore'))]
            else:
                decoded_data['flags'] = [flag.decode('ASCII', 'ignore') for flag in information.split(b'$') if flag.strip() and all(32 <= ord(c) <= 127 for c in flag.decode('ASCII', 'ignore'))]
        else:
            if more_follows:
                decoded_data['is_fragmented'] = True
                complete_data = fragment_buffer.add_fragment(cir_index, cir_ID, tx_seq, information, more_follows)
                if complete_data:
                    decoded_data['information'] = complete_data
            else:
                complete_data = fragment_buffer.add_fragment(cir_index, cir_ID, tx_seq, information, more_follows)
                decoded_data['information'] = complete_data if complete_data else information

    elif opcode_value == 0x06:  # Information Acknowledge
        pass

    elif opcode_value == 0x07:  # PID Change
        if len(ax25_payload) < 21:
            raise NetRomDecodingERROR({'payload': ax25_payload}, "Payload too short for PID Change")
        decoded_data['pid'] = ax25_payload[20]
        payload_offset = 21

    elif opcode_value == 0x00:  # INP Route Record
        information = ax25_payload[payload_offset:]
        decoded_data['information'] = information
        route = []
        offset = 0
        max_hops = 8
        while offset + 8 <= len(information) and len(route) < max_hops:
            call, status = decode_ax25call(information[offset:offset + 7])
            if call == "INVALID":
                logger.warning(f"Invalid call at offset {offset}: {information[offset:offset+7].hex()}")
                break
            hop_counter = information[offset + 7] & 0x1F if offset + 7 < len(information) else 0  # Maskiere zu 5 Bits (0-31)
            # Stern-Marker basierend auf ECHO_FLAG (status & 0x80)
            marker = True if (information[offset + 7] & 0x80) else False
            route.append((call, hop_counter, marker))
            offset += 8
        decoded_data['inp_route'] = route
        remaining = information[offset:]
        decoded_data['inp_marker'] = remaining
        if remaining:
            if b'$N' in remaining:
                decoded_data['inp_capable'] = True
                parts = remaining.split(b'$N')
                decoded_data['inp_marker'] = parts[0]
                decoded_data['flags'] = [
                    flag.decode('ASCII', 'ignore')
                    for flag in parts[1].split(b'$')
                    if flag.strip() and all(32 <= ord(c) <= 127 for c in flag.decode('ASCII', 'ignore'))
                ]
            else:
                if len(remaining) == 1 and remaining[0] in {0x9d}:
                    decoded_data['inp_marker'] = remaining.hex()
                else:
                    decoded_data['flags'] = [
                        flag.decode('ASCII', 'ignore')
                        for flag in remaining.split(b'$')
                        if flag.strip() and all(32 <= ord(c) <= 127 for c in flag.decode('ASCII', 'ignore'))
                    ]
        if not route and not remaining:
            logger.warning(f"No route or marker decoded: {information.hex()}")
            decoded_data['raw_data'] = information.hex()

    else:
        logger.warning(f"Unknown opcode: {opcode_value}, treating as information")
        decoded_data['information'] = ax25_payload[payload_offset:]
        decoded_data['raw_data'] = ax25_payload[payload_offset:].hex()

    if 'last_rx_seq' in decoded_data:
        if rx_seq != (decoded_data['last_rx_seq'] + 1) % 256:
            logger.warning(f"Sequence number discontinuity: expected {(decoded_data['last_rx_seq'] + 1) % 256}, got {rx_seq}")
    decoded_data['last_rx_seq'] = rx_seq
    return decoded_data

def NetRom_decode_I(ax25_payload: bytes):
    if not ax25_payload:
        logger.warning("Empty payload")
        return {}
    # Check for RIF format
    if len(ax25_payload) >= 1 and int(ax25_payload[0]) == 0xFF:
        #logger.debug(f"Detected RIF format, payload: {ax25_payload.hex()}")
        rif_data = decode_RIF(ax25_payload)
        return {'rif_data': rif_data, 'is_rif': True}
    # Decode as INP/DHLC
    try:
        decoded_data = decode_INP_DHLC(ax25_payload)
        if decoded_data.get('is_rif', False):
            rif_data = decode_RIF(ax25_payload[20:])  # Skip network/transport headers
            decoded_data['rif_data'] = rif_data
        return decoded_data
    except NetRomDecodingERROR as e:
        logger.error(f"Failed to decode INP/DHLC: {str(e)}")
        return {}

def NetRom_decode_I_mon(netrom_cfg: dict) -> str:
    if netrom_cfg.get('is_rif', False) or 'rif_data' in netrom_cfg:
        return NetRom_decode_RIF_mon(netrom_cfg)

    call_to = netrom_cfg.get('call_to', '')
    monitor_str = f"┌──┴─▶ NET/ROM▽ {netrom_cfg.get('call_from', '')}->{call_to} ttl {netrom_cfg.get('time_to_live', '')}\n"

    cir_index_str = f"{netrom_cfg.get('cir_index', 0):02x}"
    cir_ID_str = f"{netrom_cfg.get('cir_ID', 0):02x}"
    opcode_str = netrom_cfg['dec_opt']['Opcode-Str']
    opcode_value = netrom_cfg['dec_opt']['Opcode-Value']

    base_info = f"CID {cir_index_str}/{cir_ID_str} txseq {netrom_cfg['tx_seq']} rxseq {netrom_cfg['rx_seq']}"
    opt_info = f"OPT: Choke({netrom_cfg['dec_opt']['Choke']}) NAK({netrom_cfg['dec_opt']['NAK']}) More({netrom_cfg['dec_opt']['More-Follows']}) Res({netrom_cfg['dec_opt']['Reserved']})"

    if call_to == 'L3RTT':
        monitor_str += f"├►L3RTT Frame: INP Capable={'Yes' if netrom_cfg.get('inp_capable', False) else 'No'}\n"
        if netrom_cfg.get('flags'):
            monitor_str += f"├►Other Flags: {netrom_cfg['flags']}\n"
        information = netrom_cfg.get('information', b'')
        info_str = information.decode('ASCII', 'ignore') if isinstance(information, bytes) else information
        monitor_str += f"├────▶ Payload▽ (ASCII) len={len(info_str)}\n"
        monitor_str += f"└►{info_str}\n"
    elif opcode_value == 0x01:
        via_str = f" via {', '.join(netrom_cfg['via_list'])}" if netrom_cfg['via_list'] else ""
        monitor_str += f"└►{opcode_str}: my ckt {cir_index_str}/{cir_ID_str} wnd {netrom_cfg['window_size']} {netrom_cfg['user_callsign']} uplink {netrom_cfg['uplink_node']}{via_str} timeout {netrom_cfg['timeout']} {'L3LOCAL' if netrom_cfg['is_l3local'] else ''}\n"
    elif opcode_value == 0x02:
        your_cir_index_str = f"{netrom_cfg.get('your_cir_index', 0):02x}"
        your_cir_ID_str = f"{netrom_cfg.get('your_cir_ID', 0):02x}"
        my_cir_index_str = f"{netrom_cfg.get('my_cir_index', 0):02x}"
        my_cir_ID_str = f"{netrom_cfg.get('my_cir_ID', 0):02x}"
        choke_status = "refused" if netrom_cfg.get('choke', 0) else ""
        monitor_str += f"└►{opcode_str}: ur ckt {your_cir_index_str}/{your_cir_ID_str} my ckt {my_cir_index_str}/{my_cir_ID_str} wnd {netrom_cfg['window_size']} {choke_status} {'L3LOCAL' if netrom_cfg['is_l3local'] else ''}\n"
    elif opcode_value in (0x03, 0x04, 0x06):
        monitor_str += f"└►{opcode_str}({hex(opcode_value)}): {base_info}\n"
    elif opcode_value == 0x07:
        monitor_str += f"└►{opcode_str}({hex(opcode_value)}): {base_info} PID {netrom_cfg['pid']:02x}\n"
    elif opcode_value == 0x00:
        max_Str_len = 0
        monitor_str += f"├►{opcode_str}({hex(opcode_value)}): {base_info}\n"
        monitor_str += f"├►{opt_info}\n"
        if netrom_cfg.get('inp_capable'):
            monitor_str += f"├►INP Capable: Yes\n"
        if netrom_cfg.get('inp_route'):
            n = 0
            route_str = ''
            for route_hop in netrom_cfg.get('inp_route', []):
                call, hop_counter, marker = route_hop
                route_str += f"{call.ljust(9)}({hop_counter}){'*' if marker else ''}"
                n += 1
                if n > 5 or marker:
                    n = 0
                    new_str = f"├►Route:   {route_str} ▽\n"
                    monitor_str += new_str
                    max_Str_len = max(max_Str_len, len(new_str))
                    route_str = '->'
                else:
                    route_str += '->'
            if route_str:
                new_str = f"├►Route: {route_str[:-2]}\n"
                monitor_str += new_str
                max_Str_len = max(max_Str_len, len(new_str))
            if monitor_str.endswith('->\n'):
                monitor_str = monitor_str[:-3] + '\n'

            #route_str = '->'.join(f"{call}({hop_counter}){'*' if marker else ''}" for call, hop_counter, marker in netrom_cfg['inp_route'])
            #monitor_str += f"├►Route: {route_str}\n"
        if netrom_cfg.get('flags'):
            monitor_str += f"├►Flags: {netrom_cfg['flags']}\n"
        marker = netrom_cfg.get('inp_marker', b'')
        if marker:
            monitor_str += f"├────▶ Marker▽ (Hex) len={len(marker)}\n"
            monitor_str += f"└►{marker.hex()}\n"
        elif netrom_cfg.get('raw_data'):
            monitor_str += f"├────▶ Raw Data▽ (Hex) len={len(netrom_cfg['raw_data'])//2}\n"
            monitor_str += f"└►{netrom_cfg['raw_data']}\n"
        else:
            if max_Str_len:
                monitor_str += f"└{'─' * (max_Str_len - 1)}┘\n"
            else:
                monitor_str += f"└►No marker or data\n"
    else:
        monitor_str += f"├►{opcode_str}({hex(opcode_value)}): {base_info}\n"
        monitor_str += f"├►{opt_info}\n"
        if netrom_cfg.get('is_fragmented'):
            monitor_str += f"├►Fragmented: {'Pending' if netrom_cfg['dec_opt']['More-Follows'] else 'Complete'}\n"
        information = netrom_cfg.get('information', b'')
        if information:
            monitor_str += f"├────▶ Payload▽ (ASCII) len={len(information)}\n"
            try:
                info_str = information.decode('ASCII', 'ignore') if isinstance(information, bytes) else information
                eol = find_eol(information) if isinstance(information, bytes) else '\n'
                payload_lines = info_str.split(eol if isinstance(eol, str) else '\n')
                while '' in payload_lines:
                    payload_lines.remove('')
                l_i = len(payload_lines)
                for line in payload_lines:
                    while len(line) > PARAM_MAX_MON_WIDTH:
                        monitor_str += f"├►{line[:PARAM_MAX_MON_WIDTH]}\n"
                        line = line[PARAM_MAX_MON_WIDTH:]
                    l_i -= 1
                    if line:
                        if l_i:
                            monitor_str += f"├►{line}\n"
                        else:
                            monitor_str += f"└►{line}\n"
            except Exception as e:
                logger.warning(f"Failed to decode information: {str(e)}")
                if isinstance(information, bytes):
                    monitor_str += f"└►RAW: {information.hex()}\n"
                else:
                    monitor_str += f"└►RAW: {information}\n"
        elif netrom_cfg.get('raw_data'):
            monitor_str += f"├────▶ Raw Data▽ (Hex) len={len(netrom_cfg['raw_data'])//2}\n"
            monitor_str += f"└►{netrom_cfg['raw_data']}\n"

    if not monitor_str.endswith('\n'):
        monitor_str += '\n'
    return monitor_str

# ======================== RIF/RIP Decoding =====================================
def decode_RIP(rip_payload: bytes, start_index: int) -> dict:
    if len(rip_payload) < 7:
        logger.error(f"Invalid RIP payload length: {len(rip_payload)} bytes, payload: {rip_payload.hex()}, start_index: {start_index}")
        return {}

    rif_data = {}
    index = 0

    # Decode callsign (7 bytes)
    raw_call = rip_payload[:7]
    call = decode_ax25call(raw_call)[0]
    if call == "INVALID":
        logger.warning(f"Invalid callsign at index {start_index}, payload: {raw_call.hex()}")
        return {}
    rif_data['call'] = call
    rif_data['raw_call'] = raw_call
    index = 7

    # Check for short 12-byte frame (Callsign + Quality + Raw Data)
    if len(rip_payload) >= 8:
        hop_count = int(rip_payload[7])
        rif_data['hop_count'] = hop_count
        index += 1
        # Store remaining bytes as raw data
        if index < len(rip_payload):
            rif_data['raw_data'] = rip_payload[index:].hex()
            index = len(rip_payload)
    else:
        logger.warning(f"Payload too short for quality or data: {rip_payload.hex()}")
        return {}

    # Handle longer frames with hop count, transport time, and options
    if len(rip_payload) >= 10:
        #hop_count = int(rip_payload[7])
        transport_time = int.from_bytes(rip_payload[8:10], byteorder='big')
        if transport_time > 65535:  # Implausible RTT
            logger.warning(f"Implausible transport time: {transport_time}, payload: {rip_payload.hex()}")
            return {}
        #rif_data['hop_count'] = hop_count
        rif_data['transport_time'] = transport_time
        index = 10
        while index < len(rip_payload):
            if rip_payload[index] == 0x00:  # EOP
                index += 1
                break
            if index + 1 >= len(rip_payload):
                logger.error(f"Incomplete option field at index {start_index + index}, payload: {rip_payload[index:].hex()}")
                break
            option_length = rip_payload[index]
            if option_length < 2 or index + option_length > len(rip_payload):
                logger.error(f"Invalid option length: {option_length} at index {start_index + index}, payload: {rip_payload[index:].hex()}")
                break
            option_type = rip_payload[index + 1]
            option_data = rip_payload[index + 2:index + option_length]
            if option_type == 0x00:  # Alias
                try:
                    alias = option_data.decode('ASCII', 'ignore').strip()
                    if alias and all(32 <= ord(c) <= 127 for c in alias):  # Valid ASCII
                        rif_data['alias'] = alias
                    else:
                        logger.warning(f"Invalid alias characters: {alias}, payload: {option_data.hex()}")
                except Exception as e:
                    logger.warning(f"Failed to decode alias: {str(e)}, payload: {option_data.hex()}")
            elif option_type == 0x01:  # IP
                if len(option_data) >= 5:
                    try:
                        ip = '.'.join(str(int(x)) for x in option_data[:4]) + f"/{int(option_data[4])}"
                        rif_data['ip'] = ip
                    except Exception as e:
                        logger.warning(f"Failed to decode IP: {str(e)}, payload: {option_data.hex()}")
                else:
                    logger.warning(f"Invalid IP option length: {len(option_data)}, payload: {option_data.hex()}")
            else:
                rif_data[f'unknown_0x{option_type:02x}'] = {
                    'length': option_length - 2,
                    'data': option_data.hex()
                }
            index += option_length

    #logger.debug(f"Decoded RIP segment: {rif_data}, bytes consumed: {index}")
    return {
        'rif_data': rif_data,
        'bytes_consumed': index
    }

def decode_RIF(payload_raw: bytes) -> list:
    if not payload_raw:
        logger.warning("Empty RIF payload")
        return []
    if payload_raw[0] != 0xFF:
        logger.error(f"Invalid RIF signature, payload: {payload_raw.hex()}")
        return []
    route_info = []
    i = 1  # Skip RIF signature (0xFF)
    while i < len(payload_raw):
        rip_data = decode_RIP(payload_raw[i:], i)
        if rip_data and 'rif_data' in rip_data and rip_data['rif_data'].get('call', 'INVALID') != "INVALID":
            route_info.append(rip_data)
            i += rip_data['bytes_consumed']
        else:
            logger.warning(f"Skipping invalid RIP segment at index {i}, payload: {payload_raw[i:i+7].hex()}")
            i += min(7, len(payload_raw) - i)  # Skip at least 7 bytes to avoid infinite loop
        if i < len(payload_raw) and payload_raw[i] == 0x00:
            i += 1
            continue
    if i < len(payload_raw):
        logger.warning(f"Excess bytes in RIF payload at index {i}: {payload_raw[i:].hex()}")
        route_info.append({'rif_data': {'raw_data': payload_raw[i:].hex()}, 'bytes_consumed': len(payload_raw) - i})
    #logger.debug(f"Decoded RIF: {route_info}")
    return route_info

def NetRom_decode_RIF_mon(netrom_cfg: dict) -> str:
    rif_data = netrom_cfg.get('rif_data', [])
    monitor_str = f"┌──┴─▶ NET/ROM RIF▽\n"
    max_Str_len = len(monitor_str)
    if netrom_cfg.get('inp_capable', False):
        new_str = f"├►INP Capable: Yes\n"
        max_Str_len = max(max_Str_len, len(new_str))
        monitor_str += new_str
    if not rif_data:
        new_str = f"├►Error: No valid RIP segments decoded\n"
        max_Str_len = max(max_Str_len, len(new_str))
        monitor_str += new_str
    for rip in rif_data:
        rif = rip['rif_data']
        call = rif.get('call', 'INVALID')
        if call == "INVALID":
            call = f"INVALID({rif.get('raw_call', 'unknown').hex()})"
        if 'hop_count' in rif and 'transport_time' in rif:
            new_str = f"├►RIP: Call={call.ljust(9)} Hop={str(rif['hop_count']).ljust(2)} RTT={rif['transport_time']}\n"
        else:
            new_str = f"├►Node: {call.ljust(9)}\n"
        max_Str_len = max(max_Str_len, len(new_str))
        monitor_str += new_str
        #if 'quality' in rif:
        #    new_str = f"├►  Quality: {rif['quality']}\n"
        #    max_Str_len = max(max_Str_len, len(new_str))
        #    monitor_str += new_str
        if 'alias' in rif:
            new_str = f"├►  Alias: {rif['alias']}\n"
            max_Str_len = max(max_Str_len, len(new_str))
            monitor_str += new_str
        if 'ip' in rif:
            new_str = f"├►  IP: {rif['ip']}\n"
            max_Str_len = max(max_Str_len, len(new_str))
            monitor_str += new_str
        for key, value in rif.items():
            if key.startswith('unknown_'):
                new_str = f"├►  Unknown Option ({key}, length={value['length']}): {value['data']}\n"
                max_Str_len = max(max_Str_len, len(new_str))
                monitor_str += new_str
    monitor_str += f"└{'─' * (max_Str_len - 1)}┘\n"
    return monitor_str