import tkinter as tk

from cfg.string_tab import STR_TABLE
from cfg.popt_config import POPT_CFG

class PrivilegWin(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, master=root.main_win)
        self._root_cl = root
        self._lang = POPT_CFG.get_guiCFG_language()
        root.settings_win = self
        self.win_height = 350
        self.win_width = 840
        self.style = root.style
        self.title(STR_TABLE['priv'][self._lang])
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root_cl.main_win.winfo_x()}+"
                      f"{self._root_cl.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        # self.attributes("-topmost", True)

        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text="Login",
                          # font=("TkFixedFont", 15),
                          # bg="green",
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)


        cancel_bt = tk.Button(self,
                              text=STR_TABLE['cancel'][self._lang],
                              # font=("TkFixedFont", 15),
                              # bg="green",
                              height=1,
                              width=8,
                              command=self.destroy_win)
        ok_bt.place(x=20, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        ##############################################
        #
        _x = 20
        _y = 20
        tk.Label(self, text=STR_TABLE['syspassword'][self._lang]).place(x=_x, y=_y)
        # self.sys_password_var = tk.StringVar(self)
        self.sys_password_ent = tk.Text(self,
                                        height=5,
                                        width=80)
        _x = 15
        _y = 60
        self.sys_password_ent.place(x=_x, y=_y)
        # Fake-Attempts inclusive real attempt
        _x = 20
        _y = 200
        tk.Label(self, text=STR_TABLE['trys'][self._lang]).place(x=_x, y=_y)
        self.fake_attempts_var = tk.StringVar(self)
        self.fake_attempts_var.set('5')
        # max_pac_opt = list(range(8))
        self.fake_attempts_ent = tk.Spinbox(self,
                                            textvariable=self.fake_attempts_var,
                                            from_=1,
                                            to=10,
                                            increment=1,
                                            width=3
                                            )
        self.fake_attempts_ent.place(x=_x + 140, y=_y - 2)
        # Fill Chars
        _x = 300
        _y = 200
        tk.Label(self, text=STR_TABLE['fillchars'][self._lang]).place(x=_x, y=_y)
        self.fill_char_var = tk.StringVar(self)
        self.fill_char_var.set('80')
        # max_pac_opt = list(range(8))
        self.fill_chars_ent = tk.Spinbox(self,
                                         textvariable=self.fill_char_var,
                                         from_=0,
                                         to=120,
                                         increment=10,
                                         width=4
                                         )
        self.fill_chars_ent.place(x=_x + 140, y=_y - 2)
        # Login CMD
        _x = 20
        _y = 240
        tk.Label(self, text=STR_TABLE['login_cmd'][self._lang]).place(x=_x, y=_y)
        self.login_cmd_var = tk.StringVar(self)
        self.login_cmd_var.set('SYS')
        tk.Entry(self, textvariable=self.login_cmd_var, width=20).place(x=_x + 170, y=_y)

        ################################################################
        ################################################################
        ###############
        # VARS
        self.db_ent = False
        conn = self._root_cl.get_conn()
        if conn is None:
            ok_bt.configure(state='disabled')
        else:
            self.db_ent = conn.user_db_ent
        if self.db_ent:
            self.sys_password_ent.delete(0.0, tk.END)
            self.sys_password_ent.insert(tk.INSERT, str(self.db_ent.sys_pw))
            self.fake_attempts_var.set(str(self.db_ent.sys_pw_parm[0]))
            self.fill_char_var.set(str(self.db_ent.sys_pw_parm[1]))

    def ok_btn_cmd(self):
        # self.root.msg_to_monitor('Lob: Du hast dir heute noch kein Lob verdient.')
        self.save_to_user_db()
        # sys_cmd = self.login_cmd_var.get()
        self._root_cl.do_priv()
        self.destroy_win()

    def save_to_user_db(self):
        self.db_ent.sys_pw = self.sys_password_ent.get(0.0, tk.END)[:-1]
        self.db_ent.sys_pw_parm = [
            int(self.fake_attempts_var.get()),
            int(self.fill_char_var.get()),
            str(self.login_cmd_var.get()),
        ]

    def destroy_win(self):
        self.destroy()
        self._root_cl.settings_win = None

    def tasker(self):
        pass

