import logging
import tkinter as tk
from tkinter import Menu
from tkinter import ttk
from ax25.ax25Statistics import MyHeard, MH_LIST
from fnc.str_fnc import conv_time_DE_str

logger = logging.getLogger(__name__)


class MHWin(tk.Toplevel):
    def __init__(self, root_win):
        tk.Toplevel.__init__(self)
        self._root_win = root_win
        ###################################
        # Vars
        self._rev_ent = False
        # self.mh_win = tk.Tk()
        self.title("MyHEARD")
        self.style = self._root_win.style
        # self.geometry("1250x700")
        self.geometry(f"1250x"
                      f"700+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        self._menubar = Menu(self)
        self.config(menu=self._menubar)
        self._menubar.add_command(label="Quit", command=self.close)
        self._menubar.add_command(label="Port-Statistik", command=lambda: self._root_win.open_port_stat_win())
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
        self._tree = ttk.Treeview(self, columns=columns, show='headings')
        self._tree.grid(row=1, column=0, sticky='nsew')
        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='ns')

        self._tree.heading('mh_last_seen', text='Letzte Paket', command=lambda: self._sort_entry('last'))
        self._tree.heading('mh_first_seen', text='Erste Paket', command=lambda: self._sort_entry('first'))
        self._tree.heading('mh_port', text='Port', command=lambda: self._sort_entry('port'))
        self._tree.heading('mh_call', text='Call', command=lambda: self._sort_entry('call'))
        self._tree.heading('mh_nPackets', text='Packets', command=lambda: self._sort_entry('pack'))
        self._tree.heading('mh_REJ', text='REJs', command=lambda: self._sort_entry('rej'))
        self._tree.heading('mh_route', text='Route', command=lambda: self._sort_entry('route'))
        self._tree.heading('mh_last_ip', text='AXIP', command=lambda: self._sort_entry('axip'))
        self._tree.heading('mh_ip_fail', text='Fail', command=lambda: self._sort_entry('axipfail'))
        self._tree.column("mh_port", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self._tree.column("mh_nPackets", anchor=tk.CENTER, stretch=tk.NO, width=80)
        self._tree.column("mh_REJ", anchor=tk.CENTER, stretch=tk.NO, width=55)
        self._tree.column("mh_ip_fail", anchor=tk.CENTER, stretch=tk.NO, width=50)
        # self.tree.column("# 2", anchor=tk.CENTER, stretch=tk.YES)
        # tree.column(1, stretch=True)

        self._tree_data = []
        self._init_tree_data()
        self._update_mh()
        self._tree.bind('<<TreeviewSelect>>', self.entry_selected)

    def entry_selected(self, event):
        for selected_item in self._tree.selection():
            item = self._tree.item(selected_item)
            record = item['values']
            # show a message
            call = record[3]
            vias = record[6]
            port = record[2]
            port = int(port.split(' ')[0])
            if vias:
                call = f'{call} {vias}'
            self._root_win.open_new_conn_win()
            self._root_win.new_conn_win.call_txt_inp.insert(tk.END, call)
            self._root_win.new_conn_win.set_port_index(port)
            self.close()

    def _update_mh(self):
        self._update_tree()

    def _init_tree_data(self):
        self._sort_entry('last')

    def _update_tree(self):
        for i in self._tree.get_children():
            self._tree.delete(i)
        for ret_ent in self._tree_data:
            self._tree.insert('', tk.END, values=ret_ent)

    def _sort_entry(self, flag: str):
        sort_date = MH_LIST.output_sort_mh_entr(flag_str=flag, reverse=self._rev_ent)
        if self._rev_ent:
            self._rev_ent = False
        else:
            self._rev_ent = True
        self._format_tree_ent(sort_date)
        self._update_tree()

    def _format_tree_ent(self, mh_list):
        self._tree_data = []
        for k in mh_list:
            ent: MyHeard
            ent = mh_list[k]
            if ent.axip_add[1]:
                axip_str = '{} - {}'.format(ent.axip_add[0], ent.axip_add[1])
            else:
                axip_str = ''
            route = ''
            if ent.all_routes:
                route = min(ent.all_routes)

            self._tree_data.append((
                f'{conv_time_DE_str(ent.last_seen)}',
                f'{conv_time_DE_str(ent.first_seen)}',
                f'{ent.port_id} {ent.port}',
                f'{ent.own_call}',
                f'{ent.pac_n}',
                f'{ent.rej_n}',
                ' '.join(route),
                f'{axip_str}',
                f'{ent.axip_fail}',
            ))

    def __del__(self):
        self._root_win.mh_window = None
        # self.destroy()

    def close(self):
        self._root_win.mh_window = None
        self.destroy()
