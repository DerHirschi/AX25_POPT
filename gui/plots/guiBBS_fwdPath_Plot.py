import tkinter as tk
from tkinter import ttk
import random
from datetime import datetime
import networkx as nx
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
from ax25.ax25InitPorts import PORT_HANDLER
from fnc.gui_fnc import generate_random_hex_color
from fnc.str_fnc import convert_str_to_datetime

# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt

DEFAULT_COUNTRY_CFG = {
    'DEU': ((51.0, 9.6), 1.2, 'red'),
    'FRA': ((47.5, 2.1), 1.2, 'green'),
    'PRT': ((39.1, -8.3), 0.5, 'pink'),
    'NLD': ((52.4, 5.5), 0.3, 'orange'),
    'CH': ((46.7, 8), 0.3, 'yellow'),
    'AT': ((47.5, 14.5), 0.4, 'brown'),
    'GBR': ((53.8, -2.3), 0.7, 'purple'),
    'FIN': ((63.7, 27.1), 0.7, 'grey'),
}
DEFAULT_REGIO_DEU_CFG = {
    'SAA': (),
    'BAY': (),
}


class FwdGraph(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.wm_title("Forward Routes")
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
        self._db = PORT_HANDLER.get_database()
        self._user_DB = PORT_HANDLER.get_userDB()
        self._db_raw = self._db.bbs_get_fwdPaths()
        self._path_data = {}
        self._call_info_vars = {}
        self._call_color_map = {}
        self._weight_color_map = {}
        self._call_default_coordinates = {}
        self._country_chk_vars = {}
        for k in list(DEFAULT_COUNTRY_CFG.keys()):
            self._country_chk_vars[k] = tk.BooleanVar(self, value=True)
        self._node_dest_key_dict = {}
        # self._init_node_vars_fm_db()
        self._init_vars_fm_raw_data()
        self._seed = 0
        self._pos = None
        #######################################################################
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.TOP)
        refresh_btn = tk.Button(btn_frame,
                                text='Refresh',
                                command=self._refresh_btn
                                )
        refresh_btn.pack(side=tk.LEFT, padx=10)
        self._style_var = tk.StringVar(self, value='Position')
        self._style_opt = {
            'Circular': nx.circular_layout,
            'Planar': nx.planar_layout,
            'Random': nx.random_layout,
            'Spectral': nx.spectral_layout,
            'Spring': nx.spring_layout,
            'Shell': nx.shell_layout,
            'Position': None,
        }
        style_opt_keys = list(self._style_opt.keys())
        style_option = tk.OptionMenu(btn_frame,
                                     self._style_var,
                                     *style_opt_keys,
                                     command=self._refresh_btn
                                     )
        style_option.pack(side=tk.LEFT, padx=10)

        node_option = [''] + list(self._node_dest_key_dict)
        node_option.sort()
        self._node_option_var = tk.StringVar(self, '')
        node_optionmen = tk.OptionMenu(btn_frame,
                                       self._node_option_var,
                                       *node_option,
                                       command=self._update_Graph
                                       )
        node_optionmen.pack(side=tk.LEFT, padx=10)

        self._full_address_name_var = tk.BooleanVar(self, value=True)
        full_add_chk = tk.Checkbutton(btn_frame,
                                      variable=self._full_address_name_var,
                                      text='Address/Call',
                                      command=self._update_Graph)
        full_add_chk.pack(side=tk.LEFT, padx=10)

        self._show_hops_var = tk.BooleanVar(self, value=True)
        show_hops_chk = tk.Checkbutton(btn_frame,
                                       variable=self._show_hops_var,
                                       text='Hops',
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

        #############################################################################
        g_frame = tk.Frame(self)
        g_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._fig, self._plot1 = plt.subplots()
        self._plot2 = self._plot1.twinx()
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FigureCanvasTkAgg(self._fig, master=g_frame)
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, g_frame)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, fill=tk.X)

        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self._init_chk_frame(right_frame)
        self._root_win.fwd_Path_plot_win = self

        # self._init_stationInfo_vars(self._path_data)
        ##self._init_vars_fm_raw_data()
        self._g = nx.Graph()
        self._refresh_btn()

    def _init_chk_frame(self, root_frame):

        for k in list(DEFAULT_COUNTRY_CFG.keys()):
            tk.Checkbutton(root_frame,
                           variable=self._country_chk_vars[k],
                           text=k,
                           command=self._refresh_btn, ).pack(padx=10, pady=5, anchor='w')

    def _init_node_vars_fm_db(self):
        node_db_data = self._db.fwd_node_get()
        if not node_db_data:
            return

        for entry in node_db_data:
            if entry[0]:
                k = entry[0]
                country_id = entry[6]

                self._node_dest_key_dict[k] = (
                    entry[1],
                    entry[2],
                    entry[3],
                    entry[4],
                    entry[5],
                    entry[6],
                    entry[7],
                )
                cfg = DEFAULT_COUNTRY_CFG.get(country_id, None)
                if k not in self._call_color_map.keys():
                    if cfg:
                        self._call_color_map[k] = cfg[2]
                    else:
                        self._call_color_map[k] = 'black'
                        print(f'!! Color not Found in CFG: {country_id} {k}!!')
                if k not in self._call_default_coordinates.keys():
                    if cfg:
                        self._call_default_coordinates[k] = (cfg[0], cfg[1])
                    else:
                        # self._call_default_coordinates[call] = ()
                        print(f'!! Default Region Coordinates not Found in CFG: {country_id} {k}!!')
                if k not in self._call_info_vars.keys():
                    userDB_data = self._user_DB.get_location(k)
                    if userDB_data:
                        self._call_info_vars[k] = self._user_DB.get_location(k)

    def _init_vars_fm_raw_data(self):
        if not self._db_raw:
            return
        self._path_data = {}

        # print(db_raw)
        for el in self._db_raw:
            self._path_data[el[1]] = dict(
                path=el[0].split('>'),
                fromBBS=el[1],
                toBBS=el[2],
                hops=el[3],
                r1=el[4],
                r2=el[5],
                r3=el[6],
                r4=el[7],
                r5=el[8],
                r6=el[9],
                lastUpdate=convert_str_to_datetime(el[10]),
            )

        self._init_node_vars_fm_db()

    def _get_country_filter(self):
        country_chk = []
        for county in list(self._country_chk_vars.keys()):
            if self._country_chk_vars[county].get():
                country_chk.append(county)
        return country_chk

    def _get_country(self, bbs_call):
        entry = self._node_dest_key_dict.get(bbs_call, ())
        if not entry:
            return ''
        return entry[5]

    def _get_address(self, bbs_call):
        entry = self._node_dest_key_dict.get(bbs_call, ())
        if not entry:
            return bbs_call
        return entry[0]

    def _get_country_color(self, bbs_call, default_color='black'):
        return self._call_color_map.get(bbs_call, default_color)

    def _refresh_btn(self, event=None):
        self._pos = None
        self._new_seed_()
        self._update_Graph()

    def _new_seed_(self):
        self._seed = random.randint(1, 10000)

    def _update_Graph(self, event=None):
        self._update_Node_pos()
        if self._pos:
            self._update_node_label()
            self._update_legend()
            self._plot1.axis('off')
            self._fig.set_facecolor('#191621')
            self._canvas.draw()

    # https://stackoverflow.com/questions/19877666/add-legends-to-linecollection-plot - uses plotted data to define the color but here we already have colors defined, so just need a Line2D object.
    @staticmethod
    def _make_proxy(clr, **kwargs):
        return Line2D([0, 1], [0, 1], color=clr, **kwargs)

    def _update_legend(self):
        if self._show_hops_var.get():

            label = []
            color = []
            hops = list(self._weight_color_map.keys())
            hops.sort()
            for k in hops:
                label.append(
                    f"Hops: {k}"
                )
                color.append(self._weight_color_map[k])
            proxies = [self._make_proxy(clr, lw=5) for clr in color]
            self._plot2.legend(proxies, label)

        label = []
        color = []
        call_color_map = list(self._call_color_map.keys())
        call_color_map.sort()
        tmp = []
        for k in call_color_map:
            country = self._get_country(k)
            if country not in tmp:
                label.append(
                    f"{country}"
                )
                color.append(self._get_country_color(k))
                tmp.append(country)
        proxies = [self._make_proxy(clr, lw=5) for clr in color]
        self._plot1.legend(proxies, label, loc='upper left')

    def _update_Node_pos(self):
        if not self._path_data:
            return

        self._plot1.clear()
        self._plot2.clear()
        self._g.clear()
        now = datetime.now()
        country_filter = self._get_country_filter()
        try:
            last_seen_var = int(self._last_seen_days_var.get())
        except ValueError:
            return
        mark_edge_call = self._node_option_var.get()
        for k in self._path_data.keys():
            seen_time = self._path_data[k].get('lastUpdate', datetime.now())
            diff = (now - seen_time).days
            if diff <= last_seen_var:
                path = self._path_data[k].get('path', [])
                if self._show_hops_var.get():
                    hops = self._path_data[k].get('hops', 0)
                else:
                    hops = 0
                if len(path) > 1:
                    """
                    country_id = self._path_data[k].get('r5', '')
                    if any([country_id not in DEFAULT_COUNTRY_CFG.keys(),
                            country_id in country_filter]):
                    """
                    if hops:
                        if hops not in self._weight_color_map.keys():
                            self._weight_color_map[hops] = generate_random_hex_color(a=60)
                        edge_color = self._weight_color_map[hops]
                        weight = hops
                    else:
                        edge_color = 'white'
                        weight = 1
                    call_1 = path[0]
                    for call_2 in path[1:]:
                        # if call_2 != call_1:  # Don't show Loops
                        country_c_1 = self._get_country(call_1)
                        country_c_2 = self._get_country(call_2)
                        if country_c_1 not in DEFAULT_COUNTRY_CFG.keys():
                            country_filter.append(country_c_1)
                        if country_c_2 not in DEFAULT_COUNTRY_CFG.keys():
                            country_filter.append(country_c_2)
                        if all((country_c_1 in country_filter,
                                country_c_2 in country_filter)):

                            if mark_edge_call in [call_1, call_2]:
                                self._g.add_edge(call_1, call_2, color='red', weight=weight + 0.8)
                            else:
                                self._g.add_edge(call_1, call_2, color=edge_color, weight=weight)

                        call_1 = call_2

        # seed_val = random.randint(0, 10000)
        if not self._pos:
            layout = self._style_opt.get(self._style_var.get(), None)
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

            else:
                self._pos = self._pos_related_layout()
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

    def _pos_related_layout(self):
        """ with help of ChatGPT """
        # Füge Nodes mit Koordinaten hinzu
        tmp = []
        for node, coordinates in self._call_info_vars.items():
            if coordinates[0] or coordinates[1]:
                pos = coordinates[1], coordinates[0]
                if pos in tmp:
                    rand = random.uniform(-0.1, 0.1)
                    pos = coordinates[1] + rand, coordinates[0] + rand
                tmp.append(pos)
                self._g.add_node(node,
                                 pos=pos)  # Beachte die Reihenfolge von (lon, lat)

        # Set 'pos' attribute for nodes with unknown coordinates
        for node in self._g.nodes:
            if 'pos' not in self._g.nodes[node]:
                default_cfg = self._call_default_coordinates.get(node, ())
                neighbors = list(self._g.neighbors(node))
                known_neighbors = [n for n in neighbors if 'pos' in self._g.nodes[n]]
                known_neighbors_country = [self._get_country(n) for n in neighbors if 'pos' in self._g.nodes[n]]
                own_country = self._get_country(node)
                if own_country in known_neighbors_country:

                    ran_dif = 0.5
                    if known_neighbors:
                        avg_lon = sum(self._g.nodes[n]['pos'][0] for n in known_neighbors) / len(known_neighbors)
                        avg_lat = sum(self._g.nodes[n]['pos'][1] for n in known_neighbors) / len(known_neighbors)
                        # Füge eine kleine zufällige Verschiebung hinzu
                        rand_lon = random.uniform(-ran_dif, ran_dif)
                        rand_lat = random.uniform(-ran_dif, ran_dif)
                        self._g.nodes[node]['pos'] = (avg_lon + rand_lon, avg_lat + rand_lat)
                else:
                    if default_cfg:
                        avg_lat = default_cfg[0][0]
                        avg_lon = default_cfg[0][1]
                        ran_dif = default_cfg[1]
                        rand_lon = random.uniform(-ran_dif, ran_dif)
                        rand_lat = random.uniform(-ran_dif, ran_dif)
                        self._g.nodes[node]['pos'] = (avg_lon + rand_lon, avg_lat + rand_lat)
                    else:
                        ran_dif = 2.3
                        rand_lon = random.uniform(-ran_dif, ran_dif)
                        rand_lat = random.uniform(-ran_dif, ran_dif)
                        self._g.nodes[node]['pos'] = (rand_lon, rand_lat)

        return nx.get_node_attributes(self._g, 'pos')

    def _update_node_label(self):
        if not self._pos:
            return
        pos = self._pos
        tmp = []
        full_add = self._full_address_name_var.get()
        for k in pos.keys():
            if k not in tmp:
                tmp.append(k)
                l_pos = pos[k]
                node_color = self._get_country_color(k, 'black')

                if full_add:
                    node_name = self._get_address(k)
                else:
                    node_name = k

                self._plot1.text(l_pos[0], l_pos[1] + 0.05,
                                 s=node_name,
                                 color='#ffffff',
                                 bbox=dict(facecolor=node_color,
                                           edgecolor='#ffffff',
                                           boxstyle='round',
                                           alpha=0.5),
                                 horizontalalignment='center',
                                 )

    def _destroy_plot(self):
        self._plot1.clear()
        self._plot2.clear()
        self._g.clear()
        self._fig.clear()
        plt.close()
        self._canvas.get_tk_widget().destroy()
        self._root_win.fwd_Path_plot_win = None
        self.destroy()
