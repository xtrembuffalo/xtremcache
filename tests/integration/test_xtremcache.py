import unittest
import tempfile
import shutil
from webbrowser import get
import yaml
from ddt import ddt, data

from xtremcache.main import main
from tests.test_utils import *

DEFAULT_TESTS_MAX_SIZE=1000000

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

    def test_configuration(self):
        self.assertEqual(self.xtremcache(
            'config',
            '--cache-dir', self.__cache_dir,
            '--max-size', str(DEFAULT_TESTS_MAX_SIZE)
        ), 0)
        self.assertTrue(os.path.isfile(self.__config_file))
        with open(self.__config_file, 'r') as f:
            datas = yaml.safe_load(f)
        self.assertEqual(datas[get_app_name()]['cache_dir'], self.__cache_dir)
        self.assertEqual(datas[get_app_name()]['max_size'], DEFAULT_TESTS_MAX_SIZE)

    @data(*get_id_data())
    def test_cache_uncache_command(self, id):
        self.assertEqual(self.xtremcache(
            'config',
            '--cache-dir', self.__cache_dir,
            '--max-size', str(DEFAULT_TESTS_MAX_SIZE)
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

    @data(*get_id_data())
    def test_uncache_failed_command(self, id):
        self.assertEqual(self.xtremcache(
            'config',
            '--cache-dir', self.__cache_dir,
            '--max-size', str(DEFAULT_TESTS_MAX_SIZE)
        ), 0)
        self.assertEqual(self.xtremcache(
            'uncache',
            '--id', id,
            self.__dir_to_uncache
        ), 1)

    @data(*get_id_data())
    def test_cache_failed_command(self, id):
        self.assertEqual(self.xtremcache(
            'config',
            '--cache-dir', self.__cache_dir,
            '--max-size', str(DEFAULT_TESTS_MAX_SIZE)
        ), 0)
        for i in range(2):
            self.assertEqual(self.xtremcache(
                'cache',
                '--id', id,
                self.__dir_to_cache
            ), i)

    def tearDown(self):
        shutil.rmtree(self._temp_dir)