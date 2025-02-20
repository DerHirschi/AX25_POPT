import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno

from cfg.default_config import getNew_BBS_FWD_cfg
from cfg.logger_config import logger
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import get_list_fm_viaStr, validate_ax25Call
from fnc.str_fnc import get_strTab
from schedule.guiPoPT_Scheduler import PoPT_Set_Scheduler
from schedule.popt_sched import getNew_schedule_config


class BBS_FWD_Settings(tk.Frame):
    def __init__(self, tabctl, root_win):
        tk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._logTag    = 'guiBBS_FWD_Settings: '
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict = self._root_win.get_root_pms_cfg()
        ###################################
        # Vars
        self._bbs_vars = {}
        # self._reverseFWD_var    = tk.BooleanVar(self, value=bool(self._pms_cfg.get('reverseFWD', True)))
        self.schedule_config    = dict(getNew_schedule_config())
        self.schedule_win       = None
        ###################################
        # GUI Stuff
        tk.Label(self, text='BBS-FWD').pack(side=tk.TOP, expand=False)
        r_btn_fr        = tk.Frame(self, borderwidth=10)
        r_tab_frame     = tk.Frame(self, borderwidth=10)

        r_btn_fr.pack(side=tk.TOP, fill=tk.X, expand=False)
        r_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # r2
        tk.Button(r_btn_fr,
                  text=self._getTabStr('new'),
                  command=self._add_new_homeBBS_tab
                  ).pack(side=tk.LEFT, fill=tk.X, expand=False)

        tk.Button(r_btn_fr,
                  text=self._getTabStr('delete'),
                  command=self._del_homeBBS_tab
                  ).pack(side=tk.RIGHT, expand=False)

        # r3 NoteBOOK Tab Stuff HomeBBS CFG
        self._tabctl = ttk.Notebook(r_tab_frame)
        self._tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabctl.bind("<<NotebookTabChanged>>", self._select_hBBS_tab)
        # r4
        tk.Button(r_tab_frame,
                  text=self._getTabStr('save'),
                  command=self._save_hBBS_tab
                  ).pack(side=tk.TOP, expand=True, pady=10)

        #################
        # Var Init
        # self._get_user_data_fm_cfg()
        if not self._pms_cfg.get('fwd_bbs_cfg', {}):
            self._add_new_homeBBS_tab()
        else:
            self._get_hBBS_vars_fm_cfg()

    def _add_new_homeBBS_tab(self):
        if 'NOCALL' in self._pms_cfg.get('fwd_bbs_cfg', {}).keys():
            return
        self._bbs_vars['NOCALL'] = self._add_homeBBS_tab()
        self._select_new_tab()

    def _add_homeBBS_tab(self, cfg=None):
        if not cfg:
            if 'NOCALL' in self._bbs_vars.keys():
                return
            cfg = getNew_BBS_FWD_cfg()
        ###########################################
        # VARs
        port_id_var         = tk.StringVar(self, value=cfg.get('port_id', '0'))
        dest_call_var       = tk.StringVar(self, value=cfg.get('dest_call', 'NOCALL'))
        regio_var           = tk.StringVar(self, value=cfg.get('regio', ''))
        rev_fwd_var         = tk.BooleanVar(self, value=cfg.get('reverseFWD', True))
        allow_rev_fwd_var   = tk.BooleanVar(self, value=cfg.get('allowRevFWD', True))
        viacalls            = ' '.join(cfg.get('via_calls', []))
        via_calls_var       = tk.StringVar(self, value=viacalls)
        axip = cfg.get('axip_add', None)
        if not axip:
            axip = ('', 0)
        axip_var            = tk.StringVar(self, value=axip[0])
        axip_port_var       = tk.StringVar(self, value=axip[1])
        ###########################################
        # Root Frame
        tab_frame   = tk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=dest_call_var.get())
        ###########################################
        # L/R Frames
        l_frame      = tk.Frame(tab_frame, borderwidth=10)
        r_frame      = tk.Frame(tab_frame, borderwidth=10)

        l_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        ttk.Separator(tab_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, expand=False)
        r_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        ###########################################
        # L Frame
        hbbs_call_f     = tk.Frame(l_frame, borderwidth=10)
        hbbs_regio_f    = tk.Frame(l_frame, borderwidth=10)
        p_id_f          = tk.Frame(l_frame, borderwidth=10)
        via_f           = tk.Frame(l_frame, borderwidth=10)
        axip_f          = tk.Frame(l_frame, borderwidth=10)
        axip_port_f     = tk.Frame(l_frame, borderwidth=10)
        # Pack it
        hbbs_call_f.pack(side=tk.TOP, expand=True, fill=tk.X)
        hbbs_regio_f.pack(side=tk.TOP, expand=True, fill=tk.X)
        p_id_f.pack(side=tk.TOP, expand=True, fill=tk.X)
        via_f.pack(side=tk.TOP, expand=True, fill=tk.X)
        axip_f.pack(side=tk.TOP, expand=True, fill=tk.X)
        axip_port_f.pack(side=tk.TOP, expand=True, fill=tk.X)

        ##################################
        tk.Label(hbbs_call_f, text='BBS Call: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(hbbs_call_f,
                 textvariable=dest_call_var,
                 width=10).pack(side=tk.LEFT, expand=False)

        tk.Label(hbbs_regio_f, text=f"{self._getTabStr('region')}: ").pack(side=tk.LEFT, expand=False)
        tk.Entry(hbbs_regio_f,
                 textvariable=regio_var,
                 width=20).pack(side=tk.LEFT, expand=False)

        tk.Label(p_id_f, text='Port ID: ').pack(side=tk.LEFT, expand=False)
        options = list(PORT_HANDLER.get_all_ports().keys())
        if not options:
            options = ['-']
            port_id_var.set(options[0])
        tk.OptionMenu(p_id_f,
                      port_id_var,
                      *options
                      ).pack(side=tk.LEFT, expand=False)


        tk.Label(via_f, text='VIA: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(via_f,
                 textvariable=via_calls_var,
                 width=40).pack(side=tk.LEFT, expand=False)


        tk.Label(axip_f, text='AXIP: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(axip_f,
                 textvariable=axip_var,
                 width=25).pack(side=tk.LEFT, expand=False)


        tk.Label(axip_port_f, text='AXIP-Port: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(axip_port_f,
                 textvariable=axip_port_var,
                 width=5).pack(side=tk.LEFT, expand=False)

        #################################################################
        # R Frame
        rev_fwd_frame   = tk.Frame(r_frame, borderwidth=10)
        allow_rev_fwd   = tk.Frame(r_frame, borderwidth=10)
        # Pack it
        rev_fwd_frame.pack(side=tk.TOP, expand=False, fill=tk.X)
        allow_rev_fwd.pack(side=tk.TOP, expand=False, fill=tk.X)
        #################
        # rev_fwd_frame
        tk.Checkbutton(rev_fwd_frame,
                       variable=rev_fwd_var,
                       text='Reverse-FWD').pack(side=tk.LEFT, expand=False)

        tk.Button(rev_fwd_frame,
                  text='Schedule',
                  command=self._open_schedWin
                  ).pack(side=tk.LEFT, expand=False, padx=120)

        #################
        # allow_rev_fwd
        tk.Checkbutton(allow_rev_fwd,
                       variable=allow_rev_fwd_var,
                       text=self._getTabStr('allowRevFWD')).pack(side=tk.LEFT, expand=False)

        return {
            'port_id_var'       : port_id_var,
            'dest_call_var'     : dest_call_var,
            'regio_var'         : regio_var,
            'via_calls_var'     : via_calls_var,
            'axip_var'          : axip_var,
            'axip_port_var'     : axip_port_var,
            'rev_fwd_var'       : rev_fwd_var,
            'allow_rev_fwd_var' : allow_rev_fwd_var,
        }

    def _del_homeBBS_tab(self):
        ret = askyesno(
            self._getTabStr('delete'),
            f"{self._getTabStr('delete')} ?",
            parent=self._root_win
        )
        if not ret:
            return
        cfg_key = self._get_sel_tabKey()
        if cfg_key:
            self._del_homeBBS_cfg(cfg_key)
            self._del_homeBBS_vars(cfg_key)
            self._tabctl.forget(self._tabctl.select())

    def _get_hBBS_vars_fm_cfg(self):
        for k, fwd_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            if not fwd_cfg:
                logger.warning(self._logTag + f"Empty FWD-CFG for {k}")
                fwd_cfg = getNew_BBS_FWD_cfg()
            self._bbs_vars[fwd_cfg.get('dest_call', 'NOCALL')] = self._add_homeBBS_tab(fwd_cfg)

    def _set_NOCALL_tab(self):
        nocall_vars = self._bbs_vars.get('NOCALL', {})
        if nocall_vars:
            port_id = 0
            try:
                port_id = int(nocall_vars['port_id_var'].get())
            except ValueError:
                pass
            dest_call = str(nocall_vars['dest_call_var'].get()).upper()
            if not validate_ax25Call(dest_call):
                dest_call = ''
            regio = str(nocall_vars['regio_var'].get()).upper()
            via_calls = str(nocall_vars['via_calls_var'].get())
            axip_ip = str(nocall_vars['axip_var'].get())
            try:
                axip_port = int(nocall_vars['axip_port_var'].get())
            except ValueError:
                axip_port = 0
            home_bbs_cfg = getNew_BBS_FWD_cfg()
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

    def _set_tab_name(self, name):
        self._tabctl.tab(self._tabctl.select(), text=name)

    def _get_hBBS_data_fm_vars(self):
        for k in list(self._bbs_vars.keys()):
            if k == 'NOCALL':
                continue
            try:
                port_id     = int(self._bbs_vars[k]['port_id_var'].get())
            except ValueError:
                continue
            dest_call       = str(self._bbs_vars[k]['dest_call_var'].get()).upper()
            if not validate_ax25Call(dest_call):
                continue
            try:
                axip_port   = int(self._bbs_vars[k]['axip_port_var'].get())
            except ValueError:
                continue
            regio           = str(self._bbs_vars[k]['regio_var'].get()).upper()
            via_calls       = str(self._bbs_vars[k]['via_calls_var'].get())
            axip_ip         = str(self._bbs_vars[k]['axip_var'].get())
            rev_fwd         = bool(self._bbs_vars[k]['rev_fwd_var'].get())
            allow_rev_fwd   = bool(self._bbs_vars[k]['allow_rev_fwd_var'].get())

            home_bbs_cfg = self._get_homeBBS_cfg(k)
            home_bbs_cfg['port_id']     = port_id
            home_bbs_cfg['regio']       = regio
            home_bbs_cfg['dest_call']   = dest_call  # # # #
            home_bbs_cfg['via_calls']   = get_list_fm_viaStr(via_calls)
            home_bbs_cfg['axip_add']    = axip_ip, axip_port
            home_bbs_cfg['reverseFWD']  = rev_fwd
            home_bbs_cfg['allowRevFWD'] = allow_rev_fwd
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
        # self._pms_cfg['fwd_bbs_cfg'][pms_cfg_k] = bbs_cfg
        self._set_homeBBS_cfg(pms_cfg_k, bbs_cfg)

    def _get_homeBBS_cfg(self, pms_cfg_k: str):
        all_bbs_cfgs = dict(self._pms_cfg.get('fwd_bbs_cfg', {}))
        return dict(all_bbs_cfgs.get(pms_cfg_k, getNew_BBS_FWD_cfg()))

    def _set_homeBBS_cfg(self, pms_cfg_k: str, bbs_cfg: dict):
        self._pms_cfg['fwd_bbs_cfg'][pms_cfg_k] = dict(bbs_cfg)

    def _del_NOCALL_homeBBS_cfg(self):
        if 'NOCALL' in self._pms_cfg.get('fwd_bbs_cfg', {}).keys():
            del self._pms_cfg['fwd_bbs_cfg']['NOCALL']

    def _del_homeBBS_cfg(self, pms_cfg_k: str):
        if pms_cfg_k in self._pms_cfg['fwd_bbs_cfg'].keys():
            self._pms_cfg['fwd_bbs_cfg'][pms_cfg_k] = None
            del self._pms_cfg['fwd_bbs_cfg'][pms_cfg_k]

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

    def _save_hBBS_tab(self):
        ind = self._get_sel_tabKey()
        if ind:
            if ind == 'NOCALL':
                self._set_NOCALL_tab()
            self._get_hBBS_data_fm_vars()

    def save_config(self):
        self._get_hBBS_data_fm_vars()
        """
        if self._pms_cfg:
            # self._cleanup_hBBS_cfg()
            self._set_homeBBS_list()
            if self._bbs_obj:
                self._bbs_obj.set_pms_cfg(self._pms_cfg)
        """

    def _cleanup_hBBS_cfg(self):
        if self._pms_cfg:
            if self._pms_cfg.get('fwd_bbs_cfg', {}).get('NOCALL', None):
                del self._pms_cfg['fwd_bbs_cfg']['NOCALL']
            for k in list(self._pms_cfg.get('fwd_bbs_cfg', {}).keys()):
                if k not in self._bbs_vars.keys():
                    del self._pms_cfg['fwd_bbs_cfg'][k]

    """
    def _set_homeBBS_list(self):
        self._pms_cfg['home_bbs'] = list(self._pms_cfg.get('home_bbs_cfg', {}).keys())
    """