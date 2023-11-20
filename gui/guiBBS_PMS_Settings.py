import tkinter as tk
from string_tab import STR_TABLE


class PMS_Settings(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        self._lang = root_win.language
        ###################################
        # Vars

        ###################################
        # self.title(STR_TABLE['msg_center'][self._lang])
        self.title('PMS Settings')
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"800x"
                      f"600+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        ###################################

        _pms_frame = tk.Frame(self)
        _ok_btn_frame = tk.Frame(self)

    def tasker(self):
        pass

    def _close(self):
        # self._bbs_obj = None
        self._root_win.settings_win = None
        self.destroy()

