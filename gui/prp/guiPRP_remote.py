import datetime
import tkinter as tk
from collections import deque
from tkinter import ttk

from ax25.ax25monitor import monitor_frame_inp
from cfg.constant import FONT, PARAM_MAX_MON_LEN, PARAM_MAX_MON_TREE_ITEMS, ENCODINGS
from gui.classes.guiCL_status_icons import StatusFrame, STATE_ICON_DEF_COLOR_DISABLED
from prp.prp_remote import PRP_RM_RESP_LOGIN, PRP_RM_RESP_LOGOUT
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab, tk_filter_bad_chars


class PRP_Tab(ttk.Frame):
    def __init__(self, root, tabclt: ttk.Notebook, mon_data: list, uid: str):
        super().__init__(tabclt)
        self._root_cl     = root
        self._uid         = uid
        self._getTabStr   = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._rx_tx_icons = root.get_rx_tx_icons()
        ###############################################
        # Vars
        self._mon_color_bg_rx = 'black'
        self._mon_color_fg_rx = '#1ed760'
        self._mon_color_bg_tx = 'black'
        self._mon_color_fg_tx = '#d9ded7'
        self._text_size    = POPT_CFG.get_guiCFG_text_size()
        ###############################################
        # GUI Vars
        # == Tree Mon Filter
        self._mon_tree_port_filter_var    = tk.StringVar(self, value='')
        self._mon_tree_fm_call_filter_var = tk.StringVar(self, value='')
        self._mon_tree_to_call_filter_var = tk.StringVar(self, value='')

        # == Text Mon Opt
        # self._mon_dec_dist_var      = tk.BooleanVar(self, value=True)
        self._mon_dec_aprs_var      = tk.BooleanVar(self, value=True)
        self._mon_dec_nr_var        = tk.BooleanVar(self, value=True)
        self._mon_dec_hex_var       = tk.BooleanVar(self, value=False)
        self._setting_mon_encoding  = tk.StringVar( self, value='Auto')
        self._mon_scroll_var        = tk.BooleanVar(self, value=True)

        # ==== Remote States
        # == Remote Mon Filter
        self._incl_filter_var       = tk.StringVar(self, value='')
        self._excl_filter_var       = tk.StringVar(self, value='')
        self._port_filter_var       = tk.StringVar(self, value='0')

        # == PRP Options
        self._prp_batch_mode_var    = tk.StringVar(self,  value='auto')
        self._prp_cli_esc_var       = tk.BooleanVar(self, value=True)

        ###############################################
        # Vertikal PW
        paned_window1 = ttk.PanedWindow(self, orient='horizontal')
        paned_window1.pack(fill='both', expand=True)

        left_frame  = ttk.Frame(paned_window1)
        right_frame = ttk.Frame(paned_window1)

        left_frame.pack( fill='both', expand=False)
        right_frame.pack(fill='both', expand=False)
        paned_window1.add(left_frame,  weight=2)
        paned_window1.add(right_frame, weight=1)
        ###############################################
        # Horizontal PW right
        #paned_window_r = ttk.PanedWindow(right_frame, orient='vertical')
        #paned_window_r.pack(fill='both', expand=True)

        rframe_upper_Status = ttk.Frame(right_frame)
        rframe_upper        = ttk.Frame(right_frame)
        #rframe_upper = ttk.Frame(paned_window_r)
        #rframe_lower = ttk.Frame(paned_window_r)

        rframe_upper_Status.pack(fill='x',    expand=False, anchor='n')
        rframe_upper.pack(       fill='both', expand=False)
        #rframe_lower.pack(fill='both', expand=False)
        #paned_window_r.add(rframe_upper, weight=1)
        #paned_window_r.add(rframe_lower, weight=1)
        ###############################################
        # Horizontal PW left
        paned_window_mon = ttk.PanedWindow(left_frame, orient='vertical')
        paned_window_mon.pack(fill='both', expand=True)

        upper_frame = ttk.Frame(paned_window_mon)
        lower_frame = ttk.Frame(paned_window_mon)

        upper_frame.pack(fill='both', expand=False)
        lower_frame.pack(fill='both', expand=False)
        paned_window_mon.add(upper_frame, weight=2)
        paned_window_mon.add(lower_frame, weight=1)
        ###############################################
        # Text Monitor  -   upper_frame
        self._init_txt_mon_frame(upper_frame)
        ###############################################
        # Monitor Tab   -   lower_frame
        self._init_mon_tree(lower_frame)
        ###############################################
        # CTRL Stuff - Status Frame   right_frame
        self._init_status_frame(rframe_upper_Status)
        ###############################################
        # CTRL Stuff -   rframe_upper
        self._init_rem_mon_ctl_frame(rframe_upper)
        ###############################################
        # Mon Darstellung / optionen  -  rframe_lower
        # self._init_txt_mon_ctl_frame(rframe_lower)
        ###############################################
        # Init Data
        for pack in mon_data:
            self._update_mon_txt(pack)
            self._update_mon_tab(pack, is_init=True)
        # Scroll up
        try:
            self._mon_tree.yview_scroll(1, "units")
        except tk.TclError:
            pass
        except Exception as e:
            null = e
            # logger.warning(e)
            pass
        #############################
        # Is Connected ?
        prp = self._get_prp()
        if prp is None:
            self._change_btn_states('rsp_stop')
            self._status_frame.set_icon_state_cfg('handshake', 'disco')
        else:
            # ==== Zustand Buttons
            # == Ist Remote Monitor aktiviert ?
            if self._get_prp_remote_stat_by_key('gui_rem_mon'):
                self._change_btn_states('rsp_start')
            else:
                self._change_btn_states('rsp_stop')

            # ==== Remote States > GUI-VARS
            self._update_gui_vars_fm_rem_state()

    #######################################
    # CTL Frames - rechte Seite
    def _init_rem_mon_ctl_frame(self, frame: ttk.Frame):
        #####################
        # Remote Mon Frame (root)
        rem_mon_ctf_f = ttk.LabelFrame(frame, text="Remote Monitor")
        rem_mon_ctf_f.pack(padx=10, pady=10, anchor='w')

        #####################
        # Filter/BTN Frame
        filter_f   = ttk.LabelFrame(rem_mon_ctf_f, text='Filter')
        button_f   = ttk.Frame(rem_mon_ctf_f)
        filter_f.pack(padx=5, pady=5)
        button_f.pack(padx=5, pady=5)

        #####################
        # Filter Frame
        port_f     = ttk.Frame(filter_f)
        incl_f     = ttk.Frame(filter_f)
        excl_f     = ttk.Frame(filter_f)
        port_f.pack(padx=5, pady=5, anchor='w')
        incl_f.pack(padx=5, pady=5, anchor='w')
        excl_f.pack(padx=5, pady=5, anchor='w')

        #========
        # Port F
        ttk.Label(port_f, text='Port:').pack(side='left')
        port_val = [str(x) for x in range(20)]
        port_sel = ttk.Combobox(port_f,
                                values=port_val,
                                width=4,
                                textvariable=self._port_filter_var
                                )
        port_sel.pack(side='left', padx=5)

        #========
        # Incl F
        ttk.Label(incl_f, text='Include:').pack(side='left')
        incl_entry = ttk.Entry(incl_f,
                               width=30,
                               textvariable=self._incl_filter_var)
        incl_entry.pack(side='left')

        # ========
        # Excl F
        ttk.Label(excl_f, text='Exclude:').pack(side='left')
        excl_entry = ttk.Entry(excl_f,
                               width=30,
                               textvariable=self._excl_filter_var)
        excl_entry.pack(side='left')

        #####################
        # Button Frame
        opt_f1 = ttk.Frame(button_f)
        btn_f1 = ttk.Frame(button_f)
        btn_f2 = ttk.Frame(button_f)
        opt_f1.pack(pady=5)
        btn_f1.pack(pady=5)
        btn_f2.pack(pady=5)
        # ========
        # opt_f1
        batch_mode_f = ttk.Frame(opt_f1)
        cli_esc_f    = ttk.Frame(opt_f1)
        batch_mode_f.pack(side='top', padx=10, anchor='w', fill='x')
        cli_esc_f.pack(   side='top', padx=10, anchor='w', fill='x')

        # Batch Mode
        ttk.Label(batch_mode_f, text='Batch Mode:').pack(side='left')
        ttk.Combobox(batch_mode_f,
                     textvariable=self._prp_batch_mode_var,
                     values=['auto', 'on', 'off']
                     ).pack(side='left', padx=5)
        # CLI ESC
        ttk.Checkbutton(cli_esc_f,
                        text='CLI-ESC (send compressed):',
                        variable=self._prp_cli_esc_var).pack(side='left')
        # ========
        # f1
        self._start_btn = ttk.Button(
            btn_f1,
            text="Start",
            command=lambda : self._cmd_start_rem_mon(),
            state='disabled'
        )
        self._update_btn = ttk.Button(
            btn_f1,
            text="Update",
            command=lambda: self._cmd_update_rem_states(),
            state='disabled'
        )
        self._login_btn = ttk.Button(
            btn_f1,
            text="Login",
            command=lambda: self._cmd_login(),
            state='disabled'
        )
        self._start_btn.pack( side='left', padx=15)
        self._update_btn.pack(side='left', padx=15)
        self._login_btn.pack( side='left', padx=15)

        # ========
        # f2
        self._stop_btn = ttk.Button(
            btn_f2,
            text="Stop",
            command=lambda : self._cmd_stop_rem_mon(),
            state='disabled'
        )
        self._disco_btn = ttk.Button(
            btn_f2,
            text="Disconnect",
            command=lambda: self._cmd_disco(),
            state='disabled'
        )
        self._logout_btn = ttk.Button(
            btn_f2,
            text="Logout",
            command=lambda: self._cmd_logout(),
            state='disabled'
        )
        # FIXME Nur zum Testen
        #self._abort_btn = ttk.Button(
        #    btn_f2,
        #    text="Abort",
        #    command=lambda: self._cmd_cli_esc_abort(),
        #    #state='disabled'
        #)

        self._stop_btn.pack(  side='left', padx=15)
        self._disco_btn.pack( side='left', padx=15)
        self._logout_btn.pack(side='left', padx=15)
        # FIXME Nur zum Testen
        #self._abort_btn.pack(side='left', padx=15)

    def _init_txt_mon_ctl_frame(self, frame: ttk.Frame):
        ############################
        # Monitor opt mon_ctf_f
        mon_ctf_f     = ttk.LabelFrame(frame, text="Monitor")
        mon_ctf_f.pack(    padx=10, pady=10, anchor='w')
        ttk.Checkbutton(mon_ctf_f, text='Auto Scroll',   variable=self._mon_scroll_var).pack(anchor='w', padx=5, pady=5)
        ttk.Checkbutton(mon_ctf_f, text='APRS',   variable=self._mon_dec_aprs_var).pack(anchor='w', padx=5, pady=5)
        ttk.Checkbutton(mon_ctf_f, text='NetROM', variable=self._mon_dec_nr_var).pack(anchor='w', padx=5, pady=5)
        ttk.Checkbutton(mon_ctf_f, text='HEX',    variable=self._mon_dec_hex_var).pack(anchor='w', padx=5, pady=5)
        #
        dec_f = ttk.Frame(mon_ctf_f)
        dec_f.pack(padx=5, pady=5)
        ttk.Label(dec_f, text='Decoding:').pack(side='left', padx=5)
        dec_val = ['Auto'] + list(ENCODINGS)
        ttk.Combobox(dec_f,
                     width=9,
                     textvariable=self._setting_mon_encoding,
                     values=dec_val).pack(side='left')

    # == Status Frame
    def _init_status_frame(self, frame: ttk.Frame):
        status_frame = ttk.Frame(frame, height=10)
        status_frame.pack(fill='x', anchor='w', padx=10)
        ######
        status_frm_cfg = {
            'horizontal': True,
            'icon_size': 10,
            'icon_pad': 5,
            'bg_color': '#313336',
            'icon_cfg': {
                'handshake': {
                    'icon_size': 12,
                    'state_cfg': {
                        'default_state': {'symbol': '⮔',
                                          'color': '#18e002',
                                          'color_disabled': STATE_ICON_DEF_COLOR_DISABLED,

                                          'blink_rate': 'alarm_0',
                                          'init_state': True,
                                          'invert_blink': False,

                                          'alarm_reset_behavior': 'restore'
                                          },
                        'init':          {'symbol': '⮔',
                                          'color': '#f0d402',
                                          'color_disabled': STATE_ICON_DEF_COLOR_DISABLED,

                                          'blink_rate': 'alarm_05',
                                          'init_state': True,
                                          'invert_blink': False,

                                          'alarm_reset_behavior': 'restore'
                                          },
                        'handshake_error': {'symbol': '⮔',
                                 'color': '#fa2020',
                                 'color_disabled': '#f0d402',
                                 'blink_rate': 'alarm_025',
                                 'init_state': True,
                                 'invert_blink': False,

                                 'alarm_reset_behavior': 'restore'
                                 },
                        'disco': {'symbol': '⮔', 'color': '#fa2020',
                                 'blink_rate': 'alarm_025',
                                 'init_state': True,
                                  'invert_blink': False,

                                  'alarm_reset_behavior': 'disable'
                                 }
                    }
                },
                'pending': {
                    'icon_size': 12,
                    'state_cfg': {
                        'default_state': {'symbol': '⭿',
                                          'color': '#03cefc',
                                          'blink_rate': 'alarm_025',
                                          'init_state': False,
                                          'invert_blink': True,
                                          'alarm_reset_behavior': 'disable'
                                          }
                    }
                },
                'monitor': {
                    'icon_size': 17,
                    'state_cfg': {
                        'default_state': {'symbol': '⎚', 'color': '#18e002',
                                          'blink_rate': 'alarm_05',
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False}
                    }
                },
                'cli-esc': {
                    'icon_size': 12,
                    'state_cfg': {
                        'default_state': {'symbol': '⌨', 'color': '#18e002',
                                          'blink_rate': 'alarm_05',
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False}
                    }
                },
                'login': {
                    'icon_size': 13,
                    'state_cfg': {
                        'default_state': {'symbol': '⚿', 'color': '#18e002',
                                          'blink_rate': 'alarm_025',
                                          'alarm_reset_behavior': 'restore',
                                          'invert_blink': False,

                                          'init_state': False}
                    }
                },
            }
        }

        self._status_frame = StatusFrame(status_frame,
                                         status_frame_cfg=status_frm_cfg)

    #######################################
    # Mon Tree
    def _init_mon_tree(self, frame: ttk.Frame):
        columns = (
            'time',
            'port',
            'from',
            'to',
            'via',
            'typ',
            'pid',
            'nr_ns',
            'cmd_poll',
            'size',
            'data',
        )
        mon_tree_pw = ttk.Panedwindow(frame, orient='horizontal')
        mon_tree_pw.pack(fill='both', expand=True)
        #
        mon_f_main = ttk.Frame(mon_tree_pw)
        mon_f_1 = ttk.Frame(mon_f_main)
        mon_f_2 = ttk.Frame(mon_f_main)
        mon_f_1.pack(fill='both', expand=True)
        mon_f_2.pack(fill='x', expand=False)
        #
        mon_filter_f = ttk.Frame(mon_tree_pw)
        mon_filter_f.pack(fill='x', expand=False)
        #
        mon_tree_pw.add(mon_f_main, weight=0)
        mon_tree_pw.add(mon_filter_f, weight=1)

        ###################################################
        self._mon_tree = ttk.Treeview(mon_f_1, columns=columns, show='tree headings', height=2)
        self._mon_tree.pack(side='left', fill='both', expand=True)

        self._mon_tree.heading('#0', text="RX/TX")
        self._mon_tree.heading('time', text=self._getTabStr('time'))
        self._mon_tree.heading('port', text='Port')
        self._mon_tree.heading('from', text=self._getTabStr('from'))
        self._mon_tree.heading('to', text=self._getTabStr('to'))
        self._mon_tree.heading('via', text='Via')
        self._mon_tree.heading('typ', text='CTL')
        self._mon_tree.heading('pid', text='PID')
        self._mon_tree.heading('nr_ns', text='NS/NR')
        self._mon_tree.heading('cmd_poll', text='CMD/POLL')
        self._mon_tree.heading('size', text='Bytes')
        self._mon_tree.heading('data', text='Data')

        self._mon_tree.column("#0", anchor='w', stretch=False, width=50)
        self._mon_tree.column("time", anchor='w', stretch=False, width=70)
        self._mon_tree.column("port", anchor='center', stretch=False, width=30)
        self._mon_tree.column("from", anchor='w', stretch=False, width=85)
        self._mon_tree.column("to", anchor='w', stretch=False, width=85)
        self._mon_tree.column("via", anchor='w', stretch=False, width=120)
        self._mon_tree.column("typ", anchor='center', stretch=False, width=50)
        self._mon_tree.column("pid", anchor='center', stretch=False, width=100)
        self._mon_tree.column("nr_ns", anchor='center', stretch=False, width=45)
        self._mon_tree.column("cmd_poll", anchor='center', stretch=False, width=50)
        self._mon_tree.column("size", anchor='center', stretch=False, width=45)
        self._mon_tree.column("data", anchor='w', stretch=False, width=700)

        # for el in list(range(100)):
        #    mon_tree.insert('', 'end', values=(el,))
        # Vertikale Scrollbar
        scrollbar_y = ttk.Scrollbar(mon_f_1, orient='vertical', command=self._mon_tree.yview)
        self._mon_tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side='left', fill='y')

        # Horizontale Scrollbar
        scrollbar_x = ttk.Scrollbar(mon_f_2, orient='horizontal', command=self._mon_tree.xview)
        self._mon_tree.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.pack(fill='x')
        ###################################################
        ttk.Label(mon_filter_f, text="Filter").pack()
        port_f = ttk.Frame(mon_filter_f)
        fm_call_f = ttk.Frame(mon_filter_f)
        to_call_f = ttk.Frame(mon_filter_f)
        btn_pack_f = ttk.Frame(mon_filter_f)
        port_f.pack(fill='x', expand=False, pady=5)
        fm_call_f.pack(fill='x', expand=False, pady=5)
        to_call_f.pack(fill='x', expand=False, pady=5)
        btn_pack_f.pack(fill='x', expand=False, pady=5)
        # Port
        ttk.Label(port_f, text='Port').pack(side='left', anchor='w', padx=5)
        opt = ['', ''] + [str(x) for x in list(POPT_CFG.get_port_CFGs().keys())]
        ttk.OptionMenu(port_f,
                       self._mon_tree_port_filter_var,
                       *opt,
                       command=lambda e: self._monitor_tree_on_filter_chg()).pack(side='left', anchor='w')
        # FM Call
        ttk.Label(fm_call_f, text='From Call').pack(side='left', anchor='w', padx=5)
        ttk.Entry(fm_call_f,
                  textvariable=self._mon_tree_fm_call_filter_var,
                  width=30).pack(side='left', anchor='w', expand=True)
        # TO Call
        ttk.Label(to_call_f, text='To Call      ').pack(side='left', anchor='w', padx=5)
        ttk.Entry(to_call_f,
                  textvariable=self._mon_tree_to_call_filter_var,
                  width=30).pack(side='left', anchor='w', expand=True)
        # BTN
        ttk.Button(btn_pack_f,
                   text='Update',
                   command=lambda: self._monitor_tree_on_filter_chg()
                   ).pack(side='left', anchor='w', padx=10)
        ttk.Button(btn_pack_f,
                   text='Reset',
                   command=lambda: self._monitor_tree_on_filter_reset()
                   ).pack(side='right', anchor='e', padx=10)

    def _monitor_tree_on_filter_chg(self):
        # TODO
        pass

    def _monitor_tree_on_filter_reset(self):
        # TODO
        pass

    #######################################
    # Text Mon
    def _init_txt_mon_frame(self, frame: ttk.Frame):
        # == PW
        pw_win = ttk.PanedWindow(frame, orient='horizontal')
        pw_win.pack(fill='both', expand=True)

        # == PW-Frame
        mon_frame = ttk.Frame(pw_win)
        opt_frame = ttk.Frame(pw_win)
        mon_frame.pack(fill='both', expand=True)
        opt_frame.pack(             expand=False)
        pw_win.add(mon_frame, weight=0)
        pw_win.add(opt_frame, weight=1)

        # == Monitor Optionen
        self._init_txt_mon_ctl_frame(opt_frame)

        # == Text Monitor
        self._mon_txt = tk.Text(mon_frame,
                                background=self._mon_color_bg_rx,
                                foreground=self._mon_color_fg_rx,
                                font=(FONT, self._text_size),
                                height=30,
                                width=100,
                                bd=0,
                                borderwidth=0,
                                relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                highlightthickness=0,
                                )
        mon_scrollbar = ttk.Scrollbar(
            mon_frame,
            orient='vertical',
            command=self._mon_txt.yview
        )
        self._mon_txt.pack(side='left', fill='both', expand=True)
        # == Scrollbar
        mon_scrollbar.pack(side='left', fill='y', expand=False)
        self._mon_txt.config(yscrollcommand=mon_scrollbar.set)

        # == Tags
        self._mon_txt.tag_config('TX',
                                 foreground=self._mon_color_fg_tx,
                                 background=self._mon_color_bg_tx,
                                 selectbackground=self._mon_color_fg_tx,
                                 selectforeground=self._mon_color_bg_tx,
                                 )
        self._mon_txt.tag_config('RX',
                                 foreground=self._mon_color_fg_rx,
                                 background=self._mon_color_bg_rx,
                                 selectbackground=self._mon_color_fg_rx,
                                 selectforeground=self._mon_color_bg_rx,
                                 )

    def _clear_monitor_data(self):
        self._mon_txt.configure(state='normal')
        self._mon_txt.delete('1.0', tk.END)
        self._mon_txt.configure(state='disabled')

    #######################################
    # CTL Remote Mon
    def _cmd_start_rem_mon(self):
        state_cfg = dict(
            gui_rem_mon=True
        )

        # self._status_frame.set_icon_alarm_state('login', login_ok)
        self._cmd_update_rem_states(state_cfg)


    def _cmd_stop_rem_mon(self):
        state_cfg = dict(
            gui_rem_mon=False
        )
        self._cmd_update_rem_states(state_cfg)

    #def _cmd_cli_esc_abort(self):
    #    prp = self._get_prp()
    #    if hasattr(prp, 'send_cmd_21'):
    #        prp.send_cmd_21()

    def _cmd_update_rem_states(self, state_cfg=None):
        if state_cfg is None:
            state_cfg = {}
        prp = self._get_prp()
        if hasattr(prp, 'send_remote_state_update'):
            incl_filter = self._incl_filter_var.get()
            excl_filter = self._excl_filter_var.get()

            incl_filter = incl_filter.split(' ')
            incl_filter = [str(x).upper() for x in incl_filter]
            while '' in incl_filter:
                incl_filter.remove('')

            excl_filter = excl_filter.split(' ')
            excl_filter = [str(x).upper() for x in excl_filter]
            while '' in excl_filter:
                excl_filter.remove('')

            ###########################
            # == Port-Filter hinzufügen, wenn kein Fehler und geändert
            try:
                port_filter = int(self._port_filter_var.get())
            except ValueError:
                port_filter = 0
            # == Batch Mode hinzufügen, wenn geändert
            batch_mode_var = self._prp_batch_mode_var.get()
            if batch_mode_var not in ['auto', 'on', 'off']:
                batch_mode_var = 'auto'
            # == CLI-ESC hinzufügen, wenn kein Fehler und geändert
            esc_cli_var        = self._prp_cli_esc_var.get()
            # == State CFG bauen
            state_cfg_to_send  = self._get_prp_remote_stats()
            if state_cfg_to_send is None:
                # Keine Verbindung mehr zur Remote Station ?
                logger.warning("PRP GUI: Keine Verbindung mehr zur Remote Station ?")
                return
            # == update state_cfg_to_send mit GUI VARS
            state_cfg_to_send.update(dict(
                rem_mon_port=port_filter,
                rem_mon_incl=incl_filter,
                rem_mon_excl=excl_filter,
                batch_mode  =batch_mode_var,
                cli_esc     =esc_cli_var,
            ))
            # == update state_cfg_to_send mit state_cfg(parameter)
            state_cfg_to_send.update(state_cfg)
            # Versuche zu senden (Prüft, ob update nötig)
            if not prp.send_remote_state_update(state_cfg_to_send):
                # Nichts zum Updaten / Nichts gesendet
                return
            # Buttons deaktivieren bis Response
            self._change_btn_states('cmd_send')


            # == Eigenen State Updaten / update_own_states
            if hasattr(prp, 'update_own_states'):
                state_update = dict(
                    # Sync CLI-ESC (komprimierung)
                    cli_esc=self._prp_cli_esc_var.get()
                )
                prp.update_own_states(state_update)
            return

    def _cmd_disco(self):
        remote_mon = self._get_prp()
        if hasattr(remote_mon, 'cmd_disco'):
            remote_mon.cmd_disco()
            self._change_btn_states('cmd_send')
            self._status_frame.set_icon_state_cfg('handshake', 'disco')
            self._status_frame.set_icon_alarm_state('handshake', True)

    def _cmd_login(self):
        remote_mon = self._get_prp()
        if hasattr(remote_mon, 'cmd_login_request'):
            remote_mon.cmd_login_request('test1234') # TODO
            self._change_btn_states('cmd_login')

    def _cmd_logout(self):
        remote_mon = self._get_prp()
        if hasattr(remote_mon, 'cmd_logout'):
            remote_mon.cmd_logout()
            self._change_btn_states('cmd_login')

    #######################################
    # Update Remote Monitor
    # == Text Monitor
    def _update_mon_txt(self, rem_mon_pack: dict):
        end_idx = self._mon_txt.index('end-1c')  # Cache Index
        # Get Data fm packet
        tx      = rem_mon_pack.get('tx', False)
        port_id = rem_mon_pack.get('port', 0)
        mon_conf = {
            "distance":  False,
            "port_name": f'P:{port_id}',
            "aprs_dec":  bool(self._mon_dec_aprs_var.get()),
            "nr_dec":    bool(self._mon_dec_nr_var.get()),
            "hex_out":   bool(self._mon_dec_hex_var.get()),
            "decoding":  str(self._setting_mon_encoding.get()),
        }
        # Get fancy Monitor Output
        mon_str  = monitor_frame_inp(rem_mon_pack, mon_conf)
        mon_text = tk_filter_bad_chars(mon_str)
        # Insert
        self._mon_txt.configure(state="normal")
        self._mon_txt.insert(tk.END, mon_text)
        # Add Tag
        tag = 'TX' if tx else 'RX'
        self._mon_txt.tag_add(tag, end_idx, self._mon_txt.index('end-1c'))
        # Cleanup
        cut_len = int(self._mon_txt.index('end-1c').split('.')[0]) - PARAM_MAX_MON_LEN + 1
        if cut_len > 0:
            self._mon_txt.delete('1.0', f"{cut_len}.0")
        # Autoscroll
        tr = float(self._mon_txt.index(tk.END)) - float(self._mon_txt.index(tk.INSERT)) < 15
        if tr or self._mon_scroll_var.get():
            self._mon_txt.see("end")
        self._mon_txt.configure(state="disabled", exportselection=True)

    # == Tab Monitor
    def _update_mon_tab(self, ax25pack_conf: dict, is_init=False):
        is_scrolled_to_top = self._mon_tree.yview()[0] == 0.0
        #user_db = self._port_handler.get_userDB()
        #mh = self._get_mh()

        port_filter = self._mon_tree_port_filter_var.get()
        fm_call_filter = self._mon_tree_fm_call_filter_var.get().split(' ')
        to_call_filter = self._mon_tree_to_call_filter_var.get().split(' ')

        fm_call_filter = [str(x.upper()).replace(' ', '') for x in list(fm_call_filter)]
        to_call_filter = [str(x.upper()).replace(' ', '') for x in list(to_call_filter)]

        via = [f"{call}{'*' if c_bit else ''}" for call, c_bit in ax25pack_conf.get('via_calls_str_c_bit', [])]
        ns_nr = f"{'' if ax25pack_conf.get('ctl_nr', -1) == -1 else ax25pack_conf.get('ctl_nr', -1)}"
        ns_nr += f"/{'' if ax25pack_conf.get('ctl_ns', -1) == -1 else ax25pack_conf.get('ctl_ns', -1)}"
        cmd_pl = f"{'+' if ax25pack_conf.get('ctl_cmd', False) else '-'}"
        cmd_pl += f"/{'+' if ax25pack_conf.get('ctl_pf', False) else '-'}"
        pay_size = len(ax25pack_conf.get('payload', b''))
        payload = ax25pack_conf.get('payload', b'').decode('UTF-8', 'ignore')
        payload = tk_filter_bad_chars(payload)
        payload = payload.replace('\n', ' ')
        #from_dist = user_db.get_distance(ax25pack_conf.get('from_call_str', -1))
        #to_dist = user_db.get_distance(ax25pack_conf.get('to_call_str', -1))
        from_call = ax25pack_conf.get('from_call_str', '')
        to_call = ax25pack_conf.get('to_call_str', '')
        port = ax25pack_conf.get('port', -1)
        ctl = ax25pack_conf.get('ctl_flag', '')
        pid = ax25pack_conf.get('pid_flag', '')

        while '' in fm_call_filter:
            fm_call_filter.remove('')
        while '' in to_call_filter:
            to_call_filter.remove('')
        # ctl_pack_filter  = self._mon_tree_ctl_packet_filter_var.get()
        # pid_pack_filter  = self._mon_tree_pid_packet_filter_var.get()

        if (
                (port_filter and port_filter != str(port)) or
                (fm_call_filter and from_call not in fm_call_filter) or
                (to_call_filter and to_call not in to_call_filter)

        ): return
        #raw_from_call = str(from_call)
        #raw_to_call = str(to_call)


        tree_data = (
            ax25pack_conf.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
            port,
            from_call,
            to_call,
            '>'.join(via),
            ctl,
            pid,
            ns_nr,
            cmd_pl,
            pay_size,
            payload,
        )
        index = 0

        is_tx = ax25pack_conf.get('tx', True)
        icon_k = {
            True:  'tx',
            False: 'rx',
        }.get(is_tx, True)


        # Get Icon
        image = self._rx_tx_icons.get(icon_k)
        tree_data_f = [tk_filter_bad_chars(el) if type(el) == str else el for el in tree_data]
        try:
            self._mon_tree.image_ref = image
            self._mon_tree.insert('', index, values=tree_data_f, image=image)

        except tk.TclError as ex:
            logger.warning("TCL Error in guiMain _monitor_tree_update")
            logger.warning(ex)
            return

        # Begrenze die Anzahl der Einträge

        tree_items = self._mon_tree.get_children()
        if len(tree_items) > PARAM_MAX_MON_TREE_ITEMS:
            # Entferne die ältesten Einträge (am Ende der Liste)
            for item in tree_items[PARAM_MAX_MON_TREE_ITEMS:]:
                self._mon_tree.delete(item)

        if not is_scrolled_to_top and not is_init:
            try:
                self._mon_tree.yview_scroll(1, "units")
            except tk.TclError:
                pass
            except Exception as e:
                null = e
                # logger.warning(e)
                pass
    ########################################
    # PRP I/O
    def update_rem_mon(self, rem_mon_pack: dict):
        self._update_mon_txt(rem_mon_pack)
        self._update_mon_tab(rem_mon_pack)

    def rx_response(self, response: str):
        print('GUI RX RESP')
        self._change_btn_states(response)
        self._update_gui_vars_fm_rem_state()

    ########################################
    # == GUI Updates
    def _change_btn_states(self, opt=''):
        prp = self._get_prp()
        if opt == 'cmd_send' or prp is None:
            """ Disables all Btn's till response """
            """ or if not connected """
            self._start_btn.configure( state='disabled')
            self._stop_btn.configure(  state='disabled')
            self._update_btn.configure(state='disabled')
            self._disco_btn.configure( state='disabled')
            self._login_btn.configure( state='disabled')
            self._logout_btn.configure(state='disabled')
            # == Status Frame Pending
            if prp is not None:
                self._status_frame.set_icon_alarm_state('pending', True)
            else:
                self._status_frame.set_icon_alarm_state('pending', False)
            return


        # Login send
        if opt == 'cmd_login':
            self._login_btn.configure( state='disabled')
            self._logout_btn.configure(state='disabled')
            self._status_frame.set_icon_alarm_state('login', True)
            self._status_frame.set_icon_alarm_state('pending', True)
            return
        # Login Response
        elif opt == PRP_RM_RESP_LOGIN:
            self._login_btn.configure( state='disabled')
            self._logout_btn.configure(state='normal')
            self._status_frame.set_icon_alarm_state('login', False)
            self._status_frame.set_icon_state('login', True)
            self._status_frame.set_icon_alarm_state('pending', False)
            return
        # Logout Response
        elif opt == PRP_RM_RESP_LOGOUT:
            self._login_btn.configure( state='normal')
            self._logout_btn.configure(state='disabled')
            self._status_frame.set_icon_alarm_state('login', False)
            self._status_frame.set_icon_state('login', False)
            self._status_frame.set_icon_alarm_state('pending', False)
            return

        self._status_frame.set_icon_alarm_state('pending', False)
        ##################
        # Is connected ?
        """ Connected """
        start_btn_state     = 'disabled'
        stop_btn_state      = 'disabled'
        update_btn_state    = 'normal'
        disco_btn_state     = 'normal'
        login_btn_state     = 'disabled'
        logout_btn_state    = 'disabled'
        """ Eingeloggt ? """
        if self._get_prp_remote_stat_by_key('login_ok'):
            logout_btn_state = 'normal'
        else:
            login_btn_state  = 'normal'

        """ Remote Monitor aktiviert ? """
        if self._get_prp_remote_stat_by_key('gui_rem_mon'):
            stop_btn_state      = 'normal'
        else:
            start_btn_state     = 'normal'

        # Set Button States
        self._start_btn.configure( state=start_btn_state)
        self._stop_btn.configure(  state=stop_btn_state)
        self._update_btn.configure(state=update_btn_state)
        self._disco_btn.configure( state=disco_btn_state)
        self._login_btn.configure( state=login_btn_state)
        self._logout_btn.configure(state=logout_btn_state)

    ########################################
    # == Helper
    def _get_prp(self):
        conn = self._root_cl.get_conn_by_uid(self._uid)
        if hasattr(conn, 'get_prp'):
            return conn.get_prp()
        return None

    ########################################
    # == Remote State I/O
    def _get_prp_remote_stat_by_key(self, state_key: str):
        prp = self._get_prp()
        if hasattr(prp, 'get_rem_state_by_key'):
            return prp.get_rem_state_by_key(state_key)
        logger.error("Attribute Error: _get_prp_remote_stat_by_key")
        return None

    def _get_prp_remote_stats(self):
        prp = self._get_prp()
        if hasattr(prp, 'get_rem_states'):
            return prp.get_rem_states()
        logger.error("Attribute Error: _get_prp_remote_cfg")
        return None

    # == GUI-Var / Remote States I/O
    def _update_gui_vars_fm_rem_state(self):
        # == Remote States von PRP holen
        remote_states: dict or None = self._get_prp_remote_stats()
        prp = self._get_prp()

        self._status_frame.set_icon_alarm_state('pending', False)
        # == Status Frame
        if hasattr(prp, 'is_handshake') and hasattr(prp, 'is_handshake_pending'):
            handshake_stat    = prp.is_handshake
            handshake_pending = prp.is_handshake_pending

            # Handshake Error
            if handshake_pending is None:
                self._status_frame.set_icon_state_cfg('handshake', 'handshake_error')
                self._status_frame.set_icon_alarm_state('handshake', True)
                # === CLI-ESC Icon ===
                self._status_frame.set_icon_state('cli-esc', False)

                # === Monitor Icon ===
                self._status_frame.set_icon_state('monitor', False)

                # === Login Icon (sicherheitshalber) ===
                self._status_frame.set_icon_state('login', False)
                return

            if not handshake_stat or handshake_pending: # Pending Handshake
                self._status_frame.set_icon_state_cfg('handshake', 'init')
                self._status_frame.set_icon_alarm_state('handshake', True)
                # === CLI-ESC Icon ===
                self._status_frame.set_icon_state('cli-esc', False)

                # === Monitor Icon ===
                self._status_frame.set_icon_state('monitor', False)

                # === Login Icon (sicherheitshalber) ===
                self._status_frame.set_icon_state('login', False)
                return

            if handshake_stat:  # Handshake OK
                self._status_frame.set_icon_state_cfg('handshake', 'default_state')
                self._status_frame.set_icon_alarm_state('handshake', False)

                # === CLI-ESC Icon ===
                cli_esc_active = remote_states.get('cli_esc', False)
                self._status_frame.set_icon_state('cli-esc', cli_esc_active)
                # self._status_frame.set_icon_alarm_state('cli-esc', cli_esc_active)

                # === Monitor Icon ===
                mon_active = remote_states.get('gui_rem_mon', False)
                self._status_frame.set_icon_state('monitor', mon_active)
                # self._status_frame.set_icon_alarm_state('monitor', mon_active)

                # === Login Icon (sicherheitshalber) ===
                login_ok = remote_states.get('login_ok', False)
                self._status_frame.set_icon_state('login', login_ok)
                # self._status_frame.set_icon_alarm_state('login', login_ok)

                ############### VARS Update
                # == Remote Mon Filter
                port_var = str(remote_states.get('rem_mon_port', 0))
                incl_var = ' '.join(remote_states.get('rem_mon_incl', []))
                excl_var = ' '.join(remote_states.get('rem_mon_excl', []))
                # == PRP Options
                prp_cli_esc_var = remote_states.get('cli_esc', False)
                prp_batch_m_var = remote_states.get('batch_mode', 'auto')
                # prp_batch_w_var = remote_states.get('batch_wait', 30)

                # == GUI Vars setzen
                self._port_filter_var.set(port_var)
                self._incl_filter_var.set(incl_var)
                self._excl_filter_var.set(excl_var)

                self._prp_cli_esc_var.set(prp_cli_esc_var)
                self._prp_batch_mode_var.set(prp_batch_m_var)

                return

        # Disco
        self._change_btn_states('rsp_stop')
        self._status_frame.set_icon_alarm_state('pending', False)
        self._status_frame.set_icon_alarm_state('handshake', False)
        self._status_frame.set_icon_state_cfg('handshake', 'disco')
        self._status_frame.set_icon_state('handshake', True)
        self._status_frame.set_icon_state('monitor', False)
        self._status_frame.set_icon_state('cli-esc', False)
        self._status_frame.set_icon_state('login', False)
        return


    ########################################
    # Status Frame Tasker
    def tab_tasker(self):
        self._status_frame.tasker()
        return True

class PRP_remoteGUI(tk.Toplevel):
    def __init__(self, root_cl):
        super().__init__(master=root_cl.main_win)
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._root      = root_cl
        self.style      = self._root.style
        self.title('PRP-Remote')
        self.geometry(f"1200x600+{self._root.main_win.winfo_x()}+{self._root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.resizable(True, True)
        # self.attributes("-topmost", True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ##################################################################
        self._rem_mon_data: dict = self._root.get_remote_monitor_pack_buffer()
        self._tab_list           = {}
        ##################################################################
        main_f = ttk.Frame(self)
        main_f.pack(expand=True, fill='both')
        ##################################################################
        frame_1 = ttk.Frame(main_f)
        frame_1.pack(expand=True, fill='both', padx=5, pady=5)
        ##################################################################
        self._tabctl = ttk.Notebook(frame_1)
        self._tabctl.pack(expand=True, fill='both')

        for uid, mon_data in self._rem_mon_data.items():
            label_txt = uid
            tab = PRP_Tab(self, self._tabctl, mon_data, uid)
            self._tabctl.add(tab, text=label_txt)
            self._tab_list[uid] = tab

        ################################
        self._root.prp_remote_win = self

    ####################################################
    def tasker(self):
        """ fm guiMain 0.25 Sec"""
        for uid, tab in self._tab_list.items():
            tab.tab_tasker()
        return True

    ####################################################
    def prp_connection_init(self, remote_uid: str):
        if remote_uid in self._rem_mon_data:
            self.gui_prp_response_handler('', remote_uid)
            return
        self._rem_mon_data[remote_uid] = deque([] * 10000, maxlen=10000)
        label_txt = remote_uid
        tab = PRP_Tab(self, self._tabctl, self._rem_mon_data[remote_uid], remote_uid)
        self._tabctl.add(tab, text=label_txt)
        self._tab_list[remote_uid] = tab

    def rem_mon_update(self, rem_mon_ax25conf: dict, remote_uid: str):
        if remote_uid not in self._rem_mon_data:
            self._rem_mon_data[remote_uid] = deque([] * 10000, maxlen=10000)
        self._rem_mon_data[remote_uid].append(rem_mon_ax25conf)

        if remote_uid not in self._tab_list:
            label_txt = remote_uid
            tab = PRP_Tab(self, self._tabctl, self._rem_mon_data[remote_uid], remote_uid)
            self._tabctl.add(tab, text=label_txt)
            self._tab_list[remote_uid] = tab
        else:
            #try:
            self._tab_list[remote_uid].update_rem_mon(rem_mon_ax25conf)
            #except Exception as ex:
            #    logger.error("Remote Mon > rem_mon_update")
            #    logger.error(ex)

    def gui_prp_response_handler(self, response: str, remote_uid: str):
        try:
            self._tab_list[remote_uid].rx_response(response)
        except Exception as ex:
            logger.warning("guiRemoteMon")
            logger.warning(ex)

    ####################################################
    def get_rx_tx_icons(self):
        return self._root.get_rx_tx_icons()

    def get_conn_by_uid(self, uid: str):
        ph = self._root.get_PH_mainGUI()
        if hasattr(ph, 'get_connections_by_uid'):
            return ph.get_connections_by_uid(uid)
        return None
    ####################################################
    #
    def _destroy_win(self):
        self.destroy()
        self._root.prp_remote_win = None

    def close(self):
        self._destroy_win()