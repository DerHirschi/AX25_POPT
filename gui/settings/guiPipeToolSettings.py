""" Opt by Grok-AI """
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
# Automatische Port-Erkennung
import serial.tools.list_ports

from ax25.ax25dec_enc import PIDByte
from cfg.constant import COLOR_MAP
from cfg.default_config import getNew_pipe_cfg
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.ax25_fnc import build_ax25uid
from fnc.str_fnc import get_strTab


class PipeTab:
    def __init__(self, root_win, pipe=None, connection=None):
        self._root_win = root_win
        self.tab_clt = root_win.tabControl
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.style = root_win.style
        self._connection = connection
        self._port_handler = root_win.get_port_handler()
        self._get_colorMap = lambda: COLOR_MAP.get(self._root_win.style_name, ('black', '#d9d9d9'))

        # Konfiguration laden
        if pipe is None:
            self.pipe_cfg = getNew_pipe_cfg()
            if connection is None:
                self.pipe_cfg['pipe_parm_Proto'] = False
                self.pipe_cfg['pipe_parm_permanent'] = True
        else:
            self.pipe_cfg = pipe.get_cfg_fm_pipe()
            if pipe.get_pipe_connection():
                self._connection = pipe.get_pipe_connection()
        # del pipe

        # Haupt-Frame mit Scrollbar (für viele Optionen sinnvoll)
        self.own_tab = ttk.Frame(self.tab_clt)
        fg, bg = self._get_colorMap()
        canvas = tk.Canvas(self.own_tab,
                           background=bg,
                           relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                           highlightthickness=0,
                           )
        scrollbar = ttk.Scrollbar(self.own_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Alle Widgets kommen jetzt in scrollable_frame
        main = scrollable_frame

        # ===================================================================
        # 1. Verbindungsparameter
        # ===================================================================
        frm_conn = ttk.LabelFrame(main, text=f" {self._getTabStr('ax25_param')} ")
        frm_conn.pack(fill="x", padx=10, pady=8)

        row = 0
        ttk.Label(frm_conn, text=f"{self._getTabStr('to')}:", width=15).grid(row=row, column=0, sticky="w", padx=5,
                                                                             pady=4)
        self.to_add_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_address_str', ''))
        self._to_add_ent = ttk.Entry(frm_conn, textvariable=self.to_add_var, width=50)
        self._to_add_ent.grid(row=row, column=1, columnspan=3, sticky="we",
                                                                         padx=5, pady=4)

        row += 1
        self.cmd_var = tk.BooleanVar(value=self.pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[0])
        self._cmd_ent = ttk.Checkbutton(frm_conn, text="CMD/RPT", variable=self.cmd_var)
        self._cmd_ent.grid(row=row, column=1, sticky="w", padx=5)
        self.poll_var = tk.BooleanVar(value=self.pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[1])
        self._poll_ent = ttk.Checkbutton(frm_conn, text="Poll", variable=self.poll_var)
        self._poll_ent.grid(row=row, column=2, sticky="w", padx=20)

        row += 1
        ttk.Label(frm_conn, text="PID:", width=15).grid(row=row, column=0, sticky="w", padx=5, pady=4)
        self.pid_var = tk.StringVar()
        pid = PIDByte()
        pac_types = dict(pid.pac_types)
        vals = []
        for x in pac_types.keys():
            pid.pac_types[int(x)]()
            vals.append(f"{hex(int(x)).upper()[2:]}>{pid.flag}")
        self._pid_ent = ttk.Combobox(frm_conn, textvariable=self.pid_var, values=vals, width=35, state="readonly")
        self._pid_ent.grid(row=row, column=1, columnspan=2, sticky="w", padx=5, pady=4)
        self.pid_var.set(f"{hex(self.pipe_cfg.get('pipe_parm_pid', 0xf0)).upper()[2:]}>{pid.flag}")

        row += 1
        ttk.Label(frm_conn, text=f"{self._getTabStr('port')}:", width=15).grid(row=row, column=0, sticky="w", padx=5,
                                                                               pady=4)
        self.port_var = tk.StringVar(value=str(self.pipe_cfg.get('pipe_parm_port', -1)))
        ports = ['-1'] + [str(p) for p in self._port_handler.get_all_ports().keys()]
        self._port_ent = ttk.Combobox(frm_conn, textvariable=self.port_var, values=ports, width=6)
        self._port_ent.grid(row=row, column=1, sticky="w", padx=5, pady=4)
        self._port_ent.bind("<KeyRelease>", self._chk_port_id)
        self._port_ent.bind("<<ComboboxSelected>>", self._chk_port_id)

        ttk.Label(frm_conn, text="Own Call:", width=12).grid(row=row, column=2, sticky="e", padx=5)
        self.call_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_own_call', ''))
        self._call_ent = ttk.Combobox(frm_conn, textvariable=self.call_var, width=12)
        self._call_ent.grid(row=row, column=3, sticky="w", padx=5)
        self._chk_port_id()

        frm_conn.columnconfigure(1, weight=1)

        # ===================================================================
        # 2. AX.25 Timing & Paketparameter
        # ===================================================================
        frm_pac = ttk.LabelFrame(main, text=f" {self._getTabStr('packet_timing_param')} ")
        frm_pac.pack(fill="x", padx=10, pady=8)

        row = 0
        ttk.Label(frm_pac, text="Max Pac:").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.max_pac_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_MaxFrame', 3))
        ttk.Spinbox(frm_pac, from_=1, to=7, textvariable=self.max_pac_var, width=5).grid(row=row, column=1, padx=8)

        ttk.Label(frm_pac, text="Pac-len:").grid(row=row, column=2, sticky="w", padx=20)
        self.pac_len_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_PacLen', 128))
        ttk.Spinbox(frm_pac, from_=1, to=256, textvariable=self.pac_len_var, width=6).grid(row=row, column=3, padx=8)

        ttk.Label(frm_pac, text="Max Pac Delay (s):").grid(row=row, column=4, sticky="w", padx=20)
        self.max_pac_delay_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_MaxPacDelay', 30))
        ttk.Spinbox(frm_pac, values=[str(x * 10) for x in range(1, 37)], textvariable=self.max_pac_delay_var,
                    width=6).grid(row=row, column=5, padx=8)

        row += 1
        ttk.Label(frm_pac, text="TX-File Check Timer (sec):").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.loop_timer_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_pipe_loop_timer', 10))
        ttk.Spinbox(frm_pac, from_=5, to=360, increment=5, textvariable=self.loop_timer_var, width=6).grid(row=row,
                                                                                                           column=1,
                                                                                                           padx=8)

        # ===================================================================
        # 3. Backend Auswahl
        # ===================================================================
        frm_backend = ttk.LabelFrame(main, text=f" {self._getTabStr('backen_config')} ")
        frm_backend.pack(fill="x", padx=10, pady=8)

        ttk.Label(frm_backend, text="Backend:").pack(side="left", padx=8, pady=6)
        self.backend_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_backend', 'file'))
        cb = ttk.Combobox(frm_backend, textvariable=self.backend_var,
                          values=[
                              'file',
                              'tcp-server',
                              'tcp-client',
                              #'serial'
                          ],
                          state="readonly", width=15)
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", lambda e: self._update_backend_fields())

        # ===================================================================
        # 4. File-Backend (immer sichtbar bei 'file')
        # ===================================================================
        self.frm_file = ttk.LabelFrame(main, text=" File Backend ")
        self.frm_file.pack(fill="x", padx=10, pady=8)

        row = 0
        ttk.Label(self.frm_file, text=f"{self._getTabStr('tx_file')}:", width=12).grid(row=row, column=0, sticky="w",
                                                                                       padx=8, pady=4)
        self.tx_filename_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_pipe_tx', ''))
        ttk.Entry(self.frm_file, textvariable=self.tx_filename_var, width=60).grid(row=row, column=1, sticky="we",
                                                                                   padx=8)
        ttk.Button(self.frm_file, text="...", width=3, command=lambda: self._select_files(tx=True)).grid(row=row,
                                                                                                         column=2,
                                                                                                         padx=4)

        row += 1
        ttk.Label(self.frm_file, text=f"{self._getTabStr('rx_file')}:", width=12).grid(row=row, column=0, sticky="w",
                                                                                       padx=8, pady=4)
        self.rx_filename_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_pipe_rx', ''))
        ttk.Entry(self.frm_file, textvariable=self.rx_filename_var, width=60).grid(row=row, column=1, sticky="we",
                                                                                   padx=8)
        ttk.Button(self.frm_file, text="...", width=3, command=lambda: self._select_files(tx=False)).grid(row=row,
                                                                                                          column=2,
                                                                                                          padx=4)

        self.frm_file.columnconfigure(1, weight=1)

        # ===================================================================
        # 5. TCP / Serial gemeinsame Optionen (nur für tcp-server, tcp-client, serial)
        # ===================================================================
        self.frm_net = ttk.LabelFrame(main, text=f" {self._getTabStr('net_ser_opt')} ")
        # wird später gepackt

        row = 0
        # --- Address / Port (nur für TCP) ---
        self.lbl_addr = ttk.Label(self.frm_net, text=f"{self._getTabStr('address')} / {self._getTabStr('port')}:")
        self.lbl_addr.grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.addr_var = tk.StringVar()
        addr = self.pipe_cfg.get('pipe_be_address', ('0.0.0.0', 8023))
        self.addr_var.set(f"{addr[0]}:{addr[1]}" if isinstance(addr, (tuple, list)) else str(addr))
        self.ent_addr = ttk.Entry(self.frm_net, textvariable=self.addr_var, width=30)
        self.ent_addr.grid(row=row, column=1, columnspan=2, sticky="we", padx=8)

        row += 1
        ttk.Label(self.frm_net, text="Send at Init:").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.send_init_var = tk.StringVar(value=self.pipe_cfg.get('pipe_be_send_at_init', ''))
        ttk.Entry(self.frm_net, textvariable=self.send_init_var, width=50).grid(row=row, column=1, columnspan=2,
                                                                                sticky="we", padx=8)

        row += 1
        self.flush_rx_var = tk.BooleanVar(value=self.pipe_cfg.get('pipe_be_flush_rx_at_init', False))
        self.flush_cb = ttk.Checkbutton(self.frm_net, text="Flush RX at Connect", variable=self.flush_rx_var)
        self.flush_cb.grid(row=row, column=1, sticky="w", padx=8, pady=2)

        #self.reinit_var = tk.BooleanVar(value=self.pipe_cfg.get('pipe_be_reinit_conn', False))
        #self.reinit_cb = ttk.Checkbutton(self.frm_net, text="Auto-Reconnect (TCP-Client)", variable=self.reinit_var)
        #self.reinit_cb.grid(row=row, column=2, sticky="w", padx=40, pady=2)

        row += 1
        ttk.Label(self.frm_net, text="C-Text:").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.ctext_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_c_text', ''))
        ttk.Entry(self.frm_net, textvariable=self.ctext_var, width=70).grid(row=row, column=1, columnspan=2,
                                                                            sticky="we", padx=8)

        row += 1
        ttk.Label(self.frm_net, text="Encoding:").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        self.encoding_var = tk.StringVar(value=self.pipe_cfg.get('pipe_parm_txt_encoder', 'UTF-8'))
        ttk.Combobox(self.frm_net, textvariable=self.encoding_var,
                     values=['UTF-8', 'CP437', 'ISO-8859-1', 'ASCII', 'latin1'], state="readonly", width=15).grid(
            row=row, column=1, sticky="w", padx=8)

        self.frm_net.columnconfigure(1, weight=1)

        # ===================================================================
        # 6. Serial-spezifische Optionen (separat!)
        # ===================================================================
        self.frm_serial = ttk.LabelFrame(main, text=f" {self._getTabStr('serial_interface')} ")

        row = 0
        ttk.Label(self.frm_serial, text="Serial Port:").grid(row=row, column=0, sticky="w", padx=8, pady=6)
        self.serial_port_var = tk.StringVar()
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        if not available_ports:
            available_ports = ['/dev/ttyUSB0', '/dev/ttyACM0', 'COM3', 'COM4']
        self.cb_serial_port = ttk.Combobox(self.frm_serial, textvariable=self.serial_port_var, values=available_ports,
                                           width=20)
        self.cb_serial_port.grid(row=row, column=1, padx=8, pady=6)

        ttk.Label(self.frm_serial, text="Baudrate:").grid(row=row, column=2, sticky="w", padx=20)
        self.baudrate_var = tk.StringVar(value="9600")
        baud_rates = ['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600']
        self.cb_baud = ttk.Combobox(self.frm_serial,
                                    textvariable=self.baudrate_var,
                                    values=baud_rates,
                                    width=12,
                                    state="readonly")
        self.cb_baud.grid(row=row, column=3, padx=8, pady=6)

        # Vorbelegung aus Config
        if isinstance(addr, (tuple, list)) and len(addr) >= 2:
            if addr[0].startswith('/dev/') or addr[0].startswith('COM'):
                self.serial_port_var.set(addr[0])
                self.baudrate_var.set(str(addr[1]) if addr[1] in baud_rates else "115200")

        self.frm_serial.columnconfigure(1, weight=1)

        # ===================================================================
        # Initiale Anzeige aktualisieren
        # ===================================================================
        self._update_backend_fields()
        self._is_unProt()

    def _select_files(self, tx=True):
        self._root_win.attributes("-topmost", False)
        # self.root.lower
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
                self.tx_filename_var.set(filenames[0])
            else:
                self.rx_filename_var.set(filenames[0])

    def _chk_port_id(self, event=None):
        vals = []
        port_id = self.port_var.get()

        if port_id:
            port_id = int(port_id)
            if port_id in self._port_handler.get_all_ports().keys():
                # vals = self._port_handler.get_all_ports()[port_id].my_stations
                vals = self._port_handler.get_stat_calls_fm_port(port_id)
            if vals:
                self.call_var.set(self.pipe_cfg.get('pipe_parm_own_call', vals[0]))
                # self.call_var.set(vals[0])
            else:
                # self.call_var.set('')
                self.call_var.set(self.pipe_cfg.get('pipe_parm_own_call', ''))

        self._call_ent.config(values=vals)

    def _update_backend_fields(self):
        backend = self.backend_var.get()

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

    def _is_unProt(self):
        if self.pipe_cfg.get('pipe_parm_Proto', True):
            self._to_add_ent.config(state='disabled')
            self._call_ent.config(state='disabled')
            self._pid_ent.config(state='disabled')
            self._cmd_ent.config(state='disabled')
            self._poll_ent.config(state='disabled')
            self._port_ent.config(state='disabled')
            # self.max_pac_ent.config(state='disabled')
            # self.pac_len_ent.config(state='disabled')
        else:
            self._to_add_ent.config(state='normal')
            self._call_ent.config(state='normal')
            self._pid_ent.config(state='normal')
            self._cmd_ent.config(state='normal')
            self._poll_ent.config(state='normal')
            # self.max_pac_ent.config(state='normal')
            # self.pac_len_ent.config(state='normal')

    def get_connection(self):
        return self._connection


class PipeToolSettings(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, master=root.main_win)
        self._root        = root
        self._getTabStr   = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        root.settings_win = self
        self.win_height   = 600
        self.win_width    = 860
        self.style      = root.style
        self.style_name = root.style_name
        self.title(self._getTabStr('pipetool_settings'))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root.main_win.winfo_x()}+"
                      f"{self._root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ##########################
        self._port_handler = root.get_PH_mainGUI()
        ##########################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ##########################
        # OK, Save, Cancel
        ok_bt = ttk.Button(main_f,
                          text=self._getTabStr('OK'),
                          #height=1,
                          width=6,
                          command=self._ok_btn_cmd)
        """
        save_bt = tk.Button(self,
                            text=STR_TABLE['save'][self.lang],
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)
        """

        cancel_bt = ttk.Button(main_f,
                              text=self._getTabStr('cancel'),
                              #height=1,
                              width=8,
                              command=self._destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        # save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)
        ####################################
        # New Station, Del Station Buttons
        ttk.Button(main_f,
                  text=self._getTabStr('new_pipe'),
                  #height=1,
                  width=10,
                  command=self._new_pipe_btn_cmd). \
            place(x=20, y=self.win_height - 590)
        ttk.Button(main_f,
                  text=self._getTabStr('new_pipe_fm_connection'),
                  #height=1,
                  width=17,
                  command=self._new_pipe_on_conn). \
            place(x=220, y=self.win_height - 590)
        tk.Button(main_f,
                  text=self._getTabStr('delete'),
                  bg="red3",
                  height=1,
                  width=10,
                  relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                  highlightthickness=0,

                  command=self._del_btn_cmd). \
            place(x=self.win_width - 141, y=self.win_height - 590)

        self.tabControl = ttk.Notebook(main_f, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self.win_height - 550)
        self.tab_list = []
        all_pipes = self._port_handler.get_all_pipes()
        for pipe in all_pipes:
            pipe_cfg = pipe.get_cfg_fm_pipe()
            if ((pipe_cfg.get('pipe_parm_permanent', False) and not pipe_cfg.get('pipe_parm_Proto', True)) or
                not (pipe_cfg.get('pipe_parm_permanent', False) and pipe_cfg.get('pipe_parm_Proto', True))):
                label_txt = f"{len(self.tab_list)}"
                # label_txt = f"{len(self.tab_list)}-{pipe.}"
                tab = PipeTab(self, pipe=pipe)
                self.tabControl.add(tab.own_tab, text=label_txt)
                self.tabControl.select(len(self.tab_list))
                self.tab_list.append(tab)

    def _set_vars(self):
        for tab in self.tab_list:
            conn        = tab.get_connection()
            pipe_cfg    = tab.pipe_cfg
            old_portID  = int(pipe_cfg['pipe_parm_port'])
            old_call    = str(pipe_cfg['pipe_parm_own_call'])
            pipe_cfg['pipe_parm_own_call']      = str(tab.call_var.get().upper())        # TODO Call/Input Vali
            pipe_cfg['pipe_parm_address_str']   = str(tab.to_add_var.get().upper())   # TODO Call/Input Vali
            pipe_cfg['pipe_parm_port']          = int(tab.port_var.get())
            pipe_cfg['pipe_parm_Proto']         = bool(conn)
            pipe_cfg['pipe_parm_permanent']     = not bool(conn)
            pipe_cfg['pipe_parm_PacLen']        = int(tab.pac_len_var.get())
            pipe_cfg['pipe_parm_MaxFrame']      = int(tab.max_pac_var.get())
            pipe_cfg['pipe_parm_pid']           = int(tab.pid_var.get().split('>')[0], 16)
            pipe_cfg['pipe_parm_cmd_pf']        = (bool(tab.cmd_var.get()), bool(tab.poll_var.get()))
            pipe_cfg['pipe_parm_pipe_tx']       = tab.tx_filename_var.get()
            pipe_cfg['pipe_parm_pipe_rx']       = tab.rx_filename_var.get()
            pipe_cfg['pipe_parm_MaxPacDelay']       = int(tab.max_pac_delay_var.get())
            pipe_cfg['pipe_parm_pipe_loop_timer']   = int(tab.loop_timer_var.get())

            # Backend-spezifische Adresse korrekt speichern
            backend = tab.backend_var.get()
            pipe_cfg['pipe_parm_backend'] = backend

            if backend in ['tcp-server', 'tcp-client']:
                addr_str = tab.addr_var.get().strip()
                if ':' in addr_str:
                    ip, port = addr_str.split(':', 1)
                    port = int(port)
                else:
                    ip, port = addr_str, 8023
                pipe_cfg['pipe_be_address'] = (ip.strip(), port)

            elif backend == 'serial':
                port = tab.serial_port_var.get().strip()
                try:
                    baud = int(tab.baudrate_var.get())
                except Exception as _ex:
                    _ex = _ex
                    baud = 9600
                pipe_cfg['pipe_be_address'] = (port, baud)

            # Rest wie gehabt
            pipe_cfg['pipe_be_send_at_init'] = tab.send_init_var.get()
            pipe_cfg['pipe_be_flush_rx_at_init'] = bool(tab.flush_rx_var.get())
            # pipe_cfg['pipe_be_reinit_conn'] = bool(tab.reinit_var.get() if backend == 'tcp-client' else False)
            pipe_cfg['pipe_be_reinit_conn'] = False
            pipe_cfg['pipe_parm_c_text'] = tab.ctext_var.get()
            pipe_cfg['pipe_parm_txt_encoder'] = tab.encoding_var.get()

            if conn:
                conn.set_pipe(pipe_cfg=pipe_cfg)
            else:
                # self._port_handler.add_pipe_PH(pipe)
                port = self._port_handler.get_port_by_id(pipe_cfg['pipe_parm_port'])
                if port:
                    port.add_pipe(pipe_cfg=pipe_cfg)

                if pipe_cfg['pipe_parm_permanent']:

                    POPT_CFG.del_pipe_CFG(f'{old_portID}-{old_call}')
                    POPT_CFG.set_pipe_CFG(pipe_cfg)
            """
            if pipe.port_id in self._port_handler.get_all_ports().keys():
                self._port_handler.get_all_ports()[pipe.port_id].pipes[pipe.uid] = pipe
                # if pipe.uid in port.pipes:
            """

    """
    def save_btn_cmd(self):
        self.set_vars()
        self._root.msg_to_monitor('Info: Pipe-Tool Settings wurden gespeichert..')
        self._root.msg_to_monitor('Lob: Gute Entscheidung!')
    """

    def _ok_btn_cmd(self):
        self._set_vars()
        self._root.ch_status_update()
        self._root.sysMsg_to_monitor('Info: Pipe-Tool Settings wurden gespeichert..')
        self._root.sysMsg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self._destroy_win()

    def _destroy_win(self):
        self.destroy()
        self._root.settings_win = None

    def tasker(self):
        pass

    def _new_pipe_btn_cmd(self):
        label_txt = f"{len(self.tab_list)}"
        tab = PipeTab(self)
        self.tabControl.add(tab.own_tab, text=label_txt)
        self.tabControl.select(len(self.tab_list))
        self.tab_list.append(tab)

    def _new_pipe_on_conn(self):
        conn = self._root.get_conn()
        if conn is not None:
            label_txt = f"{len(self.tab_list)}"
            tab = PipeTab(self, connection=conn)
            self.tabControl.add(tab.own_tab, text=label_txt)
            #self.tabControl.select(len(self.tab_list))
            self.tab_list.append(tab)

    def _del_btn_cmd(self):
        try:
            ind = self.tabControl.index('current')
        except tk.TclError:
            pass
        else:
            pipe_cfg = self.tab_list[ind].pipe_cfg
            # FIXME check empty cfg
            #  if empty:
            #     if ind in self.tab_list:
            #         del self.tab_list[ind]
            #     self.tabControl.forget(ind)
            add_str   = pipe_cfg.get('pipe_parm_address_str', '')
            own_call  = pipe_cfg.get('pipe_parm_own_call', '')
            dest_call = add_str.split(' ')[0]
            via_calls = add_str.split(' ')[1:]
            uid = build_ax25uid(
                from_call_str=own_call,
                to_call_str=dest_call,
                via_calls=via_calls,
                dec=False
            )
            """
            try:
                dummy_pipe = AX25Pipe(pipe_cfg=pipe_cfg)
            except AttributeError:
                if ind in self.tab_list:
                    del self.tab_list[ind]
                self.tabControl.forget(ind)
                return
            """
            conn = self.tab_list[ind].get_connection()
            if conn is not None:
                conn.del_pipe_fm_conn()
            else:
                conn = self._root.get_conn()
                if conn:
                    conn.del_pipe_fm_conn()
            port_id = pipe_cfg['pipe_parm_port']
            #uid = dummy_pipe.get_pipe_uid()
            if port_id == -1:
                for port_id in self._port_handler.get_all_ports().keys():
                    if uid in self._port_handler.get_all_ports()[port_id].pipes.keys():
                        del self._port_handler.get_all_ports()[port_id].pipes[uid]
            else:
                if port_id in self._port_handler.get_all_ports().keys():
                    if uid in self._port_handler.get_all_ports()[port_id].pipes.keys():
                        del self._port_handler.get_all_ports()[port_id].pipes[uid]
            if self.tab_list[ind].pipe_cfg.get('pipe_parm_permanent', False):
                if not POPT_CFG.del_pipe_CFG_fm_CallPort(pipe_cfg.get('pipe_parm_own_call', ''),
                                                     pipe_cfg.get('pipe_parm_port', -1)):

                    logger.debug('PipeGUI: Error DEL PIPE')
            del self.tab_list[ind]
            self.tabControl.forget(ind)
            self._root.ch_status_update()
            #del dummy_pipe

    def get_port_handler(self):
        return self._port_handler