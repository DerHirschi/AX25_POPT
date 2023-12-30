import tkinter as tk
import random

import networkx as nx
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
import matplotlib

from ax25.ax25InitPorts import PORT_HANDLER

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
        # self._db_raw = self._db.bbs_get_fwdPaths()
        self._path_data = []
        self._call_info_vars = {}
        self._call_color_map = {}
        self._call_default_coordinates = {}
        self._node_dest_key_dict = {}
        self._init_node_vars_fm_db()
        #######################################################################
        btn_frame = tk.Frame(self)
        btn_frame.pack()
        refresh_btn = tk.Button(btn_frame,
                                text='Refresh',
                                command=self._update_Graph
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
                                     command=self._update_Graph
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

        #############################################################################
        g_frame = tk.Frame(self)
        g_frame.pack(expand=True, fill=tk.BOTH)

        self._fig, self._plot1 = plt.subplots()
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FigureCanvasTkAgg(self._fig, master=g_frame)
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, self)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, fill=tk.X)

        self._root_win.fwd_Path_plot_win = self

        # self._init_stationInfo_vars(self._path_data)
        self._init_vars_fm_raw_data()
        self._g = nx.Graph()
        self._update_Graph()

    def _init_node_vars_fm_db(self):
        node_db_data = self._db.fwd_node_get()
        if not node_db_data:
            return
        for entry in node_db_data:
            if entry[0]:
                k = entry[0]
                self._node_dest_key_dict[k] = (
                    entry[1],
                    entry[2],
                    entry[3],
                    entry[4],
                    entry[5],
                    entry[6],
                    entry[7],
                )
                country_id = entry[6]
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
        db_raw = self._db.bbs_get_fwdPaths()
        self._path_data = [x[0].split('>') for x in db_raw]

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

    def _update_Graph(self, event=None):
        pos = self._update_Node_pos()
        if pos:
            self._update_node_label(pos)
            self._plot1.axis('off')
            self._fig.set_facecolor('#191621')
            self._canvas.draw()

    def _update_Node_pos(self):
        if not self._path_data:
            return
        if not self._path_data[0]:
            return
        self._plot1.clear()
        self._g.clear()

        mark_edge_call = self._node_option_var.get()
        for path in self._path_data:
            if len(path) > 1:
                call_1 = path[0]
                for call_2 in path[1:]:
                    # if call_2 != call_1:  # Don't show Loops
                    if mark_edge_call in [call_1, call_2]:
                        self._g.add_edge(call_1, call_2, color='red', weight=2)
                    else:
                        self._g.add_edge(call_1, call_2, color='white', weight=1.5)

                    call_1 = call_2

        # seed_val = random.randint(0, 10000)

        layout = self._style_opt.get(self._style_var.get(), None)
        if layout:
            pos = layout(self._g)
        else:
            pos = self._pos_related_layout()

        colors = nx.get_edge_attributes(self._g, 'color').values()
        weights = nx.get_edge_attributes(self._g, 'weight').values()

        nx.draw_networkx(self._g, pos=pos, ax=self._plot1,
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
        return pos

    def _pos_related_layout(self):
        # Füge Nodes mit Koordinaten hinzu
        for node, coordinates in self._call_info_vars.items():
            if coordinates[0] or coordinates[1]:
                self._g.add_node(node,
                                 pos=(coordinates[1], coordinates[0]))  # Beachte die Reihenfolge von (lon, lat)

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

    def _update_node_label(self, pos):
        if not pos:
            return
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
        plt.close()
        self._canvas.get_tk_widget().destroy()
        self._root_win.fwd_Path_plot_win = None
        self.destroy()
