import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from ax25.ax25InitPorts import PORT_HANDLER
from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from constant import FONT
from string_tab import STR_TABLE


class AISmonitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_cl = root_win
        self._lang = self._root_cl.language
        self._text_size = int(self._root_cl.text_size)
        self._win_height = 700
        self._win_width = 1500
        # self.style = self._root_cl.style
        self.title(STR_TABLE['aprs_mon'][self._lang])
        self.geometry(f"{self._win_width}x"
                      f"{self._win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        # self.resizable(False, False)
        self.lift()
        self._ais_obj = PORT_HANDLER.get_aprs_ais()

        # Frame für den linken Bereich
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Scrolled Text-Frame auf der linken Seite
        text_frame = ttk.Frame(left_frame)
        text_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Scrolled Text erstellen
        self._text_widget = ScrolledText(text_frame,
                                         background='black',
                                         foreground='green',
                                         width=85
                                         )
        self._text_widget.configure(font=(FONT, self._text_size))
        self._text_widget.pack(fill=tk.BOTH, expand=True)

        # Frame für den rechten Bereich
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self._autoscroll_var = tk.BooleanVar(self)
        self._autoscroll_var.set(True)
        tk.Checkbutton(right_frame,
                       variable=self._autoscroll_var,
                       text="Autoscroll  ",
                       command=self._scroll_to_end).pack(side=tk.TOP, padx=2)
        self._new_user_var = tk.BooleanVar(self)
        self._new_user_var.set(False)
        tk.Checkbutton(right_frame,
                       variable=self._new_user_var,
                       text="UserDB      ",
                       command=self._chk_new_user
                       ).pack(side=tk.TOP, padx=2)
        self._call_filter = tk.BooleanVar(self)
        self._call_filter.set(False)
        tk.Checkbutton(right_frame,
                       variable=self._call_filter,
                       text="Call-Filter  ",
                       command=self._chk_call_filter
                       ).pack(side=tk.TOP, padx=2)

        tk.Label(right_frame, text="Call-Filter:").pack(side=tk.TOP, padx=2)
        self._call_filter_calls_var = tk.StringVar(self)
        tk.Entry(right_frame,
                 textvariable=self._call_filter_calls_var,
                 width=20
                 ).pack(side=tk.TOP, padx=2)

        tk.Button(right_frame,
                  text=STR_TABLE['delete'][self._lang],
                  command=self._del_buffer
                  ).pack(side=tk.TOP, padx=2)

        # Konfigurieren des Grid-Layouts
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)

        # Text-Widget an die Größe des Hauptfensters anpassen
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        if self._ais_obj is not None:
            self._new_user_var.set(self._ais_obj.add_new_user)
        self.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())

        self._ais_aprs_stations = {}
        self._ais_aprs_stat_calls = []
        if self._ais_obj is not None:
            self._ais_aprs_stations = self._ais_obj.ais_aprs_stations
            self._ais_aprs_stat_calls.append(self._ais_obj.ais_call)
            self._ais_obj.ais_mon_gui = self
            """
            for port_id in self._ais_aprs_stations.keys():
                if self._ais_aprs_stations[port_id].aprs_parm_call:
                    self._ais_aprs_stat_calls.append(
                        self._ais_aprs_stations[port_id].aprs_parm_call
                    )
            """
        root_win.aprs_mon_win = self
        self._init_ais_mon()

    def _init_ais_mon(self):
        if self._ais_obj is not None:
            _tr = False
            for _el in list(self._ais_obj.ais_rx_buff):
                if _el:
                    if self._call_filter.get():
                        if _el[1]['from'] in self._ais_aprs_stat_calls:
                            _tr = True
                            _tmp = format_aprs_f_aprs_mon(_el, self._ais_obj.ais_loc,
                                                          add_new_user=self._ais_obj.add_new_user)
                            self._text_widget.insert(tk.END, _tmp)
                    else:
                        _tr = True
                        _tmp = format_aprs_f_aprs_mon(_el, self._ais_obj.ais_loc,
                                                      add_new_user=self._ais_obj.add_new_user)
                        self._text_widget.insert(tk.END, _tmp)
            if _tr:
                self._scroll_to_end()

    def pack_to_mon(self, date_time, pack):
        _tr = False
        if self._call_filter.get():
            if pack['from'] in self._ais_aprs_stat_calls:
                _tr = True
                tmp = format_aprs_f_aprs_mon((date_time, pack), self._ais_obj.ais_loc,
                                             add_new_user=self._ais_obj.add_new_user)
                self._text_widget.insert(tk.END, tmp)
        else:
            _tr = True
            tmp = format_aprs_f_aprs_mon((date_time, pack), self._ais_obj.ais_loc,
                                         add_new_user=self._ais_obj.add_new_user)
            self._text_widget.insert(tk.END, tmp)

        if _tr:
            self._scroll_to_end()

    def _increase_textsize(self):
        self._text_size += 1
        self._text_size = max(self._text_size, 3)
        self._text_widget.configure(font=(FONT, self._text_size))

    def _decrease_textsize(self):
        self._text_size -= 1
        self._text_size = max(self._text_size, 3)
        self._text_widget.configure(font=(FONT, self._text_size))

    def _chk_call_filter(self):
        self._ais_aprs_stations = {}
        self._ais_aprs_stat_calls = []
        if self._ais_obj is not None:
            self._ais_aprs_stations = self._ais_obj.ais_aprs_stations
            self._ais_aprs_stat_calls.append(self._ais_obj.ais_call)
            """
            for port_id in self._ais_aprs_stations.keys():
                if self._ais_aprs_stations[port_id].aprs_parm_call:
                    self._ais_aprs_stat_calls.append(
                        self._ais_aprs_stations[port_id].aprs_parm_call
                    )
            """
        calls = self._call_filter_calls_var.get()
        calls = calls.split(' ')
        tmp = []
        for el in list(calls):
            if el:
                tmp.append(el.upper())
        calls = tmp
        self._ais_aprs_stat_calls = self._ais_aprs_stat_calls + calls

    def _chk_new_user(self):
        if self._ais_obj is not None:
            self._ais_obj.add_new_user = self._new_user_var.get()

    def _del_buffer(self):
        if self._ais_obj is not None:
            self._ais_obj.del_ais_rx_buff()
        self._text_widget.delete(0.0, tk.END)

    def _scroll_to_end(self):
        if self._autoscroll_var.get():
            self._text_widget.see(tk.END)

    def _destroy_win(self):
        # self.tasker = lambda: 0
        del self._ais_obj.ais_mon_gui
        self._ais_obj.ais_mon_gui = None
        del self._ais_obj
        self._ais_obj = None
        del self._root_cl.aprs_mon_win
        self._root_cl.aprs_mon_win = None
        self._text_widget.delete(0.0, tk.END)
        # self._text_widget.quit()
        self._text_widget.destroy()
        del self._text_widget
        self._text_widget = None
        del self._root_cl
        # self.style = None
        self._root_cl = None
        # self._ais_obj.ais_rx_buff = self._tmp_buffer + self._ais_obj.ais_rx_buff
        self.destroy()
