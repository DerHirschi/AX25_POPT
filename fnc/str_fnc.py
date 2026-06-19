import random
import time
import re
from datetime import datetime, timedelta
import string
from bbs.bbs_constant import EOL, CR
from cfg.logger_config import logger
from cfg.constant import ENCODINGS, SQL_TIME_FORMAT
from cfg.string_tab import STR_TABLE


STR_EOL = tuple(x.decode('UTF-8') for x in EOL)

def get_kb_str_fm_bytes(len_: int):
    return f"{len_/1024:.2f} kb"


# Entfernt ALLES, was in tkinter Probleme macht – außer \n und \r
_TK_DANGEROUS_CHARS = re.compile(
    r"[\U00010000-\U0010FFFF"    # Alle Zeichen außerhalb BMP (4-Byte-Emojis etc.)
    r"\x00-\x09\x0b\x0c\x0e-\x1f"  # C0-Steuerzeichen außer \n (0x0A) und \r (0x0D)
    r"\x7f-\x9f"                  # DELETE + C1-Steuerzeichen
    r"\ufeff"                     # BOM
    r"\u200b-\u200f"              # Zero-Width Space, Joiner, etc.
    r"\u202a-\u202e"              # BiDi-Steuerzeichen (LRE, RLE, PDF, ...)
    r"\u2066-\u2069"              # Arabic/Persian Isolates
    r"\ufff9-\ufffb"              # Interlinear Annotation (sehr selten, aber bösartig)
    r"]+",
    re.UNICODE
)

def tk_filter_bad_chars(text: str):
    if not text:
        return ""
    text = text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    text = _TK_DANGEROUS_CHARS.sub("", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")  # einheitliche Zeilenumbrüche

"""
def tk_filter_bad_chars(inp: str):
    #Fix for:
    #_tkinter.TclError: character U+1f449 is above the range (U+0000-U+FFFF) allowed by Tcl
    #Source: https://itecnote.com/tecnote/python-tkinter-tclerror-character-u1f449-is-above-the-range-u0000-uffff-allowed-by-tcl/
    char_list = [inp[j] for j in range(len(inp)) if ord(inp[j]) in range(65536)]
    inp = ''
    for j in char_list:
        inp = inp + j
    return inp
"""

def time_to_decimal(dt):
    total_minutes = dt.hour * 60 + dt.minute + dt.second / 60.0  # Gesamtminuten seit Mitternacht
    decimal_value = total_minutes / 60.0  # Umrechnung in Dezimalform
    return decimal_value


def conv_time_for_sorting(dateti: datetime.now()):
    try:
        return dateti.strftime('%y%m%d%H%M%S')
    except AttributeError:
        return "---"


def conv_time_for_key(dateti: datetime.now()):
    return dateti.strftime('%y%m%d%H%M%S')


def conv_time_US_str(dateti=None):
    if not dateti:
        return datetime.now().strftime('%m/%d/%y %H:%M:%S')
    return dateti.strftime('%m/%d/%y %H:%M:%S')


def conv_time_DE_str(dateti=None):
    if type(dateti) == str:
        logger.warning(f"conv_time_DE_str: is str !!!!")
        logger.warning(f"conv_time_DE_str: {dateti}")
        return dateti
    try:
        if not dateti:
            return str(datetime.now().strftime('%d.%m.%y %H:%M:%S'))
        return str(dateti.strftime('%d.%m.%y %H:%M:%S'))
    except Exception as ex:
        logger.error(f"conv_time_DE_str: {ex}")
        logger.error(f"conv_time_DE_str: {dateti}")
        return '---'

def str_to_datetime(date_str=None):
    if not date_str:
        return datetime.now()
    try:
        return datetime.strptime(date_str, '%d.%m.%y %H:%M:%S')
    except ValueError:
        return datetime.now()

def get_file_timestamp():
    return datetime.now().strftime('%d%m/%y-%H%M')


def get_timedelta_CLIstr(dateti: datetime.now(), r_just=True):
    time_delta = datetime.now() - dateti
    td_days = time_delta.days
    td_hours = int(time_delta.seconds / 3600)
    td_min = int(time_delta.seconds / 60)
    td_sec = time_delta.seconds

    if td_days:
        # td_hours = td_hours - td_days * 24
        if r_just:
            time_delta_str = f'{str(td_days).rjust(3, " ")}d,{str(td_hours).rjust(2, " ")}h'
        else:
            time_delta_str = f'{td_days}d,{td_hours}h'
    elif td_hours:
        td_min = td_min - td_hours * 60
        if r_just:
            time_delta_str = f'{str(td_hours).rjust(3, " ")}h,{str(td_min).rjust(2, " ")}m'
        else:
            time_delta_str = f'{td_hours}h,{td_min}m'
    elif td_min:
        td_sec = td_sec - td_min * 60
        if r_just:
            time_delta_str = f'{str(td_min).rjust(3, " ")}m,{str(td_sec).rjust(2, " ")}s'
        else:
            time_delta_str = f'{td_min}m,{td_sec}s'
    else:
        if r_just:
            time_delta_str = f'{str(td_sec).rjust(7, " ")}s'
        else:
            time_delta_str = f'{td_sec}s'
    return time_delta_str


def days_hours_minutes(td):
    """ https://stackoverflow.com/questions/2119472/convert-a-timedelta-to-days-hours-and-minutes """
    return td.days, td.seconds//3600, (td.seconds//60)%60


def get_timedelta_str_fm_sec(time_st: time.time(), r_just=True):
    td_sec = int(time_st)
    td_min = int(td_sec / 60)
    td_hours = int(td_sec / 3600)
    td_days = int(td_hours / 24)

    if td_days:
        # td_hours = td_hours - td_days * 24
        if r_just:
            time_delta_str = f'{str(td_days).rjust(3, " ")}d,{str(td_hours).rjust(2, " ")}h'
        else:
            time_delta_str = f'{td_days}d,{td_hours}h'

    elif td_hours:
        td_min = td_min - td_hours * 60
        if r_just:
            time_delta_str = f'{str(td_hours).rjust(3, " ")}h,{str(td_min).rjust(2, " ")}m'
        else:
            time_delta_str = f'{td_hours}h,{td_min}m'
    elif td_min:
        td_sec = td_sec - td_min * 60
        if r_just:
            time_delta_str = f'{str(td_min).rjust(3, " ")}m,{str(td_sec).rjust(2, " ")}s'
        else:
            time_delta_str = f'{td_min}m,{td_sec}s'
    else:
        if r_just:
            time_delta_str = f'{str(td_sec).rjust(7, " ")}s'
        else:
            time_delta_str = f'{td_sec}s'
    return time_delta_str


def convert_str_to_datetime(date_str, date_format=SQL_TIME_FORMAT):
    try:
        converted_date = datetime.strptime(date_str, date_format)
        return converted_date
    except (ValueError, TypeError):
        return 0


def conv_timestamp_delta(delta):
    if delta:
        timestamp = str(delta)
        timestamp = timestamp.split(':')
        if len(timestamp) > 3:
            days, hours, minutes, seconds = timestamp
            hours += days * 24
        else:
            hours, minutes, seconds = timestamp
        return f"{hours.zfill(2)}:{minutes.zfill(2)}:{str(round(float(seconds))).zfill(2)}"
    return "--:--:--"


def get_time_delta(dateti: datetime.now()):
    return str(datetime.now() - dateti).split('.')[0]


def calculate_percentage(data_length, data_sent):
    if not data_sent or not data_length:
        # Divided by Zero
        return 0
    return round((data_sent / data_length) * 100, 1)


def calculate_time_remaining(time_delta, data_length, data_sent):
    remaining_data = data_length - data_sent
    if remaining_data <= 0 or not time_delta or not data_sent:
        return 0, 0, 0
    time_remaining = 0
    baud_rate = 0
    percentage_completion = 0
    if data_sent and time_delta:
        percentage_completion = calculate_percentage(data_length, data_sent)
        time_per_byte = time_delta.total_seconds() / data_sent
        time_remaining = timedelta(seconds=remaining_data * time_per_byte)
    if time_delta.total_seconds() > 0:
        baud_rate = (data_sent * 8) / time_delta.total_seconds()  # Convert data_sent to bits
    return time_remaining, int(baud_rate), percentage_completion


def format_number(number):
    """ By: ChatGP. This shit makes me lazy. """
    number_str = str(number)[::-1]
    formatted_str = ""
    for i, digit in enumerate(number_str, start=1):
        formatted_str += digit
        if i % 3 == 0 and i != len(number_str):
            formatted_str += "."
    formatted_number = formatted_str[::-1]
    return formatted_number


def is_plausible_text(text: str):
    """By Grok3-AI"""
    """Prüft, ob der Text sinnvoll aussieht (überwiegend druckbare Zeichen)."""
    if not text:
        return False
    # Anteil druckbarer Zeichen (ASCII, Buchstaben, Zahlen, Satzzeichen)
    printable_ratio = sum(c in string.printable for c in text) / len(text)
    # Anteil von Steuerzeichen (außer \n, \t, etc.)
    control_chars = sum(1 for c in text if c < '\x20' and c not in '\n\r\täöpÄÖÜßéÉ<>-_#*+-/=|.,:' or c in 'Σⁿ▀▄Θ─α') / len(text)
    return printable_ratio > 0.7 and control_chars < 0.05  # 90 % druckbar, wenige Steuerzeichen

def try_decode(data: bytes, ignore: bool = False):
    """By Grok3-AI"""
    # Schritt 1: Prüfe, ob Daten wahrscheinlich binär sind
    if not data:
        return '<BIN> 0', "Auto: NO-DATA"
    non_printable_ratio = sum(1 for b in data if b < 32 or b > 126) / len(data)
    if non_printable_ratio > 0.5:  # Zu viele nicht-druckbare Bytes -> Binärdaten
        return f'<BIN> {len(data)}', "Auto: BIN"

    # Schritt 2: Probiere Kodierungen in der Reihenfolge
    for encoding in ENCODINGS:
        try:
            decoded = data.decode(encoding)
            if is_plausible_text(decoded):
                return decoded, f"Auto: {encoding}"
        except UnicodeDecodeError:
            pass

    # Schritt 3: Wenn ignore=True, dekodiere mit UTF-8 und ignoriere Fehler
    if ignore:
        return data.decode('UTF-8', errors='ignore'), "Auto: UTF-8(ignore)"

    # Schritt 4: Rückgabe als Binärdaten, wenn nichts passt
    return f'<BIN> {len(data)}', "Auto: BIN-"


def find_decoding(inp: b''):
    res = []
    for enc in ENCODINGS:
        try:
            probe = inp.decode(enc)
            if probe in ['ä', 'Ä']:
                res.append(enc)
        except UnicodeDecodeError:
            pass
    if not res:
        return False
    if len(res) > 1:
        logger.warning(f"find_decoding() more then 1 Result: {res} inp: {inp}")
    return res[0]


def convert_umlaute_to_ascii(in_str: str):
    return in_str.replace('ä', 'ae')\
        .replace('ö', 'oe')\
        .replace('ü', 'ue')\
        .replace('Ä', 'Ae')\
        .replace('Ö', 'Oe')\
        .replace('Ü', 'Ue')\
        .replace('ß', 'ss')


def is_byte_ascii(s: int):
    return 32 <= s <= 126


def get_weekDay_fm_dt(now_weekday):
    return ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO'][now_weekday]

def get_strTab(str_key: str, lang_index=1, warning=True, fallback=False):
    if not str_key:
        return str_key
    if str_key not in STR_TABLE.keys():
        if warning:
            logger.warning(f"get_strTab() str_key: {str_key}")
            logger.warning(f"  No translation found for: {str_key}")
            logger.warning(f"  Ignore warning if no translation is needed.")
        return str_key
    lang_tab = STR_TABLE.get(str_key, ())
    try:
        transl_str = lang_tab[lang_index]
    except IndexError:
        logger.error(f"get_strTab() str_key: {str_key}")
        logger.error(f"  Language not found- Lang-Ind: {lang_index}")
        return str_key

    if transl_str:
        return transl_str

    # ===== Fallback if no Translation
    if fallback:
        logger.error(f"get_strTab() Fallback Error !!!!!")
        logger.error(f"  Translation empty for KEY: {str_key}")
        logger.error(f"  Lang-Ind: {lang_index}")
        return str_key
    logger.warning(f"get_strTab() Fallback no Translation found !!")
    logger.warning(f"  Translation empty for KEY: {str_key}")
    logger.warning(f"  Lang-Ind: {lang_index}")
    return get_strTab(str_key, fallback=True)



def zeilenumbruch(text: str, max_zeichen=79, umbruch='\n'):
    if len(text) <= max_zeichen:
        return text
    lines = []
    while True:
        letztes_leerzeichen = text.rfind(' ', 0, max_zeichen + 1)
        if letztes_leerzeichen <= 0:
            lines.append(text[:max_zeichen])
            text = text[max_zeichen:]
        else:
            lines.append(text[:letztes_leerzeichen])
            text = text[letztes_leerzeichen + 1:]
        if len(text) <= max_zeichen:
            lines.append(text)
            break
    return umbruch.join(lines)

def zeilenumbruch_lines(text: str, max_zeichen=79, umbruch='\n'):
    line_list = text.split(umbruch)
    text = ''
    for line in line_list:
        text += zeilenumbruch(line, max_zeichen, umbruch) + umbruch
    return text[:-1]

def lob_gen(lang: int):
    bis = 5
    lob_str = f"lob{random.randint(1, bis)}"
    return get_strTab(lob_str, lang)


def find_eol(msg: bytes):
    # Find EOL Syntax
    for tmp_eol in EOL:
        if tmp_eol in msg:
            return tmp_eol
    return CR


def find_eol_in_str(msg: str, default='\r'):
    # Find EOL Syntax
    for tmp_eol in STR_EOL:
        if tmp_eol in msg:
            return tmp_eol
    return default

def version_tuple(v: str):
    return tuple(int(x) for x in v.split('.'))