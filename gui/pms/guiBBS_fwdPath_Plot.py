import tkinter as tk
import networkx as nx
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread
import matplotlib

from ax25.ax25InitPorts import PORT_HANDLER

matplotlib.use('Agg')
from matplotlib import pyplot as plt


class FwdGraph(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.wm_title("Port Statistik")
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
        btn_frame = tk.Frame(self)
        btn_frame.pack()
        refresh_btn = tk.Button(btn_frame,
                                text='Refresh',
                                command=self._update_Graph
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
        }
        style_opt_keys = list(self._style_opt.keys())
        style_option = tk.OptionMenu(btn_frame,
                                     self._style_var,
                                     *style_opt_keys,
                                     command=self._update_Graph
                                     )
        style_option.pack(side=tk.LEFT, padx=10)

        g_frame = tk.Frame(self)
        g_frame.pack(expand=True, fill=tk.BOTH)

        self._fig, self._plot1 = plt.subplots()
        self._fig.subplots_adjust(top=1.00, bottom=0.00, left=0.00, right=1.00, hspace=0.00)
        self._canvas = FigureCanvasTkAgg(self._fig, master=g_frame)
        self._canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        # Werkzeugleisten für die Plots erstellen
        toolbar1 = NavigationToolbar2Tk(self._canvas, self)
        toolbar1.update()
        toolbar1.pack(side=tk.TOP, fill=tk.X)

        self._root_win.fwd_Path_plot_win = self

        db = PORT_HANDLER.get_database()
        self._path_data = db.bbs_get_fwdPaths()
        self._g = nx.Graph()
        self._update_Graph()

    def _update_Graph(self, event=None):
        if not self._path_data:
            return
        if not self._path_data[0]:
            return
        self._plot1.clear()
        self._g.clear()
        fwd_list = [x[0].split('>') for x in self._path_data]
        # Building Graph
        for path in fwd_list:
            if len(path) > 1:
                call_1 = path[0]
                for call_2 in path[1:]:
                    self._g.add_edge(call_1, call_2)
                    call_1 = call_2

        # seed_val = random.randint(0, 10000)

        layout = self._style_opt.get(self._style_var.get(), None)
        if not layout:
            return
        pos = layout(self._g)
        nx.draw_networkx(self._g, pos=pos, ax=self._plot1,
                         with_labels=False, node_shape='o',
                         node_size=200,
                         node_color='#386de0',
                         edge_color='#ffffff',
                         width=1.5,
                         # alpha=0.7
                         )
        """
        nx.draw_networkx_labels(self._g,
                                pos=pos,
                                ax=self._plot1,
                                font_size=17)
        """

        tmp = []
        for k in pos.keys():
            if k not in tmp:
                tmp.append(k)
                l_pos = pos[k]

                self._plot1.text(l_pos[0], l_pos[1] + 0.05,
                                 s=k,
                                 color='#ffffff',
                                 bbox=dict(facecolor='red',
                                           edgecolor='#ffffff',
                                           boxstyle='round',
                                           alpha=0.5),
                                 horizontalalignment='center',
                                 )

        self._plot1.axis('off')
        self._fig.set_facecolor('#191621')
        self._canvas.draw()

    def _destroy_plot(self):
        plt.close()
        self._canvas.get_tk_widget().destroy()
        self._root_win.fwd_Path_plot_win = None
        self.destroy()

