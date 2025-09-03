import time
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from ax25.ax25InitPorts import PORT_HANDLER
from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from cfg.constant import FONT
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import tk_filter_bad_chars, get_strTab


class AISmonitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_cl = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._text_size = int(self._root_cl.text_size)
        self._win_height = 700
        self._win_width = 1500
        # self.style = self._root_cl.style
        self.title(self._getTabStr('aprs_mon'))
        self.geometry(f"{self._win_width}x"
                      f"{self._win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        # self.resizable(False, False)
        self.lift()
        ##############################################
        ##############################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ##############################################
        self._ais_obj = PORT_HANDLER.get_aprs_ais()

        # Frame für den linken Bereich
        left_frame = ttk.Frame(main_f)
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
        right_frame = ttk.Frame(main_f)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self._autoscroll_var = tk.BooleanVar(self)
        self._autoscroll_var.set(True)
        ttk.Checkbutton(right_frame,
                       variable=self._autoscroll_var,
                       text="Autoscroll  ",
                       command=self._scroll_to_end).pack(side=tk.TOP, padx=2)
        self._new_user_var = tk.BooleanVar(self)
        self._new_user_var.set(False)
        ttk.Checkbutton(right_frame,
                       variable=self._new_user_var,
                       text="UserDB      ",
                       command=self._chk_new_user
                       ).pack(side=tk.TOP, padx=2)
        self._call_filter = tk.BooleanVar(self)
        self._call_filter.set(False)
        ttk.Checkbutton(right_frame,
                       variable=self._call_filter,
                       text="Call-Filter  ",
                       command=self._chk_call_filter
                       ).pack(side=tk.TOP, padx=2)

        ttk.Label(right_frame, text="Call-Filter:").pack(side=tk.TOP, padx=2)
        self._call_filter_calls_var = tk.StringVar(self)
        ttk.Entry(right_frame,
                 textvariable=self._call_filter_calls_var,
                 width=20
                 ).pack(side=tk.TOP, padx=2)

        ttk.Button(right_frame,
                  text=self._getTabStr('delete'),
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
        ########################################################
        self._ais_aprs_stations = {}
        self._ais_aprs_stat_calls = []
        self._tasker_q_timer = time.time()
        self._tasker_q = []

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
            tr = False
            for el in list(self._ais_obj.ais_rx_buff):
                if el:
                    if self._call_filter.get():
                        if el['from'] in self._ais_aprs_stat_calls:
                            tr = True
                            tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc,
                                                          add_new_user=self._ais_obj.add_new_user)
                            self._text_widget.insert(tk.END, tmp)
                    else:
                        tr = True
                        tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc,
                                                      add_new_user=self._ais_obj.add_new_user)
                        self._text_widget.insert(tk.END, tmp)
            if tr:
                self._scroll_to_end()

    def tasker(self):
        if not self._tasker_q:
            return False
        if time.time() < self._tasker_q_timer:
            return False
        self._tasker_q_timer = time.time() + 0.1
        n = 10
        if len(self._tasker_q) > 10:
            logger.warning(f"len(self._tasker_q) > 10: {len(self._tasker_q)}")
            logger.warning(f"self._tasker_q: {self._tasker_q}")
        while self._tasker_q and n:
            task, arg = self._tasker_q[0]
            self._tasker_q = self._tasker_q[1:]
            if task == 'pack_to_mon':
                self._pack_to_mon_task(arg)
            n -= 1

        return True

    def _add_tasker_q(self, fnc: str, arg):
        if (fnc, None) in self._tasker_q:
            return
        self._tasker_q.append(
            (fnc, arg)
        )

    def set_ais_obj(self):
        self._ais_obj = PORT_HANDLER.get_aprs_ais()

    def pack_to_mon(self, pack):
        self._add_tasker_q("pack_to_mon", pack)

    def _pack_to_mon_task(self, pack):
        tr = False
        if self._call_filter.get():
            if pack['from'] in self._ais_aprs_stat_calls:
                tr = True
                tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc,
                                             add_new_user=self._ais_obj.add_new_user)
                tmp = tk_filter_bad_chars(tmp)
                self._text_widget.insert(tk.END, tmp)
        else:
            tr = True
            tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc,
                                         add_new_user=self._ais_obj.add_new_user)
            tmp = tk_filter_bad_chars(tmp)
            self._text_widget.insert(tk.END, tmp)

        if tr:
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
        self._ais_obj.ais_mon_gui = None
        self._root_cl.aprs_mon_win = None
        # self._ais_obj.ais_rx_buff = self._tmp_buffer + self._ais_obj.ais_rx_buff
        self.destroy()
