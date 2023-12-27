import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ax25.ax25InitPorts import PORT_HANDLER
from fnc.str_fnc import convert_str_to_datetime
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt


class PlotWindow(tk.Toplevel):
    def __init__(self, root_cl):
        tk.Toplevel.__init__(self)
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
            pass
        ##############################
        self._root_win = root_cl
        self._db = PORT_HANDLER.get_MH()
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

        # Plot erstellen
        self._fig, self._plot1 = plt.subplots()
        self._fig.set_facecolor('xkcd:light grey')
        self._plot1.set_facecolor('#000000')
        # self.plot1.set_title("Plot 1")
        """
        self._plot2 = self._plot1.twinx()
        self._plot2.set_facecolor('#000000')
        self._plot2.yaxis.tick_right()
        """
        # self.plot2.set_title("Plot 2")
        self._fig.subplots_adjust(top=0.98, bottom=0.05, left=0.05, right=0.98, hspace=0.10)

        # Canvas für den Plot erstellen und in das Tkinter-Fenster einbetten
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die Plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, self)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, fill=tk.X)

        self._change_xlim()
        self._plot1.legend(
                           fontsize=8,
                           )
        """
        self._plot2.legend(['Daten gesamt', 'Nutzdaten'],
                           fontsize=8,
                           loc='right')
        """
        self._root_win.port_stat_win = self
        # self._canvas.draw()

    def _update_plots(self):
        port_id = int(self._port_var.get())
        db_data = self._db.PortStat_get_data_by_port(port_id)
        if not db_data:
            return

        # tmp_n_packets = []
        tmp_I_packets = []
        tmp_REJ_packets = []
        # tmp_SREJ_packets = []
        tmp_RR_packets = []
        tmp_RNR_packets = []
        tmp_UI_packets = []
        # tmp_UA_packets = []
        # tmp_DM_packets = []
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
            # print(f"DIF sec: {min_dif.total_seconds()}")
            min_dif = int(min_dif.total_seconds() / 60) - 1
            # print(f"DIF ceil: {min_dif}")
            last_ts = timestamt_dt
            null_list = list(range(min_dif))
            # print(null_list)
            null_list.reverse()
            for minu in null_list:
                tmp_I_packets.append(0)
                tmp_REJ_packets.append(0)
                # tmp_SREJ_packets.append(0)
                tmp_RR_packets.append(0)
                tmp_RNR_packets.append(0)
                tmp_UI_packets.append(0)
                # tmp_UA_packets.append(0)
                # tmp_DM_packets.append(0)
                tmp_SABM_packets.append(0)
                tmp_DISC_packets.append(0)
                tmp_FRMR_packets.append(0)
                dif = ts_now - timestamt_dt
                dif_sec = dif.total_seconds() + (60 * (minu + 1))
                # print(f"null: {round(dif_sec)}")
                x_scale.append(dif_sec / 3600)

            tmp_I_packets.append(data[4])
            tmp_SABM_packets.append(data[5])
            # tmp_DM_packets.append(data[6])
            tmp_DISC_packets.append(data[7])
            tmp_REJ_packets.append(data[8])
            # tmp_SREJ_packets.append(data[9])
            tmp_RR_packets.append(data[10])
            tmp_RNR_packets.append(data[11])
            # tmp_UA_packets.append(data[12])
            tmp_UI_packets.append(data[13])
            tmp_FRMR_packets.append(data[14])
            dif = ts_now - timestamt_dt
            # print(f"----: {round(round(dif.total_seconds()))}")
            x_scale.append(dif.total_seconds() / 3600)

        # print(x_scale)
        self._plot1.plot(x_scale, tmp_I_packets, label='I')
        self._plot1.plot(x_scale, tmp_UI_packets, label='UI')
        self._plot1.plot(x_scale, tmp_REJ_packets, label='REJ')
        self._plot1.plot(x_scale, tmp_RR_packets, label='RR')
        self._plot1.plot(x_scale, tmp_RNR_packets, label='RNR')
        self._plot1.plot(x_scale, tmp_SABM_packets, label='SABM')
        self._plot1.plot(x_scale, tmp_DISC_packets, label='DISC')
        self._plot1.plot(x_scale, tmp_FRMR_packets, label='FRMR')

    def _change_xlim(self, event=None):
        self._plot1.clear()
        self._update_plots()
        try:
            days = int(self._hour_var.get())
        except ValueError:
            return
        if not days:
            return
        self._plot1.legend(
            fontsize=8,
        )
        lim = 24 * days
        self._plot1.set_xlim([lim, 0])  # x-Achse auf 24 Stunden begrenzen
        # self._plot2.set_xlim([hours, 0])  # x-Achse auf 24 Stunden begrenzen
        self._canvas.draw()

    def destroy_plot(self):
        plt.close()
        self._canvas.get_tk_widget().destroy()
        self._root_win.port_stat_win = None
        self.destroy()

