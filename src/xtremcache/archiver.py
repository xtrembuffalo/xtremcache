from abc import abstractmethod
import shutil
import os
import pathlib

# Cache / Uncache
class Archiver():
    def __init__(self, archive_path) -> None:
        self.archive_path = archive_path

    @property
    @abstractmethod
    def format(self):
        pass

    @property
    @abstractmethod
    def ext(self):
        pass

    @property
    def archive_path(self):
        return self.__archive_path
    
    @property
    def archive_path_with_ext(self):
        return self.archive_path + f'.{self.ext}'
    
    @archive_path.setter
    def archive_path(self, path):
        self.__archive_path = path

    def archive(self, path):
        rt = False
        try:
            shutil.make_archive(
                base_name=self.archive_path,
                format=self.format,
                root_dir=os.path.dirname(path),
                base_dir=os.path.basename(path))
            rt = True
        except Exception as e:
            print("Impossible to create archive:")
            print(e)
        return rt

    def extract(self, path):
        rt = False
        try:
            shutil.unpack_archive(
                filename=self.archive_path_with_ext,
                extract_dir=path,
                format=self.format)
            rt = True
        except Exception as e:
            print("Impossible to extract archive:")
            print(e)
        return rt

class ZipArchiver(Archiver):
    def __init__(self, archive_path) -> None:
        super().__init__(archive_path)
    
    @property
    @abstractmethod
    def format(self):
        return 'zip'

    @property
    @abstractmethod
    def ext(self):
        return 'zip'

class GZipArchiver(Archiver):
    def __init__(self, archive_path) -> None:
        super().__init__(archive_path)
        
    @property
    @abstractmethod
    def format(self):
        return 'gztar'

    @property
    @abstractmethod
    def ext(self):
        return 'tar.gz'