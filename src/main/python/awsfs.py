#!/usr/bin/env python

import logging

from errno import *
from stat import S_IFDIR, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

import boto3

class VNode:
    def is_dir(self):
        raise Exception("Abstract!")

    def get_children(self):
        raise Exception("Abstract!")

    def get_child(self, name):
        for (cname, cnode) in self.get_children():
            if name == cname:
                return cnode
        return None

    def read(self):
        raise Exception("Abstract!")

    def write(self, bytes):
        raise Exception("Abstract!")

    def get_size(self):
        raise Exception("Abstract!")


class VDir(VNode):
    def is_dir(self):
        return True

    def get_size(self):
        return 0


class VFile:
    def is_dir(self):
        return False


class StaticFile(VFile):
    def __init__(self, contents):
        self.contents = contents

    def read(self):
        return self.contents

    def write(self, _):
        pass

    def get_size(self):
        return len(self.contents)


class RootDir(VDir):
    def __init__(self):
        self.children = [("dynamodb", DynamoDir()), ("ec2", Ec2Dir())]

    def get_children(self):
        return self.children


class DynamoDir(VDir):
    def __init__(self):
        self.children = None

    def get_children(self):
        if not self.children:
            self.children = [
                (region_name, DynamoRegionDir(region_name))
                for region_name
                in ["us-east-1", "us-west-2", "us-west-1", "eu-west-1",
                    "eu-central-1", "ap-southeast-1", "ap-northeast-1",
                    "sa-east-1"]]
        return self.children


class DynamoRegionDir(VDir):
    def __init__(self, region):
        self.region = region

        def load(_):
            db = boto3.client('dynamodb', region_name=self.region)
            result = []
            for page in db.get_paginator('list_tables').paginate():
                result += [
                    (table_name, DynamoTable(self.region, table_name))
                    for table_name
                    in page['TableNames']]
            return result

        self.cache = LoadingCache(load, 5)

    def get_children(self):
        children = self.cache.get('children')
        return children


class DynamoTable(VDir):
    def __init__(self, region, table_name):
        pass

    def get_children(self):
        return [("some item", StaticFile("its value".encode()))]


class Ec2Dir(VDir):
    def get_children(self):
        return [("some node", StaticFile("its value".encode()))]


if not hasattr(__builtins__, 'bytes'):
    bytes = str


class Awsfs(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

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
        return 0

    def chown(self, path, uid, gid):
        pass

    def create(self, path, mode):
        return ENOENT

    def getattr(self, path, fh=None):
        node = self.resolve(path)
        if node.is_dir():
            return dict(st_mode=(S_IFDIR | 0755), st_ctime=time(),
                               st_mtime=time(), st_atime=time(), st_nlink=2)
        else:
            return dict(st_mode=(S_IFREG), st_nlink=1,
                                st_size=node.get_size(), st_ctime=time(), st_mtime=time(),
                                st_atime=time())

    def getxattr(self, path, name, position=0):
        return ''

    def listxattr(self, path):
        return []

    def mkdir(self, path, mode):
        return ENOENT

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
        return ENOENT

    def removexattr(self, path, name):
        return ENOENT

    def rename(self, old, new):
        return ENOENT

    def rmdir(self, path):
        return ENOENT

    def setxattr(self, path, name, value, options, position=0):
        return ENOENT

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        return ENOENT

    def truncate(self, path, length, fh=None):
        return ENOENT

    def unlink(self, path):
        return ENOENT

    def utimens(self, path, times=None):
        return ENOENT

    def write(self, path, data, offset, fh):
        return ENOENT


class LoadingCache:
    def __init__(self, load_func, ttl_secs):
        self.cache = dict()
        self.load_func = load_func
        self.ttl_secs = ttl_secs

    def get(self, key):
        if key in self.cache:
            (value, expiry) = self.cache[key]
            if time() < expiry:
                return value

        new_value = self.load_func(key)
        self.cache[key] = (new_value, time() + self.ttl_secs)
        return new_value


if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    logging.getLogger().setLevel(logging.DEBUG)
    fuse = FUSE(Awsfs(), argv[1], foreground=True)
