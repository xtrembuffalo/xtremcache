from re import A
import sys
import os
import argparse
from pathlib import Path

from xtremcache.configuration import ConfigurationFactory
from xtremcache.utils import *
from xtremcache.cachemanager import CacheManager

# Configuration
class CommandRunner():
    """Convert input command (executable arguments) to CacheManager method."""
    
    def __init__(self, manager) -> None:
        self.__manager = manager

    def cache(self, args):
        self.__manager.cache(id = getattr(args, 'id', None),
                             path = getattr(args, 'path', None),
                             force = getattr(args, 'force', None))
    
    def uncache(self, args):
        self.__manager.uncache(id = getattr(args, 'id', None),
                               path = getattr(args, 'path', None))

# Argument parser
def get_args():
    parser = argparse.ArgumentParser(
        description='Local cache'
    )
    sub_parsers = parser.add_subparsers(help="subparsers", dest='command')
    
    # Put in cache
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
    
    # Configuration file location
    parser.add_argument(
        '--config-file',
        '-c',
        type=str,
        required=False,
        default=os.path.join(Path.home(), f".{get_app_name()}", 'config'),
        help='Max cache size (Mo).'
    )
    return parser.parse_args()

def command_runnner(args, configuration):
    command = getattr(args, 'command', None)
    if command:
        command_runner = CommandRunner(CacheManager(configuration.cache_dir, configuration.max_size))
        attr = getattr(command_runner, command, None)
        if attr is not None:
            attr(args)

def run(args):
    # Init configuration
    configuration = ConfigurationFactory(args.config_file).from_file()
    print(configuration)

    # Command runner
    command_runnner(args, configuration)

def main():
    return run(get_args())

if __name__ == '__main__':
    sys.exit(main())