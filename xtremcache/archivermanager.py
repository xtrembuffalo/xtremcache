from abc import abstractmethod
import shutil
import os

from xtremcache.utils import *

def create_archiver(cache_dir):
    return GZipArchiver(cache_dir) if isUnix() else ZipArchiver(cache_dir)

# Cache / Uncache
class ArchiveManager():
    def __init__(self, cache_dir):
        self._cache_dir = cache_dir

    @property
    @abstractmethod
    def format(self):
        pass

    @property
    @abstractmethod
    def ext(self):
        pass

    def id_to_hash(self, id):
        return str_to_md5(id)

    def id_to_filename(self, id):
        return f"{self.id_to_hash(id)}.{self.ext}"

    def id_to_archive_path(self, id):
        return os.path.join(self._cache_dir, self.id_to_filename(id))

    def archive(self, id, path):
        archive_path = self.id_to_archive_path(id)
        if not os.path.exists(path):
            raise XtremCacheFileNotFoundError(path)
        try:
            root_dir = os.path.realpath(path if os.path.isdir(path) else os.path.dirname(path))
            shutil.make_archive(
                base_name=remove_file_extention(archive_path),
                format=self.format,
                root_dir=root_dir,
                base_dir='.')
        except Exception as e:
            raise XtremCacheArchiveCreationError(e)
        return archive_path

    def extract(self, id, path):
        archive_path = self.id_to_archive_path(id)
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            shutil.unpack_archive(
                filename=archive_path,
                extract_dir=path,
                format=self.format)
        except Exception as e:
            raise XtremCacheArchiveExtractionError(e)

class ZipArchiver(ArchiveManager):
    def __init__(self, cache_dir) -> None:
        super().__init__(cache_dir)
    
    @property
    @abstractmethod
    def format(self):
        return 'zip'

    @property
    @abstractmethod
    def ext(self):
        return 'zip'

class GZipArchiver(ArchiveManager):
    def __init__(self, cache_dir) -> None:
        super().__init__(cache_dir)
        
    @property
    @abstractmethod
    def format(self):
        return 'gztar'

    @property
    @abstractmethod
    def ext(self):
        return 'tar.gz'