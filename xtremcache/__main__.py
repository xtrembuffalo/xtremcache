import sys
from xtremcache.main import exec

def main():
    sys.exit(exec(sys.argv[1:]))

if __name__ == '__main__':
    main()