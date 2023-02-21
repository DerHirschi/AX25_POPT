import tkinter as tk
from tkinter import ttk as ttk
from config_station import DefaultStation, DefaultPortConfig
from main import AX25Port
from cli.cli import *


class StatSetTab:
    def __init__(self, main_stt_win, setting: DefaultStation, tabclt:  ttk.Notebook):
        self.tab_clt = tabclt
        self.ports_sett: {int: DefaultPortConfig} = main_stt_win.all_port_settings
        height = main_stt_win.win_height
        width = main_stt_win.win_width
        self.station_setting = setting
        self.style = main_stt_win.style
        self.tab = ttk.Frame(self.tab_clt)
        #################
        # Call
        call_x = 20
        call_y = 570
        call_label = tk.Label(self.tab, text='Call:')
        call_label.place(x=call_x, y=height - call_y)
        self.call = tk.Entry(self.tab, width=10)
        self.call.place(x=call_x + 55, y=height - call_y)
        self.call.insert(tk.END, self.station_setting.stat_parm_Call)
        #################
        # CLI
        cli_x = 280
        cli_y = 570
        cli_label = tk.Label(self.tab, text='CLI:')
        cli_label.place(x=cli_x, y=height - cli_y)
        self.cli_select_var = tk.StringVar(self.tab)
        self.cli_opt = {
            UserCLI.cli_name: UserCLI,
            NodeCLI.cli_name: NodeCLI,
            NoneCLI.cli_name: NoneCLI,
        }
        opt = list(self.cli_opt.keys())
        self.cli_select_var.set(self.station_setting.stat_parm_cli.cli_name)      # default value
        cli = tk.OptionMenu(self.tab, self.cli_select_var, *opt)
        cli.configure(width=8, height=1)
        cli.place(x=cli_x + 55, y=height - cli_y - 5)

        #######################
        # Device Port Selector
        dev_sel_x = 1040
        dev_sel_y = 535
        dev_label = tk.Label(self.tab, text='Geräte-Port:')
        dev_label.place(x=20, y=height - dev_sel_y)
        self.port_set_var: {int: (tk.IntVar, tk.Checkbutton)} = {}

        for k in self.ports_sett.keys():
            self.ports_sett: {int: DefaultPortConfig}
            var = tk.IntVar()
            dev_check = tk.Checkbutton(self.tab, text=self.ports_sett[k].parm_PortName, variable=var)
            tmp_port = self.ports_sett[k]
            for el in tmp_port.parm_StationCalls:
                if el in self.station_setting.stat_parm_Call:
                    #  if station_setting.stat_parm_Call in ports[k].parm_StationCalls:
                    var.set(1)
                    dev_check.select()

            f = 72
            dev_check.place(x=width - (dev_sel_x - 35 - ((k + 1) * f)), y=height - dev_sel_y)
            self.port_set_var[k] = (var, dev_check)

        #################
        # MaxPac
        max_pac_x = 20
        max_pac_y = 500
        max_pac_label = tk.Label(self.tab, text='Max-Pac:')
        max_pac_label.place(x=max_pac_x, y=height - max_pac_y)
        self.max_pac_select_var = tk.StringVar(self.tab)
        opt = range(1, 8)
        self. max_pac_select_var.set(str(self.station_setting.stat_parm_MaxFrame))  # default value
        self.max_pac = tk.OptionMenu(self.tab, self.max_pac_select_var, *opt)
        self.max_pac.configure(width=4, height=1)
        self.max_pac.place(x=max_pac_x + 78, y=height - max_pac_y - 5)

        #################
        # PacLen
        pac_len_x = 180
        pac_len_y = 500
        pac_len_label = tk.Label(self.tab, text='Pac-Len:')
        pac_len_label.place(x=pac_len_x, y=height - pac_len_y)
        self.pac_len = tk.Entry(self.tab, width=3)
        self.pac_len.place(x=pac_len_x + 75, y=height - pac_len_y)
        self.pac_len.insert(tk.END, str(self.station_setting.stat_parm_PacLen))

        #################
        # DIGI TODO
        digi_x = 305
        digi_y = 500
        self.digi_set_var = tk.IntVar()
        self.digi = tk.Checkbutton(self.tab, text='DIGI', width=4, variable=self.digi_set_var)
        self.digi.place(x=digi_x, y=height - digi_y)

        ##################
        # Smart DIGI TODO
        digi_x = 390
        digi_y = 500
        self.smart_digi_set_var = tk.IntVar()
        self.smart_digi = tk.Checkbutton(self.tab, text='Managed-DIGI', width=10, variable=self.smart_digi_set_var)
        self.smart_digi.place(x=digi_x, y=height - digi_y)

        ###########################
        # Tabs for C-Text an so on
        # Root Tab
        digi_x = 20
        digi_y = 460
        # Root Tab
        textTab = ttk.Notebook(self.tab, height=height - 330, width=width - (digi_x * 4))
        textTab.place(x=digi_x, y=height - digi_y)
        # C-Text
        tab_ctext = ttk.Frame(textTab)
        self.c_text_ent = tk.Text(tab_ctext, bg='white', font=("Courier", 12))
        self.c_text_ent.configure(width=80, height=11)
        self.c_text_ent.place(x=5, y=15)
        self.c_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_ctext)
        # Bye Text
        tab_byetext = ttk.Frame(textTab)
        self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self.bye_text_ent.configure(width=80, height=11)
        self.bye_text_ent.place(x=5, y=15)
        self.bye_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_bye_text)

        textTab.add(tab_ctext, text='C Text')
        textTab.add(tab_byetext, text='Quit Text')

        self.update_vars_fm_cfg()

    def update_vars_fm_cfg(self):
        # CALL
        self.call.delete(0, tk.END)
        self.call.insert(tk.END, self.station_setting.stat_parm_Call)
        # CLI
        self.cli_select_var.set(self.station_setting.stat_parm_cli.cli_name)
        # Ports
        for k in self.ports_sett.keys():
            self.ports_sett: {int: DefaultPortConfig}
            var = self.port_set_var[k][0]
            var.set(0)
            dev_check = self.port_set_var[k][1]
            dev_check.deselect()
            dev_check.configure(text=self.ports_sett[k].parm_PortName)
            tmp_ports = self.ports_sett[k]
            for el in tmp_ports.parm_StationCalls:
                if el in self.station_setting.stat_parm_Call:
                    var.set(1)
                    dev_check.select()
        # MaxPac
        self.max_pac_select_var.set(str(self.station_setting.stat_parm_MaxFrame))  # default value
        self.max_pac.update()
        # PacLen
        self.pac_len.delete(0, tk.END)
        self.pac_len.insert(tk.END, str(self.station_setting.stat_parm_PacLen))
        # DIGI
        self.digi_set_var.set(1)        # TODO
        self.digi.select()
        # Smart DIGI
        self.smart_digi_set_var.set(1)  # TODO
        self.smart_digi.select()
        # C-Text
        self.c_text_ent.delete('1.0', tk.END)
        self.c_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_ctext)
        # Bye Text
        self.bye_text_ent.delete('1.0', tk.END)
        self.bye_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_bye_text)

    def set_vars_to_cfg(self):
        # CALL
        call = self.call.get()
        self.station_setting.stat_parm_Call = call
        # CLI
        cli_key = self.cli_select_var.get()
        self.station_setting.stat_parm_cli = self.cli_opt[cli_key]
        # MaxPac
        self.station_setting.stat_parm_MaxFrame = int(self.max_pac_select_var.get())
        # PacLen
        var_paclen = int(self.pac_len.get())    # TODO try: to/or/and Filter input
        self.station_setting.stat_parm_PacLen = var_paclen
        # DIGI
        self.station_setting.stat_parm_is_StupidDigi = bool(self.digi_set_var.get())
        # Smart DIGI
        self.station_setting.stat_parm_isSmartDigi = bool(self.smart_digi_set_var.get())
        # C-Text
        self.station_setting.stat_parm_cli_ctext = self.c_text_ent.get('1.0', tk.END)
        # Bye Text
        self.station_setting.stat_parm_cli_bye_text = self.bye_text_ent.get('1.0', tk.END)
        # Ports
        for k in self.ports_sett.keys():
            var = self.port_set_var[k][0].get()
            if var:
                self.ports_sett[k].parm_Stations.append(self.station_setting)

        # TODO ReInit / Save / Load / bla



class StationSettingsWin:
    def __init__(self, main_cl):
        self.main_class = main_cl
        self.all_ax25_ports = main_cl.ax25_port_handler.ax25_ports
        self.all_port_settings: {int: DefaultPortConfig} = {}
        # self.all_ports: {int: AX25Port} = {}
        self.all_stat_settings: [DefaultStation] = []
        for k in list(self.all_ax25_ports.keys()):
            self.all_port_settings[k] = self.all_ax25_ports[k].port_cfg
            # print(dir(self.all_port_settings[k]))
            for stat_sett in self.all_ax25_ports[k].port_cfg.parm_Stations:
                stat_sett: DefaultStation
                if stat_sett not in self.all_stat_settings:
                    self.all_stat_settings.append(stat_sett)
        self.all_dev_types = list(main_cl.ax25_port_handler.ax25types.keys())

        self.win_height = 600
        self.win_width = 1059
        self.style = main_cl.style
        self.settings_win = tk.Tk()
        self.settings_win.title("Einstellungen")
        self.settings_win.geometry("{}x{}".format(self.win_width, self.win_height))
        self.settings_win.protocol("WM_DELETE_WINDOW", self.destroy_new_conn_win)
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
                             command=self.destroy_new_conn_win)

        save_bt = tk.Button(self.settings_win,
                            text="Speichern",
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self.set_all_vars_to_cfg)

        cancel_bt = tk.Button(self.settings_win,
                              text="Abbrechen",
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self.destroy_new_conn_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)
        ####################################
        # New Station, Del Station Buttons
        new_st_bt = tk.Button(self.settings_win,
                              text="Neue Station",
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=10,
                              command=self.destroy_new_conn_win)
        del_st_bt = tk.Button(self.settings_win,
                              text="Löschen",
                              # font=("TkFixedFont", 15),
                              bg="red3",
                              height=1,
                              width=10,
                              command=self.destroy_new_conn_win)

        new_st_bt.place(x=20, y=self.win_height - 590)
        del_st_bt.place(x=self.win_width - 141, y=self.win_height - 590)
        ####################################
        # Tab

        # Root Tab
        self.tabControl = ttk.Notebook(self.settings_win, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self.win_height - 550)
        # Tab Vars
        # self.tab_index = 0
        self.tab_list: [ttk.Frame] = []
        # Tab Frames ( Station Setting )
        for sett in self.all_stat_settings:
            sett: DefaultStation
            tab = StatSetTab(self, sett, self.tabControl)
            self.tab_list.append(tab)
            self.tabControl.add(tab.tab, text=sett.stat_parm_Call)

        # self.tabControl.pack(expand=0, fill="both")

    def set_all_vars_to_cfg(self):
        """
        for k in self.all_port_settings.keys():
            all_att = dir(self.all_port_settings[k])
            for att in all_att:
                #print("sett {} - {}".format(att, self.all_port_settings[k].__dict__.get(att)))
                print("sett {} - {}".format(att, getattr(self.all_port_settings[k], att)))

        for k in self.all_ax25_ports.keys():
            all_att = dir(self.all_ax25_ports[k][0].port_cfg)
            for att in all_att:
               #  print("port {} - {}".format(att, self.all_ax25_ports[k][0].port_cfg.__dict__.get(att)))
                print("port {} - {}".format(att, getattr(self.all_ax25_ports[k][0].port_cfg, att)))
        """
        # Del new_parm_Stations from all ports
        for k in self.all_port_settings.keys():
            self.all_port_settings[k].parm_Stations = []
        for el in self.tab_list:
            el.set_vars_to_cfg()
        for k in self.all_port_settings.keys():
            self.all_port_settings[k].save_to_pickl()
        """    
        for k in self.all_port_settings.keys():
            old_cfg = self.all_port_settings[k]
        """
        """
        print("---------------------------------------------")
        for k in self.all_port_settings.keys():
            all_att = dir(self.all_port_settings[k])
            for att in all_att:
                print("sett {} - {}".format(att, self.all_port_settings[k].__dict__.get(att)))

        for k in self.all_ax25_ports.keys():
            all_att = dir(self.all_ax25_ports[k][0].port_cfg)
            for att in all_att:
                print("sett {} - {}".format(att, self.all_ax25_ports[k][0].port_cfg.__dict__.get(att)))
        """

    def destroy_new_conn_win(self):
        self.settings_win.destroy()
        self.main_class.settings_win = None

