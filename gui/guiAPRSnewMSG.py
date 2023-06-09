import tkinter as tk
from tkinter import ttk

from ax25aprs.aprs_dec import parse_aprs_fm_aprsframe
from constant import APRS_SW_ID
from fnc.str_fnc import convert_umlaute_to_ascii
from string_tab import STR_TABLE


class NewMessageWindow(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root_cl = root_win.root_cl
        self.aprs_root = root_win
        self.aprs_root.new_msg_win = self
        self.port_handler = self.root_cl.ax25_port_handler
        self.lang = self.root_cl.language
        self.text_size = self.root_cl.text_size
        self.win_height = 250
        self.win_width = 700
        self.style = self.root_cl.style
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root_cl.main_win.winfo_x()}+"
                      f"{self.root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.resizable(False, False)
        self.lift()
        self.title(STR_TABLE['new_msg'][self.lang])

        # Oberer Bereich: Dropdown-Menüs und Eingabefelder
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, padx=10, pady=10)

        label1 = ttk.Label(top_frame, text="Port:")
        label1.pack(side=tk.LEFT, padx=5)

        port_vals = ['I-NET'] + list(self.port_handler.ax25_ports.keys())
        self.port_var = tk.StringVar(self)
        dropdown1 = ttk.Combobox(top_frame,
                                 width=3,
                                 values=port_vals,
                                 textvariable=self.port_var
                                 )
        dropdown1.pack(side=tk.LEFT, padx=5)

        label2 = ttk.Label(top_frame, text="     From:")
        label2.pack(side=tk.LEFT, padx=60)

        from_vals = list(self.port_handler.ax25_stations_settings.keys())
        self.from_var = tk.StringVar(self)
        dropdown2 = ttk.Combobox(top_frame,
                                 width=10,
                                 values=from_vals,
                                 textvariable=self.from_var
                                 )
        dropdown2.pack(side=tk.LEFT, padx=5)

        top_bottom_frame = ttk.Frame(self)
        top_bottom_frame.pack(side=tk.TOP, padx=10, pady=10)

        label3 = ttk.Label(top_bottom_frame, text="To:   ")
        label3.pack(side=tk.LEFT)
        self.to_call_ent = ttk.Entry(top_bottom_frame, width=50)
        self.to_call_ent.pack(side=tk.LEFT, padx=5)

        # Mittlerer Bereich: Mehrzeiliges Eingabefeld
        middle_frame = ttk.Frame(self)
        middle_frame.pack(side=tk.TOP, padx=10, pady=10)

        self.msg_entry = tk.Text(middle_frame,
                                 width=67,
                                 height=3,
                                 background='black',
                                 foreground='white',
                                 fg='white',
                                 insertbackground='white'
                                 )
        self.msg_entry.pack(fill=tk.BOTH, expand=True)

        self.ack_var = tk.BooleanVar(self)
        ack_check = ttk.Checkbutton(top_frame,
                                    text="ACK",
                                    variable=self.ack_var,
                                    )
        self.ack_var.set(True)
        ack_check.pack(side=tk.LEFT, padx=60)


        # Unterer Bereich: Button
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.TOP, padx=10, pady=10)

        button = ttk.Button(bottom_frame, text="Nachricht senden", command=self.send_message)
        button.pack()
        self.bind('<Return>', self.send_message)

    def send_message(self, event=None):
        with_ack = self.ack_var.get()
        msg = self.msg_entry.get(0.0, tk.END)[:-1].replace('\n', '')
        from_call = self.from_var.get()
        port_id = self.port_var.get()
        if port_id.isdigit():
            port_id = int(port_id)
        if from_call in self.port_handler.ax25_stations_settings:
            add_str = self.to_call_ent.get().upper()
            if add_str:
                # to_call = APRS_SW_ID
                tmp = add_str.split(' ')
                to_call = tmp[0]
                path = tmp[1:]
                aprs_str = f"{from_call}>{APRS_SW_ID}"
                for el in path:
                    aprs_str += f",{el}"
                aprs_str += f"::{to_call.ljust(9)}:dummy"
                aprs_pack = parse_aprs_fm_aprsframe(aprs_str)
                if aprs_pack:
                    aprs_pack['popt_port_id'] = port_id
                    self.aprs_root.aprs_ais.send_pn_msg(aprs_pack, msg, with_ack)

                self.destroy_win()

    def destroy_win(self):
        self.aprs_root.new_msg_win = None
        self.destroy()
