import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

from ax25.ax25InitPorts import PORT_HANDLER


class PlotWindow(tk.Toplevel):
    def __init__(self, root_cl):
        tk.Toplevel.__init__(self)
        self.wm_title("Port Statistik")
        # self.root_cl = root_cl
        self.geometry(f"800x"
                      f"600+"
                      f"{root_cl.main_win.winfo_x()}+"
                      f"{root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        ##################
        upper_frame = tk.Frame(self)
        upper_frame.pack()

        # Spinbox für Ports erstellen
        port_label = tk.Label(upper_frame, text="Port:  ")
        port_label.pack(side=tk.LEFT)
        self.port_var = tk.IntVar(self)
        self.port_var.set(0)
        self.port_spinbox = ttk.Spinbox(upper_frame,
                                        textvariable=self.port_var,
                                        width=2,
                                        from_=0,
                                        to=10,
                                        command=self._update_plots
                                        )
        self.port_spinbox.pack(side=tk.LEFT)
        tk.Label(upper_frame, text='                  ').pack(side=tk.LEFT)
        # Spinbox für Stunden erstellen

        hour_label = tk.Label(upper_frame, text="Stunden zurück:  ")
        hour_label.pack(side=tk.LEFT)
        self.hour_var = tk.IntVar(self)
        self.hour_spinbox = ttk.Spinbox(upper_frame,
                                        textvariable=self.hour_var,
                                        from_=0,
                                        to=23,
                                        width=4,
                                        command=self._update_plots,
                                        state='disabled'
                                        )

        self.hour_spinbox.pack(side=tk.LEFT)

        # Plot erstellen
        self._fig = Figure(figsize=(5, 4), dpi=100)
        self._fig.set_facecolor('xkcd:light grey')

        self._plot1 = self._fig.add_subplot(211)
        self._plot1.set_facecolor('#000000')
        # self.plot1.set_title("Plot 1")

        self._plot2 = self._fig.add_subplot(212)
        self._plot2.set_facecolor('#000000')
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

        self._update_plots()
        self._plot1.legend(['Bytes', 'I', 'UI', 'REJ', 'RR', 'RNR', 'SABM', ],
                           fontsize=8,
                           loc='right')
        self._plot2.legend(['Daten gesamt', 'Nutzdaten'],
                           fontsize=8,
                           loc='right')

        self._canvas.draw()

    def _update_plots(self):
        # self.plot2.clear()
        port_id = self.port_var.get()
        db = PORT_HANDLER.get_MH().port_statistik_DB.get(port_id, {})

        range_day = True
        now = datetime.datetime.now() - datetime.timedelta(hours=self.hour_var.get())
        date_str = now.strftime('%d/%m/%y')
        now_hour = now.hour

        # print(db)
        tmp_n_packets = []
        tmp_I_packets = []
        tmp_REJ_packets = []
        tmp_RR_packets = []
        tmp_RNR_packets = []
        tmp_UI_packets = []
        tmp_SABM_packets = []
        tmp_ALL_data = []
        tmp_DATA_data = []

        if date_str in list(db.keys()):
            # self.plot1.clf()
            las_day = date_str
            if now_hour == 0 or range_day:
                ind = list(db.keys()).index(date_str) - 1
                if ind >= 0:
                    las_day = list(db.keys())[ind]
                else:
                    las_day = ''
            day_hours = list(range(0, now_hour + 1))
            last_hours = list(range(now_hour + 1, 24))
            min_list = list(range(60))
            day_hours.reverse()
            last_hours.reverse()
            min_list.reverse()
            for h in day_hours:
                if h in db[date_str].keys():
                    for minu in min_list:
                        if (h == now.hour and minu <= now.minute) or h != now.hour:
                            tmp_n_packets.append(db[date_str][h]['N_pack'][minu])
                            tmp_I_packets.append(db[date_str][h]['I'][minu])
                            tmp_REJ_packets.append(db[date_str][h]['REJ'][minu])
                            tmp_RR_packets.append(db[date_str][h]['RR'][minu])
                            tmp_RNR_packets.append(db[date_str][h]['RNR'][minu])
                            tmp_UI_packets.append(db[date_str][h]['UI'][minu])
                            tmp_SABM_packets.append(db[date_str][h]['SABM'][minu])
                            tmp_ALL_data.append(db[date_str][h]['DATA_W_HEADER'][minu])
                            tmp_DATA_data.append(db[date_str][h]['DATA'][minu])
                        # if h == dt_now.hour and minu < dt_now.minute:
                        #     break
            for h in last_hours:
                if las_day:
                    if h in db[las_day].keys():
                        for minu in min_list:
                            tmp_n_packets.append(db[las_day][h]['N_pack'][minu])
                            tmp_I_packets.append(db[las_day][h]['I'][minu])
                            tmp_REJ_packets.append(db[las_day][h]['REJ'][minu])
                            tmp_RR_packets.append(db[las_day][h]['RR'][minu])
                            tmp_RNR_packets.append(db[las_day][h]['RNR'][minu])
                            tmp_UI_packets.append(db[las_day][h]['UI'][minu])
                            tmp_SABM_packets.append(db[las_day][h]['SABM'][minu])
                            tmp_ALL_data.append(db[las_day][h]['DATA_W_HEADER'][minu])
                            tmp_DATA_data.append(db[las_day][h]['DATA'][minu])
                    else:
                        for minu in min_list:
                            tmp_n_packets.append(0)
                            tmp_I_packets.append(0)
                            tmp_REJ_packets.append(0)
                            tmp_RR_packets.append(0)
                            tmp_RNR_packets.append(0)
                            tmp_UI_packets.append(0)
                            tmp_SABM_packets.append(0)
                            tmp_ALL_data.append(0)
                            tmp_DATA_data.append(0)
                else:
                    for minu in min_list:
                        tmp_n_packets.append(0)
                        tmp_I_packets.append(0)
                        tmp_REJ_packets.append(0)
                        tmp_RR_packets.append(0)
                        tmp_RNR_packets.append(0)
                        tmp_UI_packets.append(0)
                        tmp_SABM_packets.append(0)
                        tmp_ALL_data.append(0)
                        tmp_DATA_data.append(0)

        if tmp_n_packets:
            x_scale = []

            for i in list(range(len(tmp_n_packets))):
                x_scale.append((i / 60))
            print(x_scale)

            self._plot1.plot(x_scale, tmp_ALL_data, label='Bytes')
            self._plot1.plot(x_scale, tmp_I_packets, label='I')
            self._plot1.plot(x_scale, tmp_UI_packets, label='UI')
            self._plot1.plot(x_scale, tmp_REJ_packets, label='REJ')
            self._plot1.plot(x_scale, tmp_RR_packets, label='RR')
            self._plot1.plot(x_scale, tmp_RNR_packets, label='RNR')
            self._plot1.plot(x_scale, tmp_SABM_packets, label='SABM')

            self._plot2.plot(
            x_scale, tmp_ALL_data,
            x_scale, tmp_DATA_data, 'r--'
            )
            self._plot1.set_xlim([0, 24])  # x-Achse auf 24 Stunden begrenzen
            self._plot2.set_xlim([0, 24])

    def destroy_win(self):
        # self.root_cl.close_port_stat_win()
        self.withdraw()

    def destroy_plot(self):

        self._canvas.close_event('all')
        self._canvas.get_tk_widget().destroy()
        self._canvas.close_event()
        self._canvas = None
        plt.close()
        self._plot1 = None
        self._plot2 = None
        del self._canvas
        del self._plot1
        del self._plot2
        self.destroy()

