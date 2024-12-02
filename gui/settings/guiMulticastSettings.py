import time
import tkinter as tk
from tkinter import ttk

from cfg.default_config import getNew_mcast_channel_cfg
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
from cfg.logger_config import logger
from fnc.str_fnc import get_timedelta_str_fm_sec
from gui.guiError import PoPTModulError


class MCAST_channel_cfg_Tab(tk.Frame):
    def __init__(self, root_tabctl, channel_cfg: dict, root_win):
        tk.Frame.__init__(self, root_tabctl)
        self.pack()
        ##################
        # Vars
        self._root_win = root_win
        self._ch_cfg = channel_cfg
        self._ch_id = tk.StringVar(self, value=channel_cfg.get('ch_id', '-1'))
        self._ch_name = tk.StringVar(self, value=channel_cfg.get('ch_name', ''))
        self._tree_data = []
        self._member_list = {}
        ##################
        # Channel Name
        opt_frame_0 = tk.Frame(self)
        opt_frame_0.pack(fill=tk.X, pady=5)
        tk.Label(opt_frame_0, text='Channel-ID').pack(side=tk.LEFT, padx=5)
        ch_id = tk.Spinbox(opt_frame_0,
                                          # text='CH-ID',
                                          textvariable=self._ch_id,
                                          from_=0,
                                          to=100,
                                          increment=1,
                                          width=4
                                  )

        ch_id.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        ##################
        # Channel Name
        opt_frame_1 = tk.Frame(self)
        opt_frame_1.pack(fill=tk.X)
        tk.Label(opt_frame_1, text='Channel-Name').pack(side=tk.LEFT, padx=5)
        ch_name = tk.Entry(opt_frame_1, textvariable=self._ch_name, width=10)
        ch_name.pack(side=tk.LEFT, padx=5, pady=5)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5, expand=False)
        ##########################################################################################
        # Member List
        opt_frame_2 = tk.Frame(self)
        opt_frame_2.pack(fill=tk.X)
        tk.Label(opt_frame_2, text='Channel Members').pack(pady=5)
        ##################
        # TREE
        tree_frame = tk.Frame(opt_frame_2)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        columns = (
            'member',
            'member_axip',
            'member_last_seen',
        )
        self._tree = ttk.Treeview(tree_frame, columns=columns, show='headings',)
        self._tree.pack(side=tk.LEFT,fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        ###
        self._tree.heading('member', text='Member', ) # command=lambda: self._sort_entry('last')
        self._tree.heading('member_axip', text='AXIP Address', ) # command=lambda: self._sort_entry('first')
        self._tree.heading('member_last_seen', text='Last seen', ) # command=lambda: self._sort_entry('first')
        ###
        self._tree.column("member", anchor=tk.W, stretch=tk.NO, width=120)
        self._tree.column("member_axip", anchor=tk.W, stretch=tk.YES, width=500)
        self._tree.column("member_last_seen", anchor=tk.W, stretch=tk.NO, width=140)
        ###
        self._tree.bind('<<TreeviewSelect>>', self._entry_selected)
        ##################################################################
        # Add / Del Member Btns
        opt_frame_3 = tk.Frame(self)
        opt_frame_3.pack(fill=tk.X)
        add_member_btn = tk.Button(
            opt_frame_3,
            text="Add",
            # command=,
        )
        add_member_btn.pack(side=tk.LEFT)
        del_member_btn = tk.Button(
            opt_frame_3,
            text="Del",
            # command=,
        )
        del_member_btn.pack(side=tk.LEFT, padx=10)
        ###################################################################
        # Init stuff
        self._update_member_tree()
        ###################################################################
        ###################################################################
        # self._init_entry_state()

    def _update_member_tree(self):
        self._init_tree_data()
        self._update_tree()

    def _init_tree_data(self):
        self._tree_data = []
        self._member_list = {}
        member_list = self._ch_cfg.get('ch_members', [])
        axip_list: dict = self._root_win.get_axip_list()
        t_o_list: dict = self._root_win.get_timeout_list()
        for member in member_list:
            member_ip = axip_list.get(member, ('', 0))
            member_t_o = get_timedelta_str_fm_sec(time.time() - t_o_list.get(member, time.time()))
            self._tree_data.append(
                (
                    f"{member}",
                    f"{member_ip[0]} - {member_ip[1]}",
                    f"{member_t_o}"
                )
            )
            self._member_list[member] = member_ip

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)

        for ret_ent in self._tree_data:
            self._tree.insert('', tk.END, values=ret_ent,)

    def _entry_selected(self, event):
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)

    def get_cfg_fm_vars(self):
        ch_id = self._ch_id.get()
        try:
            ch_id = int(ch_id)
        except ValueError:
            return {}
        ch_cfg: dict = getNew_mcast_channel_cfg(ch_id)
        ch_cfg['ch_name'] = str(self._ch_name.get())[:10]
        member_list = []
        member_add_list = {}
        for member, axip in self._member_list.items():
            if member not in member_list:
                member_list.append(member)
            if member not in member_add_list:
                member_add_list[member] = axip
        ch_cfg['ch_members'] = member_list
        ch_cfg['member_add_list'] = member_add_list
        return ch_cfg

class MulticastSettings(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._lang = root_win.language
        self._root_win = root_win
        win_width = 800
        win_height = 580
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.main_win.winfo_x()}+"
                      f"{root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        # self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.title('MCast-Settings')
        # self._root_win.DIGI_settings_win = self
        self._root_win.settings_win = self
        ph = self._root_win.get_PH_manGUI()
        if not hasattr(ph, 'get_mcast_server'):
            self.destroy_win()
            raise PoPTModulError
        self._mcast = ph.get_mcast_server()
        if not hasattr(self._mcast, 'get_mcast_cfgs'):
            self.destroy_win()
            raise PoPTModulError
        self._mcast_cfg: dict = self._mcast.get_mcast_cfgs()
        #####################################################################

        upper_frame_1 = tk.Frame(self)
        upper_frame_1.pack(fill=tk.X)
        ##
        label_1 = tk.Label(upper_frame_1, text='TEST')
        label_1.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        label_2 = tk.Label(upper_frame_1, text='TEST1')
        label_2.pack(side=tk.LEFT, padx=5, pady=5)
        ##########
        upper_frame_2 = tk.Frame(self)
        upper_frame_2.pack(fill=tk.X)
        ##
        add_ch_btn = tk.Button(
            upper_frame_2,
            text='Add Channel',
            command=self._new_ch_btn,
        )
        add_ch_btn.pack(side=tk.LEFT, anchor=tk.W, padx=10)
        del_ch_btn = tk.Button(
            upper_frame_2,
            text='Del Channel',
            command=self._del_ch_btn,
        )
        del_ch_btn.pack(side=tk.LEFT, padx=20, pady=5)

        #####################################################################

        self._tabControl = ttk.Notebook(self)
        self._tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=15)
        # Tab Vars
        self._tab_list: {int: MCAST_channel_cfg_Tab} = {}

        all_channels = self._mcast_cfg.get('mcast_ch_conf', {})
        for ch_id, ch_cfg in all_channels.items():
            tab = MCAST_channel_cfg_Tab(self._tabControl, ch_cfg, self)
            self._tab_list[ch_id] = tab
            port_lable_text = f'CH {ch_id}'
            self._tabControl.add(tab, text=port_lable_text)

        ###########################################
        # BTN
        btn_frame = tk.Frame(self, height=50)
        btn_frame.pack(expand=False, fill=tk.X, padx=10, pady=15)
        ok_btn = tk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_frame, text=STR_TABLE['save'][self._lang], command=self._save_btn)
        save_btn.pack(side=tk.LEFT)

        abort_btn = tk.Button(btn_frame, text=STR_TABLE['cancel'][self._lang], command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    ################################################
    def _new_ch_btn(self):
        last_ch_id = 0
        while last_ch_id in self._mcast_cfg.get('mcast_ch_conf', {}):
            last_ch_id += 1
            if last_ch_id == 100:
                break
        tab = MCAST_channel_cfg_Tab(self._tabControl, getNew_mcast_channel_cfg(last_ch_id), self)
        self._tab_list[last_ch_id] = tab
        port_lable_text = f'CH {last_ch_id}'
        self._tabControl.add(tab, text=port_lable_text)
        self._tabControl.select(last_ch_id)

    def _del_ch_btn(self):
        try:
            tab_ind = self._tabControl.index('current')
            ind = self._tabControl.tab('current')
        except tk.TclError as e:
            logger.error(f"guiMcast-Sett: {e}")
            return
        ind = ind['text']
        try:
            ch_id = int(ind.replace('CH ', '')[0])
        except ValueError as e:
            logger.error(f"guiMcast-Sett: {e}")
            return
        if ch_id not in self._mcast_cfg.get('mcast_ch_conf', {}):
            self._tabControl.forget(tab_ind)
            del self._tab_list[ch_id]
            return
        ch_cfgs = self._mcast_cfg.get('mcast_ch_conf', {})
        del ch_cfgs[ch_id]
        self._mcast_cfg['mcast_ch_conf'] = dict(ch_cfgs)
        del self._tab_list[ch_id]
        self._tabControl.forget(tab_ind)

    ################################################
    def _ok_btn(self):
        self._set_cfg_to_mcast()
        self.destroy_win()

    def _save_btn(self):
        self._save_cfg()

    def _abort_btn(self):
        self.destroy_win()

    def _set_cfg_to_mcast(self):

        ch_configs = {}
        member_add_list = {}
        for tab_id, tab in sorted(self._tab_list.items()):
            ch_cfg: dict = tab.get_cfg_fm_vars()
            if not ch_cfg:
                continue
            ch_id = ch_cfg.get('ch_id', -1)
            if any((ch_id < 0, ch_id in ch_configs)):
                continue
            tmp_add_list = ch_cfg.get('member_add_list', {})
            for mem_call, axip in tmp_add_list.items():
                if mem_call not in member_add_list:
                    member_add_list[mem_call] = tuple(axip)
            del ch_cfg['member_add_list']
            ch_configs[ch_id] = dict(ch_cfg)

        # for new_ch_id in sorted(list(ch_configs.keys())):


        conf: dict = dict(self._mcast_cfg)
        conf['mcast_axip_list'] = member_add_list
        conf['mcast_ch_conf'] = dict(ch_configs)
        POPT_CFG.set_MCast_CFG(conf)


    def _save_cfg(self):
        self._set_cfg_to_mcast()
        self._mcast.reinit_mcast_cfgs()
        # POPT_CFG.save_MAIN_CFG_to_file()

    def get_axip_list(self):
        return self._mcast_cfg.get('mcast_axip_list', {})

    def get_timeout_list(self):
        return self._mcast.get_mcast_timeout_list()

    def destroy_win(self):
        self._root_win.settings_win = None
        self.destroy()
