from optparse import Option
from pathlib import Path
from textwrap import dedent

import pytest

import flowen
from flowen.config import Config, config


class TestConfigCmdlineParsing:
    @pytest.mark.skip
    def test_config_options(self):
        opt1 = Option(
            "-G", "--glong", default=42, type=int, dest="gdest", help="g value"
        )
        conf = config._reparse()

        conf.addoptions("testing group", opt1)
        assert config.option.gdest == 17

    @pytest.mark.skip
    def test_config_cmdline_options(self, tmp_path: Path):
        src = dedent("""\
            from optparse import Option
            from config import config

            group = config.addoptions(
                "testing group",
                Option(
                    "-G",
                    "--glong",
                    action="store",
                    default=42,
                    type=int,
                    dest="gdest",
                    help="g value.",
                ),
                Option(
                    "-T",
                    "--tlong",
                    action="callback",
                    help="t value.",
                ),
            )
        """)

        (tmp_path / "contest.py").write_text(src)
        print(config._reparse())

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


class TestConfigTmpdir:
    def test_getbasetemp(self, tmp_path):
        conf = Config(tmp_path)
        conf.basetemp = "hello"
        assert conf.getbasetemp() == "hello"

    @pytest.mark.skip
    def test_mktemp(self, tmp_path):
        """我没搞懂这个测试用例的测试意图"""

    @pytest.mark.skip
    def test_reparse(self, testdir):
        """我没搞懂这个测试用例的测试意图"""
