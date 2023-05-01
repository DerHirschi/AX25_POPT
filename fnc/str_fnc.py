from datetime import datetime
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


def get_time_delta(dateti: datetime.now()):
    return str(datetime.now() - dateti).split('.')[0]


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
