"""
TODO:
    - Port 0 (Monitor) MH-Plot
"""

import tkinter as tk
from tkinter import ttk
# from matplotlib.backends._backend_tk import NavigationToolbar2Tk
#import matplotlib as mpl
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FIGc
from gui import FigureCanvasTkAgg as FIGc
import networkx as nx
import random

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab

#mpl.use('Agg')
#from matplotlib import pyplot as plt2
from gui import plt

class LiveConnPath(ttk.Frame):
    def __init__(self, tabctl):
        ttk.Frame.__init__(self, tabctl)
        self.pack(fill=tk.BOTH, expand=True)
        # self._root_win = root_win
        self._lang = POPT_CFG.get_guiCFG_language()
        self._pos = None
        self._channel_id = 1
        self._path_data = {}
        path_data = POPT_CFG.get_pacman_data()
        for ch_id, ch_data in path_data.items():
            path_data, last_hop, seed = ch_data
            self._path_data[ch_id] = path_data, 'HOME', seed
        # self._path_data = POPT_CFG.get_pacman_data()
        self._connected_path = {}
        """
        test_data = {
            1: ({
                'Home': ['test1', 'test3'],
                'test3': ['AAAA', 'BBBB'],
                'BBBB': ['CCCC'],
            }, 'LAST_HOPP'),
        }
        """
        ##########################
        # Plot Frame
        g_frame = ttk.Frame(self)
        g_frame.pack(fill=tk.BOTH, expand=True)

        self._fig, self._plot1 = plt.subplots(dpi=50)
        # self._plot2 = self._plot1.twinx()
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FIGc(self._fig, master=g_frame)
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die plots erstellen
        # toolbar1 = NavigationToolbar2Tk(self._canvas, g_frame)
        # toolbar1.update()
        # toolbar1.pack(side=tk.TOP, fill=tk.X)
        ####################################
        # BTN Fram
        btn_frame = ttk.Frame(self)
        btn_frame.pack()
        ttk.Button(btn_frame, text='Refresh', command=self._refresh_btn).pack(side=tk.LEFT, padx=20)
        ttk.Button(btn_frame, text=get_strTab('delete', self._lang), command=self._reset_btn).pack(side=tk.LEFT, padx=20)

        self._g = nx.Graph()
        self._plot1.axis('off')
        self._fig.set_facecolor('#191621')
        self._canvas.draw()

    def _reset_btn(self, event=None):
        self._path_data[self._channel_id] = ({}, 'HOME', int(random.randint(1, 10000)))
        self._update_Graph(self._channel_id)

    def _refresh_btn(self, event=None):
        self._new_seed()
        self._update_Graph(self._channel_id)

    def _new_seed(self):
        path_data, last_hop, seed = self._get_ch_data(self._channel_id)
        seed = random.randint(1, 10000)
        self._path_data[self._channel_id] = dict(path_data), str(last_hop), int(seed)

    def _update_Graph(self, ch_id: int):
        # self._init_vars_fm_raw_data()
        self._update_Node_pos(ch_id)
        self._update_node_label()
        self._plot1.axis('off')
        # self._fig.set_facecolor('#191621')
        self._canvas.draw()
        #self._fig.canvas.draw()
        #self._fig.canvas.flush_events()
        self._canvas.flush_events()

    def _update_node_label(self):
        if not self._pos:
            return
        path_data, last_hop, seed = self._get_ch_data(self._channel_id)
        tmp = []
        for node_name, l_pos in self._pos.items():
            if node_name not in tmp:
                tmp.append(node_name)
                if node_name == last_hop:
                    node_color = '#f70505'
                else:
                    node_color = 'black'
                self._plot1.text(l_pos[0], l_pos[1] + 0.06,
                                 s=node_name,
                                 color='#ffffff',
                                 bbox=dict(
                                     facecolor=node_color,
                                     edgecolor='#ffffff',
                                     boxstyle='round',
                                     alpha=0.5,),
                                 horizontalalignment='center',
                                 fontsize=15
                                 )

    def _update_Node_pos(self, ch_id: int):
        self._plot1.clear()
        self._g.clear()
        self._pos = None
        path_data, last_hop, seed = self._path_data.get(ch_id, self._get_ch_data(ch_id))
        if not path_data:
            return
        # self._pos = None
        filter_dbl = []
        for node1, dest_nodes in path_data.items():
            for node2 in dest_nodes:
                if any((
                        (node1, node2) in filter_dbl,
                        (node2, node1) in filter_dbl,
                )):
                    continue
                if self._is_conn_path(ch_id, (node1, node2)):
                    self._add_edge(node1, node2, 'red', weight=1.7)
                else:
                    self._add_edge(node1, node2, 'white', weight=1.1)
                filter_dbl.append((node1, node2))

        self._pos = nx.spring_layout(self._g, seed=seed)

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

    def _add_edge(self, e1: str, e2: str, col='white', weight=1.2):
        if not all((e1, e2)):
            return
        own_calls = POPT_CFG.get_stat_CFG_keys()
        if e1 in own_calls:
            e1 = 'HOME'
        if e2 in own_calls:
            e2 = 'HOME'
        self._g.add_edge(e1, e2, color=col, weight=weight)

    def _get_ch_data(self, ch_id: int):
        return self._path_data.get(ch_id, ({}, 'HOME', int(random.randint(1, 10000))))

    def _is_conn_path(self, ch_id: int, nodes: tuple):
        conn_path = list(self._connected_path.get(ch_id, ['HOME']))
        if not conn_path:
            return False
        if conn_path == list(nodes):
            return True
        for node1, node2 in zip(nodes, nodes[1:]):
            for i in range(len(conn_path) - 1):
                if [node1, node2] == conn_path[i:i + 2] or [node2, node1] == conn_path[i:i + 2]:
                    return True
        return False

    ###############################################
    #
    def change_node(self, ch_id: int, node: str):
        path_data, last_hop, seed = self._get_ch_data(ch_id)
        if node == last_hop:
            return
        node_path = list(path_data.get(last_hop, []))
        conn_path = list(self._connected_path.get(ch_id, ['HOME']))
        if node not in node_path:
            node_path.append(node)
        if node not in conn_path:
            conn_path.append(node)
        else:
            conn_path.reverse()
            i = conn_path.index(node)
            if i != -1:
                conn_path = conn_path[i:]
            conn_path.reverse()

        path_data[last_hop] = list(node_path)
        last_hop = str(node)

        self._path_data[ch_id] = dict(path_data), str(last_hop), int(seed)
        self._connected_path[ch_id] = list(conn_path)

    def reset_last_hop(self, ch_id: int):
        path_data, last_hop, seed = self._get_ch_data(ch_id)
        last_hop = 'HOME'
        self._path_data[ch_id] = dict(path_data), str(last_hop), int(seed)
        self._connected_path[ch_id] = ['HOME']

    def update_plot_f_ch(self, ch_id):
        self._channel_id = int(ch_id)
        self._update_Graph(ch_id)

    def save_path_data(self):
        POPT_CFG.set_pacman_data(dict(self._path_data))
