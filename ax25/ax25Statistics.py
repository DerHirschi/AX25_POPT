from ax25.ax25dec_enc import get_call_str, AX25Frame
from datetime import datetime
import time
import os
import pickle

mh_data_file = 'data/mh_data.pkl'


def get_time_str():
    now = datetime.now()
    return now.strftime('%d/%m/%y %H:%M:%S')


class MyHeard(object):
    def __init__(self):
        self.own_call = ''
        self.to_calls = ["""call_str"""]
        # TODO Routen/VIA
        self.port = ''
        self.first_seen = get_time_str()
        self.last_seen = get_time_str()
        self.pac_n = 1                      # N Packets
        self.byte_n = 0                     # N Bytes
        self.h_byte_n = 0                   # N Header Bytes
        self.rej_n = 0                      # N REJ
        self.axip_add = '', 0               # IP, Port


class MH(object):
    def __init__(self):
        self.calls: {str: MyHeard} = {}
        try:
            with open(mh_data_file, 'rb') as inp:
                self.calls = pickle.load(inp)
        except FileNotFoundError:
            os.system('touch {}'.format(mh_data_file))
        except EOFError:
            pass

        """
        self.connections = {
            # conn_id: bla TODO Reverse id 
        }
        """

    def __del__(self):
        pass

    def mh_inp(self, ax25_frame: AX25Frame, port_id, axip_add=None):
        ########################
        # Call Stat
        call_str = ax25_frame.from_call.call_str

        if call_str not in self.calls.keys():
            ent = MyHeard()
            ent.own_call = call_str
            ent.to_calls = [ax25_frame.to_call.call_str]
            ent.port = port_id
            ent.byte_n = ax25_frame.data_len
            ent.h_byte_n = len(ax25_frame.hexstr) - ax25_frame.data_len
            ent.axip_add = axip_add
            if ax25_frame.ctl_byte.flag == 'REJ':
                ent.rej_n = 1
            self.calls[call_str] = ent
        else:
            ent: MyHeard
            ent = self.calls[call_str]
            ent.pac_n += 1
            ent.port = port_id
            ent.byte_n += ax25_frame.data_len
            ent.last_seen = get_time_str()
            to_c_str = ax25_frame.to_call.call_str
            if to_c_str not in ent.to_calls:
                ent.to_calls.append(to_c_str)
            ent.h_byte_n += len(ax25_frame.hexstr) - ax25_frame.data_len
            if ax25_frame.ctl_byte.flag == 'REJ':
                ent.rej_n += 1
            self.calls[call_str] = ent

    def mh_get_data_fm_call(self, call_str):
        return self.calls[call_str]

    def output_sort_entr(self, n: int):
        temp = {}
        self.calls: {str: MyHeard}
        for k in self.calls.keys():
            flag: MyHeard = self.calls[k]
            temp[flag.last_seen] = self.calls[k]

        temp_k = list(temp.keys())
        temp_k.sort()
        temp_k.reverse()
        temp_ret = []
        c = 0
        for k in temp_k:

            temp_ret.append(temp[k])
            c += 1
            if c > n:
                break

        return temp_ret

    """
    def mh_get_last_port_obj(self, call_str):
        p_id = self.mh_get_data_fm_call(call_str)
        p_id = p_id['port']
        return config.ax_ports[p_id]
    """

    def mh_get_last_ip(self, call_str):
        out = self.mh_get_data_fm_call(call_str)
        out = out['axip_add']
        return out

    def mh_out_cli(self):
        out = ''
        out += '\r                       < MH - List >\r\r'
        c = 0
        tp = 0
        tb = 0
        rj = 0
        for call in list(self.calls.keys()):

            out += 'P:{:2}>{:5} {:9} {:3}'.format(self.calls[call].port,
                                                self.calls[call].last_seen,
                                                call,
                                                '')

            tp += self.calls[call].pac_n
            tb += self.calls[call].byte_n
            rj += self.calls[call].rej_n
            c += 1
            if c == 2:  # Breite
                c = 0
                out += '\r'
        out += '\r'
        out += '\rTotal Packets Rec.: ' + str(tp)
        out += '\rTotal REJ-Packets Rec.: ' + str(rj)
        out += '\rTotal Bytes Rec.: ' + str(tb)
        out += '\r'

        return out

    def save_mh_data(self):
        try:
            with open(mh_data_file, 'wb') as outp:
                pickle.dump(self.calls, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            os.system('touch {}'.format(mh_data_file))
            with open(mh_data_file, 'wb') as outp:
                pickle.dump(self.calls, outp, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    mh_data_file = '../data/mh_data.pkl'
    mh = MH()
    print(mh.mh_out_cli())
