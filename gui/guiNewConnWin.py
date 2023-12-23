# TODO AGAIN
import tkinter as tk
from tkinter import ttk
import ax25.ax25dec_enc
from UserDB.UserDBmain import USER_DB
from ax25.ax25InitPorts import PORT_HANDLER
# from ax25.ax25Statistics import MH_LIST
from fnc.socket_fnc import get_ip_by_hostname, check_ip_add_format


class ProcCallInput:
    def __init__(self, call_inp: str):
        self.ssid = 0
        self.call = ''
        self.call_str = ''
        self.via: [ax25.ax25dec_enc.Call] = []
        call_inp = call_inp.split('\r')[0]
        call_inp = call_inp.split('\n')[0]
        call = call_inp.split(' ')
        via = ''
        if len(call) > 1:
            via = call[1:]
        call = call[0]
        call = call.replace(' ', '')
        call = call.split('-')
        if 6 >= len(call[0]) > 1:
            self.call = call[0].upper()
            self.call_str = call[0].upper()
            if len(call) > 1:
                if call[1].isdigit():
                    if int(call[1]) > 0 or int(call[1]) < 16:
                        self.call_str += ('-' + call[1])
                        self.ssid = int(call[1])
        for c in via:
            new_c = ax25.ax25dec_enc.Call()
            new_c.call_str = c.upper()
            self.via.append(new_c)


class ConnHistory(object):
    # TODO WTF .. change to DICT
    def __init__(self,
                 own_call: str,
                 dest_call: str,
                 add_str: str,
                 port_id: int,
                 ):
        self.own_call = str(own_call)
        self.dest_call = str(dest_call)
        self.address_str = str(add_str)
        self.port_id = int(port_id)


class NewConnWin(tk.Toplevel):
    # TODO Again . . .
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self._main = main_win
        self.style = self._main.style
        self._conn_hist: {str: ConnHistory} = self._main.connect_history
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
        self.port_index = 0
        self.port_btn: {int: tk.Button} = {}
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
            self.port_btn[port] = tmp

        self._set_port_btn()

        call_label = tk.Label(self,
                              text='Ziel:',
                              foreground='black',
                              font=("TkFixedFont", 11),
                              height=1,
                              width=5)
        call_label.place(x=2, y=40)
        """
        self.call_txt_inp = tk.Text(self, background='grey80', foreground='black',
                                    font=("TkFixedFont", 12),
                                    height=1,
                                    width=45)
        """
        vals = list(self._conn_hist.keys())
        vals.reverse()
        self.call_txt_inp = tk.ttk.Combobox(self,
                                            font=("TkFixedFont", 11),
                                            # height=1,
                                            values=vals,
                                            width=45
                                            )
        self.call_txt_inp.bind("<<ComboboxSelected>>", self._set_conn_hist)
        self.call_txt_inp.place(x=80, y=40)
        self.ax_ip_ip = None
        self.ax_ip_port = None
        ############
        # Own Call
        self.own_call_var = tk.StringVar(self)
        opt = ['NOCALL']
        if self.port_index in PORT_HANDLER.get_all_ports().keys():
            opt = PORT_HANDLER.get_all_ports()[self.port_index].my_stations
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
        self.call_txt_inp.focus_set()
        self.set_port_index(self.port_index)
        ##############
        # KEY BINDS
        self.bind('<Return>', lambda event: self._process_new_conn_win())
        self.bind('<KP_Enter>', lambda event: self._process_new_conn_win())
        self.bind('<Escape>', lambda event: self._destroy_new_conn_win())

        self._main.new_conn_win = self

    def set_port_index(self, index: int):
        self.port_index = index
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
                call_str = self.call_txt_inp.get()
                call_obj = ProcCallInput(call_str)

                # axip_fm_db = USER_DB.get_AXIP(str(call_obj.call_str))
                mh_ent = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(call_obj.call_str, port.port_cfg.parm_axip_fail)
                # Just if u switch after enter in call
                if mh_ent[1]:
                    ip = mh_ent[0]
                    prt = str(mh_ent[1])
                    self.ax_ip_ip[1].delete('1.0', tk.END)
                    self.ax_ip_ip[1].insert(tk.END, ip)
                    self.ax_ip_port[1].delete('1.0', tk.END)
                    self.ax_ip_port[1].insert(tk.END, prt)
                self.call_txt_inp.focus_set()
                self.own_call_dd_men.destroy()
                opt = PORT_HANDLER.get_all_ports()[self.port_index].my_stations
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
                opt = PORT_HANDLER.get_all_ports()[self.port_index].my_stations
                self.own_call_dd_men = tk.OptionMenu(self, self.own_call_var, *opt)
                self.own_call_dd_men.place(x=80, y=80)
                self.own_call_dd_men.configure()
                if opt:
                    self.own_call_var.set(opt[0])

            self._set_port_btn()

    def _set_port_btn(self):
        for k in self.port_btn.keys():
            btn = self.port_btn[k]
            if k == self.port_index:
                btn.configure(bg='green')
            else:
                btn.configure(bg='red')

    def _process_new_conn_win(self):
        txt_win = self.call_txt_inp
        # call = txt_win.get('0.0', tk.END)
        call = txt_win.get()

        call_obj = ProcCallInput(call)
        if call_obj.call:

            ax_frame = ax25.ax25dec_enc.AX25Frame()
            ax_frame.from_call.call_str = self.own_call_var.get()
            ax_frame.to_call.call = call_obj.call
            ax_frame.to_call.ssid = call_obj.ssid
            ax_frame.via_calls = call_obj.via
            port = PORT_HANDLER.get_port_by_index(self.port_index)
            if port:
                if port.port_typ == 'AXIP':
                    mh_ent = PORT_HANDLER.get_MH().get_AXIP_fm_DB_MH(call_obj.call_str, port.port_cfg.parm_axip_fail)
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
                        USER_DB.set_AXIP(str(call_obj.call_str), (axip_ip_inp, axip_port))
                    """
                    check_ip = check_ip.split('.')
                    tr = True
                    for el in check_ip:
                        if not el.isdigit():
                            tr = False
                    """
                    if axip_port.isdigit() and check_ip_add_format(axip_ip):
                        ax_frame.axip_add = axip_ip, int(axip_port)
                        # PORT_HANDLER.get_MH().mh_inp_axip_add(call_obj.call_str, (axip_ip_inp, axip_port))
                        # print('CHECK')

                # TODO Error or Not Processing if no IP
                # ax_frame.ctl_byte.SABMcByte()
                conn = PORT_HANDLER.get_all_ports()[self.port_index].new_connection(ax25_frame=ax_frame)
                if conn:
                    # conn: AX25Conn
                    PORT_HANDLER.insert_conn2all_conn_var(new_conn=conn, ind=self._main.channel_index)
                else:
                    self._main.send_to_qso('\n*** Busy. No free SSID available.\n\n', self.port_index)
                if call.upper() in self._conn_hist.keys():
                    del self._conn_hist[call.upper()]
                self._conn_hist[call.upper()] = ConnHistory(
                    own_call=ax_frame.from_call.call,
                    dest_call=call_obj.call_str,
                    add_str=call,
                    port_id=self.port_index,
                )
                self._main.ch_status_update()
                self._main.change_conn_btn()
                self._destroy_new_conn_win()

    def _set_conn_hist(self, event):
        # call = txt_win.get('0.0', tk.END)
        ent_key = self.call_txt_inp.get()
        if ent_key in self._conn_hist:
            ent: ConnHistory = self._conn_hist[ent_key]
            self.set_port_index(ent.port_id)

    def insert_conn_hist(self):
        pass

    def _destroy_new_conn_win(self):
        self.destroy()
        self._main.new_conn_win = None
