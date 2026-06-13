import tkinter as tk
from tkinter import ttk, Menu, messagebox
from datetime import datetime, timedelta
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import convert_str_to_datetime, get_strTab
from gui import NavigationToolbar2Tk, FigureCanvasTkAgg
from gui import plt


class _PlotPanel:
    """Einzelner Plot-Panel mit eigenem Cache, Config und Figure"""

    FRAME_TYPES = ['I', 'SABM', 'DM', 'DISC', 'REJ', 'SREJ', 'RR', 'RNR', 'UA', 'UI', 'FRMR']
    PLOT_TYPES = ['port_plot_line', 'port_plot_stacked_area', 'port_plot_grouped_bar',
                  'port_plot_stacked_bar', 'port_plot_pie', 'port_plot_horizontal_bar']
    DATA_TYPES = ['port_data_bytes', 'port_data_count']

    _BYTE_COL = {'I': 4, 'SABM': 5, 'DM': 6, 'DISC': 7, 'REJ': 8, 'SREJ': 9,
                 'RR': 10, 'RNR': 11, 'UA': 12, 'UI': 13, 'FRMR': 14}
    _COUNT_COL = {'I': 15, 'SABM': 16, 'DM': 17, 'DISC': 18, 'REJ': 19, 'SREJ': 20,
                  'RR': 21, 'RNR': 22, 'UI': 23, 'UA': 24, 'FRMR': 25}

    COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
              '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8']

    def __init__(self, master, mh, on_config_change):
        self._mh = mh
        self._on_config_change = on_config_change
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

        self._cache_rows = None
        self._cache_key = None

        self._port_var = tk.IntVar(value=0)
        now = datetime.now()
        self._from_date_var = tk.StringVar(value=(now - timedelta(days=1)).strftime('%d.%m.%Y'))
        self._to_date_var = tk.StringVar(value=now.strftime('%d.%m.%Y'))
        self._plot_type_var = tk.StringVar(value=self.PLOT_TYPES[0])
        self._data_type_var = tk.StringVar(value=self.DATA_TYPES[0])
        self._chk_vars = {ft: tk.BooleanVar(value=True) for ft in self.FRAME_TYPES}

        self._build_ui(master)
        self._setup_figure()

    # -----------------------------------------------------------------
    # UI-Aufbau
    # -----------------------------------------------------------------
    def _build_ui(self, master):
        self._outer = ttk.LabelFrame(master)
        ctrl = tk.Frame(self._outer)
        ctrl.pack(fill=tk.X, padx=2, pady=(2, 0))

        tk.Label(ctrl, text=self._getTabStr('port_stat_port')).pack(side=tk.LEFT)
        ttk.Spinbox(ctrl, textvariable=self._port_var, width=2, from_=0, to=10,
                    command=self._on_change).pack(side=tk.LEFT, padx=(0, 4))

        tk.Label(ctrl, text=self._getTabStr('port_stat_from')).pack(side=tk.LEFT)
        vcmd = (master.register(self._validate_date), '%P')
        from_entry = ttk.Entry(ctrl, textvariable=self._from_date_var, width=10,
                               validate='focusout', validatecommand=vcmd)
        from_entry.pack(side=tk.LEFT, padx=(0, 2))
        from_entry.bind('<FocusOut>', self._on_date_change)
        from_entry.bind('<Return>', self._on_date_change)

        tk.Label(ctrl, text=self._getTabStr('port_stat_to')).pack(side=tk.LEFT)
        to_entry = ttk.Entry(ctrl, textvariable=self._to_date_var, width=10,
                             validate='focusout', validatecommand=vcmd)
        to_entry.pack(side=tk.LEFT, padx=(0, 4))
        to_entry.bind('<FocusOut>', self._on_date_change)
        to_entry.bind('<Return>', self._on_date_change)

        self._make_menubtn(ctrl, self._plot_type_var, self.PLOT_TYPES,
                           self._on_render).pack(side=tk.LEFT, padx=(0, 4))
        self._make_menubtn(ctrl, self._data_type_var, self.DATA_TYPES,
                           self._on_render).pack(side=tk.LEFT)

        chk = tk.Frame(self._outer)
        chk.pack(fill=tk.X, padx=2, pady=(0, 0))
        for ft in self.FRAME_TYPES:
            tk.Checkbutton(chk, variable=self._chk_vars[ft], text=ft,
                           command=self._on_render).pack(side=tk.LEFT, padx=1)

    def _make_menubtn(self, parent, variable, keys, callback=None):
        btn = tk.Menubutton(parent, text=self._getTabStr(variable.get()),
                            relief=tk.RAISED)
        menu = tk.Menu(btn, tearoff=False)
        btn.configure(menu=menu)
        for key in keys:
            menu.add_command(
                label=self._getTabStr(key),
                command=lambda k=key: self._on_menu_select(variable, btn, k, callback)
            )
        return btn

    def _on_menu_select(self, variable, btn, key, callback):
        variable.set(key)
        btn.configure(text=self._getTabStr(key))
        if callback:
            callback()

    def _setup_figure(self):
        self._fig, self._plot1 = plt.subplots()
        self._fig.set_facecolor('xkcd:light grey')
        self._plot1.set_facecolor('#000000')
        self._fig.subplots_adjust(top=0.95, bottom=0.10, left=0.10, right=0.98)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self._outer)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH, padx=2, pady=(0, 2))

        toolbar = NavigationToolbar2Tk(self._canvas, self._outer)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)

    # -----------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------
    @staticmethod
    def _validate_date(date_str):
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    def _on_date_change(self, event=None):
        self._reload_data()
        self._render()
        if self._on_config_change:
            self._on_config_change(self)

    def _on_change(self):
        self._reload_data()
        self._render()
        if self._on_config_change:
            self._on_config_change(self)

    def _on_render(self, event=None):
        self._render()
        if self._on_config_change:
            self._on_config_change(self)

    # -----------------------------------------------------------------
    # Cache
    # -----------------------------------------------------------------
    def _reload_data(self, force=False):
        port_id = int(self._port_var.get())
        from_str = self._from_date_var.get()
        to_str = self._to_date_var.get()
        key = (port_id, from_str, to_str)
        if not force and self._cache_key == key and self._cache_rows is not None:
            return
        self._cache_key = key
        from_dt, to_dt, _, _ = self._get_span()
        self._cache_rows = self._mh.PortStat_get_data_by_port_range(port_id, from_dt, to_dt)

    def reload(self):
        self._reload_data(force=True)
        self._render()

    # -----------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------
    def render(self, event=None):
        self._reload_data()
        self._render()

    def _setup_axes(self):
        self._fig.clf()
        self._plot1 = self._fig.add_subplot(111)
        self._plot1.set_facecolor('#000000')
        self._fig.set_facecolor('xkcd:light grey')
        self._fig.subplots_adjust(top=0.95, bottom=0.10, left=0.10, right=0.98)

    def _render(self, event=None):
        self._setup_axes()
        if not self._cache_rows:
            self._plot1.text(0.5, 0.5, self._getTabStr('port_stat_no_data'), ha='center', va='center',
                             transform=self._plot1.transAxes, color='white')
            self._canvas.draw()
            return

        active = self._get_active_flags()
        data_type = self._data_type_var.get()
        plot_type = self._plot_type_var.get()

        if plot_type in ('port_plot_line', 'port_plot_stacked_area'):
            x_vals, ft_data = self._compute_time_series(active, data_type)
            if not x_vals:
                self._canvas.draw()
                return
            if plot_type == 'port_plot_line':
                self._render_line(x_vals, ft_data, active)
            else:
                self._render_stacked_area(x_vals, ft_data, active)
            _, _, total_h, _ = self._get_span()
            self._plot1.set_xlim([total_h, 0])
            self._plot1.set_xlabel(self._getTabStr('port_stat_hours_ago'))
        elif plot_type == 'port_plot_stacked_bar':
            x_vals, ft_data = self._compute_hourly_buckets(active, data_type)
            self._render_stacked_bar(x_vals, ft_data, active)
            _, _, total_h, _ = self._get_span()
            self._plot1.set_xlim([total_h, 0])
            self._plot1.set_xlabel(self._getTabStr('port_stat_hours_ago'))
        elif plot_type == 'port_plot_grouped_bar':
            agg = self._compute_aggregate(active, data_type)
            agg = self._normalize_agg_by_days(agg)
            self._render_grouped_bar(agg, data_type)
        elif plot_type == 'port_plot_pie':
            agg = self._compute_aggregate(active, data_type)
            self._render_pie(agg)
        elif plot_type == 'port_plot_horizontal_bar':
            agg = self._compute_aggregate(active, data_type)
            agg = self._normalize_agg_by_days(agg)
            self._render_horizontal_bar(agg, data_type)

        if plot_type in ('port_plot_line', 'port_plot_stacked_area', 'port_plot_stacked_bar') and active:
            self._plot1.legend(fontsize=7, loc='upper right')
        self._canvas.draw()

    def _get_active_flags(self):
        return [ft for ft in self.FRAME_TYPES if self._chk_vars[ft].get()]

    # -----------------------------------------------------------------
    # Datenaufbereitung
    # -----------------------------------------------------------------
    def _get_span(self):
        """Gibt (from_dt, to_dt, span_h, span_days) aus den Date-StringVars zurück."""
        try:
            from_dt = datetime.strptime(self._from_date_var.get(), '%d.%m.%Y')
            to_dt = datetime.strptime(self._to_date_var.get(), '%d.%m.%Y') + timedelta(days=1)
            span_s = (to_dt - from_dt).total_seconds()
            return from_dt, to_dt, span_s / 3600, span_s / 86400
        except Exception:
            now = datetime.now()
            return now - timedelta(days=1), now, 24.0, 1.0

    def _get_val(self, row, frame_type, data_type):
        if data_type == 'port_data_count':
            return float(row[self._COUNT_COL[frame_type]])
        return float(row[self._BYTE_COL[frame_type]])

    def _compute_time_series(self, active, data_type):
        if not self._cache_rows:
            return [], {}
        _, ref_dt, total_h, _ = self._get_span()
        x_vals = []
        ft_data = {ft: [] for ft in active}
        last_ts = None
        for row in self._cache_rows:
            try:
                ts = convert_str_to_datetime(row[1])
            except Exception:
                continue
            if last_ts is not None:
                gap = int((ts - last_ts).total_seconds() / 60) - 1
                for m in range(max(0, gap)):
                    gap_ts = last_ts + timedelta(minutes=m + 1)
                    x_vals.append((ref_dt - gap_ts).total_seconds() / 3600)
                    for ft in active:
                        ft_data[ft].append(0)
            x_vals.append((ref_dt - ts).total_seconds() / 3600)
            for ft in active:
                ft_data[ft].append(self._get_val(row, ft, data_type))
            last_ts = ts
        return x_vals, ft_data

    def _compute_hourly_buckets(self, active, data_type):
        if not self._cache_rows:
            return [], {}
        from_dt, to_dt, total_h, _ = self._get_span()
        if total_h <= 72:
            bucket_h = 1
        elif total_h <= 336:
            bucket_h = 6
        elif total_h <= 1440:
            bucket_h = 24
        elif total_h <= 17520:
            bucket_h = 168
        else:
            bucket_h = 720
        n_buckets = max(1, int(total_h / bucket_h))
        buckets = {i: {ft: 0.0 for ft in active} for i in range(n_buckets)}
        for row in self._cache_rows:
            try:
                ts = convert_str_to_datetime(row[1])
            except Exception:
                continue
            if ts < from_dt or ts >= to_dt:
                continue
            hours_ago = (to_dt - ts).total_seconds() / 3600
            idx = n_buckets - 1 - int(hours_ago / bucket_h)
            if 0 <= idx < n_buckets:
                for ft in active:
                    buckets[idx][ft] += self._get_val(row, ft, data_type)
        x_vals = [total_h - (i + 0.5) * bucket_h for i in range(n_buckets)]
        ft_data = {ft: [buckets[i][ft] for i in range(n_buckets)] for ft in active}
        return x_vals, ft_data

    def _compute_aggregate(self, active, data_type):
        if not self._cache_rows:
            return {ft: 0.0 for ft in active}
        agg = {ft: 0.0 for ft in active}
        for row in self._cache_rows:
            for ft in active:
                agg[ft] += self._get_val(row, ft, data_type)
        return agg

    def _normalize_agg_by_days(self, agg):
        _, _, _, days = self._get_span()
        days = max(days, 1.0)
        if days <= 1:
            return agg
        return {ft: v / days for ft, v in agg.items()}

    # -----------------------------------------------------------------
    # Plot-Renderer
    # -----------------------------------------------------------------
    def _render_line(self, x_vals, ft_data, active):
        for ft in active:
            color = self.COLORS[self.FRAME_TYPES.index(ft) % len(self.COLORS)]
            self._plot1.plot(x_vals, ft_data[ft], label=ft, color=color, linewidth=1)
        self._plot1.set_ylabel(self._getTabStr(self._data_type_var.get()))

    def _render_stacked_area(self, x_vals, ft_data, active):
        stack = [ft_data[ft] for ft in active]
        colors = [self.COLORS[self.FRAME_TYPES.index(ft) % len(self.COLORS)] for ft in active]
        self._plot1.stackplot(x_vals, *stack, labels=active, colors=colors)
        self._plot1.set_ylabel(self._getTabStr(self._data_type_var.get()))

    def _render_stacked_bar(self, x_vals, ft_data, active):
        n = len(x_vals)
        bottom = [0.0] * n
        for ft in active:
            vals = ft_data[ft]
            color = self.COLORS[self.FRAME_TYPES.index(ft) % len(self.COLORS)]
            self._plot1.bar(x_vals, vals, bottom=bottom, label=ft, color=color, width=0.8)
            bottom = [bottom[i] + vals[i] for i in range(n)]
        self._plot1.set_ylabel(self._getTabStr(self._data_type_var.get()))

    def _render_grouped_bar(self, agg, data_type):
        active = [ft for ft in self.FRAME_TYPES if ft in agg]
        if not active:
            return
        x = range(len(active))
        values = [agg[ft] for ft in active]
        colors = [self.COLORS[self.FRAME_TYPES.index(ft) % len(self.COLORS)] for ft in active]
        self._plot1.bar(x, values, color=colors, width=0.6)
        self._plot1.set_xticks(list(x))
        self._plot1.set_xticklabels(active, fontsize=7)
        self._plot1.set_ylabel(self._getTabStr(data_type))

    def _render_pie(self, agg):
        active = [ft for ft in self.FRAME_TYPES if ft in agg and agg[ft] > 0]
        if not active:
            return
        values = [agg[ft] for ft in active]
        colors = [self.COLORS[self.FRAME_TYPES.index(ft) % len(self.COLORS)] for ft in active]
        self._plot1.pie(values, labels=active, autopct='%1.1f%%',
                        colors=colors, startangle=90)
        self._plot1.axis('equal')

    def _render_horizontal_bar(self, agg, data_type):
        active = [ft for ft in self.FRAME_TYPES if ft in agg]
        if not active:
            return
        values = [agg[ft] for ft in active]
        colors = [self.COLORS[self.FRAME_TYPES.index(ft) % len(self.COLORS)] for ft in active]
        self._plot1.barh(range(len(active)), values, color=colors, height=0.6)
        self._plot1.set_yticks(range(len(active)))
        self._plot1.set_yticklabels(active, fontsize=7)
        self._plot1.set_xlabel(self._getTabStr(data_type))

    # -----------------------------------------------------------------
    # Daten für die Tabelle (wird vom Besitzer abgefragt)
    # -----------------------------------------------------------------
    def get_table_data(self):
        """Gibt (cnt_dict, byt_dict) für die Tabelle zurück"""
        cnt_tot = {ft: 0 for ft in self.FRAME_TYPES}
        byt_tot = {ft: 0 for ft in self.FRAME_TYPES}
        if not self._cache_rows:
            return cnt_tot, byt_tot
        for row in self._cache_rows:
            for ft in self.FRAME_TYPES:
                cnt_tot[ft] += row[self._COUNT_COL[ft]]
                byt_tot[ft] += row[self._BYTE_COL[ft]]
        return cnt_tot, byt_tot

    def get_span_hours(self):
        try:
            from_dt = datetime.strptime(self._from_date_var.get(), '%d.%m.%Y')
            to_dt = datetime.strptime(self._to_date_var.get(), '%d.%m.%Y') + timedelta(days=1)
            return max((to_dt - from_dt).total_seconds() / 3600, 1.0)
        except Exception:
            return 1.0

    def get_cache_key(self):
        return self._cache_key

    # -----------------------------------------------------------------
    # Cleanup
    # -----------------------------------------------------------------
    def destroy(self):
        self._plot1.clear()
        plt.close(self._fig)
        self._canvas.get_tk_widget().destroy()


class PlotWindow(tk.Toplevel):
    """Port-Statistik-Fenster mit 2 Plot-Panels nebeneinander und Tabelle"""

    def __init__(self, root_cl):
        tk.Toplevel.__init__(self, master=root_cl.main_win)
        self._root_win = root_cl
        self._popt_handler = root_cl.get_PH_mainGUI()
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.wm_title(self._getTabStr('port_stat_title'))
        self.geometry(f"1000x650+{root_cl.main_win.winfo_x()}+{root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_plot)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)

        self._mh = self._popt_handler.get_MH()
        self._panels = []
        self._active_panel = None

        self._build_ui()
        self._init_menubar()

        for p in self._panels:
            p.render()
        self._active_panel = self._panels[0]
        self._update_table()

        self._root_win.toplevel_manager.port_stat_win = self

    # -----------------------------------------------------------------
    # UI-Aufbau
    # -----------------------------------------------------------------
    def _build_ui(self):
        # Vertikales PanedWindow (Plots + Tabelle)
        self._pw = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self._pw.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Horizontales PanedWindow für 2 Plot-Panels
        self._hpw = ttk.PanedWindow(self._pw, orient=tk.HORIZONTAL)
        self._pw.add(self._hpw, weight=2)

        for i in range(2):
            panel = _PlotPanel(self._hpw, self._mh, self._on_panel_change)
            self._hpw.add(panel._outer, weight=1)
            self._panels.append(panel)

        # Tabellen-Frame
        table_frame = tk.Frame(self._pw)
        self._pw.add(table_frame, weight=1)

        cols = ('frame', 'count', 'bytes', 'pct_cnt', 'pct_byt', 'avg', 'rate')
        headings = (self._getTabStr('port_stat_tbl_frame'), self._getTabStr('port_stat_tbl_count'),
                    self._getTabStr('port_stat_tbl_bytes'), self._getTabStr('port_stat_tbl_pct_cnt'),
                    self._getTabStr('port_stat_tbl_pct_byt'), self._getTabStr('port_stat_tbl_avg'),
                    self._getTabStr('port_stat_tbl_rate'))
        self._tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=6)
        for col, hdr in zip(cols, headings):
            self._tree.heading(col, text=hdr)
            self._tree.column(col, width=70, anchor='e' if col != 'frame' else 'w')
        self._tree.column('frame', width=70)
        self._tree.column('count', width=80)
        self._tree.column('bytes', width=90)
        self._tree.column('pct_cnt', width=75)
        self._tree.column('pct_byt', width=75)
        self._tree.column('avg', width=85)
        self._tree.column('rate', width=80)

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll_y.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # PW-Ratio wiederherstellen
        gui_cfg = POPT_CFG.load_guiPARM_main()
        ratio = gui_cfg.get('port_stat_pw_ratio', 0.7)
        self.after(100, lambda: self._restore_pw_ratio(ratio))
        self._pw.bind('<ButtonRelease-1>', self._on_sash_release)

    def _restore_pw_ratio(self, ratio):
        try:
            total = self._pw.winfo_height()
            if total > 10:
                top = int(total * ratio)
                self._pw.sashpos(0, top)
        except Exception:
            pass

    def _on_sash_release(self, event):
        try:
            total = self._pw.winfo_height()
            pos = self._pw.sashpos(0)
            if total > 0:
                gui_cfg = POPT_CFG.load_guiPARM_main()
                gui_cfg['port_stat_pw_ratio'] = pos / total
                POPT_CFG.save_guiPARM_main(gui_cfg)
        except Exception:
            pass

    # -----------------------------------------------------------------
    # Panel-Event
    # -----------------------------------------------------------------
    def _on_panel_change(self, panel):
        self._active_panel = panel
        self._update_table()

    # -----------------------------------------------------------------
    # Tabelle
    # -----------------------------------------------------------------
    def _update_table(self):
        for item in self._tree.get_children():
            self._tree.delete(item)

        if not self._active_panel:
            return
        cnt_tot, byt_tot = self._active_panel.get_table_data()
        total_cnt = sum(cnt_tot.values())
        total_byt = sum(byt_tot.values())
        if total_cnt == 0:
            return
        span_h = self._active_panel.get_span_hours()

        for ft in _PlotPanel.FRAME_TYPES:
            c = cnt_tot[ft]
            b = byt_tot[ft]
            if c == 0:
                continue
            pct_c = (c / total_cnt * 100) if total_cnt > 0 else 0
            pct_b = (b / total_byt * 100) if total_byt > 0 else 0

            c_str = f"{c / 1_000_000:.1f}M" if c >= 1_000_000 else (f"{c / 1_000:.0f}K" if c >= 1_000 else str(c))
            b_str = f"{b / 1_000_000:.1f}M" if b >= 1_000_000 else (f"{b / 1_000:.0f}K" if b >= 1_000 else str(b))
            avg_str = f"{b / c:.0f}" if c > 0 else "-"
            rate_str = f"{c / span_h:.1f}"

            self._tree.insert('', tk.END, values=(
                ft, c_str, b_str,
                f"{pct_c:.1f}", f"{pct_b:.1f}",
                avg_str, rate_str
            ))

        tc_str = (f"{total_cnt / 1_000_000:.1f}M" if total_cnt >= 1_000_000
                  else (f"{total_cnt / 1_000:.0f}K" if total_cnt >= 1_000 else str(total_cnt)))
        tb_str = (f"{total_byt / 1_000_000:.1f}M" if total_byt >= 1_000_000
                  else (f"{total_byt / 1_000:.0f}K" if total_byt >= 1_000 else str(total_byt)))
        self._tree.insert('', tk.END, values=(
            self._getTabStr('port_stat_tbl_total'), tc_str, tb_str, '100.0', '100.0', '-',
            f"{total_cnt / span_h:.1f}"
        ), tags=('total',))
        self._tree.tag_configure('total', font=('', 9, 'bold'))

    # -----------------------------------------------------------------
    # Menü
    # -----------------------------------------------------------------
    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        data_menu = Menu(menubar, tearoff=False)
        data_menu.add_command(label=self._getTabStr('del_all'), command=self._reset_PortStat)
        menubar.add_cascade(label=self._getTabStr('data'), menu=data_menu, underline=0)

    def _reset_PortStat(self, event=None):
        if not self._mh:
            return
        if messagebox.askokcancel(title=self._getTabStr('msg_box_delete_data'),
                                  message=self._getTabStr('msg_box_delete_data_msg'),
                                  parent=self):
            self._mh.PortStat_reset()
            for p in self._panels:
                p.reload()
            self._update_table()

    def destroy_plot(self):
        for p in self._panels:
            p.destroy()
        self._root_win.toplevel_manager.port_stat_win = None
        self.destroy()
