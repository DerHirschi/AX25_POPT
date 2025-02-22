import tkinter as tk
from tkinter import ttk, scrolledtext

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from cfg.constant import FONT, ENCODINGS
from fnc.str_fnc import format_number, get_strTab
from gui.pms.guiBBS_newMSG import BBS_newMSG
from gui.guiMsgBoxes import save_file_dialog
from cfg.string_tab import STR_TABLE


class MSG_Center(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win  = root_win
        self._lang      = POPT_CFG.get_guiCFG_language()
        self._getTabStr = lambda str_k: get_strTab(str_k, self._lang)
        ###################################
        # Vars
        PORT_HANDLER.set_pmsMailAlarm(False)
        self._bbs_obj       = PORT_HANDLER.get_bbs()
        self._sort_rev      = False
        self._last_sort_col = {}
        self._selected_msg  = {
            'P': {},
            'B': {},
            'O': {},
            'S': {},
        }
        self._var_encoding      = tk.StringVar(self, 'UTF-8')
        self.text_size          = int(POPT_CFG.load_guiPARM_main().get('guiMsgC_parm_text_size', self._root_win.text_size))
        self._text_size_tabs    = 10
        self.newPMS_MSG_win     = self._root_win.newPMS_MSG_win
        ###################################
        self.title(STR_TABLE['msg_center'][self._lang])
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
        self._tabControl_type.pack(side=tk.TOP, fill=tk.BOTH, expand=True, )

        BBS_tab_frame = tk.Frame(self)
        APRS_tab_frame = tk.Frame(self)
        BBS_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        APRS_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_type.add(BBS_tab_frame, text='PMS', padding=8)
        self._tabControl_type.add(APRS_tab_frame, text='APRS', padding=8, state='disabled') # TODO
        ################################################
        # APRS-TAB
        self._tabControl = ttk.Notebook(
            APRS_tab_frame,
        )
        self._tabControl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tab_PN  = ttk.Frame(self._tabControl)
        tab_BL  = ttk.Frame(self._tabControl)
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
        self._tabControl.bind("<<NotebookTabChanged>>", self.on_bbsTab_select)
        tab_PN      = ttk.Frame(self._tabControl)
        tab_BL      = ttk.Frame(self._tabControl)
        tab_OUT     = ttk.Frame(self._tabControl)
        tab_SAVE    = ttk.Frame(self._tabControl)
        self._tabControl.add(tab_PN, text='Private')
        self._tabControl.add(tab_BL, text='Bulletin')
        self._tabControl.add(tab_OUT, text='Gesendet')
        self._tabControl.add(tab_SAVE, text='Gespeichert')

        ######################################################
        # ######### BBS/PN
        pn_pan_frame = tk.Frame(tab_PN)
        pn_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pw_pn = ttk.PanedWindow(pn_pan_frame, orient=tk.VERTICAL)

        top_f = tk.Frame(pw_pn)
        lower_f_main = tk.Frame(pw_pn)
        lower_f_top = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        pw_pn.add(top_f, weight=1)
        pw_pn.add(lower_f_main, weight=1)
        pw_pn.pack(fill=tk.BOTH, expand=True)
        ########################
        # ## top_f / Msg Table
        self._pn_tree       = None
        self._init_pn_tree(top_f)
        self._pn_tree_data  = []
        self._pn_data       = []
        self._update_PN_tree_data()
        ########################
        self._var_pn_from_label     = tk.StringVar(self, '')
        self._var_pn_to_label       = tk.StringVar(self, '')
        self._var_pn_subj_label     = tk.StringVar(self, '')
        self._var_pn_time_label     = tk.StringVar(self, '')
        self._var_pn_bid_label      = tk.StringVar(self, '')
        # self._var_pn_encoding     = tk.StringVar(self, 'UTF-8')
        self._var_pn_msg_size       = tk.StringVar(self, ' Size: --- Bytes')

        # ## lower_f_top / MSG Header ect.
        self._pn_text   = None
        self._init_pn_lower_frame(lower_f_top)
        self._init_pn_footer_frame(lower_f_top)

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
        # self._var_bl_encoding = tk.StringVar(self, 'UTF-8')
        self._var_bl_msg_size = tk.StringVar(self, ' Size: --- Bytes')
        # ## lower_f_lower / Msg Text
        self._bl_text = None
        self._init_bl_lower_frame(lower_f_lower)
        self._init_bl_footer_frame(lower_f_lower)

        ######################################################
        # ######### BBS/OUT
        out_pan_frame = tk.Frame(tab_OUT)
        out_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pw_out = ttk.PanedWindow(out_pan_frame, orient=tk.VERTICAL)

        top_f = tk.Frame(pw_out)
        lower_f_main = tk.Frame(pw_out)
        lower_f_top = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        pw_out.add(top_f, weight=1)
        pw_out.add(lower_f_main, weight=1)
        pw_out.pack(fill=tk.BOTH, expand=True)
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
        # self._var_out_encoding = tk.StringVar(self, 'UTF-8')
        self._var_out_msg_size = tk.StringVar(self, ' Size: --- Bytes')
        # ## lower_f_top / MSG Header ect.
        self._out_text = None
        self._init_out_lower_frame(lower_f_top)
        self._init_out_footer_frame(lower_f_top)
        ######################################################
        # ######### BBS/Drafts/Saved Msg
        pn_pan_frame = tk.Frame(tab_SAVE)
        pn_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pw_pn = ttk.PanedWindow(pn_pan_frame, orient=tk.VERTICAL)

        top_f = tk.Frame(pw_pn)
        lower_f_main = tk.Frame(pw_pn)
        lower_f_top = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        pw_pn.add(top_f, weight=1)
        pw_pn.add(lower_f_main, weight=1)
        pw_pn.pack(fill=tk.BOTH, expand=True)
        ########################
        # ## top_f / Msg Table
        self._sv_tree = None
        self._init_sv_tree(top_f)
        self._sv_tree_data = []
        self._sv_data = []
        self._update_SV_tree_data()
        ########################
        self._var_sv_from_label = tk.StringVar(self, '')
        self._var_sv_to_label = tk.StringVar(self, '')
        self._var_sv_subj_label = tk.StringVar(self, '')
        self._var_sv_time_label = tk.StringVar(self, '')
        self._var_sv_bid_label = tk.StringVar(self, '')
        self._var_sv_msg_size = tk.StringVar(self, ' Size: --- Bytes')

        # ## lower_f_top / MSG Header ect.
        self._sv_text = None
        self._init_sv_lower_frame(lower_f_top)
        self._init_sv_footer_frame(lower_f_top)

        ###############################################
        # Keybindings
        self.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())
        self.bind('<Control-c>', lambda event: self._copy_select())
        #####################
        # Get Settings fm CFG
        self._root_win.MSG_Center_win = self
        self._init_Vars_fm_Cfg()

    def _init_Menu(self):
        menubar = tk.Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = tk.Menu(menubar, tearoff=False)
        MenuVerb.add_command(label='Neu', command=lambda: self._open_newMSG_win())
        MenuVerb.add_separator()
        MenuVerb.add_command(label='Alles sofort senden', command=lambda: self._do_pms_autoFWD())
        menubar.add_cascade(label='Nachricht', menu=MenuVerb, underline=0)
        # ### Bearbeiten
        MenuEdit = tk.Menu(menubar, tearoff=False)
        MenuEdit.add_command(label='Alle als gelesen markieren',
                              command=self._set_all_to_oldMSG,
                              underline=0)
        MenuVerb.add_separator()
        MenuEdit.add_command(label=STR_TABLE['save_to_file'][self._lang],
                              command=self._save_msg_to_file,
                              underline=0)
        menubar.add_cascade(label=STR_TABLE['edit'][self._lang], menu=MenuEdit, underline=0)

    def _init_Vars_fm_Cfg(self):
        pass
        # self.text_size = int(POPT_CFG.get_guiCFG_main().get('guiMsgC_parm_text_size', self._root_win.text_size))

    def _save_Vars_to_Cfg(self):
        cfg = POPT_CFG.load_guiPARM_main()
        cfg['guiMsgC_parm_text_size'] = self.text_size

        POPT_CFG.save_guiPARM_main(cfg)

    # PN TAB
    def _init_pn_tree(self, root_frame):
        columns = (
            'Neu',
            'Betreff',
            'Von',
            'flag',
            'Datum',
        )

        self._pn_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
        self._pn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._pn_tree.yview)
        self._pn_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._pn_tree.heading('Neu',        text=self._getTabStr('new'), command=lambda: self._sort_entry('Neu', self._pn_tree))
        self._pn_tree.heading('Betreff',    text=self._getTabStr('subject'), command=lambda: self._sort_entry('Betreff', self._pn_tree))
        self._pn_tree.heading('Von',        text=self._getTabStr('from'), command=lambda: self._sort_entry('Von', self._pn_tree))
        self._pn_tree.heading('flag',      text='Flag', command=lambda: self._sort_entry('flag', self._pn_tree))
        self._pn_tree.heading('Datum',      text=self._getTabStr('date_time'), command=lambda: self._sort_entry('Datum', self._pn_tree))
        self._pn_tree.column("Neu", anchor=tk.CENTER, stretch=tk.NO, width=40)
        self._pn_tree.column("Betreff", anchor='w', stretch=tk.YES, width=190)
        self._pn_tree.column("Von", anchor='w', stretch=tk.YES, width=190)
        self._pn_tree.column("flag", anchor='w', stretch=tk.NO, width=60)
        self._pn_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        self._pn_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._pn_tree.bind('<<TreeviewSelect>>', self._PN_entry_selected)
        # self._pn_tree.get_children()

    def _init_pn_lower_frame(self, root_frame):
        btn_frame = tk.Frame(root_frame, height=30)
        header_frame = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        btn_frame_r = tk.Frame(btn_frame)
        btn_frame_l = tk.Frame(btn_frame)
        btn_frame_l.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        btn_frame_r.pack(side=tk.LEFT, expand=False, anchor='e')

        tk.Button(btn_frame_l,
                  text=self._getTabStr('new'),
                  command=lambda: self._open_newMSG_win()
                  ).pack(side=tk.LEFT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('delete'),
                  command=lambda: self._delete_msg()
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('save'),
                  # TODO cmd
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('forward'),
                  command=lambda: self._open_newMSG_win_forward('P')
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('Answer'),
                  command=lambda: self._open_newMSG_win_reply('P'),
                  ).pack(side=tk.RIGHT, expand=False)

        from_label      = tk.Label(header_frame, textvariable=self._var_pn_from_label)
        to_label        = tk.Label(header_frame, textvariable=self._var_pn_to_label)
        subject_label   = tk.Label(header_frame, textvariable=self._var_pn_subj_label)
        time_label      = tk.Label(header_frame, textvariable=self._var_pn_time_label)
        bid_label       = tk.Label(header_frame, textvariable=self._var_pn_bid_label)
        from_label.place(x=2, y=0)
        to_label.place(x=2, y=25)
        subject_label.place(x=2, y=50)
        time_label.place(relx=0.98, y=36, anchor=tk.E)
        bid_label.place(relx=0.98, y=61, anchor=tk.E)

        # ## lower_f_lower / Msg Text
        self._pn_text = scrolledtext.ScrolledText(root_frame,
                                                  font=(FONT, self.text_size),
                                                  bd=0,
                                                  height=3,
                                                  borderwidth=0,
                                                  background='black',
                                                  foreground='white',
                                                  state="disabled",
                                                  )
        self._pn_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _init_pn_footer_frame(self, root_frame):
        footer_frame = tk.Frame(root_frame, height=15)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        txt_encoding_ent = tk.OptionMenu(
            footer_frame,
            self._var_encoding,
            *ENCODINGS,
            command=self._update_PN_msg
        )
        txt_encoding_ent.configure(
            font=(None, 6),
            border=0,
            borderwidth=0,
            height=1
        )
        txt_encoding_ent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        tk.Label(footer_frame,
                 textvariable=self._var_pn_msg_size,
                 font=(None, 7),
                 ).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    # BL TAB
    def _init_bl_tree(self, root_frame):
        columns = (
            'Neu',
            'Betreff',
            'Von',
            'An',
            'vert',
            'flag',
            'Datum',
        )

        self._bl_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
        self._bl_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._bl_tree.yview)
        self._bl_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._bl_tree.heading('Neu', text=self._getTabStr('new'), command=lambda: self._sort_entry('Neu', self._bl_tree))
        self._bl_tree.heading('Betreff', text=self._getTabStr('subject'), command=lambda: self._sort_entry('Betreff', self._bl_tree))
        self._bl_tree.heading('Von', text=self._getTabStr('from'), command=lambda: self._sort_entry('Von', self._bl_tree))
        self._bl_tree.heading('An', text=self._getTabStr('to'), command=lambda: self._sort_entry('An', self._bl_tree))
        self._bl_tree.heading('vert', text='@', command=lambda: self._sort_entry('vert', self._bl_tree))
        self._bl_tree.heading('flag', text='Flag', command=lambda: self._sort_entry('flag', self._bl_tree))
        self._bl_tree.heading('Datum', text=self._getTabStr('date_time'), command=lambda: self._sort_entry('Datum', self._bl_tree))
        self._bl_tree.column("Neu", anchor=tk.CENTER, stretch=tk.NO, width=40)
        self._bl_tree.column("Betreff", anchor='w', stretch=tk.YES, width=270)
        self._bl_tree.column("Von", anchor='w', stretch=tk.YES, width=180)
        self._bl_tree.column("An", anchor='w', stretch=tk.YES, width=100)
        self._bl_tree.column("vert", anchor='w', stretch=tk.NO, width=50)
        self._bl_tree.column("flag", anchor='w', stretch=tk.NO, width=60)
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

        btn_frame_r = tk.Frame(btn_frame)
        btn_frame_l = tk.Frame(btn_frame)
        btn_frame_l.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        btn_frame_r.pack(side=tk.LEFT, expand=False, anchor='e')

        tk.Button(btn_frame_l,
                  text=self._getTabStr('new'),
                  command=lambda: self._open_newMSG_win()
                  ).pack(side=tk.LEFT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('delete'),
                  command=lambda: self._delete_msg()
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('save'),
                  # TODO cmd
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('forward'),
                  command=lambda: self._open_newMSG_win_forward('B')
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('answer'),
                  command=lambda: self._open_newMSG_win_reply('B'),
                  ).pack(side=tk.RIGHT, expand=False)

        # Header Frame
        from_label      = tk.Label(header_frame, textvariable=self._var_bl_from_label)
        to_label        = tk.Label(header_frame, textvariable=self._var_bl_to_label)
        subject_label   = tk.Label(header_frame, textvariable=self._var_bl_subj_label)
        time_label      = tk.Label(header_frame, textvariable=self._var_bl_time_label)
        bid_label       = tk.Label(header_frame, textvariable=self._var_bl_bid_label)
        from_label.place(x=2, y=0)
        to_label.place(x=2, y=25)
        subject_label.place(x=2, y=50)
        time_label.place(relx=0.98, y=36, anchor=tk.E)
        bid_label.place(relx=0.98, y=61, anchor=tk.E)

        self._bl_text = scrolledtext.ScrolledText(root_frame,
                                                  font=(FONT, self.text_size),
                                                  bd=0,
                                                  height=3,
                                                  background='black',
                                                  foreground='white',
                                                  borderwidth=0,
                                                  state="disabled",
                                                  )
        self._bl_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _init_bl_footer_frame(self, root_frame):
        footer_frame = tk.Frame(root_frame, height=15)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        txt_encoding_ent = tk.OptionMenu(
            footer_frame,
            self._var_encoding,
            *ENCODINGS,
            command=self._update_BL_msg
        )
        txt_encoding_ent.configure(
            font=(None, 6),
            border=0,
            borderwidth=0,
            height=1,
        )
        txt_encoding_ent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        tk.Label(footer_frame,
                 textvariable=self._var_bl_msg_size,
                 font=(None, 7),
                 ).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

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

        self._out_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
        self._out_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._out_tree.yview)
        self._out_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._out_tree.heading('gesendet', text='  ', command=lambda: self._sort_entry('gesendet', self._out_tree))
        self._out_tree.heading('Betreff', text=self._getTabStr('subject'), command=lambda: self._sort_entry('Betreff', self._out_tree))
        self._out_tree.heading('An', text=self._getTabStr('to'), command=lambda: self._sort_entry('An', self._out_tree))
        self._out_tree.heading('fwd_bbs', text=f"{self._getTabStr('to')} BBS", command=lambda: self._sort_entry('fwd_bbs', self._out_tree))
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

        btn_frame_r = tk.Frame(btn_frame)
        btn_frame_l = tk.Frame(btn_frame)
        btn_frame_l.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        btn_frame_r.pack(side=tk.LEFT, expand=False, anchor='e')

        # tk.Button(btn_frame, text='Speichern').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_l,
                  text='Start FWD',
                  command=lambda: self._do_pms_autoFWD()
                  ).pack(side=tk.LEFT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('delete'),
                  command=lambda: self._delete_msg()
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('save'),
                  command=lambda: self._save_outMSG()
                  ).pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('forward'),
                  command=lambda: self._open_newMSG_win_forward('O')
                  ).pack(side=tk.RIGHT, expand=False)
        # tk.Button(btn_frame, text='Antworten').pack(side=tk.RIGHT, expand=False)

        from_label      = tk.Label(header_frame, textvariable=self._var_out_from_label)
        to_label        = tk.Label(header_frame, textvariable=self._var_out_to_label)
        subject_label   = tk.Label(header_frame, textvariable=self._var_out_subj_label)
        time_label      = tk.Label(header_frame, textvariable=self._var_out_time_label)
        bid_label       = tk.Label(header_frame, textvariable=self._var_out_bid_label)
        from_label.place(x=2, y=0)
        to_label.place(x=2, y=25)
        subject_label.place(x=2, y=50)
        time_label.place(relx=0.98, y=36, anchor=tk.E)
        bid_label.place(relx=0.98, y=61, anchor=tk.E)

        # ## lower_f_lower / Msg Text
        self._out_text = scrolledtext.ScrolledText(root_frame,
                                                   font=(FONT, self.text_size),
                                                   bd=0,
                                                   height=3,
                                                   borderwidth=0,
                                                   background='black',
                                                   foreground='white',
                                                   state="disabled",
                                                   )
        self._out_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _init_out_footer_frame(self, root_frame):
        footer_frame = tk.Frame(root_frame, height=15)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        txt_encoding_ent = tk.OptionMenu(
            footer_frame,
            self._var_encoding,
            *ENCODINGS,
            command=self._update_OUT_msg
        )
        txt_encoding_ent.configure(
            font=(None, 6),
            border=0,
            borderwidth=0,
            height=1
        )
        txt_encoding_ent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        tk.Label(footer_frame,
                 textvariable=self._var_out_msg_size,
                 font=(None, 7),
                 ).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    # SV TAB
    def _init_sv_tree(self, root_frame):
        columns = (
            'Typ',
            'Betreff',
            'Von',
            'An',
            'Datum',
        )

        self._sv_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
        self._sv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._sv_tree.yview)
        self._sv_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._sv_tree.heading('Typ', text='Typ', command=lambda: self._sort_entry('Typ', self._sv_tree))
        self._sv_tree.heading('Betreff', text=self._getTabStr('subject'), command=lambda: self._sort_entry('Betreff', self._sv_tree))
        self._sv_tree.heading('Von', text=self._getTabStr('from'), command=lambda: self._sort_entry('Von', self._sv_tree))
        self._sv_tree.heading('An', text=self._getTabStr('to'), command=lambda: self._sort_entry('An', self._sv_tree))
        self._sv_tree.heading('Datum', text=self._getTabStr('date_time'), command=lambda: self._sort_entry('Datum', self._sv_tree))
        self._sv_tree.column("Typ", anchor='w', stretch=tk.NO, width=50)
        self._sv_tree.column("Betreff", anchor='w', stretch=tk.YES, width=190)
        self._sv_tree.column("Von", anchor='w', stretch=tk.YES, width=190)
        self._sv_tree.column("An", anchor='w', stretch=tk.YES, width=190)
        self._sv_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        # self._sv_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        # self._sv_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._sv_tree.bind('<<TreeviewSelect>>', self._SV_entry_selected)

    def _init_sv_lower_frame(self, root_frame):
        btn_frame = tk.Frame(root_frame, height=30)
        header_frame = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        btn_frame_r = tk.Frame(btn_frame)
        btn_frame_l = tk.Frame(btn_frame)
        btn_frame_l.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        btn_frame_r.pack(side=tk.LEFT, expand=False, anchor='e')

        tk.Button(btn_frame_l,
                  text=self._getTabStr('new'),
                  command=lambda: self._open_newMSG_win()
                  ).pack(side=tk.LEFT, expand=False)
        # tk.Button(btn_frame, text='Speichern').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('delete'),
                  command=lambda: self._delete_msg()
                  ).pack(side=tk.RIGHT, expand=False)
        # TODO ? tk.Button(btn_frame_r, text='Als Vorlage').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('edit'),
                  command=lambda: self._open_newMSG_win_reply('S'),
                  ).pack(side=tk.RIGHT, expand=False)

        from_label = tk.Label(header_frame, textvariable=self._var_sv_from_label)
        to_label = tk.Label(header_frame, textvariable=self._var_sv_to_label)
        subject_label = tk.Label(header_frame, textvariable=self._var_sv_subj_label)
        time_label = tk.Label(header_frame, textvariable=self._var_sv_time_label)
        bid_label = tk.Label(header_frame, textvariable=self._var_sv_bid_label)
        from_label.place(x=2, y=0)
        to_label.place(x=2, y=25)
        subject_label.place(x=2, y=50)
        time_label.place(relx=0.98, y=36, anchor=tk.E)
        bid_label.place(relx=0.98, y=61, anchor=tk.E)

        # ## lower_f_lower / Msg Text
        self._sv_text = scrolledtext.ScrolledText(root_frame,
                                                  font=(FONT, self.text_size),
                                                  bd=0,
                                                  height=3,
                                                  borderwidth=0,
                                                  background='black',
                                                  foreground='white',
                                                  state="disabled",
                                                  )
        self._sv_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _init_sv_footer_frame(self, root_frame):
        footer_frame = tk.Frame(root_frame, height=15)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        txt_encoding_ent = tk.OptionMenu(
            footer_frame,
            self._var_encoding,
            *ENCODINGS,
            command=self._update_SV_msg
        )
        txt_encoding_ent.configure(
            font=(None, 6),
            border=0,
            borderwidth=0,
            height=1
        )
        txt_encoding_ent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        tk.Label(footer_frame,
                 textvariable=self._var_sv_msg_size,
                 font=(None, 7),
                 ).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    ################################
    # PN
    def _update_PN_tree_data(self):
        self._get_PN_data()
        self._format_PN_tree_data()
        self._update_PN_tree()

    def _get_PN_data(self):
        self._pn_data = self._bbs_obj.get_pn_msg_tab()

    def _get_PN_MSG_data(self, bid):
        return self._bbs_obj.get_pn_msg_fm_BID(bid)

    def _set_PN_MSG_notNew(self, bid: str):
        self._bbs_obj.set_in_msg_notNew(bid)

    def _format_PN_tree_data(self):
        self._pn_tree_data = []
        for el in self._pn_data:
            from_call = f"{el[1]}"
            if el[2]:
                from_call += f"@{el[2]}"
            new = ''
            if int(el[6]):
                new = '✉'
            self._pn_tree_data.append((
                f'{new}',
                f'{el[4]}',
                f'{from_call}',
                f'{el[7]}',
                f'{el[5]}',
                f'{el[0]}',  # BID
            ))

    def _update_PN_tree(self):
        # curItem = self._pn_tree.selection()
        # curItem = self._pn_tree.selection_get()
        # print(curItem)
        # print(self._pn_tree.item(curItem))
        for i in self._pn_tree.get_children():
            self._pn_tree.delete(i)
        for ret_ent in self._pn_tree_data:
            if ret_ent[0]:
                tag = 'neu'
            else:
                tag = 'alt'
            self._pn_tree.insert('', tk.END, values=ret_ent[:-1], tags=(tag, ret_ent[-1]))
        self._update_sort_entry(self._pn_tree)

    def _PN_entry_selected(self, event=None):
        bid = ''
        for selected_item in self._pn_tree.selection():
            item = self._pn_tree.item(selected_item)
            bid = item['tags'][1]
        if bid:
            self._PN_show_msg_fm_BID(bid)
            self._update_PN_tree_data()

    def _update_PN_msg(self, event=None):
        msg = self._selected_msg['P'].get('msg', b'')
        if msg:
            enc = self._var_encoding.get()
            self._selected_msg['P']['enc'] = enc
            msg = msg.decode(enc, 'ignore')
            msg = str(msg).replace('\r', '\n')
            self._pn_text.configure(state='normal')
            self._pn_text.delete('1.0', tk.END)
            self._pn_text.insert('1.0', msg)
            self._pn_text.configure(state='disabled')

    def _PN_show_msg_fm_BID(self, bid):
        if bid:
            self._pn_text.configure(state='normal')
            self._pn_text.delete('1.0', tk.END)
            db_data = self._get_PN_MSG_data(bid)
            self._set_PN_MSG_notNew(bid)
            if db_data:
                enc = self._var_encoding.get()
                db_data['enc'] = enc
                self._selected_msg['P'] = db_data
                bid = db_data['bid']
                from_call   = db_data['from_call']
                from_bbs    = db_data['from_bbs']
                to_call     = db_data['to_call']  # Cat
                to_bbs      = db_data['to_bbs']  # Verteiler
                subj        = db_data['subject']
                msg         = db_data['msg']
                msg_time    = db_data['time']
                size        = format_number(len(msg))
                msg         = msg.decode(enc, 'ignore')
                msg         = str(msg).replace('\r', '\n')
                if from_bbs:
                    from_call   = from_call + ' @ ' + from_bbs
                if to_bbs:
                    to_call     = to_call + ' @ ' + to_bbs

                self._var_pn_from_label.set(f"From     : {from_call}")
                self._var_pn_to_label.set(f"To          : {to_call}")
                self._var_pn_subj_label.set(f"Subject : {subj}")
                self._var_pn_time_label.set(f"{msg_time}")
                self._var_pn_bid_label.set(f"BID : {bid}")
                self._var_pn_msg_size.set(f' Size: {size} Bytes')

                self._pn_text.insert('1.0', msg)

            self._pn_text.configure(state='disabled')

    def _delete_PN(self, bid: str):
        if bid:
            return self._bbs_obj.del_in_by_BID(bid)

    ###########
    # Bulletin
    def _update_BL_tree_data(self):
        self._get_BL_data()
        self._format_BL_tree_data()
        self._update_BL_tree()
        self._update_CAT_tree()

    def _get_BL_data(self):
        self._bl_data = self._bbs_obj.get_bl_msg_tab()

    def _get_BL_MSG_data(self, bid):
        return self._bbs_obj.get_bl_msg_fm_BID(bid)

    def _set_BL_MSG_notNew(self, bid: str):
        self._bbs_obj.set_in_msg_notNew(bid)

    def _format_BL_tree_data(self):
        self._bl_tree_data = []
        self._bl_cat_tree_data = []
        new_tr = {}
        for el in self._bl_data:
            from_call = f"{el[1]}"
            if el[2]:
                from_call += f"@{el[2]}"
            new = ''
            if int(el[7]):
                new = '✉'
                new_tr[el[3]] = True
            if not self._bl_cat_filter or self._bl_cat_filter == el[3]:
                self._bl_tree_data.append((
                    f'{new}',
                    f'{el[5]}',
                    f'{from_call}',
                    f'{el[3]}',  # Cat
                    f'{el[4]}',
                    f'{el[8]}',  # Flag
                    f'{el[6]}',  # Date
                    f'{el[0]}',  # BID
                ))
        # Category Tab
        any_tr = False
        for el in self._bl_data:
            tr = new_tr.get(el[3], False)
            if tr:
                any_tr = True
            if (tr, el[3]) not in self._bl_cat_tree_data:
                self._bl_cat_tree_data.append((tr, el[3]))

        self._bl_cat_tree_data.sort(key=lambda x: x[1])
        self._bl_cat_tree_data = [(any_tr, 'ALL*')] + self._bl_cat_tree_data

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
            self._BL_show_msg_fm_BID(bid)
            self._update_BL_tree_data()

    def _update_BL_msg(self, event=None):
        msg = self._selected_msg['B'].get('msg', b'')
        if msg:
            enc = self._var_encoding.get()
            self._selected_msg['B']['enc'] = enc
            msg = msg.decode(enc, 'ignore')
            msg = str(msg).replace('\r', '\n')
            self._bl_text.configure(state='normal')
            self._bl_text.delete('1.0', tk.END)
            self._bl_text.insert('1.0', msg)
            self._bl_text.configure(state='disabled')

    def _BL_show_msg_fm_BID(self, bid):
        if bid:
            self._bl_text.configure(state='normal')
            self._bl_text.delete('1.0', tk.END)
            db_data = self._get_BL_MSG_data(bid)
            self._set_BL_MSG_notNew(bid)
            if db_data:
                enc         = self._var_encoding.get()
                db_data['enc']   = enc
                self._selected_msg['B'] = db_data
                bid         = db_data['bid']
                from_call   = db_data['from_call']
                from_bbs    = db_data['from_bbs']
                to_call     = db_data['to_call']  # Cat
                to_bbs      = db_data['to_bbs']  # Verteiler
                subj        = db_data['subject']
                msg         = db_data['msg']
                # _path = _db_data[9]
                msg_time    = db_data['time']
                size        = format_number(len(msg))
                msg         = msg.decode(enc, 'ignore')
                msg         = str(msg).replace('\r', '\n')
                if from_bbs:
                    from_call = from_call + ' @ ' + from_bbs
                if to_bbs:
                    to_call = to_call + ' @ ' + to_bbs

                self._var_bl_from_label.set(f"From     : {from_call}")
                self._var_bl_to_label.set(f"To          : {to_call}")
                self._var_bl_subj_label.set(f"Subject : {subj}")
                self._var_bl_time_label.set(f"{msg_time}")
                self._var_bl_bid_label.set(f"BID: {bid}")
                self._var_bl_msg_size.set(f' Size: {size} Bytes')

                # self._bl_text.insert(tk.INSERT, try_decode(_msg, ignore=True))
                self._bl_text.insert('1.0', msg)
            self._bl_text.configure(state='disabled')

    def _delete_BL(self, bid: str):
        if bid:
            return self._bbs_obj.del_in_by_BID(bid)

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
        self._out_data = self._bbs_obj.get_fwd_q_tab()

    def _get_OUT_MSG_data(self, bid):
        return self._bbs_obj.get_out_msg_fm_BID(bid)

    def _format_OUT_tree_data(self):
        self._out_tree_data = []
        for el in self._out_data:
            to_call = f"{el[3]}"
            if el[4]:
                to_call += f"@{el[4]}"
            fwd_done = ''
            if el[9] != 'F':
                fwd_done = '✔'
            tx_time = ''
            if el[10]:
                tx_time = el[10]
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
                f'{fwd_done}',
                f'{el[6]}',
                f'{to_call}',
                f'{el[5]}',
                f'{el[8]}',
                f'{el[9]}',
                f'{tx_time}',
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
        self._update_sort_entry(self._out_tree)

    def _OUT_entry_selected(self, event=None):
        bid = ''
        for selected_item in self._out_tree.selection():
            item = self._out_tree.item(selected_item)
            bid = item['tags'][1]
        if bid:
            self._OUT_show_msg_fm_BID(bid)
            # self._update_OUT_tree_data()
            # self._update_sort_entry(self._out_tree)

    def _update_OUT_msg(self, event=None):
        # self._OUT_show_msg_fm_BID(self._selected_out_BID)
        msg = self._selected_msg['O'].get('msg', b'')
        if msg:
            enc = self._var_encoding.get()
            self._selected_msg['O']['enc'] = enc
            msg = msg.decode(enc, 'ignore')
            msg = str(msg).replace('\r', '\n')
            self._out_text.configure(state='normal')
            self._out_text.delete('1.0', tk.END)
            self._out_text.insert('1.0', msg)
            self._out_text.configure(state='disabled')

    def _OUT_show_msg_fm_BID(self, bid):
        if bid:
            self._out_text.configure(state='normal')
            self._out_text.delete('1.0', tk.END)
            db_data = self._get_OUT_MSG_data(bid)
            if db_data:
                _enc = self._var_encoding.get()
                db_data['enc'] = _enc
                self._selected_msg['O'] = db_data
                _bid = db_data['bid']
                _from = db_data['from_call']
                _from_bbs = db_data['from_bbs_call']
                _to = db_data['to_call']  # Cat
                _to_bbs = db_data['to_bbs']  # Verteiler
                _to_bbs_fwd = db_data['fwd_bbs']  # Verteiler
                _subj = db_data['subject']
                _msg = db_data['msg']
                # _path = _db_data[9]
                _time = db_data['tx-time']
                _size = format_number(len(_msg))
                _msg = _msg.decode(_enc, 'ignore')
                _msg = str(_msg).replace('\r', '\n')
                if _from_bbs:
                    _from = _from + ' @ ' + _from_bbs
                if _to_bbs:
                    _to = _to + ' @ ' + _to_bbs

                _to += f' > {_to_bbs_fwd}'

                self._var_out_from_label.set(f"From     : {_from}")
                self._var_out_to_label.set(f"To          : {_to}")
                self._var_out_subj_label.set(f"Subject : {_subj}")
                self._var_out_time_label.set(f"{_time}")
                self._var_out_bid_label.set(f"BID: {_bid}")
                self._var_out_msg_size.set(f' Size: {_size} Bytes')

                self._out_text.insert('1.0', _msg)

            self._out_text.configure(state='disabled')

    def _delete_OUT(self, bid: str):
        if bid:
            return self._bbs_obj.del_out_by_BID(bid)

    ################################
    # OUT Tab
    def _update_SV_tree_data(self):
        self._get_SV_data()
        self._format_SV_tree_data()
        self._update_SV_tree()

    def _get_SV_data(self):
        self._sv_data = self._bbs_obj.get_sv_msg_tab()

    def _get_SV_MSG_data(self, mid):
        return self._bbs_obj.get_sv_msg_fm_BID(mid)

    def _format_SV_tree_data(self):
        self._sv_tree_data = []
        for el in self._sv_data:
            from_call = f"{el[1]}"
            if el[2]:
                from_call += f"@{el[2]}"
            to_call = f"{el[3]}"
            if el[4]:
                to_call += f"@{el[4]}"
            self._sv_tree_data.append((
                f'{el[7]}',     # TYP
                f'{el[5]}',     # SUB
                f'{from_call}',
                f'{to_call}',
                f'{el[6]}',     # DATE
                f'{el[0]}',     # MID
            ))

    def _update_SV_tree(self):
        for i in self._sv_tree.get_children():
            self._sv_tree.delete(i)
        for ret_ent in self._sv_tree_data:
            self._sv_tree.insert('', tk.END, values=ret_ent[:-1], tags=('dummy', ret_ent[-1]))
        self._update_sort_entry(self._sv_tree)

    def _SV_entry_selected(self, event=None):
        mid = ''
        for selected_item in self._sv_tree.selection():
            item = self._sv_tree.item(selected_item)
            mid = item['tags'][1]
        if mid:
            self._SV_show_msg_fm_MID(mid)
            self._update_SV_tree_data()

    def _update_SV_msg(self, event=None):
        msg = self._selected_msg['S'].get('msg', b'')
        if msg:
            enc = self._var_encoding.get()
            self._selected_msg['S']['enc'] = enc
            msg = msg.decode(enc, 'ignore')
            msg = str(msg).replace('\r', '\n')
            self._sv_text.configure(state='normal')
            self._sv_text.delete('1.0', tk.END)
            self._sv_text.insert('1.0', msg)
            self._sv_text.configure(state='disabled')

    def _SV_show_msg_fm_MID(self, mid):
        if mid:
            self._sv_text.configure(state='normal')
            self._sv_text.delete('1.0', tk.END)
            db_data = self._get_SV_MSG_data(mid)
            if db_data:
                _enc = self._var_encoding.get()
                db_data['enc'] = _enc
                self._selected_msg['S'] = db_data
                _mid = db_data['mid']
                _from = db_data['from_call']
                _from_bbs = db_data['from_bbs']
                _to = db_data['to_call']  # Cat
                _to_bbs = db_data['to_bbs']  # Verteiler
                _subj = db_data['subject']
                _msg = db_data['msg']
                _time = db_data['time']
                _size = format_number(len(_msg))
                _msg = _msg.decode(_enc, 'ignore')
                _msg = str(_msg).replace('\r', '\n')
                if _from_bbs:
                    _from = _from + ' @ ' + _from_bbs
                if _to_bbs:
                    _to = _to + ' @ ' + _to_bbs

                self._var_sv_from_label.set(f"From     : {_from}")
                self._var_sv_to_label.set(f"To          : {_to}")
                self._var_sv_subj_label.set(f"Subject : {_subj}")
                self._var_sv_time_label.set(f"{_time}")
                self._var_sv_bid_label.set(f"MID : {_mid}")
                self._var_sv_msg_size.set(f' Size: {_size} Bytes')

                self._sv_text.insert('1.0', _msg)

            self._sv_text.configure(state='disabled')

    def _delete_SV(self, mid: str):
        if mid:
            return self._bbs_obj.del_sv_by_MID(mid)

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
        _tmp.sort(reverse=not self._sort_rev)
        for index, (val, k) in enumerate(_tmp):
            tree.move(k, '', int(index))

    #####################################
    # GUI
    def _increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        self._bl_text.configure(font=(FONT, self.text_size))
        self._pn_text.configure(font=(FONT, self.text_size))
        self._out_text.configure(font=(FONT, self.text_size))
        self._sv_text.configure(font=(FONT, self.text_size))

    def _decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self._bl_text.configure(font=(FONT, self.text_size))
        self._pn_text.configure(font=(FONT, self.text_size))
        self._out_text.configure(font=(FONT, self.text_size))
        self._sv_text.configure(font=(FONT, self.text_size))

    def _update_textsize_trees(self):
        # TODO
        self._bl_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._pn_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._bl_cat_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_cat_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

    def _delete_msg(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return

        bid_mid = {
            0: self._selected_msg['P'].get('bid', ''),
            1: self._selected_msg['B'].get('bid', ''),
            2: self._selected_msg['O'].get('bid', ''),
            3: self._selected_msg['S'].get('mid', ''),
        }.get(ind, '')
        del_fnc = {
            0: self._delete_PN,
            1: self._delete_BL,
            2: self._delete_OUT,
            3: self._delete_SV,
        }.get(ind, None)
        if del_fnc is not None:
            tree = {
                0: self._pn_tree,
                1: self._bl_tree,
                2: self._out_tree,
                3: self._sv_tree,
            }[ind]
            bid_next_msg = ''
            ind_ex = 0
            for i in tree.get_children():
                ind_ex += 1
                if tree.item(i)['tags'][1] == bid_mid:
                    try:
                        bid_next_msg = tree.item(tree.get_children()[ind_ex]).get('tags', [])
                        if len(bid_next_msg) == 2:
                            bid_next_msg = bid_next_msg[1]
                    except IndexError:
                        pass
                    # print(bid_next_msg)
                    break
            if del_fnc(bid_mid):
                self.on_bbsTab_select()
                if bid_next_msg:
                    fnc = {
                        0: self._PN_show_msg_fm_BID,
                        1: self._BL_show_msg_fm_BID,
                        2: self._OUT_show_msg_fm_BID,
                        3: self._SV_show_msg_fm_MID,
                    }.get(ind)
                    fnc(bid_next_msg)
                    self.tree_update_task()

    def _save_outMSG(self):
        bid = self._selected_msg['O'].get('bid', '')
        if bid:
            mid = int(bid[:6])
            # print(mid)
            self._bbs_obj.get_db().pms_save_outMsg_by_MID(mid)

    def _copy_select(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        text = {
            0: self._pn_text,
            1: self._bl_text,
            2: self._out_text,
            3: self._sv_text,
        }[ind]
        if text.tag_ranges("sel"):
            self.clipboard_clear()
            self.clipboard_append(text.selection_get())
            text.tag_remove(tk.SEL, "1.0", tk.END)

    def _open_newMSG_win_reply(self, typ: str):
        if self.newPMS_MSG_win is None:
            if self._selected_msg.get(typ, None):
                msg = dict(self._selected_msg[typ])
                msg['subject'] = ('Re: ' + msg.get('subject', ''))
                self.newPMS_MSG_win = BBS_newMSG(self, msg)

    def _open_newMSG_win_forward(self, typ: str):
        if self.newPMS_MSG_win is None:
            if self._selected_msg.get(typ, None):
                msg: dict = dict(self._selected_msg[typ])
                msg['flag'] = 'E'
                msg['typ'] = 'P'
                msg['to_call'] = ''
                msg['to_bbs'] = ''
                msg['subject'] = ('Fwd: ' + msg['subject'])
                self.newPMS_MSG_win = BBS_newMSG(self, msg)

    def _open_newMSG_win(self):
        if self.newPMS_MSG_win:
            return
        self.newPMS_MSG_win = BBS_newMSG(self)

    def on_bbsTab_select(self, event=None):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        enc = {
            0: self._selected_msg['P'].get('enc', 'UTF-8'),
            1: self._selected_msg['B'].get('enc', 'UTF-8'),
            2: self._selected_msg['O'].get('enc', 'UTF-8'),
            3: self._selected_msg['S'].get('enc', 'UTF-8'),
        }.get(ind, 'UTF-8')
        self._var_encoding.set(enc)
        self.tree_update_task()
        # self._pn_tree.selection_toggle(self._pn_tree.focus())
        # print(f'>>> {self._pn_tree.selection()}')

    def tree_update_task(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        update_task = {
            0: self._update_PN_tree_data,
            1: self._update_BL_tree_data,
            2: self._update_OUT_tree_data,
            3: self._update_SV_tree_data,
        }.get(ind, None)
        if update_task:
            update_task()
        # self._pn_tree.selection_set('"Row 0"')

    ####################
    def _save_msg_to_file(self, event=None):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        msg_text = {
            0: self._pn_text,
            1: self._bl_text,
            2: self._out_text,
            3: self._sv_text,
        }.get(ind, None)
        if msg_text:
            data = msg_text.get('1.0', tk.END)
            save_file_dialog(data)

    def _do_pms_autoFWD(self):
        self._bbs_obj.start_man_autoFwd()

    def _set_all_to_oldMSG(self):   # Set all Msg to read Status
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        fnc = {
            0: self._bbs_obj.set_all_pn_msg_notNew,
            1: self._bbs_obj.set_all_bl_msg_notNew,
        }.get(ind, None)
        if fnc:
            fnc()
            self.on_bbsTab_select()

    def _close(self):
        self._save_Vars_to_Cfg()
        self._bbs_obj = None
        self._root_win.MSG_Center_win = None
        self.destroy()
