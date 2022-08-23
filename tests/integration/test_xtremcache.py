import unittest
import tempfile
import shutil
from ddt import ddt, data

from xtremcache.bddmanager import *
from xtremcache.exceptions import *

@ddt
class TestXtremcache(unittest.TestCase):
    def setUp(self):
        self.__temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.__temp_dir)

