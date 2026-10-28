import argparse

import flowen
from flowen import parseopt


class TestParser:
    def test_init(self, capsys):
        parser = parseopt.Parser(usage="xyz")
        with flowen.raises(SystemExit):
            parser.parse(["-h"])

        out, _ = capsys.readouterr()
        assert out.find("xyz") != -1

    def test_group_add_and_get(self):
        parser = parseopt.Parser()
        group = parser.addgroup("hello", description="desc")
        assert group.title == "hello"
        assert group.description == "desc"

        with flowen.raises(ValueError):
            parser.addgroup("hello")

        group2 = parser.getgroup("hello")
        assert group2 is group

    def test_getgroup_addsgroup(self):
        parser = parseopt.Parser()
        group = parser.getgroup("hello", description="desc")

        assert group.title == "hello"
        assert group.description == "desc"

        group2 = parser.getgroup("hello")
        assert group2 is group

    def test_group_addoption(self):
        parse = argparse.ArgumentParser()
        group = parse.add_argument_group("hello")
        group.add_argument("--option1", action="store_true")
        assert len(group._group_actions) == 1
        assert isinstance(group._group_actions[0], argparse.Action)

    def test_group_shortopt_lowercase(self):
        parser = parseopt.Parser()
        group = parser.addgroup("hello")
        assert len(group._group_actions) == 0
        group.add_argument("-x", action="store_true")
        assert len(group._group_actions) == 1

    def test_parser_addoption(self):
        parser = parseopt.Parser()
        group = parser.getgroup("custom options")
        assert len(group._group_actions) == 0
        group.add_argument("--option1", action="store_true")
        assert len(group._group_actions) == 1

    def test_parse(self):
        parser = parseopt.Parser()
        parser.add_argument("--hello", dest="hello", action="store")
        args = parser.parse(["--hello", "world"])
        assert args.hello == "world"

    def test_parse_will_set_default(self):
        parser = parseopt.Parser()
        parser.add_argument("--hello", dest="hello", default="x", action="store")
        args = parser.parse([])
        assert args.hello == "x"

        del args.hello
        assert not hasattr(args, "hello")

    def test_parse_setoption(self):
        parser = parseopt.Parser()
        parser.add_argument("--hello", dest="hello", action="store")
        parser.add_argument("--world", dest="world", default=42)

        class A:
            pass

        option = A()
        args = parser.parse(["--hello", "world"], option)
        assert option.hello == "world"
        assert option.world == 42
        assert args is option

    def test_parse_defaultgetter(self):
        def defaultget(option):
            option.__dict__["hello"] = "world"
            option.__dict__["this"] = 42

        parser = parseopt.Parser(processopt=defaultget)
        parser.add_argument("--this", dest="this", type=int, action="store")
        parser.add_argument("--hello", dest="hello", type=str, action="store")
        parser.add_argument("--no", dest="no", action="store_true")
        args = parser.parse([])
        assert args.hello == "world"
        assert args.this == 42
