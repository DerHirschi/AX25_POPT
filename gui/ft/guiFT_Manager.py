""" GUI build with: ChatGP """
import time
import tkinter as tk
from tkinter import ttk, Menu

from ax25.ax25InitPorts import PORT_HANDLER
from cfg.popt_config import POPT_CFG
from cfg.string_tab import STR_TABLE
from fnc.str_fnc import get_kb_str_fm_bytes, conv_timestamp_delta, format_number


class FileTransferManager(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self)

        self.overview_frame = None
        self._root_win = root
        # self.port_handler = self.root.ax25_port_handler
        self._lang = POPT_CFG.get_guiCFG_language()
        self.win_height = 600
        self.win_width = 1050
        self.style = root.style
        self.title("File Transfer Manager")
        self.geometry(
            f"{self.win_width}x{self.win_height}+{self._root_win.main_win.winfo_x()}+{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self._update_tree_param = 3  # Sec
        self._update_tree_timer = 0
        self._progress_label_var = tk.StringVar(self)
        self._size_label_var = tk.StringVar(self)
        self._time_label_var = tk.StringVar(self)
        self._bps_label_var = tk.StringVar(self)
        self._dir_label_var = tk.StringVar(self)

        self._tx_wait_var = tk.StringVar(self)

        self._ft_obj_list = []
        self._selected_ft_obj = None
        self._create_widgets()
        self._populate_query_list()
        self._set_abort_pause_btn()
        self._init_menubar()
        root.settings_win = self

    def _init_menubar(self):
        menubar = Menu(self, tearoff=False)
        self.config(menu=menubar)
        MenuVerb = Menu(menubar, tearoff=False)
        MenuVerb.add_command(label=STR_TABLE['send_file'][self._lang], command=self._open_txFile_win)
        menubar.add_cascade(label=STR_TABLE['file_1'][self._lang], menu=MenuVerb, underline=0)

    def destroy_win(self):
        self._root_win.settings_win = None
        self.destroy()

    def tasker(self):
        percentage_completion = 0
        size_var = 'Size: ---,- / ---,- kb'
        time_var = 'Time: --:--:-- / --:--:--'
        bps_var = 'BPS: ---.---'
        percent_var = '---.- %'
        dir_var = ''
        if self._selected_ft_obj is not None:
            percentage_completion, data_len, data_sendet, time_spend, time_remaining, baud_rate = self._selected_ft_obj.get_ft_infos()
            percent_var = f"{percentage_completion} %"
            data_len = get_kb_str_fm_bytes(data_len)
            data_sendet = get_kb_str_fm_bytes(data_sendet)
            size_var = f'Size: {data_sendet} / {data_len}'
            t_spend = conv_timestamp_delta(time_spend)
            t_remaining = conv_timestamp_delta(time_remaining)
            time_var = f'Time: {t_spend} / {t_remaining}'
            bps_var = f"BPS: {format_number(baud_rate)}"
            dir_var = f"{self._selected_ft_obj.dir} / {self._selected_ft_obj.get_ft_info_status()}"

        self.progress_bar['value'] = percentage_completion
        self._progress_label_var.set(percent_var)
        self._size_label_var.set(size_var)
        self._time_label_var.set(time_var)
        self._bps_label_var.set(bps_var)
        self._dir_label_var.set(dir_var)

        if self._update_tree_timer < time.time():
            """ Low Prio """
            self._update_tree_timer = time.time() + self._update_tree_param
            self._populate_query_list()
            self._update_overview()

    def _create_widgets(self):
        # Create the overview frame
        self.overview_frame = ttk.Frame(self)
        self.overview_frame.pack(padx=10, pady=10)

        self.overview_frame.columnconfigure(0, minsize=5, weight=0)
        self.overview_frame.columnconfigure(1, weight=1)
        self.overview_frame.columnconfigure(2, minsize=80, weight=0)
        self.overview_frame.columnconfigure(3, weight=1)
        self.overview_frame.columnconfigure(4, minsize=80, weight=0)
        self.overview_frame.columnconfigure(5, weight=1)
        self.overview_frame.columnconfigure(6, minsize=5, weight=0)

        # Create the overview text on the left side
        self.overview_text = tk.Text(self.overview_frame, height=6, width=50)
        self.overview_text.grid(column=1, row=0, sticky='nsew')
        # self.overview_text.pack(side=tk.LEFT, anchor=tk.W)

        # Create the progress bar and label below the overview text
        self.progress_bar_frame = ttk.Frame(self.overview_frame)
        self.progress_bar_frame.grid(column=3, row=0, sticky='nsew')
        # self.progress_bar_frame.pack(side=tk.LEFT, padx=10, pady=20)

        # Create the buttons and combobox on the right side
        self.buttons_frame = ttk.Frame(self.overview_frame)
        self.buttons_frame.grid(column=5, row=0, sticky='nsew')
        # self.buttons_frame.pack(side=tk.LEFT, padx=10, pady=20, anchor=tk.E)


        self.progress_bar = ttk.Progressbar(self.progress_bar_frame, length=200, mode='determinate')
        self.progress_bar.pack(pady=5)
        ttk.Label(self.progress_bar_frame, textvariable=self._progress_label_var).pack(pady=5)

        ttk.Label(self.progress_bar_frame, textvariable=self._size_label_var).pack(pady=1, anchor=tk.W)
        ttk.Label(self.progress_bar_frame, textvariable=self._time_label_var).pack(pady=1, anchor=tk.W)
        ttk.Label(self.progress_bar_frame, textvariable=self._bps_label_var).pack(pady=1, anchor=tk.W)
        ttk.Label(self.progress_bar_frame, textvariable=self._dir_label_var).pack(pady=1, anchor=tk.W)

        combobox_values = list(range(0, 361, 5))
        combobox_values = [str(x) for x in combobox_values]
        tx_wait_frame = ttk.Frame(self.buttons_frame)
        tk.Label(tx_wait_frame, text="TX-Wait: ").pack(side=tk.LEFT, padx=5)

        self._combobox = ttk.Combobox(tx_wait_frame,
                                      values=combobox_values,
                                      textvariable=self._tx_wait_var,
                                      width=4,
                                      state='disabled')
        self._combobox.pack(padx=5)
        self._combobox.bind("<<ComboboxSelected>>", self._tx_wait_combox_cmd)
        tx_wait_frame.pack(pady=5)

        self._pause_button = ttk.Button(self.buttons_frame,
                                        text="Pause",
                                        command=self._pause_btn_cmd,
                                        state='disabled')
        self._pause_button.pack(pady=5)

        self._abort_button = ttk.Button(self.buttons_frame,
                                        text="Abort",
                                        command=self._abort_btn_cmd,
                                        state='disabled')
        self._abort_button.pack(pady=5)

        # Create the top frame
        top_frame = ttk.Frame(self)
        top_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create the query list
        treeview_columns = ("No", "Ch", "File Name", "Size", "TX/RX", "Typ", "Status", "Progress")
        self._treeview = ttk.Treeview(top_frame, columns=treeview_columns, show="headings")
        self._treeview.heading("No", text="#")
        self._treeview.heading("Ch", text="Ch")
        self._treeview.heading("File Name", text="File Name")
        self._treeview.heading("Size", text="Size")
        self._treeview.heading("Status", text="Status")
        self._treeview.heading("TX/RX", text="TX/RX", )
        self._treeview.heading("Typ", text="Typ")
        self._treeview.heading("Progress", text="%")
        self._treeview.column("No", stretch=tk.NO, width=30)
        self._treeview.column("Ch", stretch=tk.NO, width=50)
        self._treeview.column("TX/RX", stretch=tk.NO, width=70)
        self._treeview.column("Progress", stretch=tk.NO, width=70)
        self._treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar for the query list
        treeview_scrollbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=self._treeview.yview)
        treeview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._treeview.configure(yscrollcommand=treeview_scrollbar.set)
        self._treeview.bind("<<TreeviewSelect>>", self._on_item_selected)
        # Create the bottom frame
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(padx=10, pady=10)

        # Create the save and cancel buttons
        ttk.Button(bottom_frame, text="OK", command=self.destroy_win).pack(side=tk.LEFT, padx=5)
        """
        self.cancel_button = ttk.Button(self.bottom_frame, text="Cancel")
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        """

    def _populate_query_list(self):
        data = []
        self._ft_obj_list = []
        ft_dict = PORT_HANDLER.get_all_ft_query()
        for ch_id in ft_dict:
            ft_list = ft_dict[ch_id]
            for el in ft_list:
                self._ft_obj_list.append(el)
                data.append(
                    (
                        str(len(data) + 1),
                        str(ch_id),
                        el.param_filename.split('/')[-1],
                        get_kb_str_fm_bytes(el.raw_data_len),
                        el.dir,
                        el.param_protocol,
                        el.get_ft_info_status(),
                        str(el.get_ft_info_percentage()),
                    )
                )
        for i in self._treeview.get_children():
            self._treeview.delete(i)
        for item in data:
            self._treeview.insert("", tk.END, values=item)

        # Bind the selection event to update the overview frame
        # self.treeview.bind("<<TreeviewSelect>>", self.on_item_selected)

    def _set_abort_pause_btn(self):
        if self._selected_ft_obj is not None:
            if self._selected_ft_obj.get_ft_active_status():
                self._abort_button.configure(state='normal')
                self._combobox.configure(state='normal')
                self._tx_wait_var.set(str(self._selected_ft_obj.param_wait))
            else:
                self._abort_button.configure(state='disabled')
                self._combobox.configure(state='disabled')
                self._pause_button.configure(state='disabled')
                return
            if self._selected_ft_obj.get_ft_can_pause():
                self._pause_button.configure(state='normal')
            else:
                self._pause_button.configure(state='disabled')
            return
        self._pause_button.configure(state='disabled')
        self._abort_button.configure(state='disabled')
        self._combobox.configure(state='disabled')

    def _abort_btn_cmd(self, event=None):
        if self._selected_ft_obj is not None:
            self._selected_ft_obj.ft_abort()

    def _pause_btn_cmd(self, event=None):
        if self._selected_ft_obj is not None:
            self._selected_ft_obj.ft_pause()

    def _tx_wait_combox_cmd(self, event=None):
        if self._selected_ft_obj is not None:
            self._selected_ft_obj.param_wait = int(self._tx_wait_var.get())

    def _update_overview(self):
        # num_var = "#: --\n"
        ch_var = "CH: - / Port: -\n"
        filename_var = "File Name:\n"
        size_var = "Size:\n"
        dir_var = "TX/RX: --\n"
        typ_var = "Typ:\n"
        status_var = "Status:\n"
        crc_var = "CRC:\n"
        if self._selected_ft_obj is not None:
            # num_var = f"#: {}\n"
            ch_var = f"CH: {self._selected_ft_obj.connection.ch_index} / Port: {self._selected_ft_obj.connection.port_id} {self._selected_ft_obj.connection.port_name}\n"
            filename_var = f"File Name: {self._selected_ft_obj.param_filename.split('/')[-1]}\n"
            size_var = f"Size: {get_kb_str_fm_bytes(self._selected_ft_obj.raw_data_len)}\n"
            dir_var = f"TX/RX: {self._selected_ft_obj.dir}\n"
            typ_var = f"Typ: {self._selected_ft_obj.param_protocol}\n"
            status_var = f"Status: {self._selected_ft_obj.get_ft_info_status()}\n"
            crc_var = f"CRC: {self._selected_ft_obj.raw_data_crc}/{hex(self._selected_ft_obj.raw_data_crc)}\n"

        self.overview_text.delete('1.0', tk.END)
        self.overview_text.insert(tk.END, "".join([
            # num_var,
            ch_var,
            filename_var,
            size_var,
            dir_var,
            typ_var,
            status_var,
            crc_var
        ]))

    def _on_item_selected(self, event=None):
        selected_item = self._treeview.focus()
        item_values = self._treeview.item(selected_item)['values']

        if item_values:
            # self.overview_text.delete('1.0', tk.END)
            ft_obj_index = int(item_values[0]) - 1
            if ft_obj_index < len(self._ft_obj_list):
                if self._selected_ft_obj != self._ft_obj_list[ft_obj_index]:
                    self._selected_ft_obj = self._ft_obj_list[ft_obj_index]
            else:
                self._selected_ft_obj = None
            """
            self.overview_text.insert(tk.END, f"CH: {item_values[1]}\n")
            self.overview_text.insert(tk.END, f"File Name: {item_values[2]}\n")

            self.overview_text.insert(tk.END, f"Size: {item_values[3]}\n")
            self.overview_text.insert(tk.END, f"TX/RX: {item_values[4]}\n")
            self.overview_text.insert(tk.END, f"Typ: {item_values[5]}\n")
            self.overview_text.insert(tk.END, f"Status: {item_values[6]}\n")
            if self.selected_ft_obj is not None:
                self.overview_text.insert(tk.END, f"CRC: {self.selected_ft_obj.raw_data_crc}/{hex(self.selected_ft_obj.raw_data_crc)}\n")
            """
        # Update the progress bar and label
        # self.progress_bar['value'] = item_values[7]
        # self.progress_label.configure(text=f"{item_values[7]}%")
        self._set_abort_pause_btn()
        self._update_overview()
        self.tasker()

    def _open_txFile_win(self):
        self._root_win.open_window('ft_send')

