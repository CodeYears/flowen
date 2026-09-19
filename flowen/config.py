from pathlib import Path

from flowen.collect import Collector, Directory, Module


class Config:
    def getfsnode(self, path: Path | str) -> Collector:
        path = Path(path)
        if path.is_dir():
            return Directory(path)

        return Module(path, parent=Directory(path.parent))
