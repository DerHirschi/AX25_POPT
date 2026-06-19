from threading import RLock
from cfg.logger_config import logger


# ======================================================
class ListBuffer:
    """ Thread locked List """
    def __init__(self, thread_lock_timer=0.001):
        self._buffer: list      = []
        self._threadLock        = RLock()

    @property
    def buffer_read(self):
        if self.is_empty:
            return None
        with self._threadLock:
            ret = self._buffer.pop(0)
            return ret

    def buffer_read_n(self, n: int):
        if self.is_empty:
            return None
        with self._threadLock:
            ret = self._buffer[:n]
            self._buffer = self._buffer[n:]
            return ret

    def buffer_read_all(self):
        if self.is_empty:
            return []
        with self._threadLock:
            ret = list(self._buffer)
            self._buffer.clear()
            return ret

    def buffer_write(self, data):
        with self._threadLock:
            self._buffer.append(data)

    def buffer_insert(self, data):
        """ Insert Data at the beginning """
        with self._threadLock:
            self._buffer = [data] + self._buffer

    def buffer_clear(self):
        with self._threadLock:
            self._buffer.clear()

    def buffer_pop(self, i=0):
        with self._threadLock:
            self._buffer.pop(i)

    def buffer_remove(self, value):
        with self._threadLock:
            self._buffer.remove(value)

    @property
    def buffer_get(self):
        with self._threadLock:
            return list(self._buffer)

    @property
    def buffer_get_and_lock(self):
        with self._threadLock:
            return self._buffer

    def buffer_set_and_unlock(self, new_buffer: list):
        with self._threadLock:
            self._buffer = new_buffer

    # == Read Only / property
    @property
    def is_empty(self):
        with self._threadLock:
            return bool(not self._buffer)

    @property
    def length(self):
        with self._threadLock:
            return len(self._buffer)

# ======================================================
class ByteArrayBuffer:
    """ Thread locked bytearray """
    def __init__(self, thread_lock_timer=0.001):
        self._buffer: bytearray = bytearray()
        self._threadLock        = RLock()

    def buffer_read(self, bytes_to_read: int):
        with self._threadLock:
            ret          = self._buffer[:bytes_to_read]
            self._buffer = self._buffer[len(ret):]
            return ret

    def buffer_flush(self):
        with self._threadLock:
            ret          = bytearray(self._buffer)
            self._buffer = bytearray()
            return ret

    def buffer_write(self, data):
        if not isinstance(data, (bytes, bytearray)):
            return False
        with self._threadLock:
            self._buffer.extend(data)
            return True

    def buffer_set(self, data):
        if not isinstance(data, (bytes, bytearray)):
            logger.error(f"Error buffer_set : {data}  - {type(data)}")
            return False
        with self._threadLock:
            self._buffer = data
            return True

    def buffer_clear(self):
        with self._threadLock:
            self._buffer = bytearray()

    # == Read Only / property
    @property
    def buffer_get(self):
        with self._threadLock:
            return bytearray(self._buffer)

    @property
    def is_empty(self):
        with self._threadLock:
            return bool(not self._buffer)

    @property
    def length(self):
        with self._threadLock:
            return len(self._buffer)

# ======================================================
class LockedDict:
    """ Thread locked Dict """
    # By Grok AI
    def __init__(self):
        self._dict = {}
        self._lock = RLock()

    def __getitem__(self, key):
        with self._lock:
            return self._dict[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._dict[key] = value

    def __delitem__(self, key):
        with self._lock:
            del self._dict[key]

    def __len__(self):
        with self._lock:
            return len(self._dict)

    def __iter__(self):
        with self._lock:
            return iter(self._dict.copy())  # Kopie für sichere Iteration

    def add(self, key, value):
        with self._lock:
            self._dict[key] = value

    def get(self, key, default=None):
        with self._lock:
            return self._dict.get(key, default)

    def pop(self, key, default=None):
        with self._lock:
            return self._dict.pop(key, default)

    def keys(self):
        with self._lock:
            return list(self._dict.keys())

    def values(self):
        with self._lock:
            return list(self._dict.values())

    def items(self):
        with self._lock:
            return list(self._dict.items())

