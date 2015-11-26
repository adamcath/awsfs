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


class SDir(VDir):
    """
    A directory with static contents.
    """
    def __init__(self, children):
        VDir.__init__(self)
        self.children = children

    def get_children(self):
        return self.children


class LDir(VDir):
    """
    A directory with lazy-loaded contents.
    """
    def __init__(self, get_children_func):
        VDir.__init__(self)
        self.get_children_func = get_children_func

    def get_children(self):
        return self.get_children_func()


class CLDir(LDir):
    """
    A directory with cached, lazy-loaded contents.
    """
    def __init__(self, get_children_func, ttl_sec=60):
        cache = LoadingCache(lambda _: get_children_func(), ttl_sec)
        LDir.__init__(self, lambda: cache.get('children'))


class SFile(VFile):
    """
    A file with static contents.
    """
    def __init__(self, contents):
        VFile.__init__(self)
        self.contents = contents
        self.size = len(self.contents)

    def read(self):
        return self.contents

    def write(self, _):
        pass

    def get_size(self):
        return self.size


class LFile(VFile):
    """
    A file with lazy-loaded contents.

    :param size Of the file, in bytes.
                If 'auto', will be computed by calling read(). This is
                inadvisable since size is reported by stat(2), which is
                generally assumed to be fast (e.g. `ls` stats every file).
    """
    def __init__(self, get_contents_func, size='auto'):
        VFile.__init__(self)
        self.get_contents_func = get_contents_func
        self.size = size
        # TODO what if the contents change? We'll cache size forever

    def read(self):
        return self.get_contents_func()

    def write(self, _):
        pass

    def get_size(self):
        return len(self.read()) if self.size == 'auto' else self.size
