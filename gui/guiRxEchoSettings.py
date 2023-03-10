import tkinter as tk
import math
from ax25.ax25Port import AX25Port


class RxEchoVars(object):
    rx_ports: {int: [str]} = {}
    tx_ports: {int: [str]} = {}


class RxEchoSettings(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self.main_cl = main_win
        main_win.settings_win = self
        ###############
        # VARS
        self.port_handler = main_win.ax25_port_handler
        self.ports: {int: AX25Port} = self.port_handler.ax25_ports
        n_ports = len(self.ports.keys())
        self.win_height = 650
        self.win_width = 280 * max(math.ceil(n_ports / 2), 2)
        self.style = main_win.style
        self.title("Baken-Einstellungen")
        self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(True, True)
        self.off_color = ''
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text="Ok",
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)

        save_bt = tk.Button(self,
                            text="Speichern",
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self.save_btn_cmd)

        cancel_bt = tk.Button(self,
                              text="Abbrechen",
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self.destroy_win)

        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        ############################
        # Ports
        self.check_vars: {int: {int: [tk.BooleanVar, tk.BooleanVar]}} = {}
        _label = tk.Label(self, text="Achtung! Diese Funktion ersetzt kein Digipeater!")
        _label.place(x=30, y=10)
        _x = 30
        for k in self.ports.keys():
            port: AX25Port = self.ports[k]
            var_dict = {}
            text = 'Port {}: {}'.format(port.port_id, port.port_cfg.parm_PortName)
            # Left
            _y = 60 + (280 * int(k % 2))
            if not k % 2 and k:
                _x += 250
                _yy = _y + 20
            _label = tk.Label(self, text=text)
            _label.place(x=_x, y=_y)

            _yy = _y + 20
            for kk in self.ports.keys():
                if kk != k:
                    # tmp_port: AX25Port = self.ports[kk]
                    _rx_text = 'Port {} RX'.format(kk)
                    rx_check_var = tk.BooleanVar(self)
                    rx_check = tk.Checkbutton(self,
                                               text=_rx_text,
                                               variable=rx_check_var)
                    rx_check.var = rx_check_var
                    rx_call_ent = tk.Entry(self, width=9)
                    rx_check.place(x=_x + 5, y=_yy)
                    rx_call_ent.place(x=_x + 125, y=_yy)

                    _tx_text = 'Port {} TX'.format(kk)
                    tx_check_var = tk.BooleanVar(self)
                    tx_check = tk.Checkbutton(self,
                                               text=_tx_text,
                                               variable=tx_check_var)
                    tx_check.var = tx_check_var
                    tx_call_ent = tk.Entry(self, width=9)
                    tx_check.place(x=_x + 5, y=_yy + 20)
                    tx_call_ent.place(x=_x + 125, y=_yy + 20)

                    _yy += 40
                    var_dict[kk] = [rx_check_var,
                                          tx_check_var,
                                          rx_check,
                                          tx_check,
                                          rx_call_ent,
                                          tx_call_ent]
                    self.off_color = tx_check.cget('background'), tx_check.cget('activebackground')
                    rx_check.configure(command=self.check_cmd)
                    tx_check.configure(command=self.check_cmd)

            self.check_vars[k] = var_dict

        #print(self.check_vars)

    def save_btn_cmd(self):

        # self.set_vars()
        self.main_cl.ax25_port_handler.save_all_port_cfgs()
        self.main_cl.msg_to_monitor('Info: RX-Echo Settings wurden gespeichert..')
        self.main_cl.msg_to_monitor('Lob: Eine sehr gute Entscheidung. Du bist großartig!')

    def ok_btn_cmd(self):
        # self.set_vars()
        # self.re_init_beacons()
        self.main_cl.msg_to_monitor('Info: RX-Echo Settings wurden gespeichert..')
        self.main_cl.msg_to_monitor('Lob: Du hast eine gute Einstellung. Mach weiter so!')
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.main_cl.settings_win = None

    def tasker(self):
        pass

    def check_cmd(self):
        """
        _rx_check_var,
        _tx_check_var,
        _rx_check,
        _tx_check,
        _rx_call_ent,
        _tx_call_ent
        """
        self.check_vars: {int: {int: [tk.BooleanVar, tk.BooleanVar]}}
        for k in self.check_vars.keys():
            port_k = self.check_vars[k]
            print('< '.format(port_k.keys()))
            for kk in port_k.keys():
                var_list = port_k[kk]
                # RX
                if var_list[0].get():
                    var_list[2].configure(background='green1', activebackground='green4')
                    var = var_list[4].get()
                    calls = []
                    if var:
                        calls = var.split(' ')

                    self.port_handler.rx_echo[k].rx_ports[kk] = calls
                else:
                    var_list[2].configure(background=self.off_color[0], activebackground=self.off_color[1])
                    if kk in list(self.port_handler.rx_echo[k].rx_ports.keys()):
                        del self.port_handler.rx_echo[k].rx_ports[kk]
                # TX
                if var_list[1].get():
                    var_list[3].configure(background='green1', activebackground='green4')
                    var = var_list[5].get()
                    calls = []
                    if var:
                        calls = var.split(' ')

                    self.port_handler.rx_echo[k].tx_ports[kk] = calls
                    print(self.port_handler.rx_echo[k].tx_ports)
                    print(self.port_handler)
                else:
                    var_list[3].configure(background=self.off_color[0], activebackground=self.off_color[1])
                    if kk in list(self.port_handler.rx_echo[k].tx_ports.keys()):
                        del self.port_handler.rx_echo[k].tx_ports[kk]
        #print(self.port_handler.rx_echo)
        print('> {}'.format(self.port_handler.rx_echo[0].tx_ports))
        for k in self.port_handler.rx_echo.keys():
            print('Port ' + str(k))
            for att in dir(self.port_handler.rx_echo[k]):
                if '__' not in att:
                    print('{} > {}'.format(att, getattr(self.port_handler.rx_echo[k], att)))
            print()
