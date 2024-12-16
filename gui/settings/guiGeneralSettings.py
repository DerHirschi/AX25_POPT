import tkinter as tk
from tkinter.colorchooser import askcolor

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class GeneralSettings(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        ################################
        self._lang = POPT_CFG.get_guiCFG_language()
        conf: dict = POPT_CFG.load_guiPARM_main()
        self._fg_rx = conf.get('gui_cfg_vor_col', 'white')
        self._fg_tx = conf.get('gui_cfg_vor_tx_col', '#25db04')
        self._bg_tx = conf.get('gui_cfg_vor_bg_col', 'black')
        #####################
        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.BOTH, expand=True)
        ############################################################
        h_frame1_l = tk.Frame(frame1)
        h_frame1_l.pack(expand=True)
        h_frame2_l = tk.Frame(frame1)
        h_frame2_l.pack(expand=True)
        ############################################################
        lang_frame = tk.Frame(h_frame1_l)
        lang_frame.pack(side=tk.LEFT,  expand=True, padx=30)
        qth_loc_frame = tk.Frame(h_frame1_l)
        qth_loc_frame.pack(side=tk.LEFT, expand=True, padx=30)
        ############################################################
        self._lang_var = tk.StringVar(self)
        self._lang_var.set('Deutsch')
        tk.Label(lang_frame, text='Sprache: ').pack(side=tk.LEFT)
        lang_ent = tk.OptionMenu(lang_frame,
                                 self._lang_var,
                                       *['Deutsch'],
                                 )
        lang_ent.configure(state='disabled') # TODO !!!
        lang_ent.pack(side=tk.LEFT)
        ############################################################
        qth_frame = tk.Frame(qth_loc_frame)
        qth_frame.pack(fill=tk.X, pady=8)
        tk.Label(qth_frame, text='QTH: ').pack(side=tk.LEFT)
        qth_ent = tk.Entry(qth_frame, width=25)
        qth_ent.pack(side=tk.LEFT)
        ############################################################
        loc_frame = tk.Frame(qth_loc_frame)
        loc_frame.pack(fill=tk.X, pady=8)
        tk.Label(loc_frame, text='Locator: ').pack(side=tk.LEFT)
        loc_ent = tk.Entry(loc_frame, width=10)
        loc_ent.pack(side=tk.LEFT)
        ############################################################
        ############################################################
        vorsch_col_frame = tk.Frame(h_frame2_l, )
        vorsch_col_frame.pack()
        ################
        tk.Label(h_frame2_l, text='Vorschreibfenster').pack(pady=15)

        self._color_example_text = tk.Text(h_frame2_l,
                                           height=5,
                                           width=40,
                                           font=('Courier', 11),
                                           background=self._bg_tx
                                           )

        self._color_example_text.pack()
        self._color_example_text.tag_config('sendet', foreground=self._fg_tx, background=self._bg_tx)
        self._color_example_text.tag_config('prewrite', foreground=self._fg_rx, background=self._bg_tx)
        self._color_example_text.insert(tk.END, 'TEST TEXT Test. 1234. 73... \n', )
        self._color_example_text.tag_add('sendet', 0.0, tk.INSERT)
        ind = str(self._color_example_text.index(tk.INSERT))
        self._color_example_text.insert(tk.END, 'TEST TEXT Test. 1234. 73... ', )
        self._color_example_text.tag_add('prewrite', ind, tk.END)
        fg_btn_frame = tk.Frame(h_frame2_l)
        fg_btn_frame.pack()
        # FG
        tk.Button(fg_btn_frame,
                  text='TX-Text',
                  command=lambda: self._choose_color('tx_fg')
                  ).pack(side=tk.LEFT, padx=10, pady=5)
        # FG
        tk.Button(fg_btn_frame,
                  text='RX-Text',
                  command=lambda: self._choose_color('rx_fg')
                  ).pack(side=tk.LEFT, padx=10)
        # BG
        tk.Button(h_frame2_l,
                  text='BG',
                  command=lambda: self._choose_color('tx_bg')
                  ).pack()


    def _choose_color(self, fg_bg: str):
        if fg_bg == 'tx_fg':
            col = askcolor(self._fg_tx,
                           title=get_strTab('text_color', self._lang))
            if not col:
                return
            if col[1] is None:
                return
            self._fg_tx = str(col[1])
        elif fg_bg == 'tx_bg':
            col = askcolor(self._bg_tx,
                           title=get_strTab('text_color', self._lang))
            if not col:
                return
            if col[1] is None:
                return
            self._bg_tx = str(col[1])
        elif fg_bg == 'rx_fg':
            col = askcolor(self._fg_rx,
                           title=get_strTab('text_color', self._lang))
            if not col:
                return
            if col[1] is None:
                return
            self._fg_rx = str(col[1])
        self._color_example_text.tag_config('sendet', foreground=self._fg_tx, background=self._bg_tx)
        self._color_example_text.tag_config('prewrite', foreground=self._fg_rx, background=self._bg_tx)
        self._color_example_text.configure(background=self._bg_tx)


    def _save_cfg(self):
        # self._set_cfg_to_port()
        pass

    @staticmethod
    def _get_config():
        return {}
        # return dict(POPT_CFG.get_digi_CFG())

    def save_config(self):
        conf: dict = POPT_CFG.load_guiPARM_main()
        old_conf = dict(conf)
        conf['gui_cfg_vor_col'] = str(self._fg_rx)
        conf['gui_cfg_vor_tx_col'] = str(self._fg_tx)
        conf['gui_cfg_vor_bg_col'] = str(self._bg_tx)
        POPT_CFG.set_guiPARM_main(conf)
        if old_conf == conf:
            return False
        return True
