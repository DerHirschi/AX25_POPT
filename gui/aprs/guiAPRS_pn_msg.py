import copy
import time
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import COLOR_MAP
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import tk_filter_bad_chars, get_strTab, zeilenumbruch, convert_umlaute_to_ascii
from gui.aprs.guiAPRSnewMSG import NewMessageWindow

class APRS_msg_SYS_PN(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._init_done     = False
        self._get_colorMap  = lambda: COLOR_MAP.get(root_win.style_name, ('black', '#d9d9d9'))
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._root_cl       = root_win
        PORT_HANDLER.set_aprsMailAlarm_PH(False)
        # self._root_cl.reset_aprsMail_alarm()
        self.text_size  = self._root_cl.text_size
        self.win_height = 600
        self.win_width  = 1200
        self.style      = self._root_cl.style
        self.style_name = self._root_cl.style_name
        self.title(self._getTabStr('aprs_pn_msg'))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        # self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ##########################
        self._aprs_ais       = PORT_HANDLER.get_aprs_ais()
        self._aprs_icon_tab  = root_win.get_aprs_icon_tab_16()
        self._aprs_pn_msg    = list(self._aprs_ais.aprs_msg_pool['message'])
        self._aprs_bl_msg    = list(self._aprs_ais.aprs_msg_pool['bulletin'])
        """
        for el in self._aprs_bl_msg:
            print(el)
        """
        self.new_msg_win     = None
        self._is_in_update   = False
        self._antwort_pack   = {}
        self._chat_address   = ('', [])
        self._sort_rev       = False
        self._dbl_pack       = []
        ##########################
        self._get_msg_from_str = lambda : (f"{self._getTabStr('msg')}: "
                                           f"{self._antwort_pack.get('from', '') if self._antwort_pack.get('from', '') not in POPT_CFG.get_stat_CFG_keys() else self._antwort_pack.get('addresse', '')}>"
                                           f"{self._antwort_pack.get('from', '') if self._antwort_pack.get('from', '') in POPT_CFG.get_stat_CFG_keys() else self._antwort_pack.get('addresse', '')}"
                                           f"{(' via ' + self._antwort_pack.get('via', '')) if self._antwort_pack.get('via', '') else ''}"
                                           f" <--> Port: {self._antwort_pack.get('port_id', '')}"
                                          )
        ##########################
        if POPT_CFG.get_stat_CFG_keys():
            self._sender_var        = tk.StringVar(self, value=str(POPT_CFG.get_stat_CFG_keys()[0]))
        else:
            self._sender_var        = tk.StringVar(self, value='')
        self._port_var          = tk.StringVar(self, value='Port: ')
        self._msg_from_var      = tk.StringVar(self, value=f"{self._getTabStr('msg')}: ")
        self._msg_to_var        = tk.StringVar(self, value=f"{self._getTabStr('to')}: -----   via: -----")
        self._char_counter_var  = tk.StringVar(self, value='67/0')
        self._with_ack_var      = tk.BooleanVar(self, value=True)
        ##########################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ##########################
        # Oberer Bereich: Rahmen für Buttons
        top_frame       = ttk.Frame(main_f)
        mid_frame       = ttk.Frame(main_f)
        bottom_frame    = ttk.Frame(main_f)
        top_frame.pack(   side=tk.TOP,    padx=10, pady=10)
        mid_frame.pack(   side=tk.TOP,    fill=tk.BOTH, expand=True)
        bottom_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        ###########################################
        self._paned_window = ttk.PanedWindow(mid_frame, orient=tk.HORIZONTAL)
        self._paned_window.pack(fill=tk.BOTH, expand=True)

        left_frame      = ttk.Frame(self._paned_window)
        middle_frame    = ttk.Frame(self._paned_window)
        right_frame     = ttk.Frame(self._paned_window)
        left_frame.pack(  side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=False)
        middle_frame.pack(side=tk.LEFT, padx=5,  pady=10, fill=tk.BOTH, expand=False)
        right_frame.pack( side=tk.LEFT, padx=5,  pady=10, fill=tk.BOTH, expand=False)
        self._paned_window.add(middle_frame, weight=0)
        self._paned_window.add(left_frame,   weight=1)
        self._paned_window.add(right_frame,  weight=2)
        # self._load_pw_pos()

        #############################################################
        # Linker Bereich: Treeview-Liste der Nachrichten
        self._tree_tabctl = ttk.Notebook(left_frame)
        self._tree_tabctl.pack(fill='both', expand=True)
        pn_frame = ttk.Frame(left_frame)
        bl_frame = ttk.Frame(left_frame)
        self._tree_tabctl.add(pn_frame, text=self._getTabStr('pn_msg'))
        self._tree_tabctl.add(bl_frame, text="Bulletin")
        """PN"""
        tree_scrollbar = ttk.Scrollbar(pn_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._messages_treeview = ttk.Treeview(
            pn_frame,
            columns=("time", "port_id", "from", "to", 'via', 'path', 'msgno', 'text'),
            show='tree headings',
            yscrollcommand=tree_scrollbar.set
        )
        self._messages_treeview.heading("time",     text=self._getTabStr('date'))
        self._messages_treeview.heading("port_id",  text="Port")
        self._messages_treeview.heading("from",     text=f"{self._getTabStr('from')}")
        self._messages_treeview.heading("to",       text=f"{self._getTabStr('to')}")
        self._messages_treeview.heading("via",      text="VIA")
        self._messages_treeview.heading("path",     text="Path")
        self._messages_treeview.heading("msgno",    text="#")
        self._messages_treeview.heading("text",     text=self._getTabStr('message'))
        self._messages_treeview.column('#0', anchor='w', stretch=False, width=50)
        self._messages_treeview.column("time",      stretch=tk.NO,  width=130)
        self._messages_treeview.column("port_id",   stretch=tk.NO,  width=45)
        self._messages_treeview.column("from",      stretch=tk.NO,  width=85)
        self._messages_treeview.column("to",        stretch=tk.NO,  width=85)
        self._messages_treeview.column("via",       stretch=tk.NO,  width=85)
        self._messages_treeview.column("path",      stretch=tk.YES, width=120)
        self._messages_treeview.column("msgno",     stretch=tk.NO,  width=45)
        self._messages_treeview.column("text",      stretch=tk.YES, width=220)
        self._messages_treeview.tag_configure("not_own", background='white', foreground='black')
        self._messages_treeview.tag_configure("is_own",  background='green2', foreground='black')
        self._messages_treeview.tag_configure("is_chat", background='yellow', foreground='black')

        self._messages_treeview.pack(fill=tk.BOTH, expand=True)
        self._messages_treeview.bind('<<TreeviewSelect>>', self._entry_selected)

        tree_scrollbar.config(command=self._messages_treeview.yview)
        btn_frame1 = ttk.Frame(pn_frame)
        btn_frame1.pack(expand=False)
        button5 = ttk.Button(btn_frame1, text=self._getTabStr('del_all'), command=self._btn_del_all_pn_msg)
        button5.pack()
        """BL"""
        tree_scrollbar = ttk.Scrollbar(bl_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._bl_messages_treeview = ttk.Treeview(
            bl_frame,
            columns=("time", "port_id", "from", "to", 'via', 'path', 'msgno', 'text'),
            show="headings",
            yscrollcommand=tree_scrollbar.set
        )
        self._bl_messages_treeview.heading("time",      text=self._getTabStr('date'),
                                           command=lambda: self._sort_entry('time', self._bl_messages_treeview))
        self._bl_messages_treeview.heading("port_id",   text="Port",
                                           command=lambda: self._sort_entry('port_id', self._bl_messages_treeview))
        self._bl_messages_treeview.heading("from",      text=f"{self._getTabStr('from')}",
                                           command=lambda: self._sort_entry('from', self._bl_messages_treeview))
        self._bl_messages_treeview.heading("to",        text=f"{self._getTabStr('to')}",
                                           command=lambda: self._sort_entry('to', self._bl_messages_treeview))
        self._bl_messages_treeview.heading("via",       text="VIA",
                                           command=lambda: self._sort_entry('via', self._bl_messages_treeview))
        self._bl_messages_treeview.heading("path",      text="Path",
                                           command=lambda: self._sort_entry('path', self._bl_messages_treeview))
        self._bl_messages_treeview.heading("msgno",     text="BID",
                                           command=lambda: self._sort_entry('msgno', self._bl_messages_treeview))
        self._bl_messages_treeview.heading("text",      text=self._getTabStr('message'))
        self._bl_messages_treeview.column("time",       stretch=tk.NO, width=130)
        self._bl_messages_treeview.column("port_id",    stretch=tk.NO, width=45)
        self._bl_messages_treeview.column("from",       stretch=tk.NO, width=85)
        self._bl_messages_treeview.column("to",         stretch=tk.NO, width=85)
        self._bl_messages_treeview.column("via",        stretch=tk.NO, width=85)
        self._bl_messages_treeview.column("path",       stretch=tk.YES, width=120)
        self._bl_messages_treeview.column("msgno",      stretch=tk.NO, width=45)
        self._bl_messages_treeview.column("text",       stretch=tk.YES, width=220)
        #self._bl_messages_treeview.tag_configure("not_own", background='white', foreground='black')
        #self._bl_messages_treeview.tag_configure("is_own", background='green2', foreground='black')
        #self._bl_messages_treeview.tag_configure("is_chat", background='yellow', foreground='black')

        self._bl_messages_treeview.pack(fill=tk.BOTH, expand=True)
        self._bl_messages_treeview.bind('<<TreeviewSelect>>', self._entry_selected)

        tree_scrollbar.config(command=self._bl_messages_treeview.yview)
        btn_frame1 = ttk.Frame(bl_frame)
        btn_frame1.pack(expand=False)
        button5 = ttk.Button(btn_frame1,
                             text=self._getTabStr('del_all'),
                             command=self._btn_del_all_bl_msg
                             )
        button5.pack()
        #############################################################
        # Mittlerer Bereich: Fenster für die Ausgabe der selektierten Nachricht
        selected_message_label = ttk.Label(middle_frame, textvariable=self._msg_from_var)
        selected_message_label.pack(anchor='w', padx=5, pady=5)
        self._selected_message_text = ScrolledText(middle_frame,
                                                   height=10,
                                                   width=67,
                                                   background='black',
                                                   foreground='white',
                                                   fg='white',
                                                   insertbackground='white',
                                                   state='disabled'
                                                   )
        self._selected_message_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self._selected_message_text.tag_config("header", foreground="green2")
        #
        to_address_label = ttk.Label(middle_frame, textvariable=self._msg_to_var)
        to_address_label.pack(anchor='w', padx=5,)
        #
        port_label = ttk.Label(middle_frame, textvariable=self._port_var)
        port_label.pack(anchor='w', padx=5, )
        #
        fg, bg = self._get_colorMap()
        self._out_text = tk.Text(middle_frame,
                                 height=3,
                                 width=67,
                                 background=bg,
                                 foreground=fg,
                                 fg=fg,
                                 insertbackground=fg
                                 )
        self._out_text.pack(fill=tk.BOTH, expand=False)
        self._out_text.bind("<KeyRelease>", self._on_key_release_inp_txt)
        # BTN Frame
        btn_frame = ttk.Frame(middle_frame)
        btn_frame.pack(fill=tk.BOTH, expand=False)
        send_btn = ttk.Button(btn_frame,
                              text=self._getTabStr('send'),
                              command=self._send_aprs_msg
                              )
        send_btn.pack(side='left', anchor='w', padx=5)
        #
        from_opt_frame = ttk.Frame(btn_frame)
        from_opt_frame.pack(side='left', padx=10)
        ttk.Label(from_opt_frame, text=f"{self._getTabStr('from')}: ").pack(side='left')
        opt = list(POPT_CFG.get_stat_CFG_keys())
        if opt:
            opt = [opt[0]] + opt
        opt_menu = ttk.OptionMenu(from_opt_frame,
                                  self._sender_var,
                                  *opt,
                                  )
        opt_menu.pack(side='left')
        #
        ack_check_btn = ttk.Checkbutton(btn_frame,
                                        text='ACK',
                                        variable=self._with_ack_var)
        ack_check_btn.pack(side='left', anchor='w', padx=10)
        #
        button4 = ttk.Button(btn_frame, text=self._getTabStr('new_msg'), command=self._btn_new_msg)
        button4.pack(side='left', padx=30)
        #
        char_c_label = ttk.Label(btn_frame, textvariable=self._char_counter_var)
        char_c_label.pack(side='right', anchor='e', padx=10)
        #############################################################
        # Rechter Bereich: Scrolled Window für den fortlaufenden Text
        selected_message_label = ttk.Label(right_frame, text='Spooler:')
        selected_message_label.pack(anchor=tk.W, padx=5, pady=5)
        spool_tree_scrollbar = ttk.Scrollbar(right_frame)
        spool_tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._spooler_treeview = ttk.Treeview(
            right_frame,
            columns=("add", "port_id", 'msgno', 'N', "time"),
            show="headings",
            yscrollcommand=spool_tree_scrollbar.set
        )
        self._spooler_treeview.heading("add",       text="Address")
        self._spooler_treeview.heading("port_id",   text="Port")
        self._spooler_treeview.heading("msgno",     text="#")
        self._spooler_treeview.heading("N",         text="N")
        self._spooler_treeview.heading("time",      text="TX in")

        self._spooler_treeview.column("add",        stretch=tk.YES, width=140)
        self._spooler_treeview.column("port_id",    stretch=tk.NO, width=45)
        self._spooler_treeview.column("msgno",      stretch=tk.NO, width=45)
        self._spooler_treeview.column("N",          stretch=tk.NO, width=20)
        self._spooler_treeview.column("time",       stretch=tk.NO, width=50)

        self._spooler_treeview.pack(fill=tk.BOTH, expand=True)
        but = ttk.Button(right_frame, text="Reset", command=self._btn_reset_spooler)
        but.pack(side=tk.LEFT, padx=5)
        but = ttk.Button(right_frame, text=self._getTabStr('delete'), command=self._btn_del_spooler)
        but.pack(side=tk.RIGHT, padx=5)

        # Unterer Bereich: Rahmen für Buttons
        button1 = ttk.Button(bottom_frame, text=self._getTabStr('close'), command=self._btn_close)
        button1.pack(side=tk.LEFT, padx=5)
        """
        button2 = ttk.Button(bottom_frame, text="Button 2", command=self.button2_clicked)
        button2.pack(side=tk.LEFT, padx=5)

        button3 = ttk.Button(bottom_frame, text="Button 3", command=self.button3_clicked)
        button3.pack(side=tk.LEFT, padx=5)
        """

        self._root_cl.aprs_pn_msg_win = self
        self.bind('<Return>', self._send_aprs_msg)
        self._update_tree()
        self._update_bl_tree()
        self._init_done = True

    ################################
    """
    def _load_pw_pos(self):
        guiCfg = POPT_CFG.load_guiPARM_main()
        pan_pos_cfg = guiCfg.get('gui_aprs_text_pan_pos', [300, 300])
        print(pan_pos_cfg)
        i = 0
        for pan_pos in pan_pos_cfg:
            self._paned_window.sashpos(i, pan_pos)
            i += 1

    def _save_pw_pos(self):
        pan_pos_cfg = []
        for pan_id in range(2):
            pan_pos_cfg.append(int(self._paned_window.sashpos(pan_id)))
        print(pan_pos_cfg)
        guiCfg = POPT_CFG.load_guiPARM_main()
        guiCfg['gui_aprs_text_pan_pos'] = tuple(pan_pos_cfg)
        POPT_CFG.save_guiPARM_main(guiCfg)
    """
    ################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    ################################
    def update_aprs_msg(self, aprs_pack):
        if aprs_pack is None:
            self._update_tree()
        elif 'message' == aprs_pack.get('format', ''):
            self._update_tree()
            if (aprs_pack.get('from', '') == self._chat_address[0]
                and aprs_pack.get('addresse', '') == self._sender_var.get()) \
                    or (aprs_pack.get('addresse', '') == self._chat_address[0]
                        and aprs_pack.get('from', '') == self._sender_var.get()):
                self._build_new_chat_fm_chat_address()
        elif 'bulletin' == aprs_pack['format']:
            self._update_tree()

    ################################
    def _update_tree(self):
        self._aprs_pn_msg = list(self._aprs_ais.aprs_msg_pool['message'])
        self._aprs_pn_msg.reverse()

        for i in self._messages_treeview.get_children():
            self._messages_treeview.delete(i)

        for form_msg in self._aprs_pn_msg:
            if all((
                form_msg['addresse'] == self._sender_var.get(),
                form_msg['from'] == self._chat_address[0]
            )):
                tag = 'is_chat'
            elif form_msg['addresse'] in POPT_CFG.get_stat_CFG_keys() \
                    or form_msg['from'] in POPT_CFG.get_stat_CFG_keys()\
                    or self._aprs_ais.is_cq_call(form_msg['addresse']):
                tag = 'is_own'
            else:
                tag = 'not_own'

            tree_data = (
                     f"{form_msg['rx_time'].strftime('%d/%m/%y %H:%M:%S')}",
                     f"{form_msg.get('port_id', '-')}",
                     f"{form_msg['from']}",
                     f"{form_msg['addresse']}",
                     f"{form_msg.get('via', '')}",
                     f"{'>'.join(form_msg.get('path', []))}",
                     f"{form_msg.get('msgNo', '')}",
                     f"{form_msg.get('message_text', '')}",
                 )
            if hasattr(self._aprs_ais, 'get_symbol_fm_node_tab'):
                symbol = self._aprs_ais.get_symbol_fm_node_tab(form_msg.get('from'))
                image  = self._aprs_icon_tab.get(symbol, None)
            else:
                image = None
            if image:
                self._messages_treeview.insert('', 'end', values=tree_data, tags=tag, image=image)
            else:
                self._messages_treeview.insert('', 'end', values=tree_data, tags=tag)

    def _update_bl_tree(self):
        self._aprs_bl_msg = list(self._aprs_ais.aprs_msg_pool['bulletin'])
        self._aprs_bl_msg.reverse()

        for i in self._bl_messages_treeview.get_children():
            self._bl_messages_treeview.delete(i)
        tree_data = []
        for form_msg in self._aprs_bl_msg:

            tree_data.append(
                ((
                     f"{form_msg['rx_time'].strftime('%d/%m/%y %H:%M:%S')}",
                     f"{form_msg.get('port_id', '-')}",
                     f"{form_msg['from']}",
                     f"{form_msg['to']}",
                     f"{form_msg.get('via', '')}",
                     f"{'>'.join(form_msg.get('path', []))}",
                     f"{form_msg.get('bid', '')}",
                     f"{form_msg.get('message_text', '')}",
                 ), """tag""")
            )

        for ret_ent in tree_data:
            self._bl_messages_treeview.insert('', 'end', values=ret_ent[0],)

    def update_spooler_tree(self):
        if not self._init_done:
            return
        for i in self._spooler_treeview.get_children():
            self._spooler_treeview.delete(i)
        #self.update()
        tree_data = []
        sp_buff: dict = self._aprs_ais.get_spooler_buffer()
        for msg_no, pack in sp_buff.items():
            if not pack['send_timer']:
                tx_timer = pack['send_timer']
            else:
                tx_timer = max(round(pack['send_timer'] - time.time()), 0)
            tree_data.append((
                f"{pack['address_str']}",
                f"{pack['port_id']}",
                f"{pack['msgNo']}",
                f"{pack['N']}",
                f"{tx_timer}",
            ))
        for ret_ent in tree_data:
            self._spooler_treeview.insert('', tk.END, values=ret_ent)

    def _on_key_release_inp_txt(self, event=None):
        ind = str(int(float(self._out_text.index(tk.INSERT)))) + '.0'
        old_text = self._out_text.get(ind,  self._out_text.index(tk.INSERT))
        text = convert_umlaute_to_ascii(old_text)
        text = zeilenumbruch(text, max_zeichen=67, umbruch='\n')
        if text != old_text:
            self._out_text.delete(ind,  self._out_text.index(tk.INSERT))
            self._out_text.insert(tk.INSERT, text)
        text_size = self._out_text.get(0.0, self._out_text.index(tk.INSERT)).split('\n')
        self._char_counter_var.set(f"{67 - len(text_size[-1])}/{len(text_size)}")

    def _entry_selected(self, event=None):
        selected_iid = self._messages_treeview.selection()
        if not selected_iid:
            return
        self._antwort_pack  = {}
        selected_iid        = selected_iid[0]
        current_idx         = self._messages_treeview.index(selected_iid)
        self._antwort_pack  = copy.deepcopy(self._aprs_pn_msg[current_idx])
        if self._antwort_pack.get('msgNo', False):
            self._with_ack_var.set(True)
        else:
            self._with_ack_var.set(False)
        self._get_chat_address()
        self._build_chat_fm_selected(current_idx)
        self._msg_from_var.set(value=self._get_msg_from_str())
        self._update_tree()

    def _get_chat_address(self):
        from_call = str (self._antwort_pack.get('addresse', ''))
        to_call   = str (self._antwort_pack.get('from', ''))
        path      = list(self._antwort_pack.get('path', []))
        port      = str (self._antwort_pack.get('port_id', ''))

        for call in list(path):
            if any((
                    call.startswith('WIDE'),
                    call.startswith('q'),
                    call.startswith('TCPIP'),
                   )):
                path.remove(call)

        if from_call == to_call:
            self._msg_to_var.set(value=f"{self._getTabStr('to')}: -----   via: -----")
            self._chat_address = ('', [])
            return
        if from_call in POPT_CFG.get_stat_CFG_keys():
            path.reverse()
        elif to_call in POPT_CFG.get_stat_CFG_keys():
            tmp         = from_call
            from_call   = to_call
            to_call     = tmp
        else:
            path.reverse()
            self._msg_to_var.set(value=f"{self._getTabStr('to')}: {to_call}   via: {' > '.join(path)}")
            self._port_var.set(value=f"Port: {port}")
            self._chat_address = (to_call, path)
            return

        self._msg_to_var.set(value=f"{self._getTabStr('to')}: {to_call}   via: {' > '.join(path)}")
        self._port_var.set(value=f"Port: {port}")
        self._chat_address = (to_call, path)
        self._sender_var.set(from_call)

    def _build_chat_fm_selected(self, current_idx):
        msg_id = f"{self._aprs_pn_msg[current_idx].get('from', '')}-{self._aprs_pn_msg[current_idx].get('addresse', '')}"
        self._dbl_pack = []
        self._selected_message_text.config(state='normal')
        self._selected_message_text.delete(0.0, tk.END)
        self._selected_message_text.config(state='disabled')

        for pack_msg in self._aprs_pn_msg[current_idx:][::-1]:
            if f"{pack_msg.get('from', '')}-{pack_msg.get('addresse', '')}" == msg_id \
            or f"{pack_msg.get('addresse', '')}-{pack_msg.get('from', '')}" == msg_id:
                self._build_chat_fm_packet(pack_msg)

    def _build_new_chat_fm_chat_address(self):
        self._dbl_pack = []
        self._selected_message_text.config(state='normal')
        self._selected_message_text.delete(0.0, tk.END)
        self._selected_message_text.config(state='disabled')

        for aprs_pack in self._aprs_pn_msg[::-1]:
            if (aprs_pack.get('from', '') == self._chat_address[0]
                and aprs_pack.get('addresse', '') == self._sender_var.get()) \
                    or (aprs_pack.get('addresse', '') == self._chat_address[0]
                        and aprs_pack.get('from', '') == self._sender_var.get()):
                self._build_chat_fm_packet(aprs_pack)

    def _build_chat_fm_packet(self, aprs_pack: dict):
        msg_id = f"{aprs_pack.get('from', '')}-{aprs_pack.get('addresse', '')}"
        msg = ''
        if aprs_pack in self._dbl_pack:
            return
        msg_nr = aprs_pack.get('msgNo', '')
        if (msg_nr, msg_id) in self._dbl_pack:
            return
        self._dbl_pack.append(aprs_pack)
        if msg_nr:
            self._dbl_pack.append((msg_nr, msg_id))
        msg += f"Time: {aprs_pack['rx_time'].strftime('%d/%m/%y %H:%M:%S')}".ljust(28)
        if msg_nr != '':
            msg += f"Msg#: {msg_nr}\n"
        else:
            msg += '\n'
        msg += f"Path: {' > '.join(aprs_pack.get('path', []))}\n"
        msg += f"From: {aprs_pack.get('from', '')}({aprs_pack.get('distance', -1)}km)".ljust(22)
        msg += f"Via : {str(aprs_pack.get('via', '')).ljust(9)}  Port: {aprs_pack.get('port_id', '')}\n"

        msg_text = tk_filter_bad_chars(aprs_pack.get('message_text', '')) + '\n\n'

        tag_ind_1 = self._selected_message_text.index(tk.INSERT)
        self._selected_message_text.config(state='normal')
        self._selected_message_text.insert(tk.END, msg)
        self._selected_message_text.tag_add('header', tag_ind_1, tk.INSERT)
        self._selected_message_text.insert(tk.END, msg_text)
        self._selected_message_text.config(state='disabled')
        self._selected_message_text.see(tk.END)

    def _send_aprs_msg(self, event=None):
        msg = self._out_text.get(0.0, tk.END)[:-1]
        while msg.endswith('\n'):
            msg = msg[:-1]
        with_ack                        = bool(self._with_ack_var.get())
        self._antwort_pack['from']      = str( self._sender_var.get())
        self._antwort_pack['addresse']  = str( self._chat_address[0])
        self._antwort_pack['path']      = list(self._chat_address[1])
        if not all((self._antwort_pack['from'], self._antwort_pack['addresse'])):
            return
        if self._aprs_ais.send_aprs_text_msg(dict(self._antwort_pack), msg, with_ack):
            self._out_text.delete(0.0, tk.END)
            self._char_counter_var.set("67/0")

    def set_new_chat(self, packet: dict):
        """ Called fm guiAPRSnewMSG.py._send_message() """
        self._antwort_pack = packet
        to_call     = str(packet.get('addresse', ''))
        from_call   = str(packet.get('from', ''))
        path        = list(packet.get('path', []))

        if from_call == to_call:
            self._msg_to_var.set(value=f"{self._getTabStr('to')}: -----   via: -----")
            self._chat_address = ('', [])
            return

        self._msg_to_var.set(value=f"{self._getTabStr('to')}: {to_call}   via: {' > '.join(path)}")
        self._chat_address = (to_call, path)
        self._sender_var.set(from_call)

    ###########################################
    def _btn_close(self):
        self._destroy_win()

    def _btn_del_spooler(self):
        if self._aprs_ais is not None:
            if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                      message=self._getTabStr('msg_box_delete_data_msg'),
                                      parent=self):
                self._aprs_ais.del_spooler()

    def _btn_reset_spooler(self):
        if self._aprs_ais is not None:
            self._aprs_ais.reset_spooler()

    def _btn_new_msg(self):
        if self.new_msg_win is None:
            NewMessageWindow(self)

    def _btn_del_all_pn_msg(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'),
                                  parent=self):
            self._aprs_ais.aprs_msg_pool['message'] = []
            self._update_tree()

    def _btn_del_all_bl_msg(self):
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'),
                                  parent=self):
            self._aprs_ais.aprs_msg_pool['bulletin'] = []
            self._update_bl_tree()

    def _destroy_win(self):
        # self._save_pw_pos()
        if hasattr(self.new_msg_win, 'destroy_win'):
            self.new_msg_win.destroy_win()
        self._root_cl.aprs_pn_msg_win = None
        self.destroy()
