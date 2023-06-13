import tkinter as tk
from tkinter import ttk
from ax25.ax25Statistics import MH_LIST
from fnc.str_fnc import conv_time_DE_str
from string_tab import STR_TABLE


class MulticastSettings(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.flag = ''
        self.root_win = root_win
        self.lang = self.root_win.language
        ###################################
        # Vars
        self.rev_ent = False

        self.title("Multicast")
        self.style = self.root_win.style
        # self.geometry("1250x700")
        self.geometry(f"800x"
                      f"400+"
                      f"{self.root_win.main_win.winfo_x()}+"
                      f"{self.root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=50)
        self.grid_rowconfigure(1, weight=1)

        tk.Label(self, text=STR_TABLE['multicast_warning'][self.lang], foreground='red').grid(column=0, row=0)
        ##########################################################################################
        # TREE
        columns = (
            'mh_last_seen',
            'mh_port',
            'mh_call',
            'mh_last_ip',
            'mh_ip_fail'
        )
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.grid(row=1, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')

        self.tree.heading('mh_last_seen', text=STR_TABLE['last_packet'][self.lang], command=lambda: self.sort_entry('last'))
        self.tree.heading('mh_port', text='Port', command=lambda: self.sort_entry('port'))
        self.tree.heading('mh_call', text='Call', command=lambda: self.sort_entry('call'))
        self.tree.heading('mh_last_ip', text='AXIP', command=lambda: self.sort_entry('axip'))
        self.tree.heading('mh_ip_fail', text='Fail', command=lambda: self.sort_entry('axipfail'))
        self.tree.column("mh_port", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self.tree.column("mh_ip_fail", anchor=tk.CENTER, stretch=tk.NO, width=50)
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)
        self.tree.tag_configure("not_set", background='white', foreground='black')
        self.tree.tag_configure("is_set", background='green', foreground='black')

        self.tree_data = []
        self.init_tree_data()
        self.update_mh()
        self.tree.bind('<<TreeviewSelect>>', self.entry_selected)

    def entry_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[2]
            ip_add = MH_LIST.mh_get_last_ip(call)
            if ip_add in self.root_win.ax25_port_handler.multicast_ip_s:
                self.root_win.ax25_port_handler.multicast_ip_s.remove(ip_add)
            else:
                self.root_win.ax25_port_handler.multicast_ip_s.append(ip_add)

        self.update_mh()

    def update_mh(self):
        self.sort_entry()
        self.update_tree()

    def init_tree_data(self):
        self.sort_entry('last')

    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ret_ent in self.tree_data:
            self.tree.insert('', tk.END, values=ret_ent[0], tags=(ret_ent[1], ))

    def sort_entry(self, flag: str = ''):
        if not flag:
            if not self.flag:
                self.flag = 'last'
        else:
            self.flag = flag

        if self.flag:
            sort_date = MH_LIST.output_sort_mh_entr(flag_str=self.flag, reverse=self.rev_ent)
            if flag:
                if self.rev_ent:
                    self.rev_ent = False
                else:
                    self.rev_ent = True
            self.format_tree_ent(sort_date)
            self.update_tree()

    def format_tree_ent(self, mh_list):
        self.tree_data = []
        for k in mh_list:
            ent = mh_list[k]
            if ent.axip_add[1]:
                # axip_str = '{} - {}'.format(ent.axip_add[0], ent.axip_add[1])
                axip_str = ent.axip_add

                route = ''
                if ent.all_routes:
                    route = min(ent.all_routes)
                if not route:
                    is_set = 'not_set'
                    if ent.axip_add in self.root_win.ax25_port_handler.multicast_ip_s:
                        is_set = 'is_set'
                    self.tree_data.append(((
                        f'{conv_time_DE_str(ent.last_seen)}',
                        f'{ent.port_id} {ent.port}',
                        f'{ent.own_call}',
                        axip_str,
                        f'{ent.axip_fail}',
                    ), is_set)

                    )
                # print(self.tree_data)

    def __del__(self):
        # self.root_win.settings_win = None
        self.root_win = None
        # self.destroy()

    def close(self):
        self.root_win.settings_win = None
        self.destroy()

    def tasker(self):
        pass
