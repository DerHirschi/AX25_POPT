import tkinter as tk

import ax25.ax25dec_enc
from config_station import get_stat_cfg
# from main import AX25PortHandler, AX25Frame, Call, AX25Port
import main


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


class NewConnWin:
    def __init__(self, main_win):
        self.main = main_win
        self.style = self.main.style
        self.ax25_port_handler = self.main.ax25_port_handler
        self.out_txt = self.main.out_txt
        self.mh = main_win.mh
        self.new_conn_win = tk.Tk()
        self.new_conn_win.title("New Connection")
        self.new_conn_win.geometry("700x285")
        self.new_conn_win.protocol("WM_DELETE_WINDOW", self.destroy_new_conn_win)
        self.new_conn_win.resizable(False, False)
        self.new_conn_win.attributes("-topmost", True)
        self.new_conn_win.columnconfigure(0, minsize=20, weight=1)
        self.new_conn_win.columnconfigure(1, minsize=100, weight=1)
        self.new_conn_win.columnconfigure(2, minsize=50, weight=5)
        self.new_conn_win.columnconfigure(3, minsize=120, weight=1)
        self.new_conn_win.columnconfigure(4, minsize=20, weight=1)
        self.new_conn_win.rowconfigure(0, minsize=38, weight=3)
        self.new_conn_win.rowconfigure(1, minsize=5, weight=5)
        self.new_conn_win.rowconfigure(2, minsize=35, weight=3)
        self.new_conn_win.rowconfigure(3, minsize=5, weight=1)
        self.new_conn_win.rowconfigure(4, minsize=40, weight=3)
        self.new_conn_win.rowconfigure(5, minsize=40, weight=1)
        self.port_index = 0
        self.port_btn: {int: tk.Button} = {}
        for port in self.ax25_port_handler.ax25_ports.keys():
            tmp = tk.Button(self.new_conn_win,
                            text=self.ax25_port_handler.ax25_ports[port].portname,
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
        """
        for k in self.port_btn.keys():
            self.port_btn[k].configure(command=lambda: self.set_port_index(int(k)))
        """

        self.set_port_btn()

        call_label = tk.Label(self.new_conn_win,
                              text='Ziel:',
                              foreground='black',
                              font=("TkFixedFont", 12),
                              height=1,
                              width=5)
        call_label.place(x=2, y=40)
        self.call_txt_inp = tk.Text(self.new_conn_win, background='grey80', foreground='black',
                                    font=("TkFixedFont", 12),
                                    height=1,
                                    width=45)
        self.call_txt_inp.place(x=80, y=40)
        self.ax_ip_ip = None
        self.ax_ip_port = None
        ############
        # Own Call
        self.own_call_var = tk.StringVar(self.new_conn_win)
        # self.own_call_opt = {}
        # self.own_call_opt = get_stat_cfg()
        opt = self.ax25_port_handler.ax25_ports[self.port_index].my_stations
        if opt:
            self.own_call_var.set(opt[0])
        self.own_call_dd_men = tk.OptionMenu(self.new_conn_win, self.own_call_var, *opt)
        ############
        # BTN
        conn_btn = tk.Button(self.new_conn_win,
                             text="Los",
                             font=("TkFixedFont", 15),
                             bg="green",
                             height=1,
                             width=4,
                             command=self.process_new_conn_win)
        conn_btn.place(x=10, y=220)
        self.call_txt_inp.focus_set()
        self.set_port_index(self.port_index)
        ##############
        # KEY BINDS
        self.new_conn_win.bind('<Return>', lambda event: self.process_new_conn_win())
        self.new_conn_win.bind('<KP_Enter>', lambda event: self.process_new_conn_win())
        self.new_conn_win.bind('<Escape>', lambda event: self.destroy_new_conn_win())

    def set_port_index(self, index: int):
        self.port_index = index
        port = self.ax25_port_handler.get_port_by_index(index)
        if port.port_typ == 'AXIP':
            self.ax_ip_ip = \
                (
                    tk.Label(self.new_conn_win,
                             text='IP:',
                             foreground='black',
                             font=("TkFixedFont", 12),
                             height=1,
                             width=5),
                    tk.Text(self.new_conn_win,
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
                    tk.Label(self.new_conn_win,
                             text='Port:',
                             foreground='black',
                             font=("TkFixedFont", 12),
                             height=1,
                             width=5),
                    tk.Text(self.new_conn_win,
                            background='grey80',
                            foreground='black',
                            font=("TkFixedFont", 12),
                            height=1,
                            width=6)
                )
            self.ax_ip_port[0].place(x=300, y=80)
            self.ax_ip_port[1].place(x=380, y=80)
            call_str = self.call_txt_inp.get('0.0', tk.END)
            call_obj = ProcCallInput(call_str)

            mh_ent = self.mh.mh_get_last_ip(call_obj.call_str)
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
            opt = self.ax25_port_handler.ax25_ports[self.port_index].my_stations
            self.own_call_dd_men = tk.OptionMenu(self.new_conn_win, self.own_call_var, *opt)
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
            opt = self.ax25_port_handler.ax25_ports[self.port_index].my_stations
            self.own_call_dd_men = tk.OptionMenu(self.new_conn_win, self.own_call_var, *opt)
            self.own_call_dd_men.place(x=80, y=80)
            self.own_call_dd_men.configure()
            if opt:
                self.own_call_var.set(opt[0])

        self.set_port_btn()

    def set_port_btn(self):
        for k in self.port_btn.keys():
            btn = self.port_btn[k]
            if k == self.port_index:
                btn.configure(bg='green')
            else:
                btn.configure(bg='red')

    def process_new_conn_win(self):
        txt_win = self.call_txt_inp
        call = txt_win.get('0.0', tk.END)

        call_obj = ProcCallInput(call)
        if call_obj.call:
            ax_frame = ax25.ax25dec_enc.AX25Frame()
            # ax_frame.from_call.call = self.ax25_port_handler.ax25_ports[self.port_index].my_stations[0]  # TODO select outgoing call
            ax_frame.from_call.call = self.own_call_var.get()
            ax_frame.to_call.call = call_obj.call
            ax_frame.to_call.ssid = call_obj.ssid
            ax_frame.via_calls = call_obj.via
            if self.ax25_port_handler.ax25_ports[self.port_index].port_typ == 'AXIP':
                mh_ent = self.mh.mh_get_last_ip(call_obj.call_str)
                # Just if u switch after enter in call
                axip_ip = self.ax_ip_ip[1].get('0.0', tk.END)[:-1]
                axip_port = self.ax_ip_port[1].get('0.0', tk.END)[:-1]
                check_ip = axip_ip.split('.')
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
                        check_ip = axip_ip.split('.')
                else:
                    check_ip = axip_ip.split('.')
                tr = True
                for el in check_ip:
                    if not el.isdigit():
                        tr = False
                if len(check_ip) == 4 and axip_port.isdigit() and tr:
                    ax_frame.axip_add = axip_ip, int(axip_port)
                    # print('CHECK')

            # TODO Error or Not Processing if no IP
            ax_frame.ctl_byte.SABMcByte()
            conn = self.ax25_port_handler.ax25_ports[self.port_index].new_connection(ax25_frame=ax_frame)
            if conn:
                # conn: AX25Conn
                self.ax25_port_handler.insert_conn2all_conn_var(new_conn=conn, ind=self.main.channel_index)
            else:
                self.out_txt.insert(tk.END, '\n*** Busy. No free SSID available.\n\n')
            self.destroy_new_conn_win()
            self.main.ch_btn_status_update()
            self.main.change_conn_btn()

    def destroy_new_conn_win(self):
        self.new_conn_win.destroy()
        self.main.new_conn_win = None
