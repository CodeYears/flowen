import inspect
from pathlib import Path

from flowen.utils import load_module


class Node:
    def __init__(self, name: str, parent: Node = None):
        from flowen.config import Config

        self.name = name
        self.parent = parent
        self.fspath: Path = getattr(parent, "fspath", None)
        self.config: Config = getattr(parent, "config", None)

    def __hash__(self):
        return hash((self.name, self.parent))

    def getparent(self, parent_type):
        cur = self.parent
        while cur:
            if isinstance(cur, parent_type):
                return cur
            cur = cur.parent
        return None

    def __eq__(self, value):
        if not isinstance(value, Node):
            return False

        return hash(self) == hash(value)

    def _getfsnode(self, path: Path):
        if path == self.fspath:
            return self

        return Module(path, self)

    def listchain(self, rootfirst: bool = False):
        l = [self]
        while True:
            cur = l[-1].parent

            if cur:
                l.append(cur)
            else:
                if not rootfirst:
                    return l
                else:
                    return reversed(l)

    def listnames(self):
        return [item.name for item in self.listchain(True)]

    def _totrail(self):
        if not self.fspath.is_relative_to(self.config.topdir):
            raise ValueError(f"{self.fspath} 不是 {self.config.topdir} 和他的子路径")

        top_parent = self.listchain()[-1]
        relpath = top_parent.fspath.relative_to(self.config.topdir)

        results = []
        for item in self.listchain():
            if isinstance(item, Directory):
                break

            results.append(item)

        return str(relpath), tuple(item.name for item in results)

    @staticmethod
    def _fromtrail(trail, config):
        col = config.getfsnode(config.topdir / trail[0])
        nodes = list(trail[1])

        while nodes:
            col = col.collect_by_name(nodes.pop(0))

        return col


class Collector(Node):
    def collect_by_name(self, name: str) -> Node:
        for item in self.collect():
            if item.name == name:
                return item


class FSCollector(Collector):
    def obj(self):
        return getattr(self.parent.obj(), self.name)

    def __init__(self, fspath, parent=None):
        super().__init__(fspath.name, parent=parent)
        self.fspath = Path(fspath)


class Directory(FSCollector):
    def collect(self):
        l = []
        for path in self.fspath.iterdir():
            res = self.consider(path)
            if res is not None:
                l.append(res)

        l.sort(key=lambda x: x.name)
        return l

    def _getitembynames(self, names: list):
        idx = names.index(self.name)
        cur = self
        for name in names[idx + 1 :]:
            cur = cur.collect_by_name(name)

        return cur

    def consider(self, path: Path):
        if path.is_file():
            return self.consider_file(path)

        if path.is_dir():
            return self.consider_dir(path)

    def consider_file(self, path: Path):
        if not (path.stem.startswith("test_") or path.stem.endswith("_test")):
            return
        if path.suffix != ".py":
            return

        return Module(path, parent=self)

    def consider_dir(self, path: Path):
        if path.name.startswith((".", "_", "{", "CVS")):
            return

        return Directory(path, parent=self)


class Module(FSCollector):
    def obj(self):
        return load_module(self.fspath)

    def collect(self):
        return list(self._bulid_items_by_name().values())

    def _bulid_items_by_name(self) -> dict:
        d = {}
        dic = getattr(self.obj(), "__dict__", {})

        for name, obj in dic.items():
            item = self.makeitem(name, obj)
            if item is not None:
                d[name] = item
        return d

    def makeitem(self, name: str, obj):
        if inspect.isclass(obj):
            return Class(name, self)

        if inspect.isfunction(obj):
            return Function(name, self)

        return None


class Class(Collector):
    def obj(self):
        return getattr(self.parent.obj(), self.name)

    def collect(self):
        return list(self._bulid_items_by_name().values())

    def _bulid_items_by_name(self) -> dict:
        d = {}
        dic = getattr(self.obj(), "__dict__", {})

        for name, obj in dic.items():
            item = self.makeitem(name, obj)
            if item is not None:
                d[name] = item
        return d

    def makeitem(self, name: str, obj):
        if inspect.isclass(obj):
            return Class(name, self)

        if inspect.isfunction(obj):
            return Function(name, self)

        return None


class Function(Node):
    pass


class Item:
    pass
