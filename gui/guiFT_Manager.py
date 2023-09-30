""" GUI build with: ChatGP """
import time
import tkinter as tk
from tkinter import ttk

from ax25.ax25InitPorts import PORT_HANDLER
from fnc.str_fnc import get_kb_str_fm_bytes, conv_timestamp_delta, format_number


class FileTransferManager(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self)

        self.root = root
        # self.port_handler = self.root.ax25_port_handler
        self.lang = self.root.language
        root.settings_win = self
        self.win_height = 600
        self.win_width = 1050
        self.update_tree_param = 3  # Sec
        self.update_tree_timer = 0
        self.style = root.style
        self.title("File Transfer Manager")
        self.geometry(
            f"{self.win_width}x{self.win_height}+{self.root.main_win.winfo_x()}+{self.root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        self.progress_label_var = tk.StringVar(self)
        self.size_label_var = tk.StringVar(self)
        self.time_label_var = tk.StringVar(self)
        self.bps_label_var = tk.StringVar(self)
        self.dir_label_var = tk.StringVar(self)

        self.tx_wait_var = tk.StringVar(self)

        self.ft_obj_list = []
        self.selected_ft_obj = None
        self.create_widgets()
        self.populate_query_list()
        self.set_abort_pause_btn()

    def destroy_win(self):
        self.root.settings_win = None
        self.destroy()

    def tasker(self):
        percentage_completion = 0
        size_var = 'Size: ---,- / ---,- kb'
        time_var = 'Time: --:--:-- / --:--:--'
        bps_var = 'BPS: ---.---'
        percent_var = '---.- %'
        dir_var = ''
        if self.selected_ft_obj is not None:
            percentage_completion, data_len, data_sendet, time_spend, time_remaining, baud_rate = self.selected_ft_obj.get_ft_infos()
            percent_var = f"{percentage_completion} %"
            data_len = get_kb_str_fm_bytes(data_len)
            data_sendet = get_kb_str_fm_bytes(data_sendet)
            size_var = f'Size: {data_sendet} / {data_len}'
            t_spend = conv_timestamp_delta(time_spend)
            t_remaining = conv_timestamp_delta(time_remaining)
            time_var = f'Time: {t_spend} / {t_remaining}'
            bps_var = f"BPS: {format_number(baud_rate)}"
            dir_var = f"{self.selected_ft_obj.dir} / {self.selected_ft_obj.get_ft_info_status()}"

        self.progress_bar['value'] = percentage_completion
        self.progress_label_var.set(percent_var)
        self.size_label_var.set(size_var)
        self.time_label_var.set(time_var)
        self.bps_label_var.set(bps_var)
        self.dir_label_var.set(dir_var)

        if self.update_tree_timer < time.time():
            """ Low Prio """
            self.update_tree_timer = time.time() + self.update_tree_param
            self.populate_query_list()
            self.update_overview()

    def create_widgets(self):
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
        ttk.Label(self.progress_bar_frame, textvariable=self.progress_label_var).pack(pady=5)

        ttk.Label(self.progress_bar_frame, textvariable=self.size_label_var).pack(pady=1, anchor=tk.W)
        ttk.Label(self.progress_bar_frame, textvariable=self.time_label_var).pack(pady=1, anchor=tk.W)
        ttk.Label(self.progress_bar_frame, textvariable=self.bps_label_var).pack(pady=1, anchor=tk.W)
        ttk.Label(self.progress_bar_frame, textvariable=self.dir_label_var).pack(pady=1, anchor=tk.W)

        combobox_values = list(range(0, 361, 5))
        combobox_values = [str(x) for x in combobox_values]
        self.tx_wait_frame = ttk.Frame(self.buttons_frame)
        tk.Label(self.tx_wait_frame, text="TX-Wait: ").pack(side=tk.LEFT, padx=5)

        self.combobox = ttk.Combobox(self.tx_wait_frame,
                                     values=combobox_values,
                                     textvariable=self.tx_wait_var,
                                     width=4,
                                     state='disabled')
        self.combobox.pack(padx=5)
        self.combobox.bind("<<ComboboxSelected>>", self.tx_wait_combox_cmd)
        self.tx_wait_frame.pack(pady=5)

        self.pause_button = ttk.Button(self.buttons_frame,
                                       text="Pause",
                                       command=self.pause_btn_cmd,
                                       state='disabled')
        self.pause_button.pack(pady=5)

        self.abort_button = ttk.Button(self.buttons_frame,
                                       text="Abort",
                                       command=self.abort_btn_cmd,
                                       state='disabled')
        self.abort_button.pack(pady=5)

        # Create the top frame
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create the query list
        self.treeview_columns = ("No", "Ch", "File Name", "Size", "TX/RX", "Typ", "Status", "Progress")
        self.treeview = ttk.Treeview(self.top_frame, columns=self.treeview_columns, show="headings")
        self.treeview.heading("No", text="#")
        self.treeview.heading("Ch", text="Ch")
        self.treeview.heading("File Name", text="File Name")
        self.treeview.heading("Size", text="Size")
        self.treeview.heading("Status", text="Status")
        self.treeview.heading("TX/RX", text="TX/RX", )
        self.treeview.heading("Typ", text="Typ")
        self.treeview.heading("Progress", text="%")
        self.treeview.column("No", stretch=tk.NO, width=30)
        self.treeview.column("Ch", stretch=tk.NO, width=50)
        self.treeview.column("TX/RX", stretch=tk.NO, width=70)
        self.treeview.column("Progress", stretch=tk.NO, width=70)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar for the query list
        self.treeview_scrollbar = ttk.Scrollbar(self.top_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=self.treeview_scrollbar.set)
        self.treeview.bind("<<TreeviewSelect>>", self.on_item_selected)
        # Create the bottom frame
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(padx=10, pady=10)

        # Create the save and cancel buttons
        self.save_button = ttk.Button(self.bottom_frame, text="OK", command=self.destroy_win)
        self.save_button.pack(side=tk.LEFT, padx=5)
        """
        self.cancel_button = ttk.Button(self.bottom_frame, text="Cancel")
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        """

    def populate_query_list(self):
        data = []
        self.ft_obj_list = []
        ft_dict = PORT_HANDLER.get_all_ft_query()
        for ch_id in ft_dict:
            ft_list = ft_dict[ch_id]
            for el in ft_list:
                self.ft_obj_list.append(el)
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
        for i in self.treeview.get_children():
            self.treeview.delete(i)
        for item in data:
            self.treeview.insert("", tk.END, values=item)

        # Bind the selection event to update the overview frame
        # self.treeview.bind("<<TreeviewSelect>>", self.on_item_selected)

    def set_abort_pause_btn(self):
        if self.selected_ft_obj is not None:
            if self.selected_ft_obj.get_ft_active_status():
                self.abort_button.configure(state='normal')
                self.combobox.configure(state='normal')
                self.tx_wait_var.set(str(self.selected_ft_obj.param_wait))
            else:
                self.abort_button.configure(state='disabled')
                self.combobox.configure(state='disabled')
                self.pause_button.configure(state='disabled')
                return
            if self.selected_ft_obj.get_ft_can_pause():
                self.pause_button.configure(state='normal')
            else:
                self.pause_button.configure(state='disabled')
            return
        self.pause_button.configure(state='disabled')
        self.abort_button.configure(state='disabled')
        self.combobox.configure(state='disabled')

    def abort_btn_cmd(self, event=None):
        if self.selected_ft_obj is not None:
            self.selected_ft_obj.ft_abort()

    def pause_btn_cmd(self, event=None):
        if self.selected_ft_obj is not None:
            self.selected_ft_obj.ft_pause()

    def tx_wait_combox_cmd(self, event=None):
        if self.selected_ft_obj is not None:
            self.selected_ft_obj.param_wait = int(self.tx_wait_var.get())

    def update_overview(self):
        # num_var = "#: --\n"
        ch_var = "CH: - / Port: -\n"
        filename_var = "File Name:\n"
        size_var = "Size:\n"
        dir_var = "TX/RX: --\n"
        typ_var = "Typ:\n"
        status_var = "Status:\n"
        crc_var = "CRC:\n"
        if self.selected_ft_obj is not None:
            # num_var = f"#: {}\n"
            ch_var = f"CH: {self.selected_ft_obj.connection.ch_index} / Port: {self.selected_ft_obj.connection.port_id} {self.selected_ft_obj.connection.port_name}\n"
            filename_var = f"File Name: {self.selected_ft_obj.param_filename.split('/')[-1]}\n"
            size_var = f"Size: {get_kb_str_fm_bytes(self.selected_ft_obj.raw_data_len)}\n"
            dir_var = f"TX/RX: {self.selected_ft_obj.dir}\n"
            typ_var = f"Typ: {self.selected_ft_obj.param_protocol}\n"
            status_var = f"Status: {self.selected_ft_obj.get_ft_info_status()}\n"
            crc_var = f"CRC: {self.selected_ft_obj.raw_data_crc}/{hex(self.selected_ft_obj.raw_data_crc)}\n"

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

    def on_item_selected(self, event=None):
        selected_item = self.treeview.focus()
        item_values = self.treeview.item(selected_item)['values']

        if item_values:
            # self.overview_text.delete('1.0', tk.END)
            ft_obj_index = int(item_values[0]) - 1
            if ft_obj_index < len(self.ft_obj_list):
                if self.selected_ft_obj != self.ft_obj_list[ft_obj_index]:
                    self.selected_ft_obj = self.ft_obj_list[ft_obj_index]
            else:
                self.selected_ft_obj = None
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
        self.set_abort_pause_btn()
        self.update_overview()
        self.tasker()

