import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab, lob_gen
from gui.bbs_gui.bbs_settings.guiBBS_Gereral_Settings import BBSGeneralSettings
from gui.bbs_gui.bbs_settings.guiBBS_FWD_Settings import BBS_FWD_Settings
from gui.bbs_gui.bbs_settings.guiBBS_Reject_Settings import BBSRejectSettings
from gui.bbs_gui.bbs_settings.guiBBS_Routing_Settings import BBSRoutingSettings


class BBSSettingsMain(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        win_width = 1200
        win_height = 660
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.main_win.winfo_x()}+"
                      f"{root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.attributes("-topmost", True)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._lang      = POPT_CFG.get_guiCFG_language()
        self._bbs_obj   = PORT_HANDLER.get_bbs()
        self._getTabStr = lambda str_k: get_strTab(str_k, self._lang)
        self._root_win  = root_win
        self.add_win    = None
        self._root_win.settings_win = self
        self.title("PMS/BBS-" + self._getTabStr('settings'))
        ###############################################################
        self._pms_cfg   = POPT_CFG.get_BBS_cfg()
        ###############################################################
        self._win_tab   = {
            'general_settings'  : BBSGeneralSettings,
            'fwd_settings'      : BBS_FWD_Settings,
            'routing_settings'  : BBSRoutingSettings,
            'reject_settings'   : BBSRejectSettings,
        }
        ###############################################################

        ###########################################
        # Nix Tree
        style = ttk.Style(self)
        style.configure('lefttab.TNotebook', tabposition='wn')
        self._tabControl = ttk.Notebook(self, style='lefttab.TNotebook')
        # self._tabControl.bind('<<NotebookTabChanged>>', self._tab_change)
        self._tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        ###########################################
        # Tab Vars
        self._tab_list = {}
        for strTab_name, frame in self._win_tab.items():
            tab = frame(self._tabControl, self)
            self._tab_list[strTab_name] = tab
            port_lable_text = f"{self._getTabStr(strTab_name).ljust(12)}"
            self._tabControl.add(tab, text=port_lable_text)

        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        ok_btn = tk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)


        save_btn = tk.Button(btn_frame, text=self._getTabStr('save'), command=self._save_btn)
        save_btn.pack(side=tk.LEFT)

        abort_btn = tk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    ################################################
    def get_root_pms_cfg(self):
        return self._pms_cfg

    def get_root_bbs_obj(self):
        return self._bbs_obj

    ################################################
    def set_homeBBS_cfg(self, pms_cfg_k: str, bbs_cfg: dict):
        self._pms_cfg['fwd_bbs_cfg'][pms_cfg_k] = dict(bbs_cfg)

    def del_homeBBS_cfg(self, pms_cfg_k: str):
        if pms_cfg_k in self._pms_cfg['fwd_bbs_cfg'].keys():
            self._pms_cfg['fwd_bbs_cfg'][pms_cfg_k] = None
            del self._pms_cfg['fwd_bbs_cfg'][pms_cfg_k]

    def _save_cfg(self):
        for strTab_name, tab in self._tab_list.items():
            if not (hasattr(tab, 'save_config')):
                continue
            if tab.save_config():
                self._root_win.sysMsg_to_monitor(
                    self._getTabStr('setting_saved').format(self._getTabStr(strTab_name))
                )
        if 'NOCALL' in self._pms_cfg.get('fwd_bbs_cfg', {}).keys():
            del self._pms_cfg['fwd_bbs_cfg']['NOCALL']
        POPT_CFG.set_BBS_cfg(self._pms_cfg)
        if not self._bbs_obj:
            return False
        self._bbs_obj.set_pms_cfg()

    ################################################
    def _ok_btn(self):
        self._root_win.sysMsg_to_monitor(self._getTabStr('hin1'))
        self._root_win.sysMsg_to_monitor(lob_gen(self._lang))
        self.destroy_win()

    def _save_btn(self):
        self._save_cfg()
        # POPT_CFG.save_PORT_CFG_to_file()
        # POPT_CFG.save_MAIN_CFG_to_file()
        self._root_win.sysMsg_to_monitor(lob_gen(self._lang))

    def _abort_btn(self):
        self._root_win.sysMsg_to_monitor(self._getTabStr('hin2'))
        self.destroy_win()

    def update_tabs(self):
        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'update_win'):
                tab.update_win()

    def destroy_win(self):
        if hasattr(self.add_win, 'destroy'):
            self.add_win.destroy()
        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'destroy_win'):
                tab.destroy_win()
        self._root_win.settings_win = None
        self.destroy()

