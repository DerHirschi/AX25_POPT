import time
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

from constant import APRS_SW_ID
from fnc.str_fnc import convert_umlaute_to_ascii
from gui.guiAPRSnewMSG import NewMessageWindow
from string_tab import STR_TABLE


class APRS_msg_SYS_PN(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root_cl = root_win
        self.root_cl.aprs_pn_msg_win = self
        self.lang = self.root_cl.language
        self.text_size = self.root_cl.text_size
        self.win_height = 700
        self.win_width = 1450
        self.style = self.root_cl.style
        self.title(STR_TABLE['aprs_pn_msg'][self.lang])
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root_cl.main_win.winfo_x()}+"
                      f"{self.root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.resizable(False, False)
        self.lift()
        self.aprs_ais = self.root_cl.ax25_port_handler.aprs_ais
        self.aprs_pn_msg = self.aprs_ais.ais_aprs_msg_pool['message']

        # Oberer Bereich: Rahmen für Buttons
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, padx=10, pady=10)

        button4 = ttk.Button(top_frame, text=STR_TABLE['new_msg'][self.lang], command=self.btn_new_msg)
        button4.pack(side=tk.LEFT, padx=5)

        button5 = ttk.Button(top_frame, text=STR_TABLE['del_all'][self.lang], command=self.btn_del_all_msg)
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

        self.messages_treeview = ttk.Treeview(
            left_frame,
            columns=("time", "port_id", "from", "to", 'via', 'msgno'),
            show="headings",
            yscrollcommand=tree_scrollbar.set
        )
        self.messages_treeview.heading("time", text="Datum")
        self.messages_treeview.heading("port_id", text="Port")
        self.messages_treeview.heading("from", text=f"{STR_TABLE['from'][self.lang]}")
        self.messages_treeview.heading("to", text=f"{STR_TABLE['to'][self.lang]}")
        self.messages_treeview.heading("via", text="VIA")
        self.messages_treeview.heading("msgno", text="#")
        self.messages_treeview.column("time", stretch=tk.NO, width=170)
        self.messages_treeview.column("port_id", stretch=tk.NO, width=50)
        self.messages_treeview.column("from", stretch=tk.NO, width=130)
        self.messages_treeview.column("to", stretch=tk.NO, width=130)
        self.messages_treeview.column("via", stretch=tk.NO, width=130)
        self.messages_treeview.column("msgno", stretch=tk.NO, width=80)
        self.messages_treeview.tag_configure("not_own", background='white', foreground='black')
        self.messages_treeview.tag_configure("is_own", background='green2', foreground='black')

        self.messages_treeview.pack(fill=tk.BOTH, expand=True)
        self.messages_treeview.bind('<<TreeviewSelect>>', self.entry_selected)

        tree_scrollbar.config(command=self.messages_treeview.yview)

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
        self.out_text = tk.Text(middle_frame,
                                height=3,
                                width=67,
                                background='black',
                                foreground='white',
                                fg='white',
                                insertbackground='white'
                                )
        self.out_text.pack(fill=tk.BOTH, expand=False)
        """
        # Rechter Bereich: Scrolled Window für den fortlaufenden Text
        right_frame = ttk.Frame(mid_frame)
        right_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        scrolled_text = ScrolledText(right_frame, width=30)
        scrolled_text.pack(fill=tk.BOTH, expand=True)
        """
        # Unterer Bereich: Rahmen für Buttons
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        button1 = ttk.Button(bottom_frame, text=STR_TABLE['close'][self.lang], command=self.btn_close)
        button1.pack(side=tk.LEFT, padx=5)
        """
        button2 = ttk.Button(bottom_frame, text="Button 2", command=self.button2_clicked)
        button2.pack(side=tk.LEFT, padx=5)

        button3 = ttk.Button(bottom_frame, text="Button 3", command=self.button3_clicked)
        button3.pack(side=tk.LEFT, padx=5)
        """
        self.new_msg_win = None
        self.antwort_pack = ()
        self.is_in_update = False
        self.bind('<Return>', self.send_aprs_msg)
        self.update_tree()

    def update_tree(self):
        while self.is_in_update:
            time.sleep(0.1)

        self.is_in_update = True
        self.aprs_pn_msg = list(self.aprs_ais.ais_aprs_msg_pool['message'])
        self.aprs_pn_msg.reverse()

        for i in self.messages_treeview.get_children():
            self.messages_treeview.delete(i)
        self.update()
        tree_data = []
        for form_msg in self.aprs_pn_msg:
            port_id = form_msg[0]
            if port_id == -1:
                port_id = 'I-NET'
            if form_msg[1][1]['addresse'] in self.root_cl.ax25_port_handler.ax25_stations_settings:
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
            self.messages_treeview.insert('', tk.END, values=ret_ent[0], tags=ret_ent[1])
        self.is_in_update = False

    def update_tree_single_pack(self, form_aprs_pack):
        self.is_in_update = True
        self.aprs_pn_msg = list(self.aprs_ais.ais_aprs_msg_pool['message'])
        self.aprs_pn_msg.reverse()
        port_id = form_aprs_pack[0]
        if port_id == -1:
            port_id = 'I-NET'
        if form_aprs_pack[1][1]['addresse'] in self.root_cl.ax25_port_handler.ax25_stations_settings:
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
        self.messages_treeview.insert('', 0, values=new_tree_data[0], tags=new_tree_data[1])
        self.is_in_update = False

    def entry_selected(self, event=None):
        selected_iid = self.messages_treeview.selection()
        self.antwort_pack = ()
        if selected_iid:
            self.selected_message_text.config(state='normal')
            self.selected_message_text.delete(0.0, tk.END)
            selected_iid = selected_iid[0]
            current_idx = self.messages_treeview.index(selected_iid)
            msg_id = f"{self.aprs_pn_msg[current_idx][1][1].get('from', '')}-{self.aprs_pn_msg[current_idx][1][1].get('addresse', '')}"
            self.antwort_pack = self.aprs_pn_msg[current_idx]
            last_pack = []

            for pack_msg in self.aprs_pn_msg[current_idx:][::-1]:
                msg = ''
                tag_ind_1 = self.selected_message_text.index(tk.INSERT)
                if f"{pack_msg[1][1].get('from', '')}-{pack_msg[1][1].get('addresse', '')}" == msg_id \
                        or f"{pack_msg[1][1].get('addresse', '')}-{pack_msg[1][1].get('from', '')}" == msg_id:
                    if pack_msg[1][1] not in last_pack:
                        last_pack.append(pack_msg[1][1])
                        msg += f"Time: {pack_msg[1][0]}".ljust(28)
                        msg_nr = pack_msg[1][1].get('msgNo', '')
                        if msg_nr != '':
                            msg += f"Msg#: {msg_nr}\n"
                        else:

                            msg += '\n'
                        msg += f"Path: {str(pack_msg[1][1].get('path', '')).replace('[', '').replace(']', '').replace(',', '')}\n".replace(
                            "'", "")
                        msg += f"From: {str(pack_msg[1][1].get('from', '')).ljust(22)}"
                        msg += f"Via : {pack_msg[1][1].get('via', '')}\n"

                        msg_text = pack_msg[1][1].get('message_text', '') + '\n\n'

                        self.selected_message_text.insert(tk.END, msg)
                        self.selected_message_text.tag_add('header', tag_ind_1, tk.INSERT)
                        self.selected_message_text.insert(tk.END, msg_text)
            self.selected_message_text.config(state='disabled')
            self.selected_message_text.see(tk.END)

    def send_aprs_msg(self, event=None):
        msg = self.out_text.get(0.0, tk.END)[:-1].replace('\n', '')
        with_ack = False
        if self.antwort_pack[1][1].get('msgNo', False):
            with_ack = True
        if self.aprs_ais.send_aprs_answer_msg(self.antwort_pack, msg, with_ack):
            self.out_text.delete(0.0, tk.END)
        """
        with_ack = False
        ack_nr = 0
        if self.antwort_pack:
            msg = self.out_text.get(0.0, tk.END)[:-1]
            msg_list = []
            while len(msg) > 67:
                msg_list.append(msg[:67])
                msg = msg[67:]
            msg_list.append(msg)
            print(msg)
            from_call = self.antwort_pack[1][1].get('addresse', '')
            print(from_call)

            if from_call in self.root_cl.ax25_port_handler.ax25_stations_settings:
                to_call = self.antwort_pack[1][1].get('from', '')
                path = self.antwort_pack[1][1].get('path', '')
                print(path)
                port_id = self.antwort_pack[0]
                if port_id == 'I-NET':
                    port_id = -1
                for el in msg_list:
                    if with_ack:
                        msg_text = f":{to_call.ljust(9)}:{el}" + "{" + f"{ack_nr}"
                    else:
                        msg_text = f":{to_call.ljust(9)}:{el}"
                    if port_id == -1:
                        self.aprs_ais.build_ais_pack(from_call=from_call, msg=msg_text)
                        self.out_text.delete(0.0, tk.END)
                    else:
                        ax_port = self.root_cl.ax25_port_handler.ax25_ports.get(port_id, False)
                        if ax_port:
                            msg_text = convert_umlaute_to_ascii(msg_text).encode('ASCII', 'ignore')
                            print(path)
                            path.reverse()
                            add_str = f"{APRS_SW_ID}"
                            print(path)
                            for elm in path:
                                elm = elm.replace('*', '')
                                add_str += f" {elm}"
                            print(path)
                            print(add_str)
                            ax_port.send_UI_frame(
                                own_call=from_call,
                                add_str=add_str,
                                text=msg_text,
                                cmd_poll=(False, True)
                            )
                            self.out_text.delete(0.0, tk.END)
        """
    def btn_close(self):
        self.destroy_win()

    def btn_new_msg(self):
        if self.new_msg_win is None:
            NewMessageWindow(self)

    def btn_del_all_msg(self):
        self.aprs_ais.ais_aprs_msg_pool['message'] = []
        self.update_tree()

    def destroy_win(self):
        self.root_cl.aprs_pn_msg_win = None
        self.destroy()
