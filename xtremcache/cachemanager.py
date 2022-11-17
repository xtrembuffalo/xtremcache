import os
import time

from xtremcache.archivermanager import create_archiver
from xtremcache.bddmanager import BddManager
from xtremcache.configuration import ConfigurationLevel, ConfigurationManager
from xtremcache.utils import *


class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    DELAY_TIME = 0.5
    DEFAULT_TIMEOUT = 60

    def __init__(self, cache_dir: str = None, max_size: int = None) -> None:
        self.__config = ConfigurationManager(cache_dir=cache_dir, max_size=max_size)
        self.__archiver = create_archiver(self.__config.cache_dir)
        self.__bdd_manager = BddManager(self.__config.cache_dir)

    @property
    def cache_dir(self):
        return self.__config.cache_dir
    
    @property
    def max_size(self):
        return self.__config.max_size

    def cache(
            self,
            id: str,
            path: str,
            force: bool = False,
            timeout: int = DEFAULT_TIMEOUT) -> None:
        """Put the file or dir at the given path in cache."""

        def _cache(
                id: str,
                path: str,
                force: bool) -> None:
            bdd = self.__bdd_manager
            cache_dir = self.cache_dir
            archiver = self.__archiver
            try:
                item = bdd.get(id)
            except XtremCacheItemNotFoundError:
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
                    _cache(id, path, False)
                else:
                    raise XtremCacheAlreadyCachedError()

        timeout_exec(timeout, _cache, id, path, force)

    def uncache(self, id: str, path: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Extract the archive with the given id at the given path."""

        def _uncache(id: str, path: str) -> None:
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
                time.sleep(self.DELAY_TIME)
                raise FunctionRetry()

        timeout_exec(timeout, _uncache, id, path)

    def __max_size_cleaning(self) -> None:
        """Delete the oldest archives to match the max_size limitation."""

        bdd = self.__bdd_manager
        all_sizes = bdd.get_all_values(bdd.Item.size)
        all_sizes.append(bdd.size)
        if len(all_sizes):
            if sum(all_sizes) >= self.max_size:
                self.remove(bdd.older.id)
                self.__max_size_cleaning()

    def remove(self, id: str = None, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Delete an archive based on its id."""
    
        def _remove(id: int) -> None:
            bdd = self.__bdd_manager
            cache_dir = self.cache_dir
            ids = [id] if id else [id for id in bdd.get_all_values(bdd.Item.id)]
            for id in ids:
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
                    time.sleep(self.DELAY_TIME)
                    raise FunctionRetry()

        timeout_exec(timeout, _remove, id)

    def config_display(self):
        """Print the full configuration thanks to tabulate lib."""

        self.__config.display()

    def set_cache_dir(self, value: str, level: ConfigurationLevel):
        """Update the cache_dir value at the given level.
        If it is not possible, raise an Exception"""

        self.__config.set_cache_dir(value, level)

    def set_max_size(self, value: str, level: ConfigurationLevel):
        """Update the max_size value at the given level.
        If it is not possible, raise an Exception"""
        
        self.__config.set_max_size(value, level)
