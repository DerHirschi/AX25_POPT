import tkinter as tk

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.gui_classes.guiRightClick_Menu import ContextMenu


class GuiMainMenu:
    def __init__(self, gui_root_cl):
        self._root_cl  = gui_root_cl
        self._root_win = gui_root_cl.main_win
        # ===================================
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # ===================================
        self._init_menubar()
        self._init_r_click_men()

    def _init_menubar(self):
        menubar = tk.Menu(self._root_win, tearoff=False)
        self._root_win.config(menu=menubar)
        #########################################################################
        # Menü 1 "Verbindungen"
        MenuVerb = tk.Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('new_conn'), command=self._root_cl.open_new_conn_win)
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
        MenuEdit.add_command(label=self._getTabStr('copy'), command=self._root_cl.copy_select, underline=0)
        MenuEdit.add_command(label=self._getTabStr('past'), command=self._root_cl.clipboard_past, underline=1)
        MenuEdit.add_separator()
        MenuEdit.add_command(label=self._getTabStr('past_qso_f_file'), command=self._root_cl.insert_fm_file,
                             underline=0)
        MenuEdit.add_command(label=self._getTabStr('save_qso_to_file'), command=self._root_cl.save_to_file,
                             underline=1)
        MenuEdit.add_command(label=self._getTabStr('save_mon_to_file'), command=self._root_cl.save_monitor_to_file,
                             underline=1)
        MenuEdit.add_separator()
        MenuEdit.add_command(label=self._getTabStr('clean_qso_win'), command=self._root_cl.clear_channel_vars,
                             underline=0)
        MenuEdit.add_command(label=self._getTabStr('clean_mon_win'), command=self._root_cl.clear_monitor_data,
                             underline=0)

        MenuEdit.add_separator()
        MenuEdit.add_command(label=self._getTabStr('clean_all_qso_win'), command=self._root_cl.clear_all_Channel_vars,
                             underline=0)
        menubar.add_cascade(label=self._getTabStr('edit'), menu=MenuEdit, underline=0)
        ####################################################################
        # Menü 3 "Tools"
        MenuTools = tk.Menu(menubar, tearoff=False)
        MenuTools.add_command(label="MH", command=self._root_cl.open_MH_win, underline=0)
        MenuTools.add_command(label=self._getTabStr('statistic'),
                              command=lambda: self._root_cl.open_window('PortStat'),
                              underline=1)
        MenuTools.add_separator()
        MenuTools.add_command(label="User-DB Tree",
                              command=lambda: self._root_cl.open_window('userDB_tree'),
                              underline=0)
        MenuTools.add_command(label=self._getTabStr('user_db'),
                              command=lambda: self._root_cl.open_user_db_win(),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('locator_calc'),
                              command=lambda: self._root_cl.open_window('locator_calc'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label="FT-Manager",
                              command=lambda: self._root_cl.open_settings_window('ft_manager'),
                              underline=0)
        MenuTools.add_command(label=self._getTabStr('send_file'),
                              command=lambda: self._root_cl.open_window('ft_send'),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('linkholder'),
                              command=lambda: self._root_cl.open_settings_window('l_holder'),
                              underline=0)
        MenuTools.add_command(label='Pipe-Tool',
                              command=lambda: self._root_cl.open_settings_window('pipe_sett'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label='Priv',
                              command=lambda: self._root_cl.open_settings_window('priv_win'),
                              underline=0)
        MenuTools.add_separator()
        # FIXME: PRP-Remote Disabled
        #MenuTools.add_command(label='Remote Monitor',
        #                      command=lambda: self.open_window('remote_monitor'),
        #                      underline=0)
        MenuTools.add_command(label='Dual-Port Monitor',
                              command=lambda: self._root_cl.open_window('dualPort_monitor'),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('right_level_editor'),
                              command=lambda: self._root_cl.open_window('right_level_editor'),
                              underline=0)
        MenuTools.add_command(label='Block List',
                              command=lambda: self._root_cl.open_BlockList_win(),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label='Kaffèmaschine',
                              command=lambda: self._root_cl.kaffee(),
                              underline=0)

        menubar.add_cascade(label=self._getTabStr('tools'), menu=MenuTools, underline=0)

        ###################################################################
        # Menü 4 Einstellungen
        MenuSettings = tk.Menu(menubar, tearoff=False)

        MenuSettings.add_command(label=self._getTabStr('settings'),
                                 command=lambda: self._root_cl.open_settings_window('all_sett'),
                                 underline=0)
        MenuSettings.add_separator()

        MenuSettings.add_command(label='Dual-Port',
                                 command=lambda: self._root_cl.open_window('dualPort_settings'),
                                 underline=0)

        menubar.add_cascade(label=self._getTabStr('settings'), menu=MenuSettings, underline=0)
        ########################################################################
        # APRS Menu
        MenuAPRS = tk.Menu(menubar, tearoff=False)
        MenuAPRS.add_command(label=self._getTabStr('aprs_mon'),
                             command=lambda: self._root_cl.open_window('aprs_mon'),
                             underline=0)
        #MenuAPRS.add_command(label="Beacon Tracer", command=self.open_be_tracer_win,
        #                     underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=self._getTabStr('wx_window'),
                             command=lambda: self._root_cl.open_window('wx_win'),
                             underline=0)
        MenuAPRS.add_command(label=self._getTabStr('pn_msg'),
                             command=lambda: self._root_cl.open_window('aprs_msg'),
                             underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=self._getTabStr('settings'),
                             command=lambda: self._root_cl.open_settings_window('aprs_sett'),
                             underline=0)
        # MenuAPRS.add_separator()
        menubar.add_cascade(label="APRS", menu=MenuAPRS, underline=0)
        ################################################################
        # BBS/PMS
        MenuBBS = tk.Menu(menubar, tearoff=False)
        MenuBBS.add_command(label=self._getTabStr('new_msg'),
                            command=lambda: self._root_cl.open_window('pms_new_msg'),
                            underline=0)
        MenuBBS.add_command(label=self._getTabStr('msg_center'),
                            command=lambda: self._root_cl.open_window('pms_msg_center'),
                            underline=0)

        MenuBBS.add_separator()
        MenuBBS.add_command(label=self._getTabStr('fwd_list'),
                            command=lambda: self._root_cl.open_window('pms_fwq_q'),
                            underline=0)
        MenuBBS.add_command(label=self._getTabStr('fwd_path'),
                            command=lambda: self._root_cl.open_window('fwdPath'),
                            underline=0)
        MenuBBS.add_separator()
        """
        MenuBBS.add_command(label=self._getTabStr('start_fwd'),
                            command=self._do_pms_fwd,
                            underline=0)
        """

        MenuBBS.add_command(label=self._getTabStr('start_auto_fwd'),
                            command=self._root_cl.do_pms_autoFWD,
                            underline=0)
        MenuBBS.add_separator()
        """
        MenuBBS.add_command(label='Old Settings',
                            command=lambda: self._root_cl.open_settings_window('pms_setting'),
                            underline=0) # pms_all_sett
        """
        MenuBBS.add_command(label=self._getTabStr('settings'),
                            command=lambda: self._root_cl.open_settings_window('pms_all_sett'),
                            underline=0)
        menubar.add_cascade(label='PMS/BBS', menu=MenuBBS, underline=0)
        #########################################################################
        # Menü 5 Hilfe
        MenuHelp = tk.Menu(menubar, tearoff=False)
        # MenuHelp.add_command(label="Hilfe", command=lambda: False, underline=0)
        MenuHelp.add_command(label=self._getTabStr('keybind'),
                             command=lambda: self._root_cl.open_settings_window('keybinds'),
                             underline=0)
        MenuHelp.add_separator()
        MenuHelp.add_command(label=self._getTabStr('about'),
                             command=lambda: self._root_cl.open_settings_window('about'),
                             underline=0)
        menubar.add_cascade(label=self._getTabStr('help'), menu=MenuHelp, underline=0)

    def _init_r_click_men(self):
        # Input
        inp_txt_men = ContextMenu(self._root_cl.inp_txt)
        inp_txt_men.add_item(self._getTabStr('cut'),  self._root_cl.cut_select)
        inp_txt_men.add_item(self._getTabStr('copy'), self._root_cl.copy_select)
        inp_txt_men.add_item(self._getTabStr('past'), self._root_cl.clipboard_past)
        inp_txt_men.add_item(self._getTabStr('select_all'), self._root_cl.select_all)
        inp_txt_men.add_separator()
        # inp_txt_men.add_item(self._getTabStr('save_to_file'), self._save_to_file)
        inp_txt_men.add_item(self._getTabStr('past_f_file'),  self._root_cl.insert_fm_file)
        inp_txt_men.add_separator()
        actions_submenu = inp_txt_men.add_submenu("F-Text")
        actions_submenu.add_command(label="F1",  command=lambda : self._root_cl.insert_ftext_fm_menu(1))
        actions_submenu.add_command(label="F2",  command=lambda : self._root_cl.insert_ftext_fm_menu(2))
        actions_submenu.add_command(label="F3",  command=lambda : self._root_cl.insert_ftext_fm_menu(3))
        actions_submenu.add_command(label="F4",  command=lambda : self._root_cl.insert_ftext_fm_menu(4))
        actions_submenu.add_command(label="F5",  command=lambda : self._root_cl.insert_ftext_fm_menu(5))
        actions_submenu.add_command(label="F6",  command=lambda : self._root_cl.insert_ftext_fm_menu(6))
        actions_submenu.add_command(label="F7",  command=lambda : self._root_cl.insert_ftext_fm_menu(7))
        actions_submenu.add_command(label="F8",  command=lambda : self._root_cl.insert_ftext_fm_menu(8))
        actions_submenu.add_command(label="F9",  command=lambda : self._root_cl.insert_ftext_fm_menu(9))
        actions_submenu.add_command(label="F10", command=lambda : self._root_cl.insert_ftext_fm_menu(10))
        actions_submenu.add_command(label="F11", command=lambda : self._root_cl.insert_ftext_fm_menu(11))
        actions_submenu.add_command(label="F12", command=lambda : self._root_cl.insert_ftext_fm_menu(12))
        inp_txt_men.add_separator()
        inp_txt_men.add_item(self._getTabStr('linkholder'),
                             lambda: self._root_cl.open_settings_window('l_holder'))
        inp_txt_men.add_item(label=self._getTabStr('send_file'),
                             command=lambda: self._root_cl.open_window('ft_send'))
        inp_txt_men.add_item(label="Priv",
                             command=lambda: self._root_cl.do_priv())
        inp_txt_men.add_separator()
        inp_txt_men.add_item(label=self._getTabStr('user_db'),
                             command=lambda: self._root_cl.open_user_db_win())
        inp_txt_men.add_separator()
        inp_txt_men.add_item(self._getTabStr('clean_prescription_win'), self._root_cl.clear_inpWin)


        # QSO
        out_txt_men = ContextMenu(self._root_cl.qso_txt)
        out_txt_men.add_item(self._getTabStr('send_selected'), self._root_cl.send_selected)
        out_txt_men.add_separator()
        out_txt_men.add_item(self._getTabStr('copy'), self._root_cl.copy_select)
        out_txt_men.add_item(self._getTabStr('save_qso_to_file'), self._root_cl.save_to_file)
        out_txt_men.add_separator()
        out_txt_men.add_item(self._getTabStr('linkholder'),
                             lambda: self._root_cl.open_settings_window('l_holder'))
        out_txt_men.add_item(label=self._getTabStr('send_file'),
                             command=lambda: self._root_cl.open_window('ft_send'))
        out_txt_men.add_item(label="Priv",
                             command=lambda: self._root_cl.do_priv())
        out_txt_men.add_separator()
        out_txt_men.add_item(label=self._getTabStr('user_db'),
                             command=lambda: self._root_cl.open_user_db_win())
        out_txt_men.add_separator()
        out_txt_men.add_item(self._getTabStr('clean_just_qso_win'), self._root_cl.clear_qsoWin)
        # Monitor
        mon_txt_men = ContextMenu(self._root_cl.mon_txt)
        mon_txt_men.add_item(self._getTabStr('copy'), self._root_cl.copy_select)
        mon_txt_men.add_item(self._getTabStr('save_mon_to_file'), self._root_cl.save_monitor_to_file)
        mon_txt_men.add_separator()
        mon_txt_men.add_item(self._getTabStr('clean_mon_win'), self._root_cl.clear_monitor_data)
        # Mon Tab
        # TODO
        #mon_tree_men = ContextMenu(self._mon_tree)
        #mon_tree_men.add_item('Connect', self._monitor_tree_conn_selected)

