import time
import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab

# from cfg.logger_config import logger

class BBS_fwd_Q(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self, master=root_win.main_win)
        self._root_win  = root_win
        self._bbs_obj   = PORT_HANDLER.get_bbs()
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        ###################################
        self.title(self._getTabStr('fwd_list'))
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1190x"
                      f"400+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        #########################################
        # Vars
        self._port_vars = {}
        self._bbs_vars  = {}
        self._tree_data = []
        self._data      = []
        self._rev_ent   = False

        # ############################### Columns ############################
        # _frame = tk.Frame(self, background='red')
        # _frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # _frame.columnconfigure(0, weight=1, minsize=1000)
        # _frame.columnconfigure(1, weight=0, minsize=150)
        # _frame.rowconfigure(0, weight=0)
        # tk.Label(_frame, text='sags').grid(row=0, column=1)
        ##########################################################################################
        # Tab-ctl
        root_frame   = ttk.Frame(self, borderwidth=10)
        root_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._tabctl = ttk.Notebook(root_frame)
        self._tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tree_frame = ttk.Frame(self._tabctl)
        port_frame = ttk.Frame(self._tabctl)
        self._tabctl.add(tree_frame, text=self._getTabStr('fwd_list'))
        self._tabctl.add(port_frame, text="FWD-Ports")
        #tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #port_frame.pack(side=tk.TOP,  fill=tk.BOTH, expand=True)

        ##########################################################################################
        # TREE

        columns = (
            'BID',
            'from',
            'to',
            'fwd_bbs_call',
            'type',
            'sub',
            'size',
        )

        self._tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self._tree.heading('BID', text='BID', command=lambda: self._sort_entry('BID'))
        self._tree.heading('from', text=self._getTabStr('from'), command=lambda: self._sort_entry('from'))
        self._tree.heading('to', text=self._getTabStr('to'), command=lambda: self._sort_entry('to'))
        self._tree.heading('fwd_bbs_call', text=f"{self._getTabStr('to')} BBS", command=lambda: self._sort_entry('fwd_bbs_call'))
        self._tree.heading('type', text='Type', command=lambda: self._sort_entry('type'))
        self._tree.heading('sub', text=self._getTabStr('subject'), command=lambda: self._sort_entry('sub'))
        self._tree.heading('size', text='Msg-Size', command=lambda: self._sort_entry('size'))
        self._tree.column("BID", anchor=tk.CENTER, stretch=tk.YES, width=130)
        self._tree.column("from", anchor=tk.CENTER, stretch=tk.YES, width=190)
        self._tree.column("to", anchor=tk.CENTER, stretch=tk.YES, width=190)
        self._tree.column("fwd_bbs_call", anchor=tk.CENTER, stretch=tk.YES, width=90)
        self._tree.column("type", anchor=tk.CENTER, stretch=tk.YES, width=60)
        self._tree.column("sub", anchor=tk.CENTER, stretch=tk.YES, width=150)
        self._tree.column("size", anchor=tk.CENTER, stretch=tk.YES, width=60)
        # self._tree.bind('<<TreeviewSelect>>', self._entry_selected)
        ###
        btn_frame = ttk.Frame(tree_frame, width=150)
        btn_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        ttk.Button(btn_frame,
                  text=self._getTabStr('start_fwd'),
                  command=self._do_fwd
                  ).pack()
        ##########################################################################################
        # port_frame
        # port_m_f = ttk.Frame(port_frame)
        # port_m_f.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._port_tabctl = ttk.Notebook(port_frame)
        self._port_tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for fwd_port_id, fwd_port_vars in self._bbs_obj.get_fwdPort_vars().items():
            port_tab_f = ttk.Frame(self._port_tabctl)
            self._port_tabctl.add(port_tab_f, text=f"FWD-Port {fwd_port_id}")
            ###############
            # L/R Frames
            l_frame = ttk.Frame(port_tab_f, borderwidth=10)
            r_frame = ttk.Frame(port_tab_f, borderwidth=10)

            l_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y, padx=10, pady=10)
            ttk.Separator(port_tab_f, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=10)
            r_frame.pack(side=tk.LEFT, expand=False, fill=tk.Y, padx=10, pady=10)
            ###############
            # l_frame
            block_timer_var     = tk.StringVar(self)
            block_byte_c_var    = tk.StringVar(self)
            block_fwd_tasks_var = tk.StringVar(self)

            block_timer_f       = ttk.Frame(l_frame)
            block_byte_c_f      = ttk.Frame(l_frame)
            block_fwd_tasks_f   = ttk.Frame(l_frame)
            reset_btn_f         = ttk.Frame(l_frame, borderwidth=10)
            block_timer_f.pack(    side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
            block_byte_c_f.pack(   side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
            block_fwd_tasks_f.pack(side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
            reset_btn_f.pack(      side=tk.TOP, expand=False, fill=tk.Y, )

            ttk.Label(block_timer_f,     textvariable=block_timer_var).pack(    anchor=tk.W)
            ttk.Label(block_byte_c_f,    textvariable=block_byte_c_var).pack(   anchor=tk.W)
            ttk.Label(block_fwd_tasks_f, textvariable=block_fwd_tasks_var).pack(anchor=tk.W)

            ttk.Button(reset_btn_f,
                      text="Reset Block",
                      command=lambda: self._do_block_reset(),
                      ).pack()

            bbs_tabctl = ttk.Notebook(r_frame)
            self._port_vars[fwd_port_id] = dict(
                block_timer_var     = block_timer_var,
                block_byte_c_var    = block_byte_c_var,
                block_fwd_tasks_var = block_fwd_tasks_var,
                bbs_tabctl          = bbs_tabctl
            )
            ##########################
            # r_frame BBS VARS
            bbs_tabctl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            for bbs_call, bbs_vars in self._bbs_obj.get_bbsQ_vars().items():
                bbs_var_port_id = POPT_CFG.get_BBS_cfg().get('fwd_bbs_cfg', {}).get(bbs_call, {}).get('port_id', -1)
                if bbs_var_port_id != fwd_port_id:
                    continue
                bbs_tab_f = ttk.Frame(bbs_tabctl)
                bbs_tabctl.add(bbs_tab_f, text=bbs_call)

                bbs_byte_c_var  = tk.StringVar(self)
                bbs_error_c_var = tk.StringVar(self)
                bbs_timeout_var = tk.StringVar(self)
                bbs_q_var       = tk.StringVar(self)
                bbs_q_done_var  = tk.StringVar(self)
                bbs_next_q_var  = tk.StringVar(self)

                frame_l  = ttk.Frame(bbs_tab_f, borderwidth=5)
                frame_m  = ttk.Frame(bbs_tab_f, borderwidth=5)
                frame_r  = ttk.Frame(bbs_tab_f, borderwidth=5)

                frame_l.pack(side=tk.LEFT)
                frame_m.pack(side=tk.LEFT)
                frame_r.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

                ###########
                # frame_l
                bbs_byte_c_f    = ttk.Frame(frame_l)
                bbs_error_c_f   = ttk.Frame(frame_l)
                bbs_timeout_f   = ttk.Frame(frame_l)
                bbs_q_f         = ttk.Frame(frame_l)
                bbs_q_done_f    = ttk.Frame(frame_l)
                bbs_next_q_f    = ttk.Frame(frame_l)
                fwd_btn_f       = ttk.Frame(frame_l, borderwidth=10)

                bbs_byte_c_f.pack(  side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
                bbs_error_c_f.pack( side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
                bbs_timeout_f.pack( side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
                bbs_q_done_f.pack(  side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
                bbs_q_f.pack(       side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
                bbs_next_q_f.pack(  side=tk.TOP, expand=False, fill=tk.Y, anchor=tk.W)
                fwd_btn_f.pack(     side=tk.TOP, expand=False, fill=tk.Y, )

                ttk.Label(bbs_byte_c_f,  textvariable=bbs_byte_c_var ).pack(anchor=tk.W)
                ttk.Label(bbs_error_c_f, textvariable=bbs_error_c_var).pack(anchor=tk.W)
                ttk.Label(bbs_timeout_f, textvariable=bbs_timeout_var).pack(anchor=tk.W)
                ttk.Label(bbs_q_f,       textvariable=bbs_q_var      ).pack(anchor=tk.W)
                ttk.Label(bbs_q_done_f,  textvariable=bbs_q_done_var ).pack(anchor=tk.W)
                ttk.Label(bbs_next_q_f,  textvariable=bbs_next_q_var ).pack(anchor=tk.W)

                ttk.Button(fwd_btn_f,
                          # text=self._getTabStr('start_fwd'),
                          text="Reset Timeout",
                          command=lambda: self._do_timeout_reset(),
                          ).pack()

                ###########
                # frame_m
                ttk.Label(frame_m, text='Next-Q').pack(pady=10)
                next_q_tree = ttk.Treeview(frame_m, columns=('bid',), show='headings', height=5)
                next_q_tree.heading('bid', text='BID')
                next_q_tree.column("bid", anchor=tk.W, stretch=tk.YES, width=160)
                next_q_tree.pack()

                ###########
                # frame_r
                ttk.Label(frame_r, text='FWD-Q').pack(pady=5)
                fwd_q_tree = ttk.Treeview(frame_r, columns=('bid', 'typ', 'msgsize', 'tosend'), show='headings')
                fwd_q_tree.heading('bid',    text='BID')
                fwd_q_tree.heading('typ',    text='Typ')
                fwd_q_tree.heading('msgsize',text='Msg Size(B)')
                fwd_q_tree.heading('tosend', text='Bytes to send')
                fwd_q_tree.column("bid",    anchor=tk.W,      stretch=tk.YES, width=160)
                fwd_q_tree.column("typ",    anchor=tk.CENTER, stretch=tk.NO,  width=60)
                fwd_q_tree.column("msgsize", anchor=tk.W,     stretch=tk.YES, width=140)
                fwd_q_tree.column("tosend", anchor=tk.W,      stretch=tk.YES, width=140)
                fwd_q_tree.pack(expand=True, fill=tk.BOTH)

                self._bbs_vars[bbs_call] = dict(
                    bbs_byte_c_var  =bbs_byte_c_var,
                    bbs_error_c_var =bbs_error_c_var,
                    bbs_timeout_var =bbs_timeout_var,
                    bbs_q_var       =bbs_q_var,
                    bbs_q_done_var  =bbs_q_done_var,
                    bbs_next_q_var  =bbs_next_q_var,
                    next_q_tree     =next_q_tree,
                    fwd_q_tree      =fwd_q_tree,
                )


        self._root_win.BBS_fwd_q_list = self
        self.tasker()

    def tasker(self):
        self._get_data()
        self._format_tree_data()
        self._update_tree()
        self._update_port_vars()
        self._update_bbs_vars()

    def _update_port_vars(self):
        fwd_port_cfgs = POPT_CFG.get_BBS_cfg().get('fwd_port_cfg', {})
        for port_id, fwd_port_var in self._bbs_obj.get_fwdPort_vars().items():
            gui_vars     = self._port_vars.get(port_id, {})
            fwd_port_cfg = fwd_port_cfgs.get(port_id, {})
            if not gui_vars:
                continue
            try:
                block_timer     = int(fwd_port_var.get('block_timer', '0'))
                block_byte_c    = int(fwd_port_var.get('block_byte_c', '0'))
                block_fwd_tasks = list(fwd_port_var.get('block_fwd_tasks', []))
            except ValueError:
                continue
            try:
                block_timer_var     = f"Block Timer: {round(((time.time() - block_timer) / 60), 1)}/{fwd_port_cfg.get('block_time', 3)} Min"
            except ZeroDivisionError:
                block_timer_var = f"Block Timer: 0/{fwd_port_cfg.get('block_time', 3)} Min"
            try:
                block_byte_c_var    = f"Block Limit: {round((block_byte_c / 1024), 2)}/{fwd_port_cfg.get('send_limit', 1)} kB"
            except ZeroDivisionError:
                block_byte_c_var    = f"Block Limit: 0/{fwd_port_cfg.get('send_limit', 1)} kB"
            block_fwd_tasks_var = f"Block Tasks: {len(block_fwd_tasks)}"

            gui_vars['block_timer_var'].set(block_timer_var)
            gui_vars['block_byte_c_var'].set(block_byte_c_var)
            gui_vars['block_fwd_tasks_var'].set(block_fwd_tasks_var)

    def _update_bbs_vars(self):
        # bbs_fwd_cfg     = POPT_CFG.get_BBS_cfg().get('fwd_bbs_cfg', {})
        bbs_Qvars: dict = self._bbs_obj.get_bbsQ_vars()

        for bbs_call, gui_vars in self._bbs_vars.items():
            bbs_var = bbs_Qvars.get(bbs_call, {})
            # bbs_cfg = bbs_fwd_cfg.get(bbs_call, {})
            if not bbs_var:
                e_msg = "ERROR"
                gui_vars['bbs_byte_c_var'].set(e_msg)
                gui_vars['bbs_error_c_var'].set(e_msg)
                gui_vars['bbs_timeout_var'].set(e_msg)
                gui_vars['bbs_q_var'].set(e_msg)
                gui_vars['bbs_q_done_var'].set(e_msg)
                gui_vars['bbs_next_q_var'].set(e_msg)
                continue
            bbs_byte_c  = bbs_var.get('bbs_fwd_byte_c',  0)
            bbs_error_c = bbs_var.get('bbs_fwd_error_c', 0)
            bbs_timeout = bbs_var.get('bbs_fwd_timeout', 0)
            bbs_q       = bbs_var.get('bbs_fwd_q',      {})
            bbs_next_q  = bbs_var.get('bbs_fwd_next_q', [])

            try:
                bbs_byte_c  = f"Mail sent: {round(float(bbs_byte_c / 1024), 2)} kB"
            except ZeroDivisionError:
                bbs_byte_c  = "Mail sent: 0.00 kB"

            bbs_error_c  = f"Errors: {bbs_error_c}"
            try:
                timeout = round(((bbs_timeout - time.time()) / 60), 1)
            except ZeroDivisionError:
                timeout = 0
            if timeout < 0:
                timeout = 0

            bbs_timeout  = f"Timeout: {timeout} Min"
            msg_in_q    = 0
            msg_done    = 0
            q_tree_data = []
            for bid, msg2fwd in bbs_q.items():
                flag = msg2fwd.get('flag', '')
                if flag == 'F':
                    msg_in_q += 1
                    q_tree_data.append((
                        msg2fwd.get('bid'          , ''),
                        msg2fwd.get('typ'          , ''),
                        msg2fwd.get('msg_size'     , 0),
                        msg2fwd.get('bytes_to_send', 0),
                    ))
                else:
                    msg_done += 1


            bbs_q            = f"FWD-Q: {msg_in_q}"
            bbs_q_done       = f"FWD-Q Done: {msg_done}"
            bbs_next_q_str   = f"Next-Q: {len(bbs_next_q)}"
            gui_vars['bbs_byte_c_var'].set(bbs_byte_c)
            gui_vars['bbs_error_c_var'].set(bbs_error_c)
            gui_vars['bbs_timeout_var'].set(bbs_timeout)
            gui_vars['bbs_q_var'].set(bbs_q)
            gui_vars['bbs_q_done_var'].set(bbs_q_done)
            gui_vars['bbs_next_q_var'].set(bbs_next_q_str)

            # Next Q
            bbs_tree = gui_vars.get('next_q_tree')
            for i in bbs_tree.get_children():
                bbs_tree.delete(i)
            for ret_ent in bbs_next_q:
                bbs_tree.insert('', tk.END, values=ret_ent)

            # FWD-q
            fwd_q_tree = gui_vars.get('fwd_q_tree')
            for i in fwd_q_tree.get_children():
                fwd_q_tree.delete(i)
            for ret_ent in q_tree_data:
                fwd_q_tree.insert('', tk.END, values=ret_ent)

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            self._tree.insert('', tk.END, values=ret_ent)

    def _get_data(self):
        self._data = list(self._bbs_obj.get_active_fwd_q_tab())

    def _format_tree_data(self):
        self._tree_data = []
        for el in self._data:
            from_call = f"{el[1]}@{el[2]}"
            to_call = f"{el[3]}@{el[4]}"
            self._tree_data.append((
                f'{el[0]}',
                f'{from_call}',
                f'{to_call}',
                f'{el[5]}',  # fwd BBS
                f'{el[6]}',  # typ
                f'{el[7]}',  # sub
                f'{el[8]}',  # size
            ))

    def _sort_entry(self, col):
        """ Source: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort """
        tmp = [(self._tree.set(k, col), k) for k in self._tree.get_children('')]
        tmp.sort(reverse=self._rev_ent)
        self._rev_ent = not self._rev_ent
        for index, (val, k) in enumerate(tmp):
            self._tree.move(k, '', int(index))

    def _do_fwd(self):
        self._bbs_obj.start_man_autoFwd()

    def _do_timeout_reset(self):
        try:
            ind = self._port_tabctl.tab('current')
        except tk.TclError:
            return
        ind = str(ind['text']).replace('FWD-Port ', '')
        try:
            current_port_id = int(ind)
        except ValueError:
            return

        gui_port_var = self._port_vars.get(current_port_id, {})
        if not gui_port_var:
            return
        bbs_tabctl = gui_port_var.get('bbs_tabctl', None)
        if not hasattr(bbs_tabctl, 'tab'):
            return
        try:
            bbs_ind = bbs_tabctl.tab('current')
        except tk.TclError:
            return
        bbs_call = bbs_ind['text']
        if bbs_call not in self._bbs_vars:
            return
        self._bbs_obj.reset_bbs_timeout_fnc(bbs_call)

    def _do_block_reset(self):
        try:
            ind = self._port_tabctl.tab('current')
        except tk.TclError:
            return
        ind = str(ind['text']).replace('FWD-Port ', '')
        try:
            current_port_id = int(ind)
        except ValueError:
            return
        self._bbs_obj.reset_port_block_fnc(current_port_id)

    def _close(self):
        # self._bbs_obj = None
        self._root_win.BBS_fwd_q_list = None
        self.destroy()
