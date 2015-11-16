from time import time
from threading import Lock


class LoadingCache:
    def __init__(self, load_func, ttl_secs=-1):
        self.lock = Lock()
        self.cache = dict()
        self.load_func = load_func
        self.ttl_secs = ttl_secs

    def get(self, key):
        with self.lock:
            if key in self.cache:
                (value, expiry) = self.cache[key]
                if self.ttl_secs == -1 or time() < expiry:
                    return value

        new_value = self.load_func(key)

        with self.lock:
            self.cache[key] = (new_value, time() + self.ttl_secs)

        return new_value
