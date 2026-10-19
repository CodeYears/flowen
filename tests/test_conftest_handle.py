from pathlib import Path

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
