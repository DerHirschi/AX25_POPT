import tkinter as tk
from tkinter import ttk as ttk
from tkinter import scrolledtext
from config_station import DefaultStation, DefaultPortConfig
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
        self.smart_digi = tk.Checkbutton(self.tab, text='Managed-DIGI', width=12, variable=self.smart_digi_set_var)
        self.smart_digi.place(x=digi_x, y=height - digi_y)

        ###############################
        # Right Side ( Name, QTH, LOC )
        self.tab.rowconfigure(0, minsize=5, weight=0)
        self.tab.columnconfigure(0, minsize=550, weight=0)
        self.tab.columnconfigure(1, weight=1)
        f_height = 135
        r_side_frame = tk.Frame(self.tab, width=435, height=f_height)
        r_side_frame.configure(bg='grey80')
        r_side_frame.grid(column=1, row=1)
        #################
        # Name
        name_x = 10
        name_y = 120
        name_label = tk.Label(r_side_frame, text='Name:')
        name_label.place(x=name_x, y=f_height - name_y)
        self.name = tk.Entry(r_side_frame, width=15)
        self.name.place(x=name_x + 75, y=f_height - name_y)
        self.name.insert(tk.END, str(self.station_setting.stat_parm_Name))
        #################
        # QTH
        qth_x = 10
        qth_y = 90
        qth_label = tk.Label(r_side_frame, text='QTH:')
        qth_label.place(x=qth_x, y=f_height - qth_y)
        self.qth = tk.Entry(r_side_frame, width=30)
        self.qth.place(x=qth_x + 75, y=f_height - qth_y)
        self.qth.insert(tk.END, str(self.station_setting.stat_parm_QTH))
        #################
        # LOC
        loc_x = 10
        loc_y = 60
        loc_label = tk.Label(r_side_frame, text='LOC:')
        loc_label.place(x=loc_x, y=f_height - loc_y)
        self.loc = tk.Entry(r_side_frame, width=6)
        self.loc.place(x=loc_x + 75, y=f_height - loc_y)
        self.loc.insert(tk.END, str(self.station_setting.stat_parm_LOC))

        ############################
        # Tabs for C-Text and so on
        # Root Tab
        digi_x = 20
        digi_y = 460
        # Root Tab
        textTab = ttk.Notebook(self.tab, height=height - 330, width=width - (digi_x * 4))
        textTab.place(x=digi_x, y=height - digi_y)
        # C-Text
        tab_ctext = ttk.Frame(textTab)
        tab_ctext.rowconfigure(0, minsize=2, weight=0)
        tab_ctext.rowconfigure(1, minsize=100, weight=1)
        tab_ctext.rowconfigure(2, minsize=2, weight=0)
        tab_ctext.columnconfigure(0, minsize=2, weight=0)
        tab_ctext.columnconfigure(1, minsize=900, weight=1)
        tab_ctext.columnconfigure(2, minsize=2, weight=0)
        # self.c_text_ent = tk.Text(tab_ctext, bg='white', font=("Courier", 12))
        self.c_text_ent = tk.Text(tab_ctext, font=("Courier", 12))
        self.c_text_ent.configure(width=80, height=11)
        # self.c_text_ent.place(x=5, y=15)
        self.c_text_ent.grid(row=1, column=1)
        self.c_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_ctext)
        # Bye Text
        tab_byetext = ttk.Frame(textTab)
        tab_byetext.rowconfigure(0, minsize=2, weight=0)
        tab_byetext.rowconfigure(1, minsize=100, weight=1)
        tab_byetext.rowconfigure(2, minsize=2, weight=0)
        tab_byetext.columnconfigure(0, minsize=2, weight=0)
        tab_byetext.columnconfigure(1, minsize=900, weight=1)
        tab_byetext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self.bye_text_ent = tk.Text(tab_byetext, font=("Courier", 12))
        self.bye_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self.bye_text_ent.grid(row=1, column=1)
        self.bye_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_bye_text)
        # Info Text
        tab_infotext = ttk.Frame(textTab)
        tab_infotext.rowconfigure(0, minsize=2, weight=0)
        tab_infotext.rowconfigure(1, minsize=100, weight=1)
        tab_infotext.rowconfigure(2, minsize=2, weight=0)
        tab_infotext.columnconfigure(0, minsize=2, weight=0)
        tab_infotext.columnconfigure(1, minsize=900, weight=1)
        tab_infotext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self.info_text_ent = tk.scrolledtext.ScrolledText(tab_infotext, font=("Courier", 12))
        self.info_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self.info_text_ent.grid(row=1, column=1)
        self.info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_itext)
        # Info Text
        tab_loinfotext = ttk.Frame(textTab)
        tab_loinfotext.rowconfigure(0, minsize=2, weight=0)
        tab_loinfotext.rowconfigure(1, minsize=100, weight=1)
        tab_loinfotext.rowconfigure(2, minsize=2, weight=0)
        tab_loinfotext.columnconfigure(0, minsize=2, weight=0)
        tab_loinfotext.columnconfigure(1, minsize=900, weight=1)
        tab_loinfotext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self.long_info_text_ent = tk.scrolledtext.ScrolledText(tab_loinfotext, font=("Courier", 12))
        self.long_info_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self.long_info_text_ent.grid(row=1, column=1)
        self.long_info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_longitext)
        # Status Text
        tab_akttext = ttk.Frame(textTab)
        tab_akttext.rowconfigure(0, minsize=2, weight=0)
        tab_akttext.rowconfigure(1, minsize=100, weight=1)
        tab_akttext.rowconfigure(2, minsize=2, weight=0)
        tab_akttext.columnconfigure(0, minsize=2, weight=0)
        tab_akttext.columnconfigure(1, minsize=900, weight=1)
        tab_akttext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self.akt_info_text_ent = tk.scrolledtext.ScrolledText(tab_akttext, font=("Courier", 12))
        self.akt_info_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self.akt_info_text_ent.grid(row=1, column=1)
        self.akt_info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_akttext)

        textTab.add(tab_ctext, text='C Text')
        textTab.add(tab_byetext, text='Quit Text')
        textTab.add(tab_infotext, text='Info Text')
        textTab.add(tab_loinfotext, text='Long-Info Text')
        textTab.add(tab_akttext, text='News Text')

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
        # Info Text
        self.info_text_ent.delete('1.0', tk.END)
        self.info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_itext)
        # Long Info Text
        self.long_info_text_ent.delete('1.0', tk.END)
        self.long_info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_longitext)
        # News Text
        self.akt_info_text_ent.delete('1.0', tk.END)
        self.akt_info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_akttext)
        # Name
        self.name.delete(0, tk.END)
        self.name.insert(tk.END, self.station_setting.stat_parm_Name)
        # QTH
        self.qth.delete(0, tk.END)
        self.qth.insert(tk.END, self.station_setting.stat_parm_QTH)
        # LOC
        self.loc.delete(0, tk.END)
        self.loc.insert(tk.END, self.station_setting.stat_parm_LOC)

    def set_vars_to_cfg(self):
        # CALL
        call = self.call.get()
        self.station_setting.stat_parm_Call = call
        # CLI
        cli_key = self.cli_select_var.get()
        self.station_setting.stat_parm_cli = self.cli_opt[cli_key]
        # MaxPac
        var_maxpac = int(self.max_pac_select_var.get())
        self.station_setting.stat_parm_MaxFrame = var_maxpac
        # PacLen
        var_paclen = int(self.pac_len.get())    # TODO try: to/or/and Filter input
        self.station_setting.stat_parm_PacLen = var_paclen
        for k in self.ports_sett.keys():
            if call in self.ports_sett[k].parm_StationCalls:
                self.ports_sett[k].parm_stat_PacLen[call] = var_paclen
                self.ports_sett[k].parm_stat_MaxFrame[call] = var_maxpac

        # DIGI
        self.station_setting.stat_parm_is_StupidDigi = bool(self.digi_set_var.get())
        # Smart DIGI
        self.station_setting.stat_parm_isSmartDigi = bool(self.smart_digi_set_var.get())
        # C-Text
        self.station_setting.stat_parm_cli_ctext = self.c_text_ent.get('1.0', tk.END)
        # Bye Text
        self.station_setting.stat_parm_cli_bye_text = self.bye_text_ent.get('1.0', tk.END)
        # Info Text
        self.station_setting.stat_parm_cli_itext = self.info_text_ent.get('1.0', tk.END)
        # Long Info Text
        self.station_setting.stat_parm_cli_longitext = self.long_info_text_ent.get('1.0', tk.END)
        # News Text
        self.station_setting.stat_parm_cli_akttext = self.akt_info_text_ent.get('1.0', tk.END)
        # Name
        self.station_setting.stat_parm_Name = self.name.get()
        # QTH
        self.station_setting.stat_parm_QTH = self.qth.get()
        # LOC   TODO: Filter
        self.station_setting.stat_parm_LOC = self.loc.get()

        # Ports
        for k in self.ports_sett.keys():
            var = self.port_set_var[k][0].get()
            if var:
                self.ports_sett[k].parm_Stations.append(self.station_setting)


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
        self.settings_win.title("Station-Einstellungen")
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
        new_st_bt = tk.Button(self.settings_win,
                              text="Neue Station",
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
        for k in self.all_port_settings.keys():
            self.all_port_settings[k].parm_Stations = []
        for el in self.tab_list:
            el.set_vars_to_cfg()

    def save_cfg_to_file(self):
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

    def save_btn_cmd(self):
        self.set_all_vars_to_cfg()
        self.save_cfg_to_file()

    def ok_btn_cmd(self):
        self.set_all_vars_to_cfg()
        self.destroy_win()

    def destroy_win(self):
        self.settings_win.destroy()
        self.main_class.settings_win = None

