from errno import *
from stat import S_IFDIR, S_IFREG
from time import time

from fuse import FuseOSError, Operations, LoggingMixIn

from vfs import *
from dynamo import dynamo_root
from ec2 import ec2_root


class RootDir(VDir):
    def __init__(self):
        VDir.__init__(self)
        self.children = [("dynamo", dynamo_root()), ("ec2", ec2_root())]

    def get_children(self):
        return self.children


class AwsOps(LoggingMixIn, Operations):
    def __init__(self):
        self.root = RootDir()

    def resolve(self, path):
        parts = path.split("/")[1:]
        if parts[-1] == '':
            del parts[-1]

        cur = self.root
        for part in parts:
            if not cur.is_dir():
                raise FuseOSError(ENOTDIR)
            child = cur.get_child(part)
            if not child:
                raise FuseOSError(ENOENT)
            cur = child

        return cur

    # The operations

    def chmod(self, path, mode):
        raise FuseOSError(EPERM)

    def chown(self, path, uid, gid):
        raise FuseOSError(EPERM)

    def create(self, path, mode, fi=None):
        raise FuseOSError(EPERM)

    def getattr(self, path, fh=None):
        node = self.resolve(path)
        if node.is_dir():
            return dict(st_mode=(S_IFDIR | 0755), st_ctime=time(),
                        st_mtime=time(), st_atime=time(), st_nlink=2)
        else:
            return dict(st_mode=S_IFREG, st_nlink=1, st_size=node.get_size(),
                        st_ctime=time(), st_mtime=time(), st_atime=time())

    def getxattr(self, path, name, position=0):
        return ''

    def listxattr(self, path):
        return []

    def mkdir(self, path, mode):
        raise FuseOSError(EPERM)

    def open(self, path, flags):
        node = self.resolve(path)
        if node.is_dir():
            raise FuseOSError(EISDIR)
        return 0

    def read(self, path, size, offset, fh):
        node = self.resolve(path)
        if node.is_dir():
            raise FuseOSError(EISDIR)

        contents = node.read()
        if len(contents) < offset + size:
            return []
        return contents[offset:offset + size]

    def readdir(self, path, fh):
        node = self.resolve(path)
        if not node.is_dir():
            raise FuseOSError(ENOTDIR)

        return [name for (name, value) in node.get_children()]

    def readlink(self, path):
        raise FuseOSError(EPERM)

    def removexattr(self, path, name):
        raise FuseOSError(EPERM)

    def rename(self, old, new):
        raise FuseOSError(EPERM)

    def rmdir(self, path):
        raise FuseOSError(EPERM)

    def setxattr(self, path, name, value, options, position=0):
        raise FuseOSError(EPERM)

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

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
