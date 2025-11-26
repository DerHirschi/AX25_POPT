import gc
import tkinter as tk
from tkinter import ttk
from math import radians, sin, cos, sqrt, atan2

from cfg.logger_config import logger
from cfg.popt_config import POPT_CFG
from fnc.loc_fnc import coordinates_to_locator, locator_to_coordinates, locator_distance
from fnc.str_fnc import get_strTab
from gui.MapView.tkMapView_override import SafeTkinterMapView


class LocatorCalculator(tk.Toplevel):
    def __init__(self, main_win):
        tk.Toplevel.__init__(self, master=main_win.main_win)
        self._root_win      = main_win
        # MapView Thread Ctrl.
        self._quit          = False
        self.is_destroyed   = False
        self._getTabStr     = lambda str_k: get_strTab(str_k, POPT_CFG.get_guiCFG_language())
        self.title(self._getTabStr('locator_calc'))

        self.style = main_win.style
        win_width  = 800
        win_height = 650
        self.geometry(f"{win_width}x"
                      f"{win_height}+"
                      f"{self._root_win.main_win.winfo_x()}+"
                      f"{self._root_win.main_win.winfo_y()}")
        self.protocol("WM_DELETE_WINDOW", self.destroy_win)
        self.resizable(False, False)
        try:
            self.iconbitmap("favicon.ico")
        except tk.TclError:
            try:
                self.iconphoto(False, tk.PhotoImage(file='popt.png'))
            except Exception as ex:
                logger.warning(ex)
        self.lift()
        ###################################
        main_f = ttk.Frame(self)
        map_f  = ttk.Frame(self)
        main_f.pack(fill='x',    expand=False)
        map_f.pack( fill='both', expand=True)
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

        # MAP
        self._map_widget = SafeTkinterMapView(root_win=self, master=map_f, corner_radius=0)
        self._map_widget.pack(fill="both", expand=True)
        #ais_cfg = POPT_CFG.get_CFG_aprs_ais()
        #lat, lon = ais_cfg.get('ais_lat', 0.0), ais_cfg.get('ais_lon', 0.0)

        # Setze die anfängliche Position und Zoom-Level (z. B. Europa)
        self._map_widget.set_position(50.0, 10.0)
        self._map_widget.set_zoom(3)
        """
        self._map_widget.add_right_click_menu_command(
            label="Set as Pos 1",
            command=lambda e: self._set_position_from_click(e, 1)
        )
        self._map_widget.add_right_click_menu_command(
            label="Set as Pos 2",
            command=lambda e: self._set_position_from_click(e, 2)
        )
        """

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

    def tasker(self):
        if self._quit:
            self._check_threads_and_destroy()
            return True
        if hasattr(self._map_widget, 'tasker'):
            return self._map_widget.tasker()
        return False

    def clean_vars(self):
        self.loc_var_1.set('')
        self.lat_var_1.set('')
        self.lon_var_1.set('')

        self.loc_var_2.set('')
        self.lat_var_2.set('')
        self.lon_var_2.set('')
        self.dist_var.set('-- km')

        self._clear_map()
        # Optional: Karte auf Standardposition zurücksetzen
        self._map_widget.set_position(50.0, 10.0)  # Europa-Mitte
        self._map_widget.set_zoom(4)

    def calculate_coordinates(self):
        loc_1 = self.loc_var_1.get().strip().upper()
        lat_1_str = self.lat_var_1.get().strip()
        lon_1_str = self.lon_var_1.get().strip()

        loc_2 = self.loc_var_2.get().strip().upper()
        lat_2_str = self.lat_var_2.get().strip()
        lon_2_str = self.lon_var_2.get().strip()

        lat_1, lon_1, lat_2, lon_2 = 0.0, 0.0, 0.0, 0.0

        # --- Position 1 ---
        if lat_1_str.replace('.', '').replace('-', '').isdigit():
            lat_1 = float(lat_1_str)
        if lon_1_str.replace('.', '').replace('-', '').isdigit():
            lon_1 = float(lon_1_str)

        if loc_1:
            try:
                lat_1, lon_1 = locator_to_coordinates(loc_1)
                self.lat_var_1.set(f"{lat_1:.6f}")
                self.lon_var_1.set(f"{lon_1:.6f}")
            except Exception as ex:
                logger.error(ex)
                pass
        elif lat_1 and lon_1:
            try:
                loc_1 = coordinates_to_locator(lat_1, lon_1)
                self.loc_var_1.set(loc_1)
            except Exception as ex:
                logger.error(ex)
                pass

        # --- Position 2 ---
        if lat_2_str.replace('.', '').replace('-', '').isdigit():
            lat_2 = float(lat_2_str)
        if lon_2_str.replace('.', '').replace('-', '').isdigit():
            lon_2 = float(lon_2_str)

        if loc_2:
            try:
                lat_2, lon_2 = locator_to_coordinates(loc_2)
                self.lat_var_2.set(f"{lat_2:.6f}")
                self.lon_var_2.set(f"{lon_2:.6f}")
            except Exception as ex:
                logger.error(ex)
                pass
        elif lat_2 and lon_2:
            try:
                loc_2 = coordinates_to_locator(lat_2, lon_2)
                self.loc_var_2.set(loc_2)
            except Exception as ex:
                logger.error(ex)
                pass

        # --- Entfernung berechnen ---
        if loc_1 and loc_2:
            try:
                dist = locator_distance(loc_1, loc_2)
                self.dist_var.set(f'{dist:.1f} km')
            except Exception as ex:
                logger.error(ex)
                self.dist_var.set('-- km')
        else:
            self.dist_var.set('-- km')

        # --- Karte aktualisieren ---
        self._update_map()

    #################################################
    def _clear_map(self):
        """Löscht alle Marker und Linien von der Karte."""
        if hasattr(self, '_marker_1'):
            self._map_widget.delete(self._marker_1)
            del self._marker_1
        if hasattr(self, '_marker_2'):
            self._map_widget.delete(self._marker_2)
            del self._marker_2
        if hasattr(self, '_line'):
            self._map_widget.delete(self._line)
            del self._line

    def _center_map_on_points(self, lat1, lon1, lat2, lon2):
        """Zentriert die Karte auf die Mitte zwischen zwei Punkten mit passendem Zoom."""
        center_lat = (lat1 + lat2) / 2
        center_lon = (lon1 + lon2) / 2
        self._map_widget.set_position(center_lat, center_lon)

        # Zoom-Level basierend auf Entfernung anpassen
        distance_km = self._haversine(lat1, lon1, lat2, lon2)
        if distance_km > 3000:
            zoom = 2
        elif distance_km > 1000:
            zoom = 3
        elif distance_km > 300:
            zoom = 5
        elif distance_km > 100:
            zoom = 7
        else:
            zoom = 9
        self._map_widget.set_zoom(zoom)

    @staticmethod
    def _haversine( lat1, lon1, lat2, lon2):
        """Berechnet die Luftlinie in km (für Zoom-Anpassung)."""
        R = 6371.0  # Erdradius in km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def _update_map(self):
        """Aktualisiert die Karte mit Markern und Linie basierend auf aktuellen Koordinaten."""
        try:
            lat1 = float(self.lat_var_1.get() or 0)
            lon1 = float(self.lon_var_1.get() or 0)
            lat2 = float(self.lat_var_2.get() or 0)
            lon2 = float(self.lon_var_2.get() or 0)

            loc1 = self.loc_var_1.get().strip().upper()
            loc2 = self.loc_var_2.get().strip().upper()

            if not (lat1 and lon1 and lat2 and lon2):
                return

            # Alte Elemente entfernen
            self._clear_map()

            # Marker hinzufügen
            self._marker_1 = self._map_widget.set_marker(
                lat1, lon1,
                text=f"1: {loc1}" if loc1 else "Pos 1",
                marker_color_circle="black",
                marker_color_outside="red",
                font=("Arial", 10, "bold")
            )
            self._marker_2 = self._map_widget.set_marker(
                lat2, lon2,
                text=f"2: {loc2}" if loc2 else "Pos 2",
                marker_color_circle="black",
                marker_color_outside="blue",
                font=("Arial", 10, "bold")
            )

            # Linie zeichnen
            self._line = self._map_widget.set_path([(lat1, lon1), (lat2, lon2)])

            # Karte zentrieren
            self._center_map_on_points(lat1, lon1, lat2, lon2)

        except Exception as ex:
            logger.warning(f"Fehler beim Aktualisieren der Karte: {ex}")
    """            
    def _set_position_from_click(self, event, pos_num):
        '''
        Wird aufgerufen, wenn der Nutzer mit Rechtsklick auf der Karte wählt:
        'Set as Pos 1' oder 'Set as Pos 2'.
        Setzt die entsprechende Position (Locator + Lat/Lon) und aktualisiert die Karte.
        '''
        try:
            # Koordinaten vom Klick-Event (Canvas → Geokoordinaten)
            lat, lon = self._map_widget.canvas_to_position(event.x, event.y)

            # Maidenhead Locator berechnen
            loc = coordinates_to_locator(lat, lon)

            # Entsprechende Felder aktualisieren
            if pos_num == 1:
                self.loc_var_1.set(loc)
                self.lat_var_1.set(f"{lat:.6f}")
                self.lon_var_1.set(f"{lon:.6f}")
            elif pos_num == 2:
                self.loc_var_2.set(loc)
                self.lat_var_2.set(f"{lat:.6f}")
                self.lon_var_2.set(f"{lon:.6f}")

            # Karte & Berechnung aktualisieren
            self.calculate_coordinates()

        except Exception as e:
            logger.error(f"Fehler in _set_position_from_click: {e}")
    """
    #################################################
    def _add_thread_gc(self, thread):
        if hasattr(self._root_win, 'add_thread_gc'):
            self._root_win.add_thread_gc(thread)

    def _close_me(self):
        if self._quit:
            return
        #self._clear_map()

        # Threads stoppen signalisieren
        self._map_widget.running = False
        self._map_widget.image_load_queue_tasks = []
        self._map_widget.image_load_queue_results = []
        for thread in self._map_widget.get_threads():
            self._add_thread_gc(thread)
        self._root_win.locator_calc_window = None
        self._root_win.add_win_gc(self)
        # Fenster/Frame unsichtbar machen, statt direkt zu zerstören
        self._quit = True
        self.withdraw()  # Macht das gesamte Toplevel unsichtbar (alternativ: self._map_pw.pack_forget() für nur den Map-Bereich)
        # Starte asynchrones Polling, um auf Threads zu warten
        self._check_threads_and_destroy()

    def _check_threads_and_destroy(self):
        map_threads = self._map_widget.get_threads()
        all_dead = all(not thread.is_alive() for thread in map_threads)

        if all_dead:
            # Alle Threads sind tot – jetzt safe zerstören
            self._map_widget.clean_cache()
            gc.collect()
            self.destroy()
            self.is_destroyed = True

    def all_dead(self):
        map_threads = self._map_widget.get_threads()
        return all(not thread.is_alive() for thread in map_threads)

    def destroy_win(self):
        self._close_me()

    def close_window(self):
        # Close the window
        self.destroy_win()

    #def destroy_win(self):
    #    self.destroy()
    #    self._root_win.locator_calc_window = None
