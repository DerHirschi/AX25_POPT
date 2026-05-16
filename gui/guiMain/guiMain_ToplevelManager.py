from gui.UserDB.guiUserDB import UserDB
from gui.UserDB.guiUserDBoverview import UserDBtreeview
from gui.aprs.guiAPRS_Monitor.guiAPRSmon import AISmonitor
from gui.aprs.guiAPRS_SMS.guiAPRS_pn_msg import APRS_msg_SYS_PN
from gui.aprs.guiAPRS_Settings.guiAPRS_Settings_Main import APRSSettingsMain
from gui.aprs.guiAPRS_wx_tree import WXWin
from gui.bbs_gui.bbs_MSGcenter_gui.guiBBS_MSG_center import MSG_Center
from gui.bbs_gui.bbs_settings.guiBBS_Settings_Main import BBSSettingsMain
from gui.bbs_gui.guiBBS_fwd_q import BBS_fwd_Q
from gui.bbs_gui.guiBBS_newMSG import BBS_newMSG
from gui.ft.guiFT_Manager import FileTransferManager
from gui.ft.guiFileTX import FileSend
from gui.guiAbout import About
from gui.guiBlockList import BlockList
from gui.guiDualPortMon import DualPort_Monitor
from gui.guiHelpKeybinds import KeyBindsHelp
from gui.guiLocatorCalc import LocatorCalculator
from gui.guiMH.guiMH import MHWin
from gui.guiNewConnWin import NewConnWin
from gui.guiPriv import PrivilegWin
from gui.guiRightLevelEditor import RightLevelEditor
from gui.plots.guiBBS_fwdPath_Plot import FwdGraph
from gui.plots.guiPlotPort import PlotWindow
from gui.prp.guiPRP_remote import PRP_remoteGUI
from gui.settings.guiDualPortSettings import DualPortSettingsWin
from gui.settings.guiLinkholderSettings import LinkHolderSettings
from gui.settings.guiPipeToolSettings import PipeToolSettings
from gui.settings.guiSettingsMain import SettingsMain


class ToplevelManager:
    def __init__(self, gui_root_cl):
        # ================================
        self._gui_root = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        # ================================
        self.new_conn_win           = None
        self.settings_win           = None
        self.mh_window              = None
        self.wx_window              = None
        self.port_stat_win          = None
        self.locator_calc_window    = None
        self.aprs_mon_win           = None
        self.aprs_pn_msg_win        = None
        self.aprs_pn_msg_frame      = []
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
        self.routingTab_win         = None
        self.prp_remote_win         = None
        self.right_level_win        = None
        # ================================

    # ================================
    @property
    def popt_handler(self):
        return self._popt_handler

    # ================================
    def tasker_prio(self):
        """ Prio Tasks every Irritation """
        tasker_ret = False
        if hasattr(self.userDB_tree_win, 'tasker'):
            task = self.userDB_tree_win.tasker()
            tasker_ret = task or tasker_ret

        if hasattr(self.userdb_win, 'tasker'):
            task = self.userdb_win.tasker()
            tasker_ret = task or tasker_ret

        # Locator Calc Win
        if hasattr(self.locator_calc_window, 'tasker'):
            task = self.locator_calc_window.tasker()
            tasker_ret = task or tasker_ret

        if hasattr(self.aprs_mon_win, 'tasker'):
            task = self.aprs_mon_win.tasker()
            tasker_ret = task or tasker_ret

        if hasattr(self.mh_window, 'tasker'):
            task = self.mh_window.tasker()
            tasker_ret = task or tasker_ret

        return tasker_ret

    def tasker_025_sec(self):
        ret = self._prp_gui_tasker()
        ret = ret or self._dualPort_monitor_task()
        return ret

    def tasker_1_sec(self):
        # TODO: Own Tasker Q
        if hasattr(self.settings_win, 'tasker'):
            self.settings_win.tasker()
        if hasattr(self.BBS_fwd_q_list, 'tasker'):
            # TODO 2 Sec Tasker
            self.BBS_fwd_q_list.tasker()
        # APRS SMS
        #self.update_aprs_spooler_task()

    def tasker_5_sec(self):
        self._aprs_wx_tree_task()

    # ================================
    # Called fm self.tasker
    def _aprs_wx_tree_task(self):
        ais = self._popt_handler.get_aprs_ais()
        if not hasattr(ais, "get_update_tr"):
            return
        if not hasattr(self.wx_window, 'update_tree_data'):
            return
        update_tr = ais.get_update_tr()
        if update_tr:
            self.wx_window.update_tree_data()

    def _prp_gui_tasker(self):
        if hasattr(self.prp_remote_win, 'tasker'):
            return self.prp_remote_win.tasker()
        return False

    def _dualPort_monitor_task(self):
        if not hasattr(self.dualPortMon_win, 'dB_mon_tasker'):
            return False
        return self.dualPortMon_win.dB_mon_tasker()

    # ================================
    # Called fm gui_root.Tasker-Q
    # APRS
    def update_aprs_spooler_task(self):
        if hasattr(self.aprs_pn_msg_win, 'update_spooler_tree'):
            self.aprs_pn_msg_win.update_spooler_tree()

    def update_aprs_msg_win_task(self, aprs_pack):
        if hasattr(self.aprs_pn_msg_win, 'update_aprs_msg'):
            self.aprs_pn_msg_win.update_aprs_msg(aprs_pack)
        for aprs_sms_frame in list(self.aprs_pn_msg_frame):
            if hasattr(aprs_sms_frame, 'update_aprs_msg_frame'):
                aprs_sms_frame.update_aprs_msg_frame()
            else:
                self.aprs_pn_msg_frame.remove(aprs_sms_frame)

    # PRP
    def prp_response_update_task(self, arg: tuple):
        # Update Remote Mon GUI if open
        if hasattr(self.prp_remote_win, 'gui_prp_response_handler'):
            resp, remote_uid = arg
            self.prp_remote_win.gui_prp_response_handler(resp, remote_uid)

    def prp_remote_update_mon(self, rem_mon_ax25conf: dict, remote_uid: str):
        # == Update Remote Mon GUI if open
        if hasattr(self.prp_remote_win, 'rem_mon_update'):
            self.prp_remote_win.rem_mon_update(rem_mon_ax25conf, remote_uid)

    # ================================
    def open_link_holder_sett(self):
        #self.main_win.update_idletasks()
        self.open_settings_window('l_holder')

    def open_ft_manager(self, event=None):
        #self.main_win.update_idletasks()
        self.open_settings_window('ft_manager')

    def open_settings_window(self, win_key: str):
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
            self.settings_win = settings_win(self._gui_root)

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
            'remote_monitor': (self.prp_remote_win, PRP_remoteGUI),
            'right_level_editor': (self.right_level_win, RightLevelEditor),

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
            win_list[1](self._gui_root)

    # UserDB
    def open_user_db_win(self, event=None, ent_key=''):
        if self.userdb_win is not None:
            return
        if not ent_key:
            conn = self._gui_root.get_conn()
            if conn is not None:
                ent_key = conn.to_call_str
        #self.main_win.update_idletasks()
        self.userdb_win = UserDB(self._gui_root, ent_key)

    # New Connection WIN
    def open_new_conn_win(self):
        self.open_window('new_conn')


    def open_MH_win(self):
        """MH WIN"""
        self._gui_root.reset_tracer_alarm()  # ??? PORTHANDLER set_tracerAlram ???
        self._popt_handler.api.set_dxAlarm(False)

        if hasattr(self.mh_window, 'lift'):
            self.mh_window.lift()
            return
        MHWin(self._gui_root)

    def open_BlockList_win(self):
        if hasattr(self.block_list_win, 'lift'):
            self.block_list_win.lift()
            return
        if self.block_list_win is not None:
            if hasattr(self.block_list_win, 'close'):
                self.block_list_win.close()
                self.block_list_win = None
                return
        self.block_list_win = BlockList(self._gui_root)

    def open_RoutingTab_win(self):
        if hasattr(self.routingTab_win, 'lift'):
            self.routingTab_win.lift()
            return
        if not hasattr(self._popt_handler, 'get_RoutingTable'):
            if hasattr(self.routingTab_win, 'close'):
                self.routingTab_win.close()
                self.routingTab_win = None
                return
        # RoutingTableWindow(self, self._port_handler.get_RoutingTable())

    # ================================
    def destroy_win(self):
        for wn in [
            self.new_conn_win,
            self.settings_win,
            self.mh_window,
            self.wx_window,
            self.userdb_win,
            self.userDB_tree_win,
            self.aprs_mon_win,
            self.aprs_pn_msg_win,
            self.BBS_fwd_q_list,
            self.MSG_Center_win,
            self.newPMS_MSG_win,
            self.fwd_Path_plot_win,
            self.dualPort_settings_win,
            self.dualPortMon_win,
            self.block_list_win,
            self.routingTab_win,
            self.prp_remote_win,
            self.right_level_win,
        ]:
            if hasattr(wn, 'destroy_win'):
                wn.destroy_win()
            if hasattr(wn, 'destroy'):
                wn.destroy()
    # ================================


