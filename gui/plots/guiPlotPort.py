import tkinter as tk
from tkinter import ttk, Menu, messagebox
from datetime import datetime
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
from fnc.str_fnc import convert_str_to_datetime
# from matplotlib.backends._backend_tk import NavigationToolbar2Tk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from gui import (NavigationToolbar2Tk, FigureCanvasTkAgg)
# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
#import matplotlib

#matplotlib.use('Agg')
#from matplotlib import pyplot as plt
from gui import plt


class PlotWindow(tk.Toplevel):
    def __init__(self, root_cl):
        tk.Toplevel.__init__(self, master=root_cl.main_win)
        self.wm_title("Port Statistik")
        # self.root_cl = root_cl
        self.geometry(f"800x"
                      f"600+"
                      f"{root_cl.main_win.winfo_x()}+"
                      f"{root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_plot)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        ##############################
        self._root_win = root_cl
        self._lang = POPT_CFG.get_guiCFG_language()
        self._mh = PORT_HANDLER.get_MH()
        ##################
        upper_frame = tk.Frame(self)
        upper_frame.pack()

        # Spinbox für Ports erstellen
        port_label = tk.Label(upper_frame, text="Port:  ")
        port_label.pack(side=tk.LEFT)
        self._port_var = tk.IntVar(self)
        self._port_var.set(0)
        self._port_spinbox = ttk.Spinbox(upper_frame,
                                         textvariable=self._port_var,
                                         width=2,
                                         from_=0,
                                         to=10,
                                         command=self._change_xlim,
                                         )
        self._port_spinbox.pack(side=tk.LEFT)
        tk.Label(upper_frame, text='                  ').pack(side=tk.LEFT)
        # Spinbox für Stunden erstellen

        hour_label = tk.Label(upper_frame, text='X-Limit (Days): ')
        hour_label.pack(side=tk.LEFT)
        self._hour_var = tk.IntVar(self, value=1)
        self._hour_spinbox = ttk.Spinbox(upper_frame,
                                         textvariable=self._hour_var,
                                         from_=1,
                                         to=3650,
                                         width=5,
                                         command=self._change_xlim,
                                         )

        self._hour_spinbox.pack(side=tk.LEFT)

        type_label = tk.Label(upper_frame, text='     Plot-Type: ')
        type_label.pack(side=tk.LEFT)
        self._type_var = tk.StringVar(self)
        self._plot_type_opt = ['Byte/Packet', 'Number/Packet']
        self._type_var.set(self._plot_type_opt[0])
        type_optMenu = tk.OptionMenu(upper_frame,
                                     self._type_var,
                                     *self._plot_type_opt,
                                     command=self._change_xlim,
                                     )

        type_optMenu.pack(side=tk.LEFT)

        plot_frame = tk.Frame(self)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Plot erstellen
        self._fig, self._plot1 = plt.subplots()
        self._fig.set_facecolor('xkcd:light grey')
        self._plot1.set_facecolor('#000000')

        self._fig.subplots_adjust(top=0.99, bottom=0.052, left=0.051, right=0.995, hspace=0.10)

        # Canvas für den Plot erstellen und in das Tkinter-Fenster einbetten
        self._canvas = FigureCanvasTkAgg(self._fig, master=plot_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, plot_frame)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, fill=tk.X)

        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._ui_chk_var = tk.BooleanVar(self, value=True)
        self._ui_chk_var = tk.BooleanVar(self, value=True)
        self._ui_chk_var = tk.BooleanVar(self, value=True)
        self._i_chk_var = tk.BooleanVar(self, value=True)
        self._rr_chk_var = tk.BooleanVar(self, value=True)
        self._rnr_chk_var = tk.BooleanVar(self, value=True)
        self._rej_chk_var = tk.BooleanVar(self, value=True)
        self._srej_chk_var = tk.BooleanVar(self, value=True)
        self._frmr_chk_var = tk.BooleanVar(self, value=True)
        self._sabm_chk_var = tk.BooleanVar(self, value=True)
        self._ua_chk_var = tk.BooleanVar(self, value=True)
        self._disc_chk_var = tk.BooleanVar(self, value=True)
        self._dm_chk_var = tk.BooleanVar(self, value=True)
        self._total_chk_var = tk.BooleanVar(self, value=True)
        self._payload_chk_var = tk.BooleanVar(self, value=True)

        self._init_chk_frame(right_frame)
        self._init_menubar()

        self._change_xlim()
        self._root_win.port_stat_win = self

    def _init_chk_frame(self, root_frame):
        tk.Checkbutton(root_frame,
                       variable=self._ui_chk_var,
                       text='UI',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._i_chk_var,
                       text='I',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._rr_chk_var,
                       text='RR',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._rnr_chk_var,
                       text='RNR',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._rej_chk_var,
                       text='REJ',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._srej_chk_var,
                       text='SREJ',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._frmr_chk_var,
                       text='FRMR',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._sabm_chk_var,
                       text='SABM',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._ua_chk_var,
                       text='UA',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._disc_chk_var,
                       text='DISC',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._dm_chk_var,
                       text='DM',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._total_chk_var,
                       text='TOTAL',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')
        tk.Checkbutton(root_frame,
                       variable=self._payload_chk_var,
                       text='PAYLOAD',
                       command=self._change_xlim,).pack(padx=15, pady=5, anchor='w')

    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=STR_TABLE['del_all'][self._lang], command=self._reset_PortStat)
        menubar.add_cascade(label=STR_TABLE['data'][self._lang], menu=MenuVerb, underline=0)

    def _update_plots_bytes(self):
        port_id = int(self._port_var.get())
        db_data = self._mh.PortStat_get_data_by_port(port_id)
        if not db_data:
            return

        # tmp_n_packets = []
        tmp_I_packets = []
        tmp_REJ_packets = []
        tmp_SREJ_packets = []
        tmp_RR_packets = []
        tmp_RNR_packets = []
        tmp_UI_packets = []
        tmp_UA_packets = []
        tmp_DM_packets = []
        tmp_SABM_packets = []
        tmp_DISC_packets = []
        tmp_FRMR_packets = []
        tmp_ALL_data = []
        tmp_DATA_data = []
        x_scale = []
        ts_now = datetime.now()
        # ts_now.replace(second=30, microsecond=0)
        # print(db_data)
        last_ts = None
        for data in db_data:
            timestamt_dt = data[1]
            timestamt_dt = convert_str_to_datetime(timestamt_dt)
            timestamt_dt.replace(second=0, microsecond=0)
            if last_ts is None:
                last_ts = timestamt_dt
            min_dif = timestamt_dt - last_ts
            min_dif = int(min_dif.total_seconds() / 60) - 1
            # TODO : min_dif = int(min_dif.total_seconds() / 60) #!!!!# - 1
            last_ts = timestamt_dt
            null_list = list(range(min_dif))
            null_list.reverse()
            for minu in null_list:
                tmp_ALL_data.append(0)
                tmp_DATA_data.append(0)
                tmp_I_packets.append(0)
                tmp_REJ_packets.append(0)
                tmp_SREJ_packets.append(0)
                tmp_RR_packets.append(0)
                tmp_RNR_packets.append(0)
                tmp_UI_packets.append(0)
                tmp_UA_packets.append(0)
                tmp_DM_packets.append(0)
                tmp_SABM_packets.append(0)
                tmp_DISC_packets.append(0)
                tmp_FRMR_packets.append(0)
                dif = ts_now - timestamt_dt
                dif_sec = dif.total_seconds() + (60 * (minu + 1))
                # print(f"null: {round(dif_sec)}")
                x_scale.append(dif_sec / 3600)

            tmp_ALL_data.append(data[26])
            tmp_DATA_data.append(data[27])
            tmp_I_packets.append(data[4])
            tmp_SABM_packets.append(data[5])
            tmp_DM_packets.append(data[6])
            tmp_DISC_packets.append(data[7])
            tmp_REJ_packets.append(data[8])
            tmp_SREJ_packets.append(data[9])
            tmp_RR_packets.append(data[10])
            tmp_RNR_packets.append(data[11])
            tmp_UA_packets.append(data[12])
            tmp_UI_packets.append(data[13])
            tmp_FRMR_packets.append(data[14])
            dif = ts_now - timestamt_dt
            # print(f"----: {round(round(dif.total_seconds()))}")
            x_scale.append(dif.total_seconds() / 3600)

        # print(x_scale)
        if self._i_chk_var.get():
            self._plot1.plot(x_scale, tmp_I_packets, label='I')
        if self._ui_chk_var.get():
            self._plot1.plot(x_scale, tmp_UI_packets, label='UI')
        if self._rej_chk_var.get():
            self._plot1.plot(x_scale, tmp_REJ_packets, label='REJ')
        if self._srej_chk_var.get():
            self._plot1.plot(x_scale, tmp_SREJ_packets, label='SREJ')
        if self._rr_chk_var.get():
            self._plot1.plot(x_scale, tmp_RR_packets, label='RR')
        if self._rnr_chk_var.get():
            self._plot1.plot(x_scale, tmp_RNR_packets, label='RNR')
        if self._sabm_chk_var.get():
            self._plot1.plot(x_scale, tmp_SABM_packets, label='SABM')
        if self._ua_chk_var.get():
            self._plot1.plot(x_scale, tmp_UA_packets, label='UA')
        if self._disc_chk_var.get():
            self._plot1.plot(x_scale, tmp_DISC_packets, label='DISC')
        if self._dm_chk_var.get():
            self._plot1.plot(x_scale, tmp_DM_packets, label='DM')
        if self._frmr_chk_var.get():
            self._plot1.plot(x_scale, tmp_FRMR_packets, label='FRMR')
        if self._total_chk_var.get():
            self._plot1.plot(x_scale, tmp_ALL_data, label='Total')
        if self._payload_chk_var.get():
            self._plot1.plot(x_scale, tmp_DATA_data, label='Payload')
        # self._plot1.set_xlabel(STR_TABLE['hours'][self._lang])
        # self._plot1.set_ylabel('Bytes')
        # self._plot1.set_title("Bytes/h")

    def _update_plots_n(self):
        port_id = int(self._port_var.get())
        db_data = self._mh.PortStat_get_data_by_port(port_id)
        if not db_data:
            return

        tmp_n_packets = []
        tmp_I_packets = []
        tmp_REJ_packets = []
        tmp_SREJ_packets = []
        tmp_RR_packets = []
        tmp_RNR_packets = []
        tmp_UI_packets = []
        tmp_UA_packets = []
        tmp_DM_packets = []
        tmp_SABM_packets = []
        tmp_DISC_packets = []
        tmp_FRMR_packets = []
        # tmp_ALL_data = []
        # tmp_DATA_data = []
        x_scale = []
        ts_now = datetime.now()
        # ts_now.replace(second=30, microsecond=0)
        # print(db_data)
        last_ts = None
        for data in db_data:
            timestamt_dt = data[1]
            timestamt_dt = convert_str_to_datetime(timestamt_dt)
            timestamt_dt.replace(second=0, microsecond=0)
            if last_ts is None:
                last_ts = timestamt_dt
            min_dif = timestamt_dt - last_ts
            min_dif = int(min_dif.total_seconds() / 60) - 1
            # TODO : min_dif = int(min_dif.total_seconds() / 60) #!!!!# - 1
            last_ts = timestamt_dt
            null_list = list(range(min_dif))
            null_list.reverse()
            for minu in null_list:
                tmp_n_packets.append(0)
                tmp_I_packets.append(0)
                tmp_REJ_packets.append(0)
                tmp_SREJ_packets.append(0)
                tmp_RR_packets.append(0)
                tmp_RNR_packets.append(0)
                tmp_UI_packets.append(0)
                tmp_UA_packets.append(0)
                tmp_DM_packets.append(0)
                tmp_SABM_packets.append(0)
                tmp_DISC_packets.append(0)
                tmp_FRMR_packets.append(0)
                dif = ts_now - timestamt_dt
                dif_sec = dif.total_seconds() + (60 * (minu + 1))
                x_scale.append(dif_sec / 3600)

            tmp_n_packets.append(data[3])
            tmp_I_packets.append(data[15])
            tmp_SABM_packets.append(data[16])
            tmp_DM_packets.append(data[6])
            tmp_DISC_packets.append(data[18])
            tmp_REJ_packets.append(data[19])
            tmp_SREJ_packets.append(data[20])
            tmp_RR_packets.append(data[21])
            tmp_RNR_packets.append(data[22])
            tmp_UA_packets.append(data[12])
            tmp_UI_packets.append(data[24])
            tmp_FRMR_packets.append(data[25])
            dif = ts_now - timestamt_dt
            x_scale.append(dif.total_seconds() / 3600)

        if self._i_chk_var.get():
            self._plot1.plot(x_scale, tmp_I_packets, label='I')
        if self._ui_chk_var.get():
            self._plot1.plot(x_scale, tmp_UI_packets, label='UI')
        if self._rej_chk_var.get():
            self._plot1.plot(x_scale, tmp_REJ_packets, label='REJ')
        if self._srej_chk_var.get():
            self._plot1.plot(x_scale, tmp_SREJ_packets, label='SREJ')
        if self._rr_chk_var.get():
            self._plot1.plot(x_scale, tmp_RR_packets, label='RR')
        if self._rnr_chk_var.get():
            self._plot1.plot(x_scale, tmp_RNR_packets, label='RNR')
        if self._sabm_chk_var.get():
            self._plot1.plot(x_scale, tmp_SABM_packets, label='SABM')
        if self._ua_chk_var.get():
            self._plot1.plot(x_scale, tmp_UA_packets, label='UA')
        if self._disc_chk_var.get():
            self._plot1.plot(x_scale, tmp_DISC_packets, label='DISC')
        if self._dm_chk_var.get():
            self._plot1.plot(x_scale, tmp_DM_packets, label='DM')
        if self._frmr_chk_var.get():
            self._plot1.plot(x_scale, tmp_FRMR_packets, label='FRMR')
        if self._total_chk_var.get():
            self._plot1.plot(x_scale, tmp_n_packets, label='Total')


        # self._plot1.set_xlabel(STR_TABLE['hours'][self._lang])
        # self._plot1.set_ylabel(STR_TABLE['number'][self._lang])
        # self._plot1.set_title("N/h")

    def _change_xlim(self, event=None):
        try:
            days = int(self._hour_var.get())
        except ValueError:
            return
        if not days:
            return
        if not self._mh:
            return
        self._plot1.clear()
        plot_type = self._type_var.get()
        if self._plot_type_opt[0] == plot_type:
            self._update_plots_bytes()
        elif self._plot_type_opt[1] == plot_type:
            self._update_plots_n()
        else:
            return

        self._plot1.legend(
            fontsize=8,
        )
        lim = 24 * days
        self._plot1.set_xlim([lim, 0])  # x-Achse auf 24 Stunden begrenzen
        # self._plot2.set_xlim([hours, 0])  # x-Achse auf 24 Stunden begrenzen
        self._canvas.draw()

    def _reset_PortStat(self, event=None):
        if not self._mh:
            return
        # self.lower()
        if messagebox.askokcancel(title=STR_TABLE.get('msg_box_delete_data', ('', '', ''))[self._lang],
                                  message=STR_TABLE.get('msg_box_delete_data_msg', ('', '', ''))[self._lang], parent=self):
            self._mh.PortStat_reset()
            self._change_xlim()
        # self.lift()

    def destroy_plot(self):
        self._plot1.clear()
        self._fig.clear()
        plt.close()
        self._canvas.get_tk_widget().destroy()
        self._root_win.port_stat_win = None
        self.destroy()
