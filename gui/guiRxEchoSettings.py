import tkinter as tk
import math
from ax25.ax25Port import AX25Port


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
            _var_dict = {}
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
                    tmp_port: AX25Port = self.ports[kk]
                    _rx_text = 'Port {} RX'.format(tmp_port.port_id)
                    _rx_check_var = tk.BooleanVar(self)
                    _rx_check = tk.Checkbutton(self,
                                               text=_rx_text,
                                               variable=_rx_check_var)
                    _rx_check.var = _rx_check_var
                    _rx_call_ent = tk.Entry(self, width=9)
                    _rx_check.place(x=_x + 5, y=_yy)
                    _rx_call_ent.place(x=_x + 125, y=_yy)

                    _tx_text = 'Port {} TX'.format(tmp_port.port_id)
                    _tx_check_var = tk.BooleanVar(self)
                    _tx_check = tk.Checkbutton(self,
                                               text=_tx_text,
                                               variable=_tx_check_var)
                    _tx_check.var = _tx_check_var
                    _tx_call_ent = tk.Entry(self, width=9)
                    _tx_check.place(x=_x + 5, y=_yy + 20)
                    _tx_call_ent.place(x=_x + 125, y=_yy + 20)

                    _yy += 40
                    _var_dict[int(kk)] = [_rx_check_var,
                                          _tx_check_var,
                                          _rx_check,
                                          _tx_check,
                                          _rx_call_ent,
                                          _tx_call_ent]
                    self.off_color = _tx_check.cget('background'), _tx_check.cget('activebackground')
                    _rx_check.configure(command=self.check_cmd)
                    _tx_check.configure(command=self.check_cmd)

            self.check_vars[int(k)] = _var_dict

        print(self.check_vars)

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
        self.check_vars: {int: {int: [tk.BooleanVar, tk.BooleanVar]}}
        for k in self.check_vars.keys():
            port = self.check_vars[k]
            for kk in port.keys():
                var_list = port[kk]
                if var_list[0].get():
                    var_list[2].configure(background='green1', activebackground='green4')
                else:
                    var_list[2].configure(background=self.off_color[0], activebackground=self.off_color[1])

                if var_list[1].get():
                    var_list[3].configure(background='green1', activebackground='green4')
                else:
                    var_list[3].configure(background=self.off_color[0], activebackground=self.off_color[1])
