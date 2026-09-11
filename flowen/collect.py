import inspect
import types


class Node:
    def __init__(self, obj, parent=None):
        self.obj = obj
        self.parent = parent

    def __eq__(self, value):
        if hasattr(value, "obj"):
            return self.obj is value.obj

        return False

    def __hash__(self):
        return hash(self.obj)

    def getparent(self, cls):
        current = self
        while current is not None:
            if cls is Module and isinstance(current.obj, types.ModuleType):
                return current
            if cls is Class and inspect.isclass(current.obj):
                return current
            current = current.parent
        return None


class Collector(Node):
    def collect_by_name(self, name: str):
        sub = getattr(self.obj, name)

        if inspect.isfunction(sub):
            return Function(sub, parent=self)

        if inspect.isclass(sub):
            return Class(sub, parent=self)


class Module(Collector):
    pass


class Class(Collector):
    pass


class Function(Collector):
    pass


class Item:
    pass
