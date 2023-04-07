from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import tkinter as tk
from ax25.ax25dec_enc import AX25Frame
from datetime import datetime

import pickle

mh_data_file = 'data/mh_data.popt'
port_stat_data_file = 'data/port_stat.popt'


def get_time_str():
    now = datetime.now()
    return now.strftime('%d/%m/%y %H:%M:%S')


class MyHeard(object):
    def __init__(self):
        self.own_call = ''
        self.to_calls = ["""call_str"""]
        self.route = []
        self.all_routes = []
        self.port = ''
        self.port_id = 0    # Not used yet
        self.first_seen = get_time_str()
        self.last_seen = get_time_str()
        self.pac_n = 0                      # N Packets
        self.byte_n = 0                     # N Bytes
        self.h_byte_n = 0                   # N Header Bytes
        self.rej_n = 0                      # N REJ
        self.axip_add = '', 0               # IP, Port
        self.axip_fail = 0                  # Fail Counter


class PortStatHourStruc(object):
    def __init__(self):
        self.n_packets_hr = {}
        self.I_packets_hr = {}
        self.SABM_packets_hr = {}
        self.DM_packets_hr = {}
        self.DISC_packets_hr = {}
        self.REJ_packets_hr = {}
        self.RR_packets_hr = {}
        self.RNR_packets_hr = {}
        self.UI_packets_hr = {}
        self.ALL_data_hr = {}
        self.DATA_data_hr = {}

        for minute in range(60):
            self.n_packets_hr[minute] = 0
            self.I_packets_hr[minute] = 0
            self.SABM_packets_hr[minute] = 0
            self.DM_packets_hr[minute] = 0
            self.DISC_packets_hr[minute] = 0
            self.REJ_packets_hr[minute] = 0
            self.RR_packets_hr[minute] = 0
            self.RNR_packets_hr[minute] = 0
            self.UI_packets_hr[minute] = 0
            self.ALL_data_hr[minute] = 0
            self.DATA_data_hr[minute] = 0


class PortStatDB(object):
    def __init__(self):
        #                   DATE   HOUR
        # TODO Init fm File and Save
        self.stat_DB_days: {'str': {int: PortStatHourStruc}} = {}

        self.bandwidth = {}
        for m in range(60):
            for s in range(6):
                ts_str = '{}:{}'.format(str(m).zfill(2), s)
                self.bandwidth[ts_str] = 0

        self.now_min = datetime.now().strftime('%M:%S')[:-1]

    def init_day_dic(self):
        ret = {}
        for hour in range(24):
            ret[hour] = PortStatHourStruc()

        return ret

    def input(self, ax_frame: AX25Frame):
        # now = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        self.input_bw_calc(ax_frame=ax_frame)
        now = datetime.now()
        date_str = now.strftime('%d/%m/%y')
        hour = now.hour
        minute = now.minute
        if date_str not in list(self.stat_DB_days.keys()):
            self.stat_DB_days[date_str] = self.init_day_dic()
            """
            if hour in list(self.stat_DB_days[date_str].keys()):
                ent = self.stat_DB_days[date_str][hour]
            else:
                ent = PortStatHourStruc()
                self.stat_DB_days[date_str][hour] = ent
            """

        self.stat_DB_days[date_str][hour].n_packets_hr[minute] += 1
        """
        if ax_frame.ctl_byte.flag == 'I':
            self.stat_DB_days[date_str][hour].I_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'UI':
            self.stat_DB_days[date_str][hour].UI_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'REJ':
            self.stat_DB_days[date_str][hour].REJ_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'RR':
            self.stat_DB_days[date_str][hour].RR_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'RNR':
            self.stat_DB_days[date_str][hour].RNR_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'SABM':
            self.stat_DB_days[date_str][hour].SABM_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'DM':
            self.stat_DB_days[date_str][hour].DM_packets_hr[minute] += 1
        elif ax_frame.ctl_byte.flag == 'DISC':
            self.stat_DB_days[date_str][hour].DISC_packets_hr[minute] += 1
        """
        if ax_frame.ctl_byte.flag == 'I':
            self.stat_DB_days[date_str][hour].I_packets_hr[minute] += len(ax_frame.bytes)
        elif ax_frame.ctl_byte.flag == 'UI':
            self.stat_DB_days[date_str][hour].UI_packets_hr[minute] += len(ax_frame.bytes)
        elif ax_frame.ctl_byte.flag == 'REJ':
            self.stat_DB_days[date_str][hour].REJ_packets_hr[minute] += len(ax_frame.bytes)
        elif ax_frame.ctl_byte.flag == 'RR':
            self.stat_DB_days[date_str][hour].RR_packets_hr[minute] += len(ax_frame.bytes)
        elif ax_frame.ctl_byte.flag == 'RNR':
            self.stat_DB_days[date_str][hour].RNR_packets_hr[minute] += len(ax_frame.bytes)
        elif ax_frame.ctl_byte.flag == 'SABM':
            self.stat_DB_days[date_str][hour].SABM_packets_hr[minute] += len(ax_frame.bytes)
        elif ax_frame.ctl_byte.flag == 'DM':
            self.stat_DB_days[date_str][hour].DM_packets_hr[minute] += len(ax_frame.bytes)
        elif ax_frame.ctl_byte.flag == 'DISC':
            self.stat_DB_days[date_str][hour].DISC_packets_hr[minute] += len(ax_frame.bytes)
        self.stat_DB_days[date_str][hour].ALL_data_hr[minute] += len(ax_frame.bytes)
        self.stat_DB_days[date_str][hour].DATA_data_hr[minute] += ax_frame.data_len

    def input_bw_calc(self, ax_frame: AX25Frame = None):
        if ax_frame is not None:
            if self.now_min == datetime.now().strftime('%M:%S')[:-1]:
                self.bandwidth[self.now_min] += len(ax_frame.bytes)
            else:
                self.now_min = datetime.now().strftime('%M:%S')[:-1]
                self.bandwidth[self.now_min] = len(ax_frame.bytes)
        else:
            if self.now_min != datetime.now().strftime('%M:%S')[:-1]:
                self.now_min = datetime.now().strftime('%M:%S')[:-1]
                self.bandwidth[self.now_min] = 0

    def plot_test_graph(self, now_hour: int = -1, day=True):
        range_day = day
        now = datetime.now()
        date_str = now.strftime('%d/%m/%y')
        if now_hour == -1:
            now_hour = now.hour
        last_hour = now.hour - 1
        now_minute = list(range(0, now.minute))
        last_hr_minute = list(range(60 - (60 - now.minute), 60))
        # print('now_minute  {}'.format(now_minute))
        # print('last_hr_minute  {}'.format(last_hr_minute))
        _tmp_n_packets = []
        _tmp_I_packets = []
        _tmp_REJ_packets = []
        _tmp_RR_packets = []
        _tmp_RNR_packets = []
        _tmp_UI_packets = []
        _tmp_SABM_packets = []
        _tmp_ALL_data = []
        _tmp_DATA_data = []
        if date_str in list(self.stat_DB_days.keys()):

            if now_hour == 0 or range_day:
                last_hour = 23
                ind = list(self.stat_DB_days.keys()).index(date_str) - 1
                if ind >= 0:
                    las_day = list(self.stat_DB_days.keys())[ind]
                else:
                    las_day = ''
                    # las_day = date_str
            else:
                las_day = date_str
            if not range_day:
                now_minute.reverse()
                last_hr_minute.reverse()
                # print('<<>>>>  {}'.format(now_minute + last_hr_minute))
                for minute in now_minute:
                    _tmp_n_packets.append(self.stat_DB_days[date_str][now_hour].n_packets_hr[minute])
                    _tmp_I_packets.append(self.stat_DB_days[date_str][now_hour].I_packets_hr[minute])
                    _tmp_REJ_packets.append(self.stat_DB_days[date_str][now_hour].REJ_packets_hr[minute])
                    _tmp_RR_packets.append(self.stat_DB_days[date_str][now_hour].RR_packets_hr[minute])
                    _tmp_RNR_packets.append(self.stat_DB_days[date_str][now_hour].RNR_packets_hr[minute])
                    _tmp_UI_packets.append(self.stat_DB_days[date_str][now_hour].UI_packets_hr[minute])
                    _tmp_SABM_packets.append(self.stat_DB_days[date_str][now_hour].SABM_packets_hr[minute])
                    _tmp_ALL_data.append(self.stat_DB_days[date_str][now_hour].ALL_data_hr[minute])
                    _tmp_DATA_data.append(self.stat_DB_days[date_str][now_hour].DATA_data_hr[minute])

                for minu in last_hr_minute:
                    if las_day:

                        _tmp_n_packets.append(self.stat_DB_days[las_day][last_hour].n_packets_hr[minu])
                        _tmp_I_packets.append(self.stat_DB_days[las_day][last_hour].I_packets_hr[minu])
                        _tmp_REJ_packets.append(self.stat_DB_days[las_day][last_hour].REJ_packets_hr[minu])
                        _tmp_RR_packets.append(self.stat_DB_days[las_day][last_hour].RR_packets_hr[minu])
                        _tmp_RNR_packets.append(self.stat_DB_days[las_day][last_hour].RNR_packets_hr[minu])
                        _tmp_UI_packets.append(self.stat_DB_days[las_day][last_hour].UI_packets_hr[minu])
                        _tmp_SABM_packets.append(self.stat_DB_days[las_day][last_hour].SABM_packets_hr[minu])
                        _tmp_ALL_data.append(self.stat_DB_days[las_day][last_hour].ALL_data_hr[minu])
                        _tmp_DATA_data.append(self.stat_DB_days[las_day][last_hour].DATA_data_hr[minu])
                    else:
                        _tmp_n_packets.append(0)
                        _tmp_I_packets.append(0)
                        _tmp_REJ_packets.append(0)
                        _tmp_RR_packets.append(0)
                        _tmp_RNR_packets.append(0)
                        _tmp_UI_packets.append(0)
                        _tmp_SABM_packets.append(0)
                        _tmp_ALL_data.append(0)
                        _tmp_DATA_data.append(0)
            else:
                day_hours = list(range(0, now_hour + 1))
                last_hours = list(range(now_hour + 1, 24))
                min_list = list(range(60))
                day_hours.reverse()
                last_hours.reverse()
                min_list.reverse()
                # print('<<>>>>  {}  {}'.format(last_hours , day_hours))
                dt_now = datetime.now()
                for h in day_hours:
                    if h in self.stat_DB_days[date_str].keys():
                        for minu in min_list:
                            if (h == dt_now.hour and minu <= dt_now.minute) or h != dt_now.hour:
                                _tmp_n_packets.append(self.stat_DB_days[date_str][h].n_packets_hr[minu])
                                _tmp_I_packets.append(self.stat_DB_days[date_str][h].I_packets_hr[minu])
                                _tmp_REJ_packets.append(self.stat_DB_days[date_str][h].REJ_packets_hr[minu])
                                _tmp_RR_packets.append(self.stat_DB_days[date_str][h].RR_packets_hr[minu])
                                _tmp_RNR_packets.append(self.stat_DB_days[date_str][h].RNR_packets_hr[minu])
                                _tmp_UI_packets.append(self.stat_DB_days[date_str][h].UI_packets_hr[minu])
                                _tmp_SABM_packets.append(self.stat_DB_days[date_str][h].SABM_packets_hr[minu])
                                _tmp_ALL_data.append(self.stat_DB_days[date_str][h].ALL_data_hr[minu])
                                _tmp_DATA_data.append(self.stat_DB_days[date_str][h].DATA_data_hr[minu])
                            # if h == dt_now.hour and minu < dt_now.minute:
                            #     break
                for h in last_hours:
                    if las_day:
                        if h in self.stat_DB_days[las_day].keys():
                            for minu in min_list:
                                _tmp_n_packets.append(self.stat_DB_days[las_day][h].n_packets_hr[minu])
                                _tmp_I_packets.append(self.stat_DB_days[las_day][h].I_packets_hr[minu])
                                _tmp_REJ_packets.append(self.stat_DB_days[las_day][h].REJ_packets_hr[minu])
                                _tmp_RR_packets.append(self.stat_DB_days[las_day][h].RR_packets_hr[minu])
                                _tmp_RNR_packets.append(self.stat_DB_days[las_day][h].RNR_packets_hr[minu])
                                _tmp_UI_packets.append(self.stat_DB_days[las_day][h].UI_packets_hr[minu])
                                _tmp_SABM_packets.append(self.stat_DB_days[las_day][h].SABM_packets_hr[minu])
                                _tmp_ALL_data.append(self.stat_DB_days[las_day][h].ALL_data_hr[minu])
                                _tmp_DATA_data.append(self.stat_DB_days[las_day][h].DATA_data_hr[minu])
                        else:
                            for minu in min_list:
                                _tmp_n_packets.append(0)
                                _tmp_I_packets.append(0)
                                _tmp_REJ_packets.append(0)
                                _tmp_RR_packets.append(0)
                                _tmp_RNR_packets.append(0)
                                _tmp_UI_packets.append(0)
                                _tmp_SABM_packets.append(0)
                                _tmp_ALL_data.append(0)
                                _tmp_DATA_data.append(0)
                    else:
                        for minu in min_list:
                            _tmp_n_packets.append(0)
                            _tmp_I_packets.append(0)
                            _tmp_REJ_packets.append(0)
                            _tmp_RR_packets.append(0)
                            _tmp_RNR_packets.append(0)
                            _tmp_UI_packets.append(0)
                            _tmp_SABM_packets.append(0)
                            _tmp_ALL_data.append(0)
                            _tmp_DATA_data.append(0)

        ke = list(range(len(_tmp_n_packets)))
        # len(ke)
        if _tmp_n_packets:
            x_scale = []
            if range_day:
                for i in list(range(len(_tmp_n_packets))):
                    x_scale.append((i / 60))
            else:
                x_scale = ke
            # print(x_scale)
            root = tk.Tk()
            root.wm_title("Port Statistik")
            root.geometry("800x600")
            # root.protocol("WM_DELETE_WINDOW", root.destroy())
            plot1 = tk.Frame(root)
            plot2 = tk.Frame(root)
            """
            _tmp_n_packets.reverse()
            _tmp_I_packets.reverse()
            _tmp_REJ_packets.reverse()
            _tmp_RR_packets.reverse()
            _tmp_UI_packets.reverse()
            _tmp_SABM_packets.reverse()
            _tmp_ALL_data.reverse()
            _tmp_DATA_data.reverse()
            """
            """
            print('------------------------')
            print(_tmp_n_packets)
            print(_tmp_I_packets)
            print(_tmp_REJ_packets)
            print(_tmp_RR_packets)
            print(_tmp_UI_packets)
            print(_tmp_SABM_packets)
            print(_tmp_ALL_data)
            print(_tmp_DATA_data)
            """

            fig = plt.figure(figsize=(5, 4), dpi=100)
            plt.style.use('dark_background')
            fig.add_subplot(111).plot(
                # x_scale, _tmp_n_packets,
                x_scale, _tmp_ALL_data,
                x_scale, _tmp_I_packets,
                x_scale, _tmp_UI_packets,
                x_scale, _tmp_REJ_packets,
                x_scale, _tmp_RR_packets,
                x_scale, _tmp_RNR_packets,
                x_scale, _tmp_SABM_packets,
            )

            # fig.axis([0, 59, 0, 50])
            """
            if not range_day:
                plt.axis([0, 59, 0, 100])
            else:
            """
            if range_day:
                plt.axis([0, 24, 0, max(_tmp_ALL_data)])
            else:
                plt.axis([0, 59, 0, max(_tmp_ALL_data)])
            # plt.axis([0, 59, 0, 50])
            plt.legend(['Bytes', 'I-Frames', 'UI-Frames', 'REJ-Frames', 'RR-Frames', 'RNR-Frames', 'SABM-Frames', ])
            #ax.suptitle('Port Statistik')

            canvas = FigureCanvasTkAgg(fig, master=plot1)  # A tk.DrawingArea.
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, plot1)
            toolbar.update()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


            fig = plt.figure(figsize=(5, 4), dpi=100)
            plt.style.use('dark_background')
            fig.add_subplot(111).plot(
                x_scale, _tmp_ALL_data,
                x_scale, _tmp_DATA_data, 'r--'

            )
            # y_max = max(_tmp_ALL_data)
            # fig.axis([0, 59, 0, 50])
            """
            if not range_day:
                plt.axis([0, 59, 0, 100])
            else:
            """
            if range_day:
                plt.axis([0, 24, 0, max(_tmp_ALL_data)])
            else:
                plt.axis([0, 59, 0, max(_tmp_ALL_data)])
            # plt.axis([0, 59, 0, 50])
            plt.legend(['Daten gesamt', 'Nutzdaten'])
            # ax.suptitle('Port Statistik')
            canvas = FigureCanvasTkAgg(fig, master=plot2)  # A tk.DrawingArea.
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2Tk(canvas, plot2)
            toolbar.update()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)



            plot1.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
            plot2.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

            frame = tk.Frame(root)
            prt_sel_var = tk.IntVar()
            prt_sel_var.set(0)
            lable = tk.Label(frame, text='Port: ')
            prt_sel = tk.Spinbox(frame,
                                         from_=0,
                                         to=7,
                                        increment=1,
                                        width=2,
                                        textvariable=prt_sel_var,
                                        state='disabled',
                                        # command=self.set_max_frame,
                                        )
            prt_sel.configure(state='disabled')
            frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=0)
            lable.grid(row=0, column=0)
            prt_sel.grid(row=0, column=1)
            # root.protocol("WM_DELETE_WINDOW", root.destroy())

    def get_bandwidth(self, baud=1200):
        self.input_bw_calc()
        ret = []
        now = datetime.now().strftime('%M:%S')[:-1]
        minutes = list(self.bandwidth.keys())
        minutes.reverse()
        ind = minutes.index(now)
        new_key_list = minutes[ind:] + minutes[:ind]
        for k in new_key_list:
            byt = int(self.bandwidth[k])
            f = (((byt * 8) / 10) * 100) / baud
            ret.append(f)
        #print(ret)
        #print(len(ret))
        return ret


class MH(object):
    def __init__(self):
        print("MH Init")
        self.calls: {str: MyHeard} = {}
        self.port_statistik_DB: {int: PortStatDB} = {}
        try:
            with open(mh_data_file, 'rb') as inp:
                self.calls = pickle.load(inp)
        except FileNotFoundError:
            pass
        except EOFError:
            pass
        port_stat_DB = []
        try:
            with open(port_stat_data_file, 'rb') as inp:
                port_stat_DB = pickle.load(inp)
        except FileNotFoundError:
            pass
        except EOFError:
            pass

        port_id = 0
        for el in port_stat_DB:
            self.port_statistik_DB[port_id] = PortStatDB()
            self.port_statistik_DB[port_id].stat_DB_days = el
            port_id += 1

        for call in list(self.calls.keys()):
            for att in dir(MyHeard):
                if not hasattr(self.calls[call], att):
                    setattr(self.calls[call], att, getattr(MyHeard, att))

        if not self.port_statistik_DB:  # Übergangsweise
            self.port_statistik_DB[0] = PortStatDB()
        self.new_call_alarm = False
        """
        self.connections = {
            # conn_id: bla TODO Reverse id 
        }
        """

    def __del__(self):
        pass

    def bw_mon_inp(self, ax25_frame: AX25Frame, port_id):
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = PortStatDB()

        self.port_statistik_DB[port_id].input(ax_frame=ax25_frame)

    def mh_inp(self, ax25_frame: AX25Frame, port_name, port_id):
        ########################
        # Port Stat
        if port_id not in self.port_statistik_DB.keys():
            self.port_statistik_DB[port_id] = PortStatDB()
        self.port_statistik_DB[port_id].input(ax_frame=ax25_frame)
        ########################
        # MH Entry
        call_str = ax25_frame.from_call.call_str
        if call_str not in self.calls.keys():
            self.new_call_alarm = True
            ent = MyHeard()
            ent.first_seen = get_time_str()
        else:
            ent = self.calls[call_str]
        ent.last_seen = get_time_str()
        ent.own_call = call_str
        ent.pac_n += 1
        ent.port = port_name
        ent.port_id = port_id
        ent.byte_n += ax25_frame.data_len
        ent.h_byte_n += len(ax25_frame.bytes) - ax25_frame.data_len
        if ax25_frame.ctl_byte.flag == 'REJ':
            ent.rej_n += 1
        # TO Calls
        to_c_str = ax25_frame.to_call.call_str
        if to_c_str not in ent.to_calls:
            ent.to_calls.append(to_c_str)
        # Routes
        ent.route = []      # Last Route
        if ax25_frame.via_calls:
            for call in ax25_frame.via_calls:
                if call.c_bit:
                    ent.route.append(call.call_str)

        if ent.route not in ent.all_routes:
            ent.all_routes.append(list(ent.route))
        # Update AXIP Address
        if ax25_frame.axip_add[0]:
            ent.axip_add = ax25_frame.axip_add

        self.calls[call_str] = ent

    def mh_get_data_fm_call(self, call_str):
        if call_str in self.calls.keys():
            return self.calls[call_str]
        return False

    def output_sort_entr(self, n: int = 0):
        """ For MH in Side Panel """
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
            if c > n and n:
                break
        return temp_ret

    def output_sort_mh_entr(self, flag_str: str, reverse: bool):
        temp = {}
        self.calls: {str: MyHeard}
        for k in self.calls.keys():
            flag: MyHeard = self.calls[k]
            key: str = {
                'last': flag.last_seen,
                'first': flag.first_seen,
                'port': str(flag.port_id),
                'call': flag.own_call,
                'pack': str(flag.pac_n),
                'rej': str(flag.rej_n),
                'route': str(max(flag.all_routes)),
                'axip': str(flag.axip_add),
                'axipfail': str(flag.axip_fail),
            }[flag_str]
            while key in temp.keys():
                key += '1'
            temp[key] = self.calls[k]

        temp_k = list(temp.keys())
        temp_k.sort()
        if not reverse:
            temp_k.reverse()
        temp_ret = {}
        for k in temp_k:
            temp_ret[k] = temp[k]
        return temp_ret

    def mh_get_last_ip(self, call_str: str, param_fail=20):
        if call_str:
            if call_str in self.calls.keys():
                if self.calls[call_str].axip_fail < param_fail:
                    return self.calls[call_str].axip_add
        return '', 0

    def mh_get_ip_fm_all(self, param_fail=20):
        ret: [(str, (str, int))] = []
        for stat_call in self.calls.keys():
            station: MyHeard = self.calls[stat_call]
            if station.axip_add and station.axip_fail < param_fail:
                ent = stat_call, station.axip_add
                ret.append(ent)
        return ret

    def mh_ip_failed(self, axip: str):
        for k in self.calls.keys:
            if self.calls[k].axip_add == axip:
                self.calls[k].axip_fail += 1

    def mh_set_ip(self, call: str, axip: (str, int)):
        self.calls[call].axip_add = axip

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
                # print(self.calls.keys())
                pickle.dump(self.calls, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(mh_data_file, 'xb') as outp:
                pickle.dump(self.calls, outp, pickle.HIGHEST_PROTOCOL)

        port_stat_DB = []
        for port_id in self.port_statistik_DB.keys():
            port_stat_DB.append(self.port_statistik_DB[port_id].stat_DB_days)
        try:
            with open(port_stat_data_file, 'wb') as outp:
                # print(self.calls.keys())
                pickle.dump(port_stat_DB, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(port_stat_data_file, 'xb') as outp:
                pickle.dump(port_stat_DB, outp, pickle.HIGHEST_PROTOCOL)
        """    
        try:
            with open(port_stat_data_file, 'wb') as outp:
                # print(self.calls.keys())
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError:
            with open(port_stat_data_file, 'xb') as outp:
                pickle.dump(self.port_statistik_DB, outp, pickle.HIGHEST_PROTOCOL)
        """


if __name__ == '__main__':
    stat = PortStatDB()
    stat.plot_test_graph()
