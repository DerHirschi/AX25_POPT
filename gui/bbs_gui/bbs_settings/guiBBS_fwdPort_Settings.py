import tkinter as tk
from tkinter import ttk

from cfg.default_config import getNew_BBS_Port_cfg
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.str_fnc import get_strTab


class BBS_FWD_PortSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._logTag    = 'BBS_fwdPort_Settings: '
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict     = dict(self._root_win.get_root_pms_cfg())
        ###################################
        # Vars
        self._gui_vars = {}
        ###########################################

        ttk.Label(self, text='FWD-Ports').pack(side=tk.TOP, expand=False)
        r_tab_frame = ttk.Frame(self, borderwidth=10)

        r_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #############
        # r_tab_frame
        self._tabctl = ttk.Notebook(r_tab_frame)
        self._tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # self._tabctl.bind("<<NotebookTabChanged>>", self._select_hBBS_tab)
        ########################
        self._get_fwdPort_vars_fm_cfg()

    def _get_fwdPort_vars_fm_cfg(self):
        fwd_port_cfg = self._pms_cfg.get('fwd_port_cfg', {})
        ax_port_ids  = list(POPT_CFG.get_port_CFGs().keys())

        for port_id in ax_port_ids:
            port_cfg = fwd_port_cfg.get(port_id, getNew_BBS_Port_cfg())
            self._gui_vars[port_id] = self._add_fwdPort_tab(port_cfg, port_id)

    def _add_fwdPort_tab(self, cfg=None, port_id=0):
        if not cfg:
            cfg = getNew_BBS_Port_cfg()
        ###########################################
        # VARs
        block_time_var   = tk.StringVar(self, value=cfg.get('block_time', '30'))
        send_limit_var   = tk.StringVar(self, value=cfg.get('send_limit', '5'))
        conn_limit_var   = tk.StringVar(self, value=cfg.get('conn_limit', '1'))

        ###########################################
        # Root Frame
        tab_frame = ttk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=f"Port {port_id}")
        ###########################################
        # L/R Frames
        l_frame = ttk.Frame(tab_frame, borderwidth=10)
        #r_frame = tk.Frame(tab_frame, borderwidth=10)

        l_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        #ttk.Separator(tab_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, expand=False)
        #r_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        ###########################################
        # L Frame
        block_time_f = ttk.Frame(l_frame, borderwidth=10)
        send_limit_f = ttk.Frame(l_frame, borderwidth=10)
        conn_limit_f = ttk.Frame(l_frame, borderwidth=10)

        # Pack it
        block_time_f.pack(side=tk.TOP, expand=False, fill=tk.X)
        send_limit_f.pack(side=tk.TOP, expand=False, fill=tk.X)
        conn_limit_f.pack(side=tk.TOP, expand=False, fill=tk.X)

        ##################################
        #
        ttk.Label(block_time_f, text='Block Time (Min): ').pack(side=tk.LEFT, expand=False)
        ttk.Spinbox(block_time_f,
                   textvariable=block_time_var,
                   from_=5,
                   to=240,
                   increment=1,
                   width=3
                   ).pack(side=tk.LEFT, expand=False)
        #
        ttk.Label(send_limit_f, text='Send Limit (kB/Block): ').pack(side=tk.LEFT, expand=False)
        ttk.Spinbox(send_limit_f,
                   textvariable=send_limit_var,
                   from_=1,
                   to=500,
                   increment=1,
                   width=3
                   ).pack(side=tk.LEFT, expand=False)
        #
        ttk.Label(conn_limit_f, text='Connection Limit: ').pack(side=tk.LEFT, expand=False)
        ttk.Spinbox(conn_limit_f,
                   textvariable=conn_limit_var,
                   from_=1,
                   to=10,
                   increment=1,
                   width=3
                   ).pack(side=tk.LEFT, expand=False)


        return {
            'block_time_var': block_time_var,
            'send_limit_var': send_limit_var,
            'conn_limit_var': conn_limit_var,

        }

    def _set_cfg_fm_GUIvars(self):
        for port_id, gui_var_tab in self._gui_vars.items():
            try:
                block_time_var   = int(gui_var_tab['block_time_var'].get())
                send_limit_var   = int(gui_var_tab['send_limit_var'].get())
                conn_limit_var   = int(gui_var_tab['conn_limit_var'].get())
            except ValueError as e:
                logger.error(self._logTag + f"_set_cfg_fm_GUIvars ({e}) - Port:{port_id}")
                continue

            fwd_port_cfg = self._pms_cfg.get('fwd_port_cfg', {}).get(port_id, getNew_BBS_Port_cfg())
            fwd_port_cfg['block_time']     = block_time_var
            fwd_port_cfg['send_limit']     = send_limit_var
            fwd_port_cfg['conn_limit']     = conn_limit_var
            self._pms_cfg['fwd_port_cfg'][port_id] = fwd_port_cfg
    #####################################
    def update_win(self):
        pass

    def save_config(self):
        self._set_cfg_fm_GUIvars()
        return True