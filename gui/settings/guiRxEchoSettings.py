import tkinter as tk
from tkinter import ttk
import math
from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import COLOR_MAP
from cfg.popt_config import POPT_CFG


class RxEchoSettings(ttk.Frame):
    def __init__(self, tabctl, root_win=None):
        ttk.Frame.__init__(self, tabctl)
        # VARS
        n_ports = len(PORT_HANDLER.get_all_ports().keys())
        self.win_height = 650
        self.win_width = 280 * max(math.ceil(n_ports / 2), 2)
        self._get_colorMap = lambda: COLOR_MAP.get(root_win.style_name, ('black', '#d9d9d9'))
        self.off_color = ''
        # Ports
        self.check_vars: {int: {int: [tk.BooleanVar, tk.BooleanVar, ttk.Checkbutton, ttk.Checkbutton, ttk.Label, ttk.Label, tk.StringVar, tk.StringVar]}} = {}
        label = ttk.Label(self, text="Achtung! Diese Funktion ersetzt kein Digipeater!")
        label.place(x=30, y=10)
        x = 30
        fg, bg = self._get_colorMap()

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
            label = ttk.Label(self, text=text)
            label.place(x=x, y=y)

            yy = y + 20
            for kk in list(PORT_HANDLER.get_all_ports().keys()):
                if kk != k:
                    # RX
                    rx_text = 'Port {} RX'.format(kk)
                    rx_check_var = tk.BooleanVar(self)
                    rx_check = ttk.Checkbutton(
                        self,
                        variable=rx_check_var,
                        #style="TCheckbutton"
                    )
                    rx_label = ttk.Label(self, text=rx_text, foreground=fg, background=bg)
                    rx_call_var = tk.StringVar(self)
                    rx_call_ent = ttk.Entry(self, width=9, textvariable=rx_call_var)
                    rx_check.place(x=x + 5, y=yy)
                    rx_label.place(x=x + 25, y=yy)
                    rx_call_ent.place(x=x + 125, y=yy)

                    # TX
                    tx_text = 'Port {} TX'.format(kk)
                    tx_check_var = tk.BooleanVar(self)
                    tx_check = ttk.Checkbutton(
                        self,
                        variable=tx_check_var,
                        #style="TCheckbutton"
                    )
                    tx_label = ttk.Label(self, text=tx_text, foreground=fg, background=bg)
                    tx_call_var = tk.StringVar(self)
                    tx_call_ent = ttk.Entry(self, width=9, textvariable=tx_call_var)
                    tx_check.place(x=x + 5, y=yy + 20)
                    tx_label.place(x=x + 25, y=yy + 20)
                    tx_call_ent.place(x=x + 125, y=yy + 20)

                    yy += 40
                    var_dict[kk] = [
                        rx_check_var,
                        tx_check_var,
                        rx_check,
                        tx_check,
                        rx_label,
                        tx_label,
                        rx_call_var,
                        tx_call_var
                    ]
                    self.off_color = (rx_label.cget('background'), rx_label.cget('background'), fg)
                    rx_check.configure(command=lambda: self._check_cmd(k, kk))
                    tx_check.configure(command=lambda: self._check_cmd(k, kk))

            self.check_vars[k] = var_dict
        self._update_settings()

    def _check_cmd(self, k, kk):
        """Aktualisiert die Label-Farben für Paar-Zustände."""
        for k in PORT_HANDLER.rx_echo.keys():
            if k in self.check_vars.keys():
                for kk in list(self.check_vars[k].keys()):
                    # RX
                    if self.check_vars[k][kk][0].get() and self.check_vars[kk][k][1].get():
                        self.check_vars[k][kk][4].configure(background='green1', foreground='black')
                        self.check_vars[kk][k][5].configure(background='green1', foreground='black')
                        var = self.check_vars[k][kk][6].get()
                        calls = []
                        if not var:
                            var = self.check_vars[kk][k][7].get().upper()
                            if var:
                                calls = var.split(' ')
                        else:
                            calls = var.split(' ')
                        PORT_HANDLER.rx_echo[k].rx_ports[kk] = list(calls)
                        PORT_HANDLER.rx_echo[kk].tx_ports[k] = list(calls)
                        self.check_vars[kk][k][7].set(var)
                        self.check_vars[k][kk][6].set(var)
                    else:
                        self.check_vars[k][kk][4].configure(
                            background=self.off_color[0], foreground=self.off_color[2]
                        )
                        self.check_vars[kk][k][5].configure(
                            background=self.off_color[0], foreground=self.off_color[2]
                        )
                        if kk in list(PORT_HANDLER.rx_echo[k].rx_ports.keys()):
                            del PORT_HANDLER.rx_echo[k].rx_ports[kk]
                        if k in list(PORT_HANDLER.rx_echo[kk].tx_ports.keys()):
                            del PORT_HANDLER.rx_echo[kk].tx_ports[k]

                    # TX
                    if self.check_vars[k][kk][1].get() and self.check_vars[kk][k][0].get():
                        self.check_vars[k][kk][5].configure(background='green1', foreground='black')
                        self.check_vars[kk][k][4].configure(background='green1', foreground='black')
                        var = self.check_vars[k][kk][7].get().upper()
                        calls = []
                        if not var:
                            var = self.check_vars[kk][k][6].get()
                            if var:
                                calls = var.split(' ')
                        else:
                            calls = var.split(' ')
                        PORT_HANDLER.rx_echo[k].tx_ports[kk] = calls
                        PORT_HANDLER.rx_echo[kk].rx_ports[k] = calls
                        self.check_vars[kk][k][6].set(var)
                        self.check_vars[k][kk][7].set(var)
                    else:
                        self.check_vars[k][kk][5].configure(
                            background=self.off_color[0], foreground=self.off_color[2]
                        )
                        self.check_vars[kk][k][4].configure(
                            background=self.off_color[0], foreground=self.off_color[2]
                        )
                        if kk in list(PORT_HANDLER.rx_echo[k].tx_ports.keys()):
                            del PORT_HANDLER.rx_echo[k].tx_ports[kk]
                        if k in list(PORT_HANDLER.rx_echo[kk].rx_ports.keys()):
                            del PORT_HANDLER.rx_echo[kk].rx_ports[k]

    def _update_settings(self):
        for k in PORT_HANDLER.rx_echo.keys():
            if k in self.check_vars.keys():
                for kk in list(self.check_vars[k].keys()):
                    tr_k_kk = False
                    tr_kk_k = False
                    # RX
                    try:
                        if k in PORT_HANDLER.rx_echo[kk].tx_ports.keys():
                            call_list_kk_k = PORT_HANDLER.rx_echo[kk].tx_ports[k]
                            call_st = ' '.join(call_list_kk_k)
                            self.check_vars[kk][k][7].set(call_st)
                            self.check_vars[kk][k][1].set(True)
                            tr_kk_k = True
                        else:
                            self.check_vars[kk][k][1].set(False)
                            self.check_vars[kk][k][7].set('')
                    except KeyError:
                        self.check_vars[kk][k][1].set(False)
                        self.check_vars[kk][k][7].set('')

                    if kk in PORT_HANDLER.rx_echo[k].rx_ports.keys():
                        call_list_k_kk = PORT_HANDLER.rx_echo[k].rx_ports[kk]
                        call_st = ' '.join(call_list_k_kk)
                        self.check_vars[k][kk][6].set(call_st)
                        self.check_vars[k][kk][0].set(True)
                        tr_k_kk = True
                    else:
                        self.check_vars[k][kk][0].set(False)
                        self.check_vars[k][kk][6].set('')

                    if tr_kk_k and tr_k_kk:
                        self.check_vars[k][kk][4].configure(background='green1', foreground='black')
                        self.check_vars[kk][k][5].configure(background='green1', foreground='black')
                    else:
                        self.check_vars[k][kk][4].configure(
                            background=self.off_color[0], foreground=self.off_color[2]
                        )
                        self.check_vars[kk][k][5].configure(
                            background=self.off_color[0], foreground=self.off_color[2]
                        )

    @staticmethod
    def get_config():
        return None

    @staticmethod
    def save_config():
        return False