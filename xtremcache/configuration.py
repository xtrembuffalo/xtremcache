from pathlib import Path
import os
from typing import Any, Dict, List
import yaml

from xtremcache.utils import *


# Configuration
class Configuration():
    """Global application configuration."""

    def __init__(self) -> None:
        self.cache_dir = os.path.join(Path.home(), f'.{get_app_name()}', 'datas')
        self.max_size = 500_000_000 # default 500 Mo

    @property
    def cache_dir(self) -> str:
        """Location of the cache directory."""

        return self.__cache_dir

    @cache_dir.setter
    def cache_dir(self, cache_dir: str) -> None:
        self.__cache_dir = cache_dir

    @property
    def max_size(self) -> int:
        """Maximal size of the cache directory in bytes."""

        return self.__max_size

    @max_size.setter
    def max_size(self, max_size: int) -> None:
        """Get max size in Mo use it in bytes."""

        self.__max_size = max_size * 1_000_000

    def __repr__(self) -> str:
        return '\n'.join([
            'Configuration:',
            f'   Cache directory: {self.cache_dir}',
            f'   Max cache size (Mo): {self.max_size / 1_000_000}'
        ])


class ConfigurationFactory():
    """Create configuration object from file or dict, or the reverse.

    All creation are safe, in the way that they extract only the wanted
    element from the base objects."""

    def __init__(self, config_file: str) -> None:
        self.__config_file = config_file

    def from_file(self, args: List[str]) -> Configuration:
        """Import the configuration from self.__config_file."""

        datas = ConfigurationFactory.read_config_file(self.__config_file)
        configuration = ConfigurationFactory.create_configuration_from_datas(datas, args)
        self.to_file(configuration)
        return configuration

    def to_file(self, configuration: Configuration) -> None:
        """Create or update a file to serialize the given configuration."""

        datas = ConfigurationFactory.create_datas_from_configuration(configuration)
        ConfigurationFactory.write_config_file(self.__config_file, datas)

    def create_configuration_from_datas(datas: dict, args: List[str] = None) -> Configuration:
        """Initialize a Configuration object from then given data dict."""

        configuration = Configuration()
        if datas or args:
            for p in get_public_props(configuration):
                v = getattr(args, p, datas.get(p, None))
                if v is not None:
                    setattr(configuration, p, v)
        return configuration

    def read_config_file(path: str) -> str:
        """Initialize a dict from the given file."""

        datas = {}
        datas[get_app_name()] = {}
        if os.path.isfile(path):
            with open(path, 'r') as f:
                datas = yaml.safe_load(f)
        return datas[get_app_name()]

    def create_datas_from_configuration(configuration: Configuration) -> Dict[str, Dict[str, Any]]:
        """Initialize a dict from the given Configuration object."""

        datas = {}
        datas[get_app_name()] = {}
        for p in get_public_props(configuration):
            v = getattr(configuration, p, None)
            if v is not None :
                datas[get_app_name()][p]=v
        return datas

    def write_config_file(path: str, datas: Dict[str, Dict[str, Any]]) -> None:
        """Create or update a file to serialize the given dict."""

        if os.path.isfile(path):
            os.remove(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w+') as f:
            yaml.safe_dump(datas, f)
