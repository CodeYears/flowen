from collections.abc import Callable
from contextlib import contextmanager


class Skipped(Exception):
    pass


@contextmanager
def raises(expected_exception, func: Callable | None = None, *args, **kwargs):
    try:
        if func is not None:
            func(*args, **kwargs)
        else:
            yield
    except expected_exception:
        pass


def exit(info: str):
    raise KeyboardInterrupt(info)


def importorskip():
    pass
