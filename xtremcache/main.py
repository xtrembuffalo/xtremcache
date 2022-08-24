import sys
import os
import argparse
import inspect
from pathlib import Path

from xtremcache.configuration import ConfigurationFactory
from xtremcache.utils import *
from xtremcache.exceptions import *
from xtremcache.cachemanager import CacheManager

# Configuration
class CommandRunner():
    """Convert input command (executable arguments) to CacheManager method."""
    
    def __init__(self, manager, configuration) -> None:
        self.__manager = manager
        self.__configuration = configuration

    def run(self, args) -> None:
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
def get_args(argv) -> argparse.Namespace:
    # Global
    parser = argparse.ArgumentParser(
        description='Local cache'
    )
    # Command
    sub_parsers = parser.add_subparsers(help="subparsers", dest='command')

    # Cache
    cache_parser = sub_parsers.add_parser('cache', help='Put in cache.')
    cache_parser.add_argument(
        '--id',
        '-i',
        type=str,
        default=None,
        help='UUID'
    )
    cache_parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='Force update current cached archive.'
    )
    cache_parser.add_argument(
        'path',
        type=str,
        help='Directory or file to cache.'
    )

    # Uncache
    uncache_parser = sub_parsers.add_parser('uncache', help='Put in cache')
    uncache_parser.add_argument(
        '--id',
        '-i',
        type=str,
        default=None,
        help='UUID'
    )
    uncache_parser.add_argument(
        'path',
        type=str,
        help='Cache destination.'
    )

    # Config
    config_parser = sub_parsers.add_parser('config', help='Configuation.')
    config_parser.add_argument(
        '--cache-dir',
        '-c',
        type=str,
        default=None,
        help='Location of datas.'
    )
    config_parser.add_argument(
        '--max-size',
        '-s',
        type=int,
        default=None,
        help='Maximum size of data dir in bytes.'
    )
    
    # Configuration file location
    parser.add_argument(
        '--config-file',
        '-c',
        type=str,
        required=False,
        default=os.path.join(Path.home(), f".{get_app_name()}", 'config'),
        help='Location of configuration file.'
    )
    
    return parser.parse_args(args=argv)

def command_runnner(args, configuration) -> None:
    CommandRunner(CacheManager(
        configuration.cache_dir,
        configuration.max_size
        ),
        configuration).run(args)

def main(argv) -> int:
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