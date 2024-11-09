import time
import tkinter as tk
import threading
from tkinter import ttk as ttk, messagebox
from tkinter.colorchooser import askcolor

from ax25.ax25InitPorts import PORT_HANDLER
from gui.guiMsgBoxes import AskMsg, WarningMsg, InfoMsg
from cfg.config_station import get_all_stat_cfg, del_port_data, DefaultPort
from fnc.os_fnc import is_linux
from cfg.string_tab import STR_TABLE


class PortSetTab:
    def __init__(self, main_stt_win, setting, tabclt: ttk.Notebook):
        self.tab_clt = tabclt
        self.main_cl = main_stt_win
        self.lang = main_stt_win.lang
        # self.ports_sett: {int: DefaultPortConfig} = main_stt_win.all_port_settings
        self._height = main_stt_win.get_win_height()
        height = self._height
        self._width = main_stt_win.win_width

        self.port_setting = setting
        port_types = PORT_HANDLER.get_ax25types_keys()
        self.style = main_stt_win.style
        self.tab = ttk.Frame(self.tab_clt)
        #################
        # Port Name
        name_x = 20
        name_y = 570
        name_label = tk.Label(self.tab, text=STR_TABLE['port_cfg_port_name'][self.lang])
        name_label.place(x=name_x, y=height - name_y)
        self._prt_name = tk.Entry(self.tab, width=5)
        self._prt_name.place(x=name_x + 420, y=height - name_y)
        self._prt_name.insert(tk.END, self.port_setting.parm_PortName)
        ######################
        # Not initialised Info
        all_ports = PORT_HANDLER.ax25_ports
        if self.port_setting.parm_PortNr in all_ports.keys():
            if not all_ports[self.port_setting.parm_PortNr].device_is_running:
                x = 520
                y = 570
                label = tk.Label(self.tab, text=STR_TABLE['port_cfg_not_init'][self.lang], fg='red')
                label.place(x=x, y=height - y)
        else:
            x = 520
            y = 570
            label = tk.Label(self.tab, text=STR_TABLE['port_cfg_not_init'][self.lang], fg='red')
            label.place(x=x, y=height - y)
        #################
        # Port Typ
        port_x = 800
        port_y = 570
        port_label = tk.Label(self.tab, text='Typ:')
        port_label.place(x=port_x, y=height - port_y)
        self._port_select_var = tk.StringVar(self.tab)

        opt = port_types
        self._port_select_var.set(self.port_setting.parm_PortTyp)  # default value
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

        #########################
        # Pseudo TXD
        ptxd_x = 20
        ptxd_y = 500
        ptxd_label = tk.Label(self.tab, text='P-TXD:')
        self._ptxd = tk.Entry(self.tab, width=5)
        self._ptxd.insert(tk.END, self.port_setting.parm_TXD)
        ptxd_help = tk.Label(self.tab, text=STR_TABLE['port_cfg_psd_txd'][self.lang])

        ptxd_label.place(x=ptxd_x, y=height - ptxd_y)
        self._ptxd.place(x=ptxd_x + 80, y=height - ptxd_y)
        ptxd_help.place(x=ptxd_x + 80 + 70, y=height - ptxd_y)

        # Baud
        calc_baud_x = 20
        calc_baud_y = 465
        calc_baud_label = tk.Label(self.tab, text='Baud:')
        self._calc_baud = tk.Entry(self.tab, width=8)
        if self.port_setting.parm_PortTyp == 'KISSSER':
            ins = self.port_setting.parm_PortParm[1]
            self._calc_baud.insert(tk.END, ins)
            self._calc_baud.configure(state="disabled")
        else:
            ins = self.port_setting.parm_baud
            self._calc_baud.insert(tk.END, ins)
            self._calc_baud.configure(state="normal")
        calc_baud_label.place(x=calc_baud_x, y=height - calc_baud_y)
        self._calc_baud.place(x=calc_baud_x + 80, y=height - calc_baud_y)

        # KISS TXD
        kiss_txd_x = 210
        kiss_txd_y = 465
        kiss_txd_label = tk.Label(self.tab, text='TXD:')
        self._kiss_txd = tk.Entry(self.tab, width=3)
        if self.port_setting.parm_kiss_is_on:
            # ins = self.port_setting.parm_PortParm[1]
            self._kiss_txd.insert(tk.END, str(self.port_setting.parm_kiss_TXD))
            self._kiss_txd.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_txd.insert(tk.END, '0')
            self._kiss_txd.configure(state="disabled")
        kiss_txd_label.place(x=kiss_txd_x, y=height - kiss_txd_y)
        self._kiss_txd.place(x=kiss_txd_x + 50, y=height - kiss_txd_y)
        # KISS PERS
        kiss_pers_x = 320
        kiss_pers_y = 465
        kiss_pers_label = tk.Label(self.tab, text='PERS:')
        self._kiss_pers = tk.Entry(self.tab, width=3)
        if self.port_setting.parm_kiss_is_on:
            # ins = self.port_setting.parm_PortParm[1]
            self._kiss_pers.insert(tk.END, str(self.port_setting.parm_kiss_Pers))
            self._kiss_pers.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_pers.insert(tk.END, '0')
            self._kiss_pers.configure(state="disabled")
        kiss_pers_label.place(x=kiss_pers_x, y=height - kiss_pers_y)
        self._kiss_pers.place(x=kiss_pers_x + 60, y=height - kiss_pers_y)
        # KISS Slot
        slot_x = 440
        slot_y = 465
        slot_label = tk.Label(self.tab, text='SLOT:')
        self._kiss_slot = tk.Entry(self.tab, width=3)
        # if self.port_setting.parm_PortTyp == 'AXIP':
        if self.port_setting.parm_kiss_is_on:
            # ins = self.port_setting.parm_PortParm[1]
            self._kiss_slot.insert(tk.END, str(self.port_setting.parm_kiss_Slot))
            self._kiss_slot.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_slot.insert(tk.END, '0')
            self._kiss_slot.configure(state="disabled")
        slot_label.place(x=slot_x, y=height - slot_y)
        self._kiss_slot.place(x=slot_x + 60, y=height - slot_y)
        # KISS TAIL
        kiss_tail_x = 560
        kiss_tail_y = 465
        kiss_tail_label = tk.Label(self.tab, text='TAIL:')
        self._kiss_tail = tk.Entry(self.tab, width=3)
        # if self.port_setting.parm_PortTyp == 'AXIP':
        if self.port_setting.parm_kiss_is_on:
            # ins = self.port_setting.parm_PortParm[1]
            self._kiss_tail.insert(tk.END, str(self.port_setting.parm_kiss_Tail))
            self._kiss_tail.configure(state="normal")
        else:
            # ins = self.port_setting.parm_baud
            self._kiss_tail.insert(tk.END, '0')
            self._kiss_tail.configure(state="disabled")
        kiss_tail_label.place(x=kiss_tail_x, y=height - kiss_tail_y)
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
                                                 command=self._update_port_parameter,
                                                 state='disabled')
        self._axip_multicast_dd.var = self._axip_multicast_var
        if self.port_setting.parm_PortTyp == 'AXIP':
            self._axip_multicast_dd.configure(state="normal")
            if self.port_setting.parm_axip_Multicast:
                self._axip_multicast_var.set(1)
                self._axip_multicast_dd.select()
            else:
                self._axip_multicast_var.set(0)
                self._axip_multicast_dd.deselect()
        else:
            self._axip_multicast_var.set(0)
            self._axip_multicast_dd.deselect()
            self._axip_multicast_dd.configure(state="disabled")
        self._axip_multicast_dd.place(x=axip_multicast_x + 20, y=height - axip_multicast_y)
        # TODO LinkTester
        axip_linktest_x = 650
        axip_linktest_y = 465
        self._axip_linktest_var = tk.IntVar(self.tab)
        # self.axip_multicast_var.set(0)
        self._axip_linktest_dd = tk.Checkbutton(self.tab, text='Linktest', variable=self._axip_multicast_var)
        if self.port_setting.parm_PortTyp == 'AXIP':
            # ins = self.port_setting.parm_PortParm[1]
            # self.kiss_tail.insert(tk.END, '0')
            self._axip_linktest_dd.configure(state="disabled")  # TODO state='normal
        else:
            # ins = self.port_setting.parm_baud
            # self.kiss_tail.insert(tk.END, '0')
            self._axip_linktest_dd.configure(state="disabled")
        # kiss_tail_label.place(x=kiss_tail_x, y=height - kiss_tail_y)
        self._axip_linktest_dd.place(x=axip_linktest_x + 50, y=height - axip_linktest_y)
        # TODO linktest Call
        test_call_x = 820
        test_call_y = 395
        test_call_label = tk.Label(self.tab, text='CALL:')
        self._test_call = tk.Entry(self.tab, width=10)
        if self.port_setting.parm_PortTyp == 'AXIP':
            # ins = self.port_setting.parm_PortParm[1]
            self._test_call.insert(tk.END, 'NOCALL')
            self._test_call.configure(state="disabled")  # TODO state='normal
        else:
            # ins = self.port_setting.parm_baud
            self._test_call.insert(tk.END, '')
            self._test_call.configure(state="disabled")
        test_call_label.place(x=test_call_x, y=height - test_call_y)
        self._test_call.place(x=test_call_x + 60, y=height - test_call_y)
        # TODO linktest Intevall
        test_inter_x = 820
        test_inter_y = 430
        test_inter_label = tk.Label(self.tab, text='Intervall:')
        self._test_inter = tk.Entry(self.tab, width=4)
        if self.port_setting.parm_PortTyp == 'AXIP':
            # ins = self.port_setting.parm_PortParm[1]
            self._test_inter.insert(tk.END, '30')
            self._test_inter.configure(state="disabled")  # TODO state='normal
        else:
            # ins = self.port_setting.parm_baud
            self._test_inter.insert(tk.END, '')
            self._test_inter.configure(state="disabled")
        test_inter_label.place(x=test_inter_x, y=height - test_inter_y)
        self._test_inter.place(x=test_inter_x + 95, y=height - test_inter_y)
        test_fail_x = 820
        test_fail_y = 465  # 395
        test_fail_label = tk.Label(self.tab, text='Versuche:')
        self._test_fail = tk.Entry(self.tab, width=4)
        self._test_fail.insert(tk.END, str(self.port_setting.parm_axip_fail))
        if self.port_setting.parm_PortTyp == 'AXIP' and not self._axip_multicast_var.get():
            self._test_fail.configure(state="normal")
        else:
            self._test_fail.configure(state="disabled")
        test_fail_label.place(x=test_fail_x, y=height - test_fail_y)
        self._test_fail.place(x=test_fail_x + 95, y=height - test_fail_y)

        # T2 auto
        _x = 120
        _y = 430
        # t1_label = tk.Label(self.tab, text='T1:')
        self._t2_auto_var = tk.BooleanVar(self.tab)
        self._t2_auto = tk.Checkbutton(self.tab, text='T2Auto', variable=self._t2_auto_var, command=self._t2_auto_check)
        self._t2_auto.var = self._t2_auto_var
        self._default_bg_clr = self._t2_auto.cget('bg')
        # self.t1.insert(tk.END, self.port_setting.parm_T1)
        # t1_label.place(x=t1_x, y=height - t1_y)
        self._t2_auto.place(x=_x, y=height - _y)
        # T2
        t2_x = 20
        t2_y = 430
        t2_label = tk.Label(self.tab, text='T2:')
        self._t2 = tk.Entry(self.tab, width=5)
        self._t2.insert(tk.END, self.port_setting.parm_T2)
        t2_label.place(x=t2_x, y=height - t2_y)
        self._t2.place(x=t2_x + 40, y=height - t2_y)
        # T3
        t3_x = 230
        t3_y = 430
        t3_label = tk.Label(self.tab, text='T3:')
        self._t3 = tk.Entry(self.tab, width=5)
        self._t3.insert(tk.END, self.port_setting.parm_T3)
        t3_label.place(x=t3_x, y=height - t3_y)
        self._t3.place(x=t3_x + 40, y=height - t3_y)
        # N2
        n2_x = 350
        n2_y = 430
        n2_label = tk.Label(self.tab, text='N2:')
        self._n2 = tk.Entry(self.tab, width=4)
        self._n2.insert(tk.END, self.port_setting.parm_N2)
        n2_label.place(x=n2_x, y=height - n2_y)
        self._n2.place(x=n2_x + 40, y=height - n2_y)
        # Kiss duplex
        _x = 520
        _y = 430
        self._kiss_duplex_var = tk.IntVar(self.tab)
        self._kiss_duplex_ent = tk.Checkbutton(self.tab, text='Full-Duplex', variable=self._kiss_duplex_var)
        self._kiss_duplex_var.set(self.port_setting.parm_kiss_F_Duplex)
        self._kiss_duplex_ent.place(x=_x, y=height - _y)
        if self.port_setting.parm_kiss_is_on:
            self._kiss_duplex_var.set(self.port_setting.parm_kiss_F_Duplex)
        else:
            self._kiss_duplex_var.set(0)
            self._kiss_duplex_ent.deselect()
            self._kiss_duplex_ent.configure(state='disabled')
        #######################
        # LAbel
        stdp_x = 20
        stdp_y = 375
        std_pam_label = tk.Label(self.tab, text=STR_TABLE['port_cfg_std_parm'][self.lang])

        std_pam_label.place(x=stdp_x, y=height - stdp_y)

        #########################
        # Port Default Packet Length
        pac_len_x = 20
        pac_len = 340
        pac_len_label = tk.Label(self.tab, text='Pac Len:')
        self._pac_len = tk.Entry(self.tab, width=5)
        self._pac_len.insert(tk.END, str(self.port_setting.parm_PacLen))
        pac_len_help = tk.Label(self.tab, text=STR_TABLE['port_cfg_pac_len'][self.lang])
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
        self._max_pac_var.set(str(self.port_setting.parm_MaxFrame))  # default value
        max_pac = tk.OptionMenu(self.tab, self._max_pac_var, *opt_max_pac)
        max_pac.configure(width=4, height=1)
        max_pac_help = tk.Label(self.tab, text=STR_TABLE['port_cfg_pac_max'][self.lang])
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
        mon_col_label = tk.Label(mon_col_frame, text=STR_TABLE['mon_color'][self.lang], bg=bg_cl)
        mon_col_label.place(x=mon_col_la_x, y=mon_col_la_y)
        #################
        # preview win TX
        # bg = self.station_setting.stat_parm_qso_col_bg
        # fg = self.station_setting.stat_parm_qso_col_text
        self._color_example_text_tx = tk.Text(mon_col_frame,
                                              height=3,
                                              width=28,
                                              font=('Courier', 11),
                                              fg=self.port_setting.parm_mon_clr_tx,
                                              bg=self.port_setting.parm_mon_clr_bg
                                              )
        self._color_example_text_tx.place(x=100, y=10)
        self._color_example_text_tx.insert(tk.END, 'TX> Test TEXT. 1234. 73...')
        # preview win RX
        self._color_example_text_rx = tk.Text(mon_col_frame,
                                              height=3,
                                              width=28,
                                              font=('Courier', 11),
                                              fg=self.port_setting.parm_mon_clr_rx,
                                              bg=self.port_setting.parm_mon_clr_bg
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
        self._all_stat_cfgs = get_all_stat_cfg()
        x_f = 0
        y_f = 1
        if self.port_setting.parm_PortNr in PORT_HANDLER.get_all_ports().keys():

            for k in self._all_stat_cfgs.keys():
                # stat = self.all_stat_cfgs[k]
                cfg_x = 20 + x_f
                cfg_y = 290 - (35 * y_f)  # Yeah X * 0
                var = tk.IntVar(self.tab)

                cfg = tk.Checkbutton(self.tab, text=k, width=10, variable=var, anchor='w', state='normal')

                if k in self.port_setting.parm_StationCalls:
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
        else:
            cfg_x = 20
            cfg_y = 290 - 35
            prim_port = PORT_HANDLER.get_dualPort_primary_PH(self.port_setting.parm_PortNr)
            prim_port_id = '! ERROR !'
            if prim_port:
                prim_port_id = prim_port.port_id
            tk.Label(self.tab,
                     text=f'Dual Port: Secondary-P: {self.port_setting.parm_PortNr}. Primary-P:  {prim_port_id}'
                     ).place(x=cfg_x, y=height - cfg_y)

        self._update_port_parameter()

    def win_tasker(self):
        # self.update_port_parameter()
        pass

    def _choose_color(self, fg_bg: str):
        self.main_cl.settings_win.attributes("-topmost", False)
        # self.main_cl.settings_win.lower()
        # self.main_cl.settings_win.lift()
        if fg_bg == 'TX':
            col = askcolor(self.port_setting.parm_mon_clr_tx, title='TX')
            if col[1] is not None:
                if col:
                    self.port_setting.parm_mon_clr_tx = col[1]
                    self._color_example_text_tx.configure(fg=col[1])
        elif fg_bg == 'RX':
            col = askcolor(self.port_setting.parm_mon_clr_rx, title='RX')
            if col[1] is not None:
                if col:
                    self.port_setting.parm_mon_clr_rx = col[1]
                    self._color_example_text_rx.configure(fg=col[1])
        elif fg_bg == 'BG':
            col = askcolor(self.port_setting.parm_mon_clr_bg, title=STR_TABLE['bg_color'][self.lang])
            if col[1] is not None:
                if col:
                    self.port_setting.parm_mon_clr_bg = col[1]
                    self._color_example_text_tx.configure(bg=col[1])
                    self._color_example_text_rx.configure(bg=col[1])

        self.main_cl.settings_win.attributes("-topmost", True)

    def _update_port_parameter(self, dummy=None):
        height = self._height
        param_sel_x = 20
        param_sel_y = 535
        param_next_line = 0
        typ = self._port_select_var.get()
        if typ == 'KISSTCP':

            self._kiss_txd.configure(state="normal")
            self._kiss_pers.configure(state="normal")
            self._kiss_tail.configure(state="normal")
            self._kiss_slot.configure(state="normal")
            self._kiss_duplex_ent.configure(state='normal')

            self._test_call.configure(state="disabled")
            self._test_inter.configure(state="disabled")
            self._test_fail.configure(state="disabled")
            self._axip_linktest_dd.configure(state="disabled")
            self._axip_multicast_dd.configure(state="disabled")
            self._ptxd.configure(state="normal")
            self._calc_baud.configure(state="normal")
            self._calc_baud.delete(0, tk.END)
            self._calc_baud.insert(tk.END, self.port_setting.parm_baud)
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
            if self.port_setting.parm_PortParm[0]:
                self._param1_ent.insert(tk.END, self.port_setting.parm_PortParm[0])
            if self.port_setting.parm_PortParm[1]:
                self._param2_ent.insert(tk.END, self.port_setting.parm_PortParm[1])
            """
            self.t1.configure(state="normal")
            self.t1.delete(0, tk.END)
            self.t1.insert(tk.END, self.port_setting.parm_T1)
            """
            self._t2.configure(state="normal")
            self._t2.delete(0, tk.END)
            self._t2.insert(tk.END, self.port_setting.parm_T2)

        elif typ == 'AXIP':
            self._axip_multicast_dd.configure(state="normal")
            self._axip_linktest_dd.configure(state="disabled")  # TODO state='normal
            """
            TODO
            self.test_call.configure(state="normal")
            self.test_inter.configure(state="normal")
            """
            if self._axip_multicast_var.get():
                self._test_fail.configure(state="normal")
            else:
                self._test_fail.configure(state="disabled")
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
            if self.port_setting.parm_PortParm[0]:
                self._param1_ent.insert(tk.END, self.port_setting.parm_PortParm[0])
            else:
                self._param1_ent.insert(tk.END, '0.0.0.0')
            if self.port_setting.parm_PortParm[1]:
                self._param2_ent.insert(tk.END, self.port_setting.parm_PortParm[1])

        elif typ == 'KISSSER':
            self._axip_linktest_dd.configure(state="disabled")
            self._axip_multicast_dd.configure(state="disabled")
            self._test_call.configure(state="disabled")
            self._test_inter.configure(state="disabled")
            self._test_fail.configure(state="disabled")

            self._kiss_txd.configure(state="normal")
            self._kiss_pers.configure(state="normal")
            self._kiss_tail.configure(state="normal")
            self._kiss_slot.configure(state="normal")
            self._kiss_duplex_ent.configure(state='normal')

            self._ptxd.configure(state="normal")
            self._calc_baud.configure(state="normal")
            self._calc_baud.delete(0, tk.END)
            # self.calc_baud.insert(tk.END, str(self.port_setting.parm_PortParm[1]))
            self._calc_baud.insert(tk.END, self.port_setting.parm_baud)
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
            if self.port_setting.parm_PortParm[0]:
                self._param1_ent.insert(tk.END, self.port_setting.parm_PortParm[0])
            else:
                if is_linux():
                    self._param1_ent.insert(tk.END, '/dev/ttyS1')
                else:
                    self._param1_ent.insert(tk.END, 'com1')
            if self.port_setting.parm_PortParm[1]:
                self._param2_ent.insert(tk.END, self.port_setting.parm_PortParm[1])

            """
            self.t1.configure(state="normal")
            self.t1.delete(0, tk.END)
            self.t1.insert(tk.END, self.port_setting.parm_T1)
            """
            self._t2.configure(state="normal")
            self._t2.delete(0, tk.END)
            self._t2.insert(tk.END, self.port_setting.parm_T2)

        if self.port_setting.parm_T2_auto:
            self._t2_auto_var.set(True)
            self._t2_auto.select()
        else:
            self._t2_auto_var.set(False)
            self._t2_auto.deselect()
        self._t2_auto_check()
        # print(self.port_setting.parm_T2_auto)

    def set_vars_to_cfg(self):
        # Port Name
        self.port_setting.parm_PortName = self._prt_name.get()
        # Port TYpe
        self.port_setting.parm_PortTyp = self._port_select_var.get()
        # Port Parameter
        tmp_param = (self._param1_ent.get(), int(self._param2_ent.get()))
        self.port_setting.parm_PortParm = tmp_param
        # Pseudo TXD
        self.port_setting.parm_TXD = int(self._ptxd.get())
        #############
        # KISS
        self.port_setting.parm_kiss_is_on = False
        if self.port_setting.parm_PortTyp in ['KISSSER', 'KISSTCP']:
            self.port_setting.parm_kiss_is_on = True
            self.port_setting.parm_kiss_TXD = int(self._kiss_txd.get())
            self.port_setting.parm_kiss_Pers = int(self._kiss_pers.get())
            self.port_setting.parm_kiss_Slot = int(self._kiss_slot.get())
            self.port_setting.parm_kiss_Tail = int(self._kiss_tail.get())
            self.port_setting.parm_kiss_F_Duplex = self._kiss_duplex_var.get()
        # Baud
        # if self.port_setting.parm_PortTyp == 'KISSSER':
        # self.calc_baud.insert(tk.END, str(self.port_setting.parm_PortParm[1]))
        self.port_setting.parm_baud = int(self._calc_baud.get())
        # T 2 auto
        self.port_setting.parm_T2_auto = bool(self._t2_auto_var.get())
        # T 2
        self.port_setting.parm_T2 = int(self._t2.get())
        # T 3
        self.port_setting.parm_T3 = int(self._t3.get())
        # N 2
        self.port_setting.parm_N2 = int(self._n2.get())
        # Port Default Packet Length
        self.port_setting.parm_PacLen = int(self._pac_len.get())
        # Port Default Max Pac
        self.port_setting.parm_MaxFrame = int(self._max_pac_var.get())
        # Monitor COLOR Selector SIDE Frame
        # TX
        # self.port_setting.parm_mon_clr_tx = self.tx_col_select_var.get()
        # RX
        # self.port_setting.parm_mon_clr_rx = self.rx_col_select_var.get()
        if self.port_setting.parm_PortTyp == 'AXIP':
            self.port_setting.parm_full_duplex = True
        else:
            self.port_setting.parm_full_duplex = False

        self.port_setting.parm_axip_Multicast = bool(self._axip_multicast_var.get())
        self.port_setting.parm_axip_fail = int(self._test_fail.get())

        self.port_setting.parm_stat_PacLen = {}
        self.port_setting.parm_stat_MaxFrame = {}
        self.port_setting.parm_cli = {}
        self.port_setting.parm_StationCalls = []
        # self.port_setting.parm_Stations = []

        for k in self._stat_check_vars.keys():
            if k in self._all_stat_cfgs.keys() and \
                    self._stat_check_vars[k].get():
                """
                print("{} {} {} {}".format(k, self.port_setting.parm_PortNr, self.stat_check_vars[k].get(),
                                           self.stat_check_vars[k]))
                """
                # var = self.stat_check_vars[k]
                # print(var.get())
                stat = self._all_stat_cfgs[k]
                self.port_setting.parm_stat_PacLen[k] = stat.stat_parm_PacLen
                self.port_setting.parm_stat_MaxFrame[k] = stat.stat_parm_MaxFrame
                self.port_setting.parm_cli[k] = stat.stat_parm_cli_cfg
                self.port_setting.parm_StationCalls.append(k)
                # self.port_setting.parm_Stations.append(stat)
                # station_save_files

    def _t2_auto_check(self):
        if self._t2_auto_var.get():
            self._t2_auto.configure(bg='green')
            self._t2.configure(state='disabled')
        else:
            self._t2_auto.configure(bg=self._default_bg_clr)
            self._t2.configure(state='normal')


class PortSettingsWin:
    def __init__(self, main_cl):
        self._main_class = main_cl
        self._win_height = 600
        self.win_width = 1059
        self.style = main_cl.style
        self.settings_win = tk.Toplevel()
        # self.settings_win
        self.settings_win.title("Port-Settings")
        # self._settings_win.geometry("{}x{}".format(self.win_width, self._win_height))
        self.settings_win.geometry(f"{self.win_width}x"
                                   f"{self._win_height}+"
                                   f"{self._main_class.main_win.winfo_x()}+"
                                   f"{self._main_class.main_win.winfo_y()}")
        self.settings_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.settings_win.resizable(False, False)
        # self.settings_win.attributes("-topmost", True)
        try:
            self.settings_win.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.settings_win.lift()
        self.lang = self._main_class.language
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self.settings_win,
                          text="OK",
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self._ok_btn_cmd)

        save_bt = tk.Button(self.settings_win,
                            text=STR_TABLE['save'][self.lang],
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self._save_btn_cmd)

        cancel_bt = tk.Button(self.settings_win,
                              text=STR_TABLE['cancel'][self.lang],
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self._destroy_win)
        ok_bt.place(x=20, y=self._win_height - 50)
        save_bt.place(x=110, y=self._win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self._win_height - 50)
        ####################################
        # New Station, Del Station Buttons
        new_port_bt = tk.Button(self.settings_win,
                                text=STR_TABLE['new_port'][self.lang],
                                # font=("TkFixedFont", 15),
                                # bg="green",
                                height=1,
                                width=10,
                                command=self._new_port_btn_cmd)
        del_st_bt = tk.Button(self.settings_win,
                              text=STR_TABLE['delete'][self.lang],
                              # font=("TkFixedFont", 15),
                              bg="red3",
                              height=1,
                              width=10,
                              command=self._del_port_btn_cmd)
        new_port_bt.place(x=20, y=self._win_height - 590)
        del_st_bt.place(x=self.win_width - 141, y=self._win_height - 590)

        # Root Tab
        self.tabControl = ttk.Notebook(self.settings_win, height=self._win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self._win_height - 550)
        # Tab Vars
        self.tab_list: {int: ttk.Frame} = {}
        # Tab Frames ( Port Settings )
        all_ports = PORT_HANDLER.ax25_ports
        for k in all_ports.keys():
            # port.port_cfg: DefaultPortConfig
            tmp = all_ports[k].port_cfg
            tab = PortSetTab(self, tmp, self.tabControl)
            self.tab_list[k] = tab
            port_lable_text = 'Port {}'.format(k)
            if not all_ports[k].device_is_running:
                port_lable_text += ' (!)'
            self.tabControl.add(tab.tab, text=port_lable_text)

    def _new_port_btn_cmd(self):
        # port.port_cfg: DefaultPortConfig
        prtcfg = DefaultPort()
        prt_id = 0
        while prt_id in self.tab_list.keys():
            prt_id += 1
        prtcfg.parm_PortNr = prt_id

        tab = PortSetTab(self, prtcfg, self.tabControl)
        port_lable_text = 'Port {}'.format(prt_id)
        self.tabControl.add(tab.tab, text=port_lable_text)
        self.tabControl.select(prt_id)
        self.tab_list[prt_id] = tab

    def _del_port_btn_cmd(self):
        self.settings_win.attributes("-topmost", False)
        msg = AskMsg(titel='lösche Port', message="Willst du diesen Port wirklich löschen? \n"
                                                  "Alle Einstellungen gehen verloren !")
        # self.settings_win.lift()
        if msg:
            try:
                # TODO Again ! Such a mess
                tab_ind = self.tabControl.index('current')
                ind = self.tabControl.tab('current')
            except tk.TclError:
                pass
            else:
                ind = ind['text']
                ind = int(ind.replace('Port ', '')[0])

                del_port_data(ind)
                PORT_HANDLER.close_port(ind)
                del self.tab_list[ind]
                self.tabControl.forget(tab_ind)

                WarningMsg('Port gelöscht', 'Das Internet wurde erfolgreich gelöscht.')
                self._main_class.sysMsg_to_monitor('Info: Port erfolgreich gelöscht.')
        else:
            InfoMsg('Abgebrochen', 'Das war eine sehr gute Entscheidung. '
                                   'Das hast du gut gemacht, mach weiter so. ')
            self._main_class.sysMsg_to_monitor('Hinweis: Irgendetwas ist abgebrochen !?!')
        self.settings_win.lift()
        # self.settings_win.attributes("-topmost", True)

    def _destroy_win(self):
        self.settings_win.destroy()
        self._main_class.settings_win = None

    def _save_btn_cmd(self):
        # TODO Cleanup
        PORT_HANDLER.disco_all_Conn()
        # self.settings_win.lower()
        messagebox.showinfo('Stationen werden disconnected !', 'Es werden alle Stationen disconnected')
        self.settings_win.lift()
        self._main_class.sysMsg_to_monitor('Info: Alle Stationen werden disconnected !')
        time.sleep(1)  # TODO Quick fix
        # TODO PORT_HANDLER.is_all_disco()
        PORT_HANDLER.disco_all_Conn()
        self._main_class.sysMsg_to_monitor('Info: Port Einstellungen werden gespeichert.')
        for port_id in self.tab_list.keys():
            self.tab_list[port_id].set_vars_to_cfg()
            self.tab_list[port_id].port_setting.save_to_pickl()
        self._main_class.sysMsg_to_monitor('Info: Port Einstellungen erfolgreich gespeichert.')
        # self._main_class.msg_to_monitor('Lob: Gute Entscheidung!')
        self._main_class.sysMsg_to_monitor('Info: Ports werden neu Initialisiert.')
        threading.Thread(target=PORT_HANDLER.reinit_all_ports).start()
        # self._main_class.ax25_port_handler.reinit_all_ports()
        # self._main_class.msg_to_monitor('Info: PortsInitialisierung beendet.')
        self._main_class.sysMsg_to_monitor('Lob: Du bist stets bemüht..')

    def _ok_btn_cmd(self):
        # TODO Cleanup
        if not PORT_HANDLER.is_all_disco():
            PORT_HANDLER.disco_all_Conn()
            messagebox.showerror('Stationen nicht disconnected', 'Nicht alle Stationen disconnected!')
            self.settings_win.lift()
            return
        for port_id in self.tab_list.keys():
            self.tab_list[port_id].set_vars_to_cfg()
            self.tab_list[port_id].port_setting.save_to_pickl()
        PORT_HANDLER.set_kiss_param_all_ports()
        self._main_class.sysMsg_to_monitor('Lob: Das war richtig. Mach weiter so.')
        self._main_class.sysMsg_to_monitor('Hinweis: Du hast auf OK gedrückt ohne zu wissen was passiert !!')
        self._main_class.tabbed_sideFrame.update_mon_port_id()
        self._destroy_win()

    def get_win_height(self):
        return self._win_height

    def tasker(self):
        pass
        """
        for tab in self.tab_list:
            tab.win_tasker()
        """
