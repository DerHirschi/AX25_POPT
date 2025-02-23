import tkinter as tk
from tkinter import ttk

from cfg.default_config import getNew_BBS_FWD_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class BBSRoutingSettings(tk.Frame):
    def __init__(self, tabctl, root_win):
        tk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._logTag    = 'BBSRoutingSettings: '
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict     = self._root_win.get_root_pms_cfg()
        ###################################
        # Vars
        self._bbs_vars = {}
        ###################################
        # Tabctl
        self._tabctl = ttk.Notebook(self)
        self._tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # self._tabctl.bind("<<NotebookTabChanged>>", self._select_hBBS_tab)

        ##########################
        # Init
        self._get_fwdBBS_vars_fm_cfg()

    def _add_fwdBBS_pn_out_tab(self, cfg=None):
        if not cfg:
            if 'NOCALL' in self._bbs_vars.keys():
                return
            cfg = getNew_BBS_FWD_cfg()
        ###########################################
        # VARs
        pn_fwd_bbs_out          = ' '.join(cfg.get('pn_fwd_bbs_out',      []))
        pn_fwd_h_out            = ' '.join(cfg.get('pn_fwd_h_out',        []))
        pn_fwd_not_h_out        = ' '.join(cfg.get('pn_fwd_not_h_out',    []))
        pn_fwd_call_out         = ' '.join(cfg.get('pn_fwd_call_out',     []))
        pn_fwd_not_call_out     = ' '.join(cfg.get('pn_fwd_not_call_out', []))

        pn_fwd_bbs_out_var      = tk.StringVar(self, value=pn_fwd_bbs_out)
        pn_fwd_h_out_var        = tk.StringVar(self, value=pn_fwd_h_out)
        pn_fwd_not_h_out_var    = tk.StringVar(self, value=pn_fwd_not_h_out)
        pn_fwd_call_out_var     = tk.StringVar(self, value=pn_fwd_call_out)
        pn_fwd_not_call_out_var = tk.StringVar(self, value=pn_fwd_not_call_out)

        ###########################################
        # Root Frame
        tab_frame   = tk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=cfg.get('dest_call', 'NOCALL'))
        #################################################################
        # Frames
        pn_bbs_out_f       = tk.Frame(self, borderwidth=10)

        # Pack it
        pn_bbs_out_f.pack(     side=tk.TOP, expand=False, fill=tk.X)

        #################
        # pn_bbs_out_f


        return {
            'pn_fwd_bbs_out_var'        : pn_fwd_bbs_out_var,
            'pn_fwd_h_out_var'          : pn_fwd_h_out_var,
            'pn_fwd_not_h_out_var'      : pn_fwd_not_h_out_var,
            'pn_fwd_call_out_var'       : pn_fwd_call_out_var,
            'pn_fwd_not_call_out_var'   : pn_fwd_not_call_out_var,

        }

    def _get_fwdBBS_vars_fm_cfg(self):
        for k, fwd_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            if not fwd_cfg:
                logger.warning(self._logTag + f"Empty FWD-CFG for {k}")
                fwd_cfg = getNew_BBS_FWD_cfg()
            self._bbs_vars[fwd_cfg.get('dest_call', 'NOCALL')] = self._add_fwdBBS_pn_out_tab(fwd_cfg)


    ####################################
    def save_config(self):
        # self._get_user_data_fm_vars()
        pass
