import pytest

from flowen.config import config


class TestConfigCmdlineParsing:
    @pytest.mark.skip
    def test_config_cmdline_options(self, testdir):
        """等 conftest 机制完善再实现"""

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
