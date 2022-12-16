import unittest
import tempfile
import os
from ddt import ddt, data

from xtremcache.archivermanager import create_archiver
from tests.test_utils import *


@ddt
class TestArchiver(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
        self.__cache_dir = os.path.join(self.__temp_dir, 'data')
        self.__dir_to_archive = os.path.join(self.__temp_dir, 'dir_to_archive')
        self.__dir_to_extract = os.path.join(self.__temp_dir, 'dir_to_extract')
        self.__archiver = create_archiver(self.__cache_dir)
        generate_dir_to_cache(self.__dir_to_archive)

    @data(*get_id_data())
    def test_archive_extract(self, id):
        self.__archiver.archive(id, self.__dir_to_archive)
        self.__archiver.extract(id, self.__dir_to_extract)
        self.assertTrue(dircmp(self.__dir_to_archive, self.__dir_to_extract))

    def test_archive_exclude_file(self):
        id = 'test_id'
        excluded_file = 'test_file_to_exclude.txt'
        with open(os.path.join(self.__dir_to_archive, excluded_file), 'a') as f:
            f.write('toto')
        excluded_files = [excluded_file]
        self.__archiver.archive(id, self.__dir_to_archive, excluded=excluded_files)
        self.__archiver.extract(id, self.__dir_to_extract)
        self.assertTrue(dircmp(self.__dir_to_archive, self.__dir_to_extract, excluded_files))
        self.assertFalse(dircmp(self.__dir_to_extract, self.__dir_to_archive, excluded_files), 'Exclude file are still in destination')

    def test_archive_exclude_dir(self):
        id = 'test_id'
        excluded_dir = os.path.join(self.__dir_to_archive, 'test_dir_to_exclude')
        generate_dir_to_cache(excluded_dir)
        excluded_files = [os.path.basename(excluded_dir)]
        self.__archiver.archive(id, self.__dir_to_archive, excluded=excluded_files)
        self.__archiver.extract(id, self.__dir_to_extract)
        self.assertTrue(dircmp(self.__dir_to_archive, self.__dir_to_extract, excluded_files))
        self.assertFalse(dircmp(self.__dir_to_extract, self.__dir_to_archive, excluded_files), 'Exclude file are still in destination')

    def tearDown(self):
        filesystem_remove(self.__temp_dir)

