from pathlib import Path

from flowen.conftest_handle import Conftest


class TestConftestValueAccessGlobal:
    def test_basic_init(self, tmp_path: Path):
        adir = tmp_path / "adir"
        adir.mkdir()
        (adir / "conftest.py").write_text("a = 1\nDirectory = 3")

        conftest = Conftest()
        conftest.setinitial([adir])

        assert conftest.rget("a") == 1
