"""
TODO:
    - F-Texte
FIXME:
    - Keine sysMSG für änderung d Station-Settings.(Nur neue/gelöschte o geänderte Calls werden returned)
    - Keine sysMSG für änderung d Port-Settings.(Nur neue o gelöschte Ports werden returned)
"""
import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab, lob_gen
from gui.guiError import PoPTAttributError
from gui.settings.guiBeaconSettings import BeaconSettings
from gui.settings.guiDigiSettings import DIGI_SettingsWin
from gui.settings.guiFTextSettings import FTextSettings
from gui.settings.guiGeneralSettings import GeneralSettings
from gui.settings.guiMCastSettings import MulticastSettings
from gui.settings.guiPortSettings import PortSettingsWin
from gui.settings.guiRxEchoSettings import RxEchoSettings
from gui.settings.guiStationSettings import StationSettingsWin



class SettingsMain(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        win_width = 1200
        win_height = 640
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.main_win.winfo_x()}+"
                      f"{root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.attributes("-topmost", True)
        self.resizable(True, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._lang = POPT_CFG.get_guiCFG_language()
        self.title(get_strTab(str_key='settings', lang_index=self._lang))
        self._root_win = root_win
        self._root_win.settings_win = self
        ###############################################################
        self._win_tab = {
            'general_settings': GeneralSettings,
            'stat_settings': StationSettingsWin,
            'port': PortSettingsWin,
            'beacon_settings': BeaconSettings,
            'Digipeater': DIGI_SettingsWin,
            'F-Text': FTextSettings,
            'MCast': MulticastSettings,
            'RX-Echo': RxEchoSettings,
        }
        ###############################################################

        ###########################################
        # Nix Tree
        style = ttk.Style(self)
        style.configure('lefttab.TNotebook', tabposition='wn')
        self._tabControl = ttk.Notebook(self, style='lefttab.TNotebook')
        # self._tabControl.bind('<<NotebookTabChanged>>', self._tab_change)
        self._tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        # Tab Vars
        self._tab_list = {}
        for strTab_name, frame in self._win_tab.items():
            tab = frame(self._tabControl, self)
            self._tab_list[strTab_name] = tab
            port_lable_text = f"{get_strTab(str_key=strTab_name, lang_index=self._lang).ljust(12)}"
            self._tabControl.add(tab, text=port_lable_text)

        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        ok_btn = tk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)


        save_btn = tk.Button(btn_frame, text=get_strTab(str_key='save', lang_index=self._lang), command=self._save_btn)
        save_btn.pack(side=tk.LEFT)

        abort_btn = tk.Button(btn_frame, text=get_strTab(str_key='cancel', lang_index=self._lang), command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    ################################################
    def _reinit_tabs(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            ind = None

        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'destroy_win'):
                tab.destroy_win()
            else:
                tab.destroy()

        self._tab_list = {}
        for strTab_name, frame in self._win_tab.items():
            tab = frame(self._tabControl, self)
            self._tab_list[strTab_name] = tab
            port_lable_text = f"{get_strTab(str_key=strTab_name, lang_index=self._lang).ljust(12)}"
            self._tabControl.add(tab, text=port_lable_text)

        if ind is not None:
            self._tabControl.select(ind)

    ################################################

    def get_PH(self):
        return self._root_win.get_PH_manGUI()

    ################################################
    def _save_cfg(self):
        reinit_tr = False
        set_tag = False
        # self.attributes('-topmost', 1)
        # self.attributes('-topmost', 0)
        # self.lower()
        for strTab_name, tab in self._tab_list.items():
            if not (hasattr(tab, 'save_config')):
                raise PoPTAttributError
            if tab.save_config():
                # FIXME: Keine sysMSG für änderung d. Station-Settings. (Nur neue o geänderte Calls werden returned)
                self._root_win.sysMsg_to_monitor(
                    get_strTab('setting_saved', self._lang).format(get_strTab(strTab_name, self._lang))
                )

                if strTab_name in ['stat_settings', 'port']:
                    set_tag = True
                    reinit_tr = True
                if strTab_name in ['general_settings']:
                    set_tag = True

        if reinit_tr:   # New Station | Station deleted
            self._reinit_tabs()
            self._root_win.tabbed_sideFrame.update_mon_port_id()
        if set_tag:
            self._root_win.set_text_tags()


    ################################################
    def _ok_btn(self):
        # self._root_win.set_text_tags()
        # self._root_win.tabbed_sideFrame.update_mon_port_id()
        self._root_win.sysMsg_to_monitor(get_strTab('hin1', self._lang))
        lob = lob_gen(self._lang)
        self._root_win.sysMsg_to_monitor(get_strTab(lob, self._lang))
        self.destroy_win()

    def _save_btn(self):
        self._save_cfg()
        POPT_CFG.save_PORT_CFG_to_file()
        POPT_CFG.save_MAIN_CFG_to_file()
        lob = lob_gen(self._lang)
        self._root_win.sysMsg_to_monitor(get_strTab(lob, self._lang))

    def _abort_btn(self):
        self._root_win.sysMsg_to_monitor(get_strTab('hin2', self._lang))
        self.destroy_win()

    def destroy_win(self):
        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'destroy_win'):
                tab.destroy_win()

        self._root_win.settings_win = None
        self.destroy()
