import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from constant import FONT
from string_tab import STR_TABLE


class AISmonitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root_cl = root_win
        self.lang = self.root_cl.language
        self.text_size = self.root_cl.text_size
        self.win_height = 700
        self.win_width = 1500
        self.style = self.root_cl.style
        self.title(STR_TABLE['aprs_mon'][self.lang])
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root_cl.main_win.winfo_x()}+"
                      f"{self.root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.resizable(False, False)
        self.lift()
        self.tmp_buffer = []
        self.ais_obj = self.root_cl.ax25_port_handler.aprs_ais
        # Frame für den linken Bereich
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Scrolled Text-Frame auf der linken Seite
        text_frame = ttk.Frame(left_frame)
        text_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Scrolled Text erstellen
        self.text_widget = ScrolledText(text_frame,
                                        background='black',
                                        foreground='green',
                                        width=85
                                        )
        self.text_widget.configure(font=(FONT, self.text_size))
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Frame für den rechten Bereich
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.autoscroll_var = tk.BooleanVar(self)
        self.autoscroll_var.set(True)
        tk.Checkbutton(right_frame,
                       variable=self.autoscroll_var,
                       text="Autoscroll  ",
                       command=self.scroll_to_end).pack(side=tk.TOP, padx=2)
        self.new_user_var = tk.BooleanVar(self)
        self.new_user_var.set(False)
        tk.Checkbutton(right_frame,
                       variable=self.new_user_var,
                       text="UserDB      ",
                       command=self.chk_new_user
                       ).pack(side=tk.TOP, padx=2)
        self.call_filter = tk.BooleanVar(self)
        self.call_filter.set(False)
        tk.Checkbutton(right_frame,
                       variable=self.call_filter,
                       text="Call-Filter  ",
                       command=self.chk_call_filter
                       ).pack(side=tk.TOP, padx=2)

        tk.Label(right_frame, text="Call-Filter:").pack(side=tk.TOP, padx=2)
        self.call_filter_calls_var = tk.StringVar(self)
        tk.Entry(right_frame,
                 textvariable=self.call_filter_calls_var,
                 width=20
                 ).pack(side=tk.TOP, padx=2)

        tk.Button(right_frame,
                  text=STR_TABLE['delete'][self.lang],
                  command=self.del_buffer
                  ).pack(side=tk.TOP, padx=2)

        # Konfigurieren des Grid-Layouts
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        # Text-Widget an die Größe des Hauptfensters anpassen
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        if self.ais_obj is not None:
            self.new_user_var.set(self.ais_obj.add_new_user)
        self.bind('<Control-plus>', lambda event: self.increase_textsize())
        self.bind('<Control-minus>', lambda event: self.decrease_textsize())

        self.ais_aprs_stations = {}
        self.ais_aprs_stat_calls = []
        if self.ais_obj is not None:
            self.ais_aprs_stations = self.ais_obj.ais_aprs_stations
            for port_id in self.ais_aprs_stations.keys():
                if self.ais_aprs_stations[port_id].aprs_parm_call:
                    self.ais_aprs_stat_calls.append(
                        self.ais_aprs_stations[port_id].aprs_parm_call
                    )

        root_win.aprs_mon_win = self
        self.tasker()

    def tasker(self):
        if self.ais_obj is not None:
            tr = False
            while self.ais_obj.ais_rx_buff:
                pack = self.ais_obj.ais_rx_buff[0]
                self.ais_obj.ais_rx_buff = self.ais_obj.ais_rx_buff[1:]
                self.tmp_buffer.append(pack)
                if self.call_filter.get():
                    if pack[1]['from'] in self.ais_aprs_stat_calls:
                        tr = True
                        tmp = format_aprs_f_aprs_mon(pack, self.ais_obj.ais_loc, add_new_user=self.ais_obj.add_new_user)
                        self.text_widget.insert(tk.END, tmp)
                else:
                    tr = True
                    tmp = format_aprs_f_aprs_mon(pack, self.ais_obj.ais_loc, add_new_user=self.ais_obj.add_new_user)
                    self.text_widget.insert(tk.END, tmp)
            if tr:
                self.scroll_to_end()

    def increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        self.text_widget.configure(font=(FONT, self.text_size))

    def decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self.text_widget.configure(font=(FONT, self.text_size))

    def chk_call_filter(self):
        self.ais_aprs_stations = {}
        self.ais_aprs_stat_calls = []
        if self.ais_obj is not None:
            self.ais_aprs_stations = self.ais_obj.ais_aprs_stations
            for port_id in self.ais_aprs_stations.keys():
                if self.ais_aprs_stations[port_id].aprs_parm_call:
                    self.ais_aprs_stat_calls.append(
                        self.ais_aprs_stations[port_id].aprs_parm_call
                    )
        calls = self.call_filter_calls_var.get()
        calls = calls.split(' ')
        tmp = []
        for el in list(calls):
            if el:
                tmp.append(el.upper())
        calls = tmp
        self.ais_aprs_stat_calls = self.ais_aprs_stat_calls + calls

    def chk_new_user(self):
        if self.ais_obj is not None:
            self.ais_obj.add_new_user = self.new_user_var.get()

    def del_buffer(self):
        self.tmp_buffer = []
        if self.ais_obj is not None:
            self.ais_obj.ais_rx_buff = []
        self.text_widget.delete(0.0, tk.END)

    def scroll_to_end(self):
        if self.autoscroll_var.get():
            self.text_widget.see(tk.END)

    def destroy_win(self):
        # self.tasker = lambda: 0
        self.root_cl.aprs_mon_win = None
        self.ais_obj.ais_rx_buff = self.tmp_buffer + self.ais_obj.ais_rx_buff
        self.destroy()

