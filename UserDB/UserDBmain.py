import sys
import datetime
import os
import pickle
import logging
from fnc.ax25_fnc import call_tuple_fm_call_str, validate_call
from fnc.cfg_fnc import set_obj_att, cleanup_obj_dict
from fnc.str_fnc import conv_time_for_sorting

# axip_clientList = 'data/axip_userList.popt'
client_db = 'data/UserDB.popt'


logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, call):
        self.call_str = call
        tmp_call = call_tuple_fm_call_str(call)
        self.Call = tmp_call[0]
        self.SSID = tmp_call[1]
        self.Alias = ''
        self.TYP = ''

        self.Name = ''
        self.Land = ''
        self.ZIP = ''
        self.QTH = ''
        self.LOC = ''
        self.Lat = 0
        self.Lon = 0
        self.Distance = 0
        self.Language = -1
        self.PRmail = ''
        self.Email = ''
        self.HTTP = ''
        self.Info = ''

        self.NODE = []
        self.BBS = []
        self.Other = []
        self.Sysop_Call = ''

        self.via_NODE_HF = ''
        self.via_NODE_AXIP = ''
        self.AXIP = ()
        self.QRG1 = ''  # 27.235FM-1200-AD/AI/FX
        self.QRG2 = ''
        self.QRG3 = ''
        self.QRG4 = ''
        self.QRG5 = ''
        self.Software = ''
        self.Encoding = 'CP437'    # 'UTF-8'

        self.last_edit = datetime.datetime.now()
        self.last_seen = datetime.datetime.now()
        self.Connects = 0

        self.pac_len = 0
        self.max_pac = 0
        self.CText = ''
        self.routes = []
        self.software_str = ''
        self.sys_pw = ''
        self.sys_pw_parm = [5, 80, 'SYS']


class UserDB:
    def __init__(self):
        print("User-DB INIT")
        logger.info("User-DB INIT")
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
        try:
            with open(client_db, 'rb') as inp:
                db_load = pickle.load(inp)
            """
            for ke in self.db.keys():
                print(ke)
            """
        except FileNotFoundError:
            if 'linux' in sys.platform:
                os.system('touch {}'.format(client_db))
            default_client = Client('ALL')
            # default_client.is_new = False
            default_client.name = 'Beacon'
            default_client.typ = 'BEACON'
            self.db = {
                'ALL': default_client
            }
        except EOFError:
            pass
        except ImportError:
            logger.error(f"User DB: Falsche Version der DB Datei. Bitte {client_db} löschen und PoPT neu starten!")
            raise

        for k in db_load.keys():
            self.db[k] = set_obj_att(new_obj=Client(db_load[k].call_str), input_obj=db_load[k])

    def get_entry(self, call_str, add_new=True):
        call_str = validate_call(call_str)
        if call_str:
            call_tup = call_tuple_fm_call_str(call_str)
            if call_str not in self.db.keys():
                if call_tup[0] not in self.db.keys():
                    print('# User DB: New User added > ' + call_str)
                    logger.info('User DB: New User added > ' + call_str)
                    if add_new:
                        self.db[call_str] = Client(call_str)
                    else:
                        return False
                else:
                    self.entry_var_upgrade(call_tup[0])
                    return self.db[call_tup[0]]
            self.entry_var_upgrade(call_str)
            return self.db[call_str]
        return False

    def new_entry(self, call_str):
        call_str = validate_call(call_str)
        if call_str:
            call_tup = call_tuple_fm_call_str(call_str)
            if call_str not in self.db.keys():
                if call_tup[0] not in self.db.keys():
                    print('# User DB: New User added > ' + call_str)
                    logger.info('User DB: New User added > ' + call_str)
                    self.db[call_str] = Client(call_str)
                    return self.db[call_str]
        return False

    def get_distance(self, call_str):
        ret = self.db.get(call_str, False)
        if ret:
            return ret.Distance
        return 0

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

    def entry_var_upgrade(self, ent_key):
        if ent_key in self.db.keys():
            compare = Client('ALL')
            for new_att in dir(compare):
                # print(new_att)
                if not hasattr(self.db[ent_key], new_att):
                    setattr(self.db[ent_key], new_att, getattr(compare, new_att))
                if not hasattr(self.db[ent_key], 'Distance'):
                    self.db[ent_key] = 0
                # print(getattr(self.db[ent_key], new_att))

    def update_var_fm_dbentry(self, fm_key: str, to_key: str):
        if fm_key not in self.db.keys():
            return False
        if to_key not in self.db.keys():
            return False
        # new_obj = Client(to_key)
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
                else:
                    setattr(self.db[to_key], att, getattr(self.db[to_key], att))
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
                'dist': str(flag.Distance),
                'land': str(flag.Land),
                'last_seen': conv_time_for_sorting(flag.last_seen),
            }[flag_str]
            while key in temp.keys():
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

    def save_data(self):
        print('Save Client DB')
        logger.info('Save Client DB')
        tmp = cleanup_obj_dict(self.db)

        try:
            with open(client_db, 'wb') as outp:
                pickle.dump(tmp, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError as e:
            # print("ERROR SAVE ClientDB: " + str(e))
            logger.error("ERROR SAVE ClientDB: " + str(e))


USER_DB = UserDB()

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
