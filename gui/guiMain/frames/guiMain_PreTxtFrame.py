import tkinter as tk
from tkinter import ttk

from cfg.constant import DEF_QSO_SYSMSG_BG, DEF_QSO_SYSMSG_FG, FONT, PARAM_MAX_PRE_LEN
from cfg.popt_config import POPT_CFG
from fnc.gui_fnc import set_all_tags


class PreTxtFrame(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent)
        self.pack(side='top', fill='both', expand=True)
        # ================================
        self._gui_root      = gui_root_cl
        self._popt_handler  = gui_root_cl.get_PH_mainGUI()
        # ================================
        self._text_size     = gui_root_cl.text_size
        # self._channel_index = gui_root_cl.channel_index
        # ================================
        # ================================
        #self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # ================================
        self._init_frame()
        self.set_tags()

    # ================================
    def _init_frame(self):
        text_frame = ttk.Frame(self)
        text_frame.pack(fill='both', expand=True)
        self._inp_txt = tk.Text(text_frame,
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
            command=self._inp_txt.yview
        )
        self._inp_txt.pack(side='left', fill='both', expand=True)
        out_scrollbar.pack(side='left', fill='y', expand=False)
        self._inp_txt.config(yscrollcommand=out_scrollbar.set)

    def set_tags(self):
        guiCFG = POPT_CFG.load_guiPARM_main()
        ##
        self._inp_txt.configure(foreground=guiCFG.get('gui_cfg_vor_col', 'white'),
                               background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        self._inp_txt.tag_config("send",
                                foreground=guiCFG.get('gui_cfg_vor_tx_col', '#25db04'),
                                background=guiCFG.get('gui_cfg_vor_bg_col', 'black'))
        self._inp_txt.tag_raise(tk.SEL)

    # ================================
    def update_qso_Vars(self):
        ch_vars = self._gui_root.get_ch_var(ch_index=self._gui_root.channel_index)

        self._inp_txt.delete('1.0', tk.END)
        self._inp_txt.insert(tk.END, ch_vars.input_win[:-1])
        set_all_tags(self._inp_txt, ch_vars.input_win_tags)


        self._inp_txt.mark_set("insert", ch_vars.input_win_cursor_index)

        # ==== Line Limit
        self._line_limit()

        ch_vars.input_win = self._inp_txt.get('1.0', 'end-1c')

        self._inp_txt.see(tk.END)

    # ================================
    def snd_text(self):
        if self._gui_root.channel_index:
            station = self._gui_root.get_conn(self._gui_root.channel_index)
            if station:
                ch_vars = self._gui_root.get_ch_var(ch_index=self._gui_root.channel_index)
                ind = str(ch_vars.input_win_index)
                if ind:
                    if float(ind) >= float(self._inp_txt.index(tk.INSERT)):
                        ind = str(self._inp_txt.index(tk.INSERT))
                    ind = str(int(float(ind))) + '.0'
                else:
                    ind = '1.0'

                txt_enc = self._gui_root.stat_info_encoding_var.get()
                if station.user_db_ent:
                    txt_enc = station.user_db_ent.Encoding
                # ind = str(int(float(self._inp_txt.index(tk.INSERT)))) + '.0'
                tmp_txt = self._inp_txt.get(ind, tk.INSERT)

                tmp_txt = (tmp_txt.replace('\n', '\r')).encode(txt_enc, 'ignore')
                station.send_data(tmp_txt)
                # self._update_qso_tx(station, tmp_txt)
                self._inp_txt.tag_remove('send', ind, str(self._inp_txt.index(tk.INSERT)))
                self._inp_txt.tag_add('send', ind, str(self._inp_txt.index(tk.INSERT)))

                # ==== Line Limit
                self._line_limit()

                #ch_vars.input_win = self._inp_txt.get('1.0', 'end-1c')
                ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))

                if '.0' in self._inp_txt.index(tk.INSERT):
                    self._inp_txt.tag_remove('send', 'insert-1c', tk.INSERT)

        else:
            self._send_UI()

    def _send_UI(self):
        ch_vars = self._gui_root.get_ch_var(ch_index=self._gui_root.channel_index)
        ind = str(ch_vars.input_win_index)
        if ind:
            if float(ind) >= float(self._inp_txt.index(tk.INSERT)):
                ind = str(self._inp_txt.index(tk.INSERT))
            ind = str(int(float(ind))) + '.0'
        else:
            ind = '1.0'
        tmp_txt = self._inp_txt.get(ind, self._inp_txt.index(tk.INSERT))
        tmp_txt = tmp_txt.replace('\n', '\r')
        port_id = int(self._gui_root.mon_port_var.get())
        if port_id in self._popt_handler.get_all_ports().keys():
            port = self._popt_handler.get_all_ports()[port_id]
            add = str(self._gui_root.mon_to_add_var.get()).upper()
            own_call = str(self._gui_root.mon_call_var.get())
            poll = bool(self._gui_root.mon_poll_var.get())
            cmd = bool(self._gui_root.mon_cmd_var.get())
            pid = self._gui_root.mon_pid_var.get()
            pid = pid.split('>')[0]
            pid = int(pid, 16)
            text = tmp_txt.encode()
            if add and own_call and text:
                text_list = [text[i:i + 256] for i in range(0, len(text), 256)]
                for el in text_list:
                    port.send_UI_frame(
                        own_call=own_call,
                        add_str=add,
                        text=el,
                        cmd_poll=(cmd, poll),
                        pid=pid
                    )
                # self._inp_txt.tag_add('send', ind, str(self._inp_txt.index(tk.INSERT)))
        ch_vars.input_win_index = str(self._inp_txt.index(tk.INSERT))
        if int(float(self._inp_txt.index(tk.INSERT))) != int(float(self._inp_txt.index(tk.END))) - 1:
            self._inp_txt.delete(tk.END, tk.END)

    # ================================
    def get_inp_txt(self):
        return self._inp_txt

    # ================================
    def _line_limit(self):
        # ==== Line Limit
        lines = int(self._inp_txt.index('end-1c').split('.')[0])
        if lines > PARAM_MAX_PRE_LEN:
            self._inp_txt.delete('1.0', f'{lines - PARAM_MAX_PRE_LEN}.0')
