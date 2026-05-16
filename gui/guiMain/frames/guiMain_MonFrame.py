import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk

from ax25.ax25_util.ax25monitor import monitor_frame_inp
from cfg.constant import MON_SYS_MSG_CLR_BG, MON_SYS_MSG_CLR_FG, FONT, DEF_PORT_MON_TX_COL, DEF_PORT_MON_BG_COL, \
    DEF_PORT_MON_RX_COL, PARAM_MAX_MON_LEN, POPT_BANNER, VER, WELCOME_SPEECH
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import tk_filter_bad_chars, get_strTab


class MonitorFrame(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent)
        # self.pack(side='bottom', fill='both', expand=True)
        # ================================
        self._gui_root     = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        self._mh           = gui_root_cl.get_MH()
        # ================================
        self._text_size    = gui_root_cl.text_size
        # ================================
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # ================================
        # GUI Vars
        self._mon_scroll_var        = gui_root_cl.mon_scroll_var
        self._mon_dec_dist_var      = gui_root_cl.mon_dec_dist_var
        self._mon_dec_aprs_var      = gui_root_cl.mon_dec_aprs_var
        self._mon_dec_nr_var        = gui_root_cl.mon_dec_nr_var
        self._mon_dec_hex_var       = gui_root_cl.mon_dec_hex_var
        self._setting_mon_encoding  = gui_root_cl.setting_mon_encoding
        # ================================
        self._init_frame()
        self.set_tags()

    # ================================
    def _init_frame(self):
        self.mon_txt = tk.Text(self,
                          background=MON_SYS_MSG_CLR_BG,
                          foreground=MON_SYS_MSG_CLR_FG,
                          font=(FONT, self._text_size),
                          height=30,
                          width=5,
                          bd=0,
                          borderwidth=0,
                          # state="disabled",
                          relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                          highlightthickness=0,
                          )
        mon_scrollbar = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.mon_txt.yview
        )
        self.mon_txt.pack(side='left', fill='both', expand=True)
        mon_scrollbar.pack(side='left', fill='y', expand=False)
        self.mon_txt.config(yscrollcommand=mon_scrollbar.set)

    def set_tags(self):
        self.mon_txt.configure(state="normal")
        # ==========================
        # Monitor Tags
        all_port = self._popt_handler.port_manager.ax25_ports
        for port_id in all_port.keys():
            tag_tx = f"tx{port_id}"
            tag_rx = f"rx{port_id}"
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_id)
            tx_fg = port_cfg.get('parm_mon_clr_tx', DEF_PORT_MON_TX_COL)
            tx_bg = port_cfg.get('parm_mon_clr_bg', DEF_PORT_MON_BG_COL)
            rx_fg = port_cfg.get('parm_mon_clr_rx', DEF_PORT_MON_RX_COL)
            self.mon_txt.tag_config(tag_tx, foreground=tx_fg,
                                    background=tx_bg,
                                    selectbackground=tx_fg,
                                    selectforeground=tx_bg,
                                    )
            self.mon_txt.tag_config(tag_rx, foreground=rx_fg,
                                    background=tx_bg,
                                    selectbackground=rx_fg,
                                    selectforeground=tx_bg,
                                    )
        self.mon_txt.tag_config("sys-msg", foreground=MON_SYS_MSG_CLR_FG,
                                background=MON_SYS_MSG_CLR_BG)
        self.mon_txt.configure(state="disabled")
        self.mon_txt.tag_raise(tk.SEL)
    # ================================
    def monitor_start_msg(self):
        # tmp_lang = int(self.language)
        # self.language = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])
        # SOUND.sprech(random.choice(WELCOME_SPEECH), wait=False)
        ban = POPT_BANNER.format(VER)
        tmp = ban.split('\r')
        for el in tmp:
            self.sysMsg_to_monitor_task(el)
        self.sysMsg_to_monitor_task('Python Other Packet Terminal ' + VER)
        for stat in POPT_CFG.get_stat_CFG_keys():
            self.sysMsg_to_monitor_task(self._getTabStr('mon_start_msg1').format(stat))
        all_ports = self._popt_handler.port_manager.ax25_ports
        for port_k in all_ports.keys():
            msg = self._getTabStr('mon_start_msg2')
            if all_ports[port_k].device_is_running:
                msg = self._getTabStr('mon_start_msg3')
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_k)
            self.sysMsg_to_monitor_task('Info: Port {}: {} - {} {}'
                                   .format(port_k,
                                           port_cfg.get('parm_PortName', ''),
                                           port_cfg.get('parm_PortTyp', ''),
                                           msg
                                           ))
            self.sysMsg_to_monitor_task('Info: Port {}: Parameter: {} | {}'
                                   .format(port_k,
                                           port_cfg.get('parm_PortParm', ('', 0))[0],
                                           port_cfg.get('parm_PortParm', ('', 0))[1],
                                           ))

    # ================================
    def sysMsg_to_monitor_task(self, var: str):
        # var += bytes.fromhex('15').decode('UTF-8')+'\n'
        """ Called from AX25Conn """
        ind = str(self.mon_txt.index(tk.INSERT))
        ins = 'SYS {0}: *** {1}\n'.format(datetime.now().strftime('%H:%M:%S'), var)

        self.mon_txt.configure(state="normal")
        self.mon_txt.insert(ind, ins)
        ind2 = self.mon_txt.index(tk.INSERT)
        self.mon_txt.tag_add("sys-msg", ind, ind2)
        self.mon_txt.configure(state="disabled")
        self._see_end_mon_win()
        """
        if 'Lob: ' in var:
            var = var.split('Lob: ')
            if len(var) > 1:
                SOUND.sprech(var[1], wait=False)
        """

    def monitor_q_task(self, mon_batch: list):
        self.mon_txt.configure(state="normal")
        mon_txt_tags = set(self.mon_txt.tag_names(None))  # Cache Tags

        full_text = ""
        tags_to_add = []
        mon_conf = {
            "distance": bool(self._mon_dec_dist_var.get()),
            "aprs_dec": bool(self._mon_dec_aprs_var.get()),
            "nr_dec": bool(self._mon_dec_nr_var.get()),
            "hex_out": bool(self._mon_dec_hex_var.get()),
            "decoding": str(self._setting_mon_encoding.get()),
        }

        end_idx = self.mon_txt.index('end-1c')  # Cache Index
        for axframe in mon_batch:
            port_conf    = axframe.get('port_conf', {})
            tx           = axframe.get('tx'       , False)
            axframe_conf = axframe
            port_id = port_conf.get('parm_PortNr', -1)
            mon_conf['port_name'] = port_conf.get('parm_PortName', '')

            mon_str = monitor_frame_inp(axframe_conf, mon_conf)
            var = tk_filter_bad_chars(mon_str)
            full_text += var

            ind_start = f"{end_idx} + {len(full_text) - len(var)}c"
            tag = f"tx{port_id}" if tx else f"rx{port_id}"
            tags_to_add.append((tag, ind_start, f"{ind_start} + {len(var)}c"))

        # Batch-Insert
        self.mon_txt.insert(tk.END, full_text)

        # Batch-Tags
        for tag, start, end in tags_to_add:
            if tag in mon_txt_tags:
                self.mon_txt.tag_add(tag, start, end)

        # Periodisches Cleanup (statt pro Task)
        cut_len = int(self.mon_txt.index('end-1c').split('.')[0]) - PARAM_MAX_MON_LEN + 1
        if cut_len > 0:
            self.mon_txt.delete('1.0', f"{cut_len}.0")

        # Autoscroll
        tr = float(self.mon_txt.index(tk.END)) - float(self.mon_txt.index(tk.INSERT)) < 15
        if tr or self._mon_scroll_var.get():
            self._see_end_mon_win()

        self.mon_txt.configure(state="disabled", exportselection=True)
        return True

    # ================================
    def _see_end_mon_win(self):
        self.mon_txt.see("end")
    # ===================================
    def get_mon_txt(self):
        return self.mon_txt