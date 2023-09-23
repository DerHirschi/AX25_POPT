import logging
import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from fnc.loc_fnc import coordinates_to_locator, locator_distance

# from fnc.str_fnc import conv_time_DE_str

logger = logging.getLogger(__name__)


class WXWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root_win = root_win
        self._ais_obj = PORT_HANDLER.get_aprs_ais()
        ###################################
        # Vars
        self._rev_ent = False
        # self.mh_win = tk.Tk()
        self.title("WX-Stations")
        self.style = self.root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1250x"
                      f"700+"
                      f"{self.root_win.main_win.winfo_x()}+"
                      f"{self.root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        self.lift()
        # ############################### Columns ############################

        ##########################################################################################
        # TREE
        columns = (
            'last_seen',
            'call',
            'port',
            'locator',
            'distance',
            'pressure',
            'humidity',
            'rain_1h',
            'rain_24h',
            'rain_since_midnight',
            'temperature',
            'wind_direction',
            'wind_gust',
            'wind_speed',
            'luminosity',
            'comment',
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._tree = ttk.Treeview(self, columns=columns, show='headings')
        self._tree.grid(row=0, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self._tree.heading('last_seen', text='Letzte Paket', command=lambda: self._sort_entry('last_seen'))
        self._tree.heading('call', text='CALL', command=lambda: self._sort_entry('call'))
        self._tree.heading('port', text='Port', command=lambda: self._sort_entry('port'))
        self._tree.heading('locator', text='LOC', command=lambda: self._sort_entry('locator'))
        self._tree.heading('distance', text='km', command=lambda: self._sort_entry('distance'))
        self._tree.heading('pressure', text='HPa', command=lambda: self._sort_entry('pressure'))
        self._tree.heading('humidity', text='Hum %', command=lambda: self._sort_entry('humidity'))
        self._tree.heading('rain_1h', text='Rain 1h', command=lambda: self._sort_entry('rain_1h'))
        self._tree.heading('rain_24h', text='Rain 24h', command=lambda: self._sort_entry('rain_24h'))
        self._tree.heading('rain_since_midnight', text='Rain Day', command=lambda: self._sort_entry('rain_since_midnight'))
        self._tree.heading('temperature', text='Temp °C', command=lambda: self._sort_entry('temperature'))
        self._tree.heading('wind_direction', text='Wind Dir', command=lambda: self._sort_entry('wind_direction'))
        self._tree.heading('wind_gust', text='Wind Gust', command=lambda: self._sort_entry('wind_gust'))
        self._tree.heading('wind_speed', text='Wind Speed', command=lambda: self._sort_entry('wind_speed'))
        self._tree.heading('luminosity', text='Lum', command=lambda: self._sort_entry('luminosity'))
        self._tree.heading('comment', text='Comment', command=lambda: self._sort_entry('comment'))
        self._tree.column("last_seen", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._tree.column("call", anchor=tk.CENTER, stretch=tk.YES, width=120)
        self._tree.column("port", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("locator", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("distance", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("pressure", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("humidity", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("rain_1h", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("rain_24h", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("rain_since_midnight", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("temperature", anchor=tk.CENTER, stretch=tk.YES, width=50)
        self._tree.column("wind_direction", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("wind_gust", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("wind_speed", anchor=tk.CENTER, stretch=tk.YES, width=80)
        self._tree.column("luminosity", anchor=tk.CENTER, stretch=tk.YES, width=50)
        self._tree.column("comment", anchor=tk.CENTER, stretch=tk.YES, width=150)
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)

        self._tree_data = []
        self._wx_data = []
        self._init_tree_data()
        # self.tree.bind('<<TreeviewSelect>>', self.entry_selected)

    def _init_tree_data(self):
        self._get_wx_data()
        self._format_tree_data()
        self._update_tree()

    def _format_tree_data(self):
        self._tree_data = []
        for k in self._wx_data:
            _loc = self._get_loc(self._wx_data[k][-1][1])
            _dist = self._get_loc_dist(_loc)
            self._tree_data.append((
                f'{self._wx_data[k][-1][0]}',
                f'{k}',
                f'{self._wx_data[k][-1][2]}',
                _loc,
                _dist,
                f'{self._wx_data[k][-1][1]["weather"].get("pressure", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("humidity", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("rain_1h", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("rain_24h", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("rain_since_midnight", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("temperature", "-"):.1f}',
                f'{self._wx_data[k][-1][1]["weather"].get("wind_direction", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("wind_gust", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("wind_speed", "-")}',
                f'{self._wx_data[k][-1][1]["weather"].get("luminosity", "-")}',
                f'{self._wx_data[k][-1][1].get("comment", "")}',
            ))

    def _sort_entry(self, col):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        if col in ['distance', 'pressure', 'humidity', 'rain_1h', 'rain_24h', 'rain_since_midnight',
                   'temperature', 'wind_gust', 'wind_speed', 'luminosity']:
            # _tmp = [(float(self._tree.set(k, col)), k) for k in self._tree.get_children()]
            _tmp = []
            _rest = []
            for k in self._tree.get_children():
                try:
                    _tmp.append((float(self._tree.set(k, col)), k))
                except ValueError:
                    _rest.append((self._tree.set(k, col), k))
            _tmp.sort(reverse=self._rev_ent)
            if self._rev_ent:
                _tmp = _tmp + _rest
            else:
                _tmp = _rest + _tmp
        else:
            _tmp = [(self._tree.set(k, col), k) for k in self._tree.get_children('')]
            _tmp.sort(reverse=self._rev_ent)
        self._rev_ent = not self._rev_ent
        for index, (val, k) in enumerate(_tmp):
            self._tree.move(k, '', int(index))

    def _get_wx_data(self):
        self._wx_data = self._ais_obj.get_wx_data()

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            self._tree.insert('', tk.END, values=ret_ent)

    @staticmethod
    def _get_loc(aprs_pack):
        _ret = coordinates_to_locator(
            aprs_pack.get('latitude', 0),
            aprs_pack.get('longitude', 0)
        )
        return _ret

    def _get_loc_dist(self, locator):
        if self._ais_obj.ais_loc:
            return locator_distance(locator, self._ais_obj.ais_loc)
        return -1

    def close(self):
        self.root_win.wx_window = None
        self.destroy()
