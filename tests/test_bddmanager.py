import unittest
import tempfile
import os
import random

from xtremcache import BddManager

class TestBddManager(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
        self.__bdd_manager = BddManager(self.__temp_dir)

    def test_add_and_read_item(self):
        item_to_add = self.__bdd_manager.create_item(id=str(random.getrandbits(128)), size=12000)
        self.__bdd_manager.add_item(item_to_add)
        item_added = self.__bdd_manager.get_item_by_id(id=item_to_add.id)
        self.assertEqual(item_to_add, item_added)