import tkinter as tk
from tkinter import ttk

from cfg.constant import DEF_QSO_SYSMSG_BG, DEF_QSO_SYSMSG_FG, FONT, DEF_STAT_QSO_TX_COL, DEF_STAT_QSO_BG_COL, \
    DEF_STAT_QSO_RX_COL, TAG_QSO_PRP_STATUS_TX, CLR_QSO_PRP_STATUS_TX, CLR_QSO_PRP_STATUS_BG, TAG_QSO_PRP_STATUS_RX, \
    CLR_QSO_PRP_STATUS_RX, SERVICE_CH_START
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import set_new_tags, set_all_tags
from fnc.str_fnc import tk_filter_bad_chars, get_strTab, conv_time_DE_str


class QsoFrame(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent)
        self.pack(side='top', fill='both', expand=True)
        # ================================
        self._gui_root      = gui_root_cl
        self._popt_handler  = gui_root_cl.get_PH_mainGUI()
        # ================================
        self._text_size     = gui_root_cl.text_size
        #self._channel_index = gui_root_cl.channel_index
        # ================================
        self._all_tag_calls = []
        # ================================
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # ================================
        self._init_frame()
        self.set_tags()

    # ================================
    def _init_frame(self):
        text_frame = ttk.Frame(self)
        text_frame.pack(fill='both', expand=True)
        self._qso_txt = tk.Text(text_frame,
                               background=DEF_QSO_SYSMSG_BG,
                               foreground=DEF_QSO_SYSMSG_FG,
                               font=(FONT, self._text_size),
                               height=30,
                               width=5,
                               bd=0,
                               borderwidth=0,
                               # state="disabled",
                               relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                               highlightthickness=0,
                               )

        out_scrollbar = ttk.Scrollbar(
            text_frame,
            orient='vertical',
            command=self._qso_txt.yview
        )
        self._qso_txt.pack( side='left', fill='both', expand=True)
        out_scrollbar.pack(side='left', fill='y', expand=False)
        self._qso_txt.config(yscrollcommand=out_scrollbar.set)

    def set_tags(self):
        self._all_tag_calls = []
        all_stat_cfg = POPT_CFG.get_stat_CFGs()
        if all_stat_cfg:
            self._qso_txt.configure(state="normal")
        #guiCFG = POPT_CFG.load_guiPARM_main()
        # ==========================
        # QSO Call/Station Tags
        for call in list(all_stat_cfg.keys()):
            stat_cfg = all_stat_cfg[call]
            tx_fg = stat_cfg.get('stat_parm_qso_col_text_tx', DEF_STAT_QSO_TX_COL)
            tx_bg = stat_cfg.get('stat_parm_qso_col_bg', DEF_STAT_QSO_BG_COL)

            rx_fg = stat_cfg.get('stat_parm_qso_col_text_rx', DEF_STAT_QSO_RX_COL)

            tx_tag = 'TX-' + str(call)
            rx_tag = 'RX-' + str(call)
            self._all_tag_calls.append(str(call))

            self._qso_txt.tag_config(tx_tag,
                                    foreground=tx_fg,
                                    background=tx_bg,
                                    selectbackground=tx_fg,
                                    selectforeground=tx_bg,
                                    )
            self._qso_txt.tag_config(rx_tag,
                                    foreground=rx_fg,
                                    background=tx_bg,
                                    selectbackground=rx_fg,
                                    selectforeground=tx_bg,
                                    )
        # ==========================
        # QSO Sys Msg / Status Msg Tags
        self._qso_txt.tag_config('SYS-MSG',
                                foreground=DEF_QSO_SYSMSG_FG,
                                background=DEF_QSO_SYSMSG_BG,
                                selectbackground=DEF_QSO_SYSMSG_FG,
                                selectforeground=DEF_QSO_SYSMSG_BG,
                                )
        self._qso_txt.tag_config('TX-NOCALL',
                                foreground='#ffffff',
                                background='#000000',
                                selectbackground='#ffffff',
                                selectforeground='#000000',
                                )
        self._qso_txt.tag_config('RX-NOCALL',
                                foreground='#000000',
                                background='#ffffff',
                                selectbackground='#000000',
                                selectforeground='#ffffff',
                                )
        # PRP CLI-ESC Status MSG
        self._qso_txt.tag_config(TAG_QSO_PRP_STATUS_TX,
                                foreground=CLR_QSO_PRP_STATUS_TX,
                                background=CLR_QSO_PRP_STATUS_BG,
                                selectbackground=CLR_QSO_PRP_STATUS_TX,
                                selectforeground=CLR_QSO_PRP_STATUS_BG,
                                )
        self._qso_txt.tag_config(TAG_QSO_PRP_STATUS_RX,
                                foreground=CLR_QSO_PRP_STATUS_RX,
                                background=CLR_QSO_PRP_STATUS_BG,
                                selectbackground=CLR_QSO_PRP_STATUS_RX,
                                selectforeground=CLR_QSO_PRP_STATUS_BG,
                                )

        self._qso_txt.configure(state="disabled")
        self._qso_txt.tag_raise(tk.SEL)

    # ================================
    def update_qso_win(self):
        all_conn = self._popt_handler.get_all_connections()
        all_conn_ch_index = list(all_conn.keys())
        tr = False
        for channel in all_conn_ch_index:
            conn = all_conn[channel]
            if conn:
                if self._update_qso(conn):
                    tr = True
        if tr:
            self._gui_root.ch_status_update()
            return True
        return False

    def _update_qso(self, conn):
        if not conn:
            return False
        if conn.ft_obj:
            # self.ch_status_update()
            return True
        if conn.rx_tx_buf_guiData:
            self._update_qso_spooler(conn)
            # self.ch_status_update()
            return True
        return False

    def _update_qso_spooler(self, conn):
        ch_id   = conn.ch_index
        gui_buf = list(conn.rx_tx_buf_guiData)
        conn.rx_tx_buf_guiData = list(conn.rx_tx_buf_guiData[len(gui_buf):])
        for qso_data in gui_buf:
            # Sys Msg (Link Setup, Connected to, ...)
            if qso_data[0] == 'SYS':
                self.sysMsg_to_qso_task(arg=(qso_data[1], ch_id))
            # PRP Msg (CLI-ESC Status)
            elif qso_data[0] in [TAG_QSO_PRP_STATUS_TX, TAG_QSO_PRP_STATUS_RX]:
                self._PRPstatus_to_qso_task(qso_data[1], ch_id, qso_data[0])
            # QSO Data
            elif qso_data[0] == 'RX':
                self._update_qso_rx(conn, qso_data[1])
            else:
                self._update_qso_tx(conn, qso_data[1])

    def _update_qso_tx(self, conn, data):
        txt_enc = 'UTF-8'
        if conn.user_db_ent:
            txt_enc = str(conn.user_db_ent.Encoding)
        my_call_str = str(conn.my_call_str)
        my_call = str(conn.my_call)
        inp = data.decode(txt_enc, 'ignore')
        inp = tk_filter_bad_chars(inp)

        Ch_var = self._gui_root.get_ch_var(ch_index=conn.ch_index)
        Ch_var.output_win += inp
        if my_call_str in self._all_tag_calls:
            tag_name_tx = f'TX-{my_call_str}'
            Ch_var.last_tag_name = my_call_str
        elif my_call in self._all_tag_calls:
            tag_name_tx = f'TX-{my_call}'
            Ch_var.last_tag_name = my_call
        else:
            tag_name_tx = f'TX-{Ch_var.last_tag_name}'

        if self._gui_root.channel_index == conn.ch_index:
            self._qso_txt.configure(state="normal")
            ind = self._qso_txt.index('end-1c')
            self._qso_txt.insert('end', inp)
            ind2 = self._qso_txt.index('end-1c')
            if tag_name_tx:
                self._qso_txt.tag_add(tag_name_tx, ind, ind2)
            self._qso_txt.configure(state="disabled",
                                   exportselection=True
                                   )
            # TODO Autoscroll
            if float(self._qso_txt.index(tk.END)) - float(self._qso_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
                self.see_end_qso_win()
        else:
            if tag_name_tx:
                Ch_var.new_tags.append(
                    (tag_name_tx, len(inp))
                )

    def _update_qso_rx(self, conn, data):
        txt_enc = 'UTF-8'
        if conn.user_db_ent:
            txt_enc = str(conn.user_db_ent.Encoding)
        my_call_str = str(conn.my_call_str)
        my_call = str(conn.my_call)
        Ch_var = self._gui_root.get_ch_var(ch_index=conn.ch_index)
        out = data.decode(txt_enc, 'ignore')
        out = tk_filter_bad_chars(out)

        # Write RX Date to Window/Channel Buffer
        Ch_var.output_win += out
        if my_call_str in self._all_tag_calls:
            tag_name_rx = f'RX-{my_call_str}'
            Ch_var.last_tag_name = my_call_str
        elif my_call in self._all_tag_calls:
            tag_name_rx = f'RX-{my_call}'
            Ch_var.last_tag_name = my_call
        else:
            logger.error('Conn: _update_qso_rx: no Tagname')
            logger.error(f"Conn: last Tag: {Ch_var.last_tag_name}")
            tag_name_rx = f'RX-{Ch_var.last_tag_name}'

        if self._gui_root.channel_index == conn.ch_index:
            if Ch_var.t2speech:
                Ch_var.t2speech_buf += out.replace('\n', '')

            self._qso_txt.configure(state="normal")
            # configuring a tag called start
            ind = self._qso_txt.index('end-1c')
            self._qso_txt.insert('end', out)
            ind2 = self._qso_txt.index('end-1c')
            if tag_name_rx:
                self._qso_txt.tag_add(tag_name_rx, ind, ind2)

            self._qso_txt.configure(state="disabled",
                                   exportselection=True
                                   )
            # TODO Autoscroll
            if float(self._qso_txt.index(tk.END)) - float(self._qso_txt.index(tk.INSERT)) < 15 or Ch_var.autoscroll:
                self.see_end_qso_win()
        else:
            Ch_var.new_data_tr = True
            if Ch_var.t2speech:
                # TODO ?????????????????????????????????????????????
                Ch_var.t2speech_buf += '{} {} . {} . {}'.format(
                    self._getTabStr('channel'),
                    conn.ch_index,
                    conn.to_call_str,
                    out.replace('\n', '')
                )
            if tag_name_rx:
                Ch_var.new_tags.append(
                    (tag_name_rx, len(out))
                )
        Ch_var.rx_beep_tr = True

    # ================================
    def update_qso_Vars(self):
        #print(f"QSO-Frame ChID: {self._channel_index} - Main ChID: {self._gui_root.channel_index}")
        ch_vars = self._gui_root.get_ch_var(ch_index=self._gui_root.channel_index)

        self._qso_txt.configure(state="normal")

        self._qso_txt.delete('1.0', tk.END)
        self._qso_txt.insert(tk.END, ch_vars.output_win)
        self._qso_txt.configure(state="disabled")
        self._qso_txt.see(tk.END)

        set_all_tags(self._qso_txt, ch_vars.output_win_tags)
        set_new_tags(self._qso_txt, ch_vars.new_tags)
        ch_vars.new_tags = []

    # ================================
    def sysMsg_to_qso_task(self, arg: tuple):
        data, ch_index = arg
        if not data or (1 > ch_index > SERVICE_CH_START - 1):
            return
        data = data.replace('\r', '')
        data = f"\n    <{conv_time_DE_str()}>\n" + data + '\n'
        data = tk_filter_bad_chars(data)
        ch_vars = self._gui_root.get_ch_var(ch_index=ch_index)
        tag_name = 'SYS-MSG'
        ch_vars.output_win += data
        if self._gui_root.channel_index == ch_index:
            tr = False
            if float(self._qso_txt.index(tk.END)) - float(self._qso_txt.index("@0,0")) < 22:
                tr = True
            self._qso_txt.configure(state="normal")

            ind = self._qso_txt.index(tk.INSERT)
            self._qso_txt.insert('end', data)
            ind2 = self._qso_txt.index(tk.INSERT)
            self._qso_txt.tag_add(tag_name, ind, ind2)
            self._qso_txt.configure(state="disabled",
                                   exportselection=True
                                   )
            if tr or self._gui_root.get_ch_var().autoscroll:
                self.see_end_qso_win()

        else:
            ch_vars.new_tags.append(
                (tag_name, len(data))
            )
            ch_vars.new_data_tr = True
        ch_vars.rx_beep_tr = True
        self._gui_root.ch_status_update()

    # ================================
    def _PRPstatus_to_qso_task(self, data: str, ch_index, tag_name: str):
        if not data or ch_index < 1:
            return
        data = tk_filter_bad_chars(data)
        data += '\n'
        ch_vars = self._gui_root.get_ch_var(ch_index=ch_index)
        ch_vars.output_win += data
        if self._gui_root.channel_index == ch_index:
            tr = False
            if float(self._qso_txt.index(tk.END)) - float(self._qso_txt.index("@0,0")) < 22:
                tr = True
            self._qso_txt.configure(state="normal")

            ind = self._qso_txt.index(tk.INSERT)
            self._qso_txt.insert('end', data)
            ind2 = self._qso_txt.index(tk.INSERT)
            self._qso_txt.tag_add(tag_name, ind, ind2)
            self._qso_txt.configure(state="disabled",
                                   exportselection=True
                                   )
            if tr or self._gui_root.get_ch_var().autoscroll:
                self.see_end_qso_win()

        else:
            ch_vars.new_tags.append(
                (tag_name, len(data))
            )
            ch_vars.new_data_tr = True
        ch_vars.rx_beep_tr = True
        self._gui_root.ch_status_update()

    # ================================
    def see_end_qso_win(self):
        self._qso_txt.see("end")

    # ================================
    def get_qso_txt(self):
        return self._qso_txt
