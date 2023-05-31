import aprslib

from fnc.loc_fnc import coordinates_to_locator, locator_distance


# print(aprslib.parse("M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:!/.(M4I^C,O `DXa/A=040849|#B>@\"v90!+|"))
# print(aprslib.parse("M0XER-4>APRS64:!/.(M4I^C,O `DXa/A=040849|#B>@\"v90!+|"))


def aprs_parse(ax25frame):
    aprs_msg_input = f"{ax25frame.from_call.call_str}>{ax25frame.to_call.call_str}"
    last_via = ''
    for via_call in ax25frame.via_calls:
        aprs_msg_input += f",{via_call.call_str}"
        if via_call.c_bit:
            aprs_msg_input += "*"
            last_via += f"{via_call.call_str} "
    print(aprs_msg_input)
    try:
        aprs_msg_input += f":{ax25frame.data.decode('UTF-8')}"
    except UnicodeDecodeError:
        print(f"APRS Data decoding error: {ax25frame.data}")
    try:
        aprs_msg = aprslib.parse(aprs_msg_input)
    except aprslib.UnknownFormat:
        return ''
    except aprslib.ParseError as e:
        print(e)
        print(aprs_msg_input)
        return ''
    else:
        print(aprs_msg)
        ret = ''
        dist = ''
        for k in aprs_msg:
            print(f"{k}: {aprs_msg[k]}")
            if aprs_msg[k]:
                if k not in ['from', 'to', 'via', 'path', 'raw', 'symbol_table', 'symbol']:
                    if k == 'messagecapable':
                        ret += f"APRS-{'m-capable'.ljust(13)}: {aprs_msg[k]}\n"
                    if k == 'gpsfixstatus':
                        ret += f"APRS-{'gpsfix'.ljust(13)}: {aprs_msg[k]}\n"
                    if k == 'text':
                        ret += f"APRS-{k.ljust(13)}:\n{aprs_msg[k]}\n"
                    else:
                        ret += f"APRS-{k.ljust(13)}: {aprs_msg[k]}\n"
                    if k == 'telemetry':
                        ret += f"APRS-{k.ljust(13)}:\n"
                        for tele_k in aprs_msg[k].keys():
                            ret += f"APRS-{k.ljust(13)}-{tele_k.ljust(4)}: {aprs_msg[k][tele_k]}\n"
                    if k == 'longitude':
                        loc = coordinates_to_locator(latitude=aprs_msg['latitude'],
                                                     longitude=aprs_msg['longitude'])
                        dist = locator_distance('JO52NU', loc)
                        ret += f"APRS-Locator      : {loc}\n"
                        ret += f"APRS-Distance     : {dist} km\n"

        if ret:
            ret = ret.replace('\r', '\n')
            if len(ret) > 1:
                if ret[-2:] == '\n\n':
                    ret = ret[:-1]

            via_str = ''
            if last_via:
                via_str = f" via {last_via}"
            if dist:
                dist = f" ({dist} km)"
            ret = f'APRS:         : {ax25frame.from_call.call_str}{dist}{via_str}\n' + ret

        return ret

