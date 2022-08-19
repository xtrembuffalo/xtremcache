import os
import logging
import time
from typing import final

from xtremcache.archiver import create_archiver
from xtremcache.bddmanager import BddManager
from xtremcache.utils import *

class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    delay_time = 0.5

    def __init__(self, cache_dir, max_size=10000) -> None:
        self.__cache_dir = cache_dir
        self.__max_size = max_size
        self.__archiver = create_archiver(self.__cache_dir)
        self.__bdd_manager = BddManager(cache_dir)

    def cache(self, id, src_path, force=False, timeout=60*10):
        timeout_exec(timeout, self.__cache, id, src_path, force)
    
    def uncache(self, id, dest_path, timeout=60*10):
        timeout_exec(timeout, self.__uncache, id, dest_path)

    def __cache(self, id, src_path, force):
        bdd = self.__bdd_manager
        try:
            item = bdd.get(id)
        except XtremCacheItemNotFound:
            item = bdd.get(id, create=True)
            try:
                archive_path = self.__archiver.archive(id, src_path)
            except Exception as e:
                bdd.delete(id)
                raise e
            else:
                item.size = os.path.getsize(archive_path)
                item.writer = False
                item.archive_path = os.path.relpath(archive_path, self.__cache_dir)
                bdd.update(item)
        else:
            if force:
                if item.can_modifie:
                    bdd.delete(id)
                    self.__cache(id, src_path, False)
                else:
                    time.sleep(self.delay_time)
                    raise FunctionRetry()
    
    def __uncache(self, id, dest_path):
        bdd = self.__bdd_manager
        item = bdd.get(id)
        if item.can_read:
            item.readers = item.readers + 1
            bdd.update(item)
            try:
                self.__archiver.extract(id, dest_path)
            except XtremCacheArchiveExtractionError as e:
                bdd.delete(id)
                raise XtremCacheArchiveExtractionError(e)
            else:
                item.readers = item.readers - 1
                bdd.update(item)
        else:
            time.sleep(self.delay_time)
            raise FunctionRetry()