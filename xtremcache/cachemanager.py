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

    def cache(self, id, src_path, force=False, timeout=10000):
        rt = False
        bdd = self.__bdd_manager
        item = bdd.get_item_by_id(id)
        if item is None:
            item = bdd.add_update_item(bdd.create_item(
                id = id,
                writer = True))
            archive_path = self.__archiver.archive(id, src_path)
            if archive_path is not None:
                item.size = os.path.getsize(archive_path)
                item.writer = False
                item.archive_path = archive_path
                rt = True if bdd.add_update_item(item) is not None else False
                if rt: self.__logger.info(f"{src_path} has been successfully cached (id={id})")
            else:
               bdd.remove_item(item)
               self.__logger.error(f"Impossible to create cache archive (check access right or disk space) (id={id})")
               rt = False
        else:
            if item.can_modifie:
                if force:
                    item.writer = True
                    item = bdd.add_update_item(item)
                    archive_path = self.__archiver.archive(id, src_path)
                    item.size = os.path.getsize(archive_path)
                    item.writer = False
                    item.archive_path = archive_path
                    rt = True if bdd.add_update_item(item) is not None else False
                    if rt: self.__logger.info(f"{src_path} has been successfully updated (id={id})")
                else:
                    self.__logger.info(f"{src_path} is aleady chached (id={id})")
            else:
                self.__logger.info(f"Waiting to have write access on archive (id={id})")
                time.sleep(self.delay_time)
                rt = self.cache(id, src_path, force)
        return rt
    
    def uncache(self, id, dest_path, timeout=10000):
        rt = False
        bdd = self.__bdd_manager
        item = bdd.get_item_by_id(id)
        if item:
            if item.can_read:
                item.readers = item.readers + 1
                bdd.add_update_item(item)
                if not self.__archiver.extract(id, dest_path):
                    self.__logger.error(f"Impossible to extract cached archive to {dest_path} (id={id})")
                else:
                    rt = True
                item.readers = item.readers - 1
                bdd.add_update_item(item)
            else:
                self.__logger.info(f"Waiting to have read access on cached archive (id={id})")
                time.sleep(self.delay_time)
                rt = self.uncache(id, dest_path, timeout)
        else:
            self.__logger.error(f"Impossible to find cached archive (id={id})")
            rt = False
        return rt