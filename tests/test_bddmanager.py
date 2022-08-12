import unittest
import tempfile
import os
import random

try:
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'xtremcache'))
    sys.path.insert(0, path)
    from bddmanager import BddManager
except:
    print(f"Impossible to import from {path}")


class TestBddManager(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
        self.__bdd_manager = BddManager(self.__temp_dir)

    def test_add_and_read_item(self):
        item_to_add = self.__bdd_manager.create_item(id=str(random.getrandbits(128)), size=12000)
        self.__bdd_manager.add_item(item_to_add)