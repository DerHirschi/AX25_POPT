import tkinter as tk
import math

from ax25.ax25InitPorts import PORT_HANDLER


class RxEchoSettings(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self._main_cl = main_win
        main_win.settings_win = self
        ###############
        # VARS
        # self.port_handler = main_win.ax25_port_handler
        n_ports = len(PORT_HANDLER.get_all_ports().keys())
        self.win_height = 650
        self.win_width = 280 * max(math.ceil(n_ports / 2), 2)
        self.style = main_win.style
        self.title("RX-Echo Einstellungen")
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._main_cl.main_win.winfo_x()}+"
                      f"{self._main_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.off_color = ''
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text="Ok",
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self._ok_btn_cmd)

        save_bt = tk.Button(self,
                            text="Speichern",
                            # font=("TkFixedFont", 15),
                            # bg="green",
                            height=1,
                            width=7,
                            command=self._save_btn_cmd)

        cancel_bt = tk.Button(self,
                              text="Abbrechen",
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self._destroy_win)

        ok_bt.place(x=20, y=self.win_height - 50)
        save_bt.place(x=110, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        ############################
        # Ports
        self.check_vars: {int: {int: [tk.BooleanVar, tk.BooleanVar, tk.Checkbutton, tk.Checkbutton, tk.Entry, tk.Entry]}} = {}
        _label = tk.Label(self, text="Achtung! Diese Funktion ersetzt kein Digipeater!")
        _label.place(x=30, y=10)
        _x = 30
        for i in range(len(list(PORT_HANDLER.get_all_ports().keys()))):
            k = list(PORT_HANDLER.get_all_ports().keys())[i]
            port = PORT_HANDLER.get_all_ports()[k]
            var_dict = {}
            text = 'Port {}: {}'.format(port.port_id, port.port_cfg.parm_PortName)
            # Left
            _y = 60 + (280 * int(i % 2))
            if not i % 2 and i:
                _x += 250
                _yy = _y + 20
            _label = tk.Label(self, text=text)
            _label.place(x=_x, y=_y)

            _yy = _y + 20
            for kk in list(PORT_HANDLER.get_all_ports().keys()):
                if kk != k:
                    # tmp_port: AX25Port = PORT_HANDLER.get_all_ports()[kk]
                    _rx_text = 'Port {} RX'.format(kk)
                    rx_check_var = tk.BooleanVar(self)
                    rx_check = tk.Checkbutton(self,
                                               text=_rx_text,
                                               variable=rx_check_var)
                    #rx_check.var = rx_check_var
                    rx_call_ent = tk.Entry(self, width=9)
                    rx_check.place(x=_x + 5, y=_yy)
                    rx_call_ent.place(x=_x + 125, y=_yy)

                    _tx_text = 'Port {} TX'.format(kk)
                    tx_check_var = tk.BooleanVar(self)
                    tx_check = tk.Checkbutton(self,
                                               text=_tx_text,
                                               variable=tx_check_var)
                    #tx_check.var = tx_check_var
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
                    rx_check.configure(command=self._check_cmd)
                    tx_check.configure(command=self._check_cmd)

            self.check_vars[k] = var_dict
        self._update_settings()
        #print(self.check_vars)

    def _save_btn_cmd(self):
        # self.set_vars()
        # PORT_HANDLER.save_all_port_cfgs()
        # self._main_cl.sysMsg_to_monitor('Info: RX-Echo Settings wurden gespeichert..')
        self._main_cl.sysMsg_to_monitor('Lob: Eine sehr gute Entscheidung. Du bist großartig!')

    def _ok_btn_cmd(self):
        # self.set_vars()
        # self.re_init_beacons()
        self._main_cl.sysMsg_to_monitor('Info: RX-Echo Settings wurden gespeichert..')
        self._main_cl.sysMsg_to_monitor('Lob: Du hast eine gute Einstellung. Mach weiter so!')
        self._destroy_win()

    def _destroy_win(self):
        self.destroy()
        self._main_cl.settings_win = None

    def tasker(self):
        pass

    def _check_cmd(self):
        """
        _rx_check_var,
        _tx_check_var,
        _rx_check,
        _tx_check,
        _rx_call_ent,
        _tx_call_ent
        """
        for k in PORT_HANDLER.rx_echo.keys():
            if k in self.check_vars.keys():
                for kk in list(self.check_vars[k].keys()):
                    # RX
                    if self.check_vars[k][kk][0].get() and self.check_vars[kk][k][1].get():
                        self.check_vars[k][kk][2].configure(background='green1', activebackground='green4')
                        self.check_vars[kk][k][3].configure(background='green1', activebackground='green4')
                        # self.check_vars[k][kk][2].select()
                        # self.check_vars[kk][k][2].select()
                        var = self.check_vars[k][kk][4].get()
                        calls = []
                        if not var:
                            var = self.check_vars[kk][k][5].get()
                            if var:
                                calls = var.split(' ')
                        else:
                            calls = var.split(' ')

                        PORT_HANDLER.rx_echo[k].rx_ports[kk] = list(calls)
                        PORT_HANDLER.rx_echo[kk].tx_ports[k] = list(calls)

                        self.check_vars[kk][k][5].delete(0, tk.END)
                        self.check_vars[kk][k][5].insert(tk.END, var)
                        self.check_vars[k][kk][4].delete(0, tk.END)
                        self.check_vars[k][kk][4].insert(tk.END, var)
                    else:
                        self.check_vars[k][kk][2].configure(background=self.off_color[0], activebackground=self.off_color[1])
                        self.check_vars[kk][k][3].configure(background=self.off_color[0], activebackground=self.off_color[1])
                        # self.check_vars[k][kk][2].deselect()
                        # self.check_vars[kk][k][2].deselect()
                        if kk in list(PORT_HANDLER.rx_echo[k].rx_ports.keys()):
                            del PORT_HANDLER.rx_echo[k].rx_ports[kk]
                        if k in list(PORT_HANDLER.rx_echo[kk].tx_ports.keys()):
                            del PORT_HANDLER.rx_echo[kk].tx_ports[k]
                    # TX
                    if self.check_vars[k][kk][1].get() and self.check_vars[kk][k][0].get():
                        self.check_vars[k][kk][3].configure(background='green1', activebackground='green4')
                        self.check_vars[kk][k][2].configure(background='green1', activebackground='green4')
                        # self.check_vars[k][kk][3].select()
                        # self.check_vars[kk][k][3].select()
                        var = self.check_vars[k][kk][5].get()
                        calls = []
                        if not var:
                            var = self.check_vars[kk][k][4].get()
                            if var:
                                calls = var.split(' ')
                        else:
                            calls = var.split(' ')
                        PORT_HANDLER.rx_echo[k].tx_ports[kk] = calls
                        PORT_HANDLER.rx_echo[kk].rx_ports[k] = calls

                        self.check_vars[kk][k][4].delete(0, tk.END)
                        self.check_vars[kk][k][4].insert(tk.END, var)
                        self.check_vars[k][kk][5].delete(0, tk.END)
                        self.check_vars[k][kk][5].insert(tk.END, var)
                    else:
                        self.check_vars[k][kk][3].configure(background=self.off_color[0], activebackground=self.off_color[1])
                        self.check_vars[kk][k][2].configure(background=self.off_color[0], activebackground=self.off_color[1])
                        # self.check_vars[k][kk][3].deselect()
                        # self.check_vars[kk][k][3].deselect()
                        if kk in list(PORT_HANDLER.rx_echo[k].tx_ports.keys()):
                            del PORT_HANDLER.rx_echo[k].tx_ports[kk]
                        if k in list(PORT_HANDLER.rx_echo[kk].rx_ports.keys()):
                            del PORT_HANDLER.rx_echo[kk].rx_ports[k]

        """
        for k in PORT_HANDLER.rx_echo.keys():
            print('Port ' + str(k))
            for att in dir(PORT_HANDLER.rx_echo[k]):
                if '__' not in att:
                    print('{} > {}'.format(att, getattr(PORT_HANDLER.rx_echo[k], att)))
                    #print(PORT_HANDLER.rx_echo[k])
            print()
        """

    def _update_settings(self):

        for k in PORT_HANDLER.rx_echo.keys():
            if k in self.check_vars.keys():
                for kk in list(self.check_vars[k].keys()):
                    tr_k_kk = False
                    tr_kk_k = False
                    # RX
                    if k in PORT_HANDLER.rx_echo[kk].tx_ports.keys():
                        self.check_vars[kk][k][5].delete(0, tk.END)

                        call_list_kk_k = PORT_HANDLER.rx_echo[kk].tx_ports[k]
                        call_st = ''
                        for el in call_list_kk_k:
                            call_st += el + ' '
                        self.check_vars[kk][k][5].insert(tk.END, call_st)
                        self.check_vars[kk][k][1].set(True)
                        tr_kk_k = True
                    else:
                        self.check_vars[kk][k][1].set(False)

                    if kk in PORT_HANDLER.rx_echo[k].rx_ports.keys():
                        self.check_vars[k][kk][4].delete(0, tk.END)

                        call_list_k_kk = PORT_HANDLER.rx_echo[k].rx_ports[kk]
                        call_st = ''
                        for el in call_list_k_kk:
                            call_st += el + ' '
                        self.check_vars[k][kk][4].insert(tk.END, call_st)
                        self.check_vars[k][kk][0].set(True)
                        tr_k_kk = True
                    else:
                        self.check_vars[k][kk][0].set(False)

                    if tr_kk_k and tr_k_kk:
                        self.check_vars[k][kk][2].configure(background='green1', activebackground='green4')
                        self.check_vars[kk][k][3].configure(background='green1', activebackground='green4')
                    else:
                        self.check_vars[k][kk][2].configure(background=self.off_color[0],
                                                            activebackground=self.off_color[1])
                        self.check_vars[kk][k][3].configure(background=self.off_color[0],
                                                            activebackground=self.off_color[1])

