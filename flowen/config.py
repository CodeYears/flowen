from pathlib import Path

from flowen.collect import Module
from flowen.utils import load_module


class Config:
    def __init__(self, paths: list[Path]):
        self.paths = paths

    def getfsnode(self, path: Path):
        return Module(load_module(path))
