import os
from argparse import ArgumentParser, _ArgumentGroup, _StoreTrueAction, _StoreFalseAction


class ArgParser:
    def __init__(self):
        self.parser = ArgumentParser()
        self.groups = []

    def addgroup(self, *args, **kwargs):
        group_row = self.parser.add_argument_group(*args, **kwargs)
        group = OptGroup(group_row)
        self.groups.append(group)
        return group


class OptGroup:
    def __init__(self, group: _ArgumentGroup):
        self.group = group
        self.options = []

    def processopt(self, opt):
        val = os.getenv("PYTEST_OPTION_" + opt.dest.upper())
        if val is None:
            if opt.default is None:
                opt.default = ("NO", "DEFAULT")
            return

        if opt.type:
            val = opt.type(val)
        elif not opt.type and isinstance(opt, (_StoreTrueAction, _StoreFalseAction)):
            val = eval(val)

        opt.default = val

    def addoption(self, *args, **kwargs):
        opt = self.group.add_argument(*args, **kwargs)
        self.processopt(opt)
        self.options.append(opt)
