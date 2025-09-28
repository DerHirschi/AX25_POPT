import tkinter as tk
from tkinter import ttk

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import lob_gen, get_strTab
from gui.aprs.guiAPRS_Settings_AIS import APRSaisSettings
from gui.aprs.guiAPRS_Settings_Beacon import APRSbeaconSettings


class APRSSettingsMain(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        win_width       = 800
        win_height      = 550
        self._root_win  = root_win
        self.style      = root_win.style
        self.style_name = root_win.style_name
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
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        self._root_win.settings_win = self
        ###############################################################
        self._lang      = POPT_CFG.get_guiCFG_language()
        self._getTabStr = lambda str_k: get_strTab(str_k, self._lang)
        self.icon_win   = None
        self.title("APRS-" + self._getTabStr('settings'))
        ###############################################################
        self._ais_cfg: dict   = POPT_CFG.get_CFG_aprs_ais()
        ###############################################################
        self._win_tab   = {
            'aprs_server'       : APRSaisSettings,
            'beacon_settings'   : APRSbeaconSettings,
        }
        ###############################################################
        main_f = ttk.Frame(self)
        main_f.pack(fill='both', expand=True)
        ###########################################
        # Nix Tree
        style = ttk.Style(self)
        style.configure('lefttab.TNotebook', tabposition='wn')
        self._tabControl = ttk.Notebook(main_f, style='lefttab.TNotebook')
        # self._tabControl.bind('<<NotebookTabChanged>>', self._tab_change)
        self._tabControl.pack(expand=True, fill='both', padx=10, pady=10)
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
        btn_frame = ttk.Frame(main_f, height=50)
        btn_frame.pack(expand=False, fill='x', padx=10, pady=10)
        ok_btn = ttk.Button(btn_frame, text=self._getTabStr('OK'), command=self._ok_btn)
        ok_btn.pack(side='left')


        save_btn = ttk.Button(btn_frame, text=self._getTabStr('save'), command=self._save_btn)
        save_btn.pack(side='left')

        abort_btn = ttk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        abort_btn.pack(side='right', anchor='e')

    ################################################

    ################################################

    ################################################
    def _save_cfg(self):
        try:
            ais = self._root_win.get_AIS_mainGUI()
            ais.save_conf_to_file()

        except Exception as ex:
            logger.error(ex)
            return

        self._ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        for strTab_name, tab in self._tab_list.items():
            if not (hasattr(tab, 'save_config')):
                continue
            if tab.save_config():
                self._root_win.sysMsg_to_monitor(
                    self._getTabStr('setting_saved').format(self._getTabStr(strTab_name))
                )
        old_cfg = POPT_CFG.get_CFG_aprs_ais()
        if old_cfg == self._ais_cfg:
            return
        try:
            POPT_CFG.set_CFG_aprs_ais(self._ais_cfg)
            ais = self._root_win.get_AIS_mainGUI()
            ais.reinit()
        except Exception as ex:
            logger.error(ex)

    """
    def del_beacon_cfg(self, cfg_key: str):
        if cfg_key in self._ais_cfg['aprs_beacons'].keys():
            #self._ais_cfg['aprs_beacons'][cfg_key] = None
            del self._ais_cfg['aprs_beacons'][cfg_key]
            #self._reinit_beacon_tabs()
    """

    def set_beacon_cfg(self, cfg: dict):
        if 'NOCALL' in cfg:
            del cfg['NOCALL']
        self._ais_cfg['aprs_beacons'] = dict(cfg)

    ################################################
    def _ok_btn(self):
        self._root_win.sysMsg_to_monitor(self._getTabStr('hin1'))
        self._root_win.sysMsg_to_monitor(lob_gen(self._lang))
        self.destroy_win()

    def _save_btn(self):
        self._save_cfg()
        self._root_win.sysMsg_to_monitor(lob_gen(self._lang))

    def _abort_btn(self):
        self._root_win.sysMsg_to_monitor(self._getTabStr('hin2'))
        self.destroy_win()

    """
    def update_tabs(self):
        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'update_win'):
                tab.update_win()
    """

    def get_aprs_cfg(self):
        return self._ais_cfg

    def destroy_win(self):
        if hasattr(self.icon_win, 'destroy_win'):
            self.icon_win.destroy_win()
        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'destroy_win'):
                tab.destroy_win()
        self._root_win.settings_win = None
        self.destroy()

