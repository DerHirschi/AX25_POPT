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


def generate_random_hex_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)

    hex_color = "#{:02x}{:02x}{:02x}".format(red, green, blue)

    return hex_color


"""
ent = tk.Entry()
ent.bind('<KeyRelease>', lambda event: get_typed(event, self.chiefs, self._to_call_var, self._to_call_ent))
ent.bind('<Key>', lambda event: detect_pressed(event, self._to_call_ent))
"""


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

