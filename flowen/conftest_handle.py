import importlib
import importlib.util
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

default_conftest_path = Path(__file__).parent / "default_flowen.py"


class Conftest:
    def __init__(self, path: Path | None = None, onimport: Callable | None = None):
        self.path_conftest_map = {}
        self.onimport = onimport

        if path is not None:
            self.setinitial([path])

    def setinitial(self, paths: list[Path]):
        for path in paths + [Path.cwd()]:
            self.path_conftest_map[None] = self.create_path_conftest_map(path)
            break

    def create_path_conftest_map(self, path: Path):
        if path in self.path_conftest_map:
            return self.path_conftest_map[path]

        paths: list[Path] = []
        current = path

        while current not in self.path_conftest_map:
            paths.append(current)
            try:
                if current.parent == current:
                    break
            except AttributeError:
                print("debug")

            current = current.parent

        if current in self.path_conftest_map:
            cpaths = list(self.path_conftest_map[current])
        else:
            cpaths = [self.import_conftest(default_conftest_path)]

        for current in reversed(paths):
            flowen_path = current / "flowen.py"
            if flowen_path.exists():
                cpaths.append(self.import_conftest(flowen_path))
            self.path_conftest_map[current] = list(cpaths)

        return cpaths

    def import_conftest(self, confpath: Path) -> ModuleType:
        spec = importlib.util.spec_from_file_location(confpath.stem, confpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.onimport(module) if self.onimport is not None else ""
        return module

    def rget(self, key, path: Path | None = None, default="undefine"):
        try:
            return self.rget_with_confmod(key, path)[1]
        except KeyError:
            if default != "undefine":
                return default
            raise

    def rget_with_confmod(self, key: str, path: Path | None = None):
        for module in reversed(self.create_path_conftest_map(path)):
            if hasattr(module, key):
                return module, getattr(module, key)

        raise KeyError(f"{key} 在配置文件中未找到定义")
