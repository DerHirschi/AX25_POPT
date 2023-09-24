from datetime import datetime, timedelta
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from fnc.loc_fnc import coordinates_to_locator
from fnc.str_fnc import convert_str_to_datetime


def adjust_list_len(target_list: list, compare_list: list):
    if len(target_list) < len(compare_list):
        target_list.extend([0] * (len(compare_list) - len(target_list)))
    return target_list


class WXPlotWindow(tk.Toplevel):
    def __init__(self, root_cl, wx_data):
        tk.Toplevel.__init__(self)
        # self.root_cl = root_cl
        self.geometry(f"800x"
                      f"600+"
                      f"{root_cl.main_win.winfo_x()}+"
                      f"{root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._wx_data = wx_data
        ##################
        # Plot erstellen
        plot_frame = tk.Frame(self)
        plot_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self._fig = Figure(figsize=(10, 1), dpi=100)
        self._fig.set_facecolor('xkcd:light grey')

        self._plot1 = self._fig.add_subplot(111)
        self._plot1.set_facecolor('#000000')

        self._fig.subplots_adjust(top=0.98, bottom=0.05, left=0.05, right=0.98,)

        # Canvas für den Plot erstellen und in das Tkinter-Fenster einbetten
        self._canvas = FigureCanvasTkAgg(self._fig, master=plot_frame)
        self._canvas.draw()
        # Werkzeugleisten für die Plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, plot_frame, pack_toolbar=False)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, )
        self._canvas.get_tk_widget().pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self._update_plots()

        self._plot1.legend(
                           fontsize=8,
                           loc='upper left'
                           )


        self._canvas.draw()
        #################
        # Info Frame
        info_frame = tk.Frame(self)
        info_frame.pack(side=tk.TOP, fill=tk.BOTH)
        _call = self._wx_data[0][1].get('from', '')
        _comment = self._wx_data[0][1].get('comment', '')
        _loc = coordinates_to_locator(
            self._wx_data[0][1].get("latitude", 0),
            self._wx_data[0][1].get("longitude", 0),
        )
        _loc = f'Locator: {_loc}'
        _lat = f'Lat: {self._wx_data[0][1].get("latitude", "")}'
        _lon = f'Lon: {self._wx_data[0][1].get("longitude", "")}'

        tk.Label(info_frame, text=_call).pack(side=tk.TOP,)
        tk.Label(info_frame, text=_comment).pack()
        tk.Label(info_frame, text=_loc).pack(side=tk.LEFT, padx=20)
        tk.Label(info_frame, text=_lat).pack(side=tk.LEFT, padx=20)
        tk.Label(info_frame, text=_lon).pack(side=tk.LEFT, padx=20)

        self.wm_title(f"WX Plot {_call}")

    def _update_plots(self):
        _delta_time_24h = datetime.now() - timedelta(hours=24)
        _x_scale = []
        _y_pressure = []
        _y_hum = []
        _y_rain_1 = []
        _y_rain_24 = []
        _y_rain_day = []
        _y_temp = []
        _y_wind_dir = []
        _y_wind_gust = []
        _y_wind_speed = []
        _y_lum = []
        _wx_data = list(self._wx_data)
        _wx_data.reverse()
        _now = datetime.now()
        for _data in self._wx_data:
            _timestamp = _data[0]
            _timestamt_dt = convert_str_to_datetime(_timestamp)
            if _timestamt_dt:
                # if datetime.now().timestamp() - _timestamt_dt.timestamp() < _delta_time_24h.timestamp():

                if 'weather' in _data[1].keys():
                    if 'pressure' in _data[1]['weather'].keys():
                        _y_pressure = adjust_list_len(_y_pressure, _x_scale)
                        _y_pressure.append(_data[1]['weather']['pressure'])

                    if 'humidity' in _data[1]['weather'].keys():
                        _y_hum = adjust_list_len(_y_hum, _x_scale)
                        _y_hum.append(_data[1]['weather']['humidity'])

                    if 'rain_1h' in _data[1]['weather'].keys():
                        _y_rain_1 = adjust_list_len(_y_rain_1, _x_scale)
                        _y_rain_1.append(_data[1]['weather']['rain_1h'])

                    if 'rain_24h' in _data[1]['weather'].keys():
                        _y_rain_24 = adjust_list_len(_y_rain_24, _x_scale)
                        _y_rain_24.append(_data[1]['weather']['rain_24h'])

                    if 'rain_since_midnight' in _data[1]['weather'].keys():
                        _y_rain_day = adjust_list_len(_y_rain_day, _x_scale)
                        _y_rain_day.append(_data[1]['weather']['rain_since_midnight'])

                    if 'temperature' in _data[1]['weather'].keys():
                        _y_temp = adjust_list_len(_y_temp, _x_scale)
                        _y_temp.append(_data[1]['weather']['temperature'])

                    if 'wind_direction' in _data[1]['weather'].keys():
                        _y_wind_dir = adjust_list_len(_y_wind_dir, _x_scale)
                        _y_wind_dir.append(_data[1]['weather']['wind_direction'])

                    if 'wind_gust' in _data[1]['weather'].keys():
                        _y_wind_gust = adjust_list_len(_y_wind_gust, _x_scale)
                        _y_wind_gust.append(_data[1]['weather']['wind_gust'])

                    if 'wind_speed' in _data[1]['weather'].keys():
                        _y_wind_speed = adjust_list_len(_y_wind_speed, _x_scale)
                        _y_wind_speed.append(_data[1]['weather']['wind_speed'])

                    if 'luminosity' in _data[1]['weather'].keys():
                        _y_lum = adjust_list_len(_y_lum, _x_scale)
                        _y_lum.append(_data[1]['weather']['luminosity'])

                    _dif = _now - _timestamt_dt
                    _x_scale.append(_dif.total_seconds() / 3600)

        if _y_pressure:
            _y_pressure = adjust_list_len(_y_pressure, _x_scale)
            self._plot1.plot(_x_scale, _y_pressure, label='Pressure')
        if _y_hum:
            _y_hum = adjust_list_len(_y_hum, _x_scale)
            self._plot1.plot(_x_scale, _y_hum, label='Humidity')
        if _y_rain_1:
            _y_rain_1 = adjust_list_len(_y_rain_1, _x_scale)
            self._plot1.plot(_x_scale, _y_rain_1, label='Rain 1h')
        if _y_rain_24:
            _y_rain_24 = adjust_list_len(_y_rain_24, _x_scale)
            self._plot1.plot(_x_scale, _y_rain_24, label='Rain 24h')
        if _y_rain_day:
            _y_rain_day = adjust_list_len(_y_rain_day, _x_scale)
            self._plot1.plot(_x_scale, _y_rain_day, label='Rain Day')
        if _y_temp:
            _y_temp = adjust_list_len(_y_temp, _x_scale)
            self._plot1.plot(_x_scale, _y_temp, label='Temperature')
        if _y_wind_dir:
            _y_wind_dir = adjust_list_len(_y_wind_dir, _x_scale)
            self._plot1.plot(_x_scale, _y_wind_dir, label='Wind Dir')
        if _y_wind_gust:
            _y_wind_gust = adjust_list_len(_y_wind_gust, _x_scale)
            self._plot1.plot(_x_scale, _y_wind_gust, label='Wind Gust')
        if _y_wind_speed:
            _y_wind_speed = adjust_list_len(_y_wind_speed, _x_scale)
            self._plot1.plot(_x_scale, _y_wind_speed, label='Wind Speed')
        if _y_lum:
            _y_lum = adjust_list_len(_y_lum, _x_scale)
            self._plot1.plot(_x_scale, _y_lum, label='Luminosity')

        self._plot1.set_xlim([24, 0])  # x-Achse auf 24 Stunden begrenzen

    def destroy_win(self):
        self.destroy_plot()

    def destroy_plot(self):
        self._canvas.close_event('all')
        self._canvas.get_tk_widget().destroy()
        self._canvas.close_event()
        plt.close()
        del self._canvas
        del self._plot1
        del self._fig
        self._canvas = None
        self._plot1 = None
        self._fig = None
        self.withdraw()
        self.destroy()

