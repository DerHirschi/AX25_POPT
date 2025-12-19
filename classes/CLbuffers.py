import time


class ListBuffer:
    """ Thread locked List """
    def __init__(self, thread_lock_timer=0.01):
        self._buffer: list      = []
        self._threadLock        = False
        self._threadLockTimer   = float(thread_lock_timer)

    def _get_thread_lock(self):
        while self._threadLock:
            time.sleep(self._threadLockTimer)
        self._threadLock = True

    @property
    def buffer_read(self):
        self._get_thread_lock()
        ret = self._buffer.pop(0)
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
        self._buffer = []
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
    def __init__(self, thread_lock_timer=0.01):
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
        self._buffer = self._buffer[bytes_to_read:]
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
    def is_empty(self):
        return bool(not self._buffer)

    @property
    def length(self):
        return len(self._buffer)