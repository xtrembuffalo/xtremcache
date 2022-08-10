import os
from archiver import ZipArchiver
from utils import Utils

class CacheManager():
    """All actions to do when file or directory is cached or exit from the cache."""

    def __init__(self, cache_dir, max_size) -> None:
        self.__cache_dir = cache_dir
        self.__max_size = max_size

    def cache(self, id, path):
        archive_name = Utils.str_to_md5(id)
        destination = os.path.join(self.__cache_dir, archive_name)
        archiver = ZipArchiver(destination)
        archiver.archive(path)
    
    def uncache(self, id, path):
        archive_name = Utils.str_to_md5(id)
        source = os.path.join(self.__cache_dir, archive_name)
        archiver = ZipArchiver(source)
        archiver.extract(path)