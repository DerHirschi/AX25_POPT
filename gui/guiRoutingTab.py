"""With help of Grok3-AI"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import networkx as nx
from gui import plt as plt
from gui import FigureCanvasTkAgg, NavigationToolbar2Tk
from cfg.constant import COLOR_MAP
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab

class RoutingTableWindow:
    """
    Toplevel-Fenster zur Anzeige der RoutingTable-Daten in einer sortierbaren Treeview
    mit farblicher Hervorhebung, einem Detailfenster und einem NetworkX-Graphen.
    """
    def __init__(self, parent, routing_table):
        self._root_win = parent
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._routing_table = routing_table
        self._window = tk.Toplevel(parent.main_win)
        self._window.title("Routing Table Viewer")
        self._window.geometry(f"{1200}x{600}+{parent.main_win.winfo_x()}+{parent.main_win.winfo_y()}")
        self._window.protocol("WM_DELETE_WINDOW", self._destroy_win)
        self._get_colorMap = lambda: COLOR_MAP.get(parent.style_name, ('#000000', '#d9d9d9'))
        fg, bg = self._get_colorMap()

        # Farbkonfiguration für Qualität und RTT
        self._quality_colors = {
            'high': ('#18cf00', 150),   # Grün für quality > 150
            'medium': ('#dec104', 50),  # Gelb für 50 <= quality <= 150
            'low': ('#e30e0e', 1),      # Rot für quality < 50, aber > 0
            'zero': (bg, 0)             # Dynamischer Hintergrund für quality = 0
        }
        self._rtt_colors = {
            'high': ('#18cf00', 1000),    # Grün für RTT ≤ 1000 (≤ 10 s)
            'medium': ('#dec104', 5000),  # Gelb für RTT 1001–5000 (10–50 s)
            'low': ('#e30e0e', 60000),    # Rot für RTT 5001–59999 (50–599,99 s)
            'invalid': ('#808080', 0)     # Grau für RTT = 0 oder 60000
        }

        # Hauptbereich: PanedWindow für Treeview (links) und Details+Graph (rechts)
        self._paned_window = ttk.PanedWindow(self._window, orient=tk.HORIZONTAL)
        self._paned_window.pack(fill=tk.BOTH, expand=True)

        # Linker Bereich: Treeview
        self._tree_frame = ttk.Frame(self._paned_window)
        self._paned_window.add(self._tree_frame, weight=2)
        self._tree = ttk.Treeview(self._tree_frame, show='headings')
        tree_scroll_y = ttk.Scrollbar(self._tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        tree_scroll_x = ttk.Scrollbar(self._tree_frame, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        # Spalten definieren
        self._columns = [
            ('callsign', self._getTabStr('Callsign'), 100),
            ('alias', self._getTabStr('Alias'), 80),
            ('type', self._getTabStr('Type'), 100),
            ('protocol', self._getTabStr('Protocol'), 80),
            ('ports', self._getTabStr('Ports'), 60),
            ('quality', self._getTabStr('Quality'), 80),
            ('rtt', self._getTabStr('RTT'), 60),
            ('hop_count', self._getTabStr('Hops'), 60),
            ('timestamp', self._getTabStr('Timestamp'), 150)
        ]
        self._tree['columns'] = [col[0] for col in self._columns]
        for col_id, col_name, width in self._columns:
            self._tree.heading(col_id, text=col_name, command=lambda c=col_id: self.sort_column(c))
            self._tree.column(col_id, width=width, anchor='w')

        # Farb-Tags für Qualität und RTT
        for level, (color, _) in self._quality_colors.items():
            self._tree.tag_configure(f'quality_{level}', background=color)
        for level, (color, _) in self._rtt_colors.items():
            self._tree.tag_configure(f'rtt_{level}', background=color)

        # Layout Treeview
        self._tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        self._tree_frame.grid_rowconfigure(0, weight=1)
        self._tree_frame.grid_columnconfigure(0, weight=1)

        # Port-Filter-Combobox
        self.add_filter_controls()

        # Rechter Bereich: Vertikales PanedWindow für Details (oben) und Graph (unten)
        self._right_paned = ttk.PanedWindow(self._paned_window, orient=tk.VERTICAL)
        self._paned_window.add(self._right_paned, weight=1)

        # Detailfenster (oben)
        self._detail_frame = ttk.Frame(self._right_paned)
        self._right_paned.add(self._detail_frame, weight=1)
        self._detail_text = tk.Text(self._detail_frame, wrap=tk.WORD, height=10, width=50)
        detail_scroll = ttk.Scrollbar(self._detail_frame, orient=tk.VERTICAL, command=self._detail_text.yview)
        self._detail_text.configure(yscrollcommand=detail_scroll.set)
        self._detail_text.grid(row=0, column=0, sticky='nsew')
        detail_scroll.grid(row=0, column=1, sticky='ns')
        self._detail_frame.grid_rowconfigure(0, weight=1)
        self._detail_frame.grid_columnconfigure(0, weight=1)

        # Graphfenster (unten)
        self._graph_frame = ttk.Frame(self._right_paned)
        self._graph_frame.configure(style='Black.TFrame')
        self._right_paned.add(self._graph_frame, weight=2)
        self._fig, self._ax = plt.subplots(figsize=(6, 4))
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._graph_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self._canvas.get_tk_widget().configure(bg='black')

        # Navigation Toolbar
        self._toolbar_frame = ttk.Frame(self._graph_frame)
        self._toolbar_frame.pack(fill=tk.X)
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._toolbar_frame)
        self._toolbar.update()

        # ttk-Style für schwarzen Frame-Hintergrund
        style = ttk.Style()
        style.configure('Black.TFrame', background='black')

        # Bindings
        self._tree.bind('<<TreeviewSelect>>', self.show_details)

        # Sortiervariablen
        self._sort_column_id = 'timestamp'
        self._sort_reverse = True  # Standard: Neueste zuerst

        # Zoom-Variablen
        self._initial_xlim = None
        self._initial_ylim = None

        self._root_win.routingTab_win = self
        # Initiale Daten laden
        self.update_treeview()

    def add_filter_controls(self):
        """Fügt eine Port-Filter-Combobox hinzu."""
        filter_frame = ttk.Frame(self._tree_frame)
        filter_frame.grid(row=2, column=0, pady=5, sticky='ew')
        ttk.Label(filter_frame, text=self._getTabStr("Port")).pack(side=tk.LEFT, padx=5)
        port_var = tk.StringVar()
        port_combo = ttk.Combobox(filter_frame, textvariable=port_var, values=['All'] + list(set(
            port for node in dict(self._routing_table.table['nodes']).values() for port in node['ports']
        )), width=10)
        port_combo.pack(side=tk.LEFT)
        port_combo.set('All')
        port_combo.bind('<<ComboboxSelected>>', lambda e: self.update_treeview(
            port_id=int(port_var.get()) if port_var.get() != 'All' else None))

    def _get_color_tag(self, value, color_map, default='low'):
        """Bestimmt den Farb-Tag basierend auf dem Wert."""
        if value == 60000:  # Spezielle Behandlung für RTT = 60000 (nicht verfügbar)
            return 'invalid'
        for level, (color, threshold) in color_map.items():
            if value <= threshold:
                return level
        return default

    def _to_networkx(self, port_id=None, selected_iid=None):
        """Erstellt einen NetworkX-Graphen aus der RoutingTable."""
        G = nx.DiGraph()
        table = self._routing_table.filter_by_port(port_id) if port_id is not None else dict(self._routing_table.table)

        # Knoten hinzufügen
        for call in table['nodes']:
            G.add_node(call)

        # Kanten hinzufügen (nur wenn from_call vorhanden)
        edge_styles = {}
        for (from_call, to_call), entries in table['connections'].items():
            if not from_call:  # Überspringe Verbindungen ohne from_call
                continue
            # Neueste Qualität für die Kante verwenden
            entry = entries[-1]  # Neuester Eintrag
            quality = entry['metrics'].get('quality', 255 - entry['metrics'].get('hop_counter', 0))
            edge_color = self._quality_colors[self._get_color_tag(quality, self._quality_colors, 'zero')][0]
            G.add_edge(from_call, to_call, quality=quality, color=edge_color, width=1, style='solid')
            edge_styles[(from_call, to_call)] = [(entry['timestamp'], 'solid')]

            # Ältere Einträge mit gestrichelter Linie
            for older_entry in entries[:-1]:
                edge_styles[(from_call, to_call)].append((older_entry['timestamp'], 'dashed'))

        # Highlighting für ausgewählte Route
        if selected_iid:
            if selected_iid.startswith('node_'):
                call = selected_iid[len('node_'):]
                for u, v, data in G.edges(data=True):
                    if u == call or v == call:
                        data['width'] = 3
                        data['color'] = 'cyan'
                        edge_styles[(u, v)][-1] = (edge_styles[(u, v)][-1][0], 'solid')
            else:
                from_call, to_call, idx = selected_iid[len('conn_'):].rsplit('_', 2)
                idx = int(idx)
                entries = table['connections'].get((from_call, to_call), [])
                if idx < len(entries) and from_call:  # Nur wenn from_call vorhanden
                    G.edges[from_call, to_call]['width'] = 3
                    G.edges[from_call, to_call]['color'] = 'cyan'
                    edge_styles[(from_call, to_call)][idx] = (entries[idx]['timestamp'], 'solid')

        return G, edge_styles

    def _draw_graph(self, port_id=None, selected_iid=None):
        """Zeichnet den NetworkX-Graphen mit festen Positionen und dunklem Hintergrund."""
        self._ax.clear()
        G, edge_styles = self._to_networkx(port_id, selected_iid)

        # Feste Positionen speichern oder wiederverwenden
        if not hasattr(self, '_pos') or len(self._pos) != len(G.nodes()):
            self._pos = nx.spring_layout(G)
        pos = self._pos

        # Dunkler Hintergrund und Transparenz
        self._fig.set_facecolor('#000000')
        self._fig.patch.set_facecolor('#000000')
        self._fig.patch.set_alpha(0)  # Figure transparent machen
        self._ax.set_facecolor('#000000')
        self._canvas.get_tk_widget().configure(bg='black')
        self._graph_frame.configure(style='Black.TFrame')

        # Axes-Position maximieren und Margen entfernen
        self._fig.tight_layout(pad=0)
        self._ax.set_position([0, 0, 1, 1])

        # Zeichne den Graphen
        edge_colors = [data['color'] for _, _, data in G.edges(data=True)]
        edge_widths = [data['width'] for _, _, data in G.edges(data=True)]
        edge_styles_list = [edge_styles.get((u, v), [('latest', 'solid')])[-1][1] for u, v in G.edges()]
        nx.draw(G, pos, ax=self._ax, with_labels=True, node_color='blue', node_size=500,
                font_size=8, font_color='white', edge_color=edge_colors, width=edge_widths,
                style=edge_styles_list, arrows=True)

        # Speichere initiale Achsengrenzen für Reset
        if self._initial_xlim is None or self._initial_ylim is None:
            x_coords = [pos[node][0] for node in G.nodes()]
            y_coords = [pos[node][1] for node in G.nodes()]
            if x_coords and y_coords:
                margin = 0.1  # 10% Rand
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                x_range = x_max - x_min
                y_range = y_max - y_min
                self._initial_xlim = (x_min - x_range * margin, x_max + x_range * margin)
                self._initial_ylim = (y_min - y_range * margin, y_max + y_range * margin)
                self._ax.set_xlim(self._initial_xlim)
                self._ax.set_ylim(self._initial_ylim)

        # Force Canvas-Update
        self._canvas.draw()
        self._canvas.draw_idle()
        self._canvas.flush_events()
        self._canvas.get_tk_widget().update()
        self._window.update_idletasks()

    def update_treeview(self, port_id=None):
        """Aktualisiert die Treeview und den Graphen mit Daten aus der RoutingTable."""
        # Aktuelle Auswahl speichern
        try:
            selected_iid = self._tree.selection()[0] if self._tree.selection() else None
        except tk.TclError:
            return

        # Bestehende Einträge löschen
        for item in self._tree.get_children():
            self._tree.delete(item)

        # Daten filtern (falls port_id angegeben)
        table = self._routing_table.filter_by_port(port_id) if port_id is not None else dict(self._routing_table.table)

        # Knoten einfügen
        for call, node in dict(table['nodes']).items():
            ports = ','.join(map(str, node['ports'].keys()))
            timestamp = datetime.fromtimestamp(node['last_seen']).strftime('%Y-%m-%d %H:%M:%S')
            quality = 0
            rtt = 0
            hop_count = 0
            for (from_c, to_c), entries in dict(table['connections']).items():
                if to_c == call:
                    for entry in entries:
                        q = entry['metrics'].get('quality', 0)
                        r = entry['metrics'].get('rtt', 0)
                        h = entry['metrics'].get('hop_counter', 0)
                        if q > quality:
                            quality = q
                        if r > 0 and (rtt == 0 or r < rtt):
                            rtt = r
                        if h > hop_count:
                            hop_count = h
            rtt_tag = f'rtt_{self._get_color_tag(rtt, self._rtt_colors, "invalid")}'
            quality_tag = f'quality_{self._get_color_tag(quality, self._quality_colors, "zero")}' if quality > 0 else rtt_tag
            tags = [quality_tag, rtt_tag]
            self._tree.insert('', 'end', iid=f'node_{call}', values=(
                call, node['alias'], '', node['protocol'], ports,
                quality, rtt, hop_count, timestamp
            ), tags=tags)

        # Verbindungen einfügen
        rTabConn = dict(table.get('connections', {}))
        for (from_call, to_call), entries in rTabConn.items():
            for i, entry in enumerate(entries):
                quality = entry['metrics'].get('quality', 255 - entry['metrics'].get('hop_counter', 0))
                rtt = entry['metrics'].get('rtt', 0)
                hop_count = entry['metrics'].get('hop_counter', 0)
                timestamp = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                ports = str(entry['metrics']['port_id'])
                rtt_tag = f'rtt_{self._get_color_tag(rtt, self._rtt_colors, "invalid")}'
                quality_tag = f'quality_{self._get_color_tag(quality, self._quality_colors, "zero")}' if quality > 0 else rtt_tag
                tags = [quality_tag, rtt_tag]
                callsign = f"{from_call}->{to_call}" if from_call else to_call
                self._tree.insert('', 'end', iid=f'conn_{from_call}_{to_call}_{i}', values=(
                    callsign, '', entry['type'], '', ports,
                    quality, rtt, hop_count, timestamp
                ), tags=tags)

        # Sortieren
        self.sort_column(self._sort_column_id, self._sort_reverse)

        # Auswahl wiederherstellen
        if selected_iid and selected_iid in self._tree.get_children():
            self._tree.selection_set(selected_iid)
            self._tree.focus(selected_iid)
            self.show_details(None)

        # Graph aktualisieren
        self._draw_graph(port_id, selected_iid)

    def sort_column(self, col, reverse=None):
        """Sortiert die Treeview nach der angegebenen Spalte."""
        if reverse is None:
            reverse = not self._sort_reverse if col == self._sort_column_id else False
        self._sort_column_id = col
        self._sort_reverse = reverse

        items = [(self._tree.set(item, col), item) for item in self._tree.get_children()]
        if col in ['quality', 'rtt', 'hop_count']:
            items.sort(key=lambda x: float(x[0]) if x[0] else 0, reverse=reverse)
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=reverse)

        for index, (value, item) in enumerate(items):
            self._tree.move(item, '', index)

        for col_id, _, _ in self._columns:
            self._tree.heading(col_id, text=self._columns[[c[0] for c in self._columns].index(col_id)][1])

    def show_details(self, event):
        """Zeigt erweiterte Informationen und highlightet die Route im Graphen."""
        self._detail_text.delete(1.0, tk.END)
        selected = self._tree.selection()
        if not selected:
            return
        item_id = selected[0]
        values = self._tree.item(item_id, 'values')
        callsign = values[0]
        details = ''
        if item_id.startswith('node_'):
            call = item_id[len('node_'):]
            node = dict(self._routing_table.table['nodes']).get(call, {})
            details = f"Node: {call}\n\n"
            for key, value in node.items():
                if key == 'info_history':
                    details += f"{key}: {len(value)} entries\n"
                    for i, frame in enumerate(value[:5], 1):
                        details += f"  Frame {i}: {frame}\n"
                elif key == 'ports':
                    details += f"{key}:\n"
                    for port_id, info in value.items():
                        details += f"  Port {port_id}: {info}\n"
                else:
                    details += f"{key}: {value}\n"
        else:
            from_call, to_call, idx = item_id[len('conn_'):].rsplit('_', 2)
            idx = int(idx)
            entries = dict(self._routing_table.table['connections']).get((from_call, to_call), [])
            if idx < len(entries):
                entry = entries[idx]
                details = f"Connection: {from_call} -> {to_call}\n\n"
                details += f"Type: {entry['type']}\n"
                details += "Metrics:\n"
                for key, value in entry['metrics'].items():
                    details += f"  {key}: {value}\n"
                details += f"Timestamp: {datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"

        self._detail_text.insert(tk.END, details)
        self._draw_graph(selected_iid=item_id)

    def _refresh(self):
        """Aktualisiert die Treeview und den Graphen mit neuen Daten."""
        self.update_treeview()

    def _destroy_win(self):
        plt.close(self._fig)
        self._window.destroy()

    def close(self):
        self._root_win.routingTab_win = None
        self._destroy_win()

    def tasker(self):
        self._refresh()