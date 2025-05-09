"""
With the help of Grok3-AI
"""
from cfg.constant import PARAM_MAX_MON_WIDTH
from fnc.str_fnc import find_eol
from cfg.logger_config import logger

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

# ======================== Exception's End ==========================================
def decode_ax25call(inp: bytes) -> str:
    if len(inp) != 7:
        logger.error(f"Invalid AX.25 call length: {len(inp)}, payload: {inp.hex()}")
        return "INVALID"
    call = ''
    for c in inp[:-1]:
        char = chr(int(c) >> 1)
        if not (char.isalnum() or char == ' '):  # Allow alphanumeric and space
            logger.error(f"Invalid character in AX.25 call: {char}, payload: {inp.hex()}")
            return "INVALID"
        call += char
    call = call.strip().upper()
    if len(call) < 2 or len(call) > 6:  # Typical callsign length
        logger.error(f"Invalid callsign length: {call}, payload: {inp.hex()}")
        return "INVALID"
    try:
        ssid = (inp[-1] >> 1) & 0x0F  # SSID from bits 4-7
    except IndexError:
        logger.error(f"Invalid SSID byte in AX.25 call, payload: {inp.hex()}")
        return "INVALID"
    if ssid > 15:
        logger.error(f"Invalid SSID: {ssid}, payload: {inp.hex()}")
        return "INVALID"
    return f"{call}-{ssid}" if ssid else call

# ======================== UI ==========================================
def NetRom_decode_UI(ax25_frame_conf: dict):
    payload = ax25_frame_conf.get('payload', b'')
    node_call = ax25_frame_conf.get('from_call_str', '')
    if not payload or not node_call:
        raise NetRomDecodingERROR(ax25_frame_conf, 'No Payload or NodeCall')
    if len(payload) < 7:
        raise NetRomDecodingERROR(ax25_frame_conf, 'Payload < 7')
    if int(payload[0]) != 0xFF:
        print(f"NetRom UI no valid Sig {hex(payload[0])} should be 0xFF ")
        raise NetRomDecodingERROR(ax25_frame_conf, f'NetRom UI no valid Sig {hex(payload[0])} should be 0xFF')
    id_of_sending_node = payload[1:7].decode('ASCII', 'ignore')
    dest_frames = payload[7:]
    tmp = []
    while dest_frames:
        tmp.append(dest_frames[:21])
        dest_frames = dest_frames[21:]

    dec_neighbor_frames = {}
    for el in tmp:
        dest_call = decode_ax25call(el[:7])
        if dest_call and dest_call != "INVALID":
            dest_id = el[7:13].decode('ASCII', 'ignore')
            best_neighbor_call = decode_ax25call(el[13:20])
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

# ==================== UI-END ==========================================
def decode_opcode(opcode_byte: int) -> dict:
    try:
        choke_flag = (opcode_byte & 0b10000000) >> 7
        nak_flag = (opcode_byte & 0b01000000) >> 6
        more_follows_flag = (opcode_byte & 0b00100000) >> 5
        reserved_flag = (opcode_byte & 0b00010000) >> 4
        opcode_value = opcode_byte & 0b00001111

        opcode_names = {
            0x00: 'inp custom',  # Proprietäre Nachricht, z. B. Laufzeitmessung
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

def decode_INP_DHLC(ax25_payload: bytes) -> dict:
    if len(ax25_payload) < 20:
        logger.error("Payload too short for NET/ROM decoding")
        return {}

    # Network Header
    networkHeader = ax25_payload[:15]
    call_from = decode_ax25call(networkHeader[:7])
    call_to = decode_ax25call(networkHeader[7:14])
    time_to_live = networkHeader[-1]

    # Transport Header
    transportHeader = ax25_payload[15:20]
    cir_index = transportHeader[0]
    cir_ID = transportHeader[1]
    tx_seq = transportHeader[2]
    rx_seq = transportHeader[3]
    op_code = transportHeader[4]
    dec_opt = decode_opcode(op_code)

    # Initialize additional fields
    decoded_data = {
        ' call_from': call_from,
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
        'is_rif': False
    }

    # Check for RIF format if INP capable
    if call_to == 'L3RTT' and len(ax25_payload) > 20 and ax25_payload[20] == 0xFF:
        information = ax25_payload[20:].decode('ASCII', 'ignore')
        if '$N' in information:
            decoded_data['inp_capable'] = True
            decoded_data['is_rif'] = True
        return decoded_data  # RIF decoding will be handled in NetRom_decode_I

    # Opcode-specific decoding
    payload_offset = 20
    if op_code == 0x01:  # Connect Request
        if len(ax25_payload) >= 35:  # Window Size (1) + User Call (7) + Origin Node (7)
            decoded_data['window_size'] = ax25_payload[20] & 0x7F
            decoded_data['user_callsign'] = decode_ax25call(ax25_payload[21:28])
            origin_node = decode_ax25call(ax25_payload[28:35])
            decoded_data['user_callsign'] += f"@{origin_node}"
            payload_offset = 35
            if len(ax25_payload) >= 37:  # Timeout (2)
                decoded_data['timeout'] = int.from_bytes(ax25_payload[35:37], byteorder='big')
                payload_offset = 37
        else:
            logger.warning("Payload too short for Connect Request")
    elif op_code == 0x02:  # Connect Acknowledge
        if len(ax25_payload) >= 25:  # Your Circuit Index (1) + Your Circuit ID (1) + My Circuit Index (1) + My Circuit ID (1) + Window Size (1)
            decoded_data['your_cir_index'] = ax25_payload[20]
            decoded_data['your_cir_ID'] = ax25_payload[21]
            decoded_data['my_cir_index'] = ax25_payload[22]
            decoded_data['my_cir_ID'] = ax25_payload[23]
            decoded_data['window_size'] = ax25_payload[24]
            decoded_data['choke'] = dec_opt['Choke']
            payload_offset = 25
        else:
            logger.warning("Payload too short for Connect Acknowledge")
    elif call_to == 'L3RTT':  # L3RTT Frame
        information = ax25_payload[20:].decode('ASCII', 'ignore')
        decoded_data['information'] = information
        # Check for INP capable flag ($N)
        if '$N' in information:
            decoded_data['inp_capable'] = True
            # Split payload to separate main text and flags
            parts = information.split('$N')
            decoded_data['information'] = parts[0].rstrip()
            decoded_data['flags'] = [flag for flag in parts[1].split('$') if flag.strip()]
        else:
            decoded_data['flags'] = [flag for flag in information.split('$') if flag.strip()]
    else:
        information = ax25_payload[payload_offset:]
        information = information.replace(b'\r', b'')
        capable_flags = information.split(b'$')
        decoded_data['information'] = capable_flags[0]
        decoded_data['capable_flags'] = capable_flags[1:] if len(capable_flags) > 1 else []

    return decoded_data

def NetRom_decode_I_mon(netrom_cfg: dict) -> str:
    if netrom_cfg.get('is_rif', False) or 'rif_data' in netrom_cfg:
        rif_data = netrom_cfg.get('rif_data', [])
        monitor_str = f"┌──┴─▶ NET/ROM RIF▽\n"
        if netrom_cfg.get('inp_capable', False):
            monitor_str += f"├►INP Capable: Yes\n"
        if not rif_data:
            monitor_str += f"├►Error: No valid RIP segments decoded\n"
        for rip in rif_data:
            call = rip['call'] if rip['call'] != "INVALID" else f"INVALID({rip.get('raw_call', 'unknown').hex()})"
            monitor_str += f"├►RIP: Call={call} Hop={rip['hop_count']} RTT={rip['transport_time']}\n"
            if 'alias' in rip['rif_data']:
                monitor_str += f"├►  Alias: {rip['rif_data']['alias']}\n"
            if 'ip' in rip['rif_data']:
                monitor_str += f"├►  IP: {rip['rif_data']['ip']}\n"
            for key, value in rip['rif_data'].items():
                if key.startswith('unknown_'):
                    monitor_str += f"├►  Unknown Option ({key}, length={value['length']}): {value['data']}\n"
        monitor_str += "└──┐\n"
        return monitor_str

    call_to = netrom_cfg.get('call_to', '')
    monitor_str = f"┌──┴─▶ NET/ROM▽ {netrom_cfg.get('call_from', '')}->{call_to} ttl {netrom_cfg.get('time_to_live', '')}\n"

    cir_index_str = f"{netrom_cfg.get('cir_index', 0):02x}"
    cir_ID_str = f"{netrom_cfg.get('cir_ID', 0):02x}"
    opcode_str = netrom_cfg['dec_opt']['Opcode-Str']
    opcode_value = netrom_cfg['dec_opt']['Opcode-Value']

    if call_to == 'L3RTT':
        monitor_str += f"├►L3RTT Frame: INP Capable={'Yes' if netrom_cfg.get('inp_capable', False) else 'No'}\n"
        if netrom_cfg.get('flags'):
            monitor_str += f"├►Other Flags: {netrom_cfg['flags']}\n"
        monitor_str += f"├────▶ Payload▽ (ASCII) len={len(netrom_cfg['information'])}\n"
        monitor_str += f"└►{netrom_cfg['information']}\n"
    elif opcode_value == 0x01:  # Connect Request
        monitor_str += f"└►{opcode_str}: my ckt {cir_index_str}/{cir_ID_str} wnd {netrom_cfg['window_size']} {netrom_cfg['user_callsign']} timeout {netrom_cfg['timeout']}\n"
    elif opcode_value == 0x02:  # Connect Acknowledge
        your_cir_index_str = f"{netrom_cfg.get('your_cir_index', 0):02x}"
        your_cir_ID_str = f"{netrom_cfg.get('your_cir_ID', 0):02x}"
        my_cir_index_str = f"{netrom_cfg.get('my_cir_index', 0):02x}"
        my_cir_ID_str = f"{netrom_cfg.get('my_cir_ID', 0):02x}"
        choke_status = "refused" if netrom_cfg.get('choke', 0) else ""
        monitor_str += f"└►{opcode_str}: ur ckt {your_cir_index_str}/{your_cir_ID_str} my ckt {my_cir_index_str}/{my_cir_ID_str} wnd {netrom_cfg['window_size']} {choke_status}\n"
    elif opcode_value in (0x03, 0x04, 0x06):
        monitor_str += f"└►{opcode_str}({hex(opcode_value)}): CID {cir_index_str}/{cir_ID_str} txseq {netrom_cfg['tx_seq']} rxseq {netrom_cfg['rx_seq']}\n"
    else:
        monitor_str += f"├►{opcode_str}({hex(opcode_value)}): CID {cir_index_str}/{cir_ID_str} txseq {netrom_cfg['tx_seq']} rxseq {netrom_cfg['rx_seq']}\n"

    if opcode_value not in (0x01, 0x02) and call_to != 'L3RTT':
        if netrom_cfg.get('capable_flags') or netrom_cfg.get('information'):
            monitor_str += f"├►OPT: Chock({netrom_cfg['dec_opt']['Choke']}) NAK({netrom_cfg['dec_opt']['NAK']}) More({netrom_cfg['dec_opt']['More-Follows']}) Res({netrom_cfg['dec_opt']['Reserved']})\n"

    if netrom_cfg.get('capable_flags'):
        monitor_str += f"├►C-Flags: {b' '.join(netrom_cfg['capable_flags']).decode('ASCII', 'ignore')}\n"
    if netrom_cfg.get('information') and call_to != 'L3RTT':
        monitor_str += f"├────▶ Payload▽ (ASCII) len={len(netrom_cfg['information'])}\n"
        eol = find_eol(netrom_cfg['information'])
        payload_lines = netrom_cfg['information'].split(eol)
        while '' in payload_lines:
            payload_lines.remove('')
        l_i = len(payload_lines)
        for line in payload_lines:
            while len(line) > PARAM_MAX_MON_WIDTH:
                monitor_str += f"├►{str(line[:PARAM_MAX_MON_WIDTH].decode('ASCII', 'ignore'))}\n"
                line = line[PARAM_MAX_MON_WIDTH:]
            l_i -= 1
            if line:
                if l_i:
                    monitor_str += f"├►{str(line.decode('ASCII', 'ignore'))}\n"
                else:
                    monitor_str += f"└►{str(line.decode('ASCII', 'ignore'))}\n"

    if not monitor_str.endswith('\n'):
        monitor_str += '\n'
    return monitor_str

def NetRom_decode_I(ax25_payload: bytes):
    if not ax25_payload:
        return {}
    if len(ax25_payload) < 20:
        return {}
    # Check for RIF format
    if int(ax25_payload[0]) == 0xFF:
        rif_data = decode_RIF(ax25_payload)
        return {'rif_data': rif_data, 'is_rif': True}
    # Decode as INP/DHLC
    decoded_data = decode_INP_DHLC(ax25_payload)
    if decoded_data.get('is_rif', False):
        rif_data = decode_RIF(ax25_payload[20:])  # Skip network/transport headers
        decoded_data['rif_data'] = rif_data
    return decoded_data

# ======================== RIF/RIP Decoding =====================================
def decode_RIP(rip_payload: bytes, start_index: int) -> dict:
    if len(rip_payload) < 10:
        logger.error(f"Invalid RIP payload length: {len(rip_payload)} bytes, payload: {rip_payload.hex()}, start_index: {start_index}")
        return {}
    raw_call = rip_payload[:7]
    call = decode_ax25call(raw_call)
    hop_count = int(rip_payload[7])
    transport_time = int.from_bytes(rip_payload[8:10], byteorder='big')
    if transport_time > 65535:  # Implausible RTT
        logger.warning(f"Implausible transport time: {transport_time}, payload: {rip_payload.hex()}")
        return {}
    rif_data = {}
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
            # logger.warning(f"Unknown option type: 0x{option_type:02x}, length: {option_length - 2}, payload: {option_data.hex()}")
        index += option_length
    return {
        'call': call,
        'raw_call': raw_call,
        'hop_count': hop_count,
        'transport_time': transport_time,
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
        if i + 10 > len(payload_raw):
            logger.error(f"Incomplete RIP at index {i}, remaining length: {len(payload_raw) - i}, payload: {payload_raw[i:].hex()}")
            break
        rip_data = decode_RIP(payload_raw[i:], i)
        if rip_data and rip_data['call'] != "INVALID":
            route_info.append(rip_data)
            i += rip_data['bytes_consumed']
        else:
            logger.warning(f"Skipping invalid RIP segment at index {i}, payload: {payload_raw[i:i+10].hex()}")
            i += 10
        if i < len(payload_raw) and payload_raw[i] == 0x00:
            i += 1
            continue
    return route_info

def NetRom_decode_RIF_mon(rif_data: list) -> str:
    monitor_str = "┌──┴─▶ NET/ROM RIF▽\n"
    if not rif_data:
        monitor_str += f"├►Error: No valid RIP segments decoded\n"
    for rip in rif_data:
        call = rip['call'] if rip['call'] != "INVALID" else f"INVALID({rip.get('raw_call', 'unknown').hex()})"
        monitor_str += f"├►RIP: Call={call} Hop={rip['hop_count']} RTT={rip['transport_time']}\n"
        if 'alias' in rip['rif_data']:
            monitor_str += f"├►  Alias: {rip['rif_data']['alias']}\n"
        if 'ip' in rip['rif_data']:
            monitor_str += f"├►  IP: {rip['rif_data']['ip']}\n"
        for key, value in rip['rif_data'].items():
            if key.startswith('unknown_'):
                monitor_str += f"├►  Unknown Option ({key}, length={value['length']}): {value['data']}\n"
    monitor_str += "└──┐\n"
    return monitor_str