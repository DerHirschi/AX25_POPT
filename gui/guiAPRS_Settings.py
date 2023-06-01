import tkinter as tk
from tkinter import ttk

from fnc.loc_fnc import locator_to_coordinates, coordinates_to_locator
from string_tab import STR_TABLE


class APRSSettingsWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root_cl = root_win
        self.lang = self.root_cl.language
        self.root_cl.settings_win = self
        self.win_height = 500
        self.win_width = 800
        self.style = self.root_cl.style
        self.title(STR_TABLE['aprs_settings'][self.lang])
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root_cl.main_win.winfo_x()}+"
                      f"{self.root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        #self.resizable(False, False)
        self.lift()
        self.all_ports = self.root_cl.ax25_port_handler.ax25_ports
        self.vars = []
        # Create a Notebook widget
        notebook = ttk.Notebook(self)

        for port_id in self.all_ports.keys():
            # Create the "Port 1" tab
            port_tab = ttk.Frame(notebook)
            notebook.add(port_tab, text=f"Port {port_id}")

            # Add content to the "Port 1" tab
            self.create_settings_widgets(port_tab, self.all_ports[port_id].port_cfg.parm_aprs_station)


        # Pack the Notebook widget
        notebook.pack(fill=tk.BOTH, expand=True)
        """
        # Create a frame for additional buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Create additional buttons
        button1 = ttk.Button(button_frame, text="Button 1")
        button1.pack(side=tk.LEFT, padx=5)

        button2 = ttk.Button(button_frame, text="Button 2")
        button2.pack(side=tk.LEFT, padx=5)
        """
        # Create OK and Cancel buttons
        button_frame2 = ttk.Frame(self)
        button_frame2.pack(side=tk.BOTTOM, padx=10, pady=10)

        ok_button = ttk.Button(button_frame2, text="OK", command=self.on_ok_button)
        ok_button.pack(side=tk.LEFT)

        cancel_button = ttk.Button(button_frame2, text="Abbrechen", command=self.on_cancel_button)
        cancel_button.pack(side=tk.RIGHT)

    def create_settings_widgets(self, tab, port_aprs):
        self.vars.append({
            'call': tk.StringVar(tab),
            'loc': tk.StringVar(tab),
            'lat': tk.StringVar(tab),
            'lon': tk.StringVar(tab),
            'text': tk.StringVar(tab),
            'digi': tk.BooleanVar(tab),
            'ais': tk.BooleanVar(tab),

        })

        # Create Call entry field
        tab.columnconfigure(0, minsize=5, weight=0)
        tab.columnconfigure(1, minsize=130, weight=0)
        tab.columnconfigure(2, minsize=200, weight=2)
        tab.columnconfigure(3, minsize=200, weight=1)
        tab.columnconfigure(4, minsize=5, weight=0)
        call_label = ttk.Label(tab, text="Call:")
        call_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        call_entry = ttk.Entry(tab, width=10, textvariable=self.vars[-1]['call'])
        call_entry.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        self.vars[-1]['call'].set(port_aprs.aprs_parm_call)

        # Create Locator entry field
        locator_label = ttk.Label(tab, text="Locator:")
        locator_label.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        locator_entry = ttk.Entry(tab, width=10, textvariable=self.vars[-1]['loc'])
        locator_entry.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        self.vars[-1]['loc'].set(port_aprs.aprs_parm_loc)


        # Create Latitude entry field
        latitude_label = ttk.Label(tab, text="Latitude:")
        latitude_label.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        latitude_entry = ttk.Entry(tab, width=10, textvariable=self.vars[-1]['lat'])
        latitude_entry.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)
        self.vars[-1]['lat'].set(port_aprs.aprs_parm_lat)


        # Create Longitude entry field
        longitude_label = ttk.Label(tab, text="Longitude:")
        longitude_label.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        longitude_entry = ttk.Entry(tab, width=10, textvariable=self.vars[-1]['lon'])
        longitude_entry.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)
        self.vars[-1]['lon'].set(port_aprs.aprs_parm_lon)

        # Create DIGI checkbutton
        digi_checkbutton_label = ttk.Label(tab, text="DIGI:")
        digi_checkbutton_label.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        digi_checkbutton = ttk.Checkbutton(tab, variable=self.vars[-1]['digi'])
        digi_checkbutton.grid(row=4, column=2, columnspan=2, padx=10, pady=5, sticky=tk.W)
        self.vars[-1]['digi'].set(port_aprs.aprs_parm_digi)

        # Create AIS checkbutton
        ais_var = tk.StringVar()
        ais_checkbutton_label = ttk.Label(tab, text="AIS:")
        ais_checkbutton_label.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
        ais_checkbutton = ttk.Checkbutton(tab, variable=self.vars[-1]['ais'])
        ais_checkbutton.grid(row=5, column=2, columnspan=2, padx=10, pady=5, sticky=tk.W)
        self.vars[-1]['ais'].set(port_aprs.aprs_parm_igate)

        # Create Baken Text label
        baken_label = ttk.Label(tab, text="Baken Text:")
        baken_label.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)

        baken_textbox = tk.Text(tab, width=85, height=5)
        baken_textbox.grid(row=7, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)
        self.vars[-1]['text'].set(port_aprs.aprs_beacon_text)

    def set_vars(self):

        ind = 0
        for port_id in self.all_ports.keys():
            lon = self.vars[ind]['lon'].get()
            lat = self.vars[ind]['lat'].get()
            loc = self.vars[ind]['loc'].get()

            if not loc:
                if lat and lon:
                    loc = coordinates_to_locator(
                        latitude=float(self.vars[ind]['lat'].get()),
                        longitude=float(self.vars[ind]['lon'].get()),
                    )
                    self.vars[ind]['loc'].set(loc)
            if not lat:
                if loc:
                    lat, lon = locator_to_coordinates(self.vars[ind]['loc'].get())
                    self.vars[ind]['lat'].set(str(lat))
                    self.vars[ind]['lon'].set(str(lon))

            self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_call = self.vars[ind]['call'].get()
            self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_loc = self.vars[ind]['loc'].get()
            self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_lat = self.vars[ind]['lat'].get()
            self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_lon = self.vars[ind]['lon'].get()
            self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_beacon_text = self.vars[ind]['text'].get()
            self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_igate = self.vars[ind]['ais'].get()
            self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_digi = self.vars[ind]['digi'].get()
            ind += 1

    def on_ok_button(self):
        self.set_vars()
        self.destroy_win()

    def on_cancel_button(self):
        # Cancel button click handler
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.root_cl.settings_win = None

    def tasker(self):
        pass
