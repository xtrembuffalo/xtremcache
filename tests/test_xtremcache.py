import unittest
import tempfile
import os
from xtremcache import CacheManager
from configuration import Configuration

class TestCache(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._temp_dir = tempfile.mkdtemp()

class TestCacheDir(TestCache):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.__dir_to_cache = os.path.join(self._temp_dir, "dir_to_cache")
        self.__dir_to_uncache = os.path.join(self._temp_dir, "dir_to_uncache")
        for i in range(10):
            sub_dir = os.path.join(self.__dir_to_cache, f"sub_dir_{i}")
            os.makedirs(sub_dir)
            with open(os.path.join(sub_dir, f"file_{i}.txt"), 'a') as f:
                f.write(f"Content of file_{i}")

    def test_cache_dir(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        id = "TestCacheDir"

        cache_manager = CacheManager(cache_dir, max_size)
        cache_manager.cache(id, self.__dir_to_cache)
        cache_manager.uncache(id, self.__dir_to_uncache)