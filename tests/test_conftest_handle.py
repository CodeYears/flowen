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
