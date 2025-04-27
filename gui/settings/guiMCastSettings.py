import time
import tkinter as tk
from tkinter import ttk

from cfg.constant import MAX_MCAST_CH
from cfg.default_config import getNew_mcast_channel_cfg
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
from cfg.logger_config import logger
from fnc.ax25_fnc import validate_ax25Call
from fnc.socket_fnc import get_ip_by_hostname
from fnc.str_fnc import get_timedelta_str_fm_sec
from gui.guiError import PoPTModulError

class MCastAddMember(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win)
        self._root_win = root_win
        self._mcast = root_win.get_mcast()

        self._lang = POPT_CFG.get_guiCFG_language()
        win_width = 550
        win_height = 180
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.attributes("-topmost", True)
        self.title('Move to Channel')
        ##################################
        f0 = ttk.Frame(self)
        f0.pack()
        ttk.Label(f0, text='Call:').pack(side=tk.LEFT, pady=15)
        #
        self._call_ent_var = tk.StringVar(self)
        ent = ttk.Entry(f0, textvariable=self._call_ent_var, width=10)
        ent.pack(side=tk.LEFT, padx=5)
        ##################################
        f1 = ttk.Frame(self)
        f1.pack()
        ttk.Label(f1, text='Adress:').pack(side=tk.LEFT, pady=15)
        #
        self._add_ent_var = tk.StringVar(self)
        ent = ttk.Entry(f1, textvariable=self._add_ent_var, width=30)
        ent.pack(side=tk.LEFT, padx=5)
        ##
        ttk.Label(f1, text='Port:').pack(side=tk.LEFT)
        #
        self._port_ent_var = tk.StringVar(self)
        p_ent = ttk.Entry(f1, textvariable=self._port_ent_var, width=6)
        p_ent.pack(side=tk.LEFT, padx=5)

        ###########################################
        ###########################################
        # BTN
        btn_frame = ttk.Frame(self)
        btn_frame.pack(expand=True, fill=tk.X, padx=10, pady=5, anchor=tk.S)
        ok_btn = ttk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)

        abort_btn = ttk.Button(btn_frame, text=STR_TABLE['cancel'][self._lang], command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    def _set_member_address(self):
        call = self._call_ent_var.get().upper()
        if not validate_ax25Call(call):
            return False
        address = self._add_ent_var.get()
        if not get_ip_by_hostname(address):
            return False
        try:
            port = int(self._port_ent_var.get())
        except ValueError:
            return False
        mcast = self._root_win.get_mcast()
        if not all((
                hasattr(mcast, 'set_member_ip'),
                hasattr(mcast, 'move_member_to_channel'),
                hasattr(mcast, 'get_mcast_cfgs'),
        )):
            return False
        if not mcast.set_member_ip(call, (address, port)):
            return False
        mcast_conf: dict = mcast.get_mcast_cfgs()
        default_ch = mcast_conf.get('mcast_default_ch', None)
        if default_ch is None:
            return False
        return mcast.move_member_to_channel(member_call=call, channel_id=default_ch)

    def _ok_btn(self):
        if self._set_member_address():
            if hasattr(self._root_win, 'reinit_MCastGui'):
                self._root_win.reinit_MCastGui()
            self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        self._root_win.value_win = None
        self.destroy()


class MCastMoveMember(tk.Toplevel):
    def __init__(self, root_win, member_call: str):
        tk.Toplevel.__init__(self, master=root_win)
        self._root_win = root_win
        self._member_call = member_call
        self._mcast = root_win.get_mcast()
        if not hasattr(self._mcast, 'get_mcast_cfgs'):
            raise PoPTModulError
        self._mcast_cfg: dict = self._mcast.get_mcast_cfgs()
        self._ackt_ch = self._mcast.get_member_channel(member_call)
        if self._ackt_ch is None:
            self.destroy_win()
            return
        self._lang = POPT_CFG.get_guiCFG_language()
        win_width = 330
        win_height = 130
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.attributes("-topmost", True)
        self.title('Move to Channel')
        ##################################
        f1 = ttk.Frame(self)
        f1.pack()
        ttk.Label(f1, text='Channel').pack(side=tk.LEFT, pady=30)
        #
        channels = list(self._mcast_cfg.get('mcast_ch_conf', {}).keys())
        self._ent_var = tk.StringVar(self, str(self._ackt_ch))
        ent = ttk.OptionMenu(f1, self._ent_var, *channels)
        ent.pack(side=tk.LEFT, padx=5)
        ###########################################
        ###########################################
        # BTN
        btn_frame = ttk.Frame(self)
        btn_frame.pack(expand=True, fill=tk.X, padx=10, pady=5, anchor=tk.S)
        ok_btn = ttk.Button(btn_frame, text=' OK ', command=self._ok_btn)
        ok_btn.pack(side=tk.LEFT)

        abort_btn = ttk.Button(btn_frame, text=STR_TABLE['cancel'][self._lang], command=self._abort_btn)
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E)

    def _move_member_to_ch(self):
        channels = list(self._mcast_cfg.get('mcast_ch_conf', {}).keys())
        try:
            sel_ch = int(self._ent_var.get())
        except ValueError:
            return False
        if self._ackt_ch == sel_ch:
            return False
        if sel_ch not in channels:
            return False
        if not hasattr(self._mcast, 'move_member_to_channel'):
            return False
        return self._mcast.move_member_to_channel(member_call=self._member_call, channel_id=sel_ch)

    def _ok_btn(self):
        if self._move_member_to_ch():
            if hasattr(self._root_win, 'reinit_MCastGui'):
                self._root_win.reinit_MCastGui()
        self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        self._root_win.value_win = None
        self.destroy()

class MCAST_channel_cfg_Tab(ttk.Frame):
    def __init__(self, root_tabctl, channel_cfg: dict, root_win):
        ttk.Frame.__init__(self, root_tabctl)
        self.pack()
        ##################
        # Vars
        self._root_win = root_win
        self._ch_cfg = channel_cfg
        self._ch_id = tk.StringVar(self, value=channel_cfg.get('ch_id', '-1'))
        self._ch_name = tk.StringVar(self, value=channel_cfg.get('ch_name', ''))
        self._ch_private = tk.BooleanVar(self, value=channel_cfg.get('ch_private', False))
        self._tree_data = []
        self._member_list = {}
        self._selected_entry = ''
        ##################
        # Channel Name
        opt_frame_0 = ttk.Frame(self)
        opt_frame_0.pack(fill=tk.X, pady=5)
        ttk.Label(opt_frame_0, text='Channel-ID').pack(side=tk.LEFT, padx=5)
        ch_id = ttk.Spinbox(opt_frame_0,
                                          # text='CH-ID',
                                          textvariable=self._ch_id,
                                          from_=0,
                                          to=MAX_MCAST_CH - 1,
                                          increment=1,
                                          width=4
                                  )

        ch_id.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        #########
        # Private
        ch_private_chb = ttk.Checkbutton(opt_frame_0, text='Private', variable=self._ch_private)
        ch_private_chb.pack(side=tk.RIGHT, anchor=tk.E, padx=5)
        mcast_cfg: dict = root_win.get_mcast().get_mcast_cfgs()
        default_ch_id = str(mcast_cfg.get('mcast_default_ch', 0))
        if self._ch_id.get() == default_ch_id:
            self._ch_private.set(False)
            ch_private_chb.configure(state='disabled')
        ##################
        # Channel Name
        opt_frame_1 = ttk.Frame(self)
        opt_frame_1.pack(fill=tk.X)
        ttk.Label(opt_frame_1, text='Channel-Name').pack(side=tk.LEFT, padx=5)
        ch_name = ttk.Entry(opt_frame_1, textvariable=self._ch_name, width=10)
        ch_name.pack(side=tk.LEFT, padx=5, pady=5)
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5, expand=False)
        ##########################################################################################
        # Member List
        opt_frame_2 = ttk.Frame(self)
        opt_frame_2.pack(fill=tk.X)
        ttk.Label(opt_frame_2, text='Channel Members').pack(pady=5)
        ##################
        # TREE
        tree_frame = ttk.Frame(opt_frame_2)
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
        opt_frame_3 = ttk.Frame(self)
        opt_frame_3.pack(fill=tk.X)
        add_member_btn = ttk.Button(
            opt_frame_3,
            text="Add Member",
            command=self._add_member_btn,
        )
        add_member_btn.pack(side=tk.LEFT)

        move_member_btn = ttk.Button(
            opt_frame_3,
            text="Move Member",
            command=self._move_member_btn,
        )
        move_member_btn.pack(side=tk.LEFT, padx=5)

        del_member_btn = ttk.Button(
            opt_frame_3,
            text="Del Member",
            command=self._del_member_btn,
        )
        del_member_btn.pack(side=tk.RIGHT, )
        ###################################################################
        # Init stuff
        self.update_member_tree()
        ###################################################################
        ###################################################################
        # self._init_entry_state()

    def update_member_tree(self):
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
    ##########################################################
    def _entry_selected(self, event):
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            call = item.get('values', [])
            if not call:
                self._selected_entry = ''
                return
            try:
                self._selected_entry = call[0]
            except IndexError:
                self._selected_entry = ''
                return


    ################################
    # BTN CMDs
    def _move_member_btn(self):
        if not self._selected_entry:
            return
        self._root_win.open_value_win(str(self._selected_entry))

    def _del_member_btn(self):
        if not self._selected_entry:
            return
        if not hasattr(self._root_win, 'del_member'):
            return
        self._root_win.del_member(str(self._selected_entry))

    def _add_member_btn(self):
        self._root_win.open_address_win()

    ##########################################################
    def get_cfg_fm_vars(self):
        ch_id = self._ch_id.get()
        try:
            ch_id = int(ch_id)
        except ValueError:
            return {}
        ch_cfg: dict = getNew_mcast_channel_cfg(ch_id)
        ch_cfg['ch_name'] = str(self._ch_name.get())[:10]
        ch_cfg['ch_private'] = bool(self._ch_private.get())
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

    def set_ch_conf(self, ch_conf: dict):
        if not ch_conf:
            return False
        self._ch_cfg = ch_conf

class MulticastSettings(ttk.Frame):
    def __init__(self, tabctl , root_win):
        ttk.Frame.__init__(self, tabctl)
        ph = root_win.get_PH()
        if not hasattr(ph, 'get_mcast_server'):
            # self.destroy_win()
            raise PoPTModulError
        self._mcast = ph.get_mcast_server()
        if not hasattr(self._mcast, 'get_mcast_cfgs'):
            # self.destroy_win()
            raise PoPTModulError
        self._lang = POPT_CFG.get_guiCFG_language()
        self._root_win = root_win
        self.value_win = None
        # win_width = 800
        # win_height = 580
        # self.style = root_win.style
        """
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.main_win.winfo_x()}+"
                      f"{root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(True, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.title('MCast-Settings')
        """
        # self._root_win.settings_win = self
        self._mcast_cfg: dict = self._mcast.get_mcast_cfgs()
        #####################################################################
        # Vars
        self._init_to_var = tk.StringVar(self, str(self._mcast_cfg.get('mcast_member_init_timeout', 5)))
        self._member_to_var = tk.StringVar(self, str(self._mcast_cfg.get('mcast_member_timeout', 60)))
        self._reg_new_user = tk.BooleanVar(self, bool(self._mcast_cfg.get('mcast_new_user_reg', True)))
        #####################################################################
        upper_frame_1 = ttk.Frame(self)
        upper_frame_1.pack(fill=tk.X, pady=10)
        ##
        to_frame = ttk.Frame(upper_frame_1)
        to_frame.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        ttk.Label(to_frame, text='Member Timeout').pack(side=tk.LEFT, anchor=tk.W, padx=5)
        member_to = ttk.Spinbox(to_frame,
                           # text='CH-ID',
                           textvariable=self._member_to_var,
                           from_=5,
                           to=120,
                           increment=5,
                           width=4
                           )
        member_to.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        ###
        init_to_frame = ttk.Frame(upper_frame_1)
        init_to_frame.pack(side=tk.LEFT, anchor=tk.W, padx=80)
        ttk.Label(init_to_frame, text='Init Timeout').pack(side=tk.LEFT, padx=5)
        init_to = ttk.Spinbox(init_to_frame,
                               # text='CH-ID',
                               textvariable=self._init_to_var,
                               from_=0,
                               to=30,
                               increment=1,
                               width=4
                               )
        init_to.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        ###
        # reg_new_user_frame = tk.Frame(upper_frame_1)
        # reg_new_user_frame.pack(side=tk.LEFT, anchor=tk.W, padx=80)
        reg_new_user = ttk.Checkbutton(upper_frame_1,
                             text='Allow new Members',
                             variable=self._reg_new_user
                             )
        reg_new_user.pack(side=tk.LEFT, anchor=tk.W, )
        ##########
        upper_frame_2 = ttk.Frame(self)
        upper_frame_2.pack(fill=tk.X)
        ##
        add_ch_btn = ttk.Button(
            upper_frame_2,
            text='Add Channel',
            command=self._new_ch_btn,
        )
        add_ch_btn.pack(side=tk.LEFT, anchor=tk.W, padx=10)

        del_ch_btn = ttk.Button(
            upper_frame_2,
            text='Del Channel',
            command=self._del_ch_btn,
        )
        del_ch_btn.pack(side=tk.LEFT, padx=20, pady=5)

        #####################################################################

        self._tabControl = ttk.Notebook(self)
        self._tabControl.bind('<<NotebookTabChanged>>', self._tab_change)
        self._tabControl.pack(expand=True, fill=tk.BOTH, padx=10, pady=15)
        # Tab Vars
        self._tab_list: {int: MCAST_channel_cfg_Tab} = {}

        all_channels = self._mcast_cfg.get('mcast_ch_conf', {})
        for ch_id, ch_cfg in all_channels.items():
            tab = MCAST_channel_cfg_Tab(self._tabControl, ch_cfg, self)
            self._tab_list[ch_id] = tab
            port_lable_text = f'CH {ch_id}'
            self._tabControl.add(tab, text=port_lable_text)

    def reinit_MCastGui(self):
        self._mcast_cfg: dict = self._mcast.get_mcast_cfgs()
        self._init_to_var.set(str(self._mcast_cfg.get('mcast_member_init_timeout', 5)))
        self._member_to_var.set(str(self._mcast_cfg.get('mcast_member_timeout', 60)))
        self._reg_new_user.set(bool(self._mcast_cfg.get('mcast_new_user_reg', True)))
        for ch_id, tab in self._tab_list.items():
            if hasattr(tab, 'set_ch_conf'):
                tab.set_ch_conf(self._mcast_cfg.get('mcast_ch_conf', {}).get(ch_id, getNew_mcast_channel_cfg(ch_id)))
            if hasattr(tab, 'update_member_tree'):
                tab.update_member_tree()

    ################################################
    def _new_ch_btn(self):
        last_ch_id = 0
        while last_ch_id in self._mcast_cfg.get('mcast_ch_conf', {}).keys():
            last_ch_id += 1
            if last_ch_id == MAX_MCAST_CH:
                return
        ch_conf = getNew_mcast_channel_cfg(last_ch_id)
        ch_lable_text = f'CH {last_ch_id}'
        ch_conf['ch_name'] = ch_lable_text
        tab = MCAST_channel_cfg_Tab(self._tabControl, ch_conf, self)
        self._tab_list[last_ch_id] = tab
        self._tabControl.add(tab, text=ch_lable_text)
        self._mcast_cfg['mcast_ch_conf'][last_ch_id] = ch_conf
        self._set_cfg_to_mcast()
        self._mcast.reinit_mcast_cfgs()
        try:
            self._tabControl.select(last_ch_id)
        except tk.TclError:
            pass

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
        self._set_cfg_to_mcast()
        self._mcast.reinit_mcast_cfgs()

    ################################################
    ################################################
    def _tab_change(self, event=None):
        self.reinit_MCastGui()

    ################################################
    def _set_cfg_to_mcast(self):
        # TODO Check if CFG has changed.. (Members has moved to other Channel)
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

        conf: dict = dict(self._mcast_cfg)
        conf['mcast_axip_list'] = member_add_list
        conf['mcast_ch_conf'] = dict(ch_configs)
        conf['mcast_new_user_reg'] = bool(self._reg_new_user.get())
        try:
            conf['mcast_member_timeout'] = int(self._member_to_var.get())
        except ValueError:
            conf['mcast_member_timeout'] = int(self._mcast_cfg.get('mcast_member_timeout', 60))
        try:
            conf['mcast_member_init_timeout'] = int(self._init_to_var.get())
        except ValueError:
            conf['mcast_member_init_timeout'] = int(self._mcast_cfg.get('mcast_member_init_timeout', 5))
        conf['mcast_server_call'] = str(POPT_CFG.get_MCast_server_call())
        logger.debug(conf)
        POPT_CFG.set_MCast_CFG(conf)

    def _save_cfg(self):
        self._set_cfg_to_mcast()
        self._mcast.reinit_mcast_cfgs()
        # POPT_CFG.save_MAIN_CFG_to_file()

    def get_axip_list(self):
        return self._mcast_cfg.get('mcast_axip_list', {})

    def get_timeout_list(self):
        return self._mcast.get_mcast_timeout_list()

    def get_mcast(self):
        return self._mcast

    def del_member(self, member_call: str ):
        if not member_call:
            return
        if not hasattr(self._mcast, 'del_member'):
            return
        self._mcast.del_member(member_call=member_call)
        self.reinit_MCastGui()

    def open_value_win(self, arg: str):
        if not arg:
            return
        if self.value_win:
            return
        self.value_win = MCastMoveMember(self, member_call=arg)

    def open_address_win(self):
        if self.value_win:
            return
        self.value_win = MCastAddMember(self)

    def destroy_win(self):
        if hasattr(self.value_win, 'destroy_win'):
            self.value_win.destroy_win()
        # self._root_win.settings_win = None
        self.destroy()

    def _get_config(self):
        return dict(self._mcast.get_mcast_cfgs())

    def save_config(self):
        old_cfg = self._get_config()
        self._set_cfg_to_mcast()
        if old_cfg == self._get_config():
            return False
        self._mcast.reinit_mcast_cfgs()
        return True
