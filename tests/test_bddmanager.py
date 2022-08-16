import unittest
import tempfile
import os
import random

from xtremcache import BddManager

class TestBddManager(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()

    def test_add_and_read_item(self):
        item = BddManager(self.__temp_dir).get_item("TestBddManager", create=True)

        item.writer = True
        BddManager(self.__temp_dir).update(item)

        item = BddManager(self.__temp_dir).get_item("TestBddManager")
        self.assertTrue(item.writer)
