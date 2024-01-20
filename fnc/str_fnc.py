import time
from datetime import datetime, timedelta
import logging
from cfg.constant import ENCODINGS, SQL_TIME_FORMAT


def get_kb_str_fm_bytes(len_: int):
    return f"{len_/1024:.2f} kb"


def tk_filter_bad_chars(inp: str):
    """
    Fix for:
    _tkinter.TclError: character U+1f449 is above the range (U+0000-U+FFFF) allowed by Tcl
    Source: https://itecnote.com/tecnote/python-tkinter-tclerror-character-u1f449-is-above-the-range-u0000-uffff-allowed-by-tcl/
    """
    char_list = [inp[j] for j in range(len(inp)) if ord(inp[j]) in range(65536)]
    inp = ''
    for j in char_list:
        inp = inp + j
    return inp


def time_to_decimal(dt):
    total_minutes = dt.hour * 60 + dt.minute + dt.second / 60.0  # Gesamtminuten seit Mitternacht
    decimal_value = total_minutes / 60.0  # Umrechnung in Dezimalform
    return decimal_value


def conv_time_for_sorting(dateti: datetime.now()):
    return dateti.strftime('%y%m%d%H%M%S')


def conv_time_for_key(dateti: datetime.now()):
    return dateti.strftime('%y%m%d%H%M%S')


def conv_time_US_str(dateti=None):
    if not dateti:
        return datetime.now().strftime('%m/%d/%y %H:%M:%S')
    return dateti.strftime('%m/%d/%y %H:%M:%S')


def conv_time_DE_str(dateti=None):
    if not dateti:
        return datetime.now().strftime('%d/%m/%y %H:%M:%S')
    return dateti.strftime('%d/%m/%y %H:%M:%S')


def get_file_timestamp():
    return datetime.now().strftime('%d%m/%y-%H%M')


def get_timedelta_CLIstr(dateti: datetime.now(), r_just=True):
    _time_delta = datetime.now() - dateti
    _td_days = _time_delta.days
    _td_hours = int(_time_delta.seconds / 3600)
    _td_min = int(_time_delta.seconds / 60)
    _td_sec = _time_delta.seconds

    if _td_days:
        # td_hours = td_hours - td_days * 24
        if r_just:
            _time_delta_str = f'{str(_td_days).rjust(3, " ")}d,{str(_td_hours).rjust(2, " ")}h'
        else:
            _time_delta_str = f'{_td_days}d,{_td_hours}h'
    elif _td_hours:
        _td_min = _td_min - _td_hours * 60
        if r_just:
            _time_delta_str = f'{str(_td_hours).rjust(3, " ")}h,{str(_td_min).rjust(2, " ")}m'
        else:
            _time_delta_str = f'{_td_hours}h,{_td_min}m'
    elif _td_min:
        _td_sec = _td_sec - _td_min * 60
        if r_just:
            _time_delta_str = f'{str(_td_min).rjust(3, " ")}m,{str(_td_sec).rjust(2, " ")}s'
        else:
            _time_delta_str = f'{_td_min}m,{_td_sec}s'
    else:
        if r_just:
            _time_delta_str = f'{str(_td_sec).rjust(7, " ")}s'
        else:
            _time_delta_str = f'{_td_sec}s'
    return _time_delta_str


def get_timedelta_str_fm_sec(time_st: time.time(), r_just=True):
    _td_sec = int(time_st)
    _td_min = int(_td_sec / 60)
    _td_hours = int(_td_sec / 3600)
    _td_days = int(_td_hours / 24)

    if _td_days:
        # td_hours = td_hours - td_days * 24
        if r_just:
            _time_delta_str = f'{str(_td_days).rjust(3, " ")}d,{str(_td_hours).rjust(2, " ")}h'
        else:
            _time_delta_str = f'{_td_days}d,{_td_hours}h'

    elif _td_hours:
        _td_min = _td_min - _td_hours * 60
        if r_just:
            _time_delta_str = f'{str(_td_hours).rjust(3, " ")}h,{str(_td_min).rjust(2, " ")}m'
        else:
            _time_delta_str = f'{_td_hours}h,{_td_min}m'
    elif _td_min:
        _td_sec = _td_sec - _td_min * 60
        if r_just:
            _time_delta_str = f'{str(_td_min).rjust(3, " ")}m,{str(_td_sec).rjust(2, " ")}s'
        else:
            _time_delta_str = f'{_td_min}m,{_td_sec}s'
    else:
        if r_just:
            _time_delta_str = f'{str(_td_sec).rjust(7, " ")}s'
        else:
            _time_delta_str = f'{_td_sec}s'
    return _time_delta_str


def convert_str_to_datetime(date_str, date_format=SQL_TIME_FORMAT):
    try:
        converted_date = datetime.strptime(date_str, date_format)
        return converted_date
    except ValueError:
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


def try_decode(data: b'', ignore=False):
    for cd in ENCODINGS:
        try:
            ret = data.decode(cd)
            return ret
        except UnicodeDecodeError:
            pass
    if ignore:
        return data.decode('UTF-8', 'ignore')
    return f'<BIN> {len(data)}'


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
        logging.warning(f"find_decoding() more then 1 Result: {res} inp: {inp}")
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

