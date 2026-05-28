import tkinter as tk
from tkinter import ttk
import random
import networkx as nx
from gui import FigureCanvasTkAgg, NavigationToolbar2Tk
from gui import plt


class EnhancedConnPathsPlot(ttk.Frame):
    def __init__(self, root_frame, root_win):
        ttk.Frame.__init__(self, root_frame)
        self.pack(fill='both', expand=True)

        self._root_win = root_win
        self._mh = root_win.get_mh()

        self._seed = random.randint(1, 10000)
        self._g = nx.Graph()

        # Steuer-Variablen
        self._use_mh_var = tk.BooleanVar(self, True)          # Klassische MH-Routen
        self._use_netplan_var = tk.BooleanVar(self, True)     # MH._path_data (Pacman/Netplan)
        self._port_var = tk.IntVar(self, value=0)
        self._search_var = tk.StringVar(self, "")

        self._show_labels_var = tk.BooleanVar(self, True)
        self._style_var = tk.StringVar(self, 'Spring')

        self._pos = None

        self._build_gui()
        self._update_graph()

    def _build_gui(self):
        # ==================== Control Bar ====================
        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        ttk.Button(ctrl, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=5)

        ttk.Checkbutton(ctrl, text="MH-Routen", variable=self._use_mh_var,
                        command=self._refresh).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(ctrl, text="Netplan (_path_data)", variable=self._use_netplan_var,
                        command=self._refresh).pack(side=tk.LEFT, padx=8)

        ttk.Label(ctrl, text="Port:").pack(side=tk.LEFT, padx=(15, 2))
        ttk.Spinbox(ctrl, from_=0, to=9, width=6, textvariable=self._port_var,
                    command=self._refresh).pack(side=tk.LEFT, padx=5)

        ttk.Label(ctrl, text="Ziel:").pack(side=tk.LEFT, padx=(20, 2))
        ttk.Entry(ctrl, textvariable=self._search_var, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="Suchen", command=self._refresh).pack(side=tk.LEFT, padx=5)

        ttk.Separator(ctrl, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)

        styles = ['Spring', 'Circular', 'Kamada-Kawai', 'Spectral']
        ttk.OptionMenu(ctrl, self._style_var, 'Spring', *styles,
                      command=lambda _: self._refresh()).pack(side=tk.LEFT, padx=5)

        ttk.Checkbutton(ctrl, text="Labels", variable=self._show_labels_var,
                        command=self._refresh).pack(side=tk.LEFT, padx=10)

        # Plot Bereich
        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._fig, self._ax = plt.subplots(figsize=(6, 3))
        self._fig.set_dpi(85)
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FigureCanvasTkAgg(self._fig, master=plot_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self._canvas, plot_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)

    def _refresh(self):
        self._seed = random.randint(1, 10000)
        self._pos = None
        self._update_graph()

    def _update_graph(self):
        self._ax.clear()
        self._g.clear()

        search = self._search_var.get().strip().upper()

        # Daten laden
        if self._use_mh_var.get():
            self._load_mh_paths(search)

        if self._use_netplan_var.get():
            self._load_netplan_paths(search)

        if len(self._g.nodes) == 0:
            self._ax.text(0.5, 0.5, "Keine Pfade gefunden", ha='center', va='center', fontsize=14)
            self._canvas.draw()
            return

        layout_name = self._style_var.get()
        # Layout
        layout_funcs = {
            'Spring': nx.spring_layout,
            'Circular': nx.circular_layout,
            'Kamada-Kawai': nx.kamada_kawai_layout,
            'Spectral': nx.spectral_layout,
        }
        layout = layout_funcs.get(layout_name, nx.spring_layout)

        if layout_name == 'Spring':
            self._pos = layout(self._g, seed=self._seed)
        else:
            self._pos = layout(self._g)

        # Zeichnen
        edge_colors = [self._g[u][v].get('color', '#666666') for u, v in self._g.edges()]
        edge_widths = [self._g[u][v].get('weight', 0.5) for u, v in self._g.edges()]

        nx.draw_networkx(self._g, pos=self._pos, ax=self._ax,
                         node_color='#1e88e5',
                         node_size=230,
                         edge_color=edge_colors,
                         width=edge_widths,
                         with_labels=False,
                         edgecolors='white',
                         linewidths=0.5)

        if self._show_labels_var.get():
            self._draw_node_labels()

        #self._ax.set_title("Verbindungswege von HOME", fontsize=14, pad=15, color='white')
        self._ax.axis('off')
        self._fig.set_facecolor('#191621')
        self._canvas.draw()

    # ====================== Daten Laden ======================

    def _load_mh_paths(self, search=""):
        """ Klassische MH-Routen (aus gui_ConnPath_plot.py angepasst) """
        port = self._port_var.get()
        mh_db = self._mh.MH_db

        for p_id, stations in mh_db.items():
            if port != 0 and p_id != port:
                continue
            for call, entry in stations.items():
                if search and search not in call.upper():
                    continue

                route = getattr(entry, 'route', [])
                if route:
                    full_path = ['HOME'] + route
                    self._add_path(full_path, source='mh', port=p_id)

    def _load_netplan_paths(self, search=""):
        """ MH.get_netplan_data - Netplan/Pacman Daten """
        if not hasattr(self._mh, 'get_netplan_data'):
            return

        port = self._port_var.get()
        path_data = self._mh.get_netplan_data()

        for p_id, nodes_dict in path_data.items():
            if port != 0 and p_id != port:
                continue

            for target_node, path_list in nodes_dict.items():
                if search and search not in target_node.upper():
                    continue

                for path in path_list:          # path ist Liste der Hops
                    if isinstance(path, (list, tuple)):
                        full_path = ['HOME'] + list(path)
                        self._add_path(full_path, source='netplan', port=p_id)

    def _add_path(self, path: list, source: str = 'mh', port: int = 0):
        """ Pfad ins Graph einfügen mit Farbe """
        if len(path) < 2:
            return

        color = '#22c55e' if source == 'mh' else '#eab308'        # Grün = MH, Gelb = Netplan

        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]
            if a == b:
                continue

            # Vermeide doppelte Kanten mit unterschiedlichen Quellen
            if self._g.has_edge(a, b):
                existing_color = self._g[a][b].get('color')
                if existing_color != color:
                    self._g[a][b]['color'] = '#f97316'          # Orange bei beiden Quellen
                    self._g[a][b]['weight'] = 1.5
            else:
                self._g.add_edge(a, b, color=color, weight=1.8, source=source, port=port)

    def _draw_node_labels(self):
        for node, (x, y) in self._pos.items():
            color = '#111111' if node == 'HOME' else 'white'
            bbox_color = '#facc15' if node == 'HOME' else '#1f2937'

            self._ax.text(x, y + 0.035, node,
                          fontsize=12 if node == 'HOME' else 9,
                          color=color,
                          ha='center',
                          bbox=dict(facecolor=bbox_color,
                                    edgecolor='white',
                                    boxstyle='round,pad=0.4',
                                    alpha=0.9))


