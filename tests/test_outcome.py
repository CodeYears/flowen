import pytest

import flowen


class TestRaises:
    def test_raises(self):
        flowen.raises(ValueError, lambda: int("qwe"))

    def test_raises_exec(self):
        flowen.raises(ValueError, lambda: exec("a, x = []"))  # noqa

    def test_raises_syntax_error(self):
        flowen.raises(SyntaxError, lambda: exec("qwe qwe qwe"))  # noqa

    def test_raises_function(self):
        flowen.raises(ValueError, int, "hello")


@pytest.mark.skip
def test_importorskip():
    """这个机制不知道干什么用的，后面实现"""


def test_pytest_exit():
    with flowen.raises(KeyboardInterrupt):
        flowen.exit("hello")
