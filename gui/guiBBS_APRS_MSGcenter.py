import logging
import tkinter as tk
from tkinter import ttk, scrolledtext

from ax25.ax25InitPorts import PORT_HANDLER
from constant import FONT
from string_tab import STR_TABLE

logger = logging.getLogger(__name__)


class MSG_Center(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        ###################################
        # Vars
        self._bbs_obj = PORT_HANDLER.get_bbs()
        self._sort_rev = False
        self._last_sort_col = {}
        self._selected_BID = ''
        self._text_size = int(root_win.text_size)
        self._text_size_tabs = 10
        ###################################
        self.title(STR_TABLE['msg_center'][self._root_win.language])
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1250x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        """
        btn_frame = tk.Frame(self, background='blue', height=10)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tk.Button(btn_frame, text='test').pack(side=tk.LEFT, expand=False)
        """
        self._sort_rev = False
        ####################
        self._init_Menu()
        ######################################################################
        # APRS/BBS TABS
        upper_frame = tk.Frame(self, )
        upper_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_type = ttk.Notebook(
            upper_frame,
            padding=5,
        )
        self._tabControl_type.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        BBS_tab_frame = tk.Frame(self)
        APRS_tab_frame = tk.Frame(self)
        BBS_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        APRS_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_type.add(BBS_tab_frame, text='PMS', padding=8)
        self._tabControl_type.add(APRS_tab_frame, text='APRS', padding=8)
        ################################################
        # APRS-TAB
        self._tabControl = ttk.Notebook(
            APRS_tab_frame,
        )
        self._tabControl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tab_PN = ttk.Frame(self._tabControl)
        tab_BL = ttk.Frame(self._tabControl)
        tab_OUT = ttk.Frame(self._tabControl)
        self._tabControl.add(tab_PN, text='Private')
        self._tabControl.add(tab_BL, text='Bulletin')
        self._tabControl.add(tab_OUT, text='Gesendet')
        # TODO APRS
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ################################################
        # BBS-TAB
        self._tabControl = ttk.Notebook(
            BBS_tab_frame,
        )
        self._tabControl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tab_PN = ttk.Frame(self._tabControl)
        tab_BL = ttk.Frame(self._tabControl)
        tab_OUT = ttk.Frame(self._tabControl)
        tab_SAVE = ttk.Frame(self._tabControl)
        self._tabControl.add(tab_PN, text='Private')
        self._tabControl.add(tab_BL, text='Bulletin')
        self._tabControl.add(tab_OUT, text='Gesendet')
        self._tabControl.add(tab_SAVE, text='Gespeichert')

        ######################################################
        # ######### BBS/PN
        pn_pan_frame = tk.Frame(tab_PN)
        pn_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        _pw_pn = ttk.PanedWindow(pn_pan_frame, orient=tk.VERTICAL)

        top_f = tk.Frame(_pw_pn)
        lower_f_main = tk.Frame(_pw_pn)
        lower_f_top = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        _pw_pn.add(top_f, weight=1)
        _pw_pn.add(lower_f_main, weight=1)
        _pw_pn.pack(fill=tk.BOTH, expand=True)
        ########################
        # ## top_f / Msg Table
        self._pn_tree = None
        self._init_pn_tree(top_f)
        self._pn_tree_data = []
        self._pn_data = []
        self._update_PN_tree_data()

        ########################
        self._var_pn_from_label = tk.StringVar(self, '')
        self._var_pn_to_label = tk.StringVar(self, '')
        self._var_pn_subj_label = tk.StringVar(self, '')
        self._var_pn_time_label = tk.StringVar(self, '')
        self._var_pn_bid_label = tk.StringVar(self, '')
        # ## lower_f_top / MSG Header ect.
        self._pn_text = None
        self._init_pn_lower_frame(lower_f_top)

        #################################################
        # ######### BBS/BL
        _pw_bl_hor = tk.PanedWindow(tab_BL, orient=tk.HORIZONTAL)
        _pw_bl_hor.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(_pw_bl_hor)
        bl_pan_frame = tk.Frame(_pw_bl_hor)

        _pw_bl_hor.add(left_frame, width=140)
        _pw_bl_hor.add(bl_pan_frame, )
        ###################
        _pw_bl = ttk.PanedWindow(bl_pan_frame, orient=tk.VERTICAL)
        top_f = tk.Frame(_pw_bl)
        lower_f_main = tk.Frame(_pw_bl)
        lower_f_lower = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_lower.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        _pw_bl.add(top_f, weight=1)
        _pw_bl.add(lower_f_main, weight=1)
        _pw_bl.pack(fill=tk.BOTH, expand=True)
        ########################
        # LEFT TAB Category's
        self._bl_cat_tree = None
        self._bl_cat_filter = ''
        self._bl_cat_tree_data = []
        self._init_bl_left_cat_tab(left_frame)
        ########################
        # ## top_f / Msg Table
        self._bl_tree = None
        self._init_bl_tree(top_f)
        self._bl_tree_data = []
        self._bl_data = []
        self._update_BL_tree_data()
        ##############
        # ## lower_f_top / MSG Header ect.
        self._var_bl_from_label = tk.StringVar(self, '')
        self._var_bl_to_label = tk.StringVar(self, '')
        self._var_bl_subj_label = tk.StringVar(self, '')
        self._var_bl_time_label = tk.StringVar(self, '')
        self._var_bl_bid_label = tk.StringVar(self, '')
        # ## lower_f_lower / Msg Text
        self._bl_text = None
        self._init_bl_lower_frame(lower_f_lower)

        ######################################################
        # ######### BBS/OUT
        out_pan_frame = tk.Frame(tab_OUT)
        out_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        _pw_out = ttk.PanedWindow(out_pan_frame, orient=tk.VERTICAL)

        top_f = tk.Frame(_pw_out)
        lower_f_main = tk.Frame(_pw_out)
        lower_f_top = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        _pw_out.add(top_f, weight=1)
        _pw_out.add(lower_f_main, weight=1)
        _pw_out.pack(fill=tk.BOTH, expand=True)
        ########################
        # ## top_f / Msg Table
        self._out_tree = None
        self._init_out_tree(top_f)
        self._out_tree_data = []
        self._out_data = []
        self._update_OUT_tree_data()

        ########################
        self._var_out_from_label = tk.StringVar(self, '')
        self._var_out_to_label = tk.StringVar(self, '')
        self._var_out_subj_label = tk.StringVar(self, '')
        self._var_out_time_label = tk.StringVar(self, '')
        self._var_out_bid_label = tk.StringVar(self, '')
        # ## lower_f_top / MSG Header ect.
        self._out_text = None
        self._init_out_lower_frame(lower_f_top)

        ###############################################
        #
        self.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())

    def _init_Menu(self):
        _menubar = tk.Menu(self, tearoff=False)
        self.config(menu=_menubar)
        _MenuVerb = tk.Menu(_menubar, tearoff=False)
        _MenuVerb.add_command(label='New Mail')
        _menubar.add_cascade(label='Mail', menu=_MenuVerb, underline=0)

    # PN TAB
    def _init_pn_tree(self, root_frame):
        columns = (
            'Neu',
            'Betreff',
            'Von',
            'Datum',
        )

        self._pn_tree = ttk.Treeview(root_frame, columns=columns, show='headings', height=25)
        self._pn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._pn_tree.yview)
        self._pn_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._pn_tree.heading('Neu', text='Neu', command=lambda: self._sort_entry('Neu', self._pn_tree))
        self._pn_tree.heading('Betreff', text='Betreff', command=lambda: self._sort_entry('Betreff', self._pn_tree))
        self._pn_tree.heading('Von', text='Von', command=lambda: self._sort_entry('Von', self._pn_tree))
        self._pn_tree.heading('Datum', text='Datum', command=lambda: self._sort_entry('Datum', self._pn_tree))
        self._pn_tree.column("Neu", anchor=tk.CENTER, stretch=tk.NO, width=40)
        self._pn_tree.column("Betreff", anchor='w', stretch=tk.YES, width=190)
        self._pn_tree.column("Von", anchor='w', stretch=tk.YES, width=190)
        self._pn_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        self._pn_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._pn_tree.bind('<<TreeviewSelect>>', self._PN_entry_selected)

    def _init_pn_lower_frame(self, root_frame):
        btn_frame = tk.Frame(root_frame, height=30)
        header_frame = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        tk.Button(btn_frame, text='Speichern').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Löschen').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Weiterleiten').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Antworten').pack(side=tk.RIGHT, expand=False)

        from_label = tk.Label(header_frame, textvariable=self._var_pn_from_label)
        to_label = tk.Label(header_frame, textvariable=self._var_pn_to_label)
        subject_label = tk.Label(header_frame, textvariable=self._var_pn_subj_label)
        time_label = tk.Label(header_frame, textvariable=self._var_pn_time_label)
        bid_label = tk.Label(header_frame, textvariable=self._var_pn_bid_label)
        from_label.place(x=2, y=0)
        to_label.place(x=2, y=25)
        subject_label.place(x=2, y=50)
        time_label.place(relx=0.98, y=36, anchor=tk.E)
        bid_label.place(relx=0.98, y=61, anchor=tk.E)

        # ## lower_f_lower / Msg Text
        self._pn_text = scrolledtext.ScrolledText(root_frame,
                                                  font=(FONT, self._text_size),
                                                  bd=0,
                                                  borderwidth=0,
                                                  background='black',
                                                  foreground='white',
                                                  state="disabled",
                                                  )
        self._pn_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # BL TAB
    def _init_bl_tree(self, root_frame):
        columns = (
            'Neu',
            'Betreff',
            'Von',
            'An',
            'vert',
            'Datum',
        )

        self._bl_tree = ttk.Treeview(root_frame, columns=columns, show='headings', height=25)
        self._bl_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._pn_tree.yview)
        self._bl_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._bl_tree.heading('Neu', text='Neu', command=lambda: self._sort_entry('Neu', self._bl_tree))
        self._bl_tree.heading('Betreff', text='Betreff', command=lambda: self._sort_entry('Betreff', self._bl_tree))
        self._bl_tree.heading('Von', text='Von', command=lambda: self._sort_entry('Von', self._bl_tree))
        self._bl_tree.heading('An', text='An', command=lambda: self._sort_entry('An', self._bl_tree))
        self._bl_tree.heading('vert', text='@', command=lambda: self._sort_entry('vert', self._bl_tree))
        self._bl_tree.heading('Datum', text='Datum', command=lambda: self._sort_entry('Datum', self._bl_tree))
        self._bl_tree.column("Neu", anchor=tk.CENTER, stretch=tk.NO, width=40)
        self._bl_tree.column("Betreff", anchor='w', stretch=tk.YES, width=270)
        self._bl_tree.column("Von", anchor='w', stretch=tk.YES, width=180)
        self._bl_tree.column("An", anchor='w', stretch=tk.YES, width=100)
        self._bl_tree.column("vert", anchor='w', stretch=tk.NO, width=50)
        self._bl_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        self._bl_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._bl_tree.bind('<<TreeviewSelect>>', self._BL_entry_selected)

    def _init_bl_left_cat_tab(self, root_frame):
        columns = (
            'cat'
        )
        self._bl_cat_tree = ttk.Treeview(root_frame, columns=columns, show="tree")
        self._bl_cat_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._bl_cat_tree.yview)
        self._bl_cat_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self._bl_cat_tree.column("#0", width=0, stretch=False)
        self._bl_cat_tree.column("cat", anchor='w', stretch=True, width=0)

        self._bl_cat_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_cat_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._bl_cat_tree.bind('<<TreeviewSelect>>', self._CAT_entry_selected)

    def _init_bl_lower_frame(self, root_frame):
        btn_frame = tk.Frame(root_frame, height=30)
        header_frame = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        tk.Button(btn_frame, text='Speichern').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Löschen').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Weiterleiten').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Antworten').pack(side=tk.RIGHT, expand=False)
        # Header Frame
        from_label = tk.Label(header_frame, textvariable=self._var_bl_from_label)
        to_label = tk.Label(header_frame, textvariable=self._var_bl_to_label)
        subject_label = tk.Label(header_frame, textvariable=self._var_bl_subj_label)
        time_label = tk.Label(header_frame, textvariable=self._var_bl_time_label)
        bid_label = tk.Label(header_frame, textvariable=self._var_bl_bid_label)
        from_label.place(x=2, y=0)
        to_label.place(x=2, y=25)
        subject_label.place(x=2, y=50)
        time_label.place(relx=0.98, y=36, anchor=tk.E)
        bid_label.place(relx=0.98, y=61, anchor=tk.E)

        self._bl_text = scrolledtext.ScrolledText(root_frame,
                                                  font=(FONT, self._text_size),
                                                  bd=0,
                                                  background='black',
                                                  foreground='white',
                                                  borderwidth=0,
                                                  state="disabled",
                                                  )
        self._bl_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # OUT TAB
    def _init_out_tree(self, root_frame):
        columns = (
            'gesendet',
            'Betreff',
            'An',
            'fwd_bbs',
            'typ',
            'flag',
            'Datum',
        )

        self._out_tree = ttk.Treeview(root_frame, columns=columns, show='headings', height=25)
        self._out_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._out_tree.yview)
        self._out_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._out_tree.heading('gesendet', text='  ', command=lambda: self._sort_entry('gesendet', self._out_tree))
        self._out_tree.heading('Betreff', text='Betreff', command=lambda: self._sort_entry('Betreff', self._out_tree))
        self._out_tree.heading('An', text='An', command=lambda: self._sort_entry('An', self._out_tree))
        self._out_tree.heading('fwd_bbs', text='An BBS', command=lambda: self._sort_entry('fwd_bbs', self._out_tree))
        self._out_tree.heading('typ', text='TYP', command=lambda: self._sort_entry('typ', self._out_tree))
        self._out_tree.heading('flag', text='Flag', command=lambda: self._sort_entry('flag', self._out_tree))
        self._out_tree.heading('Datum', text='TX-Time', command=lambda: self._sort_entry('Datum', self._out_tree))
        self._out_tree.column("gesendet", anchor=tk.CENTER, stretch=tk.NO, width=40)
        self._out_tree.column("Betreff", anchor='w', stretch=tk.YES, width=230)
        self._out_tree.column("An", anchor='w', stretch=tk.YES, width=100)
        self._out_tree.column("fwd_bbs", anchor='w', stretch=tk.YES, width=60)
        self._out_tree.column("typ", anchor='w', stretch=tk.NO, width=45)
        self._out_tree.column("flag", anchor='w', stretch=tk.NO, width=45)
        self._out_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        self._out_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._out_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._out_tree.bind('<<TreeviewSelect>>', self._OUT_entry_selected)

    def _init_out_lower_frame(self, root_frame):
        btn_frame = tk.Frame(root_frame, height=30)
        header_frame = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        # tk.Button(btn_frame, text='Speichern').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Löschen').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Weiterleiten').pack(side=tk.RIGHT, expand=False)
        # tk.Button(btn_frame, text='Antworten').pack(side=tk.RIGHT, expand=False)

        from_label = tk.Label(header_frame, textvariable=self._var_out_from_label)
        to_label = tk.Label(header_frame, textvariable=self._var_out_to_label)
        subject_label = tk.Label(header_frame, textvariable=self._var_out_subj_label)
        time_label = tk.Label(header_frame, textvariable=self._var_out_time_label)
        bid_label = tk.Label(header_frame, textvariable=self._var_out_bid_label)
        from_label.place(x=2, y=0)
        to_label.place(x=2, y=25)
        subject_label.place(x=2, y=50)
        time_label.place(relx=0.98, y=36, anchor=tk.E)
        bid_label.place(relx=0.98, y=61, anchor=tk.E)

        # ## lower_f_lower / Msg Text
        self._out_text = scrolledtext.ScrolledText(root_frame,
                                                   font=(FONT, self._text_size),
                                                   bd=0,
                                                   borderwidth=0,
                                                   background='black',
                                                   foreground='white',
                                                   state="disabled",
                                                   )
        self._out_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    ################################
    # PN
    def _update_PN_tree_data(self):
        self._get_PN_data()
        self._format_PN_tree_data()
        self._update_PN_tree()

    def _get_PN_data(self):
        self._pn_data = list(self._bbs_obj.get_pn_msg_tab())

    def _get_PN_MSG_data(self, bid):
        return list(self._bbs_obj.get_pn_msg_fm_BID(bid))

    def _format_PN_tree_data(self):
        self._pn_tree_data = []
        for el in self._pn_data:
            _from_call = f"{el[1]}"
            if el[2]:
                _from_call += f"@{el[2]}"
            _new = ''
            if int(el[6]):
                _new = '✉'
            self._pn_tree_data.append((
                f'{_new}',
                f'{el[4]}',
                f'{_from_call}',
                f'{el[5]}',
                f'{el[0]}',  # BID
            ))

    def _update_PN_tree(self):
        for i in self._pn_tree.get_children():
            self._pn_tree.delete(i)
        for ret_ent in self._pn_tree_data:
            if ret_ent[0]:
                tag = 'neu'
            else:
                tag = 'alt'
            self._pn_tree.insert('', tk.END, values=ret_ent[:-1], tags=(tag, ret_ent[-1]))

    def _PN_entry_selected(self, event=None):
        bid = ''
        for selected_item in self._pn_tree.selection():
            item = self._pn_tree.item(selected_item)
            bid = item['tags'][1]
        if bid:
            self._selected_BID = str(bid)
            self._PN_show_msg_fm_BID(bid)
            self._update_PN_tree_data()
            self._update_sort_entry(self._pn_tree)

    def _PN_show_msg_fm_BID(self, bid):
        if bid:
            self._pn_text.configure(state='normal')
            self._pn_text.delete('1.0', tk.END)
            db_data = self._get_PN_MSG_data(bid)
            if db_data:
                db_data = db_data[0]
                _bid = db_data[0]
                _from = db_data[1]
                _from_bbs = db_data[2]
                _to = db_data[3]  # Cat
                _to_bbs = db_data[4]  # Verteiler
                _subj = db_data[6]
                _msg = db_data[8]
                # _path = _db_data[9]
                _time = db_data[10]
                # _size = len(_msg)
                # TODO Change Decoding
                _msg = _msg.decode('UTF-8', 'ignore')
                _msg = str(_msg).replace('\r', '\n')
                if _from_bbs:
                    _from = _from + ' @ ' + _from_bbs
                if _to_bbs:
                    _to = _to + ' @ ' + _to_bbs

                self._var_pn_from_label.set(f"From: {_from}")
                self._var_pn_to_label.set(f"To    : {_to}")
                self._var_pn_subj_label.set(f"{_subj}")
                self._var_pn_time_label.set(f"{_time}")
                self._var_pn_bid_label.set(f"BID: {_bid}")

                self._pn_text.insert('1.0', _msg)

            self._pn_text.configure(state='disabled')

    ###########
    # Bulletin
    def _update_BL_tree_data(self):
        self._get_BL_data()
        self._format_BL_tree_data()
        self._update_BL_tree()
        self._update_CAT_tree()

    def _get_BL_data(self):
        self._bl_data = list(self._bbs_obj.get_bl_msg_tab())

    def _get_BL_MSG_data(self, bid):
        return list(self._bbs_obj.get_bl_msg_fm_BID(bid))

    def _format_BL_tree_data(self):
        self._bl_tree_data = []
        self._bl_cat_tree_data = []
        _new_tr = {}
        for el in self._bl_data:
            _from_call = f"{el[1]}"
            if el[2]:
                _from_call += f"@{el[2]}"
            _new = ''
            if int(el[7]):
                _new = '✉'
                _new_tr[el[3]] = True
            if not self._bl_cat_filter or self._bl_cat_filter == el[3]:
                self._bl_tree_data.append((
                    f'{_new}',
                    f'{el[5]}',
                    f'{_from_call}',
                    f'{el[3]}',  # Cat
                    f'{el[4]}',
                    f'{el[6]}',
                    f'{el[0]}',  # BID
                ))
        # Category Tab
        _any_tr = False
        for el in self._bl_data:
            _tr = _new_tr.get(el[3], False)
            if _tr:
                _any_tr = True
            if (_tr, el[3]) not in self._bl_cat_tree_data:
                self._bl_cat_tree_data.append((_tr, el[3]))

        self._bl_cat_tree_data.sort(key=lambda x: x[1])
        self._bl_cat_tree_data = [(_any_tr, 'ALL*')] + self._bl_cat_tree_data

    def _update_BL_tree(self):
        for i in self._bl_tree.get_children():
            self._bl_tree.delete(i)
        for ret_ent in self._bl_tree_data:
            if ret_ent[0]:
                tag = 'neu'
            else:
                tag = 'alt'
            self._bl_tree.insert('', tk.END, values=ret_ent[:-1], tags=(tag, ret_ent[-1]))
        self._update_sort_entry(self._bl_tree)

    def _BL_entry_selected(self, event=None):
        bid = ''
        for selected_item in self._bl_tree.selection():
            item = self._bl_tree.item(selected_item)
            bid = item['tags'][1]
        if bid:
            self._selected_BID = str(bid)
            self._BL_show_msg_fm_BID(bid)
            self._update_BL_tree_data()
            self._update_sort_entry(self._bl_tree)

    def _BL_show_msg_fm_BID(self, bid):
        if bid:
            self._bl_text.configure(state='normal')
            self._bl_text.delete('1.0', tk.END)
            db_data = self._get_BL_MSG_data(bid)
            if db_data:
                db_data = db_data[0]
                _bid = db_data[0]
                _from = db_data[1]
                _from_bbs = db_data[2]
                _to = db_data[3]  # Cat
                _to_bbs = db_data[4]  # Verteiler
                _subj = db_data[6]
                _msg = db_data[8]
                # _path = _db_data[9]
                _time = db_data[10]
                # _size = len(_msg)
                # TODO Change Decoding
                _msg = _msg.decode('UTF-8', 'ignore')
                _msg = str(_msg).replace('\r', '\n')
                if _from_bbs:
                    _from = _from + ' @ ' + _from_bbs
                if _to_bbs:
                    _to = _to + ' @ ' + _to_bbs

                self._var_bl_from_label.set(f"From: {_from}")
                self._var_bl_to_label.set(f"To    : {_to}")
                self._var_bl_subj_label.set(f"{_subj}")
                self._var_bl_time_label.set(f"{_time}")
                self._var_bl_bid_label.set(f"BID: {_bid}")

                # self._bl_text.insert(tk.INSERT, try_decode(_msg, ignore=True))
                self._bl_text.insert('1.0', _msg)
            self._bl_text.configure(state='disabled')

    ###################
    # Bulletin Category
    def _update_CAT_tree(self):
        for i in self._bl_cat_tree.get_children():
            self._bl_cat_tree.delete(i)
        for ret_ent in self._bl_cat_tree_data:
            if ret_ent[0]:
                tag = 'neu'
            else:
                tag = 'alt'
            self._bl_cat_tree.insert('', tk.END, values=ret_ent[1], tags=(tag,))

    def _CAT_entry_selected(self, event=None):
        for selected_item in self._bl_cat_tree.selection():
            item = self._bl_cat_tree.item(selected_item)
            record = item['values']
            if record[0] == 'ALL*':
                self._bl_cat_filter = ''
            else:
                self._bl_cat_filter = str(record[0])
        self._update_BL_tree_data()

    ################################
    # OUT TAB
    def _update_OUT_tree_data(self):
        self._get_OUT_data()
        self._format_OUT_tree_data()
        self._update_OUT_tree()

    def _get_OUT_data(self):
        self._out_data = list(self._bbs_obj.get_fwd_q_tab())

    def _get_OUT_MSG_data(self, bid):
        return list(self._bbs_obj.get_out_msg_fm_BID(bid))

    def _format_OUT_tree_data(self):
        self._out_tree_data = []
        for el in self._out_data:
            _to_call = f"{el[3]}"
            if el[4]:
                _to_call += f"@{el[4]}"
            _fwd_done = ''
            if el[9] != 'F':
                _fwd_done = '✔'
            _tx_time = ''
            if el[10]:
                _tx_time = el[10]
            """
            'gesendet',
            'Betreff',
            'An',
            'fwd_bbs',
            'typ',
            'flag',
            'Datum',
            """
            self._out_tree_data.append((
                f'{_fwd_done}',
                f'{el[6]}',
                f'{_to_call}',
                f'{el[5]}',
                f'{el[8]}',
                f'{el[9]}',
                f'{_tx_time}',
                f'{el[0]}',  # BID
            ))

    def _update_OUT_tree(self):
        for i in self._out_tree.get_children():
            self._out_tree.delete(i)
        for ret_ent in self._out_tree_data:
            if not ret_ent[0]:
                tag = 'neu'
            else:
                tag = 'alt'
            self._out_tree.insert('', tk.END, values=ret_ent[:-1], tags=(tag, ret_ent[-1]))

    def _OUT_entry_selected(self, event=None):
        bid = ''
        for selected_item in self._out_tree.selection():
            item = self._out_tree.item(selected_item)
            bid = item['tags'][1]
        if bid:
            self._selected_BID = str(bid)
            self._OUT_show_msg_fm_BID(bid)
            # self._update_OUT_tree_data()
            # self._update_sort_entry(self._out_tree)

    def _OUT_show_msg_fm_BID(self, bid):
        if bid:
            self._out_text.configure(state='normal')
            self._out_text.delete('1.0', tk.END)
            db_data = self._get_OUT_MSG_data(bid)
            if db_data:
                db_data = db_data[0]
                _bid = db_data[1]
                _from = db_data[3]
                _from_bbs = db_data[4]
                _to = db_data[5]  # Cat
                _to_bbs = db_data[6]  # Verteiler
                _to_bbs_fwd = db_data[7]  # Verteiler
                _subj = db_data[9]
                _msg = db_data[11]
                # _path = _db_data[9]
                _time = db_data[12]
                # _size = len(_msg)
                # TODO Change Decoding
                _msg = _msg.decode('UTF-8', 'ignore')
                _msg = str(_msg).replace('\r', '\n')
                if _from_bbs:
                    _from = _from + ' @ ' + _from_bbs
                if _to_bbs:
                    _to = _to + ' @ ' + _to_bbs

                _to += f' > {_to_bbs_fwd}'

                self._var_out_from_label.set(f"From: {_from}")
                self._var_out_to_label.set(f"To    : {_to}")
                self._var_out_subj_label.set(f"{_subj}")
                self._var_out_time_label.set(f"{_time}")
                self._var_out_bid_label.set(f"BID: {_bid}")

                self._out_text.insert('1.0', _msg)

            self._out_text.configure(state='disabled')

    #####################################
    # Global
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        _tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        _tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        self._last_sort_col[tree] = col
        for index, (val, k) in enumerate(_tmp):
            tree.move(k, '', int(index))

    def _update_sort_entry(self, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        col = self._last_sort_col.get(tree, 'Datum')
        _tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        _tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        self._last_sort_col[tree] = col
        for index, (val, k) in enumerate(_tmp):
            tree.move(k, '', int(index))

    #####################################
    # GUI
    def _increase_textsize(self):
        self._text_size += 1
        self._text_size = max(self._text_size, 3)
        self._bl_text.configure(font=(FONT, self._text_size))
        self._pn_text.configure(font=(FONT, self._text_size))

    def _decrease_textsize(self):
        self._text_size -= 1
        self._text_size = max(self._text_size, 3)
        self._bl_text.configure(font=(FONT, self._text_size))
        self._pn_text.configure(font=(FONT, self._text_size))

    def _update_textsize_trees(self):
        # TODO
        self._bl_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._pn_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._bl_cat_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_cat_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

    def _close(self):
        self._bbs_obj = None
        self._root_win.MSG_Center = None
        self.destroy()
