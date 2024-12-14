from tkinter import ttk as ttk
from tkinter import filedialog as fd
from tkinter import scrolledtext
from tkinter.colorchooser import askcolor

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import CFG_data_path, CFG_usertxt_path
from cfg.default_config import getNew_pipe_cfg, getNew_station_cfg
from cli.cliMain import CLI_OPT
from fnc.ax25_fnc import validate_ax25Call
from fnc.file_fnc import get_str_fm_file, save_str_to_file
from gui.guiMsgBoxes import *
from cfg.string_tab import STR_TABLE


class StatSetTab:
    def __init__(self, new_setting, tabclt: ttk.Notebook):
        # self.ports_sett: {int: DefaultPort} = main_stt_win.ax25_porthandler.ax25_port_settings
        height = 600
        width = 1059
        # self._main_cl = main_stt_win
        # self.style = main_stt_win.style
        self.own_tab = ttk.Frame(tabclt)
        self._lang = POPT_CFG.get_guiCFG_language()

        self._new_station_setting = new_setting
        # self.station_setting = setting
        self._stat_call = self._new_station_setting.get('stat_parm_Call', 'NOCALL')
        self._gui = PORT_HANDLER.get_gui()
        #################
        # Call
        call_x = 20
        call_y = 570
        call_label = tk.Label(self.own_tab, text=f'{STR_TABLE["call"][self._lang]}:')
        call_label.place(x=call_x, y=height - call_y)
        self.call = tk.Entry(self.own_tab, width=10)
        self.call.place(x=call_x + 55, y=height - call_y)
        # self.call.insert(tk.END, self._stat_call)
        #################
        # CLI
        cli_x = 280
        cli_y = 570
        cli_label = tk.Label(self.own_tab, text='CLI:')
        cli_label.place(x=cli_x, y=height - cli_y)
        self._cli_select_var = tk.StringVar(self.own_tab)
        self._cli_opt = CLI_OPT
        opt = list(self._cli_opt.keys())

        cli = tk.OptionMenu(self.own_tab, self._cli_select_var, *opt, command=self.chk_CLI)
        cli.configure(width=8, height=1)
        cli.place(x=cli_x + 55, y=height - cli_y - 5)

        #################
        # MaxPac
        max_pac_x = 20
        max_pac_y = 500
        max_pac_label = tk.Label(self.own_tab, text='Max-Pac:')
        max_pac_label.place(x=max_pac_x, y=height - max_pac_y)
        self._max_pac_select_var = tk.StringVar(self.own_tab)
        opt = range(8)
        # self._max_pac_select_var.set(str(self.station_setting.stat_parm_MaxFrame))  # default value
        self._max_pac = tk.OptionMenu(self.own_tab, self._max_pac_select_var, *opt)
        self._max_pac.configure(width=4, height=1)
        self._max_pac.place(x=max_pac_x + 78, y=height - max_pac_y - 5)

        #################
        # PacLen
        pac_len_x = 180
        pac_len_y = 500
        pac_len_label = tk.Label(self.own_tab, text='Pac-Len:')
        pac_len_label.place(x=pac_len_x, y=height - pac_len_y)
        self._pac_len = tk.Entry(self.own_tab, width=3)
        self._pac_len.place(x=pac_len_x + 75, y=height - pac_len_y)
        # self._pac_len.insert(tk.END, str(self.station_setting.stat_parm_PacLen))

        #################
        # DIGI
        """
        digi_x = 305
        digi_y = 500
        self._digi_set_var = tk.BooleanVar()
        digi = tk.Checkbutton(self.own_tab,
                              text='DIGI',
                              width=4,
                              variable=self._digi_set_var,
                              )
        digi.place(x=digi_x, y=height - digi_y)
        """
        # self._digi_set_var.set(self.station_setting.stat_parm_is_Digi)
        ##################
        # Smart DIGI
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
        name_label = tk.Label(r_side_frame, text=f'{STR_TABLE["name"][self._lang]}:')
        name_label.place(x=name_x, y=f_height - name_y)
        self._name = tk.Entry(r_side_frame, width=15)
        self._name.place(x=name_x + 75, y=f_height - name_y)
        # self._name.insert(tk.END, str(self.station_setting.stat_parm_Name))
        #################
        # QTH
        qth_x = 10
        qth_y = 90
        qth_label = tk.Label(r_side_frame, text='QTH:')
        qth_label.place(x=qth_x, y=f_height - qth_y)
        self._qth = tk.Entry(r_side_frame, width=30)
        self._qth.place(x=qth_x + 75, y=f_height - qth_y)
        self._qth.insert(tk.END, str(self._gui.own_qth))
        #################
        # LOC
        loc_x = 10
        loc_y = 60
        loc_label = tk.Label(r_side_frame, text='LOC:')
        loc_label.place(x=loc_x, y=f_height - loc_y)
        self._loc = tk.Entry(r_side_frame, width=6)
        self._loc.place(x=loc_x + 75, y=f_height - loc_y)
        self._loc.insert(tk.END, str(self._gui.own_loc))


        ############################
        # Tabs for C-Text and so on
        # Root Tab
        digi_x = 20
        digi_y = 460
        # Root Tab
        self._textTab = ttk.Notebook(self.own_tab, height=height - 330, width=width - (digi_x * 4))
        self._textTab.place(x=digi_x, y=height - digi_y)
        # C-Text
        tab_ctext = ttk.Frame(self._textTab)
        tab_ctext.rowconfigure(0, minsize=2, weight=0)
        tab_ctext.rowconfigure(1, minsize=100, weight=1)
        tab_ctext.rowconfigure(2, minsize=2, weight=0)
        tab_ctext.columnconfigure(0, minsize=2, weight=0)
        tab_ctext.columnconfigure(1, minsize=900, weight=1)
        tab_ctext.columnconfigure(2, minsize=2, weight=0)

        c_text = self._load_fm_file(self._stat_call + '.ctx')
        b_text = self._load_fm_file(self._stat_call + '.btx')
        i_text = self._load_fm_file(self._stat_call + '.itx')
        li_text = self._load_fm_file(self._stat_call + '.litx')
        a_text = self._load_fm_file(self._stat_call + '.atx')
        if c_text is None:
            c_text = STR_TABLE['default_ctext'][self._lang]
        if b_text is None:
            b_text = ''
        if i_text is None:
            i_text = ''
        if li_text is None:
            li_text = ''
        if a_text is None:
            a_text = ''



        # self.c_text_ent = tk.Text(tab_ctext, bg='white', font=("Courier", 12))
        self._c_text_ent = tk.Text(tab_ctext, font=("Courier", 12))
        self._c_text_ent.configure(width=80, height=11)
        # self.c_text_ent.place(x=5, y=15)
        self._c_text_ent.grid(row=1, column=1)
        # self.c_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_ctext)
        self._c_text_ent.insert(tk.END, c_text)

        # Bye Text
        tab_byetext = ttk.Frame(self._textTab)
        tab_byetext.rowconfigure(0, minsize=2, weight=0)
        tab_byetext.rowconfigure(1, minsize=100, weight=1)
        tab_byetext.rowconfigure(2, minsize=2, weight=0)
        tab_byetext.columnconfigure(0, minsize=2, weight=0)
        tab_byetext.columnconfigure(1, minsize=900, weight=1)
        tab_byetext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self._bye_text_ent = tk.Text(tab_byetext, font=("Courier", 12))
        self._bye_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self._bye_text_ent.grid(row=1, column=1)
        # self.bye_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_bye_text)
        self._bye_text_ent.insert(tk.END, b_text)

        # Info Text
        tab_infotext = ttk.Frame(self._textTab)
        tab_infotext.rowconfigure(0, minsize=2, weight=0)
        tab_infotext.rowconfigure(1, minsize=100, weight=1)
        tab_infotext.rowconfigure(2, minsize=2, weight=0)
        tab_infotext.columnconfigure(0, minsize=2, weight=0)
        tab_infotext.columnconfigure(1, minsize=900, weight=1)
        tab_infotext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self._info_text_ent = tk.scrolledtext.ScrolledText(tab_infotext, font=("Courier", 12))
        self._info_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self._info_text_ent.grid(row=1, column=1)
        # self.info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_itext)
        self._info_text_ent.insert(tk.END, i_text)

        # Info Text
        tab_loinfotext = ttk.Frame(self._textTab)
        tab_loinfotext.rowconfigure(0, minsize=2, weight=0)
        tab_loinfotext.rowconfigure(1, minsize=100, weight=1)
        tab_loinfotext.rowconfigure(2, minsize=2, weight=0)
        tab_loinfotext.columnconfigure(0, minsize=2, weight=0)
        tab_loinfotext.columnconfigure(1, minsize=900, weight=1)
        tab_loinfotext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self._long_info_text_ent = tk.scrolledtext.ScrolledText(tab_loinfotext, font=("Courier", 12))
        self._long_info_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self._long_info_text_ent.grid(row=1, column=1)
        # self.long_info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_longitext)
        self._long_info_text_ent.insert(tk.END, li_text)

        # Status Text
        tab_akttext = ttk.Frame(self._textTab)
        tab_akttext.rowconfigure(0, minsize=2, weight=0)
        tab_akttext.rowconfigure(1, minsize=100, weight=1)
        tab_akttext.rowconfigure(2, minsize=2, weight=0)
        tab_akttext.columnconfigure(0, minsize=2, weight=0)
        tab_akttext.columnconfigure(1, minsize=900, weight=1)
        tab_akttext.columnconfigure(2, minsize=2, weight=0)
        # self.bye_text_ent = tk.Text(tab_byetext, bg='white', font=("Courier", 12))
        self._akt_info_text_ent = tk.scrolledtext.ScrolledText(tab_akttext, font=("Courier", 12))
        self._akt_info_text_ent.configure(width=80, height=11)
        # self.bye_text_ent.place(x=5, y=15)
        self._akt_info_text_ent.grid(row=1, column=1)
        # self.akt_info_text_ent.insert(tk.END, self.station_setting.stat_parm_cli_akttext)
        self._akt_info_text_ent.insert(tk.END, a_text)
        # ########################################################################################
        # ########################################################################################
        # Pipe
        tab_pipe = ttk.Frame(self._textTab)
        # TX-File Check Timer
        _x = 10
        _y = 10

        tk.Label(tab_pipe, text='TX-File Check Timer (sek/sec):').place(x=_x, y=_y)
        self._loop_timer_var = tk.StringVar(tab_pipe)
        # self.loop_timer_var.set(self.pipe.parm_tx_file_check_timer)
        self._loop_timer = tk.Spinbox(tab_pipe,
                                      from_=5,
                                      to=360,
                                      increment=5,
                                      width=3,
                                      textvariable=self._loop_timer_var,
                                      # command=self.set_max_frame,
                                      # state='disabled'
                                      )
        self._loop_timer.place(x=_x + 270, y=_y)
        #################
        # TX FILE
        _x = 10
        _y = 60
        tk.Label(tab_pipe, text=f"{STR_TABLE['tx_file'][self._lang]}:").place(x=_x, y=_y)
        self._tx_filename_var = tk.StringVar(tab_pipe)
        # self._tx_filename_var.set(self.pipe.tx_filename)
        self._tx_filename = tk.Entry(tab_pipe, textvariable=self._tx_filename_var, width=50)
        # self._tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self._tx_filename.place(x=_x + 140, y=_y)
        tk.Button(tab_pipe,
                  text=f"{STR_TABLE['file_1'][self._lang]}",
                  command=lambda: self.select_files(tx=True)
                  ).place(x=_x + 710, y=_y - 2)
        #################################
        # RX FILE
        _x = 10
        _y = 100
        tk.Label(tab_pipe, text=f"{STR_TABLE['rx_file'][self._lang]}:").place(x=_x, y=_y)
        self._rx_filename_var = tk.StringVar(tab_pipe)
        # self.rx_filename_var.set(self.pipe.rx_filename)
        self._rx_filename = tk.Entry(tab_pipe, textvariable=self._rx_filename_var, width=50)
        # self._tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self._rx_filename.place(x=_x + 140, y=_y)
        tk.Button(tab_pipe,
                  text=f"{STR_TABLE['file_1'][self._lang]}",
                  command=lambda: self.select_files(tx=False)
                  ).place(x=_x + 710, y=_y - 2)

        # Individual Colors for QSO Window
        tab_colors = ttk.Frame(self._textTab)

        self._color_example_text = tk.Text(tab_colors,
                                           height=5,
                                           width=50,
                                           font=('Courier', 11),)
        self._color_example_text.place(x=200, y=10)
        self._color_example_text.insert(tk.END, 'TEST TEXT Test. 1234. 73... ')
        # FG
        tk.Button(tab_colors,
                  text='TX-Text',
                  command=lambda: self._choose_color('tx_fg')
                  ).place(x=20, y=20)

        # BG
        tk.Button(tab_colors,
                  text='BG',
                  command=lambda: self._choose_color('tx_bg')
                  ).place(x=20, y=100)


        self._color_example_text_rx = tk.Text(tab_colors,
                                              height=5,
                                              width=50,
                                              font=('Courier', 11),)
        self._color_example_text_rx.place(x=200, y=130)
        self._color_example_text_rx.insert(tk.END, 'TEST TEXT Test. 1234. 73... ')
        # FG
        tk.Button(tab_colors,
                  text='RX-Text',
                  command=lambda: self._choose_color('rx_fg')
                  ).place(x=20, y=140)
        # stat_qso_col_tx = self._new_station_setting.get('stat_parm_qso_col_text_tx', 'white')
        # stat_qso_col_rx = self._new_station_setting.get('stat_parm_qso_col_text_rx', '#25db04')
        # stat_qso_col_bg = self._new_station_setting.get('stat_parm_qso_col_bg', 'black')
        self._qso_fg_tx = self._new_station_setting.get('stat_parm_qso_col_text_tx', 'white')
        self._qso_bg_tx = self._new_station_setting.get('stat_parm_qso_col_bg', 'black')
        self._qso_fg_rx = self._new_station_setting.get('stat_parm_qso_col_text_rx', '#25db04')

        self._textTab.add(tab_ctext, text=STR_TABLE['c_text'][self._lang])
        self._textTab.add(tab_byetext, text=STR_TABLE['q_text'][self._lang])
        self._textTab.add(tab_infotext, text=STR_TABLE['i_text'][self._lang])
        self._textTab.add(tab_loinfotext, text=STR_TABLE['li_text'][self._lang])
        self._textTab.add(tab_akttext, text=STR_TABLE['news_text'][self._lang])
        self._textTab.add(tab_pipe, text='Pipe')
        self._textTab.add(tab_colors, text=STR_TABLE['qso_win_color'][self._lang])

        self._update_vars_fm_cfg()

    def _load_fm_file(self, filename: str):
        file_n = CFG_data_path + \
                      CFG_usertxt_path + \
                      self._stat_call + '/' + \
                      filename
        """
        if out:
            return out
        return ''
        """
        return get_str_fm_file(file_n)

    def _save_to_file(self, filename: str, data: str):
        file_n = CFG_data_path + \
                      CFG_usertxt_path + \
                      self._stat_call + '/' + \
                      filename
        out = save_str_to_file(file_n, data)
        if out:
            return out
        return ''

    def _choose_color(self, fg_bg: str):
        # self._main_cl.settings_win.attributes("-topmost", False)
        # self._main_cl.settings_win.lower()
        if fg_bg == 'tx_fg':
            col = askcolor(self._qso_fg_tx,
                           title=STR_TABLE['text_color'][self._lang])
            # self._main_cl.settings_win.lift()
            if not col:
                # self._main_cl.settings_win.attributes("-topmost", True)
                return
            if col[1] is None:
                # self._main_cl.settings_win.attributes("-topmost", True)
                return
            self._qso_fg_tx = str(col[1])
            self._color_example_text.configure(fg=str(col[1]))
        elif fg_bg == 'tx_bg':
            col = askcolor(self._qso_bg_tx,
                           title=STR_TABLE['text_color'][self._lang])
            # self._main_cl.settings_win.lift()
            if not col:
                # self._main_cl.settings_win.attributes("-topmost", True)
                return
            if col[1] is None:
                # self._main_cl.settings_win.attributes("-topmost", True)
                return
            self._qso_bg_tx = str(col[1])
            self._color_example_text.configure(bg=str(col[1]))
            self._color_example_text_rx.configure(bg=str(col[1]))
        elif fg_bg == 'rx_fg':
            col = askcolor(self._qso_fg_rx,
                           title=STR_TABLE['text_color'][self._lang])
            # self._main_cl.settings_win.lift()
            if not col:
                # self._main_cl.settings_win.attributes("-topmost", True)
                return
            if col[1] is None:
                # self._main_cl.settings_win.attributes("-topmost", True)
                return
            self._qso_fg_rx = str(col[1])
            self._color_example_text_rx.configure(fg=str(col[1]))
        # self._main_cl.settings_win.lift()
        # self._main_cl.settings_win.attributes("-topmost", True)

    def chk_CLI(self, event=None):
        # print(self._cli_select_var.get())
        if self._cli_select_var.get() != 'PIPE':
            self._loop_timer.configure(state='disabled')
            self._tx_filename.configure(state='disabled')
            self._rx_filename.configure(state='disabled')
            # self.cli_select_var.set(self.station_setting.stat_parm_cli.cli_name)
            self._c_text_ent.configure(state='normal')
            self._bye_text_ent.configure(state='normal')
            self._info_text_ent.configure(state='normal')
            self._long_info_text_ent.configure(state='normal')
            self._akt_info_text_ent.configure(state='normal')
            self._textTab.select(0)
        else:
            # self.cli_select_var.set('PIPE')  # default value
            self._c_text_ent.configure(state='disabled')
            self._bye_text_ent.configure(state='disabled')
            self._info_text_ent.configure(state='disabled')
            self._long_info_text_ent.configure(state='disabled')
            self._akt_info_text_ent.configure(state='disabled')

            self._loop_timer.configure(state='normal')
            self._tx_filename.configure(state='normal')
            self._rx_filename.configure(state='normal')

            # pipe = self.station_setting.stat_parm_pipe
            # self._tx_filename_var.set(pipe.tx_filename)
            # self._rx_filename_var.set(pipe.rx_filename)
            # self.loop_timer_var.set(str(pipe.parm_tx_file_check_timer))
            self._textTab.select(5)

    def select_files(self, tx=True):
        # self.main_cl.attributes("-topmost", False)
        # self.root.lower
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )
        # self._main_cl.settings_win.lower()
        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='data/',
            filetypes=filetypes)
        # self._main_cl.settings_win.lift()
        if filenames:
            if tx:
                self._tx_filename_var.set(filenames[0])
            else:
                self._rx_filename_var.set(filenames[0])

    def _update_vars_fm_cfg(self):
        stat_call = self._new_station_setting.get('stat_parm_Call', '')
        stat_name = self._new_station_setting.get('stat_parm_Name', '')
        stat_is_digi = POPT_CFG.get_digi_is_enabled(stat_call)
        # stat_is_digi = self._new_station_setting.get('stat_parm_is_Digi', False)
        # stat_cli_cfg = self._new_station_setting.get('stat_parm_cli_cfg', getNew_CLI_cfg())   # TODO
        stat_cli_typ = self._new_station_setting.get('stat_parm_cli', 'NO-CLI')
        stat_paclen = self._new_station_setting.get('stat_parm_PacLen', 0)
        stat_maxframe = self._new_station_setting.get('stat_parm_MaxFrame', 0)
        stat_qso_col_tx = self._new_station_setting.get('stat_parm_qso_col_text_tx', 'white')
        stat_qso_col_rx = self._new_station_setting.get('stat_parm_qso_col_text_rx', '#25db04')
        stat_qso_col_bg = self._new_station_setting.get('stat_parm_qso_col_bg', 'black')

        self._qso_bg_tx = stat_qso_col_bg
        self._qso_fg_tx = stat_qso_col_tx
        self._qso_fg_rx = stat_qso_col_rx
        self._color_example_text.configure(bg=stat_qso_col_bg)
        self._color_example_text_rx.configure(bg=stat_qso_col_bg)

        self._color_example_text.configure(fg=stat_qso_col_tx)
        self._color_example_text_rx.configure(fg=stat_qso_col_rx)

        # CALL
        self.call.delete(0, tk.END)
        # self.call.insert(tk.END, self.station_setting.stat_parm_Call)
        self.call.insert(tk.END, stat_call)
        # CLI
        # self._cli_select_var.set(self.station_setting.stat_parm_cli_cfg.get('cli_typ', 'NO-CLI'))
        self._cli_select_var.set(stat_cli_typ)
        # Name
        self._name.delete(0, tk.END)
        # self._name.insert(tk.END, self.station_setting.stat_parm_Name)
        self._name.insert(tk.END, stat_name)
        # QTH TODO --- Global CFG
        self._qth.delete(0, tk.END)
        self._qth.insert(tk.END, str(self._gui.own_qth))
        # LOC TODO --- Global CFG
        self._loc.delete(0, tk.END)
        self._loc.insert(tk.END, str(self._gui.own_loc))
        # Ports

        # MaxPac
        # self._max_pac_select_var.set(str(self.station_setting.stat_parm_MaxFrame))  # default value
        self._max_pac_select_var.set(str(stat_maxframe))  # default value
        self._max_pac.update()
        # PacLen
        self._pac_len.delete(0, tk.END)
        # self._pac_len.insert(tk.END, str(self.station_setting.stat_parm_PacLen))
        self._pac_len.insert(tk.END, str(stat_paclen))
        # DIGI
        # self._digi_set_var.set(self.station_setting.stat_parm_is_Digi)

        # self._digi_set_var.set(stat_is_digi)
        # self.digi.select()
        c_text = self._load_fm_file(self._stat_call + '.ctx')
        b_text = self._load_fm_file(self._stat_call + '.btx')
        i_text = self._load_fm_file(self._stat_call + '.itx')
        li_text = self._load_fm_file(self._stat_call + '.litx')
        a_text = self._load_fm_file(self._stat_call + '.atx')
        if c_text is None:
            c_text = STR_TABLE['default_ctext'][self._lang]
        if b_text is None:
            b_text = STR_TABLE['default_btext'][self._lang]
        if i_text is None:
            i_text = ''
        if li_text is None:
            li_text = ''
        if a_text is None:
            a_text = ''

        # C-Text
        self._c_text_ent.delete('1.0', tk.END)
        self._c_text_ent.insert(tk.END, c_text)
        # Bye Text
        self._bye_text_ent.delete('1.0', tk.END)
        self._bye_text_ent.insert(tk.END, b_text)
        # Info Text
        self._info_text_ent.delete('1.0', tk.END)
        self._info_text_ent.insert(tk.END,i_text)
        # Long Info Text
        self._long_info_text_ent.delete('1.0', tk.END)
        self._long_info_text_ent.insert(tk.END, li_text)
        # News Text
        self._akt_info_text_ent.delete('1.0', tk.END)
        self._akt_info_text_ent.insert(tk.END, a_text)

        pipe_cfg = POPT_CFG.get_pipe_CFG_fm_UID(stat_call, -1)
        # get(self.station_setting.stat_parm_Call, {})

        if not pipe_cfg:
            self._loop_timer.configure(state='disabled')
            self._tx_filename.configure(state='disabled')
            self._rx_filename.configure(state='disabled')
            # self._cli_select_var.set(self.station_setting.stat_parm_cli_cfg.get('cli_typ', 'NO-CLI'))
            self._cli_select_var.set(stat_cli_typ)
        else:
            self._cli_select_var.set('PIPE')  # default value
            self._c_text_ent.configure(state='disabled')
            self._bye_text_ent.configure(state='disabled')
            self._info_text_ent.configure(state='disabled')
            self._long_info_text_ent.configure(state='disabled')
            self._akt_info_text_ent.configure(state='disabled')

            # pipe = pipe_cfg.get('stat_parm_pipe', None)
            # self._tx_filename_var.set(pipe.tx_filename)
            self._tx_filename_var.set(pipe_cfg.get('pipe_parm_pipe_tx', ''))
            # self._rx_filename_var.set(pipe.rx_filename)
            self._rx_filename_var.set(pipe_cfg.get('pipe_parm_pipe_rx', ''))
            # self._loop_timer_var.set(str(pipe.parm_tx_file_check_timer))
            self._loop_timer_var.set(str(pipe_cfg.get('pipe_parm_pipe_loop_timer', 10)))
            self._textTab.select(5)

    def set_vars_to_cfg(self):
        # CALL
        call = self.call.get().upper()

        self.call.delete(0, tk.END)
        self.call.insert(tk.END, call)
        old_call = str(self._new_station_setting.get('stat_parm_Call', ''))
        self._stat_call = str(call)
        # self.station_setting.stat_parm_Call = call

        var_maxpac = self._new_station_setting.get('stat_parm_MaxFrame', 0)
        var_paclen = self._new_station_setting.get('stat_parm_PacLen', 0)
        try:
            # MaxPac
            var_maxpac = int(self._max_pac_select_var.get())
            # PacLen
            var_paclen = int(self._pac_len.get())
        except ValueError:
            pass

        # self.station_setting.stat_parm_MaxFrame = var_maxpac
        # self.station_setting.stat_parm_PacLen = var_paclen

        # CLI
        cli_key = self._cli_select_var.get()
        if cli_key not in ['PIPE']:
            # self.station_setting.stat_parm_cli = self._cli_opt[cli_key]
            # self.station_setting.stat_parm_pipe = False
            POPT_CFG.del_pipe_CFG(f'{-1}-{old_call}')
            # self.station_setting.stat_parm_cli = cli_key
            # pass
        else:
            # self.station_setting.stat_parm_pipe = True
            # self.station_setting.stat_parm_cli = 'NO-CLI'
            POPT_CFG.del_pipe_CFG(f'{-1}-{old_call}')
            new_pipe_cfg = getNew_pipe_cfg()
            # new_pipe_cfg = self._cli_opt[cli_key]
            new_pipe_cfg['pipe_parm_own_call'] = call
            new_pipe_cfg['pipe_parm_pipe_tx'] = str(self._tx_filename_var.get())
            new_pipe_cfg['pipe_parm_pipe_rx'] = str(self._rx_filename_var.get())
            try:
                new_pipe_cfg['pipe_parm_pipe_loop_timer'] = int(self._loop_timer_var.get())
            except ValueError:
                new_pipe_cfg['pipe_parm_pipe_loop_timer'] = 10
            new_pipe_cfg['pipe_parm_PacLen'] = var_paclen
            new_pipe_cfg['pipe_parm_MaxFrame'] = var_maxpac
            new_pipe_cfg['pipe_parm_Proto'] = True
            new_pipe_cfg['pipe_parm_permanent'] = True
            new_pipe_cfg['pipe_parm_port'] = -1

            POPT_CFG.set_pipe_CFG(new_pipe_cfg)

        # self.station_setting.stat_parm_cli_cfg = dict(stat_parm_cli_cfg)
        self._save_to_file(self._stat_call + '.ctx', self._c_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.btx', self._bye_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.itx', self._info_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.litx', self._long_info_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.atx', self._akt_info_text_ent.get('1.0', tk.END)[:-1])
        # Name
        # self.station_setting.stat_parm_Name = self._name.get()
        #######################################################
        # TODO: To Global CFGs
        # QTH
        self._gui.own_qth = str(self._qth.get())
        # LOC   TODO: Filter
        self._gui.own_loc = str(self._loc.get())
        #######################################################
        # COLORS
        # self.station_setting.stat_parm_qso_col_text_tx = self._qso_fg_tx
        # self.station_setting.stat_parm_qso_col_bg = self._qso_bg_tx
        # self.station_setting.stat_parm_qso_col_text_rx = self._qso_fg_rx

        #######################################################
        #######################################################
        # New CFG
        self._new_station_setting['stat_parm_Call'] = str(call)
        self._new_station_setting['stat_parm_Name'] = str(self._name.get())
        # self._new_station_setting['stat_parm_is_Digi'] = bool(self._digi_set_var.get())
        self._new_station_setting['stat_parm_cli'] = str(cli_key)
        self._new_station_setting['stat_parm_PacLen'] = int(var_paclen)
        self._new_station_setting['stat_parm_MaxFrame'] = int(var_maxpac)
        self._new_station_setting['stat_parm_qso_col_text_tx'] = str(self._qso_fg_tx)
        self._new_station_setting['stat_parm_qso_col_text_rx'] = str(self._qso_fg_rx)
        self._new_station_setting['stat_parm_qso_col_bg'] = str(self._qso_bg_tx)

        # cli_cfg = self._new_station_setting.get('stat_parm_cli_cfg', getNew_CLI_cfg())
        """
        digi_cfg = POPT_CFG.get_digi_CFG_for_Call(call)
        digi_cfg.update(dict(
            digi_enabled=bool(self._digi_set_var.get()),
        ))
        POPT_CFG.set_digi_CFG_f_call(call, digi_cfg)
        """
        if old_call != call:
            POPT_CFG.del_stat_CFG_fm_call(old_call)

        POPT_CFG.set_digi_CFG_f_call(call, POPT_CFG.get_digi_CFG_for_Call(call))
        # self._new_station_setting['stat_parm_Digi_cfg'] = dict(digi_cfg)
        # stat_cli_cfg = self._new_station_setting.get('stat_parm_cli_cfg', getNew_CLI_cfg())   # TODO

    def get_new_stat_sett(self):
        return self._new_station_setting

class StationSettingsWin(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        # self._root_win = main_cl
        self._lang = POPT_CFG.get_guiCFG_language()
        self._old_cfg = self._get_config()
        self.win_height = 600
        self.win_width = 1059
        ####################################
        # New Station, Del Station Buttons
        new_st_bt = tk.Button(self,
                              text=STR_TABLE['new_stat'][self._lang],
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=10,
                              command=self._new_stat_btn_cmd)
        del_st_bt = tk.Button(self,
                              text=STR_TABLE['delete'][self._lang],
                              # font=("TkFixedFont", 15),
                              bg="red3",
                              height=1,
                              width=10,
                              command=self._del_station_btn)

        new_st_bt.place(x=20, y=self.win_height - 590)
        del_st_bt.place(x=self.win_width - 141, y=self.win_height - 590)
        ####################################
        # Tab

        # Root Tab
        self._tabControl = ttk.Notebook(self, height=self.win_height - 140, width=self.win_width - 40)
        self._tabControl.place(x=20, y=self.win_height - 550)
        # Tab Vars
        # self.tab_index = 0
        self._tab_list: [ttk.Frame] = []
        # Tab Frames ( Station Setting )
        new_stat_settings = POPT_CFG.get_stat_CFGs()
        for k, cfg in new_stat_settings.items():
            tab = StatSetTab(cfg, self._tabControl)
            self._tab_list.append(tab)
            self._tabControl.add(tab.own_tab, text=k)

    def _call_vali(self):
        for el in self._tab_list:
            call = el.call.get().upper()
            if not validate_ax25Call(call):
                #self.settings_win.lower()
                call_vali_warning()
                #self.settings_win.lift()
                el.call.select_range(0, 'end')
                return False
        return True

    def _set_all_vars_to_cfg(self):
        """
        for k in self.all_port_settings.keys():
            self.all_port_settings[k].parm_Stations = []
        """
        if not self._call_vali():
            return False
        dbl_calls = []
        for el in self._tab_list:
            call = el.call.get().upper()
            if call not in dbl_calls:
                el.set_vars_to_cfg()
                self._tabControl.tab(self._tab_list.index(el), text=call)
                dbl_calls.append(call)
            else:
                el.call.delete(0, tk.END)
                el.call.insert(tk.END, getNew_station_cfg().get('stat_parm_Call', 'NOCALL'))

        # PORT_HANDLER.update_digi_setting()

    def _save_cfg_to_file(self):
        for conf in self._tab_list:
            new_stat_conf = conf.get_new_stat_sett()
            if new_stat_conf.get('stat_parm_Call', '') != getNew_station_cfg().get('stat_parm_Call', ''):
                POPT_CFG.set_stat_CFG_fm_conf(new_stat_conf)

    def _new_stat_btn_cmd(self):
        # sett = DefaultStation()
        new_sett = getNew_station_cfg()
        tab = StatSetTab(new_sett, self._tabControl)
        self._tabControl.add(tab.own_tab, text=new_sett.get('stat_parm_Call', 'NOCALL'))
        self._tabControl.select(len(self._tab_list))
        self._tab_list.append(tab)
        # print(self._tabControl.index('current'))

    def _del_station_btn(self):
        #self.settings_win.attributes("-topmost", False)
        msg = AskMsg(titel=STR_TABLE['del_station_hint_1'][self._lang], message=STR_TABLE['del_station_hint_2'][self._lang])
        # self.settings_win.lift()
        if msg:
            try:
                ind = self._tabControl.index('current')
            except tk.TclError:
                pass
            else:
                tab: StatSetTab = self._tab_list[ind]
                call = tab.call.get()
                POPT_CFG.del_stat_CFG_fm_call(call=call)   # Del Pipe-CFG
                # del_user_data(call)
                del self._tab_list[ind]
                self._tabControl.forget(ind)

                WarningMsg(STR_TABLE['del_station_warning_1'][self._lang], STR_TABLE['del_station_warning_2'][self._lang])
                #self._root_win.sysMsg_to_monitor(STR_TABLE['del_station_hint'][self._lang])
        else:
            InfoMsg(STR_TABLE['aborted'][self._lang], STR_TABLE['lob3'][self._lang])
            #self._root_win.sysMsg_to_monitor(STR_TABLE['hin2'][self._lang])
        #self.settings_win.lift()
        # self.settings_win.attributes("-topmost", True)

    @staticmethod
    def _get_config():
        return dict(POPT_CFG.get_stat_CFGs())

    def save_config(self):
        self._set_all_vars_to_cfg()
        self._save_cfg_to_file()
        return self._old_cfg != self._get_config()

