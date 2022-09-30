import argparse
import inspect
from typing import List

from xtremcache.configuration import Configuration, ConfigurationFactory
from xtremcache.utils import *
from xtremcache.exceptions import *
from xtremcache.cachemanager import CacheManager


# Configuration
class CommandRunner():
    """Convert input command (executable arguments) to CacheManager method."""

    def __init__(self, manager: CacheManager) -> None:
        self.__manager = manager

    def run(self, args: List[str]) -> None:
        """Execute the given command internally."""

        command = getattr(args, 'command', None)
        if command:
            try:
                command_func = getattr(self.__manager, command, None)
                if command_func:
                    kwargs = {}
                    for key in inspect.getfullargspec(command_func).args:
                        if key != 'self':
                            kwargs[key] = getattr(args, key, None)
                    command_func(**kwargs)
            except Exception as e:
                print(e)
                raise XtremCacheInputError(e)


# Argument parser
def get_args(argv: List[str]) -> argparse.Namespace:
    """Parse argument from argv into a coherant namespace."""

    # Global
    parser = argparse.ArgumentParser(
        description='Handle generic file and directories caching')

    # Command
    sub_parsers = parser.add_subparsers(
        help='subparsers',
        dest='command')

    # Cache
    cache_parser = sub_parsers.add_parser(
        'cache',
        help='Save file or directory with unique id.')
    cache_parser.add_argument(
        '--id',
        '-i',
        type=str,
        default=None,
        help='Unique identificator.')
    cache_parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='Force update current cached file or directory.')
    cache_parser.add_argument(
        'path',
        type=str,
        help='Directory or file to cache.')

    # Uncache
    uncache_parser = sub_parsers.add_parser(
        'uncache',
        help='Extract cached file or directory.')
    uncache_parser.add_argument(
        '--id',
        '-i',
        type=str,
        default=None,
        help='Unique identificator.')
    uncache_parser.add_argument(
        'path',
        type=str,
        help='Destination file or directory.')

    # Remove one
    remove_parser = sub_parsers.add_parser(
        'remove',
        help='Remove specific item.')
    remove_parser.add_argument(
        '--id',
        '-i',
        type=str,
        default=None,
        help='Unique identificator.')

    # Remove all
    sub_parsers.add_parser(
        'remove_all',
        help='Remove all cached item.')

    # Config
    config_parser = sub_parsers.add_parser(
        'config',
        help='Configuation.')
    config_parser.add_argument(
        '--cache-dir',
        '-c',
        type=str,
        default=None,
        help='Location of datas.')
    config_parser.add_argument(
        '--max-size',
        '-s',
        type=int,
        default=None,
        help='Maximum size of data dir in Mo.')

    # Configuration file location
    parser.add_argument(
        '--config-file',
        '-c',
        type=str,
        required=False,
        default=os.path.join(Path.home(), f'.{get_app_name()}', 'config'),
        help='Location of configuration file.')

    return parser.parse_args(args=argv)

def command_runnner(args: List[str], configuration: Configuration) -> None:
    """Execute the given command internally."""

    CommandRunner(CacheManager(
        configuration.cache_dir,
        configuration.max_size
    )).run(args)

def exec(argv: List[str]) -> int:
    """Handle the full process execution in command line."""

    rt = 0
    try:
        args = get_args(argv=argv)
        command_runnner(
            args,
            ConfigurationFactory(args.config_file).from_file(args))
    except Exception as e:
        print(e)
        rt = 1
    return rt
