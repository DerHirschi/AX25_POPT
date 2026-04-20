import tkinter as tk
from tkinter import ttk

from cfg.constant import COLOR_MAP, FONT_STAT_BAR, TEXT_SIZE_STATUS, STATION_TYPS, STAT_BAR_TXT_CLR, STAT_BAR_CLR, \
    ENCODINGS, CLI_TYP_DIGI, CLI_TYP_PIPE
from cfg.logger_config import logger
from fnc.str_fnc import get_time_delta


class ConnStatusBar(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent)
        # self.pack(side='bottom', fill='both', expand=True)
        # ================================
        self._gui_root     = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        self._style_name   = gui_root_cl.style_name
        # ================================
        self._get_colorMap = lambda : COLOR_MAP.get(self._style_name, ('#000000',  '#d9d9d9'))
        # ================================
        self._stat_info_name_var        = tk.StringVar(self)
        self._stat_info_qth_var         = tk.StringVar(self)
        self._stat_info_loc_var         = tk.StringVar(self)
        self._stat_info_typ_var         = tk.StringVar(self)
        self._stat_info_sw_var          = tk.StringVar(self)
        self._stat_info_timer_var       = tk.StringVar(self)
        self._stat_info_encoding_var    = gui_root_cl.stat_info_encoding_var
        self._stat_info_status_var      = tk.StringVar(self)

        # ================================
        self._init_frame()

    # ================================
    def _init_frame(self):
        ###############################################
        # Connection Status bar
        name_f  = ttk.Frame(self)
        qth_f   = ttk.Frame(self)
        loc_f   = ttk.Frame(self)
        typ_f   = tk.Frame( self, bg="#0ed8c3")
        sw_f    = tk.Frame( self, bg="#ffd444")
        stat_f  = ttk.Frame(self)
        time_f  = ttk.Frame(self)
        enc_f   = ttk.Frame(self)

        name_f.pack(side='left', expand=True, anchor="center")
        qth_f.pack( side='left', expand=True, anchor="center")
        loc_f.pack( side='left', expand=True, anchor="center", padx=5)
        typ_f.pack( side='left', expand=True, anchor="center", fill='x')
        sw_f.pack(  side='left', expand=True, anchor="center", fill='x')
        stat_f.pack(side='left', expand=False, anchor="center")
        time_f.pack(side='left', expand=False, anchor="center", padx=7)
        enc_f.pack( side='left', expand=False, anchor="center", fill='x')

        fg, bg = self._get_colorMap()

        name_label = ttk.Label(name_f,
                               textvariable=self._stat_info_name_var,
                               # bg=STAT_BAR_CLR,
                               # height=1,
                               borderwidth=0,
                               border=0,
                               # fg=fg,
                               # bg=bg,
                               font=(FONT_STAT_BAR, TEXT_SIZE_STATUS, 'bold')

                               )
        name_label.pack()
        name_label.bind('<Button-1>', self._gui_root.open_user_db_win)
        qth_label = tk.Label(qth_f,
                             textvariable=self._stat_info_qth_var,
                             bg=bg,
                             fg=fg,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS)
                             )
        qth_label.bind('<Button-1>', self._gui_root.open_user_db_win)
        qth_label.pack()
        loc_label = tk.Label(loc_f,
                             textvariable=self._stat_info_loc_var,
                             bg=bg,
                             fg=fg,
                             height=1,
                             borderwidth=0,
                             border=0,
                             font=(FONT_STAT_BAR, TEXT_SIZE_STATUS)
                             )
        loc_label.bind('<Button-1>', self._gui_root.open_user_db_win)
        loc_label.pack()

        opt = list(STATION_TYPS)
        stat_typ = tk.OptionMenu(
            typ_f,
            self._stat_info_typ_var,
            *opt,
            command=self._set_stat_typ,
        )
        stat_typ.configure(
            background="#0ed8c3",
            fg=STAT_BAR_TXT_CLR,
            # width=8,
            height=1,
            borderwidth=0,
            border=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,),
            relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
            highlightthickness=0,
        )
        stat_typ.pack(fill='x', expand=True, padx=6)

        tk.Label(sw_f,
                 textvariable=self._stat_info_sw_var,
                 # width=18,
                 bg="#ffd444",
                 # fg="red3",
                 height=1,
                 borderwidth=0,
                 border=0,
                 font=(FONT_STAT_BAR, TEXT_SIZE_STATUS),
                 relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                 highlightthickness=0,
                 ).pack(fill='x', expand=True, padx=6)

        self.status_label = tk.Label(stat_f,
                                     textvariable=self._stat_info_status_var,
                                     bg=STAT_BAR_CLR,
                                     fg="red3",
                                     height=1,
                                     borderwidth=0,
                                     border=0,
                                     font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,),
                                     relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
                                     highlightthickness=0,
                                     width=7
                                     )
        self.status_label.pack()
        self.status_label.bind('<Button-1>', self._gui_root.do_priv)

        ttk.Label(time_f,
                  textvariable=self._stat_info_timer_var,
                  # width=6,
                  # height=1,
                  borderwidth=0,
                  border=0,
                  # bg="steel blue",
                  # fg="red3",
                  font=(FONT_STAT_BAR, TEXT_SIZE_STATUS,)
                  ).pack(fill='x', expand=True)
        opt = ENCODINGS
        txt_encoding_ent = tk.OptionMenu(
            enc_f,
            self._stat_info_encoding_var,
            *opt,
            command=self._change_txt_encoding
        )
        txt_encoding_ent.configure(
            background="steel blue",
            height=1,
            width=8,
            borderwidth=0,
            border=0,
            font=(FONT_STAT_BAR, TEXT_SIZE_STATUS - 1,),
            relief="flat",  # Flache Optik für ttk-ähnliches Aussehen
            highlightthickness=0,
        )
        txt_encoding_ent.pack(fill='x', expand=False)

    # ================================
    def update_station_info(self):
        name = '-------'
        qth = '-------'
        loc = '------'
        # _dist = 0
        status = '-------'
        typ = '-----'
        sw = '---------'
        enc = 'UTF-8'
        conn = self._gui_root.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                if db_ent.Name:
                    name = db_ent.Name
                if db_ent.QTH:
                    qth = db_ent.QTH
                if db_ent.LOC:
                    loc = db_ent.LOC
                if db_ent.Distance > 0:
                    loc += f" ({db_ent.Distance} km)"
                if db_ent.TYP:
                    typ = db_ent.TYP
                if db_ent.Software:
                    sw = db_ent.Software
                enc = db_ent.Encoding
            if conn.is_link:
                status = CLI_TYP_DIGI
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', )
            elif conn.pipe is not None:
                status = CLI_TYP_PIPE
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', )
            elif conn.ft_obj is not None:
                status = f'{conn.ft_obj.dir} FILE'
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    # self.status_label.bind('<Button-1>', lambda: self._open_settings_window('ft_manager'))
                    self.status_label.bind('<Button-1>', self._gui_root.open_ft_manager)
            else:
                status = ''
                try:
                    if conn.cli.sysop_priv:
                        status += 'S'
                    else:
                        status += '-'
                    if conn.link_holder_on:
                        status += 'L'
                    else:
                        status += '-'
                    if conn.is_RNR:
                        status += 'R'
                    else:
                        status += '-'
                except Exception as ex:
                    logger.error(ex)
                    status = '---'
                status += '----'
                if self._stat_info_status_var.get() != status:
                    self._stat_info_status_var.set(status)
                    self.status_label.bind('<Button-1>', self._gui_root.do_priv)
        elif self._stat_info_status_var.get() != status:
            self._stat_info_status_var.set(status)
            self.status_label.bind('<Button-1>', )
        """
        if _dist:
            loc += f" ({_dist} km)"
        """
        # if self.stat_info_status_var.get() != _status:
        #     self.stat_info_status_var.set(_status)
        if self._stat_info_name_var.get() != name:
            self._stat_info_name_var.set(name)
        if self._stat_info_qth_var.get() != qth:
            self._stat_info_qth_var.set(qth)
        if self._stat_info_loc_var.get() != loc:
            self._stat_info_loc_var.set(loc)
        if self._stat_info_typ_var.get() != typ:
            self._stat_info_typ_var.set(typ)
        if self._stat_info_sw_var.get() != sw:
            self._stat_info_sw_var.set(sw)
        if self._stat_info_encoding_var.get() != enc:
            self._stat_info_encoding_var.set(enc)

    def update_stat_info_conn_timer(self):
        conn = self._gui_root.get_conn()
        if conn is not None:
            if hasattr(conn, 'cli'):
                self._stat_info_timer_var.set(get_time_delta(conn.cli.time_start))
                return
        if self._stat_info_timer_var.get() != '--:--:--':
            self._stat_info_timer_var.set('--:--:--')

    # ================================
    def _set_stat_typ(self, event=None):
        conn = self._gui_root.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                db_ent.TYP = self._stat_info_typ_var.get()
        else:
            self._stat_info_typ_var.set('-----')

    def _change_txt_encoding(self, event=None, enc=''):
        conn = self._gui_root.get_conn()
        if conn is not None:
            db_ent = conn.user_db_ent
            if db_ent:
                if not enc:
                    enc = self._stat_info_encoding_var.get()
                db_ent.Encoding = enc
        else:
            self._stat_info_encoding_var.set('UTF-8')
    # ================================
