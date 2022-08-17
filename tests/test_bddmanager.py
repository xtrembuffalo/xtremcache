import unittest
import tempfile
from ddt import ddt, data

from xtremcache import *
from test_utils import *

def populate(bdd):
    id_list = [get_random_text() for i in range(10)]
    item_list = []
    for id in id_list:
        item = bdd.get(id, create=True)
        item.writer = False
        item.size = random.randint(0, 1000)
        item.readers = random.randint(0, 1000)
        bdd.update(item)
        item_list.append(item)
    return item_list

@ddt
class TestBddManager(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
        self.__bdd = BddManager(self.__temp_dir)

    @data(*get_id_data())
    def test_add_and_read_item(self, id):
        item = self.__bdd.get(id, create=True)

        item.writer = True
        self.__bdd.update(item)

        item = self.__bdd.get(id)
        self.assertTrue(item.writer)

    @data(*get_id_data())
    def test_read_nonexistent_item(self, id):
        self.assertRaises(XtremCacheItemNotFound, self.__bdd.get, id)

    @data(*get_id_data())
    def test_update_non_existing_item(self, id):
        item = self.__bdd.create_item(id)
        self.assertRaises(XtremCacheItemNotFound, self.__bdd.update, item)

    def test_clean_all_item(self):
        # Populate and clean and repeat
        for i in range(3):
            item_list = populate(self.__bdd)
            self.__bdd.delete_all()  
            for item in item_list:
                self.assertRaises(XtremCacheItemNotFound, self.__bdd.get, item.id)
    
    def test_get_all_item(self):
        # Populate and get_all and repeat
        for i in range(3):
            populate(self.__bdd)
            for item in self.__bdd.get_all():
                self.assertTrue(item == self.__bdd.get(item.id))

    def test_get_all_item_values(self):
        # Populate and get_all and repeat
        for i in range(3):
            item_list = populate(self.__bdd)
            size_sum = sum(item.size for item in item_list)
            values_list_from_bdd = self.__bdd.get_all_values('size')
            self.assertTrue(size_sum, sum(values_list_from_bdd))

