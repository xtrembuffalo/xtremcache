import unittest
import tempfile
import yaml
from ddt import ddt, data

from xtremcache.main import exec
from tests.test_utils import *


TESTS_MAX_SIZE_INT=10_000_000
TESTS_MAX_SIZE_STR='10m'


@ddt
class TestXtremcache(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self._old_cwd = os.getcwd()
        os.chdir(self._temp_dir)
        self._config_file = os.path.join(self._temp_dir, 'config.yml')
        self._cache_dir = os.path.join(self._temp_dir, 'data')
        self._dir_to_cache = os.path.join(self._temp_dir, 'dir_to_cache')
        self._dir_to_uncache = os.path.join(self._temp_dir, 'dir_to_uncache')
        generate_dir_to_cache(self._dir_to_cache)
        # Set the configuration
        self.assertEqual(self.xtremcache(
            'config',
            'set',
            'cache_dir', self._cache_dir,
            '--local'
        ), 0)
        self.assertEqual(self.xtremcache(
            'config',
            'set',
            'max_size', TESTS_MAX_SIZE_STR,
            '--local'
        ), 0)

    def tearDown(self):
        os.chdir(self._old_cwd)
        remove_file(self._temp_dir)

    def xtremcache(self, *args):
        return exec(list(args))

    def test_configuration(self):
        self.assertTrue(os.path.isfile(self._config_file))
        with open(self._config_file, 'r') as f:
            data = yaml.safe_load(f)
        self.assertEqual(data['cache_dir'], self._cache_dir)
        self.assertEqual(data['max_size'], TESTS_MAX_SIZE_STR)

    @data(*get_id_data())
    def test_cache_uncache_command(self, id):
        self.assertEqual(self.xtremcache(
            'cache',
            '--id', id,
            self._dir_to_cache
        ), 0)
        self.assertEqual(self.xtremcache(
            'uncache',
            '--id', id,
            self._dir_to_uncache
        ), 0)
        self.assertTrue(dircmp(self._dir_to_uncache, self._dir_to_cache))

    @data(*get_id_data())
    def test_uncache_failed_command(self, id):
        self.assertEqual(self.xtremcache(
            'uncache',
            '--id', id,
            self._dir_to_uncache
        ), 1)

    @data(*get_id_data())
    def test_cache_failed_command(self, id):
        for i in range(2):
            self.assertEqual(self.xtremcache(
                'cache',
                '--id', id,
                self._dir_to_cache
            ), i)

    @data(*get_id_data())
    def test_remove_command(self, id):
        self.assertEqual(self.xtremcache(
            'cache',
            '--id', id,
            self._dir_to_cache
        ), 0)
        self.assertEqual(self.xtremcache(
            'remove',
            '--id', id
        ), 0)
        self.assertEqual(self.xtremcache(
            'uncache',
            '--id', id,
            self._dir_to_uncache
        ), 1)

    @data(*get_id_data())
    def test_remove_all_command(self, id):
        for i in range(2):
            self.assertEqual(self.xtremcache(
                'cache',
                '--id', id + str(i),
                self._dir_to_cache
            ), 0)
        self.assertEqual(self.xtremcache(
            'remove'
        ), 0)
        for i in range(2):
            self.assertEqual(self.xtremcache(
                'uncache',
                '--id', id + str(i),
                self._dir_to_uncache
            ), 1)
