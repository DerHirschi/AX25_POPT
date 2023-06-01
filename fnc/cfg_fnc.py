def cleanup_obj(class_obj: object):
    for att in dir(class_obj):
        if '__' not in att and not callable(getattr(class_obj, att)):
            setattr(class_obj, att, getattr(class_obj, att))
    return class_obj


def set_obj_att(new_obj: object, input_obj: object):
    inp = cleanup_obj(input_obj)
    for att in dir(inp):
        if '__' not in att:
            setattr(new_obj, att, getattr(inp, att))
    return new_obj


def cleanup_obj_dict(inp_dict: dict):
    tmp = {}
    for k in inp_dict.keys():
        tmp[k] = cleanup_obj(inp_dict[k])
    return tmp
