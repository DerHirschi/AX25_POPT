import pickle
import os

import logging

from cfg.constant import CFG_data_path, CFG_usertxt_path
from cfg.default_config import getNew_pipe_cfg, getNew_station_cfg

logger = logging.getLogger(__name__)


def cleanup_obj(class_obj: object):
    for att in dir(class_obj):
        if '__' not in att and not callable(getattr(class_obj, att)):
            setattr(class_obj, att, getattr(class_obj, att))
    return class_obj


def convert_obj_to_dict(class_obj: object):
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
        tmp[k] = convert_obj_to_dict(inp_dict[k])
    return tmp


def save_to_file(filename: str, data):
    try:
        with open(CFG_data_path + filename, 'wb') as f:
            pickle.dump(data, f, 2)
    except FileNotFoundError:
        with open(CFG_data_path + filename, 'xb') as f:
            pickle.dump(data, f, 2)
    except EOFError as e:
        print(f"save_to_file Error: {e}")
        logger.error(f"save_to_file Error: {e}")
        logger.error(f"save_to_file Error: {data}")
        print(f"save_to_file Error: {data}")
    except TypeError as e:
        print(f"save_to_file Error: {e}")
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


def get_all_pipe_cfg():
    stat_cfg_path = CFG_data_path + CFG_usertxt_path
    stat_cfg = [x[0] for x in os.walk(stat_cfg_path)]
    ret = {}
    if len(stat_cfg) > 1:
        stat_cfg = stat_cfg[1:]
        for folder in stat_cfg:
            call = folder.split('/')[-1]
            temp = {}
            try:
                with open(folder + '/stat' + call + '.popt', 'rb') as inp:
                    temp = pickle.load(inp)
            except (FileNotFoundError, EOFError):
                pass
            except ImportError:
                logger.error(
                    f"Pipe CFG: Falsche Version der CFG Datei. Bitte {folder + '/stat' + call + '.popt'} löschen und PoPT neu starten!")
                pass
            if temp and call:
                loaded_pipe_cfg = temp.get('pipe_cfg', {})
                if loaded_pipe_cfg:
                    default_pipe_cfg = getNew_pipe_cfg()
                    for cfg_keys in list(loaded_pipe_cfg.keys()):
                        default_pipe_cfg[cfg_keys] = loaded_pipe_cfg[cfg_keys]
                    ret[call] = default_pipe_cfg
    return ret


def save_station_to_file(conf):
    if conf.stat_parm_Call != getNew_station_cfg().get('stat_parm_Call', ''):
        exist_userpath(conf.stat_parm_Call)
        file = '{1}{0}/stat{0}.popt'.format(conf.stat_parm_Call, CFG_usertxt_path)
        save_station = {}
        for att in dir(conf):
            if '__' not in att and not callable(getattr(conf, att)):
                save_station[att] = getattr(conf, att)

        # if conf.stat_parm_pipe:
        # pipe_cfgs = POPT_CFG.get_pipe_CFG()
        # if conf.stat_parm_Call in pipe_cfgs.keys():
        # pipecfg = pipe_cfgs[conf.stat_parm_Call]
        # save_station.stat_parm_pipe = True
        # save_station['pipe_cfg'] = pipe_cfgs
        """
        save_station['stat_parm_pipe_tx'] = pipecfg.stat_parm_pipe.tx_filename
        save_station['stat_parm_pipe_rx'] = pipecfg.stat_parm_pipe.rx_filename
        save_station['stat_parm_pipe_loop_timer'] = pipecfg.stat_parm_pipe.parm_tx_file_check_timer
        save_station['stat_parm_pipe'] = True
        """


        save_to_file(file, save_station)


def exist_userpath(usercall: str):
    if not os.path.exists(CFG_data_path + CFG_usertxt_path + usercall):
        # print(CFG_data_path + CFG_usertxt_path + usercall)
        os.makedirs(CFG_data_path + CFG_usertxt_path + usercall)
        return False
    return True
