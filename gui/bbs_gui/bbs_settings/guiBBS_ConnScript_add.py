import tkinter as tk
from tkinter import ttk, messagebox
from cfg.default_config import getNew_BBS_FWD_cfg
from cfg.popt_config import POPT_CFG
from cfg.logger_config import logger
from fnc.ax25_fnc import validate_ax25Call
from fnc.str_fnc import get_strTab

class BBSaddConnScript(tk.Toplevel):
    def __init__(self, root_win, dest_call: str):
        tk.Toplevel.__init__(self, master=root_win)
        win_width  = 600
        win_height = 350
        self.style = root_win.style
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{root_win.winfo_x()}+"
                      f"{root_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.attributes("-topmost", True)
        self.resizable(True, True)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        #########################
        main_f = ttk.Frame(self)
        main_f.pack(fill="both", expand=True)
        #########################
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self._root_win      = root_win
        self._root_win.add_win = self
        self.title(f"Connect Script - {dest_call}")
        ####################################################
        # CFG
        self._dest_call     = dest_call
        self._pms_cfg: dict = self._root_win.get_root_pms_cfg()
        self._fwd_bbs_cfg   = self._pms_cfg.get('fwd_bbs_cfg', {}).get(dest_call, getNew_BBS_FWD_cfg())
        self._conn_script   = self._fwd_bbs_cfg.get('conn_script', [])
        """
        self._conn_script   = [
            {'cmd': 'c celle',  'dest_call': 'CEN0DE', 'wait': 0},
            {'cmd': 'm',        'dest_call': 'CE0BBS', 'wait': 0}
        ]
        """
        ####################################################
        self._dest_call_var = tk.StringVar(self)
        self._command_var   = tk.StringVar(self)
        self._wait_var      = tk.StringVar(self, value='0')
        ####################################################
        tree_frame      = ttk.Frame(main_f)
        input_frame     = ttk.Frame(main_f, height=50)
        upper_btn_frame = ttk.Frame(main_f, height=50)
        btn_frame       = ttk.Frame(main_f, height=50)
        tree_frame.pack(        expand=True,  fill="both")
        input_frame.pack(       expand=True,  fill="x")
        upper_btn_frame.pack(   expand=False)
        btn_frame.pack(         expand=False, fill="x", padx=10, pady=10)
        ###########################################
        # tree_frame
        col = [
            'dest',
            'cmd',
            'wait'
        ]
        self._tree = ttk.Treeview(tree_frame, columns=col, show="headings")
        self._tree.pack(side="left", fill="both", expand=True)
        self._tree.heading('dest', text=self._getTabStr('ziel'))
        self._tree.heading('cmd',  text=self._getTabStr('command'))
        self._tree.heading('wait', text=f"{self._getTabStr('wait')} (s)")
        self._tree.column("dest", anchor='w', stretch=tk.NO,  width=65)
        self._tree.column("cmd",  anchor='w', stretch=tk.YES, width=250)
        self._tree.column("wait", anchor='center', stretch=tk.NO,  width=70)
        ###########################################
        # input_frame
        ttk.Entry(input_frame,
                  textvariable=self._dest_call_var ,
                  width=10).pack(side='left', padx=5)
        ttk.Entry(input_frame,
                  textvariable=self._command_var ,
                  width=50).pack(side='left')
        ttk.Spinbox(input_frame,
                    textvariable=self._wait_var,
                    width=4,
                    from_=0,
                    to=180,
                    increment=5).pack(side='left', padx=15)
        ###########################################
        # upper_btn_frame
        add_btn = ttk.Button(upper_btn_frame, text=self._getTabStr('add'),    command=self._add_btn)
        del_btn = ttk.Button(upper_btn_frame, text=self._getTabStr('delete'), command=self._delete_btn)
        add_btn.pack(side="left", anchor="center")
        del_btn.pack(side="left", anchor="center")
        ###########################################
        # BTN btn_frame
        save_btn  = ttk.Button(btn_frame, text=self._getTabStr('save'),   command=self._save_btn)
        abort_btn = ttk.Button(btn_frame, text=self._getTabStr('cancel'), command=self._abort_btn)
        save_btn.pack(side="left")
        abort_btn.pack(side="right", anchor="e")
        self._update_tree()

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)

        for line in self._conn_script:
            line: dict
            val = [
                line.get('dest_call', ''),
                line.get('cmd', ''),
                str(line.get('wait', 0)),
            ]
            self._tree.insert('', 'end', values=val, )


    def _add_btn(self):
        dest_call = self._dest_call_var.get().upper()
        cmd       = self._command_var.get()
        try:
            wait  = int(self._wait_var.get())
        except ValueError:
            wait = 0
        if not validate_ax25Call(dest_call):
            messagebox.showerror(title=self._getTabStr('invalid_axcall_warning1'),
                                 message=self._getTabStr('invalid_axcall_warning2'))
            return

        self._conn_script.append({
            'cmd':          cmd,
            'dest_call':    dest_call,
            'wait':         wait,
        })
        self._update_tree()

    def _delete_btn(self):
        if not self._conn_script:
            return
        self._conn_script = self._conn_script[:-1]
        self._update_tree()

    def _save_btn(self):
        self._fwd_bbs_cfg['conn_script'] = list(self._conn_script)
        self.destroy_win()

    def _abort_btn(self):
        self.destroy_win()

    def destroy_win(self):
        if hasattr(self._root_win, 'lift'):
            self._root_win.lift()
        self._root_win.add_win = None
        self.destroy()