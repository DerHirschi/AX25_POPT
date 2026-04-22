import time
from threading import RLock

# ======================================================
class ListBuffer:
    """ Thread locked List """
    def __init__(self, thread_lock_timer=0.001):
        self._buffer: list      = []
        self._threadLock        = False
        self._threadLockTimer   = float(thread_lock_timer)

    def _get_thread_lock(self):
        while self._threadLock:
            time.sleep(self._threadLockTimer)
        self._threadLock = True

    @property
    def buffer_read(self):
        if self.is_empty:
            return None
        self._get_thread_lock()
        ret = self._buffer.pop(0)
        self._threadLock = False
        return ret

    def buffer_read_n(self, n: int):
        if self.is_empty:
            return None
        self._get_thread_lock()
        ret = self._buffer[:n]
        self._buffer = self._buffer[n:]
        self._threadLock = False
        return ret

    def buffer_write(self, data):
        self._get_thread_lock()
        self._buffer.append(data)
        self._threadLock = False

    def buffer_insert(self, data):
        """ Insert Data at the beginning """
        self._get_thread_lock()
        self._buffer = [data] + self._buffer
        self._threadLock = False

    def buffer_clear(self):
        self._get_thread_lock()
        self._buffer.clear()
        self._threadLock = False

    def buffer_pop(self, i=0):
        self._get_thread_lock()
        self._buffer.pop(i)
        self._threadLock = False

    def buffer_remove(self, value):
        self._get_thread_lock()
        self._buffer.remove(value)
        self._threadLock = False

    @property
    def buffer_get(self):
        return list(self._buffer)

    @property
    def buffer_get_and_lock(self):
        self._get_thread_lock()
        return self._buffer

    def buffer_set_and_unlock(self, new_buffer: list):
        self._buffer = new_buffer
        self._threadLock = False

    # == Read Only / property
    @property
    def is_empty(self):
        return bool(not self._buffer)

    @property
    def length(self):
        return len(self._buffer)

# ======================================================
class ByteArrayBuffer:
    """ Thread locked bytearray """
    def __init__(self, thread_lock_timer=0.001):
        self._buffer: bytearray = bytearray()
        self._threadLock        = False
        self._threadLockTimer   = float(thread_lock_timer)

    def _get_thread_lock(self):
        while self._threadLock:
            time.sleep(self._threadLockTimer)
        self._threadLock = True

    def buffer_read(self, bytes_to_read: int):
        self._get_thread_lock()
        ret          = self._buffer[:bytes_to_read]
        self._buffer = self._buffer[len(ret):]
        self._threadLock = False
        return ret

    def buffer_flush(self):
        self._get_thread_lock()
        ret          = bytearray(self._buffer)
        self._buffer = bytearray()
        self._threadLock = False
        return ret

    def buffer_write(self, data):
        if not isinstance(data, (bytes, bytearray)):
            return False
        self._get_thread_lock()
        self._buffer.extend(data)
        self._threadLock = False
        return True

    def buffer_set(self, data):
        if not isinstance(data, (bytes, bytearray)):
            print(f"Error : {data}  - {type(data)}")
            return False
        self._get_thread_lock()
        self._buffer = data
        self._threadLock = False
        return True

    def buffer_clear(self):
        self._get_thread_lock()
        self._buffer = bytearray()
        self._threadLock = False

    # == Read Only / property
    @property
    def buffer_get(self):
        return bytearray(self._buffer)

    @property
    def is_empty(self):
        return bool(not self._buffer)

    @property
    def length(self):
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