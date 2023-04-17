import sys
import datetime
import os
import pickle
from fnc.ax25_fnc import call_tuple_fm_call_str

# axip_clientList = 'data/axip_userList.popt'
client_db = 'data/UserDB.popt'

"""
def get_ssid(inp):
    if inp.find('-') != -1:
        return inp[:inp.find('-')].upper(), int(inp[inp.find('-') + 1:].upper())
    else:
        return inp, 0
"""


class Client(object):
    def __init__(self, call):
        self.call_str = call
        tmp_call = call_tuple_fm_call_str(call)
        self.call = tmp_call[0]
        self.ssid = tmp_call[1]
        self.typ = ''

        self.name = ''
        self.land = ''
        self.zip = ''
        self.qth = ''
        self.loc = ''
        self.language = ''
        self.prmail = ''
        self.email = ''
        self.http = ''
        self.info = ''

        self.node = []
        self.bbs = []
        self.other = []

        self.via_NODE_HF = ''
        self.via_NODE_AXIP = ''
        self.axip_addr = ()
        self.qrg1 = ''  # 27.235FM-1200-AD/AI/FX
        self.qrg2 = ''
        self.qrg3 = ''
        self.qrg4 = ''
        self.qrg5 = ''
        self.software = ''

        self.last_edit_by = ''
        self.last_edit = datetime.datetime.now()
        self.is_new = True

        self.pac_len = 0
        self.max_pac = 0
        self.info_text = ''
        self.routes = []


class UserDB:
    def __init__(self):
        print("User-DB INIT")
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
            default_client.typ = 'Beacon'
            self.db = {
                'ALL': default_client
            }
        except EOFError:
            pass

    def get_entry(self, call):
        if call not in self.db.keys():
            print('# Client DB: New User added > ' + call)
            self.db[call] = Client(call)
        return self.db[call]

    def save_data(self):
        print('Save Client DB')
        try:
            with open(client_db, 'wb') as outp:
                pickle.dump(self.db, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError as e:
            print("ERROR SAVE ClientDB: " + str(e))

"""
class AXIPClientDB(object):
    def __init__(self, port):
        self.port = port
        self.clients = {
            # 'call_str': {
            #       'addr': (),
            #       'lastsee': 0.0,
            # }
        }
        try:
            with open(axip_clientList, 'rb') as inp:
                self.clients = pickle.load(inp)
        except FileNotFoundError:
            os.system('touch {}'.format(axip_clientList))
        except EOFError:
            pass

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

    def save_data(self):
        try:
            with open(axip_clientList, 'wb') as outp:
                pickle.dump(self.clients, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError as e:
            print("ERROR SAVE AXIPClients: " + str(e))

"""