import os
import pickle
import time

from backend.code import config


class Cache:

    def __init__(self, id: str, default=None, verbose=True):
        cache_folder = config.cache_path
        self.hits = 0
        self.misses = 0
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        if id is None:
            raise ValueError("id must not be None")

        self.cache_file = cache_folder + id + ".pkl"

        if os.path.exists(self.cache_file):
            if verbose:
                print(f"Loading cache with id {id}...")
            start = time.time()
            with open(self.cache_file, 'rb') as file:
                self.value = pickle.load(file)
            if verbose:
                print(f"Cache loaded in {config.rounding_policy(time.time() - start)} seconds")
        else:
            if verbose:
                print(f"Creating cache with id {id}...")
            if default is None:
                raise ValueError("default must not be None")
            self.value = default

    def save(self):
        with open(self.cache_file, 'wb') as file:
            pickle.dump(self.value, file)

    def hit(self):
        self.hits += 1

    def miss(self):
        self.misses += 1

    def report(self):
        print(f"Cache report for {self.cache_file}:")
        print(f"  Hits: {self.hits}")
        print(f"  Misses: {self.misses}")
        print(f"  Hit rate: {self.hits / (self.hits + self.misses) * 100}%")

