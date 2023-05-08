import tkinter as tk
from tkinter import filedialog as fd
from ax25.ax25FileTransfer import FileTX
from string_tab import STR_TABLE


class FileSend(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self)
        self.root = main_win
        main_win.settings_win = self
        self.win_height = 600
        self.win_width = 900
        self.style = main_win.style
        self.title(STR_TABLE['send_file'][self.root.language])
        # self.geometry("{}x{}".format(self.win_width, self.win_height))
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root.main_win.winfo_x()}+"
                      f"{self.root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        self.lift()
        ###############
        # VARS
        # self.port_handler = main_win.ax25_port_handler
        self.FileOBJ = None
        ##########################
        # OK, Save, Cancel
        ok_bt = tk.Button(self,
                          text=STR_TABLE['OK'][self.root.language],
                          height=1,
                          width=6,
                          command=self.ok_btn_cmd)

        cancel_bt = tk.Button(self,
                              text=STR_TABLE['cancel'][self.root.language],
                              height=1,
                              width=8,
                              command=self.chancel_btn_cmd)
        ok_bt.place(x=20, y=self.win_height - 50)
        cancel_bt.place(x=self.win_width - 120, y=self.win_height - 50)

        #################
        # Aus Datei
        _x = 20
        _y = 20
        # call_y = 100
        _label = tk.Label(self, text=STR_TABLE['file_2'][self.root.language])
        self.filename_var = tk.StringVar(self)
        self.filename = tk.Entry(self, textvariable=self.filename_var, width=50)
        # self.filename.bind("<KeyRelease>", self.on_key_press_filename_ent)
        openfile_btn = tk.Button(self, text=STR_TABLE['file_1'][self.root.language], command=self.select_files)

        _label.place(x=_x, y=_y)
        self.filename.place(x=_x + 70, y=_y)
        openfile_btn.place(x=_x + 640, y=_y - 2)

        #################
        # Protokoll
        _x = 20
        _y = 80
        _label = tk.Label(self, text=STR_TABLE['protocol'][self.root.language])
        self.protocol_var = tk.StringVar(self)
        opt = [
            'Text',
            # 'AutoBin',
        ]
        self.protocol_var.set(opt[0])
        prot = tk.OptionMenu(self, self.protocol_var, *opt, command=self.change_settings)
        prot.configure(width=8, height=1)

        _label.place(x=_x, y=_y)
        prot.place(x=_x + 100, y=_y - 5)

        #################
        #
        _x = 340
        _y = 80
        _label = tk.Label(self, text=STR_TABLE['send_if_free'][self.root.language])
        self.wait_tx_var = tk.IntVar(self)
        self.wait_tx_var.set(0)
        wait_tx = tk.Spinbox(self,
                             from_=0,
                             to=60,
                             increment=2,
                             width=3,
                             textvariable=self.wait_tx_var,
                             command=self.change_settings
                             )
        _label.place(x=_x, y=_y)
        wait_tx.place(x=_x + 290, y=_y)

        #################
        #
        _x = 20
        _y = 120
        self.file_size = tk.Label(self, text='')
        self.file_size.place(x=_x, y=_y)

    def select_files(self):
        self.attributes("-topmost", False)
        # self.root.lower
        filetypes = (
            ('text files', '*.txt'),
            ('All files', '*.*')
        )

        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='data/',
            filetypes=filetypes)

        if filenames:
            prot = self.protocol_var.get()
            wait = self.wait_tx_var.get()
            self.FileOBJ = FileTX(
                filename=filenames[0],
                protocol=prot,
                tx_wait=wait
            )
            if not self.FileOBJ.e:
                self.filename.insert(tk.END, filenames[0])
                self.filename_var.set(filenames[0])
                self.update_file_size()

    def update_file_size(self):
        if self.FileOBJ is not None:
            if not self.FileOBJ.e:
                size = len(self.FileOBJ.data)
                size = size / 1024
                text = f"{STR_TABLE['size'][self.root.language]} {size} kb"
                self.file_size.configure(text=text)
            else:
                self.file_size.configure(text='')
        else:
            self.file_size.configure(text='')

    def change_settings(self, event=None):
        if self.FileOBJ is not None:
            if not self.FileOBJ.e:
                prot = self.protocol_var.get()
                wait = self.wait_tx_var.get()
                f_n = self.filename_var.get()
                self.FileOBJ.param_filename = f_n
                self.FileOBJ.param_protocol = prot
                self.FileOBJ.param_wait = wait
                self.FileOBJ.change_settings()
        self.update_file_size()

    def chancel_btn_cmd(self):
        if self.FileOBJ is not None:
            del self.FileOBJ
        self.destroy_win()

    def ok_btn_cmd(self):
        self.change_settings()
        if self.FileOBJ is not None:
            if not self.FileOBJ.e:
                # self.FileOBJ.reset_timer()
                conn = self.root.get_conn()
                if conn:
                    if self.FileOBJ not in conn.ft_tx_queue:
                        conn.ft_tx_queue.append(self.FileOBJ)
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.root.settings_win = None

    def tasker(self):
        pass
