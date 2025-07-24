import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab
from gui.bbs_gui.bbs_MSGcenter_gui.guiBBS_MSG_c_BBS import MSG_Center_BBS
from gui.bbs_gui.bbs_MSGcenter_gui.guiBBS_MSG_c_PMS import MSG_Center_PMS
from gui.bbs_gui.guiBBS_newMSG import BBS_newMSG


class MSG_Center(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        # Vars
        PORT_HANDLER.set_pmsMailAlarm(False)
        self._bbs_obj           = PORT_HANDLER.get_bbs()
        self.text_size          = int(POPT_CFG.load_guiPARM_main().get('guiMsgC_parm_text_size', self._root_win.text_size))
        self.newPMS_MSG_win     = self._root_win.newPMS_MSG_win
        ###################################
        self.title(self._getTabStr('msg_center'))
        self.style      = self._root_win.style
        self.style_name = self._root_win.style_name
        # self.geometry("1250x700")
        self.geometry(f"1250x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ######################################################################
        # APRS/BBS TABS
        upper_frame = ttk.Frame(self, )
        upper_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_type = ttk.Notebook(
            upper_frame,
            padding=5,
        )
        self._tabControl_type.pack(side=tk.TOP, fill=tk.BOTH, expand=True, )

        self._PMS_tab_frame   = MSG_Center_PMS(self)
        self._BBS_tab_frame   = MSG_Center_BBS(self)
        APRS_tab_frame  = ttk.Frame(self)
        self._PMS_tab_frame.pack( side=tk.TOP, fill=tk.BOTH, expand=True)
        self._BBS_tab_frame.pack( side=tk.TOP, fill=tk.BOTH, expand=True)
        APRS_tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_type.add(self._PMS_tab_frame,  text='PMS',  padding=8)
        self._tabControl_type.add(self._BBS_tab_frame,  text='BBS',  padding=8)
        self._tabControl_type.add(APRS_tab_frame, text='APRS', padding=8, state='disabled') # TODO
        ################################################
        # APRS-TAB
        # TODO APRS
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ################################################
        # ---------------------------------------------
        ###############################################
        self._init_Menu()
        ###############################################
        # Keybindings
        self.bind('<Control-plus>',  lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())
        self.bind('<Control-c>', lambda event: self._copy_select())
        #####################
        # Get Settings fm CFG
        self._root_win.MSG_Center_win = self
        self._init_Vars_fm_Cfg()

    def _init_Menu(self):
        menubar = tk.Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = tk.Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('new'), command=lambda: self._open_newMSG_win())
        MenuVerb.add_separator()
        MenuVerb.add_command(label=self._getTabStr('send_all_now'), command=lambda: self._do_pms_autoFWD())
        menubar.add_cascade(label=self._getTabStr('msg'), menu=MenuVerb, underline=0)
        # ### Bearbeiten
        #MenuEdit = tk.Menu(menubar, tearoff=False)
        #MenuEdit.add_command(label=self._getTabStr('mark_all_read'),
        #                      command=self._set_all_to_oldMSG,
        #                      underline=0)
        #MenuVerb.add_separator()
        #MenuEdit.add_command(label=self._getTabStr('save_to_file'),
        #                      command=self._save_msg_to_file,
        #                      underline=0)
        #menubar.add_cascade(label=self._getTabStr('edit'), menu=MenuEdit, underline=0)

    def _init_Vars_fm_Cfg(self):
        pass
        # self.text_size = int(POPT_CFG.get_guiCFG_main().get('guiMsgC_parm_text_size', self._root_win.text_size))

    def _save_Vars_to_Cfg(self):
        cfg = POPT_CFG.load_guiPARM_main()
        cfg['guiMsgC_parm_text_size'] = self.text_size
        POPT_CFG.save_guiPARM_main(cfg)

    #####################################
    # GUI
    def _set_all_to_oldMSG(self):
        # TODO
        pass

    def _increase_textsize(self):
        self.text_size += 1
        self.text_size = max(self.text_size, 3)
        self._BBS_tab_frame.increase_textsize()
        self._PMS_tab_frame.increase_textsize()

    def _decrease_textsize(self):
        self.text_size -= 1
        self.text_size = max(self.text_size, 3)
        self._BBS_tab_frame.decrease_textsize()
        self._PMS_tab_frame.decrease_textsize()

    def _update_textsize_trees(self):
        self._BBS_tab_frame.update_textsize_trees()
        self._PMS_tab_frame.update_textsize_trees()

    def _copy_select(self):
        try:
            ind = self._tabControl_type.index(self._tabControl_type.select())
        except tk.TclError:
            return
        sel_tab = {
            0: self._PMS_tab_frame,
            1: self._BBS_tab_frame,
        }.get(ind, None)
        if hasattr(sel_tab, 'copy_select'):
            sel_tab.copy_select()

    ################################
    def _open_newMSG_win(self):
        if self.newPMS_MSG_win:
            return
        self.newPMS_MSG_win = BBS_newMSG(self)

    ################################
    def tree_update_task(self):
        # Global Update trigger fm Porthandler
        # TODO
        """
        try:
            ind = self._tabControl.index(self._tabControl.select())
        except tk.TclError:
            return
        update_task = {
            0: self._update_PN_tree_data,
            1: self._update_BL_tree_data,
            2: self._update_OUT_tree_data,
            # 3: self._update_SV_tree_data_pms,
        }.get(ind, None)
        if update_task:
            update_task()
        # self._pn_tree.selection_set('"Row 0"')
        """
        pass

    ####################
    def _do_pms_autoFWD(self):
        self._bbs_obj.start_man_autoFwd()


    ################################
    def _close(self):
        self._save_Vars_to_Cfg()
        self._bbs_obj = None
        self._root_win.MSG_Center_win = None
        self.destroy()
