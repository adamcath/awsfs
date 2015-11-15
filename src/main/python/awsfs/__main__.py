import logging
from sys import argv, exit

from fuse import FUSE

from awsfs import AwsOps

if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(AwsOps(), argv[1], foreground=False)
