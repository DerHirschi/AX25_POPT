import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25dec_enc import PIDByte
from ax25.ax25UI_Pipe import AX25Pipe
from cfg.default_config import getNew_pipe_cfg
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE


class PipeTab:
    def __init__(self, root_win, pipe=None, connection=None):
        self._root_win = root_win
        self.tab_clt = root_win.tabControl
        self.lang = root_win.lang
        self.style = root_win.style
        self.own_tab = ttk.Frame(self.tab_clt)
        self._connection = connection
        if pipe is None:
            self.pipe_cfg = getNew_pipe_cfg()
            self.pipe_cfg['pipe_parm_Proto'] = False
            self.pipe_cfg['pipe_parm_permanent'] = True
        else:
            self.pipe_cfg = pipe.get_cfg_fm_pipe()
            if pipe.get_pipe_connection():
                self._connection = pipe.get_pipe_connection()
        del pipe
        #########################################################
        # Address
        x = 10
        y = 10
        self.to_add_var = tk.StringVar(self.own_tab)
        tk.Label(self.own_tab, text=f"{STR_TABLE['to'][self.lang]}:").place(x=x, y=y)
        # if self.pipe.add_str:
        if self.pipe_cfg.get('pipe_parm_address_str', ''):
            self.to_add_var.set(self.pipe_cfg.get('pipe_parm_address_str', ''))
        self._to_add_ent = tk.Entry(self.own_tab,
                                    textvariable=self.to_add_var,
                                    width=50)
        self._to_add_ent.place(x=x + 40, y=y)

        # CMD/RPT
        x = 10
        y = 80
        self.cmd_var = tk.BooleanVar(self.own_tab)
        self.cmd_var.set(self.pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[0])
        self._cmd_ent = tk.Checkbutton(self.own_tab,
                                       variable=self.cmd_var,
                                       text='CMD/RPT')
        self._cmd_ent.place(x=x, y=y)

        # Poll
        x = 10
        y = 105
        self.poll_var = tk.BooleanVar(self.own_tab)
        self.poll_var.set(self.pipe_cfg.get('pipe_parm_cmd_pf', (False, False))[1])
        self._poll_ent = tk.Checkbutton(self.own_tab,
                                        variable=self.poll_var,
                                        text='Poll')
        self._poll_ent.place(x=x, y=y)

        # Port
        x = 40
        y = 140
        tk.Label(self.own_tab, text=f"{STR_TABLE['port'][self.lang]}:").place(x=x, y=y)
        self.port_var = tk.StringVar(self.own_tab)
        self.port_var.set(self.pipe_cfg.get('pipe_parm_port', -1))
        vals = ['-1']
        if PORT_HANDLER.get_all_ports().keys():
            vals += [str(x) for x in list(PORT_HANDLER.get_all_ports().keys())]
        self._port_ent = tk.ttk.Combobox(self.own_tab,
                                         width=4,
                                         textvariable=self.port_var,
                                         values=vals,
                                         )
        self._port_ent.bind("<KeyRelease>", self._chk_port_id)
        self._port_ent.bind("<<ComboboxSelected>>", self._chk_port_id)
        self._port_ent.place(x=x + 50, y=y)
        # Max Pac
        x = 240
        y = 140
        tk.Label(self.own_tab, text="Max Pac:").place(x=x, y=y)
        self.max_pac_var = tk.StringVar(self.own_tab)
        self.max_pac_var.set(self.pipe_cfg.get('pipe_parm_MaxFrame', 3))
        vals = [str(x) for x in range(1, 8)]
        max_pac_ent = tk.ttk.Spinbox(self.own_tab,
                                          width=2,
                                          textvariable=self.max_pac_var,
                                          values=vals,
                                          )
        max_pac_ent.place(x=x + 160, y=y)
        # Pac len
        x = 490
        y = 140
        tk.Label(self.own_tab, text="Pac-len:").place(x=x, y=y)
        self.pac_len_var = tk.StringVar(self.own_tab)
        self.pac_len_var.set(self.pipe_cfg.get('pipe_parm_PacLen', 128))
        vals = [str(x) for x in range(1, 257)]
        pac_len_ent = tk.ttk.Spinbox(self.own_tab,
                                          width=3,
                                          textvariable=self.pac_len_var,
                                          values=vals,
                                          )
        pac_len_ent.place(x=x + 75, y=y)
        # Max Pac Delay
        x = 240
        y = 175
        tk.Label(self.own_tab, text="Max Pac Delay (s):").place(x=x, y=y)
        self.max_pac_delay_var = tk.StringVar(self.own_tab)
        self.max_pac_delay_var.set(self.pipe_cfg.get('pipe_parm_MaxPacDelay', 30))
        vals = [str(x * 10) for x in range(1, 37)]
        max_pac_delay = tk.ttk.Spinbox(self.own_tab,
                                            width=3,
                                            textvariable=self.max_pac_delay_var,
                                            values=vals,
                                            )
        max_pac_delay.place(x=x + 160, y=y)
        # Calls
        x = 40
        y = 175
        self.call_var = tk.StringVar(self.own_tab)
        """
        _vals = []
        port_id = int(self.port_var.get())
        if port_id in PORT_HANDLER.get_all_ports().keys():
            _vals = PORT_HANDLER.get_all_ports()[port_id].my_stations
        if _vals:
            if self.pipe.ax25_frame.from_call.call_str:
                self.call_var.set(self.pipe.ax25_frame.from_call.call_str)
            else:
                self.call_var.set(_vals[0])
        """
        self.call_var.set(self.pipe_cfg.get('pipe_parm_own_call', ''))
        self._call_ent = tk.ttk.Combobox(self.own_tab,
                                         width=9,
                                         textvariable=self.call_var,
                                         # values=_vals,
                                         )
        self._call_ent.place(x=x, y=y)
        self._chk_port_id()

        # PID
        x = 10
        y = 45
        self.pid_var = tk.StringVar(self.own_tab)
        tk.Label(self.own_tab, text='PID:').place(x=x, y=y)
        pid = PIDByte()
        pac_types = dict(pid.pac_types)
        vals = []
        for x in list(pac_types.keys()):
            pid.pac_types[int(x)]()
            vals.append(f"{str(hex(int(x))).upper()}>{pid.flag}")
        self._pid_ent = tk.ttk.Combobox(self.own_tab,
                                        width=30,
                                        values=vals,
                                        textvariable=self.pid_var)
        pid = f"{str(hex(self.pipe_cfg.get('pipe_parm_pid', 0xf0)))}"
        self.pid_var.set(pid)
        self._pid_ent.place(x=x + 40, y=y)
        # Loop Timer
        x = 10
        y = self._root_win.win_height - 255 - 80  # iam lazy
        tk.Label(self.own_tab, text='TX-File Check Timer (sek/sec):').place(x=x, y=y)
        self.loop_timer_var = tk.StringVar(self.own_tab)
        self.loop_timer_var.set(self.pipe_cfg.get('pipe_parm_pipe_loop_timer', 10))
        loop_timer = tk.Spinbox(self.own_tab,
                                     from_=5,
                                     to=360,
                                     increment=5,
                                     width=3,
                                     textvariable=self.loop_timer_var,
                                     # command=self.set_max_frame,
                                     # state='disabled'
                                     )
        loop_timer.place(x=x + 270, y=y)

        #################
        # TX FILE
        x = 10
        y = self._root_win.win_height - 220 - 80  # iam lazy
        tk.Label(self.own_tab, text=f"{STR_TABLE['tx_file'][self.lang]}:").place(x=x, y=y)
        self.tx_filename_var = tk.StringVar(self.own_tab)
        self.tx_filename_var.set(self.pipe_cfg.get('pipe_parm_pipe_tx', ''))
        tx_filename = tk.Entry(self.own_tab, textvariable=self.tx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        tx_filename.place(x=x + 140, y=y)
        tk.Button(self.own_tab,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  command=lambda: self._select_files(tx=True)
                  ).place(x=x + 710, y=y - 2)
        #################
        # RX FILE
        x = 10
        y = self._root_win.win_height - 180 - 80  # iam lazy
        tk.Label(self.own_tab, text=f"{STR_TABLE['rx_file'][self.lang]}:").place(x=x, y=y)
        self.rx_filename_var = tk.StringVar(self.own_tab)
        self.rx_filename_var.set(self.pipe_cfg.get('pipe_parm_pipe_rx', ''))
        rx_filename = tk.Entry(self.own_tab, textvariable=self.rx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        rx_filename.place(x=x + 140, y=y)
        tk.Button(self.own_tab,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  command=lambda: self._select_files(tx=False)
                  ).place(x=x + 710, y=y - 2)

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
            filetypes=filetypes)

        if filenames:
            if tx:
                self.tx_filename_var.set(filenames[0])
            else:
                self.rx_filename_var.set(filenames[0])

    def _chk_port_id(self, event=None):
        vals = []
        port_id = self.port_var.get()
        print(port_id)

        if port_id:
            port_id = int(port_id)
            if port_id in PORT_HANDLER.get_all_ports().keys():
                vals = PORT_HANDLER.get_all_ports()[port_id].my_stations
            if vals:
                self.call_var.set(self.pipe_cfg.get('pipe_parm_own_call', vals[0]))
                # self.call_var.set(vals[0])
            else:
                # self.call_var.set('')
                self.call_var.set(self.pipe_cfg.get('pipe_parm_own_call', ''))

        self._call_ent.config(values=vals)

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
        tk.Toplevel.__init__(self)
        self._root = root
        self.lang = self._root.language
        root.settings_win = self
        self.win_height = 600
        self.win_width = 860
        self.style = root.style
        self.title(STR_TABLE['pipetool_settings'][self.lang])
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root.main_win.winfo_x()}+"
                      f"{self._root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()

        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text=STR_TABLE['OK'][self.lang],
                          height=1,
                          width=6,
                          command=self._ok_btn_cmd)
        """
        save_bt = tk.Button(self,
                            text=STR_TABLE['save'][self.lang],
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)
        """

        cancel_bt = tk.Button(self,
                              text=STR_TABLE['cancel'][self.lang],
                              height=1,
                              width=8,
                              command=self._destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        # save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)
        ####################################
        # New Station, Del Station Buttons
        tk.Button(self,
                  text=STR_TABLE['new_pipe'][self.lang],
                  height=1,
                  width=10,
                  command=self._new_pipe_btn_cmd). \
            place(x=20, y=self.win_height - 590)
        tk.Button(self,
                  text=STR_TABLE['new_pipe_fm_connection'][self.lang],
                  height=1,
                  width=17,
                  command=self._new_pipe_on_conn). \
            place(x=220, y=self.win_height - 590)
        tk.Button(self,
                  text=STR_TABLE['delete'][self.lang],
                  bg="red3",
                  height=1,
                  width=10,
                  command=self._del_btn_cmd). \
            place(x=self.win_width - 141, y=self.win_height - 590)

        self.tabControl = ttk.Notebook(self, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self.win_height - 550)
        self.tab_list: [ttk.Frame] = []
        all_pipes = PORT_HANDLER.get_all_pipes()
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
            conn = tab.get_connection()
            pipe_cfg = tab.pipe_cfg
            old_portID = int(pipe_cfg['pipe_parm_port'])
            old_call = str(pipe_cfg['pipe_parm_own_call'])
            pipe_cfg['pipe_parm_own_call'] = str(tab.call_var.get().upper())        # TODO Call/Input Vali
            pipe_cfg['pipe_parm_address_str'] = str(tab.to_add_var.get().upper())   # TODO Call/Input Vali
            pipe_cfg['pipe_parm_port'] = int(tab.port_var.get())
            pipe_cfg['pipe_parm_Proto'] = bool(conn)
            pipe_cfg['pipe_parm_permanent'] = not bool(conn)
            pipe_cfg['pipe_parm_PacLen'] = int(tab.pac_len_var.get())
            pipe_cfg['pipe_parm_MaxFrame'] = int(tab.max_pac_var.get())
            pipe_cfg['pipe_parm_pid'] = int(tab.pid_var.get().split('>')[0], 16)
            pipe_cfg['pipe_parm_cmd_pf'] = (bool(tab.cmd_var.get()), bool(tab.poll_var.get()))
            pipe_cfg['pipe_parm_pipe_tx'] = tab.tx_filename_var.get()
            pipe_cfg['pipe_parm_pipe_rx'] = tab.rx_filename_var.get()
            pipe_cfg['pipe_parm_MaxPacDelay'] = int(tab.max_pac_delay_var.get())
            pipe_cfg['pipe_parm_pipe_loop_timer'] = int(tab.loop_timer_var.get())

            if conn:
                conn.set_pipe(pipe_cfg=pipe_cfg)
            else:
                # PORT_HANDLER.add_pipe_PH(pipe)
                port = PORT_HANDLER.get_port_by_id(pipe_cfg['pipe_parm_port'])
                if port:
                    port.add_pipe(pipe_cfg=pipe_cfg)

                if pipe_cfg['pipe_parm_permanent']:

                    POPT_CFG.del_pipe_CFG(f'{old_portID}-{old_call}')
                    POPT_CFG.set_pipe_CFG(pipe_cfg)
            """
            if pipe.port_id in PORT_HANDLER.get_all_ports().keys():
                PORT_HANDLER.get_all_ports()[pipe.port_id].pipes[pipe.uid] = pipe
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
            dummy_pipe = AX25Pipe(
                connection=conn
            )
            label_txt = f"{len(self.tab_list)}"
            tab = PipeTab(self, pipe=dummy_pipe, connection=conn)
            self.tabControl.add(tab.own_tab, text=label_txt)
            self.tabControl.select(len(self.tab_list))
            self.tab_list.append(tab)

    def _del_btn_cmd(self):
        try:
            ind = self.tabControl.index('current')
        except tk.TclError:
            pass
        else:
            pipe_cfg = self.tab_list[ind].pipe_cfg
            dummy_pipe = AX25Pipe(pipe_cfg=pipe_cfg)
            conn = self.tab_list[ind].get_connection()
            if conn is not None:
                conn.del_pipe_fm_conn()
            else:
                conn = self._root.get_conn()
                if conn:
                    conn.del_pipe_fm_conn()
            port_id = pipe_cfg['pipe_parm_port']
            uid = dummy_pipe.get_pipe_uid()        # TODO uid_generator_fnc
            if port_id == -1:
                for port_id in PORT_HANDLER.get_all_ports().keys():
                    if uid in PORT_HANDLER.get_all_ports()[port_id].pipes.keys():
                        del PORT_HANDLER.get_all_ports()[port_id].pipes[uid]
            else:
                if port_id in PORT_HANDLER.get_all_ports().keys():
                    if uid in PORT_HANDLER.get_all_ports()[port_id].pipes.keys():
                        del PORT_HANDLER.get_all_ports()[port_id].pipes[uid]
            if self.tab_list[ind].pipe_cfg.get('pipe_parm_permanent', False):
                if not POPT_CFG.del_pipe_CFG_fm_CallPort(pipe_cfg.get('pipe_parm_own_call', ''),
                                                     pipe_cfg.get('pipe_parm_port', -1)):

                    print('Error DEL PIPE')
            del self.tab_list[ind]
            self.tabControl.forget(ind)
            self._root.ch_status_update()
            del dummy_pipe
