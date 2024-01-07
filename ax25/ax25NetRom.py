from fnc.str_fnc import is_byte_ascii


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


def NetRom_decode_UI(ax25_payload: bytes):
    if not ax25_payload:
        return
    if len(ax25_payload) < 7:
        # NetRom Minimum 20
        return
    if int(ax25_payload[0]) != 0xFF:
        print(f"NetRom UI no valid Sig {hex(ax25_payload[0])} should be 0xFF ")
        return
    print('Net-Rom UI')
    id_of_sending_node = ax25_payload[1:7].decode('ASCII', 'ignore')
    print(f"ID sending Node: {id_of_sending_node}")
    dest_frames = ax25_payload[7:]
    tmp = []
    while dest_frames:
        tmp.append(dest_frames[:21])
        dest_frames = dest_frames[21:]
    print(f"Dest_raw: {tmp}")
    dec_neighbor_frames = []
    for el in tmp:
        dec_neighbor_frames.append(
            dict(
                dest_call=decode_ax25call(el[:7])[0],
                dest_id=el[7:13].decode('ASCII', 'ignore'),
                best_neighbor_call=decode_ax25call(el[13:20])[0],
                qual=int(el[-1])
            )
        )
    print(dec_neighbor_frames)

    monitor_str = f"NET/ROM Routing: {id_of_sending_node}\r"
    monitor_str += "Neighbors - Alias  - BestNeighbor - BestQual\r"

    for neighbor in dec_neighbor_frames:
        monitor_str += f"{neighbor['dest_call']}    - {neighbor['dest_id']} - {neighbor['best_neighbor_call']}       - {neighbor['qual']}\r"
    return monitor_str
