import tkinter as tk
from tkinter import ttk

from bbs.bbs_constant import CR, LF
from cfg.constant import FONT, COLOR_MAP, ENCODINGS
from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import delete_tree
from fnc.str_fnc import get_strTab, format_number
from gui.bbs_gui.guiBBS_newMSG import BBS_newMSG
from gui.guiMsgBoxes import save_file_dialog
from gui.gui_classes.guiRightClick_Menu import ContextMenu


class MSG_Center_base(ttk.Frame):
    def __init__(self, root_win):
        ttk.Frame.__init__(self, root_win)
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.style              = root_win.style
        self._root_win          = root_win
        self._bbs_obj           = root_win.bbs_obj
        self._popt_handler      = root_win.get_popt_handler()
        self.newPMS_MSG_win     = self._root_win.newPMS_MSG_win
        self.text_size          = root_win.text_size
        self._text_size_tabs    = 10
        self._sort_rev          = False
        self._last_sort_col     = {}
        self._selected_msg      = {
            'P': {}, 'B': {}, 'O': {}, 'S': {}, 'F': {}, 'H': {}, 'T': {},
        }
        self.style_name    = self._root_win.style_name
        self._get_colorMap = lambda: COLOR_MAP.get(self.style_name, ('black', '#d9d9d9'))
        self._var_encoding = tk.StringVar(self, 'UTF-8')

        self._tabControl = ttk.Notebook(self)
        self._tabControl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._pn_tree       = None
        self._bl_tree       = None
        self._bl_cat_tree   = None
        self._out_tree      = None
        self._sv_tree       = None
        self._hold_tree     = None
        self._trash_tree    = None

        self._pn_text       = None
        self._bl_text       = None
        self._out_text      = None
        self._sv_text       = None
        self._fwdQ_text     = None
        self._hold_text     = None
        self._trash_text    = None

        self._BL_selected   = []
        self._PN_selected   = []
        self._OUT_selected  = []

        self._text_tab = {}

    # ================================================================
    # Layout Factories
    # ================================================================
    @staticmethod
    def _build_vertical_split(parent, weight_top=1, weight_bot=1):
        pw = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        top_f = ttk.Frame(pw)
        lower_main = ttk.Frame(pw)
        lower_inner = ttk.Frame(lower_main)
        for w in (top_f, lower_main, lower_inner):
            w.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pw.add(top_f, weight=weight_top)
        pw.add(lower_main, weight=weight_bot)
        pw.pack(fill=tk.BOTH, expand=True)
        return top_f, lower_inner

    @staticmethod
    def _build_horizontal_split(parent, weight_left=0, weight_right=1):
        pw = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        left_f = ttk.Frame(pw)
        right_f = ttk.Frame(pw)
        pw.add(left_f, weight=weight_left)
        pw.add(right_f, weight=weight_right)
        pw.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        return left_f, right_f

    def _build_tree(self, parent, columns_spec, callback, selectmode='browse'):
        cols = [c[0] for c in columns_spec]
        tree = ttk.Treeview(parent, columns=cols, show='headings', selectmode=selectmode)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        for cid, hdg, w, st, anc in columns_spec:
            tree.heading(cid, text=hdg, command=lambda c=cid: self._sort_entry(c, tree))
            tree.column(cid, anchor=anc, stretch=st, width=w)
        tree.bind('<<TreeviewSelect>>', callback)
        return tree

    @staticmethod
    def _build_category_tree(parent, callback):
        tree = ttk.Treeview(parent, columns=('cat',), show="tree")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        tree.column("#0", width=0, stretch=False)
        tree.column("cat", anchor='w', stretch=True, width=100)
        tree.bind('<<TreeviewSelect>>', callback)
        return tree

    def _build_text_widget(self, parent):
        f = ttk.Frame(parent)
        f.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        txt = tk.Text(f, font=(FONT, self.text_size), bd=0, height=3,
                      borderwidth=0, background='black', foreground='white',
                      state="disabled", relief="flat", highlightthickness=0)
        sb = ttk.Scrollbar(f, orient=tk.VERTICAL, command=txt.yview)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        txt.config(yscrollcommand=sb.set)
        return txt

    def _build_header_labels(self, parent, prefix, show_rx_time=False):
        hf = ttk.Frame(parent, height=80)
        hf.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        h = lambda f: tk.StringVar(self, '')
        setattr(self, f'_var_{prefix}_from_label', h(''))
        setattr(self, f'_var_{prefix}_to_label', h(''))
        setattr(self, f'_var_{prefix}_subj_label', h(''))
        setattr(self, f'_var_{prefix}_time_label', h(''))
        if show_rx_time:
            setattr(self, f'_var_{prefix}_rx_time_label', h(''))
        setattr(self, f'_var_{prefix}_bid_label', h(''))
        setattr(self, f'_var_{prefix}_msg_size', tk.StringVar(self, ' Size: --- Bytes'))
        g = lambda n: getattr(self, n)
        ttk.Label(hf, textvariable=g(f'_var_{prefix}_from_label')).place(x=2, y=0)
        ttk.Label(hf, textvariable=g(f'_var_{prefix}_to_label')).place(x=2, y=25)
        ttk.Label(hf, textvariable=g(f'_var_{prefix}_subj_label')).place(x=2, y=50)
        ttk.Label(hf, textvariable=g(f'_var_{prefix}_time_label')).place(relx=0.98, y=11, anchor=tk.E)
        if show_rx_time:
            ttk.Label(hf, textvariable=g(f'_var_{prefix}_rx_time_label')).place(relx=0.98, y=36, anchor=tk.E)
            ttk.Label(hf, textvariable=g(f'_var_{prefix}_bid_label')).place(relx=0.98, y=61, anchor=tk.E)
        else:
            ttk.Label(hf, textvariable=g(f'_var_{prefix}_bid_label')).place(relx=0.98, y=36, anchor=tk.E)

    def _build_encoding_footer(self, parent, callback):
        f = ttk.Frame(parent, height=15)
        f.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        size_var = tk.StringVar(self, ' Size: --- Bytes')
        ttk.Label(f, textvariable=size_var, font=(None, 7)).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        enc_menu = tk.OptionMenu(f, self._var_encoding, *ENCODINGS, command=callback)
        fg, bg = self._get_colorMap()
        enc_menu.configure(font=(None, 6), border=0, borderwidth=0, height=1,
                           fg=fg, bg=bg, relief="flat", highlightthickness=0)
        enc_menu.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        return size_var

    @staticmethod
    def _build_button_bar(parent, left_btns=None, right_btns=None):
        bf = ttk.Frame(parent, height=30)
        bf.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        fl = ttk.Frame(bf)
        fr = ttk.Frame(bf)
        fl.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
        fr.pack(side=tk.LEFT, expand=False, anchor='e')
        if left_btns:
            for text, cmd in left_btns:
                ttk.Button(fl, text=text, command=cmd).pack(side=tk.LEFT, expand=False)
        if right_btns:
            for text, cmd in right_btns:
                ttk.Button(fr, text=text, command=cmd).pack(side=tk.RIGHT, expand=False)
        return bf

    def _build_tab_content(self, parent, prefix, enc_callback,
                           left_btns=None, right_btns=None,
                           show_rx_time=False):
        self._build_button_bar(parent, left_btns, right_btns)
        self._build_header_labels(parent, prefix, show_rx_time)
        txt = self._build_text_widget(parent)
        setattr(self, f'_{prefix}_text', txt)
        size_var = self._build_encoding_footer(parent, lambda e: enc_callback())
        return txt, size_var

    # ================================================================
    # Tree Helpers
    # ================================================================
    def _fill_tree(self, tree, data, tag_fn, sort_col=None):
        delete_tree(tree)
        for row in data:
            tree.insert('', tk.END, values=row, tags=tag_fn(row))
        if sort_col:
            self._update_sort_entry(tree, sort_col)

    def _configure_tree_tags(self, tree):
        tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

    # ================================================================
    # Message Display Helpers
    # ================================================================

    @staticmethod
    def _decode_msg(msg, enc, bbs_style=False):
        if bbs_style:
            msg = msg.replace(CR + LF, LF)
            msg = msg.replace(CR, LF)
            msg = msg.decode(enc, 'ignore')
        else:
            msg = msg.decode(enc, 'ignore')
            msg = str(msg).replace(CR.decode(), LF.decode())
        return msg

    @staticmethod
    def _format_call(call, bbs):
        return f"{call} @ {bbs}" if bbs else call

    def _set_msg_labels(self, prefix, from_call='', to_call='', subj='',
                        msg_time='', rx_time=None, bid='', size='',
                        time_suffix='', label='BID'):
        g = lambda n: getattr(self, f'_var_{prefix}_{n}')
        g('from_label').set(f"From     : {from_call}")
        g('to_label').set(f"To          : {to_call}")
        g('subj_label').set(f"Subject : {subj}")
        g('time_label').set(f"{msg_time}{time_suffix}")
        if rx_time is not None and hasattr(self, f'_var_{prefix}_rx_time_label'):
            g('rx_time_label').set(f"RX-Time: {rx_time}         ")
        g('bid_label').set(f"{label}: {bid}")
        g('msg_size').set(f' Size: {size} Bytes')

    def _display_msg(self, text_widget, storage_key, db_data,
                     var_prefix, bbs_style=False, show_header=False,
                     time_field='time', rx_time_field=None,
                     from_bbs_field='from_bbs', to_bbs_field='to_bbs',
                     fwd_bbs_field=None, label='BID', time_suffix=''):
        if not db_data:
            return
        enc = self._var_encoding.get()
        db_data['enc'] = enc
        self._selected_msg[storage_key] = db_data

        bid_val = db_data.get('bid', '')
        from_call = db_data.get('from_call', '')
        from_bbs = db_data.get(from_bbs_field, '')
        to_call = db_data.get('to_call', '')
        to_bbs = db_data.get(to_bbs_field, '')
        subj = db_data.get('subject', '')

        if show_header and db_data.get('header'):
            msg = db_data['header'] + CR + CR + db_data['msg']
        else:
            msg = db_data.get('msg', b'')

        msg_time = db_data.get(time_field, '')
        rx_time = db_data.get(rx_time_field) if rx_time_field else None
        size = format_number(len(msg))

        msg = self._decode_msg(msg, enc, bbs_style)
        from_call = self._format_call(from_call, from_bbs)
        to_call = self._format_call(to_call, to_bbs)

        if fwd_bbs_field:
            to_bbs_fwd = db_data.get(fwd_bbs_field, '')
            if to_bbs_fwd:
                to_call += f' > {to_bbs_fwd}'

        text_widget.configure(state='normal')
        text_widget.delete('1.0', tk.END)
        text_widget.insert('1.0', msg)
        text_widget.configure(state='disabled')

        self._set_msg_labels(var_prefix, from_call=from_call, to_call=to_call,
                             subj=subj, msg_time=msg_time, rx_time=rx_time,
                             bid=bid_val, size=size, time_suffix=time_suffix,
                             label=label)

    def _update_msg_by_encoding(self, storage_key, text_widget):
        msg_data = self._selected_msg[storage_key].get('msg', b'')
        if msg_data:
            enc = self._var_encoding.get()
            self._selected_msg[storage_key]['enc'] = enc
            msg = msg_data.decode(enc, 'ignore')
            msg = str(msg).replace(CR.decode(), LF.decode())
            text_widget.configure(state='normal')
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', msg)
            text_widget.configure(state='disabled')

    def _update_msg_by_encoding_bbs(self, storage_key, text_widget):
        msg_data = self._selected_msg[storage_key].get('msg', b'')
        if msg_data:
            enc = self._var_encoding.get()
            self._selected_msg[storage_key]['enc'] = enc
            msg = msg_data.replace(CR + LF, LF)
            msg = msg.replace(CR, LF)
            msg = msg.decode(enc, 'ignore')
            text_widget.configure(state='normal')
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', msg)
            text_widget.configure(state='disabled')

    # ================================================================
    # Right-Click Menu
    # ================================================================

    def _init_RClick_menu(self):
        for attr in ('_pn_text', '_bl_text', '_out_text', '_sv_text',
                     '_fwdQ_text', '_hold_text', '_trash_text'):
            txt = getattr(self, attr, None)
            if txt:
                men = ContextMenu(txt)
                men.add_item(self._getTabStr('copy'), self.copy_select)
                men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)

    # ================================================================
    # Sort
    # ================================================================

    def _sort_entry(self, col, tree):
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        self._last_sort_col[tree] = col
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    def _update_sort_entry(self, tree, col='Datum'):
        col = self._last_sort_col.get(tree, col)
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=not self._sort_rev)
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    # ================================================================
    # New MSG Wnd
    # ================================================================

    def _open_newMSG_win_reply(self, typ: str):
        if self.newPMS_MSG_win is None:
            if self._selected_msg.get(typ, None):
                msg = dict(self._selected_msg[typ])
                msg['subject'] = ('Re: ' + msg.get('subject', ''))
                self.newPMS_MSG_win = BBS_newMSG(self, msg)

    def _open_newMSG_win_forward(self, typ: str):
        if self.newPMS_MSG_win is None:
            if self._selected_msg.get(typ, None):
                msg = dict(self._selected_msg[typ])
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

    def _do_pms_autoFWD(self):
        self._bbs_obj.start_man_autoFwd()

    # ================================================================
    # Tree Update (stubs / shared)
    # ================================================================

    def tree_update_task(self):
        pass

    def _update_PN_tree_data(self):
        pass

    def _update_BL_tree_data(self):
        pass

    def _update_OUT_tree_data(self):
        self._get_OUT_data()
        self._format_OUT_tree_data()
        self._update_OUT_tree()

    def _format_OUT_tree_data(self):
        self._out_tree_data = []
        for el in self._out_data:
            to_call = f"{el[3]}"
            if el[4]:
                to_call += f"@{el[4]}"
            from_call = f"{el[1]}"
            if el[2]:
                from_call += f"@{el[2]}"
            fwd_done = ''
            if el[8] != 'F':
                fwd_done = '✔'
            tx_time = ''
            if el[9]:
                tx_time = el[9]
            self._out_tree_data.append((
                f'{fwd_done}',
                f'{el[5]}',
                f'{from_call}',
                f'{to_call}',
                f'{el[7]}',
                f'{el[8]}',
                f'{tx_time}',
                f'{el[0]}',
            ))

    def _update_OUT_tree(self):
        pass

    def _get_OUT_data(self):
        self._out_data = self._bbs_obj.get_out_tab()

    def _get_OUT_MSG_data(self, bid):
        return self._bbs_obj.get_out_msg_fm_BID(bid)

    def _update_SV_tree_data(self):
        pass

    def _update_hold_tree_data(self):
        pass

    def _update_trash_tree_data(self):
        pass

    def on_bbsTab_select(self, event=None):
        pass

    def _set_all_to_oldMSG(self):
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

    def _save_outMSG(self):
        bid = self._selected_msg['O'].get('bid', '')
        if bid:
            mid = int(bid[:6])
            self._bbs_obj.get_db().pms_save_outMsg_by_MID(mid)

    # ================================================================
    # Copy / Save
    # ================================================================

    def copy_select(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        text = self._text_tab.get(ind, None)
        if text is None:
            return
        if text.tag_ranges("sel"):
            self.clipboard_clear()
            self.clipboard_append(text.selection_get())
            text.tag_remove(tk.SEL, "1.0", tk.END)

    def _save_msg_to_file(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        msg_text = self._text_tab.get(ind, None)
        if msg_text:
            data = msg_text.get('1.0', tk.END)[:-1]
            save_file_dialog(data, self._root_win)

    # ================================================================
    # Delete
    # ================================================================

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
            }.get(ind, None)
            if tree is None:
                return
            tr = False
            for selected_item in tree.selection():
                item = tree.item(selected_item)
                _, bid = item['tags']
                if del_fnc(bid):
                    tr = True
            if tr:
                self.on_bbsTab_select()
                self.tree_update_task()
            bid_next_msg = ''
            ind_ex = 0
            for i in tree.get_children():
                ind_ex += 1
                if tree.item(i)['tags'][1] in bid_mid:
                    try:
                        bid_next_msg = tree.item(tree.get_children()[ind_ex]).get('tags', [])
                        if len(bid_next_msg) == 2:
                            bid_next_msg = bid_next_msg[1]
                    except IndexError:
                        pass
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

    def _delete_PN(self, bid: str):
        if bid:
            return self._bbs_obj.del_in_by_BID(bid)
        return False

    def _delete_PN_btn(self):
        if not self._PN_selected:
            return
        self._bbs_obj.del_in_by_BID_list(self._PN_selected)
        self._PN_selected = []
        self._update_PN_tree_data()
        self._update_trash_tree_data()

    def _delete_BL(self, bid: str):
        if bid:
            return self._bbs_obj.del_in_by_BID(bid)
        return False

    def _delete_BL_btn(self):
        if not self._BL_selected:
            return
        self._bbs_obj.del_in_by_BID_list(self._BL_selected)
        self._BL_selected = []
        self._update_BL_tree_data()
        self._update_trash_tree_data()

    def _delete_OUT(self, bid: str):
        if bid:
            return self._bbs_obj.del_out_by_BID(bid)
        return False

    def _delete_OUT_btn(self):
        if not self._OUT_selected:
            return
        self._bbs_obj.del_out_by_BID_list(self._OUT_selected)
        self._OUT_selected = []
        self._update_OUT_tree_data()
        self._update_trash_tree_data()

    def _delete_SV(self, bid: str):
        if bid:
            return self._bbs_obj.del_sv_by_MID(bid)
        return False

    # ================================================================
    # Show Msg Stubs (overridden by subclasses)
    # ================================================================

    def _PN_show_msg_fm_BID(self, mid):
        pass

    def _BL_show_msg_fm_BID(self, mid):
        pass

    def _OUT_show_msg_fm_BID(self, mid):
        pass

    def _SV_show_msg_fm_MID(self, mid):
        pass

    # ================================================================
    # GUI: Text Size
    # ================================================================

    def _resize_texts(self, delta):
        self.text_size = max(self.text_size + delta, 3)
        for attr in ('_bl_text', '_pn_text', '_out_text', '_sv_text',
                     '_fwdQ_text', '_hold_text', '_trash_text'):
            txt = getattr(self, attr, None)
            if txt and hasattr(txt, 'configure'):
                txt.configure(font=(FONT, self.text_size))

    def increase_textsize(self):
        self._resize_texts(1)

    def decrease_textsize(self):
        self._resize_texts(-1)

    def update_textsize_trees(self):
        for tree in (self._bl_tree, self._pn_tree, self._bl_cat_tree):
            if tree:
                tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
                tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))

    def get_popt_handler(self):
        return self._popt_handler
