import unittest
import tempfile

from xtremcache import BddManager
from test_utils import *

class TestBddManager(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()

    def test_add_and_read_item(self):
        item = BddManager(self.__temp_dir).get_item("TestBddManager", create=True)

        item.writer = True
        BddManager(self.__temp_dir).update(item)

        item = BddManager(self.__temp_dir).get_item("TestBddManager")
        self.assertTrue(item.writer)

    def test_read_nonexistent_item(self):
        self.assertIsNone(BddManager(self.__temp_dir).get_item("TestBddManager", create=False))

    def test_clean_all_item(self):
        def populate():
            id_list = [get_random_text() for i in range(10)]
            for id in id_list:
                bdd = BddManager(self.__temp_dir)
                item = bdd.get_item(id, create=True)
                item.writer = False
                bdd.update(item)
            return id_list
        
        # Populate and clean and repeat
        for i in range(3):
            id_list = populate()
            BddManager(self.__temp_dir).delete_all()  
            for id in id_list:
                self.assertFalse(BddManager(self.__temp_dir).get_item(id, create=False))
