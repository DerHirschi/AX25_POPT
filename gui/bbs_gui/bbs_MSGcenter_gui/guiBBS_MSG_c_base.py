import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import FONT
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.bbs_gui.guiBBS_newMSG import BBS_newMSG
from gui.guiMsgBoxes import save_file_dialog


class MSG_Center_base(tk.Frame):
    def __init__(self, root_win):
        tk.Frame.__init__(self, root_win)
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
        }
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
        #
        self._pn_text       = None
        self._bl_text       = None
        self._out_text      = None
        self._sv_text       = None
        self._hold_text     = None

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
        pass

    def _update_SV_tree_data(self):
        pass

    def _update_hold_tree_data(self):
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
        }.get(ind, None)
        if text is None:
            return
        if text.tag_ranges("sel"):
            self.clipboard_clear()
            self.clipboard_append(text.selection_get())
            text.tag_remove(tk.SEL, "1.0", tk.END)

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
        if msg_text is None:
            return
        data = msg_text.get('1.0', tk.END)
        save_file_dialog(data)

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

    def _delete_BL(self, bid: str):
        if bid:
            return self._bbs_obj.del_in_by_BID(bid)

    def _delete_OUT(self, bid: str):
        if bid:
            return self._bbs_obj.del_out_by_BID(bid)

    def _delete_SV(self, bid: str):
        if bid:
            return self._bbs_obj.del_sv_by_MID(bid)

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
        self._bl_text.configure(font=(FONT, self.text_size))
        self._pn_text.configure(font=(FONT, self.text_size))
        self._out_text.configure(font=(FONT, self.text_size))
        self._sv_text.configure(font=(FONT, self.text_size))

    def decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self._bl_text.configure(font=(FONT, self.text_size))
        self._pn_text.configure(font=(FONT, self.text_size))
        self._out_text.configure(font=(FONT, self.text_size))
        self._sv_text.configure(font=(FONT, self.text_size))

    def update_textsize_trees(self):
        self._bl_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._pn_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._pn_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
        self._bl_cat_tree.tag_configure('neu', font=(None, self._text_size_tabs, 'bold'))
        self._bl_cat_tree.tag_configure('alt', font=(None, self._text_size_tabs, ''))
