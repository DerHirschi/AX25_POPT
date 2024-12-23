import tkinter as tk

# from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random
import matplotlib
from matplotlib.font_manager import font_scalings

from cfg.constant import FONT
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab

matplotlib.use('Agg')
from matplotlib import pyplot as plt

class LiveConnPath(tk.Frame):
    def __init__(self, tabctl):
        tk.Frame.__init__(self, tabctl)
        self.pack(fill=tk.BOTH, expand=True)
        # self._root_win = root_win
        self._lang = POPT_CFG.get_guiCFG_language()
        self._pos = None
        self._channel_id = 1
        self._path_data = {}
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
        g_frame = tk.Frame(self)
        g_frame.pack(fill=tk.BOTH, expand=True)

        self._fig, self._plot1 = plt.subplots(dpi=50)
        # self._plot2 = self._plot1.twinx()
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FigureCanvasTkAgg(self._fig, master=g_frame)
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die plots erstellen
        # toolbar1 = NavigationToolbar2Tk(self._canvas, g_frame)
        # toolbar1.update()
        # toolbar1.pack(side=tk.TOP, fill=tk.X)
        ####################################
        # BTN Fram
        btn_frame = tk.Frame(self)
        btn_frame.pack()
        tk.Button(btn_frame, text='Refresh', command=self._refresh_btn).pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text=get_strTab('delete', self._lang), command=self._reset_btn).pack(side=tk.LEFT, padx=20)

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
        self._fig.set_facecolor('#191621')
        self._canvas.draw()

    def _update_node_label(self):
        if not self._pos:
            return
        tmp = []
        for node_name, l_pos in self._pos.items():
            if node_name not in tmp:
                tmp.append(node_name)
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
        print(f"Update: {ch_id}")
        self._plot1.clear()
        self._g.clear()
        self._pos = None
        path_data, last_hop, seed = self._path_data.get(ch_id, self._get_ch_data(ch_id))
        print(f"Update: {path_data}")
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

                print(f"{node1} - {node2}")
                self._add_edge(node1, node2, 'white')
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

    ###############################################
    #
    def change_node(self, ch_id: int, node: str):
        path_data, last_hop, seed = self._get_ch_data(ch_id)
        node_path = list(path_data.get(last_hop, []))
        if node not in node_path:
            node_path.append(node)
        path_data[last_hop] = list(node_path)
        last_hop = str(node)
        self._path_data[ch_id] = dict(path_data), str(last_hop), int(seed)
        # print(self._path_data)
        # self._update_Graph(ch_id)

    def reset_last_hop(self, ch_id: int, node='HOME'):
        path_data, last_hop, seed = self._get_ch_data(ch_id)
        last_hop = node
        self._path_data[ch_id] = dict(path_data), str(last_hop), int(seed)

    def update_plot_f_ch(self, ch_id):
        # path_data, last_hop, seed = self._path_data.get(ch_id, DEFAULT_PATH_DATA)
        # self._pos = nx.spring_layout(self._g, seed=seed)
        self._channel_id = int(ch_id)
        self._update_Graph(ch_id)

    def _get_ch_data(self, ch_id: int):
        return self._path_data.get(ch_id, ({}, 'HOME', int(random.randint(1, 10000))))

    def _add_edge(self, e1: str, e2: str, col='white', weight=1.1):
        if not all((e1, e2)):
            return
        own_calls = POPT_CFG.get_stat_CFG_keys()
        if e1 in own_calls:
            e1 = 'HOME'
        if e2 in own_calls:
            e2 = 'HOME'
        self._g.add_edge(e1, e2, color=col, weight=weight)
