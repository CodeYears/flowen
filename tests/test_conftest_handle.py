from pathlib import Path

import flowen
from flowen.conftest_handle import Conftest


def parpare_conftest_env(tmp_path: Path):
    adir = tmp_path / "adir"
    adir.mkdir()
    (adir / "conftest.py").write_text("a = 1\nDirectory = 3")

    (adir / "b").mkdir()
    (adir / "b" / "conftest.py").write_text("b=2\na=1.5")
    return tmp_path


class TestConftestValueAccessGlobal:
    def test_basic_init(self, tmp_path: Path):
        adir = parpare_conftest_env(tmp_path) / "adir"
        conftest = Conftest()
        conftest.setinitial([adir])

        assert conftest.rget("a") == 1

    def test_onimport(self, tmp_path: Path):
        l = []
        adir = parpare_conftest_env(tmp_path) / "adir"
        conftest = Conftest(onimport=l.append)
        conftest.setinitial([adir])
        assert len(l) == 2
        assert conftest.rget("a") == 1
        assert conftest.rget("b", adir / "b") == 2
        assert len(l) == 3

    def test_immediate_initialiation_and_incremental_are_the_same(self, tmp_path: Path):
        conftest = Conftest()
        tmp_path = parpare_conftest_env(tmp_path)
        conftest.create_path_conftest_map(tmp_path)
        snap1 = len(conftest.path_conftest_map)

        conftest.create_path_conftest_map(tmp_path / "adir")
        assert len(conftest.path_conftest_map) == snap1 + 1

        conftest.create_path_conftest_map(tmp_path / "b")
        assert len(conftest.path_conftest_map) == snap1 + 2

    def test_default_Module_setting_is_visible_always(self, tmp_path: Path):
        from flowen import Module

        tmp_path = parpare_conftest_env(tmp_path)
        for path in tmp_path.parents:
            conftest = Conftest(path)
            assert conftest.rget("Module") == Module

    def test_default_has_lower_prio(self, tmp_path: Path):
        tmp_path = parpare_conftest_env(tmp_path)
        conftest = Conftest(tmp_path / "adir")
        assert conftest.rget("Directory") == 3

    def test_value_access_not_existing(self, tmp_path: Path):
        tmp_path = parpare_conftest_env(tmp_path)
        conftest = Conftest(tmp_path)
        with flowen.raises(KeyError):
            conftest.rget("a")

    def test_value_access_by_path(self, tmp_path: Path):
        tmp_path = parpare_conftest_env(tmp_path)
        conftest = Conftest(tmp_path)
        assert conftest.rget("a", tmp_path / "adir") == 1
        assert conftest.rget("a", tmp_path / "adir" / "b") == 1.5

    def test_value_access_with_init_one_conftest(self, tmp_path: Path):
        tmp_path = parpare_conftest_env(tmp_path)
        conftest = Conftest(tmp_path / "adir")
        assert conftest.rget("a") == 1

    def test_value_access_with_init_two_conftests(self, tmp_path: Path):
        tmp_path = parpare_conftest_env(tmp_path)
        conftest = Conftest(tmp_path / "adir" / "b")
        assert conftest.rget("a") == 1.5

    def test_value_access_with_confmod(self, tmp_path: Path):
        tmp_path = parpare_conftest_env(tmp_path)

        topdir = tmp_path / "adir" / "b"
        (topdir / "xx").mkdir(parents=True)

        conftest = Conftest(topdir)
        mod, value = conftest.rget_with_confmod("a", topdir)
        assert value == 1.5
        path = Path(mod.__file__)
        assert path.parent == topdir
        assert path.stem == "conftest"
