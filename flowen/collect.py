import inspect
from inspect import getmro
from pathlib import Path

from flowen.utils import load_module


class Node:
    def __init__(self, name: str, parent: Node = None):
        self.name = name
        self.parent = parent
        self.fspath: Path = getattr(parent, "fspath", None)
        self.config = getattr(parent, "config", None)

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
        return l

    def consider(self):
        if self.fspath.is_file():
            res = self.consider_file()

        return res

    def consider_file(self, path: Path):
        if path.name.startswith("pytest_") and path.suffix == ".py":
            return Module(path.name, parent=self)


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
