import random
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, scrolledtext

from cfg.constant import CFG_aprs_icon_path, PARAM_MAX_MON_WIDTH
from cfg.logger_config import logger
from fnc.str_fnc import find_eol_in_str, zeilenumbruch_lines


def get_all_tags(text_wig):
    ret = {}
    tag_names = text_wig.tag_names(index=None)
    for tag_n in tag_names:
        ret[tag_n] = text_wig.tag_ranges(tag_n)
    return ret


def set_all_tags(text_wig, tag_dic):
    for tag_n in list(tag_dic.keys()):
        tag_list = tag_dic[tag_n]
        tmp = []
        for el in tag_list:
            tmp.append(el)
            if len(tmp) == 2:
                text_wig.tag_add(tag_n, tmp[0], tmp[1])
                tmp = []


def set_new_tags(text_wig, tag_list):
    tmp = 1
    for a in tag_list:
        tmp += a[1]
    for el in tag_list:
        tag_name, tag_len = el
        if tag_len:
            ind = text_wig.index(f'end-{tmp}c')
            ind2 = f'{ind}+{tag_len}c'
            text_wig.tag_add(tag_name, ind, ind2)
            tmp -= tag_len


def cleanup_tags(tag_ranges):
    ret = {}
    for tag_n in tag_ranges:
        ret[tag_n] = []
        for el in tag_ranges[tag_n]:
            if hasattr(el, 'string'):
                ret[tag_n].append(el.string)
            else:
                ret[tag_n].append(el)
    return ret


def generate_random_hex_color(a=0, b=255):
    red = random.randint(a, b)
    green = random.randint(a, b)
    blue = random.randint(a, b)

    hex_color = "#{:02x}{:02x}{:02x}".format(red, green, blue)

    return hex_color


def match_string(add_list, entry_var):
    """ Source: https://stackoverflow.com/questions/58428545/clarify-functionality-of-tkinter-autocomplete-entry"""
    hits = []
    got = entry_var.get()
    for item in add_list:
        if item.startswith(got.upper()):
            hits.append(item)
    return hits


def get_typed(event, add_list, entry_var, entry):
    """ Source: https://stackoverflow.com/questions/58428545/clarify-functionality-of-tkinter-autocomplete-entry"""
    if len(event.keysym) == 1:
        hits = match_string(add_list, entry_var)
        show_hit(hits, entry_var, entry)


def show_hit(lst, entry_var, entry):
    """ Source: https://stackoverflow.com/questions/58428545/clarify-functionality-of-tkinter-autocomplete-entry"""
    if len(lst) == 1:
        pos = entry.index('insert')
        entry_var.set(lst[0])
        entry.selection_range(pos, 'end')


def detect_pressed(event, entry):
    """ Source: https://stackoverflow.com/questions/58428545/clarify-functionality-of-tkinter-autocomplete-entry"""
    key = event.keysym
    if len(key) == 1:
        pos = entry.index('insert')
        entry.delete(pos, 'end')


def get_image(image_path: str, size=(16, 16)):
    try:
        image = Image.open(image_path)
        image = image.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as ex:
        logger.error(f"Error while loading {image_path}. Size: {size}")
        logger.error(ex)
    return None

def build_aprs_icon_tab(size=(16, 16)):
    get_path = lambda f_name: f"{CFG_aprs_icon_path}/{f_name}.png"
    return {
        # Table 0 ( / )
        ("/", "!"): get_image(get_path("0-01"), size),
        ("/", '"'): get_image(get_path("0-02"), size),
        ("/", "#"): get_image(get_path("0-03"), size),
        ("/", "$"): get_image(get_path("0-04"), size),
        ("/", "%"): get_image(get_path("0-05"), size),
        ("/", "&"): get_image(get_path("0-06"), size),
        ("/", "'"): get_image(get_path("0-07"), size),
        ("/", "("): get_image(get_path("0-08"), size),
        ("/", ")"): get_image(get_path("0-09"), size),
        ("/", "*"): get_image(get_path("0-10"), size),
        ("/", "+"): get_image(get_path("0-11"), size),
        ("/", ","): get_image(get_path("0-12"), size),
        ("/", "-"): get_image(get_path("0-13"), size),
        ("/", "."): get_image(get_path("0-14"), size),
        ("/", "/"): get_image(get_path("0-15"), size),
        ("/", "0"): get_image(get_path("0-16"), size),

        ("/", "1"): get_image(get_path("0-17"), size),
        ("/", "2"): get_image(get_path("0-18"), size),
        ("/", "3"): get_image(get_path("0-19"), size),
        ("/", "4"): get_image(get_path("0-20"), size),
        ("/", "5"): get_image(get_path("0-21"), size),
        ("/", "6"): get_image(get_path("0-22"), size),
        ("/", "7"): get_image(get_path("0-23"), size),
        ("/", "8"): get_image(get_path("0-24"), size),
        ("/", "9"): get_image(get_path("0-25"), size),
        ("/", ":"): get_image(get_path("0-26"), size),
        ("/", ";"): get_image(get_path("0-27"), size),
        ("/", "<"): get_image(get_path("0-28"), size),
        ("/", "="): get_image(get_path("0-29"), size),
        ("/", ">"): get_image(get_path("0-30"), size),
        ("/", "?"): get_image(get_path("0-31"), size),
        ("/", "@"): get_image(get_path("0-32"), size),

        ("/", "A"): get_image(get_path("0-33"), size),
        ("/", "B"): get_image(get_path("0-34"), size),
        ("/", "C"): get_image(get_path("0-35"), size),
        ("/", "D"): get_image(get_path("0-36"), size),
        ("/", "E"): get_image(get_path("0-37"), size),
        ("/", "F"): get_image(get_path("0-38"), size),
        ("/", "G"): get_image(get_path("0-39"), size),
        ("/", "H"): get_image(get_path("0-40"), size),
        ("/", "I"): get_image(get_path("0-41"), size),
        ("/", "J"): get_image(get_path("0-42"), size),
        ("/", "K"): get_image(get_path("0-43"), size),
        ("/", "L"): get_image(get_path("0-44"), size),
        ("/", "M"): get_image(get_path("0-45"), size),
        ("/", "N"): get_image(get_path("0-46"), size),
        ("/", "O"): get_image(get_path("0-47"), size),
        ("/", "P"): get_image(get_path("0-48"), size),

        ("/", "Q"): get_image(get_path("0-49"), size),
        ("/", "R"): get_image(get_path("0-50"), size),
        ("/", "S"): get_image(get_path("0-51"), size),
        ("/", "T"): get_image(get_path("0-52"), size),
        ("/", "U"): get_image(get_path("0-53"), size),
        ("/", "V"): get_image(get_path("0-54"), size),
        ("/", "W"): get_image(get_path("0-55"), size),
        ("/", "X"): get_image(get_path("0-56"), size),
        ("/", "Y"): get_image(get_path("0-57"), size),
        ("/", "Z"): get_image(get_path("0-58"), size),
        ("/", "["): get_image(get_path("0-59"), size),
        ("/", "\\"): get_image(get_path("0-60"), size),
        ("/", "]"): get_image(get_path("0-61"), size),
        ("/", "^"): get_image(get_path("0-62"), size),
        ("/", "_"): get_image(get_path("0-63"), size),
        ("/", "`"): get_image(get_path("0-64"), size),

        ("/", "a"): get_image(get_path("0-65"), size),
        ("/", "b"): get_image(get_path("0-66"), size),
        ("/", "c"): get_image(get_path("0-67"), size),
        ("/", "d"): get_image(get_path("0-68"), size),
        ("/", "e"): get_image(get_path("0-69"), size),
        ("/", "f"): get_image(get_path("0-70"), size),
        ("/", "g"): get_image(get_path("0-71"), size),
        ("/", "h"): get_image(get_path("0-72"), size),
        ("/", "i"): get_image(get_path("0-73"), size),
        ("/", "j"): get_image(get_path("0-74"), size),
        ("/", "k"): get_image(get_path("0-75"), size),
        ("/", "l"): get_image(get_path("0-76"), size),
        ("/", "m"): get_image(get_path("0-77"), size),
        ("/", "n"): get_image(get_path("0-78"), size),
        ("/", "o"): get_image(get_path("0-79"), size),
        ("/", "p"): get_image(get_path("0-80"), size),

        ("/", "q"): get_image(get_path("0-81"), size),
        ("/", "r"): get_image(get_path("0-82"), size),
        ("/", "s"): get_image(get_path("0-83"), size),
        ("/", "t"): get_image(get_path("0-84"), size),
        ("/", "u"): get_image(get_path("0-85"), size),
        ("/", "v"): get_image(get_path("0-86"), size),
        ("/", "w"): get_image(get_path("0-87"), size),
        ("/", "x"): get_image(get_path("0-88"), size),
        ("/", "y"): get_image(get_path("0-89"), size),
        ("/", "z"): get_image(get_path("0-90"), size),
        ("/", "{"): get_image(get_path("0-91"), size),
        #("/", ""): get_image(get_path("0-92"), size),
        ("/", "}"): get_image(get_path("0-93"), size),
        #("/", ""): get_image(get_path("0-94"), size),
        #("/", ""): get_image(get_path("0-95"), size),
        #("/", ""): get_image(get_path("0-96"), size),
        # Table 1 ( \ )
        ("\\", "!"): get_image(get_path("1-01"), size),
        ("\\", '"'): get_image(get_path("1-02"), size),
        ("\\", "#"): get_image(get_path("1-03"), size),
        ("\\", "$"): get_image(get_path("1-04"), size),
        ("\\", "%"): get_image(get_path("1-05"), size),
        ("\\", "&"): get_image(get_path("1-06"), size),
        ("\\", "'"): get_image(get_path("1-07"), size),
        ("\\", "("): get_image(get_path("1-08"), size),
        ("\\", ")"): get_image(get_path("1-09"), size),
        ("\\", "*"): get_image(get_path("1-10"), size),
        ("\\", "+"): get_image(get_path("1-11"), size),
        ("\\", ","): get_image(get_path("1-12"), size),
        ("\\", "-"): get_image(get_path("1-13"), size),
        ("\\", "."): get_image(get_path("1-14"), size),
        ("\\", "/"): get_image(get_path("1-15"), size),
        ("\\", "0"): get_image(get_path("1-16"), size),

        ("\\", "1"): get_image(get_path("1-17"), size),
        ("\\", "2"): get_image(get_path("1-18"), size),
        ("\\", "3"): get_image(get_path("1-19"), size),
        ("\\", "4"): get_image(get_path("1-20"), size),
        ("\\", "5"): get_image(get_path("1-21"), size),
        ("\\", "6"): get_image(get_path("1-22"), size),
        ("\\", "7"): get_image(get_path("1-23"), size),
        ("\\", "8"): get_image(get_path("1-24"), size),
        ("\\", "9"): get_image(get_path("1-25"), size),
        ("\\", ":"): get_image(get_path("1-26"), size),
        ("\\", ";"): get_image(get_path("1-27"), size),
        ("\\", "<"): get_image(get_path("1-28"), size),
        ("\\", "="): get_image(get_path("1-29"), size),
        ("\\", ">"): get_image(get_path("1-30"), size),
        ("\\", "?"): get_image(get_path("1-31"), size),
        ("\\", "@"): get_image(get_path("1-32"), size),

        ("\\", "A"): get_image(get_path("1-33"), size),
        ("\\", "B"): get_image(get_path("1-34"), size),
        ("\\", "C"): get_image(get_path("1-35"), size),
        ("\\", "D"): get_image(get_path("1-36"), size),
        ("\\", "E"): get_image(get_path("1-37"), size),
        ("\\", "F"): get_image(get_path("1-38"), size),
        ("\\", "G"): get_image(get_path("1-39"), size),
        ("\\", "H"): get_image(get_path("1-40"), size),
        ("\\", "I"): get_image(get_path("1-41"), size),
        ("\\", "J"): get_image(get_path("1-42"), size),
        ("\\", "K"): get_image(get_path("1-43"), size),
        ("\\", "L"): get_image(get_path("1-44"), size),
        ("\\", "M"): get_image(get_path("1-45"), size),
        ("\\", "N"): get_image(get_path("1-46"), size),
        ("\\", "O"): get_image(get_path("1-47"), size),
        ("\\", "P"): get_image(get_path("1-48"), size),

        ("\\", "Q"): get_image(get_path("1-49"), size),
        ("\\", "R"): get_image(get_path("1-50"), size),
        ("\\", "S"): get_image(get_path("1-51"), size),
        ("\\", "T"): get_image(get_path("1-52"), size),
        ("\\", "U"): get_image(get_path("1-53"), size),
        ("\\", "V"): get_image(get_path("1-54"), size),
        ("\\", "W"): get_image(get_path("1-55"), size),
        ("\\", "X"): get_image(get_path("1-56"), size),
        ("\\", "Y"): get_image(get_path("1-57"), size),
        ("\\", "Z"): get_image(get_path("1-58"), size),
        ("\\", "["): get_image(get_path("1-59"), size),
        ("\\", "\\"): get_image(get_path("1-60"), size),
        ("\\", "]"): get_image(get_path("1-61"), size),
        ("\\", "^"): get_image(get_path("1-62"), size),
        ("\\", "_"): get_image(get_path("1-63"), size),
        ("\\", "`"): get_image(get_path("1-64"), size),

        ("\\", "a"): get_image(get_path("1-65"), size),
        ("\\", "b"): get_image(get_path("1-66"), size),
        ("\\", "c"): get_image(get_path("1-67"), size),
        ("\\", "d"): get_image(get_path("1-68"), size),
        ("\\", "e"): get_image(get_path("1-69"), size),
        ("\\", "f"): get_image(get_path("1-70"), size),
        ("\\", "g"): get_image(get_path("1-71"), size),
        ("\\", "h"): get_image(get_path("1-72"), size),
        ("\\", "i"): get_image(get_path("1-73"), size),
        ("\\", "j"): get_image(get_path("1-74"), size),
        ("\\", "k"): get_image(get_path("1-75"), size),
        ("\\", "l"): get_image(get_path("1-76"), size),
        ("\\", "m"): get_image(get_path("1-77"), size),
        ("\\", "n"): get_image(get_path("1-78"), size),
        ("\\", "o"): get_image(get_path("1-79"), size),
        ("\\", "p"): get_image(get_path("1-80"), size),

        ("\\", "q"): get_image(get_path("1-81"), size),
        ("\\", "r"): get_image(get_path("1-82"), size),
        ("\\", "s"): get_image(get_path("1-83"), size),
        ("\\", "t"): get_image(get_path("1-84"), size),
        ("\\", "u"): get_image(get_path("1-85"), size),
        ("\\", "v"): get_image(get_path("1-86"), size),
        ("\\", "w"): get_image(get_path("1-87"), size),
        ("\\", "x"): get_image(get_path("1-88"), size),
        ("\\", "y"): get_image(get_path("1-89"), size),
        ("\\", "z"): get_image(get_path("1-90"), size),
        ("\\", "{"): get_image(get_path("1-91"), size),
        #("\\", ""): get_image(get_path("1-92"), size),
        ("\\", "}"): get_image(get_path("1-93"), size),
        #("\\", ""): get_image(get_path("1-94"), size),
        #("\\", ""): get_image(get_path("1-95"), size),
        #("\\", ""): get_image(get_path("1-96"), size),
    }

#################################
# Tree
def delete_tree(tree: ttk.Treeview):
    for i in tree.get_children():
        tree.delete(i)

#################################
# Text Widgets
def limit_ch_vars_output(ch_vars, max_lines=5000):
    text = ch_vars.output_win
    if not text:
        return

    eol  = find_eol_in_str(text, default='\n')
    text = zeilenumbruch_lines(text, PARAM_MAX_MON_WIDTH, eol)

    newlines = text.count(eol)
    if text.endswith(eol):
        tk_lines = newlines
    else:
        tk_lines = newlines + 1

    if tk_lines <= max_lines:
        return

    remove_count = tk_lines - max_lines

    count = 0
    trim_pos = 0
    for i, c in enumerate(text):
        if c == eol:
            count += 1
            if count == remove_count:
                trim_pos = i + 1
                break

    if trim_pos == 0:
        return

    removed_chars = trim_pos
    old_len = len(text)

    ch_vars.output_win = text[trim_pos:]

    old_text_len = old_len - sum(l for _, l in ch_vars.new_tags)

    if removed_chars > old_text_len:
        removed_from_new = removed_chars - old_text_len
        cum_len = 0
        tags_to_keep = []
        for tag_name, tag_len in ch_vars.new_tags:
            if cum_len + tag_len <= removed_from_new:
                cum_len += tag_len
                continue
            elif cum_len < removed_from_new:
                new_len = cum_len + tag_len - removed_from_new
                tags_to_keep.append((tag_name, new_len))
                cum_len += tag_len
            else:
                tags_to_keep.append((tag_name, tag_len))
                cum_len += tag_len
        ch_vars.new_tags = tags_to_keep

    if ch_vars.output_win_tags:
        result = {}
        for tag_name, ranges in ch_vars.output_win_tags.items():
            new_ranges = []
            for i in range(0, len(ranges), 2):
                start = str(ranges[i])
                end = str(ranges[i + 1])
                start_line = int(start.split('.')[0])
                end_line = int(end.split('.')[0])
                if start_line > remove_count:
                    start_char = start.split('.')[1]
                    end_char = end.split('.')[1]
                    new_start = f"{start_line - remove_count}.{start_char}"
                    new_end = f"{end_line - remove_count}.{end_char}"
                    new_ranges.extend([new_start, new_end])
                elif end_line > remove_count:
                    end_char = end.split('.')[1]
                    new_start = "1.0"
                    new_end = f"{end_line - remove_count}.{end_char}"
                    new_ranges.extend([new_start, new_end])
            if new_ranges:
                result[tag_name] = new_ranges
        ch_vars.output_win_tags = result

def text_widget_select_all(text_ent: tk.Text or tk.scrolledtext):
    text_ent.tag_remove("send", "1.0", tk.END)
    text_ent.tag_add(tk.SEL, "1.0", tk.END)
    text_ent.mark_set(tk.INSERT, "1.0")  # Setzt den Cursor an den Anfang
    text_ent.see(tk.INSERT)  #


