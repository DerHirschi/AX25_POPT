import tkinter as tk

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
        self._pms_cfg: dict = self._root_win.get_root_pms_cfg()
        ###################################
        # Vars
        self._bid_var           = tk.StringVar(self)
        self._bid_ent_var       = tk.StringVar(self)
        self._own_regio_var     = tk.StringVar(self,  value=str(self._pms_cfg.get('regio', '')))
        self._own_call_var      = tk.StringVar(self,  value=str(self._pms_cfg.get('user', '')))
        self._singleConn_var    = tk.BooleanVar(self, value=bool(self._pms_cfg.get('single_auto_conn', True)))
        self._autoConn_var      = tk.BooleanVar(self, value=bool(self._pms_cfg.get('auto_conn', False)))
        self._pnAutoPath_var    = tk.BooleanVar(self, value=bool(self._pms_cfg.get('pn_auto_path', True)))
        ###################################
        # GUI Stuff
        own_call_fr     = tk.Frame(self, borderwidth=5)
        own_regio_fr    = tk.Frame(self, borderwidth=5)

        bid_fr          = tk.Frame(self, borderwidth=5)
        bid_btn_fr      = tk.Frame(self, borderwidth=5)
        btn_fr          = tk.Frame(self, borderwidth=5)
        chk_fr          = tk.Frame(self, borderwidth=5)
        chk_f2          = tk.Frame(self, borderwidth=5)
        #############
        tk.Label(self, text=self._getTabStr('own_station')).pack(side=tk.TOP, expand=False)

        own_call_fr.pack(side=tk.TOP, fill=tk.X, expand=False, pady=12)
        own_regio_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        bid_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        chk_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        chk_f2.pack(side=tk.TOP, fill=tk.X, expand=False)

        tk.Label(own_call_fr, text='CALL: ', width=10).pack(side=tk.LEFT, expand=False)
        tk.Entry(own_call_fr,
                 textvariable=self._own_call_var,
                 width=7).pack(side=tk.LEFT, expand=False)

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
        # chk_f2
        tk.Checkbutton(chk_f2,
                       variable=self._pnAutoPath_var,
                       text='PM Auto-Path').pack(side=tk.LEFT, expand=False)


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
        self._pms_cfg['single_auto_conn']   = bool(self._singleConn_var.get())
        self._pms_cfg['auto_conn']          = bool(self._autoConn_var.get())
        self._pms_cfg['pn_auto_path']       = bool(self._pnAutoPath_var.get())

    ####################################
    def save_config(self):
        self._get_user_data_fm_vars()
