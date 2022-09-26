import os
import time

from xtremcache.archivermanager import create_archiver
from xtremcache.bddmanager import BddManager
from xtremcache.utils import *

class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    delay_time = 0.5
    default_timeout = 60

    def __init__(
        self,
        cache_dir,
        max_size) -> None:
        self.__cache_dir = cache_dir
        self.__max_size = max_size
        self.__archiver = create_archiver(self.__cache_dir)
        self.__bdd_manager = BddManager(cache_dir)

    def cache(
        self,
        id,
        path,
        force=False,
        timeout=default_timeout):
        def cache(
            id,
            path,
            force):
            bdd = self.__bdd_manager
            cache_dir = self.__cache_dir
            archiver = self.__archiver
            try:
                item = bdd.get(id)
            except XtremCacheItemNotFound:
                item = bdd.get(id, create=True)
                try:
                    archive_path = archiver.archive(id, path)
                except Exception as e:
                    item.writer = False
                    bdd.update(item)
                    self.remove(id)
                    raise e
                else:
                    item.size = os.path.getsize(archive_path)
                    item.writer = False
                    item.archive_path = os.path.relpath(archive_path, cache_dir)
                    bdd.update(item)
                    self.__max_size_cleaning()
            else:
                if force:
                    self.remove(id)
                    cache(
                        id,
                        path,
                        False)
                else:
                    raise XtremCacheAlreadyCached()
            
        timeout_exec(
            timeout,
            cache,
            id,
            path,
            force
        )
    
    def uncache(
        self,
        id, 
        path, 
        timeout=default_timeout):
        def uncache(
            id,
            path):
            bdd = self.__bdd_manager
            archiver = self.__archiver
            item = bdd.get(id)
            if item.can_read:
                item.readers = item.readers + 1
                bdd.update(item)
                try:
                    archiver.extract(id, path)
                except XtremCacheArchiveExtractionError as e:
                    item.readers = item.readers - 1
                    bdd.update(item)
                    self.remove(id)
                    raise XtremCacheArchiveExtractionError(e)
                else:
                    item.readers = item.readers - 1
                    bdd.update(item)
            else:
                time.sleep(self.delay_time)
                raise FunctionRetry()
        timeout_exec(
            timeout,
            uncache,
            id,
            path)

    def __max_size_cleaning(self):
        bdd = self.__bdd_manager
        all_sizes = bdd.get_all_values(bdd.Item.size)
        all_sizes.append(bdd.size)
        if len(all_sizes):
            if sum(all_sizes) >= self.__max_size:
                self.remove(bdd.older.id)
                self.__max_size_cleaning()

    def remove_all(
        self,
        timeout=default_timeout):
        bdd = self.__bdd_manager
        for id in bdd.get_all_values(bdd.Item.id):
            self.remove(id, timeout)

    def remove(
        self,
        id,
        timeout=default_timeout):
        def remove(id):
            bdd = self.__bdd_manager
            cache_dir = self.__cache_dir
            item = bdd.get(id)
            if item.can_modifie:
                item.writer = True
                bdd.update(item)
                try:
                    c_cwd = os.getcwd()
                    os.makedirs(cache_dir, exist_ok=True)
                    os.chdir(cache_dir)
                    if item.archive_path and os.path.exists(item.archive_path):
                        os.remove(item.archive_path)
                    os.chdir(c_cwd)
                except Exception as e:
                    raise XtremCacheArchiveRemovingError(e)
                bdd.delete(item.id)
            else:
                time.sleep(self.delay_time)
                raise FunctionRetry()
        timeout_exec(
            timeout,
            remove,
            id)