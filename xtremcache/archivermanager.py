from abc import abstractmethod
import os
import subprocess
from glob import glob
from typing import List

from xtremcache.utils import *


# Cache / Uncache
class ArchiveManager():
    """Create an archive from id."""

    def __init__(self, cache_dir: str) -> None:
        self._cache_dir = cache_dir

    @property
    @abstractmethod
    def zip_exec(self) -> str:
        """Path to the zip exe."""

        pass

    @property
    @abstractmethod
    def unzip_exec(self) -> str:
        """Path to the unzip exe."""

        pass

    @property
    def ext(self) -> str:
        """Extention of created archive."""

        return 'zip'

    def id_to_hash(self, id: str) -> str:
        """Convert archive id into md5 hash."""

        return str_to_md5(id)

    def id_to_filename(self, id: str) -> str:
        """Convert archive id into the archive file name."""

        return f'{self.id_to_hash(id)}.zip'

    def id_to_archive_path(self, id: str) -> str:
        """Convert archive id into the archive path."""

        return os.path.join(self._cache_dir, self.id_to_filename(id))

    def archive(
            self,
            id: str,
            src_path: str,
            compression_level: int = 6,
            excluded: List[str] = []) -> str:
        """Archive the dir or file at the given path with the given id."""

        dest_path = self.id_to_archive_path(id)
        if not os.path.exists(src_path):
            raise XtremCacheFileNotFoundError(src_path)
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            exclude_args = []
            for excl in excluded:
                exclude_args += [
                    '-x', rf"{excl}"
                    if os.path.isfile(os.path.join(src_path, excl))
                    else rf"'{excl}/*'"
                ]
            src_is_dir = os.path.isdir(src_path)
            inputs = glob(os.path.join(src_path, '*')) if src_is_dir else glob(src_path)
            inputs = list(map(lambda p: os.path.relpath(p, src_path), inputs))
            subprocess.run([
                    self.zip_exec,
                    f'-{compression_level}',
                    '-y',
                    '-q',
                    '-r',
                    '-FS',
                    dest_path
                ] + inputs + exclude_args,
                cwd=src_path if src_is_dir else os.path.dirname(src_path),
                check=True)
        except Exception as e:
            raise XtremCacheArchiveCreationError(id, e)
        return dest_path

    def extract(self, id: str, path: str) -> None:
        """Extract the id's archive at the given path."""

        archive_path = self.id_to_archive_path(id)
        try:
            os.makedirs(path, exist_ok=True)
            subprocess.run([
                    self.unzip_exec,
                    '-qq',
                    '-u',
                    archive_path,
                    '-d',
                    path
                ],
                check=True)
            pass
        except Exception as e:
            raise XtremCacheArchiveExtractionError(path, e)


class WinArchiver(ArchiveManager):
    """Zip archive format."""

    UNZIP_VERSION = 'v6.00'
    ZIP_VERSION = 'v3.0'

    def __init__(self, cache_dir: str) -> None:
        super().__init__(cache_dir)

    @property
    @abstractmethod
    def zip_exec(self) -> str:
        """Path to the zip exe."""

        return os.path.join(xtremcache_location(), 'ext', 'msys2', 'zip', self.ZIP_VERSION, 'bin', 'zip')

    @property
    @abstractmethod
    def unzip_exec(self) -> str:
        """Path to the unzip exe."""

        return os.path.join(xtremcache_location(), 'ext', 'msys2', 'unzip', self.UNZIP_VERSION, 'bin', 'unzip')


class LnxArchiver(ArchiveManager):
    """Gztar archive format."""

    def __init__(self, cache_dir: str) -> None:
        super().__init__(cache_dir)

    @property
    @abstractmethod
    def zip_exec(self) -> str:
        """Path to the zip exe."""

        return 'zip'

    @property
    @abstractmethod
    def unzip_exec(self) -> str:
        """Path to the unzip exe."""

        return 'unzip'


def create_archiver(cache_dir: str) -> ArchiveManager:
    """Factory of archvier depending of the os."""

    return LnxArchiver(cache_dir) if isUnix() else WinArchiver(cache_dir)
