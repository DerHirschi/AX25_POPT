import gc
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from collections import deque
from memory_profiler import profile
import psutil
# process = psutil.Process(os.getpid())


class BWPlotApp(tk.Toplevel):
    @profile(precision=3)
    def __init__(self, _root_cl):
        tk.Toplevel.__init__(self)
        self.withdraw()
        # gc.collect()
        self._fig = Figure(figsize=(8, 4), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._ax.cla()
        self._ax.clear()
        self._ax.set_xlabel('Zeit (s)')
        self._ax.set_ylabel('CPU-Auslastung (%)')

        self._cpu_loads = deque([0] * 120, maxlen=120)
        self._line, = self._ax.plot(self._cpu_loads)

        self._canvas = FigureCanvasTkAgg(self._fig, master=_root_cl.get_side_frame())
        self._canvas.draw()
        self._widget = self._canvas.get_tk_widget()
        self._widget.grid(row=5, column=0, columnspan=7, sticky="nsew")

        # self._animation = root_cl.tasker
        self._animation = None

    @staticmethod
    def _get_cpu_load():
        return psutil.cpu_percent()

    @profile(precision=3)
    def _update_plot(self):
        #self._ax.cla()  # Lösche den alten Plot
        #self._ax.set_xlabel('Zeit (s)')
        #self._ax.set_ylabel('CPU-Auslastung (%)')

        _cpu_load = self._get_cpu_load()
        self._cpu_loads.append(_cpu_load)
        #self._line, = self._ax.plot(self._cpu_loads)  # Erstelle den neuen Plot
        self._line.set_ydata(self._cpu_loads)
        self._ax.relim()
        self._ax.autoscale_view(True, True, True)
        self._canvas.draw()
    
    """
    def _start_animation(self):
        self._update_plot()
        self._animation = self.after(1000, self._start_animation)
    """
    @profile(precision=3)
    def _stop_animation(self):
        self._widget.grid_forget()
        self._ax.cla()
        self._ax.clear()
        #self._canvas.get_tk_widget().forget_grid()
        self._canvas.figure.clf()
        self._canvas.figure.clear()
        self._canvas.get_tk_widget().destroy()

        self.destroy()

        if self._animation is not None:
            self.after_cancel(self._animation)
            self._animation = None
        gc.collect()
        """
        print(f"GB: {gc.garbage}\n")
        print(f"CB: {gc.callbacks}\n")
        _r = weakref.ref(self)
        print(f"WE: {_r}\n")
        del _r
        print(f"WE: {weakref.ref(self)}\n")
        """
        #print(f"OB: {gc.get_objects()}\n")

    """
    def _run(self):
        self._start_animation()
        self.mainloop()
    """
    def bw_tasker(self):
        self._update_plot()

    def destroy_win(self):
        self._stop_animation()
        self.destroy()

# BW_PLOT = threading.Thread(target=BWPlotApp).start()
"""
# Beispiel für die Verwendung
if __name__ == "__main__":
    try:
        cpu_plot_app = BWPlotApp()
        cpu_plot_app._run()
    except KeyboardInterrupt:

        cpu_plot_app = BWPlotApp()
        cpu_plot_app._run()
"""