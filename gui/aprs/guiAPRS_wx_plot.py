from datetime import datetime
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
                      f"640+"
                      f"{root_cl.main_win.winfo_x()}+"
                      f"{root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._wx_data = wx_data
        #################
        # Settings Frame Frame
        settings_frame = tk.Frame(self)
        settings_frame.pack(side=tk.TOP)
        self._xLimt_var = tk.StringVar(self, value='7')
        tk.Label(settings_frame, text='X-Limit (Days): ').pack(side=tk.LEFT)
        tk.Spinbox(settings_frame,
                   from_=1,
                   to=3650,
                   increment=1,
                   width=5,
                   textvariable=self._xLimt_var,
                   command=self._change_xlim,
                   ).pack(side=tk.LEFT)
        ##################
        # Plot erstellen
        plot_frame = tk.Frame(self)
        plot_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        # fig = Figure(figsize=(10, 1), dpi=100)
        # fig = plt.figure(figsize=(10, 1), dpi=100)
        fig, self._plot1 = plt.subplots()
        fig.set_facecolor('xkcd:light grey')
        self._plot1.set_facecolor('#000000')
        self._plot2 = self._plot1.twinx()
        self._plot2.set_facecolor('#000000')
        self._plot2.yaxis.tick_right()

        fig.subplots_adjust(top=0.95, bottom=0.05, left=0.07, right=0.93, )

        # Canvas für den Plot erstellen und in das Tkinter-Fenster einbetten
        self._canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self._canvas.draw()
        # Werkzeugleisten für die Plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, plot_frame, pack_toolbar=False)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, )
        self._canvas.get_tk_widget().pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self._canvas.draw()
        #################
        # Info Frame
        info_frame = tk.Frame(self)
        info_frame.pack(side=tk.TOP, fill=tk.BOTH)
        self._change_xlim()
        self._plot1.legend(
            fontsize=8,
            loc='upper left'
        )
        self._plot2.legend(
            fontsize=8,
            loc='upper right'
        )
        if self._wx_data:
            if self._wx_data[-1]:
                call = self._wx_data[-1][10]
                comment = self._wx_data[-1][11]
                location_frame = tk.Frame(info_frame)

                wx_data_str = (f"{self._wx_data[-1][15]}: "
                               f"Temp: {self._wx_data[-1][5]}°C | "
                               f"Hum: {self._wx_data[-1][1]}% | "
                               f"Pres: {self._wx_data[-1][0]}hPa")

                tk.Label(info_frame, text=call).pack(side=tk.TOP, )
                tk.Label(info_frame, text=comment).pack(side=tk.TOP, )
                tk.Label(info_frame, text=wx_data_str).pack(side=tk.TOP, )
                location_frame.pack(side=tk.TOP, )

                loc = f'Locator: {self._wx_data[-1][12]}'
                lat = f'Lat: {self._wx_data[-1][13]}'
                lon = f'Lon: {self._wx_data[-1][14]}'
                tk.Label(location_frame, text=loc).pack(side=tk.LEFT, padx=20)
                tk.Label(location_frame, text=lat).pack(side=tk.LEFT, padx=20)
                tk.Label(location_frame, text=lon).pack(side=tk.LEFT, padx=20)

                self.wm_title(f"WX Plot {call}")

    def _update_plot(self):
        if not self._wx_data:
            return
        # _delta_time_24h = datetime.now() - timedelta(hours=24)
        x_scale = []
        y_pressure = []
        y_hum = []
        y_rain_1 = []
        y_rain_24 = []
        y_rain_day = []
        y_temp = []
        y_wind_dir = []
        y_wind_gust = []
        y_wind_speed = []
        y_lum = []
        ts_now = datetime.now()
        for data in self._wx_data:
            timestamt_dt = data[-1]
            timestamt_dt = convert_str_to_datetime(timestamt_dt)
            if timestamt_dt:
                if data[0]:
                    y_pressure.append(float(data[0]))
                    # y_pressure = adjust_list_len(y_pressure, x_scale)
                if data[1]:
                    y_hum.append(float(data[1]))
                    # y_hum = adjust_list_len(y_hum, x_scale)
                if data[2]:
                    y_rain_1.append(float(data[2]))
                    # y_rain_1 = adjust_list_len(y_rain_1, x_scale)
                if data[3]:
                    y_rain_24.append(float(data[3]))
                    # y_rain_24 = adjust_list_len(y_rain_24, x_scale)
                if data[4]:
                    y_rain_day.append(float(data[4]))
                    # y_rain_day = adjust_list_len(y_rain_day, x_scale)
                if data[5]:
                    y_temp.append(float(data[5]))
                    # y_temp = adjust_list_len(y_temp, x_scale)
                if data[6]:
                    y_wind_dir.append(float(data[6]))
                    # y_wind_dir = adjust_list_len(y_wind_dir, x_scale)
                if data[7]:
                    y_wind_gust.append(float(data[7]))
                    # y_wind_gust = adjust_list_len(y_wind_gust, x_scale)
                if data[8]:
                    y_wind_speed.append(float(data[8]))
                    # y_wind_speed = adjust_list_len(y_wind_speed, x_scale)
                if data[9]:
                    y_lum.append(float(data[9]))
                    # y_lum = adjust_list_len(y_lum, x_scale)

                # if datetime.now().timestamp() - _timestamt_dt.timestamp() < _delta_time_24h.timestamp():

                dif = ts_now - timestamt_dt
                x_scale.append(dif.total_seconds() / 3600)

        if y_pressure:
            y_pressure = adjust_list_len(y_pressure, x_scale)
            self._plot2.plot(x_scale, y_pressure, label='Pressure', color='yellow', linestyle='dashed')
        if y_hum:
            y_hum = adjust_list_len(y_hum, x_scale)
            self._plot1.plot(x_scale, y_hum, label='Humidity', color='blue')
        if y_rain_1:
            y_rain_1 = adjust_list_len(y_rain_1, x_scale)
            self._plot1.plot(x_scale, y_rain_1, label='Rain 1h')
        if y_rain_24:
            y_rain_24 = adjust_list_len(y_rain_24, x_scale)
            self._plot1.plot(x_scale, y_rain_24, label='Rain 24h')
        if y_rain_day:
            y_rain_day = adjust_list_len(y_rain_day, x_scale)
            self._plot1.plot(x_scale, y_rain_day, label='Rain Day')
        if y_temp:
            y_temp = adjust_list_len(y_temp, x_scale)
            self._plot1.plot(x_scale, y_temp, label='Temperature', color='red')
        if y_wind_dir:
            y_wind_dir = adjust_list_len(y_wind_dir, x_scale)
            self._plot1.plot(x_scale, y_wind_dir, label='Wind Dir')
        if y_wind_gust:
            y_wind_gust = adjust_list_len(y_wind_gust, x_scale)
            self._plot1.plot(x_scale, y_wind_gust, label='Wind Gust')
        if y_wind_speed:
            y_wind_speed = adjust_list_len(y_wind_speed, x_scale)
            self._plot1.plot(x_scale, y_wind_speed, label='Wind Speed')
        if y_lum:
            y_lum = adjust_list_len(y_lum, x_scale)
            self._plot1.plot(x_scale, y_lum, label='Luminosity', color='orange')


    def _change_xlim(self, event=None):
        self._update_plot()
        try:
            days = int(self._xLimt_var.get())
        except ValueError:
            return
        if not days:
            return
        lim = 24 * days
        print(lim)
        self._plot1.set_xlim([lim, 0])  # x-Achse auf 24 Stunden begrenzen
        self._plot2.set_xlim([lim, 0])  # x-Achse auf 24 Stunden begrenzen
        self._canvas.draw()

    def destroy_win(self):
        self.destroy_plot()

    def destroy_plot(self):
        # self._canvas.close_event('all')
        # self._canvas.get_tk_widget().destroy()
        # self._canvas.close_event()
        plt.close()
        # del self._canvas
        del self._plot1
        del self._plot2
        # del self._fig
        # self._canvas = None
        self._plot1 = None
        self._plot2 = None
        # self._fig = None
        self.withdraw()
        self.destroy()
