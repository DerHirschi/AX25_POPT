import tkinter as tk
from tkinter import ttk
from datetime import datetime

from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random
from ax25.ax25InitPorts import PORT_HANDLER

# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
import matplotlib

from fnc.gui_fnc import generate_random_hex_color

matplotlib.use('Agg')
from matplotlib import pyplot as plt


class ConnPathsPlot(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.wm_title("MH Routes")
        self._root_win = root_win
        self.geometry(f"800x"
                      f"600+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_plot)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        #######################################################################
        self._seed = random.randint(1, 10000)
        self._path_data = {}
        self._node_key = {}
        self._pos = None
        self._port = tk.IntVar(self, value=0)
        self._mh = PORT_HANDLER.get_MH()
        self._show_last_route_var = tk.BooleanVar(self, value=False)

        self._init_vars_fm_raw_data()
        #######################################################################
        #######################################################################
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.TOP)
        refresh_btn = tk.Button(btn_frame,
                                text='Refresh',
                                command=self._refresh_btn
                                )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        self._style_var = tk.StringVar(self, value='Spring')
        self._style_opt = {
            'Circular': nx.circular_layout,
            'Planar': nx.planar_layout,
            'Random': nx.random_layout,
            'Spectral': nx.spectral_layout,
            'Spring': nx.spring_layout,
            'Shell': nx.shell_layout,
            # 'Position': None,
        }
        style_opt_keys = list(self._style_opt.keys())
        style_option = tk.OptionMenu(btn_frame,
                                     self._style_var,
                                     *style_opt_keys,
                                     command=self._refresh_btn
                                     )
        style_option.pack(side=tk.LEFT, padx=10)

        node_option = [''] + list(self._node_key)
        node_option.sort()
        self._node_option_var = tk.StringVar(self, '')
        node_optionmen = tk.OptionMenu(btn_frame,
                                       self._node_option_var,
                                       *node_option,
                                       command=self._update_Graph
                                       )
        node_optionmen.pack(side=tk.LEFT, padx=10)

        self._show_all_routes_var = tk.BooleanVar(self, value=True)
        show_hops_chk = tk.Checkbutton(btn_frame,
                                       variable=self._show_all_routes_var,
                                       text='All Routes',
                                       command=self._update_Graph)
        show_hops_chk.pack(side=tk.LEFT, padx=10)
        # Last seen
        self._last_seen_days_var = tk.IntVar(self, value=30)
        last_seen_days = ttk.Spinbox(btn_frame,
                                     textvariable=self._last_seen_days_var,
                                     from_=1,
                                     to=1095,
                                     increment=5,
                                     width=4,
                                     command=self._refresh_btn)
        tk.Label(btn_frame, text='Last seen(Days):').pack(side=tk.LEFT, padx=10)
        last_seen_days.pack(side=tk.LEFT, padx=10)

        show_hops_chk = tk.Checkbutton(btn_frame,
                                       variable=self._show_last_route_var,
                                       text='last Route',
                                       command=self._update_Graph)
        show_hops_chk.pack(side=tk.LEFT, padx=10)

        port = ttk.Spinbox(btn_frame,
                           textvariable=self._port,
                           from_=0,
                           to=15,
                           increment=1,
                           width=4,
                           command=self._update_Graph)
        tk.Label(btn_frame, text='Port:').pack(side=tk.LEFT, padx=10)
        port.pack(side=tk.LEFT, padx=10)
        #############################################################################

        g_frame = tk.Frame(self)
        g_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig, self._plot1 = plt.subplots()
        # self._plot2 = self._plot1.twinx()
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FigureCanvasTkAgg(self._fig, master=g_frame)
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, g_frame)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, fill=tk.X)

        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        # self._init_chk_frame(right_frame)
        self._root_win.conn_Path_plot_win = self

        # self._init_stationInfo_vars(self._path_data)
        ##self._init_vars_fm_raw_data()
        self._g = nx.Graph()
        self._update_Graph()

    def _refresh_btn(self, event=None):
        self._pos = None
        self._new_seed_()
        self._update_Graph()

    def _new_seed_(self):
        self._seed = random.randint(1, 10000)

    def _update_Graph(self, event=None):
        self._init_vars_fm_raw_data()
        self._update_Node_pos()
        if self._pos:
            self._update_node_label()
            # self._update_legend()
            self._plot1.axis('off')
            self._fig.set_facecolor('#191621')
            self._canvas.draw()

    def _init_vars_fm_raw_data(self):
        if not self._mh:
            return
        self._path_data = {}
        data = self._mh.get_mh_db_by_port(self._port.get())
        last_route = self._show_last_route_var.get()
        for k in data.keys():
            el = data[k]
            if last_route:
                self._path_data[el.own_call] = dict(
                    route=[el.route],
                    lastUpdate=el.last_seen,
                )
            else:
                self._path_data[el.own_call] = dict(
                    route=el.all_routes,
                    lastUpdate=el.last_seen,
                )
        self._node_key = list(data.keys())
        print(self._path_data)

    def _update_Node_pos(self):
        if not self._path_data:
            return
        self._plot1.clear()
        self._g.clear()
        self._pos = None
        now = datetime.now()
        # country_filter = self._get_country_filter()
        try:
            last_seen_var = int(self._last_seen_days_var.get())
        except ValueError:
            return
        is_markt = False
        mark_edge_call = self._node_option_var.get()
        show_all_routes = self._show_all_routes_var.get()
        for k in self._path_data.keys():
            if show_all_routes or not mark_edge_call or (k == mark_edge_call and not show_all_routes):
                seen_time = self._path_data[k].get('lastUpdate', datetime.now())
                diff = (now - seen_time).days
                if diff <= last_seen_var:
                    path = self._path_data[k].get('route', [])
                    edge_color = 'white'
                    weight = 1
                    if path:
                        for route in path:
                            weight = len(route) + 1
                            route.reverse()
                            call1 = 'HOME'
                            if k in mark_edge_call:
                                if is_markt:
                                    edge_color = generate_random_hex_color(a=60)
                                else:
                                    edge_color = 'red'
                                    is_markt = True

                            for station in route:
                                self._g.add_edge(call1, station, color=edge_color, weight=weight)
                                call1 = station
                            self._g.add_edge(call1, k, color=edge_color, weight=weight)

                    else:
                        self._g.add_edge('HOME', k, color=edge_color, weight=weight)
        # seed_val = random.randint(0, 10000)
        if not self._pos:
            layout = self._style_opt.get(self._style_var.get(), None)
            # layout = nx.spring_layout
            if layout:
                if layout.__name__ == nx.spring_layout.__name__:
                    self._pos = layout(self._g, seed=self._seed)
                else:
                    try:
                        self._pos = layout(self._g)
                    except nx.NetworkXException as e:
                        print(e)
                        self._pos = None
                        return
            """
            else:
                self._pos = self._pos_related_layout()
            """
        if self._pos:
            colors = nx.get_edge_attributes(self._g, 'color').values()
            weights = nx.get_edge_attributes(self._g, 'weight').values()

            nx.draw_networkx(self._g, pos=self._pos, ax=self._plot1,
                             with_labels=False, node_shape='o',
                             node_size=200,
                             node_color='#386de0',
                             edge_color=colors,
                             width=list(weights),
                             # alpha=0.7
                             )
            """
            nx.draw_networkx_labels(self._g,
                                    pos=pos,
                                    ax=self._plot1,
                                    font_size=17)
            """

    def _update_node_label(self):
        if not self._pos:
            return
        pos = self._pos
        tmp = []
        # full_add = self._full_address_name_var.get()
        for k in pos.keys():
            if k not in tmp:
                tmp.append(k)
                l_pos = pos[k]
                node_name = k

                self._plot1.text(l_pos[0], l_pos[1] + 0.05,
                                 s=node_name,
                                 color='#ffffff',
                                 bbox=dict(
                                     # facecolor=node_color,
                                     edgecolor='#ffffff',
                                     boxstyle='round',
                                     alpha=0.5),
                                 horizontalalignment='center',
                                 )

    def _destroy_plot(self):
        self._plot1.clear()
        self._g.clear()
        self._fig.clear()
        plt.close()
        self._canvas.get_tk_widget().destroy()
        self._root_win.conn_Path_plot_win = None
        self.destroy()
