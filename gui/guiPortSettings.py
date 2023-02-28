import tkinter as tk
from tkinter import ttk as ttk
from gui.vars import ALL_COLOURS
from config_station import DefaultStation, DefaultPortConfig, get_stat_cfg


class PortSetTab:
    def __init__(self, main_stt_win, setting: DefaultPortConfig, tabclt: ttk.Notebook):
        self.tab_clt = tabclt
        # self.ports_sett: {int: DefaultPortConfig} = main_stt_win.all_port_settings
        self.height = main_stt_win.win_height
        height = self.height
        self.width = main_stt_win.win_width
        width = self.width
        self.port_setting = setting
        self.port_handler = main_stt_win.ax25_handler
        port_types = list(self.port_handler.ax25types.keys())
        self.style = main_stt_win.style
        self.tab = ttk.Frame(self.tab_clt)
        #################
        # Port Name
        name_x = 20
        name_y = 570
        name_label = tk.Label(self.tab, text='Port Bezeichnung für MH und Monitor( Max: 4 ):')
        name_label.place(x=name_x, y=height - name_y)
        self.prt_name = tk.Entry(self.tab, width=5)
        self.prt_name.place(x=name_x + 420, y=height - name_y)
        self.prt_name.insert(tk.END, self.port_setting.parm_PortName)
        #################
        # Port Typ
        port_x = 800
        port_y = 570
        port_label = tk.Label(self.tab, text='Typ:')
        port_label.place(x=port_x, y=height - port_y)
        self.port_select_var = tk.StringVar(self.tab)

        opt = port_types
        self.port_select_var.set(self.port_setting.parm_PortTyp)      # default value
        port_men = tk.OptionMenu(self.tab, self.port_select_var, *opt)
        port_men.configure(width=10, height=1)
        port_men.place(x=port_x + 55, y=height - port_y - 5)
        #######################
        # Port Parameter
        param_sel_x = 20
        param_sel_y = 535
        param_next_line = 0
        # param_label = tk.Label(self.tab, text='Port-Parameter:')
        # param_label.place(x=param_sel_x, y=height - param_sel_y)
        self.param1_label = tk.Label(self.tab)
        self.param1_ent = tk.Entry(self.tab)
        self.param2_label = tk.Label(self.tab)
        self.param2_ent = tk.Entry(self.tab)
        self.param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
        self.param1_ent.place(x=param_sel_x + 80, y=height - param_sel_y + param_next_line)
        self.param2_label.place(x=param_sel_x + 500, y=height - param_sel_y + param_next_line)
        self.param2_ent.place(x=param_sel_x + 500 + 50, y=height - param_sel_y + param_next_line)

        #########################
        # Pseudo TXD
        ptxd_x = 20
        ptxd_y = 500
        ptxd_label = tk.Label(self.tab, text='P-TXD:')
        self.ptxd = tk.Entry(self.tab, width=5)
        self.ptxd.insert(tk.END, self.port_setting.parm_TXD)
        ptxd_help = tk.Label(self.tab, text='Pseudo TX-Delay (Wartezeit zwischen TX und RX). '
                                            'Wird nicht als KISS Parameter am TNC gesetzt.')
        ptxd_label.place(x=ptxd_x, y=height - ptxd_y)
        self.ptxd.place(x=ptxd_x + 80, y=height - ptxd_y)
        ptxd_help.place(x=ptxd_x + 80 + 70, y=height - ptxd_y)

        # Baud
        calc_baud_x = 20
        calc_baud_y = 465
        calc_baud_label = tk.Label(self.tab, text='Baud:')
        self.calc_baud = tk.Entry(self.tab, width=8)
        if self.port_setting.parm_PortTyp == 'KISSSER':
            ins = self.port_setting.parm_PortParm[1]
            self.calc_baud.insert(tk.END, ins)
            self.calc_baud.configure(state="disabled")
        else:
            ins = self.port_setting.parm_baud
            self.calc_baud.insert(tk.END, ins)
            self.calc_baud.configure(state="normal")
        calc_baud_label.place(x=calc_baud_x, y=height - calc_baud_y)
        self.calc_baud.place(x=calc_baud_x + 80, y=height - calc_baud_y)
        # T1
        t1_x = 20
        t1_y = 430
        t1_label = tk.Label(self.tab, text='T1:')
        self.t1 = tk.Entry(self.tab, width=5)
        self.t1.insert(tk.END, self.port_setting.parm_T1)
        t1_label.place(x=t1_x, y=height - t1_y)
        self.t1.place(x=t1_x + 40, y=height - t1_y)
        # T2
        t2_x = 140
        t2_y = 430
        t2_label = tk.Label(self.tab, text='T2:')
        self.t2 = tk.Entry(self.tab, width=5)
        self.t2.insert(tk.END, self.port_setting.parm_T2)
        t2_label.place(x=t2_x, y=height - t2_y)
        self.t2.place(x=t2_x + 40, y=height - t2_y)
        # T3
        t3_x = 260
        t3_y = 430
        t3_label = tk.Label(self.tab, text='T3:')
        self.t3 = tk.Entry(self.tab, width=5)
        self.t3.insert(tk.END, self.port_setting.parm_T3)
        t3_label.place(x=t3_x, y=height - t3_y)
        self.t3.place(x=t3_x + 40, y=height - t3_y)
        # N2
        n2_x = 380
        n2_y = 430
        n2_label = tk.Label(self.tab, text='N2:')
        self.n2 = tk.Entry(self.tab, width=5)
        self.n2.insert(tk.END, self.port_setting.parm_N2)
        n2_label.place(x=n2_x, y=height - n2_y)
        self.n2.place(x=n2_x + 40, y=height - n2_y)

        #######################
        # LAbel
        stdp_x = 20
        stdp_y = 375
        std_pam_label = tk.Label(self.tab, text='Standard Parameter. Werden genutzt wenn nirgendwo anders '
                                                '(Station/Client) definiert.')
        std_pam_label.place(x=stdp_x, y=height - stdp_y)

        #########################
        # Port Default Packet Length
        pac_len_x = 20
        pac_len = 340
        pac_len_label = tk.Label(self.tab, text='Pac Len:')
        self.pac_len = tk.Entry(self.tab, width=5)
        self.pac_len.insert(tk.END, str(self.port_setting.parm_PacLen))
        pac_len_help = tk.Label(self.tab, text='Paket Länge. 1 - 256')
        pac_len_label.place(x=pac_len_x, y=height - pac_len)
        self.pac_len.place(x=pac_len_x + 80, y=height - pac_len)
        pac_len_help.place(x=pac_len_x + 80 + 70, y=height - pac_len)

        #########################
        # Port Default Max Pac
        max_pac_x = 20
        max_pac_y = 305
        max_pac_label = tk.Label(self.tab, text='Max Pac:')

        opt_max_pac = list(range(1, 8))
        self.max_pac_var = tk.StringVar(self.tab)
        self.max_pac_var.set(str(self.port_setting.parm_MaxFrame))  # default value
        max_pac = tk.OptionMenu(self.tab, self.max_pac_var, *opt_max_pac)
        max_pac.configure(width=4, height=1)
        max_pac_help = tk.Label(self.tab, text='Max Paket Anzahl. 1 - 7')
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
        mon_col_label = tk.Label(mon_col_frame, text='Monitor Farben', bg=bg_cl)
        mon_col_label.place(x=mon_col_la_x, y=mon_col_la_y)
        #################
        # TX
        tx_sel_x = 20
        tx_sel_y = 50
        tx_sel_label = tk.Label(mon_col_frame, text='TX:', bg=bg_cl)
        self.tx_col_select_var = tk.StringVar(self.tab)
        self.tx_col_select_var.set(self.port_setting.parm_mon_clr_tx)  # default value
        tx_sel = tk.ttk.Combobox(mon_col_frame, textvariable=self.tx_col_select_var, values=ALL_COLOURS)
        #tx_sel.configure(width=18, height=20, bg=bg_cl)
        tx_sel_label.place(x=tx_sel_x, y=tx_sel_y)
        tx_sel.place(x=tx_sel_x + 55, y=tx_sel_y)
        #################
        # RX
        rx_sel_x = 20
        rx_sel_y = 85
        rx_sel_label = tk.Label(mon_col_frame, text='RX:', bg=bg_cl)
        self.rx_col_select_var = tk.StringVar(self.tab)
        self.rx_col_select_var.set(self.port_setting.parm_mon_clr_rx)  # default value
        rx_sel = tk.ttk.Combobox(mon_col_frame, textvariable=self.rx_col_select_var, values=ALL_COLOURS)
        # tx_sel.configure(width=18, height=20, bg=bg_cl)
        rx_sel_label.place(x=rx_sel_x, y=rx_sel_y)
        rx_sel.place(x=rx_sel_x + 55, y=rx_sel_y)

        #####################################
        #################
        # Station CFGs
        self.stat_check_vars = {}
        self.all_stat_cfgs = get_stat_cfg()
        x_f = 0
        y_f = 1

        for k in self.all_stat_cfgs.keys():
            stat = self.all_stat_cfgs[k]
            cfg_x = 20 + x_f
            cfg_y = 290 - (35 * y_f)    # Yeah X * 0
            cfg_set_var = tk.IntVar()
            cfg = tk.Checkbutton(self.tab, text=k, width=10, variable=cfg_set_var, anchor='w')
            if k in self.port_setting.parm_StationCalls:
                cfg_set_var.set(1)
                cfg.select()
            cfg.place(x=cfg_x, y=height - cfg_y)
            if y_f == 3:
                y_f = 1
                x_f += 150
            else:
                y_f += 1

            self.stat_check_vars[k] = cfg_set_var

        self.update_port_parameter()

    def win_tasker(self):
        # TODO: Add to Mainloop (ROOT Frame/Win)
        self.update_port_parameter()

    def update_port_parameter(self):
        # TODO trigger from loop to update when new port typ is set
        height = self.height
        param_sel_x = 20
        param_sel_y = 535
        param_next_line = 0
        typ = self.port_select_var.get()
        if typ == 'KISSTCP':
            self.calc_baud.configure(state="normal")
            self.calc_baud.delete(0, tk.END)
            self.calc_baud.insert(tk.END, self.port_setting.parm_baud)
            self.param1_label.configure(text='Adresse:')
            self.param1_ent.configure(width=28)
            self.param2_label.configure(text='Port:')
            self.param2_ent.configure(width=7)
            self.param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
            self.param1_ent.place(x=param_sel_x + 80, y=height - param_sel_y + param_next_line)
            self.param2_label.place(x=param_sel_x + 500, y=height - param_sel_y + param_next_line)
            self.param2_ent.place(x=param_sel_x + 500 + 50, y=height - param_sel_y + param_next_line)
            self.param1_ent.delete(0, tk.END)
            self.param2_ent.delete(0, tk.END)
            if self.port_setting.parm_PortParm[0]:
                self.param1_ent.insert(tk.END, self.port_setting.parm_PortParm[0])
            if self.port_setting.parm_PortParm[1]:
                self.param2_ent.insert(tk.END, self.port_setting.parm_PortParm[1])
        elif typ == 'AXIP':
            self.calc_baud.configure(state="normal")
            self.calc_baud.delete(0, tk.END)
            self.calc_baud.insert(tk.END, self.port_setting.parm_baud)
            self.param1_label.configure(text='Adresse:')
            self.param1_ent.configure(width=28)
            self.param2_label.configure(text='Port:')
            self.param2_ent.configure(width=7)
            self.param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
            self.param1_ent.place(x=param_sel_x + 80, y=height - param_sel_y + param_next_line)
            self.param2_label.place(x=param_sel_x + 500, y=height - param_sel_y + param_next_line)
            self.param2_ent.place(x=param_sel_x + 500 + 50, y=height - param_sel_y + param_next_line)

            self.param1_ent.delete(0, tk.END)
            self.param2_ent.delete(0, tk.END)
            if self.port_setting.parm_PortParm[0]:
                self.param1_ent.insert(tk.END, self.port_setting.parm_PortParm[0])
            else:
                self.param1_ent.insert(tk.END, '0.0.0.0')
            if self.port_setting.parm_PortParm[1]:
                self.param2_ent.insert(tk.END, self.port_setting.parm_PortParm[1])

        elif typ == 'KISSSER':
            self.calc_baud.configure(state="normal")
            self.calc_baud.delete(0, tk.END)
            self.calc_baud.insert(tk.END, str(self.port_setting.parm_PortParm[1]))
            self.calc_baud.configure(state="disabled")

            self.param1_label.configure(text='Port:')
            self.param1_ent.configure(width=15)
            self.param2_label.configure(text='Baud:')
            self.param2_ent.configure(width=7)
            self.param1_label.place(x=param_sel_x, y=height - param_sel_y + param_next_line)
            self.param1_ent.place(x=param_sel_x + 50, y=height - param_sel_y + param_next_line)
            self.param2_label.place(x=param_sel_x + 250, y=height - param_sel_y + param_next_line)
            self.param2_ent.place(x=param_sel_x + 250 + 60, y=height - param_sel_y + param_next_line)

            self.param1_ent.delete(0, tk.END)
            self.param2_ent.delete(0, tk.END)
            if self.port_setting.parm_PortParm[0]:
                self.param1_ent.insert(tk.END, self.port_setting.parm_PortParm[0])
            if self.port_setting.parm_PortParm[1]:
                self.param2_ent.insert(tk.END, self.port_setting.parm_PortParm[1])

    def set_vars_to_cfg(self):
        # Port TYpe
        self.port_setting.parm_PortTyp = self.port_select_var.get()
        # Port Parameter
        tmp_param = (self.param1_ent.get(), int(self.param2_ent.get()))
        self.port_setting.parm_PortParm = tmp_param
        # Pseudo TXD
        self.port_setting.parm_TXD = int(self.ptxd.get())
        # Baud
        self.port_setting.parm_baud = int(self.calc_baud.get())
        # T 1
        self.port_setting.parm_T1 = int(self.t1.get())
        # T 2
        self.port_setting.parm_T2 = int(self.t2.get())
        # T 3
        self.port_setting.parm_T3 = int(self.t3.get())
        # N 2
        self.port_setting.parm_N2 = int(self.n2.get())
        # Port Default Packet Length
        self.port_setting.parm_PacLen = int(self.pac_len.get())
        # Port Default Max Pac
        self.port_setting.parm_MaxFrame = int(self.max_pac_var.get())
        # Monitor COLOR Selector SIDE Frame
        # TX
        self.port_setting.parm_mon_clr_tx = self.tx_col_select_var.get()
        # RX
        self.port_setting.parm_mon_clr_rx = self.rx_col_select_var.get()


class PortSettingsWin:
    def __init__(self, main_cl):
        self.main_class = main_cl
        self.all_ax25_ports = main_cl.ax25_port_handler.ax25_ports
        self.ax25_handler = main_cl.ax25_port_handler
        self.win_height = 600
        self.win_width = 1059
        self.style = main_cl.style
        self.settings_win = tk.Tk()
        self.settings_win.title("Port-Einstellungen")
        self.settings_win.geometry("{}x{}".format(self.win_width, self.win_height))
        self.settings_win.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.settings_win.resizable(False, False)
        self.settings_win.attributes("-topmost", True)
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self.settings_win,
                          text="Ok",
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self.destroy_win)

        save_bt = tk.Button(self.settings_win,
                            text="Speichern",
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)

        cancel_bt = tk.Button(self.settings_win,
                              text="Abbrechen",
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)
        ####################################
        # New Station, Del Station Buttons
        new_port_bt = tk.Button(self.settings_win,
                                  text="Neuer Port",
                                  # font=("TkFixedFont", 15),
                                  # bg="green",
                                  height=1,
                                  width=10,
                                  command=self.destroy_win)
        del_st_bt = tk.Button(self.settings_win,
                              text="Löschen",
                              # font=("TkFixedFont", 15),
                              bg="red3",
                              height=1,
                              width=10,
                              command=self.destroy_win)
        new_port_bt.place(x=20, y=self.win_height - 590)
        del_st_bt.place(x=self.win_width - 141, y=self.win_height - 590)

        # Root Tab
        self.tabControl = ttk.Notebook(self.settings_win, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self.win_height - 550)
        # Tab Vars
        self.tab_list: [ttk.Frame] = []
        # Tab Frames ( Port Settings )
        for k in self.all_ax25_ports.keys():
            # port.port_cfg: DefaultPortConfig
            tmp: DefaultPortConfig = self.all_ax25_ports[k].port_cfg
            tab = PortSetTab(self, tmp, self.tabControl)
            self.tab_list.append(tab)
            port_lable_text = 'Port {}'.format(k)
            self.tabControl.add(tab.tab, text=port_lable_text)

    def destroy_win(self):
            self.settings_win.destroy()
            self.main_class.settings_win = None

    def save_btn_cmd(self):
        for port_set in self.tab_list:
            port_set.set_vars_to_cfg()


