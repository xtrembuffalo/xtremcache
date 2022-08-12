import os

from archiver import GZipArchiver, ZipArchiver
from utils import Utils
from bddmanager import BddManager

class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    def __init__(self, cache_dir, max_size) -> None:
        self.__cache_dir = cache_dir
        self.__max_size = max_size
        self.__Archiver = GZipArchiver if Utils.isUnix() else ZipArchiver
        self.__bdd_manager = BddManager(cache_dir)

    def __archive(self, archive_name, path):
        destination = os.path.join(self.__cache_dir, archive_name)
        return self.__Archiver(destination).archive(path)
        
    def __extract(self, archive_name, path):
        source = os.path.join(self.__cache_dir, archive_name)
        return self.__Archiver(source).extract(path)

    def __create_item(self, id, archive_name):
        archive_path = os.path.join(self.__cache_dir, archive_name)
        archive_path_with_ext = self.__Archiver(archive_path).archive_path_with_ext

        size = os.path.getsize(archive_path_with_ext)
        return self.__bdd_manager.create_item(id=id, size=size)

    def cache(self, id, path):
        rt = True

        archive_name = Utils.str_to_md5(id)
        rt |= self.__archive(archive_name, path)

        item = self.__create_item(id, archive_name)
        rt |= self.__bdd_manager.add_item(item)
        return rt
    
    def uncache(self, id, path):
        rt = True
        archive_name = Utils.str_to_md5(id)
        rt |= self.__extract(archive_name, path)
        return rt