import tkinter as tk
from tkinter import ttk

from cfg.popt_config import POPT_CFG
from fnc.loc_fnc import coordinates_to_locator, locator_to_coordinates, locator_distance
from fnc.str_fnc import get_strTab


class LocatorCalculator(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self.root = main_win
        self._getTabStr = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.title(self._getTabStr('locator_calc'))

        self.style = main_win.style
        self.win_height = 250
        self.win_width  = 800
        self.geometry(f"{self.win_width}x"
                      f"{self.win_height}+"
                      f"{self.root.main_win.winfo_x()}+"
                      f"{self.root.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            pass
        self.lift()
        ###################################
        main_f = ttk.Frame(self)
        main_f.pack(fill=tk.BOTH, expand=True)
        ###################################
        self.loc_var_1 = tk.StringVar(self)
        self.lat_var_1 = tk.StringVar(self)
        self.lon_var_1 = tk.StringVar(self)

        self.loc_var_2 = tk.StringVar(self)
        self.lat_var_2 = tk.StringVar(self)
        self.lon_var_2 = tk.StringVar(self)

        self.dist_var = tk.StringVar(self)
        self.dist_var.set('-- km')
        # Create frame for script info
        script_info_frame = ttk.Frame(main_f)
        script_info_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Create label for script author
        author_label = ttk.Label(script_info_frame, text="Script by: 4X1MD")
        author_label.pack()

        # Create label for script repository
        repo_label = ttk.Label(script_info_frame, text="https://github.com/4x1md/qth_locator_functions.git")
        repo_label.pack()

        # Create frame for left side
        left_frame = ttk.Frame(main_f)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Create Locator entry field on left side
        locator_label_left = ttk.Label(left_frame, text="Locator:")
        locator_label_left.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        locator_entry_left = ttk.Entry(left_frame, width=10, textvariable=self.loc_var_1)
        locator_entry_left.grid(row=0, column=1, padx=5, pady=5)

        # Create Latitude entry field on left side
        latitude_label_left = ttk.Label(left_frame, text="Latitude:")
        latitude_label_left.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        latitude_entry_left = ttk.Entry(left_frame, width=10, textvariable=self.lat_var_1)
        latitude_entry_left.grid(row=1, column=1, padx=5, pady=5)

        # Create Longitude entry field on left side
        longitude_label_left = ttk.Label(left_frame, text="Longitude:")
        longitude_label_left.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        longitude_entry_left = ttk.Entry(left_frame, width=10,  textvariable=self.lon_var_1)
        longitude_entry_left.grid(row=2, column=1, padx=5, pady=5)

        # Create frame for right side
        right_frame = ttk.Frame(main_f)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Create Locator entry field on right side
        locator_label_right = ttk.Label(right_frame, text="Locator:")
        locator_label_right.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        locator_entry_right = ttk.Entry(right_frame, width=10,  textvariable=self.loc_var_2)
        locator_entry_right.grid(row=0, column=1, padx=5, pady=5)

        # Create Latitude entry field on right side
        latitude_label_right = ttk.Label(right_frame, text="Latitude:")
        latitude_label_right.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        latitude_entry_right = ttk.Entry(right_frame, width=10,  textvariable=self.lat_var_2)
        latitude_entry_right.grid(row=1, column=1, padx=5, pady=5)

        # Create Longitude entry field on right side
        longitude_label_right = ttk.Label(right_frame, text="Longitude:")
        longitude_label_right.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        longitude_entry_right = ttk.Entry(right_frame, width=10,  textvariable=self.lon_var_2)
        longitude_entry_right.grid(row=2, column=1, padx=5, pady=5)

        # Create label for result
        result_label = ttk.Label(main_f, textvariable=self.dist_var)
        result_label.pack(pady=10)


        # Create frame for buttons
        button_frame = ttk.Frame(main_f)
        button_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Create Calculate button
        calculate_button = ttk.Button(button_frame, text=self._getTabStr('go'), command=self.calculate_coordinates)
        calculate_button.pack(side=tk.LEFT, padx=5)

        # Create Close button
        close_button = ttk.Button(button_frame, text=self._getTabStr('close'), command=self.close_window)
        close_button.pack(side=tk.LEFT, padx=5)

        # Create frame for buttons
        button_frame = ttk.Frame(main_f)
        button_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Create Calculate button
        calculate_button = ttk.Button(button_frame, text=self._getTabStr('delete'), command=self.clean_vars)
        calculate_button.pack(side=tk.LEFT, padx=5)
        main_win.locator_calc_window = self

    def clean_vars(self):
        self.loc_var_1.set('')
        self.lat_var_1.set('')
        self.lon_var_1.set('')

        self.loc_var_2.set('')
        self.lat_var_2.set('')
        self.lon_var_2.set('')
        self.dist_var.set('-- km')

    def calculate_coordinates(self):
        loc_1 = self.loc_var_1.get()
        lat_1 = self.lat_var_1.get()
        lon_1 = self.lon_var_1.get()

        loc_2 = self.loc_var_2.get()
        lat_2 = self.lat_var_2.get()
        lon_2 = self.lon_var_2.get()

        if not lat_1.isdigit():
            lat_1 = 0
        else:
            lat_1 = float(lat_1)
        if not lon_1.isdigit():
            lon_1 = 0
        else:
            lon_1 = float(lon_1)
        if not lat_2.isdigit():
            lat_2 = 0
        else:
            lat_2 = float(lat_2)
        if not lon_2.isdigit():
            lon_2 = 0
        else:
            lon_2 = float(lon_2)

        if lat_1 and lon_1:
            if not loc_1:
                loc_1 = coordinates_to_locator(lat_1, lon_1)
                self.loc_var_1.set(loc_1)

        if lat_2 and lon_2:
            if not loc_2:
                loc_2 = coordinates_to_locator(lat_2, lon_2)
                self.loc_var_2.set(loc_2)

        if loc_1:
            if not lat_1 or not lon_1:
                lat_1, lon_1 = locator_to_coordinates(loc_1)
                self.lat_var_1.set(str(lat_1))
                self.lon_var_1.set(str(lon_1))

        if loc_2:
            if not lat_2 or not lon_2:
                lat_2, lon_2 = locator_to_coordinates(loc_2)
                self.lat_var_2.set(str(lat_2))
                self.lon_var_2.set(str(lon_2))

        if loc_1 and loc_2:
            dist = locator_distance(loc_1, loc_2)
            self.dist_var.set(f'{dist} km')
        else:
            self.dist_var.set('-- km')

    def close_window(self):
        # Close the window
        self.destroy_win()

    def destroy_win(self):
        self.destroy()
        self.root.locator_calc_window = None
