import sys
import datetime
import os
import pickle
import logging
from fnc.ax25_fnc import call_tuple_fm_call_str, validate_call

# axip_clientList = 'data/axip_userList.popt'
client_db = 'data/UserDB.popt'

"""
def get_ssid(inp):
    if inp.find('-') != -1:
        return inp[:inp.find('-')].upper(), int(inp[inp.find('-') + 1:].upper())
    else:
        return inp, 0
"""
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
        self.Encoding = 'UTF-8'

        self.last_edit = datetime.datetime.now()
        self.Connects = 0

        self.pac_len = 0
        self.max_pac = 0
        self.CText = ''
        self.routes = []
        self.software_str = ''


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
        ]
        self.db = {}
        try:
            with open(client_db, 'rb') as inp:
                self.db = pickle.load(inp)
            for ke in self.db.keys():
                print(ke)
        except FileNotFoundError:
            if 'linux' in sys.platform:
                os.system('touch {}'.format(client_db))
            default_client = Client('ALL')
            default_client.is_new = False
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

    def entry_var_upgrade(self, ent_key):
        if ent_key in self.db.keys():
            compare = Client('ALL')
            for new_att in dir(compare):
                # print(new_att)
                if not hasattr(self.db[ent_key], new_att):
                    setattr(self.db[ent_key], new_att, getattr(compare, new_att))
                # print(getattr(self.db[ent_key], new_att))

    def save_data(self):
        print('Save Client DB')
        logger.info('Save Client DB')
        try:
            with open(client_db, 'wb') as outp:
                pickle.dump(self.db, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError as e:
            # print("ERROR SAVE ClientDB: " + str(e))
            logger.error("ERROR SAVE ClientDB: " + str(e))

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