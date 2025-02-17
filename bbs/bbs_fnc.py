from datetime import datetime

from cfg.constant import BBS_SW_ID, VER, SQL_TIME_FORMAT
from cfg.logger_config import logger


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
    # print("build_new_msg_header -------------")
    bbs_call = msg_struc['sender_bbs'].split('.')[0]
    mid = msg_struc['mid']
    bid = f"{str(mid).rjust(6, '0')}{bbs_call}"
    msg_struc['tx-time'] = datetime.now().strftime(SQL_TIME_FORMAT)
    utc = datetime.strptime(msg_struc['utctime'], SQL_TIME_FORMAT)
    msg_struc['mid'] = mid
    msg_struc['bid_mid'] = bid
    # _utc = datetime.utcnow()
    # msg_struc['utctime'] = _utc.strftime(SQL_TIME_FORMAT)
    # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
    # R:231101/0520z @:MD2SAW.#SAW.SAA.DEU.EU #:000003 $:000003MD2SAW
    header = (f"R:{str(utc.year)[2:].rjust(2, '0')}"
               f'{str(utc.month).rjust(2, "0")}'
               f'{str(utc.day).rjust(2, "0")}/'
               f'{str(utc.hour).rjust(2, "0")}'
               f'{str(utc.minute).rjust(2, "0")}z '
               f'@:{msg_struc["sender_bbs"]} '
               f'#:{str(mid).rjust(6, "0")} '
               f'$:{bid}\r')
    # _header += '\r'
    # _header += f'From: {msg_struc["sender"]}@{msg_struc["sender_bbs"]}\r'
    # _header += f'To  : {msg_struc["receiver"]}@{msg_struc["recipient_bbs"]}\r'
    # _header += '\r'
    msg_struc['header'] = header.encode('ASCII', 'ignore')

    return msg_struc


def parse_fwd_paths(path_list: list):
    # TODO: get Time from Header timecode
    """
    R:231004/1739Z @:MD2BBS.#SAW.SAA.DEU.EU #:18122 [Salzwedel] $:2620_KE2BBS
    R:231004/1112Z 2620@KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23
    [['MD2BBS.#SAW.SAA.DEU.EU', 'Salzwedel] $:2620_KE2BBS'], ['KE2BBS.#KEH.BAY.DEU.EU', 'KE2BBS.#KEH.BAY.DEU.EU BPQK6.0.23']]
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
    """
    if path_str[-1].upper() != 'Z':
        print(f"TS-Parser Z not FOUND: {path_str}")
        return ''
    """
    return (
        f"{path_str[:2]}-"
        f"{path_str[2:4]}-"
        f"{path_str[4:6]} "
        f"{path_str[7:9]}:"
        f"{path_str[9:11]}:"
        "00")
