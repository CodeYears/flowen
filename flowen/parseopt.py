import argparse
from collections.abc import Callable


class Parser:
    def __init__(self, usage=None, processopt: Callable | None = None):
        self._parser = argparse.ArgumentParser(usage=usage or "default usage")
        self._default_group = self._parser.add_argument_group("default")
        self.groups = {"default": self._default_group}
        self.processopt = processopt

    def parse(self, args: list, namespace=None):
        parse_args = self._parser.parse_args(args, namespace)
        if self.processopt:
            self.processopt(parse_args)

        return parse_args

    def add_argument(self, *args, **kwargs):
        self._default_group.add_argument(*args, **kwargs)

    def addgroup(self, title: str, description: str | None = None):
        if title in self.groups:
            raise ValueError(f"{title} 参数组已存在")

        group = self._parser.add_argument_group(title, description)
        self.groups[title] = group
        return group

    def getgroup(self, title: str, description: str | None = None):
        try:
            return self.groups[title]
        except KeyError:
            return self.addgroup(title, description)
