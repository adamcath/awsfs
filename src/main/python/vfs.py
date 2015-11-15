class VNode:
    def __init__(self):
        pass

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

    def write(self, bytebuf):
        raise Exception("Abstract!")

    def get_size(self):
        raise Exception("Abstract!")


class VDir(VNode):
    def is_dir(self):
        return True

    def get_size(self):
        return 0


class VFile(VNode):
    def is_dir(self):
        return False


class StaticFile(VFile):
    def __init__(self, contents):
        VFile.__init__(self)
        self.contents = contents

    def read(self):
        return self.contents

    def write(self, _):
        pass

    def get_size(self):
        return len(self.contents)
