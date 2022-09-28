import unittest
import tempfile
import shutil
import os
from ddt import ddt, data

from xtremcache.archivermanager import create_archiver
from tests.test_utils import *

@ddt
class TestArchiver(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
        self.__cache_dir = os.path.join(self.__temp_dir, 'datas')
        self.__dir_to_archive = os.path.join(self.__temp_dir, 'dir_to_archive')
        self.__dir_to_extract = os.path.join(self.__temp_dir, 'dir_to_extract')
        self.__archiver = create_archiver(self.__cache_dir)
        generate_dir_to_cache(self.__dir_to_archive)

    @data(*get_id_data())
    def test_archive_extract(self, id):
        self.__archiver.archive(id, self.__dir_to_archive)
        self.__archiver.extract(id, self.__dir_to_extract)
        self.assertTrue(dircmp(self.__dir_to_archive, self.__dir_to_extract))

    def tearDown(self):
        shutil.rmtree(self.__temp_dir)

