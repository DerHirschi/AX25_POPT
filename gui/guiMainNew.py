import tkinter as tk
from tkinter import ttk
import logging
import threading
from playsound import playsound

from gui.guiTxtFrame import TxTframe
from main import VER, AX25PortHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)

LOOP_DELAY = 50  # ms
TEXT_SIZE = 15
TEXT_SIZE_STATUS = 11
FONT = "Courier"
TXT_BACKGROUND_CLR = 'black'
TXT_OUT_CLR = 'red'
TXT_INP_CLR = 'yellow'
TXT_INP_CURSOR_CLR = 'white'
TXT_MON_CLR = 'green'


def pl_sound(snd_file: str):
    snd = threading.Thread(target=playsound, args=(snd_file,))
    snd.start()


class ChVars:
    output_win = ''
    input_win = ''
    new_data_tr = False
    rx_beep_tr = False


class TkMainWin:
    def __init__(self, port_handler: AX25PortHandler):
        self.main_win = tk.Tk()
        self.main_win.title("P.ython o.ther P.acket T.erminal {}".format(VER))
        self.main_win.geometry("1400x850")
        #self.pw_inp = ttk.PanedWindow(orient=tk.HORIZONTAL)
        # change style to classic (Windows only)
        # to show the sash and handle
        self.style = ttk.Style()
        self.style.theme_use('classic')
        self.main_win.columnconfigure(0, minsize=500, weight=1)
        self.main_win.columnconfigure(1, minsize=150, weight=1)
        self.main_win.rowconfigure(0, minsize=80, weight=0)
        self.main_win.rowconfigure(1, minsize=300, weight=2)

        # self.txt_frame = tk.Frame(self.main_win, width=500, height=30)

        self.txt_win = TxTframe()

        # self.txt_win.init(self.main_win)
        # self.txt_win.grid(row=1, column=0, sticky="nsew")

        self.main_win.mainloop()


if __name__ == '__main__':
    try:
        TkMainWin()
    except KeyboardInterrupt:
        pass
    print("Ende")
