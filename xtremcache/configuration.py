import os
from abc import ABC, abstractproperty
from enum import Enum
import re
from typing import List

import yaml
from tabulate import tabulate

from xtremcache.utils import *


class ConfigurationLevel(Enum):
    HARD_CODED = 'Default'
    GLOBAL_FILE = 'Global file'
    LOCAL_FILE = 'Local file'
    ENV_VAR = 'Environement variables'
    RUNTIME = 'Runtime'


class Configuration(ABC):
    @abstractproperty
    def id_(self) -> str:
        """Return a unique printable / readable identifier for this configuration."""

        pass

    @abstractproperty
    def cache_dir(self) -> str:
        """Compute and return the dir location of all archive database."""

        pass

    @abstractproperty
    def max_size(self) -> int:
        """Compute and return the maximum size of the all archive database."""

        pass

    @property
    def is_set_cache_dir(self) -> bool:
        """Return True if the cache_dir variable is set in this config."""

        return self.cache_dir != None

    @property
    def is_set_max_size(self) -> bool:
        """Return True if the max_size variable is set in this config."""

        return self.max_size != None

    def set_cache_dir(self, value: str) -> None:
        """Update the cahe_dir value. (Not mandatory)"""

        raise NotImplementedError(f'This type of configuration ({self.id_} do not allow cache_dir updates.')

    def set_max_size(self, value: str) -> None:
        """Update the max_size value. (Not mandatory)"""

        raise NotImplementedError(f'This type of configuration ({self.id_} do not allow max_size updates.')


class HardcodedConfiguration(Configuration):
    @property
    def id_(self) -> str:
        return ConfigurationLevel.HARD_CODED.value

    @property
    def cache_dir(self) -> str: 
        if isUnix():
            path = os.path.join('~', f'.{get_app_name()}')
        else:
            path = os.path.join(os.getenv('LOCALAPPDATA'), f'.{get_app_name()}')
        return path

    @property
    def max_size(self) -> int:
        return 50_000_000_000 # in bytes

    @property
    def is_set_cache_dir(self) -> bool:
        return True

    @property
    def is_set_max_size(self) -> bool:
        return True


class FileConfiguration(Configuration, ABC):
    @abstractproperty
    def config_path(self) -> str:
        pass

    def _read_yaml_properties(self) -> dict:
        file_content = dict()
        if os.path.isfile(self.config_path):
            with open(self.config_path, 'r') as f:
                file_content = yaml.safe_load(f)
        return file_content

    @property
    def cache_dir(self) -> str:
        return self._read_yaml_properties().get('cache_dir')

    @property
    def max_size(self) -> int:
        return convert_size(self._read_yaml_properties().get('max_size'))

    def set_cache_dir(self, value: str) -> None:
        file_content = self._read_yaml_properties()
        file_content['cache_dir'] = value
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(file_content, f, default_flow_style=False)

    def set_max_size(self, value: str) -> None:
        if not re.match(r'^\d+[tgm]$', value):
            raise XtremCacheInputError(
                f'Invalid max_size format: get {value}, correct format is \d+[tgm] e.g.: \'5g\', \'100m\' or \'1t\'.')
        file_content = self._read_yaml_properties()
        file_content['max_size'] = value
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(file_content, f, default_flow_style=False)


class HomeFileConfiguration(FileConfiguration):
    @property
    def config_path(self) -> str:
        if isUnix():
            return os.path.join('~', f'.{get_app_name()}', 'config.yml')
        else:
            return os.path.join(os.getenv('LOCALAPPDATA'), f'.{get_app_name()}', 'config.yml')

    @property
    def id_(self) -> str:
        return ConfigurationLevel.GLOBAL_FILE.value


class LocalFileConfiguration(FileConfiguration):
    @property
    def config_path(self) -> str:
        return os.path.join('.', 'config.yml')

    @property
    def id_(self) -> str:
        return ConfigurationLevel.LOCAL_FILE.value


class EnvironementConfiguration(Configuration):
    @property
    def id_(self) -> str:
        return ConfigurationLevel.ENV_VAR.value

    @property
    def cache_dir(self) -> str:
        return self.__env_cache_dir()

    @property
    def max_size(self) -> int:
        return convert_size(self.__env_max_size())

    def __env_cache_dir(self) -> str:
        return os.getenv('XCACHE_CACHE_DIR')

    def __env_max_size(self) -> str:
        return os.getenv('XCACHE_MAX_SIZE')


class RuntimeConfiguration(Configuration):
    def __init__(self, cache_dir: str, max_size: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__max_size = convert_size(max_size)
        self.__cache_dir = cache_dir

    @property
    def id_(self) -> str:
        return ConfigurationLevel.RUNTIME.value
    
    @property
    def cache_dir(self) -> str:
        return self.__cache_dir

    @property
    def max_size(self) -> int:
        return self.__max_size


class ConfigurationManager:
    def __init__(
            self,
            configuration_priority: List[Configuration] = [
                HardcodedConfiguration(),
                HomeFileConfiguration(),
                LocalFileConfiguration(),
                EnvironementConfiguration(),
            ],
            cache_dir: str = None,
            max_size: str = None) -> None:
        configuration_priority.append(RuntimeConfiguration(cache_dir, max_size))
        self.__configuration_priority = configuration_priority


    @property
    def cache_dir(self) -> str:
        for config in reversed(self.__configuration_priority):
            if config.is_set_cache_dir:
                return config.cache_dir

    @property
    def max_size(self) -> int:
        for config in reversed(self.__configuration_priority):
            if config.is_set_max_size:
                return config.max_size

    def set_cache_dir(self, value: Any, level: ConfigurationLevel):
        """Update cache_dir variable."""

        for config in reversed(self.__configuration_priority):
            if config.id_ == level:
                config.set_cache_dir(value)
                return
        raise ValueError(f'The given configuration {level} is not known.')
        
    def set_max_size(self, value: str, level: ConfigurationLevel):
        """Update max_size variable."""

        for config in reversed(self.__configuration_priority):
            if config.id_ == level:
                config.set_max_size(value)
                return
        raise ValueError(f'The given configuration {level} is not known.')

    def display(self):
        """Print the full configuration thanks to tabulate lib."""

        not_defined_value = 'Not defined'
        config_table = [
            [
                c.id_,
                c.cache_dir if c.is_set_cache_dir else not_defined_value,
                c.max_size if c.is_set_max_size else not_defined_value
            ]
            for c in self.__configuration_priority
        ]
        header = ['Origin', 'cache_dir', 'max_size']
        footer = [['Used values', self.cache_dir, self.max_size]]
        print(tabulate(config_table + footer, header, tablefmt='psql'))


def convert_size(raw_size: str) -> int:
    """Interpret the given raw_size str from terra, giga, mega or bytes to bytes.
    Return None if None is given."""

    if raw_size == None:
        return None
    if re.match(r'^\d+[tgm]$', str(raw_size)):
        multiplicator_map = {
            't': 1_000_000_000_000,
            'g': 1_000_000_000,
            'm': 1_000_000
        }
        return int(raw_size[:-1]) * multiplicator_map[raw_size[-1].lower()]
    elif re.match(r'^\d+$', str(raw_size)):
        return int(raw_size)
    else:
        raise XtremCacheInputError(
            f'Invalid max_size format: get {raw_size}, correct format is \d+[tgm]? e.g.: \'5g\', \'100m\', \'5000\' or \'1t\'.')
