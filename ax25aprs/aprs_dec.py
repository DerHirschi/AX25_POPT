import aprslib

from UserDB.UserDBmain import USER_DB
from fnc.loc_fnc import coordinates_to_locator, locator_distance


# print(aprslib.parse("M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:!/.(M4I^C,O `DXa/A=040849|#B>@\"v90!+|"))
# print(aprslib.parse("M0XER-4>APRS64:!/.(M4I^C,O `DXa/A=040849|#B>@\"v90!+|"))

def parse_aprs_msg(ax25frame):
    aprs_msg_input = f"{ax25frame.from_call.call_str}>{ax25frame.to_call.call_str}"
    for via_call in ax25frame.via_calls:
        aprs_msg_input += f",{via_call.call_str}"
        if via_call.c_bit:
            aprs_msg_input += "*"
    # print(aprs_msg_input)
    try:
        aprs_msg_input += f":{ax25frame.data.decode('UTF-8')}"
    except UnicodeDecodeError:
        # print(f"APRS Data decoding error: {ax25frame.data}")
        return {}
    try:
        aprs_msg = aprslib.parse(aprs_msg_input)
    except aprslib.UnknownFormat:
        return {}
    except aprslib.ParseError as e:
        # print(e)
        # print(aprs_msg_input)
        return {}
    else:
        return aprs_msg


def format_aprs_f_monitor(ax25frame, own_locator):
    if not ax25frame.aprs_data:
        return ''
    aprs_msg = ax25frame.aprs_data
    # print(aprs_msg)
    ret, dist = format_aprs_msg(aprs_msg, own_locator)
    if 'subpacket' in aprs_msg.keys():
        ret += 'APRS-subpacket    :\n' + format_aprs_msg(aprs_msg['subpacket'], own_locator)[0]
    if 'weather' in aprs_msg.keys():
        ret += 'APRS-weather      :\n' + format_aprs_msg(aprs_msg['weather'], own_locator)[0]

    if ret:
        ret = ret.replace('\r', '\n')
        if len(ret) > 1:
            if ret[-2:] == '\n\n':
                ret = ret[:-1]

        last_via = ''
        for el in aprs_msg['path']:
            if '*' in el:
                last_via += f"{el[:-1]} "
        if last_via:
            via_str = f" via {last_via}"
        else:
            via_str = ''
        if dist:
            dist = f" ({dist} km)"
        ret = f'APRS              : {ax25frame.from_call.call_str}{dist}{via_str}\n' + ret

    return ret


def format_aprs_msg(aprs_frame: aprslib.parse, own_locator):
    ret = ''
    dist = ''
    db_ent = USER_DB.new_entry(aprs_frame['from'])
    for k in aprs_frame:
        # print(f"{k}: {aprs_frame[k]}")
        if aprs_frame[k]:
            if k not in ['from', 'to', 'via', 'path', 'raw', 'symbol_table', 'symbol', 'subpacket', 'weather']:
                if k == 'messagecapable':
                    ret += f"APRS-{'m-capable'.ljust(13)}: {aprs_frame[k]}\n"
                if k == 'gpsfixstatus':
                    ret += f"APRS-{'gpsfix'.ljust(13)}: {aprs_frame[k]}\n"
                if k == 'text':
                    ret += f"APRS-{k.ljust(13)}:\n{aprs_frame[k]}\n"
                else:
                    ret += f"APRS-{k.ljust(13)}: {aprs_frame[k]}\n"
                if k == 'telemetry':
                    ret += f"APRS-{k.ljust(13)}:\n"
                    for tele_k in aprs_frame[k].keys():
                        ret += f"APRS-{k.ljust(13)}-{tele_k.ljust(4)}: {aprs_frame[k][tele_k]}\n"
                if k == 'longitude':
                    loc = coordinates_to_locator(latitude=aprs_frame['latitude'],
                                                 longitude=aprs_frame['longitude'])
                    ret += f"APRS-Locator      : {loc}\n"
                    if db_ent:
                        db_ent.LOC = loc
                        db_ent.Lat = aprs_frame['latitude']
                        db_ent.Lon = aprs_frame['longitude']
                    if own_locator:
                        dist = locator_distance(own_locator, loc)
                        ret += f"APRS-Distance     : {dist} km\n"
                        if db_ent:
                            db_ent.Distance = dist
    return ret, dist



