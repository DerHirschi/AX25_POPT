import tkinter as tk

from cfg.constant import F_KEY_TAB_LINUX, F_KEY_TAB_WIN, FONT
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cli.StringVARS import replace_StringVARS
from fnc.os_fnc import is_linux
from fnc.str_fnc import get_strTab, zeilenumbruch_lines, zeilenumbruch
from gui.guiMsgBoxes import save_file_dialog, open_file_dialog
from gui.gui_classes.guiRightClick_Menu import ContextMenu


class GuiUtilities:
    def __init__(self, gui_root_cl):
        self._root_cl       = gui_root_cl
        self._popt_handler  = gui_root_cl.get_PH_mainGUI()
        # ===================================
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # ===================================
        self._main_win  = gui_root_cl.main_win
        self._inp_txt   = gui_root_cl.inp_txt
        self._qso_txt   = gui_root_cl.qso_txt
        self._mon_txt   = gui_root_cl.mon_txt
        # ===================================
        self._guiChannels = gui_root_cl.guiChannels
        self._toplevelMng = gui_root_cl.toplevel_manager


    # ===================================
    # Main Menu Bar
    def init_menubar(self):
        menubar = tk.Menu(self._main_win, tearoff=False)
        self._main_win.config(menu=menubar)
        #########################################################################
        # Menü 1 "Verbindungen"
        MenuVerb = tk.Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('new_conn'), command=self._toplevelMng.open_new_conn_win)
        MenuVerb.add_command(label=self._getTabStr('disconnect'), command=self._root_cl.disco_conn)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('disconnect_all'), command=self._root_cl.disco_all)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('port_unblock_all'),
                             command=lambda: self._root_cl.set_port_blocking(0) )
        MenuVerb.add_command(label=self._getTabStr('port_block_ignore_all'),
                             command=lambda: self._root_cl.set_port_blocking(1))
        MenuVerb.add_command(label=self._getTabStr('port_block_reject_all'),
                             command=lambda: self._root_cl.set_port_blocking(2))
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('quit'), command=self._root_cl.quit_popt)
        menubar.add_cascade(label=self._getTabStr('connections'), menu=MenuVerb, underline=0)
        #####################################################################
        # Menü 2 "Bearbeiten"
        MenuEdit = tk.Menu(menubar, tearoff=False)
        MenuEdit.add_command(label=self._getTabStr('copy'), command=self._copy_select, underline=0)
        MenuEdit.add_command(label=self._getTabStr('past'), command=self._clipboard_past, underline=1)
        MenuEdit.add_separator()
        MenuEdit.add_command(label=self._getTabStr('past_qso_f_file'), command=self._insert_fm_file,
                             underline=0)
        MenuEdit.add_command(label=self._getTabStr('save_qso_to_file'), command=self._save_to_file,
                             underline=1)
        MenuEdit.add_command(label=self._getTabStr('save_mon_to_file'), command=self._save_monitor_to_file,
                             underline=1)
        MenuEdit.add_separator()
        MenuEdit.add_command(label=self._getTabStr('clean_qso_win'), command=self._guiChannels.clear_channel_vars,
                             underline=0)
        MenuEdit.add_command(label=self._getTabStr('clean_mon_win'), command=self._clear_monitor_data,
                             underline=0)

        MenuEdit.add_separator()
        MenuEdit.add_command(label=self._getTabStr('clean_all_qso_win'), command=self._guiChannels.clear_all_Channel_vars,
                             underline=0)
        menubar.add_cascade(label=self._getTabStr('edit'), menu=MenuEdit, underline=0)
        ####################################################################
        # Menü 3 "Tools"
        MenuTools = tk.Menu(menubar, tearoff=False)
        MenuTools.add_command(label="MH", command=self._toplevelMng.open_MH_win, underline=0)
        MenuTools.add_command(label=self._getTabStr('statistic'),
                              command=lambda: self._toplevelMng.open_window('PortStat'),
                              underline=1)
        MenuTools.add_separator()
        MenuTools.add_command(label="User-DB Tree",
                              command=lambda: self._toplevelMng.open_window('userDB_tree'),
                              underline=0)
        MenuTools.add_command(label=self._getTabStr('user_db'),
                              command=lambda: self._toplevelMng.open_user_db_win(),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('locator_calc'),
                              command=lambda: self._toplevelMng.open_window('locator_calc'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label="FT-Manager",
                              command=lambda: self._toplevelMng.open_settings_window('ft_manager'),
                              underline=0)
        MenuTools.add_command(label=self._getTabStr('send_file'),
                              command=lambda: self._toplevelMng.open_window('ft_send'),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('linkholder'),
                              command=lambda: self._toplevelMng.open_settings_window('l_holder'),
                              underline=0)
        MenuTools.add_command(label='Pipe-Tool',
                              command=lambda: self._toplevelMng.open_settings_window('pipe_sett'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label='Priv',
                              command=lambda: self._toplevelMng.open_settings_window('priv_win'),
                              underline=0)
        MenuTools.add_separator()
        # FIXME: PRP-Remote Disabled
        #MenuTools.add_command(label='Remote Monitor',
        #                      command=lambda: self.open_window('remote_monitor'),
        #                      underline=0)
        MenuTools.add_command(label='Dual-Port Monitor',
                              command=lambda: self._toplevelMng.open_window('dualPort_monitor'),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('right_level_editor'),
                              command=lambda: self._toplevelMng.open_window('right_level_editor'),
                              underline=0)
        MenuTools.add_command(label='Block List',
                              command=lambda: self._toplevelMng.open_BlockList_win(),
                              underline=0)
        MenuTools.add_separator()

        #MenuTools.add_command(label='Routing-Tab',
        #                      command=lambda: self._toplevelMng.open_RoutingTab_win(),
        #                      underline=0)
        MenuTools.add_command(label='Kaffèmaschine',
                              command=lambda: self._root_cl.kaffee(),
                              underline=0)

        menubar.add_cascade(label=self._getTabStr('tools'), menu=MenuTools, underline=0)

        ###################################################################
        # Menü 4 Einstellungen
        MenuSettings = tk.Menu(menubar, tearoff=False)

        MenuSettings.add_command(label=self._getTabStr('settings'),
                                 command=lambda: self._toplevelMng.open_settings_window('all_sett'),
                                 underline=0)
        MenuSettings.add_separator()

        MenuSettings.add_command(label='Dual-Port',
                                 command=lambda: self._toplevelMng.open_window('dualPort_settings'),
                                 underline=0)

        menubar.add_cascade(label=self._getTabStr('settings'), menu=MenuSettings, underline=0)
        ########################################################################
        # APRS Menu
        MenuAPRS = tk.Menu(menubar, tearoff=False)
        MenuAPRS.add_command(label=self._getTabStr('aprs_mon'),
                             command=lambda: self._toplevelMng.open_window('aprs_mon'),
                             underline=0)
        #MenuAPRS.add_command(label="Beacon Tracer", command=self.open_be_tracer_win,
        #                     underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=self._getTabStr('wx_window'),
                             command=lambda: self._toplevelMng.open_window('wx_win'),
                             underline=0)
        MenuAPRS.add_command(label=self._getTabStr('pn_msg'),
                             command=lambda: self._toplevelMng.open_window('aprs_msg'),
                             underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=self._getTabStr('settings'),
                             command=lambda: self._toplevelMng.open_settings_window('aprs_sett'),
                             underline=0)
        # MenuAPRS.add_separator()
        menubar.add_cascade(label="APRS", menu=MenuAPRS, underline=0)
        ################################################################
        # BBS/PMS
        MenuBBS = tk.Menu(menubar, tearoff=False)
        MenuBBS.add_command(label=self._getTabStr('new_msg'),
                            command=lambda: self._toplevelMng.open_window('pms_new_msg'),
                            underline=0)
        MenuBBS.add_command(label=self._getTabStr('msg_center'),
                            command=lambda: self._toplevelMng.open_window('pms_msg_center'),
                            underline=0)

        MenuBBS.add_separator()
        MenuBBS.add_command(label=self._getTabStr('fwd_list'),
                            command=lambda: self._toplevelMng.open_window('pms_fwq_q'),
                            underline=0)
        MenuBBS.add_command(label=self._getTabStr('fwd_path'),
                            command=lambda: self._toplevelMng.open_window('fwdPath'),
                            underline=0)
        MenuBBS.add_separator()
        """
        MenuBBS.add_command(label=self._getTabStr('start_fwd'),
                            command=self._do_pms_fwd,
                            underline=0)
        """

        MenuBBS.add_command(label=self._getTabStr('start_auto_fwd'),
                            command=self._do_pms_autoFWD,
                            underline=0)
        MenuBBS.add_separator()
        """
        MenuBBS.add_command(label='Old Settings',
                            command=lambda: self._toplevelMng.open_settings_window('pms_setting'),
                            underline=0) # pms_all_sett
        """
        MenuBBS.add_command(label=self._getTabStr('settings'),
                            command=lambda: self._toplevelMng.open_settings_window('pms_all_sett'),
                            underline=0)
        menubar.add_cascade(label='PMS/BBS', menu=MenuBBS, underline=0)
        #########################################################################
        # Menü 5 Hilfe
        MenuHelp = tk.Menu(menubar, tearoff=False)
        # MenuHelp.add_command(label="Hilfe", command=lambda: False, underline=0)
        MenuHelp.add_command(label=self._getTabStr('keybind'),
                             command=lambda: self._toplevelMng.open_settings_window('keybinds'),
                             underline=0)
        MenuHelp.add_separator()
        MenuHelp.add_command(label=self._getTabStr('about'),
                             command=lambda: self._toplevelMng.open_settings_window('about'),
                             underline=0)
        menubar.add_cascade(label=self._getTabStr('help'), menu=MenuHelp, underline=0)

    # ===================================
    # R-Click Menu
    def init_r_click_men(self):
        # Input
        inp_txt_men = ContextMenu(self._inp_txt)
        inp_txt_men.add_item(self._getTabStr('cut'), self._cut_select)
        inp_txt_men.add_item(self._getTabStr('copy'), self._copy_select)
        inp_txt_men.add_item(self._getTabStr('past'), self._clipboard_past)
        inp_txt_men.add_item(self._getTabStr('select_all'), self._select_all)
        inp_txt_men.add_separator()
        # inp_txt_men.add_item(self._getTabStr('save_to_file'), self._save_to_file)
        inp_txt_men.add_item(self._getTabStr('past_f_file'), self._insert_fm_file)
        inp_txt_men.add_separator()
        actions_submenu = inp_txt_men.add_submenu("F-Text")
        actions_submenu.add_command(label="F1", command=lambda : self._insert_ftext_fm_menu(1))
        actions_submenu.add_command(label="F2", command=lambda : self._insert_ftext_fm_menu(2))
        actions_submenu.add_command(label="F3", command=lambda : self._insert_ftext_fm_menu(3))
        actions_submenu.add_command(label="F4", command=lambda : self._insert_ftext_fm_menu(4))
        actions_submenu.add_command(label="F5", command=lambda : self._insert_ftext_fm_menu(5))
        actions_submenu.add_command(label="F6", command=lambda : self._insert_ftext_fm_menu(6))
        actions_submenu.add_command(label="F7", command=lambda : self._insert_ftext_fm_menu(7))
        actions_submenu.add_command(label="F8", command=lambda : self._insert_ftext_fm_menu(8))
        actions_submenu.add_command(label="F9", command=lambda : self._insert_ftext_fm_menu(9))
        actions_submenu.add_command(label="F10", command=lambda : self._insert_ftext_fm_menu(10))
        actions_submenu.add_command(label="F11", command=lambda : self._insert_ftext_fm_menu(11))
        actions_submenu.add_command(label="F12", command=lambda : self._insert_ftext_fm_menu(12))
        inp_txt_men.add_separator()
        inp_txt_men.add_item(self._getTabStr('linkholder'),
                             lambda: self._toplevelMng.open_settings_window('l_holder'))
        inp_txt_men.add_item(label=self._getTabStr('send_file'),
                             command=lambda: self._toplevelMng.open_window('ft_send'))
        inp_txt_men.add_item(label="Priv",
                             command=lambda: self._root_cl.do_priv())
        inp_txt_men.add_separator()
        inp_txt_men.add_item(label=self._getTabStr('user_db'),
                             command=lambda: self._toplevelMng.open_user_db_win())
        inp_txt_men.add_separator()
        inp_txt_men.add_item(self._getTabStr('clean_prescription_win'), self._clear_inpWin)


        # QSO
        out_txt_men = ContextMenu(self._qso_txt)
        out_txt_men.add_item(self._getTabStr('send_selected'), self._send_selected)
        out_txt_men.add_separator()
        out_txt_men.add_item(self._getTabStr('copy'), self._copy_select)
        out_txt_men.add_item(self._getTabStr('save_qso_to_file'), self._save_to_file)
        out_txt_men.add_separator()
        out_txt_men.add_item(self._getTabStr('linkholder'),
                             lambda: self._toplevelMng.open_settings_window('l_holder'))
        out_txt_men.add_item(label=self._getTabStr('send_file'),
                             command=lambda: self._toplevelMng.open_window('ft_send'))
        out_txt_men.add_item(label="Priv",
                             command=lambda: self._root_cl.do_priv())
        out_txt_men.add_separator()
        out_txt_men.add_item(label=self._getTabStr('user_db'),
                             command=lambda: self._toplevelMng.open_user_db_win())
        out_txt_men.add_separator()
        out_txt_men.add_item(self._getTabStr('clean_just_qso_win'), self._clear_qsoWin)
        # Monitor
        mon_txt_men = ContextMenu(self._mon_txt)
        mon_txt_men.add_item(self._getTabStr('copy'), self._copy_select)
        mon_txt_men.add_item(self._getTabStr('save_mon_to_file'), self._save_monitor_to_file)
        mon_txt_men.add_separator()
        mon_txt_men.add_item(self._getTabStr('clean_mon_win'), self._clear_monitor_data)
        # Mon Tab
        # TODO
        #mon_tree_men = ContextMenu(self._mon_tree)
        #mon_tree_men.add_item('Connect', self._monitor_tree_conn_selected)

    # ===================================
    # Keybindings
    def set_binds(self):
        self._inp_txt.bind("<ButtonRelease-1>", self._on_click_inp_txt)
        self._inp_txt.bind("<KeyRelease>", self._on_key_release_inp_txt)

    def set_keybinds(self):
        self._main_win.unbind("<Key-F10>")
        self._main_win.unbind("<KeyPress-F10>")
        # self.main_win.bind("<KeyPress>",lambda event: self.callback(event))
        # lambda event: print(f"{event.keysym} - {event.keycode}\n {type(event.keysym)} - {type(event.keycode)}
        #####################
        # F-TEXT
        if is_linux():
            r = 13
        else:
            r = 11
        for fi in range(1, r):
            self._main_win.bind(f'<Shift-F{fi}>', self._insert_ftext)
        #####################
        self._main_win.bind('<F1>',             lambda event: self._root_cl.switch_channel(1))
        self._main_win.bind('<F2>',             lambda event: self._root_cl.switch_channel(2))
        self._main_win.bind('<F3>',             lambda event: self._root_cl.switch_channel(3))
        self._main_win.bind('<F4>',             lambda event: self._root_cl.switch_channel(4))
        self._main_win.bind('<F5>',             lambda event: self._root_cl.switch_channel(5))
        self._main_win.bind('<F6>',             lambda event: self._root_cl.switch_channel(6))
        self._main_win.bind('<F7>',             lambda event: self._root_cl.switch_channel(7))
        self._main_win.bind('<F8>',             lambda event: self._root_cl.switch_channel(8))
        self._main_win.bind('<F9>',             lambda event: self._root_cl.switch_channel(9))
        self._main_win.bind('<F10>',            lambda event: self._root_cl.switch_channel(10))
        self._main_win.bind('<F12>',            lambda event: self._root_cl.switch_channel(0))
        self._main_win.bind('<Return>',                 self._root_cl.snd_text)
        self._main_win.bind('<KeyRelease-Return>',      self._release_return)
        self._main_win.bind('<Shift-KeyPress-Return>',  self._shift_return)
        self._main_win.bind('<KeyRelease-Left>',        self._arrow_keys)
        self._main_win.bind('<KeyRelease-Right>',       self._arrow_keys)
        self._main_win.bind('<KeyRelease-Up>',          self._arrow_keys)
        self._main_win.bind('<KeyRelease-Down>',        self._arrow_keys)
        # self.main_win.bind('<KP_Enter>', self.snd_text)
        self._main_win.bind('<Alt-c>',          lambda event: self._toplevelMng.open_new_conn_win())
        self._main_win.bind('<Escape>',         lambda event: self._toplevelMng.open_new_conn_win())
        self._main_win.bind('<Alt-d>',          lambda event: self._root_cl.disco_conn())
        self._main_win.bind('<Control-c>',      lambda event: self._copy_select())
        #self.main_win.bind('<Control-v>',      lambda event: self._clipboard_past())
        self._main_win.bind('<Control-x>',      lambda event: self._cut_select())
        # self.main_win.bind('<Control-v>',     lambda event: self.clipboard_past())
        self._main_win.bind('<Control-a>',      lambda event: self._select_all())
        self._main_win.bind('<Control-plus>',   lambda event: self._increase_textsize())
        self._main_win.bind('<Control-minus>',  lambda event: self._decrease_textsize())
        # self.main_win.bind('<Control-Right>', lambda event: self._text_win_bigger())
        # self.main_win.bind('<Control-Left>',  lambda event: self._text_win_smaller())

        self._main_win.bind('<Key>',            lambda event: self._any_key(event))

    # ===================================
    # Keybindings - Helper
    def _any_key(self, event: tk.Event):
        if event.keycode == 104:  # Numpad Enter
            self._inp_txt.insert(tk.INSERT, '\n')
            self._root_cl.snd_text(event)

    def _arrow_keys(self, event=None):
        self._on_click_inp_txt()

    def _shift_return(self, event=None):
        pass

    def _release_return(self, event=None):
        pass

    def _on_click_inp_txt(self, event=None):
        self._inp_txt.tag_add('send', 0.0, tk.END)
        ind = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'
        self._inp_txt.tag_remove('send', ind, tk.INSERT)
        ch_vars = self._root_cl.get_ch_var(ch_index=self._root_cl.channel_index)
        ch_vars.input_win_index = ind

    def _on_key_release_inp_txt(self, event=None):
        ind = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'
        old_text = self._inp_txt.get(ind, self._inp_txt.index(tk.INSERT))
        text = zeilenumbruch(old_text)
        if old_text == text:
            self._inp_txt.tag_remove('send', ind, tk.INSERT)
            return
        self._inp_txt.delete(ind, self._inp_txt.index(tk.INSERT))
        self._inp_txt.insert(tk.INSERT, text)
        self._inp_txt.tag_remove('send', ind, tk.INSERT)
    # == Helper =========================
    # Clipboard Stuff
    def _copy_select(self):
        if self._qso_txt.tag_ranges("sel"):
            self._main_win.clipboard_clear()
            self._main_win.clipboard_append(self._qso_txt.selection_get())
            self._qso_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._inp_txt.tag_ranges("sel"):
            self._main_win.clipboard_clear()
            self._main_win.clipboard_append(self._inp_txt.selection_get())
            self._inp_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._mon_txt.tag_ranges("sel"):
            self._main_win.clipboard_clear()
            self._main_win.clipboard_append(self._mon_txt.selection_get())
            self._mon_txt.tag_remove(tk.SEL, "1.0", tk.END)

    def _cut_select(self):
        if self._inp_txt.tag_ranges("sel"):
            self._main_win.clipboard_clear()
            self._main_win.clipboard_append(self._inp_txt.selection_get())
            self._inp_txt.delete('sel.first', 'sel.last')
            self._inp_txt.see(tk.INSERT)

    def _clipboard_past(self):
        try:
            clp_brd = self._main_win.clipboard_get()
        except tk.TclError:
            logger.warning("GuiUtilities: TclError Clipboard no STR")
            return

        if clp_brd:
            self._inp_txt.insert(tk.INSERT, clp_brd)
            self._inp_txt.see(tk.INSERT)

    def _select_all(self):
        self._inp_txt.tag_remove("send", "1.0", tk.END)
        self._inp_txt.tag_add(tk.SEL, "1.0", tk.END)
        self._inp_txt.mark_set(tk.INSERT, "1.0")  # Setzt den Cursor an den Anfang
        self._inp_txt.see(tk.INSERT)  #

    def _send_selected(self):
        if not self._root_cl.channel_index:
            return
        if not self._qso_txt.tag_ranges("sel"):
            return
        selected_text = self._qso_txt.selection_get()
        selected_text += '\n'
        #self._inp_txt.tag_remove('send', '0.0', 'end')
        self._inp_txt.insert('insert', '\n')
        #ind = self._inp_txt.index(tk.INSERT)
        ch_vars = self._root_cl.get_ch_var(ch_index=self._root_cl.channel_index)
        ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))
        self._inp_txt.insert('insert', selected_text)
        #self._inp_txt.tag_add('send', ind, str(self._inp_txt.index(tk.INSERT)))
        self._root_cl.snd_text()
        self._qso_txt.tag_remove(tk.SEL, "1.0", tk.END)
        self._inp_txt.tag_remove('send', "0.0", str(self._inp_txt.index('end')))
        self._inp_txt.tag_add('send', "0.0", str(self._inp_txt.index('end')))

    # ===================================
    # Pre-write Text Stuff
    def _insert_fm_file(self):
        data = open_file_dialog(self._main_win)
        if not data:
            return
        ch_enc = self._root_cl.stat_info_encoding_var.get()
        if not ch_enc:
            data = data.decode('UTF-8', 'ignore')
        else:
            data = data.decode(ch_enc, 'ignore')
        data = zeilenumbruch_lines(data)
        self._inp_txt.insert(tk.INSERT, data)
        self._see_end_inp_win()
        return

    def _save_to_file(self):
        data = self._qso_txt.get('1.0', tk.END)
        # FIXME Codec : UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1090-1097: ordinal not in range(256)
        save_file_dialog(data, self._main_win)

    # ===================================
    # Monitor Text Stuff
    def _clear_monitor_data(self):
        self._mon_txt.configure(state='normal')
        self._mon_txt.delete('1.0', tk.END)
        self._mon_txt.configure(state='disabled')

    def _save_monitor_to_file(self):
        data = self._mon_txt.get('1.0', tk.END)
        # FIXME Codec : UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1090-1097: ordinal not in range(256)
        save_file_dialog(data)

    # ===================================
    # F-Text
    def _insert_ftext_fm_menu(self, f_nr: int):
        try:
            text, enc = POPT_CFG.get_f_text_fm_id(f_id=f_nr)
        except ValueError:
            return
        if not text:
            return
        ch_enc = self._root_cl.stat_info_encoding_var.get()
        if any((ch_enc == enc, not ch_enc)):
            text = text.decode(enc, 'ignore')
        else:
            text = text.decode(ch_enc, 'ignore')
        conn = self._root_cl.get_conn()
        text = replace_StringVARS(input_string=text, port_handler=self._popt_handler, connection=conn)
        text = zeilenumbruch_lines(text)
        self._root_cl.inp_txt.insert(tk.INSERT, text)
        self._see_end_inp_win()
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
        ch_enc = self._root_cl.stat_info_encoding_var.get()
        if any((ch_enc == enc, not ch_enc)):
            text = text.decode(enc, 'ignore')
        else:
            text = text.decode(ch_enc, 'ignore')
        conn = self._root_cl.get_conn()
        text = replace_StringVARS(input_string=text, port_handler=self._popt_handler, connection=conn)
        text = zeilenumbruch_lines(text)
        self._inp_txt.insert(tk.INSERT, text)
        self._see_end_inp_win()
        return
    # ===================================
    def _clear_inpWin(self):
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]
        chVars = self._root_cl.channel_vars[self._root_cl.channel_index]
        chVars.input_win                = ''
        chVars.input_win_tags           = {}
        chVars.input_win_index          = '1.0'
        chVars.input_win_cursor_index   = tk.INSERT

    def _clear_qsoWin(self):
        self._qso_txt.configure(state='normal')
        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.configure(state='disabled')
        # del self._channel_vars[self.channel_index]

        chVars = self._root_cl.channel_vars[self._root_cl.channel_index]
        chVars.output_win       = ''
        chVars.output_win_tags  = {}
        chVars.t2speech_buf     = ''

    # ===================================
    # GUI Sizing/Formatting Stuff
    def _increase_textsize(self):
        self._root_cl.text_size += 1
        self._root_cl.text_size = max(self._root_cl.text_size, 3)
        self._inp_txt.configure(font=(FONT, self._root_cl.text_size), )
        self._qso_txt.configure(font=(FONT, self._root_cl.text_size), )
        self._mon_txt.configure(font=(FONT, self._root_cl.text_size), )

    def _decrease_textsize(self):
        self._root_cl.text_size -= 1
        self.text_size = max(self._root_cl.text_size, 3)
        self._inp_txt.configure(font=(FONT, self._root_cl.text_size), )
        self._qso_txt.configure(font=(FONT, self._root_cl.text_size), )
        self._mon_txt.configure(font=(FONT, self._root_cl.text_size), )

    # ===================================
    def _see_end_inp_win(self):
        self._inp_txt.see("end")

    # ===================================
    def _do_pms_autoFWD(self):
        self._popt_handler.get_bbs().start_man_autoFwd()