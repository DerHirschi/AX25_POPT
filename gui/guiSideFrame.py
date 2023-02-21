import tkinter as tk
from tkinter import ttk, Checkbutton

import main


class SideTabbedFrame:
    def __init__(self, main_cl):
        self.main_win = main_cl
        self.mh = main.GLB_MH_list
        self.style = self.main_win.style
        self.side_btn_frame_top = self.main_win.side_btn_frame_top
        self.tab_side_frame = tk.Frame(self.side_btn_frame_top, width=300, height=400)
        self.tab_side_frame.grid(row=4, column=0, columnspan=6, pady=10, sticky="nsew")
        self.tabControl = ttk.Notebook(self.tab_side_frame, height=300, width=500)
        # self.tabControl.grid(row=3, column=0, columnspan=5, sticky="nsew")

        tab1 = ttk.Frame(self.tabControl)
        self.tab2_mh = ttk.Frame(self.tabControl)
        tab3 = ttk.Frame(self.tabControl)
        self.tab4_settings = ttk.Frame(self.tabControl)

        self.tabControl.add(tab1, text='Station')
        self.tabControl.add(self.tab2_mh, text='MH')
        self.tabControl.add(tab3, text='Ports')
        self.tabControl.add(self.tab4_settings, text='Settings')
        self.tabControl.pack(expand=0, fill="both")
        self.tabControl.select(self.tab2_mh)
        ttk.Label(tab1,
                  text="TEST").grid(column=0,
                                    row=0,
                                    padx=30,
                                    pady=30)
        # MH ##########################
        self.tab2_mh.columnconfigure(0, minsize=85, weight=10)
        self.tab2_mh.columnconfigure(1, minsize=100, weight=9)
        self.tab2_mh.columnconfigure(2, minsize=50, weight=8)
        self.tab2_mh.columnconfigure(3, minsize=50, weight=8)
        self.tab2_mh.columnconfigure(4, minsize=50, weight=9)
        tk.Label(self.tab2_mh, text="Zeit", width=85).grid(row=0, column=0)
        tk.Label(self.tab2_mh, text="Call", width=100).grid(row=0, column=1)
        tk.Label(self.tab2_mh, text="PACK", width=50).grid(row=0, column=2)
        tk.Label(self.tab2_mh, text="REJ", width=50).grid(row=0, column=3)
        tk.Label(self.tab2_mh, text="Route", width=50).grid(row=0, column=4)
        self.side_mh: {int: [tk.Entry, tk.Entry, tk.Entry, tk.Entry, tk.Entry]} = {}
        for row in range(9):
            a = tk.Entry(self.tab2_mh, width=85)
            b = tk.Entry(self.tab2_mh, width=80)
            # b = tk.Button(self.tab2_mh, width=100)
            c = tk.Entry(self.tab2_mh, width=20)
            d = tk.Entry(self.tab2_mh, width=20)
            e = tk.Entry(self.tab2_mh, width=100)
            a.grid(row=row + 1, column=0)
            b.grid(row=row + 1, column=1)
            c.grid(row=row + 1, column=2)
            d.grid(row=row + 1, column=3)
            e.grid(row=row + 1, column=4)
            self.side_mh[row + 1] = [a, b, c, d, e]
        self.update_side_mh()

        # Settings ##########################
        self.sound_on = tk.IntVar()
        Checkbutton(self.tab4_settings,
                    text="Sound",
                    variable=self.sound_on,
                    ).grid(column=0,
                           row=0,
                           padx=5,
                           pady=0
                           )
        self.sound_on.set(1)
        """
        self.sound_on = tk.IntVar()
        Checkbutton(self.tab4_settings,
                    text="Test   ",
                    variable=self.sound_on,
                    ).grid(column=0,
                           row=1
                           )
        """

    def update_side_mh(self):
        mh_ent = self.mh.output_sort_entr(8)
        c = 1
        for el in mh_ent:
            self.side_mh[c][0].delete(0, tk.END)
            self.side_mh[c][0].insert(0, el.last_seen.split(' ')[1])
            self.side_mh[c][1].delete(0, tk.END)
            self.side_mh[c][1].insert(0, el.own_call)
            # self.side_mh[c][1].configure(text=el.own_call)
            self.side_mh[c][2].delete(0, tk.END)
            self.side_mh[c][2].insert(0, el.pac_n)
            self.side_mh[c][3].delete(0, tk.END)
            self.side_mh[c][3].insert(0, el.rej_n)
            self.side_mh[c][4].delete(0, tk.END)
            self.side_mh[c][4].insert(0, el.route)
            c += 1
