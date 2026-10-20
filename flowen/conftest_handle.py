import importlib
import importlib.util
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

default_conftest_path = Path(__file__).parent / "default_conftest.py"


class Conftest:
    def __init__(self, path: Path | None = None, onimport: Callable | None = None):
        self.path_conftest_map = {}
        self.conf_modules = []
        self.onimport = onimport

        if path is not None:
            self.setinitial([path])

    def setinitial(self, paths: list[Path]):
        path = paths[0]

        self.conf_modules.append(self.import_conftest(default_conftest_path))
        self.create_path_conftest_map(path)

    def create_path_conftest_map(self, path: Path):
        for cur in [path] + list(path.parents):
            conf_path = cur / "conftest.py"

            if not conf_path.exists():
                self.path_conftest_map[cur] = list(self.conf_modules)
                continue

            if cur in self.path_conftest_map:
                continue

            conf_module = self.import_conftest(conf_path)
            self.conf_modules.append(conf_module)

            self.path_conftest_map[cur] = list(self.conf_modules)

    def import_conftest(self, confpath: Path) -> ModuleType:
        spec = importlib.util.spec_from_file_location(confpath.stem, confpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.onimport(module) if self.onimport is not None else ""
        return module

    def rget(self, key, path: Path | None = None):
        return self.rget_with_confmod(key, path)[1]

    def rget_with_confmod(self, key: str, path: Path | None = None):
        if path is None:
            for module in self.conf_modules:
                if hasattr(module, key):
                    return module, getattr(module, key)
        else:
            self.create_path_conftest_map(path)
            for module in reversed(self.path_conftest_map[path]):
                if hasattr(module, key):
                    return module, getattr(module, key)

        raise KeyError(key)
