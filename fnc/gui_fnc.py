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
