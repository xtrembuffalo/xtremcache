from abc import abstractmethod
import shutil
import os
import pathlib

# Cache / Uncache
class Archiver():
    def __init__(self, archive_path) -> None:
        self.__archive_path = archive_path

    @abstractmethod
    def archive(sources):
       pass

    @abstractmethod
    def extract(sources):
       pass

    @property
    def archive_path(self):
        return self.__archive_path

class ZipArchiver():
    format = 'zip'
    
    def __init__(self, archive_path) -> None:
        self.archive_path = archive_path

    @property
    def archive_path(self):
        return self.__archive_path

    @archive_path.setter
    def archive_path(self, path):
        suffix = pathlib.Path(path).suffix
        self.__archive_path = path if suffix else '.'.join([path, ZipArchiver.format])

    @property
    def archive_path_without_ext(self):
        return os.path.join(os.path.dirname(self.__archive_path),
                            pathlib.Path(self.__archive_path).stem)

    @abstractmethod
    def archive(self, path):
        rt = True
        try:
            shutil.make_archive(
                base_name=self.archive_path_without_ext,
                format=ZipArchiver.format,
                root_dir=os.path.dirname(path),
                base_dir=os.path.basename(path))
            rt = False
        except Exception as e:
            print("Impossible to create archive:")
            print(e)
        return rt

    @abstractmethod
    def extract(self, path):
        rt = True
        try:
            shutil.unpack_archive(
                filename=self.archive_path,
                extract_dir=path,
                format=ZipArchiver.format)
            rt = False
        except Exception as e:
            print("Impossible to extract archive:")
            print(e)
        return rt

       
