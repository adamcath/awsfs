from time import time


class LoadingCache:
    def __init__(self, load_func, ttl_secs):
        self.cache = dict()
        self.load_func = load_func
        self.ttl_secs = ttl_secs

    def get(self, key):
        if key in self.cache:
            (value, expiry) = self.cache[key]
            if time() < expiry:
                return value

        new_value = self.load_func(key)
        self.cache[key] = (new_value, time() + self.ttl_secs)
        return new_value
