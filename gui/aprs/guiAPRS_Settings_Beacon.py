import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno

from cfg.constant import APRS_INET_PORT_ID, APRS_POS_BEACON_COMMENT_MAX
from cfg.default_config import getNew_APRS_beacon_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import validate_ax25Call
from fnc.gui_fnc import build_aprs_icon_tab
from fnc.str_fnc import get_strTab
from gui.aprs.guiAPRS_symbol_tab import APRSymbolTab
from schedule.guiPoPT_Scheduler import PoPT_Set_Scheduler
from schedule.popt_sched import getNew_schedule_config


class APRSbeaconSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style          = root_win.style
        self.style_name     = root_win.style_name
        self._root_win      = root_win
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._aprs_icon_tab = build_aprs_icon_tab((32, 32))
        ###################################
        # CFG
        ais_cfg:          dict  = self._root_win.get_aprs_cfg()
        self._beacon_cfg: dict  = ais_cfg.get('aprs_beacons', {})
        self.schedule_config    = getNew_schedule_config()
        self.selected_icon      = ''
        ###################################
        self.symbol_win   = None
        self.schedule_win = None
        ###################################
        # VAR's
        self._tab_vars    = {}
        ###################################
        fram_1 = ttk.Frame(self)
        fram_2 = ttk.Frame(self)
        fram_1.pack(fill='x',    expand=False,  padx=15, pady=15)
        fram_2.pack(fill='both', expand=False, padx=15, pady=15)
        ###################################
        ttk.Button(fram_1,
                   text=self._getTabStr('new'),
                   command=self._add_new_tab
                   ).pack(side='left', fill='x', expand=False)

        ttk.Button(fram_1,
                   text=self._getTabStr('delete'),
                   command=self._del_tab
                   ).pack(side='right', expand=False)
        ##
        self._tabctl = ttk.Notebook(fram_2)
        self._tabctl.pack(side='top', fill='both', expand=True)
        #self._tabctl.bind("<<NotebookTabChanged>>", self._select_hBBS_tab)
        ###################################

        if not self._beacon_cfg:
            self._add_new_tab()
        else:
            self._get_vars_fm_cfg()

    #############################################
    def _get_vars_fm_cfg(self):
        for k, cfg in self._beacon_cfg.items():
            if not cfg:
                logger.warning(f"Empty APRS-Beacon CFG for {k}")
                cfg = getNew_APRS_beacon_cfg()
            self._add_new_tab(cfg)


    def _add_new_tab(self, cfg=None):
        if not cfg:
            cfg = getNew_APRS_beacon_cfg()
            if cfg.get('be_from', '') in self._beacon_cfg:
                return {}
        ###########################################
        # VARs
        be_text_var           = tk.StringVar( self, value=cfg.get('be_text',            ''))
        be_from_var           = tk.StringVar( self, value=cfg.get('be_from',            'NOCALL'))
        be_via_var            = tk.StringVar( self, value=cfg.get('be_via',             ''))
        be_wide_var           = tk.StringVar( self, value=str(cfg.get('be_wide',        0)))
        be_enabled_var        = tk.BooleanVar(self, value=cfg.get('be_enabled',         True))

        port_opt  = list(POPT_CFG.get_port_CFGs().keys()) + [APRS_INET_PORT_ID]
        port_cfg  = cfg.get('be_ports',  [])
        port_vars = {}
        for port_id in port_opt:
            if str(port_id) in port_cfg:
                port_vars[str(port_id)] = tk.BooleanVar(self, value=True)
            else:
                port_vars[str(port_id)] = tk.BooleanVar(self, value=False)
        #
        ###########################################
        # Root Frame
        tab_frame   = ttk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=be_from_var.get())
        ###########################################
        # Frames
        frame_1      = ttk.Frame(tab_frame)
        frame_1.pack(expand=True,  fill='both')
        #################################################################
        # R Frame
        addr_f       = ttk.Frame(frame_1)
        ports_f      = ttk.Frame(frame_1)
        symbol_btn_f = ttk.Frame(frame_1)
        text_f       = ttk.Frame(frame_1)
        sched_btn_f  = ttk.Frame(frame_1)

        # Pack it
        addr_f.pack(            side='top',  expand=False, fill='x', padx=15, pady=10)
        ports_f.pack(           side='top',  expand=False, fill='x', padx=15, pady=10)
        symbol_btn_f.pack(      side='top',  expand=False, fill='x', padx=15, pady=10)
        text_f.pack(            side='top',  expand=False, fill='x', padx=15, pady=10)
        sched_btn_f.pack(       side='top',  expand=False, fill='x', padx=15, pady=10)

        #################
        # from_f
        my_call_f = ttk.Frame(addr_f)
        my_call_f.pack(side='left')
        opt = POPT_CFG.get_stat_CFG_keys()
        if opt:
            opt = [cfg.get('be_from', opt[0])] + opt

        ttk.Label(my_call_f, text=f"{self._getTabStr('from')}: ").pack(side='left', anchor='w')
        ttk.OptionMenu(my_call_f,
                       be_from_var, *opt,
                       command=lambda e :self._set_tab_key()).pack(side='left', anchor='w', padx=10)
        #################
        # via_f
        via_f = ttk.Frame(addr_f)
        via_f.pack(side='left')
        ttk.Label(via_f, text="VIA: ").pack(side='left', anchor='w')
        ttk.Entry(via_f, textvariable=be_via_var, width=20).pack(side='left', anchor='w', padx=10)
        #################
        # wide_f
        wide_f = ttk.Frame(addr_f)
        wide_f.pack(side='left')
        wide_opt = [str(cfg.get('be_wide', 0))] + [str(x) for x in range(0, 8)]
        ttk.Label(wide_f, text="WIDE: ").pack(side='left', anchor='w')
        ttk.OptionMenu(wide_f, be_wide_var, *wide_opt).pack(side='left', anchor='w', padx=10)
        ########-----------#########
        # ports_f
        ttk.Label(ports_f, text="Ports").pack(anchor='w')
        p_frame = ttk.Frame(ports_f)
        p_frame.pack(fill='x')
        for port_id, var in port_vars.items():
            ttk.Checkbutton(p_frame, variable=var, text=port_id).pack(side='left', padx=10)

        ########-----------#########
        # symbol_btn_f
        ttk.Button(symbol_btn_f,
                   text=f"Symbol/Icon",
                   command=self._open_IconWin
                   ).pack(side='left', anchor='w', padx=20)

        symbol_cfg = cfg.get('be_symbol', '')
        if not symbol_cfg:
            img = None
        else:
            sym1, sym2 = symbol_cfg
            img = self._aprs_icon_tab.get((sym1, sym2), None)
        if img is not None:
            icon_label       = ttk.Label(symbol_btn_f,image=img)
            icon_label.image = img
        else:
            icon_label = ttk.Label(symbol_btn_f)
        icon_label.pack(side='left',padx=10)
        ########-----------#########
        # text_f
        ttk.Label(text_f, text=f"{self._getTabStr('comment')} :").pack(side='top', anchor='w', padx=10, pady=10)
        ttk.Entry(text_f, textvariable=be_text_var, width=45).pack(side='top', anchor='w', padx=10)

        ########-----------#########
        # sched_btn_f
        ttk.Button(sched_btn_f,
                   text=f"{self._getTabStr('scheduler')}",
                   command=self._open_schedWin
                   ).pack(side='left', anchor='w', padx=20)
        ttk.Checkbutton(sched_btn_f,
                        text=self._getTabStr('active'),
                        variable=be_enabled_var).pack(side='right', anchor='e', padx=20)

        ret = {
            'be_text_var'           : be_text_var,
            'be_from_var'           : be_from_var,
            'be_via_var'            : be_via_var,
            'be_wide_var'           : be_wide_var,
            'be_enabled_var'        : be_enabled_var,
            'port_vars'             : port_vars,
            'icon_label'            : icon_label,
        }
        self._tab_vars[cfg.get('be_from', 'NOCALL')] = ret
        if cfg.get('be_from', '') not in self._beacon_cfg:
            self._beacon_cfg[cfg.get('be_from', 'NOCALL')] = cfg
        return ret

    def _del_tab(self):
        ret = askyesno(
            self._getTabStr('delete'),
            f"{self._getTabStr('delete')} ?",
            parent=self._root_win
        )
        if not ret:
            return
        cfg_key = self._get_sel_tabKey()
        if cfg_key:
            self._del_beacon_cfg(cfg_key)
            self._del_tab_vars(cfg_key)
            self._tabctl.forget(self._tabctl.select())

    def _del_tab_vars(self, cfg_key: str):
        if cfg_key in self._tab_vars.keys():
            del self._tab_vars[cfg_key]

    def _del_beacon_cfg(self, cfg_key: str):
        if cfg_key in self._beacon_cfg:
            del self._beacon_cfg[cfg_key]

    def _set_tab_key(self):
        ind = self._get_sel_tabKey()
        if not ind:
            return
        #if ind == 'NOCALL':
        #    self._set_NOCALL_tab()
        #    return
        tab_vars = self._tab_vars.get(ind, {})
        if not tab_vars:
            return
        try:
            from_call = tab_vars.get('be_from_var').get()
        except Exception as ex:
            logger.error(ex)
            return
        if not from_call:
            return
        if from_call in self._tab_vars:
            tab_vars.get('be_from_var').set(ind)
            return
        self._tab_vars[from_call] = dict(tab_vars)
        if ind in self._tab_vars:
            del self._tab_vars[ind]

        if ind not in self._beacon_cfg:
            self._beacon_cfg[from_call] = getNew_APRS_beacon_cfg()
        else:
            self._beacon_cfg[from_call] = dict(self._beacon_cfg[ind])
            del self._beacon_cfg[ind]
        self._beacon_cfg[from_call]['be_from'] = from_call
        self._set_tab_name(from_call)

    def _set_NOCALL_tab(self):
        nocall_vars = self._tab_vars.get('NOCALL', {})
        if nocall_vars:
            try:
                from_call: str = nocall_vars['be_from_var'].get()
            except Exception as ex:
                logger.error(ex)
                return
            if any((
                    from_call in self._tab_vars,
                    from_call in self._beacon_cfg
            )):
                nocall_vars.get('be_from_var').set('NOCALL')
                return

            self._tab_vars[from_call] = dict(nocall_vars)
            del self._tab_vars['NOCALL']
            self._set_tab_name(from_call)
            if 'NOCALL' not in self._beacon_cfg:
                self._beacon_cfg[from_call] = getNew_APRS_beacon_cfg()
            else:
                self._beacon_cfg[from_call] = dict(self._beacon_cfg['NOCALL'])
                del self._beacon_cfg['NOCALL']
            self._beacon_cfg[from_call] = getNew_APRS_beacon_cfg()
            self._beacon_cfg[from_call]['be_from'] = from_call

    #############################################
    def _select_tab(self, event=None):
        ind = self._get_sel_tabKey()
        if ind:
            self._select_scheCfg(ind)
            self._select_symbolCfg(ind)

    def _get_sel_tabKey(self):
        try:
            return self._tabctl.tab(self._tabctl.select(), "text")
        except tk.TclError:
            return ''

    def _set_tab_name(self, name):
        self._tabctl.tab(self._tabctl.select(), text=name)

    #############################################
    def _select_scheCfg(self, cfg_k: str):
        cfg = self._beacon_cfg.get(cfg_k, getNew_APRS_beacon_cfg())
        self.schedule_config = dict(cfg.get('be_scheduler_cfg', dict(getNew_schedule_config())))

    def _save_scheCfg(self, cfg_k: str):
        cfg = self._beacon_cfg.get(cfg_k, getNew_APRS_beacon_cfg())
        cfg['be_scheduler_cfg'] = dict(self.schedule_config)
        self._beacon_cfg[cfg_k] = dict(cfg)

    #############################################
    def _select_symbolCfg(self, cfg_k: str):
        cfg = self._beacon_cfg.get(cfg_k, getNew_APRS_beacon_cfg())
        self.selected_icon = str(cfg.get('be_symbol', ''))

    def _save_symbolCfg(self, cfg_k: str):
        cfg = self._beacon_cfg.get(cfg_k, getNew_APRS_beacon_cfg())
        cfg['be_symbol'] = str(self.selected_icon)
        self._beacon_cfg[cfg_k] = cfg
        # self._set_symbol(cfg_k)

    def _set_symbol(self, cfg_k: str):
        symbol     = self._beacon_cfg.get(cfg_k, getNew_APRS_beacon_cfg()).get('be_symbol', '')
        print(f"-- {symbol}")
        if not symbol:
            return
        sym1, sym2 = symbol
        img = self._aprs_icon_tab.get((sym1, sym2), None)
        if img is None:
            print('img none')
            return
        print(cfg_k)
        icon_label = self._tab_vars.get(cfg_k, {}).get('icon_label')
        icon_label: ttk.Label
        icon_label.configure(image=img)
        icon_label.image = img
        #self.update_idletasks()

    #############################################
    def _open_schedWin(self):
        """
        try:
            self.schedule_config['repeat_min'] = int(float(self.intervall_var.get()))
        except ValueError:
            pass
        try:
            self.schedule_config['move'] = int(float(self.move_var.get()))
        except ValueError:
            pass
        """
        if hasattr(self.schedule_win, 'lift'):
            self.schedule_win.lift()
            return
        ind = self._get_sel_tabKey()
        if not ind:
            return
        self._select_scheCfg(ind)
        PoPT_Set_Scheduler(self)

    def scheduler_config_save_task(self):
        """ Task fm PoPT-Scheduler_win"""
        ind = self._get_sel_tabKey()
        if ind:
            self._save_scheCfg(ind)

    #############################################
    def _open_IconWin(self):
        if hasattr(self.symbol_win, 'lift'):
            self.symbol_win.lift()
            return
        ind = self._get_sel_tabKey()
        if not ind:
            return
        self._select_symbolCfg(ind)
        APRSymbolTab(self)

    def icon_config_save_task(self):
        """ Task fm PoPT-Scheduler_win"""
        ind = self._get_sel_tabKey()
        if ind:
            self._save_symbolCfg(ind)
            self._set_symbol(ind)

    #############################################
    def _get_data_fm_vars(self):
        for k, tab_vars in dict(self._tab_vars).items():
            if k == 'NOCALL':
                continue
            tab_vars: dict
            selected_ports = []
            for port_id, port_var in tab_vars.get('port_vars', {}).items():
                if port_var.get():
                    selected_ports.append(port_id)

            from_call       = str(self._tab_vars[k]['be_from_var'].get()).upper()
            via_calls       = str(self._tab_vars[k]['be_via_var'].get() ).upper()

            temp = via_calls.split(' ')
            for call in temp:
                if not validate_ax25Call(call):
                    via_calls = ''
                    break
            try:
                wide = int(self._tab_vars[k]['be_wide_var'].get())
            except ValueError:
                wide = 0

            text = str(self._tab_vars[k]['be_text_var'].get()).replace('\n', '')[:APRS_POS_BEACON_COMMENT_MAX]

            cfg = self._beacon_cfg.get(k, getNew_APRS_beacon_cfg())
            cfg['be_text']      = text
            cfg['be_from']      = from_call
            cfg['be_via']       = via_calls
            cfg['be_wide']      = wide
            cfg['be_ports']     = selected_ports
            cfg['be_enabled']   = bool(self._tab_vars[k]['be_enabled_var'].get())
            if k != from_call:
                self._tab_vars[from_call] = dict(self._tab_vars[k])
                self._set_tab_name(from_call)
                del self._tab_vars[k]
            self._set_beacon_cfg(from_call, cfg)
        self._cleanup_cfg()

    def _set_beacon_cfg(self, cfg_k: str, cfg: dict):
        #if cfg_k == 'NOCALL':
        #    return
        self._beacon_cfg[cfg_k] = cfg


    def _cleanup_cfg(self):
        if self._beacon_cfg:
            #if self._beacon_cfg.get('NOCALL', None):
            #    #del self._ais_cfg['aprs_beacons']['NOCALL']
            #    self._del_beacon_cfg('NOCALL')
            for k in list(self._beacon_cfg.keys()):
                if k not in self._tab_vars.keys():
                    self._del_beacon_cfg(k)

    #############################################

    def save_config(self):
        # self._set_NOCALL_tab()
        self._get_data_fm_vars()
        self._root_win.set_beacon_cfg(dict(self._beacon_cfg))
        return True

    #############################################
    def get_icon_tab(self):
        return self._aprs_icon_tab

    #############################################
    def destroy_win(self):
        if hasattr(self.symbol_win, 'destroy_win'):
            self.symbol_win.destroy_win()
        if hasattr(self.schedule_win, 'destroy_win'):
            self.schedule_win.destroy_win()
        self.destroy()