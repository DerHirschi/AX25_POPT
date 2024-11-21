import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import validate_call, get_list_fm_viaStr
from schedule.guiPoPT_Scheduler import PoPT_Set_Scheduler
from schedule.popt_sched import getNew_schedule_config
# from cfg.logger_config import logger


class PMS_Settings(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        ###################################
        # Vars
        self._bbs_obj = PORT_HANDLER.get_bbs()
        self._bbs_vars = {}
        self._bid_var = tk.StringVar(self)
        self._bid_ent_var = tk.StringVar(self)
        self._own_regio_var = tk.StringVar(self)
        self._own_call_var = tk.StringVar(self)
        self._singleConn_var = tk.BooleanVar(self)
        self._silentConn_var = tk.BooleanVar(self)
        self._autoConn_var = tk.BooleanVar(self)
        self.schedule_config = dict(getNew_schedule_config())
        self.schedule_win = None
        ###################################
        # CFG
        self._pms_cfg = self._bbs_obj.get_pms_cfg()
        self._pms_cfg['home_bbs_cfg'] = dict(self._pms_cfg['home_bbs_cfg'])
        self._pms_cfg['home_bbs'] = list(self._pms_cfg['home_bbs'])
        self._pms_cfg['regio'] = str(self._pms_cfg['regio'])
        self._pms_cfg['user'] = str(self._pms_cfg['user'])
        self._pms_cfg['single_auto_conn'] = bool(self._pms_cfg['single_auto_conn'])
        self._pms_cfg['auto_conn'] = bool(self._pms_cfg['auto_conn'])
        # TODO self._pms_cfg['auto_conn_silent'] = bool(self._pms_cfg.get('auto_conn_silent', True))
        ######################
        # TK Stuff
        # self.title(STR_TABLE['fwd_list'][self._root_win.language])
        self.title('PMS Einstellungen')
        self.style = self._root_win.style
        self.geometry(f"1010x"
                      f"620+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        # self.resizable(width=False, height=False)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        ###################################
        # Frames
        l_frame = tk.Frame(self, borderwidth=20)
        r_frame = tk.Frame(self, borderwidth=20)
        l_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, expand=False)
        r_frame.pack(side=tk.LEFT, expand=False, anchor='n')
        ###################################
        # L

        own_call_fr = tk.Frame(l_frame, borderwidth=5)
        own_regio_fr = tk.Frame(l_frame, borderwidth=5)

        bid_fr = tk.Frame(l_frame, borderwidth=5)
        bid_btn_fr = tk.Frame(l_frame, borderwidth=5)
        btn_fr = tk.Frame(l_frame, borderwidth=5)

        tk.Label(l_frame, text='Eigene Station').pack(side=tk.TOP, expand=False)
        own_call_fr.pack(side=tk.TOP, fill=tk.X, expand=False, pady=12)
        tk.Label(own_call_fr, text='CALL: ', width=10).pack(side=tk.LEFT, expand=False)
        tk.Entry(own_call_fr,
                 textvariable=self._own_call_var,
                 width=7).pack(side=tk.LEFT, expand=False)

        own_regio_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        tk.Label(own_regio_fr, text='Region: ', width=10).pack(side=tk.LEFT, expand=False)
        tk.Entry(own_regio_fr,
                 textvariable=self._own_regio_var,
                 width=20).pack(side=tk.LEFT, expand=False)

        bid_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        tk.Label(bid_fr, textvariable=self._bid_var).pack(side=tk.TOP, expand=False)

        bid_btn_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        tk.Button(bid_btn_fr,
                  text='Set MID',
                  command=self._set_MID
                  ).pack(side=tk.LEFT, fill=tk.X, expand=False, padx=15)
        tk.Entry(bid_btn_fr,
                 width=8,
                 textvariable=self._bid_ent_var
                 ).pack(side=tk.LEFT, fill=tk.X, expand=False)

        btn_fr.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        self._init_btn_frame(btn_fr)
        ###################################
        # R
        tk.Label(r_frame, text='HomeBBS').pack(side=tk.TOP, expand=False)
        r_check_fr = tk.Frame(r_frame, borderwidth=5)
        r_btn_fr = tk.Frame(r_frame, borderwidth=20)
        r_tab_frame = tk.Frame(r_frame, borderwidth=20)

        r_check_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        r_btn_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        r_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        # r1
        tk.Checkbutton(r_check_fr,
                       variable=self._autoConn_var,
                       text='AutoFWD').pack(side=tk.LEFT, expand=True)
        tk.Checkbutton(r_check_fr,
                       variable=self._singleConn_var,
                       text='Single Conn').pack(side=tk.LEFT, expand=True)
        tk.Checkbutton(r_check_fr,
                       variable=self._silentConn_var,
                       text='Silent Conn',
                       state='disabled',  # TODO Silent Conn/Service Port
                       ).pack(side=tk.LEFT, expand=True)

        # r2
        tk.Button(r_btn_fr,
                  text='Neu',
                  command=self._add_new_homeBBS_tab
                  ).pack(side=tk.LEFT, fill=tk.X, expand=False)
        tk.Button(r_btn_fr,
                  text='Löschen',
                  command=self._del_homeBBS_tab
                  ).pack(side=tk.RIGHT, expand=False)

        # r3 NoteBOOK Tab Stuff HomeBBS CFG
        self._tabctl = ttk.Notebook(
            r_tab_frame, height=300
        )
        self._tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self._tabctl.bind("<<NotebookTabChanged>>", self._select_hBBS_tab)
        # r4
        tk.Button(r_tab_frame,
                  text='Speichern',
                  command=self._save_hBBS_tab
                  ).pack(side=tk.TOP, expand=False, pady=10)
        #################
        # Var Init
        self._get_BID()
        self._get_user_data_fm_cfg()
        if not self._pms_cfg.get('home_bbs_cfg', {}):
            self._add_new_homeBBS_tab()
        else:
            self._get_hBBS_vars_fm_cfg()

    def _init_btn_frame(self, frame: tk.Frame):
        tk.Button(frame,
                  text='Ok',
                  command=self._ok_btn
                  ).pack(side=tk.LEFT, expand=False, padx=20)
        tk.Button(frame,
                  text='Speichern',
                  command=self._save_btn
                  ).pack(side=tk.LEFT, expand=False, padx=20)
        tk.Button(frame,
                  text='Abbrechen',
                  command=self._close
                  ).pack(side=tk.RIGHT, expand=False, padx=20)

    def _add_new_homeBBS_tab(self):
        if 'NOCALL' in self._pms_cfg.get('home_bbs_cfg', {}).keys():
            return
        self._bbs_vars['NOCALL'] = self._add_homeBBS_tab()
        self._select_new_tab()

    def _add_homeBBS_tab(self, cfg=None):
        if not cfg:
            if 'NOCALL' in self._bbs_vars.keys():
                return
            cfg = POPT_CFG.get_default_CFG_by_key('pms_home_bbs')
        port_id_var = tk.StringVar(self, value=cfg.get('port_id', '0'))
        dest_call_var = tk.StringVar(self, value=cfg.get('dest_call', 'NOCALL'))
        regio_var = tk.StringVar(self, value=cfg.get('regio', ''))
        viacalls = ' '.join(cfg.get('via_calls', []))
        via_calls_var = tk.StringVar(self, value=viacalls)
        axip = cfg.get('axip_add', None)
        if not axip:
            axip = ('', 0)
        axip_var = tk.StringVar(self, value=axip[0])
        axip_port_var = tk.StringVar(self, value=axip[1])

        tab_frame = tk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=dest_call_var.get())
        hbbs_call_f = tk.Frame(tab_frame, borderwidth=10)
        hbbs_call_f.pack(side=tk.TOP, expand=True, anchor='w')
        tk.Label(hbbs_call_f, text='BBS Call: ', width=10).pack(side=tk.LEFT, expand=False, anchor='w')
        tk.Entry(hbbs_call_f,
                 textvariable=dest_call_var,
                 width=10).pack(side=tk.LEFT, expand=False)

        hbbs_regio_f = tk.Frame(tab_frame, borderwidth=10)
        hbbs_regio_f.pack(side=tk.TOP, expand=True, anchor='w')
        tk.Label(hbbs_regio_f, text='Regio: ', width=10).pack(side=tk.LEFT, expand=False, anchor='w')
        tk.Entry(hbbs_regio_f,
                 textvariable=regio_var,
                 width=20).pack(side=tk.LEFT, expand=False)

        p_id_f = tk.Frame(tab_frame, borderwidth=10)
        p_id_f.pack(side=tk.TOP, expand=True, anchor='w')
        tk.Label(p_id_f, text='Port ID: ', width=10).pack(side=tk.LEFT, expand=False)
        options = list(PORT_HANDLER.get_all_ports().keys())
        if not options:
            options = ['-']
            port_id_var.set(options[0])
        tk.OptionMenu(p_id_f,
                      port_id_var,
                      *options
                      ).pack(side=tk.LEFT, expand=False)

        via_f = tk.Frame(tab_frame, borderwidth=10)
        via_f.pack(side=tk.TOP, expand=True, anchor='w')
        tk.Label(via_f, text='VIA: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(via_f,
                 textvariable=via_calls_var,
                 width=40).pack(side=tk.LEFT, expand=False)

        axip_f = tk.Frame(tab_frame, borderwidth=10)
        axip_f.pack(side=tk.TOP, expand=True, anchor='w')
        tk.Label(axip_f, text='AXIP: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(axip_f,
                 textvariable=axip_var,
                 width=25).pack(side=tk.LEFT, expand=False)

        axip_port_f = tk.Frame(tab_frame, borderwidth=10)
        axip_port_f.pack(side=tk.TOP, expand=True, anchor='w')
        tk.Label(axip_port_f, text='AXIP-Port: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(axip_port_f,
                 textvariable=axip_port_var,
                 width=5).pack(side=tk.LEFT, expand=False)

        # sched_btn_f = tk.Frame(tab_frame, borderwidth=10)
        # sched_btn_f.pack(side=tk.TOP, expand=False)
        tk.Button(axip_port_f,
                  text='Schedule',
                  command=self._open_schedWin
                  ).pack(side=tk.LEFT, expand=False, padx=120)

        return {
            'port_id_var': port_id_var,
            'dest_call_var': dest_call_var,
            'regio_var': regio_var,
            'via_calls_var': via_calls_var,
            'axip_var': axip_var,
            'axip_port_var': axip_port_var,
        }

    def _del_homeBBS_tab(self):
        cfg_key = self._get_sel_tabKey()
        if cfg_key:
            self._del_homeBBS_cfg(cfg_key)
            self._del_homeBBS_vars(cfg_key)
            self._tabctl.forget(self._tabctl.select())

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

    def _get_user_data_fm_cfg(self):
        self._own_call_var.set(self._pms_cfg.get('user', 'NOCALL'))
        self._own_regio_var.set(self._pms_cfg.get('regio', 'NOCALL'))
        self._singleConn_var.set(self._pms_cfg.get('single_auto_conn', True))
        self._silentConn_var.set(self._pms_cfg.get('auto_conn_silent', True))
        self._autoConn_var.set(self._pms_cfg.get('auto_conn', False))

    def _get_hBBS_vars_fm_cfg(self):
        home_bbs_cfg = self._pms_cfg.get('home_bbs_cfg', {})
        for k in home_bbs_cfg.keys():
            cfg = home_bbs_cfg.get(k, {})
            if cfg:
                # self._port_id_var.set(str(cfg.get('port_id', '-')))
                """
                'port_id': 1,
                'regio': '#SAW.SAA.DEU.EU',
                # 'own_call': user,
                'dest_call': 'MD2BBS',
                'via_calls': ['CB0SAW'],
                'axip_add': ('', 0),
                'scheduler_cfg': sched1,
                """
                self._bbs_vars[cfg.get('dest_call', 'NOCALL')] = self._add_homeBBS_tab(cfg)

    def _get_user_data_fm_vars(self):
        """
        'user': 'MD2SAW',
        'regio': '#SAW.SAA.DEU.EU',
        'single_auto_conn': True,
        'auto_conn': True,
        """
        user = self._own_call_var.get()
        if user == 'NOCALL':
            return
        user = validate_call(user)
        if not user:
            return
        self._pms_cfg['user'] = user
        self._pms_cfg['regio'] = str(self._own_regio_var.get().upper())  # TODO Validator
        self._pms_cfg['single_auto_conn'] = bool(self._singleConn_var.get())
        self._pms_cfg['auto_conn_silent'] = bool(self._silentConn_var.get())
        self._pms_cfg['auto_conn'] = bool(self._autoConn_var.get())

    def _set_NOCALL_tab(self):
        nocall_vars = self._bbs_vars.get('NOCALL', {})
        if nocall_vars:
            port_id = 0
            try:
                port_id = int(nocall_vars['port_id_var'].get())
            except ValueError:
                pass
            dest_call = validate_call(nocall_vars['dest_call_var'].get())
            regio = str(nocall_vars['regio_var'].get()).upper()
            via_calls = str(nocall_vars['via_calls_var'].get())
            axip_ip = str(nocall_vars['axip_var'].get())
            try:
                axip_port = int(nocall_vars['axip_port_var'].get())
            except ValueError:
                axip_port = 0
            home_bbs_cfg = POPT_CFG.get_default_CFG_by_key('pms_home_bbs')
            home_bbs_cfg['port_id'] = port_id
            home_bbs_cfg['regio'] = regio
            home_bbs_cfg['dest_call'] = dest_call
            home_bbs_cfg['via_calls'] = get_list_fm_viaStr(via_calls)
            home_bbs_cfg['axip_add'] = axip_ip, axip_port
            self._set_homeBBS_cfg(dest_call, home_bbs_cfg)
            self._bbs_vars[dest_call] = dict(self._bbs_vars['NOCALL'])
            self._set_tab_name(dest_call)
            self._bbs_vars['NOCALL'] = {}
            self._del_NOCALL_homeBBS_cfg()

    def _save_hBBS_tab(self):
        ind = self._get_sel_tabKey()
        if ind:
            if ind == 'NOCALL':
                self._set_NOCALL_tab()
            self._get_hBBS_data_fm_vars()

    def _set_tab_name(self, name):
        self._tabctl.tab(self._tabctl.select(), text=name)

    def _get_hBBS_data_fm_vars(self):
        for k in list(self._bbs_vars.keys()):
            if k != 'NOCALL':
                port_id = 0
                try:
                    port_id = int(self._bbs_vars[k]['port_id_var'].get())
                except ValueError:
                    pass
                dest_call = validate_call(self._bbs_vars[k]['dest_call_var'].get())
                regio = str(self._bbs_vars[k]['regio_var'].get()).upper()
                via_calls = str(self._bbs_vars[k]['via_calls_var'].get())
                axip_ip = str(self._bbs_vars[k]['axip_var'].get())
                try:
                    axip_port = int(self._bbs_vars[k]['axip_port_var'].get())
                except ValueError:
                    axip_port = 0

                home_bbs_cfg = self._get_homeBBS_cfg(k)
                home_bbs_cfg['port_id'] = port_id
                home_bbs_cfg['regio'] = regio
                home_bbs_cfg['dest_call'] = dest_call  # # # #
                home_bbs_cfg['via_calls'] = get_list_fm_viaStr(via_calls)
                home_bbs_cfg['axip_add'] = axip_ip, axip_port
                if k != dest_call:
                    self._bbs_vars[dest_call] = dict(self._bbs_vars[k])
                    self._set_tab_name(dest_call)
                    del self._bbs_vars[k]
                self._set_homeBBS_cfg(k, home_bbs_cfg)
        self._cleanup_hBBS_cfg()

    def _del_homeBBS_vars(self, cfg_key):
        if cfg_key in self._bbs_vars.keys():
            self._bbs_vars[cfg_key] = None
            del self._bbs_vars[cfg_key]

    def tasker(self):
        pass

    def _select_new_tab(self):
        self._tabctl.select(len(self._bbs_vars.keys()) - 1)

    def _open_schedWin(self):
        ind = self._get_sel_tabKey()
        if ind:
            self._select_scheCfg(ind)
            if not self.schedule_win:
                PoPT_Set_Scheduler(self)

    def _select_scheCfg(self, pms_cfg_k: str):
        bbs_cfg = self._get_homeBBS_cfg(pms_cfg_k)
        self.schedule_config = dict(bbs_cfg.get('scheduler_cfg', dict(getNew_schedule_config())))

    def _save_scheCfg(self, pms_cfg_k: str):
        bbs_cfg = self._get_homeBBS_cfg(pms_cfg_k)
        bbs_cfg['scheduler_cfg'] = dict(self.schedule_config)
        # self._pms_cfg['home_bbs_cfg'][pms_cfg_k] = bbs_cfg
        self._set_homeBBS_cfg(pms_cfg_k, bbs_cfg)

    def _get_homeBBS_cfg(self, pms_cfg_k: str):
        all_bbs_cfgs = dict(self._pms_cfg.get('home_bbs_cfg', {}))
        return dict(all_bbs_cfgs.get(pms_cfg_k, POPT_CFG.get_default_CFG_by_key('pms_home_bbs')))

    def _set_homeBBS_cfg(self, pms_cfg_k: str, bbs_cfg: dict):
        self._pms_cfg['home_bbs_cfg'][pms_cfg_k] = dict(bbs_cfg)

    def _del_NOCALL_homeBBS_cfg(self):
        if 'NOCALL' in self._pms_cfg.get('home_bbs_cfg', {}).keys():
            del self._pms_cfg['home_bbs_cfg']['NOCALL']

    def _del_homeBBS_cfg(self, pms_cfg_k: str):
        if pms_cfg_k in self._pms_cfg['home_bbs_cfg'].keys():
            self._pms_cfg['home_bbs_cfg'][pms_cfg_k] = None
            del self._pms_cfg['home_bbs_cfg'][pms_cfg_k]

    def scheduler_config_save_task(self):
        """ Task fm PoPT-Scheduler_win"""
        ind = self._get_sel_tabKey()
        if ind:
            self._save_scheCfg(ind)

    def _select_hBBS_tab(self, event=None):
        ind = self._get_sel_tabKey()
        if ind:
            self._select_scheCfg(ind)

    def _get_sel_tabKey(self):
        try:
            return self._tabctl.tab(self._tabctl.select(), "text")
        except tk.TclError:
            return ''

    def _save_pms_cfg(self):
        self._get_hBBS_data_fm_vars()
        self._get_user_data_fm_vars()
        if self._pms_cfg:
            # self._cleanup_hBBS_cfg()
            self._set_homeBBS_list()
            if self._bbs_obj:
                self._bbs_obj.set_pms_cfg(self._pms_cfg)

    def _cleanup_hBBS_cfg(self):
        if self._pms_cfg:
            if self._pms_cfg.get('home_bbs_cfg', {}).get('NOCALL', None):
                del self._pms_cfg['home_bbs_cfg']['NOCALL']
            for k in list(self._pms_cfg.get('home_bbs_cfg', {}).keys()):
                if k not in self._bbs_vars.keys():
                    del self._pms_cfg['home_bbs_cfg'][k]

    def _set_homeBBS_list(self):
        self._pms_cfg['home_bbs'] = list(self._pms_cfg.get('home_bbs_cfg', {}).keys())

    def _save_btn(self):
        self._save_pms_cfg()
        POPT_CFG.save_MAIN_CFG_to_file()

    def _ok_btn(self):
        self._save_pms_cfg()
        self._close()

    def _close(self):
        if self.schedule_win:
            self.schedule_win.destroy()
        self._bbs_obj = None
        self._pms_cfg = None
        self._bbs_vars = None
        del self._root_win.settings_win
        self._root_win.settings_win = None
        self.destroy()
