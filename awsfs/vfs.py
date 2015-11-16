from stat import S_IFDIR, S_IFREG, S_IFLNK

from cache import LoadingCache


class VNode:
    def __init__(self):
        pass

    def is_dir(self):
        raise Exception("Abstract!")

    def get_type(self):
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

    def write(self, bytebuf):
        raise Exception("Abstract!")

    def get_size(self):
        raise Exception("Abstract!")


class VDir(VNode):
    def is_dir(self):
        return True

    def get_type(self):
        return S_IFDIR

    def get_size(self):
        return 0


class VFile(VNode):
    def is_dir(self):
        return False

    def get_type(self):
        return S_IFREG


class VLink(VFile):
    def __init__(self, dest):
        VFile.__init__(self)
        self.dest = dest

    def get_type(self):
        return S_IFLNK

    def get_size(self):
        return len(self.dest.encode())

    def read(self):
        return self.dest.encode()


class LazyReadOnlyDir(VDir):
    def __init__(self, get_children_func):
        VDir.__init__(self)
        self.get_children_func = get_children_func

    def get_children(self):
        return self.get_children_func()


class CachedLazyReadOnlyDir(LazyReadOnlyDir):
    def __init__(self, get_children_func, ttl_sec):
        cache = LoadingCache(lambda _: get_children_func(), ttl_sec)
        LazyReadOnlyDir.__init__(self, lambda: cache.get('children'))


class LazyReadOnlyFile(VFile):
    def __init__(self, get_contents_func):
        VFile.__init__(self)
        self.get_contents_func = get_contents_func

    def read(self):
        return self.get_contents_func()

    def write(self, _):
        pass

    def get_size(self):
        # TODO This is crappy for perf. Does it really need to be accurate?
        return len(self.read())


class StaticFile(LazyReadOnlyFile):
    def __init__(self, contents):
        LazyReadOnlyFile.__init__(self, lambda: contents)
