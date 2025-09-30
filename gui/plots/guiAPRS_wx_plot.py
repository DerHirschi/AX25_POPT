""" Opt by Grok-AI """
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib

matplotlib.use('TkAgg')  # Ensure TkAgg backend for thread safety
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from gui import plt as plt
from fnc.str_fnc import convert_str_to_datetime
from cfg.logger_config import logger


def adjust_list_len(target_list: list, compare_list: list) -> list:
    """Adjust the length of target_list to match compare_list by padding with zeros."""
    if len(target_list) < len(compare_list):
        target_list.extend([0] * (len(compare_list) - len(target_list)))
    return target_list


class WXPlotWindow(tk.Toplevel):
    def __init__(self, root_cl, wx_data):
        super().__init__(master=root_cl.main_win)
        self.root_cl = root_cl
        self.wx_data = wx_data
        self.title("WX Plot")
        self.geometry(f"800x640+{root_cl.main_win.winfo_x()}+{root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_plot)

        # Set window icon
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(f"Failed to set window icon: {ex}")

        self.lift()
        self._initialize_ui()
        self._update_info_frame()
        self._update_plot()

    def _initialize_ui(self):
        """Initialize the UI components."""
        # Settings Frame
        settings_frame = ttk.Frame(self)
        settings_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.x_limit_var = tk.StringVar(value='7')
        ttk.Label(settings_frame, text='X-Limit (Days): ').pack(side=tk.LEFT)
        ttk.Spinbox(
            settings_frame,
            from_=1,
            to=3650,
            increment=1,
            width=5,
            textvariable=self.x_limit_var,
            command=self._update_plot
        ).pack(side=tk.LEFT, padx=5)

        # Plot Frame
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Initialize Matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.fig.set_facecolor('xkcd:light grey')
        self.plot1 = self.fig.add_subplot(111)
        self.plot1.set_facecolor('#000000')
        self.plot2 = self.plot1.twinx()
        self.plot2.set_facecolor('#000000')
        self.plot2.yaxis.tick_right()
        self.fig.subplots_adjust(top=0.95, bottom=0.1, left=0.05, right=0.95)

        # Canvas and Toolbar
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Info Frame
        self.info_frame = ttk.Frame(self.plot_frame)
        self.info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Right Frame for Checkbuttons
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self._initialize_checkbuttons(right_frame)

    def _initialize_checkbuttons(self, parent):
        """Initialize checkbuttons for plot data selection."""
        self.check_vars = {
            'Pressure': tk.BooleanVar(value=True),
            'Humidity': tk.BooleanVar(value=True),
            'Rain 1h': tk.BooleanVar(value=True),
            'Rain 24h': tk.BooleanVar(value=True),
            'Rain Day': tk.BooleanVar(value=True),
            'Temperature': tk.BooleanVar(value=True),
            'Wind Dir': tk.BooleanVar(value=True),
            'Wind Gust': tk.BooleanVar(value=True),
            'Wind Speed': tk.BooleanVar(value=True),
            'Luminosity': tk.BooleanVar(value=True),
        }

        for label, var in self.check_vars.items():
            ttk.Checkbutton(
                parent,
                text=label,
                variable=var,
                command=self._update_plot
            ).pack(padx=15, pady=5, anchor='w')

    def _update_info_frame(self):
        """Update the info frame with the latest weather data."""
        if not self.wx_data or not self.wx_data[-1]:
            return

        for widget in self.info_frame.winfo_children():
            widget.destroy()

        call = self.wx_data[-1][10]
        comment = self.wx_data[-1][11]
        wx_data_str = (
            f"{self.wx_data[-1][15]}: "
            f"Temp: {self.wx_data[-1][5]}°C | "
            f"Hum: {self.wx_data[-1][1]}% | "
            f"Pres: {self.wx_data[-1][0]}hPa"
        )
        location_frame = ttk.Frame(self.info_frame)

        ttk.Label(self.info_frame, text=call).pack(side=tk.TOP)
        ttk.Label(self.info_frame, text=comment).pack(side=tk.TOP)
        ttk.Label(self.info_frame, text=wx_data_str).pack(side=tk.TOP)

        loc = f'Locator: {self.wx_data[-1][12]}'
        lat = f'Lat: {self.wx_data[-1][13]}'
        lon = f'Lon: {self.wx_data[-1][14]}'
        ttk.Label(location_frame, text=loc).pack(side=tk.LEFT, padx=20)
        ttk.Label(location_frame, text=lat).pack(side=tk.LEFT, padx=20)
        ttk.Label(location_frame, text=lon).pack(side=tk.LEFT, padx=20)
        location_frame.pack(side=tk.TOP)

        self.title(f"WX Plot {call}")

    def _update_plot(self, event=None):
        """Update the plot based on current settings, excluding null data from the last data point to now."""
        if not self.wx_data:
            return

        self.plot1.clear()
        self.plot2.clear()

        # Prepare data
        x_scale = []
        data_dict = {
            'Pressure': [],
            'Humidity': [],
            'Rain 1h': [],
            'Rain 24h': [],
            'Rain Day': [],
            'Temperature': [],
            'Wind Dir': [],
            'Wind Gust': [],
            'Wind Speed': [],
            'Luminosity': []
        }

        ts_now = datetime.now()
        for data in self.wx_data:
            timestamp_dt = convert_str_to_datetime(data[15])
            if not timestamp_dt:
                continue

            dif = ts_now - timestamp_dt
            hours_diff = dif.total_seconds() / 3600

            # Only include data points up to the last valid data point
            valid_data = False
            for idx, key in enumerate(data_dict.keys()):
                if data[idx] and data[idx] != '':
                    valid_data = True
                    data_dict[key].append(float(data[idx]))
                else:
                    data_dict[key].append(None)  # Use None for null data

            if valid_data:
                x_scale.append(hours_diff)

        # Plot data
        colors = {
            'Pressure': 'yellow',
            'Humidity': 'blue',
            'Rain 1h': 'cyan',
            'Rain 24h': 'green',
            'Rain Day': 'lime',
            'Temperature': 'red',
            'Wind Dir': 'purple',
            'Wind Gust': 'magenta',
            'Wind Speed': 'pink',
            'Luminosity': 'orange'
        }

        for key, var in self.check_vars.items():
            if var.get() and data_dict[key]:
                y_data = adjust_list_len([y for y in data_dict[key] if y is not None], x_scale)
                if key == 'Pressure':
                    self.plot2.plot(x_scale[:len(y_data)], y_data, label=key, color=colors[key], linestyle='dashed')
                else:
                    self.plot1.plot(x_scale[:len(y_data)], y_data, label=key, color=colors[key])

        # Set axis limits
        try:
            days = int(self.x_limit_var.get())
            if days > 0:
                lim = 24 * days
                self.plot1.set_xlim(lim, 0)
                self.plot2.set_xlim(lim, 0)
        except ValueError:
            pass

        # Configure legends
        self.plot1.legend(fontsize=8, loc='upper left')
        self.plot2.legend(fontsize=8, loc='upper right')

        self.canvas.draw()

    def destroy_plot(self):
        """Clean up resources and close the window."""
        try:
            self.plot1.clear()
            self.plot2.clear()
            self.fig.clear()
            plt.close(self.fig)
            self.canvas.get_tk_widget().destroy()
            #self.canvas = None
            self.destroy()
        except Exception as ex:
            logger.error(f"Error during plot cleanup: {ex}")