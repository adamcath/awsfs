import logging
import logging.handlers
from sys import argv, exit, stderr

from awsfs import AwsOps


usage = '''usage: awsfs path

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

    try:
        from fuse import FUSE
    except EnvironmentError as e:
        if e.message != 'Unable to find libfuse':
            raise
        error('awsfs requires the native package FUSE to be installed.')
        error('You can get it from https://osxfuse.github.io,')
        error('or from homebrew: `brew install Caskroom/cask/osxfuse`.')
        exit(2)

    setup_logging()

    FUSE(AwsOps(), argv[1], foreground=False)


def error(line):
    stderr.write(line + '\n')
    stderr.flush()


def setup_logging():

    # Add syslog handler
    syslog_handler = logging.handlers.SysLogHandler(address='/var/run/syslog')
    syslog_handler.setFormatter(
        logging.Formatter(
            'awsfs: %(levelname)s %(threadName)s %(name)s %(message)s'))
    logging.getLogger().addHandler(syslog_handler)

    # Add file handler
    file_handler = logging.handlers.RotatingFileHandler(
        'awsfs.log', maxBytes=1024 * 1024 * 10)
    file_handler.setFormatter(
        logging.Formatter(
            '%(levelname)s %(threadName)s %(name)s %(message)s'))
    logging.getLogger().addHandler(file_handler)

    # Set log levels
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger('botocore.vendored.requests.packages.urllib3') \
        .setLevel(logging.WARNING)


if __name__ == '__main__':
    main()
