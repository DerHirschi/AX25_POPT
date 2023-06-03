import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from string_tab import STR_TABLE


class AISmonitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root_cl = root_win
        self.lang = self.root_cl.language
        self.win_height = 700
        self.win_width = 1100
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
        self.text_widget = ScrolledText(text_frame, background='black', foreground='green')
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Frame für den rechten Bereich
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.autoscroll_var = tk.BooleanVar(self)
        self.autoscroll_var.set(True)
        tk.Checkbutton(right_frame,
                       variable=self.autoscroll_var,
                       text="Autoscroll",
                       command=self.scroll_to_end).pack(side=tk.TOP, padx=2)
        self.new_user_var = tk.BooleanVar(self)
        self.new_user_var.set(False)
        tk.Checkbutton(right_frame,
                       variable=self.new_user_var,
                       text="UserDB    ",
                       command=self.chk_new_user).pack(side=tk.TOP, padx=2)

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
        root_win.aprs_mon_win = self
        self.tasker()

    def tasker(self):
        if self.ais_obj is not None:
            while self.ais_obj.ais_rx_buff \
                    and self.ais_obj.loop_is_running \
                    and self.ais_obj.active:
                pack = self.ais_obj.ais_rx_buff[0]
                self.ais_obj.ais_rx_buff = self.ais_obj.ais_rx_buff[1:]
                self.tmp_buffer.append(pack)
                tmp = format_aprs_f_aprs_mon(pack, self.ais_obj.ais_loc, add_new_user=self.ais_obj.add_new_user)
                # self.text_widget.delete(0.0, tk.END)
                self.text_widget.insert(tk.INSERT, tmp)
            self.scroll_to_end()

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

