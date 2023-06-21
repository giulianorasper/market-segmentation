import os
import pickle
import time

from backend.code import config


class Cache:

    def __init__(self, id: str, default):
        cache_folder = config.cache_path
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        if id is None:
            raise ValueError("id must not be None")

        self.cache_file = cache_folder + id + ".pkl"

        if os.path.exists(self.cache_file):
            print(f"Loading cache with id {id}...")
            start = time.time()
            with open(self.cache_file, 'rb') as file:
                self.value = pickle.load(file)
            print(f"Cache loaded in {config.rounding_policy(time.time() - start)} seconds")
        else:
            print(f"Creating cache with id {id}...")
            self.value = default

    def save(self):
        with open(self.cache_file, 'wb') as file:
            pickle.dump(self.value, file)

