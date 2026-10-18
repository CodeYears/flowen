import importlib
import importlib.util
from pathlib import Path
from types import ModuleType


class Conftest:
    def __init__(self):
        self.path_conftest_map = {}
        self.conf_modules = []

    def setinitial(self, paths: list[Path]):
        path = paths[0]

        for cur in [path] + list(path.parents):
            conf_path = cur / "conftest.py"

            if not conf_path.exists():
                continue

            conf_module = self.import_conftest(conf_path)
            self.conf_modules.insert(0, conf_module)

            self.path_conftest_map[cur] = list(self.conf_modules)

    def import_conftest(self, confpath: Path) -> ModuleType:
        spec = importlib.util.spec_from_file_location(confpath.stem, confpath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def rget(self, key: str):
        for module in self.conf_modules:
            if hasattr(module, key):
                return getattr(module, key)

        raise KeyError(key)
