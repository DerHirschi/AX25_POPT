import tkinter as tk
from tkinter import ttk, Menu
from UserDB.UserDBmain import USER_DB
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from fnc.ax25_fnc import get_list_fm_viaStr
from fnc.socket_fnc import get_ip_by_hostname, check_ip_add_format
from fnc.str_fnc import get_strTab


def getNew_ConnHistory(own_call: str,
                       dest_call: str,
                       add_str: str,
                       port_id: int):
    return {
        'own_call': str(own_call),
        'dest_call': str(dest_call),
        'address_str': str(add_str),
        'port_id': int(port_id),
    }


class NewConnWin(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._main      = main_win
        self.style      = self._main.style
        self._conn_hist = self._main.connect_history
        self.title(self._getTabStr('newcon_title'))
        self.geometry(f"640x220+{self._main.main_win.winfo_x()}+{self._main.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_new_conn_win)
        self.resizable(True, True)
        self.attributes("-topmost", True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        #################################################
        # Vars
        ch_id = self._main.get_free_channel(self._main.channel_index)
        self._port_index                 = 0
        self._port_btn: {int: tk.Button} = {}
        self._call_txt_inp_var           = tk.StringVar(self)
        self._own_call_var               = tk.StringVar(self)
        self._ch_id_var                  = tk.StringVar(self, value=str(ch_id))
        self._axip_ip_var                = tk.StringVar(self)
        self._axip_port_var              = tk.StringVar(self)
        self._ax_ip_ip                   = None
        self._ax_ip_port                 = None
        #################################################
        #
        port_btn_frame   = tk.Frame(self, borderwidth=5)
        dest_call_frame  = tk.Frame(self, borderwidth=5)
        self._axip_frame = tk.Frame(self, borderwidth=5)
        own_call_frame   = tk.Frame(self, borderwidth=5)
        lower_btn_frame  = tk.Frame(self, borderwidth=15)

        port_btn_frame.pack(  side=tk.TOP,    fill=tk.X, padx=10)
        dest_call_frame.pack( side=tk.TOP,    fill=tk.X)
        self._axip_frame.pack(side=tk.TOP,    fill=tk.X, padx=27)
        own_call_frame.pack(  side=tk.TOP,    fill=tk.X, padx=62)
        lower_btn_frame.pack( side=tk.BOTTOM, fill=tk.X)

        port_list = list(PORT_HANDLER.get_all_ports().keys())
        port_list.sort()
        for port in port_list:
            btn = tk.Button(port_btn_frame,
                            text=PORT_HANDLER.get_all_ports()[port].portname,
                            bg="red",
                            width=5,
                            height=1,
                            command=lambda l_port=port: self._set_port_index(l_port)
                            )
            btn.pack(side=tk.LEFT)
            self._port_btn[port] = btn


        call_label = tk.Label(dest_call_frame,
                              text=self._getTabStr('newcon_ziel'),
                              foreground='black',
                              font=("TkFixedFont", 11),
                              height=1,
                              width=5)
        call_label.pack(side=tk.LEFT)

        vals = list(self._conn_hist.keys())
        vals.reverse()
        # self._chiefs = []
        self._call_txt_inp = tk.ttk.Combobox(dest_call_frame,
                                             font=("TkFixedFont", 11),
                                             # height=1,
                                             values=vals,
                                             # width=40,
                                             textvariable=self._call_txt_inp_var
                                             )
        self._call_txt_inp.bind("<<ComboboxSelected>>", self._set_conn_hist)
        # self._call_txt_inp.bind('<KeyRelease>',
        #                         lambda event: get_typed(event, self._chiefs, self.call_txt_inp_var, self._call_txt_inp))
        # self._call_txt_inp.bind('<Key>', lambda event: detect_pressed(event, self._call_txt_inp))
        self._call_txt_inp.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ############
        # AXIP
        self._ax_ip_ip = \
            (
                tk.Label(self._axip_frame,
                         text='IP:',
                         font=("TkFixedFont", 11)),
                tk.Entry(self._axip_frame,
                         textvariable=self._axip_ip_var,
                         font=("TkFixedFont", 11),
                         width=15),
            )
        self._ax_ip_ip[0].pack(side=tk.LEFT)
        self._ax_ip_ip[1].pack(side=tk.LEFT, padx=10)
        self._ax_ip_port = \
            (
                tk.Label(self._axip_frame,
                         text='Port:',
                         font=("TkFixedFont", 11)),
                tk.Entry(self._axip_frame,
                         textvariable=self._axip_port_var,
                         font=("TkFixedFont", 11),
                         width=6)
            )
        self._ax_ip_port[0].pack(side=tk.LEFT, padx=25)
        self._ax_ip_port[1].pack(side=tk.LEFT, padx=10)

        ############
        # Own Call
        opt = ['NOCALL']
        if self._port_index in PORT_HANDLER.get_all_ports().keys():
            # opt = PORT_HANDLER.get_all_ports()[self._port_index].my_stations
            opt = PORT_HANDLER.get_stat_calls_fm_port(self._port_index)
            if not opt:
                opt = ['NOCALL']
            self._own_call_var.set(opt[0])

        self._own_call_dd_men = tk.OptionMenu(own_call_frame,
                                              self._own_call_var,
                                              *opt)
        self._own_call_dd_men.pack(side=tk.LEFT)
        ############
        # CH-ID
        ch_id_frame = tk.Frame(own_call_frame)
        ch_id_frame.pack(side=tk.LEFT, padx=120)
        ch_opt = self._main.get_all_free_channels()
        if not ch_opt:
            ch_opt = ['']
        tk.Label(ch_id_frame,
                 text=self._getTabStr('channel'),
                 font=("TkFixedFont", 11),
                 ).pack(side=tk.LEFT, padx=15)
        ch_id_opt = tk.OptionMenu(ch_id_frame,
                                              self._ch_id_var,
                                              *ch_opt)
        ch_id_opt.pack(side=tk.LEFT)
        ############
        # BTN
        conn_btn = tk.Button(lower_btn_frame,
                             text=self._getTabStr('go'),
                             font=("TkFixedFont", 13),
                             bg="green",
                             #height=1,
                             #width=4,
                             command=self._process_new_conn_win)
        conn_btn.pack(side=tk.LEFT, padx=10)
        abort_btn = tk.Button(lower_btn_frame,
                             text=self._getTabStr('cancel'),
                             #font=("TkFixedFont", 13),
                             #height=1,
                             #width=4,
                             command=lambda: self._destroy_new_conn_win())
        abort_btn.pack(side=tk.RIGHT, anchor=tk.E, padx=10)
        ##############
        # KEY BINDS
        self.bind('<Return>',   lambda event: self._process_new_conn_win())
        self.bind('<KP_Enter>', lambda event: self._process_new_conn_win())
        self.bind('<Escape>',   lambda event: self._destroy_new_conn_win())
        ##############
        # Menubar
        self._init_menubar()
        self._main.new_conn_win = self
        ##############
        self._set_port_btn()

        self._call_txt_inp.focus_set()
        self._set_port_index(self._port_index)

    def _init_menubar(self):
        menubar     = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb    = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('delete'), command=self._reset_conn_history)
        menubar.add_cascade( label=self._getTabStr('newcon_history'), menu=MenuVerb, underline=0)

    def _set_port_index(self, index: int):
        port = PORT_HANDLER.get_port_by_index(index)
        if port:
            index = port.port_id
            self._port_index = index
            if port.port_typ == 'AXIP':

                call_str = self._call_txt_inp_var.get().upper()
                if call_str:
                    call_str = call_str.split(' ')[0]
                self._ax_ip_ip[1].configure(state='normal')
                self._ax_ip_port[1].configure(state='normal')
                mh_ent = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(call_str, 0)
                # Just if u switch after enter in call
                if mh_ent[1]:
                    ip  = mh_ent[0]
                    prt = str(mh_ent[1])
                    self._axip_ip_var.set(ip)
                    self._axip_port_var.set(prt)
                self._call_txt_inp.focus_set()

                port = PORT_HANDLER.get_port_by_index(self._port_index)
                if not port:
                    opt = ['']
                else:
                    opt = PORT_HANDLER.get_stat_calls_fm_port(self._port_index)
                if not opt:
                    opt = ['']

                self._own_call_var.set('')
                self._own_call_dd_men['menu'].delete(0, 'end')

                # Insert list of new options (tk._setit hooks them up to var)
                for el in opt:
                    self._own_call_dd_men['menu'].add_command(label=el,
                                                              command=tk._setit(self._own_call_var, el))
                if opt:
                    self._own_call_var.set(opt[0])

            else:
                if self._ax_ip_ip is not None:
                    self._ax_ip_ip[1].configure(state='disabled')
                    self._ax_ip_port[1].configure(state='disabled')

                port = PORT_HANDLER.get_port_by_index(self._port_index)
                if not port:
                    opt = ['']
                else:
                    opt = PORT_HANDLER.get_stat_calls_fm_port(self._port_index)
                if not opt:
                    opt = ['']
                self._own_call_var.set('')
                self._own_call_dd_men['menu'].delete(0, 'end')

                # Insert list of new options (tk._setit hooks them up to var)
                for el in opt:
                    self._own_call_dd_men['menu'].add_command(label=el,
                                                              command=tk._setit(self._own_call_var, el))

                if opt:
                    self._own_call_var.set(opt[0])
            self._set_port_btn()

    def _set_port_btn(self):
        for k in self._port_btn.keys():
            btn = self._port_btn[k]
            if k == self._port_index:
                btn.configure(bg='green')
            else:
                btn.configure(bg='red')

    def _process_new_conn_win(self):
        axip_address    = ('', 0)
        addrs_str       = self._call_txt_inp_var.get().upper()
        # ch_id           = self._main.get_free_channel(self._main.channel_index)
        try:
            ch_id       = int(self._ch_id_var.get())
        except ValueError:
            ch_id        = self._main.get_free_channel(self._main.channel_index)
        if ch_id is None:
            self._main.sysMsg_to_monitor('*** Error. No free Channel.')
            return
        if addrs_str:
            own_call = self._own_call_var.get()
            call_list = get_list_fm_viaStr(addrs_str)
            if not call_list:
                self._main.sysMsg_to_qso('*** Error. No valid Address.', ch_id)
                return
            dest_call = call_list[0]
            via_calls = call_list[1:]
            port = PORT_HANDLER.get_port_by_index(self._port_index)
            if port:
                if port.port_typ == 'AXIP':
                    # Just if u switch after enter in call
                    axip_ip_inp = self._ax_ip_ip[1].get()
                    axip_port   = self._ax_ip_port[1].get()
                    axip_ip     = get_ip_by_hostname(axip_ip_inp)
                    if not axip_ip and not check_ip_add_format(axip_ip_inp):
                        mh_ent = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(dest_call)
                        if mh_ent[0]:
                            ip = mh_ent[0]
                            prt = str(mh_ent[1])
                            self._ax_ip_ip[1].delete('1.0', tk.END)
                            self._ax_ip_ip[1].insert(tk.END, ip)
                            self._ax_ip_port[1].delete('1.0', tk.END)
                            self._ax_ip_port[1].insert(tk.END, prt)
                            axip_port = prt
                            if check_ip_add_format(ip):
                                axip_ip = ip
                            else:
                                axip_ip = get_ip_by_hostname(axip_ip)
                    else:

                        USER_DB.set_AXIP(str(dest_call), (axip_ip_inp, axip_port))

                    if axip_port.isdigit() and check_ip_add_format(axip_ip):
                        axip_address = axip_ip, int(axip_port)
                    else:
                        self._main.sysMsg_to_qso('*** Error. No valid AXIP-Address.', ch_id)
                        return

                # conn = PORT_HANDLER.get_all_ports()[self.port_index].new_connection(ax25_frame=ax_frame)
                conn, msg = PORT_HANDLER.new_outgoing_connection(
                    dest_call=dest_call,
                    own_call=own_call,
                    via_calls=via_calls,  # Auto lookup in MH if not exclusive Mode
                    port_id=self._port_index,  # -1 Auto lookup in MH list
                    axip_add=axip_address,  # AXIP Adress
                    exclusive=True,  # True = no lookup in MH list
                    link_conn=None,  # Linked Connection AX25Conn
                    channel=int(ch_id)  # Channel/Connection Index = Channel-ID
                )
                self._main.sysMsg_to_qso(msg, ch_id)

                if conn:
                    if addrs_str in list(self._conn_hist.keys()):
                        # Bring the newest Entry up in the List
                        del self._conn_hist[addrs_str]
                    self._conn_hist[addrs_str] = getNew_ConnHistory(
                        own_call=own_call,
                        dest_call=dest_call,
                        add_str=addrs_str,
                        port_id=self._port_index,
                    )
                    self._main.ch_status_update()
                    self._destroy_new_conn_win()

    def _set_conn_hist(self, event):
        ent_key  = self._call_txt_inp_var.get().upper()
        port_id  = self._conn_hist.get(ent_key, {}).get('port_id', None)
        own_call = self._conn_hist.get(ent_key, {}).get('own_call', '')
        if port_id is not None:
            self._set_port_index(port_id)
        if own_call:
            self._own_call_var.set(own_call)

    def _set_ownCall_fm_hist(self):
        ent_key  = self._call_txt_inp_var.get().upper()
        own_call = self._conn_hist.get(ent_key, {}).get('own_call', '')
        if own_call:
            self._own_call_var.set(own_call)

    def preset_ent(self, call: str, port_id: int):
        if not call:
            return
        self._call_txt_inp_var.set(call.upper())
        self._set_port_index(port_id)
        self._set_ownCall_fm_hist()

    def _reset_conn_history(self, event=None):
        self._conn_hist            = {}
        self._main.connect_history = {}
        vals = list(self._conn_hist.keys())
        vals.reverse()
        self._call_txt_inp.config(values=vals)

    def _destroy_new_conn_win(self):
        self.destroy()
        self._main.new_conn_win = None
