import glob
import unittest
import tempfile
import os
from pathlib import Path
from filecmp import dircmp

from xtremcache import CacheManager
from xtremcache import Utils

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
            file = os.path.join(sub_dir, f"file_{i}.txt")
            with open(file, 'a') as f:
                f.write(f"Content of file_{i}")
            if Utils.isUnix():
                cwd = os.getcwd()
                os.chdir(os.path.dirname(file))
                os.symlink(os.path.basename(file), f"file_{i}_symnlink.txt")
                os.chdir(cwd)

    def test_cache_dir(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        id = "TestCacheDir"

        cache_manager = CacheManager(cache_dir, max_size)
        self.assertTrue(cache_manager.cache(id, self.__dir_to_cache))
        self.assertTrue(cache_manager.uncache(id, self.__dir_to_uncache))

        dircmp_res = dircmp(self.__dir_to_uncache, self.__dir_to_cache)
        self.assertListEqual(dircmp_res.diff_files, [])

        if Utils.isUnix():
            symnlink = glob.glob(os.path.join(self.__dir_to_uncache, '**', 'file_*_symnlink.txt'), recursive=True)
            self.assertNotEqual(symnlink, [])
            for f in symnlink:
                self.assertTrue(os.path.islink(f))

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
        self.assertTrue(cache_manager.cache(id, self.__file_to_cache))
        os.remove(self.__file_to_cache)
        self.assertTrue(cache_manager.uncache(id, self._temp_dir))

        self.assertEqual(Path(self.__file_to_cache).read_text(), self.__file_content)