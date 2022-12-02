import argparse
import inspect
import logging
from typing import List

from xtremcache import log_level
from xtremcache.cachemanager import CacheManager
from xtremcache.exceptions import *
from xtremcache.utils import *


class XtreamCacheArgumentParser:
    """Handle arguments parsing in command line usage."""

    def __init__(self):
        # Global parser
        self._parser = argparse.ArgumentParser(
            description='Cache files and directories with unique identifiers and later uncache them to specific locations.')
        self._parser.add_argument(
            '--timeout', '-t',
            dest='timeout',
            type=str,
            action='store',
            required=False,
            help='Maximum time of execution in second before stop of the process.')
        def int_between_0_and_50(string: str) -> int:
            # try:
            tested_int = int(string)
            if tested_int in range(log_level.NOTSET, log_level.CRITICAL+1):
                return tested_int
            else:
                raise ValueError()
        self._parser.add_argument(
            '--verbosity', '-v',
            dest='verbosity',
            type=int_between_0_and_50,
            required=False,
            default=30,
            help=f'Level of verbosity of XtremCache from {log_level.NOTSET} for debugging to {log_level.CRITICAL} for critical only.')

        # Command parser
        command_parser = self._parser.add_subparsers(
            dest='command',
            required=True,
            help='Choose the command to run.')

        # Cache parser
        cache_parser = command_parser.add_parser(
            'cache',
            description='Cache the given file or directory.')
        cache_parser.add_argument(
            '--force', '-f',
            dest='force',
            action='store_true',
            required=False,
            help='Force to update current cached file or directory if the id is already used.')
        cache_parser.add_argument(
            '--id', '-i',
            dest='id',
            type=str,
            action='store',
            required=True,
            help='Unique id that will be give to the archive in cache.')
        cache_parser.add_argument(
            'path',
            type=str,
            help='Path to the file or directory to store in cache.')
        cache_parser.add_argument(
            '--excluded', '-x',
            dest='excluded',
            type=str,
            nargs='*',
            action='store',
            required=False,
            help='Explicitly exclude the specified list of file and dir (relative path from given target).')
        cache_parser.add_argument(
            '--compression-level', '-c',
            dest='compression_level',
            type=int,
            choices=range(0, 10),
            required=False,
            default=6,
            help='Level of compression 0 is the fastest and 9 is the most compressed (based on zip -#).')

        # Uncache parser
        uncache_parser = command_parser.add_parser(
            'uncache',
            description='Uncache a archive from cache.')
        uncache_parser.add_argument(
            '--id', '-i',
            dest='id',
            type=str,
            required=True,
            help='Id of the wanted archive to uncache.')
        uncache_parser.add_argument(
            'path',
            type=str,
            help='Destination file or directory.')

        # Remove parser
        remove_parser = command_parser.add_parser(
            'remove',
            description='Remove archives from cache.')
        remove_parser.add_argument(
            '--id', '-i',
            dest='id',
            type=str,
            required=False,
            help='Id of the archive to remove, if not specified, remove all archives.')

        # Config parser
        config_parser = command_parser.add_parser(
            'config',
            description='Administrate xtreamcache configuration.')
        config_subcommand = config_parser.add_subparsers(
            dest='config_subcommand',
            required=True,
            help='Choose configuration subcommand to run.')
        config_subcommand.add_parser(
            'display',
            description='Display all configurations layer used.')
        config_set_parser = config_subcommand.add_parser(
            'set',
            description='Edit the file configuration.')
        config_set_parser.add_argument(
            'var',
            type=str,
            help='Name of the variable to change.')
        config_set_parser.add_argument(
            'value',
            type=str,
            help='New value to apply at the given variable.')
        config_set_level = config_set_parser.add_mutually_exclusive_group()
        config_set_level.add_argument(
            '--local', '-l',
            action='store_const',
            dest='level',
            const='local',
            default='local')
        config_set_level.add_argument(
            '--global', '--glob' '-g',
            action='store_const',
            dest='level',
            const='global')

    def get_args(self, argv: List[str]) -> argparse.Namespace:
        """Parse argument from argv into a coherant namespace."""

        args = self._parser.parse_args(argv)
        return args


class CommandRunner():
    """Convert input command (executable arguments) to CacheManager method and run them."""

    def __init__(self, manager: CacheManager) -> None:
        self.__manager = manager

    def run(self, args: List[str]) -> None:
        """Execute the given command internally."""

        if args.command == 'config':
            return self.config_run(args)
        try:
            # Extract args from command only they are usefull for this sub_command.
            command_func = getattr(self.__manager, args.command)
            wanted_args = filter(lambda k: k != 'self', inspect.getfullargspec(command_func).args)
            # Build the wanted list of kwargs from past argument.
            kwargs = {}
            for key in wanted_args:
                value = getattr(args, key, None)
                if value:
                    kwargs[key] = value        
        except Exception as e:
            logging.error(e)
            raise XtremCacheInputError(e)
        command_func(**kwargs)

    def config_run(self, args: List[str]) -> None:
        """Execute the given config command internally."""

        if args.config_subcommand == 'set':
            try:
                command_func = {
                    'cache_dir': self.__manager.set_cache_dir,
                    'max_size': self.__manager.set_max_size,
                }[args.var]
            except KeyError as e:
                raise XtremCacheInputError(f'Impossible to set the varibale: {e}')
            level = {
                'local': 'Local file',
                'global': 'Global file',
            }[args.level]
            command_func(args.value, level)
            self.__manager.display()
        elif args.config_subcommand == 'display':
            command_func = getattr(self.__manager, args.config_subcommand)
            kwargs = {
                key: getattr(args, key, None)
                for key
                in inspect.getfullargspec(command_func).args
                if key != 'self'
            }
            command_func(**kwargs)


def exec(argv: List[str]) -> int:
    """Handle the full process execution in command line."""

    rt = 0
    try:
        args = XtreamCacheArgumentParser().get_args(argv)
        logging.basicConfig(
            level=args.verbosity,
            format='[XtremCache %(levelname)s - %(asctime)s]: %(message)s')
        CommandRunner(CacheManager(
            cache_dir=args.cache_dir if 'cache_dir' in args else None,
            max_size=args.max_size if 'max_size' in args else None,
            verbosity=args.verbosity
        )).run(args)
    except Exception as e:
        logging.error(f'{e.__class__.__name__}: {e}')
        rt = 1
    return rt
