import random


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
