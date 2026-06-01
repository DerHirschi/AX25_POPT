# gui/UserDB/guiPRPRights.py
import tkinter as tk
from tkinter import ttk

from cfg.constant import COLOR_MAP
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cli.cli_const import CLI_DEF_CMD_ALL
from fnc.str_fnc import get_strTab
from prp.prp_const import PRP_FNC_TAB


class GUI_PRP_Rights(ttk.Frame):
    """
    Tab für PRP-Rechte im UserDB-Notebook.
    Benutzerfreundlich mit Checkboxes – kein JSON!
    - Vordefinierte Level (Dropdown)
    - Individuelle Funktionen (Checkboxes)
    - Zugangspasswort
    - Komplett sperren
    """

    def __init__(self, frame, user_db_gui):
        super().__init__(frame)
        self._user_db_gui = user_db_gui
        self.style_name = user_db_gui.style_name
        self._get_colorMap = lambda : COLOR_MAP.get(self.style_name, ('#000000',  '#d9d9d9'))
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

        self._functions_tab = dict(PRP_FNC_TAB)  # Kopie machen!
        self._functions     = sorted(list(set(CLI_DEF_CMD_ALL + list(PRP_FNC_TAB.keys()))))

        # Vordefinierte Levels aus Config
        self._levels = list(POPT_CFG.right_level_tab.keys())

        self._current_entry = None
        self._vars_wo = {}  # Für Checkboxes vars
        self._vars_w  = {}  # Für Checkboxes vars

        self._create_widgets()
        self._load_current()

    def _create_widgets(self):
        self._level_var   = tk.StringVar()
        self._blocked_var = tk.BooleanVar()
        self._pw_var      = tk.StringVar()
        self._show_pw_var = tk.BooleanVar()

        main_frame = ttk.LabelFrame(self, text=self._getTabStr('remote_rights'))
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === Rechte-Level ===
        level_frame = ttk.LabelFrame(main_frame, text=self._getTabStr('right_level'))
        level_frame.pack(fill="x", pady=5, padx=5)

        ttk.Label(level_frame, text="Level:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.level_combo = ttk.Combobox(level_frame, textvariable=self._level_var, values=self._levels, state="readonly",
                                        width=15)
        self.level_combo.grid(row=0, column=1, padx=10, pady=8)
        self.level_combo.bind("<<ComboboxSelected>>", self._apply_level)

        ttk.Checkbutton(level_frame, text=self._getTabStr('block_remote_access'),
                        variable=self._blocked_var).grid(row=0, column=2, sticky="w", padx=30, pady=8)

        # === Individuelle Rechte === (mit horizontaler Scrollbar)
        rights_frame = ttk.LabelFrame(main_frame, text=self._getTabStr('individual_rights'))
        rights_frame.pack(fill="both", expand=True, pady=5, padx=5)

        cmd_tab = ttk.Notebook(rights_frame)
        cmd_tab.pack(fill="both", expand=True, pady=5, padx=5)

        wo_login_f = ttk.Frame(cmd_tab)
        w_login_f  = ttk.Frame(cmd_tab)

        cmd_tab.add(wo_login_f, text=self._getTabStr('without_login'))
        cmd_tab.add(w_login_f, text=self._getTabStr('with_login'))
        #wo_login_f.pack(fill='both', expand=True)
        #w_login_f.pack(fill='both', expand=True)

        # Canvas + Scrollbar
        fg, bg = self._get_colorMap()

        # == wo_login
        canvas_wo = tk.Canvas(wo_login_f, height=10,
                           bg=bg,
                           background=bg,
                           relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                           highlightthickness=0,
                           )
        scrollbar = ttk.Scrollbar(wo_login_f, orient="horizontal", command=canvas_wo.xview)
        canvas_wo.configure(xscrollcommand=scrollbar.set)

        scrollbar.pack(side="bottom", fill="x")
        canvas_wo.pack(side="top", fill="both", expand=True)

        # Innerer Frame im Canvas (hier kommen die Checkboxes rein)
        scrollable_frame = ttk.Frame(canvas_wo)
        canvas_wo.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Grid für Checkboxes im scrollable_frame
        row = 0
        col = 0
        for func in self._functions:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(scrollable_frame,
                                 text=self._get_function_name(func),
                                 variable=var,
                                 command=lambda :self._on_cmd_select_wo())
            cb.grid(row=row, column=col, sticky="w", padx=15, pady=4)

            self._vars_wo[func] = var, cb


            row += 1
            if row > 4:  # Mehr Zeilen erlauben → mehr Spalten möglich
                row = 0
                col += 1

        # Wichtig: Scrollregion aktualisieren, wenn der Inhalt geladen wird
        scrollable_frame.update_idletasks()  # Sicherstellen, dass Größe berechnet wird
        canvas_wo.config(scrollregion=canvas_wo.bbox("all"))

        # Event binden: Wenn sich die Größe des inneren Frames ändert → Scrollregion neu setzen
        scrollable_frame.bind("<Configure>", lambda e: canvas_wo.configure(scrollregion=canvas_wo.bbox("all")))

        # Optional: Mausrad für horizontales Scrollen (unter Windows/Linux)
        # --- Mausrad horizontales Scrollen NUR wenn Maus über dem Canvas-Bereich ---
        def _on_horizontal_scroll(event):
            # Nur reagieren, wenn Maus über dem Canvas oder scrollable_frame ist
            if event.widget.winfo_containing(event.x_root, event.y_root) in [canvas_wo, scrollable_frame]:
                canvas_wo.xview_scroll(-1 * int(event.delta / 120), "units")

        def _on_linux_scroll_up(event):
            if event.widget.winfo_containing(event.x_root, event.y_root) in [canvas_wo, scrollable_frame]:
                canvas_wo.xview_scroll(-1, "units")

        def _on_linux_scroll_down(event):
            if event.widget.winfo_containing(event.x_root, event.y_root) in [canvas_wo, scrollable_frame]:
                canvas_wo.xview_scroll(1, "units")

        # Plattform-spezifische Bindings – nur lokal auf den Canvas!
        canvas_wo.bind("<MouseWheel>", _on_horizontal_scroll)  # Windows + macOS (vertikal → horizontal umleiten)
        canvas_wo.bind("<Button-4>", _on_linux_scroll_up)  # Linux Scroll up
        canvas_wo.bind("<Button-5>", _on_linux_scroll_down)  # Linux Scroll down

        # Zusätzlich: Falls macOS horizontales Scrollen mit Shift + Rad unterstützt
        canvas_wo.bind("<Shift-MouseWheel>", _on_horizontal_scroll)

        # Optional: Auch über dem scrollable_frame innen reagieren (falls Maus dort ist)
        scrollable_frame.bind("<MouseWheel>", _on_horizontal_scroll)
        scrollable_frame.bind("<Button-4>", _on_linux_scroll_up)
        scrollable_frame.bind("<Button-5>", _on_linux_scroll_down)


        # =========================================================================
        # == w_login
        canvas = tk.Canvas(w_login_f, height=10,
                              bg=bg,
                              background=bg,
                              relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                              highlightthickness=0,
                              )
        scrollbar_w = ttk.Scrollbar(w_login_f, orient="horizontal", command=canvas.xview)
        canvas.configure(xscrollcommand=scrollbar_w.set)

        scrollbar_w.pack(side="bottom", fill="x")
        canvas.pack(side="top", fill="both", expand=True)

        # Innerer Frame im Canvas (hier kommen die Checkboxes rein)
        scrollable_frame_w = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame_w, anchor="nw")

        # Grid für Checkboxes im scrollable_frame_w
        row = 0
        col = 0
        for func in self._functions:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(scrollable_frame_w,
                                 text=self._get_function_name(func),
                                 variable=var,
                                 command=lambda :self._on_cmd_select_w())
            cb.grid(row=row, column=col, sticky="w", padx=15, pady=4)
            self._vars_w[func] = var, cb

            row += 1
            if row > 4:  # Mehr Zeilen erlauben → mehr Spalten möglich
                row = 0
                col += 1

        # Wichtig: Scrollregion aktualisieren, wenn der Inhalt geladen wird
        scrollable_frame_w.update_idletasks()  # Sicherstellen, dass Größe berechnet wird
        canvas.config(scrollregion=canvas.bbox("all"))

        # Event binden: Wenn sich die Größe des inneren Frames ändert → Scrollregion neu setzen
        scrollable_frame_w.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Optional: Mausrad für horizontales Scrollen (unter Windows/Linux)
        # --- Mausrad horizontales Scrollen NUR wenn Maus über dem Canvas-Bereich ---
        def _on_horizontal_scroll(event):
            # Nur reagieren, wenn Maus über dem Canvas oder scrollable_frame_w ist
            if event.widget.winfo_containing(event.x_root, event.y_root) in [canvas, scrollable_frame_w]:
                canvas.xview_scroll(-1 * int(event.delta / 120), "units")

        def _on_linux_scroll_up(event):
            if event.widget.winfo_containing(event.x_root, event.y_root) in [canvas, scrollable_frame_w]:
                canvas.xview_scroll(-1, "units")

        def _on_linux_scroll_down(event):
            if event.widget.winfo_containing(event.x_root, event.y_root) in [canvas, scrollable_frame_w]:
                canvas.xview_scroll(1, "units")

        # Plattform-spezifische Bindings – nur lokal auf den Canvas!
        canvas.bind("<MouseWheel>", _on_horizontal_scroll)  # Windows + macOS (vertikal → horizontal umleiten)
        canvas.bind("<Button-4>", _on_linux_scroll_up)  # Linux Scroll up
        canvas.bind("<Button-5>", _on_linux_scroll_down)  # Linux Scroll down

        # Zusätzlich: Falls macOS horizontales Scrollen mit Shift + Rad unterstützt
        canvas.bind("<Shift-MouseWheel>", _on_horizontal_scroll)

        # Optional: Auch über dem scrollable_frame_w innen reagieren (falls Maus dort ist)
        scrollable_frame_w.bind("<MouseWheel>", _on_horizontal_scroll)
        scrollable_frame_w.bind("<Button-4>", _on_linux_scroll_up)
        scrollable_frame_w.bind("<Button-5>", _on_linux_scroll_down)

        # === Zugangspasswort ===
        pw_frame = ttk.LabelFrame(main_frame, text=self._getTabStr('password_for_prp_login'))
        pw_frame.pack(fill="x", pady=5, padx=5)

        ttk.Label(pw_frame, text="Passwort:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.pw_entry = ttk.Entry(pw_frame, textvariable=self._pw_var, show="*", width=30)
        self.pw_entry.grid(row=0, column=1, padx=10, pady=8)

        ttk.Checkbutton(pw_frame, text=self._getTabStr('show'), variable=self._show_pw_var,
                        command=self._toggle_pw).grid(row=0, column=2, padx=10)

    def _get_function_name(self, func_key):

        for cmd in CLI_DEF_CMD_ALL:
            if cmd not in self._functions_tab:
                self._functions_tab[cmd] = f"{cmd}"
        return self._functions_tab.get(func_key, func_key.replace('_', ' ').title())

    def _toggle_pw(self):
        show = "" if self._show_pw_var.get() else "*"
        self.pw_entry.config(show=show)

    def _apply_level(self, event=None):
        """Wendet vordefiniertes Level auf Checkboxes an"""
        level = self._level_var.get()
        if not level or level not in POPT_CFG.right_level_tab:
            return

        level_rights = POPT_CFG.right_level_tab[level]
        self._set_cmd_vars(level_rights)

    def _set_cmd_vars(self, rights: dict):
        # Custom-Rechte
        allowed_wo = set()
        allowed_w = set()

        allowed_wo.update(rights.get('no_login', []))
        allowed_w.update(rights.get('with_login', []))
        for func, var in self._vars_wo.items():
            if func in allowed_wo or 'all' in allowed_wo:
                var[0].set(True)
                var[1].configure(state='normal')
                self._vars_w[func][1].configure(state='disabled')
            else:
                var[0].set(False)
                self._vars_w[func][1].configure(state='normal')
                if func in allowed_w or 'all' in allowed_w:
                    self._vars_w[func][0].set(True)
                    var[1].configure(state='disabled')
                else:
                    self._vars_w[func][0].set(False)


    def _load_current(self):
        self._current_entry = self._user_db_gui.current_ent
        if not self._current_entry:
            self._level_var.set(self._levels[0] if self._levels else "")
            for var in self._vars_wo.values():
                var[1].configure(state='normal')
                var[0].set(False)
            for var in self._vars_w.values():
                var[1].configure(state='normal')
                var[0].set(False)
            self._pw_var.set("")
            self._blocked_var.set(False)
            return

        # Rechte aus DB laden (als dict mit 'no_login' / 'with_login')
        prp_rights = getattr(self._current_entry, 'rights', None)
        if isinstance(prp_rights, dict) and 'no_login' in prp_rights:
            # Custom-Rechte
            self._set_cmd_vars(prp_rights)
            self._level_var.set("Custom")
        else:
            # Predefined Level
            level = str(prp_rights) if prp_rights else POPT_CFG.global_rights.get('default_level', 'basic')
            self._level_var.set(level)
            self._apply_level()

        # Passwort
        auth_pw = getattr(self._current_entry, 'auth_password', None)
        self._pw_var.set(auth_pw or "")

        # Blocked
        self._blocked_var.set(getattr(self._current_entry, 'blocked', False))

    def save(self):
        if not self._current_entry:
            logger.warning("Kein User zum Speichern")
            return

        level = self._level_var.get()
        if level == "Custom":
            # Rechte als Dict speichern
            allowed_no_login   = []
            allowed_with_login = []

            for func, var in self._vars_wo.items():
                if var[0].get():

                    allowed_no_login.append(func)

            for func, var in self._vars_w.items():
                if var[0].get():
                    allowed_with_login.append(func)

            custom_rights = {
                'no_login':   list(set(allowed_no_login)),
                'with_login': list(set(allowed_with_login))
            }
            setattr(self._current_entry, 'rights', custom_rights)
        else:
            setattr(self._current_entry, 'rights', level)

        # Passwort
        pw = self._pw_var.get().strip()
        if pw:
            setattr(self._current_entry, 'auth_password', pw)
        else:
            setattr(self._current_entry, 'auth_password', None)

        # Blocked
        setattr(self._current_entry, 'blocked', self._blocked_var.get())

        #self._user_db.save_data()
        logger.info(f"PRP-Rechte für {self._current_entry.call_str} gespeichert")
        #self.user_db_gui._root_win.sysMsg_to_monitor(f"PRP-Rechte für {self.current_entry.call_str} gespeichert")

    def _on_cmd_select_w(self, event=None):
        if self._level_var.get() != "Custom":
            self._level_var.set("Custom")

        for func, var in self._vars_w.items():
            if var[0].get():
                self._vars_wo[func][0].set(False)
                self._vars_wo[func][1].configure(state='disabled')
            else:
                self._vars_wo[func][1].configure(state='normal')

    def _on_cmd_select_wo(self):
        if self._level_var.get() != "Custom":
            self._level_var.set("Custom")

        for func, var in self._vars_wo.items():
            if var[0].get():
                self._vars_w[func][0].set(False)
                self._vars_w[func][1].configure(state='disabled')
            else:
                self._vars_w[func][1].configure(state='normal')

    def on_entry_selected(self):
        self._load_current()