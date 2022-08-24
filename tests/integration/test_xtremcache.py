import unittest
import tempfile
import shutil
from ddt import ddt, data

from xtremcache.main import main
from tests.test_utils import *

DEFAULT_MAX_SIZE=1000000

@ddt
class TestXtremcache(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.__config_file = os.path.join(self._temp_dir, 'config.yml')
        self.__cache_dir = os.path.join(self._temp_dir, 'datas')
        self.__dir_to_cache = os.path.join(self._temp_dir, 'dir_to_cache')
        self.__dir_to_uncache = os.path.join(self._temp_dir, 'dir_to_uncache')
        generate_dir_to_cache(self.__dir_to_cache)

    def xtremcache(self, *args):
        return main(['--config-file', self.__config_file] + list(args))

    @data(*get_id_data())
    def test_cache_uncache_command(self, id):
        self.assertEqual(self.xtremcache(
            'config',
            '--cache-dir', self.__cache_dir,
            '--max-size', str(DEFAULT_MAX_SIZE)
        ), 0)

        self.assertEqual(self.xtremcache(
            'cache',
            '--id', id,
            self.__dir_to_cache
        ), 0)

        self.assertEqual(self.xtremcache(
            'uncache',
            '--id', id,
            self.__dir_to_uncache
        ), 0)
        self.assertTrue(dircmp(self.__dir_to_uncache, self.__dir_to_cache))

    def tearDown(self):
        shutil.rmtree(self._temp_dir)