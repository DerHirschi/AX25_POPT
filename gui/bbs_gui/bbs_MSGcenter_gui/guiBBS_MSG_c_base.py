import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import FONT, COLOR_MAP
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.bbs_gui.guiBBS_newMSG import BBS_newMSG
from gui.guiMsgBoxes import save_file_dialog
from gui.guiRightClick_Menu import ContextMenu


class MSG_Center_base(ttk.Frame):
    def __init__(self, root_win):
        ttk.Frame.__init__(self, root_win)
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.style              = root_win.style
        self._root_win          = root_win
        self._bbs_obj           = PORT_HANDLER.get_bbs()
        self.newPMS_MSG_win     = self._root_win.newPMS_MSG_win
        self.text_size          = root_win.text_size
        self._text_size_tabs    = 10
        self._sort_rev          = False
        self._last_sort_col     = {}
        self._selected_msg      = {
            'P': {},
            'B': {},
            'O': {},
            'S': {},
            'F': {},
            'H': {},
            'T': {},
        }
        ###################################
        self.style_name    = self._root_win.style_name
        self._get_colorMap = lambda: COLOR_MAP.get(self.style_name, ('black', '#d9d9d9'))
        ###################################
        # Vars
        self._var_encoding = tk.StringVar(self, 'UTF-8')
        ###################################
        # Tabctl
        self._tabControl = ttk.Notebook(
            self,
        )
        self._tabControl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        ###################################
        #
        self._pn_tree       = None
        self._bl_tree       = None
        self._bl_cat_tree   = None
        self._out_tree      = None
        self._sv_tree       = None
        self._hold_tree     = None
        self._trash_tree    = None
        #
        self._pn_text       = None
        self._bl_text       = None
        self._out_text      = None
        self._sv_text       = None
        self._fwdQ_text     = None
        self._hold_text     = None
        self._trash_text    = None
        #
        self._BL_selected  = []
        self._PN_selected  = []
        self._OUT_selected = []
        #
        self._text_tab = {}

    def _init_RClick_menu(self):
        # PN
        if self._pn_text:
            pn_txt_men = ContextMenu(self._pn_text)
            pn_txt_men.add_item(self._getTabStr('copy'), self.copy_select)
            pn_txt_men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)
        # BL
        if self._bl_text:
            bl_txt_men = ContextMenu(self._bl_text)
            bl_txt_men.add_item(self._getTabStr('copy'), self.copy_select)
            bl_txt_men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)
        # OUT
        if self._out_text:
            out_txt_men = ContextMenu(self._out_text)
            out_txt_men.add_item(self._getTabStr('copy'), self.copy_select)
            out_txt_men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)
        # sv
        if self._sv_text:
            sv_txt_men = ContextMenu(self._sv_text)
            sv_txt_men.add_item(self._getTabStr('copy'), self.copy_select)
            sv_txt_men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)
        # fwdQ
        if self._fwdQ_text:
            fwdQ_txt_men = ContextMenu(self._fwdQ_text)
            fwdQ_txt_men.add_item(self._getTabStr('copy'), self.copy_select)
            fwdQ_txt_men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)
        # Hold
        if self._hold_text:
            hold_txt_men = ContextMenu(self._hold_text)
            hold_txt_men.add_item(self._getTabStr('copy'), self.copy_select)
            hold_txt_men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)
        # Trash
        if self._trash_text:
            trash_txt_men = ContextMenu(self._trash_text)
            trash_txt_men.add_item(self._getTabStr('copy'), self.copy_select)
            trash_txt_men.add_item(self._getTabStr('save_to_file'), self._save_msg_to_file)


    def _sort_entry(self, col, tree):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=self._sort_rev)
        self._sort_rev = not self._sort_rev
        self._last_sort_col[tree] = col
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

    def _update_sort_entry(self, tree, col='Datum'):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        col = self._last_sort_col.get(tree, col)
        tmp = [(tree.set(k, col), k) for k in tree.get_children('')]
        tmp.sort(reverse=not self._sort_rev)
        for index, (val, k) in enumerate(tmp):
            tree.move(k, '', int(index))

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
                msg['flag']         = 'E'
                msg['typ']          = 'P'
                msg['to_call']      = ''
                msg['to_bbs']       = ''
                msg['subject'] = ('Fwd: ' + msg['subject'])
                self.newPMS_MSG_win = BBS_newMSG(self, msg)

    def _open_newMSG_win(self):
        if self.newPMS_MSG_win:
            return
        self.newPMS_MSG_win = BBS_newMSG(self)

    def _do_pms_autoFWD(self):
        self._bbs_obj.start_man_autoFwd()

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
            """
            'gesendet',
            'Betreff',
            'Von',
            'An',
            #'fwd_bbs',
            'typ',
            'flag',
            'Datum',
            """
            self._out_tree_data.append((
                f'{fwd_done}',
                f'{el[5]}',
                f'{from_call}',
                f'{to_call}',
                # f'{el[5]}',
                f'{el[7]}',
                f'{el[8]}',
                f'{tx_time}',
                f'{el[0]}',  # BID
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

    def _set_all_to_oldMSG(self):   # Set all Msg to read Status
        # TODO
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
            # print(mid)
            self._bbs_obj.get_db().pms_save_outMsg_by_MID(mid)

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
            # FIXME Codec : UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1090-1097: ordinal not in range(256)
            save_file_dialog(data, self._root_win)


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
                tag_name, bid = item['tags']
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

    def _delete_PN(self, bid: str):
        if bid:
            return self._bbs_obj.del_in_by_BID(bid)
        return False

    def _delete_PN_btn(self):
        # for bid in self._hold_selected:
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
        # for bid in self._hold_selected:
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
        # for bid in self._hold_selected:
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

    def _PN_show_msg_fm_BID(self, mid):
        pass

    def _BL_show_msg_fm_BID(self, mid):
        pass

    def _OUT_show_msg_fm_BID(self, mid):
        pass

    def _SV_show_msg_fm_MID(self, mid):
        pass

    ############################################
    # GUI
    def increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        if hasattr(self._bl_text, 'configure'):
            self._bl_text.configure(font=(FONT, self.text_size))
        if hasattr(self._pn_text, 'configure'):
            self._pn_text.configure(font=(FONT, self.text_size))
        if hasattr(self._out_text, 'configure'):
            self._out_text.configure(font=(FONT, self.text_size))
        if hasattr(self._sv_text, 'configure'):
            self._sv_text.configure(font=(FONT, self.text_size))
        if hasattr(self._fwdQ_text, 'configure'):
            self._fwdQ_text.configure(font=(FONT, self.text_size))
        if hasattr(self._hold_text, 'configure'):
            self._hold_text.configure(font=(FONT, self.text_size))
        if hasattr(self._trash_text, 'configure'):
            self._trash_text.configure(font=(FONT, self.text_size))

    def decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        if hasattr(self._bl_text, 'configure'):
            self._bl_text.configure(font=(FONT, self.text_size))
        if hasattr(self._pn_text, 'configure'):
            self._pn_text.configure(font=(FONT, self.text_size))
        if hasattr(self._out_text, 'configure'):
            self._out_text.configure(font=(FONT, self.text_size))
        if hasattr(self._sv_text, 'configure'):
            self._sv_text.configure(font=(FONT, self.text_size))
        if hasattr(self._fwdQ_text, 'configure'):
            self._fwdQ_text.configure(font=(FONT, self.text_size))
        if hasattr(self._hold_text, 'configure'):
            self._hold_text.configure(font=(FONT, self.text_size))
        if hasattr(self._trash_text, 'configure'):
            self._trash_text.configure(font=(FONT, self.text_size))

    def update_textsize_trees(self):
        self._bl_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._pn_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._bl_cat_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_cat_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
    #################################