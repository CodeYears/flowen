import os
from collections.abc import Callable
from pathlib import Path

from flowen.collect import Collector, Directory, Module
from flowen.conftest_handle import Conftest
from flowen.parseopt import Parser


class CmdOptions:
    def __init__(self, parser: Parser):
        self._parser = parser._parser

    def __getattr__(self, name):
        return getattr(self._parser.parse_args([]), name)


class Config:
    def __init__(self, topdir=None):
        self._parser = Parser()
        self.topdir = topdir
        self.conftest = Conftest()
        self.option = CmdOptions(self._parser)

    def getfsnode(self, path: Path | str) -> Collector:
        path = Path(path)
        if path.is_dir():
            col = Directory(path)
        else:
            col = Module(path, parent=Directory(path.parent))

        col.config = self
        return col

    def parse(self, args: list):
        assert not hasattr(self, "args")
        self.conftest.setinitial(args)

        if not args:
            args.append(Path.cwd())

        self.args = [Path(arg) for arg in args]
        self.topdir = gettopdir(self.args)

    def _reparse(self, args: list) -> Config:
        global config
        old_config = config
        try:
            temp_config = Config()
            temp_config.parse(args)
            return temp_config

        finally:
            config = old_config

    def addoptions(self, group_name: str, configure: Callable):
        group = self._parser.addgroup(group_name)
        configure(group)
        return group

    def getbasetemp(self):
        if hasattr(self, "basetemp"):
            return self.basetemp


def gettopdir(args: list[Path]):
    common = Path(os.path.commonpath(args))
    if common.is_dir():
        return common

    return common.parent


config = Config()
