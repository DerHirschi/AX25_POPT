import threading
import time
from tkintermapview import TkinterMapView

from cfg.logger_config import logger


class SafeTkinterMapView(TkinterMapView):
    def __init__(self, root_win, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self._root_win = root_win
        while self.pre_cache_thread.is_alive():
            time.sleep(0.03)

        self._task_timer = time.time() + 0.1
        self.last_pre_cache_position = None
        self._radius = 1
        self._image_load_thread_pool = []
        self.running = True
        self.pre_cache_thread = threading.Thread(daemon=False, target=self._pre_cache)
        self.pre_cache_thread.start()

    """Override's"""
    def pre_cache(self):
        pass

    def update_canvas_tile_images(self):
        pass

    def load_images_background(self):
        pass

    def tasker(self):
        if not self.running:
            return False
        if time.time() < self._task_timer:
            return False
        self._task_timer = time.time() + 0.1
        self._pre_cache_task()
        self._update_canvas_tile_images()
        self._img_loader_task()
        self._clean_cache()  # Cache-Cleanup im Hauptthread
        return True

    def _img_loader_task(self):
        for thr in list(self._image_load_thread_pool):
            if not thr.is_alive():
                self._image_load_thread_pool.remove(thr)

        for i in range(15 - len(self._image_load_thread_pool)):  # Erhöht auf 15 für bessere Zoom-Performance
            image_load_thread = threading.Thread(daemon=False, target=self._load_images_background)
            image_load_thread.start()
            self._image_load_thread_pool.append(image_load_thread)

    def _pre_cache_task(self):
        if self.pre_cache_thread.is_alive():
            return False
        self.pre_cache_thread.join()
        self.pre_cache_thread = threading.Thread(daemon=False, target=self._pre_cache)
        self.pre_cache_thread.start()
        return True

    def _load_images_background(self):
        n = 15
        while len(self.image_load_queue_tasks) > 0 and n and self.running:
            n -= 1
            task = self.image_load_queue_tasks.pop()
            zoom = task[0][0]
            x, y = task[0][1], task[0][2]
            canvas_tile = task[1]

            image = self.get_tile_image_from_cache(zoom, x, y)
            if image is False:
                # request_image NICHT direkt im Thread aufrufen, sondern Daten vorbereiten
                try:
                    image = self.request_image(zoom, x, y, db_cursor=None)
                except Exception as e:
                    print(f"Error in request_image: {e}")
                    self.image_load_queue_tasks.append(task)
                    continue
                if image is None:
                    self.image_load_queue_tasks.append(task)
                    continue

            # Ergebnis in die Queue für Hauptthread
            self.image_load_queue_results.append(((zoom, x, y), canvas_tile, image))

    def _update_canvas_tile_images(self):
        n = 15
        while self.image_load_queue_results and self.running and n:
            result = self.image_load_queue_results.pop(0)
            zoom, x, y = result[0][0], result[0][1], result[0][2]
            canvas_tile = result[1]
            image = result[2]
            if zoom == round(self.zoom):
                try:
                    canvas_tile.set_image(image)  # Im Hauptthread
                except Exception as e:
                    print(f"Error in set_image: {e}")
            n -= 1

    def _pre_cache(self):
        if not hasattr(self, '_radius'):
            return
        if not self.running:
            return
        radius = self._radius
        zoom = round(self.zoom)
        if self.last_pre_cache_position != self.pre_cache_position:
            self.last_pre_cache_position = self.pre_cache_position
            zoom = round(self.zoom)
            radius = 1

        if self.last_pre_cache_position is not None and radius <= 8 and self.running:
            for x in range(self.pre_cache_position[0] - radius, self.pre_cache_position[0] + radius + 1):
                if not self.running:
                    return
                if f"{zoom}{x}{self.pre_cache_position[1] + radius}" not in self.tile_image_cache and self.running:
                    self.request_image(zoom, x, self.pre_cache_position[1] + radius, db_cursor=None)
                if f"{zoom}{x}{self.pre_cache_position[1] - radius}" not in self.tile_image_cache and self.running:
                    self.request_image(zoom, x, self.pre_cache_position[1] - radius, db_cursor=None)

            for y in range(self.pre_cache_position[1] - radius, self.pre_cache_position[1] + radius + 1):
                if not self.running:
                    return
                if f"{zoom}{self.pre_cache_position[0] + radius}{y}" not in self.tile_image_cache and self.running:
                    self.request_image(zoom, self.pre_cache_position[0] + radius, y, db_cursor=None)
                if f"{zoom}{self.pre_cache_position[0] - radius}{y}" not in self.tile_image_cache and self.running:
                    self.request_image(zoom, self.pre_cache_position[0] - radius, y, db_cursor=None)

            radius += 1

        # Kein del hier – Cache-Cleanup in _clean_cache

    def _clean_cache(self):
        """ Cache-Cleanup im Hauptthread """
        while len(self.tile_image_cache) > 2000 and self.running:
            print(f"Del Cache, size: {len(self.tile_image_cache)}")  # Debugging
            del self.tile_image_cache[list(self.tile_image_cache.keys())[0]]
        #if hasattr(self._root_win, 'set_MapView_cache'):
        #    self._root_win.set_MapView_cache(self.tile_image_cache)

    def get_threads(self):
        return self._image_load_thread_pool + [self.pre_cache_thread]

    def clean_cache(self):
        while self.tile_image_cache:
            del self.tile_image_cache[list(self.tile_image_cache.keys())[0]]
        logger.debug("MapView: clean_cache() - Done")

    def destroy(self):
        self.running = False
        self.image_load_queue_tasks = []
        self.image_load_queue_results = []
        self._clean_cache()  # Cache leeren im Hauptthread
        self.tile_image_cache.clear()  # Sicherstellen, dass alle Images freigegeben werden
        super().destroy()