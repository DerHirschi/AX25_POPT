from datetime import datetime


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


def conv_time_US_str(dateti: datetime.now()):
    return dateti.strftime('%m/%d/%y %H:%M:%S')


def conv_time_DE_str(dateti: datetime.now()):
    return dateti.strftime('%d/%m/%y %H:%M:%S')


def get_time_delta(dateti: datetime.now()):
    return str(datetime.now() - dateti).split('.')[0]

