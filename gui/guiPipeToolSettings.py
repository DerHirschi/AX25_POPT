import tkinter as tk
from tkinter import ttk

from ax25.ax25dec_enc import PIDByte
from string_tab import STR_TABLE


class AX25PipeTab:
    def __init__(self, root_win, tabclt: ttk.Notebook):
        self.tab_clt = tabclt
        self.root_win = root_win
        self.lang = root_win.lang
        self.style = root_win.style
        self.own_tab = ttk.Frame(self.tab_clt)
        #########################################################
        # Address
        _x = 10
        _y = 10
        self.to_add_var = tk.StringVar(self.own_tab)
        tk.Label(self.own_tab, text=f"{STR_TABLE['to'][self.lang]}:").place(x=_x, y=_y)
        self.to_add_ent = tk.Entry(self.own_tab, textvariable=self.to_add_var)
        self.to_add_ent.place(x=_x + 40, y=_y)

        # CMD/RPT
        _x = 10
        _y = 80
        self.cmd_var = tk.BooleanVar(self.own_tab)
        self.cmd_ent = tk.Checkbutton(self.own_tab,
                                      variable=self.cmd_var,
                                      text='CMD/RPT')
        self.cmd_ent.place(x=_x, y=_y)

        # Poll
        _x = 10
        _y = 105
        self.poll_var = tk.BooleanVar(self.own_tab)
        self.poll_ent = tk.Checkbutton(self.own_tab,
                                       variable=self.poll_var,
                                       text='Poll')
        self.poll_ent.place(x=_x, y=_y)

        # Port
        _x = 40
        _y = 140
        tk.Label(self.own_tab, text=f"{STR_TABLE['port'][self.lang]}:").place(x=_x, y=_y)
        self.port_var = tk.StringVar(self.own_tab)
        self.port_var.set('0')
        _vals = ['0']
        if self.root_win.root.ax25_port_handler.ax25_ports.keys():
            _vals = [str(x) for x in list(self.root_win.root.ax25_port_handler.ax25_ports.keys())]
        self.port_ent = tk.ttk.Combobox(self.own_tab,
                                        width=4,
                                        textvariable=self.port_var,
                                        values=_vals,
                                        )
        self.port_ent.place(x=_x + 50, y=_y)
        # self.mon_port_ent.bind("<<ComboboxSelected>>", self.chk_mon_port)
        # Calls
        _x = 40
        _y = 175
        self.call_var = tk.StringVar(self.own_tab)
        _vals = []
        # if self.main_win.ax25_port_handler.ax25_ports.keys():
        #     _vals = [str(x) for x in list(self.main_win.ax25_port_handler.ax25_ports.keys())]
        port_id = int(self.port_var.get())
        if port_id in self.root_win.root.ax25_port_handler.ax25_ports.keys():
            _vals = self.root_win.root.ax25_port_handler.ax25_ports[port_id].my_stations
        if _vals:
            self.call_var.set(_vals[0])
        self.call_ent = tk.ttk.Combobox(self.own_tab,
                                        width=9,
                                        textvariable=self.call_var,
                                        values=_vals,
                                        )
        self.call_ent.place(x=_x, y=_y)

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
                                       width=20,
                                       values=_vals,
                                       textvariable=self.pid_var)
        self.pid_var.set(_vals[0])
        self.pid_ent.place(x=_x + 40, y=_y)
        # Loop Timer
        _x = 10
        _y = self.root_win.win_height - 255 - 80    # iam lazy
        tk.Label(self.own_tab, text='TX-File Check Timer (sek/sec):').place(x=_x, y=_y)
        self.loop_timer_var = tk.StringVar(self.own_tab)
        self.loop_timer_var.set('10')
        self.loop_timer = tk.Spinbox(self.own_tab,
                                     from_=1,
                                     to=60,
                                     increment=1,
                                     width=2,
                                     textvariable=self.loop_timer_var,
                                     # command=self.set_max_frame,
                                     # state='disabled'
                                     )
        self.loop_timer.place(x=_x + 270, y=_y)

        #################
        # TX FILE
        _x = 10
        _y = self.root_win.win_height - 220 - 80    # iam lazy
        tk.Label(self.own_tab, text=f"{STR_TABLE['tx_file'][self.lang]}:").place(x=_x, y=_y)
        self.tx_filename_var = tk.StringVar(self.own_tab)
        self.tx_filename = tk.Entry(self.own_tab, textvariable=self.tx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self.tx_filename.place(x=_x + 140, y=_y)
        tk.Button(self.own_tab,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  # command=self.select_files
                  ).place(x=_x + 710, y=_y - 2)
        #################
        # RX FILE
        _x = 10
        _y = self.root_win.win_height - 180 - 80    # iam lazy
        tk.Label(self.own_tab, text=f"{STR_TABLE['rx_file'][self.lang]}:").place(x=_x, y=_y)
        self.rx_filename_var = tk.StringVar(self.own_tab)
        self.rx_filename = tk.Entry(self.own_tab, textvariable=self.rx_filename_var, width=50)
        # self.tx_filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        self.rx_filename.place(x=_x + 140, y=_y)
        tk.Button(self.own_tab,
                  text=f"{STR_TABLE['file_1'][self.lang]}",
                  # command=self.select_files
                  ).place(x=_x + 710, y=_y - 2)


class PipeToolSettings(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self)
        self.root = root
        self.lang = self.root.language
        root.settings_win = self
        self.win_height = 600
        self.win_width = 860
        self.style = root.style
        self.title(STR_TABLE['pipetool_settings'][self.lang])
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root.main_win.winfo_x()}+"
                      f"{self.root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        self.lift()

        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text=STR_TABLE['OK'][self.lang],
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)

        save_bt = tk.Button(self,
                            text=STR_TABLE['save'][self.lang],
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)

        cancel_bt = tk.Button(self,
                              text=STR_TABLE['cancel'][self.lang],
                              height=1,
                              width=8,
                              command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)
        ####################################
        # New Station, Del Station Buttons
        tk.Button(self,
                  text=STR_TABLE['new_pipe'][self.lang],
                  height=1,
                  width=10,
                  command=self.new_pipe_btn_cmd). \
            place(x=20, y=self.win_height - 590)
        tk.Button(self,
                  text=STR_TABLE['delete'][self.lang],
                  bg="red3",
                  height=1,
                  width=10,
                  command=self.del_btn_cmd). \
            place(x=self.win_width - 141, y=self.win_height - 590)

        self.tabControl = ttk.Notebook(self, height=self.win_height - 140, width=self.win_width - 40)
        self.tabControl.place(x=20, y=self.win_height - 550)
        self.tab_list: [ttk.Frame] = []

    def save_btn_cmd(self):
        self.root.msg_to_monitor('Info: Pipe-Tool Settings wurden gespeichert..')
        self.root.msg_to_monitor('Lob: Gute Entscheidung!')

    def ok_btn_cmd(self):
        self.root.msg_to_monitor('Info: Pipe-Tool Settings wurden gespeichert..')
        self.root.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.root.settings_win = None

    def tasker(self):
        pass

    def new_pipe_btn_cmd(self):
        label_txt = f"{len(self.tab_list)}"
        tab = AX25PipeTab(self, self.tabControl)
        self.tabControl.add(tab.own_tab, text=label_txt)
        self.tabControl.select(len(self.tab_list))
        self.tab_list.append(tab)

    def del_btn_cmd(self):
        try:
            ind = self.tabControl.index('current')
        except tk.TclError:
            pass
        else:
            del self.tab_list[ind]
            self.tabControl.forget(ind)
