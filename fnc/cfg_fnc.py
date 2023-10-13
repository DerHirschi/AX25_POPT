import pickle

import logging
from constant import CFG_data_path

logger = logging.getLogger(__name__)


def cleanup_obj(class_obj: object):
    for att in dir(class_obj):
        if '__' not in att and not callable(getattr(class_obj, att)):
            setattr(class_obj, att, getattr(class_obj, att))
    return class_obj


def cleanup_obj_to_dict(class_obj: object):
    out = {}
    for att in dir(class_obj):
        if '__' not in att and not callable(getattr(class_obj, att)):
            out[att] = getattr(class_obj, att)
    return out


def set_obj_att(new_obj: object, input_obj: object):
    inp = cleanup_obj(input_obj)
    for att in dir(inp):
        if hasattr(new_obj, att):
            if '__' not in att and not callable(getattr(new_obj, att)) and not callable(getattr(input_obj, att)):
                setattr(new_obj, att, getattr(inp, att))
    return new_obj


def set_obj_att_fm_dict(new_obj: object, input_obj: dict):
    for att in list(input_obj.keys()):
        if hasattr(new_obj, att):
            if '__' not in att and not callable(getattr(new_obj, att)):
                setattr(new_obj, att, input_obj[att])
    return new_obj


def cleanup_obj_dict(inp_dict: dict):
    tmp = {}
    for k in inp_dict.keys():
        # tmp[k] = cleanup_obj(inp_dict[k])
        tmp[k] = cleanup_obj_to_dict(inp_dict[k])
    return tmp


def save_to_file(filename: str, data):
    try:
        with open(CFG_data_path + filename, 'wb') as f:
            pickle.dump(data, f, 2)
    except FileNotFoundError:
        with open(CFG_data_path + filename, 'xb') as f:
            pickle.dump(data, f, 2)
    except EOFError:
        pass
    except TypeError as e:
        logger.error(f"save_to_file Error: {e}")
        logger.error(f"save_to_file Error: {data}")
        print(f"save_to_file Error: {data}")


def load_fm_file(filename: str):
    try:
        with open(CFG_data_path + filename, 'rb') as inp:
            return pickle.load(inp)
    except (FileNotFoundError, EOFError):
        return ''
    except ImportError:
        logger.error(
            f"CFG: Falsche Version der CFG Datei. Bitte {CFG_data_path + filename} löschen und PoPT neu starten!")
        raise
