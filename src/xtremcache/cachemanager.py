import os

from archiver import ZipArchiver
from utils import Utils

class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    def __init__(self, cache_dir, max_size) -> None:
        self.__cache_dir = cache_dir
        self.__max_size = max_size

    def __archive(self, archive_name, path):
        destination = os.path.join(self.__cache_dir, archive_name)
        return ZipArchiver(destination).archive(path)
        
    def __extract(self, archive_name, path):
        source = os.path.join(self.__cache_dir, archive_name)
        return ZipArchiver(source).extract(path)

    def cache(self, id, path):
        rt = True
        archive_name = Utils.str_to_md5(id)
        rt |= self.__archive(archive_name, path)
        return rt
    
    def uncache(self, id, path):
        rt = True
        archive_name = Utils.str_to_md5(id)
        rt |= self.__extract(archive_name, path)
        return rt