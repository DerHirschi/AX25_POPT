import tkinter as tk
from tkinter import ttk

from fnc.gui_fnc import delete_tree
from gui.bbs_gui.bbs_MSGcenter_gui.guiBBS_MSG_c_base import MSG_Center_base


class MSG_Center_PMS(MSG_Center_base):
    def __init__(self, root_win):
        MSG_Center_base.__init__(self, root_win)
        self._tabControl.bind("<<NotebookTabChanged>>", self.on_bbsTab_select)

        tab_PN  = ttk.Frame(self._tabControl)
        tab_BL  = ttk.Frame(self._tabControl)
        tab_OUT = ttk.Frame(self._tabControl)
        tab_SV  = ttk.Frame(self._tabControl)
        self._tabControl.add(tab_PN,  text=self._getTabStr('private'))
        self._tabControl.add(tab_BL,  text='Bulletin')
        self._tabControl.add(tab_OUT, text=self._getTabStr('msgC_sendet_msg'))
        self._tabControl.add(tab_SV,  text=self._getTabStr('saved'))

        self._init_pn_tab(tab_PN)
        self._init_bl_tab(tab_BL)
        self._init_out_tab(tab_OUT)
        self._init_sv_tab(tab_SV)

        self._text_tab = {
            0: self._pn_text,
            1: self._bl_text,
            2: self._out_text,
            3: self._sv_text,
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
            3: self._selected_msg['S'].get('enc', 'UTF-8'),
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
            3: self._update_SV_tree_data,
        }.get(ind, lambda: None)()

    # ================================================================
    # PN Tab
    # ================================================================

    def _init_pn_tab(self, parent):
        top_f, lower_inner = self._build_vertical_split(parent)
        self._pn_tree = self._build_tree(top_f, [
            ('Neu',    self._getTabStr('new'),       40,  False, 'center'),
            ('Betreff', self._getTabStr('subject'),  190, True,  'w'),
            ('Von',    self._getTabStr('from'),      130, True,  'w'),
            ('An',     self._getTabStr('to'),        130, True,  'w'),
            ('Datum',  self._getTabStr('date_time'), 220, False, 'w'),
        ], self._PN_entry_selected)
        self._pn_tree_data = []
        self._pn_data = []
        self._configure_tree_tags(self._pn_tree)
        self._update_PN_tree_data()
        self._build_tab_content(lower_inner, 'pn', self._update_PN_msg,
            left_btns=[(self._getTabStr('new'), self._open_newMSG_win)],
            right_btns=[
                (self._getTabStr('delete'),  self._delete_PN_btn),
                (self._getTabStr('save'),    None),
                (self._getTabStr('forward'), lambda: self._open_newMSG_win_forward('P')),
                (self._getTabStr('answer'),  lambda: self._open_newMSG_win_reply('P')),
            ],
            show_rx_time=True)

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
                date = '20' + date
            self._pn_tree_data.append((
                f'{new}', f'{el[5]}', f'{from_call}', f'{to_call}',
                f'{date}', f'{el[0]}',
            ))

    def _update_PN_tree(self):
        self._fill_tree(self._pn_tree, self._pn_tree_data,
                        lambda r: ('neu' if r[0] else 'alt', r[-1]),
                        'Datum')

    def _PN_entry_selected(self, event=None):
        self._PN_selected = []
        bid = ''
        for item in self._pn_tree.selection():
            tag_name, bid = self._pn_tree.item(item)['tags']
            self._PN_selected.append(bid)
            if tag_name == 'neu':
                self._pn_tree.item(item, tags=('alt', bid))
                v = list(self._pn_tree.item(item)['values'])
                v[0] = ''
                self._pn_tree.item(item, values=v)
        if bid:
            self._PN_show_msg_fm_BID(bid)

    def _update_PN_msg(self, event=None):
        self._update_msg_by_encoding('P', self._pn_text)

    def _PN_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_PN_MSG_data(bid)
        self._set_PN_MSG_notNew(bid)
        if db_data:
            self._display_msg(self._pn_text, 'P', db_data,
                              var_prefix='pn', bbs_style=False,
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
            ('Neu',    self._getTabStr('new'),       40,  False, 'center'),
            ('Betreff', self._getTabStr('subject'),  270, True,  'w'),
            ('Von',    self._getTabStr('from'),      180, True,  'w'),
            ('An',     self._getTabStr('to'),        100, True,  'w'),
            ('vert',   '@',                          50,  False, 'w'),
            ('flag',   'Flag',                       60,  False, 'w'),
            ('Datum',  self._getTabStr('date_time'), 220, False, 'w'),
        ], self._BL_entry_selected)
        self._bl_tree_data = []
        self._bl_data = []
        self._configure_tree_tags(self._bl_tree)
        self._update_BL_tree_data()

        self._build_tab_content(lower_inner, 'bl', self._update_BL_msg,
            left_btns=[(self._getTabStr('new'), self._open_newMSG_win)],
            right_btns=[
                (self._getTabStr('delete'),  self._delete_BL_btn),
                (self._getTabStr('save'),    None),
                (self._getTabStr('forward'), lambda: self._open_newMSG_win_forward('B')),
                (self._getTabStr('answer'),  lambda: self._open_newMSG_win_reply('B')),
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
                date = '20' + date
            if not self._bl_cat_filter or self._bl_cat_filter == el[4]:
                self._bl_tree_data.append((
                    f'{new}', f'{el[6]}', f'{from_call}', f'{el[4]}',
                    f'{el[5]}', f'{el[9]}', f'{date}', f'{el[1]}',
                ))
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
        self._fill_tree(self._bl_tree, self._bl_tree_data,
                        lambda r: ('neu' if r[0] else 'alt', r[-1]),
                        'Datum')

    def _BL_entry_selected(self, event=None):
        self._BL_selected = []
        bid = ''
        for item in self._bl_tree.selection():
            tag_name, bid = self._bl_tree.item(item)['tags']
            self._BL_selected.append(bid)
            if tag_name == 'neu':
                self._bl_tree.item(item, tags=('alt', bid))
                v = list(self._bl_tree.item(item)['values'])
                v[0] = ''
                self._bl_tree.item(item, values=v)
        if bid:
            self._BL_show_msg_fm_BID(bid)

    def _update_BL_msg(self, event=None):
        self._update_msg_by_encoding('B', self._bl_text)

    def _BL_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_BL_MSG_data(bid)
        self._set_BL_MSG_notNew(bid)
        if db_data:
            self._display_msg(self._bl_text, 'B', db_data,
                              var_prefix='bl', bbs_style=False,
                              time_field='time', rx_time_field='rx-time',
                              time_suffix=' (utc)')

    def _get_BL_MSG_data(self, bid):
        return self._bbs_obj.get_bl_msg_fm_BID(bid)

    def _set_BL_MSG_notNew(self, bid: str):
        self._bbs_obj.set_in_msg_notNew(bid)

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
        self._configure_tree_tags(self._out_tree)
        self._update_OUT_tree_data()
        self._build_tab_content(lower_inner, 'out', self._update_OUT_msg,
            right_btns=[
                (self._getTabStr('delete'),  self._delete_OUT_btn),
                (self._getTabStr('save'),    self._save_outMSG),
                (self._getTabStr('forward'), lambda: self._open_newMSG_win_forward('O')),
            ])

    def _update_OUT_tree(self):
        self._fill_tree(self._out_tree, self._out_tree_data,
                        lambda r: ('neu' if not r[0] else 'alt', r[-1]),
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
        self._update_msg_by_encoding('O', self._out_text)

    def _OUT_show_msg_fm_BID(self, bid):
        if not bid:
            return
        db_data = self._get_OUT_MSG_data(bid)
        if db_data:
            self._display_msg(self._out_text, 'O', db_data,
                              var_prefix='out', bbs_style=False,
                              time_field='tx-time',
                              from_bbs_field='from_bbs_call',
                              fwd_bbs_field='fwd_bbs')

    # ================================================================
    # SV Tab
    # ================================================================

    def _init_sv_tab(self, parent):
        top_f, lower_inner = self._build_vertical_split(parent)
        self._sv_tree = self._build_tree(top_f, [
            ('Typ',     'Typ',                            50,  False, 'w'),
            ('Betreff', self._getTabStr('subject'),       190, True,  'w'),
            ('Von',     self._getTabStr('from'),          190, True,  'w'),
            ('An',      self._getTabStr('to'),            190, True,  'w'),
            ('Datum',   self._getTabStr('date_time'),     220, False, 'w'),
        ], self._SV_entry_selected)
        self._sv_tree_data = []
        self._sv_data = []
        self._sv_selected = []
        self._update_SV_tree_data()
        self._build_tab_content(lower_inner, 'sv', self._update_SV_msg,
            left_btns=[(self._getTabStr('new'), self._open_newMSG_win)],
            right_btns=[
                (self._getTabStr('delete'), self._delete_SV_btn),
                (self._getTabStr('edit'),   lambda: self._open_newMSG_win_reply('S')),
            ])

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
                f'{el[7]}', f'{el[5]}', f'{from_call}', f'{to_call}',
                f'{el[6]}', f'{el[0]}',
            ))

    def _update_SV_tree(self):
        self._fill_tree(self._sv_tree, self._sv_tree_data,
                        lambda r: ('dummy', r[-1]),
                        'Datum')

    def _SV_entry_selected(self, event=None):
        self._sv_selected = []
        mid = ''
        for item in self._sv_tree.selection():
            mid = self._sv_tree.item(item)['tags'][1]
            self._sv_selected.append(mid)
        if mid:
            self._SV_show_msg_fm_MID(mid)

    def _update_SV_msg(self, event=None):
        self._update_msg_by_encoding('S', self._sv_text)

    def _SV_show_msg_fm_MID(self, mid):
        if not mid:
            return
        db_data = self._get_SV_MSG_data(mid)
        if db_data:
            self._display_msg(self._sv_text, 'S', db_data,
                              var_prefix='sv', bbs_style=False,
                              time_field='time', label='MID')

    def _delete_SV_btn(self):
        for mid in self._sv_selected:
            self._bbs_obj.del_sv_by_MID(mid)
        self._sv_selected = []
        self._update_SV_tree_data()
