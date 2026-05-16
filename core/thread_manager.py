import threading

from cfg.logger_config import logger
from classes.CLbuffers import LockedDict


class ThreadManager:
    """ Core Thread Manager for non-GUI Threads """
    def __init__(self, popt_handler):
        logger.info("Thread-Manager: Init")
        self._popt_handler = popt_handler
        # ===================================
        self._thread_gc = LockedDict()

    # =============================
    def add_thread(self, thread: threading.Thread):
        if not hasattr(thread, 'name'):
            logger.error(f"Thread-Manager: AttributeError !")
            return False
        th_name = thread.name
        if th_name in self._thread_gc.keys():
            old_th: threading.Thread = self._thread_gc.get(th_name)
            if hasattr(old_th, 'is_alive'):
                if old_th.is_alive():
                    logger.error(f"Thread-Manager: Thread '{th_name}' is already running and still alive !")
                    del thread
                    return False
            if hasattr(old_th, 'join'):
                logger.debug(f"Thread-Manager: Joining old Thread '{th_name}'.")
                old_th.join()
            logger.debug(f"Thread-Manager: Old Thread '{th_name}' deleted.")
            del self._thread_gc[th_name]
        thread.start()
        self._thread_gc.add(th_name, thread)
        logger.debug(f"Thread-Manager: Thread '{th_name}' started!")
        logger.debug(f"Thread-Manager: {len(self._thread_gc.keys())} Threads.")
        logger.debug(f"Thread-Manager: Threads: {', '.join(self._thread_gc.keys())}")
        return True

    def is_alive_thread(self, thread_name: str):
        th = self._thread_gc.get(thread_name, None)
        if hasattr(th, 'is_alive'):
            return th.is_alive()
        return False

    # =============================
    def thread_GC_cleanup_task(self):
        #logger.debug(f"Thread-Manager: Cleanup: {len(self._thread_gc.keys())} Threads.")
        #logger.debug(f"Thread-Manager: Cleanup: Threads: {', '.join(self._thread_gc.keys())}")
        for th_name, thread in self._thread_gc.items():
            thread: threading.Thread
            if not hasattr(thread, 'is_alive'):
                logger.debug(f"Thread-Manager: Cleanup: {th_name}. No Attribute.")
                del self._thread_gc[th_name]
                continue

            if not thread.is_alive():
                logger.debug(f"Thread-Manager: Cleanup: {th_name}. Not alive.")
                if hasattr(thread, 'join'):
                    logger.debug(f"Thread-Manager: Cleanup: Joining {th_name}. Not alive.")
                    thread.join()
                logger.debug(f"Thread-Manager: Cleanup: Deleting {th_name}. Not alive.")
                del self._thread_gc[th_name]

    # =============================
    # Check Threads are alive
    def wait_for_GC_threads(self):
        n = 0
        logger.info(f"Thread-Manager: Checking {len(self._thread_gc)} Threads..")
        for th_name, th in self._thread_gc.items():
            th: threading.Thread
            if hasattr(th, 'is_alive'):
                n += 1
                while th.is_alive():
                    logger.warning(f"  !Thread {n} ({th.name}) is still alive. Waiting for Thread to be closed !")
                    th.join(timeout=1)
            logger.info(f"  -Thread {n} ({th.name}) is done. Removing Thread.")
            del self._thread_gc[th_name]
        logger.info(f"Thread-Manager: done..")

