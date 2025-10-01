import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, Menu

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab, format_number, conv_time_DE_str, conv_timestamp_delta


# from cfg.logger_config import logger

class BBS_fwd_Q(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        port_handler = root_win.get_PH_mainGUI()
        self._root_win              = root_win
        self._bbs_obj               = port_handler.get_bbs()
        self._getTabStr             = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._conn_typ_icon_tab     = root_win.get_conn_typ_icon_16()
        ###################################
        self.title(self._getTabStr('fwd_list'))
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1430x"
                      f"420+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        #########################################
        # Vars
        self._port_vars             = {}
        self._bbs_vars              = {}
        self._tree_data             = []
        self._stat_tree_data        = []
        self._data                  = []
        self._rev_ent               = False
        self._last_sort             = ''
        self._selected_bbs          = []
        self._selected_fwdid        = []
        self._tabctl_i              = self._getTabStr('fwd_list')
        self._old_conn_hist_len     = 0
        self._rev_conn_his          = False
        ##########################################################################################
        self._conn_hist_label_var       = tk.StringVar(self, value='')
        self._port_filter_var           = tk.StringVar(self, value='')
        self._typ_filter_var            = tk.StringVar(self, value='')
        ##########################################################################################
        self._update_conn_hist_label = lambda n: self._conn_hist_label_var.set(f"Total: {n}")
        ##########################################################################################
        # Tab-ctl
        root_frame   = ttk.Frame(self, borderwidth=10)
        root_frame.pack(side='top', fill='both', expand=True)
        self._tabctl = ttk.Notebook(root_frame)
        self._tabctl.bind("<<NotebookTabChanged>>", self._on_mainTab_change)
        self._tabctl.pack(side='top', fill='both', expand=True)

        tree_frame = ttk.Frame(self._tabctl)
        port_frame = ttk.Frame(self._tabctl)
        stat_frame = ttk.Frame(self._tabctl)
        cohi_frame = ttk.Frame(self._tabctl)
        self._tabctl.add(tree_frame, text=self._getTabStr('fwd_list'))
        self._tabctl.add(port_frame, text="FWD-Ports")
        self._tabctl.add(stat_frame, text=self._getTabStr('statistic'))
        self._tabctl.add(cohi_frame, text=self._getTabStr('connection_history'))
        #tree_frame.pack(side='left', fill='both', expand=True)
        #port_frame.pack(side='top',  fill='both', expand=True)

        ##########################################################################################
        # TREE
        columns = (
            'FWDID',
            'BID',
            'from',
            'to',
            'fwd_bbs_call',
            'type',
            'sub',
            'size',
        )

        self._tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self._tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y', expand=False)

        self._tree.heading('FWDID', text='FWD-ID', command=lambda: self._sort_entry(self._tree, 'FWDID'))
        self._tree.heading('BID', text='BID', command=lambda: self._sort_entry(self._tree, 'BID'))
        self._tree.heading('from', text=self._getTabStr('from'), command=lambda: self._sort_entry(self._tree, 'from'))
        self._tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry(self._tree, 'to'))
        self._tree.heading('fwd_bbs_call', text=f"{self._getTabStr('to')} BBS", command=lambda: self._sort_entry(self._tree, 'fwd_bbs_call'))
        self._tree.heading('type', text='Type', command=lambda: self._sort_entry(self._tree, 'type'))
        self._tree.heading('sub', text=self._getTabStr('subject'), command=lambda: self._sort_entry(self._tree, 'sub'))
        self._tree.heading('size', text='Msg-Size', command=lambda: self._sort_entry(self._tree, 'size'))
        self._tree.column("FWDID", anchor='w', stretch=tk.YES, width=170)
        self._tree.column("BID", anchor='w', stretch=tk.YES, width=130)
        self._tree.column("from", anchor='w', stretch=tk.YES, width=190)
        self._tree.column("to", anchor='w', stretch=tk.YES, width=190)
        self._tree.column("fwd_bbs_call", anchor='w', stretch=tk.YES, width=90)
        self._tree.column("type", anchor='center', stretch=tk.YES, width=60)
        self._tree.column("sub", anchor='w', stretch=tk.YES, width=150)
        self._tree.column("size", anchor='w', stretch=tk.YES, width=60)
        self._tree.bind('<<TreeviewSelect>>', self._entry_selected)
        ###
        btn_frame = ttk.Frame(tree_frame, width=150)
        btn_frame.pack(side='left', fill='y', expand=False)
        ttk.Button(btn_frame,
                  text=self._getTabStr('start_fwd'),
                  command=self._do_fwd
                  ).pack()
        ttk.Button(btn_frame,
                   text=self._getTabStr('delete'),
                   command=self._del_fwd_id
                   ).pack()
        ##########################################################################################
        # port_frame

        self._port_tabctl = ttk.Notebook(port_frame)
        self._port_tabctl.bind("<<NotebookTabChanged>>", self._update_bbs_vars)

        self._port_tabctl.pack(side='top', fill='both', expand=True)

        for fwd_port_id, fwd_port_vars in self._bbs_obj.get_fwdPort_vars().items():
            port_tab_f = ttk.Frame(self._port_tabctl)
            self._port_tabctl.add(port_tab_f, text=f"FWD-Port {fwd_port_id}")
            ###############
            # L/R Frames
            l_frame = ttk.Frame(port_tab_f, borderwidth=10)
            r_frame = ttk.Frame(port_tab_f, borderwidth=10)

            l_frame.pack(side='left', expand=False, fill='y', padx=10, pady=10)
            ttk.Separator(port_tab_f, orient='vertical').pack(side='left', fill='y', expand=False, padx=10)
            r_frame.pack(side='left', expand=False, fill='y', padx=10, pady=10)
            ###############
            # l_frame
            block_timer_var     = tk.StringVar(self)
            block_byte_c_var    = tk.StringVar(self)
            block_fwd_tasks_var = tk.StringVar(self)

            block_timer_f       = ttk.Frame(l_frame)
            block_byte_c_f      = ttk.Frame(l_frame)
            block_fwd_tasks_f   = ttk.Frame(l_frame)
            reset_btn_f         = ttk.Frame(l_frame, borderwidth=10)
            block_timer_f.pack(    side='top', expand=False, fill='y', anchor='w')
            block_byte_c_f.pack(   side='top', expand=False, fill='y', anchor='w')
            block_fwd_tasks_f.pack(side='top', expand=False, fill='y', anchor='w')
            reset_btn_f.pack(      side='top', expand=False, fill='y', )

            ttk.Label(block_timer_f,     textvariable=block_timer_var).pack(    anchor='w')
            ttk.Label(block_byte_c_f,    textvariable=block_byte_c_var).pack(   anchor='w')
            ttk.Label(block_fwd_tasks_f, textvariable=block_fwd_tasks_var).pack(anchor='w')

            ttk.Button(reset_btn_f,
                      text="Reset Block",
                      command=lambda: self._do_block_reset(),
                      ).pack()

            bbs_tabctl = ttk.Notebook(r_frame)
            bbs_tabctl.bind("<<NotebookTabChanged>>", self._update_bbs_vars)
            self._port_vars[fwd_port_id] = dict(
                block_timer_var     = block_timer_var,
                block_byte_c_var    = block_byte_c_var,
                block_fwd_tasks_var = block_fwd_tasks_var,
                bbs_tabctl          = bbs_tabctl
            )
            ##########################
            # r_frame BBS VARS
            bbs_tabctl.pack(side='top', fill='both', expand=True)
            for bbs_call, bbs_vars in self._bbs_obj.get_bbsQ_vars().items():
                bbs_var_port_id = POPT_CFG.get_BBS_cfg().get('fwd_bbs_cfg', {}).get(bbs_call, {}).get('port_id', -1)
                if bbs_var_port_id != fwd_port_id:
                    continue
                bbs_tab_f = ttk.Frame(bbs_tabctl)
                bbs_tabctl.add(bbs_tab_f, text=bbs_call)

                bbs_byte_c_var  = tk.StringVar(self)
                bbs_error_c_var = tk.StringVar(self)
                bbs_timeout_var = tk.StringVar(self)
                bbs_q_var       = tk.StringVar(self)
                bbs_q_done_var  = tk.StringVar(self)
                bbs_next_q_var  = tk.StringVar(self)

                frame_l  = ttk.Frame(bbs_tab_f, borderwidth=5)
                frame_m  = ttk.Frame(bbs_tab_f, borderwidth=5)
                frame_r  = ttk.Frame(bbs_tab_f, borderwidth=5)
                frame_rr = ttk.Frame(bbs_tab_f, borderwidth=5)

                frame_l.pack(side='left')
                frame_m.pack(side='left')
                frame_r.pack(side='left', expand=True, fill='both')
                ttk.Separator(bbs_tab_f, orient='vertical').pack(side='left', fill='y', expand=False, padx=10)
                frame_rr.pack(side='left', expand=True, fill='both')

                ###########
                # frame_l
                bbs_byte_c_f    = ttk.Frame(frame_l)
                bbs_error_c_f   = ttk.Frame(frame_l)
                bbs_timeout_f   = ttk.Frame(frame_l)
                bbs_q_f         = ttk.Frame(frame_l)
                bbs_q_done_f    = ttk.Frame(frame_l)
                bbs_next_q_f    = ttk.Frame(frame_l)
                fwd_btn_f       = ttk.Frame(frame_l, borderwidth=10)

                bbs_byte_c_f.pack(  side='top', expand=False, fill='y', anchor='w')
                bbs_error_c_f.pack( side='top', expand=False, fill='y', anchor='w')
                bbs_timeout_f.pack( side='top', expand=False, fill='y', anchor='w')
                bbs_q_done_f.pack(  side='top', expand=False, fill='y', anchor='w')
                bbs_q_f.pack(       side='top', expand=False, fill='y', anchor='w')
                bbs_next_q_f.pack(  side='top', expand=False, fill='y', anchor='w')
                fwd_btn_f.pack(     side='top', expand=False, fill='y', )

                ttk.Label(bbs_byte_c_f,  textvariable=bbs_byte_c_var ).pack(anchor='w')
                ttk.Label(bbs_error_c_f, textvariable=bbs_error_c_var).pack(anchor='w')
                ttk.Label(bbs_timeout_f, textvariable=bbs_timeout_var).pack(anchor='w')
                ttk.Label(bbs_q_f,       textvariable=bbs_q_var      ).pack(anchor='w')
                ttk.Label(bbs_q_done_f,  textvariable=bbs_q_done_var ).pack(anchor='w')
                ttk.Label(bbs_next_q_f,  textvariable=bbs_next_q_var ).pack(anchor='w')

                ttk.Button(fwd_btn_f,
                          # text=self._getTabStr('start_fwd'),
                          text="Reset Timeout",
                          command=lambda: self._do_timeout_reset(),
                          ).pack()
                ttk.Button(fwd_btn_f,
                           text=self._getTabStr('start_fwd'),
                           command=self._do_fwd_to
                           ).pack()
                ###########
                # frame_m
                ttk.Label(frame_m, text='Next-Q').pack(pady=10)
                next_q_tree = ttk.Treeview(frame_m, columns=('bid',), show='headings', height=5)
                next_q_tree.heading('bid', text='BID')
                next_q_tree.column("bid", anchor='w', stretch=tk.YES, width=160)
                next_q_tree.pack()

                ###########
                # frame_r
                ttk.Label(frame_r, text='FWD-Q').pack(pady=5)
                fwd_q_tree = ttk.Treeview(frame_r, columns=('bid', 'typ', 'msgsize', 'tosend'), show='headings')
                fwd_q_tree.heading('bid',    text='BID')
                fwd_q_tree.heading('typ',    text='Typ')
                fwd_q_tree.heading('msgsize',text='Msg Size(B)')
                fwd_q_tree.heading('tosend', text='Bytes to send')
                fwd_q_tree.column("bid",    anchor='w',      stretch=tk.YES, width=160)
                fwd_q_tree.column("typ",    anchor='center', stretch=tk.NO,  width=60)
                fwd_q_tree.column("msgsize", anchor='w',     stretch=tk.YES, width=140)
                fwd_q_tree.column("tosend", anchor='w',      stretch=tk.YES, width=140)
                fwd_q_tree.pack(expand=True, fill='both')

                ###########
                # frame_rr
                mail_pn_rx_var      = tk.StringVar(self)
                mail_pn_tx_var      = tk.StringVar(self)
                mail_bl_rx_var      = tk.StringVar(self)
                mail_bl_tx_var      = tk.StringVar(self)
                mail_rx_hold_var    = tk.StringVar(self)
                mail_tx_hold_var    = tk.StringVar(self)
                mail_rx_rej_var     = tk.StringVar(self)
                mail_tx_rej_var     = tk.StringVar(self)
                mail_rx_error_var   = tk.StringVar(self)
                mail_tx_error_var   = tk.StringVar(self)
                #
                mail_bytes_rx_var   = tk.StringVar(self)
                mail_bytes_tx_var   = tk.StringVar(self)
                bytes_rx_var        = tk.StringVar(self)
                bytes_tx_var        = tk.StringVar(self)
                connect_c_var       = tk.StringVar(self)
                connect_e_var       = tk.StringVar(self)

                stat_f_l = ttk.Frame(frame_rr)
                stat_f_r = ttk.Frame(frame_rr)
                stat_f_l.pack(side='left', fill='both')
                stat_f_r.pack(side='left', fill='both', padx=30)
                ttk.Label(stat_f_l, textvariable=mail_pn_rx_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_pn_tx_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_bl_rx_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_bl_tx_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_rx_hold_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_tx_hold_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_rx_rej_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_tx_rej_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_rx_error_var).pack(anchor='w')
                ttk.Label(stat_f_l, textvariable=mail_tx_error_var).pack(anchor='w')
                #
                ttk.Label(stat_f_r, textvariable=mail_bytes_rx_var).pack(anchor='w')
                ttk.Label(stat_f_r, textvariable=mail_bytes_tx_var).pack(anchor='w')
                ttk.Label(stat_f_r, textvariable=bytes_rx_var).pack(anchor='w')
                ttk.Label(stat_f_r, textvariable=bytes_tx_var).pack(anchor='w')
                ttk.Label(stat_f_r, textvariable=connect_c_var).pack(anchor='w')
                ttk.Label(stat_f_r, textvariable=connect_e_var).pack(anchor='w')


                self._bbs_vars[bbs_call] = dict(
                    bbs_byte_c_var  =bbs_byte_c_var,
                    bbs_error_c_var =bbs_error_c_var,
                    bbs_timeout_var =bbs_timeout_var,
                    bbs_q_var       =bbs_q_var,
                    bbs_q_done_var  =bbs_q_done_var,
                    bbs_next_q_var  =bbs_next_q_var,
                    next_q_tree     =next_q_tree,
                    fwd_q_tree      =fwd_q_tree,
                    #
                    mail_pn_rx_var      =mail_pn_rx_var,
                    mail_pn_tx_var      =mail_pn_tx_var,
                    mail_bl_rx_var      =mail_bl_rx_var,
                    mail_bl_tx_var      =mail_bl_tx_var,
                    mail_rx_hold_var      =mail_rx_hold_var,
                    mail_tx_hold_var      =mail_tx_hold_var,
                    mail_rx_rej_var      =mail_rx_rej_var,
                    mail_tx_rej_var      =mail_tx_rej_var,
                    mail_rx_error_var      =mail_rx_error_var,
                    mail_tx_error_var      =mail_tx_error_var,
                    #
                    mail_bytes_rx_var=mail_bytes_rx_var,
                    mail_bytes_tx_var=mail_bytes_tx_var,
                    bytes_rx_var=bytes_rx_var,
                    bytes_tx_var=bytes_tx_var,
                    connect_c_var=connect_c_var,
                    connect_e_var=connect_e_var,
                )

        ##########################################################################################
        # Statistic/Counter TREE
        columns = (
            'BBS',
            'MAILRX',
            'MAILTX',
            'PNRX',
            'PNTX',
            'BLRX',
            'BLTX',
            'HELDRX',
            'HELDTX',
            'REJRX',
            'REJTX',
            'MERX',
            'METX',
            'MAILDATARX',
            'MAILDATATX',
            'DATARX',
            'DATATX',
            'CONN',
            'CONNE',
        )

        self._stat_tree = ttk.Treeview(stat_frame, columns=columns, show='headings')
        self._stat_tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        stat_scrollbar = ttk.Scrollbar(stat_frame, orient='vertical', command=self._stat_tree.yview)
        self._stat_tree.configure(yscrollcommand=stat_scrollbar.set)
        stat_scrollbar.pack(side='left', fill='y', expand=False)

        self._stat_tree.heading('BBS', text='BBS', command=lambda: self._sort_entry(self._stat_tree, 'BBS'))
        self._stat_tree.heading('MAILRX', text='Mail-RX', command=lambda: self._sort_entry(self._stat_tree, 'MAILRX'))
        self._stat_tree.heading('MAILTX', text='Mail-TX', command=lambda: self._sort_entry(self._stat_tree, 'MAILTX'))
        self._stat_tree.heading('PNRX', text='P-RX', command=lambda: self._sort_entry(self._stat_tree, 'PNRX'))
        self._stat_tree.heading('PNTX', text='P-TX', command=lambda: self._sort_entry(self._stat_tree, 'PNTX'))
        self._stat_tree.heading('BLRX', text='B-RX', command=lambda: self._sort_entry(self._stat_tree, 'BLRX'))
        self._stat_tree.heading('BLTX', text='B-TX', command=lambda: self._sort_entry(self._stat_tree, 'BLTX'))
        self._stat_tree.heading('HELDRX', text='H-RX', command=lambda: self._sort_entry(self._stat_tree, 'HELDRX'))
        self._stat_tree.heading('HELDTX', text='H-TX', command=lambda: self._sort_entry(self._stat_tree, 'HELDTX'))
        self._stat_tree.heading('REJRX', text='REJ-RX', command=lambda: self._sort_entry(self._stat_tree, 'REJRX'))
        self._stat_tree.heading('REJTX', text='REJ-TX', command=lambda: self._sort_entry(self._stat_tree, 'REJTX'))
        self._stat_tree.heading('MERX', text='Error-RX', command=lambda: self._sort_entry(self._stat_tree, 'MERX'))
        self._stat_tree.heading('METX', text='Error-TX', command=lambda: self._sort_entry(self._stat_tree, 'METX'))

        self._stat_tree.heading('MAILDATARX', text='Mail-RX (kB)', command=lambda: self._sort_entry(self._stat_tree, 'MAILDATARX'))
        self._stat_tree.heading('MAILDATATX', text='Mail-TX (kB)', command=lambda: self._sort_entry(self._stat_tree, 'MAILDATATX'))
        self._stat_tree.heading('DATARX', text='Data-RX (kB)', command=lambda: self._sort_entry(self._stat_tree, 'DATARX'))
        self._stat_tree.heading('DATATX', text='Data-TX (kB)', command=lambda: self._sort_entry(self._stat_tree, 'DATATX'))
        self._stat_tree.heading('CONN', text='Conn', command=lambda: self._sort_entry(self._stat_tree, 'CONN'))
        self._stat_tree.heading('CONNE', text='Conn E', command=lambda: self._sort_entry(self._stat_tree, 'CONNE'))

        self._stat_tree.column("BBS", anchor='w', stretch=tk.NO, width=80)
        self._stat_tree.column("MAILRX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("MAILTX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("PNRX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("PNTX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("BLRX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("BLTX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("HELDRX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("HELDTX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("REJRX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("REJTX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("MERX", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("METX", anchor='w', stretch=tk.YES, width=60)

        self._stat_tree.column("MAILDATARX", anchor='w', stretch=tk.YES, width=80)
        self._stat_tree.column("MAILDATATX", anchor='w', stretch=tk.YES, width=80)
        self._stat_tree.column("DATARX", anchor='w', stretch=tk.YES, width=80)
        self._stat_tree.column("DATATX", anchor='w', stretch=tk.YES, width=80)
        self._stat_tree.column("CONN", anchor='w', stretch=tk.YES, width=60)
        self._stat_tree.column("CONNE", anchor='w', stretch=tk.YES, width=60)
        ##########################################################################################
        # Connection History TREE
        co_lable_f = ttk.Frame(cohi_frame)
        co_tree_f  = ttk.Frame(cohi_frame)
        co_lable_f.pack(fill='x',    pady=5)
        co_tree_f.pack( fill='both', expand=True)
        ###
        f1 = ttk.Frame(co_lable_f)
        f2 = ttk.Frame(co_lable_f)
        f1.pack(side='left', anchor='w', padx=10)
        f2.pack(side='left', anchor='w', padx=50)

        # f1
        ttk.Label(f1, text='Filter: ').pack(side='left', anchor='w', padx=10)
        ttk.Label(f1, text='Port: '  ).pack(side='left', anchor='w', padx=0)
        opt = ['', ''] + list(POPT_CFG.get_port_CFGs().keys())
        ttk.OptionMenu(f1,
                       self._port_filter_var,
                       *opt,
                       command=lambda e: self._on_filter_select()
                       ).pack(side='left', anchor='w', )

        ttk.Label(f1, text='Typ: ').pack(side='left', anchor='w', padx=15)
        opt = ['', '', 'FWD', 'BOX']
        ttk.OptionMenu(f1,
                       self._typ_filter_var,
                       *opt,
                       command=lambda e: self._on_filter_select()
                       ).pack(side='left', anchor='w', )
        #
        # f2
        ttk.Label(f2, textvariable=self._conn_hist_label_var).pack()
        ###
        columns = (
            'channel',
            'call',
            'own_call',
            'port',
            'dist',
            'loc',
            'typ',
            'via',
            'dauer',
            'tx_bytes_n',
            'rx_bytes_n',
            'tx_pack_n',
            'rx_pack_n',
            'time',
        )

        self._conn_his_tab = ttk.Treeview(co_tree_f, columns=columns, show='tree headings')

        self._conn_his_tab.heading('channel', text='CH', command=lambda: self._sort_conn_his('channel'))
        self._conn_his_tab.heading('call', text='To', command=lambda: self._sort_conn_his('call'))
        self._conn_his_tab.heading('own_call', text='Station', command=lambda: self._sort_conn_his('own_call'))
        self._conn_his_tab.heading('port', text='Port', command=lambda: self._sort_conn_his('port'))
        self._conn_his_tab.heading('dist', text='km', command=lambda: self._sort_conn_his('dist'))
        self._conn_his_tab.heading('loc', text='Locator', command=lambda: self._sort_conn_his('loc'))
        self._conn_his_tab.heading('typ', text='Typ', command=lambda: self._sort_conn_his('typ'))
        self._conn_his_tab.heading('via', text='VIA', command=lambda: self._sort_conn_his('via'))
        self._conn_his_tab.heading('dauer', text='Duration', command=lambda: self._sort_conn_his('dauer'))
        self._conn_his_tab.heading('tx_bytes_n', text='Bytes TX', command=lambda: self._sort_conn_his('tx_bytes_n'))
        self._conn_his_tab.heading('rx_bytes_n', text='Bytes RX', command=lambda: self._sort_conn_his('rx_bytes_n'))
        self._conn_his_tab.heading('tx_pack_n', text='Pac. TX', command=lambda: self._sort_conn_his('tx_pack_n'))
        self._conn_his_tab.heading('rx_pack_n', text='Pac. RX', command=lambda: self._sort_conn_his('rx_pack_n'))
        self._conn_his_tab.heading('time', text='Time', command=lambda: self._sort_conn_his('time'))

        self._conn_his_tab.column("#0", anchor='w', stretch=tk.NO, width=45)
        self._conn_his_tab.column("channel", anchor='center', stretch=tk.NO, width=40)
        self._conn_his_tab.column("call", anchor='w', stretch=tk.NO, width=90)
        self._conn_his_tab.column("own_call", anchor='w', stretch=tk.NO, width=90)
        self._conn_his_tab.column("port", anchor='center', stretch=tk.NO, width=50)
        self._conn_his_tab.column("dist", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("loc", anchor='w', stretch=tk.NO, width=100)
        self._conn_his_tab.column("typ", anchor='w', stretch=tk.NO, width=110)
        self._conn_his_tab.column("via", anchor='w', stretch=tk.YES, width=90)
        self._conn_his_tab.column("dauer", anchor='center', stretch=tk.NO, width=90)
        self._conn_his_tab.column("tx_bytes_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("rx_bytes_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("tx_pack_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("rx_pack_n", anchor='w', stretch=tk.NO, width=50)
        self._conn_his_tab.column("time", anchor='w', stretch=tk.NO, width=130)
        self._conn_his_tab.pack(side='left', fill='both', expand=True)

        scrollbar_y = ttk.Scrollbar(co_tree_f, orient='vertical', command=self._conn_his_tab.yview)
        self._conn_his_tab.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side='left', fill='y')
        # self._conn_his_tab.tag_configure("bell", background=CFG_TR_DX_ALARM_BG_CLR, foreground='black')
        # self._connects_tree.bind('<<TreeviewSelect>>', self._connects_entry_selected)

        ##########################################################################################
        #self._update_conn_his()
        self._init_menubar()
        self._root_win.BBS_fwd_q_list = self
        self.tasker()

    ##################################################
    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('del_all'), command=lambda : self._reset_fwd_statistic())
        menubar.add_cascade(label=self._getTabStr('statistic'), menu=MenuVerb, underline=0)

    ##################################################
    def tasker(self):
        {
            self._getTabStr('fwd_list')          : self._update_fwdQ_tree,
            "FWD-Ports"                          : self._update_port_tab,
            self._getTabStr('statistic')         : self._update_stat_tree,
            self._getTabStr('connection_history'): self._update_conn_his,
        }.get(self._tabctl_i, self._dummy_task)()

    def _dummy_task(self):
        pass
    ###########################################
    def _update_stat_tree(self):
        new_data = self._update_stat_tree_data()
        if new_data == self._stat_tree_data:
            return
        for i in self._stat_tree.get_children():
            self._stat_tree.delete(i)
        for ret_ent in new_data:
            self._stat_tree.insert('', "end", values=ret_ent)
        self._stat_tree_data = new_data

    def _update_stat_tree_data(self):
        bbs_Qvars: dict = self._bbs_obj.get_bbsQ_vars()
        ret = []
        for bbs_call, bbs_var in bbs_Qvars.items():
            # Statistics
            statistics = bbs_var.get('bbs_fwd_statistic', {})
            mail_rx_sum = statistics.get('mail_pn_rx', 0) + statistics.get('mail_bl_rx', 0)
            mail_tx_sum = statistics.get('mail_pn_tx', 0) + statistics.get('mail_bl_tx', 0)
            ret.append((
                bbs_call,
                mail_rx_sum,
                mail_tx_sum,
                statistics.get('mail_pn_rx', -1),
                statistics.get('mail_pn_tx', -1),
                statistics.get('mail_bl_rx', -1),
                statistics.get('mail_bl_tx', -1),
                statistics.get('mail_rx_hold', -1),
                statistics.get('mail_tx_hold', -1),
                statistics.get('mail_rx_rej', -1),
                statistics.get('mail_tx_rej', -1),
                statistics.get('mail_rx_error', -1),
                statistics.get('mail_tx_error', -1),

                statistics.get('mail_bytes_rx', -1)
                if statistics.get('mail_bytes_rx', -1) < 1
                else round((statistics.get('mail_bytes_rx', -1) / 1024), 1),

                statistics.get('mail_bytes_tx', -1)
                if statistics.get('mail_bytes_tx', -1) < 1
                else round((statistics.get('mail_bytes_tx', -1) / 1024), 1),

                statistics.get('bytes_rx', -1)
                if statistics.get('bytes_rx', -1) < 1
                else round((statistics.get('bytes_rx', -1) / 1024), 1),

                statistics.get('bytes_tx', -1)
                if statistics.get('bytes_tx', -1) < 1
                else round((statistics.get('bytes_tx', -1) / 1024), 1),

                statistics.get('connect_c', -1),
                statistics.get('connect_e', -1),
            ))
        return ret

    ###########################################
    def _update_port_tab(self):
        fwd_port_cfgs = POPT_CFG.get_BBS_cfg().get('fwd_port_cfg', {})
        for port_id, fwd_port_var in self._bbs_obj.get_fwdPort_vars().items():
            gui_vars     = self._port_vars.get(port_id, {})
            fwd_port_cfg = fwd_port_cfgs.get(port_id, {})
            if not gui_vars:
                continue
            try:
                block_timer     = int(fwd_port_var.get('block_timer', '0'))
                block_byte_c    = int(fwd_port_var.get('block_byte_c', '0'))
                block_fwd_tasks = list(fwd_port_var.get('block_fwd_tasks', []))
            except ValueError:
                continue
            try:
                block_timer_var     = f"Block Timer: {round(((time.time() - block_timer) / 60), 1)}/{fwd_port_cfg.get('block_time', 3)} Min"
            except ZeroDivisionError:
                block_timer_var = f"Block Timer: 0/{fwd_port_cfg.get('block_time', 3)} Min"
            try:
                block_byte_c_var    = f"Block Limit: {round((block_byte_c / 1024), 2)}/{fwd_port_cfg.get('send_limit', 1)} kB"
            except ZeroDivisionError:
                block_byte_c_var    = f"Block Limit: 0/{fwd_port_cfg.get('send_limit', 1)} kB"
            block_fwd_tasks_var = f"Block Tasks: {len(block_fwd_tasks)}"

            gui_vars['block_timer_var'].set(block_timer_var)
            gui_vars['block_byte_c_var'].set(block_byte_c_var)
            gui_vars['block_fwd_tasks_var'].set(block_fwd_tasks_var)
        self._update_port_vars()
        self._update_bbs_vars()

    def _update_port_vars(self):
        fwd_port_cfgs = POPT_CFG.get_BBS_cfg().get('fwd_port_cfg', {})
        for port_id, fwd_port_var in self._bbs_obj.get_fwdPort_vars().items():
            gui_vars     = self._port_vars.get(port_id, {})
            fwd_port_cfg = fwd_port_cfgs.get(port_id, {})
            if not gui_vars:
                continue
            try:
                block_timer     = int(fwd_port_var.get('block_timer', '0'))
                block_byte_c    = int(fwd_port_var.get('block_byte_c', '0'))
                block_fwd_tasks = list(fwd_port_var.get('block_fwd_tasks', []))
            except ValueError:
                continue
            try:
                block_timer_var     = f"Block Timer: {round(((time.time() - block_timer) / 60), 1)}/{fwd_port_cfg.get('block_time', 3)} Min"
            except ZeroDivisionError:
                block_timer_var = f"Block Timer: 0/{fwd_port_cfg.get('block_time', 3)} Min"
            try:
                block_byte_c_var    = f"Block Limit: {round((block_byte_c / 1024), 2)}/{fwd_port_cfg.get('send_limit', 1)} kB"
            except ZeroDivisionError:
                block_byte_c_var    = f"Block Limit: 0/{fwd_port_cfg.get('send_limit', 1)} kB"
            block_fwd_tasks_var = f"Block Tasks: {len(block_fwd_tasks)}"

            gui_vars['block_timer_var'].set(block_timer_var)
            gui_vars['block_byte_c_var'].set(block_byte_c_var)
            gui_vars['block_fwd_tasks_var'].set(block_fwd_tasks_var)

    def _update_bbs_vars(self, event=None):
        # bbs_fwd_cfg     = POPT_CFG.get_BBS_cfg().get('fwd_bbs_cfg', {})
        bbs_Qvars: dict = self._bbs_obj.get_bbsQ_vars()

        for bbs_call, gui_vars in self._bbs_vars.items():
            if bbs_call != self._get_bbs_tab():
                continue
            bbs_var = bbs_Qvars.get(bbs_call, {})
            # bbs_cfg = bbs_fwd_cfg.get(bbs_call, {})
            if not bbs_var:
                e_msg = "ERROR"
                gui_vars['bbs_byte_c_var'].set(e_msg)
                gui_vars['bbs_error_c_var'].set(e_msg)
                gui_vars['bbs_timeout_var'].set(e_msg)
                gui_vars['bbs_q_var'].set(e_msg)
                gui_vars['bbs_q_done_var'].set(e_msg)
                gui_vars['bbs_next_q_var'].set(e_msg)
                #
                gui_vars['mail_pn_rx_var'].set('')
                gui_vars['mail_pn_tx_var'].set('')
                gui_vars['mail_bl_rx_var'].set('')
                gui_vars['mail_bl_tx_var'].set('')
                gui_vars['mail_rx_hold_var'].set('')
                gui_vars['mail_tx_hold_var'].set('')
                gui_vars['mail_rx_rej_var'].set('')
                gui_vars['mail_tx_rej_var'].set('')
                gui_vars['mail_rx_error_var'].set('')
                gui_vars['mail_tx_error_var'].set('')

                gui_vars['mail_bytes_rx_var'].set('')
                gui_vars['mail_bytes_tx_var'].set('')
                gui_vars['bytes_rx_var'].set('')
                gui_vars['bytes_tx_var'].set('')
                gui_vars['connect_c_var'].set('')
                gui_vars['connect_e_var'].set('')
                continue
            bbs_byte_c  = bbs_var.get('bbs_fwd_byte_c',  0)
            bbs_error_c = bbs_var.get('bbs_fwd_error_c', 0)
            bbs_timeout = bbs_var.get('bbs_fwd_timeout', 0)
            bbs_q       = bbs_var.get('bbs_fwd_q',      {})
            bbs_next_q  = bbs_var.get('bbs_fwd_next_q', [])

            try:
                bbs_byte_c  = f"Mail sent: {round(float(bbs_byte_c / 1024), 2)} kB"
            except ZeroDivisionError:
                bbs_byte_c  = "Mail sent: 0.00 kB"

            bbs_error_c  = f"Errors: {bbs_error_c}"
            try:
                timeout = round(((bbs_timeout - time.time()) / 60), 1)
            except ZeroDivisionError:
                timeout = 0
            if timeout < 0:
                timeout = 0

            bbs_timeout  = f"Timeout: {timeout} Min"
            msg_in_q    = 0
            msg_done    = 0
            q_tree_data = []
            for bid, msg2fwd in bbs_q.items():
                flag = msg2fwd.get('flag', '')
                if flag == 'F':
                    msg_in_q += 1
                    q_tree_data.append((
                        msg2fwd.get('bid'          , ''),
                        msg2fwd.get('typ'          , ''),
                        msg2fwd.get('msg_size'     , 0),
                        msg2fwd.get('bytes_to_send', 0),
                    ))
                else:
                    msg_done += 1


            bbs_q            = f"FWD-Q: {msg_in_q}"
            bbs_q_done       = f"FWD-Q Done: {msg_done}"
            bbs_next_q_str   = f"Next-Q: {len(bbs_next_q)}"
            gui_vars['bbs_byte_c_var'].set(bbs_byte_c)
            gui_vars['bbs_error_c_var'].set(bbs_error_c)
            gui_vars['bbs_timeout_var'].set(bbs_timeout)
            gui_vars['bbs_q_var'].set(bbs_q)
            gui_vars['bbs_q_done_var'].set(bbs_q_done)
            gui_vars['bbs_next_q_var'].set(bbs_next_q_str)

            # Next Q
            bbs_tree = gui_vars.get('next_q_tree')
            for i in bbs_tree.get_children():
                bbs_tree.delete(i)
            for ret_ent in bbs_next_q:
                bbs_tree.insert('', 'end', values=ret_ent)

            # FWD-q
            fwd_q_tree = gui_vars.get('fwd_q_tree')
            for i in fwd_q_tree.get_children():
                fwd_q_tree.delete(i)
            for ret_ent in q_tree_data:
                fwd_q_tree.insert('', 'end', values=ret_ent)

            # Statistics
            statistics = bbs_var.get('bbs_fwd_statistic', {})
            mail_pn_rx = statistics.get('mail_pn_rx', 'Error')
            mail_pn_tx = statistics.get('mail_pn_tx', 'Error')
            mail_bl_rx = statistics.get('mail_bl_rx', 'Error')
            mail_bl_tx = statistics.get('mail_bl_tx', 'Error')
            mail_rx_hold = statistics.get('mail_rx_hold', 'Error')
            mail_tx_hold = statistics.get('mail_tx_hold', 'Error')
            mail_rx_rej = statistics.get('mail_rx_rej', 'Error')
            mail_tx_rej = statistics.get('mail_tx_rej', 'Error')
            mail_rx_error = statistics.get('mail_rx_error', 'Error')
            mail_tx_error = statistics.get('mail_tx_error', 'Error')

            mail_bytes_rx = statistics.get('mail_bytes_rx', 'Error')
            mail_bytes_tx = statistics.get('mail_bytes_tx', 'Error')
            bytes_rx = statistics.get('bytes_rx', 'Error')
            bytes_tx = statistics.get('bytes_tx', 'Error')
            connect_c = statistics.get('connect_c', 'Error')
            connect_e = statistics.get('connect_e', 'Error')

            gui_vars['mail_pn_rx_var'].set(f"Private RX: {mail_pn_rx}")
            gui_vars['mail_pn_tx_var'].set(f"Private TX: {mail_pn_tx}")
            gui_vars['mail_bl_rx_var'].set(f"Bulletin RX: {mail_bl_rx}")
            gui_vars['mail_bl_tx_var'].set(f"Bulletin TX: {mail_bl_tx}")
            gui_vars['mail_rx_hold_var'].set(f"Held RX: {mail_rx_hold}")
            gui_vars['mail_tx_hold_var'].set(f"Held TX: {mail_tx_hold}")
            gui_vars['mail_rx_rej_var'].set(f"Rejected RX: {mail_rx_rej}")
            gui_vars['mail_tx_rej_var'].set(f"Rejected TX: {mail_tx_rej}")
            gui_vars['mail_rx_error_var'].set(f"Error RX: {mail_rx_error}")
            gui_vars['mail_tx_error_var'].set(f"Error TX: {mail_tx_error}")

            try:
                gui_vars['mail_bytes_rx_var'].set(f"Mails RX: {mail_bytes_rx if type(mail_bytes_rx) != int else round((mail_bytes_rx/ 1024), 1)} kB")
            except ValueError:
                gui_vars['mail_bytes_rx_var'].set(f"Mails RX: {mail_bytes_rx}")
            try:
                gui_vars['mail_bytes_tx_var'].set(f"Mails TX: {mail_bytes_tx if type(mail_bytes_tx) != int else round((mail_bytes_tx/ 1024), 1)} kB")
            except ValueError:
                gui_vars['mail_bytes_tx_var'].set(f"Mails TX: {mail_bytes_tx}")

            try:
                gui_vars['bytes_rx_var'].set(f"Total RX: {bytes_rx if type(bytes_rx) != int else round((bytes_rx/ 1024), 1)} kB")
            except ValueError:
                gui_vars['bytes_rx_var'].set(f"Total RX: {bytes_rx}")
            try:
                gui_vars['bytes_tx_var'].set(f"Total TX: {bytes_tx if type(bytes_tx) != int else round((bytes_tx/ 1024), 1)} kB")
            except ValueError:
                gui_vars['bytes_tx_var'].set(f"Total TX: {bytes_tx}")

            gui_vars['connect_c_var'].set(f"Connects: {connect_c}")
            gui_vars['connect_e_var'].set(f"Connect Errors: {connect_e}")

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            self._tree.insert('', 'end', values=ret_ent)

    def _update_fwdQ_tree(self):
        data = list(self._bbs_obj.get_active_fwd_q_tab())
        if self._data != data:
            self._data = data
            self._format_tree_data()
            self._update_tree()
            if self._last_sort:
                self._rev_ent = not self._rev_ent
                self._sort_entry(self._tree, self._last_sort)

    def _format_tree_data(self):
        self._tree_data = []
        for el in self._data:
            from_call = f"{el[2]}@{el[3]}"
            to_call = f"{el[4]}@{el[5]}"
            self._tree_data.append((
                f'{el[0]}',
                f'{el[1]}',
                f'{from_call}',
                f'{to_call}',
                f'{el[6]}',  # fwd BBS
                f'{el[7]}',  # typ
                f'{el[8]}',  # sub
                f'{el[9]}',  # size
            ))

    ##########################
    # Connection History
    def _update_conn_his(self):
        mh = self._get_mh()
        if not hasattr(mh, 'get_conn_hist'):
            return
        conn_history = mh.get_conn_hist()
        if len(conn_history) == self._old_conn_hist_len:
            return
        new_entries = conn_history[self._old_conn_hist_len:]
        port_filter_var = self._port_filter_var.get()
        typ_filter_var  = self._typ_filter_var.get()
        n = 0
        for ent in new_entries:  # Reversed, um neueste zuerst einzufügen
            ent: dict
            port = ent.get('port_id', -1)
            typ  = ent.get('typ', '')
            if typ not in ('BOX', 'Task: FWD'):
                continue

            if port_filter_var and port_filter_var != str(port):
                continue

            if typ_filter_var and typ != {
                'BOX': 'BOX',
                'FWD': 'Task: FWD',
            }.get(typ_filter_var, ''):
                continue

            image_typ = str(typ)
            if 'DIGI' in image_typ:
                image_typ = 'DIGI'
            if ent.get('disco', False):
                image_typ += '-DISCO'
            else:
                image_typ += '-CONN'
            if ent.get('conn_incoming', False):
                image_typ += '-IN'
            else:
                image_typ += '-OUT'

            image = self._conn_typ_icon_tab.get(image_typ, None)
            tags = ()  # Optional: tags = ('disco',) if ent.disco else ()

            # Formatiere Dauer (dauer: Time)
            if ent.get('disco', False):
                duration_str = conv_timestamp_delta(ent.get('duration'))
            else:
                duration_str = "--:--:--"

            # Formatiere Startzeit (time: Duration)
            time_str = conv_time_DE_str(ent.get('time'))

            ent_values = (
                ent.get('ch_id', 0),  # channel
                ent.get('from_call', ''),  # call (To)
                ent.get('own_call', ''),  # own_call (Station)
                port,  # port
                ent.get('distance', -1),  # Distance
                ent.get('locator', ''),
                typ,  # typ
                '>'.join(ent.get('via', [])),
                duration_str,  # dauer (Time)
                format_number(ent.get('tx_bytes_n', 0)),  #
                format_number(ent.get('rx_bytes_n', 0)),  #
                format_number(ent.get('tx_pack_n', 0)),  #
                format_number(ent.get('rx_pack_n', 0)),  #
                time_str,  # time (Duration)
            )
            if image:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags, image=image)
            else:
                self._conn_his_tab.insert('', 0, values=ent_values, tags=tags)

            n += 1

        self._update_conn_hist_label(n)
        self._old_conn_hist_len = len(conn_history)

    def _sort_conn_his(self, flag: str):
        # Thanks Grok-AI
        # Alle Einträge aus dem Treeview holen
        items = [(self._conn_his_tab.set(k, flag), k) for k in self._conn_his_tab.get_children('')]

        # Sortierfunktion basierend auf Flag definieren
        def sort_key(item):
            value = item[0]
            if flag == 'channel':
                return int(value) if value else 0
            elif flag == 'port':
                return int(value) if value else -1
            elif flag == 'dist':
                return int(value) if value else -1
            elif flag == 'dauer':
                # Dauer als Sekunden umwandeln (z.B. "--:--:--" ignorieren, sonst HH:MM:SS)
                if value == "--:--:--":
                    return 0
                try:
                    h, m, s = map(int, value.split(':'))
                    return h * 3600 + m * 60 + s
                except ValueError:
                    return 0
            elif flag == 'time':
                # Deutsches Format parsen: DD.MM.YYYY HH:MM:SS
                try:
                    return datetime.strptime(value, '%d/%m/%y %H:%M:%S')
                except ValueError:
                    return datetime.min  # Ungültige Zeiten ans Ende sortieren
            else:
                # Für Strings: lexikographisch, leere Strings ans Ende
                return value if value else ''

        # Sortieren
        items.sort(key=sort_key, reverse=self._rev_conn_his)

        # Richtungswechsel für nächsten Klick
        self._rev_conn_his = not self._rev_conn_his

        # Einträge neu einfügen
        for index, (val, k) in enumerate(items):
            self._conn_his_tab.move(k, '', index)

    def _on_filter_select(self):
        for i in self._conn_his_tab.get_children():
            self._conn_his_tab.delete(i)
        self._old_conn_hist_len = 0
        self._update_conn_his()

    #######################################
    def _sort_entry(self, tree, col):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        self._last_sort = col

        def convert_value(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return val

        tmp = [(convert_value(tree.set(k, col)), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._rev_ent)
        self._rev_ent = not self._rev_ent
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    def _entry_selected(self, event=None):
        self._selected_bbs     = []
        self._selected_fwdid = []
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            fwd_id   = item['values'][0]
            bbs_call = item['values'][4]
            if fwd_id not in self._selected_fwdid:
                self._selected_fwdid.append(fwd_id)
            if bbs_call not in self._selected_bbs:
                self._selected_bbs.append(bbs_call)

    def _del_fwd_id(self):
        if not self._selected_fwdid:
            return
        self._bbs_obj.del_fwd_q_by_FWD_ID(self._selected_fwdid)
        check = []
        for bbs_call in self._selected_bbs:
            if bbs_call in check:
                continue
            self._bbs_obj.del_bbs_fwdQ(bbs_call)
            check.append(bbs_call)
        self._selected_fwdid = []
        self._selected_bbs   = []
        self._update_fwdQ_tree()

    def _do_fwd_to(self):
        bbs_call = self._get_bbs_tab()
        if bbs_call not in self._bbs_vars:
            return
        self._bbs_obj.start_autoFwd(bbs_call)

    def _do_fwd(self):
        if not self._selected_bbs:
            self._do_fwd_all()
            return
        for bbs_call in self._selected_bbs:
            self._bbs_obj.start_autoFwd(bbs_call)

    def _do_fwd_all(self):
        self._bbs_obj.start_man_autoFwd()

    def _do_timeout_reset(self):
        try:
            ind = self._port_tabctl.tab('current')
        except tk.TclError:
            return
        ind = str(ind['text']).replace('FWD-Port ', '')
        try:
            current_port_id = int(ind)
        except ValueError:
            return

        gui_port_var = self._port_vars.get(current_port_id, {})
        if not gui_port_var:
            return
        bbs_tabctl = gui_port_var.get('bbs_tabctl', None)
        if not hasattr(bbs_tabctl, 'tab'):
            return
        try:
            bbs_ind = bbs_tabctl.tab('current')
        except tk.TclError:
            return
        bbs_call = bbs_ind['text']
        if bbs_call not in self._bbs_vars:
            return
        self._bbs_obj.reset_bbs_timeout_fnc(bbs_call)

    def _do_block_reset(self):
        try:
            ind = self._port_tabctl.tab('current')
        except tk.TclError:
            return
        ind = str(ind['text']).replace('FWD-Port ', '')
        try:
            current_port_id = int(ind)
        except ValueError:
            return
        self._bbs_obj.reset_port_block_fnc(current_port_id)
    ###############################
    def _reset_fwd_statistic(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'),
                                  parent=self):
            if hasattr(self._bbs_obj, 'reset_bbs_statistic'):
                self._bbs_obj.reset_bbs_statistic()
                self._update_stat_tree()

    ###############################
    #
    def _get_bbs_tab(self):
        try:
            ind = self._port_tabctl.tab('current')
        except tk.TclError:
            return ''
        ind = str(ind['text']).replace('FWD-Port ', '')
        try:
            current_port_id = int(ind)
        except ValueError:
            return ''

        gui_port_var = self._port_vars.get(current_port_id, {})
        if not gui_port_var:
            return ''
        bbs_tabctl = gui_port_var.get('bbs_tabctl', None)
        if not hasattr(bbs_tabctl, 'tab'):
            return ''
        try:
            bbs_ind = bbs_tabctl.tab('current')
        except tk.TclError:
            return ''
        bbs_call = bbs_ind['text']
        if bbs_call not in self._bbs_vars:
            return ''
        return bbs_call

    def _get_mh(self):
        try:
            port_handler = self._root_win.get_PH_mainGUI()
            return port_handler.get_MH()
        except Exception as ex:
            logger.error(ex)
            return None
    ###########################################
    #
    def _on_mainTab_change(self, event=None):
        try:
            ind = self._tabctl.tab('current')
            self._tabctl_i = str(ind['text'])
        except tk.TclError:
            return
        except Exception as ex:
            logger.error(ex)
            return



    def _close(self):
        # self._bbs_obj = None
        self._root_win.BBS_fwd_q_list = None
        self.destroy()
