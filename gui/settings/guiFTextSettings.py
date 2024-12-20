from cfg.popt_config import POPT_CFG
import tkinter as tk


class FTextSettings(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        ################################
        self._lang = POPT_CFG.get_guiCFG_language()

    def save_config(self):
        pass
        """
        conf: dict = POPT_CFG.load_guiPARM_main()
        old_conf = dict(conf)
        conf['gui_cfg_vor_col'] = str(self._fg_rx)
        conf['gui_cfg_vor_tx_col'] = str(self._fg_tx)
        conf['gui_cfg_vor_bg_col'] = str(self._bg_tx)
        lang_ind = LANG_IND.get(self._lang_var.get(), LANGUAGE)
        conf['gui_lang'] = int(lang_ind)
        conf['gui_cfg_locator'] = str(self._loc_var.get())
        conf['gui_cfg_qth'] = str(self._qth_var.get())


        POPT_CFG.set_guiPARM_main(conf)
        if old_conf == conf:
            return False
        return True
        """
