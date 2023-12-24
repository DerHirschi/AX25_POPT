# TODO AGAIN
import tkinter as tk
from tkinter import ttk, Menu
from UserDB.UserDBmain import USER_DB
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.string_tab import STR_TABLE
from fnc.ax25_fnc import get_list_fm_viaStr
# from ax25.ax25Statistics import MH_LIST
from fnc.socket_fnc import get_ip_by_hostname, check_ip_add_format


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
    # TODO Again . . .
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self._main = main_win
        self._lang = self._main.language
        self.style = self._main.style
        self._conn_hist = self._main.connect_history
        # self._new_conn_win = tk.Tk()
        self.title("New Connection")
        self.geometry(f"700x285+{self._main.main_win.winfo_x()}+{self._main.main_win.winfo_y()}")
        # self.geometry("700x285")
        self.protocol("WM_DELETE_WINDOW", self._destroy_new_conn_win)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.columnconfigure(0, minsize=20, weight=1)
        self.columnconfigure(1, minsize=100, weight=1)
        self.columnconfigure(2, minsize=50, weight=5)
        self.columnconfigure(3, minsize=120, weight=1)
        self.columnconfigure(4, minsize=20, weight=1)
        self.rowconfigure(0, minsize=38, weight=3)
        self.rowconfigure(1, minsize=5, weight=5)
        self.rowconfigure(2, minsize=35, weight=3)
        self.rowconfigure(3, minsize=5, weight=1)
        self.rowconfigure(4, minsize=40, weight=3)
        self.rowconfigure(5, minsize=40, weight=1)
        self._port_index = 0
        self._port_btn: {int: tk.Button} = {}
        for port in PORT_HANDLER.get_all_ports().keys():
            tmp = tk.Button(self,
                            text=PORT_HANDLER.get_all_ports()[port].portname,
                            bg="red",
                            width=5,
                            height=1,
                            command=lambda l_port=port: self.set_port_index(l_port)
                            )
            if port:
                tmp.place(x=10 + (80 * port), y=1)
            else:
                tmp.place(x=10, y=1)
            self._port_btn[port] = tmp

        self._set_port_btn()

        call_label = tk.Label(self,
                              text='Ziel:',
                              foreground='black',
                              font=("TkFixedFont", 11),
                              height=1,
                              width=5)
        call_label.place(x=2, y=40)

        vals = list(self._conn_hist.keys())
        vals.reverse()
        self.call_txt_inp_var = tk.StringVar(self)
        # self._chiefs = []
        self._call_txt_inp = tk.ttk.Combobox(self,
                                             font=("TkFixedFont", 11),
                                             # height=1,
                                             values=vals,
                                             width=45,
                                             textvariable=self.call_txt_inp_var
                                             )
        self._call_txt_inp.bind("<<ComboboxSelected>>", self._set_conn_hist)
        # self._call_txt_inp.bind('<KeyRelease>',
        #                         lambda event: get_typed(event, self._chiefs, self.call_txt_inp_var, self._call_txt_inp))
        # self._call_txt_inp.bind('<Key>', lambda event: detect_pressed(event, self._call_txt_inp))
        self._call_txt_inp.place(x=80, y=40)
        self.ax_ip_ip = None
        self.ax_ip_port = None
        ############
        # Own Call
        self.own_call_var = tk.StringVar(self)
        opt = ['NOCALL']
        if self._port_index in PORT_HANDLER.get_all_ports().keys():
            opt = PORT_HANDLER.get_all_ports()[self._port_index].my_stations
            if not opt:
                opt = ['NOCALL']
            self.own_call_var.set(opt[0])

        self.own_call_dd_men = tk.OptionMenu(self, self.own_call_var, *opt)
        ############
        # BTN
        conn_btn = tk.Button(self,
                             text="Los",
                             font=("TkFixedFont", 13),
                             bg="green",
                             height=1,
                             width=4,
                             command=self._process_new_conn_win)
        conn_btn.place(x=10, y=220)
        self._call_txt_inp.focus_set()
        self.set_port_index(self._port_index)
        ##############
        # KEY BINDS
        self.bind('<Return>', lambda event: self._process_new_conn_win())
        self.bind('<KP_Enter>', lambda event: self._process_new_conn_win())
        self.bind('<Escape>', lambda event: self._destroy_new_conn_win())
        ##############
        # Menubar
        self._init_menubar()
        self._main.new_conn_win = self

    def _init_menubar(self):
        _menubar = Menu(self, tearoff=False)
        self.config(menu=_menubar)
        _MenuVerb = Menu(_menubar, tearoff=False)
        _MenuVerb.add_command(label=STR_TABLE['delete'][self._lang], command=self._reset_conn_history)
        _menubar.add_cascade(label='History', menu=_MenuVerb, underline=0)

    def set_port_index(self, index: int):
        self._port_index = index
        port = PORT_HANDLER.get_port_by_index(index)
        if port:
            if port.port_typ == 'AXIP':
                self.ax_ip_ip = \
                    (
                        tk.Label(self,
                                 text='IP:',
                                 foreground='black',
                                 font=("TkFixedFont", 12),
                                 height=1,
                                 width=5),
                        tk.Text(self,
                                background='grey80',
                                foreground='black',
                                font=("TkFixedFont", 12),
                                height=1,
                                width=15),
                    )
                self.ax_ip_ip[0].place(x=2, y=80)
                self.ax_ip_ip[1].place(x=80, y=80)
                self.ax_ip_port = \
                    (
                        tk.Label(self,
                                 text='Port:',
                                 foreground='black',
                                 font=("TkFixedFont", 12),
                                 height=1,
                                 width=5),
                        tk.Text(self,
                                background='grey80',
                                foreground='black',
                                font=("TkFixedFont", 12),
                                height=1,
                                width=6)
                    )
                self.ax_ip_port[0].place(x=300, y=80)
                self.ax_ip_port[1].place(x=380, y=80)
                call_str = self.call_txt_inp_var.get()

                # axip_fm_db = USER_DB.get_AXIP(str(call_obj.call_str))
                mh_ent = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(call_str, port.port_cfg.parm_axip_fail)
                # Just if u switch after enter in call
                if mh_ent[1]:
                    ip = mh_ent[0]
                    prt = str(mh_ent[1])
                    self.ax_ip_ip[1].delete('1.0', tk.END)
                    self.ax_ip_ip[1].insert(tk.END, ip)
                    self.ax_ip_port[1].delete('1.0', tk.END)
                    self.ax_ip_port[1].insert(tk.END, prt)
                self._call_txt_inp.focus_set()
                self.own_call_dd_men.destroy()
                opt = PORT_HANDLER.get_all_ports()[self._port_index].my_stations
                self.own_call_dd_men = tk.OptionMenu(self, self.own_call_var, *opt)
                self.own_call_dd_men.place(x=80, y=120)
                self.own_call_dd_men.configure()
                if opt:
                    self.own_call_var.set(opt[0])

            else:
                if self.ax_ip_ip is not None:
                    self.ax_ip_ip[0].destroy()
                    self.ax_ip_ip[1].destroy()
                    self.ax_ip_port[0].destroy()
                    self.ax_ip_port[1].destroy()
                self.own_call_dd_men.destroy()
                opt = PORT_HANDLER.get_all_ports()[self._port_index].my_stations
                self.own_call_dd_men = tk.OptionMenu(self, self.own_call_var, *opt)
                self.own_call_dd_men.place(x=80, y=80)
                self.own_call_dd_men.configure()
                if opt:
                    self.own_call_var.set(opt[0])
            self._set_port_btn()

    def _set_port_btn(self):
        # self._chiefs = PORT_HANDLER.get_MH().get_unsort_entrys_fm_port(self._port_index)
        for k in self._port_btn.keys():
            btn = self._port_btn[k]
            if k == self._port_index:
                btn.configure(bg='green')
            else:
                btn.configure(bg='red')

    def _process_new_conn_win(self):
        axip_address = ('', 0)
        addrs_str = self.call_txt_inp_var.get()
        ch_id = self._main.get_free_channel(self._main.channel_index)
        if addrs_str:
            own_call = self.own_call_var.get()
            call_list = get_list_fm_viaStr(addrs_str)
            if not call_list:
                self._main.sysMsg_to_qso('*** Error. No valid Address.', ch_id)
                return
            dest_call = call_list[0]
            via_calls = call_list[1:]
            port = PORT_HANDLER.get_port_by_index(self._port_index)
            if port:
                if port.port_typ == 'AXIP':
                    mh_ent = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(dest_call, port.port_cfg.parm_axip_fail)
                    # Just if u switch after enter in call
                    axip_ip_inp = self.ax_ip_ip[1].get('0.0', tk.END)[:-1]
                    axip_port = self.ax_ip_port[1].get('0.0', tk.END)[:-1]
                    axip_ip = get_ip_by_hostname(axip_ip_inp)
                    if not axip_ip:
                        if mh_ent[1]:
                            ip = mh_ent[0]
                            prt = str(mh_ent[1])
                            self.ax_ip_ip[1].delete('1.0', tk.END)
                            self.ax_ip_ip[1].insert(tk.END, ip)
                            self.ax_ip_port[1].delete('1.0', tk.END)
                            self.ax_ip_port[1].insert(tk.END, prt)
                            axip_port = prt
                            axip_ip = ip
                            axip_ip = get_ip_by_hostname(axip_ip)
                    else:
                        USER_DB.set_AXIP(str(dest_call), (axip_ip_inp, axip_port))

                    if axip_port.isdigit() and check_ip_add_format(axip_ip):
                        axip_address = axip_ip, int(axip_port)
                    else:
                        self._main.sysMsg_to_qso('*** Error. No valid AXIP-Address.', ch_id)
                        return

                # conn = PORT_HANDLER.get_all_ports()[self.port_index].new_connection(ax25_frame=ax_frame)
                is_connected, msg, conn = PORT_HANDLER.new_outgoing_connection(
                    dest_call=dest_call,
                    own_call=own_call,
                    via_calls=via_calls,  # Auto lookup in MH if not exclusive Mode
                    port_id=self._port_index,  # -1 Auto lookup in MH list
                    axip_add=axip_address,  # AXIP Adress
                    exclusive=True,  # True = no lookup in MH list
                    link_conn=None,  # Linked Connection AX25Conn
                    channel=int(ch_id)  # Channel/Connection Index = Channel-ID
                )
                msg = str(msg).replace('\r', '')
                self._main.sysMsg_to_qso(msg,ch_id)

                if is_connected:
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
        ent_key = self.call_txt_inp_var.get()
        port_id = self._conn_hist.get(ent_key, {}).get('port_id', None)
        own_call = self._conn_hist.get(ent_key, {}).get('own_call', '')
        if port_id is not None:
            self.set_port_index(port_id)
        if own_call:
            self.own_call_var.set(own_call)

    def _reset_conn_history(self, event=None):
        self._conn_hist = {}
        self._main.connect_history = {}
        vals = list(self._conn_hist.keys())
        vals.reverse()
        self._call_txt_inp.config(values=vals)

    def _destroy_new_conn_win(self):
        self.destroy()
        self._main.new_conn_win = None
