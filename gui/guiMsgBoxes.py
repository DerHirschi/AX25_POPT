import tkinter as tk
from tkinter import messagebox, font, filedialog
import sys

from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab

getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

def open_file_dialog(master_win=None):
    filetypes = (
        ('All files', '*.*'),
        ('text files', '*.txt'),
    )
    try:
        if master_win:
            name = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=filetypes,
                parent=master_win)
        else:
            name = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=filetypes)
    except PermissionError:
        return b''
    if name:
        with open(name, 'rb') as output:
            return output.read()
    return b''


def save_file_dialog(data, master_win=None):
    filetypes = (
        ('All files', '*.*'),
        ('text files', '*.txt'),
    )
    try:
        if master_win:
            f = filedialog.asksaveasfile(mode='w',
                                         defaultextension=".txt",
                                         filetypes=filetypes,
                                         parent=master_win)
        else:
            f = filedialog.asksaveasfile(mode='w',
                                         defaultextension=".txt",
                                         filetypes=filetypes)
    except PermissionError:
        return False
    if f is None:
        return DeprecationWarning
    try:
        f.write(data)
    except UnicodeEncodeError:
        # FIXME Codec : UnicodeEncodeError: 'latin-1' codec can't encode characters in position 1090-1097: ordinal not in range(256)
        pass
    f.close()
    return True

def call_vali_warning(root_win):
    mb = messagebox.showerror(getTabStr('call_vali_warning_1'),
                              getTabStr('call_vali_warning_2'),
                              parent=root_win)
    mb.upper()


class ErrorMsg(tk.Toplevel):
    def __init__(self, titel, message):
        self.msg = message
        temp = []
        if '\n' in self.msg:
            temp = self.msg.split('\n')
            self.msg = ''
        if not temp:
            while len(self.msg) > 47:
                temp.append(self.msg[:47] + '\n')
                self.msg = self.msg[47:]
        self.msg = '\n'.join(temp) + self.msg
        self.msg_title = titel
        if 'linux' in sys.platform:
            tk.Toplevel.__init__(self)
            self.columnconfigure(0, minsize=20, weight=1)
            self.columnconfigure(2, minsize=20, weight=1)
            self.rowconfigure(0, minsize=10, weight=0)
            self.rowconfigure(2, minsize=35, weight=1)
            self.rowconfigure(4, minsize=10, weight=0)
            self.title(self.msg_title)
            w = 480  # width for the Tk root
            h = 150  # height for the Tk root

            # get screen width and height
            ws = self.winfo_screenwidth()  # width of the screen
            hs = self.winfo_screenheight()  # height of the screen

            # calculate x and y coordinates for the Tk root window
            x = (ws / 2) - (w / 2)
            y = (hs / 2) - (h / 2)

            self.geometry('%dx%d+%d+%d' % (w, h, x, y))
            self.protocol("WM_DELETE_WINDOW", self.destroy)
            self.resizable(False, False)
            self.attributes("-topmost", True)
            try:
                self.iconbitmap("favicon.ico")
            except tk.TclError:
                pass
            self.lift()  # Puts Window on top
            self.grab_set()  # Prevents other Tkinter windows from being used
            self.init()
        else:
            self.grab_set()
            self.win_msg()

    def win_msg(self):
        messagebox.showerror(self.msg_title, self.msg)

    def init(self):
        tk.Label(self, text=self.msg).grid(row=1, column=1)
        tk.Button(self, command=self.destroy, text="OK").grid(row=3, column=1)


class InfoMsg(ErrorMsg):
    def init(self):
        tk.Label(self, text=self.msg).grid(row=1, column=1)
        tk.Button(self, command=self.destroy, text="OK").grid(row=3, column=1)

    def win_msg(self):
        messagebox.showinfo(self.msg_title, self.msg)


class WarningMsg(ErrorMsg):
    def init(self):
        self.lift()
        tk.Label(self, text=self.msg).grid(row=1, column=1)
        tk.Button(self, command=self.destroy, text="OK").grid(row=3, column=1)

    def win_msg(self):
        messagebox.showwarning(self.msg_title, self.msg)


# class AskMsg(tk.Toplevel):
def AskMsg(titel, message, parent_win):
    # def __init__(self, titel, message):
    msg = message
    temp = []
    if '\n' in msg:
        temp = msg.split('\n')
        msg = ''
    if not temp:
        while len(msg) > 47:
            temp.append(msg[:47] + '\n')
            msg = msg[47:]
    msg = '\n'.join(temp) + msg
    if 'linux' in sys.platform:
        font1 = font.Font(name='TkCaptionFont', exists=True)
        font1.config(family='courier new', size=8)

    return messagebox.askokcancel(title=titel, message=msg, parent=parent_win)





"""
def win_msg(self):
    self.ret = messagebox.askokcancel(title=self.msg_title, message=self.msg)

def set_ret(self, inp: bool):
    self.ret = inp
    self.destroy()
"""
"""
def wait_for_ret(self):
    while self.ret is None:
        time.sleep(0.1)
    # self.destroy()
    return self.ret
"""
"""
def init(self):
    tk.Label(self, text=self.msg).grid(row=1, column=1, columnspan=3)
    tk.Button(self, command=lambda: self.set_ret(True), text="OK").grid(row=3, column=1)
    tk.Button(self, command=lambda: self.set_ret(False), text="Abbrechen").grid(row=3, column=3)
"""