import logging
import os
import time

from xtremcache.archivermanager import create_archiver
from xtremcache.bddmanager import BddManager
from xtremcache.configuration import ConfigurationLevel, ConfigurationManager
from xtremcache.utils import *


class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    VERBOSE = logging.DEBUG
    INFO = logging.INFO
    QUIET = logging.ERROR

    _DELAY_TIME = 0.5
    _DEFAULT_TIMEOUT = 60

    def __init__(self, cache_dir: str = None, max_size: str = None, log_level: int = logging.WARNING) -> None:
        self.__config = ConfigurationManager(cache_dir=cache_dir, max_size=max_size)
        self.__archiver = create_archiver(self.__config.cache_dir)
        logging.basicConfig(
            level=log_level,
            format='[xtremcache %(levelname)s - %(asctime)s]: %(message)s',
            datefmt='%H:%M:%S')
        self.__bdd_manager = BddManager(self.__config.cache_dir, log_level)

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
            compression_level: int = 6,
            excluded: List[str] = [],
            timeout: int = _DEFAULT_TIMEOUT) -> None:
        """Put the file or dir at the given path in cache."""

        def _cache(
                id: str,
                path: str,
                force: bool,
                compression_level: int = 6,
                excluded: List[str] = []) -> None:
            bdd = self.__bdd_manager
            cache_dir = self.cache_dir
            archiver = self.__archiver
            try:
                item = bdd.get(id)
            except XtremCacheItemNotFoundError:
                item = bdd.get(id, create=True)
                try:
                    archive_path = archiver.archive(
                        id,
                        path,
                        compression_level,
                        excluded)
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
                    logging.info(f'"{id}" is cached.')
                    if item.size < (self.max_size - bdd.size):
                        self.__max_size_cleaning()
                    else:
                        self.remove(id)
                        raise XtremCacheMaxSizeCachedError(id)
            else:
                if force:
                    self.remove(id)
                    _cache(id, path, False)
                else:
                    raise XtremCacheAlreadyCachedError(id)

        timeout_exec(timeout, _cache, id, path, force, compression_level, excluded)

    def uncache(self, id: str, path: str, timeout: int = _DEFAULT_TIMEOUT) -> None:
        """Extract the archive with the given id at the given path."""

        def _uncache(id: str, path: str) -> None:
            bdd = self.__bdd_manager
            archiver = self.__archiver
            try:
                item = bdd.get(id)
            except XtremCacheItemNotFoundError as e:
                logging.error(f'Impossible to find "{id}"')
                raise e
            if item.can_read:
                item.readers = item.readers + 1
                bdd.update(item)
                try:
                    archiver.extract(id, path)
                    logging.info(f'"{id}" was uncached to {path}.')
                except XtremCacheArchiveExtractionError as e:
                    item.readers = item.readers - 1
                    bdd.update(item)
                    self.remove(id)
                    raise e
                else:
                    item.readers = item.readers - 1
                    bdd.update(item)
            else:
                time.sleep(self._DELAY_TIME)
                raise FunctionRecallAsked(_uncache)

        timeout_exec(timeout, _uncache, id, path)

    def __max_size_cleaning(self, removed_list=None) -> None:
        """Delete the oldest archives to match the max_size limitation.
        
        Return the list of deleted Item."""

        if removed_list == None:
            removed_list = []
        bdd = self.__bdd_manager
        all_sizes = bdd.get_all_values(bdd.Item.size)
        all_sizes.append(bdd.size)
        if len(all_sizes):
            if sum(all_sizes) >= self.max_size:
                self.remove(bdd.older.id)
                removed_list.append(bdd.older)
                self.__max_size_cleaning(removed_list)
        return removed_list

    def remove(self, id: str = None, timeout: int = _DEFAULT_TIMEOUT) -> None:
        """Delete an archive based on its id."""

        def _remove(id: int) -> None:
            bdd = self.__bdd_manager
            cache_dir = self.cache_dir
            ids = [id] if id else bdd.get_all_values(bdd.Item.id)
            if not ids:
                logging.info('Empty cache, nothing to remove.')
            for id in ids:
                try:
                    item = bdd.get(id)
                except XtremCacheItemNotFoundError as e:
                    logging.error(f'Unable to find "{id}".')
                    raise e
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
                        raise XtremCacheArchiveRemovingError(id, e)
                    bdd.delete(item.id)
                else:
                    time.sleep(self._DELAY_TIME)
                    raise FunctionRecallAsked(_remove)

        timeout_exec(timeout, _remove, id)

    def display(self):
        """Print the full configuration thanks to tabulate lib."""

        self.__config.display()

    def set_cache_dir(self, value: str, level: ConfigurationLevel):
        """Update the cache_dir value at the given level.
        If it is not possible, raise an Exception"""

        self.__config.set_cache_dir(value, level)
        logging.info(f'Cache dir have been updated at {level} level.')

    def set_max_size(self, value: str, level: ConfigurationLevel):
        """Update the max_size value at the given level.
        If it is not possible, raise an Exception"""

        self.__config.set_max_size(value, level)
        logging.info(f'Max size have been updated at {level} level.')
