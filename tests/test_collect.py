from pathlib import Path
from textwrap import dedent

from flowen.collect import Class, Collector, Function, Item, Module
from flowen.config import config


class TestCollector:
    def test_collect_versus_item(self):

        assert not issubclass(Collector, Item)
        assert not issubclass(Item, Collector)

    def test_check_equality(self, tmp_path):

        src = dedent("""\
            def test_pass():
                pass

            def test_fail():
                assert 0
        """)

        file_path = tmp_path / "test_demo.py"
        file_path.write_text(src)

        modcol = config.getfsnode(file_path)

        fn1 = modcol.collect_by_name("test_pass")
        assert isinstance(fn1, Function)

        fn2 = modcol.collect_by_name("test_pass")
        assert isinstance(fn2, Function)

        assert fn1 == fn2
        assert fn1 != modcol
        assert hash(fn1) == hash(fn2)

        fn3 = modcol.collect_by_name("test_fail")
        assert isinstance(fn3, Function)
        assert fn1 != fn3

        for fn in fn1, fn2, fn3:
            assert fn != 3
            assert fn != modcol
            assert fn != [1, 2, 3]
            assert [1, 2, 3] != fn
            assert modcol != fn

    def test_getparent(self, tmp_path: Path):
        src = dedent("""\
            class TestClass:
                def test_foo():
                    pass
        """)

        file_path = tmp_path / "test_demo.py"
        file_path.write_text(src)

        modcol = config.getfsnode(file_path)

        cls = modcol.collect_by_name("TestClass")
        fn = cls.collect_by_name("test_foo")

        parent = fn.getparent(Module)
        assert parent is modcol

        parent = fn.getparent(Class)
        assert parent is cls

    def test_to_trail_and_back(self, tmp_path: Path):
        a = tmp_path / "a"
        a.mkdir()

        x = a / "test_trail.py"
        x.touch()

        conf = config._reparse([x])
        col = conf.getfsnode(x)

        trail = col._totrail()
        assert trail[0] == a.relative_to(conf.topdir)
        assert trail[1] == ("test_trail.py",)

        col2 = Collector._fromtrail(trail, conf)
        assert col2.listnames() == col.listnames()
