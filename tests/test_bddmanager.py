import unittest
import tempfile

from xtremcache import BddManager
from test_utils import *

def populate(bdd):
    id_list = [get_random_text() for i in range(10)]
    for id in id_list:
        item = bdd.get(id, create=True)
        item.writer = False
        item.size = random.randint(0, 1000)
        item.readers = random.randint(0, 1000)
        bdd.update(item)
        yield item

class TestBddManager(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()

    def test_add_and_read_item(self):
        item = BddManager(self.__temp_dir).get("TestBddManager", create=True)

        item.writer = True
        BddManager(self.__temp_dir).update(item)

        item = BddManager(self.__temp_dir).get("TestBddManager")
        self.assertTrue(item.writer)

    def test_read_nonexistent_item(self):
        self.assertIsNone(BddManager(self.__temp_dir).get("TestBddManager", create=False))

    def test_clean_all_item(self):
        # Populate and clean and repeat
        for i in range(3):
            item_list = populate(BddManager(self.__temp_dir))
            BddManager(self.__temp_dir).delete_all()  
            for item in item_list:
                self.assertFalse(BddManager(self.__temp_dir).get(item.id, create=False))
    
    def test_get_all_item(self):
        # Populate and get_all and repeat
        for i in range(3):
            populate(BddManager(self.__temp_dir))
            for item in BddManager(self.__temp_dir).get_all():
                self.assertTrue(item == BddManager(self.__temp_dir).get(item.id))

    def test_get_all_item_values(self):
        # Populate and get_all and repeat
        for i in range(3):
            item_list = populate(BddManager(self.__temp_dir))
            size_sum = sum(item.size for item in item_list)
            values_list_from_bdd = BddManager(self.__temp_dir).get_all_values('size')
            self.assertTrue(size_sum, sum(values_list_from_bdd))
            
            
