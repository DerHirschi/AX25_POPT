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
    symbol = '  '
    ret, dist = format_aprs_msg(aprs_msg, own_locator, aprs_msg)
    if 'subpacket' in aprs_msg.keys():
        ret += '├►SUBPACKET    :\n' + format_aprs_msg(aprs_msg['subpacket'], own_locator, aprs_msg)[0]
    if 'weather' in aprs_msg.keys():
        ret += '├►WEATHER ☀☁   :\n' + format_aprs_msg(aprs_msg['weather'], own_locator, aprs_msg)[0]
        symbol = '☀☁'
    if 'format' in aprs_msg.keys():
        if 'message' == aprs_msg['format']:
            # symbol = '✉  '
            symbol = ' ＠'
        if 'telemetry-message' == aprs_msg['format']:
            # symbol = ' ℡'
            symbol = ' ☍'
        if 'telemetry' == aprs_msg['format']:
            symbol = ' ☍'
        if 'beacon' == aprs_msg['format']:
            symbol = ' ▣'
        if 'wx' == aprs_msg['format']:
            symbol = '☀☁'
        if 'object' == aprs_msg['format']:
            symbol = ' ✚'
        if 'status' == aprs_msg['format']:
            symbol = ' ۩'

    if ret:

        if 'text' in aprs_msg.keys():
            if aprs_msg['text']:
                if aprs_msg['text'][0] == '\n':
                    ret += f"└┬►TEXT\n ▽{aprs_msg['text']}\n"
                else:
                    ret += f"└┬►TEXT\n ▽\n{aprs_msg['text']}\n"
            else:
                ret += f"└─►TEXT        : n/a\n"
        elif 'comment' in aprs_msg.keys():
            if aprs_msg['comment']:
                if aprs_msg['comment'][0] == '\n':
                    ret += f"└┬►COMMENT\n ▽{aprs_msg['comment']}\n"
                else:
                    ret += f"└┬►COMMENT\n ▽\n{aprs_msg['comment']}\n"
            else:
                ret += f"└─►COMMENT     : n/a\n"


        ret = ret.replace('\r', '\n')
        if len(ret) > 1:
            if ret[-2:] == '\n\n':
                ret = ret[:-1]

        last_via = ''
        for el in aprs_msg['path']:
            if '*' in el:
                via_dis = USER_DB.get_distance(el[:-1])
                if via_dis:
                    last_via += f"{el[:-1]}({via_dis} km)"
                else:
                    last_via += f"{el[:-1]} "

        via_str = ''
        if last_via:
            via_str = f" via {last_via}"
        if dist:
            dist = f" ({dist} km)"
        else:
            dist = ''
        ret = f'┌──┴─▶APRS :{symbol} : {ax25frame.from_call.call_str}{dist}{via_str}\n' + ret

    return ret


def format_aprs_msg(aprs_frame: aprslib.parse, own_locator, full_aprs_frame: aprslib.parse):
    ret = ''
    dist = ''
    db_ent = USER_DB.get_entry(full_aprs_frame['from'])
    for k in aprs_frame:
        # print(f"{k}: {aprs_frame[k]}")
        if aprs_frame[k]:
            if k not in ['from', 'to', 'via', 'path', 'raw', 'symbol_table', 'symbol', 'subpacket', 'weather']:
                if k == 'messagecapable':
                    ret += f"├►{'m-capable'.upper().ljust(13)}: {aprs_frame[k]}\n"
                elif k == 'gpsfixstatus':
                    ret += f"├►{'gpsfix'.upper().ljust(13)}: {aprs_frame[k]}\n"
                    """
                    if k in ['text', 'comment']:
                        if aprs_frame[k][0] == '\n':
                            ret += f"└┬►{k.upper()}\n ▽{aprs_frame[k]}\n"
                        else:
                            ret += f"└┬►{k.upper()}\n ▽\n{aprs_frame[k]}\n"
                    else:
                    """

                elif k == 'telemetry':
                    ret += f"├►{k.upper().ljust(13)}:\n"
                    for tele_k in aprs_frame[k].keys():
                        ret += f"├►{k.upper().ljust(13)}-{tele_k.ljust(4)}: {aprs_frame[k][tele_k]}\n"
                elif k == 'longitude':
                    loc = coordinates_to_locator(latitude=aprs_frame['latitude'],
                                                 longitude=aprs_frame['longitude'])
                    ret += f"├►LOCATOR      : {loc}\n"
                    if db_ent:
                        if not db_ent.LOC:
                            db_ent.LOC = loc
                        if not db_ent.Lat:
                            db_ent.Lat = aprs_frame['latitude']
                            db_ent.Lon = aprs_frame['longitude']
                    if own_locator:
                        dist = locator_distance(own_locator, loc)
                        ret += f"├►DISTANCE     : {dist} km\n"
                    if db_ent:
                        db_ent.Distance = dist
                elif k in ['tPARM', 'tUNIT', 'tEQNS']:
                    ret += f"└┬►{k.upper().ljust(13)}\n"
                    for ind in range(len(aprs_frame[k])):
                        el = aprs_frame[k][ind]
                        if ind + 1 < len(aprs_frame[k]):
                            ret += f" ├► {el}\n"
                        else:
                            ret += f" └► {el}\n"
                elif k in ['text', 'comment']:
                    pass
                else:
                    ret += f"├►{k.upper().ljust(13)}: {aprs_frame[k]}\n"
    if db_ent:
        # if not db_ent.Distance:
        if db_ent.LOC:
            db_ent.Distance = locator_distance(own_locator, db_ent.LOC)
            dist = locator_distance(own_locator, db_ent.LOC)

    return ret, dist



