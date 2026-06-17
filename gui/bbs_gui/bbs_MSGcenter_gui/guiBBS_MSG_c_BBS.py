import tkinter as tk
from tkinter import ttk

from fnc.gui_fnc import delete_tree
from gui.bbs_gui.bbs_MSGcenter_gui.guiBBS_MSG_c_base import MSG_Center_base


class MSG_Center_BBS(MSG_Center_base):
    def __init__(self, root_win):
        MSG_Center_base.__init__(self, root_win)
        self._tabControl.bind("<<NotebookTabChanged>>", self.on_bbsTab_select)

        tab_PN     = ttk.Frame(self._tabControl)
        tab_BL     = ttk.Frame(self._tabControl)
        tab_OUT    = ttk.Frame(self._tabControl)
        tab_FWD_Q  = ttk.Frame(self._tabControl)
        tab_HOLD   = ttk.Frame(self._tabControl)
        tab_TRASH  = ttk.Frame(self._tabControl)
        self._tabControl.add(tab_PN,    text=self._getTabStr('private'))
        self._tabControl.add(tab_BL,    text='Bulletin')
        self._tabControl.add(tab_OUT,   text=self._getTabStr('msgC_sendet_msg'))
        self._tabControl.add(tab_FWD_Q, text=self._getTabStr('fwd_list'))
        self._tabControl.add(tab_HOLD,  text='Hold')
        self._tabControl.add(tab_TRASH, text=self._getTabStr('msgC_trash_bin'))

        self._init_pn_tab(tab_PN)
        self._init_bl_tab(tab_BL)
        self._init_out_tab(tab_OUT)
        self._init_fwdQ_tab(tab_FWD_Q)
        self._init_hold_tab(tab_HOLD)
        self._init_trash_tab(tab_TRASH)

        self._text_tab = {
            0: self._pn_text,
            1: self._bl_text,
            2: self._out_text,
            3: self._fwdQ_text,
            4: self._hold_text,
            5: self._trash_text,
        }
        self._init_RClick_menu()

    def on_bbsTab_select(self, event=None):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except (tk.TclError, AttributeError):
            return
        enc = {
            0: self._selected_msg['P'].get('enc', 'UTF-8'),
            1: self._selected_msg['B'].get('enc', 'UTF-8'),
            2: self._selected_msg['O'].get('enc', 'UTF-8'),
            3: self._selected_msg['F'].get('enc', 'UTF-8'),
            4: self._selected_msg['H'].get('enc', 'UTF-8'),
        }.get(ind, 'UTF-8')
        self._var_encoding.set(enc)
        self.tree_update_task()

    def tree_update_task(self):
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        {
            0: self._update_PN_tree_data,
            1: self._update_BL_tree_data,
            2: self._update_OUT_tree_data,
            3: self._update_fwdQ_tree_data,
            4: self._update_hold_tree_data,
        }.get(ind, lambda: None)()

    # ================================================================
    # PN Tab
    # ================================================================

    def _init_pn_tab(self, parent):
        top_f, lower_inner = self._build_vertical_split(parent)
        self._pn_tree = self._build_tree(top_f, [
            ('msgid',   'MSG-ID',                         60,  False, 'w'),
            ('bid',     'BID',                            150, False, 'w'),
            ('Betreff', self._getTabStr('subject'),       190, True,  'w'),
            ('Von',     self._getTabStr('from'),          130, True,  'w'),
            ('An',      self._getTabStr('to'),            130, True,  'w'),
            ('flag',    'Flag',                           60,  False, 'w'),
            ('notnew',  self._getTabStr('read_ed'),       40,  False, 'w'),
            ('Datum',   self._getTabStr('date_time'),     220, False, 'w'),
        ], self._PN_entry_selected, selectmode='extended')
        self._pn_tree_data = []
        self._pn_data = []
        self._update_PN_tree_data()
        self._build_tab_content(lower_inner, 'pn', self._update_PN_msg,
            right_btns=[
                (self._getTabStr('delete'), self._delete_PN_btn),
            ],
            show_rx_time=True)

    def _update_PN_tree_data(self):
        self._get_PN_data()
        self._format_PN_tree_data()
        self._update_PN_tree()

    def _get_PN_data(self):
        self._pn_data = self._bbs_obj.get_pn_msg_tab()

    def _get_PN_MSG_data(self, bid):
        return self._bbs_obj.get_pn_msg_fm_BID(bid)

    def _format_PN_tree_data(self):
        self._pn_tree_data = []
        for el in self._pn_data:
            from_call = f"{el[2]}"
            if el[3]:
                from_call += f"@{el[3]}"
            to_call = f"{el[4]}"
            if el[5]:
                to_call += f"@{el[5]}"
            new = '✓'
            if int(el[8]):
                new = ''
            date = el[7]
            tmp = str(date).split('-')[0]
            if len(tmp) == 2:
                date = '20' + date
            self._pn_tree_data.append((
                f'{int(el[0]):06d}',  f'{el[1]}',  f'{el[6]}',  f'{from_call}',
                f'{to_call}', f'{el[9]}', f'{new}',    f'{date}',
            ))

    def _update_PN_tree(self):
        self._fill_tree(self._pn_tree, self._pn_tree_data,
                        lambda r: ('dummy', r[1]),
                        'Datum')

    def _PN_entry_selected(self, event=None):
        self._PN_selected = []
        bid = ''
        for item in self._pn_tree.selection():
            bid = self._pn_tree.item(item)['tags'][1]
            self._PN_selected.append(bid)
        if bid:
            self._PN_show_msg_fm_BID(bid)

    def _update_PN_msg(self, event=None):
        self._update_msg_by_encoding_bbs('P', self._pn_text)

    def _PN_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_PN_MSG_data(bid)
        if db_data:
            self._display_msg(self._pn_text, 'P', db_data,
                              var_prefix='pn', bbs_style=True, show_header=True,
                              time_field='time', rx_time_field='rx-time',
                              time_suffix=' (utc)')

    # ================================================================
    # BL Tab
    # ================================================================

    def _init_bl_tab(self, parent):
        left_f, right_f = self._build_horizontal_split(parent, weight_left=0, weight_right=1)
        top_f, lower_inner = self._build_vertical_split(right_f)

        self._bl_cat_filter = ''
        self._bl_cat_tree_data = []
        self._bl_cat_tree = self._build_category_tree(left_f, self._CAT_entry_selected)
        self._configure_tree_tags(self._bl_cat_tree)

        self._bl_tree = self._build_tree(top_f, [
            ('msgid',   'MSG-ID',                         60,  False, 'w'),
            ('bid',     'BID',                            150, False, 'w'),
            ('Betreff', self._getTabStr('subject'),       270, True,  'w'),
            ('Von',     self._getTabStr('from'),          180, True,  'w'),
            ('An',      self._getTabStr('to'),            100, True,  'w'),
            ('vert',    '@',                              50,  False, 'w'),
            ('flag',    'Flag',                           60,  False, 'w'),
            ('Datum',   self._getTabStr('date_time'),     220, False, 'w'),
        ], self._BL_entry_selected)
        self._bl_tree_data = []
        self._bl_data = []
        self._update_BL_tree_data()

        self._build_tab_content(lower_inner, 'bl', self._update_BL_msg,
            right_btns=[
                (self._getTabStr('delete'), self._delete_BL_btn),
            ],
            show_rx_time=True)

    def _update_BL_tree_data(self):
        self._get_BL_data()
        self._format_BL_tree_data()
        self._update_BL_tree()
        self._update_CAT_tree()

    def _get_BL_data(self):
        self._bl_data = self._bbs_obj.get_bl_msg_tab()

    def _format_BL_tree_data(self):
        self._bl_tree_data = []
        self._bl_cat_tree_data = []
        for el in self._bl_data:
            from_call = f"{el[2]}"
            if el[3]:
                from_call += f"@{el[3]}"
            date = el[7]
            tmp = str(date).split('-')[0]
            if len(tmp) == 2:
                date = '20' + date
            if not self._bl_cat_filter or self._bl_cat_filter == el[4]:
                self._bl_tree_data.append((
                    f'{int(el[0]):06d}',  f'{el[1]}',  f'{el[6]}',  f'{from_call}',
                    f'{el[4]}',  f'{el[5]}',  f'{el[9]}',  f'{date}',
                ))
        for el in self._bl_data:
            if (False, el[4]) not in self._bl_cat_tree_data:
                self._bl_cat_tree_data.append((False, el[4]))
        self._bl_cat_tree_data.sort(key=lambda x: x[1])
        self._bl_cat_tree_data = [(False, 'ALL*')] + self._bl_cat_tree_data

    def _update_BL_tree(self):
        self._fill_tree(self._bl_tree, self._bl_tree_data,
                        lambda r: ('dummy', r[1]),
                        'Datum')

    def _BL_entry_selected(self, event=None):
        self._BL_selected = []
        bid = ''
        for item in self._bl_tree.selection():
            bid = self._bl_tree.item(item)['tags'][1]
            self._BL_selected.append(bid)
        if bid:
            self._BL_show_msg_fm_BID(bid)

    def _update_BL_msg(self, event=None):
        self._update_msg_by_encoding_bbs('B', self._bl_text)

    def _BL_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_BL_MSG_data(bid)
        if db_data:
            self._display_msg(self._bl_text, 'B', db_data,
                              var_prefix='bl', bbs_style=True, show_header=True,
                              time_field='time', rx_time_field='rx-time',
                              time_suffix=' (utc)')

    def _get_BL_MSG_data(self, bid):
        return self._bbs_obj.get_bl_msg_fm_BID(bid)

    # ================================================================
    # Bulletin Category
    # ================================================================

    def _update_CAT_tree(self):
        delete_tree(self._bl_cat_tree)
        for tr, cat in self._bl_cat_tree_data:
            tag = 'neu' if tr else 'alt'
            self._bl_cat_tree.insert('', tk.END, values=cat, tags=(tag,))

    def _CAT_entry_selected(self, event=None):
        for item in self._bl_cat_tree.selection():
            record = self._bl_cat_tree.item(item)['values']
            self._bl_cat_filter = '' if record[0] == 'ALL*' else str(record[0])
        self._update_BL_tree_data()

    # ================================================================
    # OUT Tab
    # ================================================================

    def _init_out_tab(self, parent):
        top_f, lower_inner = self._build_vertical_split(parent)
        self._out_tree = self._build_tree(top_f, [
            ('gesendet', '  ',                             40,  False, 'center'),
            ('Betreff',  self._getTabStr('subject'),       230, True,  'w'),
            ('Von',      self._getTabStr('from'),          100, True,  'w'),
            ('An',       self._getTabStr('to'),            100, True,  'w'),
            ('typ',      'TYP',                            45,  False, 'w'),
            ('flag',     'Flag',                           45,  False, 'w'),
            ('Datum',    'TX-Time',                        220, False, 'w'),
        ], self._OUT_entry_selected)
        self._out_tree_data = []
        self._out_data = []
        self._update_OUT_tree_data()

        self._build_tab_content(lower_inner, 'out', self._update_OUT_msg,
            right_btns=[
                (self._getTabStr('delete'), self._delete_OUT_btn),
            ])

    def _update_OUT_tree(self):
        self._fill_tree(self._out_tree, self._out_tree_data,
                        lambda r: ('dummy', r[-1]),
                        'Datum')

    def _OUT_entry_selected(self, event=None):
        self._OUT_selected = []
        bid = ''
        for item in self._out_tree.selection():
            bid = self._out_tree.item(item)['tags'][1]
            self._OUT_selected.append(bid)
        if bid:
            self._OUT_show_msg_fm_BID(bid)

    def _update_OUT_msg(self, event=None):
        self._update_msg_by_encoding_bbs('O', self._out_text)

    def _OUT_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_OUT_MSG_data(bid)
        if db_data:
            self._display_msg(self._out_text, 'O', db_data,
                              var_prefix='out', bbs_style=True, show_header=True,
                              time_field='tx-time',
                              from_bbs_field='from_bbs_call',
                              fwd_bbs_field='fwd_bbs')

    # ================================================================
    # FWD-Q Tab
    # ================================================================

    def _init_fwdQ_tab(self, parent):
        top_f, lower_inner = self._build_vertical_split(parent)
        self._fwdQ_tree = self._build_tree(top_f, [
            ('mid',     'MID',                            65,  False, 'w'),
            ('bid',     'BID',                            120, False, 'w'),
            ('Betreff', self._getTabStr('subject'),       230, True,  'w'),
            ('Von',     self._getTabStr('from'),          120, True,  'w'),
            ('An',      self._getTabStr('to'),            120, True,  'w'),
            ('fwd_bbs', f"{self._getTabStr('to')} BBS",   60,  True,  'w'),
            ('typ',     'TYP',                            45,  False, 'w'),
            ('size',    'Size',                           80,  False, 'w'),
            ('flag',    'Flag',                           60,  False, 'w'),
            ('trys',    'Try s',                          80,  False, 'w'),
        ], self._fwdQ_entry_selected)
        self._fwdQ_tree_data = []
        self._fwdQ_data = []
        self._fwdQ_selected = []
        self._selected_bbs = []
        self._update_fwdQ_tree_data()
        self._build_tab_content(lower_inner, 'fwdQ', self._update_fwdQ_msg,
            right_btns=[
                (self._getTabStr('delete'), self._delete_fwdQ),
            ])

    def _update_fwdQ_tree_data(self):
        self._get_fwdQ_data()
        self._format_fwdQ_tree_data()
        self._update_fwdQ_tree()

    def _get_fwdQ_data(self):
        self._fwdQ_data = self._bbs_obj.get_fwd_q_tab_bbs()

    def _get_fwdQ_MSG_data(self, bid):
        return self._bbs_obj.get_out_msg_fm_BID(bid)

    def _format_fwdQ_tree_data(self):
        self._fwdQ_tree_data = []
        for el in self._fwdQ_data:
            to_call = f"{el[4]}"
            if el[5]:
                to_call += f"@{el[5]}"
            from_call = f"{el[2]}"
            if el[3]:
                from_call += f"@{el[3]}"
            self._fwdQ_tree_data.append((
                f'{int(el[0]):06d}',  f'{el[1]}',  f'{el[8]}',  f'{from_call}',
                f'{to_call}', f'{el[6]}', f'{el[7]}',  f'{el[9]}',
                f'{el[10]}', f'{el[11]}', f'{el[12]}',
            ))

    def _update_fwdQ_tree(self):
        self._fill_tree(self._fwdQ_tree, self._fwdQ_tree_data,
                        lambda r: ('dummy', r[-1], r[1]),
                        'mid')

    def _fwdQ_entry_selected(self, event=None):
        self._fwdQ_selected = []
        self._selected_bbs = []
        bid = ''
        for item in self._fwdQ_tree.selection():
            vals = self._fwdQ_tree.item(item)['values']
            tags = self._fwdQ_tree.item(item)['tags']
            self._fwdQ_selected.append(tags[1])
            bbs_call = vals[5]
            if bbs_call not in self._selected_bbs:
                self._selected_bbs.append(bbs_call)
            bid = tags[2]
        if bid:
            self._fwdQ_show_msg_fm_BID(bid)

    def _update_fwdQ_msg(self, event=None):
        self._update_msg_by_encoding_bbs('F', self._fwdQ_text)

    def _fwdQ_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_fwdQ_MSG_data(bid)
        if db_data:
            self._display_msg(self._fwdQ_text, 'F', db_data,
                              var_prefix='fwdQ', bbs_style=True, show_header=True,
                              time_field='tx-time',
                              from_bbs_field='from_bbs_call',
                              fwd_bbs_field='fwd_bbs')

    def _delete_fwdQ(self):
        if not self._fwdQ_selected:
            return
        self._bbs_obj.del_fwd_q_by_FWD_ID(self._fwdQ_selected)
        for bbs_call in self._selected_bbs:
            self._bbs_obj.del_bbs_fwdQ(bbs_call)
        self._fwdQ_selected = []
        self._selected_bbs = []
        self._update_fwdQ_tree_data()

    # ================================================================
    # Hold Tab
    # ================================================================

    def _init_hold_tab(self, parent):
        top_f, lower_inner = self._build_vertical_split(parent)
        self._hold_tree = self._build_tree(top_f, [
            ('mid',     'MID',                            65,  False, 'w'),
            ('bid',     'BID',                            120, False, 'w'),
            ('Betreff', self._getTabStr('subject'),       230, True,  'w'),
            ('Von',     self._getTabStr('from'),          120, True,  'w'),
            ('An',      self._getTabStr('to'),            120, True,  'w'),
            ('typ',     'TYP',                            45,  False, 'w'),
            ('size',    'Size',                           80,  False, 'w'),
            ('flag',    'Flag',                           60,  False, 'w'),
        ], self._hold_entry_selected)
        self._hold_tree_data = []
        self._hold_data = []
        self._hold_selected = []
        self._update_hold_tree_data()
        self._build_tab_content(lower_inner, 'hold', self._update_hold_msg,
            left_btns=[('UNHOLD', self._unhold_btn)],
            right_btns=[
                (self._getTabStr('delete'), self._delete_hold_btn),
            ])

    def _update_hold_tree_data(self):
        self._get_hold_data()
        self._format_hold_tree_data()
        self._update_hold_tree()

    def _get_hold_data(self):
        self._hold_data = self._bbs_obj.get_hold_tab_bbs()

    def _get_hold_MSG_data(self, bid):
        return self._bbs_obj.get_hold_msg_fm_BID(bid)

    def _format_hold_tree_data(self):
        self._hold_tree_data = []
        for el in self._hold_data:
            to_call = f"{el[4]}"
            if el[5]:
                to_call += f"@{el[5]}"
            from_call = f"{el[2]}"
            if el[3]:
                from_call += f"@{el[3]}"
            self._hold_tree_data.append((
                f'{int(el[0]):06d}',  f'{el[1]}',  f'{el[7]}',  f'{from_call}',
                f'{to_call}', f'{el[6]}', f'{el[8]}',  f'{el[9]}',
            ))

    def _update_hold_tree(self):
        self._fill_tree(self._hold_tree, self._hold_tree_data,
                        lambda r: ('dummy', r[1]),
                        'mid')

    def _hold_entry_selected(self, event=None):
        self._hold_selected = []
        bid = ''
        for item in self._hold_tree.selection():
            bid = self._hold_tree.item(item)['tags'][1]
            self._hold_selected.append(bid)
        if bid:
            self._hold_show_msg_fm_BID(bid)

    def _update_hold_msg(self, event=None):
        self._update_msg_by_encoding_bbs('H', self._hold_text)

    def _hold_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_hold_MSG_data(bid)
        if db_data:
            self._display_msg(self._hold_text, 'H', db_data,
                              var_prefix='hold', bbs_style=True, show_header=True,
                              time_field='rx-time')

    def _delete_hold_btn(self):
        if not self._hold_selected:
            return
        self._bbs_obj.del_in_by_BID_list(self._hold_selected)
        self._hold_selected = []
        self._update_hold_tree_data()

    def _unhold_btn(self):
        if not self._hold_selected:
            return
        self._bbs_obj.unhold_msg_by_BID(self._hold_selected)
        self._hold_selected = []
        self._update_hold_tree_data()

    # ================================================================
    # Trash Tab
    # ================================================================

    def _init_trash_tab(self, parent):
        top_f, lower_inner = self._build_vertical_split(parent)
        self._trash_tree = self._build_tree(top_f, [
            ('mid',     'MID',                            65,  False, 'w'),
            ('Betreff', self._getTabStr('subject'),       230, True,  'w'),
            ('Von',     self._getTabStr('from'),          120, True,  'w'),
            ('An',      self._getTabStr('to'),            120, True,  'w'),
            ('typ',     'TYP',                            45,  False, 'w'),
            ('size',    'Size',                           80,  False, 'w'),
            ('tag',     'IN/OUT',                         60,  False, 'w'),
        ], self._trash_entry_selected)
        self._trash_tree_data = []
        self._trash_data = []
        self._trash_selected = []
        self._update_trash_tree_data()
        self._build_tab_content(lower_inner, 'trash', self._update_trash_msg,
            right_btns=[
                (self._getTabStr('delete'), self._delete_trash_btn),
            ])

    def _update_trash_tree_data(self):
        self._get_trash_data()
        self._format_trash_tree_data()
        self._update_trash_tree()

    def _get_trash_data(self):
        self._trash_data = self._bbs_obj.get_trash_tab_bbs()

    def _get_trash_MSG_data(self, mid, tag):
        return self._bbs_obj.get_trash_msg_fm_BID(mid, tag)

    def _format_trash_tree_data(self):
        self._trash_tree_data = []
        for i, data_set in enumerate(self._trash_data):
            tag = ('IN', 'OUT')[i]
            for el in data_set:
                to_call = f"{el[4]}"
                if el[5]:
                    to_call += f"@{el[5]}"
                from_call = f"{el[2]}"
                if el[3]:
                    from_call += f"@{el[3]}"
                self._trash_tree_data.append((
                    f'{el[0]}',  f'{el[7]}',  f'{from_call}',
                    f'{to_call}', f'{el[6]}', f'{el[8]}',  tag,
                ))

    def _update_trash_tree(self):
        self._fill_tree(self._trash_tree, self._trash_tree_data,
                        lambda r: ('dummy', r[0], r[-1]),
                        'mid')

    def _trash_entry_selected(self, event=None):
        self._trash_selected = []
        mid = ''
        tag = ''
        for item in self._trash_tree.selection():
            tags = self._trash_tree.item(item)['tags']
            mid = tags[1]
            tag = tags[2]
            self._trash_selected.append((mid, tag))
        if mid and tag:
            self._trash_show_msg_fm_BID(mid, tag)

    def _update_trash_msg(self, event=None):
        self._update_msg_by_encoding_bbs('T', self._trash_text)

    def _trash_show_msg_fm_BID(self, mid, tag):
        if not mid:
            return
        db_data = self._get_trash_MSG_data(mid, tag)
        if db_data:
            self._display_msg(self._trash_text, 'T', db_data,
                              var_prefix='trash', bbs_style=True, show_header=True,
                              time_field='rx-time')

    def _delete_trash_btn(self):
        tmp = {'IN': [], 'OUT': []}
        for mid, tag in self._trash_selected:
            tmp[tag].append(mid)
        self._bbs_obj.del_trash_in_by_BID(tmp.get('IN', []))
        self._bbs_obj.del_trash_out_by_BID(tmp.get('OUT', []))
        self._trash_selected = []
        self._update_trash_tree_data()
