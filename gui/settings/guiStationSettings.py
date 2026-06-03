import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from tkinter import scrolledtext
from tkinter.colorchooser import askcolor
# Automatische Port-Erkennung
import serial.tools.list_ports

from cfg.constant import CFG_data_path, CFG_usertxt_path, COLOR_MAP, CLI_TYP_PIPE, CLI_TYP_NO_CLI
from cfg.default_config import getNew_pipe_cfg, getNew_station_cfg
from cfg.popt_config import POPT_CFG
from cli import CLI_OPT
from fnc.ax25_fnc import validate_ax25Call
from fnc.file_fnc import get_str_fm_file, save_str_to_file
from fnc.str_fnc import zeilenumbruch_lines, zeilenumbruch, get_strTab
from gui.guiMsgBoxes import AskMsg, call_vali_warning


class StatSetTab:
    def __init__(self, new_setting, tabclt: ttk.Notebook, root):
        self._root_win     = root
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._get_colorMap = lambda: COLOR_MAP.get(root.style_name, ('black', '#d9d9d9'))
        self.own_tab       = ttk.Frame(tabclt)
        #########################################################################
        # Config
        self._new_station_setting = new_setting
        self._stat_call = self._new_station_setting.get('stat_parm_Call', 'NOCALL')

        c_text  = self._load_fm_file(self._stat_call + '.ctx')
        b_text  = self._load_fm_file(self._stat_call + '.btx')
        i_text  = self._load_fm_file(self._stat_call + '.itx')
        li_text = self._load_fm_file(self._stat_call + '.litx')
        a_text  = self._load_fm_file(self._stat_call + '.atx')

        if c_text is None:
            c_text = zeilenumbruch_lines(self._getTabStr('default_ctext'))
        if b_text is None:
            b_text = zeilenumbruch_lines(self._getTabStr('default_btext'))
        if i_text is None:
            i_text = ''
        if li_text is None:
            li_text = ''
        if a_text is None:
            a_text = ''

        stat_call       = self._new_station_setting.get('stat_parm_Call', '')
        stat_name       = self._new_station_setting.get('stat_parm_Name', '')
        stat_cli_typ    = self._new_station_setting.get('stat_parm_cli', CLI_TYP_NO_CLI)
        stat_paclen     = self._new_station_setting.get('stat_parm_PacLen', 0)
        stat_maxframe   = self._new_station_setting.get('stat_parm_MaxFrame', 0)
        # Pipe
        pipe_cfg        = POPT_CFG.get_pipe_CFG_fm_UID(stat_call, -1)
        #########################################################################
        # Vars
        self._qso_fg_tx = self._new_station_setting.get('stat_parm_qso_col_text_tx', 'white')
        self._qso_bg_tx = self._new_station_setting.get('stat_parm_qso_col_bg', 'black')
        self._qso_fg_rx = self._new_station_setting.get('stat_parm_qso_col_text_rx', '#25db04')
        #########################################################################
        # Gui-Vars
        self.call_var         = tk.StringVar(self.own_tab, value=stat_call)
        self._cli_select_var  = tk.StringVar(self.own_tab, value=stat_cli_typ)
        self._name_var        = tk.StringVar(self.own_tab, value=stat_name)
        self._max_pac_var     = tk.StringVar(self.own_tab, value=str(stat_maxframe))
        self._len_pac_var     = tk.StringVar(self.own_tab, value=str(stat_paclen))
        # Pipe
        self._backend_var       = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_parm_backend', 'file'))
        self._tx_filename_var   = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_parm_pipe_tx', ''))
        self._rx_filename_var   = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_parm_pipe_rx', ''))
        self._loop_timer_var    = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_parm_pipe_loop_timer', 10))
        self._max_pac_delay_var = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_parm_MaxPacDelay', 30))
        self._addr_var          = tk.StringVar(self.own_tab)
        self._send_init_var     = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_be_send_at_init', ''))
        self._flush_rx_var      = tk.BooleanVar(self.own_tab,value=pipe_cfg.get('pipe_be_flush_rx_at_init', False))
        self._pipe_ctext_var    = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_parm_c_text', ''))
        # self._pipe_encoding_var = tk.StringVar(self.own_tab, value=pipe_cfg.get('pipe_parm_txt_encoder', 'UTF-8'))
        self._serial_port_var   = tk.StringVar(self.own_tab, )
        self._baudrate_var      = tk.StringVar(self.own_tab, value="9600")
        addr = pipe_cfg.get('pipe_be_address', ('0.0.0.0', 8023))
        self._addr_var.set(f"{addr[0]}:{addr[1]}" if isinstance(addr, (tuple, list)) else str(addr))
        # Vorbelegung aus Config
        baud_rates = ['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600']
        if isinstance(addr, (tuple, list)) and len(addr) >= 2:
            if addr[0].startswith('/dev/') or addr[0].startswith('COM'):
                self._serial_port_var.set(addr[0])
                self._baudrate_var.set(str(addr[1]) if addr[1] in baud_rates else "115200")

        #########################################################################
        # Frames
        upper_frame = ttk.Frame(self.own_tab)
        tab_frame   = ttk.Frame(self.own_tab)
        upper_frame.pack(fill='x',    expand=False)
        tab_frame.pack(  fill='both', expand=True, padx=5, pady=5)
        # =======================================================================
        # Upper Frame
        u_frame = ttk.Frame(upper_frame)
        l_frame = ttk.Frame(upper_frame)
        u_frame.pack(padx=5, pady=10,fill='x')
        l_frame.pack(padx=5, pady=10,fill='x')
        # u_frame
        call_f = ttk.Frame(u_frame)
        cli_f  = ttk.Frame(u_frame)
        name_f = ttk.Frame(u_frame)
        call_f.pack(side='left', padx=10)
        cli_f.pack( side='left', padx=50)
        name_f.pack(side='left', padx=50)
        # l_frame
        maxPac_f = ttk.Frame(l_frame)
        lenPac_f = ttk.Frame(l_frame)
        maxPac_f.pack(side='left', padx=10)
        lenPac_f.pack(side='left', padx=30)
        #########################################################################
        # Call
        ttk.Label(call_f, text=f'{self._getTabStr("call")}:').pack(side='left', padx=5)
        self.call = ttk.Entry(call_f,
                              textvariable=self.call_var,
                              width=10)
        self.call.pack(side='left')
        # self.call.insert(tk.END, self._stat_call)
        #########################################################################
        # CLI
        ttk.Label(cli_f, text='Station-Typ:').pack(side='left', padx=5)
        opt = list(CLI_OPT.keys())
        opt = [self._cli_select_var.get()] + opt
        cli = ttk.OptionMenu(cli_f, self._cli_select_var, *opt, command=self.chk_CLI)
        cli.pack(side='left')
        #################
        # Name
        ttk.Label(name_f, text=f'{self._getTabStr("name")}:').pack(side='left', padx=5)
        self._name = ttk.Entry(
            name_f,
            textvariable=self._name_var,
            width=15)
        self._name.pack(side='left')
        #################
        # MaxPac
        ttk.Label(maxPac_f, text='Max-Pac:').pack(side='left', padx=5)
        self._max_pac = ttk.Spinbox(maxPac_f,
                                    textvariable=self._max_pac_var,
                                    from_=0,
                                    to=7,
                                    increment=1,
                                    width=2)
        self._max_pac.pack(side='left')
        #################
        # PacLen
        ttk.Label(lenPac_f, text='Pac-Len:').pack(side='left', padx=5)
        self._pac_len = ttk.Entry(lenPac_f,
                                  textvariable=self._len_pac_var,
                                  width=3)
        self._pac_len.pack(side='left')

        # ========================================================================================
        # ========================================================================================
        # Tabs for C-Text and so on
        # Root Tab
        self._textTab = ttk.Notebook(tab_frame)
        self._textTab.pack(fill='both', expand=True)
        # ########################################################################################
        # ========================================================================================
        # C-Text Tab
        tab_ctext = ttk.Frame(self._textTab)
        tab_ctext.pack(expand=True, fill='both')

        self._c_text_ent = tk.Text(tab_ctext, font=("Courier", 12))
        self._c_text_ent.configure(width=80)
        self._c_text_ent.pack(fill='y', padx=50, pady=40)
        self._c_text_ent.insert(tk.END, c_text)

        # ########################################################################################
        # ========================================================================================
        # Bye Text Tab
        tab_byetext = ttk.Frame(self._textTab)
        tab_byetext.pack(expand=True, fill='both')

        self._bye_text_ent = tk.Text(tab_byetext, font=("Courier", 12))
        self._bye_text_ent.configure(width=80)
        self._bye_text_ent.pack(fill='y', padx=50, pady=40)
        self._bye_text_ent.insert(tk.END, b_text)

        # ########################################################################################
        # ========================================================================================
        # Info Text Tab
        tab_infotext = ttk.Frame(self._textTab)
        tab_infotext.pack(expand=True, fill='both')

        self._info_text_ent = tk.scrolledtext.ScrolledText(tab_infotext, font=("Courier", 12))
        self._info_text_ent.configure(width=80)
        self._info_text_ent.pack(fill='y', padx=50, pady=20)
        self._info_text_ent.insert(tk.END, i_text)

        # ########################################################################################
        # ========================================================================================
        # Long Info Text Tab
        tab_loinfotext = ttk.Frame(self._textTab)
        tab_loinfotext.pack(expand=True, fill='both')

        self._long_info_text_ent = tk.scrolledtext.ScrolledText(tab_loinfotext, font=("Courier", 12))
        self._long_info_text_ent.configure(width=80)
        self._long_info_text_ent.pack(fill='y', padx=50, pady=20)
        self._long_info_text_ent.insert(tk.END, li_text)

        # ########################################################################################
        # ========================================================================================
        # Status Text Tab
        tab_akttext = ttk.Frame(self._textTab)
        tab_akttext.pack(expand=True, fill='both')

        self._akt_info_text_ent = tk.scrolledtext.ScrolledText(tab_akttext, font=("Courier", 12))
        self._akt_info_text_ent.configure(width=80)
        self._akt_info_text_ent.pack(fill='y', padx=50, pady=20)
        self._akt_info_text_ent.insert(tk.END, a_text)

        # ########################################################################################
        # ========================================================================================
        # Pipe Tab
        tab_pipe = ttk.Frame(self._textTab)

        # ===================================================================
        # 2. AX.25 Timing & Paketparameter
        # ===================================================================
        frm_pac = ttk.LabelFrame(tab_pipe, text=f" {self._getTabStr('packet_timing_param')} ")
        frm_pac.pack(fill="x", padx=10, pady=8)

        row = 0

        ttk.Label(frm_pac, text="Max Pac Delay (s):").grid(row=row, column=4, sticky="w", padx=20)
        ttk.Spinbox(frm_pac, values=[str(x * 10) for x in range(1, 37)], textvariable=self._max_pac_delay_var,
                    width=6).grid(row=row, column=5, padx=8)

        #row += 1
        ttk.Label(frm_pac, text="TX-File Check Timer (s):").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        ttk.Spinbox(frm_pac, from_=5, to=360, increment=5, textvariable=self._loop_timer_var, width=6).grid(row=row,
                                                                                                           column=1,
                                                                                                           padx=8)

        # ===================================================================
        # 3. Backend Auswahl
        # ===================================================================
        frm_backend = ttk.LabelFrame(tab_pipe, text=f" {self._getTabStr('backen_config')} ")
        frm_backend.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm_backend, text="Backend:").pack(side="left", padx=8, pady=6)
        cb = ttk.Combobox(frm_backend, textvariable=self._backend_var,
                          values=[
                              'file',
                              'tcp-server',
                              'tcp-client',
                              'serial'
                          ],
                          state="readonly", width=15)
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", lambda e: self._update_backend_fields())

        # ===================================================================
        # 4. File-Backend (immer sichtbar bei 'file')
        # ===================================================================
        self.frm_file = ttk.LabelFrame(tab_pipe, text=" File Backend ")
        self.frm_file.pack(fill="x", padx=10, pady=8)

        row = 0
        ttk.Label(self.frm_file, text=f"{self._getTabStr('tx_file')}:", width=12).grid(row=row, column=0, sticky="w",
                                                                                       padx=8, pady=4)
        ttk.Entry(self.frm_file, textvariable=self._tx_filename_var, width=60).grid(row=row, column=1, sticky="we",
                                                                                   padx=8)
        ttk.Button(self.frm_file, text="...", width=3, command=lambda: self._select_files(tx=True)).grid(row=row,
                                                                                                         column=2,
                                                                                                         padx=4)

        row += 1
        ttk.Label(self.frm_file, text=f"{self._getTabStr('rx_file')}:", width=12).grid(row=row, column=0, sticky="w",
                                                                                       padx=8, pady=4)
        ttk.Entry(self.frm_file, textvariable=self._rx_filename_var, width=60).grid(row=row, column=1, sticky="we",
                                                                                   padx=8)
        ttk.Button(self.frm_file, text="...", width=3, command=lambda: self._select_files(tx=False)).grid(row=row,
                                                                                                          column=2,
                                                                                                          padx=4)

        self.frm_file.columnconfigure(1, weight=1)

        # ===================================================================
        # 5. TCP / Serial gemeinsame Optionen (nur für tcp-server, tcp-client, serial)
        # ===================================================================
        self.frm_net = ttk.LabelFrame(tab_pipe, text=f" {self._getTabStr('net_ser_opt')} ")
        # wird später gepackt

        row = 0
        # --- Address / Port (nur für TCP) ---
        self.lbl_addr = ttk.Label(self.frm_net, text=f"{self._getTabStr('address')} / {self._getTabStr('port')}:")
        self.lbl_addr.grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.ent_addr = ttk.Entry(self.frm_net, textvariable=self._addr_var, width=30)
        self.ent_addr.grid(row=row, column=1, columnspan=2, sticky="we", padx=8)

        row += 1
        ttk.Label(self.frm_net, text="Send at Init:").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(self.frm_net, textvariable=self._send_init_var, width=50).grid(row=row, column=1, columnspan=2,
                                                                                sticky="we", padx=8)

        row += 1
        self.flush_cb = ttk.Checkbutton(self.frm_net, text="Flush RX at Connect", variable=self._flush_rx_var)
        self.flush_cb.grid(row=row, column=1, sticky="w", padx=8, pady=2)

        # self.reinit_var = tk.BooleanVar(value=self.pipe_cfg.get('pipe_be_reinit_conn', False))
        # self.reinit_cb = ttk.Checkbutton(self.frm_net, text="Auto-Reconnect (TCP-Client)", variable=self.reinit_var)
        # self.reinit_cb.grid(row=row, column=2, sticky="w", padx=40, pady=2)

        row += 1
        ttk.Label(self.frm_net, text="C-Text:").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(self.frm_net, textvariable=self._pipe_ctext_var, width=70).grid(row=row, column=1, columnspan=2,
                                                                            sticky="we", padx=8)
        """
        row += 1
        ttk.Label(self.frm_net, text="Encoding:").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        ttk.Combobox(self.frm_net, textvariable=self._pipe_encoding_var,
                     values=['UTF-8', 'CP437', 'ISO-8859-1', 'ASCII', 'latin1'], state="readonly", width=15).grid(
            row=row, column=1, sticky="w", padx=8)
        """
        self.frm_net.columnconfigure(1, weight=1)

        # ===================================================================
        # 6. Serial-spezifische Optionen (separat!)
        # ===================================================================
        self.frm_serial = ttk.LabelFrame(tab_pipe, text=f" {self._getTabStr('serial_interface')} ")

        row = 0
        ttk.Label(self.frm_serial, text="Serial Port:").grid(row=row, column=0, sticky="w", padx=8, pady=6)
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        if not available_ports:
            available_ports = ['/dev/ttyUSB0', '/dev/ttyACM0', 'COM3', 'COM4']
        self.cb_serial_port = ttk.Combobox(self.frm_serial, textvariable=self._serial_port_var, values=available_ports,
                                           width=20)
        self.cb_serial_port.grid(row=row, column=1, padx=8, pady=6)

        ttk.Label(self.frm_serial, text="Baudrate:").grid(row=row, column=2, sticky="w", padx=20)
        self.cb_baud = ttk.Combobox(self.frm_serial,
                                    textvariable=self._baudrate_var,
                                    values=baud_rates,
                                    width=12,
                                    state="readonly")
        self.cb_baud.grid(row=row, column=3, padx=8, pady=6)

        self.frm_serial.columnconfigure(1, weight=1)

        # ########################################################################################
        # ========================================================================================
        # Individual Colors for QSO Window Tab
        tab_colors = ttk.Frame(self._textTab)

        self._color_example_text = tk.Text(tab_colors,
                                           height=5,
                                           width=50,
                                           font=('Courier', 11),
                                           bg=str(self._qso_bg_tx),
                                           fg=str(self._qso_fg_tx)
                                           )
        self._color_example_text.place(x=200, y=10)
        self._color_example_text.insert(tk.END, 'TEST TEXT Test. 1234. 73... ')
        # FG
        ttk.Button(tab_colors,
                  text='TX-Text',
                  command=lambda: self._choose_color('tx_fg')
                  ).place(x=20, y=20)

        # BG
        ttk.Button(tab_colors,
                  text='BG',
                  command=lambda: self._choose_color('tx_bg')
                  ).place(x=20, y=100)


        self._color_example_text_rx = tk.Text(tab_colors,
                                              height=5,
                                              width=50,
                                              font=('Courier', 11),
                                              bg=str(self._qso_bg_tx),
                                              fg=str(self._qso_fg_rx)
                                              )
        self._color_example_text_rx.place(x=200, y=130)
        self._color_example_text_rx.insert(tk.END, 'TEST TEXT Test. 1234. 73... ')
        # FG
        ttk.Button(tab_colors,
                  text='RX-Text',
                  command=lambda: self._choose_color('rx_fg')
                  ).place(x=20, y=140)

        # ===========================================================================================
        #
        self._textTab.add(tab_ctext,        text=self._getTabStr('c_text'))
        self._textTab.add(tab_byetext,      text=self._getTabStr('q_text'))
        self._textTab.add(tab_infotext,     text=self._getTabStr('i_text'))
        self._textTab.add(tab_loinfotext,   text=self._getTabStr('li_text'))
        self._textTab.add(tab_akttext,      text=self._getTabStr('news_text'))
        self._textTab.add(tab_pipe,         text='Pipe')
        self._textTab.add(tab_colors,       text=self._getTabStr('qso_win_color'))

        self._c_text_ent.bind(          "<KeyRelease>", lambda e:self._chk_umbruch(self._c_text_ent))
        self._info_text_ent.bind(       "<KeyRelease>", lambda e:self._chk_umbruch(self._info_text_ent))
        self._long_info_text_ent.bind(  "<KeyRelease>", lambda e:self._chk_umbruch(self._long_info_text_ent))
        self._akt_info_text_ent.bind(   "<KeyRelease>", lambda e:self._chk_umbruch(self._akt_info_text_ent))
        self._bye_text_ent.bind(        "<KeyRelease>", lambda e:self._chk_umbruch(self._bye_text_ent))
        self._update_backend_fields()
        if pipe_cfg:
            self._textTab.select(5)

    @staticmethod
    def _chk_umbruch(tx_widget: tk.Text):
        ind2 = str(int(float(tx_widget.index(tk.INSERT)))) + '.0'
        old_text = tx_widget.get(ind2, tx_widget.index(tk.INSERT))
        text = zeilenumbruch(old_text)
        if old_text == text:
            return
        tx_widget.delete(ind2, tx_widget.index(tk.INSERT))
        tx_widget.insert(tk.INSERT, text)


    def _load_fm_file(self, filename: str):
        file_n = CFG_data_path + \
                      CFG_usertxt_path + \
                      self._stat_call + '/' + \
                      filename

        ret = get_str_fm_file(file_n)
        if ret is None:
            return ''
        return ret

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
        if fg_bg == 'tx_fg':
            col = askcolor(self._qso_fg_tx,
                           title=self._getTabStr('text_color'), parent=self._root_win)
            if not col:
                return
            if col[1] is None:
                return
            self._qso_fg_tx = str(col[1])
            self._color_example_text.configure(fg=str(col[1]))
        elif fg_bg == 'tx_bg':
            col = askcolor(self._qso_bg_tx,
                           title=self._getTabStr('text_color'), parent=self._root_win)
            if not col:
                return
            if col[1] is None:
                return
            self._qso_bg_tx = str(col[1])
            self._color_example_text.configure(bg=str(col[1]))
            self._color_example_text_rx.configure(bg=str(col[1]))
        elif fg_bg == 'rx_fg':
            col = askcolor(self._qso_fg_rx,
                           title=self._getTabStr('text_color'), parent=self._root_win)
            if not col:
                return
            if col[1] is None:
                return
            self._qso_fg_rx = str(col[1])
            self._color_example_text_rx.configure(fg=str(col[1]))

    def chk_CLI(self, event=None):
        # print(self._cli_select_var.get())
        if self._cli_select_var.get() != CLI_TYP_PIPE:
            #self._loop_timer.configure(state='disabled')
            #self._tx_filename.configure(state='disabled')
            #self._rx_filename.configure(state='disabled')
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

            #self._loop_timer.configure(state='normal')
            #self._tx_filename.configure(state='normal')
            #self._rx_filename.configure(state='normal')

            # self.loop_timer_var.set(str(pipe.parm_tx_file_check_timer))
            self._textTab.select(5)

    def _update_backend_fields(self):
        backend = self._backend_var.get()

        if backend == 'file':
            self.frm_file.pack(fill="x", padx=10, pady=8)
            self.frm_net.pack_forget()
            self.frm_serial.pack_forget()

        elif backend in ['tcp-server', 'tcp-client']:
            self.frm_file.pack_forget()
            self.frm_net.pack(fill="x", padx=10, pady=8)
            self.frm_serial.pack_forget()

            # Address-Feld anzeigen
            self.lbl_addr.grid()
            self.ent_addr.grid()

            # Auto-Reconnect nur bei TCP-Client
            if backend == 'tcp-client':
                # self.reinit_cb.grid()
                self.flush_cb.grid()
            else:
                # self.reinit_cb.grid_remove()
                self.flush_cb.grid_remove()

        elif backend == 'serial':
            self.frm_file.pack_forget()
            self.frm_net.pack(fill="x", padx=10, pady=8)
            self.frm_serial.pack(fill="x", padx=10, pady=8)

            # Address-Feld verstecken, Serial-Felder anzeigen
            self.lbl_addr.grid_remove()
            self.ent_addr.grid_remove()
            #self.reinit_cb.grid_remove()  # macht bei Serial keinen Sinn

        else:
            self.frm_file.pack_forget()
            self.frm_net.pack_forget()
            self.frm_serial.pack_forget()

    def _select_files(self, tx=True):
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )
        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='data/',
            filetypes=filetypes,
            parent=self._root_win)
        if filenames:
            if tx:
                self._tx_filename_var.set(filenames[0])
            else:
                self._rx_filename_var.set(filenames[0])

    def set_vars_to_cfg(self):
        # CALL
        call = self.call_var.get().upper()
        self.call_var.set(call)
        old_call = str(self._new_station_setting.get('stat_parm_Call', ''))
        self._stat_call = str(call)
        # self.station_setting.stat_parm_Call = call

        var_maxpac = self._new_station_setting.get('stat_parm_MaxFrame', 0)
        var_paclen = self._new_station_setting.get('stat_parm_PacLen', 0)
        try:
            # MaxPac
            var_maxpac = int(self._max_pac_var.get())
            # PacLen
            var_paclen = int(self._len_pac_var.get())
        except ValueError:
            pass

        # CLI
        cli_key = self._cli_select_var.get()
        if cli_key not in [CLI_TYP_PIPE]:
            POPT_CFG.del_pipe_CFG(f'{-1}-{old_call}')
        else:
            # PIPE
            POPT_CFG.del_pipe_CFG(f'{-1}-{old_call}')
            new_pipe_cfg = getNew_pipe_cfg()
            new_pipe_cfg['pipe_parm_own_call']  = call
            new_pipe_cfg['pipe_parm_pipe_tx']   = str(self._tx_filename_var.get())
            new_pipe_cfg['pipe_parm_pipe_rx']   = str(self._rx_filename_var.get())
            try:
                new_pipe_cfg['pipe_parm_pipe_loop_timer'] = int(self._loop_timer_var.get())
            except ValueError:
                new_pipe_cfg['pipe_parm_pipe_loop_timer'] = 10
            new_pipe_cfg['pipe_parm_PacLen']        = var_paclen
            new_pipe_cfg['pipe_parm_MaxFrame']      = var_maxpac
            new_pipe_cfg['pipe_parm_Proto']         = True
            new_pipe_cfg['pipe_parm_permanent']     = True
            new_pipe_cfg['pipe_parm_port']          = -1

            new_pipe_cfg['pipe_parm_MaxPacDelay']   = int(self._max_pac_delay_var.get())

            # Backend-spezifische Adresse korrekt speichern
            backend = self._backend_var.get()
            new_pipe_cfg['pipe_parm_backend'] = backend

            if backend in ['tcp-server', 'tcp-client']:
                addr_str = self._addr_var.get().strip()
                if ':' in addr_str:
                    ip, port = addr_str.split(':', 1)
                    port = int(port)
                else:
                    ip, port = addr_str, 8023
                new_pipe_cfg['pipe_be_address'] = (ip.strip(), port)

            elif backend == 'serial':
                port = self._serial_port_var.get().strip()
                try:
                    baud = int(self._baudrate_var.get())
                except Exception as _ex:
                    _ex = _ex
                    baud = 9600
                new_pipe_cfg['pipe_be_address'] = (port, baud)

            # Rest wie gehabt
            new_pipe_cfg['pipe_be_send_at_init']     = self._send_init_var.get()
            new_pipe_cfg['pipe_parm_c_text']         = self._pipe_ctext_var.get()
            new_pipe_cfg['pipe_be_flush_rx_at_init'] = bool(self._flush_rx_var.get())
            new_pipe_cfg['pipe_be_reinit_conn']      = False
            #new_pipe_cfg['pipe_parm_txt_encoder']    = self._pipe_encoding_var.get()

            POPT_CFG.set_pipe_CFG(new_pipe_cfg)

        #######################################################
        # self.station_setting.stat_parm_cli_cfg = dict(stat_parm_cli_cfg)
        self._save_to_file(self._stat_call + '.ctx', self._c_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.btx', self._bye_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.itx', self._info_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.litx', self._long_info_text_ent.get('1.0', tk.END)[:-1])
        self._save_to_file(self._stat_call + '.atx', self._akt_info_text_ent.get('1.0', tk.END)[:-1])

        #######################################################
        # New CFG
        self._new_station_setting['stat_parm_Call']             = str(call)
        self._new_station_setting['stat_parm_Name']             = str(self._name_var.get())
        # self._new_station_setting['stat_parm_is_Digi'] = bool(self._digi_set_var.get())
        self._new_station_setting['stat_parm_cli']              = str(cli_key)
        self._new_station_setting['stat_parm_PacLen']           = int(var_paclen)
        self._new_station_setting['stat_parm_MaxFrame']         = int(var_maxpac)
        self._new_station_setting['stat_parm_qso_col_text_tx']  = str(self._qso_fg_tx)
        self._new_station_setting['stat_parm_qso_col_text_rx']  = str(self._qso_fg_rx)
        self._new_station_setting['stat_parm_qso_col_bg']       = str(self._qso_bg_tx)


        if old_call != call:
            POPT_CFG.del_stat_CFG_fm_call(old_call)

        POPT_CFG.set_digi_CFG_f_call(call, POPT_CFG.get_digi_CFG_for_Call(call))

    def get_new_stat_sett(self):
        return self._new_station_setting

class StationSettingsWin(ttk.Frame):
    def __init__(self, tabctl, root_win=None):
        ttk.Frame.__init__(self, tabctl)
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._old_cfg   = self._get_config()
        self.style_name = root_win.style_name
        ####################################
        # Frames
        upper_frame = ttk.Frame(self)
        btn_frame   = ttk.Frame(self)
        btn_frame.pack(  fill='x',   expand=False, pady=10, padx=10)
        upper_frame.pack(fill='both', expand=True)
        ####################################
        # New Station, Del Station Buttons
        new_st_bt = ttk.Button(btn_frame,
                              text=self._getTabStr('new_stat'),
                              width=10,
                              command=self._new_stat_btn_cmd)
        del_st_bt = tk.Button(btn_frame,
                              text=self._getTabStr('delete'),
                              bg="red3",
                              width=10,
                              command=self._del_station_btn,
                              relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                              highlightthickness=0,
                              )

        new_st_bt.pack(side='left',  anchor='w')
        del_st_bt.pack(side='right', anchor='e')
        ####################################
        # Tab
        # Root Tab
        self._tabControl = ttk.Notebook(upper_frame)
        self._tabControl.pack(fill='both', expand=True)
        # Tab Vars
        # self.tab_index = 0
        self._tab_list = []
        # Tab Frames ( Station Setting )
        new_stat_settings = POPT_CFG.get_stat_CFGs()
        for k, cfg in new_stat_settings.items():
            tab = StatSetTab(cfg, self._tabControl, self)
            self._tab_list.append(tab)
            self._tabControl.add(tab.own_tab, text=k)

    def _call_vali(self):
        for el in self._tab_list:
            call = el.call_var.get().upper()
            if not validate_ax25Call(call):
                call_vali_warning(self)
                el.call.select_range(0, 'end')
                return False
        return True

    def _set_all_vars_to_cfg(self):
        if not self._call_vali():
            return
        dbl_calls = []
        for el in self._tab_list:
            call = el.call_var.get().upper()
            if call not in dbl_calls:
                el.set_vars_to_cfg()
                self._tabControl.tab(self._tab_list.index(el), text=call)
                dbl_calls.append(call)
            else:
                el.call_var.set(getNew_station_cfg().get('stat_parm_Call', 'NOCALL'))

    def _save_cfg_to_file(self):
        for conf in self._tab_list:
            new_stat_conf = conf.get_new_stat_sett()
            if new_stat_conf.get('stat_parm_Call', '') != getNew_station_cfg().get('stat_parm_Call', ''):
                POPT_CFG.set_stat_CFG_fm_conf(new_stat_conf)

    def _new_stat_btn_cmd(self):
        new_sett = getNew_station_cfg()
        tab = StatSetTab(new_sett, self._tabControl, self)
        self._tabControl.add(tab.own_tab, text=new_sett.get('stat_parm_Call', 'NOCALL'))
        self._tabControl.select(len(self._tab_list))
        self._tab_list.append(tab)

    def _del_station_btn(self):
        msg = AskMsg(titel=self._getTabStr('del_station_hint_1'), message=self._getTabStr('del_station_hint_2'), parent_win=self)
        if msg:
            try:
                ind = self._tabControl.index('current')
            except tk.TclError:
                pass
            else:
                tab: StatSetTab = self._tab_list[ind]
                call = tab.call_var.get()
                POPT_CFG.del_stat_CFG_fm_call(call=call)   # Del Pipe-CFG
                del self._tab_list[ind]
                self._tabControl.forget(ind)

                messagebox.showwarning(self._getTabStr('del_station_warning_1'), self._getTabStr('del_station_warning_2'), parent=self)
                #self._root_win.sysMsg_to_monitor(STR_TABLE['del_station_hint'][self._lang])
        else:
            messagebox.showinfo(self._getTabStr('aborted'), self._getTabStr('lob3'), parent=self)
            #self._root_win.sysMsg_to_monitor(STR_TABLE['hin2'][self._lang])

    @staticmethod
    def _get_config():
        return dict(POPT_CFG.get_stat_CFGs())

    def save_config(self):
        self._set_all_vars_to_cfg()
        self._save_cfg_to_file()
        return self._old_cfg != self._get_config()

