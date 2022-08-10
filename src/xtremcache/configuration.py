from pathlib import Path
from src.xtremcache.utils import Utils
import os
import yaml

class ConfigurationFactory():
    def __init__(self, config_file) -> None:
        self.__config_file = config_file

    def from_file(self):
        datas = ConfigurationFactory.read_config_file(self.__config_file)
        configuration = ConfigurationFactory.create_configuration_from_datas(datas)
        self.to_file(configuration)
        return configuration

    def to_file(self, configuration):
        datas = ConfigurationFactory.create_datas_from_configuration(configuration)
        ConfigurationFactory.write_config_file(self.__config_file, datas)

    def create_configuration_from_datas(datas):
        configuration = Configuration()
        if datas:
            for p in Utils.get_public_props(configuration):
                v = datas.get(p, None)
                if v is not None:
                    setattr(configuration, p, v)
        return configuration

    def read_config_file(path):
        datas = {}
        datas[Utils.get_app_name()] = {}
        if os.path.isfile(path):
            with open(path, 'r') as f:
                datas = yaml.safe_load(f)
        return datas[Utils.get_app_name()]

    def create_datas_from_configuration(configuration):
        datas = {}
        datas[Utils.get_app_name()] = {}
        for p in Utils.get_public_props(configuration):
            v = getattr(configuration, p, None)
            if v is not None :
                datas[Utils.get_app_name()][p]=v
        return datas

    def write_config_file(path, datas):
        if os.path.isfile(path):
            os.remove(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w+') as f:
            yaml.safe_dump(datas, f)

# Configuration
class Configuration():
    """Global application configuration."""
    def __init__(self) -> None:
        self.cache_dir = os.path.join(Path.home(), f'.{Utils.get_app_name()}', 'datas')
        self.max_size = 10000

    @property
    def cache_dir(self):
        return self.__cache_dir

    @cache_dir.setter
    def cache_dir(self, cache_dir):
        self.__cache_dir = cache_dir
    
    @property
    def max_size(self):
        return self.__max_size

    @max_size.setter
    def max_size(self, max_size):
        self.__max_size = max_size

    def __repr__(self) -> str:
        return "\n".join([
            "Configuration:",
            f"   Cache directory: {self.cache_dir}",
            f"   Max cache size (Mo): {self.max_size}"])