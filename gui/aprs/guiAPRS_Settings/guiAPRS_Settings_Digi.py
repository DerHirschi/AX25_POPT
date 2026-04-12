import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.str_fnc import get_strTab


class APRSdigiSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style            = root_win.style
        self.style_name       = root_win.style_name
        self._root_win        = root_win
        self._getTabStr       = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

        ###################################
        # CFG laden
        self._digi_cfg: dict = POPT_CFG.get_CFG_aprs_digi() or {}

        ###################################
        # GUI Variablen
        self._digi_active_var       = tk.BooleanVar(self, value=self._digi_cfg.get('digi_active', True))
        self._digi_fillin_var       = tk.BooleanVar(self, value=self._digi_cfg.get('digi_fillin', True))
        self._digi_trace_active_var = tk.BooleanVar(self, value=self._digi_cfg.get('digi_trace_active', True))
        self._digi_trace_all_var    = tk.BooleanVar(self, value=self._digi_cfg.get('digi_trace_all', False))
        self._digi_dup_time_var     = tk.IntVar(self,     value=self._digi_cfg.get('digi_dup_time', 30))

        # Mycall (nur Anzeige, da es aus AIS-CFG kommt)
        ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        self._mycall = ais_cfg.get('ais_call', 'NOCALL').upper()

        all_ports = list(POPT_CFG.get_port_CFGs().keys())
        self._digi_ports = all_ports

        self._digi_port_vars = {}
        saved_ports = self._digi_cfg.get('digi_ports', [])
        for port_id in self._digi_ports:
            active = str(port_id) in [str(p) for p in saved_ports]
            self._digi_port_vars[str(port_id)] = tk.BooleanVar(self, value=active)

        ###################################
        # GUI aufbauen
        self._build_gui()

    def _build_gui(self):
        pad_x = 15
        pad_y = 12

        main_f = ttk.LabelFrame(self, text=self._getTabStr('digi_settings'))
        main_f.pack(fill='both', expand=True, padx=10, pady=10)

        row = 0

        # --- Digipeater aktiv ---
        ttk.Checkbutton(main_f,
                        text=self._getTabStr('digi_active'),
                        variable=self._digi_active_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        row += 1

        ttk.Separator(main_f, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=pad_x, pady=8)
        row += 1

        # --- Fill-In Digi (WIDE1-1 only) ---
        ttk.Checkbutton(main_f,
                        text=self._getTabStr('digi_fillin'),
                        variable=self._digi_fillin_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        row += 1

        # --- TRACE aktiv ---
        ttk.Checkbutton(main_f,
                        text=self._getTabStr('digi_trace_active'),
                        variable=self._digi_trace_active_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        row += 1

        # --- TRACE auch für WIDE2+ ---
        ttk.Checkbutton(main_f,
                        text=self._getTabStr('digi_trace_all'),
                        variable=self._digi_trace_all_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        row += 1

        ttk.Separator(main_f, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', padx=pad_x, pady=8)
        row += 1

        # --- Duplikat-Filter Zeit ---
        f_dup = ttk.Frame(main_f)
        f_dup.grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        ttk.Label(f_dup, text=self._getTabStr('digi_dup_time')).pack(side='left')
        ttk.Spinbox(f_dup, from_=5, to=300, width=6, textvariable=self._digi_dup_time_var).pack(side='left', padx=8)
        ttk.Label(f_dup, text=self._getTabStr('seconds') or "Sekunden").pack(side='left')
        row += 1

        # Hinweis zum Duplikat-Filter
        """
        ttk.Label(main_f,
                  text="(Zeitraum, in dem identische Pakete als Duplikat erkannt und nicht gedigipeatet werden)",
                  foreground="gray", justify='left').grid(
            row=row, column=0, columnspan=2, sticky='w', padx=pad_x + 20, pady=(2, 12))
        
        row += 1
        """
        # Ports, auf denen der Digipeater aktiv sein soll ===
        ttk.Label(main_f, text=self._getTabStr('digi_ports') or "Digipeater aktiv auf folgenden Ports:").grid(
            row=row, column=0, sticky='nw', padx=pad_x, pady=(pad_y, 5))
        row += 1

        port_frame = ttk.Frame(main_f)
        port_frame.grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x + 10, pady=5)

        col = 0
        for port_id, var in self._digi_port_vars.items():
            ttk.Checkbutton(port_frame, text=str(port_id), variable=var).grid(
                row=0, column=col, padx=12, pady=4, sticky='w')
            col += 1
            if col > 5:  # maximal 6 pro Zeile
                col = 0
                row += 1  # neue Zeile
        row += 1

        # --- Mycall Anzeige (nur Info) ---
        f_call = ttk.Frame(main_f)
        f_call.grid(row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=pad_y)
        ttk.Label(f_call, text="Digipeater Call:").pack(side='left')
        ttk.Label(f_call, text=self._mycall, font=("TkDefaultFont", 10, "bold")).pack(side='left', padx=8)
        row += 1

        # Hinweis-Text unten
        hint = self._getTabStr('digi_hint')
        ttk.Label(main_f, text=hint, foreground="gray", justify='left').grid(
            row=row, column=0, columnspan=2, sticky='w', padx=pad_x, pady=(15, 10))


    # =============================================
    # Speichern
    # =============================================
    def save_config(self):
        """Wird vom APRSSettingsMain aufgerufen"""
        try:
            new_cfg = {
                'digi_active':        bool(self._digi_active_var.get()),
                'digi_fillin':        bool(self._digi_fillin_var.get()),
                'digi_trace_active':  bool(self._digi_trace_active_var.get()),
                'digi_trace_all':     bool(self._digi_trace_all_var.get()),
                'digi_dup_time':      int(self._digi_dup_time_var.get()),
                'digi_ports':         [port_id for port_id, var in self._digi_port_vars.items() if var.get()]
            }

            POPT_CFG.set_CFG_aprs_digi(new_cfg)
            logger.info("APRS Digipeater Config gespeichert")
            return True

        except Exception as ex:
            logger.error(f"Fehler beim Speichern der Digipeater Config: {ex}")
            return False

    def destroy_win(self):
        self.destroy()