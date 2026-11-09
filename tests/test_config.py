from argparse import _ArgumentGroup
from pathlib import Path
from textwrap import dedent

import pytest

import flowen
from flowen.config import config
from flowen.outcome import Skipped


class TestConfigCmdlineParsing:
    def test_config_options(self):
        conf = config._reparse([])

        def configure(group: _ArgumentGroup):
            group.add_argument(
                "-G",
                "--glong",
                action="store",
                default=42,
                type=int,
                dest="gdest",
                help="g value.",
            )

        conf.addoptions("testing group", configure)
        assert conf.option.gdest == 42

    def test_config_cmdline_options(self, tmp_path: Path):
        src = dedent("""\
            from argparse import _ArgumentGroup
            from flowen.config import config

            def configure(group: _ArgumentGroup):
                group.add_argument(
                    "-G",
                    "--glong",
                    action="store",
                    default=42,
                    type=int,
                    dest="gdest",
                    help="g value.",
                )

                group.add_argument(
                    "-T",
                    "--tlong",
                    help="t value",
                )
            group = config.addoptions("testing group", configure)
        """)

        (tmp_path / "flowen.py").write_text(src)
        conf = config._reparse([tmp_path])
        args = conf._parser.parse(["-G", "17"])
        assert args.gdest == 17

    def test_parser_addoption_default_env(self, monkeypatch):
        import os

        group = config._parser.addgroup("hello")

        monkeypatch.setitem(os.environ, "PYTEST_OPTION_OPTION1", "True")
        group.add_argument("--option1", action="store_true")
        assert config._parser.parse([]).option1 is True

        monkeypatch.setitem(os.environ, "PYTEST_OPTION_OPTION2", "abc")
        group.add_argument("--option2", action="store", default="x")
        assert config._parser.parse([]).option2 == "abc"

        monkeypatch.setitem(os.environ, "PYTEST_OPTION_OPTION3", "32")
        group.add_argument("--option3", action="store", type=int)
        assert config._parser.parse([]).option3 == 32

        group.add_argument("--option4", action="store", type=int)
        assert config._parser.parse([]).option4 is None

    @pytest.mark.skip
    def test_parser_addoption_default_conftest(self, tmp_path: Path):
        """verbose 是 pytest_terminal.py 插件插入的参数，目前插件机制尚未实现"""

        (tmp_path / "conftest.py").write_text("pytest_option_verbose=True")
        conf = config._reparse([tmp_path])
        assert conf.conftest.rget("pytest_option_verbose")

    def test_config_cmdline_options_only_lowercase(self, tmp_path: Path):
        src = dedent("""\
            import argparse
            from flowen.config import config

            def add_configure(group: argparse._ArgumentGroup):
                group.add_argument(
                    "-g",
                    "--glong",
                    action="store",
                    default=42,
                    type=int,
                    dest="gdest",
                    help="g value.",
                )
            config.addoptions("testing group", add_configure)
        """)
        (tmp_path / "flowen.py").write_text(src)
        conf = config._reparse([tmp_path])
        args = conf._parser.parse(["-g", "17"])
        assert args.gdest == 17

    def test_parsing_again_fails(self, tmp_path: Path):
        conf = config._reparse([tmp_path])
        with flowen.raises(AssertionError):
            conf.parse([])


class TestConfigTmpdir:
    def test_getbasetemp(self):
        conf = config._reparse([])
        conf.basetemp = Path("hello")

        assert conf.getbasetemp() == Path("hello")

    def test_mktemp(self, tmp_path):
        conf = config._reparse([])
        conf.basetemp = tmp_path / "hello"
        conf.basetemp.mkdir()

        tmp = conf.mktemp("world")
        assert tmp.relative_to(conf.basetemp) == Path("world")

        tmp = conf.mktemp("this", numbered=True)
        assert tmp.relative_to(conf.basetemp).name.startswith("this")

        tmp2 = conf.mktemp("this", numbered=True)
        assert tmp2.relative_to(conf.basetemp).name.startswith("this")

        assert tmp2 != tmp

    def test_reparse(self, tmp_path):
        conf = config._reparse([])
        conf.basetemp = tmp_path / "my"
        conf.basetemp.mkdir()

        conf2 = conf._reparse([])
        assert conf2.basetemp.is_relative_to(conf.basetemp)

        conf3 = conf._reparse([])
        assert conf3.basetemp.is_relative_to(conf.basetemp)

        assert conf2.basetemp != conf3.basetemp


class TestConfigAPI:
    def test_config_getvalue_honours_flowen(self, tmp_path: Path):
        flowen_file = tmp_path / "flowen.py"
        flowen_file.write_text("x = 1")

        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "flowen.py").write_text("x = 2\ny = 3")

        conf = config._reparse([tmp_path])

        assert conf.getvalue("x") == 1
        assert conf.getvalue("x", sub) == 2

        with pytest.raises(KeyError):
            conf.getvalue("y")

        conf = config._reparse([sub])

        assert conf.getvalue("x") == 2
        assert conf.getvalue("y") == 3
        assert conf.getvalue("x", tmp_path) == 1

        with pytest.raises(KeyError):
            conf.getvalue("y", tmp_path)

    def test_config_getvalueorskip(self):
        with pytest.raises(Skipped):
            config.getvalueorskip("hello")

        # 这里的 verbose 参数是由插件注册进去的，插件机制暂未实现
        # verbose = config.getvalueorskip("verbose")
        # assert verbose == config.option.verbose

        with pytest.raises(Skipped):
            config.getvalueorskip("hello")

    def test_config_overwrite(self, tmp_path: Path):
        conftest = tmp_path / "flowen.py"
        conftest.write_text("x = 1")

        conf = config._reparse([tmp_path])

        assert conf.getvalue("x") == 1

        conf.option.x = 2
        assert conf.getvalue("x") == 2

        conf2 = conf._reparse([tmp_path])
        assert conf2.getvalue("x") == 1

    def test_getconftest_pathlist(self, tmp_path: Path):
        somepath = tmp_path / "x" / "y" / "z"

        src = dedent(f"""\
            from pathlib import Path
            
            pathlist = ['Path(.)', {str(somepath)!r}]"
        """)
        (tmp_path / "flowen.py").write_text(src)

        conftest = tmp_path / "flowen.py"
        conftest.write_text(src)

        conf = config._reparse([conftest])
        assert conf.getconftest_pathlist("notexist") is None

        paths = conf.getconftest_pathlist("pathlist")
        print(paths)
        # assert paths == [tmp_path, somepath]
