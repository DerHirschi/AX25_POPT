import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from UserDB.UserDBmain import USER_DB
from ax25.ax25InitPorts import PORT_HANDLER
from bbs.bbs_constant import GET_MSG_STRUC
from cfg.logger_config import logger, BBS_LOG
from cfg.popt_config import POPT_CFG
from cfg.constant import FONT, ENCODINGS, DEV_PRMAIL_ADD, COLOR_MAP, F_KEY_TAB_LINUX, F_KEY_TAB_WIN
from cli.StringVARS import replace_StringVARS
from fnc.gui_fnc import get_typed, detect_pressed
from fnc.os_fnc import is_linux
from fnc.str_fnc import format_number, zeilenumbruch, zeilenumbruch_lines, get_strTab
from gui.guiMsgBoxes import open_file_dialog, save_file_dialog, WarningMsg
from gui.guiRightClick_Menu import ContextMenu


class BBS_newMSG(tk.Toplevel):
    def __init__(self, root_win, reply_msg=None):
        tk.Toplevel.__init__(self, )
        if reply_msg is None:
            reply_msg   = {}
        self._root_win  = root_win
        self._bbs_obj   = PORT_HANDLER.get_bbs()
        self.text_size  = int(POPT_CFG.load_guiPARM_main().get('guiMsgC_parm_text_size', self._root_win.text_size))
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        self.title(self._getTabStr('new_pr_mail'))
        self.style = self._root_win.style
        style_name = self._root_win.style_name
        self._get_colorMap = lambda: COLOR_MAP.get(style_name, ('black', '#d9d9d9'))
        if hasattr(self._root_win, 'main_win'):
            win = self._root_win.main_win
        else:
            win = self._root_win
        self.geometry(f"1150x"
                      f"700+"
                      f"{win.winfo_x()}+"
                      f"{win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        # self.attributes("-topmost", True)
        # self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ###################################
        ####################
        self._init_Menu()
        ####################
        # VARS
        self._reply_msg         = reply_msg
        self._mid               = 0
        self._msg_data          = {}
        self._msg_typ_var       = tk.StringVar(self, 'P')
        self._home_bbs_var      = tk.StringVar(self)
        self._from_call_var     = tk.StringVar(self)
        self._to_call_var       = tk.StringVar(self)
        self._to_cc_call_var    = tk.StringVar(self)
        self._subject_var       = tk.StringVar(self)
        self._var_encoding      = tk.StringVar(self, 'UTF-8')
        self._var_msg_size      = tk.StringVar(self, ' Size: 0 Bytes')

        prmail_list = USER_DB.get_all_PRmail()
        if DEV_PRMAIL_ADD not in prmail_list:
            prmail_list.append(DEV_PRMAIL_ADD)
        self._chiefs = prmail_list

        ####################
        # Frames
        frame_btn_oben  = ttk.Frame(self, height=30)
        frame_oben      = ttk.Frame(self, height=200)
        frame_unten     = ttk.Frame(self)
        footer_frame    = ttk.Frame(self, height=20)

        frame_btn_oben.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        frame_oben.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        frame_unten.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        #####################
        # Upper BTN Frame
        self._init_upper_btn_frame(frame_btn_oben)
        #####################
        # Header Frame
        self._init_header_frame(frame_oben)
        #####################
        # Text Frame
        self._text = None
        self._init_txt_frame(frame_unten)
        #####################
        # Footer Frame
        self._init_footer_frame(footer_frame)
        #####################
        # Init Header from reply MSG
        self._root_win.newPMS_MSG_win = self
        if self._reply_msg:
            self._init_data_f_reply()
        self.bind('<Key>',           self._update_msg_size)
        self.bind('<Control-c>',     lambda event: self._copy_select())
        # self.bind('<Control-v>',     lambda event: self._clipboard_past())
        self.bind('<Control-x>',     lambda event: self._cut_select())
        self.bind('<Control-plus>',  lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())
        #####################
        # F-TEXT
        if is_linux():
            r = 13
        else:
            r = 11
        for fi in range(1, r):
            self.bind(f'<Shift-F{fi}>', self._insert_ftext)
        #####################
        self._init_RClick_menu()

    def _init_RClick_menu(self):
        if self._text:
            txt_men = ContextMenu(self._text)
            txt_men.add_item(self._getTabStr('cut'),  self._cut_select)
            txt_men.add_separator()
            txt_men.add_item(self._getTabStr('copy'), self._copy_select)
            txt_men.add_item(self._getTabStr('past'), self._clipboard_past)
            txt_men.add_separator()
            actions_submenu = txt_men.add_submenu("F-Text")
            actions_submenu.add_command(label="F1", command=lambda: self._insert_ftext_fm_menu(1))
            actions_submenu.add_command(label="F2", command=lambda: self._insert_ftext_fm_menu(2))
            actions_submenu.add_command(label="F3", command=lambda: self._insert_ftext_fm_menu(3))
            actions_submenu.add_command(label="F4", command=lambda: self._insert_ftext_fm_menu(4))
            actions_submenu.add_command(label="F5", command=lambda: self._insert_ftext_fm_menu(5))
            actions_submenu.add_command(label="F6", command=lambda: self._insert_ftext_fm_menu(6))
            actions_submenu.add_command(label="F7", command=lambda: self._insert_ftext_fm_menu(7))
            actions_submenu.add_command(label="F8", command=lambda: self._insert_ftext_fm_menu(8))
            actions_submenu.add_command(label="F9", command=lambda: self._insert_ftext_fm_menu(9))
            actions_submenu.add_command(label="F10", command=lambda: self._insert_ftext_fm_menu(10))
            actions_submenu.add_command(label="F11", command=lambda: self._insert_ftext_fm_menu(11))
            actions_submenu.add_command(label="F12", command=lambda: self._insert_ftext_fm_menu(12))

            txt_men.add_separator()
            txt_men.add_item(self._getTabStr('past_f_file'), self._insert_fm_file)

    def _on_key_release_inp_txt(self, event=None):
        ind2 = str(int(float(self._text.index(tk.INSERT)))) + '.0'
        text = zeilenumbruch(self._text.get(ind2,  self._text.index(tk.INSERT)))
        self._text.delete(ind2,  self._text.index(tk.INSERT))
        self._text.insert(tk.INSERT, text)

    def _init_Menu(self):
        menubar = tk.Menu(self, tearoff=False)
        self.config(menu=menubar)
        # ### Mail
        MenuVerb = tk.Menu(menubar, tearoff=False)
        MenuVerb.add_command(
            label=self._getTabStr('send'),
            command=self._btn_send_msg,
        )
        menubar.add_cascade(label='Mail', menu=MenuVerb, underline=0)
        # ### Bearbeiten
        MenuEdit = tk.Menu(menubar, tearoff=False)
        MenuEdit.add_command(label=self._getTabStr('past_f_file'),
                              command=self._insert_fm_file,
                              underline=0)
        MenuEdit.add_command(label=self._getTabStr('save_to_file'),
                              command=self._save_to_file,
                              underline=0)
        menubar.add_cascade(label=self._getTabStr('edit'), menu=MenuEdit, underline=0)

    def _init_upper_btn_frame(self, root_frame):
        ttk.Button(root_frame,
                  text=self._getTabStr('send'),
                  command=self._btn_send_msg
                  ).pack(side=tk.LEFT, expand=False)
        ttk.Button(root_frame,
                  text=self._getTabStr('save_draft'),
                  command=self._btn_save_msg
                  ).pack(side=tk.LEFT, expand=False, padx=10)
        ttk.Button(root_frame,
                  text=self._getTabStr('discard'),
                  command=self._btn_delete_all
                  ).pack(side=tk.RIGHT, expand=False, anchor='e')

    def _init_header_frame(self, root_frame):
        from_frame  = ttk.Frame(root_frame)
        to_frame    = ttk.Frame(root_frame)
        subj_frame  = ttk.Frame(root_frame)
        from_frame.pack(side=tk.TOP, expand=True, anchor='w', padx=10, pady=10)
        to_frame.pack(side=tk.TOP,   expand=True, anchor='w', padx=10, pady=5, fill=tk.X)
        subj_frame.pack(side=tk.TOP, expand=True, anchor='w', padx=10, pady=5)

        ttk.Label(from_frame, text=f"{self._getTabStr('from')}: ").pack(side=tk.LEFT, expand=False)

        stat_cfg = POPT_CFG.get_stat_CFGs_by_typ('USER')
        opt      = list(stat_cfg.keys())
        if opt:
            self._from_call_var.set(opt[0])
            opt = [opt[0]] + opt
        else:
            opt = ['', '']
        ttk.OptionMenu(from_frame,
                 self._from_call_var,
                 *opt
                 ).pack(side=tk.LEFT, fill=tk.X, expand=False, padx=25)

        typ_frame = ttk.Frame(from_frame)
        typ_frame.pack(side=tk.LEFT, expand=True, padx=130)
        ttk.Label(typ_frame, text='Typ: ').pack(side=tk.LEFT, expand=False, )
        opt = [self._msg_typ_var.get()] + ['P', 'B']
        ttk.OptionMenu(typ_frame,
                      self._msg_typ_var,
                      *opt, ).pack(side=tk.LEFT, expand=False, )


        ttk.Label(from_frame, text='FWD-BBS: ').pack(side=tk.LEFT, expand=False, padx=25)
        opt = ['AUTO', 'AUTO'] + self._bbs_obj.get_pms_cfg().get('home_bbs', [])
        if opt:
            self._home_bbs_var.set(opt[0])
        ttk.OptionMenu(from_frame,
                      self._home_bbs_var,
                      *opt, ).pack(side=tk.LEFT, expand=False)


        ttk.Label(to_frame, text=f"{self._getTabStr('to')}: ").pack(side=tk.LEFT, expand=False)
        self._to_call_ent = ttk.Entry(to_frame,
                                     textvariable=self._to_call_var,
                                     # highlightcolor='blue',
                                     # fg='white',
                                     # bg='black',
                                     width=40)
        self._to_call_ent.pack(side=tk.LEFT, expand=False, padx=35)
        self._to_call_ent.bind('<KeyRelease>',
                               lambda event: get_typed(event, self._chiefs, self._to_call_var, self._to_call_ent))
        self._to_call_ent.bind('<Key>', lambda event: detect_pressed(event, self._to_call_ent))
        ttk.Label(to_frame, text='CC: ').pack(side=tk.LEFT, expand=False, padx=20)
        self._cc_entry = ttk.Entry(to_frame,
                                  textvariable=self._to_cc_call_var,
                                  width=40)
        self._cc_entry.pack(side=tk.LEFT, expand=False)
        self._cc_entry.bind('<KeyRelease>',
                            lambda event: get_typed(event, self._chiefs, self._to_cc_call_var, self._cc_entry))
        self._cc_entry.bind('<Key>', lambda event: detect_pressed(event, self._cc_entry))

        ttk.Label(subj_frame, text=f"{self._getTabStr('subject')}: ").pack(side=tk.LEFT, expand=False)
        ttk.Entry(subj_frame,
                 textvariable=self._subject_var,
                 width=91).pack(side=tk.LEFT, expand=False)

    def _init_txt_frame(self, root_frame):
        frame = ttk.Frame(root_frame)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._text = tk.Text(frame,
                           font=(FONT, self.text_size),
                           bd=0,
                           height=3,
                           borderwidth=0,
                           background='black',
                           foreground='white',
                           insertbackground='white',
                             relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                             highlightthickness=0,
                           # state="disabled",
                           )
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=self._text.yview
        )
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self._text.config(yscrollcommand=scrollbar.set)
        self._text.bind("<KeyRelease>", self._on_key_release_inp_txt)

    def _init_footer_frame(self, root_frame):
        footer_frame = ttk.Frame(root_frame, height=15)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            footer_frame,
            self._var_encoding,
            *opt,
            # command=self._update_PN_msg
        )
        fg, bg = self._get_colorMap()
        txt_encoding_ent.configure(
            font=(None, 6),
            border=0,
            borderwidth=0,
            height=1,
            fg=fg,
            bg=bg,
            relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
            highlightthickness=0,
        )
        txt_encoding_ent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        ttk.Label(footer_frame,
                 textvariable=self._var_msg_size,
                 font=(None, 7),
                 ).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    def _increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        self._text.configure(font=(FONT, self.text_size))

    def _decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self._text.configure(font=(FONT, self.text_size))

    def _init_data_f_reply(self):
        if self._reply_msg.get('flag', '') == 'E':
            self._data_for_draft_msg()
        else:
            self._data_for_reply_msg()

    def _data_for_reply_msg(self):
        if self._reply_msg.get('typ', 'P') == 'B':
            to_add = self._reply_msg['to_call']
            to_bbs = self._reply_msg['to_bbs']
            if to_bbs:
                to_add = to_add + '@' + to_bbs
        else:
            to_add = self._reply_msg['from_call']
            to_bbs = self._reply_msg['from_bbs']
            if to_bbs:
                to_add = to_add + '@' + to_bbs
            user_call = self._bbs_obj.get_pms_cfg().get('user', '')
            if self._reply_msg['to_call'] == user_call:
                self._from_call_var.set(self._reply_msg['to_call'])

        rep_msg = self._reply_msg.get('msg', b'').decode(self._var_encoding.get(), 'ignore')
        # subject = 'RE: ' + self._reply_msg['subject']
        rep_msg = '> ' + rep_msg.replace('\r', '\n> ') + '\n'
        rep_msg = f"{self._reply_msg['time']} fm {self._reply_msg['from_call']}:\n\n" + rep_msg
        self._msg_typ_var.set(self._reply_msg['typ'])
        self._to_call_var.set(to_add)
        self._subject_var.set(self._reply_msg.get('subject', 'Re: '))
        self._var_encoding.set(self._reply_msg.get('enc', 'UTF-8'))
        self._text.insert('1.0', rep_msg)
        self._text.focus_set()

    def _data_for_draft_msg(self):
        to_add = self._reply_msg['to_call']
        to_bbs = self._reply_msg['to_bbs']
        if to_bbs:
            to_add = to_add + '@' + to_bbs
        user_call = self._bbs_obj.get_pms_cfg().get('user', '')
        if self._reply_msg['from_call'] == user_call:
            self._from_call_var.set(self._reply_msg['from_call'])
        rep_msg = self._reply_msg.get('msg', b'').decode(self._var_encoding.get(), 'ignore')
        rep_msg = rep_msg.replace('\r', '\n')
        self._msg_typ_var.set(self._reply_msg['typ'])
        self._to_call_var.set(to_add)
        self._subject_var.set(self._reply_msg['subject'])
        self._var_encoding.set(self._reply_msg.get('enc', 'UTF-8'))
        self._text.insert('1.0', rep_msg)
        self._text.focus_set()

    def _btn_send_msg(self, event=None):
        if not self._save_msg():
            return
        if self._send_msg():
            self._send_msg_cc()
            self._close()

    def _btn_save_msg(self, event=None):
        # self.lower()
        if self._save_msg():
            messagebox.showinfo(title=self._getTabStr('save_draft_hint1'), message=self._getTabStr('save_draft_hint2'), parent=self)
        else:
            messagebox.showerror(title=self._getTabStr('not_save_draft_hint1'),
                                 message=self._getTabStr('not_save_draft_hint2'), parent=self)
        # self.lift()

    def _btn_delete_all(self, event=None):
        # self.lower()
        if messagebox.askokcancel(title=self._getTabStr('del_message_hint1'), message=self._getTabStr('del_message_hint2'), parent=self):
            self._text.delete('1.0', tk.END)
            self._subject_var.set('')
            self._to_cc_call_var.set('')
            self._to_call_var.set('')
        # self.lift()

    def _save_msg(self):
        sender = self._from_call_var.get().upper()
        if not sender:
            logger.error("PMS-newMSG: sender")
            return False
        regio_add = self._bbs_obj.get_pms_cfg().get('regio', '').upper()
        bbs_call  = self._bbs_obj.get_pms_cfg().get('user', '').upper()
        if any((not regio_add, not bbs_call)):
            logger.error(f"PMS-newMSG: regio_add/bbs_call: {regio_add}/{bbs_call}")
            return False
        recv_call = self._to_call_var.get().upper()
        if not recv_call:
            logger.error("PMS-newMSG: recv_call")
            return False
        tmp = recv_call.split('@')
        if len(tmp) == 1:
            recv_call, recv_bbs = tmp[0], ''
        elif len(tmp) == 2:
            recv_call, recv_bbs = tmp[0], tmp[1]
        else:
            logger.error("PMS-newMSG: len(recv_bbs)")
            return False

        typ = self._msg_typ_var.get()
        if typ not in ['P', 'B']:
            logger.error("PMS-newMSG: typ")
            return False
        subj = self._subject_var.get()
        if not subj:
            logger.error("PMS-newMSG: subj")
            return False
        if typ == 'P':
            if not recv_bbs:
                pr_mail_add = USER_DB.get_PRmail(sender)
                bbs_add = pr_mail_add.split('@')[-1]
                if '.' in bbs_add:
                    recv_bbs = bbs_add
            if not '.' in recv_bbs:
                #print('No----')
                #print(f'No: {recv_bbs}')
                recv_bbs = USER_DB.get_PRmail(recv_bbs)
                #print(f'No: {recv_bbs}')


        cc_add      = self._to_cc_call_var.get()
        enc         = self._var_encoding.get()
        msg_text    = str(self._text.get('1.0', tk.END)[:-1])
        msg_text    = zeilenumbruch_lines(msg_text)
        msg_text    = msg_text.replace('\n', '\r')
        msg_text    = msg_text.encode(enc, 'ignore')

        sender_bbs = bbs_call + '.' + regio_add
        self._msg_data = GET_MSG_STRUC()
        self._msg_data.update({
            'sender':        sender,
            'sender_bbs':    sender_bbs,
            'receiver':      recv_call.upper(),
            'recipient_bbs': recv_bbs.upper(),
            'subject':       subj,
            'msg':           msg_text,
            'message_type':  typ,
            'cc_add':        cc_add,
        })
        # Entwurf Nachrichten
        if self._reply_msg.get('mid', ''):
            self._mid = self._reply_msg.get('mid')
            self._msg_data['mid'] = self._reply_msg.get('mid')
            return self._bbs_obj.update_msg(self._msg_data)
        # Neue Nachrichten
        self._mid = self._bbs_obj.new_msg(self._msg_data)
        if not self._mid:
            BBS_LOG.error("PMS-newMSG: _mid")
            return False
        return True

    def _send_msg_cc(self):
        if not self._msg_data.get('cc_add', ''):
            return False
        tmp = self._msg_data.get('cc_add').split('@')
        if len(tmp) == 1:
            recv_call, recv_bbs = tmp[0], ''
        elif len(tmp) == 2:
            recv_call, recv_bbs = tmp[0], tmp[1]
        else:
            logger.error("PMS-newMSG: len(recv_bbs)")
            return False
        self._msg_data['receiver'] = recv_call.upper()
        self._msg_data['recipient_bbs'] = recv_bbs.upper()
        self._msg_data['message_type'] = 'P'
        self._msg_data['subject'] = 'CC: ' + self._msg_data['subject']
        self._mid = self._bbs_obj.new_msg(self._msg_data)
        if not self._mid:
            logger.error("PMS-newMSG: _mid")
            return False
        return self._send_msg()

    def _send_msg(self):
        if not self._mid:
            return False
        if not self._dest_call_check():
            return False
        home_bbs = self._home_bbs_var.get()
        if not home_bbs:
            return False
        if home_bbs == 'AUTO':
            return self._bbs_obj.add_local_msg_to_fwd_by_id(self._mid)
        home_bbs = home_bbs.split('.')[0]
        return self._bbs_obj.add_local_msg_to_fwd_by_id(self._mid, home_bbs)

    def _dest_call_check(self):
        to_call = str(self._msg_data.get('receiver', ''))
        to_bbs  = str(self._msg_data.get('recipient_bbs', ''))
        msg_typ = str(self._msg_data.get('message_type', ''))
        # to_address = f"{to_call}@{to_bbs}"
        if not to_call:
            self._to_call_warning()
            return False
        if not to_bbs:
            self._to_call_warning()
        if not '.' in to_bbs and msg_typ == 'P':
            self._to_call_warning()
            return False
        return True

    def _to_call_warning(self):
        self._to_call_ent.focus_set()
        WarningMsg(self._getTabStr('invalid_call_warning1'),
                   self._getTabStr('invalid_call_warning2'))
        self.lift()

    def _update_msg_size(self, event=None):
        size = len(self._text.get('1.0', tk.INSERT))
        self._var_msg_size.set(f" Size: {format_number(size)} Bytes")

    def _copy_select(self):
        if self._text.tag_ranges("sel"):
            self.clipboard_clear()
            self.clipboard_append(self._text.selection_get())
            self._text.tag_remove(tk.SEL, "1.0", tk.END)

    def _cut_select(self):
        if self._text.tag_ranges("sel"):
            self.clipboard_clear()
            self.clipboard_append(self._text.selection_get())
            self._text.delete('sel.first', 'sel.last')

    def _clipboard_past(self):
        if not self._text:
            return
        try:
            if not self._text.focus_get() == self._text:
                return
            clp_brd = self.clipboard_get()
        except tk.TclError:
            return
        self._text.insert(tk.INSERT, clp_brd)

    def _insert_fm_file(self):
        data = open_file_dialog(self)
        self.lift()
        if data:
            if type(data) == bytes:
                decoder = self._var_encoding.get()
                self._text.insert(tk.INSERT, data.decode(decoder, 'ignore'))
                return
            self._text.insert(tk.INSERT, data)
            self._text.see(tk.INSERT)

    def _save_to_file(self):
        data = self._text.get('1.0', tk.END)
        save_file_dialog(data, self)
        self.lift()

    def _insert_ftext_fm_menu(self, f_nr: int):
        try:
            text, enc = POPT_CFG.get_f_text_fm_id(f_id=f_nr)
        except ValueError:
            return
        if not text:
            return
        decoder = self._var_encoding.get()
        if any((decoder == enc, not decoder)):
            text = text.decode(enc, 'ignore')
        else:
            text = text.decode(decoder, 'ignore')
        text = replace_StringVARS(input_string=text, port_handler=PORT_HANDLER)
        text = zeilenumbruch_lines(text)
        self._text.insert(tk.INSERT, text)
        self._text.see(tk.INSERT)
        return

    def _insert_ftext(self, event=None):
        # if not hasattr(event, 'keysym'):
        if not hasattr(event, 'keycode'):
            return
        try:
            if is_linux():
                fi = int(F_KEY_TAB_LINUX[event.keycode])
            else:
                fi = int(F_KEY_TAB_WIN[event.keycode])
        except (ValueError, KeyError):
            return
        try:
            text, enc = POPT_CFG.get_f_text_fm_id(f_id=fi)
        except ValueError:
            return
        if not text:
            return
        ch_enc = self._var_encoding.get()
        if any((ch_enc == enc, not ch_enc)):
            text = text.decode(enc, 'ignore')
        else:
            text = text.decode(ch_enc, 'ignore')
        text = replace_StringVARS(input_string=text, port_handler=PORT_HANDLER)
        text = zeilenumbruch_lines(text)
        self._text.insert(tk.INSERT, text)
        self._text.see(tk.INSERT)
        return

    def _close(self):
        # self._bbs_obj = None
        if hasattr(self._root_win, 'on_bbsTab_select'):
            self._root_win.on_bbsTab_select()
        self._root_win.newPMS_MSG_win = None
        self.destroy()
