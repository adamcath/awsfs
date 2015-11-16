import logging
import logging.handlers
from sys import argv, exit

from fuse import FUSE

from awsfs import AwsOps


def main():
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    syslog_handler = logging.handlers.SysLogHandler(address='/var/run/syslog')
    syslog_handler.setFormatter(
        logging.Formatter(
            'awsfs: %(threadName)s %(message)s'))
    logging.getLogger().addHandler(syslog_handler)

    logging.getLogger().setLevel(logging.DEBUG)

    FUSE(AwsOps(), argv[1], foreground=False)


if __name__ == '__main__':
    main()
