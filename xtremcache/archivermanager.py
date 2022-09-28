from abc import abstractmethod
import shutil
import os

from xtremcache.utils import *


def create_archiver(cache_dir):
    """Factory of archvier depending of the os."""

    return GZipArchiver(cache_dir) if isUnix() else ZipArchiver(cache_dir)


# Cache / Uncache
class ArchiveManager():
    """Create an archive from id."""

    def __init__(self, cache_dir):
        self._cache_dir = cache_dir

    @property
    @abstractmethod
    def format(self):
        """Format of the handled archives."""

        pass

    @property
    @abstractmethod
    def ext(self):
        """Extention of the handled archives."""

        pass

    def id_to_hash(self, id):
        """Convert archive id into md5 hash."""

        return str_to_md5(id)

    def id_to_filename(self, id):
        """Convert archive id into the archive file name."""

        return f'{self.id_to_hash(id)}.{self.ext}'

    def id_to_archive_path(self, id):
        """Convert archive id into the archive path."""

        return os.path.join(self._cache_dir, self.id_to_filename(id))

    def archive(self, id, path):
        """Archive a dir or file with the given id."""

        archive_path = self.id_to_archive_path(id)
        if not os.path.exists(path):
            raise XtremCacheFileNotFoundError(path)
        try:
            root_dir = os.path.realpath(
                path if os.path.isdir(path)
                else os.path.dirname(path))
            shutil.make_archive(
                base_name=remove_file_extention(archive_path),
                format=self.format,
                root_dir=root_dir,
                base_dir='.')
        except Exception as e:
            raise XtremCacheArchiveCreationError(e)
        return archive_path

    def extract(self, id, path):
        """Extract the id's archive at the given path."""

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
    """Zip archive format."""

    def __init__(self, cache_dir) -> None:
        super().__init__(cache_dir)

    @property
    @abstractmethod
    def format(self):
        """Format of the handled archives."""

        return 'zip'

    @property
    @abstractmethod
    def ext(self):
        """Extention of the handled archives."""

        return 'zip'

class GZipArchiver(ArchiveManager):
    """Gztar archive format."""

    def __init__(self, cache_dir) -> None:
        super().__init__(cache_dir)

    @property
    @abstractmethod
    def format(self):
        """Format of the handled archives."""

        return 'gztar'

    @property
    @abstractmethod
    def ext(self):
        """Extention of the handled archives."""

        return 'tar.gz'
