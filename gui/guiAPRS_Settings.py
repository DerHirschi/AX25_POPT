import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from fnc.loc_fnc import locator_to_coordinates, coordinates_to_locator
from string_tab import STR_TABLE


class APRSSettingsWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_cl = root_win
        self.lang = self._root_cl.language
        self._root_cl.settings_win = self
        self.win_height = 620
        self.win_width = 800
        self.style = self._root_cl.style
        self.title(STR_TABLE['aprs_settings'][self.lang])
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._all_ports = PORT_HANDLER.get_all_ports()
        self._ais = PORT_HANDLER.get_aprs_ais()
        self._vars = []

        self.ais_call_var = tk.StringVar(self)
        self.ais_pass_var = tk.StringVar(self)
        self.ais_port_var = tk.StringVar(self)
        self.ais_host_var = tk.StringVar(self)
        self.ais_loc_var = tk.StringVar(self)
        self.ais_lat_var = tk.StringVar(self)
        self.ais_lon_var = tk.StringVar(self)
        self.ais_run_var = tk.BooleanVar(self)
        self.ais_add_new_user_var = tk.BooleanVar(self)
        if self._ais is not None:
            self.ais_call_var.set(self._ais.ais_call)
            self.ais_pass_var.set(self._ais.ais_pass)
            self.ais_port_var.set(str(self._ais.ais_host[1]))
            self.ais_host_var.set(self._ais.ais_host[0])
            self.ais_lat_var.set(str(self._ais.ais_lat))
            self.ais_lon_var.set(str(self._ais.ais_lon))
            self.ais_loc_var.set(self._ais.ais_loc)
            self.ais_run_var.set(self._ais.ais_active)
            self.ais_add_new_user_var.set(self._ais.add_new_user)

        ais_conf_frame = ttk.Frame(self)
        ais_conf_frame.pack(side=tk.TOP, padx=10, pady=10)
        ais_conf_frame.rowconfigure(0, minsize=40, weight=0)
        ais_conf_frame.columnconfigure(0, minsize=5, weight=0)
        ais_conf_frame.columnconfigure(1, minsize=60, weight=1)
        ais_conf_frame.columnconfigure(2, minsize=120, weight=1)
        ais_conf_frame.columnconfigure(3, minsize=30, weight=0)
        ais_conf_frame.columnconfigure(4, minsize=80, weight=1)
        ais_conf_frame.columnconfigure(5, minsize=120, weight=1)
        ais_conf_frame.columnconfigure(6, minsize=5, weight=0)
        ttk.Label(ais_conf_frame, text="AIS/APRS-Server Config").place(x=240, y=0)

        ttk.Label(ais_conf_frame, text="Call:").grid(row=2, column=1, sticky=tk.W)
        ais_call_ent = ttk.Entry(ais_conf_frame, width=10, textvariable=self.ais_call_var)
        ais_call_ent.grid(row=2, column=2,  sticky=tk.W)

        ttk.Label(ais_conf_frame, text="Passw:").grid(row=3, column=1, sticky=tk.W)
        ais_call_ent = ttk.Entry(ais_conf_frame, width=20, textvariable=self.ais_pass_var)
        ais_call_ent.grid(row=3, column=2, sticky=tk.W)

        ttk.Label(ais_conf_frame, text="Adresse:").grid(row=2, column=4, sticky=tk.W)
        ais_call_ent = ttk.Entry(ais_conf_frame, width=30, textvariable=self.ais_host_var)
        ais_call_ent.grid(row=2, column=5, sticky=tk.W)

        ttk.Label(ais_conf_frame, text="Port:").grid(row=3, column=4, sticky=tk.W)
        ais_call_ent = ttk.Entry(ais_conf_frame, width=10, textvariable=self.ais_port_var)
        ais_call_ent.grid(row=3, column=5, sticky=tk.W)

        # Create Locator entry field
        locator_label = ttk.Label(ais_conf_frame, text="Locator:")
        locator_label.grid(row=4, column=1, sticky=tk.W)
        locator_entry = ttk.Entry(ais_conf_frame, width=10, textvariable=self.ais_loc_var)
        locator_entry.grid(row=4, column=2, sticky=tk.W)
        # self.vars[-1]['loc'].set(port_aprs.aprs_parm_loc)

        # Create Latitude entry field
        latitude_label = ttk.Label(ais_conf_frame, text="Latitude:")
        latitude_label.grid(row=4, column=4, sticky=tk.W)
        latitude_entry = ttk.Entry(ais_conf_frame, width=10, textvariable=self.ais_lat_var)
        latitude_entry.grid(row=4, column=5, sticky=tk.W)


        # Create Longitude entry field
        longitude_label = ttk.Label(ais_conf_frame, text="Longitude:")
        longitude_label.grid(row=5, column=4, sticky=tk.W)
        longitude_entry = ttk.Entry(ais_conf_frame, width=10, textvariable=self.ais_lon_var)
        longitude_entry.grid(row=5, column=5, sticky=tk.W)
        # self.vars[-1]['lon'].set(port_aprs.aprs_parm_lon)

        tk.Checkbutton(ais_conf_frame, text="Run", variable=self.ais_run_var).grid(row=5, column=1, sticky=tk.W)
        tk.Checkbutton(ais_conf_frame, text="Add to UserDB", variable=self.ais_add_new_user_var).grid(row=6, column=1, columnspan=3, sticky=tk.W)

        # Create a Notebook widget
        notebook = ttk.Notebook(self)

        for port_id in self._all_ports.keys():
            # Create the "Port 1" tab
            port_tab = ttk.Frame(notebook)
            notebook.add(port_tab, text=f"Port {port_id}")

            # Add content to the "Port 1" tab
            self.create_settings_widgets(port_tab, self._all_ports[port_id].port_cfg.parm_aprs_station)


        # Pack the Notebook widget
        notebook.pack(fill=tk.BOTH, expand=True)

        # Create OK and Cancel buttons
        button_frame2 = ttk.Frame(self)
        button_frame2.pack(side=tk.BOTTOM, padx=10, pady=10)

        ok_button = ttk.Button(button_frame2, text="OK", command=self._on_ok_button)
        ok_button.pack(side=tk.LEFT)

        cancel_button = ttk.Button(button_frame2, text="Abbrechen", command=self._on_cancel_button)
        cancel_button.pack(side=tk.RIGHT)

    def create_settings_widgets(self, tab, port_aprs):
        self._vars.append({
            'call': tk.StringVar(tab),
            # 'loc': tk.StringVar(tab),
            # 'lat': tk.StringVar(tab),
            # 'lon': tk.StringVar(tab),
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
        call_entry = ttk.Entry(tab, width=10, textvariable=self._vars[-1]['call'], state='disabled')
        call_entry.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        # self.vars[-1]['call'].set(port_aprs.aprs_parm_call)

        # Create DIGI checkbutton
        digi_checkbutton_label = ttk.Label(tab, text="DIGI:")
        digi_checkbutton_label.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        digi_checkbutton = ttk.Checkbutton(tab, variable=self._vars[-1]['digi'], state='disabled')
        digi_checkbutton.grid(row=4, column=2, columnspan=2, padx=10, pady=5, sticky=tk.W)
        self._vars[-1]['digi'].set(port_aprs.aprs_parm_digi)

        # Create AIS checkbutton
        ais_checkbutton_label = ttk.Label(tab, text="I-GATE:")
        ais_checkbutton_label.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
        ais_checkbutton = ttk.Checkbutton(tab, variable=self._vars[-1]['ais'], state='disabled')
        ais_checkbutton.grid(row=5, column=2, columnspan=2, padx=10, pady=5, sticky=tk.W)
        self._vars[-1]['ais'].set(port_aprs.aprs_parm_igate)

        # Create Baken Text label
        baken_label = ttk.Label(tab, text="Baken Text:")
        baken_label.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)

        baken_textbox = tk.Text(tab, width=85, height=3, state='disabled')
        baken_textbox.grid(row=7, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)
        # self.vars[-1]['text'].set(port_aprs.aprs_beacon_text)

    def _set_vars(self):
        _ind = 0
        _aprs_station = {}
        for port_id in self._all_ports.keys():
            # self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_call = self.vars[ind]['call'].get()
            # self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_beacon_text = self.vars[ind]['text'].get()
            self._all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_igate = self._vars[_ind]['ais'].get()
            self._all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_digi = self._vars[_ind]['digi'].get()

            self._all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_loc = self._vars[_ind]['digi'].get()
            if self._ais is not None:
                # self.all_ports[port_id].port_cfg.parm_aprs_station.aprs_ais = self.ais
                self._all_ports[port_id].port_cfg.parm_aprs_station.aprs_parm_loc = self._ais.ais_loc
            _aprs_station[port_id] = self._all_ports[port_id].port_cfg.parm_aprs_station
            _ind += 1

        try:
            _lon = float(self.ais_lon_var.get())
        except ValueError:
            _lon = 0
        try:
            _lat = float(self.ais_lat_var.get())
        except ValueError:
            _lat = 0
        _loc = self.ais_loc_var.get()

        if not _loc:
            if _lat and _lon:
                _loc = coordinates_to_locator(
                    latitude=_lat,
                    longitude=_lon,
                )
                self.ais_loc_var.set(_loc)
        if not _lat or not _lon:
            if _loc:
                _lat, _lon = locator_to_coordinates(_loc)
                self.ais_lat_var.set(str(_lat))
                self.ais_lon_var.set(str(_lon))

        if self._ais is not None:
            # self._ais.task_halt()
            self._ais.ais_close()
            self._ais.ais_call = self.ais_call_var.get()
            self._ais.ais_pass = self.ais_pass_var.get()
            self._ais.ais_active = self.ais_run_var.get()
            self._ais.add_new_user = self.ais_add_new_user_var.get()
            self._ais.ais_loc = _loc
            self._ais.ais_lat = float(_lat)
            self._ais.ais_lon = float(_lon)
            self._ais.ais_aprs_stations = _aprs_station

            if self.ais_port_var.get().isdigit():
                self._ais.ais_host = self.ais_host_var.get(), int(self.ais_port_var.get())
            self._ais.save_conf_to_file()
            if self._ais.ais_active:
                self._ais.login()
            PORT_HANDLER.init_aprs_ais()

    def _on_ok_button(self):
        self._set_vars()
        self._destroy_win()

    def _on_cancel_button(self):
        # Cancel button click handler
        self._destroy_win()

    def _destroy_win(self):
        self._root_cl.settings_win = None
        self.destroy()

    def tasker(self):
        pass
