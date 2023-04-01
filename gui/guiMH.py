import logging
import tkinter as tk
from tkinter import Menu
from tkinter import ttk
from ax25.ax25Statistics import MyHeard
# import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class MHWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self.root_win = root_win
        self.mh = self.root_win.mh
        ###################################
        # Vars
        self.rev_ent = False
        # self.mh_win = tk.Tk()
        self.title("MHEARD")
        self.style = self.root_win.style
        self.geometry("1250x700")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        self.menubar = Menu(self)
        self.config(menu=self.menubar)
        self.menubar.add_command(label="Quit", command=self.close)
        self.menubar.add_command(label="Port-Statistik", command=lambda: self.mh.port_statistik_DB[0].plot_test_graph())
        # ############################### Columns ############################
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=50)
        self.grid_rowconfigure(1, weight=1)
        ##########################################################################################
        # TREE
        columns = (
            'mh_last_seen',
            'mh_first_seen' ,
            'mh_port', 'mh_call',
            'mh_nPackets',
            'mh_REJ',
            'mh_route',
            'mh_last_ip',
            'mh_ip_fail'
        )
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.grid(row=1, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')

        self.tree.heading('mh_last_seen', text='Letzte Paket', command=lambda: self.sort_entry('last'))
        self.tree.heading('mh_first_seen', text='Erste Paket', command=lambda: self.sort_entry('first'))
        self.tree.heading('mh_port', text='Port', command=lambda: self.sort_entry('port'))
        self.tree.heading('mh_call', text='Call', command=lambda: self.sort_entry('call'))
        self.tree.heading('mh_nPackets', text='Packets', command=lambda: self.sort_entry('pack'))
        self.tree.heading('mh_REJ', text='REJs', command=lambda: self.sort_entry('rej'))
        self.tree.heading('mh_route', text='Route', command=lambda: self.sort_entry('route'))
        self.tree.heading('mh_last_ip', text='AXIP', command=lambda: self.sort_entry('axip'))
        self.tree.heading('mh_ip_fail', text='Fail', command=lambda: self.sort_entry('axipfail'))
        self.tree.column("mh_port", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self.tree.column("mh_nPackets", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self.tree.column("mh_REJ", anchor=tk.CENTER, stretch=tk.NO, width=55)
        self.tree.column("mh_ip_fail", anchor=tk.CENTER, stretch=tk.NO, width=50)
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)

        self.tree_data = []
        self.init_tree_data()
        self.update_mh()
        self.tree.bind('<<TreeviewSelect>>', self.entry_selected)

    def entry_selected(self, event):
        for selected_item in  self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[3]
            vias = record[6]
            port = record[2]
            port = int(port.split(' ')[0])
            if vias:
                call = f'{call} {vias}'
            self.root_win.open_new_conn_win()
            self.root_win.new_conn_win.call_txt_inp.insert(tk.END, call)
            self.root_win.new_conn_win.set_port_index(port)
            self.close()

    def update_mh(self):
        self.update_tree()

    def init_tree_data(self):
        self.sort_entry('last')

    def update_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for ret_ent in self.tree_data:
            self.tree.insert('', tk.END, values=ret_ent)

    def sort_entry(self, flag: str):
        sort_date = self.mh.output_sort_mh_entr(flag_str=flag, reverse=self.rev_ent)
        if self.rev_ent:
            self.rev_ent = False
        else:
            self.rev_ent = True
        self.format_tree_ent(sort_date)
        self.update_tree()

    def format_tree_ent(self, mh_list):
        self.tree_data = []
        for k in mh_list:
            ent: MyHeard
            ent = mh_list[k]
            if ent.axip_add[1]:
                axip_str = '{} - {}'.format(ent.axip_add[0], ent.axip_add[1])
            else:
                axip_str = ''
            route = ''
            if ent.route:
                route = ent.route
            self.tree_data.append((
                f'{ent.last_seen}',
                f'{ent.first_seen}',
                f'{ent.port_id} {ent.port}',
                f'{ent.own_call}',
                f'{ent.pac_n}',
                f'{ent.rej_n}',
                ' '.join(route),
                f'{axip_str}',
                f'{ent.axip_fail}',
            ))

    def __del__(self):
        self.root_win.mh_window = None
        self.destroy()

    def close(self):
        self.root_win.mh_window = None
        self.destroy()
