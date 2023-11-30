import tkinter as tk
from tkinter import scrolledtext, messagebox

from UserDB.UserDBmain import USER_DB
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from constant import FONT, ENCODINGS, DEV_PRMAIL_ADD
from fnc.gui_fnc import get_typed, detect_pressed
from fnc.str_fnc import format_number
from gui.guiMsgBoxes import open_file_dialog, save_file_dialog, WarningMsg
from string_tab import STR_TABLE


class BBS_newMSG(tk.Toplevel):
    def __init__(self, root_win, reply_msg=None):
        tk.Toplevel.__init__(self)
        if reply_msg is None:
            reply_msg = {}
        self._root_win = root_win
        self._bbs_obj = PORT_HANDLER.get_bbs()
        self.text_size = int(POPT_CFG.get_guiPARM_main().get('guiMsgC_parm_text_size', self._root_win.text_size))
        self.language = root_win.language
        ###################################
        self.title(STR_TABLE['new_pr_mail'][self.language])
        self.style = self._root_win.style
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
            pass
        self.lift()
        ####################
        self._init_Menu()
        ####################
        # VARS
        self._reply_msg = reply_msg
        self._mid = 0
        self._msg_data = {}
        self._msg_typ_var = tk.StringVar(self, 'P')
        self._home_bbs_var = tk.StringVar(self)
        self._from_call_var = tk.StringVar(self)
        self._to_call_var = tk.StringVar(self)
        self._to_cc_call_var = tk.StringVar(self)
        self._subject_var = tk.StringVar(self)
        self._var_encoding = tk.StringVar(self, 'UTF-8')
        self._var_msg_size = tk.StringVar(self, ' Size: 0 Bytes')

        prmail_list = USER_DB.get_all_PRmail()
        if DEV_PRMAIL_ADD not in prmail_list:
            prmail_list.append(DEV_PRMAIL_ADD)
        self._chiefs = prmail_list

        ####################
        # Frames
        frame_btn_oben = tk.Frame(self, height=30)
        frame_oben = tk.Frame(self, height=200)
        frame_unten = tk.Frame(self)
        footer_frame = tk.Frame(self, height=20)

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
        if self._reply_msg:
            self._init_data_f_reply()
        self.bind('<Key>', self._update_msg_size)
        self.bind('<Control-c>', lambda event: self._copy_select())
        self.bind('<Control-x>', lambda event: self._cut_select())

    def _init_Menu(self):
        _menubar = tk.Menu(self, tearoff=False)
        self.config(menu=_menubar)
        # ### Mail
        _MenuVerb = tk.Menu(_menubar, tearoff=False)
        _MenuVerb.add_command(
            label='Senden',
            command=self._btn_send_msg,
        )
        _menubar.add_cascade(label='Mail', menu=_MenuVerb, underline=0)
        # ### Bearbeiten
        _MenuEdit = tk.Menu(_menubar, tearoff=False)
        _MenuEdit.add_command(label=STR_TABLE['past_f_file'][self.language],
                              command=self._insert_fm_file,
                              underline=0)
        _MenuEdit.add_command(label=STR_TABLE['save_to_file'][self.language],
                              command=self._save_to_file,
                              underline=0)
        _menubar.add_cascade(label=STR_TABLE['edit'][self.language], menu=_MenuEdit, underline=0)

    def _init_upper_btn_frame(self, root_frame):
        tk.Button(root_frame,
                  text='Senden',
                  command=self._btn_send_msg
                  ).pack(side=tk.LEFT, expand=False)
        tk.Button(root_frame,
                  text='Entwurf Speichern',
                  command=self._btn_save_msg
                  ).pack(side=tk.LEFT, expand=False, padx=10)
        tk.Button(root_frame,
                  text='Verwerfen',
                  command=self._btn_delete_all
                  ).pack(side=tk.RIGHT, expand=False, anchor='e')

    def _init_header_frame(self, root_frame):
        from_frame = tk.Frame(root_frame)
        to_frame = tk.Frame(root_frame)
        subj_frame = tk.Frame(root_frame)
        from_frame.pack(side=tk.TOP, expand=True, anchor='w', padx=10, pady=10)
        to_frame.pack(side=tk.TOP, expand=True, fill=tk.X, anchor='w', padx=10, pady=5)
        subj_frame.pack(side=tk.TOP, expand=True, anchor='w', padx=10, pady=5)

        tk.Label(from_frame, text='Von: ').pack(side=tk.LEFT, expand=False)
        _user_call = self._bbs_obj.get_pms_cfg().get('user', '')
        if _user_call:
            self._from_call_var.set(_user_call)
        tk.Entry(from_frame,
                 textvariable=self._from_call_var,
                 state='disabled'
                 ).pack(side=tk.LEFT, fill=tk.X, expand=False, padx=25)

        typ_frame = tk.Frame(from_frame)
        typ_frame.pack(side=tk.LEFT, expand=True, padx=130)
        tk.Label(typ_frame, text='Typ: ').pack(side=tk.LEFT, expand=False, )
        opt = ['P', 'B']
        tk.OptionMenu(typ_frame,
                      self._msg_typ_var,
                      *opt, ).pack(side=tk.LEFT, expand=False, )

        tk.Label(from_frame, text='HomeBBS: ').pack(side=tk.LEFT, expand=False, padx=25)
        opt = self._bbs_obj.get_pms_cfg().get('home_bbs', [])
        if opt:
            self._home_bbs_var.set(opt[0])
        tk.OptionMenu(from_frame,
                      self._home_bbs_var,
                      *opt, ).pack(side=tk.LEFT, expand=False)

        tk.Label(to_frame, text='An: ').pack(side=tk.LEFT, expand=False)
        self._to_call_ent = tk.Entry(to_frame,
                                     textvariable=self._to_call_var,
                                     # highlightcolor='blue',
                                     # fg='white',
                                     # bg='black',
                                     width=40)
        self._to_call_ent.pack(side=tk.LEFT, expand=False, padx=35)
        self._to_call_ent.bind('<KeyRelease>',
                               lambda event: get_typed(event, self._chiefs, self._to_call_var, self._to_call_ent))
        self._to_call_ent.bind('<Key>', lambda event: detect_pressed(event, self._to_call_ent))
        tk.Label(to_frame, text='CC: ').pack(side=tk.LEFT, expand=False, padx=20)
        self._cc_entry = tk.Entry(to_frame,
                                  textvariable=self._to_cc_call_var,
                                  width=40)
        self._cc_entry.pack(side=tk.LEFT, expand=False)
        self._cc_entry.bind('<KeyRelease>',
                            lambda event: get_typed(event, self._chiefs, self._to_cc_call_var, self._cc_entry))
        self._cc_entry.bind('<Key>', lambda event: detect_pressed(event, self._cc_entry))

        tk.Label(subj_frame, text='Betreff: ').pack(side=tk.LEFT, expand=False)
        tk.Entry(subj_frame,
                 textvariable=self._subject_var,
                 width=91).pack(side=tk.LEFT, expand=False)

    def _init_txt_frame(self, root_frame):
        frame = tk.Frame(root_frame)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._text = scrolledtext.ScrolledText(frame,
                                               font=(FONT, self.text_size),
                                               bd=0,
                                               height=3,
                                               borderwidth=0,
                                               background='black',
                                               foreground='white',
                                               insertbackground='white'
                                               # state="disabled",
                                               )
        self._text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _init_footer_frame(self, root_frame):
        footer_frame = tk.Frame(root_frame, height=15)
        footer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            footer_frame,
            self._var_encoding,
            *opt,
            # command=self._update_PN_msg
        )
        txt_encoding_ent.configure(
            font=(None, 6),
            border=0,
            borderwidth=0,
            height=1
        )
        txt_encoding_ent.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        tk.Label(footer_frame,
                 textvariable=self._var_msg_size,
                 font=(None, 7),
                 ).pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

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
        if self._save_msg():
            messagebox.showinfo(title='Entwurf gespeichert! ', message='Nachricht wurde als Entwurf gespeichert.')
        else:
            messagebox.showerror(title='Entwurf nicht gespeichert! ',
                                 message='Entwurf konnte nicht gespeichert werden.')

    def _btn_delete_all(self, event=None):
        if messagebox.askokcancel(title='Nachricht löschen? ', message='Nachricht wirklich verwerfen?'):
            self._text.delete('1.0', tk.END)
            self._subject_var.set('')
            self._to_cc_call_var.set('')
            self._to_call_var.set('')

    def _save_msg(self):
        sender = self._from_call_var.get()
        if not sender:
            print("E: sender")
            return False
        regio_add = self._bbs_obj.get_pms_cfg().get('regio', '')
        if not regio_add:
            print("E: regio_add")
            return False
        recv_call = self._to_call_var.get()
        if not recv_call:
            print("E: recv_call")
            return False
        tmp = recv_call.split('@')
        if len(tmp) == 1:
            recv_bbs = ''
        elif len(tmp) == 2:
            recv_call, recv_bbs = tmp[0], tmp[1]
        else:
            print("E: len(recv_bbs)")
            return False

        typ = self._msg_typ_var.get()
        if typ not in ['P', 'B']:
            print("E: typ")
            return False
        subj = self._subject_var.get()
        if not subj:
            print("E: subj")
            return False
        cc_add = self._to_cc_call_var.get()
        enc = self._var_encoding.get()
        msg_text = str(self._text.get('1.0', tk.END)[:-1])
        msg_text = msg_text.replace('\n', '\r')
        msg_text = msg_text.encode(enc, 'ignore')
        sender_bbs = sender + '.' + regio_add
        self._msg_data = {
            'sender': sender.upper(),
            'sender_bbs': sender_bbs.upper(),
            'receiver': recv_call.upper(),
            'recipient_bbs': recv_bbs.upper(),
            'subject': subj,
            'msg': msg_text,
            'message_type': typ,
            'cc_add': cc_add,
        }
        # Entwurf Nachrichten
        if self._reply_msg.get('mid', ''):
            self._mid = self._reply_msg.get('mid')
            self._msg_data['mid'] = self._reply_msg.get('mid')
            return self._bbs_obj.update_msg(self._msg_data)
        # Neue Nachrichten
        self._mid = self._bbs_obj.new_msg(self._msg_data)
        if not self._mid:
            print("E: _mid")
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
            print("E: len(recv_bbs)")
            return False
        self._msg_data['receiver'] = recv_call.upper()
        self._msg_data['recipient_bbs'] = recv_bbs.upper()
        self._msg_data['message_type'] = 'P'
        self._msg_data['subject'] = 'CC: ' + self._msg_data['subject']
        self._mid = self._bbs_obj.new_msg(self._msg_data)
        if not self._mid:
            print("E: _mid")
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
        home_bbs = home_bbs.split('.')[0]
        return self._bbs_obj.add_msg_to_fwd_by_id(self._mid, home_bbs)

    def _dest_call_check(self):
        to_call = str(self._to_call_var.get())
        if '@' not in to_call:
            self._to_call_warning()
            return False
        if not to_call.split('@')[1]:
            self._to_call_warning()
            return False
        return True

    def _to_call_warning(self):
        self._to_call_ent.focus_set()
        WarningMsg('Adresse nicht korrekt', 'Die Adresse des Empfängers ist nicht korrekt.   Keine BBS')
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

    def _insert_fm_file(self):
        data = open_file_dialog()
        self.lift()
        if data:
            if type(data) == bytes:
                decoder = self._var_encoding.get()
                self._text.insert(tk.INSERT, data.decode(decoder, 'ignore'))
                return
            self._text.insert(tk.INSERT, data)

    def _save_to_file(self):
        data = self._text.get('1.0', tk.END)
        save_file_dialog(data)
        self.lift()

    def _close(self):
        self._bbs_obj = None
        if hasattr(self._root_win, 'on_bbsTab_select'):
            self._root_win.on_bbsTab_select()
        self._root_win.newPMS_MSG_win = None
        self.destroy()
