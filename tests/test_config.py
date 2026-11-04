from argparse import _ArgumentGroup
from pathlib import Path
from textwrap import dedent

import pytest

import flowen
from flowen.config import config


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
        # 环境初始化
        (tmp_path / "flowen.py").write_text(src)
        conf = config._reparse([tmp_path])
        args = conf._parser.parse(["-g", "17"])
        assert args.gdest == 17

    def test_parsing_again_fails(self, tmp_path: Path):
        conf = config._reparse([tmp_path])
        with flowen.raises(AssertionError):
            conf.parse([])
