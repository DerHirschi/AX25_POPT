import time
import tkinter as tk
from tkinter import ttk

from ax25.ax25_l3.ax25_L3_StateTab import AX25L3_STATE_TAB
from cfg.constant import FONT_STAT_BAR, TEXT_SIZE_STATUS, STAT_BAR_TXT_CLR, COLOR_MAP, STATUS_BG
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class AX25StatusFrame(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent, height=18)
        #self.pack(side='bottom', fill='x', expand=False)
        # ================================
        self._gui_root     = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        self._style_name   = gui_root_cl.style_name
        # ================================
        self._get_colorMap = lambda : COLOR_MAP.get(self._style_name, ('#000000',  '#d9d9d9'))
        # ================================
        self._status_text_tab = {}
        for k, col in STATUS_BG.items():
            status_text = get_strTab(k, POPT_CFG.get_guiCFG_language(), warning=False)
            self._status_text_tab[k] = status_text, col
        # ================================
        self._status_name_var   = tk.StringVar(self)
        self._status_status_var = tk.StringVar(self)
        self._status_unack_var  = tk.StringVar(self)
        self._status_vs_var     = tk.StringVar(self)
        self._status_n2_var     = tk.StringVar(self)
        self._status_t1_var     = tk.StringVar(self)
        self._status_t2_var     = tk.StringVar(self)
        self._status_rtt_var    = tk.StringVar(self)
        self._status_t3_var     = tk.StringVar(self)
        self.rx_beep_var        = tk.IntVar(self)
        self.ts_box_var         = tk.IntVar(self)
        # ================================
        self._init_ax25status_frame()

    # ===========================================
    def _init_ax25status_frame(self):
        statusBa_frame = ttk.Frame(self, height=18)
        statusBa_frame.pack(expand=False, fill='x')

        name_f      = ttk.Frame(statusBa_frame, width=60)
        stat_f      = ttk.Frame(statusBa_frame, width=40)
        nack_f      = ttk.Frame(statusBa_frame, width=40)
        vsvr_f      = ttk.Frame(statusBa_frame, width=40)
        n2_f        = ttk.Frame(statusBa_frame, width=20)
        t1_f        = ttk.Frame(statusBa_frame, width=20)
        t2_f        = ttk.Frame(statusBa_frame, width=20)
        rtt_f       = ttk.Frame(statusBa_frame, width=20)
        t3_f        = ttk.Frame(statusBa_frame, width=20)
        rx_beep_f   = ttk.Frame(statusBa_frame, width=50)
        # ts_f        = ttk.Frame(self, width=20)

        name_f.pack(side='left', expand=True)
        stat_f.pack(side='left', expand=False)
        nack_f.pack(side='left', expand=False)
        vsvr_f.pack(side='left', expand=True)
        n2_f.pack(  side='left', expand=True)
        t1_f.pack(  side='left', expand=True)
        t2_f.pack(  side='left', expand=True)
        rtt_f.pack( side='left', expand=True)
        t3_f.pack(  side='left', expand=True)
        rx_beep_f.pack(side='left', expand=False)
        # ts_f.pack(  side='left', expand=False)

        fg, bg = self._get_colorMap()
        tk.Label(name_f,
                 textvariable=self._status_name_var,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 foreground=fg,
                 bg=bg,
                 width=10
                 ).pack(side='left', anchor='w')

        self._status_status = tk.Label(stat_f,
                                       textvariable=self._status_status_var,
                                       font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                       bg=bg,
                                       foreground=STAT_BAR_TXT_CLR,
                                       # width=8
                                       )
        self._status_status.pack()

        self._status_unack = tk.Label(nack_f,
                                      textvariable=self._status_unack_var,
                                      foreground=STAT_BAR_TXT_CLR,
                                      font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                      bg=bg,
                                      # width=8
                                      )
        self._status_unack.pack(side='left', anchor='w', expand=True)

        tk.Label(vsvr_f,
                 textvariable=self._status_vs_var,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 bg=bg,
                 foreground=fg
                 ).pack(side='left', anchor='w')

        self._status_n2 = tk.Label(n2_f,
                                   textvariable=self._status_n2_var,
                                   font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                   bg=bg,
                                   foreground=fg,
                                   width=5
                                   )
        self._status_n2.pack(side='left', anchor='w')

        tk.Label(t1_f,
                 textvariable=self._status_t1_var,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 bg=bg,
                 foreground=fg
                 ).pack(side='left', anchor='w')
        # PARM T2
        tk.Label(t2_f,
                 textvariable=self._status_t2_var,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 bg=bg,
                 foreground=fg
                 ).pack(side='left', anchor='w')
        # RTT
        tk.Label(rtt_f,
                 textvariable=self._status_rtt_var,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 bg=bg,
                 foreground=fg
                 ).pack(side='left', anchor='w')

        tk.Label(t3_f,
                 textvariable=self._status_t3_var,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 bg=bg,
                 foreground=fg
                 ).pack(side='left', anchor='w')
        # Checkbox RX-BEEP
        self.rx_beep_box = tk.Checkbutton(rx_beep_f,
                                          text="RX-BEEP",
                                          bg=bg,
                                          font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                          activebackground=bg,
                                          background=bg,
                                          borderwidth=0,
                                          onvalue=1, offvalue=0,
                                          foreground=fg,
                                          variable=self.rx_beep_var,
                                          command=self._chk_rx_beep,

                                          border=False,
                                          relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                          highlightthickness=0,
                                          )
        self.rx_beep_box.pack(side='left', anchor='w')
        # TODO Checkbox Time Stamp
        """
        self._ts_box_box = ttk.Checkbutton(ts_f,
                                       text="T-S",
                                       #font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                                       #bg=bg,
                                       #borderwidth=0,
                                       #activebackground=bg,
                                       onvalue=1, offvalue=0,
                                       #foreground=fg,
                                       variable=self._ts_box_var,
                                       command=self._chk_timestamp,
                                       state='disabled'
                                       )
        # self._ts_box_box.pack(side='left', anchor='w') # TODO
        """

    # ===========================================
    def update_status_bar(self):
        ret = False
        station = self._gui_root.get_conn(self._gui_root.channel_index)
        fg, bg = self._get_colorMap()
        if station is not None:
            from_call = str(station.my_call_str)
            status = AX25L3_STATE_TAB[station.l3_state_id][1]
            # uid = station.ax25_out_frame.addr_uid
            n2 = station.n2
            unAck = f" nACK: {station.get_unACK_buff_len} "
            vs_vr = f"VS/VR: {station.vr}/{station.vs}"
            n2_text = f"N2: {n2}"
            t1_text = f"T1: {max(0, int(station.t1 - time.time()))}"
            rtt_text = 'RTT: {:.1f}/{:.1f}'.format(station.RTT_Timer.rtt_last, station.RTT_Timer.rtt_average)
            t3_text = f"T3: {max(0, int(station.t3 - time.time()))}"
            if station.get_port_cfg.get('parm_T2_auto', True):
                t2_text = f"T2: {int(station.get_param_T2 * 1000)}A"
            else:
                t2_text = f"T2: {int(station.get_param_T2 * 1000)}"
            status_text, status_bg = self._status_text_tab.get(status, ('', bg))
            if status_text:
                status_text = f" {status_text} "
            ##
            if self._status_name_var.get() != from_call:
                self._status_name_var.set(from_call)
                ret = True

            if self._status_status_var.get() != status_text:
                self._status_status_var.set(status_text)
                self._status_status.configure(bg=status_bg)
                ret = True

            if self._status_unack_var.get() != unAck:
                self._status_unack_var.set(unAck)
                if station.get_unACK_buff_len:
                    if self._status_unack.cget('bg') != 'yellow':
                        self._status_unack.configure(bg='yellow')
                else:
                    if self._status_unack.cget('bg') != 'green':
                        self._status_unack.configure(bg='green')
                ret = True

            if self._status_vs_var.get() != vs_vr:
                self._status_vs_var.set(vs_vr)
                ret = True
            if self._status_n2_var.get() != n2_text:
                self._status_n2_var.set(n2_text)
                if n2 > 4:
                    if self._status_n2.cget('bg') != 'yellow':
                        self._status_n2.configure(fg='black')
                        self._status_n2.configure(bg='yellow')
                elif n2 > 10:
                    if self._status_n2.cget('bg') != 'orange':
                        self._status_n2.configure(fg='black')
                        self._status_n2.configure(bg='orange')
                else:
                    if self._status_n2.cget('bg') != bg:
                        self._status_n2.configure(bg=bg)
                        self._status_n2.configure(fg=fg)
                ret = True

            if self._status_t1_var.get() != t1_text:
                self._status_t1_var.set(t1_text)
                ret = True

            if self._status_t2_var.get() != t2_text:
                self._status_t2_var.set(t2_text)
                ret = True

            if self._status_rtt_var.get() != rtt_text:
                self._status_rtt_var.set(rtt_text)
                ret = True

            if self._status_t3_var.get() != t3_text:
                self._status_t3_var.set(t3_text)
                ret = True
        else:

            if self._status_status.cget('bg') != bg:
                # self.status_name.configure(text="", bg=STAT_BAR_CLR)
                self._status_name_var.set('')
                self._status_status.configure(bg=bg)
                self._status_status_var.set('')
                self._status_unack.configure(bg=bg)
                self._status_unack_var.set('')
                self._status_vs_var.set('')
                self._status_n2.configure(bg=bg)
                self._status_n2.configure(fg=fg)
                self._status_n2_var.set('')
                self._status_t1_var.set('')
                self._status_t2_var.set('')
                self._status_t3_var.set('')
                self._status_rtt_var.set('')
                ret = True
        return ret

    # ===========================================
    def _chk_rx_beep(self):
        rx_beep_check = self.rx_beep_var.get()
        bg = self._get_colorMap()[1]
        if rx_beep_check:
            if self.rx_beep_box.cget('bg') != 'green':
                self.rx_beep_box.configure(bg='green', activebackground='green')
        else:
            if self.rx_beep_box.cget('bg') != bg:
                self.rx_beep_box.configure(bg=bg, activebackground=bg, background=bg)
        self._gui_root.get_ch_var().rx_beep_opt = rx_beep_check
