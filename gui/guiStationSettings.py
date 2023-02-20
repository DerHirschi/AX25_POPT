import tkinter as tk
from tkinter import ttk as ttk
from config_station import DefaultStation, DefaultPortConfig
from main import AX25Port
from cli.cli import *


class StatSetTab:
    def __init__(self, main_stt_win, setting: DefaultStation, tabclt:  ttk.Notebook):
        self.tab_clt = tabclt
        ports: {int: DefaultPortConfig} = main_stt_win.all_port_settings
        height = main_stt_win.win_height
        width = main_stt_win.win_width
        station_setting = setting
        self.style = main_stt_win.style
        self.tab = ttk.Frame(self.tab_clt)
        #################
        # Call
        call_x = 780
        call_y = 570
        call_label = tk.Label(self.tab, text='Call:')
        call_label.place(x=width - call_x, y=height - call_y)
        self.call = tk.Entry(self.tab, width=10)
        self.call.place(x=width - call_x + 55, y=height - call_y)
        self.call.insert(tk.END, station_setting.stat_parm_Call)
        #################
        # CLI
        cli_x = 520
        cli_y = 570
        cli_label = tk.Label(self.tab, text='CLI:')
        cli_label.place(x=width - cli_x, y=height - cli_y)
        self.cli_select_var = tk.StringVar(self.tab)
        self.cli_opt = {
            UserCLI.cli_name: UserCLI,
            NodeCLI.cli_name: NodeCLI,
            NoneCLI.cli_name: NoneCLI,
        }
        opt = list(self.cli_opt.keys())
        self.cli_select_var.set(station_setting.stat_parm_cli.cli_name)      # default value
        cli = tk.OptionMenu(self.tab, self.cli_select_var, *opt)
        cli.configure(width=8, height=1)
        cli.place(x=width - cli_x + 55, y=height - cli_y - 5)

        #######################
        # Device Port Selector
        dev_sel_x = 780
        dev_sel_y = 535
        dev_label = tk.Label(self.tab, text='Geräte-Port:')
        dev_label.place(x=width - dev_sel_x, y=height - dev_sel_y)
        self.port_set_var: {int: tk.IntVar} = {}

        for k in ports.keys():
            ports: {int: DefaultPortConfig}
            var = tk.IntVar()
            dev_check = tk.Checkbutton(self.tab, text=ports[k].parm_PortName, variable=var)
            print(ports[k])
            print(ports[k].parm_StationCalls)
            for el in ports[k].parm_StationCalls:
                if el in station_setting.stat_parm_Call:
                    #  if station_setting.stat_parm_Call in ports[k].parm_StationCalls:
                    var.set(1)
                    dev_check.select()

            f = 72
            dev_check.place(x=width - (dev_sel_x - 35 - ((k + 1) * f)), y=height - dev_sel_y)
            self.port_set_var[k] = var

            #################
            # MaxPac
            max_pac_x = 780
            max_pac_y = 500
            max_pac_label = tk.Label(self.tab, text='Max-Pac:')
            max_pac_label.place(x=width - max_pac_x, y=height - max_pac_y)
            self.max_pac_select_var = tk.StringVar(self.tab)
            opt = range(1, 8)
            self. max_pac_select_var.set(str(station_setting.stat_parm_MaxFrame))  # default value
            max_pac = tk.OptionMenu(self.tab, self.max_pac_select_var, *opt)
            max_pac.configure(width=4, height=1)
            max_pac.place(x=width - max_pac_x + 78, y=height - max_pac_y - 5)

            #################
            # PacLen
            pac_len_x = 600
            pac_len_y = 500
            pac_len_label = tk.Label(self.tab, text='Pac-Len:')
            pac_len_label.place(x=width - pac_len_x, y=height - pac_len_y)
            self.max_pac = tk.Entry(self.tab, width=5)
            self.max_pac.place(x=width - pac_len_x + 75, y=height - pac_len_y)
            self.max_pac.insert(tk.END, str(station_setting.stat_parm_PacLen))




class StationSettingsWin:
    def __init__(self, main):
        self.main_class = main
        self.all_ax25_ports = main.ax25_port_handler.ax25_ports
        self.all_port_settings: {int: DefaultPortConfig} = {}
        # self.all_ports: {int: AX25Port} = {}
        self.all_stat_settings: [DefaultStation] = []
        for k in list(self.all_ax25_ports.keys()):
            self.all_port_settings[k] = self.all_ax25_ports[k][1]
            for stat_sett in self.all_ax25_ports[k][1].parm_Stations:
                stat_sett: DefaultStation
                if stat_sett not in self.all_stat_settings:
                    self.all_stat_settings.append(stat_sett)
        self.all_dev_types = list(main.ax25_port_handler.ax25types.keys())

        self.win_height = 600
        self.win_width = 800
        self.style = main.style
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
                          command=self.destroy_new_conn_win)

        cancel_bt = tk.Button(self.settings_win,
                            text="Abbrechen",
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=8,
                            command=self.destroy_new_conn_win)
        ok_bt.place(x=self.win_width - 780, y=self.win_height - 50)
        save_bt.place(x=self.win_width - 690, y=self.win_height - 50)
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

        new_st_bt.place(x=self.win_width - 780, y=self.win_height - 590)
        del_st_bt.place(x=self.win_width - 141, y=self.win_height - 590)
        ####################################
        # Tab

        # Root Tab
        self.tabControl = ttk.Notebook(self.settings_win, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=self.win_width - 780, y=self.win_height - 550)
        # Tab Vars
        self.tab_index = 0
        self.tab_dict: {int: ttk.Frame} = {}
        # Tab Frames ( Station Setting )
        for sett in self.all_stat_settings:
            sett: DefaultStation
            tab = StatSetTab(self, sett, self.tabControl)

            self.tabControl.add(tab.tab, text=sett.stat_parm_Call)

        # self.tabControl.pack(expand=0, fill="both")

    def destroy_new_conn_win(self):
        self.settings_win.destroy()
        self.main_class.settings_win = None

