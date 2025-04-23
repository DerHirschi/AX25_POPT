import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import validate_ax25Call
from fnc.str_fnc import get_strTab


class BBSGeneralSettings(tk.Frame):
    def __init__(self, tabctl, root_win):
        tk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._root_win  = root_win
        self._bbs_obj   = PORT_HANDLER.get_bbs()
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict     = self._root_win.get_root_pms_cfg()
        ###################################
        # Vars
        self._bid_var           = tk.StringVar(self)
        self._bid_ent_var       = tk.StringVar(self)
        self._sysop_call_var    = tk.StringVar(self,  value=str(self._pms_cfg.get('sysop',              '')))
        self._own_regio_var     = tk.StringVar(self,  value=str(self._pms_cfg.get('regio',              '')))
        self._own_call_var      = tk.StringVar(self,  value=str(self._pms_cfg.get('user',               '')))
        self._singleConn_var    = tk.BooleanVar(self, value=bool(self._pms_cfg.get('single_auto_conn',  True)))
        self._autoConn_var      = tk.BooleanVar(self, value=bool(self._pms_cfg.get('auto_conn',         False)))
        self._pnAutoPath_var    = tk.StringVar(self,  value=str(self._pms_cfg.get('pn_auto_path',       1)))
        self._bin_mode_var      = tk.BooleanVar(self, value=bool(self._pms_cfg.get('bin_mode',          True)))
        self._bbs_mode_var      = tk.BooleanVar(self, value=bool(not self._pms_cfg.get('enable_fwd',          True)))
        local_distr_cfg         = ' '.join(self._pms_cfg.get('local_dist',  []))
        local_theme_cfg         = ' '.join(self._pms_cfg.get('local_theme', []))
        block_bbs_cfg           = ' '.join(self._pms_cfg.get('block_bbs',   []))
        block_call_cfg          = ' '.join(self._pms_cfg.get('block_call',  []))
        self._localDistr_var    = tk.StringVar(self,  value=local_distr_cfg)
        self._localTheme_var    = tk.StringVar(self,  value=local_theme_cfg)
        self._blockBBS_var      = tk.StringVar(self,  value=block_bbs_cfg)
        self._blockCALL_var     = tk.StringVar(self,  value=block_call_cfg)

        ###################################
        # GUI Stuff
        ###########################################
        # L/R Frames
        l_frame = tk.Frame(self, borderwidth=20)
        r_frame = tk.Frame(self, borderwidth=10)

        l_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, expand=False)
        r_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y)

        ###########################################
        # L Frames
        sysop_call_fr   = tk.Frame(l_frame, borderwidth=5)
        own_call_fr     = tk.Frame(l_frame, borderwidth=5)
        own_regio_fr    = tk.Frame(l_frame, borderwidth=5)

        bid_fr          = tk.Frame(l_frame, borderwidth=5)
        bid_btn_fr      = tk.Frame(l_frame, borderwidth=5)
        btn_fr          = tk.Frame(l_frame, borderwidth=5)
        chk_fr          = tk.Frame(l_frame, borderwidth=5)
        binM_f          = tk.Frame(l_frame, borderwidth=5)
        bbsM_f          = tk.Frame(l_frame, borderwidth=5)
        chk_f2          = tk.Frame(l_frame, borderwidth=5)
        help_f          = tk.Frame(l_frame, borderwidth=5)
        #############
        tk.Label(l_frame, text=self._getTabStr('own_station')).pack(side=tk.TOP, expand=False)

        sysop_call_fr.pack( side=tk.TOP, fill=tk.X, expand=False, pady=12)
        own_call_fr.pack(   side=tk.TOP, fill=tk.X, expand=False)
        own_regio_fr.pack(  side=tk.TOP, fill=tk.X, expand=False)
        bid_fr.pack(        side=tk.TOP, fill=tk.X, expand=False)
        bid_btn_fr.pack(    side=tk.TOP, fill=tk.X, expand=False)
        btn_fr.pack(        side=tk.TOP, fill=tk.X, expand=False)
        chk_fr.pack(        side=tk.TOP, fill=tk.X, expand=False)
        binM_f.pack(        side=tk.TOP, fill=tk.X, expand=False)
        bbsM_f.pack(        side=tk.TOP, fill=tk.X, expand=False)
        chk_f2.pack(        side=tk.TOP, fill=tk.X, expand=False)
        help_f.pack(        side=tk.TOP, fill=tk.X, expand=False)

        tk.Label(sysop_call_fr, text='Sysop-CALL: ', width=10).pack(side=tk.LEFT, expand=False)
        opt = list(POPT_CFG.get_stat_CFGs_by_typ().keys())
        if not opt:
            opt = ['']
        tk.OptionMenu(sysop_call_fr,
                 self._sysop_call_var,
                 *opt,
                 ).pack(side=tk.LEFT, expand=False)

        tk.Label(own_call_fr, text='BBS-CALL: ', width=10).pack(side=tk.LEFT, expand=False)
        opt = list(POPT_CFG.get_stat_CFGs_by_typ('BOX').keys())
        if not opt:
            opt = ['']
        tk.OptionMenu(own_call_fr,
                self._own_call_var,
                 *opt
                 ).pack(side=tk.LEFT, expand=False)

        tk.Label(own_regio_fr, text=f"{self._getTabStr('region')}: ", width=10).pack(side=tk.LEFT, expand=False)
        tk.Entry(own_regio_fr,
                 textvariable=self._own_regio_var,
                 width=20).pack(side=tk.LEFT, expand=False)

        tk.Label(bid_fr, textvariable=self._bid_var).pack(side=tk.LEFT, expand=False, padx=110)

        tk.Button(bid_btn_fr,
                  text='Set MID',
                  command=self._set_MID
                  ).pack(side=tk.LEFT, fill=tk.X, expand=False, padx=15)
        tk.Entry(bid_btn_fr,
                 width=8,
                 textvariable=self._bid_ent_var
                 ).pack(side=tk.LEFT, fill=tk.X, expand=False)

        ###################
        # chk_fr
        tk.Checkbutton(chk_fr,
                       variable=self._autoConn_var,
                       text='Outgoing FWD').pack(side=tk.LEFT, expand=False)
        tk.Checkbutton(chk_fr,
                       variable=self._singleConn_var,
                       text='Single Conn').pack(side=tk.LEFT, expand=False)
        ###################
        # binM_f
        tk.Checkbutton(binM_f,
                       variable=self._bin_mode_var,
                       text='BIN Mode').pack(side=tk.LEFT, expand=False)
        ###################
        # bbsM_f
        tk.Checkbutton(bbsM_f,
                       variable=self._bbs_mode_var,
                       text='PMS Mode (no S&F)').pack(side=tk.LEFT, expand=False)
        ###################
        # chk_f2
        tk.Spinbox(chk_f2,
                    from_=0,
                    to=2,
                    increment=1,
                    width=2,
                    textvariable=self._pnAutoPath_var,
                 ).pack(side=tk.LEFT, expand=False, padx=7, pady=15)
        tk.Label(chk_f2, text='PN Auto-Path').pack(side=tk.LEFT, expand=False, padx=5)
        ###################
        # help_f
        help_text  = self._getTabStr('fwd_autoPath_help').split('\n')
        for line in help_text:
            tk.Label(help_f, text=line).pack(side=tk.TOP, expand=False, padx=20, anchor='w')
        ##############################d#############
        # R Frames
        local_dist_ent_f         = tk.Frame(r_frame, borderwidth=5)
        local_theme_ent_f        = tk.Frame(r_frame, borderwidth=5)
        block_bbs_ent_f          = tk.Frame(r_frame, borderwidth=5)
        block_call_ent_f         = tk.Frame(r_frame, borderwidth=5)
        #############
        tk.Label(r_frame, text=self._getTabStr('bbs_sett_fwd_global')).pack(side=tk.TOP, expand=False)

        local_dist_ent_f.pack(  side=tk.TOP, fill=tk.X, expand=False, pady=12)
        local_theme_ent_f.pack( side=tk.TOP, fill=tk.X, expand=False)
        block_bbs_ent_f.pack(   side=tk.TOP, fill=tk.X, expand=False)
        block_call_ent_f.pack(  side=tk.TOP, fill=tk.X, expand=False)

        ###################
        # local_dist_ent_f Dist
        tk.Label(local_dist_ent_f,
                 text=f"{self._getTabStr('bbs_sett_local_dist')}: ").pack(side=tk.TOP, expand=False, anchor='w')
        tk.Entry(local_dist_ent_f,
                 textvariable=self._localDistr_var,
                 width=84).pack(side=tk.TOP, expand=True, anchor='w')

        ###################
        # local_theme_ent_f Theme
        tk.Label(local_theme_ent_f,
                 text=f"{self._getTabStr('bbs_sett_local_theme')}: ").pack(side=tk.TOP, expand=False, anchor='w')
        tk.Entry(local_theme_ent_f,
                 textvariable=self._localTheme_var,
                 width=84).pack(side=tk.TOP, expand=True, anchor='w')

        ###################
        # block_bbs_ent_f BBS Block
        tk.Label(block_bbs_ent_f,
                 text=f"{self._getTabStr('bbs_sett_block_bbs')}: ").pack(side=tk.TOP, expand=False, anchor='w')
        tk.Entry(block_bbs_ent_f,
                 textvariable=self._blockBBS_var,
                 width=84).pack(side=tk.TOP, expand=True, anchor='w')

        ###################
        # block_call_ent_f CALL Block
        tk.Label(block_call_ent_f,
                 text=f"{self._getTabStr('bbs_sett_block_call')}: ").pack(side=tk.TOP, expand=False, anchor='w')
        tk.Entry(block_call_ent_f,
                 textvariable=self._blockCALL_var,
                 width=84).pack(side=tk.TOP, expand=True, anchor='w')


        ###################################
        # INIT Stuff
        self._get_BID()

    def _get_BID(self):
        bid = self._bbs_obj.get_bid()
        self._bid_ent_var.set(str(bid))
        bid_str = f"MID: {bid}"
        self._bid_var.set(bid_str)

    def _set_MID(self):
        mid = self._bid_ent_var.get()
        try:
            mid = int(mid)
        except ValueError:
            return
        self._bbs_obj.set_bid(mid)
        self._get_BID()

    ####################################
    def _get_user_data_fm_vars(self):
        user = self._own_call_var.get().upper()
        if user == 'NOCALL':
            return
        if not validate_ax25Call(user):
            return
        self._pms_cfg['user']               = user
        self._pms_cfg['regio']              = str(self._own_regio_var.get().upper())  # TODO Validator
        self._pms_cfg['sysop']              = str(self._sysop_call_var.get())
        self._pms_cfg['single_auto_conn']   = bool(self._singleConn_var.get())
        self._pms_cfg['auto_conn']          = bool(self._autoConn_var.get())
        self._pms_cfg['bin_mode']           = bool(self._bin_mode_var.get())
        self._pms_cfg['enable_fwd']         = not bool(self._bbs_mode_var.get())
        try:
            self._pms_cfg['pn_auto_path']   = int(self._pnAutoPath_var.get())
        except ValueError:
            self._pms_cfg['pn_auto_path']   = 0

        local_distr_cfg     =   self._validate_entry(self._localDistr_var.get())
        local_theme_cfg     =   self._validate_entry(self._localTheme_var.get())
        block_bbs_cfg       =   self._validate_entry(self._blockBBS_var.get())
        block_call_cfg      =   self._validate_entry(self._blockCALL_var.get())
        self._pms_cfg['local_dist']   = local_distr_cfg
        self._pms_cfg['local_theme']  = local_theme_cfg
        self._pms_cfg['block_bbs']    = block_bbs_cfg
        self._pms_cfg['block_call']   = block_call_cfg

    @staticmethod
    def _validate_entry(str_in: str):
        tmp = str_in.split(' ')
        ret = []
        for el in tmp:
            tmp_el = el.split('-')[0].upper()
            if not tmp_el:
                continue
            if tmp_el in ret:
                continue
            if not validate_ax25Call(tmp_el):
                continue
            ret.append(tmp_el)
        return ret



    ####################################
    def save_config(self):
        self._get_user_data_fm_vars()
        return True
