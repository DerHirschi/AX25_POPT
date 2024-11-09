from fnc.str_fnc import is_byte_ascii
import logging

logger = logging.getLogger(__name__)

# ======================== Exception's ==========================================


class NetRomDecodingERROR(Exception):
    def __init__(self, ax25_frame_conf: dict, e_text=''):
        payload = ax25_frame_conf.get('payload', b'')
        node_call = ax25_frame_conf.get('from_call_str', '')
        out_str = f"NetRomDecodingERROR: {e_text}\n"
        out_str += f"node_call: {node_call}\n"
        out_str += f"payload: {payload}\n"
        out_str += f"payload hex: {payload.hex()}\n"
        print(out_str)
        logger.error(out_str)

# ======================== Exception's End ==========================================


def decode_ax25call(inp: b''):
    call = ''
    for c in inp[:-1]:
        call += chr(int(c) >> 1)
    call = call.replace(' ', '').upper()
    """Address > CRRSSID1    Digi > HRRSSID1"""
    try:
        bi = bin(inp[-1])[2:].zfill(8)
    except IndexError:
        return ''
    ssid = int(bi[3:7], 2)  # SSID Bit 4 - 7
    if not ssid:
        return call
    return f"{call}-{ssid}"


# ======================== UI ==========================================
# Old netRom
def NetRom_decode_UI(ax25_frame_conf: dict):
    """ Old NetRom """
    payload = ax25_frame_conf.get('payload', b'')
    node_call = ax25_frame_conf.get('from_call_str', '')
    if not payload or not node_call:
        raise NetRomDecodingERROR(ax25_frame_conf, 'No Payload or NodeCall')
    if len(payload) < 7:
        # NetRom Minimum 20
        raise NetRomDecodingERROR(ax25_frame_conf, 'Payload < 7')
    if int(payload[0]) != 0xFF:
        print(f"NetRom UI no valid Sig {hex(payload[0])} should be 0xFF ")
        raise NetRomDecodingERROR(ax25_frame_conf, f'NetRom UI no valid Sig {hex(payload[0])} should be 0xFF')
    print('Net-Rom UI')
    id_of_sending_node = payload[1:7].decode('ASCII', 'ignore')
    print(f"ID sending Node: {id_of_sending_node}")
    dest_frames = payload[7:]
    tmp = []
    while dest_frames:
        tmp.append(dest_frames[:21])
        dest_frames = dest_frames[21:]

    dec_neighbor_frames = {}
    for el in tmp:
        dest_call = decode_ax25call(el[:7])
        if dest_call:
            dest_id = el[7:13].decode('ASCII', 'ignore')
            best_neighbor_call = decode_ax25call(el[13:20])
            if best_neighbor_call:
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


def NetRom_decode_UI_mon(ax25_frame_conf: dict):
    """ Old NetRom """
    netrom_cfg = ax25_frame_conf.get('netrom_cfg', {})
    call_of_sending_node = netrom_cfg.get('node_call', '')
    id_of_sending_node = netrom_cfg.get('node_id', '')
    node_nb_list = netrom_cfg.get('node_nb_list', {})

    monitor_str = f"NET/ROM Routing: {id_of_sending_node}:{call_of_sending_node}\n"
    monitor_str += "Neighbors - Alias  - BestNeighbor - BestQual\n"

    for de, item in node_nb_list.items():
        de_id = item.get('dest_id', '')
        best_nb = item.get('best_neighbor_call', '')
        qaul = item.get('qual', '')
        monitor_str += f"{de.ljust(9)} - {de_id.ljust(6)} - {best_nb.ljust(12)} - {qaul}\n"
    return monitor_str

# ==================== UI-END ==========================================


def decode_opcode(opcode_byte):
    # Bit-Masken für die verschiedenen Bits im OpCode-Byte
    chock_flag = (opcode_byte & 0b10000) >> 4
    nak_flag = (opcode_byte & 0b1000) >> 3
    more_follows_flag = (opcode_byte & 0b100) >> 2
    reserved_flag = (opcode_byte & 0b10) >> 1
    optcode_value = opcode_byte & 0b1111

    return {
        'OPT-Chock': chock_flag,
        'OPT-NAK': nak_flag,
        'OPT-More-Follows': more_follows_flag,
        'OPT-Reserved': reserved_flag,
        'OPT-OptCode-Val': optcode_value
    }


def decode_IP(ip_data: bytes):
    return int(ip_data[0]), int(ip_data[1]), int(ip_data[2]), int(ip_data[3]), int(ip_data[4]),


def decode_RIF_old(rif_data: bytes):
    if not rif_data:
        return {}
    # while rif_data:
    if int(rif_data[0]) == 0x00:
        index = 1
        while is_byte_ascii(rif_data[index]):
            index += 1

        if index >= len(rif_data):
            return {}
        alias = rif_data[1:index].decode('ASCII')
        index += 1
        if index >= len(rif_data):
            return {}
        length = int(rif_data[index])
        index += 1
        if index >= len(rif_data):
            return {}
        typ = rif_data[index]
        index += 1
        if index >= len(rif_data):
            return {}

        if typ == 0x01:
            return dict(
                alias=alias,
                length=length,
                typ=hex(typ),
                ip=decode_IP(rif_data[index:index + 5])

            )

    print(f"RIF-fail {rif_data}")
    return {}


def decode_RIP(rip_payload):
    call = decode_ax25call(rip_payload[:7])
    if not call:
        return {}
    hop_C = int(rip_payload[8])
    transport_time = (rip_payload[9] << 8) | rip_payload[10]
    rif = []
    if len(rip_payload) > 10:
        rif = decode_RIF_old(rip_payload[11:])
        print(rif)
    opt_fields = rip_payload[11:]

    return dict(
        call=call,
        hop_C=hop_C,
        transport_time=transport_time,
        opt_fields=opt_fields,
        rif_data=rif
    )



def decode_RIF(payload_raw):
    # Liste zum Speichern der decodierten Routeninformationen
    route_info = []
    print("---- RIF ----")
    print(f"decode_routing_frame len: {len(payload_raw)}")
    i = 0
    # Ist noch mind.ein RIP(ohne Optionen) im  RIF ?
    # (Call + Hop + Time + EOP = 7 + 1 + 2 + 1 = 11)

    while i+10 < len(payload_raw):
        if payload_raw[i] != 0xFF:
            print('Error 0xFF Flag ')
            return
        i += 1
        while i+10 < len(payload_raw):
            print("---- RIP ----")
            # Durchlaufen der Rohdaten-Payload, beginnend mit dem zweiten Byte (das erste Byte wird übersprungen)
            call = decode_ax25call(payload_raw[i:i + 7])
            i += 7
            hop_c = payload_raw[i]
            i += 1
            rtt = int.from_bytes(payload_raw[i: i + 2], byteorder='big')
            i += 2

            # opt_len = payload_raw[i]
            # i += 1
            opt_typ = payload_raw[i]
            print(f"Call: {call} - hop-C: {hop_c} - rtt: {rtt} - opt_len:{'####'} - opt_typ:{hex(opt_typ)}")
            opt_field = {
                0x00: 'Alias',
                0x01: 'IP',
            }.get(opt_typ, None)
            if opt_field:
                print(f"Opt-Field: {hex(opt_typ)} - {opt_field}")
            else:
                print(f"Opt-Field: {hex(opt_typ)} !! UNKNOWN !!")
            i += 1
            if opt_typ == 0x00:
                ident = b''
                while i < len(payload_raw):
                    print(f'---{payload_raw[i: i + 1]}----')
                    opt_len = payload_raw[i]

                    print(f"opt_len: {opt_len}")

                    if opt_len == 0x00:
                        i += 1
                        break
                    if opt_len == 0xFF:
                        break

                    if opt_len > len(payload_raw) - i:
                        print("INP-Fehler!")
                        i += 1
                        ident = payload_raw[i: i + 1]
                    else:
                        if not opt_len:
                            print("Fehler OPT-LEN 0")
                            i += 1
                            ident = payload_raw[i: i + 1]
                        else:
                            i += 1
                            opt_len -= 1
                            ident = payload_raw[i: i+opt_len]
                            i += opt_len

                print(f"Ident: {ident} - {ident.decode('ASCII', 'ignore')}")
            elif opt_typ == 0x01:
                ip = payload_raw[i:i + 4]
                netmask = payload_raw[i + 5]
                print(f"IP: {int(ip[0])}.{int(ip[1])}.{int(ip[2])}.{int(ip[3])}/{int(netmask)}")
                i += 5
            else:
                print('No RIF Option')
                while True:
                    i += 1
                    print(f'{payload_raw[i: i + 1]}')
                    if payload_raw[i] == 0x00:
                        i += 1
                        break
                    if payload_raw[i] == 0xFF:
                        break
            if i == len(payload_raw):
                print("Done !")
                break
            if payload_raw[i] == 0xFF:
                break

    return route_info

# ===========================================================================================


def decode_INP_DHLC(ax25_payload: bytes):
    """ Inter-Node HDLC Frame """
    # Information message
    networkHeader = ax25_payload[:15]
    transportHeader = ax25_payload[15:20]
    information = ax25_payload[20:]
    information = information.replace(b'\r', b'')
    capable_flags = information.split(b'$')
    information = capable_flags[0]
    capable_flags = capable_flags[1:]
    capable_flags = [r for r in capable_flags]

    # Network Header
    call_from = decode_ax25call(networkHeader[:7])
    call_to = decode_ax25call(networkHeader[7:14])
    time_to_live = networkHeader[-1]

    # Transport Header
    cir_index = transportHeader[0]
    cir_ID = transportHeader[1]
    tx_seq = transportHeader[2]
    rx_seq = transportHeader[3]
    op_code = transportHeader[4]

    if call_to == 'L3RTT':
        print(f"Net-Rom Inter-Node HDLC Frame - L3RTT RTT Frame")
        monitor_str = "Net-Rom Inter-Node HDLC Frame - L3RTT RTT Frame\n"
    else:
        print("Net-Rom Inter-Node HDLC Frame")
        monitor_str = "Net-Rom Inter-Node HDLC Frame\n"
    print(f"{call_from} > {call_to}")
    print(f"TTL: {time_to_live} ")
    print(f"Transport: {transportHeader} ")
    print(f"Circuit Index: {cir_index} ")
    print(f"Circuit ID: {cir_ID} ")
    print(f"TX Seq: {tx_seq} ")
    print(f"RX Seq: {rx_seq} ")
    print(f"Opt: {op_code} - {hex(op_code)} ")
    dec_opt = decode_opcode(op_code)
    for k in dec_opt.keys():
        print(f"{k}: {dec_opt[k]}")

    opcodes = {
        0x01: 'Connect Request',
        0x02: 'Connect acknowledg',
        0x03: 'Disconnect request',
        0x04: 'Disconnect acknowledg',
        0x05: 'Information',
        0x06: 'Information acknowledg',
    }.get(op_code, None)
    if opcodes:
        print(f"OPT: {opcodes}")
    else:
        print(f"OPT: {op_code} !!unknown!!")

    print(f"C-Flags: {b' '.join(capable_flags)}")
    print("Info: ")
    print(information)
    print(f"RAW in: {ax25_payload.hex()}")

    monitor_str += f"{call_from} > {call_to}\n"
    # monitor_str += f"Transport: {transportHeader}\r"
    monitor_str += f"TTL: {time_to_live}\n"
    monitor_str += f"Circuit Index: {cir_index}\n"
    monitor_str += f"Circuit ID: {cir_ID}\n"
    monitor_str += f"TX Seq: {tx_seq}\n"
    monitor_str += f"RX Seq: {rx_seq}\n"
    monitor_str += f"OPT-Byte: {hex(op_code)}/{opcodes}\n"
    for k in dec_opt.keys():
        monitor_str += f"{k}: {dec_opt[k]}\n"
    monitor_str += f"C-Flags: {b' '.join(capable_flags)}\n"
    monitor_str += f"Info: {information.decode('ASCII', 'ignore')}\n"
    return monitor_str


def NetRom_decode_I(ax25_payload: bytes):
    if not ax25_payload:
        return ''
    if len(ax25_payload) < 20:
        # NetRom Minimum 20
        return ''
    print('')
    print('==============================NEU========================================')
    opcodes = {
        0x00: 'EOP (End of Packet)',
        0x01: 'IP (Information Packet)',
        0x02: 'L3RTT (Layer 3 Round-Trip Time)',
        0xff: 'RIF',
    }.get(ax25_payload[0], None)
    if opcodes:
        print(f"OPT1: {opcodes}")
    else:
        print(f"OPT1-no Opt: {ax25_payload[0]}")

    if int(ax25_payload[0]) == 0xFF:
        # Routing Information Frame
        print(f"RoutingFrame_raw: {ax25_payload}")
        print(f"RoutingFrame_raw.hex: {ax25_payload.hex()}")
        # Decodieren der Rohdaten-Payload
        decoded_routes = decode_RIF(ax25_payload)

        # Ausgabe der decodierten Routeninformationen
        print("INP Route Information Frame:")
        print("{:<15s} {:<8s} {:<8s}".format("Call", "Quality", "RTT"))
        """
        for route in decoded_routes:
            print("{:<15s} {:<8d} {:<8d}".format(route[0], route[1], route[2]))
        """
        """
        print('========RIP======')
        dec_rip = decode_RIP(ax25_payload[1:])
        for k in dec_rip.keys():
            if k == 'rif_data':
                print("RIF----")
                for kk in dec_rip[k].keys():
                    print(f"{kk}: {dec_rip[k][kk]}")
            else:
                print(f"{k}: {dec_rip[k]}")
        """

        """
        monitor_str = "Net-Rom RIF\n"
        monitor_str += f"Raw: {ax25_payload.hex()}\r"

        for k in dec_rip.keys():
            if k == 'rif_data':
                monitor_str += "RIF----\r"
                for kk in dec_rip[k].keys():
                    monitor_str += f"{kk}: {dec_rip[k][kk]}\r"
            else:
                monitor_str += f"{k}: {dec_rip[k]}\r"
        """

        return ''

    else:
        # Inter-Node HDLC Frame
        return decode_INP_DHLC(ax25_payload)



