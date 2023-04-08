import tkinter as tk
from tkinter import ttk


class LinkHolderSettings(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self)
        self.root_win = root
        self.root_win.settings_win = self
        self.win_height = 285
        self.win_width = 850
        self.style = self.root_win.style
        self.title("Link Halter")
        self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root_win.main_win.winfo_x()}+"
                      f"{self.root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(True, True)
        self.lift()
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text="Ok",
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)


        cancel_bt = tk.Button(self,
                              text="Abbrechen",
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        # On/OFF Checkbox
        _x = 20
        _y = 20
        self.l_holder_chk_var = tk.BooleanVar(self)
        self.l_holder_chk = tk.Checkbutton(self,
                                           text='Aktivieren',
                                           variable=self.l_holder_chk_var
                                           )

        self.l_holder_chk.place(x=_x, y=_y)

        # Intervall
        _x = 320
        _y = 20
        _label = tk.Label(self, text='Intervall (Minuten):')
        self.intervall_var = tk.IntVar()
        self.intervall_var.set(30)
        val = []
        for n in range(125):
            if n and not n % 5:
                val.append(str(n))

        self.intervall = tk.ttk.Combobox(self,
                                         width=4,
                                         textvariable=self.intervall_var,
                                         values=val,
                                         )
        _label.place(x=_x, y=_y)
        self.intervall.place(x=_x + 180, y=_y)

        # Text
        _x = 20
        _y = 60
        self.text = tk.Text(self,
                            width=80,
                            height=5)
        self.text.place(x=_x, y=_y)

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
            self.conn.link_holder_on = self.l_holder_chk_var.get()
            self.conn.link_holder_interval = self.intervall_var.get()
            text = self.text.get('1.0', tk.END)[:-1]
            text = text.replace('\n', '\r')
            self.conn.link_holder_text = text
            if self.conn.link_holder_on:
                self.root_win.tabbed_sideFrame.link_holder.select()
            else:
                self.root_win.tabbed_sideFrame.link_holder.deselect()
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.root_win.settings_win = None

    def tasker(self):
        pass
