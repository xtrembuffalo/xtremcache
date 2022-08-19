import glob
import shutil
import unittest
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from filecmp import dircmp
from ddt import ddt, data

from xtremcache import CacheManager, BddManager, ArchiveManager
from test_utils import *
from xtremcache import *

@ddt
class TestCacheDir(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.__cache_dir = os.path.join(self._temp_dir, 'datas')
        self.__cache_manager = CacheManager(self.__cache_dir)
        self.__dir_to_cache = os.path.join(self._temp_dir, "dir_to_cache")
        generate_dir_to_cache(self.__dir_to_cache)
        self.__dir_to_uncache = os.path.join(self._temp_dir, "dir_to_uncache")
    
    @data(*get_id_data())
    def test_cache_dir(self, id):
        self.__cache_manager.cache(id, self.__dir_to_cache)
        self.__cache_manager.uncache(id, self.__dir_to_uncache)
        dircmp_res = dircmp(self.__dir_to_uncache, self.__dir_to_cache)
        self.assertListEqual(dircmp_res.diff_files, [])
        if isUnix():
            symlink = glob.glob(os.path.join(self.__dir_to_uncache, '**', '*_symlink.txt'), recursive=True)
            self.assertNotEqual(symlink, [])
            for f in symlink:
                self.assertTrue(os.path.islink(f))

    @data(*get_id_data())
    def test_cache_non_existing_dir(self, id):
        self.assertRaises(XtremCacheItemNotFound, self.__cache_manager.uncache, id, self.__dir_to_uncache)

    def tearDown(self):
        shutil.rmtree(self._temp_dir)

@ddt
class TestCacheFile(unittest.TestCase):
    def setUp(self):
        self.__file_content = f"Content of file"
        self._temp_dir = tempfile.mkdtemp()
        self.__cache_dir = os.path.join(self._temp_dir, 'datas')
        self.__cache_manager = CacheManager(self.__cache_dir)
        self.__file_to_cache = os.path.join(self._temp_dir, "file_to_cache.txt")
        with open(self.__file_to_cache, 'a') as f:
            f.write(self.__file_content)

    @data(*get_id_data())
    def test_cache_file(self, id):
        self.__cache_manager.cache(id, self.__file_to_cache)
        os.remove(self.__file_to_cache)
        self.__cache_manager.uncache(id, self._temp_dir)
        self.assertEqual(Path(self.__file_to_cache).read_text(), self.__file_content)

    @data(*get_id_data())
    def test_cache_non_existing_file(self, id):
        self.assertRaises(XtremCacheFileNotFoundError, self.__cache_manager.cache, id, self.__file_to_cache  + "__")
        self.assertRaises(XtremCacheItemNotFound, self.__cache_manager.uncache, id, self._temp_dir)

    def tearDown(self):
        shutil.rmtree(self._temp_dir)

@ddt
class TestCacheGlobal(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.__cache_dir = os.path.join(self._temp_dir, 'datas')
        self.__cache_manager = CacheManager(self.__cache_dir)
        self.__dir_to_cache = os.path.join(self._temp_dir, "dir_to_cache")
        generate_dir_to_cache(self.__dir_to_cache)
        self.__dir_to_uncache = os.path.join(self._temp_dir, "dir_to_uncache")

    @data(*get_id_data())
    def test_uncache_non_existing_archive(self, id):
        self.assertRaises(XtremCacheItemNotFound, self.__cache_manager.uncache, id, '.')

    @data(*get_id_data())
    def test_force_cache(self, id):
        self.__cache_manager.cache(id, self.__dir_to_cache)
        shutil.rmtree(self.__dir_to_cache)
        generate_dir_to_cache(self.__dir_to_cache)
        self.__cache_manager.cache(id, self.__dir_to_cache, force=True)
        self.__cache_manager.uncache(id, self.__dir_to_uncache)
        dircmp_res = dircmp(self.__dir_to_uncache, self.__dir_to_cache)
        self.assertListEqual(dircmp_res.diff_files, [])

    @data(*get_id_data())
    def test_timeout(self, id):
        self.__cache_manager.cache(id, self.__dir_to_cache)
        bdd_manager = BddManager(self.__cache_dir)
        item = bdd_manager.get(id)
        item.writer = True
        bdd_manager.update(item)
        start_time = time.time()
        timeout=2
        self.assertRaises(XtremCacheTimeoutError, self.__cache_manager.uncache, id, self.__dir_to_uncache, timeout=timeout)
        self.assertGreaterEqual(time.time() - start_time, timeout)

    @data(*get_id_data())
    def test_extraction_error(self, id):
        self.__cache_manager.cache(id, self.__dir_to_cache)
        filter  = os.path.join(self.__cache_dir, f"*.{create_archiver(self.__cache_dir).ext}")
        [os.remove(file) for file in glob.glob(filter)]
        self.assertRaises(XtremCacheArchiveExtractionError, self.__cache_manager.uncache, id, self.__dir_to_uncache)
        self.assertRaises(XtremCacheItemNotFound, self.__cache_manager.uncache, id, self.__dir_to_uncache)
        self.__cache_manager.cache(id, self.__dir_to_cache)
        self.__cache_manager.uncache(id, self.__dir_to_uncache)

    @data(*get_id_data())
    def test_archive_creation_error(self, id):
        archive_manager = create_archiver(self.__cache_dir)
        os.makedirs(os.path.join(self.__cache_dir, str_to_md5(id) + '.' + archive_manager.ext), exist_ok=True)
        self.assertRaises(XtremCacheArchiveCreationError, self.__cache_manager.cache, id, self.__dir_to_cache)
        self.assertRaises(XtremCacheItemNotFound, self.__cache_manager.uncache, id, self.__dir_to_uncache)

    def tearDown(self):
        shutil.rmtree(self._temp_dir)

@ddt
class TestCacheConcurrent(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.__cache_dir = os.path.join(self._temp_dir, 'datas')
        self.__dir_to_cache = os.path.join(self._temp_dir, "dir_to_cache")
        generate_dir_to_cache(self.__dir_to_cache)

    @data(*get_id_data())
    def test_concurrent_same_id(self, id):
        def exec_cache(cache_dir, dir_to_cache, id, index):
            cache_manager = CacheManager(cache_dir)
            cache_manager.cache(id, dir_to_cache)
            dir_to_uncache = os.path.join(self._temp_dir, f"dir_to_uncache_{index}")
            os.makedirs(dir_to_uncache)
            cache_manager.uncache(id, dir_to_uncache)
            dircmp_res = dircmp(dir_to_cache, dir_to_uncache)
            self.assertListEqual(dircmp_res.diff_files, [])

        for index in range(3):   
            with ThreadPoolExecutor() as executor:
                executor.submit(exec_cache, self.__cache_dir, self.__dir_to_cache, id, index)

    @data(*get_id_data())
    def test_concurrent(self, id):
        def exec_cache(cache_dir, dir_to_cache, id, index):
            id = id + f'{index}'
            cache_manager = CacheManager(cache_dir)
            cache_manager.cache(id + f'{index}', dir_to_cache)
            dir_to_uncache = os.path.join(self._temp_dir, f"dir_to_uncache_{index}")
            os.makedirs(dir_to_uncache)
            cache_manager.uncache(id, dir_to_uncache)
            dircmp_res = dircmp(dir_to_cache, dir_to_uncache)
            self.assertListEqual(dircmp_res.diff_files, [])

        for index in range(3):   
            with ThreadPoolExecutor() as executor:
                executor.submit(exec_cache, self.__cache_dir, self.__dir_to_cache, id, index)

    def tearDown(self):
        shutil.rmtree(self._temp_dir)