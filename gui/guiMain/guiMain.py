import random
import time
import tkinter as tk
from collections import deque
from tkinter import ttk, messagebox
import threading
from core.popt_core import PoPTCore
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import format_number, conv_timestamp_delta, get_kb_str_fm_bytes, get_strTab

from gui.guiMain.frames.guiMain_AX25StatusFrame import AX25StatusFrame
from gui.guiMain.frames.guiMain_BwPlotFrame import BwPlotFrame
from gui.guiMain.frames.guiMain_ChBtnFrame import ChBtnFrame
from gui.guiMain.frames.guiMain_AlarmFrame import AlarmIconFrame
from gui.guiMain.frames.guiMain_ConnStatusFrame import ConnStatusBar
from gui.guiMain.frames.guiMain_MonFrame import MonitorFrame
from gui.guiMain.frames.guiMain_MonTreeFrame import MonitorTreeFrame
from gui.guiMain.frames.guiMain_PreTxtFrame import PreTxtFrame
from gui.guiMain.frames.guiMain_QsoFrame import QsoFrame
from gui.guiMain.frames.guiMain_TabbedSideFrame import SideTabbedFrame
from gui.guiMain.guiMain_ChVars import GUIChannels
from gui.guiMain.guiMain_Icons import GuiIcons
from gui.guiMain.guiMain_Utilities import GuiUtilities
from gui.guiMain.guiMain_ToplevelManager import ToplevelManager

from cfg.constant import POPT_BANNER, WELCOME_SPEECH, VER, CFG_sound_RX_BEEP, \
    SERVICE_CH_START, COLOR_MAP, STYLES_AWTHEMES_PATH, STYLES_AWTHEMES, \
    GUI_TASKER_Q_RUNTIME, GUI_TASKER_TIME_D_UNTIL_BURN, GUI_TASKER_BURN_DELAY, GUI_TASKER_NOT_BURN_DELAY
from fnc.os_fnc import get_root_dir
from fnc.gui_fnc import get_all_tags
from sound.popt_sound import SOUND
from gui.plots.guiLiveConnPath import LiveConnPath



class PoPT_GUI_Main:
    def __init__(self, popt_handler: PoPTCore):
        ######################################
        # GUI Stuff
        self._logTag = 'GUI-Main: '
        logger.info(self._logTag + 'start..')
        ###########################################
        self.main_win   = tk.Tk()
        ###########################################
        self.style_name = POPT_CFG.get_guiCFG_style_name()
        logger.info(self._logTag + f'loading Style: {self.style_name}')
        self.style = ttk.Style(self.main_win)

        if self.style_name in STYLES_AWTHEMES:
            try:
                self.style.tk.call('lappend', 'auto_path', STYLES_AWTHEMES_PATH)
                self.style.tk.call('package', 'require', 'awthemes')
                self.style.tk.call('::themeutils::setHighlightColor', self.style_name, '#007000') # TODO
                self.style.tk.call('package', 'require', self.style_name)
                self.style.theme_use(self.style_name)
            except tk.TclError:
                logger.warning(self._logTag + 'awthemes-10.4.0 not found in folder data')
                logger.warning(self._logTag + '  1. If you want to use awthemes, download:')
                logger.warning(self._logTag + '     https://sourceforge.net/projects/tcl-awthemes/')
                logger.warning(self._logTag + '  2. Extract the contents of the file awthemes-10.4.0.zip')
                logger.warning(self._logTag + '     into the data/ folder')
                logger.warning(self._logTag + '')
                self.style_name = 'default'
                self.style.theme_use(self.style_name)
        else:
            try:
                self.style.theme_use(self.style_name)
            except tk.TclError:
                logger.warning(self._logTag + f'TclError Style{self.style_name}')
                self.style_name = 'default'
                self.style.theme_use(self.style_name)

        logger.info(self._logTag + f'Using style_name: {self.style_name}')
        #################################################################
        self.main_win.title(f"P.ython o.ther P.acket T.erminal {VER}")
        guiCfg = POPT_CFG.load_guiPARM_main()
        self.main_win.geometry(f"{guiCfg.get('gui_parm_main_width', 1400)}x{guiCfg.get('gui_parm_main_height', 850)}")
        # self.main_win.attributes('-topmost', 0)
        try:
            self.main_win.iconbitmap("favicon.ico")
        except Exception as ex:
            logger.warning(self._logTag + f"Couldn't load favicon.ico: {ex}")
            logger.info(self._logTag + "Try to load popt.png.")
            try:
                self.main_win.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(self._logTag + f"Couldn't load popt.png: {ex}")
        self.main_win.protocol("WM_DELETE_WINDOW", self._destroy_win)
        ######################################
        ######################################
        self._popt_handler = popt_handler
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._get_colorMap = lambda : COLOR_MAP.get(self.style_name, ('#000000',  '#d9d9d9'))
        ######################################
        # Init Vars
        self._mh        = self._popt_handler.get_MH()
        self.text_size  = POPT_CFG.load_guiPARM_main().get('gui_parm_text_size', 13)
        ###############################
        self._root_dir  = get_root_dir()
        self._root_dir  = self._root_dir.replace('/', '//')
        ###############################
        # Icons
        self.guiIcon    = GuiIcons()
        #####################
        # Buffer
        self.connect_history        = POPT_CFG.load_guiPARM_main().get('gui_parm_connect_history', {})
        self._remote_mon_pack_buff  = {}
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
        # Stat INFO (Name,QTH usw)
        self.stat_info_encoding_var = tk.StringVar(self.main_win)
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
        all_ports = self._popt_handler.port_manager.ax25_ports
        for port_id in all_ports:
            self.mon_port_on_vars[port_id] = tk.BooleanVar(self.main_win)
            self.mon_port_on_vars[port_id].set(True)
        self.mon_port_var.set('0')
        ################################################
        # Controlling
        self.channel_index  = 1
        self._mon_mode      = 0
        self._tracer_alarm  = False
        ####################
        self._quit          = False
        self._init_state    = 0
        self._thread_gc: list[threading.Thread] = []    # Thread Garbage colletor
        self._win_gc                            = []
        # GUI PARAM
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
        ########################################
        ########################################
        # Toplevel Win Manager
        self.toplevel_manager = ToplevelManager(self)

        ######################################
        ######################################
        # L/R PW
        self._main_pw       = ttk.PanedWindow(self.main_win, orient='horizontal')
        self._main_pw.pack(fill='both', expand=True)

        l_frame             = ttk.Frame(self._main_pw)
        self._r_frame       = ttk.Frame(self._main_pw)
        r_pack_frame        = ttk.Frame(self._r_frame)
        self._r_frame.pack(fill='both', expand=True)
        r_pack_frame.pack( fill='both', expand=True)

        self._main_pw.add(l_frame,       weight=1)
        self._main_pw.add(self._r_frame, weight=0)

        ###########################################
        ###########################################
        # Channel Buttons
        self._chBtn_frame = ChBtnFrame(self, l_frame)
        self._chBtn_frame.pack(side='bottom', fill='x', expand=False)

        ###########################################
        ###########################################
        # Input Output TXT Frames and Status Bar
        self._pw = ttk.PanedWindow(l_frame, orient='vertical', )
        self._pw.pack(side='bottom', expand=1, fill='both')
        # =====================================
        # Upper
        self._TXT_upper_frame   = ttk.Frame(self._pw, borderwidth=0, height=20)
        # Mid
        self._TXT_mid_frame     = ttk.Frame(self._pw, borderwidth=0, )
        # Lower
        self._TXT_lower_frame   = ttk.Frame(self._pw, borderwidth=0, )
        # =====================================
        self._TXT_upper_frame.pack(side='bottom', expand=1, fill='both')
        self._TXT_mid_frame.pack(  side='bottom', expand=1, fill='both')
        self._TXT_lower_frame.pack(side='bottom', expand=1, fill='both')
        self._pw.add(self._TXT_upper_frame, weight=1)
        self._pw.add(self._TXT_mid_frame,   weight=1)
        self._pw.add(self._TXT_lower_frame, weight=1)
        # =====================================
        winPos_cfgTab = {
            0: self._TXT_upper_frame,
            1: self._TXT_mid_frame,
            2: self._TXT_lower_frame,
        }
        txtWin_pos_cfg  = POPT_CFG.get_guiCFG_textWin_pos()
        # =====================================
        # AX25 Status Bar / Connection Status Bar
        qso_frame           = winPos_cfgTab[txtWin_pos_cfg[1]]
        self._AX25StatusBar = AX25StatusFrame(self, qso_frame)
        self.ConnStatusBar  = ConnStatusBar(  self, qso_frame)
        self._AX25StatusBar.pack(side='top',    expand=False, fill='x')
        self.ConnStatusBar.pack( side='bottom', expand=False, fill='x')

        # =====================================
        # Text Frames (QSO/PreWrite/Monitor)
        self._init_prewrite_frame(winPos_cfgTab[txtWin_pos_cfg[0]])
        self._init_qso_frame(     winPos_cfgTab[txtWin_pos_cfg[1]])
        self._init_monitor_frame( winPos_cfgTab[txtWin_pos_cfg[2]])

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
        # Channel Vars / GUI Channels
        self.guiChannels  = GUIChannels(self)
        self.channel_vars = self.guiChannels.channel_vars

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
        # ================================================
        # tabbed Frame
        self._BwPlot            = BwPlotFrame( self, self.main_win)
        self._Pacman            = LiveConnPath(self, self.main_win)
        self.tabbed_sideFrame   = SideTabbedFrame(self, tabbedF_upper_frame, path_frame=self._Pacman)
        self.tabbed_sideFrame2  = SideTabbedFrame(self, tabbedF_lower_frame, plot_frame=self._BwPlot)

        ######################################################################
        # GUI Utility Stuff
        self._guiUtils = GuiUtilities(self)
        self._guiUtils.init_menubar()       # MenuBar
        self._guiUtils.init_r_click_men()   # R-Click Menu
        self._guiUtils.set_binds()          # Global Key-Bindings
        self._guiUtils.set_keybinds()       # Key-Bindings

        ######################################################################
        # set Ch Btn Color
        self.ch_status_update()
        # Init Vars fm CFG
        self._init_GUI_vars_fm_CFG()
        self._set_CFG()
        # Text Tags
        self.set_text_tags()
        # .....
        self.update_qso_Vars()
        ############################
        self._monitor_start_msg()
        ############################
        self._Pacman.update_plot_f_ch()
        ##########################################
        # Menubar fix if app starts in fullscreen
        geom = self.main_win.winfo_geometry()
        self.main_win.geometry(geom)
        self._load_pw_pos()
        #################################
        # set GUI Var to Port Handler
        self._popt_handler.set_gui(self)
        #######################
        # LOOP LOOP LOOP
        self.main_win.after(GUI_TASKER_NOT_BURN_DELAY, self._tasker)
        logger.info(self._logTag + 'Init Done')
        logger.info(self._logTag + "Unblocking Ports")
        self._popt_handler.port_manager.unblock_all_ports()
        logger.info(self._logTag + 'Start Tasker')
        self.main_win.mainloop()

    ##############################################################
    def quit_popt(self):
        self._destroy_win()

    def _destroy_win(self):
        if self._quit:
            return
        self.set_port_blocking(1)
        self._popt_handler.connection_manager.disco_all_Conn()
        self._quit = True
        self._popt_handler.close_sound_PH()
        self._thread_gc += SOUND.get_sound_thread()
        self._monFrame.sysMsg_to_monitor_task(self._getTabStr('mon_end_msg1'))
        self._popt_handler.connection_manager.disco_all_Conn()
        """"""
        self.toplevel_manager.destroy_win()
        """"""
        logger.info('GUI: Closing GUI: Save GUI Vars & Parameter.')
        self._save_all_data()
        logger.info('GUI: Closing GUI: Closing Ports.')
        self._monFrame.sysMsg_to_monitor_task('Closing Ports.')
        threading.Thread(target=self._popt_handler.close_popt).start()

    def _save_GUIvars(self):
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
        guiCfg['gui_parm_new_call_alarm']   = bool(self._mh.parm_new_call_alarm)
        guiCfg['gui_parm_channel_index']    = int(self.channel_index)
        guiCfg['gui_parm_text_size']        = int(self.text_size)
        guiCfg['gui_parm_connect_history']  = dict(self.connect_history)
        # guiCfg['gui_cfg_locator'] = str(self.own_loc)
        # guiCfg['gui_cfg_qth'] = str(self.own_qth)
        POPT_CFG.save_guiPARM_main(guiCfg)

    def _save_all_data(self):
        self._monFrame.sysMsg_to_monitor_task('Save all Data')
        self._Pacman.save_path_data()
        self._save_GUIvars()
        self._save_pw_pos()
        self.guiChannels.save_Channel_Vars()
        #self._popt_handler.save_popt_data()

    def add_save_all_data_task(self):
        self._add_tasker_q("_save_all_data", None, False)

    ####################
    # Init Stuff
    def _init_GUI_vars_fm_CFG(self):
        #########################
        # GUI-Vars fm cfg
        guiCfg = POPT_CFG.load_guiPARM_main()
        self.setting_sound.set(guiCfg.get('gui_cfg_sound', False))
        self.setting_bake.set(guiCfg.get('gui_cfg_beacon', False))
        self.setting_rx_echo.set(guiCfg.get('gui_cfg_rx_echo', False))
        self.set_rxEcho_icon(self.setting_rx_echo.get())
        self._popt_handler.port_manager.rx_echo_on = bool(self.setting_rx_echo.get())
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
        """ Tab Index / Side Frame Tabs """
        tab1_index, tab2_index = guiCfg.get('gui_cfg_rtab_index', (None, None))
        self.tabbed_sideFrame.set_tab_index(tab1_index)
        self.tabbed_sideFrame2.set_tab_index(tab2_index)

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
    def _init_btn(self, frame):
        self._conn_btn = tk.Button(frame,
                                   text="Connect",
                                   bg="green",
                                   width=8,
                                   command=self.toplevel_manager.open_new_conn_win,
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

    def _init_prewrite_frame(self, parent_frame: ttk.Frame):
        self._pre_txt_frame = PreTxtFrame(self, parent_frame)
        self.inp_txt        = self._pre_txt_frame.get_inp_txt()

    def _init_qso_frame(self, parent_frame: ttk.Frame):
        self._qso_frame = QsoFrame(self, parent_frame)
        self.qso_txt    = self._qso_frame.get_qso_txt()

    def _init_monitor_frame(self, parent_frame: ttk.Frame):
        self._mon_pw = ttk.Panedwindow(parent_frame, orient='vertical')
        self._mon_pw.pack(fill='both', expand=True)

        self._monFrame       = MonitorFrame(self, self._mon_pw)
        self._mon_tree_frame = MonitorTreeFrame(self, self._mon_pw)

        self._monFrame.pack(      fill='both', expand=True)
        self._mon_tree_frame.pack(fill='both', expand=True)

        self._mon_pw.add(self._monFrame,       weight=1)
        self._mon_pw.add(self._mon_tree_frame, weight=0)

        self.mon_txt         = self._monFrame.get_mon_txt()

    #######################################
    # Text Tags
    def set_text_tags(self):
        self._qso_frame.set_tags()
        self._monFrame.set_tags()
        self._pre_txt_frame.set_tags()

    ##########################
    # Start Message in Monitor
    def _monitor_start_msg(self):
        # tmp_lang = int(self.language)
        # self.language = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        SOUND.sprech(random.choice(WELCOME_SPEECH), wait=False)
        ban = POPT_BANNER.format(VER)
        tmp = ban.split('\r')
        for el in tmp:
            self._monFrame.sysMsg_to_monitor_task(el)
        self._monFrame.sysMsg_to_monitor_task('Python Other Packet Terminal ' + VER)
        for stat in POPT_CFG.get_stat_CFG_keys():
            self._monFrame.sysMsg_to_monitor_task(self._getTabStr('mon_start_msg1').format(stat))
        all_ports = self._popt_handler.port_manager.ax25_ports
        for port_k in all_ports.keys():
            msg = self._getTabStr('mon_start_msg2')
            if all_ports[port_k].device_is_running:
                msg = self._getTabStr('mon_start_msg3')
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_k)
            self._monFrame.sysMsg_to_monitor_task('Info: Port {}: {} - {} {}'
                                   .format(port_k,
                                           port_cfg.get('parm_PortName', ''),
                                           port_cfg.get('parm_PortTyp', ''),
                                           msg
                                           ))
            self._monFrame.sysMsg_to_monitor_task('Info: Port {}: Parameter: {} | {}'
                                   .format(port_k,
                                           port_cfg.get('parm_PortParm', ('', 0))[0],
                                           port_cfg.get('parm_PortParm', ('', 0))[1],
                                           ))

    # END Init Stuff
    ######################################################################
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
        for k in self.channel_vars.keys():
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
            self._tasker_prio()                         # Port-Handler Tasker, ..., ...
            task_0_25 = self._tasker_025_sec()          # 0.25 & 0.5 Sec(flip flop)
            task_1_00 = self._tasker_1_sec()            # 1.00 Sec
            update_needed = task_0_25 or task_1_00
            # Nur wenn vorherige Tasks nicht ausgeführt wurden
            if not update_needed:
                update_needed = self._tasker_5_sec()    # 5.00 Sec
            # Nur wenn vorherige Tasks ausgeführt wurden
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
        if not self._popt_handler.get_ph_end():
            return False
        #if self._tasker_q:
        #    logger.info('GUI: Still jobs in _tasker_q')
        #    return False
        th_name = []
        for gc_thread in self._thread_gc:
            if hasattr(gc_thread, 'is_alive'):
                if gc_thread.is_alive():
                    th_name.append(gc_thread.name)
        if th_name:
            logger.info(self._logTag + f'Waiting for {len(th_name)} Threads ! Please Wait ...')
            for thname in th_name:
                logger.debug(f"  - Waiting for Thread: {thname}")
            return False
        self.main_win.quit()
        try:
            self.main_win.destroy()
            logger.info('GUI: Closing GUI: Done')
        except Exception as ex:
            logger.warning(ex)
        return True

    def _tasker_queue(self, start_time: time.time):
        if not self._tasker_q and not self._tasker_q_prio:
            return False

        if self._tasker_q_prio:
            while self._tasker_q_prio and self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME):
                task, arg = self._tasker_q_prio.pop(0)
                if task == 'sysMsg_to_monitor':
                    self._monFrame.sysMsg_to_monitor_task(arg)
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
                    self._Pacman.add_LivePath_plot_task(node, ch_id, path)
                elif task == 'resetHome_LivePath_plot':
                    ch_id = arg
                    self._Pacman.resetHome_LivePath_plot_task(ch_id)
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
                    self.toplevel_manager.update_aprs_spooler_task()
                elif task == 'update_aprs_msg_win':
                    self.toplevel_manager.update_aprs_msg_win_task(arg)
                #elif task == 'update_tracer_win':
                #    self._update_tracer_win_task()

        if self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME) and not self._quit and self._tasker_q:
            # Non Prio
            while self._tasker_q and self._get_tasker_q_can_run(start_time, GUI_TASKER_Q_RUNTIME):
                task, arg = self._tasker_q.pop(0)
                if task == '_monitor_tree_update':
                    self._mon_tree_frame.monitor_tree_update_task(arg)
                elif task == '_monitor_q_task':
                    self._monFrame.monitor_q_task(arg)
                elif task == '_remote_monitor_update_task':
                    rem_mon_data, remote_uid = arg
                    self._remote_monitor_update_task(rem_mon_data ,remote_uid)
                elif task == '_prp_response_update_task':
                    rem_mon_data, remote_uid = arg
                    self.toplevel_manager.prp_response_update_task(rem_mon_data, remote_uid)
                elif task == '_init_popt_remote_task':
                    self._init_popt_remote_task(arg)
                elif task == '_save_all_data':
                    self._save_all_data()

        return True

    def _tasker_prio(self):
        """ Prio Tasks every Irritation """
        tasker_ret = False
        """ PoPT-Core Tasker """
        if hasattr(self._popt_handler, 'popt_core_task'):
            timer = time.time()
            self._popt_handler.popt_core_task()
            t_delta = time.time() - timer
            if t_delta > GUI_TASKER_TIME_D_UNTIL_BURN:
                logger.warning(f"PH-Tasker Overload: Loop needs {round(t_delta, 2)}s to process !!")

        """ Toplevel Win Tasker """
        task        = self.toplevel_manager.tasker_prio()
        tasker_ret  = task or tasker_ret
        task_01     = self._monitor_task()
        tasker_ret  = tasker_ret or task_01
        return tasker_ret

    def _tasker_025_sec(self):
        """ 0.25 Sec """
        if time.time() > self._non_prio_task_timer:
            self._non_prio_task_timer = time.time() + self._parm_non_prio_task_timer
            #####################
            task_02 = self._qso_frame.update_qso_win()
            task_03 = self._SideFrame_tasker()
            task_04 = self._AX25StatusBar.update_status_bar()
            """ Toplevel Win Tasker """
            task_05 = self.toplevel_manager.tasker_025_sec()
            ret = (task_02 or
                   task_03 or
                   task_04 or
                   task_05
                   )

            if self._flip025:
                task_05_01 = self._AlarmIcon_tasker05()
                ret = task_05_01 or ret
            #####################
            self._flip025 = not self._flip025
            return ret
        return False

    def _tasker_1_sec(self):
        """ 1 Sec """
        if time.time() > self._non_non_prio_task_timer:
            #####################
            self.ConnStatusBar.update_stat_info_conn_timer()
            self._update_ft_info()
            self._AlarmIcon_tasker1()
            self._chBtn_frame.tasker()
            """ Toplevel Win Tasker """
            self.toplevel_manager.tasker_1_sec()
            # APRS - MSG Spooler
            self._update_aprs_spooler()
            if SOUND.master_sound_on:
                # TODO Sound Task
                self._rx_beep_sound()
                if SOUND.master_sprech_on:
                    self._check_sprech_ch_buf()

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
            self._BwPlot.update_bw_mon()
            """ Toplevel Win Tasker """
            self.toplevel_manager.tasker_5_sec()
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
    ######################################################################
    def _update_aprs_spooler(self):
        self._add_tasker_q("update_aprs_spooler", None)

    def update_aprs_msg_win(self, aprs_pack):
        self._add_tasker_q("update_aprs_msg_win", aprs_pack)

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
            return (
                self.tabbed_sideFrame.tasker() or
                self.tabbed_sideFrame.on_ch_stat_change()
            )

        return (
            self.tabbed_sideFrame2.tasker() or
            self.tabbed_sideFrame2.on_ch_stat_change()
        )

    def _check_port_blocking_task(self):
        if hasattr(self._popt_handler, 'port_manager'):
            if hasattr(self._popt_handler.port_manager, 'get_glb_port_blocking'):
                if not self._popt_handler.port_manager.get_glb_port_blocking():
                    self._Alarm_Frame.set_PortBlocking(set_on=False)
                else:
                    self._Alarm_Frame.set_PortBlocking(set_on=True, blinking=True)
    ###############################################################
    # QSO WIN
    def update_qso_Vars(self):
        self._qso_frame.update_qso_Vars()
        self._pre_txt_frame.update_qso_Vars()

        ch_vars = self.get_ch_var(ch_index=self.channel_index)
        bg      = self._get_colorMap()[1]
        ch_vars.new_data_tr = False
        ch_vars.rx_beep_tr  = False

        # self.main_class: gui.guiMainNew.TkMainWin
        if ch_vars.rx_beep_opt and self.channel_index:
            self._AX25StatusBar.rx_beep_var.set(1)
            self._AX25StatusBar.rx_beep_box.configure(bg='green')
        else:
            self._AX25StatusBar.rx_beep_var.set(0)
            self._AX25StatusBar.rx_beep_box.configure(bg=bg)

        if ch_vars.timestamp_opt and self.channel_index:
            self._AX25StatusBar.ts_box_var.set(True)
            #self._ts_box_box.configure(bg='green')
        else:
            self._AX25StatusBar.ts_box_var.set(False)
            #self._ts_box_box.configure(bg=bg)

    def sysMsg_to_qso(self, data: str, ch_index):
        self._add_tasker_q("sysMsg_to_qso", (data, ch_index))

    def sysMsg_to_qso_task(self, data: str, ch_index):
        self._qso_frame.sysMsg_to_qso_task(data, ch_index)

    def see_end_qso_win(self):
        self._qso_frame.see_end_qso_win()
    # END QSO WIN
    ###############################################################

    ###############################################################
    # Monitor WIN
    def sysMsg_to_monitor(self, var: str):
        self._add_tasker_q("sysMsg_to_monitor", var)

    def _monitor_task(self):
        mon_buff = self._popt_handler.get_monitor_data()
        if not mon_buff:
            return False
        new_mon_buff        = []
        for axframe_conf in mon_buff:
            port_id = axframe_conf.get('port', -1)

            self._mon_tree_frame.mon_pack_buff.append(dict(axframe_conf))
            if port_id not in self.mon_port_on_vars:
                logger.error(f"_monitor_task: port_id ({port_id}) not in mon_port_on_vars({self.mon_port_on_vars.keys()})")
                continue
            if not self.mon_port_on_vars[port_id].get():
                continue
            new_mon_buff.append(axframe_conf)

        """ Monitor Tree """
        self.monitor_tree_update(new_mon_buff)
        """ Monitor """
        self._add_tasker_q('_monitor_q_task',
                           new_mon_buff,
                           False)
        return True
    # END Monitor WIN
    ###############################################################
    ###############################################################
    # Monitor Tree
    def monitor_tree_update(self, ax25pack_batch: list):
        self._add_tasker_q("_monitor_tree_update", ax25pack_batch, prio=False)

    ###############################################################
    # Remote Monitor
    # === Init
    def init_popt_remote(self, uid: str):
        """ Init fm Connection """
        self._add_tasker_q("_init_popt_remote_task", uid, prio=False)

    def _init_popt_remote_task(self, uid: str):
        if uid not in self._remote_mon_pack_buff:
            self._remote_mon_pack_buff[uid] = deque([] * 10000, maxlen=10000)
        # Update Remote Mon GUI if open
        if hasattr(self.toplevel_manager.prp_remote_win, 'prp_connection_init'):
            self.toplevel_manager.prp_remote_win.prp_connection_init(uid)

    # === TX Cmds
    """
    def send_rem_mon_start(self, cfg: dict, uid: str):
        conn = self._port_handler.get_connections_by_uid(uid)
        if not hasattr(conn, 'get_remote_mon'):
            logger.error(f"Can't find Connection UID ({uid})")
            return
        remote_mon = conn.get_remote_mon()
        remote_mon.cmd_start_gui_remote_mon(cfg)

    def send_rem_mon_stop(self, uid: str):
        conn = self._port_handler.get_connections_by_uid(uid)
        if not hasattr(conn, 'get_remote_mon'):
            logger.error(f"Can't find Connection UID ({uid})")
            return
        remote_mon = conn.get_remote_mon()
        remote_mon.cmd_stop_gui_remote_mon()
    """
    # === RX
    def prp_response_update(self, resp: str, remote_uid: str):
        self._add_tasker_q("_prp_response_update_task", (resp, remote_uid), prio=False)

    def remote_monitor_update_gui(self, ax25pack: dict, remote_uid: str):
        self._add_tasker_q("_remote_monitor_update_task", (ax25pack, remote_uid), prio=False)

    def _remote_monitor_update_task(self, rem_mon_ax25conf: dict, remote_uid: str):
        if not rem_mon_ax25conf:
            return

        # == Remote Monitor Buffer
        if remote_uid not in self._remote_mon_pack_buff:
            self._remote_mon_pack_buff[remote_uid] = deque([] * 10000, maxlen=10000)
        self._remote_mon_pack_buff[remote_uid].append(rem_mon_ax25conf)

        # == Update Remote Mon GUI if open
        self.toplevel_manager.prp_remote_update_mon(rem_mon_ax25conf, remote_uid)

    # === Getta
    def get_remote_monitor_pack_buffer(self):
        return dict(self._remote_mon_pack_buff)

    #######################################################################
    #######################################################################
    # DISCO
    def disco_conn(self):
        conn = self.get_conn(self.channel_index)
        if conn is not None:
            conn.conn_disco()

    def disco_all(self):
        if messagebox.askokcancel(title=self._getTabStr('disconnect_all'),
                                  message=self._getTabStr('disconnect_all_ask'),
                                  parent=self.main_win):
            self._popt_handler.connection_manager.disco_all_Conn()

    # DISCO ENDE
    def kaffee(self):
        self._monFrame.sysMsg_to_monitor_task('Hinweis: Hier gibt es nur Muckefuck !')
        SOUND.sprech('Gluck gluck gluck blubber blubber')
        #self.open_RoutingTab_win()

    def do_priv(self, event=None):
        conn = self.get_conn()
        if conn is not None:
            if conn.user_db_ent:
                if conn.user_db_ent.sys_pw:
                    conn.cli.start_baycom_login()
                else:
                    self.toplevel_manager.open_settings_window('priv_win')

    #######################################################################
    #######################################################################
    # SEND TEXT
    def snd_text(self, event=None):
        self._pre_txt_frame.snd_text()

    # SEND TEXT
    #######################################################################
    #######################################################################
    # Conn Path Plot
    def add_LivePath_plot(self, node: str, ch_id: int, path=None):
        self._add_tasker_q("add_LivePath_plot", (node, ch_id, path))

    def resetHome_LivePath_plot(self, ch_id: int):
        self._add_tasker_q("resetHome_LivePath_plot", ch_id)

    # END Conn Path Plot
    #######################################################################
    # =====================================
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
                self._conn_btn.configure(bg="red", text="Disconnect", command=self.disco_conn)
        elif self._conn_btn.cget('bg') != "green":
            self._conn_btn.configure(text="Connect", bg="green", command=self.toplevel_manager.open_new_conn_win)
        self._chBtn_frame.ch_btn_status_update()

    # =====================================
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

    def _ch_btn_clk(self, ind: int):
        old_ch_vars = self.get_ch_var(ch_index=int(self.channel_index))
        old_ch_vars.input_win       = self.inp_txt.get('1.0', tk.END)
        old_ch_vars.input_win_tags  = get_all_tags(self.inp_txt)
        old_ch_vars.output_win_tags = get_all_tags(self.qso_txt)
        old_ch_vars.input_win_cursor_index = self.inp_txt.index(tk.INSERT)
        self.channel_index = int(ind)
        self.update_qso_Vars()
        self.ch_status_update()
        self.conn_btn_update()
        self._reset_noty_bell()
        self._Pacman.update_plot_f_ch(self.channel_index)
        self._kanal_switch()  # Sprech

    # =====================================
    def ch_status_update(self):
        """ Triggerd when Connection Status has changed (Conn-accept, -end, -resset)"""
        self._add_tasker_q("ch_status_update", None)

    def _ch_status_update_task(self):
        self._chBtn_frame.ch_btn_status_update()
        self.on_channel_status_change()

    def on_channel_status_change(self):
        """ Triggerd when Connection Status has changed + additional Trigger"""
        self._add_tasker_q("on_channel_status_change", None)

    def _on_channel_status_change_task(self):
        self.tabbed_sideFrame.on_ch_stat_change()
        self.tabbed_sideFrame2.on_ch_stat_change()
        self.ConnStatusBar.update_station_info()

    # =====================================
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
    def set_tracer(self, state=None):
        ais_obj = self._popt_handler.get_aprs_ais()
        if ais_obj is not None:
            ais_obj.set_be_tracer_active(bool(self.setting_tracer.get()))
        else:
            self.setting_tracer.set(False)
        self.set_auto_tracer()
        # FIXME
        # self.tabbed_sideFrame.set_auto_tracer_state()
        # self.tabbed_sideFrame.set_auto_tracer_state()
        # self.set_tracer_icon()

    def get_tracer(self):
        ais_obj = self._popt_handler.get_aprs_ais()
        if ais_obj is not None:
            return bool(ais_obj.get_be_tracer_active)
        return False

    def set_tracer_fm_aprs(self):
        ais_obj = self._popt_handler.get_aprs_ais()
        if ais_obj is not None:
            self.setting_tracer.set(ais_obj.get_be_tracer_active)
        else:
            self.setting_tracer.set(False)
        self.tabbed_sideFrame.set_auto_tracer_state()
        self.tabbed_sideFrame2.set_auto_tracer_state()

    def set_auto_tracer(self, event=None):
        ais_obj = self._popt_handler.get_aprs_ais()
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

    def set_auto_tracer_duration(self, dur):
        ais_obj = self._popt_handler.get_aprs_ais()
        if ais_obj is not None:
            if type(dur) is int:
                ais_obj.tracer_auto_tracer_duration_set(dur)
                self.set_auto_tracer()

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
        if self.toplevel_manager.aprs_pn_msg_win:
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
        self.tabbed_sideFrame.reset_dx_alarm()
        self.tabbed_sideFrame2.reset_dx_alarm()

    def pmsMail_alarm(self):
        self._add_tasker_q("pmsMail_alarm", None)

    def _pmsMail_alarm_task(self):
        if self.toplevel_manager.MSG_Center_win:
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
        if self.toplevel_manager.MSG_Center_win:
            self.toplevel_manager.MSG_Center_win.tree_update_task()

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

    def _reset_noty_bell(self):
        conn = self.get_conn(self.channel_index)
        if not conn:
            return
        if conn.noty_bell:
            conn.noty_bell = False
            self._popt_handler.api.reset_noty_bell_PH()

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
            th = threading.Thread(target=self._noty_bell, args=(ch_id, msg))
            th.start()
            self.add_thread_gc(th)

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
        self.guiChannels.set_var_to_all_ch_param()

    #####################################
    def set_port_blocking(self, state=0):
        if hasattr(self._popt_handler, 'port_manager'):
            if hasattr(self._popt_handler.port_manager, 'block_all_ports'):
                self._popt_handler.port_manager.block_all_ports(state)

    # =====================================
    def get_conn(self, con_ind: int = 0):
        # TODO Call just if necessary
        # TODO current Chanel.connection to var, prevent unnecessary calls
        if not con_ind:
            con_ind = int(self.channel_index)
        all_conn = self._popt_handler.get_all_connections()
        if con_ind in all_conn.keys():
            return all_conn[con_ind]
        return None

    # Channel Vars
    def get_ch_var(self, ch_index=0):
        return self.guiChannels.get_ch_var(ch_index=ch_index)

    # =====================================
    def get_PH_mainGUI(self):
        return self._popt_handler

    def get_AIS_mainGUI(self):
        if hasattr(self._popt_handler, 'get_aprs_ais'):
            return self._popt_handler.get_aprs_ais()
        logger.error("AttributeError: hasattr(self._port_handler, 'get_aprs_ais')")
        raise AttributeError

    def get_ais_mon_gui(self):
        return self.toplevel_manager.aprs_mon_win

    def get_MH(self):
        return self._mh