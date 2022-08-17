import glob
import shutil
import unittest
import tempfile
import os
from pathlib import Path
from filecmp import dircmp

from xtremcache import CacheManager, BddManager
from test_utils import *

class TestCacheDir(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.__dir_to_cache = os.path.join(self._temp_dir, "dir_to_cache")
        generate_dir_to_cache(self.__dir_to_cache)
        self.__dir_to_uncache = os.path.join(self._temp_dir, "dir_to_uncache")
        
    def test_cache_dir(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        id = "TestCacheDir"
        cache_manager = CacheManager(cache_dir, max_size)
        self.assertTrue(cache_manager.cache(id, self.__dir_to_cache))
        self.assertTrue(cache_manager.uncache(id, self.__dir_to_uncache))
        dircmp_res = dircmp(self.__dir_to_uncache, self.__dir_to_cache)
        self.assertListEqual(dircmp_res.diff_files, [])
        if isUnix():
            symlink = glob.glob(os.path.join(self.__dir_to_uncache, '**', '*_symlink.txt'), recursive=True)
            self.assertNotEqual(symlink, [])
            for f in symlink:
                self.assertTrue(os.path.islink(f))

    def test_cache_non_existing_dir(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        id = "TestCacheDir"
        cache_manager = CacheManager(cache_dir, max_size)
        self.assertFalse(cache_manager.cache(id, self.__dir_to_cache + "__"))
        self.assertFalse(cache_manager.uncache(id, self.__dir_to_uncache))

class TestCacheFile(unittest.TestCase):
    def setUp(self):
        self.__file_content = f"Content of file"
        self._temp_dir = tempfile.mkdtemp()
        self.__file_to_cache = os.path.join(self._temp_dir, "file_to_cache.txt")
        with open(self.__file_to_cache, 'a') as f:
            f.write(self.__file_content)

    def test_cache_file(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        id = "TestCacheFile"
        cache_manager = CacheManager(cache_dir, max_size)
        self.assertTrue(cache_manager.cache(id, self.__file_to_cache))
        os.remove(self.__file_to_cache)
        self.assertTrue(cache_manager.uncache(id, self._temp_dir))
        self.assertEqual(Path(self.__file_to_cache).read_text(), self.__file_content)

    def test_cache_non_existing_file(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        id = "TestCacheFile"
        cache_manager = CacheManager(cache_dir, max_size)
        self.assertFalse(cache_manager.cache(id, self.__file_to_cache  + "__"))
        self.assertFalse(cache_manager.uncache(id, self._temp_dir))

class TestCacheGlobal(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.__dir_to_cache = os.path.join(self._temp_dir, "dir_to_cache")
        generate_dir_to_cache(self.__dir_to_cache)
        self.__dir_to_uncache = os.path.join(self._temp_dir, "dir_to_uncache")

    def test_uncache_non_existing_archive(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        cache_manager = CacheManager(cache_dir, max_size)
        self.assertFalse(cache_manager.uncache("TestCacheNotExists", '.'))

    def test_force_cache(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        cache_manager = CacheManager(cache_dir, max_size)
        self.assertTrue(cache_manager.cache("TestForceCache", self.__dir_to_cache))
        shutil.rmtree(self.__dir_to_cache)
        generate_dir_to_cache(self.__dir_to_cache)
        self.assertTrue(cache_manager.cache("TestForceCache", self.__dir_to_cache, force=True))
        self.assertTrue(cache_manager.uncache("TestForceCache", self.__dir_to_uncache))
        dircmp_res = dircmp(self.__dir_to_uncache, self.__dir_to_cache)
        self.assertListEqual(dircmp_res.diff_files, [])

    def test_asyc_cache(self):
        cache_dir = os.path.join(self._temp_dir, 'datas')
        max_size = 100
        cache_manager = CacheManager(cache_dir, max_size)
        self.assertTrue(cache_manager.cache("TestAsyncCache", self.__dir_to_cache))
        bdd_manager = BddManager(cache_dir)
        item = bdd_manager.get("TestAsyncCache")
        item.writer = True
        bdd_manager.update(item)
        start_time = time.time()
        timeout=2
        self.assertFalse(cache_manager.uncache("TestAsyncCache", self.__dir_to_uncache, timeout=timeout))
        self.assertGreaterEqual(time.time() - start_time, timeout)