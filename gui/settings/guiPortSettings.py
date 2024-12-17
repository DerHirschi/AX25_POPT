import tkinter as tk
from tkinter import ttk as ttk, messagebox
from tkinter.colorchooser import askcolor

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import DEF_PORT_MON_TX_COL, DEF_PORT_MON_BG_COL, DEF_PORT_MON_RX_COL, TNC_KISS_START_CMD, \
    TNC_KISS_END_CMD
from cfg.default_config import getNew_port_cfg
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.guiMsgBoxes import AskMsg, WarningMsg, InfoMsg
from cfg.cfg_fnc import del_port_data
from fnc.os_fnc import is_linux


class PortSetTab:
    def __init__(self, main_stt_win, new_settings, tabclt: ttk.Notebook):
        self._main_cl = main_stt_win
        self._lang = POPT_CFG.get_guiCFG_language()
        self._height = 600
        height = self._height
        self._width = 1059

        self._need_reinit = False
        self._port_setting: dict = new_settings
        port_types = PORT_HANDLER.get_ax25types_keys()
        self.tab = ttk.Frame(tabclt)
        #################
        # Port Name
        name_x = 20
        name_y = 570
        name_label = tk.Label(self.tab, text=get_strTab('port_cfg_port_name', self._lang))
        name_label.place(x=name_x, y=height - name_y)
        self._prt_name = tk.Entry(self.tab, width=5)
        self._prt_name.place(x=name_x + 420, y=height - name_y)
        self._prt_name.insert(tk.END, self._port_setting.get('parm_PortName', ''))
        ######################
        # Not initialised Info
        # all_ports = PORT_HANDLER.ax25_ports
        all_ports = PORT_HANDLER.get_all_ports_f_cfg()
        new_cfg = getNew_port_cfg()
        if self._port_setting.get('parm_PortNr', -1) in all_ports.keys():
            if not all_ports[self._port_setting.get('parm_PortNr', -1)].device_is_running:
                x = 520
                y = 570
                label = tk.Label(self.tab, text=get_strTab('port_cfg_not_init', self._lang), fg='red')
                label.place(x=x, y=height - y)
        else:
            x = 520
            y = 570
            label = tk.Label(self.tab, text=get_strTab('port_cfg_not_init', self._lang), fg='red')
            label.place(x=x, y=height - y)
        #################
        # Port Typ
        port_x = 800
        port_y = 570
        port_label = tk.Label(self.tab, text='Typ:')
        port_label.place(x=port_x, y=height - port_y)
        self._port_select_var = tk.StringVar(self.tab)

        opt = port_types
        self._port_select_var.set(self._port_setting.get('parm_PortTyp', new_cfg.get('parm_PortTyp', '')))  # default value
        port_men = tk.OptionMenu(self.tab, self._port_select_var, *opt, command=self._update_port_parameter)
        port_men.configure(width=10, height=1)
        port_men.place(x=port_x + 55, y=height - port_y - 5)
        #######################
        # Port Parameter
        param_sel_x = 20
        param_sel_y = 535
        param_next_line = 0
        # param_label = tk.Label(self.tab, text='Port-Parameter:')
        # param_label.place(x=param_sel_x, y=height - param_sel_y)
        self._param1_label = tk.Label(self.tab)
        self._param1_ent = tk.Entry(self.tab)
        self._param2_label = tk.Label(self.tab)
        self._param2_ent = tk.Entry(self.tab)
        self._param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
        self._param1_ent.place(x=param_sel_x + 80, y=height - param_sel_y + param_next_line)
        self._param2_label.place(x=param_sel_x + 500, y=height - param_sel_y + param_next_line)
        self._param2_ent.place(x=param_sel_x + 500 + 50, y=height - param_sel_y + param_next_line)
        self._param1_ent.bind('<KeyRelease>', self.set_need_reinit)
        self._param2_ent.bind('<KeyRelease>', self.set_need_reinit)

        #########################
        # Pseudo TXD
        ptxd_x = 20
        ptxd_y = 500
        ptxd_label = tk.Label(self.tab, text='P-TXD:')
        self._ptxd = tk.Entry(self.tab, width=5)
        self._ptxd.insert(tk.END, self._port_setting.get('parm_TXD', new_cfg.get('parm_TXD', 400)))
        ptxd_help = tk.Label(self.tab, text=get_strTab('port_cfg_psd_txd', self._lang))

        ptxd_label.place(x=ptxd_x, y=height - ptxd_y)
        self._ptxd.place(x=ptxd_x + 80, y=height - ptxd_y)
        ptxd_help.place(x=ptxd_x + 80 + 70, y=height - ptxd_y)

        # Baud
        calc_baud_x = 20
        calc_baud_y = 465
        calc_baud_label = tk.Label(self.tab, text='Baud:')
        self._calc_baud = tk.Entry(self.tab, width=8)
        if self._port_setting.get('parm_PortTyp', '') == 'KISSSER':
            ins = self._port_setting.get('parm_PortParm', new_cfg.get('parm_PortParm', ('', 0)))[1]
            self._calc_baud.insert(tk.END, ins)
            self._calc_baud.configure(state="disabled")
        else:
            ins = self._port_setting.get('parm_baud', new_cfg.get('parm_baud', 1200))
            self._calc_baud.insert(tk.END, ins)
            self._calc_baud.configure(state="normal")
        calc_baud_label.place(x=calc_baud_x, y=height - calc_baud_y)
        self._calc_baud.place(x=calc_baud_x + 80, y=height - calc_baud_y)

        # KISS TXD
        kiss_txd_x = 210
        kiss_txd_y = 465
        kiss_txd_label = tk.Label(self.tab, text='TXD:')
        self._kiss_txd = tk.Entry(self.tab, width=3)
        if self._port_setting.get('parm_kiss_is_on', new_cfg.get('parm_kiss_is_on', True)):
            # ins = self.port_setting.parm_PortParm[1]
            self._kiss_txd.insert(tk.END, str(self._port_setting.get('parm_kiss_TXD',new_cfg.get('parm_kiss_TXD', 35))))
            self._kiss_txd.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_txd.insert(tk.END, '0')
            self._kiss_txd.configure(state="disabled")
        self._kiss_txd.bind('<KeyRelease>', self.set_need_reinit)
        kiss_txd_label.place(x=kiss_txd_x, y=height - kiss_txd_y)
        self._kiss_txd.place(x=kiss_txd_x + 50, y=height - kiss_txd_y)
        # KISS PERS
        kiss_pers_x = 320
        kiss_pers_y = 465
        kiss_pers_label = tk.Label(self.tab, text='PERS:')
        self._kiss_pers = tk.Entry(self.tab, width=3)
        if self._port_setting.get('parm_kiss_is_on', new_cfg.get('parm_kiss_is_on', True)):
            # ins = self.port_setting.parm_PortParm[1]
            # self._kiss_pers.insert(tk.END, str(self._port_setting.parm_kiss_Pers))
            self._kiss_pers.insert(tk.END, str(self._port_setting.get('parm_kiss_Pers',
                                                              new_cfg.get('parm_kiss_Pers', 16))))
            self._kiss_pers.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_pers.insert(tk.END, '0')
            self._kiss_pers.configure(state="disabled")
        self._kiss_pers.bind('<KeyRelease>', self.set_need_reinit)
        kiss_pers_label.place(x=kiss_pers_x, y=height - kiss_pers_y)
        self._kiss_pers.place(x=kiss_pers_x + 60, y=height - kiss_pers_y)
        # KISS Slot
        slot_x = 440
        slot_y = 465
        slot_label = tk.Label(self.tab, text='SLOT:')
        self._kiss_slot = tk.Entry(self.tab, width=3)
        # if self.port_setting.parm_PortTyp == 'AXIP':
        if self._port_setting.get('parm_kiss_is_on', new_cfg.get('parm_kiss_is_on', True)):
            # ins = self.port_setting.parm_PortParm[1]
            # self._kiss_slot.insert(tk.END, str(self._port_setting.parm_kiss_Slot))
            self._kiss_slot.insert(tk.END,
                                   str(self._port_setting.get('parm_kiss_Slot',
                                                              new_cfg.get('parm_kiss_Slot', 30))))
            self._kiss_slot.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_slot.insert(tk.END, '0')
            self._kiss_slot.configure(state="disabled")
        slot_label.place(x=slot_x, y=height - slot_y)
        self._kiss_slot.bind('<KeyRelease>', self.set_need_reinit)
        self._kiss_slot.place(x=slot_x + 60, y=height - slot_y)
        # KISS TAIL
        kiss_tail_x = 560
        kiss_tail_y = 465
        kiss_tail_label = tk.Label(self.tab, text='TAIL:')
        self._kiss_tail = tk.Entry(self.tab, width=3)
        # if self.port_setting.parm_PortTyp == 'AXIP':
        if self._port_setting.get('parm_kiss_is_on', new_cfg.get('parm_kiss_is_on', True)):
            # ins = self.port_setting.parm_PortParm[1]
            # self._kiss_tail.insert(tk.END, str(self._port_setting.parm_kiss_Tail))
            self._kiss_tail.insert(tk.END, str(self._port_setting.get('parm_kiss_Tail',
                                                              new_cfg.get('parm_kiss_Tail', 15))))
            self._kiss_tail.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_tail.insert(tk.END, '0')
            self._kiss_tail.configure(state="disabled")
        kiss_tail_label.place(x=kiss_tail_x, y=height - kiss_tail_y)
        self._kiss_tail.bind('<KeyRelease>', self.set_need_reinit)
        self._kiss_tail.place(x=kiss_tail_x + 50, y=height - kiss_tail_y)
        ########################

        ########################
        # TODO AXIP related options ( Multicast, LinkTest, TestCall, Intervall, Max-Fail-counter )
        axip_multicast_x = 800
        axip_multicast_y = 535
        self._axip_multicast_var = tk.IntVar(self.tab)
        self._axip_multicast_dd = tk.Checkbutton(self.tab,
                                                 text='AXIP-Multicast',
                                                 variable=self._axip_multicast_var,
                                                 command=self._update_Mcast_settings,
                                                 state='disabled')
        self._axip_multicast_dd.var = self._axip_multicast_var
        if self._port_setting.get('parm_PortTyp', '') == 'AXIP':
            mcast_port = PORT_HANDLER.get_mcast_server().get_mcast_port()
            if not hasattr(mcast_port, 'port_id'):
                self._axip_multicast_dd.configure(state="normal")
                # if self._port_setting.parm_axip_Multicast:
                if self._port_setting.get('parm_axip_Multicast', new_cfg.get('parm_axip_Multicast', False)):
                    self._axip_multicast_var.set(1)
                    self._axip_multicast_dd.select()
                else:
                    self._axip_multicast_var.set(0)
                    self._axip_multicast_dd.deselect()
            else:
                mcast_port_id = int(mcast_port.port_id)
                if self._port_setting.get('parm_PortNr', -1) == mcast_port_id:

                    self._axip_multicast_dd.configure(state="normal")
                    self._axip_multicast_var.set(1)
                    self._axip_multicast_dd.select()
                else:
                    self._axip_multicast_dd.configure(state="disabled")
                    self._axip_multicast_var.set(0)
                    self._axip_multicast_dd.deselect()
        else:
            self._axip_multicast_var.set(0)
            self._axip_multicast_dd.deselect()
            self._axip_multicast_dd.configure(state="disabled")
        self._axip_multicast_dd.place(x=axip_multicast_x + 20, y=height - axip_multicast_y)
        # KISS START / END
        kiss_start_x = 630
        kiss_start_y = 465
        kiss_start_label = tk.Label(self.tab, text='KISSMODE START:')
        kiss_start_label.place(x=kiss_start_x + 50, y=height - kiss_start_y)
        self._kiss_start_cmd_tab = {}
        opt = ['']
        for cmd in TNC_KISS_START_CMD:
            if str(cmd)[2:-1] not in opt:
                try:
                    self._kiss_start_cmd_tab[str(cmd)[2:-1]] = cmd
                    opt += [str(cmd)[2:-1]]
                except IndexError:
                    pass
        # opt = [''] + [str(x) for x in TNC_KISS_START_CMD] # + ['CUSTOM']
        self._kiss_start_var = tk.StringVar(self.tab)
        try:
            self._kiss_start_var.set(
                str(self._port_setting.get('parm_kiss_init_cmd', new_cfg.get('parm_kiss_init_cmd', '')))[2:-1]
            )  # default value
        except IndexError:
            self._kiss_start_var.set('')

        kiss_start_men = tk.OptionMenu(self.tab, self._kiss_start_var, *opt, command=self.set_need_reinit)
        kiss_start_men.configure(width=10, height=1)
        kiss_start_men.place(x=kiss_start_x + 220, y=height - kiss_start_y)

        kiss_end_x = 630
        kiss_end_y = 430
        kiss_end_label = tk.Label(self.tab, text='KISSMODE END:')
        kiss_end_label.place(x=kiss_end_x + 50, y=height - kiss_end_y)
        self._kiss_end_cmd_tab = {}
        opt = ['']
        for cmd in TNC_KISS_END_CMD:
            if str(cmd)[2:-1] not in opt:
                try:
                    self._kiss_end_cmd_tab[str(cmd)[2:-1]] = cmd
                    opt += [str(cmd)[2:-1]]
                except IndexError:
                    pass
        # opt = [''] + [str(x) for x in TNC_KISS_END_CMD]# + ['CUSTOM']
        self._kiss_end_var = tk.StringVar(self.tab)
        try:
            self._kiss_end_var.set(
                str(self._port_setting.get('parm_kiss_end_cmd', new_cfg.get('parm_kiss_end_cmd', '')))[2:-1]
            )  # default value
        except IndexError:
            self._kiss_end_var.set('')
        kiss_end_men = tk.OptionMenu(self.tab, self._kiss_end_var, *opt, command=self.set_need_reinit)
        kiss_end_men.configure(width=10, height=1)
        kiss_end_men.place(x=kiss_end_x + 220, y=height - kiss_end_y)

        # T2 auto
        x = 120
        y = 430
        # t1_label = tk.Label(self.tab, text='T1:')
        self._t2_auto_var = tk.BooleanVar(self.tab)
        self._t2_auto = tk.Checkbutton(self.tab, text='T2Auto', variable=self._t2_auto_var, command=self._t2_auto_check)
        self._t2_auto.var = self._t2_auto_var
        self._default_bg_clr = self._t2_auto.cget('bg')
        # self.t1.insert(tk.END, self.port_setting.parm_T1)
        # t1_label.place(x=t1_x, y=height - t1_y)
        self._t2_auto.place(x=x, y=height - y)
        # T2
        t2_x = 20
        t2_y = 430
        t2_label = tk.Label(self.tab, text='T2:')
        self._t2 = tk.Entry(self.tab, width=5)
        # self._t2.insert(tk.END, self._port_setting.parm_T2)
        self._t2.insert(tk.END, self._port_setting.get('parm_T2', new_cfg.get('parm_T2', 1700)))
        t2_label.place(x=t2_x, y=height - t2_y)
        self._t2.place(x=t2_x + 40, y=height - t2_y)
        # T3
        t3_x = 230
        t3_y = 430
        t3_label = tk.Label(self.tab, text='T3:')
        self._t3 = tk.Entry(self.tab, width=5)
        # self._t3.insert(tk.END, self._port_setting.parm_T3)
        self._t3.insert(tk.END, self._port_setting.get('parm_T3', new_cfg.get('parm_T3', 180)))
        t3_label.place(x=t3_x, y=height - t3_y)
        self._t3.place(x=t3_x + 40, y=height - t3_y)
        # N2
        n2_x = 350
        n2_y = 430
        n2_label = tk.Label(self.tab, text='N2:')
        self._n2 = tk.Entry(self.tab, width=4)
        # self._n2.insert(tk.END, self._port_setting.parm_N2)
        self._n2.insert(tk.END, self._port_setting.get('parm_N2', new_cfg.get('parm_N2', 20)))
        n2_label.place(x=n2_x, y=height - n2_y)
        self._n2.place(x=n2_x + 40, y=height - n2_y)
        # Kiss duplex
        x = 520
        y = 430
        self._kiss_duplex_var = tk.IntVar(self.tab)
        self._kiss_duplex_ent = tk.Checkbutton(self.tab, text='Full-Duplex', variable=self._kiss_duplex_var)
        # self._kiss_duplex_var.set(self._port_setting.parm_kiss_F_Duplex)
        self._kiss_duplex_var.set(self._port_setting.get('parm_kiss_F_Duplex', new_cfg.get('parm_kiss_F_Duplex', 0)))
        self._kiss_duplex_ent.place(x=x, y=height - y)
        if self._port_setting.get('parm_kiss_is_on', new_cfg.get('parm_kiss_is_on', True)):
            # self._kiss_duplex_var.set(self._port_setting.parm_kiss_F_Duplex)
            self._kiss_duplex_var.set(self._port_setting.get('parm_kiss_F_Duplex', new_cfg.get('parm_kiss_F_Duplex', 0)))
        else:
            self._kiss_duplex_var.set(0)
            self._kiss_duplex_ent.deselect()
            self._kiss_duplex_ent.configure(state='disabled')
        #######################
        # LAbel
        stdp_x = 20
        stdp_y = 375
        std_pam_label = tk.Label(self.tab, text=get_strTab('port_cfg_std_parm', self._lang))

        std_pam_label.place(x=stdp_x, y=height - stdp_y)

        #########################
        # Port Default Packet Length
        pac_len_x = 20
        pac_len = 340
        pac_len_label = tk.Label(self.tab, text='Pac Len:')
        self._pac_len = tk.Entry(self.tab, width=5)
        # self._pac_len.insert(tk.END, str(self._port_setting.parm_PacLen))
        self._pac_len.insert(tk.END, str(self._port_setting.get('parm_PacLen', new_cfg.get('parm_PacLen', 160))))
        pac_len_help = tk.Label(self.tab, text=get_strTab('port_cfg_pac_len', self._lang))
        pac_len_label.place(x=pac_len_x, y=height - pac_len)
        self._pac_len.place(x=pac_len_x + 80, y=height - pac_len)
        pac_len_help.place(x=pac_len_x + 80 + 70, y=height - pac_len)

        #########################
        # Port Default Max Pac
        max_pac_x = 20
        max_pac_y = 305
        max_pac_label = tk.Label(self.tab, text='Max Pac:')

        opt_max_pac = list(range(1, 8))
        self._max_pac_var = tk.StringVar(self.tab)
        # self._max_pac_var.set(str(self._port_setting.parm_MaxFrame))  # default value
        self._max_pac_var.set(str(self._port_setting.get('parm_MaxFrame', new_cfg.get('parm_MaxFrame', 3))))  # default value
        max_pac = tk.OptionMenu(self.tab, self._max_pac_var, *opt_max_pac)
        max_pac.configure(width=4, height=1)
        max_pac_help = tk.Label(self.tab, text=get_strTab('port_cfg_pac_max', self._lang))
        max_pac_label.place(x=max_pac_x, y=height - max_pac_y)
        max_pac.place(x=max_pac_x + 80, y=height - max_pac_y)
        max_pac_help.place(x=max_pac_x + 80 + 70, y=height - max_pac_y)

        ####################################
        # Monitor COLOR Selector SIDE Frame
        f_x = 480
        f_y = 340
        f_height = 180
        bg_cl = 'grey80'
        mon_col_frame = tk.Frame(self.tab, width=440, height=f_height)
        mon_col_frame.configure(bg=bg_cl)
        mon_col_frame.place(x=f_x, y=height - f_y)
        # Label
        mon_col_la_x = 160
        mon_col_la_y = 15
        mon_col_label = tk.Label(mon_col_frame, text=get_strTab('mon_color', self._lang), bg=bg_cl)
        mon_col_label.place(x=mon_col_la_x, y=mon_col_la_y)
        #################
        # preview win TX
        # bg = self.station_setting.stat_parm_qso_col_bg
        # fg = self.station_setting.stat_parm_qso_col_text
        self._color_example_text_tx = tk.Text(mon_col_frame,
                                              height=3,
                                              width=28,
                                              font=('Courier', 11),
                                              # fg=self._port_setting.parm_mon_clr_tx,
                                              fg=self._port_setting.get('parm_mon_clr_tx', new_cfg.get('parm_mon_clr_tx', DEF_PORT_MON_TX_COL)),
                                              bg=self._port_setting.get('parm_mon_clr_bg', new_cfg.get('parm_mon_clr_bg', DEF_PORT_MON_BG_COL)),
                                              # bg=self._port_setting.parm_mon_clr_bg
                                              )
        self._color_example_text_tx.place(x=100, y=10)
        self._color_example_text_tx.insert(tk.END, 'TX> Test TEXT. 1234. 73...')
        # preview win RX
        self._color_example_text_rx = tk.Text(mon_col_frame,
                                              height=3,
                                              width=28,
                                              font=('Courier', 11),
                                              # fg=self._port_setting.parm_mon_clr_rx,
                                              # bg=self._port_setting.parm_mon_clr_bg
                                              fg = self._port_setting.get('parm_mon_clr_rx', new_cfg.get('parm_mon_clr_rx', DEF_PORT_MON_RX_COL)),
                                              bg = self._port_setting.get('parm_mon_clr_bg', new_cfg.get('parm_mon_clr_bg', DEF_PORT_MON_BG_COL)),

        )
        self._color_example_text_rx.place(x=100, y=100)
        self._color_example_text_rx.insert(tk.END, 'RX> Test TEXT. 1234. 73...')
        #################
        # TX
        tx_sel_x = 20
        tx_sel_y = 20
        tk.Button(mon_col_frame,
                  text='TX',
                  command=lambda: self._choose_color('TX')
                  ).place(x=tx_sel_x, y=tx_sel_y)

        #################
        # RX
        rx_sel_x = 20
        rx_sel_y = 70
        tk.Button(mon_col_frame,
                  text='RX',
                  command=lambda: self._choose_color('RX')
                  ).place(x=rx_sel_x, y=rx_sel_y)
        #################
        # BG
        bg_sel_x = 20
        bg_sel_y = 120
        tk.Button(mon_col_frame,
                  text='BG',
                  command=lambda: self._choose_color('BG')
                  ).place(x=bg_sel_x, y=bg_sel_y)

        #####################################
        #################
        # Station CFGs

        self._stat_check_vars = {}
        # self._all_stat_cfgs = get_all_stat_cfg()
        self._all_stat_cfgs = POPT_CFG.get_stat_CFGs()
        x_f = 0
        y_f = 1
        # if self._port_setting.parm_PortNr in PORT_HANDLER.get_all_ports().keys():
        # if self._port_setting.get('parm_PortNr', new_cfg.get('parm_PortNr', -1)) in PORT_HANDLER.get_all_ports().keys():
        prim_port = PORT_HANDLER.get_dualPort_primary_PH(
            self._port_setting.get('parm_PortNr', new_cfg.get('parm_PortNr', -1)))

        if prim_port:
            prim_port_id = prim_port.port_id
            if prim_port_id != self._port_setting.get('parm_PortNr', new_cfg.get('parm_PortNr', -1)):
                cfg_x = 20
                cfg_y = 290 - 35
                # prim_port = PORT_HANDLER.get_dualPort_primary_PH(self._port_setting.get('parm_PortNr', new_cfg.get('parm_PortNr', -1)))
                # prim_port_id = '! ERROR !'
                # if prim_port:
                tk.Label(self.tab,
                         text=f"Dual Port: Secondary-P: {self._port_setting.get('parm_PortNr', new_cfg.get('parm_PortNr', -1))}. Primary-P:  {prim_port_id}"
                         ).place(x=cfg_x, y=height - cfg_y)

                self._update_port_parameter()
                return
        self._update_port_parameter()



        for k in self._all_stat_cfgs.keys():
            # stat = self.all_stat_cfgs[k]
            cfg_x = 20 + x_f
            cfg_y = 290 - (35 * y_f)  # Yeah X * 0
            var = tk.IntVar(self.tab)

            cfg = tk.Checkbutton(self.tab, text=k, width=10, variable=var, anchor='w', state='normal')

            # if k in self._port_setting.parm_StationCalls:
            if k in self._port_setting.get('parm_StationCalls', new_cfg.get('parm_StationCalls', [])):
                var.set(1)
                cfg.select()
            # cfg.var = var
            self._stat_check_vars[k] = var
            cfg.place(x=cfg_x, y=height - cfg_y)
            cfg.var = var
            if y_f == 3:
                y_f = 1
                x_f += 150
            else:
                y_f += 1

    def _choose_color(self, fg_bg: str):
        new_cfg = getNew_port_cfg()
        if fg_bg == 'TX':
            # col = askcolor(self._port_setting.parm_mon_clr_tx, title='TX')
            col: tuple = askcolor(self._port_setting.get('parm_mon_clr_tx',
                                                  new_cfg.get('parm_mon_clr_tx', DEF_PORT_MON_TX_COL)),
                           title='TX')
            if col[1] is not None:
                if col:
                    self._port_setting['parm_mon_clr_tx'] = col[1]
                    self._color_example_text_tx.configure(fg=col[1])
        elif fg_bg == 'RX':
            # col = askcolor(self._port_setting.parm_mon_clr_rx, title='RX')
            col = askcolor(self._port_setting.get('parm_mon_clr_rx',
                                                  new_cfg.get('parm_mon_clr_rx', DEF_PORT_MON_RX_COL)),
                           title='RX')
            if col[1] is not None:
                if col:
                    # self._port_setting.parm_mon_clr_rx = col[1]
                    self._port_setting['parm_mon_clr_rx'] = col[1]
                    self._color_example_text_rx.configure(fg=col[1])
        elif fg_bg == 'BG':
            # col = askcolor(self._port_setting.parm_mon_clr_bg, title=STR_TABLE['bg_color'][self._lang])
            col = askcolor(self._port_setting.get('parm_mon_clr_bg',
                                                  new_cfg.get('parm_mon_clr_bg', DEF_PORT_MON_BG_COL)),
                           title=get_strTab('bg_color', self._lang))
            if col[1] is not None:
                if col:
                    # self._port_setting.parm_mon_clr_bg = col[1]
                    self._port_setting['parm_mon_clr_bg'] = col[1]
                    self._color_example_text_tx.configure(bg=col[1])
                    self._color_example_text_rx.configure(bg=col[1])

        #self._main_cl.get_root_sett_win().attributes("-topmost", True)

    def _update_Mcast_settings(self, event=None):
        self._main_cl.switch_mcast_chb(self._axip_multicast_var.get(), self._port_setting.get('parm_PortNr', -1))

    def disable_mcast(self, port_id, disable):
        if self._port_select_var.get() != 'AXIP':
            self._axip_multicast_dd.configure(state='disabled')
        else:
            if disable:
                self._axip_multicast_dd.configure(state='disabled')
            else:
                self._axip_multicast_dd.configure(state='normal')

    def _update_port_parameter(self, dummy=None):
        height = self._height
        param_sel_x = 20
        param_sel_y = 535
        param_next_line = 0
        typ = self._port_select_var.get()
        new_port_cfg = getNew_port_cfg()
        if typ == 'KISSTCP':

            self._kiss_txd.configure(state="normal")
            self._kiss_pers.configure(state="normal")
            self._kiss_tail.configure(state="normal")
            self._kiss_slot.configure(state="normal")
            self._kiss_duplex_ent.configure(state='normal')

            #self._test_call.configure(state="disabled")
            #self._test_inter.configure(state="disabled")
            #self._test_fail.configure(state="disabled")
            #self._axip_linktest_dd.configure(state="disabled")
            self._axip_multicast_dd.configure(state="disabled")
            self._ptxd.configure(state="normal")
            self._calc_baud.configure(state="normal")
            self._calc_baud.delete(0, tk.END)
            # self._calc_baud.insert(tk.END, self._port_setting.parm_baud)
            self._calc_baud.insert(tk.END, self._port_setting.get('parm_baud', new_port_cfg.get('parm_baud', 1200)))
            self._param1_label.configure(text='Adresse:')
            self._param1_ent.configure(width=28)
            self._param2_label.configure(text='Port:')
            self._param2_ent.configure(width=7)
            self._param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
            self._param1_ent.place(x=param_sel_x + 80, y=height - param_sel_y + param_next_line)
            self._param2_label.place(x=param_sel_x + 500, y=height - param_sel_y + param_next_line)
            self._param2_ent.place(x=param_sel_x + 500 + 50, y=height - param_sel_y + param_next_line)
            self._param1_ent.delete(0, tk.END)
            self._param2_ent.delete(0, tk.END)
            # if self._port_setting.parm_PortParm[0]:
            # if self._port_setting.get('parm_PortParm', new_cfg.get('parm_PortParm', ('', 0)))[0]:
                # self._param1_ent.insert(tk.END, self._port_setting.parm_PortParm[0])
            self._param1_ent.insert(tk.END, self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[0])
            # if self._port_setting.parm_PortParm[1]:
            # if self._port_setting.get('parm_PortParm', new_cfg.get('parm_PortParm', ('', 0)))[1]:
                # self._param2_ent.insert(tk.END, self._port_setting.parm_PortParm[1])
            self._param2_ent.insert(tk.END, self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[1])
            """
            self.t1.configure(state="normal")
            self.t1.delete(0, tk.END)
            self.t1.insert(tk.END, self.port_setting.parm_T1)
            """
            self._t2.configure(state="normal")
            self._t2.delete(0, tk.END)
            # self._t2.insert(tk.END, self._port_setting.parm_T2)
            self._t2.insert(tk.END, self._port_setting.get('parm_T2', new_port_cfg.get('parm_T2', 1700)))

        elif typ == 'AXIP':

            mcast_port = PORT_HANDLER.get_mcast_server().get_mcast_port()
            if not hasattr(mcast_port, 'port_id'):
                self._axip_multicast_dd.configure(state="normal")
                # if self._port_setting.parm_axip_Multicast:
                if self._port_setting.get('parm_axip_Multicast',False):
                    self._axip_multicast_var.set(1)
                    self._axip_multicast_dd.select()
                else:
                    self._axip_multicast_var.set(0)
                    self._axip_multicast_dd.deselect()
            else:
                mcast_port_id = int(mcast_port.port_id)
                if self._port_setting.get('parm_PortNr', -1) == mcast_port_id:

                    self._axip_multicast_dd.configure(state="normal")
                    self._axip_multicast_var.set(1)
                    self._axip_multicast_dd.select()
                else:
                    self._axip_multicast_dd.configure(state="disabled")
                    self._axip_multicast_var.set(0)
                    self._axip_multicast_dd.deselect()


            self._kiss_txd.configure(state="disabled")
            self._kiss_pers.configure(state="disabled")
            self._kiss_tail.configure(state="disabled")
            self._kiss_slot.configure(state="disabled")
            self._kiss_duplex_ent.configure(state='disabled')

            self._ptxd.configure(state="normal")
            self._ptxd.delete(0, tk.END)
            self._ptxd.insert(tk.END, '1')
            self._ptxd.configure(state="disabled")

            self._calc_baud.configure(state="normal")
            self._calc_baud.delete(0, tk.END)
            self._calc_baud.insert(tk.END, '115200')
            self._calc_baud.configure(state="disabled")
            """
            self.t1.configure(state="normal")
            self.t1.delete(0, tk.END)
            self.t1.insert(tk.END, '1')
            self.t1.configure(state="disabled")
            """
            self._t2.configure(state="normal")

            self._t2.delete(0, tk.END)
            self._t2.insert(tk.END, '1')
            self._t2.configure(state="disabled")

            self._param1_label.configure(text='Adresse:')
            self._param1_ent.configure(width=28)
            self._param2_label.configure(text='Port:')
            self._param2_ent.configure(width=7)
            self._param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
            self._param1_ent.place(x=param_sel_x + 80, y=height - param_sel_y + param_next_line)
            self._param2_label.place(x=param_sel_x + 500, y=height - param_sel_y + param_next_line)
            self._param2_ent.place(x=param_sel_x + 500 + 50, y=height - param_sel_y + param_next_line)

            self._param1_ent.delete(0, tk.END)
            self._param2_ent.delete(0, tk.END)
            if self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[0]:
                # self._param1_ent.insert(tk.END, self._port_setting.parm_PortParm[0])
                self._param1_ent.insert(tk.END, self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[0])
            else:
                self._param1_ent.insert(tk.END, '0.0.0.0')
            # if self._port_setting.parm_PortParm[1]:
            if self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[1]:
                self._param2_ent.insert(tk.END, self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[1])

        elif typ == 'KISSSER':
            #self._axip_linktest_dd.configure(state="disabled")
            self._axip_multicast_dd.configure(state="disabled")
            #self._test_call.configure(state="disabled")
            #self._test_inter.configure(state="disabled")
            #self._test_fail.configure(state="disabled")

            self._kiss_txd.configure(state="normal")
            self._kiss_pers.configure(state="normal")
            self._kiss_tail.configure(state="normal")
            self._kiss_slot.configure(state="normal")
            self._kiss_duplex_ent.configure(state='normal')

            self._ptxd.configure(state="normal")
            self._calc_baud.configure(state="normal")
            self._calc_baud.delete(0, tk.END)
            # self.calc_baud.insert(tk.END, str(self.port_setting.parm_PortParm[1]))
            # self._calc_baud.insert(tk.END, self._port_setting.parm_baud)
            self._calc_baud.insert(tk.END, self._port_setting.get('parm_baud', new_port_cfg.get('parm_baud', 1200)))
            # self.calc_baud.configure(state="normal")
            self._param1_ent.configure(width=15)

            self._param1_label.configure(text='Port:')

            self._param2_label.configure(text='Baud:')
            self._param2_ent.configure(width=7)
            self._param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
            self._param1_ent.place(x=param_sel_x + 50, y=height - param_sel_y + param_next_line)
            self._param2_label.place(x=param_sel_x + 250, y=height - param_sel_y + param_next_line)
            self._param2_ent.place(x=param_sel_x + 250 + 60, y=height - param_sel_y + param_next_line)

            self._param1_ent.delete(0, tk.END)
            self._param2_ent.delete(0, tk.END)
            if self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[0]:
                self._param1_ent.insert(tk.END, self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[0])
            else:
                if is_linux():
                    self._param1_ent.insert(tk.END, '/dev/ttyS1')
                else:
                    self._param1_ent.insert(tk.END, 'com1')
            if self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[1]:
                self._param2_ent.insert(tk.END, self._port_setting.get('parm_PortParm', new_port_cfg.get('parm_PortParm', ('', 0)))[1])

            """
            self.t1.configure(state="normal")
            self.t1.delete(0, tk.END)
            self.t1.insert(tk.END, self.port_setting.parm_T1)
            """
            self._t2.configure(state="normal")
            self._t2.delete(0, tk.END)
            # self._t2.insert(tk.END, self._port_setting.parm_T2)
            self._t2.insert(tk.END, self._port_setting.get('parm_T2', new_port_cfg.get('parm_T2', 1700)))

        # if self._port_setting.parm_T2_auto:
        if self._port_setting.get('parm_T2_auto', new_port_cfg.get('parm_T2_auto', True)):
            self._t2_auto_var.set(True)
            self._t2_auto.select()
        else:
            self._t2_auto_var.set(False)
            self._t2_auto.deselect()
        self._t2_auto_check()
        # print(self.port_setting.parm_T2_auto)

    def set_vars_to_cfg(self, event=None):
        old_cfg = dict(self._port_setting)
        # Port Name
        self._port_setting['parm_PortName'] = self._prt_name.get()
        # Port TYpe
        old_typ = str(self._port_setting.get('parm_PortTyp', ''))
        self._port_setting['parm_PortTyp'] = self._port_select_var.get()
        if all((self._port_setting.get('parm_PortTyp', ''),
                self._port_setting.get('parm_PortTyp', '') != old_typ)):
            self._need_reinit = True
        # Port Parameter
        try:
            tmp_param = (self._param1_ent.get(), int(self._param2_ent.get()))
        except ValueError:
            tmp_param = (self._param1_ent.get(), 0)
        self._port_setting['parm_PortParm'] = tmp_param
        # Pseudo TXD
        try:
            self._port_setting['parm_TXD'] = int(self._ptxd.get())
        except ValueError:
            self._port_setting['parm_TXD'] = 30

        #############
        # KISS
        if self._port_select_var.get() in ['KISSSER', 'KISSTCP']:
            self._port_setting['parm_kiss_is_on'] = True
            self._port_setting['parm_kiss_TXD'] = int(self._kiss_txd.get())
            self._port_setting['parm_kiss_Pers'] = int(self._kiss_pers.get())
            self._port_setting['parm_kiss_Slot'] = int(self._kiss_slot.get())
            self._port_setting['parm_kiss_Tail'] = int(self._kiss_tail.get())
            self._port_setting['parm_kiss_F_Duplex'] = self._kiss_duplex_var.get()
        else:
            self._port_setting['parm_kiss_is_on'] = False

        self._port_setting['parm_kiss_init_cmd'] = self._kiss_start_cmd_tab.get(self._kiss_start_var.get(), b'')
        self._port_setting['parm_kiss_end_cmd'] = self._kiss_end_cmd_tab.get(self._kiss_end_var.get(), b'')
        # Baud
        # if self.port_setting.parm_PortTyp == 'KISSSER':
        # self.calc_baud.insert(tk.END, str(self.port_setting.parm_PortParm[1]))
        self._port_setting['parm_baud'] = int(self._calc_baud.get())
        # T 2 auto
        self._port_setting['parm_T2_auto'] = bool(self._t2_auto_var.get())
        # T 2
        self._port_setting['parm_T2'] = int(self._t2.get())
        # T 3
        self._port_setting['parm_T3'] = int(self._t3.get())
        # N 2
        self._port_setting['parm_N2'] = int(self._n2.get())
        # Port Default Packet Length
        self._port_setting['parm_PacLen'] = int(self._pac_len.get())
        # Port Default Max Pac
        self._port_setting['parm_MaxFrame'] = int(self._max_pac_var.get())
        # Monitor COLOR Selector SIDE Frame
        # TX
        # self.port_setting.parm_mon_clr_tx = self.tx_col_select_var.get()
        # RX
        # self.port_setting.parm_mon_clr_rx = self.rx_col_select_var.get()
        if self._port_select_var.get() == 'AXIP':
            self._port_setting['parm_full_duplex'] = True   # FIXME: Alte Programme bekommen Probleme damit.
        else:
            self._port_setting['parm_full_duplex'] = False

        self._port_setting['parm_axip_Multicast'] = bool(self._axip_multicast_var.get())
        # self._port_setting['parm_axip_fail'] = int(self._test_fail.get())

        # self._port_setting['parm_StationCalls'] = []
        # self.port_setting.parm_Stations = []
        stat_calls = []
        for k in self._stat_check_vars.keys():
            if k in self._all_stat_cfgs.keys() and \
                    self._stat_check_vars[k].get():
                stat_calls.append(k)

        self._port_setting['parm_StationCalls'] = stat_calls
        self._save_cfg_to_poptCFG()
        if all((self._port_setting.get('arm_PortTyp', ''),
                old_cfg != self._port_setting)):
            self._need_reinit = True
        # self._need_reinit = False

    def need_reinit(self):
        return self._need_reinit

    def set_need_reinit(self, event=None):
        self._need_reinit = True

    def _save_cfg_to_poptCFG(self):
        if not self._port_setting.get('parm_PortTyp'):
            return False
        POPT_CFG.set_port_CFG_fm_id(self._port_setting.get('parm_PortNr', -1),
                                    self._port_setting)

    def _t2_auto_check(self):
        if self._t2_auto_var.get():
            self._t2_auto.configure(bg='green')
            self._t2.configure(state='disabled')
        else:
            self._t2_auto.configure(bg=self._default_bg_clr)
            self._t2.configure(state='normal')


class PortSettingsWin(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        win_height = 600
        win_width = 1059
        self._need_GUI_reinit = False   # Reinit SettingsGUI Tabs
        self._lang = POPT_CFG.get_guiCFG_language()
        ##########################
        ####################################
        # New Station, Del Station Buttons
        new_port_bt = tk.Button(self,
                                text=get_strTab('new_port', self._lang),
                                # font=("TkFixedFont", 15),
                                # bg="green",
                                height=1,
                                width=10,
                                command=self._new_port_btn_cmd)
        del_st_bt = tk.Button(self,
                              text=get_strTab('delete', self._lang),
                              # font=("TkFixedFont", 15),
                              bg="red3",
                              height=1,
                              width=10,
                              command=self._del_port_btn_cmd)
        new_port_bt.place(x=20, y=win_height - 590)
        del_st_bt.place(x=win_width - 141, y=win_height - 590)

        # Root Tab
        self._tabControl = ttk.Notebook(self, height=win_height - 140, width=win_width - 40)
        self._tabControl.place(x=20, y=win_height - 550)
        # Tab Vars
        self._tab_list: {int: ttk.Frame} = {}
        # Tab Frames ( Port Settings )
        all_ports = PORT_HANDLER.get_all_ports_f_cfg()
        all_port_cfgs = POPT_CFG.get_port_CFGs()
        for port_id, port_cfg in all_port_cfgs.items():
            # new_settings = POPT_CFG.get_port_CFG_fm_id(port_id=port_id)
            tab = PortSetTab(self, port_cfg, self._tabControl)
            self._tab_list[port_id] = tab
            port_lable_text = 'Port {}'.format(port_id)
            if port_id not in all_ports:
                port_lable_text += ' (!)'
            elif not all_ports[port_id].device_is_running:
                port_lable_text += ' (!)'
            self._tabControl.add(tab.tab, text=port_lable_text)

    def switch_mcast_chb(self, disable: bool, port_nr: int):
        for port_id, tab in self._tab_list.items():
            if port_id != port_nr:
                tab.disable_mcast(port_id, disable)

    def _new_port_btn_cmd(self):
        new_prtcfg = getNew_port_cfg()
        prt_id = 0
        while prt_id in self._tab_list.keys():
            prt_id += 1
        new_prtcfg['parm_PortNr'] = int(prt_id)
        tab = PortSetTab(self, new_prtcfg , self._tabControl)
        tab.set_need_reinit()
        self._tabControl.add(tab.tab, text=f'Port {prt_id}')
        self._tabControl.select(prt_id)
        self._tab_list[prt_id] = tab

    def _del_port_btn_cmd(self):
        msg = AskMsg(titel='lösche Port', message="Willst du diesen Port wirklich löschen? \n"
                                                  "Alle Einstellungen gehen verloren !", parent_win=self)
        if msg:
            try:
                tab_ind = self._tabControl.index('current')
                ind = self._tabControl.tab('current')
            except tk.TclError:
                pass
            else:
                # PORT_HANDLER.disco_all_Conn()
                # messagebox.showinfo('Stationen werden disconnected !', 'Es werden alle Stationen disconnected')
                ind = ind['text']
                ind = int(ind.replace('Port ', '')[0])
                del_port_data(ind)

                PORT_HANDLER.disco_conn_fm_port(ind)
                PORT_HANDLER.close_port(ind)
                if POPT_CFG.del_port_CFG_fm_id(ind):
                    del self._tab_list[ind]
                    self._tabControl.forget(tab_ind)
                    messagebox.showinfo('Port gelöscht', 'Das Internet wurde erfolgreich gelöscht.', parent=self)
                    #self._main_class.sysMsg_to_monitor('Info: Port erfolgreich gelöscht.')
                    self._need_GUI_reinit = True    # Reinit SettingsGUI Tabs
                else:
                    logger.error(f'Port {ind} konnte nicht gelöscht werden')
                    #self._main_class.sysMsg_to_monitor(f'Port {ind} konnte nicht gelöscht werden')
        else:
            messagebox.showinfo('Abgebrochen', 'Das war eine sehr gute Entscheidung. '
                                   'Das hast du gut gemacht, mach weiter so. ', parent=self)
            #self._main_class.sysMsg_to_monitor('Hinweis: Irgendetwas ist abgebrochen !?!')

    @staticmethod
    def _get_config():
        return dict(POPT_CFG.get_port_CFGs())

    def save_config(self):
        # old_cfg = self._get_config()
        for port_id in self._tab_list.keys():
            self._tab_list[port_id].set_vars_to_cfg()
            if self._tab_list[port_id].need_reinit():
                if PORT_HANDLER.get_all_connections():
                    PORT_HANDLER.disco_all_Conn()
                    # messagebox.showinfo('Stationen werden disconnected !', 'Es werden alle Stationen disconnected')
                    messagebox.showinfo(get_strTab('all_disco1', self._lang),
                                        get_strTab('all_disco2', self._lang),
                                        parent=self)

                PORT_HANDLER.reinit_port(port_id)
                self._need_GUI_reinit = True
        """        
        if old_cfg == self._get_config():
            return self._need_GUI_reinit
        """
        """
        if self._need_GUI_reinit:
            threading.Thread(target=PORT_HANDLER.reinit_all_ports).start()
            # self._need_GUI_reinit = False
        """
        return self._need_GUI_reinit
