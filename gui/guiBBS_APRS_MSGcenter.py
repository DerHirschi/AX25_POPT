import logging
import tkinter as tk
from tkinter import ttk, scrolledtext

from ax25.ax25InitPorts import PORT_HANDLER
from string_tab import STR_TABLE

logger = logging.getLogger(__name__)


class MSG_Center(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        self._bbs_obj = PORT_HANDLER.get_bbs()
        # self._ais_obj.wx_tree_gui = self
        ###################################
        # Vars
        self._rev_ent = False
        self._last_sort_col = None
        # self.mh_win = tk.Tk()
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
        self._rev_ent = False
        ####################
        self._init_Menu()
        ######################################################################
        upper_frame = tk.Frame(self, )
        upper_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_type = ttk.Notebook(
            upper_frame,
            padding=5,
            # height=300,
            # width=500
        )
        self._tabControl_type.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        BBS_tab_frame = tk.Frame(self)
        BBS_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        APRS_tab_frame = tk.Frame(self, background='green')
        APRS_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_type.add(BBS_tab_frame, text='PMS', padding=8)
        self._tabControl_type.add(APRS_tab_frame, text='APRS', padding=8)
        # style = ttk.Style(self)
        # style.configure('TNotebook', tabposition='s')
        self._tabControl = ttk.Notebook(
            BBS_tab_frame,
            # style='TNotebook'
            # height=300,
            # width=500
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
        self._bl_text = None
        self._init_bl_lower_frame(lower_f_lower)

    def _init_Menu(self):
        _menubar = tk.Menu(self, tearoff=False)
        self.config(menu=_menubar)
        _MenuVerb = tk.Menu(_menubar, tearoff=False)
        _MenuVerb.add_command(label='New Mail')
        _menubar.add_cascade(label='Mail', menu=_MenuVerb, underline=0)

    def _init_pn_tree(self, root_frame):
        columns = (
            'Neu',
            'Betreff',
            'Von',
            'Datum',
        )

        self._pn_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
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
        self._pn_tree.column("Datum", anchor='w', stretch=tk.NO, width=200)

        self._pn_tree.tag_configure('neu', font=(None, 10, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, 10, ''))

    def _init_bl_tree(self, root_frame):
        columns = (
            'Neu',
            'Betreff',
            'Von',
            'An',
            'vert',
            'Datum',
        )

        self._bl_tree = ttk.Treeview(root_frame, columns=columns, show='headings')
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
        self._bl_tree.column("Datum", anchor='w', stretch=tk.NO, width=200)

        self._bl_tree.tag_configure('neu', font=(None, 10, 'bold'))
        self._bl_tree.tag_configure('alt', font=(None, 10, ''))

    def _init_pn_lower_frame(self, root_frame):
        btn_frame = tk.Frame(root_frame, height=30)
        header_frame = tk.Frame(root_frame, height=80)
        btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        header_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        tk.Button(btn_frame, text='Speichern').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Löschen').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Weiterleiten').pack(side=tk.RIGHT, expand=False)
        tk.Button(btn_frame, text='Antworten').pack(side=tk.RIGHT, expand=False)

        from_label = tk.Label(header_frame, text='From: MD2SAW@MD2BBS.#SAW.SAA.DEU.EU(Manuel)')
        from_label.place(x=2, y=0)
        to_label = tk.Label(header_frame, text='To: MD2SAW')
        to_label.place(x=2, y=25)
        topic_label = tk.Label(header_frame, text='Betreff: Test Mail bla')
        topic_label.place(x=2, y=50)
        time_label = tk.Label(header_frame, text='2023-10-31 09:21:29')
        time_label.place(relx=0.98, y=36, anchor=tk.E)

        # ## lower_f_lower / Msg Text
        self._pn_text = scrolledtext.ScrolledText(root_frame,
                                                  font=("Courier", 10),
                                                  bd=0,
                                                  borderwidth=0,
                                                  state="disabled",
                                                  )
        self._pn_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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

        self._bl_cat_tree.tag_configure('neu', font=(None, 10, 'bold'))
        self._bl_cat_tree.tag_configure('alt', font=(None, 10, ''))

        self._bl_cat_tree.bind('<<TreeviewSelect>>', self._BL_entry_selected)

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
        from_label = tk.Label(header_frame, text='From: MD2SAW@MD2BBS.#SAW.SAA.DEU.EU(Manuel)')
        from_label.place(x=2, y=0)
        to_label = tk.Label(header_frame, text='To: MD2SAW')
        to_label.place(x=2, y=25)
        topic_label = tk.Label(header_frame, text='Betreff: Test Mail bla')
        topic_label.place(x=2, y=50)
        time_label = tk.Label(header_frame, text='2023-10-31 09:21:29')
        time_label.place(relx=0.98, y=36, anchor=tk.E)

        # ## lower_f_lower / Msg Text
        self._bl_text = scrolledtext.ScrolledText(root_frame,
                                                  font=("Courier", 10),
                                                  bd=0,
                                                  borderwidth=0,
                                                  state="disabled",
                                                  )
        self._bl_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    ################################
    # PN
    def _update_PN_tree_data(self):
        self._get_PN_data()
        self._format_PN_tree_data()
        self._update_PN_tree()

    def _get_PN_data(self):
        self._pn_data = list(self._bbs_obj.get_pn_msg_tab())

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
            ))

    def _update_PN_tree(self):
        for i in self._pn_tree.get_children():
            self._pn_tree.delete(i)
        for ret_ent in self._pn_tree_data:
            if ret_ent[0]:
                tag = 'neu'
            else:
                tag = 'alt'
            self._pn_tree.insert('', tk.END, values=ret_ent, tags=(tag,))

    ###########
    # Bulletin
    def _update_BL_tree_data(self):
        self._get_BL_data()
        self._format_BL_tree_data()
        self._update_BL_tree()
        self._update_CAT_tree()

    def _get_BL_data(self):
        self._bl_data = list(self._bbs_obj.get_bl_msg_tab())

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
            self._bl_tree.insert('', tk.END, values=ret_ent, tags=(tag,))

    # Buletin Category
    def _update_CAT_tree(self):
        for i in self._bl_cat_tree.get_children():
            self._bl_cat_tree.delete(i)
        for ret_ent in self._bl_cat_tree_data:
            if ret_ent[0]:
                tag = 'neu'
            else:
                tag = 'alt'
            self._bl_cat_tree.insert('', tk.END, values=ret_ent[1], tags=(tag,))

    def _BL_entry_selected(self, event=None):
        for selected_item in self._bl_cat_tree.selection():
            item = self._bl_cat_tree.item(selected_item)
            record = item['values']
            if record[0] == 'ALL*':
                self._bl_cat_filter = ''
            else:
                self._bl_cat_filter = str(record[0])
        self._update_BL_tree_data()

    #####################################
    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        _tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        _tmp.sort(reverse=self._rev_ent)
        self._rev_ent = not self._rev_ent
        for index, (val, k) in enumerate(_tmp):
            tree.move(k, '', int(index))

    def _close(self):
        self._bbs_obj = None
        self._root_win.MSG_Center = None
        self.destroy()
