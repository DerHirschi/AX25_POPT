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
        self._bbs_vars      = {}
        self._sort_rev      = False
        self._last_sort_col = {}
        ###################################
        # Tabctl
        self._tabctl = ttk.Notebook(self)
        self._tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # self._tabctl.bind("<<NotebookTabChanged>>", self._select_hBBS_tab)

        ##########################
        # Init
        self._get_fwdBBS_vars_fm_cfg()

        self._update_all_trees()



    def _add_fwdBBS_pn_out_tab(self, cfg=None):
        if not cfg:
            cfg = getNew_BBS_FWD_cfg()
        """
        ###########################################
        # VARs
        pn_fwd_bbs_out          = ' '.join(cfg.get('pn_fwd_bbs_out',      []))
        pn_fwd_not_bbs_out      = ' '.join(cfg.get('pn_fwd_not_bbs_out',  []))
        pn_fwd_h_out            = ' '.join(cfg.get('pn_fwd_h_out',        []))
        pn_fwd_not_h_out        = ' '.join(cfg.get('pn_fwd_not_h_out',    []))
        pn_fwd_call_out         = ' '.join(cfg.get('pn_fwd_call_out',     []))
        pn_fwd_not_call_out     = ' '.join(cfg.get('pn_fwd_not_call_out', []))

        pn_fwd_bbs_out_var      = tk.StringVar(self, value=pn_fwd_bbs_out)
        pn_fwd_not_bbs_out_var  = tk.StringVar(self, value=pn_fwd_not_bbs_out)
        pn_fwd_h_out_var        = tk.StringVar(self, value=pn_fwd_h_out)
        pn_fwd_not_h_out_var    = tk.StringVar(self, value=pn_fwd_not_h_out)
        pn_fwd_call_out_var     = tk.StringVar(self, value=pn_fwd_call_out)
        pn_fwd_not_call_out_var = tk.StringVar(self, value=pn_fwd_not_call_out)
        """
        ###########################################
        # Root Frame
        tab_frame   = tk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=cfg.get('dest_call', 'NOCALL'))
        ###########################################
        # Local TabCtrl
        tabctl = ttk.Notebook(tab_frame)
        tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        p_incoming_frame  = tk.Frame(tabctl)
        p_outgoing_frame  = tk.Frame(tabctl)
        bl_incoming_frame = tk.Frame(tabctl)
        bl_outgoing_frame = tk.Frame(tabctl)
        tabctl.add(p_incoming_frame,  text='P-Incoming')
        tabctl.add(p_outgoing_frame,  text='P-Outgoing')
        tabctl.add(bl_incoming_frame, text='BL-Incoming')
        tabctl.add(bl_outgoing_frame, text='BL-Outgoing')
        #################################################################
        # Frames
        pn_label_f          = tk.Frame(p_outgoing_frame)
        pn_bbs_out_f        = tk.Frame(p_outgoing_frame)
        pn_not_bbs_out_f    = tk.Frame(p_outgoing_frame)
        pn_h_out_f          = tk.Frame(p_outgoing_frame)
        pn_not_h_out_f      = tk.Frame(p_outgoing_frame)
        pn_call_out_f       = tk.Frame(p_outgoing_frame)
        pn_not_call_out_f   = tk.Frame(p_outgoing_frame)

        # Pack it

        pn_label_f.pack(         side=tk.TOP,  expand=False,fill=tk.X)
        pn_bbs_out_f.pack(       side=tk.LEFT, expand=True, fill=tk.BOTH)
        pn_not_bbs_out_f.pack(   side=tk.LEFT, expand=True, fill=tk.BOTH)
        pn_h_out_f.pack(         side=tk.LEFT, expand=True, fill=tk.BOTH)
        pn_not_h_out_f.pack(     side=tk.LEFT, expand=True, fill=tk.BOTH)
        pn_call_out_f.pack(      side=tk.LEFT, expand=True, fill=tk.BOTH)
        pn_not_call_out_f.pack(  side=tk.LEFT, expand=True, fill=tk.BOTH)

        #############################################
        tk.Label(pn_label_f,
                 text=self._getTabStr('bbs_sett_pn_bbs_out'),
                 height=2
                 ).pack(side=tk.TOP, expand=False, fill=tk.X)
        #############################################
        # pn_bbs_out_f
        pn_bbs_out_tree = ttk.Treeview(pn_bbs_out_f, columns=('c1',), show='headings', )
        pn_bbs_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_bbs_out_tree.heading('c1', text='BBS', command=lambda: self._sort_entry('c1', pn_bbs_out_tree))
        pn_bbs_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        #############################################
        # pn_not_bbs_out_f
        pn_nbbs_out_tree = ttk.Treeview(pn_not_bbs_out_f, columns=('c1',), show='headings', )
        pn_nbbs_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_nbbs_out_tree.heading('c1', text='!BBS', command=lambda: self._sort_entry('c1', pn_nbbs_out_tree))
        pn_nbbs_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        #################
        # pn_h_out_f
        pn_h_out_tree = ttk.Treeview(pn_h_out_f, columns=('c1',), show='headings')
        pn_h_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_h_out_tree.heading('c1', text='H', command=lambda: self._sort_entry('c1', pn_h_out_tree))
        pn_h_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)

        #################
        # pn_not_h_out_f
        pn_nh_out_tree = ttk.Treeview(pn_not_h_out_f, columns=('c1',), show='headings')
        pn_nh_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_nh_out_tree.heading('c1', text='!H', command=lambda: self._sort_entry('c1', pn_nh_out_tree))
        pn_nh_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)

        #################
        # pn_call_out_f
        pn_call_out_tree = ttk.Treeview(pn_call_out_f, columns=('c1',), show='headings')
        pn_call_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_call_out_tree.heading('c1', text='CALL', command=lambda: self._sort_entry('c1', pn_call_out_tree))
        pn_call_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)

        #################
        # pn_not_call_out_f
        pn_ncall_out_tree = ttk.Treeview(pn_not_call_out_f, columns=('c1',), show='headings')
        pn_ncall_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_ncall_out_tree.heading('c1', text='!CALL', command=lambda: self._sort_entry('c1', pn_ncall_out_tree))
        pn_ncall_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)


        return {
            'pn_bbs_out_tree':          pn_bbs_out_tree,
            'pn_nbbs_out_tree':         pn_nbbs_out_tree,
            'pn_h_out_tree':            pn_h_out_tree,
            'pn_nh_out_tree':           pn_nh_out_tree,
            'pn_call_out_tree':         pn_call_out_tree,
            'pn_ncall_out_tree':        pn_ncall_out_tree,
        }

    def _update_all_trees(self):
        for dest_call, tree_cfg in self._bbs_vars.items():
            tree_cfg: dict
            for tree_name, tree in tree_cfg.items():
                tree_data_fm_cfg = {
                    'pn_bbs_out_tree':      self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get('pn_fwd_bbs_out', []),
                    'pn_nbbs_out_tree':     self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get('pn_fwd_not_bbs_out', []),
                    'pn_h_out_tree':        self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get('pn_fwd_h_out', []),
                    'pn_nh_out_tree':       self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get('pn_fwd_not_h_out', []),
                    'pn_call_out_tree':     self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get('pn_fwd_call_out', []),
                    'pn_ncall_out_tree':    self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get('pn_fwd_not_call_out', []),
                }.get(tree_name, [])
                # tree_data_fm_cfg = ['test', '1', 'TTT']
                self._update_tree(tree, tree_data_fm_cfg)

    def _update_tree(self, tree, tree_data_list):
        for i in tree.get_children():
            tree.delete(i)
        for ret_ent in tree_data_list:
            tree.insert('', tk.END, values=ret_ent, tags=('dummy', ret_ent))
        self._update_sort_entry(tree)

    def _update_sort_entry(self, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        col = self._last_sort_col.get(tree, 'c1')
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=not self._sort_rev)
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    def _get_fwdBBS_vars_fm_cfg(self):
        for k, fwd_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            if not fwd_cfg:
                logger.warning(self._logTag + f"Empty FWD-CFG for {k}")
                fwd_cfg = getNew_BBS_FWD_cfg()
            self._bbs_vars[fwd_cfg.get('dest_call', 'NOCALL')] = self._add_fwdBBS_pn_out_tab(fwd_cfg)

    ####################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        self._last_sort_col[tree] = col
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))
    ####################################
    def save_config(self):
        # self._get_user_data_fm_vars()
        pass
