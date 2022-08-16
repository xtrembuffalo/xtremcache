from ast import Delete
import os
import logging
import time

from xtremcache.archiver import create_archiver
from xtremcache.bddmanager import BddManager
from xtremcache.utils import *

class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    delay_time = 0.5

    def __init__(self, cache_dir, max_size) -> None:
        self.__cache_dir = cache_dir
        self.__max_size = max_size
        self.__archiver = create_archiver(self.__cache_dir)
        self.__bdd_manager = BddManager(cache_dir)
        self.__logger = logging.getLogger(get_app_name())

    def cache(self, *args, **kwargs):
        return self.__cache(*args, **kwargs)
    
    def uncache(self, *args, **kwargs):
        return self.__uncache(*args, **kwargs)

    def __cache(self, id, src_path, force=False):
        rt = False
        bdd = self.__bdd_manager
        item = bdd.get_item(id, create=False)
        if item is None:
            item = bdd.get_item(id, create=True)
            archive_path = self.__archiver.archive(id, src_path)
            if archive_path is not None:
                item.size = os.path.getsize(archive_path)
                item.writer = False
                item.archive_path = os.path.relpath(archive_path, self.__cache_dir)
                rt = bdd.update(item)
                if rt: self.__logger.info(f"{src_path} has been successfully cached (id={id})")
            else:
               bdd.delete(id)
               self.__logger.error(f"Impossible to create cache archive (check access right or disk space) (id={id})")
               rt = False
        else:
            if item.can_modifie:
                if force:
                    bdd.delete(id)
                    rt = self.cache(id, src_path, False)
                else:
                    self.__logger.info(f"{src_path} is aleady chached (id={id})")
            else:
                self.__logger.info(f"Waiting to have write access on archive (id={id})")
                time.sleep(self.delay_time)
                rt = self.cache(id, src_path, force)
        return rt
    
    def __uncache(self, id, dest_path, force=False):
        rt = False
        bdd = self.__bdd_manager
        item = bdd.get_item(id, create=False)
        if item:
            if item.can_read or force:
                item.readers = item.readers + 1
                bdd.update(item)
                if not self.__archiver.extract(id, dest_path):
                    self.__logger.error(f"Impossible to extract cached archive to {dest_path} (id={id})")
                else:
                    rt = True
                item.readers = item.readers - 1
                bdd.update(item)
            else:
                self.__logger.info(f"Waiting to have read access on cached archive (id={id})")
                time.sleep(self.delay_time)
                rt = self.uncache(id, dest_path)
        else:
            self.__logger.error(f"Impossible to find cached archive (id={id})")
            rt = False
        return rt