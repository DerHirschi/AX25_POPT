import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.loc_fnc import coordinates_to_locator, locator_to_coordinates
from fnc.str_fnc import get_strTab

class APRSaisSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._ais_cfg: dict = self._root_win.get_aprs_cfg()
        ###################################
        # VAR's
        self._ais_call_var = tk.StringVar(self,  value=    self._ais_cfg.get('ais_call', ''))
        self._ais_pass_var = tk.StringVar(self,  value=    self._ais_cfg.get('ais_pass', ''))
        self._ais_host_var = tk.StringVar(self,  value=    self._ais_cfg.get('ais_host', ('cbaprs.dyndns.org', 27234))[0])
        self._ais_port_var = tk.StringVar(self,  value=str(self._ais_cfg.get('ais_host', ('cbaprs.dyndns.org', 27234))[1]))
        self._ais_loc_var  = tk.StringVar(self,  value=    self._ais_cfg.get('ais_loc', ''))
        self._ais_lat_var  = tk.StringVar(self,  value=str(self._ais_cfg.get('ais_lat', 0.0)))
        self._ais_lon_var  = tk.StringVar(self,  value=str(self._ais_cfg.get('ais_lon', 0.0)))
        self._ais_run_var  = tk.BooleanVar(self, value=    self._ais_cfg.get('ais_active', False))
        ###################################
        fram_l = ttk.Frame(self)
        fram_r = ttk.Frame(self)
        fram_l.pack(side='left', fill='both', expand=True, padx=15, pady=15)
        fram_r.pack(side='left', fill='both', expand=True, padx=15, pady=15)
        ###################################
        # fram_l
        call_f = ttk.Frame(fram_l)
        call_f.pack(anchor='w', pady=5)
        call_f.grid_columnconfigure(0, minsize=120)
        call_f.grid_columnconfigure(1, minsize=100)

        ttk.Label(call_f, text='Call: ').grid(row=0, column=0, sticky='w')
        ttk.Entry(call_f, textvariable=self._ais_call_var, width=10).grid(row=0, column=1, sticky='w')
        #######
        pass_f = ttk.Frame(fram_l)
        pass_f.pack(anchor='w', pady=5)
        pass_f.grid_columnconfigure(0, minsize=120)
        pass_f.grid_columnconfigure(1, minsize=100)

        ttk.Label(pass_f, text=f"{self._getTabStr('password')}: ").grid(row=0, column=0, sticky='w')
        ttk.Entry(pass_f, textvariable=self._ais_pass_var, width=10).grid(row=0, column=1, sticky='w')
        #######
        host_f = ttk.Frame(fram_l)
        host_f.pack(anchor='w', pady=5)
        host_f.grid_columnconfigure(0, minsize=120)
        host_f.grid_columnconfigure(1, minsize=100)

        ttk.Label(host_f, text=f"Server-{self._getTabStr('address')}: ").grid(row=0, column=0, sticky='w')
        ttk.Entry(host_f, textvariable=self._ais_host_var, width=25).grid(row=0, column=1, sticky='w')
        #######
        port_f = ttk.Frame(fram_l)
        port_f.pack(anchor='w', pady=5)
        port_f.grid_columnconfigure(0, minsize=120)
        port_f.grid_columnconfigure(1, minsize=100)

        ttk.Label(port_f, text=f"Server-{self._getTabStr('port')}: ").grid(row=0, column=0, sticky='w')
        ttk.Entry(port_f, textvariable=self._ais_port_var, width=10).grid(row=0, column=1, sticky='w')
        #######
        connect_f = ttk.Frame(fram_l)
        connect_f.pack(anchor='w', pady=5)

        ttk.Checkbutton(connect_f,
                        text=self._getTabStr('conn_2_aprs_server'),
                        variable=self._ais_run_var).pack(anchor='w')
        ###################################
        # fram_r
        loc_f = ttk.Frame(fram_r)
        loc_f.pack(anchor='w', pady=5)
        loc_f.grid_columnconfigure(0, minsize=120)
        loc_f.grid_columnconfigure(1, minsize=100)

        ttk.Label(loc_f, text="Locator: ").grid(row=0, column=0, sticky='w')
        ttk.Entry(loc_f, textvariable=self._ais_loc_var, width=10).grid(row=0, column=1, sticky='w')
        #######
        lat_f = ttk.Frame(fram_r)
        lat_f.pack(anchor='w', pady=5)
        lat_f.grid_columnconfigure(0, minsize=120)
        lat_f.grid_columnconfigure(1, minsize=100)

        ttk.Label(lat_f, text=f"Latitude: ").grid(row=0, column=0, sticky='w')
        ttk.Entry(lat_f, textvariable=self._ais_lat_var, width=10).grid(row=0, column=1, sticky='w')
        #######
        lon_f = ttk.Frame(fram_r)
        lon_f.pack(anchor='w', pady=5)
        lon_f.grid_columnconfigure(0, minsize=120)
        lon_f.grid_columnconfigure(1, minsize=100)

        ttk.Label(lon_f, text=f"Longitude: ").grid(row=0, column=0, sticky='w')
        ttk.Entry(lon_f, textvariable=self._ais_lon_var, width=10).grid(row=0, column=1, sticky='w')
        #######

    def save_config(self):
        try:
            lon = float(self._ais_lon_var.get())
        except ValueError:
            lon = 0
        try:
            lat = float(self._ais_lat_var.get())
        except ValueError:
            lat = 0
        loc = self._ais_loc_var.get()

        if not loc:
            if lat and lon:
                loc = coordinates_to_locator(
                    latitude=lat,
                    longitude=lon,
                )
                self._ais_loc_var.set(loc)
        if not lat or not lon:
            if loc:
                lat, lon = locator_to_coordinates(loc)
                self._ais_lat_var.set(str(lat))
                self._ais_lon_var.set(str(lon))
        aprs_cfg                = self._root_win.get_aprs_cfg()
        aprs_cfg['ais_call']    = self._ais_call_var.get()
        aprs_cfg['ais_pass']    = self._ais_pass_var.get()
        aprs_cfg['ais_loc']     = self._ais_loc_var.get()
        try:
            aprs_cfg['ais_lat'] = float(self._ais_lat_var.get())
        except ValueError:
            aprs_cfg['ais_lat'] = 0.0
        try:
            aprs_cfg['ais_lon'] = float(self._ais_lon_var.get())
        except ValueError:
            aprs_cfg['ais_lon'] = 0.0
        aprs_cfg['ais_active']  = self._ais_run_var.get()
        try:
            aprs_cfg['ais_host']    = self._ais_host_var.get(), int(self._ais_port_var.get())
        except ValueError:
            pass
