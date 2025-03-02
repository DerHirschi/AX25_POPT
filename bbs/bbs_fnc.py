import re
from datetime import datetime

from bbs.bbs_constant import GET_MSG_STRUC, STAMP, MSG_ID, STAMP_BID, STAMP_MSG_NUM
from cfg.constant import BBS_SW_ID, VER, SQL_TIME_FORMAT
from cfg.logger_config import logger
from fnc.sql_fnc import convert_sql_list


def generate_sid(features=("F", "M", "H")):
    """
    EXAMPLE: [ZFJ - 2.3 - H$]
    """
    # Format the FEATURE_LIST
    formatted_feature_list = "".join(features)
    # Generate the SID
    sid = f"[{BBS_SW_ID}-{VER}-{formatted_feature_list}$]"

    return sid


def parse_forward_header(header):
    # FB P MD2BBS MD2SAW MD2SAW 18243-MD2BBS 502
    # FB P MD2BBS MD2SAW MD2SAW 18245-MD2BBS 502
    # FB P MD2BBS MD2SAW MD2SAW 18248-MD2BBS 502
    # FB B DBO527 SAW STATUS 4CWDBO527004 109836
    # FB B MD2SAW SAW TEST 11139-MD2BBS 5
    hdr = header.split(' ')
    if len(hdr) != 7:
        logger.debug(f"PH!!: {header}")
        return None
    if hdr[0] != 'FB':
        logger.debug(f"PH!!: {header}")
        return None
    if hdr[1] not in ['P', 'B']:
        logger.debug(f"PH!!: {header}")
        return None

    tmp = hdr[5].split('-')
    mid = tmp[0]
    recipient = ''
    if len(tmp) == 2:
        recipient = tmp[1]
    msg_struc = GET_MSG_STRUC()
    msg_struc.update({
        "message_type": hdr[1],
        "sender": hdr[2],
        "recipient_bbs": hdr[3],
        "receiver": hdr[4],
        "mid": mid,
        "bid_mid": hdr[5],
        "sender_bbs": recipient,
        "message_size": hdr[6]
    })
    return msg_struc


def build_fwd_msg_header(msg_struc: dict, fwd_bbs_address: str):
    # print("build_fwd_msg_header -------------")
    # print(msg_struc)
    bbs_address              = fwd_bbs_address
    bbs_call                 = bbs_address.split('.')[0]
    bid                      = msg_struc.get('bid_mid', '')
    msg_struc['tx-time']     = datetime.now().strftime(SQL_TIME_FORMAT)
    utc                      = datetime.strptime(msg_struc['utctime'], SQL_TIME_FORMAT)
    # old_header               = msg_struc.get('header', b'')
    old_path                 = msg_struc.get('path', "")
    if type(old_path) == str:
        old_path             = convert_sql_list(old_path)
    if not bid:
        msg_struc['bid_mid'] = f"{str(msg_struc['mid']).rjust(6, '0')}{bbs_call}"

    # _utc = datetime.datetime.now(datetime.UTC)
    # msg_struc['utctime'] = _utc.strftime(SQL_TIME_FORMAT)
    # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
    # R:231101/0520z @:MD2SAW.#SAW.SAA.DEU.EU #:000003 $:000003MD2SAW

    header = (f"R:{str(utc.year)[2:].rjust(2, '0')}"
               f'{str(utc.month).rjust(2, "0")}'
               f'{str(utc.day).rjust(2, "0")}/'
               f'{str(utc.hour).rjust(2, "0")}'
               f'{str(utc.minute).rjust(2, "0")}z '
               f'@:{bbs_address} '  
               f'#:{str(msg_struc["mid"]).rjust(6, "0")} '
               f'$:{msg_struc["bid_mid"]}')
    # msg_struc['header'] = old_header + header.encode('ASCII', 'ignore') + b'\r'
    old_path = [header] + old_path
    new_header = b''
    for line in old_path:
        new_header += line.encode('ASCII', 'ignore') + b'\r'
    msg_struc['path']   = old_path
    msg_struc['header'] = new_header
    # print("build_fwd_msg_header ---RES------")
    # print(msg_struc)
    return msg_struc

def parse_fwd_paths(path_list: list):
    """
    For FWD Route Tab
    R:231004/1739Z @:MD2BBS.#SAW.SAA.DEU.EU #:18122 [Salzwedel] $:2620_KE2BBS
    R:231004/1112Z 2620@KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23
    :return [['MD2BBS.#SAW.SAA.DEU.EU', 'Salzwedel] $:2620_KE2BBS'], ['KE2BBS.#KEH.BAY.DEU.EU', 'KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23']]
    """
    path = []
    for line in path_list:
        if "R:" in line:
            if "@" in line:
                # print(line + "\n")
                tmp = line.split("@")[-1]
                add = tmp.split(" ")[0].replace(":", "")
                if '[' and ']' in tmp:
                    path.append((add, tmp.split(" [")[-1].split("]")[0]))
                else:
                    path.append((add,))
                """
                path.append([line.split("@")[-1].split(" ")[0].replace(":", ""),
                             line.split("@")[-1].split(" [")[-1]])
                """
    # print(path)
    return path

def parse_path_line(path_line: bytes):
    """
    R:231004/1739Z @:MD2BBS.#SAW.SAA.DEU.EU #:18122 [Salzwedel] $:2620_KE2BBS
    R:231004/1112Z 2620@KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23

    R:230303/1415Z @:MD2BBS.#SAW.SAA.DEU.EU #:12174 [Salzwedel]         $:14786_GY3SAL
    R:230303/1401z @:VB1BOX.#SAX.DEU.EU                                 $:14786_GY3SAL
    R:230303/1330Z @:NL3VKL.NBO.NLD.EU      #:6636 [Uden]               $:14786_GY3SAL
    R:230303/1327Z @:NL3PRC.NH.NLD.EU       #:4448 [Den Helder JO22JX]  $:14786_GY3SAL
    R:230303/1323Z @:GY1BBS.ZL.NLD.EU       #:328 [ST ANNALAND] FBB7.01.35 alpha   # No BID ???
    """
    if not path_line.startswith(STAMP):
        return {}
    path_str    = path_line.decode('ASCII', 'ignore')
    path_data   = path_line.split(b' ')
    try:
        time_stamp                  = parse_path_timestamp( path_data[0] )
        bid, bbs_call, bbs_address  = parse_path_host(      path_data[1] )
        mid                         = parse_path_mid(       path_data[2] )
        flagged_bid                 = parse_path_bid(       path_data[-1])
    except IndexError:
        logger.error(f"parse_path_line IndexError path_data: {path_data}")
        return {}
    if not bid and flagged_bid:
        bid = flagged_bid

    if bid != flagged_bid:
        logger.warning(f"parse_path_line found two BIDs in Stamp. {path_line}")
        logger.warning(f"flagged_bid != bid. {flagged_bid} != {bid}")
        logger.warning(f"Using $:flagged_bid as bid: {flagged_bid}")
        bid = flagged_bid
    if not bid:
        logger.warning(f"parse_path_line no BID found !. {path_line}")
        logger.info(f"Try to Build BID fm MSG-ID and BBS-CALL. {mid}_{bbs_call}")
        if not mid or not bbs_call:
            logger.error(f"parse_path_line can't build BID !. {path_line}")
        else:
            bid = MSG_ID(mid, bbs_call)
            logger.info(f"Build BID: {bid}")

    return dict(
        path_str        = path_str,
        time_stamp      = time_stamp,
        bid             = bid,
        mid             = mid,
        bbs_call        = bbs_call,
        bbs_address     = bbs_address,
    )

def parse_path_timestamp(path_line: bytes):
    if not path_line.startswith(STAMP):
        return ""
    path_line   = path_line.replace(STAMP, b'')
    path_str    = path_line.decode('ASCII', 'ignore')
    dt_year     = str(datetime.now().year)
    return (
        f"{dt_year[:2]}{path_str[:2]}-"
        f"{path_str[2:4]}-"
        f"{path_str[4:6]} "
        f"{path_str[7:9]}:"
        f"{path_str[9:11]}:"
        "00")

def parse_path_host(path_line: bytes):
    path_line = path_line.decode('ASCII', 'ignore')
    if not '@' in path_line:
        return '', '', ''
    bid, bbs_call, bbs_address     = '', '', ''
    tmp     = path_line.split('@')
    if tmp[0]:
        bid = tmp[0]
    bbs_address = tmp[1]
    if bbs_address.startswith(':'):
        bbs_address = bbs_address[1:]
    bbs_call = bbs_address.split('.')[0]
    if bid:
        bid = MSG_ID(bid, bbs_call)

    return bid, bbs_call, bbs_address

def parse_path_bid(path_line: bytes):
    if STAMP_BID not in path_line:
        return ''
    bid = path_line.split(STAMP_BID)[-1].decode('ASCII', 'ignore')
    return bid

def parse_path_mid(path_line: bytes):
    if not STAMP_MSG_NUM in path_line:
        return ''
    mid = path_line.split(STAMP_MSG_NUM)[-1].decode('ASCII', 'ignore')
    return mid

def parse_header_timestamp(path_str: str):
    if path_str[:2] != 'R:':
        logger.debug(f"TS-Parser R not FOUND: {path_str}")
        return ''
    path_str = path_str[2:].split(' ')[0]
    dt_year = str(datetime.now().year)
    return (
        f"{dt_year[:2]}{path_str[:2]}-"
        f"{path_str[2:4]}-"
        f"{path_str[4:6]} "
        f"{path_str[7:9]}:"
        f"{path_str[9:11]}:"
        "00")

def get_pathlist_fm_header(path_header: list):
    # print(path_header)
    path_list = parse_fwd_paths(path_header)
    # print(path_list)
    ret = []
    for path in path_list:
        bbs_address = path[0]
        bbs_call    = bbs_address.split('.')[0]
        ret.append(bbs_call)
    return ret

def spilt_regio(bbs_address: str):
    temp = bbs_address.split('.')
    ret = []
    for el in temp:
        if el.startswith('#'):
            ret.append(el[1:])
        else:
            ret.append(el)
    return ret[1:]

def extract_wp_data(wp_data: str):
    """
    TODO: by myself
    By: Grok-3 beta (x.com)
    Extrahiert strukturierte Daten aus WP-Datenbank-Einträgen.
    Args:
        wp_data (str): Roher WP-Datenbank-Text

    Returns:
        List[Dict]: Liste mit extrahierten Einträgen
    """
    # Ergebnis-Liste
    entries = []

    # Regex-Muster für die Hauptbestandteile
    pattern = r"On (\d{6})\s+([A-Z0-9]+)\s+@\s+([A-Z0-9.#]+)\s*(zip\s+(D-\d+|\?)?)?\s*([^@]+)?$"
    grid_pattern = r'\[?[A-R]{2}\d{2}[A-X]{0,2}\]?'

    # Zeilen aufteilen und "[ From WP @ MD2BBS ]" ignorieren
    lines = [line.strip() for line in wp_data.split('\r') if line.strip() and not line.startswith('[')]

    for line in lines:
        # print(line)
        match = re.match(pattern, line)
        if match:
            # Extrahierte Gruppen
            date_str, callsign, host, _, zip_code, additional_info = match.groups()

            # Datum parsen (Format: YYMMDD)
            try:
                date = datetime.strptime(date_str, '%y%m%d')
                # Falls Jahr < 2000, nehmen wir an, es ist 20XX statt 19XX
                if date.year < 2000:
                    date = date.replace(year=date.year + 100)
            except ValueError:
                date = None

            # Zusätzliche Informationen aufteilen
            location    = ""
            grid        = ""
            name        = ""

            if additional_info:
                # Grid-Square (JO/JN + 4 Zeichen) suchen
                grid_match = re.search(grid_pattern, additional_info)
                if grid_match:
                    grid = grid_match.group()

                # Restliche Infos aufteilen
                info_parts = additional_info.split()
                remaining_parts = [part for part in info_parts if not part == grid]

                # Name und Location extrahieren
                if remaining_parts:
                    # Letzter Teil könnte der Standort sein
                    location = remaining_parts[-1]
                    # Alles davor könnte der Name sein
                    if len(remaining_parts) > 1:
                        name = " ".join(remaining_parts[:-1])
                    elif len(remaining_parts) == 1 and not grid:
                        name = remaining_parts[0]

            # Strukturierten Eintrag erstellen
            ret = {
                "date":         date,
                "callsign":     callsign,
                "host":         host,
                "zip_code":     zip_code if zip_code else None,
                "name":         name.strip() if name.strip() else None,
                "location":     location.strip() if location.strip() else None,
                "grid":         grid if grid else None
            }
            entries.append(ret)

    return entries

if __name__ == '__main__':

    pass