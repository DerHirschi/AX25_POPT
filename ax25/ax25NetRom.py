from fnc.str_fnc import is_byte_ascii
import logging

logger = logging.getLogger(__name__)


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


def decode_ax25call(inp: b''):
    call = ''
    for c in inp[:-1]:
        call += chr(int(c) >> 1)
    call = call.replace(' ', '').upper()
    """Address > CRRSSID1    Digi > HRRSSID1"""
    bi = bin(int(hex(inp[-1])[2:], 16))[2:].zfill(8)
    # s_bit = bool(int(bi[7], 2))  # Stop Bit      Bit 8
    # c_bit = bool(int(bi[0], 2))  # C bzw H Bit   Bit 1
    ssid = int(bi[3:7], 2)  # SSID          Bit 4 - 7
    # r_bits = bi[1:3]  # Bit 2 - 3 not used. Free to use for any application .?..
    # call_str = get_call_str(call, ssid)
    """
    print(f"NetRom ax25call_decoder: {call_str}\n"
          f"s-bit: {s_bit}\n"
          f"c-bit: {c_bit}\n"
          f"r-bits:{r_bits}\n\n")
    """
    return call, ssid


# ======================== UI ==========================================

def NetRom_decode_UI(ax25_frame_conf: dict):
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
        dest_call = decode_ax25call(el[:7])[0]
        dest_id = el[7:13].decode('ASCII', 'ignore')
        best_neighbor_call = decode_ax25call(el[13:20])[0]
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


def decode_RIF(rif_data: bytes):
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
    hop_C = int(rip_payload[8])
    transport_time = (rip_payload[9] << 8) | rip_payload[10]
    rif = []
    if len(rip_payload) > 10:
        rif = decode_RIF(rip_payload[11:])
        print(rif)
    opt_fields = rip_payload[11:]

    return dict(
        call=call,
        hop_C=hop_C,
        transport_time=transport_time,
        opt_fields=opt_fields,
        rif_data=rif
    )


def NetRom_decode_I(ax25_payload: bytes):
    if not ax25_payload:
        return ''
    if len(ax25_payload) < 20:
        # NetRom Minimum 20
        return ''

    if int(ax25_payload[0]) == 0xFF:
        # Routing Information Frame
        print(f"RoutingFrame_raw: {ax25_payload}")
        print(f"RoutingFrame_raw.hex: {ax25_payload.hex()}")
        """
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
        opcodes = {
            int(b'\x00'.hex()): 'EOP (End of Packet)',
            int(b'\x01'.hex()): 'IP (Information Packet)',
            int(b'\x02'.hex()): 'L3RTT (Layer 3 Round-Trip Time)',
        }.get(ax25_payload[0], None)
        if not opcodes:
            print("")
            return ''
        """
        monitor_str = "Net-Rom RIF\r"
        # monitor_str += f"Raw: {ax25_payload.hex()}\r"
        """
        for k in dec_rip.keys():
            if k == 'rif_data':
                monitor_str += "RIF----\r"
                for kk in dec_rip[k].keys():
                    monitor_str += f"{kk}: {dec_rip[k][kk]}\r"
            else:
                monitor_str += f"{k}: {dec_rip[k]}\r"
        """

        return monitor_str

    else:
        # Information message
        networkHeader = ax25_payload[:15]
        transportHeader = ax25_payload[15:20]
        information = ax25_payload[20:]

        # Network Header
        call_from = networkHeader[:7]
        print(call_from)
        call_from = decode_ax25call(call_from)

        call_to = networkHeader[7:14]
        print(call_to)
        call_to = decode_ax25call(call_to)
        time_to_live = networkHeader[-1]

        # Transport Header
        cir_index = transportHeader[0]
        cir_ID = transportHeader[1]
        tx_seq = transportHeader[2]
        rx_seq = transportHeader[3]
        op_code = transportHeader[4]

        print("Net-Rom Inter-Node HDLC Frame")
        print(f"{call_from[0]}-{call_from[1]} > {call_to[0]}-{call_to[1]} ")
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
        print(f"Info: {information.decode('ASCII', 'ignore')}")
        print(f"RAW in: {ax25_payload.hex()}")

        monitor_str = "Net-Rom Inter-Node HDLC Frame\r"
        monitor_str += f"{call_from[0]}-{call_from[1]} > {call_to[0]}-{call_to[1]}\r"
        # monitor_str += f"Transport: {transportHeader}\r"
        monitor_str += f"TTL: {time_to_live}\r"
        monitor_str += f"Circuit Index: {cir_index}\r"
        monitor_str += f"Circuit ID: {cir_ID} "
        monitor_str += f"TX Seq: {tx_seq}\r"
        monitor_str += f"RX Seq: {rx_seq}\r"
        monitor_str += f"OPT-Byte: {hex(op_code)}\r"
        for k in dec_opt.keys():
            monitor_str += f"{k}: {dec_opt[k]}\r"
        monitor_str += f"Info: {information.decode('ASCII', 'ignore')}\r"
        return monitor_str



