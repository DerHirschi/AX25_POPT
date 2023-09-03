import time
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from ax25.ax25InitPorts import PORT_HANDLER
from fnc.str_fnc import tk_filter_bad_chars
from gui.guiAPRSnewMSG import NewMessageWindow
from string_tab import STR_TABLE


class APRS_msg_SYS_PN(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._init_done = False
        self._root_cl = root_win
        self._root_cl.aprs_pn_msg_win = self
        self.lang = self._root_cl.language
        self.text_size = self._root_cl.text_size
        self.win_height = 700
        self.win_width = 1450
        self.style = self._root_cl.style
        self.title(STR_TABLE['aprs_pn_msg'][self.lang])
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        # self.resizable(False, False)
        self.lift()
        self._aprs_ais = PORT_HANDLER.get_aprs_ais()
        self._aprs_pn_msg = self._aprs_ais.ais_aprs_msg_pool['message']

        # Oberer Bereich: Rahmen für Buttons
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, padx=10, pady=10)

        button4 = ttk.Button(top_frame, text=STR_TABLE['new_msg'][self.lang], command=self._btn_new_msg)
        button4.pack(side=tk.LEFT, padx=5)

        button5 = ttk.Button(top_frame, text=STR_TABLE['del_all'][self.lang], command=self._btn_del_all_msg)
        button5.pack(side=tk.LEFT, padx=5)
        """"
        button6 = ttk.Button(top_frame, text="Button 6", command=self.button6_clicked)
        button6.pack(side=tk.LEFT, padx=5)
        """
        mid_frame = ttk.Frame(self)
        mid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Linker Bereich: Treeview-Liste der Nachrichten
        left_frame = ttk.Frame(mid_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=False)

        # Scrollbar für die Treeview
        tree_scrollbar = ttk.Scrollbar(left_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._messages_treeview = ttk.Treeview(
            left_frame,
            columns=("time", "port_id", "from", "to", 'via', 'msgno'),
            show="headings",
            yscrollcommand=tree_scrollbar.set
        )
        self._messages_treeview.heading("time", text="Datum")
        self._messages_treeview.heading("port_id", text="Port")
        self._messages_treeview.heading("from", text=f"{STR_TABLE['from'][self.lang]}")
        self._messages_treeview.heading("to", text=f"{STR_TABLE['to'][self.lang]}")
        self._messages_treeview.heading("via", text="VIA")
        self._messages_treeview.heading("msgno", text="#")
        self._messages_treeview.column("time", stretch=tk.NO, width=170)
        self._messages_treeview.column("port_id", stretch=tk.NO, width=50)
        self._messages_treeview.column("from", stretch=tk.NO, width=130)
        self._messages_treeview.column("to", stretch=tk.NO, width=130)
        self._messages_treeview.column("via", stretch=tk.NO, width=130)
        self._messages_treeview.column("msgno", stretch=tk.NO, width=60)
        self._messages_treeview.tag_configure("not_own", background='white', foreground='black')
        self._messages_treeview.tag_configure("is_own", background='green2', foreground='black')

        self._messages_treeview.pack(fill=tk.BOTH, expand=True)
        self._messages_treeview.bind('<<TreeviewSelect>>', self._entry_selected)

        tree_scrollbar.config(command=self._messages_treeview.yview)

        # Mittlerer Bereich: Fenster für die Ausgabe der selektierten Nachricht
        middle_frame = ttk.Frame(mid_frame)
        middle_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=False)

        selected_message_label = ttk.Label(middle_frame, text=f"{STR_TABLE['msg'][self.lang]}:")
        selected_message_label.pack(anchor=tk.W, padx=5, pady=5)

        self.selected_message_text = ScrolledText(middle_frame,
                                                  height=10,
                                                  width=67,
                                                  background='black',
                                                  foreground='white',
                                                  fg='white',
                                                  insertbackground='white',
                                                  state='disabled'
                                                  )
        self.selected_message_text.pack(fill=tk.BOTH, expand=True)
        self.selected_message_text.tag_config("header", foreground="green2")
        self._out_text = tk.Text(middle_frame,
                                height=3,
                                width=67,
                                background='black',
                                foreground='white',
                                fg='white',
                                insertbackground='white'
                                )
        self._out_text.pack(fill=tk.BOTH, expand=False)

        # Rechter Bereich: Scrolled Window für den fortlaufenden Text
        right_frame = ttk.Frame(mid_frame)
        right_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=False)
        selected_message_label = ttk.Label(right_frame, text='Spooler:')
        selected_message_label.pack(anchor=tk.W, padx=5, pady=5)
        sppol_tree_scrollbar = ttk.Scrollbar(right_frame)
        sppol_tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.spooler_treeview = ttk.Treeview(
            right_frame,
            columns=("add", "port_id", 'msgno', 'N', "time"),
            show="headings",
            yscrollcommand=sppol_tree_scrollbar.set
        )
        self.spooler_treeview.heading("add", text="Address")
        self.spooler_treeview.heading("port_id", text="Port")
        self.spooler_treeview.heading("msgno", text="#")
        self.spooler_treeview.heading("N", text="N")
        self.spooler_treeview.heading("time", text="TX in")

        self.spooler_treeview.column("add", stretch=tk.NO, width=200)
        self.spooler_treeview.column("port_id", stretch=tk.NO, width=60)
        self.spooler_treeview.column("msgno", stretch=tk.NO, width=60)
        self.spooler_treeview.column("N", stretch=tk.NO, width=20)
        self.spooler_treeview.column("time", stretch=tk.NO, width=60)
        self.spooler_treeview.pack(fill=tk.BOTH, expand=True)
        but = ttk.Button(right_frame, text="Reset", command=self._btn_reset_spooler)
        but.pack(side=tk.LEFT, padx=5)
        but = ttk.Button(right_frame, text=STR_TABLE['delete'][self.lang], command=self._btn_del_spooler)
        but.pack(side=tk.RIGHT, padx=5)

        # Unterer Bereich: Rahmen für Buttons
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        button1 = ttk.Button(bottom_frame, text=STR_TABLE['close'][self.lang], command=self._btn_close)
        button1.pack(side=tk.LEFT, padx=5)
        """
        button2 = ttk.Button(bottom_frame, text="Button 2", command=self.button2_clicked)
        button2.pack(side=tk.LEFT, padx=5)

        button3 = ttk.Button(bottom_frame, text="Button 3", command=self.button3_clicked)
        button3.pack(side=tk.LEFT, padx=5)
        """
        self._new_msg_win = None
        self._antwort_pack = ()
        self._is_in_update = False
        self.bind('<Return>', self._send_aprs_msg)
        self._update_tree()
        self._init_done = True

    def _update_tree(self):
        while self._is_in_update:
            time.sleep(0.1)

        self._is_in_update = True
        self._aprs_pn_msg = list(self._aprs_ais.ais_aprs_msg_pool['message'])
        self._aprs_pn_msg.reverse()

        for i in self._messages_treeview.get_children():
            self._messages_treeview.delete(i)
        self.update()
        tree_data = []
        for form_msg in self._aprs_pn_msg:
            port_id = form_msg[0]
            if port_id == -1:
                port_id = 'I-NET'
            if form_msg[1][1]['addresse'] in PORT_HANDLER.ax25_stations_settings \
                    or form_msg[1][1]['from'] in PORT_HANDLER.ax25_stations_settings:
                is_own = 'is_own'
            else:
                is_own = 'not_own'
            tree_data.append(
                ((
                     f"{form_msg[1][0]}",
                     f"{port_id}",
                     f"{form_msg[1][1]['from']}",
                     f"{form_msg[1][1]['addresse']}",
                     f"{form_msg[1][1].get('via', '')}",
                     f"{form_msg[1][1].get('msgNo', '')}",
                 ), is_own)
            )

        for ret_ent in tree_data:
            self._messages_treeview.insert('', tk.END, values=ret_ent[0], tags=ret_ent[1])
        self._is_in_update = False

    def update_tree_single_pack(self, form_aprs_pack):
        if self._init_done:
            self._is_in_update = True
            self._aprs_pn_msg = list(self._aprs_ais.ais_aprs_msg_pool['message'])
            self._aprs_pn_msg.reverse()
            port_id = form_aprs_pack[0]
            if port_id == -1:
                port_id = 'I-NET'
            if form_aprs_pack[1][1]['addresse'] in PORT_HANDLER.ax25_stations_settings \
                    or form_aprs_pack[1][1]['from'] in PORT_HANDLER.ax25_stations_settings:
                is_own = 'is_own'
            else:
                is_own = 'not_own'

            new_tree_data = ((
                         f"{form_aprs_pack[1][0]}",
                         f"{port_id}",
                         f"{form_aprs_pack[1][1]['from']}",
                         f"{form_aprs_pack[1][1]['addresse']}",
                         f"{form_aprs_pack[1][1].get('via', '')}",
                         f"{form_aprs_pack[1][1].get('msgNo', '')}",
                     ), is_own)
            self._messages_treeview.insert('', 0, values=new_tree_data[0], tags=new_tree_data[1])
            self._is_in_update = False

    def update_spooler_tree(self):
        if self._init_done:
            for i in self.spooler_treeview.get_children():
                self.spooler_treeview.delete(i)
            self.update()
            tree_data = []
            for msg_no in self._aprs_ais.spooler_buffer:
                pack = self._aprs_ais.spooler_buffer[msg_no]
                if not pack['send_timer']:
                    tx_timer = pack['send_timer']
                else:
                    tx_timer = max(round(pack['send_timer'] - time.time()), 0)
                tree_data.append((
                    f"{pack['address_str']}",
                    f"{pack['popt_port_id']}",
                    f"{pack['msgNo']}",
                    f"{pack['N']}",
                    f"{tx_timer}",

                ))
            for ret_ent in tree_data:
                self.spooler_treeview.insert('', tk.END, values=ret_ent)

    def _entry_selected(self, event=None):
        show_no_dbl = True
        selected_iid = self._messages_treeview.selection()
        self._antwort_pack = ()
        if selected_iid:
            self.selected_message_text.config(state='normal')
            self.selected_message_text.delete(0.0, tk.END)
            selected_iid = selected_iid[0]
            current_idx = self._messages_treeview.index(selected_iid)
            msg_id = f"{self._aprs_pn_msg[current_idx][1][1].get('from', '')}-{self._aprs_pn_msg[current_idx][1][1].get('addresse', '')}"
            self._antwort_pack = self._aprs_pn_msg[current_idx]
            dbl_pack = []

            for pack_msg in self._aprs_pn_msg[current_idx:][::-1]:
                msg = ''
                tag_ind_1 = self.selected_message_text.index(tk.INSERT)
                if f"{pack_msg[1][1].get('from', '')}-{pack_msg[1][1].get('addresse', '')}" == msg_id \
                        or f"{pack_msg[1][1].get('addresse', '')}-{pack_msg[1][1].get('from', '')}" == msg_id:
                    if show_no_dbl:
                        if pack_msg[1][1] not in dbl_pack:
                            msg_nr = pack_msg[1][1].get('msgNo', '')
                            if msg_nr not in dbl_pack:
                                dbl_pack.append(pack_msg[1][1])
                                if msg_nr:
                                    dbl_pack.append(msg_nr)
                                msg += f"Time: {pack_msg[1][0]}".ljust(28)
                                if msg_nr != '':
                                    msg += f"Msg#: {msg_nr}\n"
                                else:

                                    msg += '\n'
                                msg += f"Path: {str(pack_msg[1][1].get('path', '')).replace('[', '').replace(']', '').replace(',', '')}\n".replace(
                                    "'", "")
                                msg += f"From: {str(pack_msg[1][1].get('from', '')).ljust(22)}"
                                msg += f"Via : {pack_msg[1][1].get('via', '')}\n"

                                msg_text = tk_filter_bad_chars(pack_msg[1][1].get('message_text', '')) + '\n\n'

                                self.selected_message_text.insert(tk.END, msg)
                                self.selected_message_text.tag_add('header', tag_ind_1, tk.INSERT)
                                self.selected_message_text.insert(tk.END, msg_text)

            self.selected_message_text.config(state='disabled')
            self.selected_message_text.see(tk.END)

    def _send_aprs_msg(self, event=None):
        msg = self._out_text.get(0.0, tk.END)[:-1].replace('\n', '')
        with_ack = False
        if self._antwort_pack[1][1].get('msgNo', False):
            with_ack = True
        if self._aprs_ais.send_aprs_answer_msg(self._antwort_pack, msg, with_ack):
            self._out_text.delete(0.0, tk.END)

    def _btn_close(self):
        self._destroy_win()

    def _btn_del_spooler(self):
        if self._aprs_ais is not None:
            self._aprs_ais.del_spooler()

    def _btn_reset_spooler(self):
        if self._aprs_ais is not None:
            self._aprs_ais.reset_spooler()

    def _btn_new_msg(self):
        if self._new_msg_win is None:
            NewMessageWindow(self)

    def _btn_del_all_msg(self):
        self._aprs_ais.ais_aprs_msg_pool['message'] = []
        self._update_tree()

    def _destroy_win(self):
        self._root_cl.aprs_pn_msg_win = None
        self.destroy()
