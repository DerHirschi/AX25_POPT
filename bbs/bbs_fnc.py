from datetime import datetime

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

    return {
        "message_type": hdr[1],
        "sender": hdr[2],
        "recipient_bbs": hdr[3],
        "receiver": hdr[4],
        "mid": mid,
        "bid_mid": hdr[5],
        "sender_bbs": recipient,
        "message_size": hdr[6]
    }


def build_new_msg_header(msg_struc: dict):
    """ Not used """
    # print("build_new_msg_header -------------")
    # print(msg_struc)
    bbs_call                 = msg_struc.get('sender_bbs', '').split('.')[0]
    bid                      = msg_struc.get('bid_mid', '')
    msg_struc['tx-time']     = datetime.now().strftime(SQL_TIME_FORMAT)
    utc                      = datetime.strptime(msg_struc['utctime'], SQL_TIME_FORMAT)
    old_header               = msg_struc.get('header', b'')
    old_path                 = msg_struc.get('path', "")
    fwd_bbs_address = msg_struc["sender_bbs"]
    if type(old_path) == str:
        old_path             = convert_sql_list(old_path)
    if not bid:
        msg_struc['bid_mid'] = f"{str(msg_struc['mid']).rjust(6, '0')}{bbs_call}"

    # _utc = datetime.utcnow()  TODO
    # msg_struc['utctime'] = _utc.strftime(SQL_TIME_FORMAT)
    # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
    # R:231101/0520z @:MD2SAW.#SAW.SAA.DEU.EU #:000003 $:000003MD2SAW

    header = (f"R:{str(utc.year)[2:].rjust(2, '0')}"
               f'{str(utc.month).rjust(2, "0")}'
               f'{str(utc.day).rjust(2, "0")}/'
               f'{str(utc.hour).rjust(2, "0")}'
               f'{str(utc.minute).rjust(2, "0")}z '
               f'@:{fwd_bbs_address} '  
               f'#:{str(msg_struc["mid"]).rjust(6, "0")} '
               f'$:{msg_struc["bid_mid"]}')
    msg_struc['header'] = old_header + header.encode('ASCII', 'ignore') + b'\r'
    old_path.append(header)
    msg_struc['path']   = old_path
    # print("build_new_msg_header ---RES------")
    # print(msg_struc)
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
    old_path.append(header)
    new_header = b''
    for line in old_path:
        new_header += line.encode('ASCII', 'ignore') + b'\r'
    msg_struc['path']   = old_path
    msg_struc['header'] = new_header
    # print("build_fwd_msg_header ---RES------")
    # print(msg_struc)
    return msg_struc

def parse_fwd_paths(path_list: list):
    # TODO: get Time from Header timecode
    """
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
    print(path_header)
    path_list = parse_fwd_paths(path_header)
    print(path_list)
    ret = []
    for path in path_list:
        bbs_address = path[0]
        bbc_call    = bbs_address.split('.')[0]
        ret.append(bbc_call)
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

