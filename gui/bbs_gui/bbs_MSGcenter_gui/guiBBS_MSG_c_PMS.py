import tkinter as tk
from tkinter import ttk, scrolledtext

from cfg.constant import FONT, ENCODINGS
from fnc.str_fnc import format_number
from gui.bbs_gui.bbs_MSGcenter_gui.guiBBS_MSG_c_base import MSG_Center_base


class MSG_Center_PMS(MSG_Center_base):
    def __init__(self, root_win):
        MSG_Center_base.__init__(self, root_win)
        # ## lower_f_top / MSG Header ect.
        # PN
        self._var_pn_from_label     = tk.StringVar(self, '')
        self._var_pn_to_label       = tk.StringVar(self, '')
        self._var_pn_subj_label     = tk.StringVar(self, '')
        self._var_pn_time_label     = tk.StringVar(self, '')
        self._var_pn_bid_label      = tk.StringVar(self, '')
        self._var_pn_msg_size       = tk.StringVar(self, ' Size: --- Bytes')
        # BL
        self._var_bl_from_label     = tk.StringVar(self, '')
        self._var_bl_to_label       = tk.StringVar(self, '')
        self._var_bl_subj_label     = tk.StringVar(self, '')
        self._var_bl_time_label     = tk.StringVar(self, '')
        self._var_bl_bid_label      = tk.StringVar(self, '')
        self._var_bl_msg_size       = tk.StringVar(self, ' Size: --- Bytes')
        # Out
        self._var_out_from_label    = tk.StringVar(self, '')
        self._var_out_to_label      = tk.StringVar(self, '')
        self._var_out_subj_label    = tk.StringVar(self, '')
        self._var_out_time_label    = tk.StringVar(self, '')
        self._var_out_bid_label     = tk.StringVar(self, '')
        self._var_out_msg_size      = tk.StringVar(self, ' Size: --- Bytes')
        # SV
        self._var_sv_from_label     = tk.StringVar(self, '')
        self._var_sv_to_label       = tk.StringVar(self, '')
        self._var_sv_subj_label     = tk.StringVar(self, '')
        self._var_sv_time_label     = tk.StringVar(self, '')
        self._var_sv_bid_label      = tk.StringVar(self, '')
        self._var_sv_msg_size       = tk.StringVar(self, ' Size: --- Bytes')

        ###################################
        # PMS-TAB
        self._tabControl.bind("<<NotebookTabChanged>>", self.on_bbsTab_select)
        tab_PN_PMS       = ttk.Frame(self._tabControl)
        tab_BL_PMS       = ttk.Frame(self._tabControl)
        tab_OUT_PMS      = ttk.Frame(self._tabControl)
        tab_SAVE_PMS     = ttk.Frame(self._tabControl)
        self._tabControl.add(tab_PN_PMS,    text=self._getTabStr('private'))
        self._tabControl.add(tab_BL_PMS,    text='Bulletin')
        self._tabControl.add(tab_OUT_PMS,   text=self._getTabStr('msgC_sendet_msg'))
        self._tabControl.add(tab_SAVE_PMS,  text=self._getTabStr('saved'))
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ################################################
        # ######### PMS/PN -----------------------------------
        pn_pan_frame = tk.Frame(tab_PN_PMS)
        pn_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pw_pn        = ttk.PanedWindow(pn_pan_frame, orient=tk.VERTICAL)

        top_f        = tk.Frame(pw_pn)
        lower_f_main = tk.Frame(pw_pn)
        lower_f_top  = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        pw_pn.add(top_f, weight=1)
        pw_pn.add(lower_f_main, weight=1)
        pw_pn.pack(fill=tk.BOTH, expand=True)
        ########################
        # ## top_f / Msg Table
        self._init_pn_tree(top_f)
        self._pn_tree_data  = []
        self._pn_data       = []
        self._update_PN_tree_data()
        ########################
        # ## lower_f_top / MSG Header ect.
        self._init_pn_lower_frame(lower_f_top)
        self._init_pn_footer_frame(lower_f_top)

        #################################################
        # ######### PMS/BL
        pw_bl_hor       = tk.PanedWindow(tab_BL_PMS, orient=tk.HORIZONTAL)
        pw_bl_hor.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        left_frame      = tk.Frame(pw_bl_hor)
        bl_pan_frame    = tk.Frame(pw_bl_hor)

        pw_bl_hor.add(left_frame, width=140)
        pw_bl_hor.add(bl_pan_frame, )
        ###################
        pw_bl           = ttk.PanedWindow(bl_pan_frame, orient=tk.VERTICAL)
        top_f           = tk.Frame(pw_bl)
        lower_f_main    = tk.Frame(pw_bl)
        lower_f_lower   = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_lower.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        pw_bl.add(top_f, weight=1)
        pw_bl.add(lower_f_main, weight=1)
        pw_bl.pack(fill=tk.BOTH, expand=True)
        ########################
        # LEFT TAB Category's
        self._bl_cat_filter     = ''
        self._bl_cat_tree_data  = []
        self._init_bl_left_cat_tab(left_frame)
        ########################
        # ## top_f / Msg Table
        self._init_bl_tree(top_f)
        self._bl_tree_data      = []
        self._bl_data           = []
        self._update_BL_tree_data()
        ##############
        # ## lower_f_lower / Msg Text
        self._init_bl_lower_frame(lower_f_lower)
        self._init_bl_footer_frame(lower_f_lower)

        ######################################################
        # ######### PMS/OUT
        out_pan_frame       = tk.Frame(tab_OUT_PMS)
        out_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pw_out              = ttk.PanedWindow(out_pan_frame, orient=tk.VERTICAL)
        top_f               = tk.Frame(pw_out)
        lower_f_main        = tk.Frame(pw_out)
        lower_f_top         = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        pw_out.add(top_f, weight=1)
        pw_out.add(lower_f_main, weight=1)
        pw_out.pack(fill=tk.BOTH, expand=True)
        ########################
        # ## top_f / Msg Table
        self._init_out_tree(top_f)
        self._out_tree_data     = []
        self._out_data          = []
        self._update_OUT_tree_data()
        ########################
        # ## lower_f_top / MSG Header ect.
        self._init_out_lower_frame(lower_f_top)
        self._init_out_footer_frame(lower_f_top)
        ######################################################
        # ######### BBS/Drafts/Saved Msg
        pn_pan_frame        = tk.Frame(tab_SAVE_PMS)
        pn_pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pw_pn               = ttk.PanedWindow(pn_pan_frame, orient=tk.VERTICAL)
        top_f               = tk.Frame(pw_pn)
        lower_f_main        = tk.Frame(pw_pn)
        lower_f_top         = tk.Frame(lower_f_main)

        top_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lower_f_main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        lower_f_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        pw_pn.add(top_f, weight=1)
        pw_pn.add(lower_f_main, weight=1)
        pw_pn.pack(fill=tk.BOTH, expand=True)
        ########################
        # ## top_f / Msg Table
        self._init_sv_tree(top_f)
        self._sv_tree_data      = []
        self._sv_data           = []
        self._sv_selected       = []
        self._update_SV_tree_data()
        ########################
        # ## lower_f_top / MSG Header ect.
        self._init_sv_lower_frame(lower_f_top)
        self._init_sv_footer_frame(lower_f_top)
        # ---------------------------------------------
        ###############################################

    def on_bbsTab_select(self, event=None):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except (tk.TclError, AttributeError):
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
    #################################################
    # Tab Init PMS
    # PN TAB
    def _init_pn_tree(self, root_frame):
        columns = (
            'Neu',
            'Betreff',
            'Von',
            'An',
            #'flag',
            'Datum',
        )

        self._pn_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
        self._pn_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(root_frame, orient=tk.VERTICAL, command=self._pn_tree.yview)
        self._pn_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._pn_tree.heading('Neu', text=self._getTabStr('new'),
                              command=lambda: self._sort_entry('Neu', self._pn_tree))
        self._pn_tree.heading('Betreff', text=self._getTabStr('subject'),
                              command=lambda: self._sort_entry('Betreff', self._pn_tree))
        self._pn_tree.heading('Von', text=self._getTabStr('from'),
                              command=lambda: self._sort_entry('Von', self._pn_tree))
        self._pn_tree.heading('An', text=self._getTabStr('to'),
                              command=lambda: self._sort_entry('An', self._pn_tree))
        # self._pn_tree.heading('flag', text='Flag', command=lambda: self._sort_entry('flag', self._pn_tree))
        self._pn_tree.heading('Datum', text=self._getTabStr('date_time'),
                              command=lambda: self._sort_entry('Datum', self._pn_tree))
        self._pn_tree.column("Neu", anchor=tk.CENTER, stretch=tk.NO, width=40)
        self._pn_tree.column("Betreff", anchor='w', stretch=tk.YES, width=190)
        self._pn_tree.column("Von", anchor='w', stretch=tk.YES, width=130)
        self._pn_tree.column("An", anchor='w', stretch=tk.YES, width=130)
        # self._pn_tree.column("flag", anchor='w', stretch=tk.NO, width=60)
        self._pn_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        self._pn_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._pn_tree.bind('<<TreeviewSelect>>', self._PN_entry_selected)
        # self._pn_tree.get_children()

    def _init_pn_lower_frame(self, root_frame):
        btn_frame       = tk.Frame(root_frame, height=30)
        header_frame    = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        btn_frame_r     = tk.Frame(btn_frame)
        btn_frame_l     = tk.Frame(btn_frame)
        btn_frame_l.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        btn_frame_r.pack(side=tk.LEFT, expand=False, anchor='e')

        tk.Button(btn_frame_l,
                  text=self._getTabStr('new'),
                  command=lambda: self._open_newMSG_win()
                  ).pack(side=tk.LEFT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('delete'),
                  command=lambda: self._delete_PN_btn()
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
                  text=self._getTabStr('answer'),
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

        self._bl_tree.heading('Neu', text=self._getTabStr('new'),
                              command=lambda: self._sort_entry('Neu', self._bl_tree))
        self._bl_tree.heading('Betreff', text=self._getTabStr('subject'),
                              command=lambda: self._sort_entry('Betreff', self._bl_tree))
        self._bl_tree.heading('Von', text=self._getTabStr('from'),
                              command=lambda: self._sort_entry('Von', self._bl_tree))
        self._bl_tree.heading('An', text=self._getTabStr('to'),
                              command=lambda: self._sort_entry('An', self._bl_tree))
        self._bl_tree.heading('vert', text='@', command=lambda: self._sort_entry('vert', self._bl_tree))
        self._bl_tree.heading('flag', text='Flag', command=lambda: self._sort_entry('flag', self._bl_tree))
        self._bl_tree.heading('Datum', text=self._getTabStr('date_time'),
                              command=lambda: self._sort_entry('Datum', self._bl_tree))
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
                  command=lambda: self._delete_BL_btn()
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
            'Von',
            'An',
            #'fwd_bbs',
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
        self._out_tree.heading('Betreff', text=self._getTabStr('subject'),
                               command=lambda: self._sort_entry('Betreff', self._out_tree))
        self._out_tree.heading('Von', text=self._getTabStr('from'),
                               command=lambda: self._sort_entry('Von', self._out_tree))
        self._out_tree.heading('An', text=self._getTabStr('to'),
                               command=lambda: self._sort_entry('An', self._out_tree))
        #self._out_tree.heading('fwd_bbs', text=f"{self._getTabStr('to')} BBS",
        #                       command=lambda: self._sort_entry('fwd_bbs', self._out_tree))
        self._out_tree.heading('typ', text='TYP', command=lambda: self._sort_entry('typ', self._out_tree))
        self._out_tree.heading('flag', text='Flag', command=lambda: self._sort_entry('flag', self._out_tree))
        self._out_tree.heading('Datum', text='TX-Time', command=lambda: self._sort_entry('Datum', self._out_tree))
        self._out_tree.column("gesendet", anchor=tk.CENTER, stretch=tk.NO, width=40)
        self._out_tree.column("Betreff", anchor='w', stretch=tk.YES, width=230)
        self._out_tree.column("Von", anchor='w', stretch=tk.YES, width=100)
        self._out_tree.column("An", anchor='w', stretch=tk.YES, width=100)
        #self._out_tree.column("fwd_bbs", anchor='w', stretch=tk.YES, width=60)
        self._out_tree.column("typ", anchor='w', stretch=tk.NO, width=45)
        self._out_tree.column("flag", anchor='w', stretch=tk.NO, width=45)
        self._out_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        self._out_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._out_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._out_tree.bind('<<TreeviewSelect>>', self._OUT_entry_selected)
        # self._out_tree.bind('<<TreeviewSelect>>', lambda event: print(event))

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
                  command=lambda: self._delete_OUT_btn()
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
        self._sv_tree.heading('Betreff', text=self._getTabStr('subject'),
                              command=lambda: self._sort_entry('Betreff', self._sv_tree))
        self._sv_tree.heading('Von', text=self._getTabStr('from'),
                              command=lambda: self._sort_entry('Von', self._sv_tree))
        self._sv_tree.heading('An', text=self._getTabStr('to'),
                              command=lambda: self._sort_entry('An', self._sv_tree))
        self._sv_tree.heading('Datum', text=self._getTabStr('date_time'),
                              command=lambda: self._sort_entry('Datum', self._sv_tree))
        self._sv_tree.column("Typ", anchor='w', stretch=tk.NO, width=50)
        self._sv_tree.column("Betreff", anchor='w', stretch=tk.YES, width=190)
        self._sv_tree.column("Von", anchor='w', stretch=tk.YES, width=190)
        self._sv_tree.column("An", anchor='w', stretch=tk.YES, width=190)
        self._sv_tree.column("Datum", anchor='w', stretch=tk.NO, width=220)

        # self._sv_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        # self._sv_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

        self._sv_tree.bind('<<TreeviewSelect>>', self._SV_entry_selected)

    def _init_sv_lower_frame(self, root_frame):
        btn_frame       = tk.Frame(root_frame, height=30)
        header_frame    = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        btn_frame_r     = tk.Frame(btn_frame)
        btn_frame_l     = tk.Frame(btn_frame)
        btn_frame_l.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        btn_frame_r.pack(side=tk.LEFT, expand=False, anchor='e')

        tk.Button(btn_frame_l,
                  text=self._getTabStr('new'),
                  command=lambda: self._open_newMSG_win()
                  ).pack(side=tk.LEFT, expand=False)
        # tk.Button(btn_frame, text='Speichern').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('delete'),
                  command=lambda: self._delete_SV_btn()
                  ).pack(side=tk.RIGHT, expand=False)
        # TODO ? tk.Button(btn_frame_r, text='Als Vorlage').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame_r,
                  text=self._getTabStr('edit'),
                  command=lambda: self._open_newMSG_win_reply('S'),
                  ).pack(side=tk.RIGHT, expand=False)

        from_label      = tk.Label(header_frame, textvariable=self._var_sv_from_label)
        to_label        = tk.Label(header_frame, textvariable=self._var_sv_to_label)
        subject_label   = tk.Label(header_frame, textvariable=self._var_sv_subj_label)
        time_label      = tk.Label(header_frame, textvariable=self._var_sv_time_label)
        bid_label       = tk.Label(header_frame, textvariable=self._var_sv_bid_label)
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
    # -----------------------------------------------
    #################################################

    ################################
    # PN PMS
    def _update_PN_tree_data(self):
        self._get_PN_data()
        self._format_PN_tree_data()
        self._update_PN_tree()

    def _get_PN_data(self):
        self._pn_data = self._bbs_obj.get_pn_msg_tab_pms_user()

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
            to_call = f"{el[3]}"
            if el[4]:
                to_call += f"@{el[4]}"

            new = ''
            if int(el[7]):
                new = '✉'
            date = el[6]
            tmp = str(date).split('-')[0]
            if len(tmp) == 2:
                # FIX for old TimeStamps
                date = '20' + date

            self._pn_tree_data.append((
                f'{new}',
                f'{el[5]}',
                f'{from_call}',
                f'{to_call}',
                # f'{el[8]}',  # FLAG
                f'{date}',   # DATE
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
        self._update_sort_entry(self._pn_tree)

    def _PN_entry_selected(self, event=None):
        bid         = ''
        tag_name    = ''
        self._PN_selected = []
        for selected_item in self._pn_tree.selection():
            item = self._pn_tree.item(selected_item)
            tag_name, bid = item['tags']
            self._PN_selected.append(bid)
        if bid:
            self._PN_show_msg_fm_BID(bid)
            if tag_name == 'neu':
                self._update_PN_tree_data()
                #self._pn_tree.focus()

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
                bid         = db_data['bid']
                from_call   = db_data['from_call']
                from_bbs    = db_data['from_bbs']
                to_call     = db_data['to_call']        # Cat
                to_bbs      = db_data['to_bbs']         # Verteiler
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

    ################################
    # Bulletin PMS
    def _update_BL_tree_data(self):
        self._get_BL_data()
        self._format_BL_tree_data()
        self._update_BL_tree()
        self._update_CAT_tree()

    def _get_BL_data(self):
        self._bl_data = self._bbs_obj.get_bl_msg_tab()

    def _format_BL_tree_data(self):
        self._bl_tree_data     = []
        self._bl_cat_tree_data = []
        new_tr = {}
        for el in self._bl_data:
            from_call = f"{el[2]}"
            if el[3]:
                from_call += f"@{el[3]}"
            new = ''
            if int(el[8]):
                new = '✉'
                new_tr[el[4]] = True
            date = el[7]
            tmp = str(date).split('-')[0]
            if len(tmp) == 2:
                # FIX for old TimeStamps
                date = '20' + date
            if not self._bl_cat_filter or self._bl_cat_filter == el[4]:
                self._bl_tree_data.append((
                    f'{new}',
                    f'{el[6]}',
                    f'{from_call}',
                    f'{el[4]}',  # Cat
                    f'{el[5]}',
                    f'{el[9]}',  # Flag
                    f'{date}',   # Date
                    f'{el[1]}',  # BID
                ))
        # Category Tab
        any_tr = False
        for el in self._bl_data:
            tr = new_tr.get(el[4], False)
            if tr:
                any_tr = True
            if (tr, el[4]) not in self._bl_cat_tree_data:
                self._bl_cat_tree_data.append((tr, el[4]))

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
        bid      = ''
        tag_name = ''
        self._BL_selected = []
        for selected_item in self._bl_tree.selection():
            item = self._bl_tree.item(selected_item)
            tag_name, bid = item['tags']
            self._BL_selected.append(bid)
        if bid:
            self._BL_show_msg_fm_BID(bid)
            if tag_name == 'neu':
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

    def _get_BL_MSG_data(self, bid):
        return self._bbs_obj.get_bl_msg_fm_BID(bid)

    def _set_BL_MSG_notNew(self, bid: str):
        self._bbs_obj.set_in_msg_notNew(bid)

    ################################
    # Bulletin Category PMS
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
    # OUT TAB PMS
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
        self._OUT_selected = []
        for selected_item in self._out_tree.selection():
            item = self._out_tree.item(selected_item)
            bid = item['tags'][1]
            self._OUT_selected.append(bid)
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
                enc             = self._var_encoding.get()
                db_data['enc']  = enc
                self._selected_msg['O'] = db_data
                bid             = db_data['bid']
                from_call       = db_data['from_call']
                from_bbs        = db_data['from_bbs_call']
                to              = db_data['to_call']  # Cat
                to_bbs          = db_data['to_bbs']  # Verteiler
                to_bbs_fwd      = db_data['fwd_bbs']  # Verteiler
                subj            = db_data['subject']
                msg             = db_data['msg']
                # _path = _db_data[9]
                msg_time        = db_data['tx-time']
                size            = format_number(len(msg))
                msg             = msg.decode(enc, 'ignore')
                msg             = str(msg).replace('\r', '\n')
                if from_bbs:
                    from_call   = from_call + ' @ ' + from_bbs
                if to_bbs:
                    to = to + ' @ ' + to_bbs

                to += f' > {to_bbs_fwd}'

                self._var_out_from_label.set(f"From     : {from_call}")
                self._var_out_to_label.set(f"To          : {to}")
                self._var_out_subj_label.set(f"Subject : {subj}")
                self._var_out_time_label.set(f"{msg_time}")
                self._var_out_bid_label.set(f"BID: {bid}")
                self._var_out_msg_size.set(f' Size: {size} Bytes')

                self._out_text.insert('1.0', msg)

            self._out_text.configure(state='disabled')

    ################################
    # Save Tab PMS
    def _update_SV_tree_data(self):
        self._get_SV_data()
        self._format_SV_tree_data()
        self._update_SV_tree()

    def _get_SV_data(self):
        self._sv_data = self._bbs_obj.get_sv_msg_tab()

    def _get_SV_MSG_data(self, mid):
        # TODO by PMS User-Call
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
        self._sv_selected = []
        for selected_item in self._sv_tree.selection():
            item = self._sv_tree.item(selected_item)
            mid = item['tags'][1]
            self._sv_selected.append(mid)
        if mid:
            self._SV_show_msg_fm_MID(mid)
            # self._update_SV_tree_data()

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
                enc            = self._var_encoding.get()
                db_data['enc'] = enc
                self._selected_msg['S'] = db_data
                mid             = db_data['mid']
                from_call       = db_data['from_call']
                from_bbs        = db_data['from_bbs']
                to_call         = db_data['to_call']  # Cat
                to_bbs          = db_data['to_bbs']  # Verteiler
                subj            = db_data['subject']
                msg             = db_data['msg']
                msg_time        = db_data['time']
                size            = format_number(len(msg))
                msg             = msg.decode(enc, 'ignore')
                msg             = str(msg).replace('\r', '\n')
                if from_bbs:
                    from_call = from_call + ' @ ' + from_bbs
                if to_bbs:
                    to_call = to_call + ' @ ' + to_bbs

                self._var_sv_from_label.set(f"From     : {from_call}")
                self._var_sv_to_label.set(f"To          : {to_call}")
                self._var_sv_subj_label.set(f"Subject : {subj}")
                self._var_sv_time_label.set(f"{msg_time}")
                self._var_sv_bid_label.set(f"MID : {mid}")
                self._var_sv_msg_size.set(f' Size: {size} Bytes')

                self._sv_text.insert('1.0', msg)

            self._sv_text.configure(state='disabled')

    def _delete_SV_btn(self):
        for mid in self._sv_selected:
            self._bbs_obj.del_sv_by_MID(mid)
        self._sv_selected = []
        self._update_SV_tree_data()
    ####################
