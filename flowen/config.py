import argparse
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
        self._parser = Parser(processopt=self.processopt)
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

        path_args, opt_args = [], []
        for item in args:
            try:
                path = Path(item)
                if path.exists():
                    path_args.append(path)
                else:
                    opt_args.append(item)
            except Exception:  # noqa
                opt_args.append(item)

        # 这里的 args 都是路径参数
        if not path_args:
            path_args.append(Path.cwd())

        self.args = path_args
        self.conftest.setinitial(self.args)
        self._parser.parse(opt_args)
        self.topdir = gettopdir(self.args)

    def _reparse(self, args: list) -> Config:
        global config
        old_config = config
        try:
            config = Config()
            config.parse(args)
            return config

        finally:
            config = old_config

    def addoptions(self, group_name: str, configure: Callable):
        group = self._parser.addgroup(group_name)
        configure(group)
        return group

    def getbasetemp(self):
        if hasattr(self, "basetemp"):
            return self.basetemp

    def processopt(self, action: argparse.Action):
        if not action.dest:
            return

        val = os.environ.get("PYTEST_OPTION_" + action.dest.upper(), None)

        if val is not None:
            if isinstance(
                action, (argparse._StoreTrueAction, argparse._StoreFalseAction)
            ):
                val = self.parse_bool_opt(val)

            elif action.type is not None:
                val = action.type(val)

            action.default = val

        else:
            self.conftest.setinitial([])
            self.conftest.rget("pytest_option_" + action.dest.lower())

    def parse_bool_opt(self, val: str):
        if val.lower() in ("true", "1", "yes"):
            return True

        elif val.lower() in ("false", "0", "no"):
            return False

        raise ValueError(f"{val} 不是布尔类型，请重新设置环境变量！")


def gettopdir(args: list[Path]):
    common = Path(os.path.commonpath(args))
    if common.is_dir():
        return common

    return common.parent


config = Config()
