import matplotlib
matplotlib.use('TkAgg')  # Verwende TkAgg statt Agg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import pyplot as plt