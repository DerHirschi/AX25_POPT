import time
import tkinter as tk
from tkinter import ttk

from cfg.constant import COLOR_MAP
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class LinkHolderSettings(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, master=root.main_win)
        self.root_win = root
        self.root_win.settings_win = self
        self.win_height = 245
        self.win_width = 850
        self.style = self.root_win.style
        self._getTabStr    = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._get_colorMap = lambda: COLOR_MAP.get(root.style_name, ('black', '#d9d9d9'))
        self.title(self._getTabStr('linkholder'))
        self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root_win.main_win.winfo_x()}+"
                      f"{self.root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ######################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ######################################
        # OK, Save, Cancel
        ok_bt = ttk.Button(main_f,
                          text=self._getTabStr('Ok'),
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          #height=1,
                          width=6,
                          command=self.ok_btn_cmd)


        cancel_bt = ttk.Button(main_f,
                              text=self._getTabStr('cancel'),
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              #height=1,
                              width=8,
                              command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        # On/OFF Checkbox
        _x = 20
        _y = 20
        self.l_holder_chk_var = tk.BooleanVar(self)
        self.l_holder_chk = ttk.Checkbutton(main_f,
                                           text=self._getTabStr('activate'),
                                           variable=self.l_holder_chk_var
                                           )

        self.l_holder_chk.place(x=_x, y=_y)

        # Intervall
        x = 320
        y = 20
        label = ttk.Label(main_f, text=f"{self._getTabStr('intervall')} (Min):")
        self.intervall_var = tk.IntVar()
        self.intervall_var.set(30)
        val = []
        for n in range(125):
            if n and not n % 5:
                val.append(str(n))

        self.intervall = ttk.Combobox(main_f,
                                         width=4,
                                         textvariable=self.intervall_var,
                                         values=val,
                                         )
        label.place(x=x, y=y)
        self.intervall.place(x=x + 180, y=y)

        # Text
        x = 20
        y = 60
        fg, bg = self._get_colorMap()
        self.text = tk.Text(main_f,
                            width=80,
                            height=5,
                            fg=fg,
                            bg=bg,
                            highlightthickness=0,
                            )
        self.text.place(x=x, y=y)

        self.conn = self.root_win.get_conn()
        if not self.conn:
            self.intervall.configure(state='disabled')
            self.text.configure(state='disabled')
            self.l_holder_chk.configure(state='disabled')
        else:
            text = self.conn.link_holder_text.replace('\r', '\n')
            self.text.insert(tk.INSERT, text)
            self.intervall_var.set(self.conn.link_holder_interval)
            self.l_holder_chk_var.set(self.conn.link_holder_on)

    def ok_btn_cmd(self):
        if self.conn:
            self.conn.link_holder_on        = bool(self.l_holder_chk_var.get())
            self.conn.link_holder_interval  = int(self.intervall_var.get())
            text = self.text.get('1.0', tk.END)[:-1]
            text = text.replace('\n', '\r')
            self.conn.link_holder_text = text
            if self.conn.link_holder_on:
                self.conn.link_holder_timer = time.time()
                self.root_win.link_holder_var.set(True)
            else:
                self.root_win.link_holder_var.set(False)
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.root_win.settings_win = None

    def tasker(self):
        pass
