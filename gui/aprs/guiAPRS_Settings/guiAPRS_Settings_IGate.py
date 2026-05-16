import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.str_fnc import get_strTab


class APRSigateSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style = root_win.style
        self.style_name = root_win.style_name
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

        ###################################
        # CFG laden
        self._igate_cfg: dict = POPT_CFG.get_CFG_aprs_igate()

        ###################################
        # GUI Variablen
        self._igate_active_var = tk.BooleanVar(self, value=self._igate_cfg.get('igate_active', False))
        self._igate_rf_to_is_var = tk.BooleanVar(self, value=self._igate_cfg.get('igate_rf_to_is', True))
        self._igate_is_to_rf_var = tk.BooleanVar(self, value=self._igate_cfg.get('igate_is_to_rf', False))
        self._igate_max_distance_var = tk.IntVar(self, value=self._igate_cfg.get('igate_max_distance', 80))
        self._igate_local_time_var = tk.IntVar(self, value=self._igate_cfg.get('igate_local_time', 45))

        # NEU: Duplikat-Filter Timer (in Sekunden)
        self._igate_dup_time_var = tk.IntVar(self, value=self._igate_cfg.get('igate_dup_time', 30))

        # Ports
        all_ports = list(POPT_CFG.get_port_CFGs().keys())
        self._igate_ports = all_ports

        self._igate_port_vars = {}
        saved_ports = self._igate_cfg.get('igate_ports', [])
        for port_id in self._igate_ports:
            active = str(port_id) in [str(p) for p in saved_ports]
            self._igate_port_vars[str(port_id)] = tk.BooleanVar(self, value=active)

        ###################################
        # GUI aufbauen
        self._build_gui()

    def _build_gui(self):
        pad_x = 15
        pad_y = 12

        main_f = ttk.LabelFrame(self, text=self._getTabStr('igate_settings') or "I-Gate Einstellungen")
        main_f.pack(fill='both', expand=True, padx=10, pady=10)

        row = 0

        # Globaler Schalter
        ttk.Checkbutton(main_f,
                        text=self._getTabStr('igate_active') or "I-Gate aktivieren",
                        variable=self._igate_active_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x,
                                                              pady=pad_y)
        row += 1

        ttk.Separator(main_f, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=pad_x,
                                                        pady=8)
        row += 1

        # RF → IS
        ttk.Checkbutton(main_f,
                        text=self._getTabStr('igate_rf_to_is') or "RF → APRS-IS (Upload)",
                        variable=self._igate_rf_to_is_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x,
                                                                pady=pad_y)
        row += 1

        # IS → RF
        ttk.Checkbutton(main_f,
                        text=self._getTabStr('igate_is_to_rf') or "APRS-IS → RF (Downlink)",
                        variable=self._igate_is_to_rf_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x,
                                                                pady=pad_y)
        row += 1

        ttk.Separator(main_f, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=pad_x,
                                                        pady=8)
        row += 1

        # Maximale Entfernung
        f_dist = ttk.Frame(main_f)
        f_dist.grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        ttk.Label(f_dist, text=self._getTabStr('igate_max_distance') or "Maximale Entfernung (km):").pack(side='left')
        ttk.Spinbox(f_dist, from_=0, to=500, width=6, textvariable=self._igate_max_distance_var).pack(side='left',
                                                                                                      padx=8)
        ttk.Label(f_dist, text="km").pack(side='left')
        row += 1

        # Lokale Zeit
        f_time = ttk.Frame(main_f)
        f_time.grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        ttk.Label(f_time, text=self._getTabStr('igate_local_time') or "Station gilt als lokal für:").pack(side='left')
        ttk.Spinbox(f_time, from_=5, to=180, width=6, textvariable=self._igate_local_time_var).pack(side='left', padx=8)
        ttk.Label(f_time, text=self._getTabStr('minutes') or "Minuten").pack(side='left')
        row += 1

        # === NEU: Duplikat-Filter ===
        ttk.Separator(main_f, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=pad_x,
                                                        pady=8)
        row += 1

        f_dup = ttk.Frame(main_f)
        f_dup.grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)

        ttk.Label(f_dup, text=self._getTabStr('igate_dup_time') or "Duplikat-Filter Zeitfenster:").pack(side='left')
        spin = ttk.Spinbox(f_dup, from_=0, to=300, width=6, textvariable=self._igate_dup_time_var)
        spin.pack(side='left', padx=8)
        ttk.Label(f_dup, text=self._getTabStr('seconds') or "Sekunden").pack(side='left')

        row += 2

        # Ports
        ttk.Label(main_f, text=self._getTabStr('igate_ports') or "Aktiv auf folgenden Ports:").grid(
            row=row, column=0, sticky='nw', padx=pad_x, pady=(pad_y, 5))
        row += 1

        port_frame = ttk.Frame(main_f)
        port_frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x + 10, pady=5)

        col = 0
        for port_id, var in self._igate_port_vars.items():
            ttk.Checkbutton(port_frame, text=str(port_id), variable=var).grid(row=0, column=col, padx=12, pady=4,
                                                                              sticky='w')
            col += 1
            if col > 5:
                col = 0
                row += 1  # Umbruch
        row += 1

    # =============================================
    # Speichern
    # =============================================
    def save_config(self):
        """Wird vom APRSSettingsMain aufgerufen"""
        try:
            new_cfg = {
                'igate_active': bool(self._igate_active_var.get()),
                'igate_rf_to_is': bool(self._igate_rf_to_is_var.get()),
                'igate_is_to_rf': bool(self._igate_is_to_rf_var.get()),
                'igate_max_distance': int(self._igate_max_distance_var.get()),
                'igate_local_time': int(self._igate_local_time_var.get()),
                'igate_dup_time': int(self._igate_dup_time_var.get()),  # NEU
                'igate_ports': [port_id for port_id, var in self._igate_port_vars.items() if var.get()]
            }

            POPT_CFG.set_CFG_aprs_igate(new_cfg)
            return True

        except Exception as ex:
            logger.error(f"Fehler beim Speichern der I-Gate Config: {ex}")
            return False

    def destroy_win(self):
        self.destroy()