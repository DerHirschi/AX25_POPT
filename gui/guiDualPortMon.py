import tkinter as tk
from tkinter import ttk, TclError, Menu

from ax25.ax25InitPorts import PORT_HANDLER
from ax25.ax25monitor import monitor_frame_inp
from cfg.constant import FONT
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import tk_filter_bad_chars, get_strTab


class DP_MonitorTab(ttk.Frame):
    def __init__(self, root_win, port):
        ttk.Frame.__init__(self, root_win)
        self.pack(fill=tk.BOTH, expand=True)
        self._text_size = POPT_CFG.get_guiCFG_text_size()
        self._port = port
        self._port_mon_buf = []
        #################################################
        upper_frame = ttk.Frame(self, height=15)
        upper_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        self._autoscroll_var = tk.BooleanVar(self, value=True)
        self._aprs_dec_var = tk.BooleanVar(self, value=False)
        autoscroll_ent = ttk.Checkbutton(upper_frame, text='Autoscroll', variable=self._autoscroll_var)
        autoscroll_ent.pack(side=tk.LEFT)
        aprs_ent = ttk.Checkbutton(upper_frame, text='APRS-Decoding', variable=self._aprs_dec_var)
        aprs_ent.pack(side=tk.LEFT)
        ##################
        # Port
        mon_frame = ttk.Frame(self)
        mon_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        pw_pn = ttk.PanedWindow(mon_frame, orient=tk.HORIZONTAL)
        frame_l = ttk.Frame(pw_pn)
        frame_r = ttk.Frame(pw_pn)
        pw_pn.add(frame_l, weight=1)
        pw_pn.add(frame_r, weight=1)
        pw_pn.pack(fill=tk.BOTH, expand=True)
        self._scroll_l = ttk.Scrollbar(frame_l, command=self.sync_scroll)
        self._primPort_text = tk.Text(frame_l,
                                      font=(FONT, self._text_size),
                                      bd=0,
                                      height=3,
                                      width=10,
                                      borderwidth=0,
                                      background='black',
                                      foreground='white',
                                      state="normal",
                                      highlightthickness=0,
                                      # wrap=tk.NONE,
                                      yscrollcommand=self._scroll_prim
                                      )
        self._primPort_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scroll_l.pack(side=tk.LEFT, fill=tk.Y)

        self._scroll_r = ttk.Scrollbar(frame_r, command=self.sync_scroll)
        self._secPort_text = tk.Text(frame_r,
                                     font=(FONT, self._text_size),
                                     bd=0,
                                     height=3,
                                     width=10,
                                     borderwidth=0,
                                     background='#000068',
                                     foreground='white',
                                     state="normal",
                                     highlightthickness=0,
                                     # wrap = tk.NONE,
                                     yscrollcommand=self._scroll_sec
                                     )
        self._secPort_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scroll_r.pack(side=tk.LEFT, fill=tk.Y)

        self._set_tags()
        self._init_text_fm_buf()
        self._see_end()

    def increase_textsize(self):
        self._text_size += 1
        self._text_size = max(self._text_size, 3)
        self._primPort_text.configure(font=(FONT, self._text_size), )
        self._secPort_text.configure(font=(FONT, self._text_size), )

    def decrease_textsize(self):
        self._text_size -= 1
        self._text_size = max(self._text_size, 3)
        self._primPort_text.configure(font=(FONT, self._text_size), )
        self._secPort_text.configure(font=(FONT, self._text_size), )

    def sync_scroll(self, *args):
        """ https://stackoverflow.com/questions/74635102/tkinter-how-can-i-sync-two-scrollbars-with-two-text-widgets-to-mirrow-each-o """
        self._primPort_text.yview(*args)
        self._secPort_text.yview(*args)
        # self._secPort_text.yview_moveto(self._primPort_text.yview()[0])

    def _scroll_sec(self, *args):
        self._scroll_r.set(*args)
        self._scroll_l.set(*args)
        self._primPort_text.yview_moveto(self._secPort_text.yview()[0])

    def _scroll_prim(self, *args):
        self._scroll_r.set(*args)
        self._scroll_l.set(*args)
        self._secPort_text.yview_moveto(self._primPort_text.yview()[0])

    def _get_mon_buf(self):
        if not self._port.check_dualPort():
            return []
        tmp = list(self._port.dualPort_monitor_buf)
        self._port_mon_buf += tmp
        self._port.dualPort_monitor_buf = self._port.dualPort_monitor_buf[len(tmp):]
        return tmp

    def del_mon_buf(self):
        self._port.dualPort_monitor_buf = []
        self._port_mon_buf = []
        self._primPort_text.configure(state='normal')
        self._primPort_text.delete('1.0', tk.END)
        self._primPort_text.configure(state='disabled')
        self._secPort_text.configure(state='normal')
        self._secPort_text.delete('1.0', tk.END)
        self._secPort_text.configure(state='disabled')

    def _init_text_fm_buf(self):
        if not self._port.check_dualPort():
            return
        mon_buf = self._get_mon_buf()
        prim_port_cfg = POPT_CFG.get_port_CFG_fm_id(self._port.dualPort_primaryPort.port_id)
        # prim_port_cfg = self._port.dualPort_primaryPort.port_cfg
        sec_port_cfg = POPT_CFG.get_port_CFG_fm_id(self._port.dualPort_secondaryPort.port_id)
        # sec_port_cfg = self._port.dualPort_secondaryPort.port_cfg
        scroll = False
        mon_conf = {
            "port_name": '',
            "distance" : False, # TODO
            "aprs_dec" : bool(self._aprs_dec_var.get()),
            "nr_dec"   : False, # TODO
            "hex_out"  : False, # TODO
            "decoding" : 'AUTO',# TODO
        }
        if mon_buf:
            self._primPort_text.configure(state='normal')
            self._secPort_text.configure(state='normal')
        for data in mon_buf:
            prim_frame = data[0].get('ax25frame', None)
            sec_frame = data[1].get('ax25frame', None)
            prim_data = ''
            sec_data = ''
            prim_ind1 = self._primPort_text.index('end-1c')
            sec_ind1 = self._secPort_text.index('end-1c')

            if any((prim_frame, sec_frame)):
                if all((prim_frame, sec_frame)):
                    mon_conf['port_name'] = prim_port_cfg.get('parm_PortName', '')
                    prim_data = monitor_frame_inp(prim_frame, mon_conf)
                    mon_conf['port_name'] = sec_port_cfg.get('parm_PortName', '')
                    sec_data  = monitor_frame_inp(sec_frame, mon_conf)

                elif prim_frame:
                    mon_conf['port_name'] = prim_port_cfg.get('parm_PortName', '')
                    prim_data = monitor_frame_inp(prim_frame, mon_conf)
                    sec_data = ''
                    for line in prim_data.split('\n'):
                        sec_data += ' ' * len(line) + '\n'
                    sec_data = sec_data[:-1]
                else:
                    mon_conf['port_name'] = sec_port_cfg.get('parm_PortName', '')
                    sec_data = monitor_frame_inp(sec_frame, mon_conf)

                    prim_data = ''
                    for line in sec_data.split('\n'):
                        prim_data += ' ' * len(line) + '\n'
                    prim_data = prim_data[:-1]
                scroll = True

            prim_data = tk_filter_bad_chars(prim_data)
            sec_data = tk_filter_bad_chars(sec_data)
            self._primPort_text.insert(tk.END, prim_data)
            self._secPort_text.insert(tk.END, sec_data)
            prim_ind2 = self._primPort_text.index('end-1c')
            sec_ind2 = self._secPort_text.index('end-1c')
            if any((
                    data[0].get('tx', False),
                    data[1].get('tx', False),
            )):
                self._primPort_text.tag_add('TX', prim_ind1, prim_ind2)
                self._secPort_text.tag_add('TX', sec_ind1, sec_ind2)

            if scroll:
                self._see_end()
        if mon_buf:
            self._primPort_text.configure(state='disabled')
            self._secPort_text.configure(state='disabled')

    def _set_tags(self):
        self._primPort_text.tag_config('TX',
                                       foreground='#90fca2',
                                       background='#000000',
                                       selectbackground='#90fca2',
                                       selectforeground='#000000',
                                       )
        self._secPort_text.tag_config('TX',
                                      foreground='#90fca2',
                                      background='#000068',
                                      selectbackground='#90fca2',
                                      selectforeground='#000068',
                                      )

    def _see_end(self):
        if self._autoscroll_var.get():
            self._primPort_text.see("end")
            self._secPort_text.see("end")

    def close_tab(self):
        self._port.dualPort_monitor_buf = self._port_mon_buf + self._port.dualPort_monitor_buf

    def tab_tasker(self):
        self._init_text_fm_buf()


class DualPort_Monitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_win  = root_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.text_size  = root_win.text_size
        self.title('Dual-Port Monitor')
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1250x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        self._root_win.dualPortMon_win = self
        #################################################
        tab_frame = ttk.Frame(self)
        tab_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_prim_ports = ttk.Notebook(
            tab_frame,
            padding=5,
        )
        self._tabControl_prim_ports.pack(side=tk.TOP, fill=tk.BOTH, expand=True, )
        self.tab_list: {int: DP_MonitorTab} = {}

        all_prim_Ports = PORT_HANDLER.get_all_dualPorts_primary()
        i = 0
        for port_id in all_prim_Ports.keys():
            port = all_prim_Ports.get(port_id, None)
            if port:
                tab = DP_MonitorTab(self._tabControl_prim_ports, port, )
                self.tab_list[i] = tab
                port_lable_text = 'Port {}'.format(port.port_id)
                self._tabControl_prim_ports.add(tab, text=port_lable_text)
                i += 1

        self._init_menubar()
        self.bind('<Control-plus>',  lambda event: self._increase_textsize())
        self.bind('<Control-plus>',  lambda event: self._increase_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())
        self.bind('<Control-minus>', lambda event: self._decrease_textsize())

    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=self._getTabStr('delete'), command=self._del_monitor_buf)
        menubar.add_cascade(label='Monitor', menu=MenuVerb, underline=0)

    def _del_monitor_buf(self):
        for k in self.tab_list.keys():
            self.tab_list[k].del_mon_buf()

    def _increase_textsize(self):
        for k in self.tab_list.keys():
            self.tab_list[k].increase_textsize()

    def _decrease_textsize(self):
        for k in self.tab_list.keys():
            self.tab_list[k].decrease_textsize()

    def dB_mon_tasker(self):
        try:
            ind = self._tabControl_prim_ports.index(self._tabControl_prim_ports.select())
        except TclError:
            pass
        else:
            if ind in self.tab_list.keys():
                self.tab_list[ind].tab_tasker()

    def _close(self):
        self._root_win.dualPortMon_win = None
        for k in self.tab_list.keys():
            self.tab_list[k].close_tab()
        self.destroy()
