import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25dec_enc import PIDByte
from ax25.ax25UI_Pipe import AX25Pipe
from ax25.ax25Connection import AX25Conn
from string_tab import STR_TABLE


class AX25PipeTab:
    def __init__(self, root_win, pipe=None, connection=None):
        self._root_win = root_win
        self.tab_clt = root_win.tabControl
        self.lang = root_win.lang
        self.style = root_win.style
        self.own_tab = ttk.Frame(self.tab_clt)
        if pipe is None:
            self.pipe = AX25Pipe(
                port_id=0,
                own_call='',
                address_str='NOCALL',
                cmd_pf=(False, False),
                pid=0xf0
            )
            self.pipe.connection = connection
        else:
            self.pipe = pipe
        #########################################################
        # Address
        _x = 10
        _y = 10
        self.to_add_var = tk.StringVar(self.own_tab)
        tk.Label(self.own_tab, text=f"{STR_TABLE['to'][self.lang]}:").place(x=_x, y=_y)
        if self.pipe.add_str:
            self.to_add_var.set(self.pipe.add_str)
        self.to_add_ent = tk.Entry(self.own_tab,
                                   textvariable=self.to_add_var,
                                   width=50)
        self.to_add_ent.place(x=_x + 40, y=_y)

        # CMD/RPT
        _x = 10
        _y = 80
        self.cmd_var = tk.BooleanVar(self.own_tab)
        self.cmd_var.set(self.pipe.ax25_frame.ctl_byte.cmd)
        self.cmd_ent = tk.Checkbutton(self.own_tab,
                                      variable=self.cmd_var,
                                      text='CMD/RPT')
        self.cmd_ent.place(x=_x, y=_y)

        # Poll
        _x = 10
        _y = 105
        self.poll_var = tk.BooleanVar(self.own_tab)
        self.poll_var.set(self.pipe.ax25_frame.ctl_byte.pf)
        self.poll_ent = tk.Checkbutton(self.own_tab,
                                       variable=self.poll_var,
                                       text='Poll')
        self.poll_ent.place(x=_x, y=_y)

        # Port
        _x = 40
        _y = 140
        tk.Label(self.own_tab, text=f"{STR_TABLE['port'][self.lang]}:").place(x=_x, y=_y)
        self.port_var = tk.StringVar(self.own_tab)
        self.port_var.set(self.pipe.port_id)
        _vals = ['0']
        if PORT_HANDLER.get_all_ports().keys():
            _vals = [str(x) for x in list(PORT_HANDLER.get_all_ports().keys())]
        self.port_ent = tk.ttk.Combobox(self.own_tab,
                                        width=4,
                                        textvariable=self.port_var,
                                        values=_vals,
                                        )
        self.port_ent.bind("<KeyRelease>", self._chk_port_id)
        self.port_ent.bind("<<ComboboxSelected>>", self._chk_port_id)
        self.port_ent.place(x=_x + 50, y=_y)
        # Max Pac
        _x = 240
        _y = 140
        tk.Label(self.own_tab, text="Max Pac:").place(x=_x, y=_y)
        self.max_pac_var = tk.StringVar(self.own_tab)
        self.max_pac_var.set(self.pipe.parm_max_pac)
        _vals = [str(x) for x in range(1, 8)]
        self.max_pac_ent = tk.ttk.Spinbox(self.own_tab,
                                          width=2,
                                          textvariable=self.max_pac_var,
                                          values=_vals,
                                          )
        self.max_pac_ent.place(x=_x + 160, y=_y)
        # Pac len
        _x = 490
        _y = 140
        tk.Label(self.own_tab, text="Pac-len:").place(x=_x, y=_y)
        self.pac_len_var = tk.StringVar(self.own_tab)
        self.pac_len_var.set(self.pipe.parm_pac_len)
        _vals = [str(x) for x in range(1, 257)]
        self.pac_len_ent = tk.ttk.Spinbox(self.own_tab,
                                          width=3,
                                          textvariable=self.pac_len_var,
                                          values=_vals,
                                          )
        self.pac_len_ent.place(x=_x + 75, y=_y)
        # Max Pac Delay
        _x = 240
        _y = 175
        tk.Label(self.own_tab, text="Max Pac Delay (s):").place(x=_x, y=_y)
        self.max_pac_delay_var = tk.StringVar(self.own_tab)
        self.max_pac_delay_var.set(self.pipe.parm_max_pac_timer)
        _vals = [str(x * 10) for x in range(1, 37)]
        self.max_pac_delay = tk.ttk.Spinbox(self.own_tab,
                                            width=3,
                                            textvariable=self.max_pac_delay_var,
                                            values=_vals,
                                            )
        self.max_pac_delay.place(x=_x + 160, y=_y)
        # Calls
        _x = 40
        _y = 175
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
        self.call_ent = tk.ttk.Combobox(self.own_tab,
                                        width=9,
                                        textvariable=self.call_var,
                                        # values=_vals,
                                        )
        self.call_ent.place(x=_x, y=_y)
        self._chk_port_id()

        # PID
        _x = 10
        _y = 45
        self.pid_var = tk.StringVar(self.own_tab)
        tk.Label(self.own_tab, text='PID:').place(x=_x, y=_y)
        pid = PIDByte()
        pac_types = dict(pid.pac_types)
        _vals = []
        for x in list(pac_types.keys()):
            pid.pac_types[int(x)]()
            _vals.append(f"{str(hex(x)).upper()}>{pid.flag}")
        self.pid_ent = tk.ttk.Combobox(self.own_tab,
                                       width=30,
                                       values=_vals,
                                       textvariable=self.pid_var)
        pid = f"{str(hex(self.pipe.ax25_frame.pid_byte.hex))}>{self.pipe.ax25_frame.pid_byte.flag}"
        self.pid_var.set(pid)
        self.pid_ent.place(x=_x + 40, y=_y)
        # Loop Timer
        _x = 10
        _y = self._root_win.win_height - 255 - 80  # iam lazy
        tk.Label(self.own_tab, text='TX-File Check Timer (sek/sec):').place(x=_x, y=_y)
        self.loop_timer_var = tk.StringVar(self.own_tab)
        self.loop_timer_var.set(self.pipe.parm_tx_file_check_timer)
        self.loop_timer = tk.Spinbox(self.own_tab,
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
        _y = self._root_win.win_height - 220 - 80  # iam lazy
        tk.Label(self.own_tab, text=f"{STR_TABLE['tx_file'][self.lang]}:").place(x=_x, y=_y)
        self.tx_filename_var = tk.StringVar(self.own_tab)
        self.tx_filename_var.set(self.pipe.tx_filename)
        self.tx_filename = tk.Entry(self.own_tab, textvariable=self.tx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self.tx_filename.place(x=_x + 140, y=_y)
        tk.Button(self.own_tab,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  command=lambda: self._select_files(tx=True)
                  ).place(x=_x + 710, y=_y - 2)
        #################
        # RX FILE
        _x = 10
        _y = self._root_win.win_height - 180 - 80  # iam lazy
        tk.Label(self.own_tab, text=f"{STR_TABLE['rx_file'][self.lang]}:").place(x=_x, y=_y)
        self.rx_filename_var = tk.StringVar(self.own_tab)
        self.rx_filename_var.set(self.pipe.rx_filename)
        self.rx_filename = tk.Entry(self.own_tab, textvariable=self.rx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self.rx_filename.place(x=_x + 140, y=_y)
        tk.Button(self.own_tab,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  command=lambda: self._select_files(tx=False)
                  ).place(x=_x + 710, y=_y - 2)

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
        _vals = []
        port_id = self.port_var.get()
        print(port_id)

        if port_id:
            port_id = int(port_id)
            if port_id in PORT_HANDLER.get_all_ports().keys():
                _vals = PORT_HANDLER.get_all_ports()[port_id].my_stations
            if _vals:
                self.call_var.set(_vals[0])
            else:
                self.call_var.set('')

        self.call_ent.config(values=_vals)

    def _is_unProt(self):
        unProt = False
        if self.pipe.connection is None:
            unProt = True

        if not unProt:

            self.to_add_ent.config(state='disabled')
            self.call_ent.config(state='disabled')
            self.pid_ent.config(state='disabled')
            self.cmd_ent.config(state='disabled')
            self.poll_ent.config(state='disabled')
            self.port_ent.config(state='disabled')
            # self.max_pac_ent.config(state='disabled')
            # self.pac_len_ent.config(state='disabled')
        else:
            self.to_add_ent.config(state='normal')
            self.call_ent.config(state='normal')
            self.pid_ent.config(state='normal')
            self.cmd_ent.config(state='normal')
            self.poll_ent.config(state='normal')
            # self.max_pac_ent.config(state='normal')
            # self.pac_len_ent.config(state='normal')


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
        self.all_pipes = PORT_HANDLER.get_all_pipes()
        for pipe in self.all_pipes:
            label_txt = f"{len(self.tab_list)}"
            tab = AX25PipeTab(self, pipe=pipe)
            self.tabControl.add(tab.own_tab, text=label_txt)
            self.tabControl.select(len(self.tab_list))
            self.tab_list.append(tab)

    def _set_vars(self):
        for tab in self.tab_list:
            pipe: AX25Pipe = tab.pipe
            pipe.ax25_frame.from_call.call_str = tab.call_var.get().upper()
            pipe.set_dest_add(tab.to_add_var.get().upper())
            pipe.port_id = int(tab.port_var.get())
            pid = int(tab.pid_var.get().split('>')[0], 16)
            pipe.parm_max_pac_timer = int(tab.max_pac_delay_var.get())
            pipe.parm_tx_file_check_timer = int(tab.loop_timer_var.get())
            pipe.tx_filename = tab.tx_filename_var.get()
            pipe.rx_filename = tab.rx_filename_var.get()
            pipe.parm_max_pac = int(tab.max_pac_var.get())
            pipe.parm_pac_len = int(tab.pac_len_var.get())
            if pipe.connection is None:
                pipe.ax25_frame.ctl_byte.UIcByte()
                pipe.ax25_frame.pid_byte.pac_types[pid]()
                pipe.ax25_frame.ctl_byte.pf = tab.poll_var.get()
                pipe.ax25_frame.ctl_byte.cmd = tab.cmd_var.get()
            pipe.change_settings()
            if pipe.connection is not None:
                # pipe.connection.pipe = pipe
                pipe.connection.set_pipe(pipe)
            if pipe.port_id in PORT_HANDLER.get_all_ports().keys():
                PORT_HANDLER.get_all_ports()[pipe.port_id].pipes[pipe.uid] = pipe
                # if pipe.uid in port.pipes:

    """
    def save_btn_cmd(self):
        self.set_vars()
        self._root.msg_to_monitor('Info: Pipe-Tool Settings wurden gespeichert..')
        self._root.msg_to_monitor('Lob: Gute Entscheidung!')
    """

    def _ok_btn_cmd(self):
        self._set_vars()
        self._root.ch_status_update()
        self._root.msg_to_monitor('Info: Pipe-Tool Settings wurden gespeichert..')
        self._root.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self._destroy_win()

    def _destroy_win(self):
        self.destroy()
        self._root.settings_win = None

    def tasker(self):
        pass

    def _new_pipe_btn_cmd(self):
        label_txt = f"{len(self.tab_list)}"
        tab = AX25PipeTab(self)
        self.tabControl.add(tab.own_tab, text=label_txt)
        self.tabControl.select(len(self.tab_list))
        self.tab_list.append(tab)

    def _new_pipe_on_conn(self):
        conn: AX25Conn = self._root.get_conn()
        if conn:
            new_pipe = AX25Pipe(
                port_id=conn.own_port.port_id,
            )
            new_pipe.connection = conn
            new_pipe.change_settings()
            # conn.pipe = new_pipe
            label_txt = f"{len(self.tab_list)}"
            tab = AX25PipeTab(self, pipe=new_pipe)
            self.tabControl.add(tab.own_tab, text=label_txt)
            self.tabControl.select(len(self.tab_list))
            self.tab_list.append(tab)

    def _del_btn_cmd(self):
        try:
            ind = self.tabControl.index('current')
        except tk.TclError:
            pass
        else:
            pipe: AX25Pipe = self.tab_list[ind].pipe
            if pipe.connection is not None:
                pipe.connection.pipe = None
            port_id = pipe.port_id
            uid = pipe.uid
            if port_id in PORT_HANDLER.get_all_ports().keys():
                if uid in PORT_HANDLER.get_all_ports()[port_id].pipes.keys():
                    del PORT_HANDLER.get_all_ports()[port_id].pipes[uid]
            del self.tab_list[ind]
            self.tabControl.forget(ind)
            self._root.ch_status_update()
