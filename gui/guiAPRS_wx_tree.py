import logging
import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from gui.guiAPRS_wx_plot import WXPlotWindow

logger = logging.getLogger(__name__)


class WXWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        self._ais_obj = PORT_HANDLER.get_aprs_ais()
        self._ais_obj.wx_tree_gui = self
        ###################################
        # Vars
        self._rev_ent = False
        self._last_sort_col = None
        # self.mh_win = tk.Tk()
        self.title("WX-Stations")
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1250x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
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

        self._tree_data = []
        self._wx_data = {}
        self._init_tree_data()
        self._tree.bind('<<TreeviewSelect>>', self._entry_selected)

    def _init_tree_data(self):
        self._get_wx_data()
        self._format_tree_data()
        self._update_tree()

    def update_tree_data(self):
        self._get_wx_data()
        self._format_tree_data()
        self._update_tree()
        if self._last_sort_col is not None:
            self._rev_ent = not self._rev_ent
            self._sort_entry(self._last_sort_col)

    def _format_tree_data(self):
        self._tree_data = []
        for k in self._wx_data:
            self._tree_data.append((
                f'{self._wx_data[k][-1]["rx_time"].strftime("%d/%m/%y %H:%M:%S")}',
                f'{k}',
                f'{self._wx_data[k][-1].get("port_id", "-")}',
                f'{self._wx_data[k][-1].get("locator", "-")}',
                f'{self._wx_data[k][-1].get("distance", -1)}',
                f'{self._wx_data[k][-1]["weather"].get("pressure", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("humidity", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("rain_1h", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("rain_24h", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("rain_since_midnight", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("temperature", -99):.1f}',
                f'{self._wx_data[k][-1]["weather"].get("wind_direction", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("wind_gust", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("wind_speed", "-")}',
                f'{self._wx_data[k][-1]["weather"].get("luminosity", "-")}',
                f'{self._wx_data[k][-1].get("comment", "")}',
            ))

    def _sort_entry(self, col):
        self._last_sort_col = col
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

    def _entry_selected(self, event):
        _key = ''
        for selected_item in self._tree.selection():
            _item = self._tree.item(selected_item)
            _key = _item['values'][1]
        if _key:
            _data = self._wx_data.get(_key, False)
            if _data:
                WXPlotWindow(self._root_win, _data)

    def close(self):
        self._ais_obj.wx_tree_gui = None
        # self._ais_obj = None
        self._root_win.wx_window = None
        self.destroy()
