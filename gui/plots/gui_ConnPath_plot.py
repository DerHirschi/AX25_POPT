import tkinter as tk
from tkinter import ttk
from datetime import datetime

from cfg.logger_config import logger
#from matplotlib.backends._backend_tk import NavigationToolbar2Tk
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from gui import FigureCanvasTkAgg
from gui import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import networkx as nx
import random
from ax25.ax25InitPorts import PORT_HANDLER
# from fnc.cfg_fnc import convert_obj_to_dict
# from fnc.gui_fnc import generate_random_hex_color

# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
#import matplotlib

from cfg.constant import MH_BEACON_FILTER
from cfg.popt_config import POPT_CFG

#matplotlib.use('Agg')
# from matplotlib import pyplot as plt
from gui import plt


class ConnPathsPlot(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.wm_title("MH Routes")
        self._root_win = root_win
        #self._get_colorMap = lambda: COLOR_MAP.get(root_win.style_name, ('black', '#d9d9d9'))

        self.geometry(f"800x"
                      f"600+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._destroy_plot)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        #######################################################################
        self._seed = random.randint(1, 10000)
        self._path_data = {}
        self._node_key = []
        self._dest_key = []
        self._own_calls = []
        self._pos = None
        self._port = tk.IntVar(self, value=0)
        self._mh = PORT_HANDLER.get_MH()
        self._show_last_route_var = tk.BooleanVar(self, value=False)
        self._show_dest_var = tk.BooleanVar(self, value=True)
        self._filter_beacon_var = tk.BooleanVar(self, value=True)

        self._init_vars_fm_raw_data()
        #######################################################################
        #######################################################################
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X)
        refresh_btn = ttk.Button(btn_frame,
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
        self._style_var.set('Spring')
        style_opt_keys = [self._style_var.get()] +  list(self._style_opt.keys())
        style_option = ttk.OptionMenu(btn_frame,
                                     self._style_var,
                                     *style_opt_keys,
                                     command=self._refresh_btn
                                     )
        style_option.pack(side=tk.LEFT, padx=10)

        # node_option = [''] + list(self._node_key)
        # node_option.sort()
        self._node_option_var = tk.StringVar(self, '')
        """
        node_optionmen = tk.OptionMenu(btn_frame,
                                       self._node_option_var,
                                       *node_option,
                                       command=self._update_Graph
                                       )
        node_optionmen.pack(side=tk.LEFT, padx=10)
        """

        show_hops_chk = ttk.Checkbutton(btn_frame,
                                       variable=self._show_dest_var,
                                       text='Show Dest',
                                       command=self._update_Graph)
        show_hops_chk.pack(side=tk.LEFT, padx=10)
        filter_beacon = ttk.Checkbutton(btn_frame,
                                       variable=self._filter_beacon_var,
                                       text='Filter Beacons',
                                       command=self._update_Graph)
        filter_beacon.pack(side=tk.LEFT, padx=10)
        # Last seen
        self._last_seen_days_var = tk.IntVar(self, value=30)
        last_seen_days = ttk.Spinbox(btn_frame,
                                     textvariable=self._last_seen_days_var,
                                     from_=1,
                                     to=1095,
                                     increment=5,
                                     width=4,
                                     command=self._refresh_btn)
        ttk.Label(btn_frame, text='Last seen(Days):').pack(side=tk.LEFT, padx=10)
        last_seen_days.pack(side=tk.LEFT, padx=10)

        show_hops_chk = ttk.Checkbutton(btn_frame,
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
        ttk.Label(btn_frame, text='Port:').pack(side=tk.LEFT, padx=10)
        port.pack(side=tk.LEFT, padx=10)
        #############################################################################

        g_frame = ttk.Frame(self)
        g_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig, self._plot1 = plt.subplots()
        # self._plot2 = self._plot1.twinx()
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FigureCanvasTkAgg(self._fig, master=g_frame)
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die plots erstellen
        #fg, bg = self._get_colorMap()
        #toolbar1.configure(
        #    bg=bg
        #)
        #toolbar1._message_label.config(background=bg, fg=fg)
        toolbar1 = NavigationToolbar2Tk(self._canvas, g_frame)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, fill=tk.X)

        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        # self._init_chk_frame(right_frame)
        self._root_win.conn_Path_plot_win = self

        # self._init_stationInfo_vars(self._path_data)
        ##self._init_vars_fm_raw_data()
        self._g = nx.Graph()
        self._update_Graph()

    def _refresh_btn(self, event=None):
        self._pos = None
        self._new_seed()
        self._update_Graph()

    def _new_seed(self):
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
        self._node_key = []
        self._dest_key = []
        port = self._port.get()
        data = self._mh.get_mh_db_by_port(port)
        if not data:
            return
        self._own_calls = []
        # tmp = PORT_HANDLER.ax25_port_settings.get(port, None)
        tmp = POPT_CFG.get_stat_CFG_keys()
        if tmp:
            self._own_calls = list(tmp)
        last_route = self._show_last_route_var.get()
        for k in list(data.keys()):
            el = data[k]
            to_calls_routes = el.to_calls
            if last_route:
                r_k = el.own_call + ','.join(el.route) + el.last_dest
                self._path_data[r_k] = dict(
                    route=list(el.route),
                    dest_call=el.last_dest,
                    from_call=el.own_call,
                    lastUpdate=el.last_seen,
                )
                if not el.route:
                    self._node_key.append(k)
                self._dest_key.append(el.last_dest)
            else:
                for to_call in to_calls_routes.keys():
                    routes: dict = to_calls_routes[to_call]
                    for route in routes.keys():
                        if route:
                            route_list = route.split(',')
                            while '' in route_list:
                                route_list.remove('')
                        else:
                            route_list = []
                        last_rx = routes[route]
                        r_k = el.own_call + route + to_call
                        self._path_data[r_k] = dict(
                            route=route_list,
                            dest_call=to_call,
                            from_call=el.own_call,
                            lastUpdate=last_rx,
                        )
                        if not route_list:
                            self._node_key.append(k)
                        self._dest_key.append(to_call)

    def _update_Node_pos(self):
        if not self._path_data:
            return
        self._plot1.clear()
        self._g.clear()
        self._pos = None
        now = datetime.now()
        try:
            last_seen_var = int(self._last_seen_days_var.get())
        except ValueError:
            return
        add_dest = self._show_dest_var.get()
        filter_beacon_of_hope = self._filter_beacon_var.get()

        # is_markt = False

        # mark_edge_call = self._node_option_var.get()
        # show_all_routes = self._show_all_routes_var.get()

        for k in self._path_data.keys():
            # if show_all_routes or not mark_edge_call or (k == mark_edge_call and not show_all_routes):
            seen_time = self._path_data[k].get('lastUpdate', datetime.now())
            diff = (now - seen_time).days
            if diff <= last_seen_var:
                path = self._path_data[k].get('route', [])
                weight = 1
                if path:
                    call1 = self._path_data[k].get('from_call', '')
                    for station in path:
                        # edge_color = 'white'
                        # weight = len(route) + 1
                        if station in self._own_calls:
                            call1 = 'HOME'
                        self._add_edge(call1, station, '', weight)
                        call1 = station
                    if add_dest:
                        dest_call = self._path_data[k].get('dest_call', '')
                        if filter_beacon_of_hope:
                            if dest_call not in MH_BEACON_FILTER:
                                self._add_edge(call1, dest_call, '', 1)
                        else:
                            self._add_edge(call1, dest_call, '', 1)
                    self._add_edge(call1, 'HOME', '', weight)

                else:
                    from_call = self._path_data[k].get('from_call', '')
                    if add_dest:
                        dest_call = self._path_data[k].get('dest_call', '')
                        if filter_beacon_of_hope:
                            if dest_call not in MH_BEACON_FILTER:
                                self._add_edge(from_call, dest_call, '', 1)
                        else:
                            self._add_edge(from_call, dest_call, '', 1)
                    self._add_edge(from_call, 'HOME', '', 1)

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
            tmp = []
            i = -9
            for node in self._pos.keys():
                if node in MH_BEACON_FILTER:
                    pos = [i/10, 0.9]
                    while pos in tmp:
                        rand = random.uniform(-0.1, 0.1)
                        pos = [i/10 + rand, 0.9]
                    tmp.append(pos)
                    self._pos[node] = pos
                    self._g.add_node(node,
                                     pos=pos)
                    i += 1
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

    def _add_edge(self, e1: str, e2: str, col='', weight=1):
        if col:
            self._g.add_edge(e1, e2, color=col, weight=weight)
            return

        if e1 in self._node_key:
            edge_color = 'white'
        else:
            edge_color = 'red'
        if e1 in self._own_calls:
            e1 = 'HOME'
        if e2 in self._own_calls:
            e2 = 'HOME'
        self._g.add_edge(e1, e2, color=edge_color, weight=weight)

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
                if node_name in self._node_key:
                    node_color = 'black'
                else:
                    node_color = '#f70505'

                self._plot1.text(l_pos[0], l_pos[1] + 0.05,
                                 s=node_name,
                                 color='#ffffff',
                                 bbox=dict(
                                     facecolor=node_color,
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
