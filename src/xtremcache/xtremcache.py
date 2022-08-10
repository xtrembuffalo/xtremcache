import sys
import os
import argparse
from src.xtremcache.archiver import ZipArchiver
from src.xtremcache.configuration import Configuration, ConfigurationFactory
from src.xtremcache.utils import Utils
from pathlib import Path

# Configuration
class CacheManager():
    def __init__(self, cache_dir, max_size) -> None:
        self.__cache_dir = cache_dir
        self.__max_size = max_size

    def cache(self, id, path):
        archive_name = Utils.str_to_md5(id)
        destination = os.path.join(self.__cache_dir, archive_name)
        archiver = ZipArchiver(destination)
        archiver.archive(path)
    
    def uncache(self, id, path):
        archive_name = Utils.str_to_md5(id)
        source = os.path.join(self.__cache_dir, archive_name)
        archiver = ZipArchiver(source)
        archiver.extract(path)

# Configuration
class CommandRunner():
    def __init__(self, manager) -> None:
        self.__manager = manager

    def cache(self, args):
        self.__manager.cache(id = getattr(args, 'id', None),
                             path = getattr(args, 'path', None))
    
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
    cache_parser = sub_parsers.add_parser('cache', help='Put in cache')
    cache_parser.add_argument(
        '--id',
        type=str,
        default=None,
        help='UUID'
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
        type=str,
        required=False,
        default=os.path.join(Path.home(), f".{Utils.get_app_name()}", 'config'),
        help='Max cache size (Mo)'
    )
    return parser.parse_args()

def run(args):
    # Init configuration
    configuration = ConfigurationFactory(args.config_file).from_file()
    print(configuration)

    # Command runner
    command_runner = CommandRunner(CacheManager(configuration.cache_dir, configuration.max_size))
    command = getattr(args, 'command', None)
    attr = getattr(command_runner, command, None)
    if attr is not None:
        attr(args)

def main():
    return run(get_args())

if __name__ == '__main__':
    sys.exit(main())