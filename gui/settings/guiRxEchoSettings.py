import tkinter as tk
import math

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG


class RxEchoSettings(tk.Frame):
    def __init__(self, tabctl, root_win=None):
        tk.Frame.__init__(self, tabctl)
        ###############
        # VARS
        n_ports = len(PORT_HANDLER.get_all_ports().keys())
        self.win_height = 650
        self.win_width = 280 * max(math.ceil(n_ports / 2), 2)

        self.off_color = ''
        ##########################
        ############################
        # Ports
        self.check_vars: {int: {int: [tk.BooleanVar, tk.BooleanVar, tk.Checkbutton, tk.Checkbutton, tk.Entry, tk.Entry]}} = {}
        label = tk.Label(self, text="Achtung! Diese Funktion ersetzt kein Digipeater!")
        label.place(x=30, y=10)
        x = 30
        for i in range(len(list(PORT_HANDLER.get_all_ports().keys()))):
            k = list(PORT_HANDLER.get_all_ports().keys())[i]
            port = PORT_HANDLER.get_all_ports()[k]
            var_dict = {}
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port.port_id)
            text = 'Port {}: {}'.format(port.port_id, port_cfg.get('parm_PortName', ''))
            # Left
            y = 60 + (280 * int(i % 2))
            if not i % 2 and i:
                x += 250
            label = tk.Label(self, text=text)
            label.place(x=x, y=y)

            yy = y + 20
            for kk in list(PORT_HANDLER.get_all_ports().keys()):
                if kk != k:
                    # tmp_port: AX25Port = PORT_HANDLER.get_all_ports()[kk]
                    rx_text = 'Port {} RX'.format(kk)
                    rx_check_var = tk.BooleanVar(self)
                    rx_check = tk.Checkbutton(self,
                                               text=rx_text,
                                               variable=rx_check_var)
                    #rx_check.var = rx_check_var
                    rx_call_ent = tk.Entry(self, width=9)
                    rx_check.place(x=x + 5, y=yy)
                    rx_call_ent.place(x=x + 125, y=yy)

                    tx_text = 'Port {} TX'.format(kk)
                    tx_check_var = tk.BooleanVar(self)
                    tx_check = tk.Checkbutton(self,
                                               text=tx_text,
                                               variable=tx_check_var)
                    #tx_check.var = tx_check_var
                    tx_call_ent = tk.Entry(self, width=9)
                    tx_check.place(x=x + 5, y=yy + 20)
                    tx_call_ent.place(x=x + 125, y=yy + 20)

                    yy += 40
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

    """
    def _save_btn_cmd(self):
        # self.set_vars()
        # PORT_HANDLER.save_all_port_cfgs()
        # self._main_cl.sysMsg_to_monitor('Info: RX-Echo Settings wurden gespeichert..')
        # self._main_cl.sysMsg_to_monitor('Lob: Eine sehr gute Entscheidung. Du bist großartig!')
        pass

    def _ok_btn_cmd(self):
        # self.set_vars()
        # self.re_init_beacons()
        # self._main_cl.sysMsg_to_monitor('Info: RX-Echo Settings wurden gespeichert..')
        # self._main_cl.sysMsg_to_monitor('Lob: Du hast eine gute Einstellung. Mach weiter so!')
        self._destroy_win()

    def _destroy_win(self):
        self.destroy()
        # self._main_cl.settings_win = None
    """


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
                    try:
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
                    except KeyError:
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

    @staticmethod
    def get_config():
        return None

    @staticmethod
    def save_config():
        return False