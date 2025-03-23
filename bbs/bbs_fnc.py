import re
from datetime import datetime

from bbs.bbs_constant import GET_MSG_STRUC, STAMP, MSG_ID, STAMP_BID, STAMP_MSG_NUM, CR, EOL, MSG_H_TO, SP, MSG_H_FROM
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

def find_eol(msg: bytes):
    # Find EOL Syntax
    for tmp_eol in EOL:
        if tmp_eol in msg:
            return tmp_eol
    return CR

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
    # if hdr[0] not in ['FB', 'FA']:
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
        "message_type":     hdr[1],
        "sender":           hdr[2],
        "recipient_bbs":    hdr[3],
        "receiver":         hdr[4],
        "mid":              mid,
        "bid_mid":          hdr[5],
        "sender_bbs":       recipient,
        "message_size":     hdr[6]
    })
    return msg_struc

def build_msg_header(msg_struc: dict, fwd_bbs_address: str):
    # print("build_fwd_msg_header -------------")
    # print(msg_struc)
    bbs_address              = fwd_bbs_address
    bbs_call                 = bbs_address.split('.')[0]
    bid                      = msg_struc.get('bid_mid', '')
    msg_struc['tx-time']     = datetime.now().strftime(SQL_TIME_FORMAT)
    utc                      = datetime.strptime(msg_struc['utctime'], SQL_TIME_FORMAT)
    subject                  = msg_struc.get('subject', '')
    old_header               = msg_struc.get('header', b'')
    old_path                 = msg_struc.get('path', "")
    from_call                = msg_struc.get('sender', "")
    from_bbs                 = msg_struc.get('sender_bbs', "")
    to_call                  = msg_struc.get('receiver', "")
    to_bbs                   = msg_struc.get('recipient_bbs', "")

    from_address    = f"{from_call}@{from_bbs}"
    to_address      = f"{to_call}@{to_bbs}"
    if type(old_path) == str:
        old_path             = convert_sql_list(old_path)
    if not bid:
        msg_struc['bid_mid'] = f"{str(msg_struc['mid']).rjust(6, '0')}{bbs_call}"

    # _utc = datetime.datetime.now(datetime.UTC)
    # msg_struc['utctime'] = _utc.strftime(SQL_TIME_FORMAT)
    # R:231101/0101Z @:MD2BBS.#SAW.SAA.DEU.EU #:18445 [Salzwedel] $:18445-MD2BBS
    # R:231101/0520z @:MD2SAW.#SAW.SAA.DEU.EU #:000003 $:000003MD2SAW

    stamp = (f"R:{str(utc.year)[2:].rjust(2, '0')}"
               f'{str(utc.month).rjust(2, "0")}'
               f'{str(utc.day).rjust(2, "0")}/'
               f'{str(utc.hour).rjust(2, "0")}'
               f'{str(utc.minute).rjust(2, "0")}z '
               f'@:{bbs_address} '  
               f'#:{str(msg_struc["mid"]).rjust(6, "0")} '
               f'$:{msg_struc["bid_mid"]}')
    # msg_struc['header'] = old_header + header.encode('ASCII', 'ignore') + b'\r'
    old_path = [stamp] + old_path
    """
    new_header = (header_lines[0] +
                  eol +
                  stamp.encode('ASCII', 'ignore') +
                  eol +
                  eol.join(header_lines[1:]))
    """
    if not old_header:
        new_header = subject.encode('ASCII', 'ignore') + CR
        for line in old_path:
            if not line:
                continue
            new_header += line.encode('ASCII', 'ignore') + CR
        new_header += CR
        new_header += MSG_H_FROM[0] + SP + from_address.encode('ASCII', 'ignore') + CR
        new_header += MSG_H_TO[1]   + SP + to_address.encode('ASCII', 'ignore') + CR
        new_header += CR

    else:
        eol = find_eol(old_header)
        header_lines = old_header.split(eol)
        new_header = header_lines[0] + eol
        new_header += stamp.encode('ASCII', 'ignore') + eol
        new_header += eol.join(header_lines[1:])

    msg_struc['path']   = old_path
    msg_struc['header'] = new_header
    """
    print("build_fwd_msg_header ---RES------")
    print(f"Old Header : {old_header}")
    print(f"New Header : {new_header}")
    """
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


class LZHDecoder:
    """ By Grok 3 beta (x.com) """
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.getbuf = 0
        self.getlen = 0
        self.N = 2048
        self.F = 60
        self.THRESHOLD = 2
        self.text_buf = bytearray(b' ' * (self.N - self.F))
        self.r = self.N - self.F

        self.d_code = bytearray([
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
            0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
            0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
            0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
            0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
            0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09,
            0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B, 0x0B,
            0x0C, 0x0C, 0x0C, 0x0C, 0x0D, 0x0D, 0x0D, 0x0D, 0x0E, 0x0E, 0x0E, 0x0E, 0x0F, 0x0F, 0x0F, 0x0F,
            0x10, 0x10, 0x10, 0x10, 0x11, 0x11, 0x11, 0x11, 0x12, 0x12, 0x12, 0x12, 0x13, 0x13, 0x13, 0x13,
            0x14, 0x14, 0x14, 0x14, 0x15, 0x15, 0x15, 0x15, 0x16, 0x16, 0x16, 0x16, 0x17, 0x17, 0x17, 0x17,
            0x18, 0x18, 0x19, 0x19, 0x1A, 0x1A, 0x1B, 0x1B, 0x1C, 0x1C, 0x1D, 0x1D, 0x1E, 0x1E, 0x1F, 0x1F,
            0x20, 0x20, 0x21, 0x21, 0x22, 0x22, 0x23, 0x23, 0x24, 0x24, 0x25, 0x25, 0x26, 0x26, 0x27, 0x27,
            0x28, 0x28, 0x29, 0x29, 0x2A, 0x2A, 0x2B, 0x2B, 0x2C, 0x2C, 0x2D, 0x2D, 0x2E, 0x2E, 0x2F, 0x2F,
            0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F
        ])
        self.d_len = bytearray([
            0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
            0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03,
            0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
            0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
            0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
            0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
            0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
            0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
            0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
            0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
            0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06, 0x06,
            0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
            0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
            0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07, 0x07,
            0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08
        ])

        self.start_huff()

    def get_bit(self):
        while self.getlen <= 8:
            if self.pos < len(self.data):
                i = self.data[self.pos]
                print(f"Reading byte at pos={self.pos}: 0x{i:02x}")
                self.pos += 1
            else:
                i = 0
            self.getbuf |= i << self.getlen
            self.getlen += 8
        i = self.getbuf & 1
        self.getbuf >>= 1
        self.getlen -= 1
        return i

    def get_byte(self):
        while self.getlen <= 8:
            if self.pos < len(self.data):
                i = self.data[self.pos]
                print(f"Reading byte at pos={self.pos}: 0x{i:02x}")
                self.pos += 1
            else:
                i = 0
            self.getbuf |= i << self.getlen
            self.getlen += 8
        i = self.getbuf & 0xff
        self.getbuf >>= 8
        self.getlen -= 8
        return i

    def start_huff(self):
        N_CHAR = 256 - self.THRESHOLD + self.F  # 314
        T = N_CHAR * 2 - 1  # 627
        R = T - 1  # 626
        self.freq = [1] * N_CHAR + [0] * (T - N_CHAR + 1)
        self.fils = list(range(N_CHAR, N_CHAR + T + 1)) + [0] * (T - N_CHAR)
        self.prnt = [0] * N_CHAR + list(range(N_CHAR)) + [0] * (T - N_CHAR + 1)

        i, j = 0, N_CHAR
        while j <= R:
            self.freq[j] = self.freq[i] + self.freq[i + 1]
            self.fils[j] = i
            self.prnt[i] = self.prnt[i + 1] = j
            i += 2
            j += 1
        self.freq[T] = 0xffff
        self.prnt[R] = 0

    def update(self, c):
        MAX_FREQ = 0x8000
        if self.freq[626] >= MAX_FREQ:
            pass  # Vereinfacht
        c = self.prnt[c + 627]
        while c != 0:
            self.freq[c] += 1
            c = self.prnt[c]

    def decode_char(self):
        c = self.fils[626]  # R
        while c < 627:  # T
            bit = self.get_bit()
            if c + bit >= len(self.fils):
                raise ValueError(f"Ungültiger Huffman-Code: c={c}, bit={bit}, fils_len={len(self.fils)}")
            c = self.fils[c + bit]
        c -= 627
        self.update(c)
        return c

    def decode_position(self):
        i = self.get_byte()
        c = self.d_code[i] << 6
        j = self.d_len[i] - 2
        while j > 0:
            i = (i << 1) | self.get_bit()
            j -= 1
        return c | (i & 0x3f)

    def decode(self):
        output = bytearray()
        count = 0
        while self.pos < len(self.data):
            count += 1
            c = self.decode_char()
            char_display = chr(c) if 32 <= c < 127 else f"0x{c:02x}"
            print(
                f"[{count}] Char: {char_display} (pos={self.pos}, r={self.r}, getbuf={self.getbuf:08x}, getlen={self.getlen})")
            if c < 256:
                output.append(c)
                self.text_buf[self.r % (self.N - self.F)] = c
                self.r += 1
            else:
                i = (self.r - self.decode_position() - 1) % self.N
                j = c - 255 + self.THRESHOLD
                print(f"[{count}] LZSS: pos={i}, len={j}")
                for k in range(j):
                    c = self.text_buf[(i + k) % (self.N - self.F)]
                    output.append(c)
                    self.text_buf[self.r % (self.N - self.F)] = c
                    self.r += 1
                    char_display = chr(c) if 32 <= c < 127 else f"0x{c:02x}"
                    print(f"[{count}]   Ref: {char_display} (r={self.r})")
        return bytes(output)


def decode_fbb_message(data):
    prefix_len = len(b'[FBB-7.0.10-AB1FHMR$]\rFA P MD2SAW MD2BOX MD2SAW 24196-MD2BBS 113\rF> F2\r')
    print(f"Prefix length: {prefix_len}")
    if len(data) < prefix_len or data[prefix_len] != 0x01:
        raise ValueError("Ungültiger Header: <SOH> erwartet")

    header_start = prefix_len
    header_len = data[header_start + 1]
    print(f"Header start: {header_start}, Header length: {header_len}")
    header_end = header_start + 2 + header_len

    if header_end > len(data):
        raise ValueError("Header-Länge überschreitet Daten")

    nul1_pos = data.find(b'\x00', header_start + 2)
    print(f"NUL1 position: {nul1_pos}")
    if nul1_pos == -1 or nul1_pos >= header_end:
        raise ValueError("Erster <NUL> nicht gefunden")
    title = data[header_start + 2:nul1_pos]
    offset_data = data[nul1_pos + 1:header_end - 1]
    offset = int(offset_data.strip() or 0)
    print(f"Title: {title}, Offset: {offset}")

    if data[header_end - 1] != 0x00 or data[header_end] != 0x02:
        raise ValueError("Ungültiger Datenblock-Start: <NUL> <STX> erwartet")

    compressed_full = data[header_end + 1:]
    eot_pos = compressed_full.rfind(b'\x04')
    if eot_pos == -1:
        raise ValueError("Kein <EOT> (0x04) in den komprimierten Daten gefunden")

    compressed_data = compressed_full[:eot_pos]
    checksum = compressed_full[eot_pos + 1] if eot_pos + 1 < len(compressed_full) else 0
    print(
        f"Compressed data start: {header_end + 1}, compressed_full length: {len(compressed_full)}, eot_pos in compressed_full: {eot_pos}")
    print(f"Compressed data length: {len(compressed_data)}, data: {compressed_data.hex()}")
    print(f"Checksum: 0x{checksum:02x}")

    decoder = LZHDecoder(compressed_data)
    decoded_data = decoder.decode()

    return decoded_data


# Testdaten aus deiner Ausgabe (angepasst an 258 Bytes)
binary_data = (
    b'[FBB-7.0.10-AB1FHMR$]\rFA P MD2SAW MD2BOX MD2SAW 24196-MD2BBS 113\rF> F2\r'
    b'\x01\x16test1234567890\x00     0\x00\x02'
    b'\x9e\xed\xb1\x02\x01\x00\x00\xef\x71\xb7\xdc\x1d\xe6\xff\x7b\xc2\xdd\xdf\xe1\xdc\xc1\xf3\x6b'
    b'\x39\x98\x9d\x9e\x85\xee\x75\x5f\x7f\x75\xaf\xb4\xe6\xf8\xec\xea\x58\xcf\xa5\x6d\xd1\xf0\xd5'
    b'\xa9\xa8\xb9\xb2\xa5\x27\x02\x7f\x16\xfa\x67\x9e\xbf\xb7\xf0\x0c\x07\xf1\xf8\x4d\x4e\xfa\x68'
    b'\x6c\x2f\xe1\x3d\xcc\xb0\xcb\x33\x96\x94\x7b\xe9\x7f\xbf\x7f\x9a\x6d\x5a\x08\x28\xe1\xed\xc7'
    b'\xf8\x89\x78\xef\xc1\x20\xe4\x36\x41\x27\x6f\xc9\x69\x1d\x80\x33\x34\xff\xbe\xd2\x73\x02\x8f'
    b'\x09\xcf\x0f\x89\x44\xe2\x34\x57\x3c\x40\x67\x90\x17\x3d\xee\xf7\xcc\xbf\xf9\x7c\xfe\x9f\x5f'
    b'\xb7\xdd\x94\x7f\xe9\x97\xf3\xfb\x22\xf8\xbc\x04\x0a\x6c\x10\x16\x73\xe0\x1b\xcb\x11\xe0\x04'
    b'\x79'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
)  # 258 Bytes

expected_output = (
    b'test1234567890\rR:250316/1220Z @:MD2BBS.#SAW.SAA.DEU.EU #:24196 [Salzwedel] $:24196-MD2BBS\r\r'
    b'From: MD2SAW@MD2BBS.#SAW.SAA.DEU.EU\rTo  : MD2SAW@MD2BOX\r\rtest1234567890\r0123456789\r'
    b'0123456789\rabcdefghijklmnopqrstuvwxyz\rabcdefghijklmnopqrstuvwxyz\r0123456789\r0123456789\r\x1a\r'
)

# Test
if __name__ == "__main__":
    try:
        decoded = decode_fbb_message(binary_data)
        print("Dekodierte Nachricht:", decoded)
        print("Erfolg:", decoded == expected_output)
        print("Länge der dekodierten Nachricht:", len(decoded))
    except ValueError as e:
        print(f"Fehler: {e}")