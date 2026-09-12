import importlib.util
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载模块: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
