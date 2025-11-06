"""
TODO: Cleanup/Again/Crap
"""
import sys
# import datetime
import os
import pickle
import json
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG

from fnc.ax25_fnc import call_tuple_fm_call_str, validate_ax25Call, validate_aprs_call
from cfg.cfg_fnc import set_obj_att, cleanup_obj_dict, set_obj_att_fm_dict
from fnc.loc_fnc import locator_to_coordinates, locator_distance, coordinates_to_locator, clean_locator
from fnc.str_fnc import conv_time_for_sorting, conv_time_DE_str, str_to_datetime
from cfg.constant import CFG_user_db, MH_BEACON_FILTER, CFG_user_db_json


class Client(object):
    # def __init__(self, call):
    call_str = 'NOCALL'
    Call = 'NOCALL'
    SSID = 0
    Alias = ''
    TYP = ''

    Name = ''
    Land = ''
    ZIP = ''
    QTH = ''
    LOC = ''
    Lat = 0
    Lon = 0
    Distance = 0
    PRmail = ''
    Email = ''
    HTTP = ''
    Info = ''

    NODE = []
    BBS = []
    Other = []
    Sysop_Call = ''

    #via_NODE_HF = ''
    #via_NODE_AXIP = ''
    AXIP = '', 0
    QRG1 = ''  # 27.235FM-1200-AD/AI/FX
    QRG2 = ''
    QRG3 = ''
    QRG4 = ''
    QRG5 = ''
    Software = ''

    last_edit = conv_time_DE_str()
    # last_seen = datetime.datetime.now() # TODO Get from MH
    last_conn       = None
    Connects        = 0
    # GUI OPT
    Encoding        = 'CP437'    # 'UTF-8'
    pac_len         = 0
    max_pac         = 0
    CText           = ''
    routes          = []
    software_str    = ''
    sys_pw          = ''
    sys_pw_autologin = False
    sys_pw_parm     = [5, 80, 'SYS']
    # CLI
    cli_sidestop    = 20
    Language        = -1
    bbs_newUser     = True
    # BOX
    # box_user_cfg = {}

class UserDB:
    def __init__(self):
        # print("User-DB Init")
        self._logTag = "User-DB: "
        logger.info("User-DB: Init")
        self.not_public_vars = [    # TODO public Vars or new CLI CMD / CLI-Tab
            'not_public_vars',
            'call_str',
            'is_new',
            'pac_len',
            'max_pac',
            'CText',
            'routes',
            'software_str',
            'sys_pw',
            'sys_pw_parm',
            'sys_pw_autologin',
            'boxopt_sidestop',
            'cli_sidestop',
            'Language',
            'Encoding',
            'QRG1',
            'QRG2',
            'QRG3',
            'QRG4',
            'QRG5',
            'box_user_cfg',
            'bbs_newUser',
            'last_conn',

        ]
        self.db = {}
        db_load = {}
        logger.info(f"User-DB: loading UserDB fm {CFG_user_db_json} ")
        try:
            with open(CFG_user_db_json, 'rb') as inp:
                db_load = json.load(inp)
            """
            for ke in self.db.keys():
                print(ke)
            """
        except FileNotFoundError:
            logger.warning(f"Error while loading USER-DB json format.")
            logger.warning(f"Try to load USER-DB with old pickle format.")
            try:
                with open(CFG_user_db, 'rb') as inp:
                    db_load = pickle.load(inp)
            except ImportError:
                logger.error(
                    f"User-DB: Falsche Version der DB Datei. Bitte {CFG_user_db} löschen und PoPT neu starten!")
                raise
            except Exception as ex:
                logger.error(f"User-DB: Error while loading: {ex}")
            except FileNotFoundError:
                logger.warning(f"User-DB: {CFG_user_db_json} not found. Creating new User-DB !")
                if 'linux' in sys.platform:
                    os.system('touch {}'.format(CFG_user_db_json))

        except EOFError:
            logger.warning(f"User-DB: Can't open {CFG_user_db_json} !!!")
        except ImportError:
            logger.error(f"User-DB: Falsche Version der DB Datei. Bitte {CFG_user_db_json} löschen und PoPT neu starten!")
            raise
        except Exception as ex:
            logger.error(f"User-DB: Error while loading: {ex}")

        default_client = Client()
        # default_client.is_new = False
        default_client.call_str = 'ALL'
        default_client.call = 'ALL'
        default_client.SSID = 0
        default_client.name = 'Beacon'
        default_client.typ = 'BEACON'
        self.db = {
            'ALL': default_client
        }
        for k in list(db_load.keys()):
            client_obj = Client()
            if type(db_load[k]) is dict:
                self.db[k] = set_obj_att_fm_dict(new_obj=client_obj, input_obj=db_load[k])
            else:
                self.db[k] = set_obj_att(new_obj=client_obj, input_obj=db_load[k])

            # "Repair old Data" TODO . CLEANUP
            if k != self.db[k].Call:
                if type(self.db[k].call_str) is str:
                    call_tup = call_tuple_fm_call_str(self.db[k].call_str)
                    self.db[k].Call = str(call_tup[0])
                    self.db[k].SSID = int(call_tup[1])
                else:
                    self.db[k].call_str = str(k)
                    self.db[k].Call = str(k)
                    self.db[k].SSID = 0
        ########################
        # Convert fm old USer-DB
        for k, db_entry in self.db.items():
            if type(db_entry.last_edit) != str:
                db_entry.last_edit = conv_time_DE_str(db_entry.last_edit)
            if type(db_entry.last_conn) == str:
                db_entry.last_conn = str_to_datetime(db_entry.last_conn)
        logger.info("User-DB: Init complete")

    def get_entry(self, call_str: str, add_new=True):
        # call_str = validate_ax25Call(call_str)
        if not hasattr(call_str, 'upper'):
            call_str = str(call_str)
        call_str = validate_aprs_call(call_str.upper())
        if call_str:
            call_tup = call_tuple_fm_call_str(call_str)
            if call_str not in self.db.keys():
                if call_tup[0] not in self.db.keys():
                    if add_new:
                        return self._new_entry(call_str)
                    else:
                        return None
                else:
                    # self.entry_var_upgrade(call_tup[0])
                    return self.db[call_tup[0]]
            # self.entry_var_upgrade(call_str)
            return self.db[call_str]
        return None

    def _new_entry(self, call_str):
        call_str = call_str.upper()
        if call_str in MH_BEACON_FILTER:
            return False
        if not validate_ax25Call(call_str):
            return False
        if call_str in self.db.keys():
            return self.db[call_str]
        call_tup = call_tuple_fm_call_str(call_str)
        # if call_tup[0] not in self.db.keys():
        # print('# User DB: New User added > ' + call_str)
        logger.info('User DB: New User added > ' + call_str)
        self.db[call_str] = Client()
        self.db[call_str].call_str = str(call_str)
        self.db[call_str].Call = str(call_tup[0])
        self.db[call_str].SSID = int(call_tup[1])
        return self.db[call_str]

    def del_entry(self, call_str: str):
        if call_str in self.db.keys():
            del self.db[call_str]
            return True
        return False

    def set_typ(self, call_str: str, typ: str, add_new=True, overwrite=False):
        ent = self.get_entry(call_str, add_new)
        if not ent:
            return
        if overwrite:
            ent.TYP = typ
        else:
            if not ent.TYP:
                ent.TYP = typ
    def get_typ(self, call_str: str):
        ent = self.get_entry(call_str, False)
        if not ent:
            return ''
        return ent.TYP

    def set_distance(self, entry_call: str):
        own_loc = POPT_CFG.get_guiCFG_locator()
        if not own_loc:
            return False
        ent = self.get_entry(entry_call, False)
        if not ent:
            return False
        if not ent.LOC:
            ent.Distance = -1
            return False
        ent.LOC = clean_locator(ent.LOC)
        ent.Distance = locator_distance(own_loc, ent.LOC)
        return True

    def set_distance_for_all(self):
        for k in list(self.db.keys()):
            self.set_distance(k)

    def get_keys_by_typ(self, typ='SYSOP'):
        ret = []
        for k in list(self.db.keys()):
            if self.db[k].TYP == typ:
                ret.append(k)
        return ret

    def get_keys_by_sysop(self, sysop: str):
        ret = {
            'NODE': [],
            'BBS': [],
        }
        for k in self.db.keys():
            if sysop == self.db[k].Sysop_Call:
                if self.db[k].TYP in ret.keys():
                    ret[self.db[k].TYP].append(k)
                else:
                    ret[self.db[k].TYP] = [k]
        return ret

    def update_var_fm_dbentry(self, fm_key: str, to_key: str):
        if fm_key not in self.db.keys():
            return False
        if to_key not in self.db.keys():
            return False
        # new_obj = Client(to_key)
        # print(self.db[to_key])
        for att in list(dir(self.db[to_key])):
            if '__' not in att:
                if not getattr(self.db[to_key], att) and att not in [
                    'software_str',
                    'Software',
                    'routes',
                    'Alias',
                    'TYP',
                    'NODE',
                    'BBS',
                    'Other',
                    'Sysop_Call',
                    'Connects',
                    'CText',
                    'last_edit',
                    'last_seen',
                    'Encoding',
                    'sys_pw',
                    'sys_pw_parm',
                    'Distance',
                ]:
                    setattr(self.db[to_key], att, getattr(self.db[fm_key], att))
                """
                else:
                    setattr(self.db[to_key], att, getattr(self.db[to_key], att))
                """
        if self.db[to_key].TYP != 'SYSOP':
            if self.db[to_key].Name and self.db[to_key].TYP:
                self.db[to_key].Name = f"{self.db[to_key].TYP}-{self.db[to_key].Name}"
            elif self.db[to_key].TYP:
                self.db[to_key].Name = f"{self.db[to_key].TYP}-{self.db[to_key].call_str}"

        # self.db[to_key] = new_obj

    def get_sort_entr(self, flag_str: str, reverse: bool):
        # TODO Move to UserDBtreeview
        temp = {}
        self.db: {str: Client}
        for k in list(self.db.keys()):
            flag: Client = self.db[k]
            """ Update new Vars .. 
            if not hasattr(flag, 'Distance'):
                flag.Distance = 0
            """
            key: str = {
                'call': str(flag.call_str),
                'sysop': str(flag.Sysop_Call),
                'typ': str(flag.TYP),
                'loc': str(flag.LOC),
                'qth': str(flag.QTH),
                'dist': flag.Distance,
                'land': str(flag.Land),
                'last_conn': '---' if flag.last_conn is None else conv_time_for_sorting(flag.last_conn),
                # 'last_seen': conv_time_for_sorting(flag.last_seen), # TODO Get from MH
            }[flag_str]
            while key in temp.keys():
                if type(key) is not str:
                    break
                key += '1'
            temp[key] = self.db[k]

        temp_k = list(temp.keys())
        temp_k.sort()
        if not reverse:
            temp_k.reverse()
        temp_ret = {}
        for k in temp_k:
            temp_ret[k] = temp[k]
        return temp_ret

    def get_qth(self, call_str):
        ent = self.get_entry(call_str, add_new=False)
        if not ent:
            return ''
        return ent.QTH

    def get_distance(self, call_str):
        ent = self.get_entry(call_str, add_new=False)
        if not ent:
            return 0
        return float(ent.Distance)

    def get_locator(self, call_str):
        ent = self.get_entry(call_str, add_new=False)
        if not ent:
            return ''
        return str(ent.LOC)

    def get_location(self, call_str):
        ent = self.get_entry(call_str, add_new=False)
        if not ent:
            return 0, 0, ''
        if all((ent.Lat, ent.Lon, ent.LOC)) :
            return ent.Lat, ent.Lon, ent.LOC
        if ent.LOC and not any((ent.Lat, ent.Lon)):
            ent.Lat, ent.Lon = locator_to_coordinates(ent.LOC)
            return ent.Lat, ent.Lon, ent.LOC
        if any((ent.Lat, ent.Lon)) and not ent.LOC:
            ent.LOC = coordinates_to_locator(ent.Lat, ent.Lon)
            return ent.Lat, ent.Lon, ent.LOC
        return 0, 0, ''

    def get_AXIP(self, call_str):
        ret = self.db.get(call_str, None)
        if ret:
            return ret.AXIP
        call = call_tuple_fm_call_str(call_str)[0]
        ret = self.db.get(call, None)
        if ret:
            return ret.AXIP
        return '', 0

    def set_AXIP(self, call_str: str, axip: tuple, new_user=False):
        if not all((call_str, axip)):
            return False
        if not axip[0]:
            return False
        if not self.db.get(call_str, None):
            if not new_user:
                return False
            self._new_entry(call_str)
        self.db[call_str].AXIP = tuple(axip)
        return True

    def set_PRmail_BBS_address(self, address: str, ):
        call_str = address.split('.')[0]
        if not call_str:
            return
        ent = self.get_entry(call_str, True)
        if not ent:
            return
        if not ent.TYP:
            ent.TYP = 'BBS'
        ent.PRmail = address

    def set_PRmail_address(self, address: str, overwrite = False):
        if not address:
            return
        call = address.split('@')[0].split('.')[0]
        ent = self.get_entry(call, True)
        if not ent:
            return
        if ent.PRmail and not overwrite:
            return
        if ent.TYP == 'BBS':
            bbs_address = address.split('@')[-1]
            if '.' in bbs_address:
                ent.PRmail  = bbs_address
            return
        if '@' in address:
            ent.PRmail = address

    def get_all_PRmail(self):
        ret = []
        for k in list(self.db.keys()):
            if self.db[k].TYP == 'SYSOP':
                if self.db[k].PRmail:
                    ret.append(self.db[k].PRmail)
        return ret

    def get_PRmail(self, call: str):
        return self.db.get(call, Client).PRmail

    ##########################################
    def get_database(self):
        return dict(self.db)

    ##########################################
    def save_data(self):
        # print('Save Client DB')
        logger.info('User-DB: Save User-DB')
        for k, db_entry in self.db.items():
            if type(db_entry.last_conn) != str:
                db_entry.last_conn = conv_time_DE_str(db_entry.last_conn)
        tmp = cleanup_obj_dict(self.db)
        try:
            with open(CFG_user_db_json, 'w') as savefile:
                json.dump(tmp, savefile)
        except FileNotFoundError as e:
            # print("ERROR SAVE ClientDB: " + str(e))
            logger.error("User-DB: Save User-DB > " + str(e))
        except Exception as e:
            logger.error(f"User-DB: Save User-DB > {e}")


USER_DB = UserDB()
# USER_DB.get_all_PRmail()
"""
class AXIPClientDB(object):

    def cli_cmd_out(self):
        out = ''
        out += '\r                       < AXIP - Clients >\r\r'
        out += '-Call-----IP:Port---------------Timeout------------------\r'
        for ke in self.clients.keys():
            out += '{:9} {:21} {:8}\r'.format(
                ke,
                self.clients[ke]['addr'][0] + ':' + str(self.clients[ke]['addr'][1]),
                round(time.time() - self.clients[ke]['lastsee'])
            )
        out += '\r'
        return out

"""
