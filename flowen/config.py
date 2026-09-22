import os
from pathlib import Path

from flowen.collect import Collector, Directory, Module


class Config:
    def getfsnode(self, path: Path | str) -> Collector:
        path = Path(path)
        if path.is_dir():
            col = Directory(path)
        else:
            col = Module(path, parent=Directory(path.parent))

        col.config = self
        return col

    def parse(self, args):
        assert not hasattr(self, "args")
        self.args = [Path(arg) for arg in args]
        self.topdir = gettopdir(self.args)

    def _reparse(self, args: list):
        global config
        old_config = config
        try:
            temp_config = Config()
            temp_config.parse(args)
            return temp_config

        finally:
            config = old_config


def gettopdir(args: list[Path]):
    common = Path(os.path.commonpath(args))
    if common.is_dir():
        return common

    return common.parent


config = Config()
