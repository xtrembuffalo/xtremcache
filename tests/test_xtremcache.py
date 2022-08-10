import unittest
import tempfile
import os
from pathlib import Path
from filecmp import dircmp

try:
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'xtremcache'))
    sys.path.insert(0, path)
    from cachemanager import CacheManager
except:
    print(f"Impossible to import from {path}")


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

        dircmp_res = dircmp(self.__dir_to_uncache, self.__dir_to_cache)
        self.assertListEqual(dircmp_res.diff_files, [])

class TestCacheFile(TestCache):
    def setUp(self):
        self.__file_content = f"Content of file"
        self._temp_dir = tempfile.mkdtemp()
        self.__file_to_cache = os.path.join(self._temp_dir, "file_to_cache.txt")
        with open(self.__file_to_cache, 'a') as f:
            f.write(self.__file_content)

    def test_cache_dir(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        id = "TestCacheFile"

        cache_manager = CacheManager(cache_dir, max_size)
        cache_manager.cache(id, self.__file_to_cache)
        os.remove(self.__file_to_cache)
        cache_manager.uncache(id, self._temp_dir)

        self.assertEqual(Path(self.__file_to_cache).read_text(), self.__file_content)