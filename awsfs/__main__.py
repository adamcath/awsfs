import logging
import logging.handlers
from sys import argv, exit, stderr


def error(line):
    stderr.write(line + '\n')
    stderr.flush()

try:
    from fuse import FUSE
except EnvironmentError as e:
    if e.message != 'Unable to find libfuse':
        raise
    error('awsfs requires the native package FUSE to be installed.')
    error('You can get it from https://osxfuse.github.io,')
    error('or from homebrew: `brew install Caskroom/cask/osxfuse`.')
    exit(2)

from awsfs import AwsOps

syslog_handler = logging.handlers.SysLogHandler(address='/var/run/syslog')
syslog_handler.setFormatter(
    logging.Formatter(
        'awsfs: %(threadName)s %(message)s'))
logging.getLogger().addHandler(syslog_handler)
logging.getLogger().setLevel(logging.DEBUG)


usage='''usage: awsfs path

Mounts a virtual device in the filesystem in which
you can access various AWS services, treating them
like directories and files.

Your AWS credentials should be in your environment.
The simplest way is to set AWS_ACCESS_KEY_ID and
AWS_SECRET_ACCESS_KEY. See the AWS docs for other
methods.

path    Where awsfs should be mounted (e.g. ~/aws).
        Must be a directory that exists and you can
        write.'''


def main():
    if len(argv) != 2:
        error(usage)
        exit(1)

    FUSE(AwsOps(), argv[1], foreground=False)


if __name__ == '__main__':
    main()
