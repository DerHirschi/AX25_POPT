import datetime
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25monitor import monitor_frame_inp
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from cfg.cfg_fnc import convert_obj_to_dict, set_obj_att_fm_dict
from cli.StringVARS import replace_StringVARS
from fnc.str_fnc import tk_filter_bad_chars, get_time_delta, format_number, conv_timestamp_delta, \
    get_kb_str_fm_bytes, conv_time_DE_str, zeilenumbruch, zeilenumbruch_lines, get_strTab
from gui.aprs.guiAISmon import AISmonitor
from gui.aprs.guiAPRS_Settings import APRSSettingsWin
from gui.aprs.guiAPRS_be_tracer import BeaconTracer
from gui.aprs.guiAPRS_pn_msg import APRS_msg_SYS_PN
from gui.aprs.guiAPRS_wx_tree import WXWin  # !!!!!!!!!!
from gui.guiDualPortMon import DualPort_Monitor
from gui.guiMain_AlarmFrame import AlarmIconFrame
from gui.guiMain_TabbedSideFrame import SideTabbedFrame
from gui.plots.gui_ConnPath_plot import ConnPathsPlot
from gui.bbs_gui.bbs_MSGcenter_gui.guiBBS_MSG_center import MSG_Center
from gui.plots.guiBBS_fwdPath_Plot import FwdGraph
from gui.bbs_gui.bbs_settings.guiBBS_Settings_Main import BBSSettingsMain
from gui.bbs_gui.guiBBS_fwd_q import BBS_fwd_Q
from gui.bbs_gui.guiBBS_newMSG import BBS_newMSG
from gui.ft.guiFT_Manager import FileTransferManager
from gui.guiLocatorCalc import LocatorCalculator
from gui.settings.guiDualPortSettings import DualPortSettingsWin
from gui.settings.guiPipeToolSettings import PipeToolSettings
from gui.plots.guiPlotPort import PlotWindow
from gui.guiPriv import PrivilegWin

from gui.UserDB.guiUserDBoverview import UserDBtreeview
from gui.guiMH import MHWin
from gui.guiNewConnWin import NewConnWin
from gui.settings.guiSettingsMain import SettingsMain
from gui.settings.guiLinkholderSettings import LinkHolderSettings
from gui.UserDB.guiUserDB import UserDB
from gui.guiAbout import About
from gui.guiHelpKeybinds import KeyBindsHelp
from gui.guiMsgBoxes import open_file_dialog, save_file_dialog
from gui.ft.guiFileTX import FileSend
from cfg.constant import FONT, POPT_BANNER, WELCOME_SPEECH, VER, MON_SYS_MSG_CLR_FG, STATION_TYPS, \
    ENCODINGS, TEXT_SIZE_STATUS, TXT_INP_CURSOR_CLR, \
    STAT_BAR_CLR, STAT_BAR_TXT_CLR, FONT_STAT_BAR, STATUS_BG, PARAM_MAX_MON_LEN, CFG_sound_RX_BEEP, \
    SERVICE_CH_START, DEF_STAT_QSO_TX_COL, DEF_STAT_QSO_BG_COL, DEF_STAT_QSO_RX_COL, DEF_PORT_MON_BG_COL, \
    DEF_PORT_MON_RX_COL, DEF_PORT_MON_TX_COL, MON_SYS_MSG_CLR_BG, F_KEY_TAB_LINUX, F_KEY_TAB_WIN, DEF_QSO_SYSMSG_FG, \
    DEF_QSO_SYSMSG_BG, MAX_SYSOP_CH, COLOR_MAP, STYLES_AWTHEMES_PATH, STYLES_AWTHEMES
from cfg.string_tab import STR_TABLE
from fnc.os_fnc import is_linux, get_root_dir
from fnc.gui_fnc import get_all_tags, set_all_tags, generate_random_hex_color, set_new_tags, cleanup_tags
from sound.popt_sound import SOUND
from gui.plots.guiLiveConnPath import LiveConnPath

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from gui import FigureCanvasTkAgg
# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread

# from matplotlib import pyplot as plt
from gui import plt


class ChVars(object):
    output_win = ''
    input_win = ''
    output_win_tags = {}
    input_win_tags = {}
    new_tags = []
    last_tag_name = 'NOCALL'
    input_win_index = '1.0'
    input_win_cursor_index = tk.INSERT
    new_data_tr = False
    rx_beep_tr = False
    rx_beep_cooldown = time.time()
    rx_beep_opt = False
    timestamp_opt = False
    t2speech = False
    t2speech_buf = ''
    autoscroll = True
    # live_path_plot_data = {}
    # live_path_plot_last_node = 'HOME'

    # self.hex_output = True


class PoPT_GUI_Main:
    def __init__(self, port_handler: PORT_HANDLER):
        ######################################
        # GUI Stuff
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._logTag = 'GUI-Main> '
        logTag = self._logTag + 'Init: '
        logger.info(logTag + 'start..')
        guiCfg = POPT_CFG.load_guiPARM_main()
        ###########################################
        self.main_win   = tk.Tk()
        ###########################################
        self.style_name = guiCfg.get('gui_parm_style_name', 'default')
        logger.info(logTag + f'loading Style: {self.style_name}')
        self.style = ttk.Style(self.main_win)

        if self.style_name in STYLES_AWTHEMES:
            try:
                self.style.tk.call('lappend', 'auto_path', STYLES_AWTHEMES_PATH)
                self.style.tk.call('package', 'require', 'awthemes')
                self.style.tk.call('::themeutils::setHighlightColor', self.style_name, '#007000') # TODO
                self.style.tk.call('package', 'require', self.style_name)
                self.style.theme_use(self.style_name)
            except tk.TclError:
                logger.warning(logTag + 'awthemes-10.4.0 not found in folder data')
                logger.warning(logTag + '  1. If you want to use awthemes, download:')
                logger.warning(logTag + '     https://sourceforge.net/projects/tcl-awthemes/')
                logger.warning(logTag + '  2. Extract the contents of the file awthemes-10.4.0.zip')
                logger.warning(logTag + '     into the data/ folder')
                logger.warning(logTag + '')
                self.style_name = 'default'
                self.style.theme_use(self.style_name)
        else:
            try:
                self.style.theme_use(self.style_name)
            except tk.TclError:
                logger.warning(logTag + f'TclError Style{self.style_name}')
                self.style_name = 'default'
                self.style.theme_use(self.style_name)

        logger.info(logTag + f'Using style_name: {self.style_name}')
        self._get_colorMap = lambda : COLOR_MAP.get(self.style_name, ('black', '#d9d9d9'))
        #################################################################
        self.main_win.title(f"P.ython o.ther P.acket T.erminal {VER}")
        self.main_win.geometry(f"{guiCfg.get('gui_parm_main_width', 1400)}x{guiCfg.get('gui_parm_main_height', 850)}")
        # self.main_win.attributes('-topmost', 0)
        try:
            self.main_win.iconbitmap("favicon.ico")
        except tk.TclError:
            logger.warning(logTag + f"Couldn't load favicon.ico ")
            pass
        self.main_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
        ######################################
        self._port_handler = port_handler
        ######################################
        # Init Vars
        self.mh         = self._port_handler.get_MH()
        self.language   = POPT_CFG.get_guiCFG_language()
        self.text_size  = POPT_CFG.load_guiPARM_main().get('gui_parm_text_size', 13)
        ###############################
        self._root_dir  = get_root_dir()
        self._root_dir  = self._root_dir.replace('/', '//')
        #####################
        # GUI VARS
        self.connect_history    = POPT_CFG.load_guiPARM_main().get('gui_parm_connect_history', {})
        # GLb Setting Vars
        self.setting_sound          = tk.BooleanVar(self.main_win)
        self.setting_sprech         = tk.BooleanVar(self.main_win)
        self.setting_bake           = tk.BooleanVar(self.main_win)
        self.setting_rx_echo        = tk.BooleanVar(self.main_win)
        self.setting_tracer         = tk.BooleanVar(self.main_win)
        self.setting_auto_tracer    = tk.BooleanVar(self.main_win)
        self.setting_dx_alarm       = tk.BooleanVar(self.main_win)
        self.setting_noty_bell      = tk.BooleanVar(self.main_win)
        self.setting_mon_encoding   = tk.StringVar( self.main_win)
        ###################
        # Status Frame Vars
        self._status_name_var       = tk.StringVar(self.main_win)
        self._status_status_var     = tk.StringVar(self.main_win)
        self._status_unack_var      = tk.StringVar(self.main_win)
        self._status_vs_var         = tk.StringVar(self.main_win)
        self._status_n2_var         = tk.StringVar(self.main_win)
        self._status_t1_var         = tk.StringVar(self.main_win)
        self._status_t2_var         = tk.StringVar(self.main_win)
        self._status_rtt_var        = tk.StringVar(self.main_win)
        self._status_t3_var         = tk.StringVar(self.main_win)
        self._rx_beep_var           = tk.IntVar(self.main_win)
        self._ts_box_var            = tk.IntVar(self.main_win)
        # OWN Stat INFO (LOC, QTH)
        self.own_loc = ''
        self.own_qth = ''
        # Stat INFO (Name,QTH usw)
        self.stat_info_name_var     = tk.StringVar(self.main_win)
        self.stat_info_qth_var      = tk.StringVar(self.main_win)
        self.stat_info_loc_var      = tk.StringVar(self.main_win)
        self.stat_info_typ_var      = tk.StringVar(self.main_win)
        self.stat_info_sw_var       = tk.StringVar(self.main_win)
        self.stat_info_timer_var    = tk.StringVar(self.main_win)
        self.stat_info_encoding_var = tk.StringVar(self.main_win)
        self.stat_info_status_var   = tk.StringVar(self.main_win)
        # Tabbed SideFrame FT
        self.ft_progress_var        = tk.StringVar(self.main_win)
        self.ft_size_var            = tk.StringVar(self.main_win)
        self.ft_duration_var        = tk.StringVar(self.main_win)
        self.ft_bps_var             = tk.StringVar(self.main_win)
        self.ft_next_tx_var         = tk.StringVar(self.main_win)
        # Tabbed SideFrame Channel
        self.link_holder_var        = tk.BooleanVar(self.main_win)
        # Tabbed SideFrame Monitor
        self.mon_to_add_var         = tk.StringVar(self.main_win)
        self.mon_cmd_var            = tk.BooleanVar(self.main_win)
        self.mon_poll_var           = tk.BooleanVar(self.main_win)
        self.mon_port_var           = tk.StringVar(self.main_win)
        self.mon_call_var           = tk.StringVar(self.main_win)
        self.mon_scroll_var         = tk.BooleanVar(self.main_win)
        self.mon_aprs_var           = tk.BooleanVar(self.main_win)
        self.mon_pid_var            = tk.StringVar(self.main_win)
        self.mon_port_on_vars       = {}
        all_ports = self._port_handler.ax25_ports
        for port_id in all_ports:
            self.mon_port_on_vars[port_id] = tk.BooleanVar(self.main_win)
            self.mon_port_on_vars[port_id].set(all_ports[port_id].monitor_out)
        self.mon_port_var.set('0')
        self.mon_aprs_var.set(True)
        ##############
        # Controlling
        self._ch_alarm      = False
        self.channel_index  = 1
        self.mon_mode       = 0
        self._quit          = False
        self._init_state    = 0
        self._tracer_alarm  = False
        self._flip05        = True
        ####################
        # GUI PARAM
        self._parm_btn_blink_time               = 1  # s
        self._parm_rx_beep_cooldown             = 2  # s
        # Tasker Timings
        self._loop_delay                        = 60  # ms
        self._parm_non_prio_task_timer          = 0.25  # s
        self._parm_non_non_prio_task_timer      = 1  # s
        self._parm_non_non_non_prio_task_timer  = 5  # s
        self._non_prio_task_timer               = time.time()
        self._non_non_prio_task_timer           = time.time()
        self._non_non_non_prio_task_timer       = time.time()
        # #### Tester
        # self._parm_test_task_timer = 60  # 5        # s
        # self._test_task_timer = time.time()
        ########################################
        ############################
        # Windows
        self.new_conn_win           = None
        self.settings_win           = None
        self.mh_window              = None
        self.wx_window              = None
        self.port_stat_win          = None
        self.be_tracer_win          = None
        self.locator_calc_window    = None
        self.aprs_mon_win           = None
        self.aprs_pn_msg_win        = None
        self.userdb_win             = None
        self.userDB_tree_win        = None
        self.FileSend_win           = None
        self.BBS_fwd_q_list         = None
        self.MSG_Center_win         = None
        self.newPMS_MSG_win         = None
        self.fwd_Path_plot_win      = None
        self.dualPort_settings_win  = None
        self.dualPortMon_win        = None
        self.conn_Path_plot_win     = None
        ####################################
        ####################################
        # Window Text Buffers & Channel Vars
        logger.info('GUI: Channel Vars Init')
        self._channel_vars = {}
        self._init_Channel_Vars()
        ######################################
        # ....
        self._main_pw       = ttk.PanedWindow(self.main_win, orient=tk.HORIZONTAL)
        self._main_pw.pack(fill=tk.BOTH, expand=True)

        l_frame             = ttk.Frame(self._main_pw)
        self._r_frame       = ttk.Frame(self._main_pw)
        r_pack_frame        = ttk.Frame(self._r_frame)
        l_frame.pack(fill=tk.BOTH, expand=True)
        self._r_frame.pack(fill=tk.BOTH, expand=True)
        r_pack_frame.pack( fill=tk.BOTH, expand=True)
        """
        if is_linux():
            self._main_pw.add(l_frame, weight=150)
        else:
            self._main_pw.add(l_frame, weight=3)
        """
        self._main_pw.add(l_frame,       weight=1)
        self._main_pw.add(self._r_frame, weight=0)
        ###########################################
        # Channel Buttons
        self._ch_btn_blink_timer    = time.time()
        self._con_btn_dict          = {}
        ch_btn_frame                = ttk.Frame(l_frame)
        ch_btn_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, )
        self._init_ch_btn_frame(ch_btn_frame)
        ###########################################
        # Input Output TXT Frames and Status Bar
        self._pw = ttk.PanedWindow(l_frame, orient=tk.VERTICAL, )
        self._pw.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)
        # Input
        self._TXT_upper_frame = ttk.Frame(self._pw, borderwidth=0, height=20)
        # QSO
        self._TXT_mid_frame = ttk.Frame(self._pw, borderwidth=0, )
        # Mon
        self._TXT_lower_frame = ttk.Frame(self._pw, borderwidth=0, )
        # Pack it
        self._TXT_upper_frame.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)
        self._TXT_mid_frame.pack(  side=tk.BOTTOM, expand=1, fill=tk.BOTH)
        self._TXT_lower_frame.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)

        self._inp_txt = None
        self._out_txt = None
        self._mon_txt = None
        self._init_TXT_frame_up()
        self._init_TXT_frame_mid()
        self._init_TXT_frame_low()

        self._pw.add(self._TXT_upper_frame, weight=1)
        self._pw.add(self._TXT_mid_frame,   weight=1)
        self._pw.add(self._TXT_lower_frame, weight=1)
        ######################################################################
        ######################################################################
        # RIGHT Pane
        self._Alarm_Frame = AlarmIconFrame(r_pack_frame, self)
        ######################################################################
        # GUI Buttons
        conn_btn_frame = ttk.Frame(r_pack_frame, )
        conn_btn_frame.pack(expand=False, pady=5, fill=tk.X)
        # conn_btn_frame.pack(anchor='w', fill=tk.X, expand=True)
        self._init_btn(conn_btn_frame)
        ######################################################################
        # Pane Tabbed Frame
        self._side_pw = ttk.PanedWindow(r_pack_frame, orient=tk.VERTICAL, )
        self._side_pw.pack(expand=True, pady=5, fill=tk.BOTH)
        #
        tabbedF_upper_frame = ttk.Frame(self._side_pw)
        tabbedF_lower_frame = ttk.Frame(self._side_pw)
        tabbedF_upper_frame.pack()
        tabbedF_lower_frame.pack()
        self._side_pw.add(tabbedF_upper_frame, weight=1)
        self._side_pw.add(tabbedF_lower_frame, weight=1)
        ##############
        # tabbed Frame
        bw_plot_frame           = ttk.Frame(self.main_win)
        self._Pacman            = LiveConnPath(self.main_win)
        self.tabbed_sideFrame   = SideTabbedFrame(self, tabbedF_upper_frame, path_frame=self._Pacman)
        self.tabbed_sideFrame2  = SideTabbedFrame(self, tabbedF_lower_frame, plot_frame=bw_plot_frame)
        ############################
        # Canvas Plot
        logger.info(logTag + 'BW-Plot Init')
        self._bw_plot_x_scale   = []
        self._bw_plot_lines     = {}
        self._init_bw_plot(bw_plot_frame)
        ###########################
        # set KEY BINDS
        self._set_binds()
        self._set_keybinds()
        # Menubar
        self._init_menubar()
        # set Ch Btn Color
        self.ch_status_update()
        # Init Vars fm CFG
        logger.info('GUI: Parm/CFG Init')
        self._init_GUI_vars_fm_CFG()
        self._init_PARM_vars()
        self._load_pw_pos()
        self._set_CFG()
        # Text Tags
        self._all_tag_calls = []
        logger.info('GUI: Text-Tag Init')
        self.set_text_tags()
        # .....
        self._update_qso_Vars()
        #############################
        # set GUI Var to Port Handler
        self._port_handler.set_gui(self)
        ############################
        self._monitor_start_msg()
        ############################
        self._Pacman.update_plot_f_ch(self.channel_index)
        ##########################################
        # Menubar fix if app starts in fullscreen
        geom = self.main_win.winfo_geometry()
        self.main_win.geometry(geom)
        #######################
        # LOOP LOOP LOOP
        self.main_win.after(self._loop_delay, self._tasker)
        logger.info('GUI: Init Done')
        logger.info('GUI: Start Tasker')
        self.main_win.mainloop()

    ##############################################################
    def __del__(self):
        pass

    def _destroy_win(self):
        self.sysMsg_to_monitor("PoPT wird beendet.")
        self._Pacman.save_path_data()
        logger.info('GUI: Closing GUI')
        for wn in [
            self.settings_win,
            self.mh_window,
            self.wx_window,
            self.userdb_win,
            self.userDB_tree_win,
            self.aprs_mon_win,
            self.aprs_pn_msg_win,
            self.be_tracer_win,
            self.BBS_fwd_q_list,
            self.MSG_Center_win,
            self.newPMS_MSG_win,
            self.fwd_Path_plot_win,
            self.dualPort_settings_win,
            self.dualPortMon_win,
            self.conn_Path_plot_win,
        ]:
            if hasattr(wn, 'destroy_win'):
                wn.destroy_win()
            if hasattr(wn, 'destroy'):
                wn.destroy()
        logger.info('GUI: Closing GUI: Save GUI Vars & Parameter.')
        self.save_GUIvars()
        self._save_parameter()
        self._save_pw_pos()
        self._save_Channel_Vars()
        logger.info('GUI: Closing GUI: Closing Ports.')
        threading.Thread(target=self._port_handler.close_popt).start()
        logger.debug('GUI: Closing GUI: Destroying all Sub-Windows')
        self._quit = True
        self.main_win.update_idletasks()
        self._loop_delay = 800
        logger.info('GUI: Closing GUI: Done')

    def save_GUIvars(self):
        #########################
        # GUI-Vars to cfg
        guiCfg = POPT_CFG.load_guiPARM_main()
        # guiCfg['gui_lang'] = int(self.language)
        guiCfg['gui_cfg_sound']         = bool(self.setting_sound.get())
        guiCfg['gui_cfg_beacon']        = bool(self.setting_bake.get())
        guiCfg['gui_cfg_rx_echo']       = bool(self.setting_rx_echo.get())
        # guiCfg['gui_cfg_tracer']      = bool(self.setting_tracer.get())
        guiCfg['gui_cfg_tracer']        = False
        guiCfg['gui_cfg_auto_tracer']   = bool(self.setting_auto_tracer.get())
        guiCfg['gui_cfg_dx_alarm']      = bool(self.setting_dx_alarm.get())
        guiCfg['gui_cfg_noty_bell']     = bool(self.setting_noty_bell.get())
        guiCfg['gui_cfg_sprech']        = bool(self.setting_sprech.get())
        guiCfg['gui_cfg_mon_encoding']  = str(self.setting_mon_encoding.get())
        try:
            guiCfg['gui_cfg_rtab_index'] = int(self.tabbed_sideFrame.get_tab_index()), int(self.tabbed_sideFrame2.get_tab_index())
        except (ValueError, tk.TclError):
            pass
        # guiCfg['gui_cfg_locator'] = str(self.own_loc)
        # guiCfg['gui_cfg_qth'] = str(self.own_qth)
        POPT_CFG.save_guiPARM_main(guiCfg)

    def _save_parameter(self):
        #########################
        # Parameter to cfg
        guiCfg = POPT_CFG.load_guiPARM_main()
        guiCfg['gui_parm_new_call_alarm']   = bool(self.mh.parm_new_call_alarm)
        guiCfg['gui_parm_channel_index']    = int(self.channel_index)
        guiCfg['gui_parm_text_size']        = int(self.text_size)
        guiCfg['gui_parm_connect_history']  = dict(self.connect_history)
        POPT_CFG.save_guiPARM_main(guiCfg)

    def _save_Channel_Vars(self):
        current_ch_vars = self.get_ch_var(ch_index=self.channel_index)
        current_ch_vars.input_win = self._inp_txt.get('1.0', tk.END)
        current_ch_vars.input_win_tags = get_all_tags(self._inp_txt)
        current_ch_vars.output_win_tags = get_all_tags(self._out_txt)
        current_ch_vars.input_win_cursor_index = self._inp_txt.index(tk.INSERT)
        # guiCfg = POPT_CFG.load_guiCH_VARS()
        ch_vars = {}
        for ch_id in list(self._channel_vars.keys()):
            ch_vars[ch_id] = convert_obj_to_dict(self._channel_vars[ch_id])
            del ch_vars[ch_id]['t2speech_buf']
            del ch_vars[ch_id]['rx_beep_cooldown']
            del ch_vars[ch_id]['rx_beep_tr']
            del ch_vars[ch_id]['output_win_tags']
            del ch_vars[ch_id]['input_win_tags']
            ch_vars[ch_id]['output_win_tags'] = cleanup_tags(self._channel_vars[ch_id].output_win_tags)
            ch_vars[ch_id]['input_win_tags'] = cleanup_tags(self._channel_vars[ch_id].input_win_tags)
        POPT_CFG.save_guiCH_VARS(dict(ch_vars))
        # POPT_CFG.save_guiCH_VARS({})

    ####################
    # Init Stuff
    def _init_Channel_Vars(self):
        cfg_ch_vars = POPT_CFG.load_guiCH_VARS()
        for ch_id in list(cfg_ch_vars.keys()):
            self._channel_vars[ch_id] = set_obj_att_fm_dict(ChVars(), cfg_ch_vars[ch_id])

    def _init_GUI_vars_fm_CFG(self):
        #########################
        # GUI-Vars fm cfg
        self.language = POPT_CFG.get_guiCFG_language()
        guiCfg = POPT_CFG.load_guiPARM_main()
        self.setting_sound.set(guiCfg.get('gui_cfg_sound', False))
        self.setting_bake.set(guiCfg.get('gui_cfg_beacon', False))
        self.setting_rx_echo.set(guiCfg.get('gui_cfg_rx_echo', False))
        self.set_rxEcho_icon(self.setting_rx_echo.get())
        self._port_handler.rx_echo_on = bool(self.setting_rx_echo.get())
        if is_linux():
            self.setting_sprech.set(guiCfg.get('gui_cfg_sprech', False))
        else:
            self.setting_sprech.set(False)
        self.setting_tracer.set(guiCfg.get('gui_cfg_tracer', False))
        self.setting_auto_tracer.set(guiCfg.get('gui_cfg_auto_tracer', False))
        self.setting_dx_alarm.set(guiCfg.get('gui_cfg_dx_alarm', True))
        self.setting_noty_bell.set(guiCfg.get('gui_cfg_noty_bell', False))
        self.setting_mon_encoding.set(guiCfg.get('gui_cfg_mon_encoding', 'Auto'))
        # OWN Loc and QTH
        self.own_loc = guiCfg.get('gui_cfg_locator', '')
        self.own_qth = guiCfg.get('gui_cfg_qth', '')
        tab1_index, tab2_index = guiCfg.get('gui_cfg_rtab_index', (None, None))
        self.tabbed_sideFrame.set_tab_index(tab1_index)
        self.tabbed_sideFrame2.set_tab_index(tab2_index)

    def _init_PARM_vars(self):
        #########################
        # Parameter fm cfg
        # ## guiCfg = POPT_CFG.load_guiPARM_main()
        # self._port_handler.get_MH().parm_new_call_alarm = guiCfg.get('gui_parm_new_call_alarm', False)
        # self.channel_index = guiCfg.get('gui_parm_channel_index', 1)
        # ## self.text_size = guiCfg.get('gui_parm_text_size', 13)
        # self.connect_history: {str: ConnHistory}
        # self._mon_buff: (
        #             ax25frame,
        #             conf,
        #             bool(tx)
        #         )
        pass

    def _set_CFG(self):
        self.set_tracer()
        self.set_auto_tracer()
        self.set_dx_alarm()
        self.set_noty_bell_active()
        self.set_Beacon_icon(self.setting_bake.get())
        self.chk_master_sprech_on()

    ###############################################################
    # Panned Win size load/save
    def _load_pw_pos(self):
        # self._main_pw     # Main Pan l/r
        # self._pw          # Text Pan 0/1/2
        # self._side_pw     # Side Frame Pan u/l
        guiCfg      = POPT_CFG.load_guiPARM_main()
        main_hight  = self.main_win.winfo_height()
        self._main_pw.sashpos(0, guiCfg.get('gui_parm_main_pan_pos', 100))
        self._side_pw.sashpos(0, guiCfg.get('gui_parm_side_pan_pos', int(main_hight/ 2)))

        text_pan_pos_cfg = guiCfg.get('gui_parm_text_pan_pos', [300, 300])
        i = 0
        for pan_pos in text_pan_pos_cfg:
            self._pw.sashpos(i, pan_pos)
            i += 1

    def _save_pw_pos(self):
        text_pan_pos_cfg = []
        for pan_id in range(2):
            text_pan_pos_cfg.append(self._pw.sashpos(pan_id))

        guiCfg = POPT_CFG.load_guiPARM_main()
        guiCfg['gui_parm_main_pan_pos'] = int(self._main_pw.sashpos(0))
        guiCfg['gui_parm_side_pan_pos'] = int(self._side_pw.sashpos(0))
        guiCfg['gui_parm_text_pan_pos'] = tuple(text_pan_pos_cfg)
        guiCfg['gui_parm_main_height']  = int(self.main_win.winfo_height())
        guiCfg['gui_parm_main_width']   = int(self.main_win.winfo_width())
        POPT_CFG.save_guiPARM_main(guiCfg)

    ###############################################################
    # GUI Init Stuff
    def _init_bw_plot(self, frame):
        for _i in list(range(60)):
            self._bw_plot_x_scale.append(_i / 6)
        self._bw_fig, self._ax = plt.subplots(dpi=100)
        self._bw_fig.subplots_adjust(left=0.1, right=0.95, top=0.99, bottom=0.15)
        self._ax.axis([0, 10, 0, 100])  # TODO As Option
        fg, bg = COLOR_MAP.get(self.style_name, ('black', 'light grey'))
        #self._bw_fig.set_facecolor('xkcd:light grey')
        self._bw_fig.set_facecolor(bg)
        # self._bw_fig.set_color('#FFFFFF')
        self._ax.set_facecolor('#191621')
        #self._ax.xaxis.label.set_color('black')
        #self._ax.yaxis.label.set_color('black')
        self._ax.xaxis.label.set_color(fg)
        self._ax.yaxis.label.set_color(fg)
        self._ax.tick_params(axis='x', colors=fg)
        self._ax.tick_params(axis='y', colors=fg)
        self._ax.set_xlabel(self._getTabStr('minutes'))
        self._ax.set_ylabel(self._getTabStr('occup'))
        # self._canvas = FigureCanvasTkAgg(self._bw_fig, master=self._r_frame)
        self._canvas = FigureCanvasTkAgg(self._bw_fig, master=frame)
        self._canvas.flush_events()
        self._canvas.draw()
        # self._canvas.get_tk_widget().grid(row=4, column=0, columnspan=7, sticky="nsew")
        self._canvas.get_tk_widget().pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        # self._canvas.get_tk_widget().config(cursor="none")
        self._bw_fig.canvas.flush_events()

    def _init_menubar(self):
        menubar = tk.Menu(self.main_win, tearoff=False)
        self.main_win.config(menu=menubar)
        #########################################################################
        # Menü 1 "Verbindungen"
        MenuVerb = tk.Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=STR_TABLE['new_conn'][self.language], command=self.open_new_conn_win)
        MenuVerb.add_command(label=STR_TABLE['disconnect'][self.language], command=self._disco_conn)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=STR_TABLE['disconnect_all'][self.language], command=self._disco_all)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=STR_TABLE['quit'][self.language], command=self._destroy_win)
        menubar.add_cascade(label=STR_TABLE['connections'][self.language], menu=MenuVerb, underline=0)
        #####################################################################
        # Menü 2 "Bearbeiten"
        MenuEdit = tk.Menu(menubar, tearoff=False)
        MenuEdit.add_command(label=STR_TABLE['copy'][self.language], command=self._copy_select, underline=0)
        MenuEdit.add_command(label=STR_TABLE['past'][self.language], command=self._clipboard_past, underline=1)
        MenuEdit.add_separator()
        MenuEdit.add_command(label=STR_TABLE['past_qso_f_file'][self.language], command=self._insert_fm_file,
                             underline=0)
        MenuEdit.add_command(label=STR_TABLE['save_qso_to_file'][self.language], command=self._save_to_file,
                             underline=1)
        MenuEdit.add_command(label=STR_TABLE['save_mon_to_file'][self.language], command=self._save_monitor_to_file,
                             underline=1)
        MenuEdit.add_separator()
        MenuEdit.add_command(label=STR_TABLE['clean_qso_win'][self.language], command=self.clear_channel_vars,
                             underline=0)
        MenuEdit.add_command(label=STR_TABLE['clean_mon_win'][self.language], command=self._clear_monitor_data,
                             underline=0)

        MenuEdit.add_separator()
        MenuEdit.add_command(label=STR_TABLE['clean_all_qso_win'][self.language], command=self._clear_all_Channel_vars,
                             underline=0)
        menubar.add_cascade(label=STR_TABLE['edit'][self.language], menu=MenuEdit, underline=0)
        ####################################################################
        # Menü 3 "Tools"
        MenuTools = tk.Menu(menubar, tearoff=False)
        MenuTools.add_command(label="MH", command=self.open_MH_win, underline=0)
        MenuTools.add_command(label="MH-Graph",
                              command=lambda: self.open_window('ConnPathPlot'),
                              underline=0)
        MenuTools.add_command(label=STR_TABLE['statistic'][self.language],
                              command=lambda: self.open_window('PortStat'),
                              underline=1)
        MenuTools.add_separator()
        MenuTools.add_command(label="User-DB Tree",
                              command=lambda: self.open_window('userDB_tree'),
                              underline=0)
        MenuTools.add_command(label=STR_TABLE['user_db'][self.language],
                              command=lambda: self.open_user_db_win(),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=STR_TABLE['locator_calc'][self.language],
                              command=lambda: self.open_window('locator_calc'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label="FT-Manager",
                              command=lambda: self._open_settings_window('ft_manager'),
                              underline=0)
        MenuTools.add_command(label=STR_TABLE['send_file'][self.language],
                              command=lambda: self.open_window('ft_send'),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=STR_TABLE['linkholder'][self.language],
                              command=lambda: self._open_settings_window('l_holder'),
                              underline=0)
        MenuTools.add_command(label='Pipe-Tool',
                              command=lambda: self._open_settings_window('pipe_sett'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label='Priv',
                              command=lambda: self._open_settings_window('priv_win'),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label='Dual-Port Monitor',
                              command=lambda: self.open_window('dualPort_monitor'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label='Kaffèmaschine',
                              command=lambda: self._kaffee(),
                              underline=0)

        menubar.add_cascade(label=STR_TABLE['tools'][self.language], menu=MenuTools, underline=0)

        ###################################################################
        # Menü 4 Einstellungen
        MenuSettings = tk.Menu(menubar, tearoff=False)

        MenuSettings.add_command(label=STR_TABLE['settings'][self.language],
                                 command=lambda: self._open_settings_window('all_sett'),
                                 underline=0)
        MenuSettings.add_separator()

        MenuSettings.add_command(label='Dual-Port',
                                 command=lambda: self.open_window('dualPort_settings'),
                                 underline=0)

        menubar.add_cascade(label=STR_TABLE['settings'][self.language], menu=MenuSettings, underline=0)
        ########################################################################
        # APRS Menu
        MenuAPRS = tk.Menu(menubar, tearoff=False)
        MenuAPRS.add_command(label=STR_TABLE['aprs_mon'][self.language],
                             command=lambda: self.open_window('aprs_mon'),
                             underline=0)
        MenuAPRS.add_command(label="Beacon Tracer", command=self.open_be_tracer_win,
                             underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=STR_TABLE['wx_window'][self.language],
                             command=lambda: self.open_window('wx_win'),
                             underline=0)
        MenuAPRS.add_command(label=STR_TABLE['pn_msg'][self.language],
                             command=lambda: self.open_window('aprs_msg'),
                             underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=STR_TABLE['settings'][self.language],
                             command=lambda: self._open_settings_window('aprs_sett'),
                             underline=0)
        # MenuAPRS.add_separator()
        menubar.add_cascade(label="APRS", menu=MenuAPRS, underline=0)
        ################################################################
        # BBS/PMS
        MenuBBS = tk.Menu(menubar, tearoff=False)
        MenuBBS.add_command(label=STR_TABLE['new_msg'][self.language],
                            command=lambda: self.open_window('pms_new_msg'),
                            underline=0)
        MenuBBS.add_command(label=STR_TABLE['msg_center'][self.language],
                            command=lambda: self.open_window('pms_msg_center'),
                            underline=0)

        MenuBBS.add_separator()
        MenuBBS.add_command(label=STR_TABLE['fwd_list'][self.language],
                            command=lambda: self.open_window('pms_fwq_q'),
                            underline=0)
        MenuBBS.add_command(label=STR_TABLE['fwd_path'][self.language],
                            command=lambda: self.open_window('fwdPath'),
                            underline=0)
        MenuBBS.add_separator()
        """
        MenuBBS.add_command(label=STR_TABLE['start_fwd'][self.language],
                            command=self._do_pms_fwd,
                            underline=0)
        """

        MenuBBS.add_command(label=STR_TABLE['start_auto_fwd'][self.language],
                            command=self._do_pms_autoFWD,
                            underline=0)
        MenuBBS.add_separator()
        """
        MenuBBS.add_command(label='Old Settings',
                            command=lambda: self._open_settings_window('pms_setting'),
                            underline=0) # pms_all_sett
        """
        MenuBBS.add_command(label=STR_TABLE['settings'][self.language],
                            command=lambda: self._open_settings_window('pms_all_sett'),
                            underline=0)
        menubar.add_cascade(label='PMS/BBS', menu=MenuBBS, underline=0)
        #########################################################################
        # Menü 5 Hilfe
        MenuHelp = tk.Menu(menubar, tearoff=False)
        # MenuHelp.add_command(label="Hilfe", command=lambda: False, underline=0)
        MenuHelp.add_command(label=STR_TABLE['keybind'][self.language],
                             command=lambda: self._open_settings_window('keybinds'),
                             underline=0)
        MenuHelp.add_separator()
        MenuHelp.add_command(label=STR_TABLE['about'][self.language],
                             command=lambda: self._open_settings_window('about'),
                             underline=0)
        menubar.add_cascade(label=STR_TABLE['help'][self.language], menu=MenuHelp, underline=0)

    def _init_btn(self, frame):
        # btn_upper_frame = tk.Frame(frame)
        # btn_upper_frame.pack(anchor='w', fill=tk.X, expand=True)
        self._conn_btn = tk.Button(frame,
                                   text="Connect",
                                   bg="green",
                                   width=8,
                                   command=self.open_new_conn_win,
                                   relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                   highlightthickness=0,
                                   )
        self._conn_btn.pack(side=tk.LEFT)

        self._mon_btn = tk.Button(frame,
                                  text="Monitor",
                                  bg="yellow",
                                  width=8,
                                  command=lambda: self.switch_channel(0),
                                  relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                  highlightthickness=0,
                                  )
        self._mon_btn.pack(side=tk.LEFT, padx=2)

    def _init_ch_btn_frame(self, root_frame):
        btn_font = ("fixedsys", 8,)
        ch_btn_frame = ttk.Frame(root_frame, )
        ch_btn_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for ch_nr in list(range(1,11)):
            ch_text_var = tk.StringVar(self.main_win, value=str(ch_nr))
            ch_btn      = tk.Button(ch_btn_frame,
                               font=btn_font,
                               textvariable=ch_text_var,
                               bg="red",
                               #command=lambda: self.switch_channel(int(f"{ch_nr}")),
                               relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                               highlightthickness=0,
                               )
            ch_btn.pack( side=tk.LEFT, anchor="center", expand=True, fill=tk.X)
            self._con_btn_dict[ch_nr] = ch_btn, ch_text_var

        self._con_btn_dict[1][0].configure(command=lambda: self.switch_channel(1))
        self._con_btn_dict[2][0].configure(command=lambda: self.switch_channel(2))
        self._con_btn_dict[3][0].configure(command=lambda: self.switch_channel(3))
        self._con_btn_dict[4][0].configure(command=lambda: self.switch_channel(4))
        self._con_btn_dict[5][0].configure(command=lambda: self.switch_channel(5))
        self._con_btn_dict[6][0].configure(command=lambda: self.switch_channel(6))
        self._con_btn_dict[7][0].configure(command=lambda: self.switch_channel(7))
        self._con_btn_dict[8][0].configure(command=lambda: self.switch_channel(8))
        self._con_btn_dict[9][0].configure(command=lambda: self.switch_channel(9))
        self._con_btn_dict[10][0].configure(command=lambda: self.switch_channel(10))

    def _init_TXT_frame_up(self):
        guiCFG        = POPT_CFG.load_guiPARM_main()
        text_frame    = ttk.Frame(self._TXT_upper_frame)
        self._inp_txt = tk.Text(text_frame,
                                                  background=guiCFG.get('gui_cfg_vor_bg_col', 'black'),
                                                  foreground=guiCFG.get('gui_cfg_vor_col', 'white'),
                                                  font=(FONT, self.text_size),
                                                  insertbackground=TXT_INP_CURSOR_CLR,
                                                  height=30,
                                                  width=5,
                                                  bd=0,
                                                  relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                                  highlightthickness=0,
                                                  )
        self._inp_txt.tag_config("send",
                                 foreground=guiCFG.get('gui_cfg_vor_tx_col', '#25db04'),
                                 background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        inp_scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self._inp_txt.yview
        )
        self._inp_txt.pack(side=tk.LEFT, fill=tk.BOTH,  expand=True)
        inp_scrollbar.pack(side=tk.LEFT, fill=tk.Y,     expand=False)
        self._inp_txt.config(yscrollcommand=inp_scrollbar.set)
        # self.in_txt_win.insert(tk.END, "Inp")
        ##############
        # Status Frame
        status_frame = ttk.Frame(self._TXT_upper_frame, height=18)
        status_frame.pack( side=tk.BOTTOM, fill=tk.X   , expand=False)
        text_frame.pack(   side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        name_f      = ttk.Frame(status_frame, width=60)
        stat_f      = ttk.Frame(status_frame, width=40)
        nack_f      = ttk.Frame(status_frame, width=40)
        vsvr_f      = ttk.Frame(status_frame, width=40)
        n2_f        = ttk.Frame(status_frame, width=20)
        t1_f        = ttk.Frame(status_frame, width=20)
        t2_f        = ttk.Frame(status_frame, width=20)
        rtt_f       = ttk.Frame(status_frame, width=20)
        t3_f        = ttk.Frame(status_frame, width=20)
        rx_beep_f   = ttk.Frame(status_frame, width=50)
        ts_f        = ttk.Frame(status_frame, width=20)

        name_f.pack(side=tk.LEFT, expand=True)
        stat_f.pack(side=tk.LEFT, expand=False)
        nack_f.pack(side=tk.LEFT, expand=False)
        vsvr_f.pack(side=tk.LEFT, expand=True)
        n2_f.pack(side=tk.LEFT, expand=True)
        t1_f.pack(side=tk.LEFT, expand=True)
        t2_f.pack(side=tk.LEFT, expand=True)
        rtt_f.pack(side=tk.LEFT, expand=True)
        t3_f.pack(side=tk.LEFT, expand=True)
        rx_beep_f.pack(side=tk.LEFT, expand=False)
        ts_f.pack(side=tk.LEFT, expand=False)

        fg, bg = self._get_colorMap()
        tk.Label(name_f,
                textvariable=self._status_name_var,
                font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                foreground=fg,
                bg=bg,
                width=10
              ).pack(side=tk.LEFT, anchor='w')

        self._status_status = tk.Label(stat_f,
                                    textvariable=self._status_status_var,
                                    font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                    bg=bg,
                                    foreground=STAT_BAR_TXT_CLR,
                                    width=8
                                    )
        self._status_status.pack(side=tk.LEFT, anchor='w', expand=True)

        self._status_unack = tk.Label(nack_f,
                                    textvariable=self._status_unack_var,
                                    foreground=STAT_BAR_TXT_CLR,
                                    font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                    bg=bg,
                                    width=8
                                   )
        self._status_unack.pack(side=tk.LEFT, anchor='w', expand=True)

        tk.Label(vsvr_f,
              textvariable=self._status_vs_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side=tk.LEFT, anchor='w')

        self._status_n2 = tk.Label(n2_f,
                                textvariable=self._status_n2_var,
                                font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                bg=bg,
                                foreground=fg,
                                width=5
                                )
        self._status_n2.pack(side=tk.LEFT, anchor='w')

        tk.Label(t1_f,
              textvariable=self._status_t1_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side=tk.LEFT, anchor='w')
        # PARM T2
        tk.Label(t2_f,
              textvariable=self._status_t2_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side=tk.LEFT, anchor='w')
        # RTT
        tk.Label(rtt_f,
              textvariable=self._status_rtt_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side=tk.LEFT, anchor='w')

        tk.Label(t3_f,
              textvariable=self._status_t3_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side=tk.LEFT, anchor='w')
        # Checkbox RX-BEEP
        self._rx_beep_box = tk.Checkbutton(rx_beep_f,
                                        text="RX-BEEP",
                                        bg=bg,
                                        font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                        activebackground=bg,
                                        background=bg,
                                        borderwidth=0,
                                        onvalue=1, offvalue=0,
                                        foreground=fg,
                                        variable=self._rx_beep_var,
                                        command=self._chk_rx_beep,
                                           border=False,
                                           relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                           highlightthickness=0,
                                        )
        self._rx_beep_box.pack(side=tk.LEFT, anchor='w')
        # TODO Checkbox Time Stamp
        self._ts_box_box = ttk.Checkbutton(ts_f,
                                       text="T-S",
                                       #font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                       #bg=bg,
                                       #borderwidth=0,
                                       #activebackground=bg,
                                       onvalue=1, offvalue=0,
                                       #foreground=fg,
                                       variable=self._ts_box_var,
                                       command=self._chk_timestamp,
                                       state='disabled'
                                       )
        # self._ts_box_box.pack(side=tk.LEFT, anchor='w') # TODO

    def _init_TXT_frame_mid(self):
        text_frame = ttk.Frame(self._TXT_mid_frame)
        stat_frame = ttk.Frame(self._TXT_mid_frame)
        stat_frame.pack(side=tk.BOTTOM, fill=tk.X,    expand=False)
        text_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self._out_txt = tk.Text(text_frame,
                              background=DEF_QSO_SYSMSG_BG,
                              foreground=DEF_QSO_SYSMSG_FG,
                              font=(FONT, self.text_size),
                              height=30,
                              width=5,
                              bd=0,
                              borderwidth=0,
                              state="disabled",
                                relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                highlightthickness=0,

                                )
        # self._out_txt.tag_config("input", foreground="white")
        out_scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self._out_txt.yview
        )
        self._out_txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        out_scrollbar.pack(side=tk.LEFT, fill=tk.Y,    expand=False)
        self._out_txt.config(yscrollcommand=out_scrollbar.set)
        # Status bar
        name_f = ttk.Frame(stat_frame)
        qth_f  = ttk.Frame(stat_frame)
        loc_f  = ttk.Frame(stat_frame)
        typ_f  =  tk.Frame(stat_frame, bg="#0ed8c3")
        sw_f   =  tk.Frame(stat_frame, bg="#ffd444")
        stat_f = ttk.Frame(stat_frame)
        time_f = ttk.Frame(stat_frame)
        enc_f  = ttk.Frame(stat_frame)

        name_f.pack(side=tk.LEFT, expand=True,  anchor="center")
        qth_f.pack( side=tk.LEFT, expand=True,  anchor="center")
        loc_f.pack( side=tk.LEFT, expand=True,  anchor="center", padx=5)
        typ_f.pack( side=tk.LEFT, expand=True,  anchor="center", fill=tk.X)
        sw_f.pack(  side=tk.LEFT, expand=True,  anchor="center", fill=tk.X)
        stat_f.pack(side=tk.LEFT, expand=False, anchor="center")
        time_f.pack(side=tk.LEFT, expand=False, anchor="center", padx=7)
        enc_f.pack( side=tk.LEFT, expand=True,  anchor="center", fill=tk.X)

        fg, bg = self._get_colorMap()

        name_label = ttk.Label(name_f,
                              textvariable=self.stat_info_name_var,
                              # bg=STAT_BAR_CLR,
                              #height=1,
                              borderwidth=0,
                              border=0,
                              #fg=fg,
                              #bg=bg,
                              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS, 'bold')

                              )
        name_label.pack()
        name_label.bind('<Button-1>', self.open_user_db_win)
        qth_label = tk.Label(qth_f,
                             textvariable=self.stat_info_qth_var,
                             bg=bg,
                             fg=fg,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS)
                             )
        qth_label.bind('<Button-1>', self.open_user_db_win)
        qth_label.pack()
        loc_label = tk.Label(loc_f,
                             textvariable=self.stat_info_loc_var,
                             bg=bg,
                             fg=fg,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS)
                             )
        loc_label.bind('<Button-1>', self.open_user_db_win)
        loc_label.pack()

        opt = list(STATION_TYPS)
        stat_typ = tk.OptionMenu(
            typ_f,
            self.stat_info_typ_var,
            *opt,
            command=self._set_stat_typ,
        )
        stat_typ.configure(
            background="#0ed8c3",
            fg=STAT_BAR_TXT_CLR,
            #width=8,
            height=1,
            borderwidth=0,
            border=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,),
            relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
            highlightthickness=0,
        )
        stat_typ.pack(fill=tk.X, expand=True, padx=6)

        tk.Label(sw_f,
                 textvariable=self.stat_info_sw_var,
                 #width=18,
                 bg="#ffd444",
                 # fg="red3",
                 height=1,
                 borderwidth=0,
                 border=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                 highlightthickness=0,
                 ).pack(fill=tk.X, expand=True, padx=6)

        self.status_label = tk.Label(stat_f,
                                     textvariable=self.stat_info_status_var,
                                     bg=STAT_BAR_CLR,
                                     fg="red3",
                                     height=1,
                                     borderwidth=0,
                                     border=0,
                                     font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,),
                                     relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                     highlightthickness=0,
                                     width=7
                                     )
        self.status_label.pack()
        self.status_label.bind('<Button-1>', self.do_priv)

        ttk.Label(time_f,
                 textvariable=self.stat_info_timer_var,
                 #width=6,
                 # height=1,
                 borderwidth=0,
                 border=0,
                 # bg="steel blue",
                 # fg="red3",
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,)
                 ).pack(fill=tk.X, expand=True)
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            enc_f,
            self.stat_info_encoding_var,
            *opt,
            command=self._change_txt_encoding
        )
        txt_encoding_ent.configure(
            background="steel blue",
            height=1,
            width=8,
            borderwidth=0,
            border=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - 1,),
            relief = "flat",  # Flache Optik für ttk-ähnliches Aussehen
            highlightthickness = 0,
        )
        txt_encoding_ent.pack(fill=tk.X, expand=True)

    def _init_TXT_frame_low(self):
        mon_frame = ttk.Frame(self._TXT_lower_frame)
        mon_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self._mon_txt = tk.Text(mon_frame,
                              background=MON_SYS_MSG_CLR_BG,
                              foreground=MON_SYS_MSG_CLR_BG,
                              font=(FONT, self.text_size),
                              height=30,
                              width=5,
                              bd=0,
                              borderwidth=0,
                              state="disabled",
                              relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                              highlightthickness=0,
                              )
        mon_scrollbar = ttk.Scrollbar(
            mon_frame,
            orient=tk.VERTICAL,
            command=self._mon_txt.yview
        )
        self._mon_txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        mon_scrollbar.pack(side=tk.LEFT, fill=tk.Y,    expand=False)
        self._mon_txt.config(yscrollcommand=mon_scrollbar.set)
    #######################################
    # Text Tags
    def set_text_tags(self):
        self._all_tag_calls = []
        all_stat_cfg = POPT_CFG.get_stat_CFGs()
        for call in list(all_stat_cfg.keys()):
            stat_cfg = all_stat_cfg[call]
            tx_fg = stat_cfg.get('stat_parm_qso_col_text_tx', DEF_STAT_QSO_TX_COL)
            tx_bg = stat_cfg.get('stat_parm_qso_col_bg', DEF_STAT_QSO_BG_COL)

            rx_fg = stat_cfg.get('stat_parm_qso_col_text_rx', DEF_STAT_QSO_RX_COL)

            tx_tag = 'TX-' + str(call)
            rx_tag = 'RX-' + str(call)
            self._all_tag_calls.append(str(call))

            self._out_txt.configure(state="normal")
            self._out_txt.tag_config(tx_tag,
                                     foreground=tx_fg,
                                     background=tx_bg,
                                     selectbackground=tx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._out_txt.tag_config(rx_tag,
                                     foreground=rx_fg,
                                     background=tx_bg,
                                     selectbackground=rx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._out_txt.tag_config('SYS-MSG',
                                     foreground=DEF_QSO_SYSMSG_FG,
                                     background=DEF_QSO_SYSMSG_BG,
                                     selectbackground=DEF_QSO_SYSMSG_FG,
                                     selectforeground=DEF_QSO_SYSMSG_BG,
                                     )
            self._out_txt.tag_config('TX-NOCALL',
                                     foreground='#ffffff',
                                     background='#000000',
                                     selectbackground='#ffffff',
                                     selectforeground='#000000',
                                     )
            self._out_txt.tag_config('RX-NOCALL',
                                     foreground='#000000',
                                     background='#ffffff',
                                     selectbackground='#000000',
                                     selectforeground='#ffffff',
                                     )
            self._out_txt.configure(state="disabled")

            self._mon_txt.configure(state="normal")

        # Monitor Tags
        all_port = self._port_handler.ax25_ports
        for port_id in all_port.keys():
            tag_tx = f"tx{port_id}"
            tag_rx = f"rx{port_id}"
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_id)
            tx_fg = port_cfg.get('parm_mon_clr_tx', DEF_PORT_MON_TX_COL)
            tx_bg = port_cfg.get('parm_mon_clr_bg', DEF_PORT_MON_BG_COL)
            rx_fg = port_cfg.get('parm_mon_clr_rx', DEF_PORT_MON_RX_COL)
            self._mon_txt.tag_config(tag_tx, foreground=tx_fg,
                                     background=tx_bg,
                                     selectbackground=tx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._mon_txt.tag_config(tag_rx, foreground=rx_fg,
                                     background=tx_bg,
                                     selectbackground=rx_fg,
                                     selectforeground=tx_bg,
                                     )
        self._mon_txt.tag_config("sys-msg", foreground=MON_SYS_MSG_CLR_FG,
                                 background=MON_SYS_MSG_CLR_BG)
        self._mon_txt.configure(state="disabled")
        guiCFG = POPT_CFG.load_guiPARM_main()
        self._inp_txt.configure(foreground=guiCFG.get('gui_cfg_vor_col', 'white'), background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        self._inp_txt.tag_config("send", foreground=guiCFG.get('gui_cfg_vor_tx_col', '#25db04'),
                                 background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        self.own_qth = guiCFG.get('gui_cfg_qth', '')
        self.own_loc = guiCFG.get('gui_cfg_locator', '')
        self.language = POPT_CFG.get_guiCFG_language()

    #######################################
    # KEYBIND Stuff
    def _set_binds(self):
        self._inp_txt.bind("<ButtonRelease-1>", self._on_click_inp_txt)
        self._inp_txt.bind("<KeyRelease>", self._on_key_release_inp_txt)

    def _set_keybinds(self):
        self.main_win.unbind("<Key-F10>")
        self.main_win.unbind("<KeyPress-F10>")
        # self.main_win.bind("<KeyPress>",lambda event: self.callback(event))
        # lambda event: print(f"{event.keysym} - {event.keycode}\n {type(event.keysym)} - {type(event.keycode)}
        #####################
        # F-TEXT
        if is_linux():
            r = 13
        else:
            r = 11
        for fi in range(1, r):
            self.main_win.bind(f'<Shift-F{fi}>', self._insert_ftext)
        #####################
        self.main_win.bind('<F1>', lambda event: self.switch_channel(1))
        self.main_win.bind('<F2>', lambda event: self.switch_channel(2))
        self.main_win.bind('<F3>', lambda event: self.switch_channel(3))
        self.main_win.bind('<F4>', lambda event: self.switch_channel(4))
        self.main_win.bind('<F5>', lambda event: self.switch_channel(5))
        self.main_win.bind('<F6>', lambda event: self.switch_channel(6))
        self.main_win.bind('<F7>', lambda event: self.switch_channel(7))
        self.main_win.bind('<F8>', lambda event: self.switch_channel(8))
        self.main_win.bind('<F9>', lambda event: self.switch_channel(9))
        self.main_win.bind('<F10>', lambda event: self.switch_channel(10))
        self.main_win.bind('<F12>', lambda event: self.switch_channel(0))
        self.main_win.bind('<Return>', self._snd_text)
        self.main_win.bind('<KeyRelease-Return>', self._release_return)
        self.main_win.bind('<Shift-KeyPress-Return>', self._shift_return)
        self.main_win.bind('<KeyRelease-Left>', self._arrow_keys)
        self.main_win.bind('<KeyRelease-Right>', self._arrow_keys)
        self.main_win.bind('<KeyRelease-Up>', self._arrow_keys)
        self.main_win.bind('<KeyRelease-Down>', self._arrow_keys)
        # self.main_win.bind('<KP_Enter>', self.snd_text)
        self.main_win.bind('<Alt-c>', lambda event: self.open_new_conn_win())
        self.main_win.bind('<Escape>', lambda event: self.open_new_conn_win())
        self.main_win.bind('<Alt-d>', lambda event: self._disco_conn())
        self.main_win.bind('<Control-c>', lambda event: self._copy_select())
        self.main_win.bind('<Control-x>', lambda event: self._cut_select())
        # self.main_win.bind('<Control-v>', lambda event: self.clipboard_past())
        self.main_win.bind('<Control-a>', lambda event: self._select_all())
        self.main_win.bind('<Control-plus>', lambda event: self._increase_textsize())
        self.main_win.bind('<Control-minus>', lambda event: self._decrease_textsize())
        # self.main_win.bind('<Control-Right>', lambda event: self._text_win_bigger())
        # self.main_win.bind('<Control-Left>', lambda event: self._text_win_smaller())

        self.main_win.bind('<Key>', lambda event: self._any_key(event))

    def _any_key(self, event: tk.Event):
        if event.keycode == 104:  # Numpad Enter
            self._snd_text(event)

    def _arrow_keys(self, event=None):
        self._on_click_inp_txt()

    def _shift_return(self, event=None):
        pass

    def _release_return(self, event=None):
        pass

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
        ch_enc = self.stat_info_encoding_var.get()
        if any((ch_enc == enc, not ch_enc)):
            text = text.decode(enc, 'ignore')
        else:
            text = text.decode(ch_enc, 'ignore')
        conn = self.get_conn()
        text = replace_StringVARS(input_string=text, port_handler=self.get_PH_manGUI(), connection=conn)
        text = zeilenumbruch_lines(text)
        self._inp_txt.insert(tk.INSERT, text)
        self.see_end_inp_win()
        return

    ##########################
    # Start Message in Monitor
    def _monitor_start_msg(self):
        # tmp_lang = int(self.language)
        # self.language = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        SOUND.sprech(random.choice(WELCOME_SPEECH))
        # self.language = int(tmp_lang)
        ban = POPT_BANNER.format(VER)
        tmp = ban.split('\r')
        for el in tmp:
            self.sysMsg_to_monitor(el)
        self.sysMsg_to_monitor('Python Other Packet Terminal ' + VER)
        for stat in POPT_CFG.get_stat_CFG_keys():
            self.sysMsg_to_monitor('Info: Stationsdaten {} erfolgreich geladen.'.format(stat))
        all_ports = self._port_handler.ax25_ports
        for port_k in all_ports.keys():
            msg = 'konnte nicht initialisiert werden!'
            if all_ports[port_k].device_is_running:
                msg = 'erfolgreich initialisiert.'
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_k)
            self.sysMsg_to_monitor('Info: Port {}: {} - {} {}'
                                   .format(port_k,
                                           port_cfg.get('parm_PortName', ''),
                                           port_cfg.get('parm_PortTyp', ''),
                                           msg
                                           ))
            self.sysMsg_to_monitor('Info: Port {}: Parameter: {} | {}'
                                   .format(port_k,
                                           port_cfg.get('parm_PortParm', ('', 0))[0],
                                           port_cfg.get('parm_PortParm', ('', 0))[1],
                                           ))

    # END Init Stuff
    ######################################################################

    ######################################################################
    # GUI Sizing/Formatting Stuff
    def _increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        self._inp_txt.configure(font=(FONT, self.text_size), )
        self._out_txt.configure(font=(FONT, self.text_size), )
        self._mon_txt.configure(font=(FONT, self.text_size), )

    def _decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self._inp_txt.configure(font=(FONT, self.text_size), )
        self._out_txt.configure(font=(FONT, self.text_size), )
        self._mon_txt.configure(font=(FONT, self.text_size), )

    ##########################
    # Clipboard Stuff
    def _copy_select(self):
        if self._out_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._out_txt.selection_get())
            self._out_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._inp_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._inp_txt.selection_get())
            self._inp_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._mon_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._mon_txt.selection_get())
            self._mon_txt.tag_remove(tk.SEL, "1.0", tk.END)

    def _cut_select(self):
        if self._out_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._out_txt.selection_get())
            self._out_txt.delete('sel.first', 'sel.last')

    def _clipboard_past(self):
        try:
            clp_brd = self.main_win.clipboard_get()
        except tk.TclError:
            logger.warning("GUI: TclError Clipboard no STR")
            return

        if clp_brd:
            self._inp_txt.insert(tk.END, clp_brd)

    def _select_all(self):
        self._inp_txt.tag_add(tk.SEL, "1.0", tk.END)
        self._inp_txt.mark_set(tk.INSERT, "1.0")
        self._inp_txt.see(tk.INSERT)

    ##########################
    # Pre-write Text Stuff
    def _insert_fm_file(self):
        data = open_file_dialog()
        if not data:
            return
        ch_enc = self.stat_info_encoding_var.get()
        if not ch_enc:
            data = data.decode('UTF-8', 'ignore')
        else:
            data = data.decode(ch_enc, 'ignore')
        data = zeilenumbruch_lines(data)
        self._inp_txt.insert(tk.INSERT, data)
        self.see_end_inp_win()
        return

    def _save_to_file(self):
        data = self._out_txt.get('1.0', tk.END)
        # FIXME Codec : UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1090-1097: ordinal not in range(256)
        save_file_dialog(data)

    ##########################
    # Monitor Text Stuff
    def _clear_monitor_data(self):
        self._mon_txt.configure(state='normal')
        self._mon_txt.delete('1.0', tk.END)
        self._mon_txt.configure(state='disabled')

    def _save_monitor_to_file(self):
        data = self._mon_txt.get('1.0', tk.END)
        # FIXME Codec : UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1090-1097: ordinal not in range(256)
        save_file_dialog(data)

    # END GUI Sizing/Formatting Stuff
    ######################################################################

    ######################################################################
    # Channel Vars
    def get_conn(self, con_ind: int = 0):
        # TODO Call just if necessary
        # TODO current Chanel.connection to var, prevent unnecessary calls
        if not con_ind:
            con_ind = int(self.channel_index)
        all_conn = self._port_handler.get_all_connections()
        if con_ind in all_conn.keys():
            return all_conn[con_ind]
        return None

    def get_ch_var(self, ch_index=0):
        if ch_index:
            if ch_index not in self._channel_vars.keys():
                self._channel_vars[ch_index] = ChVars()
            return self._channel_vars[ch_index]

        if self.channel_index not in self._channel_vars.keys():
            self._channel_vars[self.channel_index] = ChVars()
        return self._channel_vars[self.channel_index]

    def set_var_to_all_ch_param(self):
        for ch_id in self._channel_vars.keys():
            ch_vars = self.get_ch_var(ch_index=ch_id)
            if not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''

    def clear_channel_vars(self):
        self._out_txt.configure(state='normal')
        self._out_txt.delete('1.0', tk.END)
        self._out_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]

        self._channel_vars[self.channel_index] = ChVars()
        self._update_qso_Vars()

    def _clear_all_Channel_vars(self):
        self._out_txt.configure(state='normal')
        self._out_txt.delete('1.0', tk.END)
        self._out_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]
        for ch_id in self._channel_vars.keys():
            self._channel_vars[ch_id] = ChVars()
        self._update_qso_Vars()

    ######################################################################
    # Sound TODO !!!
    def _kanal_switch(self):
        """ Triggered on CH BTN Click """
        threading.Thread(target=self._kanal_switch_sprech_th).start()

    def _kanal_switch_sprech_th(self):
        conn = self.get_conn(self.channel_index)
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        if conn is not None:
            if ch_vars.t2speech \
                    and ch_vars.t2speech_buf:
                # to_speech = 'Kanal {} .'.format(self.channel_index)
                # to_speech += '{} .'.format(conn.to_call_str)
                to_speech = str(ch_vars.t2speech_buf)
                if SOUND.sprech(to_speech):
                    ch_vars.t2speech_buf = ''

            else:
                ch_vars.t2speech_buf = ''
                SOUND.sprech('{} {} . {} .'.format(STR_TABLE['channel'][self.language],
                                                   self.channel_index,
                                                   conn.to_call_str))

        else:
            if not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''
                SOUND.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            elif ch_vars.t2speech_buf:
                if SOUND.sprech(ch_vars.t2speech_buf):
                    ch_vars.t2speech_buf = ''
                else:
                    SOUND.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))
            else:
                SOUND.sprech('{} {} .'.format(STR_TABLE['channel'][self.language], self.channel_index))

    def _check_sprech_ch_buf(self):
        conn = self.get_conn(self.channel_index)
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        if conn is not None:
            if ch_vars.t2speech and ch_vars.t2speech_buf:
                to_speech = str(ch_vars.t2speech_buf)
                if SOUND.master_sprech_on and SOUND.master_sound_on:
                    if SOUND.sprech(to_speech):
                        ch_vars.t2speech_buf = ''
                else:
                    ch_vars.t2speech_buf = ''

            elif not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''
        else:
            ch_vars.t2speech_buf = ''

    def _rx_beep_sound(self):
        for k in self._channel_vars.keys():
            if 0 < k < SERVICE_CH_START:
                ch_vars = self.get_ch_var(ch_index=k)
                if ch_vars.rx_beep_cooldown < time.time():
                    ch_vars.rx_beep_cooldown = time.time() + self._parm_rx_beep_cooldown
                    if ch_vars.rx_beep_opt:
                        if ch_vars.rx_beep_tr:
                            ch_vars.rx_beep_tr = False
                            SOUND.sound_play(self._root_dir + CFG_sound_RX_BEEP, False)

    # Sound
    ######################################################################
    #
    ######################################################################
    # TASKER
    def _tasker(self):  # MAINLOOP
        if self._quit:
            self._tasker_quit()
        else:
            prio = self._tasker_prio()
            if not self._tasker_05_sec():
                if not self._tasker_1_sec():
                    if not self._tasker_5_sec() and not prio:
                        self.main_win.update_idletasks()
            # self._tasker_tester()
        self.main_win.after(self._loop_delay, self._tasker)

    def _tasker_quit(self):
        if self._port_handler.check_all_ports_closed():
            self._port_handler.close_gui()
            logger.info('GUI: Closing GUI: _tasker_quit Done.')

    def _tasker_prio(self):
        """ Prio Tasks every Irritation flip flop """
        """
        if self._prio_task_flip:
            
        else:
           
        self._prio_task_flip = not self._prio_task_flip
        """
        return self._monitor_task()

    def _tasker_05_sec(self):
        """ 0.5 Sec """
        if time.time() > self._non_prio_task_timer:
            #####################
            # self._aprs_task()
            # self._monitor_task()
            self._dualPort_monitor_task()
            self._update_qso_win()
            self._SideFrame_tasker()
            self._update_status_win()
            self._AlarmIcon_tasker05()
            #####################
            self._flip05 = not self._flip05
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            return True
        return False

    def _tasker_1_sec(self):
        """ 1 Sec """
        if time.time() > self._non_non_prio_task_timer:
            #####################
            self._update_stat_info_conn_timer()
            self._update_ft_info()
            self._AlarmIcon_tasker1()
            if self._ch_alarm:
                self._ch_btn_status_update()
            if hasattr(self.settings_win, 'tasker'):
                self.settings_win.tasker()
            if hasattr(self.BBS_fwd_q_list, 'tasker'):
                # TODO 2 Sec Tasker
                self.BBS_fwd_q_list.tasker()
            if SOUND.master_sound_on:
                # TODO Sound Task
                self._rx_beep_sound()
                if SOUND.master_sprech_on:
                    self._check_sprech_ch_buf()
            """
            if self.MSG_Center is not None:
                self.MSG_Center.tasker()
            """
            """
            if self.aprs_mon_win is not None:
                self.aprs_mon_win.tasker()
            """
            #####################
            self._non_non_prio_task_timer = time.time() + self._parm_non_non_prio_task_timer
            return True
        return False

    def _tasker_5_sec(self):
        """ 5 Sec """
        if time.time() > self._non_non_non_prio_task_timer:
            if self._init_state < 2:
                self._init_state += 1
                if self._init_state == 2:
                    self.reset_diesel()
            #####################
            self._update_bw_mon()
            self._aprs_wx_tree_task()
            #####################
            self._non_non_non_prio_task_timer = time.time() + self._parm_non_non_non_prio_task_timer
            return True
        return False

    # END TASKER
    ######################################################################
    def _aprs_wx_tree_task(self):
        if self._port_handler.get_aprs_ais() is not None:
            self._port_handler.get_aprs_ais().aprs_wx_tree_task()

    def _AlarmIcon_tasker05(self):
        if self._Alarm_Frame:
            self._Alarm_Frame.AlarmIcon_tasker05()

    def _AlarmIcon_tasker1(self):
        if self._Alarm_Frame:
            self._Alarm_Frame.AlarmIcon_tasker1()

    def _SideFrame_tasker(self):
        if self._flip05:
            self.tabbed_sideFrame.tasker()
            self.tabbed_sideFrame.on_ch_stat_change()
        else:
            self.tabbed_sideFrame2.tasker()
            self.tabbed_sideFrame2.on_ch_stat_change()

    ###############################################################
    # QSO WIN

    def _update_qso_win(self):
        all_conn = self._port_handler.get_all_connections()
        all_conn_ch_index = list(all_conn.keys())
        tr = False
        for channel in all_conn_ch_index:
            conn = all_conn[channel]
            if conn:
                if self._update_qso(conn):
                    tr = True
        if tr:
            self.ch_status_update()

    def _update_qso(self, conn):
        if not conn:
            return False
        if conn.ft_obj:
            # self.ch_status_update()
            return False
        if conn.rx_tx_buf_guiData:
            self._update_qso_spooler(conn)
            # self.ch_status_update()
            return True
        return False

    def _update_qso_spooler(self, conn):
        gui_buf = list(conn.rx_tx_buf_guiData)
        conn.rx_tx_buf_guiData = list(conn.rx_tx_buf_guiData[len(gui_buf):])
        for qso_data in gui_buf:
            if qso_data[0] == 'TX':
                self._update_qso_tx(conn, qso_data[1])
            else:
                self._update_qso_rx(conn, qso_data[1])

    def _update_qso_tx(self, conn, data):
        txt_enc = 'UTF-8'
        if conn.user_db_ent:
            txt_enc = str(conn.user_db_ent.Encoding)
        my_call_str = str(conn.my_call_str)
        my_call = str(conn.my_call)
        inp = data.decode(txt_enc, 'ignore').replace('\r', '\n')
        inp = tk_filter_bad_chars(inp)

        Ch_var = self.get_ch_var(ch_index=conn.ch_index)
        Ch_var.output_win += inp
        if my_call_str in self._all_tag_calls:
            tag_name_tx = f'TX-{my_call_str}'
            Ch_var.last_tag_name = my_call_str
        elif my_call in self._all_tag_calls:
            tag_name_tx = f'TX-{my_call}'
            Ch_var.last_tag_name = my_call
        else:
            tag_name_tx = f'TX-{Ch_var.last_tag_name}'

        if self.channel_index == conn.ch_index:
            self._out_txt.configure(state="normal")
            ind = self._out_txt.index('end-1c')
            self._out_txt.insert('end', inp)
            ind2 = self._out_txt.index('end-1c')
            if tag_name_tx:
                self._out_txt.tag_add(tag_name_tx, ind, ind2)
            self._out_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            # TODO Autoscroll
            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
                self.see_end_qso_win()
        else:
            if tag_name_tx:
                Ch_var.new_tags.append(
                    (tag_name_tx, len(inp))
                )

    def _update_qso_rx(self, conn, data):
        txt_enc = 'UTF-8'
        if conn.user_db_ent:
            txt_enc = str(conn.user_db_ent.Encoding)
        my_call_str = str(conn.my_call_str)
        my_call = str(conn.my_call)
        Ch_var = self.get_ch_var(ch_index=conn.ch_index)
        out = data.decode(txt_enc, 'ignore')
        out = out.replace('\r', '\n')
        out = tk_filter_bad_chars(out)

        # Write RX Date to Window/Channel Buffer
        Ch_var.output_win += out
        if my_call_str in self._all_tag_calls:
            tag_name_rx = f'RX-{my_call_str}'
            Ch_var.last_tag_name = my_call_str
        elif my_call in self._all_tag_calls:
            tag_name_rx = f'RX-{my_call}'
            Ch_var.last_tag_name = my_call
        else:
            logger.error('Conn: _update_qso_rx: no Tagname')
            print('Conn: _update_qso_rx: no Tagname')
            print(f"Conn: last Tag: {Ch_var.last_tag_name}")
            logger.error(f"Conn: last Tag: {Ch_var.last_tag_name}")
            tag_name_rx = f'RX-{Ch_var.last_tag_name}'

        if self.channel_index == conn.ch_index:
            if Ch_var.t2speech:
                Ch_var.t2speech_buf += out.replace('\n', '')

            self._out_txt.configure(state="normal")
            # configuring a tag called start
            ind = self._out_txt.index('end-1c')
            self._out_txt.insert('end', out)
            ind2 = self._out_txt.index('end-1c')
            if tag_name_rx:
                self._out_txt.tag_add(tag_name_rx, ind, ind2)

            self._out_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            # TODO Autoscroll
            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
                self.see_end_qso_win()
        else:
            Ch_var.new_data_tr = True
            if Ch_var.t2speech:
                # TODO ?????????????????????????????????????????????
                Ch_var.t2speech_buf += '{} {} . {} . {}'.format(
                    STR_TABLE['channel'][self.language],
                    conn.ch_index,
                    conn.to_call_str,
                    out.replace('\n', '')
                )
            if tag_name_rx:
                Ch_var.new_tags.append(
                    (tag_name_rx, len(out))
                )
        Ch_var.rx_beep_tr = True

    def _update_qso_Vars(self):
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        bg = self._get_colorMap()[1]
        ch_vars.new_data_tr = False
        ch_vars.rx_beep_tr  = False

        self._out_txt.configure(state="normal")

        self._out_txt.delete('1.0', tk.END)
        self._out_txt.insert(tk.END, ch_vars.output_win)
        self._out_txt.configure(state="disabled")
        self._out_txt.see(tk.END)

        self._inp_txt.delete('1.0', tk.END)
        self._inp_txt.insert(tk.END, ch_vars.input_win[:-1])
        set_all_tags(self._inp_txt, ch_vars.input_win_tags)
        set_all_tags(self._out_txt, ch_vars.output_win_tags)
        set_new_tags(self._out_txt, ch_vars.new_tags)
        ch_vars.new_tags = []
        self._inp_txt.mark_set("insert", ch_vars.input_win_cursor_index)
        self._inp_txt.see(tk.END)

        # self.main_class: gui.guiMainNew.TkMainWin
        if ch_vars.rx_beep_opt and self.channel_index:
            self._rx_beep_box.select()
            self._rx_beep_box.configure(bg='green')
        else:
            self._rx_beep_box.deselect()
            self._rx_beep_box.configure(bg=bg)

        if ch_vars.timestamp_opt and self.channel_index:
            self._ts_box_var.set(True)
            #self._ts_box_box.configure(bg='green')
        else:
            self._ts_box_var.set(False)
            #self._ts_box_box.configure(bg=bg)

    def sysMsg_to_qso(self, data, ch_index):
        # FIXME: Wait for spooler (async)
        if not data:
            return
        if 1 > ch_index > SERVICE_CH_START - 1:
            return False
        data = data.replace('\r', '')
        data = f"\n    <{conv_time_DE_str()}>\n" + data + '\n'
        data = tk_filter_bad_chars(data)
        ch_vars = self.get_ch_var(ch_index=ch_index)
        tag_name = 'SYS-MSG'
        ch_vars.output_win += data
        if self.channel_index == ch_index:
            tr = False
            if float(self._out_txt.index(tk.END)) - float(self._out_txt.index("@0,0")) < 22:
                tr = True
            self._out_txt.configure(state="normal")

            ind = self._out_txt.index(tk.INSERT)
            self._out_txt.insert('end', data)
            ind2 = self._out_txt.index(tk.INSERT)
            self._out_txt.tag_add(tag_name, ind, ind2)
            self._out_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            if tr or self.get_ch_var().autoscroll:
                self.see_end_qso_win()

        else:
            ch_vars.new_tags.append(
                (tag_name, len(data))
            )
            ch_vars.new_data_tr = True
        ch_vars.rx_beep_tr = True
        self.ch_status_update()

    # END QSO WIN
    ###############################################################
    ###############################################################
    # Monitor WIN

    def sysMsg_to_monitor(self, var: str):
        # var += bytes.fromhex('15').decode('UTF-8')+'\n'
        """ Called from AX25Conn """
        ind = str(self._mon_txt.index(tk.INSERT))
        ins = 'SYS {0}: *** {1}\n'.format(datetime.datetime.now().strftime('%H:%M:%S'), var)

        self._mon_txt.configure(state="normal")
        self._mon_txt.insert(ind, ins)
        ind2 = self._mon_txt.index(tk.INSERT)
        self._mon_txt.tag_add("sys-msg", ind, ind2)
        self._mon_txt.configure(state="disabled")
        self._see_end_mon_win()
        if 'Lob: ' in var:
            var = var.split('Lob: ')
            if len(var) > 1:
                SOUND.sprech(var[1])

    """
    def update_monitor(self, ax25frame, port_conf, tx=False):
        # Called from AX25Conn 
        self._mon_buff.append((
            ax25frame,
            port_conf,
            bool(tx)
        ))
    """

    def _monitor_task(self):
        mon_buff = self._port_handler.get_monitor_data()
        if mon_buff:
            tr = False
            self._mon_txt.configure(state="normal")
            for axframe_conf, port_conf, tx in mon_buff:
                port_id = port_conf.get('parm_PortNr', -1)
                mon_out = monitor_frame_inp(axframe_conf, port_conf, self.setting_mon_encoding.get())
                if self.mon_aprs_var.get():
                    mon_str = mon_out[0] + mon_out[1]
                else:
                    mon_str = mon_out[0]
                if not mon_str.endswith('\n'):
                    mon_str += '\n'
                var = tk_filter_bad_chars(mon_str)
                ind = self._mon_txt.index('end-1c')
                # TODO Autoscroll
                if float(self._mon_txt.index(tk.END)) - float(self._mon_txt.index(tk.INSERT)) < 15:
                    tr = True
                if tx:
                    tag = f"tx{port_id}"
                else:
                    tag = f"rx{port_id}"

                if tag in self._mon_txt.tag_names(None):
                    self._mon_txt.insert(tk.END, var, tag)
                else:
                    self._mon_txt.insert(tk.END, var)
                    ind2 = self._mon_txt.index('end-1c')
                    self._mon_txt.tag_add(tag, ind, ind2)
            cut_len = int(self._mon_txt.index('end-1c').split('.')[0]) - PARAM_MAX_MON_LEN + 1
            if cut_len > 0:
                self._mon_txt.delete('1.0', f"{cut_len}.0")
            if tr or self.mon_scroll_var.get():
                self._see_end_mon_win()
            self._mon_txt.configure(state="disabled", exportselection=True)
            return True
        return False

    def see_end_inp_win(self):
        self._inp_txt.see("end")

    def see_end_qso_win(self):
        self._out_txt.see("end")

    def _see_end_mon_win(self):
        self._mon_txt.see("end")

    # END Monitor WIN
    ###############################################################

    ###############################################################
    # Dual Port
    def _dualPort_monitor_task(self):
        if not self.dualPortMon_win:
            return False
        self.dualPortMon_win.dB_mon_tasker()
        return True

    ###############################################################

    ###############################################################
    # Open Toplevel Win

    def open_link_holder_sett(self):
        self._open_settings_window('l_holder')

    def open_ft_manager(self, event=None):
        self._open_settings_window('ft_manager')

    def _open_settings_window(self, win_key: str):
        if not win_key:
            return
        if self.settings_win:
            self.settings_win.lift()
            return
        settings_win = {
            'priv_win': PrivilegWin,            # Priv Win              # TODO move to open_window
            'keybinds': KeyBindsHelp,           # Keybinds Help WIN     # TODO move to open_window
            'about': About,                     # About WIN             # TODO move to open_window
            'aprs_sett': APRSSettingsWin,       # APRS Settings
            'ft_manager': FileTransferManager,  # FT Manager            # TODO move to open_window
            'pipe_sett': PipeToolSettings,      # Pipe Tool
            # 'user_db': UserDB,  # UserDB
            'l_holder': LinkHolderSettings,     # Linkholder
            'pms_all_sett': BBSSettingsMain,    # New PMS Settings
            'all_sett': SettingsMain,           # New All Settings
        }.get(win_key, '')
        if callable(settings_win):
            self.settings_win = settings_win(self)

    def open_window(self, win_key: str):
        # self._open_window('new_conn')
        if not win_key:
            return
        win_list = {
            'new_conn': (self.new_conn_win, NewConnWin),
            'wx_win': (self.wx_window, WXWin),
            'locator_calc': (self.locator_calc_window, LocatorCalculator),
            'aprs_mon': (self.aprs_mon_win, AISmonitor),
            'aprs_msg': (self.aprs_pn_msg_win, APRS_msg_SYS_PN),
            'pms_fwq_q': (self.BBS_fwd_q_list, BBS_fwd_Q),
            'pms_msg_center': (self.MSG_Center_win, MSG_Center),
            'pms_new_msg': (self.newPMS_MSG_win, BBS_newMSG),
            'userDB_tree': (self.userDB_tree_win, UserDBtreeview),
            'ft_send': (self.FileSend_win, FileSend),
            'PortStat': (self.port_stat_win, PlotWindow),
            'fwdPath': (self.fwd_Path_plot_win, FwdGraph),
            'dualPort_settings': (self.dualPort_settings_win, DualPortSettingsWin),
            'dualPort_monitor': (self.dualPortMon_win, DualPort_Monitor),
            'ConnPathPlot': (self.conn_Path_plot_win, ConnPathsPlot),
            # TODO .......

        }.get(win_key, None)
        if not win_list:
            return
        if win_list[0]:
            if hasattr(win_list[0], 'lift'):
                win_list[0].lift()
            return
        if callable(win_list[1]):
            win_list[1](self)

    ##########################
    # UserDB
    def open_user_db_win(self, event=None, ent_key=''):
        if self.userdb_win is None:
            if not ent_key:
                conn = self.get_conn()
                if conn is not None:
                    ent_key = conn.to_call_str
            self.userdb_win = UserDB(self, ent_key)

    ##########################
    # New Connection WIN
    def open_new_conn_win(self):
        self.open_window('new_conn')

    ######################
    # APRS Beacon Tracer
    def open_be_tracer_win(self):
        self.reset_tracer_alarm()  # ??? PORTHANDLER set_tracerAlram ???
        if self.be_tracer_win is None:
            self.be_tracer_win = BeaconTracer(self)

    ###################
    # MH WIN
    def open_MH_win(self):
        """MH WIN"""
        self._port_handler.set_dxAlarm(False)
        if self.mh_window is None:
            MHWin(self)
        self.tabbed_sideFrame.reset_dx_alarm()
        self.tabbed_sideFrame2.reset_dx_alarm()

    #######################################################
    """
    def gui_set_distance(self):
        self._set_distance_fm_conn()
    """
    """
    def _set_distance_fm_conn(self):
        conn = self.get_conn()
        if conn is not None:
            conn.set_distance()
            return True
        return False
    """

    #######################################################################
    # DISCO
    def _disco_conn(self):
        conn = self.get_conn(self.channel_index)
        if conn is not None:
            conn.conn_disco()

    def _disco_all(self):
        if messagebox.askokcancel(title=STR_TABLE.get('disconnect_all', ('', '', ''))[self.language],
                                  message=STR_TABLE.get('disconnect_all_ask', ('', '', ''))[self.language],
                                  parent=self.main_win):
            self._port_handler.disco_all_Conn()

    # DISCO ENDE
    #######################################################################
    #######################################################################
    # SEND TEXT OUT
    def _snd_text(self, event: tk.Event):
        if self.channel_index:
            station = self.get_conn(self.channel_index)
            if station:
                ch_vars = self.get_ch_var(ch_index=self.channel_index)
                ind = str(ch_vars.input_win_index)
                if ind:
                    if float(ind) >= float(self._inp_txt.index(tk.INSERT)):
                        ind = str(self._inp_txt.index(tk.INSERT))
                    ind = str(int(float(ind))) + '.0'
                else:
                    ind = '1.0'

                txt_enc = self.stat_info_encoding_var.get()
                if station.user_db_ent:
                    txt_enc = station.user_db_ent.Encoding
                # ind = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'
                tmp_txt = self._inp_txt.get(ind, tk.INSERT)

                tmp_txt = tmp_txt.replace('\n', '\r')
                station.send_data(tmp_txt.encode(txt_enc, 'ignore'))

                self._inp_txt.tag_remove('send', ind, str(self._inp_txt.index(tk.INSERT)))
                self._inp_txt.tag_add('send', ind, str(self._inp_txt.index(tk.INSERT)))

                ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))

                if '.0' in self._inp_txt.index(tk.INSERT):
                    self._inp_txt.tag_remove('send', 'insert-1c', tk.INSERT)

        else:
            self._send_to_monitor()

    def _send_to_monitor(self):
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        ind = str(ch_vars.input_win_index)
        if ind:
            if float(ind) >= float(self._inp_txt.index(tk.INSERT)):
                ind = str(self._inp_txt.index(tk.INSERT))
            ind = str(int(float(ind))) + '.0'
        else:
            ind = '1.0'
        tmp_txt = self._inp_txt.get(ind, self._inp_txt.index(tk.INSERT))
        tmp_txt = tmp_txt.replace('\n', '\r')
        port_id = int(self.mon_port_var.get())
        if port_id in self._port_handler.get_all_ports().keys():
            port = self._port_handler.get_all_ports()[port_id]
            add = str(self.mon_to_add_var.get()).upper()
            own_call = str(self.mon_call_var.get())
            poll = bool(self.mon_poll_var.get())
            cmd = bool(self.mon_cmd_var.get())
            pid = self.mon_pid_var.get()
            pid = pid.split('>')[0]
            pid = int(pid, 16)
            text = tmp_txt.encode()
            if add and own_call and text:
                text_list = [text[i:i + 256] for i in range(0, len(text), 256)]
                for el in text_list:
                    port.send_UI_frame(
                        own_call=own_call,
                        add_str=add,
                        text=el,
                        cmd_poll=(cmd, poll),
                        pid=pid
                    )
                # self.inp_txt.tag_add('send', ind, str(self.inp_txt.index(tk.INSERT)))
        ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))
        if int(float(self._inp_txt.index(tk.INSERT))) != int(float(self._inp_txt.index(tk.END))) - 1:
            self._inp_txt.delete(tk.END, tk.END)

    def _on_click_inp_txt(self, event=None):
        self._inp_txt.tag_add('send', 0.0, tk.END)
        ind = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'
        self._inp_txt.tag_remove('send', ind, tk.INSERT)
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        ch_vars.input_win_index = ind

    def _on_key_release_inp_txt(self, event=None):
        ind = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'
        text = zeilenumbruch(self._inp_txt.get(ind,  self._inp_txt.index(tk.INSERT)))
        self._inp_txt.delete(ind,  self._inp_txt.index(tk.INSERT))
        self._inp_txt.insert(tk.INSERT, text)
        self._inp_txt.tag_remove('send', ind, tk.INSERT)

    # SEND TEXT OUT
    #######################################################################
    # BW Plot
    def _update_bw_mon(self):
        tr = False
        for port_id in list(self._port_handler.ax25_ports.keys()):
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_id)
            data = self.mh.get_bandwidth(
                port_id,
                port_cfg.get('parm_baud', 1200),
            )
            label = f"{port_cfg.get('parm_PortName', '')}"
            if port_id not in self._bw_plot_lines:
                self._bw_plot_lines[int(port_id)], = self._ax.plot(self._bw_plot_x_scale, data, label=label)
                self._ax.legend()
                tr = True
            else:
                if list(data) != list(self._bw_plot_lines[int(port_id)].get_data()[1]):
                    self._bw_plot_lines[int(port_id)].set_ydata(data)
                    tr = True
        if tr:
            self._draw_bw_plot()

    def _draw_bw_plot(self):
        self._bw_fig.canvas.draw()
        self._bw_fig.canvas.flush_events()
        self._canvas.flush_events()

    # END BW Plot
    #######################################################################
    #######################################################################
    # Conn Path Plot
    def add_LivePath_plot(self, node: str, ch_id: int, path=None):
        if path is None:
            path = []
        # print(f"CH: {ch_id} self.CH_ID: {self.channel_index} - Node: {node} - Path: {path}")
        for digi in path:
            self._Pacman.change_node(node=digi, ch_id=ch_id)
        self._Pacman.change_node(node=node, ch_id=ch_id)
        if ch_id == self.channel_index:
            if not POPT_CFG.get_pacman_fix():
                self._Pacman.update_plot_f_ch(ch_id=ch_id)

    def resetHome_LivePath_plot(self, ch_id: int):
        # print(f"CH: {ch_id} self.CH_ID: {self.channel_index} - RESET")
        self._Pacman.reset_last_hop(ch_id=ch_id)
        if ch_id == self.channel_index:
            if not POPT_CFG.get_pacman_fix():
                self._Pacman.update_plot_f_ch(ch_id=ch_id)
    # ENDConn Path Plot
    #######################################################################

    def _kaffee(self):
        self.sysMsg_to_monitor('Hinweis: Hier gibt es nur Muckefuck !')
        SOUND.sprech('Gluck gluck gluck blubber blubber')
        #print(self._inp_txt.cget('height'))
        #print(self._pw.sashpos(0))
        #self._pw.sashpos(0, 20)
        # self._inp_txt.configure(height= 200)
        # self._port_handler.set_dxAlarm()
        # self._port_handler.set_tracerAlarm()
        # ## self._port_handler.debug_Connections()
        # self._Alarm_Frame.set_pmsMailAlarm()
        # self.set_noty_bell()
        # self._do_bbs_fwd()
        # self.conn_task = AutoConnTask()
        # print(get_mail_import())
        #self._save_pw_pos()
        #self._load_pw_pos()

    def _do_pms_autoFWD(self):
        self._port_handler.get_bbs().start_man_autoFwd()

    def _do_pms_fwd(self):
        conn = self.get_conn()
        if conn is not None:
            conn.bbsFwd_start_reverse()

    def do_priv(self, event=None):
        conn = self.get_conn()
        if conn is not None:
            if conn.user_db_ent:
                if conn.user_db_ent.sys_pw:
                    conn.cli.start_baycom_login()
                else:
                    self._open_settings_window('priv_win')

    def _switch_monitor_mode(self):
        self._switch_mon_mode()
        if self.mon_mode:
            # self.channel_index = int(self.mon_mode)
            self._ch_btn_clk(int(self.mon_mode))
            self.mon_mode = 0
            self._mon_btn.configure(bg='yellow')
            self.ch_status_update()
            self._load_pw_pos()
            return

        self.mon_mode = int(self.channel_index)
        self._ch_btn_clk(0)
        self._mon_btn.configure(bg='green')
        self.ch_status_update()

    def switch_channel(self, ch_ind: int = 0):
        # Channel 0 = Monitor
        if not ch_ind:
            self._switch_monitor_mode()
        else:
            if self.mon_mode:
                self.mon_mode = int(ch_ind)
                self._switch_monitor_mode()
            else:
                self._ch_btn_clk(ch_ind)
        self.on_channel_status_change()

    #####################################################################
    #
    def conn_btn_update(self):
        """
        Called fm:
        self._ch_btn_clk
        self._port_handler.accept_new_connection
        self._port_handler.end_connection
        """
        conn = self.get_conn(self.channel_index)
        if conn:
            if self._conn_btn.cget('bg') != "red":
                self._conn_btn.configure(bg="red", text="Disconnect", command=self._disco_conn)
        elif self._conn_btn.cget('bg') != "green":
            self._conn_btn.configure(text="Connect", bg="green", command=self.open_new_conn_win)
        self._ch_btn_status_update()

    def ch_status_update(self):
        """ Triggerd when Connection Status has changed (Conn-accept, -end, -resset)"""
        self._ch_btn_status_update()
        self.on_channel_status_change()

    def _ch_btn_clk(self, ind: int):
        old_ch_vars = self.get_ch_var(ch_index=int(self.channel_index))
        old_ch_vars.input_win = self._inp_txt.get('1.0', tk.END)
        old_ch_vars.input_win_tags = get_all_tags(self._inp_txt)
        old_ch_vars.output_win_tags = get_all_tags(self._out_txt)
        old_ch_vars.input_win_cursor_index = self._inp_txt.index(tk.INSERT)
        self.channel_index = ind
        self._update_qso_Vars()
        self.ch_status_update()
        self.conn_btn_update()
        self.reset_noty_bell()
        self._Pacman.update_plot_f_ch(self.channel_index)
        self._kanal_switch()  # Sprech

    def reset_noty_bell(self):
        conn = self.get_conn(self.channel_index)
        if not conn:
            return
        if conn.noty_bell:
            conn.noty_bell = False
            self.reset_noty_bell_alarm()

    def reset_noty_bell_alarm(self):
        self._Alarm_Frame.set_Bell_alarm(False)
        self._Alarm_Frame.set_Bell_active(self.setting_noty_bell.get())

    def set_noty_bell(self, ch_id, msg=''):
        conn = self.get_conn(ch_id)
        if not conn:
            return
        self._Alarm_Frame.set_Bell_alarm()

        if self.setting_noty_bell.get():
            if self.setting_sound.get():
                SOUND.bell_sound()
            threading.Thread(target=self._noty_bell, args=(ch_id, msg)).start()

    def _noty_bell(self, ch_id, msg=''):
        conn = self.get_conn(ch_id)
        if not conn:
            return
        if not msg:
            msg = f"{conn.to_call_str} {STR_TABLE['cmd_bell_gui_msg'][self.language]}"
        if messagebox.askokcancel(f"Bell {STR_TABLE['channel'][self.language]} {ch_id}",
                                  msg, parent=self.main_win):
            if not self._quit:
                self.switch_channel(ch_id)

    def set_noty_bell_active(self):
        self._Alarm_Frame.set_Bell_active(self.setting_noty_bell.get())

    def set_aprsMail_alarm(self):
        self._Alarm_Frame.set_aprsMail_alarm(True)

    def reset_aprsMail_alarm(self):
        self._Alarm_Frame.set_aprsMail_alarm(False)

    def _ch_btn_status_update(self):
        # TODO Call just if necessary
        # TODO not calling in Tasker Loop for Channel Alarm (change BTN Color)
        # self.main_class.on_channel_status_change()
        ch_alarm = False
        # if self._port_handler.get_all_connections().keys():
        for i in list(self._con_btn_dict.keys()):
            all_conn = self._port_handler.get_all_connections()
            if i in list(all_conn.keys()):
                btn_txt = all_conn[i].to_call_str
                is_link = all_conn[i].is_link
                is_pipe = all_conn[i].pipe
                if is_link:
                    btn_txt = 'L>' + btn_txt
                elif is_pipe:
                    btn_txt = 'P>' + btn_txt
                if self._con_btn_dict[i][1].get() != btn_txt:
                    self._con_btn_dict[i][1].set(btn_txt)
                if i == self.channel_index:
                    if is_link:
                        if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue2':
                            self._con_btn_dict[i][0].configure(bg='SteelBlue2')
                    elif is_pipe:
                        if self._con_btn_dict[i][0].cget('bg') != 'cyan2':
                            self._con_btn_dict[i][0].configure(bg='cyan2')
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'green2':
                            self._con_btn_dict[i][0].configure(bg='green2')
                        self.set_ch_new_data_tr(i, False)
                else:
                    if self.get_ch_new_data_tr(i):
                        if is_link:
                            if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue4':
                                self._con_btn_dict[i][0].configure(bg='SteelBlue4')
                            # ch_alarm = False
                        elif is_pipe:
                            if self._con_btn_dict[i][0].cget('bg') != 'cyan4':
                                self._con_btn_dict[i][0].configure(bg='cyan4')
                            # ch_alarm = False
                        else:
                            ch_alarm = True
                            self._ch_btn_alarm(self._con_btn_dict[i][0])
                    else:
                        if is_link:
                            # ch_alarm = False
                            if self._con_btn_dict[i][0].cget('bg') != 'SteelBlue4':
                                self._con_btn_dict[i][0].configure(bg='SteelBlue4')
                        elif is_pipe:
                            if self._con_btn_dict[i][0].cget('bg') != 'cyan4':
                                self._con_btn_dict[i][0].configure(bg='cyan4')
                            # ch_alarm = False
                        else:
                            if self._con_btn_dict[i][0].cget('bg') != 'green4':
                                self._con_btn_dict[i][0].configure(bg='green4')
            else:
                if self._con_btn_dict[i][1].get() != str(i):
                    # self.con_btn_dict[i].configure(text=str(i))
                    self._con_btn_dict[i][1].set(str(i))

                if not self.get_ch_new_data_tr(i):
                    if i == self.channel_index:
                        if self._con_btn_dict[i][0].cget('bg') != 'red2':
                            self._con_btn_dict[i][0].configure(bg='red2')
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'red4':
                            self._con_btn_dict[i][0].configure(bg='red4')
                else:
                    if i == self.channel_index:
                        if self._con_btn_dict[i][0].cget('bg') != 'red2':
                            self._con_btn_dict[i][0].configure(bg='red2')
                        self.set_ch_new_data_tr(i, False)
                    else:
                        if self._con_btn_dict[i][0].cget('bg') != 'yellow':
                            self._con_btn_dict[i][0].configure(bg='yellow')


        if self._ch_btn_blink_timer < time.time():
            self._ch_btn_blink_timer = time.time() + self._parm_btn_blink_time
        self._ch_alarm = ch_alarm

    def _ch_btn_alarm(self, btn: tk.Button):
        if self._ch_btn_blink_timer < time.time():
            clr = generate_random_hex_color()
            if btn.cget('bg') != clr:
                btn.configure(bg=clr)

    def on_channel_status_change(self):
        """ Triggerd when Connection Status has changed + additional Trigger"""
        self.tabbed_sideFrame.on_ch_stat_change()
        self.tabbed_sideFrame2.on_ch_stat_change()
        self.update_station_info()

    def _update_stat_info_conn_timer(self):
        conn = self.get_conn()
        if conn is not None:
            if hasattr(conn, 'cli'):
                self.stat_info_timer_var.set(get_time_delta(conn.cli.time_start))
                return
        if self.stat_info_timer_var.get() != '--:--:--':
            self.stat_info_timer_var.set('--:--:--')

    def update_station_info(self):
        name = '-------'
        qth = '-------'
        loc = '------'
        # _dist = 0
        status = '-------'
        typ = '-----'
        sw = '---------'
        enc = ''
        conn = self.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                if db_ent.Name:
                    name = db_ent.Name
                if db_ent.QTH:
                    qth = db_ent.QTH
                if db_ent.LOC:
                    loc = db_ent.LOC
                if db_ent.Distance > 0:
                    loc += f" ({db_ent.Distance} km)"
                if db_ent.TYP:
                    typ = db_ent.TYP
                if db_ent.Software:
                    sw = db_ent.Software
                enc = db_ent.Encoding
            if conn.is_link:
                status = 'DIGI'
                if self.stat_info_status_var.get() != status:
                    self.stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', )
            elif conn.pipe is not None:
                status = 'PIPE'
                if self.stat_info_status_var.get() != status:
                    self.stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', )
            elif conn.ft_obj is not None:
                status = f'{conn.ft_obj.dir} FILE'
                if self.stat_info_status_var.get() != status:
                    self.stat_info_status_var.set(status)
                    # self.status_label.bind('<Button-1>', lambda: self._open_settings_window('ft_manager'))
                    self.status_label.bind('<Button-1>', self.open_ft_manager)
            else:
                status = ''
                if conn.cli.sysop_priv:
                    status += 'S'
                else:
                    status += '-'
                if conn.link_holder_on:
                    status += 'L'
                else:
                    status += '-'
                if conn.is_RNR:
                    status += 'R'
                else:
                    status += '-'
                status += '----'
                if self.stat_info_status_var.get() != status:
                    self.stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', self.do_priv)
        elif self.stat_info_status_var.get() != status:
            self.stat_info_status_var.set(status)
            self.status_label.bind('<Button-1>', )
        """
        if _dist:
            loc += f" ({_dist} km)"
        """
        # if self.stat_info_status_var.get() != _status:
        #     self.stat_info_status_var.set(_status)
        if self.stat_info_name_var.get() != name:
            self.stat_info_name_var.set(name)
        if self.stat_info_qth_var.get() != qth:
            self.stat_info_qth_var.set(qth)
        if self.stat_info_loc_var.get() != loc:
            self.stat_info_loc_var.set(loc)
        if self.stat_info_typ_var.get() != typ:
            self.stat_info_typ_var.set(typ)
        if self.stat_info_sw_var.get() != sw:
            self.stat_info_sw_var.set(sw)
        if self.stat_info_encoding_var.get() != enc:
            self.stat_info_encoding_var.set(enc)

    def _update_ft_info(self):
        prog_val = 0
        prog_var = '---.- %'
        size_var = 'Size: ---,- / ---,- kb'
        dur_var = 'Time: --:--:-- / --:--:--'
        bps_var = 'BPS: ---.---'
        next_tx = 'TX in: --- s'
        conn = self.get_conn()
        if conn:
            if conn.ft_obj:
                ft_obj = conn.ft_obj
                percentage_completion, data_len, data_sendet, time_spend, time_remaining, baud_rate = ft_obj.get_ft_infos()
                prog_val = percentage_completion
                prog_var = f"{percentage_completion} %"
                data_len = get_kb_str_fm_bytes(data_len)
                data_sendet = get_kb_str_fm_bytes(data_sendet)
                size_var = f'Size: {data_sendet} / {data_len}'
                t_spend = conv_timestamp_delta(time_spend)
                t_remaining = conv_timestamp_delta(time_remaining)
                dur_var = f'Time: {t_spend} / {t_remaining}'
                bps_var = f"BPS: {format_number(baud_rate)}"
                if ft_obj.param_wait:
                    n_tx = ft_obj.last_tx - time.time()
                    next_tx = f'TX in: {max(round(n_tx), 0)} s'

        if self.ft_duration_var.get() != dur_var:
            self.tabbed_sideFrame.ft_progress['value'] = prog_val
            self.tabbed_sideFrame2.ft_progress['value'] = prog_val
            self.ft_progress_var.set(prog_var)
            self.ft_size_var.set(size_var)
            self.ft_duration_var.set(dur_var)
            self.ft_bps_var.set(bps_var)
            self.ft_next_tx_var.set(next_tx)

    #########################################
    # TxTframe FNCs
    def _update_status_win(self):
        station = self.get_conn(self.channel_index)
        fg, bg = self._get_colorMap()
        if station is not None:
            from_call = str(station.my_call_str)
            status = station.zustand_tab[station.get_state()][1]
            # uid = station.ax25_out_frame.addr_uid
            n2 = station.n2
            unAck = f"nACK: {len(station.tx_buf_unACK.keys())}"
            vs_vr = f"VS/VR: {station.vr}/{station.vs}"
            n2_text = f"N2: {n2}"
            t1_text = f"T1: {max(0, int(station.t1 - time.time()))}"
            rtt_text = 'RTT: {:.1f}/{:.1f}'.format(station.RTT_Timer.rtt_last, station.RTT_Timer.rtt_average)
            t3_text = f"T3: {max(0, int(station.t3 - time.time()))}"
            if station.get_port_cfg().get('parm_T2_auto', True):
                t2_text = f"T2: {int(station.get_param_T2() * 1000)}A"
            else:
                t2_text = f"T2: {int(station.get_param_T2() * 1000)}"
            if self._status_name_var.get() != from_call:
                self._status_name_var.set(from_call)
            if self._status_status_var.get() != status:
                status_bg = STATUS_BG[status]
                self._status_status_var.set(status)
                self._status_status.configure(bg=status_bg)
            if self._status_unack_var.get() != unAck:
                self._status_unack_var.set(unAck)
                if len(station.tx_buf_unACK.keys()):
                    if self._status_unack.cget('bg') != 'yellow':
                        self._status_unack.configure(bg='yellow')
                else:
                    if self._status_unack.cget('bg') != 'green':
                        self._status_unack.configure(bg='green')
            if self._status_vs_var.get() != vs_vr:
                self._status_vs_var.set(vs_vr)
            if self._status_n2_var.get() != n2_text:
                self._status_n2_var.set(n2_text)
                if n2 > 4:
                    if self._status_n2.cget('bg') != 'yellow':
                        self._status_n2.configure(fg='black')
                        self._status_n2.configure(bg='yellow')
                elif n2 > 10:
                    if self._status_n2.cget('bg') != 'orange':
                        self._status_n2.configure(fg='black')
                        self._status_n2.configure(bg='orange')
                else:
                    if self._status_n2.cget('bg') != bg:
                        self._status_n2.configure(bg=bg)
                        self._status_n2.configure(fg=fg)
            if self._status_t1_var.get() != t1_text:
                self._status_t1_var.set(t1_text)
            if self._status_t2_var.get() != t2_text:
                self._status_t2_var.set(t2_text)
            if self._status_rtt_var.get() != rtt_text:
                self._status_rtt_var.set(rtt_text)
            if self._status_t3_var.get() != t3_text:
                self._status_t3_var.set(t3_text)

        else:

            if self._status_status.cget('bg') != bg:
                # self.status_name.configure(text="", bg=STAT_BAR_CLR)
                self._status_name_var.set('')
                self._status_status.configure(bg=bg)
                self._status_status_var.set('')
                self._status_unack.configure(bg=bg)
                self._status_unack_var.set('')
                self._status_vs_var.set('')
                self._status_n2.configure(bg=bg)
                self._status_n2.configure(fg=fg)
                self._status_n2_var.set('')
                self._status_t1_var.set('')
                self._status_t2_var.set('')
                self._status_t3_var.set('')
                self._status_rtt_var.set('')

    def _switch_mon_mode(self):
        if self.mon_mode:
            try:
                self._pw.remove(self._TXT_upper_frame)
                self._pw.remove(self._TXT_lower_frame)
            except tk.TclError:
                pass
            self._pw.add(self._TXT_upper_frame, weight=1)
            self._pw.add(self._TXT_mid_frame,   weight=1)
            self._pw.add(self._TXT_lower_frame, weight=1)
            #self._load_pw_pos()

        else:
            self._save_pw_pos()
            self._pw.remove(self._TXT_mid_frame)

    def _chk_rx_beep(self):
        rx_beep_check = self._rx_beep_var.get()
        bg = self._get_colorMap()[1]
        if rx_beep_check:
            if self._rx_beep_box.cget('bg') != 'green':
                self._rx_beep_box.configure(bg='green', activebackground='green')
        else:
            if self._rx_beep_box.cget('bg') != bg:
                self._rx_beep_box.configure(bg=bg, activebackground=bg, background=bg)
        self.get_ch_var().rx_beep_opt = rx_beep_check

    def _chk_timestamp(self):
        """
        ts_check = self._ts_box_var.get()
        bg = self._get_colorMap()[1]
        if ts_check:
            if self._ts_box_box.cget('bg') != 'green':
                self._ts_box_box.configure(bg='green', activebackground='green')
        else:
            if self._ts_box_box.cget('bg') != bg:
                self._ts_box_box.configure(bg=bg, activebackground=bg)

        self.get_ch_var().timestamp_opt = ts_check
        """
        pass


    def _set_stat_typ(self, event=None):
        conn = self.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                db_ent.TYP = self.stat_info_typ_var.get()
        else:
            self.stat_info_typ_var.set('-----')

    def _change_txt_encoding(self, event=None, enc=''):
        conn = self.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                if not enc:
                    enc = self.stat_info_encoding_var.get()
                db_ent.Encoding = enc
        else:
            self.stat_info_encoding_var.set('')

    ##########################################
    #
    def get_free_channel(self, start_channel=1):
        if not self.get_conn(con_ind=start_channel):
            return start_channel
        for ch_id in range(1, MAX_SYSOP_CH):
            if not self.get_conn(con_ind=ch_id):
                return ch_id
        return None

    def get_all_free_channels(self):
        ret = []
        for ch_id in range(1, MAX_SYSOP_CH):
            if not self.get_conn(con_ind=ch_id):
                ret.append(ch_id)
        return ret

    def get_ch_new_data_tr(self, ch_id):
        return bool(self.get_ch_var(ch_index=ch_id).new_data_tr)

    def set_ch_new_data_tr(self, ch_id, state: bool):
        self.get_ch_var(ch_index=ch_id).new_data_tr = state

    ##########################################
    #
    def set_tracer(self, state=None):
        ais_obj = self._port_handler.get_aprs_ais()
        if ais_obj is not None:
            ais_obj.be_tracer_active = bool(self.setting_tracer.get())
        else:
            self.setting_tracer.set(False)
        self.set_auto_tracer()
        # FIXME
        # self.tabbed_sideFrame.set_auto_tracer_state()
        # self.tabbed_sideFrame.set_auto_tracer_state()
        # self.set_tracer_icon()

    def get_tracer(self):
        ais_obj = self._port_handler.get_aprs_ais()
        if ais_obj is not None:
            return bool(ais_obj.be_tracer_active)
        return False

    def get_auto_tracer(self):
        ais_obj = self._port_handler.get_aprs_ais()
        if ais_obj is not None:
            return bool(ais_obj.be_auto_tracer_active)
        return False

    def set_tracer_fm_aprs(self):
        ais_obj = self._port_handler.get_aprs_ais()
        if ais_obj is not None:
            self.setting_tracer.set(ais_obj.be_tracer_active)
        else:
            self.setting_tracer.set(False)
        self.tabbed_sideFrame.set_auto_tracer_state()
        self.tabbed_sideFrame2.set_auto_tracer_state()

    def set_auto_tracer(self, event=None):
        ais_obj = self._port_handler.get_aprs_ais()
        set_to = False
        if ais_obj is not None:
            self.set_tracer_fm_aprs()
            if self.setting_tracer.get():
                set_to = False
            else:
                set_to = bool(self.setting_auto_tracer.get())
            ais_obj.tracer_auto_tracer_set(set_to)
        self.setting_auto_tracer.set(set_to)
        self.tabbed_sideFrame.set_auto_tracer_state()
        self.tabbed_sideFrame2.set_auto_tracer_state()
        # self.set_tracer_icon()

    def get_auto_tracer_duration(self):
        ais_obj = self._port_handler.get_aprs_ais()
        if ais_obj is None:
            return 0
        return ais_obj.be_auto_tracer_duration

    def set_auto_tracer_duration(self, dur):
        ais_obj = self._port_handler.get_aprs_ais()
        if ais_obj is not None:
            if type(dur) is int:
                ais_obj.tracer_auto_tracer_duration_set(dur)
                self.set_auto_tracer()

    def set_dx_alarm(self, event=None):
        dx_alarm = bool(self.setting_dx_alarm.get())
        if not dx_alarm:
            self.setting_auto_tracer.set(False)
        self.set_auto_tracer()
        if self._Alarm_Frame:
            self._Alarm_Frame.set_dxAlarm_active(dx_alarm)

    def get_dx_alarm(self):
        return bool(self.setting_dx_alarm.get())

    ######################################################################

    def dx_alarm(self):
        """ Alarm when new User in MH List """
        if self.setting_dx_alarm.get():
            self._Alarm_Frame.set_dxAlarm(True)

    def tracer_alarm(self):
        """ Tracer Alarm """
        self._tracer_alarm = True
        self._Alarm_Frame.set_tracerAlarm(True)

    def reset_tracer_alarm(self):
        """ Tracer Alarm """
        if self._tracer_alarm:
            self._Alarm_Frame.set_tracerAlarm(False)
            self._tracer_alarm = False

    def reset_dx_alarm(self):
        dx_alarm = bool(self.setting_dx_alarm.get())
        self._Alarm_Frame.set_dxAlarm_active(dx_alarm)

    def pmsMail_alarm(self):
        if self.MSG_Center_win:
            return
        self._Alarm_Frame.set_pmsMailAlarm(True)

    def reset_pmsMail_alarm(self):
        self._Alarm_Frame.set_pmsMailAlarm(False)

    def pmsFwd_alarm(self):
        self._Alarm_Frame.set_pms_fwd_alarm(True)

    def reset_pmsFwd_alarm(self):
        self._Alarm_Frame.set_pms_fwd_alarm(False)
        if self.MSG_Center_win:
            self.MSG_Center_win.tree_update_task()

    def set_diesel(self):
        self._Alarm_Frame.set_diesel(True)
        self._init_state = 0

    def reset_diesel(self):
        self._Alarm_Frame.set_diesel(False)

    def set_rxEcho_icon(self, alarm_set=True):
        self._Alarm_Frame.set_rxEcho_icon(alarm_set=alarm_set)

    def set_Beacon_icon(self, alarm_set=True):
        self._Alarm_Frame.set_beacon_icon(alarm_set=alarm_set)

    def chk_master_sprech_on(self):
        if self.setting_sprech.get():
            SOUND.master_sprech_on = True
            self.tabbed_sideFrame.t2speech.configure(state='normal')
            self.tabbed_sideFrame2.t2speech.configure(state='normal')
        else:
            SOUND.master_sprech_on = False
            self.tabbed_sideFrame.t2speech.configure(state='disabled')
            self.tabbed_sideFrame2.t2speech.configure(state='disabled')
        self.set_var_to_all_ch_param()


    def get_PH_manGUI(self):
        return self._port_handler
