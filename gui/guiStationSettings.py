from tkinter import ttk as ttk
from tkinter import filedialog as fd
from tkinter import scrolledtext
from tkinter.colorchooser import askcolor
from config_station import DefaultStation, DefaultPort, save_station_to_file, del_user_data
from cli.cli import *
from ax25.ax25UI_Pipe import AX25Pipe
from gui.guiMsgBoxes import *
from string_tab import STR_TABLE


class StatSetTab:
    def __init__(self, main_stt_win, setting: DefaultStation, tabclt: ttk.Notebook):
        self.tab_clt = tabclt
        self.ports_sett: {int: DefaultPort} = main_stt_win.ax25_porthandler.ax25_port_settings
        height = main_stt_win.win_height
        width = main_stt_win.win_width
        self.main_cl = main_stt_win
        self.station_setting = setting
        self.style = main_stt_win.style
        self.own_tab = ttk.Frame(self.tab_clt)
        self.lang = main_stt_win.lang
        #################
        # Call
        call_x = 20
        call_y = 570
        call_label = tk.Label(self.own_tab, text=f'{STR_TABLE["call"][self.lang]}:')
        call_label.place(x=call_x, y=height - call_y)
        self.call = tk.Entry(self.own_tab, width=10)
        self.call.place(x=call_x + 55, y=height - call_y)
        self.call.insert(tk.END, self.station_setting.stat_parm_Call)
        #################
        # CLI
        cli_x = 280
        cli_y = 570
        cli_label = tk.Label(self.own_tab, text='CLI:')
        cli_label.place(x=cli_x, y=height - cli_y)
        self.cli_select_var = tk.StringVar(self.own_tab)
        self.cli_opt = {
            UserCLI.cli_name: UserCLI,
            NodeCLI.cli_name: NodeCLI,
            NoneCLI.cli_name: NoneCLI,
            'PIPE': AX25Pipe
        }
        opt = list(self.cli_opt.keys())

        cli = tk.OptionMenu(self.own_tab, self.cli_select_var, *opt, command=self.chk_CLI)
        cli.configure(width=8, height=1)
        cli.place(x=cli_x + 55, y=height - cli_y - 5)

        #################
        # MaxPac
        max_pac_x = 20
        max_pac_y = 500
        max_pac_label = tk.Label(self.own_tab, text='Max-Pac:')
        max_pac_label.place(x=max_pac_x, y=height - max_pac_y)
        self.max_pac_select_var = tk.StringVar(self.own_tab)
        opt = range(1, 8)
        self.max_pac_select_var.set(str(self.station_setting.stat_parm_MaxFrame))  # default value
        self.max_pac = tk.OptionMenu(self.own_tab, self.max_pac_select_var, *opt)
        self.max_pac.configure(width=4, height=1)
        self.max_pac.place(x=max_pac_x + 78, y=height - max_pac_y - 5)

        #################
        # PacLen
        pac_len_x = 180
        pac_len_y = 500
        pac_len_label = tk.Label(self.own_tab, text='Pac-Len:')
        pac_len_label.place(x=pac_len_x, y=height - pac_len_y)
        self.pac_len = tk.Entry(self.own_tab, width=3)
        self.pac_len.place(x=pac_len_x + 75, y=height - pac_len_y)
        self.pac_len.insert(tk.END, str(self.station_setting.stat_parm_PacLen))

        #################
        # DIGI
        digi_x = 305
        digi_y = 500
        self.digi_set_var = tk.BooleanVar()
        self.digi = tk.Checkbutton(self.own_tab,
                                   text='DIGI',
                                   width=4,
                                   variable=self.digi_set_var,
                                   )
        self.digi.place(x=digi_x, y=height - digi_y)
        self.digi_set_var.set(self.station_setting.stat_parm_is_StupidDigi)
        ##################
        # Smart DIGI TODO
        digi_x = 390
        digi_y = 500
        self.smart_digi_set_var = tk.IntVar()
        self.smart_digi = tk.Checkbutton(self.own_tab,
                                         text='Managed-DIGI',
                                         width=12,
                                         variable=self.smart_digi_set_var,
                                         state='disabled'   # TODO
                                         )
        self.smart_digi.place(x=digi_x, y=height - digi_y)

        ###############################
        # Right Side ( Name, QTH, LOC )
        self.own_tab.rowconfigure(0, minsize=5, weight=0)
        self.own_tab.columnconfigure(0, minsize=550, weight=0)
        self.own_tab.columnconfigure(1, weight=1)
        f_height = 135
        r_side_frame = tk.Frame(self.own_tab, width=435, height=f_height)
        r_side_frame.configure(bg='grey80')
        r_side_frame.grid(column=1, row=1)
        #################
        # Name
        name_x = 10
        name_y = 120
        name_label = tk.Label(r_side_frame, text=f'{STR_TABLE["name"][self.lang]}:')
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
        self.textTab = ttk.Notebook(self.own_tab, height=height - 330, width=width - (digi_x * 4))
        self.textTab.place(x=digi_x, y=height - digi_y)
        # C-Text
        tab_ctext = ttk.Frame(self.textTab)
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
        tab_byetext = ttk.Frame(self.textTab)
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
        tab_infotext = ttk.Frame(self.textTab)
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
        tab_loinfotext = ttk.Frame(self.textTab)
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
        tab_akttext = ttk.Frame(self.textTab)
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

        # Pipe
        tab_pipe = ttk.Frame(self.textTab)
        # TX-File Check Timer
        _x = 10
        _y = 10

        tk.Label(tab_pipe, text='TX-File Check Timer (sek/sec):').place(x=_x, y=_y)
        self.loop_timer_var = tk.StringVar(tab_pipe)
        # self.loop_timer_var.set(self.pipe.parm_tx_file_check_timer)
        self.loop_timer = tk.Spinbox(tab_pipe,
                                     from_=5,
                                     to=360,
                                     increment=5,
                                     width=3,
                                     textvariable=self.loop_timer_var,
                                     # command=self.set_max_frame,
                                     # state='disabled'
                                     )
        self.loop_timer.place(x=_x + 270, y=_y)
        #################
        # TX FILE
        _x = 10
        _y = 60
        tk.Label(tab_pipe, text=f"{STR_TABLE['tx_file'][self.lang]}:").place(x=_x, y=_y)
        self.tx_filename_var = tk.StringVar(tab_pipe)
        # self.tx_filename_var.set(self.pipe.tx_filename)
        self.tx_filename = tk.Entry(tab_pipe, textvariable=self.tx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self.tx_filename.place(x=_x + 140, y=_y)
        tk.Button(tab_pipe,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  command=lambda: self.select_files(tx=True)
                  ).place(x=_x + 710, y=_y - 2)
        #################
        # RX FILE
        _x = 10
        _y = 100
        tk.Label(tab_pipe, text=f"{STR_TABLE['rx_file'][self.lang]}:").place(x=_x, y=_y)
        self.rx_filename_var = tk.StringVar(tab_pipe)
        # self.rx_filename_var.set(self.pipe.rx_filename)
        self.rx_filename = tk.Entry(tab_pipe, textvariable=self.rx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self.rx_filename.place(x=_x + 140, y=_y)
        tk.Button(tab_pipe,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  command=lambda: self.select_files(tx=False)
                  ).place(x=_x + 710, y=_y - 2)

        # Individual Colors for QSO Window
        tab_colors = ttk.Frame(self.textTab)
        bg = self.station_setting.stat_parm_qso_col_bg
        fg = self.station_setting.stat_parm_qso_col_text
        self.color_example_text = tk.Text(tab_colors,
                                          height=6,
                                          width=50,
                                          font=('Courier', 11),
                                          fg=fg,
                                          bg=bg)
        self.color_example_text.place(x=200, y=10)
        self.color_example_text.insert(tk.END, 'TEST TEXT Test. 1234. 73... ')
        # FG
        tk.Button(tab_colors,
                  text='Text',
                  command= lambda : self.choose_color(True)
                  ).place(x=20, y=20)

        # BG
        tk.Button(tab_colors,
                  text='BG',
                  command= lambda : self.choose_color(False)
                  ).place(x=20, y=120)

        self.textTab.add(tab_ctext, text=STR_TABLE['c_text'][self.lang])
        self.textTab.add(tab_byetext, text=STR_TABLE['q_text'][self.lang])
        self.textTab.add(tab_infotext, text=STR_TABLE['i_text'][self.lang])
        self.textTab.add(tab_loinfotext, text=STR_TABLE['li_text'][self.lang])
        self.textTab.add(tab_akttext, text=STR_TABLE['news_text'][self.lang])
        self.textTab.add(tab_pipe, text='Pipe')
        self.textTab.add(tab_colors, text=STR_TABLE['qso_win_color'][self.lang])

        self.update_vars_fm_cfg()

    def choose_color(self, fg_bg: bool):
        self.main_cl.settings_win.attributes("-topmost", False)
        if fg_bg:
            col = askcolor(self.station_setting.stat_parm_qso_col_text,
                           title=STR_TABLE['text_color'][self.lang])
            if col[1] is not None:
                # print(col)
                if col:
                    self.station_setting.stat_parm_qso_col_text = col[1]
                    self.color_example_text.configure(fg=col[1])
        else:
            col = askcolor(self.station_setting.stat_parm_qso_col_bg,
                           title=STR_TABLE['bg_color'][self.lang])
            if col[1] is not None:
                if col:
                    self.station_setting.stat_parm_qso_col_bg = col[1]
                    self.color_example_text.configure(bg=col[1])
        self.main_cl.settings_win.attributes("-topmost", True)

    def chk_CLI(self, event=None):
        if self.cli_select_var.get() != 'PIPE':
            self.loop_timer.configure(state='disabled')
            self.tx_filename.configure(state='disabled')
            self.rx_filename.configure(state='disabled')
            # self.cli_select_var.set(self.station_setting.stat_parm_cli.cli_name)
            self.c_text_ent.configure(state='normal')
            self.bye_text_ent.configure(state='normal')
            self.info_text_ent.configure(state='normal')
            self.long_info_text_ent.configure(state='normal')
            self.akt_info_text_ent.configure(state='normal')
            self.textTab.select(0)
        else:
            # self.cli_select_var.set('PIPE')  # default value
            self.c_text_ent.configure(state='disabled')
            self.bye_text_ent.configure(state='disabled')
            self.info_text_ent.configure(state='disabled')
            self.long_info_text_ent.configure(state='disabled')
            self.akt_info_text_ent.configure(state='disabled')

            self.loop_timer.configure(state='normal')
            self.tx_filename.configure(state='normal')
            self.rx_filename.configure(state='normal')

            #pipe = self.station_setting.stat_parm_pipe
            #self.tx_filename_var.set(pipe.tx_filename)
            #self.rx_filename_var.set(pipe.rx_filename)
            #self.loop_timer_var.set(str(pipe.parm_tx_file_check_timer))
            self.textTab.select(5)

    def select_files(self, tx=True):
        # self.main_cl.attributes("-topmost", False)
        # self.root.lower
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='data/',
            filetypes=filetypes)

        if filenames:
            if tx:
                self.tx_filename_var.set(filenames[0])
            else:
                self.rx_filename_var.set(filenames[0])

    def update_vars_fm_cfg(self):
        # CALL
        self.call.delete(0, tk.END)
        self.call.insert(tk.END, self.station_setting.stat_parm_Call)
        # CLI
        self.cli_select_var.set(self.station_setting.stat_parm_cli.cli_name)
        # Ports
        """
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
        """
        # MaxPac
        self.max_pac_select_var.set(str(self.station_setting.stat_parm_MaxFrame))  # default value
        self.max_pac.update()
        # PacLen
        self.pac_len.delete(0, tk.END)
        self.pac_len.insert(tk.END, str(self.station_setting.stat_parm_PacLen))
        # DIGI
        self.digi_set_var.set(self.station_setting.stat_parm_is_StupidDigi)
        # self.digi.select()
        # Smart DIGI
        # self.smart_digi_set_var.set(1)  # TODO
        # self.smart_digi.select()
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
        if self.station_setting.stat_parm_pipe is None:
            self.loop_timer.configure(state='disabled')
            self.tx_filename.configure(state='disabled')
            self.rx_filename.configure(state='disabled')
            self.cli_select_var.set(self.station_setting.stat_parm_cli.cli_name)
        else:
            self.cli_select_var.set('PIPE')  # default value
            self.c_text_ent.configure(state='disabled')
            self.bye_text_ent.configure(state='disabled')
            self.info_text_ent.configure(state='disabled')
            self.long_info_text_ent.configure(state='disabled')
            self.akt_info_text_ent.configure(state='disabled')

            pipe = self.station_setting.stat_parm_pipe
            self.tx_filename_var.set(pipe.tx_filename)
            self.rx_filename_var.set(pipe.rx_filename)
            self.loop_timer_var.set(str(pipe.parm_tx_file_check_timer))
            self.textTab.select(5)

    def set_vars_to_cfg(self):
        # CALL
        call = self.call.get().upper()
        self.call.delete(0, tk.END)
        self.call.insert(tk.END, call)
        self.station_setting.stat_parm_Call = call
        # CLI
        cli_key = self.cli_select_var.get()
        if cli_key not in ['PIPE']:
            self.station_setting.stat_parm_cli = self.cli_opt[cli_key]
        else:
            self.station_setting.stat_parm_cli = NoneCLI
            new_pipe = self.cli_opt[cli_key]
            new_pipe.tx_filename = self.tx_filename_var.get()
            new_pipe.rx_filename = self.rx_filename_var.get()
            new_pipe.parm_tx_file_check_timer = int(self.loop_timer_var.get())
            self.station_setting.stat_parm_pipe = self.cli_opt[cli_key]

        # MaxPac
        var_maxpac = int(self.max_pac_select_var.get())
        self.station_setting.stat_parm_MaxFrame = var_maxpac
        # PacLen
        var_paclen = int(self.pac_len.get())
        self.station_setting.stat_parm_PacLen = var_paclen

        for k in self.ports_sett.keys():
            """
            print(self.ports_sett[k])
            for att in dir(self.ports_sett[k]):
                print(att)
            """
            if call in self.ports_sett[k].parm_StationCalls:
                self.ports_sett[k].parm_stat_PacLen[call] = var_paclen
                self.ports_sett[k].parm_stat_MaxFrame[call] = var_maxpac

        # DIGI
        self.station_setting.stat_parm_is_StupidDigi = bool(self.digi_set_var.get())
        # Smart DIGI
        self.station_setting.stat_parm_isSmartDigi = bool(self.smart_digi_set_var.get())
        # C-Text
        self.station_setting.stat_parm_cli_ctext = self.c_text_ent.get('1.0', tk.END)[:-1]
        # Bye Text
        self.station_setting.stat_parm_cli_bye_text = self.bye_text_ent.get('1.0', tk.END)[:-1]
        # Info Text
        self.station_setting.stat_parm_cli_itext = self.info_text_ent.get('1.0', tk.END)[:-1]
        # Long Info Text
        self.station_setting.stat_parm_cli_longitext = self.long_info_text_ent.get('1.0', tk.END)[:-1]
        # News Text
        self.station_setting.stat_parm_cli_akttext = self.akt_info_text_ent.get('1.0', tk.END)[:-1]
        # Name
        self.station_setting.stat_parm_Name = self.name.get()
        # QTH
        self.station_setting.stat_parm_QTH = self.qth.get()
        # LOC   TODO: Filter
        self.station_setting.stat_parm_LOC = self.loc.get()


class StationSettingsWin:
    def __init__(self, main_cl):
        self.main_class = main_cl
        self.lang = self.main_class.language
        self.ax25_porthandler = main_cl.ax25_port_handler
        # self.all_port_settings: {int: PortConfigInit} = {}
        # self.all_ports: {int: AX25Port} = {}
        self.all_stat_settings: {str: DefaultStation} = main_cl.ax25_port_handler.ax25_stations_settings

        self.all_dev_types = list(main_cl.ax25_port_handler.ax25types.keys())

        self.win_height = 600
        self.win_width = 1059
        self.style = main_cl.style
        # self.settings_win = tk.Tk()
        self.settings_win = tk.Toplevel()
        # self.settings_win.option_add('*Dialog.msg.font', 'Helvetica 8')
        self.settings_win.title(STR_TABLE['stat_settings'][self.lang])
        self.settings_win.geometry("{}x{}".format(self.win_width, self.win_height))
        self.settings_win.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.main_class.main_win.winfo_x()}+"
                      f"{self.main_class.main_win.winfo_y()}")
        self.settings_win.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.settings_win.resizable(False, False)
        self.settings_win.attributes("-topmost", True)
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self.settings_win,
                          text=STR_TABLE['OK'][self.lang],
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)

        save_bt = tk.Button(self.settings_win,
                            text=STR_TABLE['save'][self.lang],
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)

        cancel_bt = tk.Button(self.settings_win,
                              text=STR_TABLE['cancel'][self.lang],
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
                              text=STR_TABLE['new_stat'][self.lang],
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=10,
                              command=self.new_stat_btn_cmd)
        del_st_bt = tk.Button(self.settings_win,
                              text=STR_TABLE['delete'][self.lang],
                              # font=("TkFixedFont", 15),
                              bg="red3",
                              height=1,
                              width=10,
                              command=self.del_station_btn)

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
        for k in self.all_stat_settings.keys():
            sett: DefaultStation = self.all_stat_settings[k]
            tab = StatSetTab(self, sett, self.tabControl)
            self.tab_list.append(tab)
            self.tabControl.add(tab.own_tab, text=k)

    def set_all_vars_to_cfg(self):
        """
        for k in self.all_port_settings.keys():
            self.all_port_settings[k].parm_Stations = []
        """
        dbl_calls = []
        for el in self.tab_list:
            call = el.call.get().upper()
            if call not in dbl_calls:
                el.set_vars_to_cfg()
                self.tabControl.tab(self.tab_list.index(el), text=call)
                dbl_calls.append(call)
            else:
                el.call.delete(0, tk.END)
                el.call.insert(tk.END, DefaultStation.stat_parm_Call)

        self.main_class.ax25_port_handler.update_digi_setting()

    def save_cfg_to_file(self):
        for conf in self.tab_list:
            stat_conf = conf.station_setting
            if stat_conf.stat_parm_Call != DefaultStation.stat_parm_Call:
                self.all_stat_settings[stat_conf.stat_parm_Call] = stat_conf
                save_station_to_file(stat_conf)
        self.main_class.msg_to_monitor(STR_TABLE['suc_save'][self.lang])

    def save_btn_cmd(self):
        self.set_all_vars_to_cfg()
        self.save_cfg_to_file()
        self.main_class.msg_to_monitor(STR_TABLE['lob1'][self.lang])

    def ok_btn_cmd(self):
        self.set_all_vars_to_cfg()
        self.save_cfg_to_file()
        self.main_class.msg_to_monitor(STR_TABLE['hin1'][self.lang])
        self.main_class.msg_to_monitor(STR_TABLE['lob2'][self.lang])

        self.destroy_win()

    def new_stat_btn_cmd(self):
        sett = DefaultStation()
        tab = StatSetTab(self, sett, self.tabControl)
        self.tabControl.add(tab.own_tab, text=sett.stat_parm_Call)
        self.tabControl.select(len(self.tab_list))
        self.tab_list.append(tab)
        # print(self.tabControl.index('current'))

    def destroy_win(self):
        self.settings_win.destroy()
        self.main_class.settings_win = None

    def tasker(self):
        pass

    def del_station_btn(self):
        self.settings_win.attributes("-topmost", False)
        msg = AskMsg(titel='lösche Station', message="Willst du diese Station wirklich löschen? \n"
                                                     "Alle Einstellungen sowie Texte gehen verloren !")
        # self.settings_win.lift()
        if msg:
            try:
                ind = self.tabControl.index('current')
            except tk.TclError:
                pass
            else:
                tab: StatSetTab = self.tab_list[ind]
                call = tab.call.get()
                del_user_data(call)
                del self.tab_list[ind]
                self.tabControl.forget(ind)

                WarningMsg('Station gelöscht', 'Laufwerk C: wurde erfolgreich formatiert.')
                self.main_class.msg_to_monitor('Hinweis: Station erfolgreich gelöscht.')
        else:
            InfoMsg('Abgebrochen', 'Das war eine gute Entscheidung. '
                                   'Mach weiter so. Das hast du gut gemacht.')
            self.main_class.msg_to_monitor('Hinweis: Knack!! Abgebrochen..')
        self.settings_win.lift()
        # self.settings_win.attributes("-topmost", True)
