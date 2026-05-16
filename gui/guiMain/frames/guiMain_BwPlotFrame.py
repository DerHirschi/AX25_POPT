from tkinter import ttk

from cfg.constant import COLOR_MAP
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab

from gui import FigureCanvasTkAgg, plt
# from gui import FigureCanvasTkAgg
# FIX: Tcl_AsyncDelete: async handler deleted by the wrong thread
# FIX: https://stackoverflow.com/questions/27147300/matplotlib-tcl-asyncdelete-async-handler-deleted-by-the-wrong-thread


class BwPlotFrame(ttk.Frame):
    def __init__(self, gui_root_cl, parent):
        super().__init__(parent)
        #self.pack(fill='both', expand=True)
        # ================================
        self._gui_root     = gui_root_cl
        self._popt_handler = gui_root_cl.get_PH_mainGUI()
        self._mh           = self._popt_handler.get_MH()
        self._style_name   = gui_root_cl.style_name
        # ================================
        self._get_colorMap = lambda : COLOR_MAP.get(self._style_name, ('#000000',  '#d9d9d9'))
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        # ================================
        self._bw_plot_x_scale   = []
        self._bw_plot_lines     = {}
        # ================================
        self._init_frame()


    def _init_frame(self):
        """Cleanup by Grok3-AI"""
        # Precompute x-scale (0 to 10 minutes, 60 steps at 10-second intervals)
        self._bw_plot_x_scale = [i / 6 for i in range(60)]  # 60 steps over 10 minutes

        # Create figure and axis
        self._bw_fig, self._ax = plt.subplots(dpi=100)
        self._bw_fig.subplots_adjust(left=0.1, right=0.95, top=0.99, bottom=0.15)
        self._ax.axis([0, 10, 0, 100])  # X: 0-10 min, Y: 0-100% occupancy

        # Styling
        fg, bg = self._get_colorMap()
        self._bw_fig.set_facecolor(bg)
        self._ax.set_facecolor('#191621')
        self._ax.xaxis.label.set_color(fg)
        self._ax.yaxis.label.set_color(fg)
        self._ax.tick_params(axis='x', colors=fg)
        self._ax.tick_params(axis='y', colors=fg)
        self._ax.set_xlabel(self._getTabStr('minutes'))
        self._ax.set_ylabel(self._getTabStr('occup'))

        # Embed in Tkinter
        self._canvas = FigureCanvasTkAgg(self._bw_fig, master=self)
        self._canvas.get_tk_widget().pack(side='top', expand=True, fill='both')
        self._canvas.draw()  # Initial draw


    def update_bw_mon(self):
        """Cleanup by Grok3-AI"""
        redraw_needed = False
        for port_id in self._popt_handler.port_manager.ax25_ports.keys():
            port_cfg = POPT_CFG.get_port_CFG_fm_id(port_id)
            baud = port_cfg.get('parm_baud', 1200)
            data = self._mh.get_bandwidth(port_id, baud)  # Annahme: gibt eine Liste zurück

            label = port_cfg.get('parm_PortName', f'Port {port_id}')

            if port_id not in self._bw_plot_lines:
                line, = self._ax.plot(self._bw_plot_x_scale, data, label=label)
                self._bw_plot_lines[port_id] = line
                self._ax.legend()
                redraw_needed = True
            else:
                # Umwandlung der aktuellen y-Daten in eine Liste für den Vergleich
                current_ydata = list(self._bw_plot_lines[port_id].get_ydata())
                if data != current_ydata:  # Direkter Listenvergleich
                    self._bw_plot_lines[port_id].set_ydata(data)
                    redraw_needed = True

        if redraw_needed:
            self._draw_bw_plot()

    def _draw_bw_plot(self):
        """Cleanup by Grok3-AI"""
        self._bw_fig.canvas.draw()
        self._bw_fig.canvas.flush_events()
