import datetime
import time
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from ax25.ax25InitPorts import PORT_HANDLER
from ax25aprs.aprs_dec import format_aprs_f_aprs_mon
from cfg.constant import FONT, SQL_TIME_FORMAT
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import tk_filter_bad_chars, get_strTab


class AISmonitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_cl       = root_win
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._text_size     = int(self._root_cl.text_size)
        self._win_height    = 700
        self._win_width     = 1500
        # self.style = self._root_cl.style
        self.title(self._getTabStr('aprs_mon'))
        self.geometry(f"{self._win_width}x"
                      f"{self._win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        # self.resizable(False, False)
        self.lift()
        ##############################################
        self._ais_obj = PORT_HANDLER.get_aprs_ais()
        self._ais_aprs_stations     = {}
        self._ais_aprs_stat_calls   = []
        self._tree_data             = []
        self._sort_rev              = False
        ####
        self._tasker_q_timer        = time.time()
        self._tasker_q              = []
        ##############################################
        self._autoscroll_var        = tk.BooleanVar(self, value=True)
        self._new_user_var          = tk.BooleanVar(self, value=False)
        self._call_filter           = tk.BooleanVar(self, value=False)
        self._call_filter_calls_var = tk.StringVar(self)
        ##############################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ##############################################
        pw      = ttk.PanedWindow(main_f, orient='horizontal')
        pw.pack(fill='both', expand=True)
        tree_f  = ttk.Frame(pw)
        mon_f   = ttk.Frame(pw)
        pw.add(tree_f, weight=1)
        pw.add(mon_f,  weight=1)

        ##############################################
        # Frame für den linken Bereich
        columns = (
            'rx_time',
            'from',
            'to',
            'path',
            'via',
            'loc',
            'typ',
            'comment',
            'raw',
        )
        self._tree = ttk.Treeview(tree_f, columns=columns, show='headings')
        self._tree.pack(side='left', fill='both', expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_f, orient='vertical', command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='left', fill='y')

        self._tree.heading('rx_time', text=self._getTabStr('date_time'), command=lambda: self._sort_entry('rx_time', self._tree))
        self._tree.heading('from',    text=self._getTabStr('from'),      command=lambda: self._sort_entry('from', self._tree))
        self._tree.heading('to',      text=self._getTabStr('to'),        command=lambda: self._sort_entry('to', self._tree))
        self._tree.heading('path',    text='Path',                       command=lambda: self._sort_entry('path', self._tree))
        self._tree.heading('via',     text='VIA',                        command=lambda: self._sort_entry('via', self._tree))
        self._tree.heading('loc',     text='Locator',                    command=lambda: self._sort_entry('loc', self._tree))
        self._tree.heading('typ',     text='Typ',                        command=lambda: self._sort_entry('typ', self._tree))
        self._tree.heading('comment', text=self._getTabStr('message'),   command=lambda: self._sort_entry('comment', self._tree))
        self._tree.heading('raw',     text='RAW',                        command=lambda: self._sort_entry('raw', self._tree))
        self._tree.column("rx_time",  anchor='w', stretch=False, width=130)
        self._tree.column("from",     anchor='w', stretch=False, width=80)
        self._tree.column("to",       anchor='w', stretch=False, width=80)
        self._tree.column("path",     anchor='w', stretch=False, width=200)
        self._tree.column("via",      anchor='w', stretch=False, width=80)
        self._tree.column("loc",      anchor='w', stretch=False, width=120)
        self._tree.column("typ",      anchor='w', stretch=False, width=100)
        self._tree.column("comment",  anchor='w', stretch=True,  width=280)
        self._tree.column("raw",      anchor='w', stretch=True,  width=280)
        ##############################################
        # Frame für den rechten Bereich
        left_frame  = ttk.Frame(mon_f)
        right_frame = ttk.Frame(mon_f)
        text_frame  = ttk.Frame(left_frame)
        left_frame.pack( side=tk.LEFT,  padx=10, pady=10, fill=tk.BOTH, expand=True)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        text_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self._text_widget = ScrolledText(text_frame,
                                         background='black',
                                         foreground='green',
                                         width=85
                                         )
        self._text_widget.configure(font=(FONT, self._text_size))
        self._text_widget.pack(fill=tk.BOTH, expand=True)

        # Frame für den rechten Bereich
        ttk.Checkbutton(right_frame,
                       variable=self._autoscroll_var,
                       text="Autoscroll  ",
                       command=self._scroll_to_end).pack(side=tk.TOP, padx=2)
        ttk.Checkbutton(right_frame,
                       variable=self._new_user_var,
                       text="UserDB      ",
                       command=self._chk_new_user
                       ).pack(side=tk.TOP, padx=2)
        ttk.Checkbutton(right_frame,
                       variable=self._call_filter,
                       text="Call-Filter  ",
                       command=self._chk_call_filter
                       ).pack(side=tk.TOP, padx=2)

        ttk.Label(right_frame, text="Call-Filter:").pack(side=tk.TOP, padx=2)
        ttk.Entry(right_frame,
                 textvariable=self._call_filter_calls_var,
                 width=20
                 ).pack(side=tk.TOP, padx=2)
        ##########
        ttk.Button(right_frame,
                  text=self._getTabStr('delete'),
                  command=self._del_buffer
                  ).pack(side=tk.TOP, padx=2)

        ########################################################
        if self._ais_obj is not None:
            self._new_user_var.set(self._ais_obj.add_new_user)
        self.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())
        ########################################################


        if self._ais_obj is not None:
            self._ais_aprs_stations = self._ais_obj.ais_aprs_stations
            self._ais_aprs_stat_calls.append(self._ais_obj.ais_call)
            self._ais_obj.ais_mon_gui = self
            """
            for port_id in self._ais_aprs_stations.keys():
                if self._ais_aprs_stations[port_id].aprs_parm_call:
                    self._ais_aprs_stat_calls.append(
                        self._ais_aprs_stations[port_id].aprs_parm_call
                    )
            """
        root_win.aprs_mon_win = self
        self._init_ais_mon()
        self._update_tree()

    #############################################################
    @staticmethod
    def _sort_entry(col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        """
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))
        """
        pass

    def _update_tree(self):
        self._del_tree()
        for ret_ent in self._tree_data:
            self._add_to_tree(tree_data=ret_ent)

    def _del_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)

    def _add_to_tree(self, tree_data: tuple, add_to_end=True):
        is_scrolled_to_top = self._tree.yview()[0] == 0.0
        if add_to_end:
            self._tree.insert('', 'end', values=tree_data)
        else:
            self._tree.insert('', 0, values=tree_data)

        if not is_scrolled_to_top and not add_to_end:
            try:
                self._tree.yview_scroll(1, "units")
            except Exception as e:
                logger.warning(e)
                pass

    @staticmethod
    def _get_treedata_fm_pack(aprs_pack: dict):
        text = aprs_pack.get('text', '')
        if not text and aprs_pack.get('comment', ''):
            text = aprs_pack.get('comment', '')
        if not text and aprs_pack.get('status', ''):
            text = aprs_pack.get('status', '')

        msg_typ = aprs_pack.get('format', '')
        if aprs_pack.get('subpacket', ''):
            msg_typ = 'subpacket'
        if aprs_pack.get('weather', ''):
            msg_typ = 'weather'

        return (
                aprs_pack.get('rx_time', datetime.datetime.now()).strftime(SQL_TIME_FORMAT),
                aprs_pack.get('from', ''),
                aprs_pack.get('to', ''),
                '>'.join(aprs_pack.get('path', [])),
                aprs_pack.get('via', ''),
                f"{aprs_pack.get('locator', '')}({round(aprs_pack.get('distance', -1))} km)",
                msg_typ,
                text,
                aprs_pack.get('raw', ''),
            )

    def _add_treedata(self, tree_data: tuple):
        self._tree_data = [tree_data] + self._tree_data
        self._tree_data = self._tree_data[:9001] # Over 9000 !!

    #############################################################
    def _init_ais_mon(self):
        if not self._ais_obj:
            self._text_widget.insert(tk.END, "*** ERROR: No AIS found ***")
            logger.error("*** ERROR: No AIS found ***")
            return
        self._tree_data = []
        tr              = False
        call_filter_var = self._call_filter.get()
        for el in list(self._ais_obj.ais_rx_buff):
            if not el:
                continue
            el: dict
            # Tree
            tree_data = self._get_treedata_fm_pack(el)
            self._add_treedata(tree_data)
            # Monitor
            if call_filter_var:
                if el.get('from', '') in self._ais_aprs_stat_calls:
                    tr = True
                    tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc,
                                                  add_new_user=bool(self._ais_obj.add_new_user))
                    self._text_widget.insert(tk.END, tmp)
            else:
                tr = True
                tmp = format_aprs_f_aprs_mon(el, self._ais_obj.ais_loc,
                                              add_new_user=bool(self._ais_obj.add_new_user))
                self._text_widget.insert(tk.END, tmp)
        if tr:
            self._scroll_to_end()

    def tasker(self):
        if not self._tasker_q:
            return False
        if time.time() < self._tasker_q_timer:
            return False
        self._tasker_q_timer = time.time() + 0.1
        n = 10
        if len(self._tasker_q) > 10:
            logger.warning(f"len(self._tasker_q) > 10: {len(self._tasker_q)}")
            logger.warning(f"self._tasker_q: {self._tasker_q}")
        while self._tasker_q and n:
            task, arg = self._tasker_q[0]
            self._tasker_q = self._tasker_q[1:]
            if task == 'pack_to_mon':
                self._pack_to_mon_task(arg)
            n -= 1

        return True

    def _add_tasker_q(self, fnc: str, arg):
        if (fnc, None) in self._tasker_q:
            return
        self._tasker_q.append((fnc, arg))

    def set_ais_obj(self):
        self._ais_obj = PORT_HANDLER.get_aprs_ais()

    def pack_to_mon(self, pack):
        self._add_tasker_q("pack_to_mon", pack)

    def _pack_to_mon_task(self, pack):
        tr = False
        tree_data = self._get_treedata_fm_pack(pack)
        self._add_treedata(tree_data)
        self._add_to_tree(tree_data, add_to_end=False)
        if self._call_filter.get():
            if pack['from'] in self._ais_aprs_stat_calls:
                tr = True
                tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc,
                                             add_new_user=self._ais_obj.add_new_user)
                tmp = tk_filter_bad_chars(tmp)
                self._text_widget.insert(tk.END, tmp)
        else:
            tr = True
            tmp = format_aprs_f_aprs_mon(pack, self._ais_obj.ais_loc,
                                         add_new_user=self._ais_obj.add_new_user)
            tmp = tk_filter_bad_chars(tmp)
            self._text_widget.insert(tk.END, tmp)

        if tr:
            self._scroll_to_end()

    def _increase_textsize(self):
        self._text_size += 1
        self._text_size = max(self._text_size, 3)
        self._text_widget.configure(font=(FONT, self._text_size))

    def _decrease_textsize(self):
        self._text_size -= 1
        self._text_size = max(self._text_size, 3)
        self._text_widget.configure(font=(FONT, self._text_size))

    def _chk_call_filter(self):
        self._ais_aprs_stations = {}
        self._ais_aprs_stat_calls = []
        if self._ais_obj is not None:
            self._ais_aprs_stations = self._ais_obj.ais_aprs_stations
            self._ais_aprs_stat_calls.append(self._ais_obj.ais_call)
            """
            for port_id in self._ais_aprs_stations.keys():
                if self._ais_aprs_stations[port_id].aprs_parm_call:
                    self._ais_aprs_stat_calls.append(
                        self._ais_aprs_stations[port_id].aprs_parm_call
                    )
            """
        calls = self._call_filter_calls_var.get()
        calls = calls.split(' ')
        tmp = []
        for el in list(calls):
            if el:
                tmp.append(el.upper())
        calls = tmp
        self._ais_aprs_stat_calls = self._ais_aprs_stat_calls + calls

    def _chk_new_user(self):
        if self._ais_obj is not None:
            self._ais_obj.add_new_user = self._new_user_var.get()

    def _del_buffer(self):
        if self._ais_obj is not None:
            self._ais_obj.del_ais_rx_buff()
        self._text_widget.delete(0.0, tk.END)

    def _scroll_to_end(self):
        if self._autoscroll_var.get():
            self._text_widget.see(tk.END)

    def _destroy_win(self):
        # self.tasker = lambda: 0
        self._ais_obj.ais_mon_gui = None
        self._root_cl.aprs_mon_win = None
        # self._ais_obj.ais_rx_buff = self._tmp_buffer + self._ais_obj.ais_rx_buff
        self.destroy()
