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
        ttk.Frame.__init__(self, tabctl)
        ################################
        self._root_win = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._lang = POPT_CFG.get_guiCFG_language()
        conf: dict = POPT_CFG.load_guiPARM_main()
        self._fg_rx = conf.get('gui_cfg_vor_col', 'white')
        self._fg_tx = conf.get('gui_cfg_vor_tx_col', '#25db04')
        self._bg_tx = conf.get('gui_cfg_vor_bg_col', 'black')
        #####################
        frame1 = ttk.Frame(self)
        frame1.pack(fill=tk.BOTH, expand=True)
        ############################################################
        h_frame1_l =ttk.Frame(frame1)
        h_frame1_l.pack(expand=True)
        h_frame2_l =ttk.Frame(frame1)
        h_frame2_l.pack(expand=True)
        ############################################################
        lang_frame =ttk.Frame(h_frame1_l)
        lang_frame.pack(side=tk.LEFT,  expand=True, padx=30)
        qth_loc_frame =ttk.Frame(h_frame1_l)
        qth_loc_frame.pack(side=tk.LEFT, expand=True, padx=30)
        ############################################################
        self._lang_var = tk.StringVar(self)
        for land, land_id in LANG_IND.items():
            if land_id == self._lang:
                self._lang_var.set(land)
        opt = list(LANG_IND.keys())
        ttk.Label(lang_frame, text=f'{self._getTabStr("language")}: ').pack(side=tk.LEFT)
        opt = [self._lang_var.get()] + opt
        lang_ent =ttk.OptionMenu(lang_frame,
                                 self._lang_var,
                                       *opt,
                                 )
        lang_ent.pack(side=tk.LEFT)
        ############################################################
        self._qth_var = tk.StringVar(self, value=conf.get('gui_cfg_qth', ''))
        qth_frame = ttk.Frame(qth_loc_frame)
        qth_frame.pack(fill=tk.X, pady=8)
        ttk.Label(qth_frame, text='QTH: ').pack(side=tk.LEFT)
        qth_ent = ttk.Entry(qth_frame, width=25, textvariable=self._qth_var)
        qth_ent.pack(side=tk.LEFT)
        ############################################################

        self._loc_var = tk.StringVar(self, value=conf.get('gui_cfg_locator', ''))
        loc_frame = ttk.Frame(qth_loc_frame)
        loc_frame.pack(fill=tk.X, pady=8)
        ttk.Label(loc_frame, text='Locator: ').pack(side=tk.LEFT)
        loc_ent = ttk.Entry(loc_frame, width=10, textvariable=self._loc_var)
        loc_ent.pack(side=tk.LEFT)
        ############################################################
        self._pacmanFix_var = tk.BooleanVar(self, value=conf.get('gui_cfg_pacman_fix', True))
        pacmanFix_frame = ttk.Frame(qth_loc_frame)
        pacmanFix_frame.pack(fill=tk.X, pady=8)
        # tk.Label(pacmanFix_frame, text='Pacman-FIX: ').pack(side=tk.LEFT)
        pacmanFix_ent = ttk.Checkbutton(pacmanFix_frame, text='Pacman-FIX', variable=self._pacmanFix_var)
        pacmanFix_ent.pack(side=tk.LEFT)
        ############################################################

        ############################################################
        text_winPos_f = ttk.Frame(h_frame2_l)
        text_winPos_f.pack(fill=tk.X, pady=8)
        ttk.Label(text_winPos_f, text=f"{self._getTabStr('text_winPos')}:").pack(side=tk.LEFT, padx=4)
        winPos_cfg =  conf.get('gui_cfg_txtWin_pos', (0, 1, 2))
        self._winPos_tab = {
            (0, 1, 2): 'TX/QSO/Monitor',    # tx/qso/mon
            (1, 0, 2): 'QSO/TX/Monitor',    # qso/tx/mon
            (1, 2, 0): 'Monitor/TX/QSO',    # mon/tx/qso
            (2, 1, 0): 'Monitor/QSO/TX',    # mon/qso/tx
            #(0, 2, 1): 'TX/Monitor/QSO',    # tx/mon/qso
            #(2, 0, 1): 'QSO/Monitor/TX',    # qso/mon/tx
        }
        self._text_winPos_var = tk.StringVar(self, value=self._winPos_tab.get(winPos_cfg, 'TX/QSO/Monitor'))
        cfg_opt = [self._text_winPos_var.get()]
        for k, txt_cfg in self._winPos_tab.items():
            cfg_opt.append(txt_cfg)
        text_winPos_ent = ttk.OptionMenu(text_winPos_f, self._text_winPos_var, *cfg_opt)
        text_winPos_ent.pack(side=tk.LEFT)

        ############################################################
        style_f = ttk.Frame(h_frame2_l)
        style_f.pack()
        ttk.Label(style_f, text="Style").pack(side=tk.LEFT, padx=3)
        self._style_var = tk.StringVar(self, value=conf.get('gui_parm_style_name', 'default'))
        if is_linux():
            opt = STYLES_BULD_IN_LINUX
        else:
            opt = STYLES_BULD_IN_WIN
        if exist_awthemes_path():
            opt += STYLES_AWTHEMES
        self._style_var.set(conf.get('gui_parm_style_name', 'default'))
        opt = [self._style_var.get()] + opt
        style_opt_men = ttk.OptionMenu(
            style_f,
            self._style_var,
            *opt
        )
        style_opt_men.pack(side=tk.LEFT)
        ############################################################
        vorsch_col_frame = ttk.Frame(h_frame2_l, )
        vorsch_col_frame.pack()
        ################
        ttk.Label(h_frame2_l, text=f"{get_strTab('prewritewin', self._lang)}:").pack(pady=15)

        self._color_example_text = tk.Text(h_frame2_l,
                                           height=5,
                                           width=40,
                                           font=('Courier', 11),
                                           background=self._bg_tx,
                                           relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                           highlightthickness=0,
                                           )

        self._color_example_text.pack()
        self._color_example_text.tag_config('sendet', foreground=self._fg_tx, background=self._bg_tx)
        self._color_example_text.tag_config('prewrite', foreground=self._fg_rx, background=self._bg_tx)
        self._color_example_text.insert(tk.END, 'TEST TEXT Test. 1234. 73... \n', )
        self._color_example_text.tag_add('sendet', 0.0, tk.INSERT)
        ind = str(self._color_example_text.index(tk.INSERT))
        self._color_example_text.insert(tk.END, 'TEST TEXT Test. 1234. 73... ', )
        self._color_example_text.tag_add('prewrite', ind, tk.END)
        fg_btn_frame = ttk.Frame(h_frame2_l)
        fg_btn_frame.pack()
        # FG
        ttk.Button(fg_btn_frame,
                  text='TX-Text',
                  command=lambda: self._choose_color('tx_fg')
                  ).pack(side=tk.LEFT, padx=10, pady=5)
        # FG
        ttk.Button(fg_btn_frame,
                  text='RX-Text',
                  command=lambda: self._choose_color('rx_fg')
                  ).pack(side=tk.LEFT, padx=10)
        # BG
        ttk.Button(h_frame2_l,
                  text='BG',
                  command=lambda: self._choose_color('tx_bg')
                  ).pack()


    def _choose_color(self, fg_bg: str):
        if fg_bg == 'tx_fg':
            col = askcolor(self._fg_tx,
                           title=get_strTab('text_color', self._lang), parent=self._root_win)
            if not col:
                return
            if col[1] is None:
                return
            self._fg_tx = str(col[1])
        elif fg_bg == 'tx_bg':
            col = askcolor(self._bg_tx,
                           title=get_strTab('text_color', self._lang), parent=self._root_win)
            if not col:
                return
            if col[1] is None:
                return
            self._bg_tx = str(col[1])
        elif fg_bg == 'rx_fg':
            col = askcolor(self._fg_rx,
                           title=get_strTab('text_color', self._lang), parent=self._root_win)
            if not col:
                return
            if col[1] is None:
                return
            self._fg_rx = str(col[1])
        self._color_example_text.tag_config('sendet', foreground=self._fg_tx, background=self._bg_tx)
        self._color_example_text.tag_config('prewrite', foreground=self._fg_rx, background=self._bg_tx)
        self._color_example_text.configure(background=self._bg_tx)

    def save_config(self):
        conf: dict = POPT_CFG.load_guiPARM_main()
        old_conf   = dict(conf)
        lang_ind   = LANG_IND.get(self._lang_var.get(), LANGUAGE)
        conf['gui_cfg_vor_col']         = str(self._fg_rx)
        conf['gui_cfg_vor_tx_col']      = str(self._fg_tx)
        conf['gui_cfg_vor_bg_col']      = str(self._bg_tx)
        conf['gui_lang']                = int(lang_ind)
        conf['gui_cfg_locator']         = str(self._loc_var.get())
        conf['gui_cfg_qth']             = str(self._qth_var.get())
        conf['gui_cfg_pacman_fix']      = bool(self._pacmanFix_var.get())
        conf['gui_parm_style_name']     = str(self._style_var.get())
        text_pos = self._text_winPos_var.get()
        for cfg_k, text_cfg in self._winPos_tab.items():
            if text_pos == text_cfg:
                conf['gui_cfg_txtWin_pos'] = cfg_k
                break
        POPT_CFG.set_guiPARM_main(conf)
        if old_conf == conf:
            return False
        return True
