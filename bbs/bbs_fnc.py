import re
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


def extract_wp_data(wp_data: str):
    """
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

    wp = ("On 220702 MD2BBS @ MD2BBS.#SAW.SAA.DEU.EU zip D-29410 SalzwedelBBS Salzwedel JO52NU\r"
    "On 250226 MD2SAW @ MD2BBS.#SAW.SAA.DEU.EU zip D-29410 Manuel Salzwedel JO52NU\r"
    "On 241028 DBO527 @ DBO527.#SAW.SAA.DEU.EU zip D-29410 SalzwedelBBS Salzwedel, JO52NU WinBox-3.02\r"
    "On 210124 DBX320 @ DBX320.#HAL.SAA.DEU.EU zip ? Halle-BBS Halle, JO51XK\r"
    "On 241119 KS1BBS @ KS1BBS.#KS.NOE.AT.EU zip ? ? OpenBCM\r"
    "On 241210 APOLO1 @ AP2BOX.#H.NDS.DEU.EU zip D-30455 Peer Hannover/Badenstedt\r"
    "On 000526 LE3FLE @ LE3FLE.FL.NLD.EU zip ? ? Lelystad\r"
    "On 230228 AP2BOX @ AP2BOX.#H.NDS.DEU.EU zip D-30455 BBS-Hannover Hannover/Badenstedt JO42UI\r"
    "On 210718 CB0SAW @ MD2BBS.#SAW.SAA.DEU.EU zip MD2BBS-D MD2BBS-de-CB MD2BBS de CB0SAW (21:57)>SAWNO\r"
    "On 241026 DMA284 @ DBO274.#NRW.DEU.EU zip D-29378 Marc-Andre Wittingen\r"
    "On 231112 DX0SAW @ DX0SAW.#SAW.SAA.DEU.EU zip ? ? Salzwedel\r"
    "On 241208 PE1FTL @ FT0BOX.#DD.SAX.DEU.EU zip 01705 Peter Freital\r"
    "On 240124 D0HHB @ D0HHB.#HAR.HH.DEU.EU zip ? BBS-Hamburg ?\r"
    "On 240523 DOK346 @ DOK346.#OS.NW.DLNET.DEU.EU zip ? ? OS JO42BG\r"
    "On 240920 FT0BOX @ FT0BOX.#DD.SAX.DEU.EU zip ? ? OpenBCM\r"
    "On 240408 MO1BBS @ MO1BBS.#WES.NRW.DEU.EU zip ? ? OpenBCM Moers\r"
    "On 250216 DAR182 @ MO1BBS.#WES.NRW.DEU.EU zip 47445 Andy Moers\r"
    "On 240607 RT3HVT @ RT3HVT.ZH.NLD.EU zip XXXX Theo OpenBCM Rotterdam\r"
    "On 240519 JB1BBS @ MD2BBS.#SAW.SAA.DEU.EU zip ? ? ?\r"
    "On 240601 DBO595 @ DBO595.#MFR.SO.DLNET.DEU.EU zip ? ? LAU JN59RM\r"
    "On 240628 CE0BBS @ CE0BBS.#CE.NDS.DEU.EU zip D-29328 BBS-Celle ?\r"
    "On 240906 MO1WX @ MO1BBS.#WES.NRW.DEU.EU zip 47445 WX-Moers Moers\r"
    "On 241204 DAC476 @ DBX233 zip D-01796 Siegmar Pirna\r"
    "On 241215 D1WKA @ MD2BBS.#SAW.SAA.DEU.EU zip D-25524 li Itzehoe\r"
    "On 241023 GF1BOX @ GF1BOX.#GF.NDS.DEU.EU zip ? ? OpenBCM MailBox GF\r"
    "On 250131 FFL0EV @ FFLB0X.#BAY.DEU.BCMNET zip D-84049 FFL-e.V. Essenbach\r"
    "On 241219 DHH841 @ DBO841.#BAY.DEU.BCMNET zip D-84187 Hans Weng\r"
    "On 250106 NB1BKM @ NB1BKM.#BAY.DEU.BCMNET zip D-83052 Box-Sysop-HF Bruckmuehl/Mangfall\r"
    "On 250116 HF1BKM @ NB1BKM.#BAY.DEU.BCMNET zip D-83052 Franz Bruckmuehl/Mangfall\r"
    "On 250218 FFLB0X @ FFLB0X.#BAY.DEU.BCMNET zip ? ? Landshut\r"
    "On 241123 DAE595 @ DBO595.#MFR.SO.DLNET.DEU.EU zip 91217 Dominik Hersbruck\r"
    "On 241126 NL3TD @ NL3TD.ZH.NLD.EU zip ? ? Rotterdam\r"
    "On 241126 NL3PRC @ NL3PRC.NH.NLD.EU zip ? ? Den Helder JO22JX\r"
    "On 241127 SK1BBS @ SK1BBS.FRL.NLD.EU zip ? ? Sneek/Snits\r"
    "On 250101 SK1DAN @ PI8SNK.FRL.NLD.EU zip ? ? ?\r"
    "On 241127 EU1BOX @ EU1BOX.#NDS.DEU.EU zip ? ? ?\r"
    "On 250131 DMB252 @ DBX320.#HAL.SAA.DEU.EU zip 91056 Manfred Erlangen\r"
    "On 241209 MD9SAW @ MD2BBS.#SAW.SAA.DEU.EU zip ? ? ?\r"
    "On 241210 LA0NEA @ EU1BOX.#NDS.DEU.EU zip 31855 Lanea-lucy Herkendorf\r"
    "On 241213 RB1BRH @ BX0BRH.#DD.SAX.DEU.EU zip ? ? ?\r"
    "On 241215 DAC996 @ MD2BBS.#SAW.SAA.DEU.EU zip 72218 Steffen Wildberg\r"
    "On 241220 DAA212 @ NOAB0X.#MFR.SO.DLNET.DEU.EU zip 91207 Sascha Lauf-a.-d.-Pegnitz\r"
    "On 241220 NOAB0X @ NOAB0X.#MFR.SO.DLNET.DEU.EU zip 91207 BBS-Lauf Lauf-a.-d.-Pegnitz\r"
    "On 241214 GM1GVM @ GV1BBS.#NWM.MVP.DEU.EU zip 23926 ? Grevesmuehlen\r"
    "On 241225 NL1TD @ NL3TD.ZH.NLD.EU zip ? ? ?\r"
    "On 241223 BK89GL @ BX0GER.#G.THR.DEU.EU.WW zip ? ? ?\r"
    "On 241229 DBX233 @ DBX233.#DD.SAX.DEU.EU zip ? ? ?\r"
    "On 250212 GV1BBS @ GV1BBS.#NWM.MVP.DEU.EU zip ? ? JO53OU Grevesmuehlen\r"
    "On 241229 FU0BOX @ FU0BOX.#NVP.MVP.DEU.EU zip ? ? ?\r"
    "On 241229 HEJ717 @ HEJ717.#BERN.CH.EU zip ? ? Brienzwiler [JN46B\r"
    "On 250201 HEJ715 @ HEJ717.#BERN.CH.EU zip 3856 Adrian Brienzwiler\r"
    "On 250201 CZ3DTC @ NB1BKM.#BAY.DEU.BCMNET zip 35002 Pepe Cheb\r"
    "On 241229 DBO274 @ DBO274.#NRW.DEU.EU zip ? ? ?\r"
    "On 241231 PI8SNK @ PI8SNK.FRL.NLD.EU zip ? ? Sneek/Snits\r"
    "On 250214 MW2GER @ BX0KMZ.#SAX.DEU.BCMNET zip 01465 Marcel Langebrueck\r"
    "On 250218 MO1AR @ MO1BBS.#WES.NRW.DEU.EU zip 47445 Andy Moers#\r"
    "On 250113 MD5SAW @ MD2BBS.#SAW.SAA.DEU.EU zip D-29410 Manuel Salzwedel\r"
    "On 250115 BX0KMZ @ BX0KMZ.#SAX.DEU.BCMNET zip ? ? ?\r"
    "On 241226 MR2KM @ BX0KMZ.#SAX.DEU.BCMNET zip 01917 Mace Kamenz\r"
    "On 250105 KM0DIG @ BX0KMZ.#SAX.DEU.BCMNET zip N Q N\r"
    "On 250131 FRB124 @ FRB124.#24.FGAQ.FRA.EU.WW zip ? ? ?\r"
    "On 250126 FRB000 @ FRB024.#24.FGAQ.FRA.EU.WW zip 13113 BBS STANDBY LAMANON\r"
    "On 250205 SL1PIR @ DBX233.#DD.SAX.DEU.EU zip D-01796 ? Pirna\r"
    "On 250209 DAC527 @ DBO527.#SAW.SAA.DEU.EU zip 29410 Mario Salzwedel\r"
    "On 250211 PGB0MB @ AP2BOX.#H.NDS.DEU.EU zip ? ? ?\r"
    "On 250212 RT1HVT @ RT3HVT.ZH.NLD.EU zip 3194 Theo Rotterdam\r"
    "On 250212 DPE185 @ MO1BBS.#WES.NRW.DEU.EU zip 47445 Peter Moers\r"
    "On 250213 DMA318 @ DBO527.#SAW.SAA.DEU.EU zip ? ? ?\r"
    "On 250217 MD2BOX @ MD2BBS.#SAW.SAA.DEU.EU zip D-29410 ? ?\r"
    "On 250218 AT8HSF @ KL8BBS.#SV.KTN.AT.EU zip 9376 ? Knappenberg\r"
    "On 250224 DQB423 @ DOK346.#OS.NW.DLNET.DEU.EU zip 58515 ? Ldenscheid\r"
    "On 250225 GY1BBS @ GY1BBS.ZL.NLD.EU zip ? ? ST ANNALAND\r"
    "On 250225 GY3SAL @ GY1BBS.ZL.NLD.EU zip ? ? ?\r"
    "[ From WP @ MD2BBS ]\r")
    result = extract_wp_data(wp)

    # Beispiel-Ausgabe der ersten paar Einträge
    for i, entry in enumerate(result, 1):
        print(f"\nEintrag {i}:")
        for key, value in entry.items():
            print(f"{key}: {value}")