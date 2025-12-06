""" Opt by Grok AI """
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor

from cfg.cfg_fnc import exist_awthemes_path
from cfg.constant import LANG_IND, LANGUAGE, STYLES_AWTHEMES, STYLES_BULD_IN_LINUX, STYLES_BULD_IN_WIN
from cfg.popt_config import POPT_CFG
from fnc.os_fnc import is_linux
from fnc.str_fnc import get_strTab


class GeneralSettings(ttk.Frame):
    def __init__(self, tabctl, root_win=None):
        super().__init__(tabctl)
        self._root_win = root_win
        self._getTabStr = lambda key: get_strTab(key, POPT_CFG.get_guiCFG_language())
        self._lang = POPT_CFG.get_guiCFG_language()

        conf = POPT_CFG.load_guiPARM_main()
        self._fg_rx = conf.get('gui_cfg_vor_col', 'white')
        self._fg_tx = conf.get('gui_cfg_vor_tx_col', '#25db04')
        self._bg_tx = conf.get('gui_cfg_vor_bg_col', 'black')

        self._build_ui(conf)

    def _build_ui(self, conf):
        # Hauptcontainer mit Padding
        main_container = ttk.Frame(self, padding="20 15")
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        # ==================== 1. Sprache & Standort ====================
        loc_lang_frame = ttk.LabelFrame(main_container, text=self._getTabStr("language") + " & QTH", padding="15 10")
        #loc_lang_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        loc_lang_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Sprache
        ttk.Label(loc_lang_frame, text=self._getTabStr("language") + ":").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self._lang_var = tk.StringVar(value=[k for k, v in LANG_IND.items() if v == self._lang][0])
        lang_menu = ttk.OptionMenu(loc_lang_frame, self._lang_var, self._lang_var.get(), *LANG_IND.keys())
        lang_menu.grid(row=0, column=1, sticky="w")

        # QTH
        ttk.Label(loc_lang_frame, text="QTH:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(8, 0))
        self._qth_var = tk.StringVar(value=conf.get('gui_cfg_qth', ''))
        ttk.Entry(loc_lang_frame, textvariable=self._qth_var, width=30).grid(row=1, column=1, sticky="w", pady=(8, 0))

        # Locator
        ttk.Label(loc_lang_frame, text="Locator:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(8, 0))
        self._loc_var = tk.StringVar(value=POPT_CFG.get_guiCFG_locator())
        ttk.Entry(loc_lang_frame, textvariable=self._loc_var, width=15).grid(row=2, column=1, sticky="w", pady=(8, 0))

        # ==================== RECHTS: Logging-Einstellungen ====================
        """
        log_conf = POPT_CFG.get_log_CFG()
        
        log_frame = ttk.LabelFrame(main_container, text=" Logging & Debug", padding="15 3")
        log_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))

        # Log-Level (Hauptlog)
        ttk.Label(log_frame, text="Log-Level:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self._log_level_var = tk.StringVar(value=log_conf.get('log_level', 'INFO'))
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        ttk.OptionMenu(log_frame, self._log_level_var, self._log_level_var.get(), *log_levels).grid(row=0, column=1,
                                                                                                    sticky="w")

        # BBS Log-Level (separat, falls vorhanden)
        ttk.Label(log_frame, text="BBS Log-Level:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self._bbs_log_level_var = tk.StringVar(value=log_conf.get('bbs_log_level', 'WARNING'))
        ttk.OptionMenu(log_frame, self._bbs_log_level_var, self._bbs_log_level_var.get(), *log_levels).grid(row=1,
                                                                                                            column=1,
                                                                                                            sticky="w",
                                                                                                            pady=(10,
                                                                                                                  0))

        # Log in Konsole ausgeben
        self._console_log_var = tk.BooleanVar(value=log_conf.get('log_to_console', True))
        ttk.Checkbutton(log_frame,
                        text=self._getTabStr('consol_log'),
                        variable=self._console_log_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=(15, 0))
        
        """
        # ==================== 2. Fensteranordnung & Style ====================
        layout_style_frame = ttk.LabelFrame(main_container, text="Layout & Design", padding="15 10")
        layout_style_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Textfenster-Reihenfolge
        ttk.Label(layout_style_frame, text=self._getTabStr('text_winPos') + ":").grid(row=0, column=0, sticky="w", padx=(0, 10))
        winPos_cfg = conf.get('gui_cfg_txtWin_pos', (0, 1, 2))
        self._winPos_tab = {
            (0, 1, 2): 'TX → QSO → Monitor',
            (1, 0, 2): 'QSO → TX → Monitor',
            (1, 2, 0): 'Monitor → TX → QSO',
            (2, 1, 0): 'Monitor → QSO → TX',
        }
        current_text = self._winPos_tab.get(winPos_cfg, 'TX → QSO → Monitor')
        self._text_winPos_var = tk.StringVar(value=current_text)
        pos_menu = ttk.OptionMenu(layout_style_frame, self._text_winPos_var, current_text, *self._winPos_tab.values())
        pos_menu.grid(row=0, column=1, sticky="w")

        # Style Auswahl
        ttk.Label(layout_style_frame, text="Theme/Style:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(8, 0))
        self._style_var = tk.StringVar(value=conf.get('gui_parm_style_name', 'default'))
        styles = STYLES_BULD_IN_LINUX if is_linux() else STYLES_BULD_IN_WIN
        if exist_awthemes_path():
            styles += STYLES_AWTHEMES
        style_menu = ttk.OptionMenu(layout_style_frame, self._style_var, self._style_var.get(), *styles)
        style_menu.grid(row=1, column=1, sticky="w", pady=(8, 0))

        # ==================== 3. Farben Vorschau (PreWrite-Fenster) ====================
        color_frame = ttk.LabelFrame(main_container, text=f"TX/RX-{self._getTabStr('text_color')} {self._getTabStr('prewritewin')}", padding="15 10")
        color_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Vorschau-Textfeld
        self._color_example_text = tk.Text(
            color_frame,
            height=6,
            width=50,
            font=('Courier New', 11, 'bold'),
            background=self._bg_tx,
            foreground=self._fg_tx,
            relief="flat",
            padx=10,
            pady=8,
            spacing1=4,
            spacing3=4
        )
        self._color_example_text.pack(pady=(0, 10), fill=tk.X)

        # Beispieltext einfügen
        self._update_preview_text()

        # Farbauswahl-Buttons
        btn_frame = ttk.Frame(color_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text=f"TX-{self._getTabStr('text_color')}", command=lambda: self._choose_color('tx_fg')).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text=f"RX-{self._getTabStr('text_color')}", command=lambda: self._choose_color('rx_fg')).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text=self._getTabStr('backgrund'), command=lambda: self._choose_color('tx_bg')).pack(side=tk.LEFT, padx=8)

    def _update_preview_text(self):
        self._color_example_text.delete("1.0", tk.END)
        self._color_example_text.tag_config('sendet', foreground=self._fg_tx, background=self._bg_tx)
        self._color_example_text.tag_config('prewrite', foreground=self._fg_rx, background=self._bg_tx)

        text1 = "► DE DL1ABC PQ23 599 599\n"
        text2 = "DL1ABC DE PQ23 599 599 KN\n"

        self._color_example_text.insert(tk.END, text1, 'sendet')
        self._color_example_text.insert(tk.END, text2, 'prewrite')
        self._color_example_text.configure(background=self._bg_tx)

    def _choose_color(self, mode: str):
        current = {'tx_fg': self._fg_tx, 'rx_fg': self._fg_rx, 'tx_bg': self._bg_tx}[mode]
        result = askcolor(current, title="Farbe wählen", parent=self._root_win)
        if not result or result[1] is None:
            return

        new_color = result[1]
        if mode == 'tx_fg':
            self._fg_tx = new_color
        elif mode == 'rx_fg':
            self._fg_rx = new_color
        elif mode == 'tx_bg':
            self._bg_tx = new_color

        self._update_preview_text()

    def save_config(self):
        conf = POPT_CFG.load_guiPARM_main()
        old_conf = dict(conf)

        # Sprache
        conf['gui_lang'] = int(LANG_IND.get(self._lang_var.get(), LANGUAGE))

        # QTH & Locator
        conf['gui_cfg_qth'] = self._qth_var.get().strip()
        conf['gui_cfg_locator'] = self._loc_var.get().strip().upper()

        # Style
        conf['gui_parm_style_name'] = self._style_var.get()

        # Fensterreihenfolge
        selected_text = self._text_winPos_var.get()
        for key, text in self._winPos_tab.items():
            if text == selected_text:
                conf['gui_cfg_txtWin_pos'] = key
                break

        # Farben
        conf['gui_cfg_vor_col'] = self._fg_rx
        conf['gui_cfg_vor_tx_col'] = self._fg_tx
        conf['gui_cfg_vor_bg_col'] = self._bg_tx
        """
        log_conf = POPT_CFG.get_log_CFG()
        log_conf['bbs_log_level']   = self._bbs_log_level_var.get()
        log_conf['log_level']       = self._log_level_var.get()
        log_conf['log_to_console']  = self._console_log_var.get()
        POPT_CFG.set_log_CFG(log_conf)
        """

        POPT_CFG.set_guiPARM_main(conf)
        return old_conf != conf