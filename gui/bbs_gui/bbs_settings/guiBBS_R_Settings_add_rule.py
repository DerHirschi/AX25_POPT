import tkinter as tk

from cfg.default_config import getNew_BBS_FWD_cfg
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.str_fnc import get_strTab


class BBS_addRuleWin(tk.Toplevel):
    def __init__(self, root_win, dest_call:str, opt_index: int):
        tk.Toplevel.__init__(self, master=root_win)
        self._logTag = "BBS_addRuleWin> "
        win_width = 430
        win_height = 170
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._lang          = POPT_CFG.get_guiCFG_language()
        self._getTabStr     = lambda str_k: get_strTab(str_k, self._lang)
        self._root_win      = root_win
        self._root_win.add_win = self
        self.title(f"Add Rule - {dest_call}")
        ####################################################
        # CFG
        self._dest_call     = dest_call
        self._rule_opt      = opt_index
        self._pms_cfg: dict = self._root_win.get_root_pms_cfg()
        self._fwd_bbs_cfg   = self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, getNew_BBS_FWD_cfg())
        ####################################################
        # OPT
        """
        0 = P-In
        1 = P-Out
        2 = BL-In
        3 = BL-Out
        """
        """
        opt_tab = {
            0: ('BBS', '!BBS', 'H', '!H', 'CALL', '!CALL'),
            1: ('BBS', '!BBS', 'H', '!H', 'CALL', '!CALL'),
            2: ('THEME', '!THEME', 'DIST', '!DIST'),
            3: ('THEME', '!THEME', 'DIST', '!DIST'),
        }
        """

        opt_tab = {
            0: ('BBS', '!BBS', 'H', '!H', 'CALL', '!CALL'),
            1: ('THEME', '!THEME', 'DIST', '!DIST'),
        }

        default_opt = opt_tab.get(opt_index, ())
        if not default_opt:
            logger.error(self._logTag + f"Wrong Opt (opt_index): {opt_index}")
            self.destroy_win()
            return
        ####################################################
        # Vars

        self._opt_var   = tk.StringVar(self, value=default_opt[0])
        self._ent_var   = tk.StringVar(self, value='')
        ####################################################
        # Frames
        upper_frame = tk.Frame(self)
        upper_frame.pack(expand=True, fill=tk.BOTH)
        optM_frame  = tk.Frame(upper_frame)
        entry_frame = tk.Frame(upper_frame)
        optM_frame.pack( expand=False, fill=tk.X, padx=10, pady=10)
        entry_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)

        optM        = tk.OptionMenu(
            optM_frame,
            self._opt_var,
            *default_opt
        )
        optM.pack(side=tk.LEFT, expand=False, padx=30)

        opt_ent     = tk.Entry(
            entry_frame,
            textvariable=self._ent_var,
            width=15
            # validate=,
            # validatecommand=
        )
        opt_ent.pack(side=tk.LEFT, expand=False, padx=30)

        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=10)
        save_btn  = tk.Button(btn_frame, text=self._getTabStr('save'),   command=self._save_btn)
        abort_btn = tk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        save_btn.pack( side=tk.LEFT)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    def _save_btn(self):
        rule_opt  = self._opt_var.get()
        opt_ent   = self._ent_var.get().replace(' ', '').upper()
        """
        0 = P-In
        1 = P-Out
        2 = BL-In
        3 = BL-Out
        0: ('BBS', '!BBS', 'H', '!H', 'CALL', '!CALL'),
        1: ('BBS', '!BBS', 'H', '!H', 'CALL', '!CALL'),
        2: ('THEME', '!THEME', 'DIST', '!DIST'),
        3: ('THEME', '!THEME', 'DIST', '!DIST'),
        """
        rule_cfg_name = {

            0: {    # P-OUT
                'BBS':      'pn_fwd_bbs_out',
                '!BBS':     'pn_fwd_not_bbs_out',
                'H':        'pn_fwd_h_out',
                '!H':       'pn_fwd_not_h_out',
                'CALL':     'pn_fwd_call_out',
                '!CALL':    'pn_fwd_not_call_out',
            },

            1: {  # BL-OUT
                'THEME':    'bl_top_out',
                '!THEME':   'bl_top_not_out',
                'DIST':     'bl_dist_out',
                '!DIST':    'bl_dist_not_out',
            },
        }.get(self._rule_opt, {}).get(rule_opt, '')
        if not rule_cfg_name:
            logger.error(self._logTag + f"No rule_cfg_name: self._rule_opt:{self._rule_opt} - rule_opt: {rule_opt}")
            return
        rule      = list(self._fwd_bbs_cfg.get(rule_cfg_name, []))
        rule.append(str(opt_ent))
        self._fwd_bbs_cfg[rule_cfg_name] = rule
        if hasattr(self._root_win, 'update_tabs'):
            self._root_win.update_tabs()
        self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        if hasattr(self._root_win, 'lift'):
            self._root_win.lift()
        self._root_win.add_win = None
        self.destroy()

