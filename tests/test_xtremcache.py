import glob
import shutil
import unittest
import tempfile
import os
import random
import string
from pathlib import Path
from filecmp import dircmp

from xtremcache import CacheManager, BddManager
from xtremcache.utils import *

def get_random_text(len=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(len))

def generate_dir_to_cache(root):
    for n in range(10):
        sub_dir = get_random_text() 
        for m in range(10):
            file_path = os.path.join(root, sub_dir, f"{get_random_text()}.tmp")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'a') as f:
                f.write(get_random_text(100))
            if isUnix():
                cwd = os.getcwd()
                os.chdir(os.path.dirname(file_path))
                os.symlink(os.path.basename(file_path), f"{get_random_text()}_symnlink.txt")
                os.chdir(cwd)

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
            symnlink = glob.glob(os.path.join(self.__dir_to_uncache, '**', 'file_*_symnlink.txt'), recursive=True)
            self.assertNotEqual(symnlink, [])
            for f in symnlink:
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