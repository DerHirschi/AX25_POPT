import re
from datetime import datetime, timezone

from bbs.bbs_constant import GET_MSG_STRUC, STAMP, MSG_ID, STAMP_BID, STAMP_MSG_NUM, CR, MSG_H_TO, SP, MSG_H_FROM, \
    SOH, NUL, EOT, STX, MSG_XH_INFO, LF
from cfg.constant import BBS_SW_ID, VER, SQL_TIME_FORMAT
from cfg.logger_config import logger
from cfg.logger_config import BBS_LOG
from fnc.lzhuf import LZHUF_Comp
from fnc.sql_fnc import convert_sql_list
from fnc.str_fnc import find_eol


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
    bin_mode = False
    if len(hdr) != 7:
        logger.debug(f"PH!!: {header}")
        return None
    # if hdr[0] != 'FB':
    if hdr[0] not in ['FB', 'FA']:
        logger.debug(f"PH!!: {header}")
        return None
    if hdr[1] not in ['P', 'B']:
        logger.debug(f"PH!!: {header}")
        return None
    if hdr[0] == 'FA':
        bin_mode = True

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
        "message_size":     hdr[6],
        "bin_mode":         bin_mode
    })
    return msg_struc



def build_msg_header(msg_struc: dict, fwd_bbs_address: str):
    #print(f"build_fwd_msg_header - BID: {msg_struc.get('bid_mid', '')}")
    #print(msg_struc)
    bbs_address              = fwd_bbs_address
    bbs_call                 = bbs_address.split('.')[0]
    bid                      = msg_struc.get('bid_mid', '')
    msg_struc['tx-time']     = datetime.now().strftime(SQL_TIME_FORMAT)
    #utc                      = datetime.strptime(msg_struc['utctime'], SQL_TIME_FORMAT)
    subject                  = msg_struc.get('subject', '')
    old_header               = msg_struc.get('header', b'')
    x_info                   = msg_struc.get('x_info', '')
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
        BBS_LOG.debug(f"No BID.. New BID: {msg_struc['bid_mid']}")

    utc = datetime.now(timezone.utc)
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
        new_header = subject.encode('ASCII', 'ignore') + CR + LF
        for line in old_path:
            if not line:
                continue
            new_header += line.encode('ASCII', 'ignore') + CR + LF
        new_header += CR + LF
        new_header += MSG_H_FROM[0] + SP + from_address.encode('ASCII', 'ignore') + CR + LF
        new_header += MSG_H_TO[1]   + SP + to_address.encode('ASCII', 'ignore') + CR + LF
        if x_info:
            enc_x_info = x_info.encode('ASCII', 'ignore')
            new_header += MSG_XH_INFO + SP + enc_x_info + CR + LF
        new_header += CR + LF
        logger.debug(f"new_header 1> : {new_header}")

    else:
        eol = find_eol(old_header)
        header_lines = old_header.split(eol)
        logger.debug(f"header_lines : {header_lines}")
        logger.debug(f"eol : {eol}")
        new_header = header_lines[0] + eol
        new_header += stamp.encode('ASCII', 'ignore') + eol
        new_header += eol.join(header_lines[1:])



    msg_struc['path']   = old_path
    msg_struc['header'] = new_header

    logger.debug("build_fwd_msg_header ---RES------")
    logger.debug(f"Old Header : {old_header}")
    logger.debug(f"New Header : {new_header}")

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

##################################################
# Decoding Bin Mail
def decode_fa_header(data: bytearray) -> dict:
    """ By Grok3-Beta (AI by X.com)"""
    logTag = "decode_fa_header()> "
    pos = 0

    if pos >= len(data) or data[pos] != SOH:
        raise ValueError("Ungültiger Header: <SOH> erwartet")
    pos += 1

    if pos >= len(data):
        raise ValueError("Unerwartetes Ende vor Header-Länge")
    header_length = data[pos]
    pos += 1

    if header_length < 3:
        raise ValueError(f"Ungültige Header-Länge: {header_length}")
    if pos + header_length > len(data):
        raise ValueError("Unerwartetes Ende im Header-Bereich")

    header_data = data[pos:pos + header_length]
    pos += header_length

    nul_positions = [i for i, byte in enumerate(header_data) if byte == NUL]
    if len(nul_positions) != 2:
        raise ValueError("Ungültiger Header: Genau zwei <NUL> erwartet")

    title_end = nul_positions[0]
    offset_start = nul_positions[0] + 1
    offset_end = nul_positions[1]

    title = header_data[:title_end]
    offset = int(header_data[offset_start:offset_end].decode('ascii'))

    compressed_data = bytearray()
    checksum = 0
    block_count = 0
    received_checksum = 0

    while pos < len(data):
        if data[pos] == EOT:
            pos += 1
            if pos >= len(data):
                raise ValueError("Unerwartetes Ende vor Prüfsumme")
            received_checksum = data[pos]
            break
        elif data[pos] != STX:
            raise ValueError(f"Ungültiger Blockstart: <STX> erwartet, erhalten {data[pos]:02x}")

        pos += 1
        if pos >= len(data):
            raise ValueError("Unerwartetes Ende vor Blockgröße")

        block_size = data[pos]
        if block_size == 0:
            block_size = 256
        pos += 1

        if pos + block_size > len(data):
            raise ValueError(f"Blockgröße {block_size} überschreitet Datenlänge bei Position {pos} und kein <EOT> gefunden")

        block_data = data[pos:pos + block_size]
        compressed_data.extend(block_data)
        for byte in block_data:
            checksum = (checksum + byte) & 0xFF
        pos += len(block_data)
        block_count += 1

    if (checksum + received_checksum) & 0xFF != 0:
        raise ValueError(f"Checksum-Fehler: Berechnet {checksum:02x}, Empfangen {received_checksum:02x}")

    result = {
        'title': title,
        'offset': offset,
        'compressed_data': compressed_data,
        'checksum': received_checksum
    }

    BBS_LOG.info(logTag + f"Header erfolgreich dekodiert:")
    BBS_LOG.info(logTag + f"  Titel: {title}")
    BBS_LOG.info(logTag + f"  Offset: {offset}")
    BBS_LOG.info(logTag + f"  Datenblöcke: {block_count}")
    BBS_LOG.info(logTag + f"  Gesamtdatengröße: {len(compressed_data)} Bytes")
    BBS_LOG.info(logTag + f"  Prüfsumme: {received_checksum:02x} (verifiziert)")

    return result


def decode_bin_mail(data: b''):
    """ By Grok3-Beta (AI by X.com) """
    logTag = "decode_bin_mail()> "
    BBS_LOG.info(logTag + f"Decoding binary mail: {len(data)} bytes, data: {data[:50].hex()}...")
    try:
        # Header dekodieren
        result = decode_fa_header(data)
    except ValueError as e:
        BBS_LOG.error(logTag + f"Fehler beim Dekodieren: {e}")
        return {}
    except Exception as e:
        BBS_LOG.error(logTag + f"Unbekannter Fehler: {e}")
        return {}

    if not result.get('compressed_data', b''):
        BBS_LOG.error(logTag + f"Keine Daten(compressed_data): {result}")
        return {}
    lzhuf = LZHUF_Comp()
    compressed             = result.get('compressed_data', b'')
    decompressed           = lzhuf.decode(compressed)
    result['decompressed'] = decompressed

    compressed_size        = len(compressed)
    decompressed_size      = len(decompressed)
    compression_ratio      = decompressed_size / compressed_size
    BBS_LOG.info(logTag + f"Komprimierte:   {compressed_size} Bytes")
    BBS_LOG.info(logTag + f"Dekomprimierte: {decompressed_size} Bytes")
    BBS_LOG.info(logTag + f"Rate:           {compression_ratio:.2f}:1")
    return result

##################################################
# Encoding Bin Mail
def calculate_checksum(data):
    """
    By Grok3-Beta (AI by X.com)
    Berechnet die Checksumme als two's complement der Summe aller Datenbytes modulo 256.
    """
    total    = sum(data) & 0xFF  # Summe modulo 256
    checksum = (-total) & 0xFF  # Two's complement
    return checksum


def create_bin_mail_header(title, offset="0"):
    """
    By Grok3-Beta (AI by X.com)
    Erstellt den Bin-Mail-Header gemäß FBB-Spezifikation.
    """
    # Titel/Filename auf 80 Bytes begrenzen und in ASCII kodieren
    title_bytes = title.encode('ascii')[:80]
    # title_bytes = title[:80]
    # Offset auf 6 Bytes begrenzen und in ASCII kodieren
    offset_bytes = str(offset).encode('ascii')[:6]

    # Header-Länge: Länge von title + <NUL> + offset + <NUL>
    header_length = len(title_bytes) + 1 + len(offset_bytes) + 1

    header = bytearray()
    header.append(SOH)  # <SOH>
    header.append(header_length)  # Länge des Headers (inkl. beider <NUL>)
    header.extend(title_bytes)  # Titel/Filename
    header.append(NUL)  # <NUL>
    header.extend(offset_bytes)  # Offset
    header.append(NUL)  # <NUL>
    return header


def split_into_blocks(compressed_data, max_block_size=256):
    """
    By Grok3-Beta (AI by X.com)
    Teilt die komprimierten Daten in Blöcke mit STX und Größe.
    """
    blocks = bytearray()
    pos = 0
    while pos < len(compressed_data):
        remaining = len(compressed_data) - pos
        block_size = min(max_block_size, remaining)
        blocks.append(STX)  # <STX>
        blocks.append(block_size if block_size < 256 else 0)  # Größe (0 = 256)
        blocks.extend(compressed_data[pos:pos + block_size])
        pos += block_size
    return blocks


def encode_fa_header(mail_content, title, offset="0"):
    """
    By Grok3-Beta (AI by X.com)
    Wandelt eine Mail in Bin-Mail-Format um (FA-Typ).
    """
    logTag = "encode_fa_header()> "
    BBS_LOG.info(logTag + f"Encoding binary mail: {len(mail_content)} bytes, Title: {title}, Offset; {offset} ")
    # 1. Mail-Inhalt als Bytes (ASCII)
    # mail_bytes = mail_content.encode('ascii', errors='ignore')
    #BBS_LOG.debug(logTag + "Komprimierung")
    # 2. Komprimierung mit LZHUF (Platzhalter)
    lzhuf = LZHUF_Comp()
    compressed_data = lzhuf.encode(mail_content)
    #BBS_LOG.debug(logTag + "Header erstellen")
    # 3. Header erstellen
    header = create_bin_mail_header(title, offset)
    #BBS_LOG.debug(logTag + "Daten in Blöcke aufteilen")
    # 4. Daten in Blöcke aufteilen
    blocks = split_into_blocks(compressed_data)

    #BBS_LOG.debug(logTag + "Checksumme")
    # 5. Checksumme über komprimierte Daten berechnen
    checksum = calculate_checksum(compressed_data)

    #BBS_LOG.debug(logTag + "Alles zusammenfügen")
    # 6. Alles zusammenfügen: Header + Blöcke + EOT + Checksum
    bin_mail = bytearray()
    bin_mail.extend(header)
    bin_mail.extend(blocks)
    bin_mail.append(0x04)  # <EOT>
    bin_mail.append(checksum)  # Checksum
    compressed_size   = len(compressed_data)
    decompressed_size = len(mail_content)
    try:
        compression_ratio = decompressed_size / compressed_size
    except ZeroDivisionError:
        compression_ratio = 0
    BBS_LOG.info(logTag + f"  Komprimierte:   {compressed_size} Bytes")
    BBS_LOG.info(logTag + f"  Dekomprimierte: {decompressed_size} Bytes")
    BBS_LOG.info(logTag + f"  Rate:           {compression_ratio:.2f}:1")
    BBS_LOG.info(logTag + f"  Checksum:       HEX {hex(checksum)} / INT {checksum}")
    BBS_LOG.info(logTag + f"  Blöcke:         {len(blocks)}")
    BBS_LOG.info(logTag + f"  Gesamtlänge:    {len(bin_mail)} Bytes")
    return bin_mail
