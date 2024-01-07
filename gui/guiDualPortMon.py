import tkinter as tk
from tkinter import ttk, scrolledtext

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.constant import FONT


class DP_MonitorTab(tk.Frame):
    def __init__(self, root_win, port):
        tk.Frame.__init__(self, root_win)
        self.pack(fill=tk.BOTH, expand=True)
        self._text_size = 12  # TODO
        ##################
        # Port
        mon_frame = tk.Frame(self)
        mon_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        pw_pn = ttk.PanedWindow(mon_frame, orient=tk.HORIZONTAL)
        frame_l = tk.Frame(pw_pn)
        frame_r = tk.Frame(pw_pn)
        pw_pn.add(frame_l, weight=1)
        pw_pn.add(frame_r, weight=1)
        pw_pn.pack(fill=tk.BOTH, expand=True)
        self._scroll_l = tk.Scrollbar(frame_l, command=self.sync_scroll)
        self._primPort_text = tk.Text(frame_l,
                                      font=(FONT, self._text_size),
                                      bd=0,
                                      height=3,
                                      width=10,
                                      borderwidth=0,
                                      background='black',
                                      foreground='white',
                                      state="normal",
                                      # wrap=tk.NONE,
                                      yscrollcommand=self._scroll_prim
                                      )
        self._primPort_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scroll_l.pack(side=tk.LEFT, fill=tk.Y)

        self._scroll_r = tk.Scrollbar(frame_r, command=self.sync_scroll)
        self._secPort_text = tk.Text(frame_r,
                                     font=(FONT, self._text_size),
                                     bd=0,
                                     height=3,
                                     width=10,
                                     borderwidth=0,
                                     background='#000068',
                                     foreground='white',
                                     state="normal",
                                     # wrap = tk.NONE,
                                     yscrollcommand=self._scroll_sec
                                     )
        self._secPort_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scroll_r.pack(side=tk.LEFT, fill=tk.Y)

        tmp = ' '.join([str(x) for x in range(5000)])
        self._primPort_text.insert(tk.END, tmp)
        self._secPort_text.insert(tk.END, tmp)

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


class DualPort_Monitor(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        self._lang = root_win.language
        self.text_size = root_win.text_size
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
            pass
        self.lift()
        self._root_win.dualPortMon_win = self
        #################################################
        upper_frame = tk.Frame(self)
        upper_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabControl_prim_ports = ttk.Notebook(
            upper_frame,
            padding=5,
        )
        self._tabControl_prim_ports.pack(side=tk.TOP, fill=tk.BOTH, expand=True, )
        self.tab_list: {int: DP_MonitorTab} = {}

        all_prim_Ports = PORT_HANDLER.get_all_dualPorts_primary()
        for port_id in all_prim_Ports.keys():
            port = all_prim_Ports.get(port_id, None)
            if port:
                tab = DP_MonitorTab(self._tabControl_prim_ports, port, )
                self.tab_list[port_id] = tab
                port_lable_text = 'Port {}'.format(port.port_id)
                self._tabControl_prim_ports.add(tab, text=port_lable_text)

    def _close(self):
        self._root_win.dualPortMon_win = None
        self.destroy()
