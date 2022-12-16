import sys
from xtremcache.main import run_xtremcache


def main():
    sys.exit(run_xtremcache(sys.argv[1:]))

if __name__ == '__main__':
    main()
