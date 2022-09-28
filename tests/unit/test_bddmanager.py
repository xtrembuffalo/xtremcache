import unittest
import tempfile
import shutil
from ddt import ddt, data

from xtremcache.bddmanager import *
from xtremcache.exceptions import *
from tests.test_utils import *

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
        self.assertRaises(XtremCacheItemNotFoundError, self.__bdd.get, id)

    @data(*get_id_data())
    def test_update_non_existing_item(self, id):
        item = self.__bdd.create_item(id)
        self.assertRaises(XtremCacheItemNotFoundError, self.__bdd.update, item)

    def test_clean_all_item(self):
        # Populate and clean and repeat
        for i in range(3):
            item_list = populate(self.__bdd)
            self.__bdd.delete_all()
            for item in item_list:
                self.assertRaises(XtremCacheItemNotFoundError, self.__bdd.get, item.id)
            self.__bdd.create_item('AddAfterRemoving')

    def test_get_all_item_values(self):
        size_sum = [item.size for item in populate(self.__bdd)]
        self.assertTrue(sum(size_sum), sum(self.__bdd.get_all_values(self.__bdd.Item.size)))

    def test_get_older(self):
        item_list = populate(self.__bdd)
        older = self.__bdd.older
        self.assertEqual(older, item_list[-1])

    def tearDown(self):
        shutil.rmtree(self.__temp_dir)

