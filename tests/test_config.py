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

        (tmp_path / "conftest.py").write_text(src)
        config._reparse([tmp_path])
        args = config._parser.parse(["-G", "17"])
        assert args.gdest == 17

    @pytest.mark.skip
    def test_parser_addoption_default_env(self, monkeypatch):
        import os

        group = config._parser.addgroup("hello")

        monkeypatch.setitem(os.environ, "PYTEST_OPTION_OPTION1", "True")
        group.addoption("--option1", action="store_true")
        assert group.options[0].default == True

        monkeypatch.setitem(os.environ, "PYTEST_OPTION_OPTION2", "abc")
        group.addoption("--option2", action="store", default="x")
        assert group.options[1].default == "abc"

        monkeypatch.setitem(os.environ, "PYTEST_OPTION_OPTION3", "32")
        group.addoption("--option3", action="store", type=int)
        assert group.options[2].default == 32

        group.addoption("--option4", action="store", type=int)
        assert group.options[3].default == ("NO", "DEFAULT")

    @pytest.mark.skip
    def test_parser_addoption_default_conftest(self):
        """等 conftest 机制完善再实现"""

    @pytest.mark.skip
    def test_config_cmdline_options_only_lowercase(self):
        """等 conftest 机制完善再实现"""

    def test_parsing_again_fails(self, tmp_path: Path):
        conf = config._reparse([tmp_path])
        with flowen.raises(AssertionError):
            conf.parse([])
