import tkinter as tk
from collections import deque
from datetime import datetime
from tkinter import ttk

from cfg.constant import PARAM_MAX_MON_TREE_ITEMS, MON_BATCH_TO_PROCESS
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import tk_filter_bad_chars, get_strTab


class MonitorTreeFrame(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent)
        # self.pack(side='bottom', fill='both', expand=True)
        # ================================
        self._gui_root     = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        self._mh           = gui_root_cl.get_MH()
        # ================================
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # ================================
        self._mon_tree_port_filter_var    = tk.StringVar(self, value='')
        self._mon_tree_to_call_filter_var = tk.StringVar(self, value='')
        self._mon_tree_fm_call_filter_var = tk.StringVar(self, value='')
        # ================================
        self.mon_pack_buff = deque([] * 10000, maxlen=10000)
        # ================================
        self._init_frame()

    # ================================
    def _init_frame(self):
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
        mon_tree_pw = ttk.Panedwindow(self, orient='horizontal')
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

    # ================================
    def monitor_tree_update_task(self, ax25pack_batch: list):
        is_scrolled_to_top = self._mon_tree.yview()[0] == 0.0
        user_db = self._popt_handler.get_userDB()
        mh = self._mh

        port_filter = self._mon_tree_port_filter_var.get()
        fm_call_filter = self._mon_tree_fm_call_filter_var.get().split(' ')
        to_call_filter = self._mon_tree_to_call_filter_var.get().split(' ')

        fm_call_filter = [str(x.upper()).replace(' ', '') for x in list(fm_call_filter)]
        to_call_filter = [str(x.upper()).replace(' ', '') for x in list(to_call_filter)]

        for ax25pack_conf in ax25pack_batch:

            via = [f"{call}{'*' if c_bit else ''}" for call, c_bit in ax25pack_conf.get('via_calls_str_c_bit', [])]
            ns_nr = f"{'' if ax25pack_conf.get('ctl_nr', -1) == -1 else ax25pack_conf.get('ctl_nr', -1)}"
            ns_nr += f"/{'' if ax25pack_conf.get('ctl_ns', -1) == -1 else ax25pack_conf.get('ctl_ns', -1)}"
            cmd_pl = f"{'+' if ax25pack_conf.get('ctl_cmd', False) else '-'}"
            cmd_pl += f"/{'+' if ax25pack_conf.get('ctl_pf', False) else '-'}"
            pay_size = len(ax25pack_conf.get('payload', b''))
            payload = ax25pack_conf.get('payload', b'').decode('UTF-8', 'ignore')
            payload = tk_filter_bad_chars(payload)
            payload = payload.replace('\n', ' ')
            from_dist = user_db.get_distance(ax25pack_conf.get('from_call_str', -1))
            to_dist = user_db.get_distance(ax25pack_conf.get('to_call_str', -1))
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
            raw_from_call = str(from_call)
            raw_to_call = str(to_call)
            if from_dist > 0:
                from_call += f'({from_dist}km)'

            if to_dist > 0:
                to_call += f'({to_dist}km)'

            tree_data = (
                ax25pack_conf.get('rx_time', datetime.now()).strftime('%H:%M:%S'),
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
                True: 'tx',
                False: 'rx',
            }.get(is_tx, True)

            """
                '', '-dx',
                '', '-term',
                '', '-node',
                '', '-bbs',
                '', '-block',
            """
            icon_k_k = ''
            # Is DX ?
            if not is_tx:
                is_dx = mh.is_dx_alarm_f_call(raw_from_call)
                if is_dx:
                    icon_k_k = '-dx'

            # Is to own Station ?
            block_list = POPT_CFG.get_block_list().get(port, {})
            if is_tx:
                own_station = POPT_CFG.get_stat_CFG_fm_call(raw_from_call.split('-')[0])
                block_state = block_list.get(raw_to_call.split('-')[0], 0)
            else:
                own_station = POPT_CFG.get_stat_CFG_fm_call(raw_to_call.split('-')[0])
                block_state = block_list.get(raw_from_call.split('-')[0], 0)

            if own_station:
                if block_state:
                    icon_k_k = '-block'
                else:
                    icon_k_k = dict(
                        USER='-term',
                        NODE='-node',
                        BOX='-bbs',
                    ).get(own_station.get('stat_parm_cli', ''), '')

            # Get Icon
            icon_k += icon_k_k
            image = self._gui_root.guiIcon.rx_tx_icons.get(icon_k)
            tree_data_f = [tk_filter_bad_chars(el) if type(el) == str else el for el in tree_data]
            try:
                self._mon_tree.image_ref = image
                self._mon_tree.insert('', index, values=tree_data_f, image=image)

            except tk.TclError as ex:
                logger.warning("TCL Error in guiMain _monitor_tree_update")
                logger.warning(ex)
                continue

        # Begrenze die Anzahl der Einträge
        tree_items = self._mon_tree.get_children()
        if len(tree_items) > PARAM_MAX_MON_TREE_ITEMS:
            # Entferne die ältesten Einträge (am Ende der Liste)
            for item in tree_items[PARAM_MAX_MON_TREE_ITEMS:]:
                self._mon_tree.delete(item)

        if not is_scrolled_to_top:
            try:
                self._mon_tree.yview_scroll(1, "units")
            except tk.TclError:
                pass
            except Exception as e:
                null = e
                # logger.warning(e)
                pass

    def _monitor_tree_on_filter_chg(self):
        for i in self._mon_tree.get_children():
            self._mon_tree.delete(i)
        batch_len = MON_BATCH_TO_PROCESS * 2
        mon_buff = list(self.mon_pack_buff)
        while mon_buff:
            self._gui_root.monitor_tree_update(mon_buff[:batch_len])
            mon_buff = mon_buff[batch_len:]

    def _monitor_tree_on_filter_reset(self):
        self._mon_tree_port_filter_var.set('')
        self._mon_tree_fm_call_filter_var.set('')
        self._mon_tree_to_call_filter_var.set('')
        self._monitor_tree_on_filter_chg()
