import tkinter as tk
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class BBSSwapSettings(ttk.Frame):
    def __init__(self, tabctl, root_win):
        ttk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._logTag    = 'BBS_SWAP_Settings: '
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict     = dict(self._root_win.get_root_pms_cfg())
        # self._rej_tab: list     = self._pms_cfg.get('reject_tab', [])
        ###################################
        # Vars
        self._sort_rev          = False
        self._last_sort_col     = {}
        self._tree_data         = []
        self._selected_items    = []
        ###########################################

    def update_win(self):
        pass