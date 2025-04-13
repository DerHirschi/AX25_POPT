import tkinter as tk
from tkinter import ttk

from cfg.default_config import getNew_BBS_FWD_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.bbs_gui.bbs_settings.guiBBS_R_Settings_add_rule import BBS_addRuleWin


class BBSRoutingSettings(tk.Frame):
    def __init__(self, tabctl, root_win):
        tk.Frame.__init__(self, tabctl)
        self.style      = root_win.style
        self._logTag    = 'BBSRoutingSettings: '
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # CFG
        self._pms_cfg: dict     = dict(self._root_win.get_root_pms_cfg())
        ###################################
        # Vars
        self._routing_trees     = {}
        self._sort_rev          = False
        self._last_sort_col     = {}
        self._del_rule          = ('', '', [])
        ###################################
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
        """ I am lazy. Just copy and past stuff """
        if not cfg:
            cfg = getNew_BBS_FWD_cfg()
        dest_call = cfg.get('dest_call', '')

        ###########################################
        # Vars
        pn_fwd_var            = tk.BooleanVar(self, value=cfg.get('pn_fwd',               True))
        bl_fwd_var            = tk.BooleanVar(self, value=cfg.get('bl_fwd',               True))
        pn_fwd_auto_path_var  = tk.BooleanVar(self, value=cfg.get('pn_fwd_auto_path',     True))

        ###########################################
        # Root Frame
        tab_frame   = tk.Frame(self._tabctl)
        self._tabctl.add(tab_frame, text=cfg.get('dest_call', 'NOCALL'))
        ###########################################
        # Local TabCtrl
        btn_m_frame = tk.Frame(tab_frame)
        btn_m_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_frame_l = tk.Frame(btn_m_frame)
        btn_frame_r = tk.Frame(btn_m_frame)
        btn_frame_l.pack(side=tk.LEFT, expand=False)
        btn_frame_r.pack(side=tk.LEFT, expand=False)
        ##############
        # btn_frame_l
        add_btn = tk.Button(btn_frame_l,
                            text=self._getTabStr('new'),
                            command=lambda :self._add_rule_btn(cfg.get('dest_call', 'NOCALL'))
                            )
        del_btn = tk.Button(btn_frame_l,
                            text=self._getTabStr('delete'),
                            command=self._del_btn
                            )
        add_btn.pack(side=tk.LEFT, padx=30, pady=15)
        del_btn.pack(side=tk.LEFT, padx=30)
        ##############
        # btn_frame_r
        #################
        # allow_pn_fwd
        tk.Checkbutton(btn_frame_r,
                       variable=pn_fwd_var,
                       text=self._getTabStr('allow_PN_FWD')).pack(side=tk.TOP, expand=False)
        #################
        # allow_bl_fwd
        tk.Checkbutton(btn_frame_r,
                       variable=bl_fwd_var,
                       text=self._getTabStr('allow_BL_FWD')).pack(side=tk.TOP, expand=False)
        #################
        # allow_pn_auto_path
        tk.Checkbutton(btn_frame_r,
                       variable=pn_fwd_auto_path_var,
                       text=self._getTabStr('allowPN_AutoPath')).pack(side=tk.TOP, expand=False)

        ##########
        tabctl = ttk.Notebook(tab_frame)
        tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        p_outgoing_frame  = tk.Frame(tabctl)
        bl_outgoing_frame = tk.Frame(tabctl)
        tabctl.add(p_outgoing_frame,  text='P-Outgoing')
        tabctl.add(bl_outgoing_frame, text='BL-Outgoing')

        #################################################################
        # PN Out
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
        pn_bbs_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='pn_fwd_bbs_out',
            dest_call=dest_call,
            tree=pn_bbs_out_tree
        ))
        #############################################
        # pn_not_bbs_out_f
        pn_nbbs_out_tree = ttk.Treeview(pn_not_bbs_out_f, columns=('c1',), show='headings', )
        pn_nbbs_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_nbbs_out_tree.heading('c1', text='!BBS', command=lambda: self._sort_entry('c1', pn_nbbs_out_tree))
        pn_nbbs_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        pn_nbbs_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='pn_fwd_not_bbs_out',
            dest_call=dest_call,
            tree=pn_nbbs_out_tree
        ))
        #################
        # pn_h_out_f
        pn_h_out_tree = ttk.Treeview(pn_h_out_f, columns=('c1',), show='headings')
        pn_h_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_h_out_tree.heading('c1', text='H', command=lambda: self._sort_entry('c1', pn_h_out_tree))
        pn_h_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        pn_h_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='pn_fwd_h_out',
            dest_call=dest_call,
            tree=pn_h_out_tree
        ))
        #################
        # pn_not_h_out_f
        pn_nh_out_tree = ttk.Treeview(pn_not_h_out_f, columns=('c1',), show='headings')
        pn_nh_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_nh_out_tree.heading('c1', text='!H', command=lambda: self._sort_entry('c1', pn_nh_out_tree))
        pn_nh_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        pn_nh_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='pn_fwd_not_h_out',
            dest_call=dest_call,
            tree=pn_nh_out_tree
        ))

        #################
        # pn_call_out_f
        pn_call_out_tree = ttk.Treeview(pn_call_out_f, columns=('c1',), show='headings')
        pn_call_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_call_out_tree.heading('c1', text='CALL', command=lambda: self._sort_entry('c1', pn_call_out_tree))
        pn_call_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        pn_call_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='pn_fwd_call_out',
            dest_call=dest_call,
            tree=pn_call_out_tree
        ))

        #################
        # pn_not_call_out_f
        pn_ncall_out_tree = ttk.Treeview(pn_not_call_out_f, columns=('c1',), show='headings')
        pn_ncall_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        pn_ncall_out_tree.heading('c1', text='!CALL', command=lambda: self._sort_entry('c1', pn_ncall_out_tree))
        pn_ncall_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        pn_ncall_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='pn_fwd_not_call_out',
            dest_call=dest_call,
            tree=pn_ncall_out_tree
        ))

        """
        #################################################################
        # BL In
        #################################################################
        # Frames
        bl_in_label_f       = tk.Frame(bl_incoming_frame)
        bl_th_in_f          = tk.Frame(bl_incoming_frame)
        bl_not_th_in_f      = tk.Frame(bl_incoming_frame)
        bl_dist_in_f        = tk.Frame(bl_incoming_frame)
        bl_not_dist_in_f    = tk.Frame(bl_incoming_frame)

        # Pack it

        bl_in_label_f.pack(     side=tk.TOP,  expand=False,fill=tk.X)
        bl_th_in_f.pack(        side=tk.LEFT, expand=True, fill=tk.BOTH)
        bl_not_th_in_f.pack(    side=tk.LEFT, expand=True, fill=tk.BOTH)
        bl_dist_in_f.pack(      side=tk.LEFT, expand=True, fill=tk.BOTH)
        bl_not_dist_in_f.pack(  side=tk.LEFT, expand=True, fill=tk.BOTH)

        #############################################
        tk.Label(bl_in_label_f,
                 text=self._getTabStr('bbs_sett_bl_bbs_in'),
                 height=2
                 ).pack(side=tk.TOP, expand=False, fill=tk.X)
        #############################################
        # pn_bbs_out_f

        #################
        # pn_h_out_f
        bl_th_in_tree = ttk.Treeview(bl_th_in_f, columns=('c1',), show='headings')
        bl_th_in_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_th_in_tree.heading('c1', text='THEME', command=lambda: self._sort_entry('c1', bl_th_in_tree))
        bl_th_in_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_th_in_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='bl_top_in',
            dest_call=dest_call,
            tree=bl_th_in_tree
        ))
        #################
        # pn_not_h_out_f
        bl_nth_in_tree = ttk.Treeview(bl_not_th_in_f, columns=('c1',), show='headings')
        bl_nth_in_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_nth_in_tree.heading('c1', text='!THEME', command=lambda: self._sort_entry('c1', bl_nth_in_tree))
        bl_nth_in_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_nth_in_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='bl_top_not_in',
            dest_call=dest_call,
            tree=bl_nth_in_tree
        ))

        #################
        # pn_call_out_f
        bl_dist_in_tree = ttk.Treeview(bl_dist_in_f, columns=('c1',), show='headings')
        bl_dist_in_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_dist_in_tree.heading('c1', text='DIST', command=lambda: self._sort_entry('c1', bl_dist_in_tree))
        bl_dist_in_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_dist_in_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='bl_dist_in',
            dest_call=dest_call,
            tree=bl_dist_in_tree
        ))
        
        #################
        # pn_not_call_out_f
        bl_n_dist_in_tree = ttk.Treeview(bl_not_dist_in_f, columns=('c1',), show='headings')
        bl_n_dist_in_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_n_dist_in_tree.heading('c1', text='!DIST', command=lambda: self._sort_entry('c1', bl_n_dist_in_tree))
        bl_n_dist_in_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_n_dist_in_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='bl_dist_not_in',
            dest_call=dest_call,
            tree=bl_n_dist_in_tree
        ))"""
        #################################################################
        # BL OUT
        #################################################################
        # Frames
        bl_out_label_f      = tk.Frame(bl_outgoing_frame)
        bl_th_out_f         = tk.Frame(bl_outgoing_frame)
        bl_not_th_out_f     = tk.Frame(bl_outgoing_frame)
        bl_dist_out_f       = tk.Frame(bl_outgoing_frame)
        bl_not_dist_out_f   = tk.Frame(bl_outgoing_frame)

        # Pack it

        bl_out_label_f.pack(        side=tk.TOP, expand=False, fill=tk.X)
        bl_th_out_f.pack(           side=tk.LEFT, expand=True, fill=tk.BOTH)
        bl_not_th_out_f.pack(       side=tk.LEFT, expand=True, fill=tk.BOTH)
        bl_dist_out_f.pack(         side=tk.LEFT, expand=True, fill=tk.BOTH)
        bl_not_dist_out_f.pack(     side=tk.LEFT, expand=True, fill=tk.BOTH)

        #############################################
        tk.Label(bl_out_label_f,
                 text=self._getTabStr('bbs_sett_bl_bbs_out'),
                 height=2
                 ).pack(side=tk.TOP, expand=False, fill=tk.X)
        #############################################
        # pn_bbs_out_f

        #################
        # pn_h_out_f
        bl_th_out_tree = ttk.Treeview(bl_th_out_f, columns=('c1',), show='headings')
        bl_th_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_th_out_tree.heading('c1', text='THEME', command=lambda: self._sort_entry('c1', bl_th_out_tree))
        bl_th_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_th_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='bl_top_out',
            dest_call=dest_call,
            tree=bl_th_out_tree
        ))

        #################
        # pn_not_h_out_f
        bl_nth_out_tree = ttk.Treeview(bl_not_th_out_f, columns=('c1',), show='headings')
        bl_nth_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_nth_out_tree.heading('c1', text='!THEME', command=lambda: self._sort_entry('c1', bl_nth_out_tree))
        bl_nth_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_nth_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='bl_top_not_out',
            dest_call=dest_call,
            tree=bl_nth_out_tree
        ))
        #################
        # pn_call_out_f
        bl_dist_out_tree = ttk.Treeview(bl_dist_out_f, columns=('c1',), show='headings')
        bl_dist_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_dist_out_tree.heading('c1', text='DIST', command=lambda: self._sort_entry('c1', bl_dist_out_tree))
        bl_dist_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_dist_out_tree.bind('<<TreeviewSelect>>', lambda event: self._tree_select(
            conf_name='bl_dist_out',
            dest_call=dest_call,
            tree=bl_dist_out_tree
        ))
        #################
        # pn_not_call_out_f
        bl_n_dist_out_tree = ttk.Treeview(bl_not_dist_out_f, columns=('c1',), show='headings')
        bl_n_dist_out_tree.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=7, pady=10)
        bl_n_dist_out_tree.heading('c1', text='!DIST', command=lambda: self._sort_entry('c1', bl_n_dist_out_tree))
        bl_n_dist_out_tree.column("c1", anchor=tk.CENTER, stretch=tk.NO, width=120)
        bl_n_dist_out_tree.bind('<<TreeviewSelect>>', lambda event:self._tree_select(
            conf_name='bl_dist_not_out',
            dest_call=dest_call,
            tree=bl_n_dist_out_tree
        ))

        return {
            'tab_clt':                  tabctl,
            # PN IN
            """
            'pn_bbs_in_tree':           pn_bbs_in_tree,
            'pn_nbbs_in_tree':          pn_nbbs_in_tree,
            'pn_h_in_tree':             pn_h_in_tree,
            'pn_nh_in_tree':            pn_nh_in_tree,
            'pn_call_in_tree':          pn_call_in_tree,
            'pn_ncall_in_tree':         pn_ncall_in_tree,
            """
            # PN Out
            'pn_bbs_out_tree':          pn_bbs_out_tree,
            'pn_nbbs_out_tree':         pn_nbbs_out_tree,
            'pn_h_out_tree':            pn_h_out_tree,
            'pn_nh_out_tree':           pn_nh_out_tree,
            'pn_call_out_tree':         pn_call_out_tree,
            'pn_ncall_out_tree':        pn_ncall_out_tree,
            # BL IN
            """
            'bl_th_in_tree':            bl_th_in_tree,
            'bl_nth_in_tree':           bl_nth_in_tree,
            'bl_dist_in_tree':          bl_dist_in_tree,
            'bl_n_dist_in_tree':        bl_n_dist_in_tree,
            """
            # BL OUT
            'bl_th_out_tree':           bl_th_out_tree,
            'bl_nth_out_tree':          bl_nth_out_tree,
            'bl_dist_out_tree':         bl_dist_out_tree,
            'bl_n_dist_out_tree':       bl_n_dist_out_tree,
            # Vars
            'pn_fwd_var':               pn_fwd_var,
            'bl_fwd_var':               bl_fwd_var,
            'pn_fwd_auto_path_var':     pn_fwd_auto_path_var,
        }

    def _update_all_trees(self):
        for dest_call, tree_cfg in self._routing_trees.items():
            tree_cfg: dict
            for tree_name, tree in tree_cfg.items():
                tree_data_fm_cfg = {

                    # PN Out
                    'pn_bbs_out_tree':      self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'pn_fwd_bbs_out', []),
                    'pn_nbbs_out_tree':     self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'pn_fwd_not_bbs_out', []),
                    'pn_h_out_tree':        self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'pn_fwd_h_out', []),
                    'pn_nh_out_tree':       self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'pn_fwd_not_h_out', []),
                    'pn_call_out_tree':     self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'pn_fwd_call_out', []),
                    'pn_ncall_out_tree':    self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'pn_fwd_not_call_out', []),
                    # BL In

                    # BL Out
                    'bl_th_out_tree': self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'bl_top_out', []),
                    'bl_nth_out_tree': self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'bl_top_not_out', []),
                    'bl_dist_out_tree': self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'bl_dist_out', []),
                    'bl_n_dist_out_tree': self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(
                        'bl_dist_not_out', []),


                }.get(tree_name, None)
                # tree_data_fm_cfg = ['test', '1', 'TTT']
                if tree_data_fm_cfg is None:
                    continue
                self._update_tree(tree, tree_data_fm_cfg)

    def _update_tree(self, tree, tree_data_list):
        for i in tree.get_children():
            tree.delete(i)
        for ret_ent in tree_data_list:
            tree.insert('', tk.END, values=ret_ent, tags=('dummy', f"_{ret_ent}"))
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
            self._routing_trees[fwd_cfg.get('dest_call', 'NOCALL')] = self._add_fwdBBS_pn_out_tab(fwd_cfg)

    ####################################
    def _add_rule_btn(self, dest_call: str):
        if hasattr(self._root_win.add_win, 'lift'):
            self._root_win.add_win.lift()
            return
        dest_cfg_tabctl = self._routing_trees.get(dest_call, {}).get('tab_clt')
        if dest_cfg_tabctl is None:
            logger.error(self._logTag + "_add_rule_btn: dest_cfg_tabctl is None")
            return
        dest_cfg_tabctl: ttk.Notebook
        try:
            ind = dest_cfg_tabctl.index(dest_cfg_tabctl.select())
        except (tk.TclError, AttributeError) as e:
            logger.error(self._logTag + f"_add_rule_btn: {e}")
            return
        """
        0 = P-In
        1 = P-Out
        2 = BL-In
        3 = BL-Out
        """
        if self._root_win.add_win is not None:
            return
        BBS_addRuleWin(self._root_win, dest_call, opt_index=ind)

    def _tree_select(self, conf_name: str, dest_call: str, tree: ttk.Treeview):
        rules = []
        for selected_item in tree.selection():
            item   = tree.item(selected_item)
            rules.append(str(item['values'][0]))
            try:
                rule = item['tags'][1]
                rules.append(str(rule))
            except IndexError:
                return
        self._del_rule = (conf_name, dest_call, rules)

    def _del_btn(self):
        conf_name, dest_call, rules = self._del_rule
        rule_conf = self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, {}).get(conf_name, [])
        for rule in rules:
            rule = rule[1:]
            while rule in rule_conf:
                rule_conf.remove(rule)
        self._del_rule = ('', '', [])
        self._update_all_trees()
        # self._pms_cfg['fwd_bbs_cfg'][dest_call][conf_name] = rule_conf

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
        for k, fwd_cfg in self._pms_cfg.get('fwd_bbs_cfg', {}).items():
            if not fwd_cfg:
                logger.warning(self._logTag + f"Empty FWD-CFG for {k}")
                fwd_cfg = getNew_BBS_FWD_cfg()
            if k not in self._routing_trees:
                logger.error(self._logTag + f"{k} not in self._routing_trees")
                logger.error(self._logTag + f"  self._routing_trees: {self._routing_trees}")
                return
            gui_cfg  = self._routing_trees[k]
            allow_pn_fwd        = bool(gui_cfg['pn_fwd_var'].get())
            allow_bl_fwd        = bool(gui_cfg['bl_fwd_var'].get())
            allow_pn_auto       = bool(gui_cfg['pn_fwd_auto_path_var'].get())

            fwd_cfg['pn_fwd'] = allow_pn_fwd
            fwd_cfg['bl_fwd'] = allow_bl_fwd
            fwd_cfg['pn_fwd_auto_path'] = allow_pn_auto


    def update_win(self):
        self._update_all_trees()

    @staticmethod
    def destroy_win():
        pass
        """
        if hasattr(self._add_win, 'destroy'):
            self._add_win.destroy()
        """

