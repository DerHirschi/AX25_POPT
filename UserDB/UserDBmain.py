import sys
import datetime
import os
import pickle
from cfg.logger_config import logger

from fnc.ax25_fnc import call_tuple_fm_call_str, validate_ax25Call, validate_aprs_call
from cfg.cfg_fnc import set_obj_att, cleanup_obj_dict, set_obj_att_fm_dict
from fnc.loc_fnc import locator_to_coordinates, locator_distance
from fnc.str_fnc import conv_time_for_sorting
from cfg.constant import CFG_user_db


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
    Language = -1
    PRmail = ''
    Email = ''
    HTTP = ''
    Info = ''

    NODE = []
    BBS = []
    Other = []
    Sysop_Call = ''

    via_NODE_HF = ''
    via_NODE_AXIP = ''
    AXIP = '', 0
    QRG1 = ''  # 27.235FM-1200-AD/AI/FX
    QRG2 = ''
    QRG3 = ''
    QRG4 = ''
    QRG5 = ''
    Software = ''
    Encoding = 'CP437'    # 'UTF-8'

    last_edit = datetime.datetime.now()
    last_seen = datetime.datetime.now()
    Connects = 0

    pac_len = 0
    max_pac = 0
    CText = ''
    routes = []
    software_str = ''
    sys_pw = ''
    sys_pw_parm = [5, 80, 'SYS']


class UserDB:
    def __init__(self):
        # print("User-DB Init")
        logger.info("User-DB: Init")
        self._port_handler = None
        self.not_public_vars = [
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
        ]
        self.db = {}
        db_load = {}
        logger.info(f"User-DB: loading UserDB fm {CFG_user_db} ")
        try:
            with open(CFG_user_db, 'rb') as inp:
                db_load = pickle.load(inp)
            """
            for ke in self.db.keys():
                print(ke)
            """
        except FileNotFoundError:
            logger.warning(f"User-DB: {CFG_user_db} not found. Creating new User-DB !")
            if 'linux' in sys.platform:
                os.system('touch {}'.format(CFG_user_db))
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
        except EOFError:
            logger.warning(f"User-DB: Can't open {CFG_user_db} !!!")
        except ImportError:
            logger.error(f"User-DB: Falsche Version der DB Datei. Bitte {CFG_user_db} löschen und PoPT neu starten!")
            raise

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

        logger.info("User-DB: Init complete")

    def set_port_handler(self, port_handler):
        self._port_handler = port_handler
        logger.info("User-DB: PH set")

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
        if validate_ax25Call(call_str):
            if call_str not in self.db.keys():
                call_tup = call_tuple_fm_call_str(call_str)
                # if call_tup[0] not in self.db.keys():
                # print('# User DB: New User added > ' + call_str)
                logger.info('User DB: New User added > ' + call_str)
                self.db[call_str] = Client()
                self.db[call_str].call_str = str(call_str)
                self.db[call_str].Call = str(call_tup[0])
                self.db[call_str].SSID = int(call_tup[1])
                return self.db[call_str]
        return False

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

    def set_pr_mail_add_for_BBS(self, address: str, ):
        call_str = address.split('.')[0]
        if not call_str:
            return
        ent = self.get_entry(call_str, True)
        if not ent:
            return
        if not ent.TYP:
            ent.TYP = 'BBS'
        ent.PRmail = address

    def set_distance(self, entry_call: str):
        if self._port_handler is None:
            return False
        own_loc = self._port_handler.get_gui().own_loc
        if not own_loc:
            return False
        ent = self.get_entry(entry_call, False)
        if not ent:
            return False
        if not ent.LOC:
            ent.Distance = -1
            return False
        ent.Distance = locator_distance(own_loc, ent.LOC)

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
                'last_seen': conv_time_for_sorting(flag.last_seen),
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

    def get_distance(self, call_str):
        ent = self.get_entry(call_str, add_new=False)
        if not ent:
            return 0
        return ent.Distance

    def get_locator(self, call_str):
        ent = self.get_entry(call_str, add_new=False)
        if not ent:
            return ''
        return ent.LOC

    def get_location(self, call_str):
        ent = self.get_entry(call_str, add_new=False)
        if not ent:
            return ()
        if ent.Lon or ent.Lon:
            return ent.Lat, ent.Lon, ent.LOC
        if ent.LOC:
            lat, lon = locator_to_coordinates(ent.LOC)
            return lat, lon, ent.LOC
        return ()

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

    def get_all_PRmail(self):
        ret = []
        for k in list(self.db.keys()):
            if self.db[k].TYP == 'SYSOP':
                if self.db[k].PRmail:
                    ret.append(self.db[k].PRmail)
        return ret

    def save_data(self):
        # print('Save Client DB')
        logger.info('User-DB: Save User-DB')
        tmp = cleanup_obj_dict(self.db)
        try:
            with open(CFG_user_db, 'wb') as outp:
                pickle.dump(tmp, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError as e:
            # print("ERROR SAVE ClientDB: " + str(e))
            logger.error("User-DB: Save User-DB > " + str(e))


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
