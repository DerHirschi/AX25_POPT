# gui/UserDB/guiRightLevelEditor.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from UserDB.UserDBmain import USER_DB
from cfg.constant import COLOR_MAP
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cli.cli_const import CLI_DEF_CMD_ALL
from fnc.str_fnc import get_strTab
from prp.prp_const import PRP_FNC_TAB


class RightLevelEditor(tk.Toplevel):
    """
    Toplevel-Fenster zum Bearbeiten der globalen Rechte-Level und glb_rights
    """

    def __init__(self, parent):
        super().__init__(parent.main_win)

        self._root_win  = parent
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

        parent.right_level_win = self

        win_width  = 1000
        win_height = 700
        self.style = parent.style
        self.style_name = parent.style_name
        self.title(self._getTabStr("right_level_editor_title"))
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        fg, self._bg = COLOR_MAP.get(self.style_name, ('#000000', '#d9d9d9'))

        # Funktionen
        #self._functions_tab = PRP_FNC_TAB
        #self._functions = CLI_DEF_CMD_ALL + list(self._functions_tab.keys())
        self._functions_tab = dict(PRP_FNC_TAB)  # Kopie machen!
        self._functions     = sorted(list(list(CLI_DEF_CMD_ALL) + list(PRP_FNC_TAB.keys())))

        # Level und Vars
        self._levels = dict(POPT_CFG.right_level_tab)
        self._no_login_vars = {}
        self._with_login_vars = {}

        # Globale Rechte laden
        self._glb_rights = dict(POPT_CFG.global_rights)

        self._create_widgets()
        self._load_all_levels()
        self._load_glb_rights()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # === Globale PRP-Rechte (oben) ===
        glb_frame = ttk.LabelFrame(main_frame, text=self._getTabStr('glb_rights_txt'))
        glb_frame.pack(fill="x", pady=(0, 15))

        grid = ttk.Frame(glb_frame)
        grid.pack(padx=10, pady=10, anchor="w")

        # Default Level
        ttk.Label(grid, text=self._getTabStr('new_user_std_level')).grid(row=0, column=0, sticky="w", pady=5)
        self._default_level_var = tk.StringVar(value=self._glb_rights.get('default_level', 'basic'))
        self._default_level_combo = ttk.Combobox(grid, textvariable=self._default_level_var, state="readonly", width=20)
        self._default_level_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        self._default_level_combo.bind("<<ComboboxSelected>>", lambda e: self._save_glb_rights())

        # Remote Zugriff erlaubt
        self._remote_allowed_var = tk.BooleanVar(value=self._glb_rights.get('remote_access_allowed', True))
        ttk.Checkbutton(grid, text=self._getTabStr('allow_remote_access'),
                        variable=self._remote_allowed_var,
                        command=self._save_glb_rights).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        # Erweiterte Rechte nur mit Login
        self._login_required_var = tk.BooleanVar(value=self._glb_rights.get('login_required_for_extended', True))
        ttk.Checkbutton(grid, text=self._getTabStr('allow_remote_access'),
                        variable=self._login_required_var,
                        command=self._save_glb_rights).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # Globale Blockliste
        #ttk.Label(grid, text="Globale Blockliste (Calls, kommagetrennt):").grid(row=3, column=0, sticky="w", pady=(15,5))
        #self.block_list_var = tk.StringVar(value=", ".join(self._glb_rights.get('block_list', [])))
        #block_entry = ttk.Entry(grid, textvariable=self.block_list_var, width=60)
        #block_entry.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        #block_entry.bind("<KeyRelease>", lambda e: self._save_glb_rights_delayed())

        grid.columnconfigure(1, weight=1)

        # === Level verwalten ===
        manage_frame = ttk.LabelFrame(main_frame, text=self._getTabStr('edit_rights'))
        manage_frame.pack(fill="x", pady=(0, 10))

        btn_frame = ttk.Frame(manage_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(btn_frame, text=self._getTabStr('new_level'), command=self._add_new_level).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=self._getTabStr('rename_level'), command=self._rename_level).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=self._getTabStr('delete_level'), command=self._delete_level, style="Danger.TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text=self._getTabStr('close'), command=lambda :self.close()).pack(side="right", padx=5)

        # Haupt-Notebook für die Level
        self._level_notebook = ttk.Notebook(main_frame)
        self._level_notebook.pack(fill="both", expand=True)

        # Style für Lösch-Button
        style = ttk.Style()
        style.configure("Danger.TButton", foreground="red")

    def _load_glb_rights(self):
        """Lädt die globalen Rechte in die GUI"""
        self._glb_rights = dict(POPT_CFG.global_rights)
        self._default_level_var.set(self._glb_rights.get('default_level', 'basic'))
        self._remote_allowed_var.set(self._glb_rights.get('remote_access_allowed', True))
        self._login_required_var.set(self._glb_rights.get('login_required_for_extended', True))
        #self.block_list_var.set(", ".join(self._glb_rights.get('block_list', [])))

        # Combobox mit aktuellen Leveln füllen
        self._default_level_combo['values'] = list(self._levels.keys())

    def _save_glb_rights(self):
        """Speichert globale Rechte sofort"""

        new_glb = {
            'default_level': self._default_level_var.get(),
            'remote_access_allowed': self._remote_allowed_var.get(),
            'login_required_for_extended': self._login_required_var.get(),
            'block_list': [],
        }

        POPT_CFG.set_global_rights(new_glb)

    """
    def _save_glb_rights_delayed(self):
        # Für das Textfeld – verzögertes Speichern beim Tippen
        self.after(800, self._save_glb_rights)  # 800ms nach letztem Tastendruck
    """

    # --- Rest wie zuvor, nur Scroll-Logik verbessert ---

    def _load_all_levels(self):
        for tab in self._level_notebook.winfo_children():
            tab.destroy()

        self._no_login_vars.clear()
        self._with_login_vars.clear()

        # Combobox aktualisieren
        self._default_level_combo['values'] = list(self._levels.keys())

        for level_name in self._levels.keys():
            self._create_level_tab(level_name)

    def _create_level_tab(self, level_name: str):
        level_frame = ttk.Frame(self._level_notebook)
        self._level_notebook.add(level_frame, text=level_name)

        inner_notebook = ttk.Notebook(level_frame)
        inner_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        tab_no = ttk.Frame(inner_notebook)
        inner_notebook.add(tab_no, text=self._getTabStr('without_login'))

        tab_with = ttk.Frame(inner_notebook)
        inner_notebook.add(tab_with, text=self._getTabStr('with_login'))

        self._create_rights_grid(tab_no, level_name, is_no_login=True)
        self._create_rights_grid(tab_with, level_name, is_no_login=False)

    def _create_rights_grid(self, parent: ttk.Frame, level_name: str, is_no_login: bool):
        canvas = tk.Canvas(parent, bg=self._bg, background=self._bg,
                           relief="flat", highlightthickness=0)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        canvas.configure(xscrollcommand=scrollbar_x.set)

        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        if level_name not in self._no_login_vars:
            self._no_login_vars[level_name] = {}
            self._with_login_vars[level_name] = {}

        vars_dict = self._no_login_vars[level_name] if is_no_login else self._with_login_vars[level_name]

        row = 0
        col = 0
        max_rows = 9

        level_cfg = self._levels.get(level_name, {'no_login': [], 'with_login': []})
        allowed_no = set(level_cfg.get('no_login', []))
        allowed_with = set(level_cfg.get('with_login', []))

        for func in self._functions:
            var = tk.BooleanVar()
            text = self._get_function_name(func)
            cb = ttk.Checkbutton(inner_frame, text=text, variable=var)

            if is_no_login:
                cb.configure(command=lambda f=func, l=level_name: self._update_dependency(l, f))
                var.set(func in allowed_no)
                vars_dict[func] = var
            else:
                var.set(func in allowed_with)
                if func in allowed_no:
                    cb.config(state="disabled")
                vars_dict[func] = (var, cb)

            cb.grid(row=row, column=col, sticky="w", padx=15, pady=4)
            row += 1
            if row > max_rows:
                row = 0
                col += 1

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        inner_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

        # Horizontales Mausrad-Scrolling (nur wenn Maus über Canvas oder inner_frame)
        def _on_mousewheel(event):
            if event.widget.winfo_containing(event.x_root, event.y_root) in [canvas, inner_frame]:
                canvas.xview_scroll(-1 * int(event.delta / 120), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        inner_frame.bind("<MouseWheel>", _on_mousewheel)

        # Linux
        canvas.bind("<Button-4>", lambda e: canvas.xview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.xview_scroll(1, "units"))
        inner_frame.bind("<Button-4>", lambda e: canvas.xview_scroll(-1, "units"))
        inner_frame.bind("<Button-5>", lambda e: canvas.xview_scroll(1, "units"))

    def _update_dependency(self, level_name: str, func: str):
        no_var = self._no_login_vars[level_name].get(func)
        if no_var is None:
            return

        with_entry = self._with_login_vars[level_name].get(func)
        if with_entry:
            with_var, with_cb = with_entry
            if no_var.get():
                with_cb.config(state="disabled")
                with_var.set(False)
            else:
                with_cb.config(state="normal")

        self._save_level(level_name)

    def _get_function_name(self, func_key: str):
        return self._functions_tab.get(func_key, func_key)

    def _save_level(self, level_name: str):
        no_login = [f for f, var in self._no_login_vars[level_name].items() if var.get()]
        with_login = [f for f, (var, _) in self._with_login_vars[level_name].items() if var.get()]

        self._levels[level_name] = {'no_login': no_login, 'with_login': with_login}
        POPT_CFG.set_right_level_tab(self._levels)

        # Default-Level-Combobox aktualisieren
        if level_name not in self._default_level_combo['values']:
            values = list(self._default_level_combo['values']) + [level_name]
            self._default_level_combo['values'] = values

    # --- Level-Management-Methoden bleiben gleich ---
    def _add_new_level(self):
        name = simpledialog.askstring(self._getTabStr('new_level'), self._getTabStr('new_level_name'), parent=self)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self._levels:
            messagebox.showwarning(self._getTabStr('already_exists'), self._getTabStr('new_level_name').format(name))
            return

        self._levels[name] = {'no_login': [], 'with_login': []}
        self._create_level_tab(name)
        self._level_notebook.select(self._level_notebook.tabs()[-1])
        self._save_level(name)

    def _rename_level(self):
        current_tab_id = self._level_notebook.select()
        if not current_tab_id:
            return
        current_name = self._level_notebook.tab(current_tab_id, "text")

        new_name = simpledialog.askstring(self._getTabStr('rename_level'), f"{self._getTabStr('new_name')}:", initialvalue=current_name, parent=self)
        if not new_name or not new_name.strip():
            return
        new_name = new_name.strip()
        if new_name in self._levels and new_name != current_name:
            messagebox.showwarning(self._getTabStr('already_exists'), self._getTabStr('new_level_name').format(new_name))
            return

        # == Level Namen in allen UserDB Einträgen ändern
        USER_DB.rename_right_level(old_level_name=current_name, new_level_name=new_name)

        self._levels[new_name]          = self._levels.pop(current_name)
        self._no_login_vars[new_name]   = self._no_login_vars.pop(current_name)
        self._with_login_vars[new_name] = self._with_login_vars.pop(current_name)

        self._level_notebook.tab(current_tab_id, text=new_name)
        POPT_CFG.set_right_level_tab(self._levels)
        # Default-Combo aktualisieren
        self._default_level_combo['values'] = list(self._levels.keys())

    def _delete_level(self):
        current_tab_id = self._level_notebook.select()
        if not current_tab_id:
            return
        level_name = self._level_notebook.tab(current_tab_id, "text")

        if level_name == self._default_level_var.get():
            messagebox.showerror(self._getTabStr('error'), self._getTabStr('error_delete_standard_level'))
            return

        if messagebox.askyesno(self._getTabStr('delete_level'), self._getTabStr('ask_delete_level').format(level_name), parent=self):
            self._level_notebook.forget(current_tab_id)
            self._levels.pop(level_name, None)
            self._no_login_vars.pop(level_name, None)
            self._with_login_vars.pop(level_name, None)

            POPT_CFG.set_right_level_tab(self._levels)
            self._default_level_combo['values'] = list(self._levels.keys())

    def destroy_win(self):
        self._root_win.right_level_win = None
        self.destroy()

    def close(self):
        self.destroy_win()