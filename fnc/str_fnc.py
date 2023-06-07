from datetime import datetime, timedelta
import logging
from constant import ENCODINGS


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


def conv_time_for_sorting(dateti: datetime.now()):
    return dateti.strftime('%y/%m/%d %H:%M:%S')


def conv_time_US_str(dateti: datetime.now()):
    return dateti.strftime('%m/%d/%y %H:%M:%S')


def conv_time_DE_str(dateti: datetime.now()):
    return dateti.strftime('%d/%m/%y %H:%M:%S')


def get_file_timestamp():
    return datetime.now().strftime('%d%m/%y-%H%M')


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
        # Divided by Zero let explode the Machine... So, better return 0
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
