import logging
import os
from errno import *
from time import time

from botocore.exceptions import NoCredentialsError, \
    PartialCredentialsError, ClientError
from fuse import FuseOSError, Operations

from iam import iam_root
from dynamo import dynamo_root
from ec2 import ec2_root
from elb import elb_root
from s3 import s3_root
from vfs import *


log = logging.getLogger('awsfs')


class AwsOps(Operations):
    def __init__(self):
        self.root = RootDir()

    def __call__(self, op, *args):
        log.debug('-> %s %s', op, repr(args))
        try:
            ret = Operations.__call__(self, op, *args)
            log.debug('<- %s %s', op, repr(ret))
            return ret
        except FuseOSError as fuse_ex:
            # The lower-level code can log at a higher level if cares to
            log.debug('<- %s %d (%s)', op, fuse_ex.errno, fuse_ex.strerror)
            raise fuse_ex
        except BaseException as e:
            # For convenience, we let the lower-level code allow some
            # exceptions to bubble out. Process those now.
            fuse_ex, level = (None, None)
            try:
                (fuse_ex, level) = self.to_fuse_ex(e)
            except:
                log.fatal('<- %s failed to parse error. '
                          'Unmounting FS and crashing!',
                          op, exc_info=True)
                self.crash()

            if fuse_ex:
                log.log(level,
                        '<- %s %d (%s): %s: %s',
                        op, fuse_ex.errno, fuse_ex.strerror,
                        e.__class__.__name__, e.message or '-')
                raise fuse_ex
            else:
                # Crap, we didn't expect this kind of error.
                # Anything that made it out here is a programming error.
                # The wise choice is to dump core so we can debug post-mortem.
                log.fatal('<- %s resulted in an unrecoverable error. '
                          'Unmounting FS and crashing!',
                          op, exc_info=True)
                self.crash()

    def to_fuse_ex(self, e):
        # Some boto functions throw this
        if isinstance(e, IOError):
            return FuseOSError(EIO), logging.WARNING

        # This should have been check on startup, but it's possible
        # for it to get screwed up later
        if (isinstance(e, NoCredentialsError) or
                isinstance(e, PartialCredentialsError)):
            return FuseOSError(ENOLINK), logging.WARNING

        # boto operations return this when they are able to make the request,
        # but it fails
        if isinstance(e, ClientError):

            error_obj = ((e.response or {}).get('Error') or {})

            # Look at a few common response codes.
            # We can't try to capture them all. There's no comprehensive list
            # online.
            code = error_obj.get('Code')
            if code in ['ResourceNotFoundException']:
                return FuseOSError(ENOENT), logging.INFO
            if code in ['AuthFailure', 'UnauthorizedOperation']:
                return FuseOSError(EPERM), logging.WARNING
            if code in ['Blocked']:
                return FuseOSError(EPERM), logging.WARNING

            # There are zillions of response codes.
            # Use the HTTP status to figure out a little more.
            # Note this is not sufficient - trying to scan a non-existent
            # dynamo table results in ResourceNotFoundException but with 400!
            status = error_obj.get('HTTPStatusCode')
            if status in [401, 402, 403]:
                return FuseOSError(EPERM), logging.WARNING
            if status in [404, 410]:
                return FuseOSError(ENOENT), logging.INFO
            if status in [409]:
                return FuseOSError(ESTALE), logging.WARNING
            if status >= 500:
                return FuseOSError(EIO), logging.WARNING

            # This is bad, but we don't really need to crash.
            # We know that our call made it through but failed.
            # I think it's worth returning a generic EIO and then looking
            # in the logs to debug.
            log.error('Unexpected boto error %s',
                      str(e.response), exc_info=True)
            return FuseOSError(EIO), logging.ERROR

        return None, None

    # Unit tests can replace this
    def crash(self):
        try:
            for handler in logging.getLogger().handlers:
                handler.flush()
        finally:
            os.abort()

    #################################################
    # The actual operations
    #################################################

    def chmod(self, path, mode):
        raise FuseOSError(EPERM)

    def chown(self, path, uid, gid):
        raise FuseOSError(EPERM)

    def create(self, path, mode, fi=None):
        raise FuseOSError(EPERM)

    def getattr(self, path, fh=None):
        node = self.root.resolve(path)
        if node.is_dir():
            return dict(st_mode=(S_IFDIR | 0755), st_ctime=time(),
                        st_mtime=time(), st_atime=time(), st_nlink=2)
        else:
            return dict(st_mode=node.get_type(), st_nlink=1,
                        st_size=node.get_size(),
                        st_ctime=time(), st_mtime=time(), st_atime=time())

    def getxattr(self, path, name, position=0):
        return ''

    def listxattr(self, path):
        return []

    def mkdir(self, path, mode):
        raise FuseOSError(EPERM)

    def open(self, path, flags):
        node = self.root.resolve(path)
        if node.is_dir():
            raise FuseOSError(EISDIR)
        return 0

    def read(self, path, size, offset, fh):
        node = self.root.resolve(path)
        if node.is_dir():
            raise FuseOSError(EISDIR)

        contents = node.read()
        if len(contents) < offset + size:
            return []
        return contents[offset:offset + size]

    def readdir(self, path, fh):
        node = self.root.resolve(path)
        if not node.is_dir():
            raise FuseOSError(ENOTDIR)

        return [name for (name, value) in node.get_children()]

    def readlink(self, path):
        node = self.root.resolve(path)
        if node.get_type() != S_IFLNK:
            raise FuseOSError(EINVAL)
        return node.read()

    def removexattr(self, path, name):
        raise FuseOSError(EPERM)

    def rename(self, old, new):
        raise FuseOSError(EPERM)

    def rmdir(self, path):
        raise FuseOSError(EPERM)

    def setxattr(self, path, name, value, options, position=0):
        raise FuseOSError(EPERM)

    def statfs(self, path):
        return dict(f_bsize=0, f_blocks=0, f_bavail=0)

    def symlink(self, target, source):
        raise FuseOSError(EPERM)

    def truncate(self, path, length, fh=None):
        raise FuseOSError(EPERM)

    def unlink(self, path):
        raise FuseOSError(EPERM)

    def utimens(self, path, times=None):
        raise FuseOSError(EPERM)

    def write(self, path, data, offset, fh):
        raise FuseOSError(EPERM)


class RootDir(VDir):
    def __init__(self):
        VDir.__init__(self)
        self.children = [
            ("iam", iam_root()),
            ("dynamo", dynamo_root()),
            ("ec2", ec2_root()),
            ("elb", elb_root()),
            ("s3", s3_root())
        ]

    def get_children(self):
        return self.children

    def resolve(self, path):
        parts = path.split("/")[1:]
        if parts[-1] == '':
            del parts[-1]

        cur = self
        for part in parts:
            if not cur.is_dir():
                raise FuseOSError(ENOTDIR)
            child = cur.get_child(part)
            if not child:
                raise FuseOSError(ENOENT)
            cur = child

        return cur
