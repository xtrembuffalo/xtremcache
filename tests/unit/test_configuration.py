import io
import os
import sys
import unittest

import yaml
from xtremcache.configuration import (Configuration, ConfigurationManager,
                                      FileConfiguration)
from xtremcache.exceptions import XtremCacheInputError


HARD_CODED_MAX_SIZE = 50_000_000_000

TEST_CACHE_DIR_PATH = os.path.join('.', 'tests')
TEST_CONFIG_FILE_PATH = os.path.join('.', 'tests', 'config.yml')
TEST_MAX_SIZE_STR = '10m'
TEST_MAX_SIZE_STR_2 = '20m'
TEST_MAX_SIZE_INT = 10_000_000
TEST_MAX_SIZE_INT_2 = 20_000_000

EMPTY_CONFIG_ID = 'Empty config'
TEST_FILE_CONFIG_ID = 'Test file config'

def create_config_file(path, cache_dir, max_size):
    config_dict = {
        'cache_dir': cache_dir,
        'max_size': max_size,
    }
    with open(path, 'w') as f:
        yaml.dump(config_dict, f)


class FileTestConfiguration(FileConfiguration):
    @property
    def id_(self) -> str:
        return TEST_FILE_CONFIG_ID
    @property
    def config_path(self) -> str:
        return TEST_CONFIG_FILE_PATH


class DummyConfiguration1(Configuration):
    @property
    def id_(self) -> str:
        return 'Dummy config 1'
    @property
    def cache_dir(self) -> str:
        return os.path.join(TEST_CACHE_DIR_PATH, '1')
    @property
    def max_size(self) -> int:
        return TEST_MAX_SIZE_INT


class DummyConfiguration2(Configuration):
    @property
    def id_(self) -> str:
        return 'Dummy config 2'
    @property
    def cache_dir(self) -> str:
        return os.path.join(TEST_CACHE_DIR_PATH, '2')
    @property
    def max_size(self) -> int:
        return TEST_MAX_SIZE_INT_2


class EmptyConfiguration(Configuration):
    @property
    def id_(self) -> str:
        return EMPTY_CONFIG_ID
    @property
    def cache_dir(self) -> str:
        return None
    @property
    def max_size(self) -> int:
        return None
    @property
    def is_set_cache_dir(self) -> bool:
        return False
    @property
    def is_set_max_size(self) -> bool:
        return False


class TestFileConfiguration(unittest.TestCase):
    def setUp(self):
        self.ftc = FileTestConfiguration()

    def tearDown(self):
        if os.path.isfile(TEST_CONFIG_FILE_PATH):
            os.remove(TEST_CONFIG_FILE_PATH)

    def test_cache_dir(self):
        self.assertEqual(self.ftc.cache_dir, None)
        create_config_file(TEST_CONFIG_FILE_PATH, TEST_CACHE_DIR_PATH, TEST_MAX_SIZE_STR)
        self.assertEqual(self.ftc.cache_dir, TEST_CACHE_DIR_PATH)

    def test_cache_dir_is_set(self):
        self.assertFalse(self.ftc.is_set_cache_dir)
        create_config_file(TEST_CONFIG_FILE_PATH, TEST_CACHE_DIR_PATH, TEST_MAX_SIZE_STR)
        self.assertTrue(self.ftc.is_set_cache_dir)

    def test_set_cache_dir(self):
        self.assertFalse(self.ftc.is_set_cache_dir)
        self.ftc.set_cache_dir(TEST_CACHE_DIR_PATH)
        self.assertTrue(self.ftc.is_set_cache_dir)
        self.assertEqual(self.ftc.cache_dir, TEST_CACHE_DIR_PATH)

    def test_max_size(self):
        self.assertEqual(self.ftc.max_size, None)
        create_config_file(TEST_CONFIG_FILE_PATH, TEST_CACHE_DIR_PATH, TEST_MAX_SIZE_STR)
        self.assertEqual(self.ftc.max_size, TEST_MAX_SIZE_INT)

    def test_max_size_is_set(self):
        self.assertFalse(self.ftc.is_set_max_size)
        create_config_file(TEST_CONFIG_FILE_PATH, TEST_CACHE_DIR_PATH, TEST_MAX_SIZE_STR)
        self.assertTrue(self.ftc.is_set_max_size)

    def test_set_max_size(self):
        self.assertFalse(self.ftc.is_set_max_size)
        self.ftc.set_max_size(TEST_MAX_SIZE_STR)
        self.assertTrue(self.ftc.is_set_max_size)
        self.assertEqual(self.ftc.max_size, TEST_MAX_SIZE_INT)


class TestConfiguration(unittest.TestCase):
    def test_strategy_priority(self):
        cfg = ConfigurationManager([DummyConfiguration1(), DummyConfiguration2()])
        self.assertEqual(cfg.max_size, TEST_MAX_SIZE_INT_2)
        cfg = ConfigurationManager([DummyConfiguration2(), DummyConfiguration1()])
        self.assertEqual(cfg.max_size, TEST_MAX_SIZE_INT)

    def test_runtime_configuration(self):
        cfg = ConfigurationManager([], max_size=TEST_MAX_SIZE_STR)
        self.assertEqual(cfg.max_size, TEST_MAX_SIZE_INT)
        cfg = ConfigurationManager([DummyConfiguration2()], max_size=TEST_MAX_SIZE_STR)
        self.assertEqual(cfg.max_size, TEST_MAX_SIZE_INT)

    def test_display(self):
        cfg = ConfigurationManager([DummyConfiguration2()], max_size=TEST_MAX_SIZE_STR)
        old_sys_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        except_display = """+----------------+-------------+------------+
| Origin         | cache_dir   |   max_size |
|----------------+-------------+------------|
| Dummy config 2 | .\\tests\\2   |   20000000 |
| Runtime        | Not defined |   10000000 |
| Used values    | .\\tests\\2   |   10000000 |
+----------------+-------------+------------+
"""
        cfg.display()
        self.assertEqual(captured_output.getvalue(), except_display)
        sys.stdout = old_sys_stdout

    def test_set_fail(self):
        cfg = ConfigurationManager([EmptyConfiguration()])
        self.assertRaises(NotImplementedError, cfg.set_cache_dir, TEST_CACHE_DIR_PATH, EMPTY_CONFIG_ID)

    def test_set_success(self):
        cfg = ConfigurationManager([FileTestConfiguration()])
        cfg.set_max_size(TEST_MAX_SIZE_STR_2, TEST_FILE_CONFIG_ID)
        self.assertEqual(cfg.max_size, TEST_MAX_SIZE_INT_2)

