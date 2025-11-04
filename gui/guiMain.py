import datetime
import random
import time
import tkinter as tk
from collections import deque
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
from gui.aprs.guiAPRS_Settings_Main import APRSSettingsMain
from gui.aprs.guiAPRS_pn_msg import APRS_msg_SYS_PN
#from gui.aprs.guiAPRS_symbol_tab import APRSymbolTab
from gui.aprs.guiAPRS_wx_tree import WXWin  # !!!!!!!!!!
from gui.guiBlockList import BlockList
from gui.guiDualPortMon import DualPort_Monitor
from gui.guiMain_AlarmFrame import AlarmIconFrame
from gui.guiMain_TabbedSideFrame import SideTabbedFrame
from gui.guiRightClick_Menu import ContextMenu
#from gui.guiRoutingTab import RoutingTableWindow
#from gui.plots.gui_ConnPath_plot import ConnPathsPlot
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
from gui.guiMH.guiMH import MHWin
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
    DEF_QSO_SYSMSG_BG, MAX_SYSOP_CH, COLOR_MAP, STYLES_AWTHEMES_PATH, STYLES_AWTHEMES, CFG_gui_icon_path, \
    PARAM_MAX_MON_TREE_ITEMS, CFG_aprs_icon_path, CFG_gui_conn_hist_path, GUI_TASKER_Q_RUNTIME, \
    GUI_TASKER_TIME_D_UNTIL_BURN, GUI_TASKER_BURN_DELAY, GUI_TASKER_NOT_BURN_DELAY, MON_BATCH_TO_PROCESS, CLI_TYP_BOX, \
    CLI_TYP_CONVERSE, CLI_TYP_TASK_FWD, CLI_TYP_SYSOP, CLI_TYP_NODE, CLI_TYP_DIGI, CLI_TYP_PIPE, CLI_TYP_NO_CLI
from fnc.os_fnc import is_linux, get_root_dir
from fnc.gui_fnc import get_all_tags, set_all_tags, generate_random_hex_color, set_new_tags, cleanup_tags, \
    build_aprs_icon_tab, get_image
from sound.popt_sound import SOUND
from gui.plots.guiLiveConnPath import LiveConnPath

from gui import FigureCanvasTkAgg, plt
# from gui import FigureCanvasTkAgg
# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread


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
        logger.info('start..')
        guiCfg = POPT_CFG.load_guiPARM_main()
        ###########################################
        self.main_win   = tk.Tk()
        ###########################################
        self.style_name = POPT_CFG.get_guiCFG_style_name()
        logger.info(f'loading Style: {self.style_name}')
        self.style = ttk.Style(self.main_win)

        if self.style_name in STYLES_AWTHEMES:
            try:
                self.style.tk.call('lappend', 'auto_path', STYLES_AWTHEMES_PATH)
                self.style.tk.call('package', 'require', 'awthemes')
                self.style.tk.call('::themeutils::setHighlightColor', self.style_name, '#007000') # TODO
                self.style.tk.call('package', 'require', self.style_name)
                self.style.theme_use(self.style_name)
            except tk.TclError:
                logger.warning('awthemes-10.4.0 not found in folder data')
                logger.warning('  1. If you want to use awthemes, download:')
                logger.warning('     https://sourceforge.net/projects/tcl-awthemes/')
                logger.warning('  2. Extract the contents of the file awthemes-10.4.0.zip')
                logger.warning('     into the data/ folder')
                logger.warning('')
                self.style_name = 'default'
                self.style.theme_use(self.style_name)
        else:
            try:
                self.style.theme_use(self.style_name)
            except tk.TclError:
                logger.warning(f'GUI: TclError Style{self.style_name}')
                self.style_name = 'default'
                self.style.theme_use(self.style_name)

        logger.info(f'Using style_name: {self.style_name}')
        self._get_colorMap = lambda : COLOR_MAP.get(self.style_name, ('#000000',  '#d9d9d9'))
        #################################################################
        self.main_win.title(f"P.ython o.ther P.acket T.erminal {VER}")
        self.main_win.geometry(f"{guiCfg.get('gui_parm_main_width', 1400)}x{guiCfg.get('gui_parm_main_height', 850)}")
        # self.main_win.attributes('-topmost', 0)
        try:
            self.main_win.iconbitmap("favicon.ico")
        except Exception as ex:
            logger.warning(f"Couldn't load favicon.ico: {ex}")
            logger.info("Try to load popt.png.")
            try:
                self.main_win.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(f"Couldn't load popt.png: {ex}")
        self.main_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
        ######################################
        ######################################
        self._port_handler = port_handler
        ######################################
        # Init Vars
        self.mh         = self._port_handler.get_MH()
        self.text_size  = POPT_CFG.load_guiPARM_main().get('gui_parm_text_size', 13)
        ###############################
        self._root_dir  = get_root_dir()
        self._root_dir  = self._root_dir.replace('/', '//')
        ###############################
        logger.info("GUI: Init APRS-Icon Tab 16x16")
        self._aprs_icon_tab_16  = build_aprs_icon_tab((16, 16))
        logger.info("GUI: Init APRS-Icon Tab 24x24")
        self._aprs_icon_tab_24  = build_aprs_icon_tab((24, 24))
        logger.info("GUI: Init Monitor-Tree-Icon Tab 16x16 & 32x16")
        self._rx_tx_icons       = {
            'rx':       get_image(CFG_gui_icon_path + '/pfeil_rechts_gruen.png'     ,size=(16, 16)),  # RX
            'tx':       get_image(CFG_gui_icon_path + '/pfeil_links_rot.png'        ,size=(16, 16)),     # TX
            'rx-node':  get_image(CFG_gui_icon_path + '/node_rx.png',  size=(32, 16)),
            'tx-node':  get_image(CFG_gui_icon_path + '/node_tx.png',  size=(32, 16)),
            'rx-bbs':   get_image(CFG_gui_icon_path + '/bbs_rx.png',   size=(32, 16)),
            'tx-bbs':   get_image(CFG_gui_icon_path + '/bbs_tx.png',   size=(32, 16)),
            'rx-term':  get_image(CFG_gui_icon_path + '/term_rx.png',  size=(32, 16)),
            'tx-term':  get_image(CFG_gui_icon_path + '/term_tx.png',  size=(32, 16)),
            'rx-dx':    get_image(CFG_gui_icon_path + '/dx_rx.png',    size=(32, 16)),
            'rx-block': get_image(CFG_gui_icon_path + '/block_rx.png', size=(32, 16)),
        }
        logger.info("GUI: InitConnection-Typ-Icon Tab 16x16 & 32x16")
        self._conn_typ_icons    = {
            # Connection Tab
            CLI_TYP_SYSOP:      get_image(CFG_aprs_icon_path + '/0-44.png', size=(16, 16)),
            CLI_TYP_NODE:       get_image(CFG_aprs_icon_path + '/0-78.png', size=(16, 16)),
            CLI_TYP_DIGI:       get_image(CFG_aprs_icon_path + '/0-82.png', size=(16, 16)),
            CLI_TYP_PIPE:       get_image(CFG_aprs_icon_path + '/1-26.png', size=(16, 16)),
            CLI_TYP_BOX:        get_image(CFG_aprs_icon_path + '/0-34.png', size=(16, 16)),
            CLI_TYP_TASK_FWD:   get_image(CFG_aprs_icon_path + '/0-61.png', size=(16, 16)),
            CLI_TYP_CONVERSE:   get_image(CFG_aprs_icon_path + '/1-54.png', size=(16, 16)),
            # Connection History Tab
            f'{CLI_TYP_SYSOP}-CONN-OUT':      get_image(CFG_gui_conn_hist_path + '/term_conn_out.png',  size=(32, 16)),
            f'{CLI_TYP_SYSOP}-CONN-IN':       get_image(CFG_gui_conn_hist_path + '/term_conn_in.png',   size=(32, 16)),
            f'{CLI_TYP_SYSOP}-DISCO-OUT':     get_image(CFG_gui_conn_hist_path + '/term_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_SYSOP}-DISCO-IN':      get_image(CFG_gui_conn_hist_path + '/term_disco_in.png',  size=(32, 16)),

            f'{CLI_TYP_NODE}-CONN-OUT':      get_image(CFG_gui_conn_hist_path + '/node_conn_out.png',  size=(32, 16)),
            f'{CLI_TYP_NODE}-CONN-IN':       get_image(CFG_gui_conn_hist_path + '/node_conn_in.png',   size=(32, 16)),
            f'{CLI_TYP_NODE}-DISCO-OUT':     get_image(CFG_gui_conn_hist_path + '/node_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_NODE}-DISCO-IN':      get_image(CFG_gui_conn_hist_path + '/node_disco_in.png',  size=(32, 16)),

            f'{CLI_TYP_DIGI}-CONN-OUT':      get_image(CFG_gui_conn_hist_path + '/digi_conn_out.png',  size=(32, 16)),
            f'{CLI_TYP_DIGI}-CONN-IN':       get_image(CFG_gui_conn_hist_path + '/digi_conn_in.png',   size=(32, 16)),
            f'{CLI_TYP_DIGI}-DISCO-OUT':     get_image(CFG_gui_conn_hist_path + '/digi_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_DIGI}-DISCO-IN':      get_image(CFG_gui_conn_hist_path + '/digi_disco_in.png',  size=(32, 16)),

            f'{CLI_TYP_NO_CLI}-CONN-OUT':    get_image(CFG_gui_conn_hist_path + '/digi_conn_out.png',  size=(32, 16)),
            f'{CLI_TYP_NO_CLI}-CONN-IN':     get_image(CFG_gui_conn_hist_path + '/digi_conn_in.png',   size=(32, 16)),
            f'{CLI_TYP_NO_CLI}-DISCO-OUT':   get_image(CFG_gui_conn_hist_path + '/digi_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_NO_CLI}-DISCO-IN':    get_image(CFG_gui_conn_hist_path + '/digi_disco_in.png',  size=(32, 16)),

            f'{CLI_TYP_PIPE}-CONN-OUT':      get_image(CFG_gui_conn_hist_path + '/pipe_conn_out.png',  size=(32, 16)),
            f'{CLI_TYP_PIPE}-CONN-IN':       get_image(CFG_gui_conn_hist_path + '/pipe_conn_in.png',   size=(32, 16)),
            f'{CLI_TYP_PIPE}-DISCO-OUT':     get_image(CFG_gui_conn_hist_path + '/pipe_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_PIPE}-DISCO-IN':      get_image(CFG_gui_conn_hist_path + '/pipe_disco_in.png',  size=(32, 16)),

            f'{CLI_TYP_BOX}-CONN-OUT':       get_image(CFG_gui_conn_hist_path + '/bbs_conn_out.png',  size=(32, 16)),
            f'{CLI_TYP_BOX}-CONN-IN':        get_image(CFG_gui_conn_hist_path + '/bbs_conn_in.png',   size=(32, 16)),
            f'{CLI_TYP_BOX}-DISCO-OUT':      get_image(CFG_gui_conn_hist_path + '/bbs_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_BOX}-DISCO-IN':       get_image(CFG_gui_conn_hist_path + '/bbs_disco_in.png',  size=(32, 16)),

            f'{CLI_TYP_TASK_FWD}-CONN-OUT': get_image(CFG_gui_conn_hist_path + '/fwd_conn_out.png',  size=(32, 16)),
            f'{CLI_TYP_TASK_FWD}-CONN-IN':  get_image(CFG_gui_conn_hist_path + '/fwd_conn_in.png',   size=(32, 16)),
            f'{CLI_TYP_TASK_FWD}-DISCO-OUT':get_image(CFG_gui_conn_hist_path + '/fwd_disco_out.png', size=(32, 16)),
            f'{CLI_TYP_TASK_FWD}-DISCO-IN': get_image(CFG_gui_conn_hist_path + '/fwd_disco_in.png',  size=(32, 16)),

            f'{CLI_TYP_CONVERSE}-CONN-OUT':    get_image(CFG_gui_conn_hist_path + '/conv_conn_out.png',    size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-CONN-IN':     get_image(CFG_gui_conn_hist_path + '/conv_conn_in.png',     size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-DISCO-OUT':   get_image(CFG_gui_conn_hist_path + '/conv_disco_out.png',   size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-DISCO-IN':    get_image(CFG_gui_conn_hist_path + '/conv_disco_in.png',    size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-CONN-INTER':  get_image(CFG_gui_conn_hist_path + '/conv_conn_inter.png',  size=(32, 16)),
            f'{CLI_TYP_CONVERSE}-DISCO-INTER': get_image(CFG_gui_conn_hist_path + '/conv_disco_inter.png', size=(32, 16)),

        }
        logger.info("GUI: Init FWD-Q-Tree-Icon Tab 16x16")
        self._fwd_q_flag_icons  = {
            'F':       get_image(CFG_aprs_icon_path + '/1-26.png',      size=(16, 16)),
            '$':       get_image(CFG_aprs_icon_path + '/0-82.png',      size=(16, 16)),
            'S+':      get_image(CFG_gui_icon_path +  '/status_ok.png', size=(16, 16)),
            'S-':      get_image(CFG_aprs_icon_path + '/1-06.png',      size=(16, 16)),
            'S=':      get_image(CFG_aprs_icon_path + '/0-67.png',      size=(16, 16)),
            'R':       get_image(CFG_aprs_icon_path + '/1-65.png',      size=(16, 16)),
            'H':       get_image(CFG_aprs_icon_path + '/0-72.png',      size=(16, 16)),
            'EE':      get_image(CFG_aprs_icon_path + '/1-78.png',      size=(16, 16)),
        }
        self._fwd_q_flag_icons.update(
            {
                'SW' : self._fwd_q_flag_icons['S='],
                'EO' : self._fwd_q_flag_icons['EE']
            }
        )
        logger.info("GUI: Init Icon Tabs. Done")
        #####################
        # Global Cache Tab
        """
        self._global_cache_tab = dict(
            tkMapView_cache={},
        )
        """
        #####################
        # Buffer
        self.connect_history    = POPT_CFG.load_guiPARM_main().get('gui_parm_connect_history', {})
        self._mon_pack_buff     = deque([] * 10000, maxlen=10000)
        #####################
        # GUI VARS
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
        # Stat INFO (Name,QTH usw)
        self._stat_info_name_var     = tk.StringVar(self.main_win)
        self._stat_info_qth_var      = tk.StringVar(self.main_win)
        self._stat_info_loc_var      = tk.StringVar(self.main_win)
        self._stat_info_typ_var      = tk.StringVar(self.main_win)
        self._stat_info_sw_var       = tk.StringVar(self.main_win)
        self._stat_info_timer_var    = tk.StringVar(self.main_win)
        self._stat_info_encoding_var = tk.StringVar(self.main_win)
        self._stat_info_status_var   = tk.StringVar(self.main_win)
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
        self.mon_pid_var            = tk.StringVar(self.main_win)
        self.mon_dec_aprs_var       = tk.BooleanVar(self.main_win)
        self.mon_dec_dist_var       = tk.BooleanVar(self.main_win)
        self.mon_dec_nr_var         = tk.BooleanVar(self.main_win)
        self.mon_dec_hex_var        = tk.BooleanVar(self.main_win)
        self.mon_port_on_vars       = {}
        all_ports = self._port_handler.ax25_ports
        for port_id in all_ports:
            self.mon_port_on_vars[port_id] = tk.BooleanVar(self.main_win)
            self.mon_port_on_vars[port_id].set(all_ports[port_id].monitor_out)
        self.mon_port_var.set('0')
        # Monitor Tree
        self._mon_tree_port_filter_var       = tk.StringVar(self.main_win, value='')
        self._mon_tree_to_call_filter_var    = tk.StringVar(self.main_win, value='')
        self._mon_tree_fm_call_filter_var    = tk.StringVar(self.main_win, value='')
        #self._mon_tree_ctl_packet_filter_var = tk.StringVar(self.main_win, value='')
        #self._mon_tree_pid_packet_filter_var = tk.StringVar(self.main_win, value='')
        ##############
        # Controlling
        self._ch_alarm      = False
        self.channel_index  = 1
        self._mon_mode      = 0
        self._tracer_alarm  = False
        ####################
        self._quit          = False
        self._init_state    = 0
        self._thread_gc: list[threading.Thread] = []    # Thread Garbage colletor
        self._win_gc                            = []
        # GUI PARAM
        self._parm_btn_blink_time               = 1  # s
        self._parm_rx_beep_cooldown             = 2  # s
        # Tasker
        self._parm_non_prio_task_timer          = 0.25  # s
        self._parm_non_non_prio_task_timer      = 1  # s
        self._parm_non_non_non_prio_task_timer  = 5  # s
        self._non_prio_task_timer               = time.time()
        self._non_non_prio_task_timer           = time.time()
        self._non_non_non_prio_task_timer       = time.time()
        self._tasker_q_timer                    = time.time()
        self._win_gc_task_timer                 = time.time() + 1
        # Tasker Q
        self._get_tasker_q_can_run              = lambda start_time, run_time: bool(run_time > time.time() - start_time)
        self._tasker_q                          = []
        self._tasker_q_prio                     = []
        #
        self._flip025                           = True
        # #### Tester
        # self._parm_test_task_timer = 60  # 5        # s
        # self._test_task_timer = time.time()
        ########################################
        ############################
        # Window
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
        self.block_list_win         = None
        #self.routingTab_win         = None
        ####################################
        ####################################
        # Window Text Buffers & Channel Vars
        logger.info('GUI: Channel Vars Init')
        self._channel_vars = {}
        self._init_Channel_Vars()
        ######################################
        # ....
        self._main_pw       = ttk.PanedWindow(self.main_win, orient='horizontal')
        self._main_pw.pack(fill='both', expand=True)

        l_frame             = ttk.Frame(self._main_pw)
        self._r_frame       = ttk.Frame(self._main_pw)
        r_pack_frame        = ttk.Frame(self._r_frame)
        l_frame.pack(      fill='both', expand=True)
        self._r_frame.pack(fill='both', expand=True)
        r_pack_frame.pack( fill='both', expand=True)
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
        ch_btn_frame.pack(side='bottom', fill='both', )
        self._init_ch_btn_frame(ch_btn_frame)
        ###########################################
        # Input Output TXT Frames and Status Bar
        self._pw = ttk.PanedWindow(l_frame, orient='vertical', )
        self._pw.pack(side='bottom', expand=1, fill='both')
        # Upper
        self._TXT_upper_frame   = ttk.Frame(self._pw, borderwidth=0, height=20)
        # Mid
        self._TXT_mid_frame     = ttk.Frame(self._pw, borderwidth=0, )
        # Lower
        self._TXT_lower_frame   = ttk.Frame(self._pw, borderwidth=0, )
        # Pack it
        self._TXT_upper_frame.pack(side='bottom', expand=1, fill='both')
        self._TXT_mid_frame.pack(  side='bottom', expand=1, fill='both')
        self._TXT_lower_frame.pack(side='bottom', expand=1, fill='both')
        self._mon_tree_frame = None
        self._mon_pw         = None
        txtWin_pos_cfg  = POPT_CFG.get_guiCFG_textWin_pos()
        winPos_cfgTab = {
            0: self._init_TXT_frame_up,
            1: self._init_TXT_frame_mid,
            2: self._init_TXT_frame_low,
        }
        self._inp_txt = winPos_cfgTab[txtWin_pos_cfg[0]]()
        self._qso_txt = winPos_cfgTab[txtWin_pos_cfg[1]]()
        self._mon_txt = winPos_cfgTab[txtWin_pos_cfg[2]](is_monitor=True)

        if self._mon_tree_frame is not None:
            self._init_mon_tree(self._mon_tree_frame)

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
        conn_btn_frame.pack(expand=False, pady=5, fill='x')
        self._init_btn(conn_btn_frame)
        ######################################################################
        # Pane Tabbed Frame
        self._side_pw = ttk.PanedWindow(r_pack_frame, orient='vertical', )
        self._side_pw.pack(expand=True, pady=5, fill='both')
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
        logger.info('GUI: BW-Plot Init')
        self._bw_plot_x_scale   = []
        self._bw_plot_lines     = {}
        self._init_bw_plot(bw_plot_frame)
        ###########################
        # set KEY BINDS
        self._set_binds()
        self._set_keybinds()
        # Menubar
        self._init_menubar()
        # Right-CLick
        self._init_r_click_men()
        # set Ch Btn Color
        self.ch_status_update()
        # Init Vars fm CFG
        logger.info('GUI: Parm/CFG Init')
        self._init_GUI_vars_fm_CFG()
        self._init_PARM_vars()
        self._set_CFG()
        # Text Tags
        self._all_tag_calls = []
        logger.info('GUI: Text-Tag Init')
        self.set_text_tags()
        # .....
        self._update_qso_Vars()
        ############################
        self._monitor_start_msg()
        ############################
        self._Pacman.update_plot_f_ch(self.channel_index)
        ############################
        logger.info('GUI: Status-Bar Text Init')
        self._status_text_tab = {}
        for k, col in STATUS_BG.items():
            status_text = get_strTab(k, POPT_CFG.get_guiCFG_language(), warning=False)
            self._status_text_tab[k] = status_text, col
        ##########################################
        # Menubar fix if app starts in fullscreen
        geom = self.main_win.winfo_geometry()
        self.main_win.geometry(geom)
        self._load_pw_pos()
        #################################
        # set GUI Var to Port Handler
        self._port_handler.set_gui(self)
        #######################
        # LOOP LOOP LOOP
        self.main_win.after(GUI_TASKER_NOT_BURN_DELAY, self._tasker)
        logger.info('GUI: Init Done')
        logger.info("GUI: Unblocking Ports")
        self._port_handler.unblock_all_ports()
        logger.info('GUI: Start Tasker')
        self.main_win.mainloop()

    ##############################################################
    def __del__(self):
        pass

    def _destroy_win(self):
        if self._quit:
            return
        self._set_port_blocking(1)
        self._port_handler.disco_all_Conn()
        self._quit = True
        self._port_handler.close_sound_PH()
        self._thread_gc += SOUND.get_sound_thread()
        self._sysMsg_to_monitor_task(self._getTabStr('mon_end_msg1'))
        self._port_handler.disco_all_Conn()
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
            self.block_list_win,
            #self.routingTab_win,
        ]:
            if hasattr(wn, 'destroy_win'):
                wn.destroy_win()
            if hasattr(wn, 'destroy'):
                wn.destroy()

        logger.info('GUI: Closing GUI: Save GUI Vars & Parameter.')
        self._sysMsg_to_monitor_task('Saving GUI Vars & Parameter.')
        self.save_GUIvars()
        self._save_parameter()
        self._save_pw_pos()
        self._save_Channel_Vars()
        logger.info('GUI: Closing GUI: Closing Ports.')
        self._sysMsg_to_monitor_task('Closing Ports.')
        threading.Thread(target=self._port_handler.close_popt).start()
        #self.main_win.update_idletasks()
        #self._loop_delay = 800
        #logger.info('GUI: Closing GUI: Done')

    def save_GUIvars(self):
        #########################
        # GUI-Vars to cfg
        guiCfg = POPT_CFG.load_guiPARM_main()
        # guiCfg['gui_lang'] = int(self.language)
        guiCfg['gui_cfg_sound']             = bool(self.setting_sound.get())
        guiCfg['gui_cfg_beacon']            = bool(self.setting_bake.get())
        guiCfg['gui_cfg_rx_echo']           = bool(self.setting_rx_echo.get())
        # guiCfg['gui_cfg_tracer']          = bool(self.setting_tracer.get())
        guiCfg['gui_cfg_tracer']            = False
        guiCfg['gui_cfg_auto_tracer']       = bool(self.setting_auto_tracer.get())
        guiCfg['gui_cfg_dx_alarm']          = bool(self.setting_dx_alarm.get())
        guiCfg['gui_cfg_noty_bell']         = bool(self.setting_noty_bell.get())
        guiCfg['gui_cfg_sprech']            = bool(self.setting_sprech.get())
        guiCfg['gui_cfg_mon_encoding']      = str(self.setting_mon_encoding.get())
        guiCfg['gui_cfg_mon_scroll']        = bool(self.mon_scroll_var.get())
        guiCfg['gui_cfg_mon_dec_aprs']      = bool(self.mon_dec_aprs_var.get())
        guiCfg['gui_cfg_mon_dec_nr']        = bool(self.mon_dec_nr_var.get())
        guiCfg['gui_cfg_mon_dec_hex']       = bool(self.mon_dec_hex_var.get())
        guiCfg['gui_cfg_mon_dec_distance']  = bool(self.mon_dec_dist_var.get())
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
        current_ch_vars.output_win_tags = get_all_tags(self._qso_txt)
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
        guiCfg = POPT_CFG.load_guiPARM_main()
        self.setting_sound.set(guiCfg.get('gui_cfg_sound', False))
        self.setting_bake.set(guiCfg.get('gui_cfg_beacon', False))
        self.setting_rx_echo.set(guiCfg.get('gui_cfg_rx_echo', False))
        self.set_rxEcho_icon(self.setting_rx_echo.get())
        self._port_handler.rx_echo_on = bool(self.setting_rx_echo.get())
        """
        if is_linux() and not is_macos():
            self.setting_sprech.set(guiCfg.get('gui_cfg_sprech', False))
        else:
            self.setting_sprech.set(False)
        """
        self.setting_sprech.set(guiCfg.get('gui_cfg_sprech', False))
        """"""
        self.setting_tracer.set(guiCfg.get('gui_cfg_tracer', False))
        self.setting_auto_tracer.set(guiCfg.get('gui_cfg_auto_tracer', False))
        self.setting_dx_alarm.set(guiCfg.get('gui_cfg_dx_alarm', True))
        self.setting_noty_bell.set(guiCfg.get('gui_cfg_noty_bell', False))
        self.setting_mon_encoding.set(guiCfg.get('gui_cfg_mon_encoding', 'Auto'))
        self.mon_scroll_var.set(guiCfg.get('gui_cfg_mon_scroll', True))
        self.mon_dec_hex_var.set(guiCfg.get('gui_cfg_mon_dec_hex', False))
        self.mon_dec_nr_var.set(guiCfg.get('gui_cfg_mon_dec_nr', True))
        self.mon_dec_dist_var.set(guiCfg.get('gui_cfg_mon_dec_distance', True))
        self.mon_dec_aprs_var.set(guiCfg.get('gui_cfg_mon_dec_aprs', True))
        # OWN Loc and QTH
        #self.own_loc = guiCfg.get('gui_cfg_locator', '')
        #self.own_qth = guiCfg.get('gui_cfg_qth', '')
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

        if hasattr(self._mon_pw, 'sashpos'):
            self._mon_pw.sashpos(0, guiCfg.get('gui_parm_mon_pw_pos', 200))  # Default: 200 Pixel

    def _save_pw_pos(self):
        if self._mon_mode:
            return
        text_pan_pos_cfg = []
        for pan_id in range(2):
            text_pan_pos_cfg.append(int(self._pw.sashpos(pan_id)))

        guiCfg = POPT_CFG.load_guiPARM_main()
        guiCfg['gui_parm_main_pan_pos'] = int(self._main_pw.sashpos(0))
        guiCfg['gui_parm_side_pan_pos'] = int(self._side_pw.sashpos(0))
        guiCfg['gui_parm_text_pan_pos'] = tuple(text_pan_pos_cfg)
        guiCfg['gui_parm_main_height']  = int(self.main_win.winfo_height())
        guiCfg['gui_parm_main_width']   = int(self.main_win.winfo_width())
        if hasattr(self._mon_pw, 'sashpos'):
            guiCfg['gui_parm_mon_pw_pos'] = int(self._mon_pw.sashpos(0))
        POPT_CFG.save_guiPARM_main(guiCfg)

    ###############################################################
    # GUI Init Stuff
    def _init_bw_plot(self, frame):
        """Cleanup by Grok3-AI"""
        # Precompute x-scale (0 to 10 minutes, 60 steps at 10-second intervals)
        self._bw_plot_x_scale = [i / 6 for i in range(60)]  # 60 steps over 10 minutes

        # Create figure and axis
        self._bw_fig, self._ax = plt.subplots(dpi=100)
        self._bw_fig.subplots_adjust(left=0.1, right=0.95, top=0.99, bottom=0.15)
        self._ax.axis([0, 10, 0, 100])  # X: 0-10 min, Y: 0-100% occupancy

        # Styling
        fg, bg = COLOR_MAP.get(self.style_name, ('black', 'lightgrey'))
        self._bw_fig.set_facecolor(bg)
        self._ax.set_facecolor('#191621')
        self._ax.xaxis.label.set_color(fg)
        self._ax.yaxis.label.set_color(fg)
        self._ax.tick_params(axis='x', colors=fg)
        self._ax.tick_params(axis='y', colors=fg)
        self._ax.set_xlabel(self._getTabStr('minutes'))
        self._ax.set_ylabel(self._getTabStr('occup'))

        # Embed in Tkinter
        self._canvas = FigureCanvasTkAgg(self._bw_fig, master=frame)
        self._canvas.get_tk_widget().pack(side=tk.TOP, expand=True, fill='both')
        self._canvas.draw()  # Initial draw

    def _init_menubar(self):
        menubar = tk.Menu(self.main_win, tearoff=False)
        self.main_win.config(menu=menubar)
        #########################################################################
        # Menü 1 "Verbindungen"
        MenuVerb = tk.Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('new_conn'), command=self.open_new_conn_win)
        MenuVerb.add_command(label=self._getTabStr('disconnect'), command=self._disco_conn)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('disconnect_all'), command=self._disco_all)
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('port_unblock_all'),
                             command=lambda: self._set_port_blocking(0) )
        MenuVerb.add_command(label=self._getTabStr('port_block_ignore_all'),
                             command=lambda: self._set_port_blocking(1))
        MenuVerb.add_command(label=self._getTabStr('port_block_reject_all'),
                             command=lambda: self._set_port_blocking(2))
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('quit'), command=self._destroy_win)
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
        MenuEdit.add_command(label=self._getTabStr('clean_qso_win'), command=self.clear_channel_vars,
                             underline=0)
        MenuEdit.add_command(label=self._getTabStr('clean_mon_win'), command=self._clear_monitor_data,
                             underline=0)

        MenuEdit.add_separator()
        MenuEdit.add_command(label=self._getTabStr('clean_all_qso_win'), command=self._clear_all_Channel_vars,
                             underline=0)
        menubar.add_cascade(label=self._getTabStr('edit'), menu=MenuEdit, underline=0)
        ####################################################################
        # Menü 3 "Tools"
        MenuTools = tk.Menu(menubar, tearoff=False)
        MenuTools.add_command(label="MH", command=self.open_MH_win, underline=0)
        MenuTools.add_command(label=self._getTabStr('statistic'),
                              command=lambda: self.open_window('PortStat'),
                              underline=1)
        MenuTools.add_separator()
        MenuTools.add_command(label="User-DB Tree",
                              command=lambda: self.open_window('userDB_tree'),
                              underline=0)
        MenuTools.add_command(label=self._getTabStr('user_db'),
                              command=lambda: self.open_user_db_win(),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('locator_calc'),
                              command=lambda: self.open_window('locator_calc'),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label="FT-Manager",
                              command=lambda: self._open_settings_window('ft_manager'),
                              underline=0)
        MenuTools.add_command(label=self._getTabStr('send_file'),
                              command=lambda: self.open_window('ft_send'),
                              underline=0)
        MenuTools.add_separator()
        MenuTools.add_command(label=self._getTabStr('linkholder'),
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
        MenuTools.add_command(label='Block List',
                              command=lambda: self.open_BlockList_win(),
                              underline=0)
        MenuTools.add_separator()

        MenuTools.add_command(label='Kaffèmaschine',
                              command=lambda: self._kaffee(),
                              underline=0)

        menubar.add_cascade(label=self._getTabStr('tools'), menu=MenuTools, underline=0)

        ###################################################################
        # Menü 4 Einstellungen
        MenuSettings = tk.Menu(menubar, tearoff=False)

        MenuSettings.add_command(label=self._getTabStr('settings'),
                                 command=lambda: self._open_settings_window('all_sett'),
                                 underline=0)
        MenuSettings.add_separator()

        MenuSettings.add_command(label='Dual-Port',
                                 command=lambda: self.open_window('dualPort_settings'),
                                 underline=0)

        menubar.add_cascade(label=self._getTabStr('settings'), menu=MenuSettings, underline=0)
        ########################################################################
        # APRS Menu
        MenuAPRS = tk.Menu(menubar, tearoff=False)
        MenuAPRS.add_command(label=self._getTabStr('aprs_mon'),
                             command=lambda: self.open_window('aprs_mon'),
                             underline=0)
        #MenuAPRS.add_command(label="Beacon Tracer", command=self.open_be_tracer_win,
        #                     underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=self._getTabStr('wx_window'),
                             command=lambda: self.open_window('wx_win'),
                             underline=0)
        MenuAPRS.add_command(label=self._getTabStr('pn_msg'),
                             command=lambda: self.open_window('aprs_msg'),
                             underline=0)
        MenuAPRS.add_separator()
        MenuAPRS.add_command(label=self._getTabStr('settings'),
                             command=lambda: self._open_settings_window('aprs_sett'),
                             underline=0)
        # MenuAPRS.add_separator()
        menubar.add_cascade(label="APRS", menu=MenuAPRS, underline=0)
        ################################################################
        # BBS/PMS
        MenuBBS = tk.Menu(menubar, tearoff=False)
        MenuBBS.add_command(label=self._getTabStr('new_msg'),
                            command=lambda: self.open_window('pms_new_msg'),
                            underline=0)
        MenuBBS.add_command(label=self._getTabStr('msg_center'),
                            command=lambda: self.open_window('pms_msg_center'),
                            underline=0)

        MenuBBS.add_separator()
        MenuBBS.add_command(label=self._getTabStr('fwd_list'),
                            command=lambda: self.open_window('pms_fwq_q'),
                            underline=0)
        MenuBBS.add_command(label=self._getTabStr('fwd_path'),
                            command=lambda: self.open_window('fwdPath'),
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
                            command=lambda: self._open_settings_window('pms_setting'),
                            underline=0) # pms_all_sett
        """
        MenuBBS.add_command(label=self._getTabStr('settings'),
                            command=lambda: self._open_settings_window('pms_all_sett'),
                            underline=0)
        menubar.add_cascade(label='PMS/BBS', menu=MenuBBS, underline=0)
        #########################################################################
        # Menü 5 Hilfe
        MenuHelp = tk.Menu(menubar, tearoff=False)
        # MenuHelp.add_command(label="Hilfe", command=lambda: False, underline=0)
        MenuHelp.add_command(label=self._getTabStr('keybind'),
                             command=lambda: self._open_settings_window('keybinds'),
                             underline=0)
        MenuHelp.add_separator()
        MenuHelp.add_command(label=self._getTabStr('about'),
                             command=lambda: self._open_settings_window('about'),
                             underline=0)
        menubar.add_cascade(label=self._getTabStr('help'), menu=MenuHelp, underline=0)

    def _init_r_click_men(self):
        # Input
        inp_txt_men = ContextMenu(self._inp_txt)
        inp_txt_men.add_item(self._getTabStr('cut'),  self._cut_select)
        inp_txt_men.add_item(self._getTabStr('copy'), self._copy_select)
        inp_txt_men.add_item(self._getTabStr('past'), self._clipboard_past)
        inp_txt_men.add_item(self._getTabStr('select_all'), self._select_all)
        inp_txt_men.add_separator()
        # inp_txt_men.add_item(self._getTabStr('save_to_file'), self._save_to_file)
        inp_txt_men.add_item(self._getTabStr('past_f_file'),  self._insert_fm_file)
        inp_txt_men.add_separator()
        actions_submenu = inp_txt_men.add_submenu("F-Text")
        actions_submenu.add_command(label="F1",  command=lambda : self._insert_ftext_fm_menu(1))
        actions_submenu.add_command(label="F2",  command=lambda : self._insert_ftext_fm_menu(2))
        actions_submenu.add_command(label="F3",  command=lambda : self._insert_ftext_fm_menu(3))
        actions_submenu.add_command(label="F4",  command=lambda : self._insert_ftext_fm_menu(4))
        actions_submenu.add_command(label="F5",  command=lambda : self._insert_ftext_fm_menu(5))
        actions_submenu.add_command(label="F6",  command=lambda : self._insert_ftext_fm_menu(6))
        actions_submenu.add_command(label="F7",  command=lambda : self._insert_ftext_fm_menu(7))
        actions_submenu.add_command(label="F8",  command=lambda : self._insert_ftext_fm_menu(8))
        actions_submenu.add_command(label="F9",  command=lambda : self._insert_ftext_fm_menu(9))
        actions_submenu.add_command(label="F10", command=lambda : self._insert_ftext_fm_menu(10))
        actions_submenu.add_command(label="F11", command=lambda : self._insert_ftext_fm_menu(11))
        actions_submenu.add_command(label="F12", command=lambda : self._insert_ftext_fm_menu(12))
        inp_txt_men.add_separator()
        inp_txt_men.add_item(self._getTabStr('linkholder'),
                             lambda: self._open_settings_window('l_holder'))
        inp_txt_men.add_item(label=self._getTabStr('send_file'),
                             command=lambda: self.open_window('ft_send'))
        inp_txt_men.add_item(label="Priv",
                             command=lambda: self.do_priv())
        inp_txt_men.add_separator()
        inp_txt_men.add_item(label=self._getTabStr('user_db'),
                             command=lambda: self.open_user_db_win())
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
                             lambda: self._open_settings_window('l_holder'))
        out_txt_men.add_item(label=self._getTabStr('send_file'),
                             command=lambda: self.open_window('ft_send'))
        out_txt_men.add_item(label="Priv",
                             command=lambda: self.do_priv())
        out_txt_men.add_separator()
        out_txt_men.add_item(label=self._getTabStr('user_db'),
                             command=lambda: self.open_user_db_win())
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

    def _init_btn(self, frame):
        # btn_upper_frame = tk.Frame(frame)
        # btn_upper_frame.pack(anchor='w', fill='x', expand=True)
        self._conn_btn = tk.Button(frame,
                                   text="Connect",
                                   bg="green",
                                   width=8,
                                   command=self.open_new_conn_win,
                                   relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                   highlightthickness=0,
                                   )
        self._conn_btn.pack(side='left')

        self._mon_btn = tk.Button(frame,
                                  text="Monitor",
                                  bg="yellow",
                                  width=8,
                                  command=lambda: self.switch_channel(0),
                                  relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                  highlightthickness=0,
                                  )
        self._mon_btn.pack(side='left', padx=2)

    def _init_ch_btn_frame(self, root_frame):
        btn_font = ("fixedsys", 8,)
        ch_btn_frame = ttk.Frame(root_frame, )
        ch_btn_frame.pack(side='top', fill='both', expand=True)

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
            ch_btn.pack( side='left', anchor="center", expand=True, fill='x')
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

    def _init_TXT_frame_up(self, is_monitor=False):
        # guiCFG          = POPT_CFG.load_guiPARM_main()
        text_frame      = ttk.Frame(self._TXT_upper_frame)
        if is_monitor:
            self._mon_pw = ttk.Panedwindow(text_frame, orient='vertical')
            self._mon_pw.pack(fill='both', expand=True)

            mon_txt_f = ttk.Frame(self._mon_pw)
            mon_tab_f = ttk.Frame(self._mon_pw)
            mon_txt_f.pack(fill='both', expand=True)
            mon_tab_f.pack(fill='both', expand=True)
            self._mon_pw.add(mon_txt_f, weight=1)
            self._mon_pw.add(mon_tab_f, weight=0)
            self._mon_tree_frame = mon_tab_f
        else:
            mon_txt_f = text_frame

        inp_txt         = tk.Text(mon_txt_f,
                      #background=guiCFG.get('gui_cfg_vor_bg_col', 'black'),
                      #foreground=guiCFG.get('gui_cfg_vor_col', 'white'),
                      font=(FONT, self.text_size),
                      insertbackground=TXT_INP_CURSOR_CLR,
                      height=30,
                      width=5,
                      bd=0,
                      relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                      highlightthickness=0,
                      )
        #inp_txt.tag_config("send",
        #                         foreground=guiCFG.get('gui_cfg_vor_tx_col', '#25db04'),
        #                         background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        inp_scrollbar = ttk.Scrollbar(
            mon_txt_f,
            orient='vertical',
            command=inp_txt.yview
        )
        inp_txt.pack(side='left', fill='both',  expand=True)
        inp_scrollbar.pack(side='left', fill='y',     expand=False)
        inp_txt.config(yscrollcommand=inp_scrollbar.set)
        # self.in_txt_win.insert(tk.END, "Inp")
        ##############
        # Status Frame
        status_frame = ttk.Frame(self._TXT_upper_frame, height=18)
        status_frame.pack( side='bottom', fill='x'   , expand=False)
        text_frame.pack(   side='bottom', fill='both', expand=True)

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
        #ts_f        = ttk.Frame(status_frame, width=20)

        name_f.pack(side='left', expand=True)
        stat_f.pack(side='left', expand=False)
        nack_f.pack(side='left', expand=False)
        vsvr_f.pack(side='left', expand=True)
        n2_f.pack(  side='left', expand=True)
        t1_f.pack(  side='left', expand=True)
        t2_f.pack(  side='left', expand=True)
        rtt_f.pack( side='left', expand=True)
        t3_f.pack(  side='left', expand=True)
        rx_beep_f.pack(side='left', expand=False)
        #ts_f.pack(  side='left', expand=False)

        fg, bg = self._get_colorMap()
        tk.Label(name_f,
                textvariable=self._status_name_var,
                font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                foreground=fg,
                bg=bg,
                width=10
              ).pack(side='left', anchor='w')

        self._status_status = tk.Label(stat_f,
                                    textvariable=self._status_status_var,
                                    font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                    bg=bg,
                                    foreground=STAT_BAR_TXT_CLR,
                                    #width=8
                                    )
        self._status_status.pack()

        self._status_unack = tk.Label(nack_f,
                                    textvariable=self._status_unack_var,
                                    foreground=STAT_BAR_TXT_CLR,
                                    font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                    bg=bg,
                                    #width=8
                                   )
        self._status_unack.pack(side='left', anchor='w', expand=True)

        tk.Label(vsvr_f,
              textvariable=self._status_vs_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side='left', anchor='w')

        self._status_n2 = tk.Label(n2_f,
                                textvariable=self._status_n2_var,
                                font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                bg=bg,
                                foreground=fg,
                                width=5
                                )
        self._status_n2.pack(side='left', anchor='w')

        tk.Label(t1_f,
              textvariable=self._status_t1_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side='left', anchor='w')
        # PARM T2
        tk.Label(t2_f,
              textvariable=self._status_t2_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side='left', anchor='w')
        # RTT
        tk.Label(rtt_f,
              textvariable=self._status_rtt_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side='left', anchor='w')

        tk.Label(t3_f,
              textvariable=self._status_t3_var,
              font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
              bg=bg,
              foreground=fg
              ).pack(side='left', anchor='w')
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
        self._rx_beep_box.pack(side='left', anchor='w')
        # TODO Checkbox Time Stamp
        """
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
        # self._ts_box_box.pack(side='left', anchor='w') # TODO
        """
        return inp_txt

    def _init_TXT_frame_mid(self, is_monitor=False):
        text_frame = ttk.Frame(self._TXT_mid_frame)
        if is_monitor:
            self._mon_pw = ttk.Panedwindow(text_frame, orient='vertical')
            self._mon_pw.pack(fill='both', expand=True)

            mon_txt_f = ttk.Frame(self._mon_pw)
            mon_tab_f = ttk.Frame(self._mon_pw)
            mon_txt_f.pack(fill='both', expand=True)
            mon_tab_f.pack(fill='both', expand=True)
            self._mon_pw.add(mon_txt_f, weight=1)
            self._mon_pw.add(mon_tab_f, weight=0)
            self._mon_tree_frame = mon_tab_f
        else:
            mon_txt_f = text_frame


        stat_frame = ttk.Frame(self._TXT_mid_frame, height=1)
        stat_frame.pack(side='bottom', fill='x',    expand=False)
        text_frame.pack(side='bottom', fill='both', expand=True)
        out_txt = tk.Text(mon_txt_f,
                              background=DEF_QSO_SYSMSG_BG,
                              foreground=DEF_QSO_SYSMSG_FG,
                              font=(FONT, self.text_size),
                              height=30,
                              width=5,
                              bd=0,
                              borderwidth=0,
                              #state="disabled",
                                relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                highlightthickness=0,

                          )
        # out_txt.tag_config("input", foreground="white")
        out_scrollbar = ttk.Scrollbar(
            mon_txt_f,
            orient='vertical',
            command=out_txt.yview
        )
        out_txt.pack(      side='left', fill='both', expand=True)
        out_scrollbar.pack(side='left', fill='y',    expand=False)
        out_txt.config(yscrollcommand=out_scrollbar.set)
        ###############################################
        # Status bar
        name_f = ttk.Frame(stat_frame)
        qth_f  = ttk.Frame(stat_frame)
        loc_f  = ttk.Frame(stat_frame)
        typ_f  =  tk.Frame(stat_frame, bg="#0ed8c3")
        sw_f   =  tk.Frame(stat_frame, bg="#ffd444")
        stat_f = ttk.Frame(stat_frame)
        time_f = ttk.Frame(stat_frame)
        enc_f  = ttk.Frame(stat_frame)

        name_f.pack(side='left', expand=True,  anchor="center")
        qth_f.pack( side='left', expand=True,  anchor="center")
        loc_f.pack( side='left', expand=True,  anchor="center", padx=5)
        typ_f.pack( side='left', expand=True,  anchor="center", fill='x')
        sw_f.pack(  side='left', expand=True,  anchor="center", fill='x')
        stat_f.pack(side='left', expand=False, anchor="center")
        time_f.pack(side='left', expand=False, anchor="center", padx=7)
        enc_f.pack( side='left', expand=False, anchor="center", fill='x')

        fg, bg = self._get_colorMap()

        name_label = ttk.Label(name_f,
                               textvariable=self._stat_info_name_var,
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
                             textvariable=self._stat_info_qth_var,
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
                             textvariable=self._stat_info_loc_var,
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
            self._stat_info_typ_var,
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
        stat_typ.pack(fill='x', expand=True, padx=6)

        tk.Label(sw_f,
                 textvariable=self._stat_info_sw_var,
                 #width=18,
                 bg="#ffd444",
                 # fg="red3",
                 height=1,
                 borderwidth=0,
                 border=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                 highlightthickness=0,
                 ).pack(fill='x', expand=True, padx=6)

        self.status_label = tk.Label(stat_f,
                                     textvariable=self._stat_info_status_var,
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
                  textvariable=self._stat_info_timer_var,
                  #width=6,
                  # height=1,
                  borderwidth=0,
                  border=0,
                  # bg="steel blue",
                  # fg="red3",
                  font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,)
                  ).pack(fill='x', expand=True)
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            enc_f,
            self._stat_info_encoding_var,
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
        txt_encoding_ent.pack(fill='x', expand=False)

        return out_txt

    def _init_TXT_frame_low(self, is_monitor=False):
        mon_frame = ttk.Frame(self._TXT_lower_frame)
        mon_frame.pack(side='bottom', fill='both', expand=True)
        if is_monitor:
            self._mon_pw = ttk.Panedwindow(mon_frame, orient='vertical')
            self._mon_pw.pack(fill='both', expand=True)

            mon_txt_f = ttk.Frame(self._mon_pw)
            mon_tab_f = ttk.Frame(self._mon_pw)
            mon_txt_f. pack(fill='both', expand=True)
            mon_tab_f. pack(fill='both', expand=True)
            self._mon_pw.add(mon_txt_f, weight=1)
            self._mon_pw.add(mon_tab_f, weight=0)
            self._mon_tree_frame = mon_tab_f
        else:
            mon_txt_f = mon_frame

        mon_txt = tk.Text(mon_txt_f,
                              background=MON_SYS_MSG_CLR_BG,
                              foreground=MON_SYS_MSG_CLR_BG,
                              font=(FONT, self.text_size),
                              height=30,
                              width=5,
                              bd=0,
                              borderwidth=0,
                              # state="disabled",
                              relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                              highlightthickness=0,
                              )
        mon_scrollbar = ttk.Scrollbar(
            mon_txt_f,
            orient='vertical',
            command=mon_txt.yview
        )
        mon_txt.pack(side='left', fill='both', expand=True)
        mon_scrollbar.pack(side='left', fill='y',    expand=False)
        mon_txt.config(yscrollcommand=mon_scrollbar.set)
        ################
        #self._init_mon_tree(mon_tab_f)
        return mon_txt

    def _init_mon_tree(self, frame: ttk.Frame):
        columns = (
            'time',
            'port',
            'from',
            'to',
            'via',
            'typ',
            'pid',
            'nr_ns',
            'cmd_poll',
            'size',
            'data',
        )
        mon_tree_pw = ttk.Panedwindow(frame, orient='horizontal')
        mon_tree_pw.pack(fill='both', expand=True)
        #
        mon_f_main = ttk.Frame(mon_tree_pw)
        mon_f_1 = ttk.Frame(mon_f_main)
        mon_f_2 = ttk.Frame(mon_f_main)
        mon_f_1.pack(fill='both', expand=True)
        mon_f_2.pack(fill='x', expand=False)
        #
        mon_filter_f = ttk.Frame(mon_tree_pw)
        mon_filter_f.pack(fill='x', expand=False)
        #
        mon_tree_pw.add(mon_f_main,    weight=0)
        mon_tree_pw.add(mon_filter_f,  weight=1)

        ###################################################
        self._mon_tree = ttk.Treeview(mon_f_1, columns=columns, show='tree headings', height=2)
        self._mon_tree.pack(side='left', fill='both', expand=True)

        self._mon_tree.heading('#0', text="RX/TX")
        self._mon_tree.heading('time', text=self._getTabStr('time'))
        self._mon_tree.heading('port', text='Port')
        self._mon_tree.heading('from', text=self._getTabStr('from'))
        self._mon_tree.heading('to', text=self._getTabStr('to'))
        self._mon_tree.heading('via', text='Via')
        self._mon_tree.heading('typ', text='CTL')
        self._mon_tree.heading('pid', text='PID')
        self._mon_tree.heading('nr_ns', text='NS/NR')
        self._mon_tree.heading('cmd_poll', text='CMD/POLL')
        self._mon_tree.heading('size', text='Bytes')
        self._mon_tree.heading('data', text='Data')

        self._mon_tree.column("#0",       anchor='w', stretch=False, width=50)
        self._mon_tree.column("time",     anchor='w', stretch=False, width=70)
        self._mon_tree.column("port",     anchor='center', stretch=False, width=30)
        self._mon_tree.column("from",     anchor='w', stretch=False, width=85)
        self._mon_tree.column("to",       anchor='w', stretch=False, width=85)
        self._mon_tree.column("via",      anchor='w', stretch=False, width=120)
        self._mon_tree.column("typ",      anchor='center', stretch=False, width=50)
        self._mon_tree.column("pid",      anchor='center', stretch=False, width=100)
        self._mon_tree.column("nr_ns",    anchor='center', stretch=False, width=45)
        self._mon_tree.column("cmd_poll", anchor='center', stretch=False, width=50)
        self._mon_tree.column("size",     anchor='center', stretch=False, width=45)
        self._mon_tree.column("data",     anchor='w', stretch=False,  width=700)

        #for el in list(range(100)):
        #    mon_tree.insert('', 'end', values=(el,))
        # Vertikale Scrollbar
        scrollbar_y = ttk.Scrollbar(mon_f_1, orient='vertical', command=self._mon_tree.yview)
        self._mon_tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side='left', fill='y')

        # Horizontale Scrollbar
        scrollbar_x = ttk.Scrollbar(mon_f_2, orient='horizontal', command=self._mon_tree.xview)
        self._mon_tree.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.pack(fill='x')
        ###################################################
        ttk.Label(mon_filter_f, text="Filter").pack()
        port_f     = ttk.Frame(mon_filter_f)
        fm_call_f  = ttk.Frame(mon_filter_f)
        to_call_f  = ttk.Frame(mon_filter_f)
        btn_pack_f = ttk.Frame(mon_filter_f)
        port_f.pack(    fill='x', expand=False, pady=5)
        fm_call_f.pack( fill='x', expand=False, pady=5)
        to_call_f.pack( fill='x', expand=False, pady=5)
        btn_pack_f.pack(fill='x', expand=False, pady=5)
        # Port
        ttk.Label(port_f, text='Port').pack(side='left', anchor='w', padx=5)
        opt = ['', ''] + [str(x) for x in list(POPT_CFG.get_port_CFGs().keys())]
        ttk.OptionMenu(port_f,
                       self._mon_tree_port_filter_var,
                       *opt,
                       command=lambda e: self._monitor_tree_on_filter_chg()).pack(side='left', anchor='w')
        # FM Call
        ttk.Label(fm_call_f, text='From Call').pack(side='left', anchor='w', padx=5)
        ttk.Entry(fm_call_f,
                  textvariable=self._mon_tree_fm_call_filter_var,
                  width=30).pack(side='left', anchor='w', expand=True)
        # TO Call
        ttk.Label(to_call_f, text='To Call      ').pack(side='left', anchor='w', padx=5)
        ttk.Entry(to_call_f,
                  textvariable=self._mon_tree_to_call_filter_var,
                  width=30).pack(side='left', anchor='w', expand=True)
        # BTN
        ttk.Button(btn_pack_f,
                   text='Update',
                   command=lambda: self._monitor_tree_on_filter_chg()
                   ).pack(side='left', anchor='w', padx=10)
        ttk.Button(btn_pack_f,
                   text='Reset',
                   command=lambda: self._monitor_tree_on_filter_reset()
                   ).pack(side='right', anchor='e', padx=10)
    #######################################
    # Text Tags
    def set_text_tags(self):
        self._all_tag_calls = []
        all_stat_cfg = POPT_CFG.get_stat_CFGs()
        if all_stat_cfg:
            self._qso_txt.configure(state="normal")
        guiCFG = POPT_CFG.load_guiPARM_main()

        for call in list(all_stat_cfg.keys()):
            stat_cfg = all_stat_cfg[call]
            tx_fg = stat_cfg.get('stat_parm_qso_col_text_tx', DEF_STAT_QSO_TX_COL)
            tx_bg = stat_cfg.get('stat_parm_qso_col_bg', DEF_STAT_QSO_BG_COL)

            rx_fg = stat_cfg.get('stat_parm_qso_col_text_rx', DEF_STAT_QSO_RX_COL)

            tx_tag = 'TX-' + str(call)
            rx_tag = 'RX-' + str(call)
            self._all_tag_calls.append(str(call))

            self._qso_txt.tag_config(tx_tag,
                                     foreground=tx_fg,
                                     background=tx_bg,
                                     selectbackground=tx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._qso_txt.tag_config(rx_tag,
                                     foreground=rx_fg,
                                     background=tx_bg,
                                     selectbackground=rx_fg,
                                     selectforeground=tx_bg,
                                     )
            self._qso_txt.tag_config('SYS-MSG',
                                     foreground=DEF_QSO_SYSMSG_FG,
                                     background=DEF_QSO_SYSMSG_BG,
                                     selectbackground=DEF_QSO_SYSMSG_FG,
                                     selectforeground=DEF_QSO_SYSMSG_BG,
                                     )
            self._qso_txt.tag_config('TX-NOCALL',
                                     foreground='#ffffff',
                                     background='#000000',
                                     selectbackground='#ffffff',
                                     selectforeground='#000000',
                                     )
            self._qso_txt.tag_config('RX-NOCALL',
                                     foreground='#000000',
                                     background='#ffffff',
                                     selectbackground='#000000',
                                     selectforeground='#ffffff',
                                     )

        self._qso_txt.configure(state="disabled")
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
        ##
        #self._mon_txt.configure(state="normal")
        self._inp_txt.configure(foreground=guiCFG.get('gui_cfg_vor_col', 'white'), background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        self._inp_txt.tag_config("send",
                                 foreground=guiCFG.get('gui_cfg_vor_tx_col', '#25db04'),
                                 background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        self._inp_txt.tag_raise(tk.SEL)
        self._qso_txt.tag_raise(tk.SEL)
        self._mon_txt.tag_raise(tk.SEL)

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
        #self.main_win.bind('<Control-v>', lambda event: self._clipboard_past())
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
            self._inp_txt.insert(tk.INSERT, '\n')
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
        ch_enc = self._stat_info_encoding_var.get()
        if any((ch_enc == enc, not ch_enc)):
            text = text.decode(enc, 'ignore')
        else:
            text = text.decode(ch_enc, 'ignore')
        conn = self.get_conn()
        text = replace_StringVARS(input_string=text, port_handler=self.get_PH_mainGUI(), connection=conn)
        text = zeilenumbruch_lines(text)
        self._inp_txt.insert(tk.INSERT, text)
        self.see_end_inp_win()
        return

    def _insert_ftext_fm_menu(self, f_nr: int):
        try:
            text, enc = POPT_CFG.get_f_text_fm_id(f_id=f_nr)
        except ValueError:
            return
        if not text:
            return
        ch_enc = self._stat_info_encoding_var.get()
        if any((ch_enc == enc, not ch_enc)):
            text = text.decode(enc, 'ignore')
        else:
            text = text.decode(ch_enc, 'ignore')
        conn = self.get_conn()
        text = replace_StringVARS(input_string=text, port_handler=self.get_PH_mainGUI(), connection=conn)
        text = zeilenumbruch_lines(text)
        self._inp_txt.insert(tk.INSERT, text)
        self.see_end_inp_win()
        return

    ##########################
    # Start Message in Monitor
    def _monitor_start_msg(self):
        # tmp_lang = int(self.language)
        # self.language = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        SOUND.sprech(random.choice(WELCOME_SPEECH), wait=False)
        ban = POPT_BANNER.format(VER)
        tmp = ban.split('\r')
        for el in tmp:
            self._sysMsg_to_monitor_task(el)
        self._sysMsg_to_monitor_task('Python Other Packet Terminal ' + VER)
        for stat in POPT_CFG.get_stat_CFG_keys():
            self._sysMsg_to_monitor_task(self._getTabStr('mon_start_msg1').format(stat))
        all_ports = self._port_handler.ax25_ports
        for port_k in all_ports.keys():
            msg = self._getTabStr('mon_start_msg2')
            if all_ports[port_k].device_is_running:
                msg = self._getTabStr('mon_start_msg3')
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_k)
            self._sysMsg_to_monitor_task('Info: Port {}: {} - {} {}'
                                   .format(port_k,
                                           port_cfg.get('parm_PortName', ''),
                                           port_cfg.get('parm_PortTyp', ''),
                                           msg
                                           ))
            self._sysMsg_to_monitor_task('Info: Port {}: Parameter: {} | {}'
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
        self._qso_txt.configure(font=(FONT, self.text_size), )
        self._mon_txt.configure(font=(FONT, self.text_size), )

    def _decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self._inp_txt.configure(font=(FONT, self.text_size), )
        self._qso_txt.configure(font=(FONT, self.text_size), )
        self._mon_txt.configure(font=(FONT, self.text_size), )

    ##########################
    # Clipboard Stuff
    def _copy_select(self):
        if self._qso_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._qso_txt.selection_get())
            self._qso_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._inp_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._inp_txt.selection_get())
            self._inp_txt.tag_remove(tk.SEL, "1.0", tk.END)
        elif self._mon_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._mon_txt.selection_get())
            self._mon_txt.tag_remove(tk.SEL, "1.0", tk.END)

    def _cut_select(self):
        if self._inp_txt.tag_ranges("sel"):
            self.main_win.clipboard_clear()
            self.main_win.clipboard_append(self._inp_txt.selection_get())
            self._inp_txt.delete('sel.first', 'sel.last')
            self._inp_txt.see(tk.INSERT)

    def _clipboard_past(self):
        try:
            clp_brd = self.main_win.clipboard_get()
        except tk.TclError:
            logger.warning("GUI: TclError Clipboard no STR")
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
        if not self.channel_index:
            return
        if not self._qso_txt.tag_ranges("sel"):
            return
        selected_text = self._qso_txt.selection_get()
        selected_text += '\n'
        #self._inp_txt.tag_remove('send', '0.0', 'end')
        self._inp_txt.insert('insert', '\n')
        #ind = self._inp_txt.index(tk.INSERT)
        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))
        self._inp_txt.insert('insert', selected_text)
        #self._inp_txt.tag_add('send', ind, str(self._inp_txt.index(tk.INSERT)))
        self._snd_text()
        self._qso_txt.tag_remove(tk.SEL, "1.0", tk.END)
        self._inp_txt.tag_remove('send', "0.0", str(self._inp_txt.index('end')))
        self._inp_txt.tag_add('send', "0.0", str(self._inp_txt.index('end')))

    ##########################
    # Pre-write Text Stuff
    def _insert_fm_file(self):
        data = open_file_dialog(self.main_win)
        if not data:
            return
        ch_enc = self._stat_info_encoding_var.get()
        if not ch_enc:
            data = data.decode('UTF-8', 'ignore')
        else:
            data = data.decode(ch_enc, 'ignore')
        data = zeilenumbruch_lines(data)
        self._inp_txt.insert(tk.INSERT, data)
        self.see_end_inp_win()
        return

    def _save_to_file(self):
        data = self._qso_txt.get('1.0', tk.END)
        # FIXME Codec : UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1090-1097: ordinal not in range(256)
        save_file_dialog(data, self.main_win)

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

    def _clear_inpWin(self):
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]
        chVars = self._channel_vars[self.channel_index]
        chVars.input_win                = ''
        chVars.input_win_tags           = {}
        chVars.input_win_index          = '1.0'
        chVars.input_win_cursor_index   = tk.INSERT

    def _clear_qsoWin(self):
        self._qso_txt.configure(state='normal')
        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.configure(state='disabled')
        # del self._channel_vars[self.channel_index]

        chVars = self._channel_vars[self.channel_index]
        chVars.output_win       = ''
        chVars.output_win_tags  = {}
        chVars.t2speech_buf     = ''

    def clear_channel_vars(self):
        self._qso_txt.configure(state='normal')
        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]

        self._channel_vars[self.channel_index] = ChVars()
        self._update_qso_Vars()

    def _clear_all_Channel_vars(self):
        self._qso_txt.configure(state='normal')
        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.configure(state='disabled')
        self._inp_txt.delete('1.0', tk.END)
        # del self._channel_vars[self.channel_index]
        for ch_id in self._channel_vars.keys():
            self._channel_vars[ch_id] = ChVars()
        self._update_qso_Vars()

    ######################################################################
    # Sound TODO !!!
    def _kanal_switch(self):
        """ Triggered on CH BTN Click """
        #threading.Thread(target=self._kanal_switch_sprech_th).start()
        self._kanal_switch_sprech_th()

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
                SOUND.sprech('{} {} . {} .'.format(self._getTabStr('channel'),
                                                   self.channel_index,
                                                   conn.to_call_str), wait=False)

        else:
            if not ch_vars.t2speech:
                ch_vars.t2speech_buf = ''
                SOUND.sprech('{} {} .'.format(self._getTabStr('channel'), self.channel_index), wait=False)
            elif ch_vars.t2speech_buf:
                if SOUND.sprech(ch_vars.t2speech_buf):
                    ch_vars.t2speech_buf = ''
                else:
                    SOUND.sprech('{} {} .'.format(self._getTabStr('channel'), self.channel_index), wait=False)
            else:
                SOUND.sprech('{} {} .'.format(self._getTabStr('channel'), self.channel_index), wait=False)

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
                            SOUND.sound_play(self._root_dir + CFG_sound_RX_BEEP)

    # Sound
    ######################################################################
    #
    ######################################################################
    # TASKER
    def _tasker(self):  # MAINLOOP
        timer_overall    = time.time()
        self._tasker_queue(timer_overall)
        self._win_gc_tasker()
        if self._quit:
            if self._tasker_quit():
                return
        else:
            self._tasker_prio()
            update_needed = self._tasker_025_sec()
            update_needed = any((self._tasker_1_sec(), update_needed))
            if not update_needed:
                update_needed = self._tasker_5_sec()
            if update_needed:
                self.main_win.update_idletasks()
        t_delta      = time.time() - timer_overall
        if t_delta > GUI_TASKER_TIME_D_UNTIL_BURN:
            logger.warning("GUI-Tasker Overload: !!")
            logger.warning(f"  GUI-Tasker   : Loop needs {round(t_delta, 2)}s to process !!")
            self.main_win.after(GUI_TASKER_BURN_DELAY, self._tasker)
        else:
            self.main_win.after(GUI_TASKER_NOT_BURN_DELAY, self._tasker)

    def _tasker_quit(self):
        if not self._port_handler.get_ph_end():
            return False
        #if self._tasker_q:
        #    logger.info('GUI: Still jobs in _tasker_q')
        #    return False
        n = 0
        for gc_thread in self._thread_gc:
            if hasattr(gc_thread, 'is_alive'):
                if gc_thread.is_alive():
                    n += 1
        if n:
            logger.info(f'GUI: Waiting for {n} Threads ! Please Wait ...')
            return False
        self.main_win.quit()
        try:
            self.main_win.destroy()
            logger.info('GUI: Closing GUI: Done')
        except Exception as ex:
            logger.warning(ex)
        return True

    def _tasker_queue(self, start_time: time.time):
        if all((not self._tasker_q, not self._tasker_q_prio)):
            return False

        if self._tasker_q_prio:
            while all((self._tasker_q_prio, self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME))):
                task, arg = self._tasker_q_prio.pop(0)
                if task == 'sysMsg_to_monitor':
                    self._sysMsg_to_monitor_task(arg)
                elif self._quit:
                    continue
                elif task == 'conn_btn_update':
                    self._conn_btn_update_task()
                elif task == 'ch_status_update':
                    self._ch_status_update_task()
                elif task == 'on_channel_status_change':
                    self._on_channel_status_change_task()
                elif task == 'add_LivePath_plot':
                    node, ch_id, path = arg
                    self._add_LivePath_plot_task(node, ch_id, path)
                elif task == 'resetHome_LivePath_plot':
                    ch_id = arg
                    self._resetHome_LivePath_plot_task(ch_id)
                elif task == 'sysMsg_to_qso':
                    data, ch_index = arg
                    self.sysMsg_to_qso_task(data, ch_index)
                elif task == 'dx_alarm':
                    self._dx_alarm_task()
                elif task == 'tracer_alarm':
                    self._tracer_alarm_task()
                elif task == 'reset_tracer_alarm':
                    self._reset_tracer_alarm_task()
                elif task == 'reset_dx_alarm':
                    self._reset_dx_alarm_task()
                elif task == 'pmsMail_alarm':
                    self._pmsMail_alarm_task()
                elif task == 'reset_pmsMail_alarm':
                    self._reset_pmsMail_alarm_task()
                elif task == 'pmsFwd_alarm':
                    self._pmsFwd_alarm_task()
                elif task == 'reset_pmsFwd_alarm':
                    self._reset_pmsFwd_alarm_task()
                elif task == 'set_diesel':
                    self._set_diesel_task()
                elif task == 'reset_diesel':
                    self._reset_diesel_task()
                elif task == 'set_rxEcho_icon':
                    alarm_set = arg
                    self._set_rxEcho_icon_task(alarm_set)
                elif task == 'set_Beacon_icon':
                    alarm_set = arg
                    self._set_Beacon_icon_task(alarm_set)
                elif task == 'set_port_block_warning':
                    self._set_port_block_warning_task()
                elif task == 'reset_noty_bell_alarm':
                    self._reset_noty_bell_alarm_task()
                elif task == 'set_noty_bell':
                    ch_id, msg = arg
                    self._set_noty_bell_task(ch_id, msg)
                elif task == 'set_noty_bell_active':
                    self._set_noty_bell_active_task()
                elif task == 'set_aprsMail_alarm':
                    self._set_aprsMail_alarm_task()
                elif task == 'reset_aprsMail_alarm':
                    self._reset_aprsMail_alarm_task()
                elif task == 'update_aprs_spooler':
                    self._update_aprs_spooler_task()
                elif task == 'update_aprs_msg_win':
                    self._update_aprs_msg_win_task(arg)
                #elif task == 'update_tracer_win':
                #    self._update_tracer_win_task()

        if all((self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME), not self._quit , self._tasker_q)):
            # Non Prio
            while all((self._tasker_q, self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME))):
                task, arg = self._tasker_q.pop(0)
                if task == '_monitor_tree_update':
                    self._monitor_tree_update_task(arg)
                elif task == '_monitor_q_task':
                    self._monitor_q_task(arg)

        return True

    def _tasker_prio(self):
        """ Prio Tasks every Irritation """
        tasker_ret = False
        if hasattr(self._port_handler, 'tasker_gui_th'):
            # tasker_ret = any((self._port_handler.tasker_gui_th(), tasker_ret))
            timer = time.time()
            self._port_handler.tasker_gui_th()
            t_delta = time.time() - timer
            if t_delta > GUI_TASKER_TIME_D_UNTIL_BURN:
                logger.warning(f"PH-Tasker Overload: Loop needs {round(t_delta, 2)}s to process !!")
        if hasattr(self.userDB_tree_win, 'tasker'):
            tasker_ret = any((self.userDB_tree_win.tasker(), tasker_ret))

        if hasattr(self.userdb_win, 'tasker'):
            tasker_ret = any((self.userdb_win.tasker(), tasker_ret))

        tasker_ret = any((self._monitor_task(),     tasker_ret))
        tasker_ret = any((self._ais_monitor_task(), tasker_ret))
        tasker_ret = any((self._mh_win_task(),      tasker_ret))
        return tasker_ret

    def _tasker_025_sec(self):
        """ 0.25 Sec """
        if time.time() > self._non_prio_task_timer:
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            #####################
            # self._aprs_task()
            # self._monitor_task()
            ret = self._dualPort_monitor_task()
            ret = any((self._update_qso_win(),    ret))
            ret = any((self._SideFrame_tasker(),  ret))
            ret = any((self._update_status_bar(), ret))
            if self._flip025:
                ret = any((self._AlarmIcon_tasker05(), ret))
            #####################
            self._flip025 = not self._flip025
            return ret
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
            if hasattr(self.routingTab_win, 'tasker'):
                self.routingTab_win.tasker()
            """
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
    def _add_tasker_q(self, fnc: str, arg, prio=True):
        if prio:
            if (fnc, None) in self._tasker_q_prio:
                return
            self._tasker_q_prio.append(
                (fnc, arg)
            )
        else:
            if (fnc, None) in self._tasker_q:
                return
            self._tasker_q.append(
                (fnc, arg)
            )

    def add_thread_gc(self, thread: threading.Thread):
        self._thread_gc.append(thread)

    def add_win_gc(self, trash_win):
        self._win_gc.append(trash_win)

    def _win_gc_tasker(self):
        if time.time() < self._win_gc_task_timer:
            return
        self._win_gc_task_timer = time.time() + 1
        for trash_win in list(self._win_gc):
            if hasattr(trash_win, 'is_destroyed'):
                if trash_win.is_destroyed:
                    if hasattr(trash_win, 'all_dead'):
                        if trash_win.all_dead():
                            self._win_gc.remove(trash_win)
                            del trash_win
                            continue
            if hasattr(trash_win, 'tasker'):
                trash_win.tasker()


    ######################################################################
    def update_aprs_spooler(self):
        self._add_tasker_q("update_aprs_spooler", None)

    def _update_aprs_spooler_task(self):
        if hasattr(self.aprs_pn_msg_win, 'update_spooler_tree'):
            self.aprs_pn_msg_win.update_spooler_tree()

    def update_aprs_msg_win(self, aprs_pack):
        self._add_tasker_q("update_aprs_msg_win", aprs_pack)

    def _update_aprs_msg_win_task(self, aprs_pack):
        if hasattr(self.aprs_pn_msg_win, 'update_aprs_msg'):
            self.aprs_pn_msg_win.update_aprs_msg(aprs_pack)

    def _aprs_wx_tree_task(self):
        ais = self._port_handler.get_aprs_ais()
        if not hasattr(ais, "get_update_tr"):
            return
        if not hasattr(self.wx_window, 'update_tree_data'):
            return
        update_tr = ais.get_update_tr()
        if update_tr:
            self._wx_update_tr = False
            self.wx_window.update_tree_data()

    def _ais_monitor_task(self):
        if hasattr(self.aprs_mon_win, 'tasker'):
           return self.aprs_mon_win.tasker()
        return False

    #######################################################################
    def _AlarmIcon_tasker05(self):
        if not hasattr(self._Alarm_Frame, 'AlarmIcon_tasker05'):
            return False
        self._Alarm_Frame.AlarmIcon_tasker05()
        return True

    def _AlarmIcon_tasker1(self):
        if not self._Alarm_Frame:
            return
        self._Alarm_Frame.AlarmIcon_tasker1()
        self._check_port_blocking_task()

    def _SideFrame_tasker(self):
        if self._flip025:
            return any((
                self.tabbed_sideFrame.tasker(),
                self.tabbed_sideFrame.on_ch_stat_change()
            ))

        return any((
            self.tabbed_sideFrame2.tasker(),
            self.tabbed_sideFrame2.on_ch_stat_change()
        ))

    def _check_port_blocking_task(self):
        if hasattr(self._port_handler, 'get_glb_port_blocking'):
            if not self._port_handler.get_glb_port_blocking():
                self._Alarm_Frame.set_PortBlocking(set_on=False)
            else:
                self._Alarm_Frame.set_PortBlocking(set_on=True, blinking=True)
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
            return True
        return False

    def _update_qso(self, conn):
        if not conn:
            return False
        if conn.ft_obj:
            # self.ch_status_update()
            return True
        if conn.rx_tx_buf_guiData:
            self._update_qso_spooler(conn)
            # self.ch_status_update()
            return True
        return False

    def _update_qso_spooler(self, conn):
        gui_buf = list(conn.rx_tx_buf_guiData)
        conn.rx_tx_buf_guiData = list(conn.rx_tx_buf_guiData[len(gui_buf):])
        for qso_data in gui_buf:
            if qso_data[0] == 'SYS':
                ch_id = conn.ch_index
                self.sysMsg_to_qso_task(qso_data[1], ch_id)
                #self._update_qso_tx(conn, qso_data[1])

            elif qso_data[0] == 'RX':
                self._update_qso_rx(conn, qso_data[1])
            else:
                self._update_qso_tx(conn, qso_data[1])

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
            self._qso_txt.configure(state="normal")
            ind = self._qso_txt.index('end-1c')
            self._qso_txt.insert('end', inp)
            ind2 = self._qso_txt.index('end-1c')
            if tag_name_tx:
                self._qso_txt.tag_add(tag_name_tx, ind, ind2)
            self._qso_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            # TODO Autoscroll
            if float(self._qso_txt.index(tk.END)) - float(self._qso_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
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
            logger.error(f"Conn: last Tag: {Ch_var.last_tag_name}")
            tag_name_rx = f'RX-{Ch_var.last_tag_name}'

        if self.channel_index == conn.ch_index:
            if Ch_var.t2speech:
                Ch_var.t2speech_buf += out.replace('\n', '')

            self._qso_txt.configure(state="normal")
            # configuring a tag called start
            ind = self._qso_txt.index('end-1c')
            self._qso_txt.insert('end', out)
            ind2 = self._qso_txt.index('end-1c')
            if tag_name_rx:
                self._qso_txt.tag_add(tag_name_rx, ind, ind2)

            self._qso_txt.configure(state="disabled",
                                    exportselection=True
                                    )
            # TODO Autoscroll
            if float(self._qso_txt.index(tk.END)) - float(self._qso_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
                self.see_end_qso_win()
        else:
            Ch_var.new_data_tr = True
            if Ch_var.t2speech:
                # TODO ?????????????????????????????????????????????
                Ch_var.t2speech_buf += '{} {} . {} . {}'.format(
                    self._getTabStr('channel'),
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

        self._qso_txt.configure(state="normal")

        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.insert(tk.END, ch_vars.output_win)
        self._qso_txt.configure(state="disabled")
        self._qso_txt.see(tk.END)

        self._inp_txt.delete('1.0', tk.END)
        self._inp_txt.insert(tk.END, ch_vars.input_win[:-1])
        set_all_tags(self._inp_txt, ch_vars.input_win_tags)
        set_all_tags(self._qso_txt, ch_vars.output_win_tags)
        set_new_tags(self._qso_txt, ch_vars.new_tags)
        ch_vars.new_tags = []
        self._inp_txt.mark_set("insert", ch_vars.input_win_cursor_index)
        self._inp_txt.see(tk.END)

        # self.main_class: gui.guiMainNew.TkMainWin
        if ch_vars.rx_beep_opt and self.channel_index:
            self._rx_beep_var.set(1)
            #self._rx_beep_box.select()
            self._rx_beep_box.configure(bg='green')
        else:
            self._rx_beep_var.set(0)
            #self._rx_beep_box.deselect()
            self._rx_beep_box.configure(bg=bg)

        if ch_vars.timestamp_opt and self.channel_index:
            self._ts_box_var.set(True)
            #self._ts_box_box.configure(bg='green')
        else:
            self._ts_box_var.set(False)
            #self._ts_box_box.configure(bg=bg)

    def sysMsg_to_qso(self, data, ch_index):
        self._add_tasker_q("sysMsg_to_qso", (data, ch_index))

    def sysMsg_to_qso_task(self, data, ch_index):
        if not data:
            return
        if 1 > ch_index > SERVICE_CH_START - 1:
            return
        data = data.replace('\r', '')
        data = f"\n    <{conv_time_DE_str()}>\n" + data + '\n'
        data = tk_filter_bad_chars(data)
        ch_vars = self.get_ch_var(ch_index=ch_index)
        tag_name = 'SYS-MSG'
        ch_vars.output_win += data
        if self.channel_index == ch_index:
            tr = False
            if float(self._qso_txt.index(tk.END)) - float(self._qso_txt.index("@0,0")) < 22:
                tr = True
            self._qso_txt.configure(state="normal")

            ind = self._qso_txt.index(tk.INSERT)
            self._qso_txt.insert('end', data)
            ind2 = self._qso_txt.index(tk.INSERT)
            self._qso_txt.tag_add(tag_name, ind, ind2)
            self._qso_txt.configure(state="disabled",
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
        self._add_tasker_q("sysMsg_to_monitor", var)

    def _sysMsg_to_monitor_task(self, var: str):
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
                SOUND.sprech(var[1], wait=False)

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
        if not mon_buff:
            return
        new_mon_buff = []
        for axframe_conf, port_conf, tx in mon_buff:
            port_id = port_conf.get('parm_PortNr', -1)
            axframe_conf['tx']        = tx
            axframe_conf['port']      = port_id
            axframe_conf['port_conf'] = port_conf
            new_mon_buff.append(axframe_conf)
            self._mon_pack_buff.append(dict(axframe_conf))

        """ Monitor Tree """
        self._monitor_tree_update(new_mon_buff)
        """ Monitor """
        self._add_tasker_q('_monitor_q_task',
                           new_mon_buff,
                           False)
        return True

    def _monitor_q_task(self, mon_batch: list):

        self._mon_txt.configure(state="normal")
        self._mon_txt_tags = set(self._mon_txt.tag_names(None))  # Cache Tags

        full_text = ""
        tags_to_add = []
        mon_conf = {
            "distance": bool(self.mon_dec_dist_var.get()),
            "aprs_dec": bool(self.mon_dec_aprs_var.get()),
            "nr_dec": bool(self.mon_dec_nr_var.get()),
            "hex_out": bool(self.mon_dec_hex_var.get()),
            "decoding": str(self.setting_mon_encoding.get()),
        }

        end_idx = self._mon_txt.index('end-1c')  # Cache Index
        for axframe in mon_batch:
            port_conf    = axframe.get('port_conf', {})
            tx           = axframe.get('tx'       , False)
            axframe_conf = axframe
            port_id = port_conf.get('parm_PortNr', -1)
            mon_conf['port_name'] = port_conf.get('parm_PortName', '')

            mon_str = monitor_frame_inp(axframe_conf, mon_conf)
            var = tk_filter_bad_chars(mon_str)
            full_text += var

            ind_start = f"{end_idx} + {len(full_text) - len(var)}c"
            tag = f"tx{port_id}" if tx else f"rx{port_id}"
            tags_to_add.append((tag, ind_start, f"{ind_start} + {len(var)}c"))

        # Batch-Insert
        self._mon_txt.insert(tk.END, full_text)

        # Batch-Tags
        for tag, start, end in tags_to_add:
            if tag in self._mon_txt_tags:
                self._mon_txt.tag_add(tag, start, end)

        # Periodisches Cleanup (statt pro Task)
        cut_len = int(self._mon_txt.index('end-1c').split('.')[0]) - PARAM_MAX_MON_LEN + 1
        if cut_len > 0:
            self._mon_txt.delete('1.0', f"{cut_len}.0")

        # Autoscroll
        tr = float(self._mon_txt.index(tk.END)) - float(self._mon_txt.index(tk.INSERT)) < 15
        if tr or self.mon_scroll_var.get():
            self._see_end_mon_win()

        self._mon_txt.configure(state="disabled", exportselection=True)
        return True

    def see_end_inp_win(self):
        self._inp_txt.see("end")

    def see_end_qso_win(self):
        self._qso_txt.see("end")

    def _see_end_mon_win(self):
        self._mon_txt.see("end")

    # END Monitor WIN
    ###############################################################
    ###############################################################
    # Monitor Tree
    def _monitor_tree_update(self, ax25pack_batch: list):
        self._add_tasker_q("_monitor_tree_update", ax25pack_batch, prio=False)

    def _monitor_tree_update_task(self, ax25pack_batch: list):
        is_scrolled_to_top  = self._mon_tree.yview()[0] == 0.0
        user_db             = self._port_handler.get_userDB()
        mh                  = self._get_mh()

        port_filter         = self._mon_tree_port_filter_var.get()
        fm_call_filter      = self._mon_tree_fm_call_filter_var.get().split(' ')
        to_call_filter      = self._mon_tree_to_call_filter_var.get().split(' ')

        fm_call_filter      = [str(x.upper()).replace(' ', '') for x in list(fm_call_filter)]
        to_call_filter      = [str(x.upper()).replace(' ', '') for x in list(to_call_filter)]

        for ax25pack_conf in ax25pack_batch:

            via = [f"{call}{'*' if c_bit else ''}" for call, c_bit in ax25pack_conf.get('via_calls_str_c_bit', [])]
            ns_nr  = f"{''  if ax25pack_conf.get('ctl_nr', -1) == -1 else ax25pack_conf.get('ctl_nr', -1)}"
            ns_nr += f"/{'' if ax25pack_conf.get('ctl_ns', -1) == -1 else ax25pack_conf.get('ctl_ns', -1)}"
            cmd_pl =  f"{'+'  if ax25pack_conf.get('ctl_cmd', False) else '-'}"
            cmd_pl += f"/{'+' if ax25pack_conf.get('ctl_pf',  False) else '-'}"
            pay_size  = len(ax25pack_conf.get('payload', b''))
            payload   = ax25pack_conf.get('payload', b'').decode('UTF-8', 'ignore')
            payload   = tk_filter_bad_chars(payload)
            payload   = payload.replace('\n', ' ').replace('\r', ' ')
            from_dist = user_db.get_distance(ax25pack_conf.get('from_call_str', -1))
            to_dist   = user_db.get_distance(ax25pack_conf.get('to_call_str', -1))
            from_call = ax25pack_conf.get('from_call_str', '')
            to_call   = ax25pack_conf.get('to_call_str', '')
            port      = ax25pack_conf.get('port', -1)
            ctl       = ax25pack_conf.get('ctl_flag', '')
            pid       = ax25pack_conf.get('pid_flag', '')

            while '' in fm_call_filter:
                fm_call_filter.remove('')
            while '' in to_call_filter:
                to_call_filter.remove('')
            #ctl_pack_filter  = self._mon_tree_ctl_packet_filter_var.get()
            #pid_pack_filter  = self._mon_tree_pid_packet_filter_var.get()

            if not all((
                any((all((port_filter,     port_filter     == str(port) )),     not port_filter)),
                any((all((fm_call_filter,  from_call       in fm_call_filter)), not fm_call_filter)),
                any((all((to_call_filter,  to_call         in to_call_filter)), not to_call_filter)),
                #all((ctl_pack_filter, ctl_pack_filter != ctl)),
                #all((pid_pack_filter, pid_pack_filter != pid)),
            )):
                return
            raw_from_call = str(from_call)
            raw_to_call   = str(to_call)
            if from_dist > 0:
                from_call += f'({from_dist}km)'

            if to_dist > 0:
                to_call += f'({to_dist}km)'

            tree_data = (
                ax25pack_conf.get('rx_time', datetime.datetime.now()).strftime('%H:%M:%S'),
                port,
                from_call,
                to_call,
                '>'.join(via),
                ctl,
                pid,
                ns_nr,
                cmd_pl,
                pay_size,
                payload,
            )
            index = 0

            is_tx = ax25pack_conf.get('tx', True)
            icon_k = {
                True:  'tx',
                False: 'rx',
            }.get(is_tx, True)

            """
                '', '-dx',
                '', '-term',
                '', '-node',
                '', '-bbs',
                '', '-block',
            """
            icon_k_k = ''
            # Is DX ?
            if not is_tx:
                is_dx = mh.is_dx_alarm_f_call(raw_from_call)
                if is_dx:
                    icon_k_k = '-dx'

            # Is to own Station ?
            block_list = POPT_CFG.get_block_list().get(port, {})
            if is_tx:
                own_station = POPT_CFG.get_stat_CFG_fm_call(raw_from_call.split('-')[0])
                block_state = block_list.get(raw_to_call.split('-')[0], 0)
            else:
                own_station = POPT_CFG.get_stat_CFG_fm_call(raw_to_call.split('-')[0])
                block_state = block_list.get(raw_from_call.split('-')[0], 0)

            if own_station:
                if block_state:
                    icon_k_k = '-block'
                else:
                    icon_k_k = dict(
                        USER=   '-term',
                        NODE=   '-node',
                        BOX=    '-bbs',
                    ).get(own_station.get('stat_parm_cli', ''), '')

            # Get Icon
            icon_k += icon_k_k
            image = self._rx_tx_icons.get(icon_k)
            tree_data_f = [tk_filter_bad_chars(el) if type(el) == str else el for el in tree_data]
            try:
                self._mon_tree.image_ref = image
                self._mon_tree.insert('', index, values=tree_data_f, image=image)

            except tk.TclError as ex:
                logger.warning("TCL Error in guiMain _monitor_tree_update")
                logger.warning(ex)
                continue

        # Begrenze die Anzahl der Einträge
        tree_items = self._mon_tree.get_children()
        if len(tree_items) > PARAM_MAX_MON_TREE_ITEMS:
            # Entferne die ältesten Einträge (am Ende der Liste)
            for item in tree_items[PARAM_MAX_MON_TREE_ITEMS:]:
                self._mon_tree.delete(item)

        if not is_scrolled_to_top:
            try:
                self._mon_tree.yview_scroll(1, "units")
            except tk.TclError:
                pass
            except Exception as e:
                null = e
                # logger.warning(e)
                pass

    def _monitor_tree_on_filter_chg(self):
        for i in self._mon_tree.get_children():
            self._mon_tree.delete(i)
        batch_len = MON_BATCH_TO_PROCESS * 2
        mon_buff = list(self._mon_pack_buff)
        while mon_buff:
            self._monitor_tree_update(mon_buff[:batch_len])
            mon_buff = mon_buff[batch_len:]

    def _monitor_tree_on_filter_reset(self):
        self._mon_tree_port_filter_var.set('')
        self._mon_tree_fm_call_filter_var.set('')
        self._mon_tree_to_call_filter_var.set('')
        self._monitor_tree_on_filter_chg()
    """
    def _monitor_tree_conn_selected(self):
        if not self._mon_tree.selection():
            return
        selected =  self._mon_tree.selection()[0]
        item     = self._mon_tree.item(selected)
        record     = item['values']
        call = record[3].split('(')[0]
        vias = record[5]
        vias = vias.replace('*', '').split('>')
        vias.reverse()
        vias = [x.split('(')[0] for x in list(vias)]
        vias = ' '.join(vias)
        port = record[2]


        if type(port) is str:
            port = int(port.split('-')[0])

        if vias:
            call = f'{call} {vias}'
        if not self.new_conn_win:
            self.open_new_conn_win()
        if self.new_conn_win:
            self.new_conn_win.preset_ent(call, port)
    """

    ###############################################################
    # Dual Port
    def _dualPort_monitor_task(self):
        if not hasattr(self.dualPortMon_win, 'dB_mon_tasker'):
            return False
        return self.dualPortMon_win.dB_mon_tasker()

    ###############################################################

    ###############################################################
    # Open Toplevel Win

    def open_link_holder_sett(self):
        #self.main_win.update_idletasks()
        self._open_settings_window('l_holder')

    def open_ft_manager(self, event=None):
        #self.main_win.update_idletasks()
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
            'aprs_sett': APRSSettingsMain,       # APRS Settings
            'ft_manager': FileTransferManager,  # FT Manager            # TODO move to open_window
            'pipe_sett': PipeToolSettings,      # Pipe Tool
            # 'user_db': UserDB,  # UserDB
            'l_holder': LinkHolderSettings,     # Linkholder
            'pms_all_sett': BBSSettingsMain,    # New PMS Settings
            'all_sett': SettingsMain,           # New All Settings
        }.get(win_key, '')
        if callable(settings_win):
            #self.main_win.update_idletasks()
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

            # TODO .......

        }.get(win_key, None)
        if not win_list:
            return
        if win_list[0]:
            if hasattr(win_list[0], 'lift'):
                win_list[0].lift()
            return
        if callable(win_list[1]):
            #self.main_win.update_idletasks()
            win_list[1](self)

    ##########################
    # UserDB
    def open_user_db_win(self, event=None, ent_key=''):
        if self.userdb_win is not None:
            return
        if not ent_key:
            conn = self.get_conn()
            if conn is not None:
                ent_key = conn.to_call_str
        #self.main_win.update_idletasks()
        self.userdb_win = UserDB(self, ent_key)

    ##########################
    # New Connection WIN
    def open_new_conn_win(self):
        self.open_window('new_conn')

    ######################
    # APRS Beacon Tracer
    """
    def open_be_tracer_win(self):
        self.reset_tracer_alarm()  # ??? PORTHANDLER set_tracerAlram ???
        if self.be_tracer_win is None:
            #self.main_win.update_idletasks()
            self.be_tracer_win = BeaconTracer(self)
    """

    ###################
    # MH WIN
    def open_MH_win(self):
        """MH WIN"""
        self.reset_tracer_alarm()  # ??? PORTHANDLER set_tracerAlram ???
        self._port_handler.set_dxAlarm(False)
        self.tabbed_sideFrame.reset_dx_alarm()
        self.tabbed_sideFrame2.reset_dx_alarm()
        if hasattr(self.mh_window, 'lift'):
            self.mh_window.lift()
            return
        MHWin(self)

    def _mh_win_task(self):
        if hasattr(self.mh_window, 'tasker'):
            return self.mh_window.tasker()
        return False

    ##################
    # Black List Win
    def open_BlockList_win(self):
        if hasattr(self.block_list_win, 'lift'):
            self.block_list_win.lift()
            return
        if self.block_list_win is not None:
            logger.error("self.block_list_win is not None. Try to close")
            if hasattr(self.block_list_win, 'close'):
                self.block_list_win.close()
                self.block_list_win = None
                return
        self.block_list_win = BlockList(self)

    ##################
    # Routing tab win
    """
    def open_RoutingTab_win(self):
        if hasattr(self.routingTab_win, 'lift'):
            self.routingTab_win.lift()
            return
        if not hasattr(self._port_handler, 'get_RoutingTable'):
            if hasattr(self.routingTab_win, 'close'):
                self.routingTab_win.close()
                self.routingTab_win = None
                return
        #RoutingTableWindow(self, self._port_handler.get_RoutingTable())
    """
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
        if messagebox.askokcancel(title=self._getTabStr('disconnect_all'),
                                  message=self._getTabStr('disconnect_all_ask'),
                                  parent=self.main_win):
            self._port_handler.disco_all_Conn()

    # DISCO ENDE
    #######################################################################
    #######################################################################
    # SEND TEXT OUT
    def _snd_text(self, event=None):
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

                txt_enc = self._stat_info_encoding_var.get()
                if station.user_db_ent:
                    txt_enc = station.user_db_ent.Encoding
                # ind = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'
                tmp_txt = self._inp_txt.get(ind, tk.INSERT)

                tmp_txt = (tmp_txt.replace('\n', '\r')).encode(txt_enc, 'ignore')
                station.send_data(tmp_txt)
                #self._update_qso_tx(station, tmp_txt)
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
        old_text = self._inp_txt.get(ind,  self._inp_txt.index(tk.INSERT))
        text = zeilenumbruch(old_text)
        if old_text == text:
            self._inp_txt.tag_remove('send', ind, tk.INSERT)
            return
        self._inp_txt.delete(ind,  self._inp_txt.index(tk.INSERT))
        self._inp_txt.insert(tk.INSERT, text)
        self._inp_txt.tag_remove('send', ind, tk.INSERT)

    # SEND TEXT OUT
    #######################################################################
    # BW Plot
    def _update_bw_mon(self):
        """Cleanup by Grok3-AI"""
        redraw_needed = False
        for port_id in self._port_handler.ax25_ports.keys():
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_id)
            baud = port_cfg.get('parm_baud', 1200)
            data = self.mh.get_bandwidth(port_id, baud)  # Annahme: gibt eine Liste zurück

            label = port_cfg.get('parm_PortName', f'Port {port_id}')

            if port_id not in self._bw_plot_lines:
                line, = self._ax.plot(self._bw_plot_x_scale, data, label=label)
                self._bw_plot_lines[port_id] = line
                self._ax.legend()
                redraw_needed = True
            else:
                # Umwandlung der aktuellen y-Daten in eine Liste für den Vergleich
                current_ydata = list(self._bw_plot_lines[port_id].get_ydata())
                if data != current_ydata:  # Direkter Listenvergleich
                    self._bw_plot_lines[port_id].set_ydata(data)
                    redraw_needed = True

        if redraw_needed:
            self._draw_bw_plot()


    def _draw_bw_plot(self):
        """Cleanup by Grok3-AI"""
        self._bw_fig.canvas.draw()
        self._bw_fig.canvas.flush_events()

    # END BW Plot
    #######################################################################
    #######################################################################
    # Conn Path Plot
    def add_LivePath_plot(self, node: str, ch_id: int, path=None):
        self._add_tasker_q("add_LivePath_plot", (node, ch_id, path))

    def _add_LivePath_plot_task(self, node: str, ch_id: int, path=None):
        if path is None:
            path = []
        # print(f"CH: {ch_id} self.CH_ID: {self.channel_index} - Node: {node} - Path: {path}")
        for digi in path:
            self._Pacman.change_node(node=digi, ch_id=ch_id)
        self._Pacman.change_node(node=node, ch_id=ch_id)
        if ch_id == self.channel_index:
            self._Pacman.update_plot_f_ch(ch_id=ch_id)

    def resetHome_LivePath_plot(self, ch_id: int):
        self._add_tasker_q("resetHome_LivePath_plot", ch_id)


    def _resetHome_LivePath_plot_task(self, ch_id: int):
        # print(f"CH: {ch_id} self.CH_ID: {self.channel_index} - RESET")
        self._Pacman.reset_last_hop(ch_id=ch_id)
        if ch_id == self.channel_index:
            #if not POPT_CFG.get_pacman_fix():
            self._Pacman.update_plot_f_ch(ch_id=ch_id)
    # ENDConn Path Plot
    #######################################################################

    def _kaffee(self):
        self._sysMsg_to_monitor_task('Hinweis: Hier gibt es nur Muckefuck !')
        SOUND.sprech('Gluck gluck gluck blubber blubber')
        #APRSymbolTab(self)
        # self.open_RoutingTab_win()
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
        if self._mon_mode:
            # self.channel_index = int(self.mon_mode)
            self._ch_btn_clk(int(self._mon_mode))
            self._mon_mode = 0
            self._mon_btn.configure(bg='yellow')
            self.ch_status_update()
            self._load_pw_pos()
            return

        self._mon_mode = int(self.channel_index)
        self._ch_btn_clk(0)
        self._mon_btn.configure(bg='green')
        self.ch_status_update()

    def switch_channel(self, ch_ind: int = 0):
        # Channel 0 = Monitor
        if not ch_ind:
            self._switch_monitor_mode()
        else:
            if self._mon_mode:
                self._mon_mode = int(ch_ind)
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
        self._add_tasker_q("conn_btn_update", None)

    def _conn_btn_update_task(self):
        conn = self.get_conn(self.channel_index)
        if conn:
            if self._conn_btn.cget('bg') != "red":
                self._conn_btn.configure(bg="red", text="Disconnect", command=self._disco_conn)
        elif self._conn_btn.cget('bg') != "green":
            self._conn_btn.configure(text="Connect", bg="green", command=self.open_new_conn_win)
        self._ch_btn_status_update()

    def ch_status_update(self):
        """ Triggerd when Connection Status has changed (Conn-accept, -end, -resset)"""
        self._add_tasker_q("ch_status_update", None)

    def _ch_status_update_task(self):
        self._ch_btn_status_update()
        self.on_channel_status_change()

    def _ch_btn_clk(self, ind: int):
        old_ch_vars = self.get_ch_var(ch_index=int(self.channel_index))
        old_ch_vars.input_win = self._inp_txt.get('1.0', tk.END)
        old_ch_vars.input_win_tags = get_all_tags(self._inp_txt)
        old_ch_vars.output_win_tags = get_all_tags(self._qso_txt)
        old_ch_vars.input_win_cursor_index = self._inp_txt.index(tk.INSERT)
        self.channel_index = ind
        self._update_qso_Vars()
        self.ch_status_update()
        self.conn_btn_update()
        self._reset_noty_bell()
        self._Pacman.update_plot_f_ch(self.channel_index)
        self._kanal_switch()  # Sprech

    def _reset_noty_bell(self):
        conn = self.get_conn(self.channel_index)
        if not conn:
            return
        if conn.noty_bell:
            conn.noty_bell = False
            self._port_handler.reset_noty_bell_PH()

    def reset_noty_bell_alarm(self):
        self._add_tasker_q("reset_noty_bell_alarm", None)

    def _reset_noty_bell_alarm_task(self):
        self._Alarm_Frame.set_Bell_alarm(False)
        self._Alarm_Frame.set_Bell_active(self.setting_noty_bell.get())

    def set_noty_bell(self, ch_id, msg=''):
        self._add_tasker_q("set_noty_bell", (ch_id, msg))

    def _set_noty_bell_task(self, ch_id, msg=''):
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
            msg = f"{conn.to_call_str} {self._getTabStr('cmd_bell_gui_msg')}"
        if messagebox.askokcancel(f"Bell {self._getTabStr('channel')} {ch_id}",
                                  msg, parent=self.main_win):
            if not self._quit:
                self.switch_channel(ch_id)

    def set_noty_bell_active(self):
        self._add_tasker_q("set_noty_bell_active", None)

    def _set_noty_bell_active_task(self):
        self._Alarm_Frame.set_Bell_active(self.setting_noty_bell.get())

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
                        self._set_ch_new_data_tr(i, False)
                else:
                    if self._get_ch_new_data_tr(i):
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

                if not self._get_ch_new_data_tr(i):
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
                        self._set_ch_new_data_tr(i, False)
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
        self._add_tasker_q("on_channel_status_change", None)

    def _on_channel_status_change_task(self):
        self.tabbed_sideFrame.on_ch_stat_change()
        self.tabbed_sideFrame2.on_ch_stat_change()
        self.update_station_info()

    def _update_stat_info_conn_timer(self):
        conn = self.get_conn()
        if conn is not None:
            if hasattr(conn, 'cli'):
                self._stat_info_timer_var.set(get_time_delta(conn.cli.time_start))
                return
        if self._stat_info_timer_var.get() != '--:--:--':
            self._stat_info_timer_var.set('--:--:--')

    def update_station_info(self):
        name = '-------'
        qth = '-------'
        loc = '------'
        # _dist = 0
        status = '-------'
        typ = '-----'
        sw = '---------'
        enc = 'UTF-8'
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
                status = CLI_TYP_DIGI
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', )
            elif conn.pipe is not None:
                status = CLI_TYP_PIPE
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', )
            elif conn.ft_obj is not None:
                status = f'{conn.ft_obj.dir} FILE'
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    # self.status_label.bind('<Button-1>', lambda: self._open_settings_window('ft_manager'))
                    self.status_label.bind('<Button-1>', self.open_ft_manager)
            else:
                status = ''
                try:
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
                except Exception as ex:
                    logger.error(ex)
                    status = '---'
                status += '----'
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', self.do_priv)
        elif self._stat_info_status_var.get() != status:
            self._stat_info_status_var.set(status)
            self.status_label.bind('<Button-1>', )
        """
        if _dist:
            loc += f" ({_dist} km)"
        """
        # if self.stat_info_status_var.get() != _status:
        #     self.stat_info_status_var.set(_status)
        if self._stat_info_name_var.get() != name:
            self._stat_info_name_var.set(name)
        if self._stat_info_qth_var.get() != qth:
            self._stat_info_qth_var.set(qth)
        if self._stat_info_loc_var.get() != loc:
            self._stat_info_loc_var.set(loc)
        if self._stat_info_typ_var.get() != typ:
            self._stat_info_typ_var.set(typ)
        if self._stat_info_sw_var.get() != sw:
            self._stat_info_sw_var.set(sw)
        if self._stat_info_encoding_var.get() != enc:
            self._stat_info_encoding_var.set(enc)

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
    def _update_status_bar(self):
        ret = False
        station = self.get_conn(self.channel_index)
        fg, bg = self._get_colorMap()
        if station is not None:
            from_call = str(station.my_call_str)
            status = station.zustand_tab[station.get_state()][1]
            # uid = station.ax25_out_frame.addr_uid
            n2 = station.n2
            unAck = f" nACK: {len(station.tx_buf_unACK.keys())} "
            vs_vr = f"VS/VR: {station.vr}/{station.vs}"
            n2_text = f"N2: {n2}"
            t1_text = f"T1: {max(0, int(station.t1 - time.time()))}"
            rtt_text = 'RTT: {:.1f}/{:.1f}'.format(station.RTT_Timer.rtt_last, station.RTT_Timer.rtt_average)
            t3_text = f"T3: {max(0, int(station.t3 - time.time()))}"
            if station.get_port_cfg().get('parm_T2_auto', True):
                t2_text = f"T2: {int(station.get_param_T2() * 1000)}A"
            else:
                t2_text = f"T2: {int(station.get_param_T2() * 1000)}"
            status_text, status_bg = self._status_text_tab.get(status, ('', bg))
            if status_text:
                status_text = f" {status_text} "
            ##
            if self._status_name_var.get() != from_call:
                self._status_name_var.set(from_call)
                ret = True

            if self._status_status_var.get() != status_text:
                self._status_status_var.set(status_text)
                self._status_status.configure(bg=status_bg)
                ret = True

            if self._status_unack_var.get() != unAck:
                self._status_unack_var.set(unAck)
                if len(station.tx_buf_unACK.keys()):
                    if self._status_unack.cget('bg') != 'yellow':
                        self._status_unack.configure(bg='yellow')
                else:
                    if self._status_unack.cget('bg') != 'green':
                        self._status_unack.configure(bg='green')
                ret = True

            if self._status_vs_var.get() != vs_vr:
                self._status_vs_var.set(vs_vr)
                ret = True
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
                ret = True

            if self._status_t1_var.get() != t1_text:
                self._status_t1_var.set(t1_text)
                ret = True

            if self._status_t2_var.get() != t2_text:
                self._status_t2_var.set(t2_text)
                ret = True

            if self._status_rtt_var.get() != rtt_text:
                self._status_rtt_var.set(rtt_text)
                ret = True

            if self._status_t3_var.get() != t3_text:
                self._status_t3_var.set(t3_text)
                ret = True
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
                ret = True
        return ret

    def _switch_mon_mode(self):
        txtWin_pos_cfg = POPT_CFG.get_guiCFG_textWin_pos()
        if self._mon_mode:
            try:
                if txtWin_pos_cfg == (1, 0, 2):
                    self._pw.remove(self._TXT_lower_frame)
                    self._pw.remove(self._TXT_mid_frame)
                elif txtWin_pos_cfg == (1, 2, 0):
                    self._pw.remove(self._TXT_upper_frame)
                    self._pw.remove(self._TXT_mid_frame)
                else:
                    self._pw.remove(self._TXT_upper_frame)
                    self._pw.remove(self._TXT_lower_frame)
            except tk.TclError:
                pass
            self._pw.add(self._TXT_upper_frame, weight=1)
            self._pw.add(self._TXT_mid_frame,   weight=1)
            self._pw.add(self._TXT_lower_frame, weight=1)
            self._load_pw_pos()

        else:
            self._save_pw_pos()
            if txtWin_pos_cfg == (1, 0, 2):
                self._pw.remove(self._TXT_upper_frame)

            elif txtWin_pos_cfg == (1, 2, 0):
                self._pw.remove(self._TXT_lower_frame)
            else:
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
                db_ent.TYP = self._stat_info_typ_var.get()
        else:
            self._stat_info_typ_var.set('-----')

    def _change_txt_encoding(self, event=None, enc=''):
        conn = self.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                if not enc:
                    enc = self._stat_info_encoding_var.get()
                db_ent.Encoding = enc
        else:
            self._stat_info_encoding_var.set('UTF-8')

    ##########################################
    #
    def get_free_channel(self, start_channel=1):
        if not start_channel:
            start_channel = 1
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

    def _get_ch_new_data_tr(self, ch_id):
        return bool(self.get_ch_var(ch_index=ch_id).new_data_tr)

    def _set_ch_new_data_tr(self, ch_id, state: bool):
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

    """
    def get_auto_tracer(self):
        ais_obj = self._port_handler.get_aprs_ais()
        if ais_obj is not None:
            return bool(ais_obj.be_auto_tracer_active)
        return False
    """

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

    #def update_tracer_win(self):
    #    self._add_tasker_q("update_tracer_win", None)

    #def _update_tracer_win_task(self):
    #    if hasattr(self.be_tracer_win, 'update_tree_data'):
    #        self.be_tracer_win.update_tree_data()

    ########
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
    # Alarm/Icon Frame
    def set_aprsMail_alarm(self):
        if self.aprs_pn_msg_win:
            self._add_tasker_q("reset_aprsMail_alarm", None)
        else:
            self._add_tasker_q("set_aprsMail_alarm", None)

    def _set_aprsMail_alarm_task(self):
        self._Alarm_Frame.set_aprsMail_alarm(True)

    def reset_aprsMail_alarm(self):
        self._add_tasker_q("reset_aprsMail_alarm", None)

    def _reset_aprsMail_alarm_task(self):
        self._Alarm_Frame.set_aprsMail_alarm(False)

    def dx_alarm(self):
        self._add_tasker_q("dx_alarm", None)

    def _dx_alarm_task(self):
        """ Alarm when new User in MH List """
        if self.setting_dx_alarm.get():
            self._Alarm_Frame.set_dxAlarm(True)

    def tracer_alarm(self):
        self._add_tasker_q("tracer_alarm", None)

    def _tracer_alarm_task(self):
        """ Tracer Alarm """
        self._tracer_alarm = True
        self._Alarm_Frame.set_tracerAlarm(True)

    def reset_tracer_alarm(self):
        self._add_tasker_q("reset_tracer_alarm", None)

    def _reset_tracer_alarm_task(self):
        """ Tracer Alarm """
        if self._tracer_alarm:
            self._Alarm_Frame.set_tracerAlarm(False)
            self._tracer_alarm = False

    def reset_dx_alarm(self):
        self._add_tasker_q("reset_dx_alarm", None)

    def _reset_dx_alarm_task(self):
        dx_alarm = bool(self.setting_dx_alarm.get())
        self._Alarm_Frame.set_dxAlarm_active(dx_alarm)

    def pmsMail_alarm(self):
        self._add_tasker_q("pmsMail_alarm", None)

    def _pmsMail_alarm_task(self):
        if self.MSG_Center_win:
            return
        self._Alarm_Frame.set_pmsMailAlarm(True)

    def reset_pmsMail_alarm(self):
        self._add_tasker_q("reset_pmsMail_alarm", None)

    def _reset_pmsMail_alarm_task(self):
        self._Alarm_Frame.set_pmsMailAlarm(False)

    def pmsFwd_alarm(self):
        self._add_tasker_q("pmsFwd_alarm", None)

    def _pmsFwd_alarm_task(self):
        self._Alarm_Frame.set_pms_fwd_alarm(True)

    def reset_pmsFwd_alarm(self):
        self._add_tasker_q("reset_pmsFwd_alarm", None)

    def _reset_pmsFwd_alarm_task(self):
        self._Alarm_Frame.set_pms_fwd_alarm(False)
        if self.MSG_Center_win:
            self.MSG_Center_win.tree_update_task()

    def set_diesel(self):
        self._add_tasker_q("set_diesel", None)

    def _set_diesel_task(self):
        self._Alarm_Frame.set_diesel(True)
        self._init_state = 0

    def reset_diesel(self):
        self._add_tasker_q("reset_diesel", None)

    def _reset_diesel_task(self):
        self._Alarm_Frame.set_diesel(False)

    def set_rxEcho_icon(self, alarm_set=True):
        self._add_tasker_q("set_rxEcho_icon", alarm_set)

    def _set_rxEcho_icon_task(self, alarm_set=True):
        self._Alarm_Frame.set_rxEcho_icon(alarm_set=alarm_set)

    def set_Beacon_icon(self, alarm_set=True):
        self._add_tasker_q("set_Beacon_icon", alarm_set)

    def _set_Beacon_icon_task(self, alarm_set=True):
        self._Alarm_Frame.set_beacon_icon(alarm_set=alarm_set)

    def set_port_block_warning(self):
        self._add_tasker_q("set_port_block_warning", None)

    def _set_port_block_warning_task(self):
        self._Alarm_Frame.set_PortBlocking_warning()

    #####################################
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

    def get_PH_mainGUI(self):
        return self._port_handler

    def _get_mh(self):
        try:
            return self._port_handler.get_MH()
        except Exception as ex:
            logger.error(ex)
            return None

    def get_AIS_mainGUI(self):
        if hasattr(self._port_handler, 'get_aprs_ais'):
            return self._port_handler.get_aprs_ais()
        logger.error("AttributeError: hasattr(self._port_handler, 'get_aprs_ais')")
        raise AttributeError

    def get_aprs_icon_tab_16(self):
        return self._aprs_icon_tab_16

    def get_aprs_icon_tab_24(self):
        return self._aprs_icon_tab_24

    def get_conn_typ_icon_16(self):
        return self._conn_typ_icons

    def get_fwd_q_icon_16(self):
        return self._fwd_q_flag_icons

    def get_ais_mon_gui(self):
        return self.aprs_mon_win

    #####################################
    def _set_port_blocking(self, state=0):
        if hasattr(self._port_handler, 'block_all_ports'):
            self._port_handler.block_all_ports(state)

    #####################################
    # Cache
    """
    def get_MapView_cache(self):
        return dict(self._global_cache_tab.get('tkMapView_cache', {}))

    def set_MapView_cache(self, cache: dict):
        #while len(cache) > 10_000:
        #    del cache[list(cache.keys())[0]]

        self._global_cache_tab['tkMapView_cache'] = dict(cache)
    """
