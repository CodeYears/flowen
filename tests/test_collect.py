from pathlib import Path
from textwrap import dedent

import pytest

from flowen.collect import Class, Collector, Function, Item, Module
from flowen.config import config


class TestCollector:
    def test_collect_versus_item(self):
        """测试收集器是不同的对象"""

        assert not issubclass(Collector, Item)
        assert not issubclass(Item, Collector)

    def test_check_equality(self, tmp_path):
        """从相同名字解析出来的结点对象应该是同一个对象"""

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
        """测试能否正常获取到父亲节点"""

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
        """
        测试一个节点的唯一 id 能否获取正确
        测试能否从配置对象和 id 能否加载出结点对象
        """

        a = tmp_path / "a"
        a.mkdir()

        x = a / "test_trail.py"
        x.touch()

        conf = config._reparse([x])
        col = conf.getfsnode(x)

        trail = col._totrail()
        assert trail[0] == str(a.relative_to(conf.topdir))
        assert trail[1] == ("test_trail.py",)

        col2 = Collector._fromtrail(trail, conf)
        assert col2.listnames() == col.listnames()

    def test_totrail_topdir_and_beyond(self, tmp_path: Path):
        conf = config._reparse([tmp_path])
        col = conf.getfsnode(conf.topdir)

        trail = col._totrail()
        assert len(trail) == 2
        assert trail[0] == "."
        assert trail[1] == ()

        col2 = Collector._fromtrail(trail, conf)
        assert col2.fspath == conf.topdir
        assert len(col2.listchain()) == 1

        col3 = conf.getfsnode(conf.topdir.parent)
        with pytest.raises(ValueError):
            col3._totrail()

    def test_listnames_and__getitembynames(self, tmp_path: Path):
        file_path = tmp_path / "test_demo.py"
        file_path.write_text("pass")

        conf = config._reparse([file_path])
        modcol = conf.getfsnode(file_path)
        names = modcol.listnames()
        dircol = conf.getfsnode(conf.topdir)

        x = dircol._getitembynames(names)
        assert modcol.name == x.name

    @pytest.mark.skip
    def test_listnames_getitembynames_custom(self):
        """该测试用例等自定义结点机制 / conftest 机制完善后再实现"""


class TestCollectFS:
    def test_ignored_certain_directories(self, tmp_path: Path):
        ignored = ["_darcs", "CVS", "{arch}", ".whatever", ".bzr"]

        for name in ignored:
            (tmp_path / name / "test_notfound.py").parent.mkdir(parents=True)

        (tmp_path / "normal" / "test_found.py").parent.mkdir()
        (tmp_path / "test_found.py").touch()

        conf = config._reparse([tmp_path])
        dircol = conf.getfsnode(tmp_path)

        items = dircol.collect()
        names = [item.name for item in items]

        assert len(items) == 2
        assert "normal" in names
        assert "test_found.py" in names

    def test_found_certain_testfiles(self, tmp_path: Path):
        (tmp_path / "test_found.py").write_text("pass")
        (tmp_path / "found_test.py").write_text("pass")

        conf = config._reparse([tmp_path])
        dircol = conf.getfsnode(tmp_path)
        items = dircol.collect()

        assert len(items) == 2
        assert items[0].name == "found_test.py"
        assert items[1].name == "test_found.py"

    def test_directory_file_sorting(self, tmp_path: Path):
        (tmp_path / "test_one.py").write_text("hello")
        (tmp_path / "x").mkdir()
        (tmp_path / "dir1").mkdir()
        (tmp_path / "test_two.py").write_text("hello")
        (tmp_path / "dir2").mkdir()

        conf = config._reparse([tmp_path])
        col = conf.getfsnode(tmp_path)
        names = [item.name for item in col.collect()]

        assert names == ["dir1", "dir2", "test_one.py", "test_two.py", "x"]


class TestCollectPluginHooks:
    @pytest.mark.skip
    def test_pytest_collect_file(self):
        """该测试用例等插件机制完善后再实现"""

    @pytest.mark.skip
    def test_pytest_collect_directory(self):
        """该测试用例等插件机制完善后再实现"""


class TestCustomConftests:
    @pytest.mark.skip
    def test_non_python_files(self):
        """该测试用例等 conftest 机制完善后再实现"""

    @pytest.mark.skip
    def test_collectignore_exclude_on_option(self):
        """该测试用例等 conftest 机制完善后再实现"""
