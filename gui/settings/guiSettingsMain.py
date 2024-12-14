import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
from gui.guiError import PoPTAttributError
from gui.settings.guiBeaconSettings import BeaconSettings
from gui.settings.guiDigiSettings import DIGI_SettingsWin
from gui.settings.guiMCastSettings import MulticastSettings
from gui.settings.guiPortSettings import PortSettingsWin
from gui.settings.guiRxEchoSettings import RxEchoSettings
from gui.settings.guiStationSettings import StationSettingsWin


class SettingsMain(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        win_width = 1200
        win_height = 800
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
        self._lang = POPT_CFG.get_guiCFG_language()
        self.title(STR_TABLE['settings'][self._lang])
        self._root_win = root_win
        self._root_win.settings_win = self
        ###############################################################
        self._win_tab = {
            'stat_settings': StationSettingsWin,
            'port': PortSettingsWin,
            'beacon_settings': BeaconSettings,
            'Digipeater': DIGI_SettingsWin,
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
            try:
                port_lable_text = f'{str(STR_TABLE[strTab_name][self._lang]).ljust(12)}'
            except (KeyError, IndexError):
                port_lable_text = f'{strTab_name.ljust(12)}'
            self._tabControl.add(tab, text=port_lable_text)

        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        ok_btn = tk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_frame, text=STR_TABLE['save'][self._lang], command=self._save_btn)
        save_btn.pack(side=tk.LEFT)

        abort_btn = tk.Button(btn_frame, text=STR_TABLE['cancel'][self._lang], command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    ################################################
    def _reinit_tabs(self):
        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'destroy_win'):
                tab.destroy_win()
            else:
                tab.destroy()

        self._tab_list = {}
        for strTab_name, frame in self._win_tab.items():
            tab = frame(self._tabControl, self)
            self._tab_list[strTab_name] = tab
            try:
                port_lable_text = f'{str(STR_TABLE[strTab_name][self._lang]).ljust(12)}'
            except (KeyError, IndexError):
                port_lable_text = f'{strTab_name.ljust(12)}'
            self._tabControl.add(tab, text=port_lable_text)

    ################################################

    def get_PH(self):
        return self._root_win.get_PH_manGUI()

    ################################################
    def _save_cfg(self):
        reinit_tr = False
        for strTab_name, tab in self._tab_list.items():
            if not (hasattr(tab, 'save_config')):
                raise PoPTAttributError
            if tab.save_config():
                reinit_tr = True
        if reinit_tr:
            self._reinit_tabs()

    ################################################
    def _ok_btn(self):
        self._root_win.set_text_tags()
        self._root_win.tabbed_sideFrame.update_mon_port_id()
        self.destroy_win()

    def _save_btn(self):
        self._save_cfg()
        POPT_CFG.save_PORT_CFG_to_file()
        POPT_CFG.save_MAIN_CFG_to_file()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        for strTab_name, tab in self._tab_list.items():
            if hasattr(tab, 'destroy_win'):
                tab.destroy_win()

        self._root_win.settings_win = None
        self.destroy()

    # STAT-SETT: self._root_win.set_text_tags()
    # PORT-SETT: self._root_win.tabbed_sideFrame.update_mon_port_id()

    """
        def _save_btn_cmd(self):
        # TODO Cleanup
        PORT_HANDLER.disco_all_Conn()

        #self.settings_win.attributes("-topmost", False)
        #self.settings_win.lower()
        messagebox.showinfo(STR_TABLE['all_station_get_disco_hint_1'][self._lang], STR_TABLE['all_station_get_disco_hint_2'][self._lang])
        #self.settings_win.lift()

        # self.settings_win.attributes("-topmost", True)
        time.sleep(1)  # TODO Quick fix
        # TODO PORT_HANDLER.is_all_disco()
        PORT_HANDLER.disco_all_Conn()
        self._set_all_vars_to_cfg()
        self._save_cfg_to_file()
        #self._root_win.sysMsg_to_monitor(STR_TABLE['lob1'][self._lang])

    def _ok_btn_cmd(self):
        # TODO Cleanup
        if not PORT_HANDLER.is_all_disco():
            PORT_HANDLER.disco_all_Conn()
            messagebox.showerror(STR_TABLE['not_all_station_disco_hint_1'][self._lang], STR_TABLE['not_all_station_disco_hint_2'][self._lang])
            #self.settings_win.lift()
            return
        self._set_all_vars_to_cfg()
        self._save_cfg_to_file()
        #self._root_win.sysMsg_to_monitor(STR_TABLE['hin1'][self._lang])
        #self._root_win.sysMsg_to_monitor(STR_TABLE['lob2'][self._lang])

        self.destroy()
    
    """
