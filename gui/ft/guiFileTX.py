import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from ax25.ax25FileTransfer import FileTransport
from cfg.constant import FT_MODES
from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.str_fnc import get_strTab


class FileSend(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self._root_win = main_win
        main_win.FileSend_win = self
        self.win_height = 200
        self.win_width  = 780
        self.style      = main_win.style
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())

        self.title(self._getTabStr('send_file'))
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='favicon.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ###############
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ###############
        # VARS
        # self.port_handler = main_win.ax25_port_handler
        self.FileOBJ = None
        ##########################
        # OK, Save, Cancel
        ok_bt = ttk.Button(main_f,
                          text=self._getTabStr('OK'),
                          # height=1,
                          width=6,
                          command=self._ok_btn_cmd)

        cancel_bt = ttk.Button(main_f,
                              text=self._getTabStr('cancel'),
                              #height=1,
                              width=8,
                              command=self._chancel_btn_cmd)
        ok_bt.place(x=20, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        #################
        # Aus Datei
        _x = 20
        _y = 20
        # call_y = 100
        _label = ttk.Label(main_f, text=self._getTabStr('file_2'))
        self.filename_var = tk.StringVar(self)
        self.filename = ttk.Entry(main_f, textvariable=self.filename_var, width=50)
        # self.filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        openfile_btn = ttk.Button(main_f, text=self._getTabStr('file_1'), command=self._select_files)

        _label.place(x=_x, y=_y)
        self.filename.place(x=_x + 70, y=_y)
        openfile_btn.place(x=_x + 640, y=_y - 2)

        #################
        # Protokoll
        _x = 20
        _y = 80
        _label = ttk.Label(main_f, text=self._getTabStr('protocol'))
        self.protocol_var = tk.StringVar(self)
        opt = FT_MODES
        opt = [opt[0]] + opt
        self.protocol_var.set(opt[0])
        prot = ttk.OptionMenu(main_f, self.protocol_var, *opt, command=self._change_settings)
        # prot.configure(width=8, height=1)

        _label.place(x=_x, y=_y)
        prot.place(x=_x + 100, y=_y - 5)

        #################
        #
        _x = 340
        _y = 80
        _label = ttk.Label(main_f, text=self._getTabStr('send_if_free'))
        self.wait_tx_var = tk.IntVar(self)
        self.wait_tx_var.set(0)
        wait_tx = ttk.Spinbox(main_f,
                             from_=0,
                             to=60,
                             increment=2,
                             width=3,
                             textvariable=self.wait_tx_var,
                             command=self._change_settings
                             )
        _label.place(x=_x, y=_y)
        wait_tx.place(x=_x + 290, y=_y)

        self.conn = self._root_win.get_conn()
        if self.conn is None:
            self.conn = False
        if not self.conn:
            ok_bt.configure(state='disabled')
            openfile_btn.configure(state='disabled')

        #################
        #
        _x = 20
        _y = 120
        self.file_size = ttk.Label(main_f, text='')
        self.file_size.place(x=_x, y=_y)

    def _select_files(self):

        self.attributes("-topmost", False)
        # self.root.lower
        filetypes = (
            ('All files', '*.*'),
            ('text files', '*.txt'),
        )

        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='data/',
            filetypes=filetypes,
            parent=self)

        if filenames:
            prot = self.protocol_var.get()
            wait = self.wait_tx_var.get()
            self.FileOBJ = FileTransport(
                filename=filenames[0],
                protocol=prot,
                connection=self.conn,
                tx_wait=wait,
                direction='TX'
            )
            if not self.FileOBJ.e:
                self.filename.insert(tk.END, filenames[0])
                self.filename_var.set(filenames[0])
                self._update_file_size()

    def _update_file_size(self):
        if self.FileOBJ is not None:
            if not self.FileOBJ.e:
                size = len(self.FileOBJ.raw_data)
                size = size / 1024
                text = f"{self._getTabStr('size')} {size} kb"
                self.file_size.configure(text=text)
            else:
                self.file_size.configure(text='')
        else:
            self.file_size.configure(text='')

    def _change_settings(self, event=None):
        if self.FileOBJ is not None:
            if not self.FileOBJ.e:
                prot = self.protocol_var.get()
                wait = self.wait_tx_var.get()
                f_n = self.filename_var.get()
                self.FileOBJ.param_filename = f_n
                self.FileOBJ.param_protocol = prot
                self.FileOBJ.param_wait = wait
                self.FileOBJ.ft_init()
        self._update_file_size()

    def _chancel_btn_cmd(self):
        if self.FileOBJ is not None:
            del self.FileOBJ
        self.destroy_win()

    def _ok_btn_cmd(self):
        self._change_settings()
        if self.FileOBJ is not None:
            if not self.FileOBJ.e:
                # self.FileOBJ.reset_timer()
                conn = self._root_win.get_conn()
                if conn is not None:
                    if self.FileOBJ not in conn.ft_queue:
                        conn.ft_queue.append(self.FileOBJ)
        self.destroy_win()

    def destroy_win(self):
        self._root_win.FileSend_win = None
        self.destroy()

    def tasker(self):
        pass
