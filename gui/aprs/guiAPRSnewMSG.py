import datetime
import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from ax25aprs.aprs_dec import parse_aprs_fm_aprsframe
from cfg.constant import APRS_SW_ID
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab, zeilenumbruch, convert_umlaute_to_ascii


class NewMessageWindow(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._aprs_root    = root_win
        self._aprs_root.new_msg_win = self
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # self._get_colorMap = lambda: COLOR_MAP.get(root_win.style_name, ('black', '#d9d9d9'))
        self.win_height    = 250
        self.win_width     = 650
        self.style = root_win.style
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, True)
        self.attributes("-topmost", True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        self.title(self._getTabStr('new_msg'))
        #######################
        self._to_call_var      = tk.StringVar(self,  value='')
        self._char_counter_var = tk.StringVar(self,  value='67/0')
        self._wide_var         = tk.StringVar(self,  value='0')
        self._ack_var          = tk.BooleanVar(self, value=True)
        #######################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        #######################
        # Oberer Bereich: Dropdown-Menüs und Eingabefelder
        top_frame = ttk.Frame(main_f)
        top_frame.pack(side=tk.TOP, padx=10, pady=10)

        label1 = ttk.Label(top_frame, text="Port:")
        label1.pack(side=tk.LEFT, padx=5)

        port_vals = ['I-NET'] + list(PORT_HANDLER.get_all_ports().keys())
        self.port_var = tk.StringVar(self)
        dropdown1 = ttk.Combobox(top_frame,
                                 width=3,
                                 values=port_vals,
                                 textvariable=self.port_var
                                 )
        dropdown1.pack(side=tk.LEFT, padx=5)
        #
        from_frame = ttk.Frame(top_frame)
        from_frame.pack(side=tk.LEFT, padx=60)
        label2 = ttk.Label(from_frame, text="From:")
        label2.pack(side=tk.LEFT)


        from_vals = POPT_CFG.get_stat_CFG_keys()
        self.from_var = tk.StringVar(self)
        dropdown2 = ttk.Combobox(from_frame,
                                 width=10,
                                 values=from_vals,
                                 textvariable=self.from_var
                                 )
        dropdown2.pack(side=tk.LEFT, padx=5)
        #
        ack_check = ttk.Checkbutton(top_frame,
                                    text="ACK",
                                    variable=self._ack_var,
                                    )
        ack_check.pack(side=tk.LEFT, padx=60)
        #############################################
        top_bottom_frame = ttk.Frame(main_f)
        top_bottom_frame.pack(side=tk.TOP, padx=10, pady=10)

        label3 = ttk.Label(top_bottom_frame, text="To & Via: ")
        label3.pack(side=tk.LEFT)
        to_call_ent = ttk.Entry(top_bottom_frame, textvariable=self._to_call_var , width=50)
        to_call_ent.pack(side=tk.LEFT, padx=5)

        ###################################################
        # Mittlerer Bereich: Mehrzeiliges Eingabefeld
        middle_frame = ttk.Frame(main_f)
        middle_frame.pack(side=tk.TOP, padx=10, pady=10, fill='y', expand=True)
        char_c_label = ttk.Label(middle_frame, textvariable=self._char_counter_var)
        char_c_label.pack(anchor='e', padx=10, pady=5)
        self._msg_entry = tk.Text(middle_frame,
                                  width=67,
                                  height=3,
                                  background='black',
                                  foreground='white',
                                  fg='white',
                                  insertbackground='white'
                                  )
        self._msg_entry.pack(fill='y', expand=True)
        self._msg_entry.bind("<KeyRelease>", self._on_key_release_inp_txt)

        # Unterer Bereich: Button
        bottom_frame = ttk.Frame(main_f)
        bottom_frame.pack(side=tk.TOP, padx=10, pady=10,fill='y')

        button = ttk.Button(bottom_frame, text="Nachricht senden", command=self._send_message)
        button.pack(fill='y')
        self.bind('<Return>', self._send_message)

    def _on_key_release_inp_txt(self, event=None):
        ind = str(int(float(self._msg_entry.index(tk.INSERT)))) + '.0'
        old_text = self._msg_entry.get(ind,  self._msg_entry.index(tk.INSERT))
        text = convert_umlaute_to_ascii(old_text)
        text = zeilenumbruch(text, max_zeichen=67, umbruch='\n')
        if text != old_text:
            self._msg_entry.delete(ind,  self._msg_entry.index(tk.INSERT))
            self._msg_entry.insert(tk.INSERT, text)
        text_size = self._msg_entry.get(0.0, self._msg_entry.index(tk.INSERT)).split('\n')
        self._char_counter_var.set(f"{67 - len(text_size[-1])}/{len(text_size)}")

    def _send_message(self, event=None):
        with_ack    = self._ack_var.get()
        msg         = self._msg_entry.get(0.0, tk.END)[:-1]
        from_call   = self.from_var.get()
        port_id     = self.port_var.get()
        if from_call in POPT_CFG.get_stat_CFG_keys():
            add_str = self._to_call_var.get().upper()
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
                    aprs_pack['port_id'] = port_id
                    aprs_pack['rx_time'] = datetime.datetime.now()
                    PORT_HANDLER.aprs_ais.send_pn_msg(aprs_pack, msg, with_ack)
                self.destroy_win()

    def destroy_win(self):
        self._aprs_root.new_msg_win = None
        self.destroy()
