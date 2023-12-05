import aprslib
from UserDB.UserDBmain import USER_DB
from fnc.loc_fnc import coordinates_to_locator, locator_distance


def parse_aprs_fm_ax25frame(ax25frame):
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
        return aprslib.parse(aprs_msg_input)
    except aprslib.UnknownFormat:
        return {}
    except aprslib.ParseError as e:
        return {}


def parse_aprs_fm_aprsframe(aprs_frame):
    try:
        return aprslib.parse(aprs_frame)
    except aprslib.UnknownFormat:
        return {}
    except aprslib.ParseError as e:
        # print(e)
        # print(aprs_msg_input)
        return {}


def format_aprs_f_aprs_mon(aprs_frame, own_locator, add_new_user=False):
    # aprs_frame = "12:12:21", aprs_frame
    ret = f"{aprs_frame['rx_time'].strftime('%d/%m/%y %H:%M:%S')}: {aprs_frame['from']} to {aprs_frame['to']}"
    if aprs_frame['path']:
        ret += " via " + ' '.join(aprs_frame['path'])
    ret += ":\n"

    msg = format_aprs_f_monitor(aprs_pack=aprs_frame, own_locator=own_locator, add_new_user=add_new_user)

    return ret + msg + '\n'


def format_aprs_f_monitor(ax25frame=None, own_locator='', aprs_pack=None, add_new_user=True):
    if ax25frame is not None:
        if ax25frame.ctl_byte.flag != 'UI':
            return ''
        aprs_msg = parse_aprs_fm_ax25frame(ax25frame)
    elif aprs_pack is not None:
        aprs_msg = aprs_pack
    else:
        return ''
    if not aprs_msg:
        return ''
    # print(aprs_msg)
    symbol = '  '
    ret, dist = format_aprs_msg(aprs_msg, own_locator, aprs_msg, add_new_user=add_new_user)
    if 'subpacket' in aprs_msg.keys():
        ret += '├►SUBPACKET    :\n' + format_aprs_msg(aprs_msg['subpacket'], own_locator, aprs_msg, add_new_user=add_new_user)[0]
    if 'weather' in aprs_msg.keys():
        ret += '├►WEATHER ☀☁   :\n' + format_aprs_msg(aprs_msg['weather'], own_locator, aprs_msg, add_new_user=add_new_user)[0]
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
        elif 'status' in aprs_msg.keys():
            ret += f"└►STATUS       : {aprs_msg['status']}\n"

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
        ret = f"┌──┴─▶APRS :{symbol} : {aprs_msg['from']}{dist}{via_str}\n" + ret
    # print(ret)
    return ret


def format_aprs_msg(aprs_frame: aprslib.parse, own_locator, full_aprs_frame: aprslib.parse, add_new_user=True):
    ret = ''
    dist = ''
    typ = ''
    loc = ''
    for k in aprs_frame:
        if aprs_frame[k]:
            # if k not in ['from', 'to',  'symbol_table', 'symbol', 'subpacket', 'weather']:
            if k not in ['from', 'to', 'raw', 'symbol_table', 'symbol', 'subpacket', 'weather']:
                if k == 'via':
                    if aprs_frame[k]:
                        ret += f"├►{k.upper().ljust(13)}: {aprs_frame[k]}\n"
                elif k == 'path':
                    ret += f"├►{'PATH'.ljust(13)}: {' '.join(aprs_frame[k])}\n"
                elif k == 'messagecapable':
                    ret += f"├►{'M-CAPABLE'.ljust(13)}: {aprs_frame[k]}\n"
                elif k == 'gpsfixstatus':
                    ret += f"├►{'GPS-FIX'.ljust(13)}: {aprs_frame[k]}\n"
                    """
                    if k in ['text', 'comment']:
                        if aprs_frame[k][0] == '\n':
                            ret += f"└┬►{k.upper()}\n ▽{aprs_frame[k]}\n"
                        else:
                            ret += f"└┬►{k.upper()}\n ▽\n{aprs_frame[k]}\n"
                    else:
                    """

                elif k == 'telemetry':
                    typ = "APRS-TELEMETRIE"
                    ret += f"├►{k.upper().ljust(13)}:\n"
                    for tele_k in aprs_frame[k].keys():
                        ret += f"├►{k.upper().ljust(13)}-{tele_k.ljust(4)}: {aprs_frame[k][tele_k]}\n"
                elif k == 'longitude':
                    ret += f"├►{k.upper().ljust(13)}: {aprs_frame[k]}\n"
                    loc = coordinates_to_locator(latitude=aprs_frame['latitude'],
                                                 longitude=aprs_frame['longitude'])
                    ret += f"├►LOCATOR      : {loc}\n"

                    if own_locator and loc:
                        dist = locator_distance(own_locator, loc)
                        ret += f"├►DISTANCE     : {dist} km\n"
                    # if db_ent:
                    #     db_ent.Distance = dist
                elif k in ['tPARM', 'tUNIT', 'tEQNS']:
                    typ = "APRS-TELEMETRIE"
                    ret += f"└┬►{k.upper().ljust(13)}\n"
                    for ind in range(len(aprs_frame[k])):
                        el = aprs_frame[k][ind]
                        if ind + 1 < len(aprs_frame[k]):
                            ret += f" ├► {el}\n"
                        else:
                            ret += f" └► {el}\n"
                elif k in ['text', 'comment', 'status']:
                    pass
                else:
                    ret += f"├►{k.upper().ljust(13)}: {aprs_frame[k]}\n"
        if k in ['weather', 'wx']:
            typ = 'APRS-WX'

    if loc:
        db_ent = USER_DB.get_entry(full_aprs_frame.get('from', ''), add_new=add_new_user)
        if db_ent:
            db_ent.LOC = loc
            db_ent.Lat = aprs_frame['latitude']
            db_ent.Lon = aprs_frame['longitude']
            if type(dist) == float:
                db_ent.Distance = float(dist)
            if not db_ent.TYP and typ:
                db_ent.TYP = typ

    return ret, dist


def extract_ack(text):
    start_index = text.find('{')  # Finde den Index der ersten öffnenden Klammer
    end_index = text.find('}')    # Finde den Index der ersten schließenden Klammer

    if start_index == -1 or end_index == -1:  # Überprüfe, ob beide Klammern im String vorhanden sind
        return text, None

    value = text[start_index + 1:end_index]  # Extrahiere den Wert zwischen den Klammern
    if start_index > 0:  # Überprüfe, ob es Text vor der öffnenden Klammer gibt
        text_before = text[:start_index]  # Extrahiere den Text vor der öffnenden Klammer
        return text_before, value

    return '', value


def get_last_digi_fm_path(pack: dict):
    _path = pack.get('path', [])
    _res = ''
    for _call in _path:
        if _call[-1] == '*':
            _res = _call[:-1]
    return _res

