import types

from flowen.collect import Class, Collector, Function, Item, Module


class TestCollector:
    def test_collect_versus_item(self):

        assert not issubclass(Collector, Item)
        assert not issubclass(Item, Collector)

    def test_check_equality(self):
        """测试节点对象是值对象"""
        module = types.ModuleType("test_module")

        def test_pass():
            pass

        def test_fail():
            assert 0

        module.test_pass = test_pass
        module.test_fail = test_fail

        modcol = Collector(module)

        fn1 = modcol.collect_by_name("test_pass")
        assert isinstance(fn1, Function)

        fn2 = modcol.collect_by_name("test_pass")
        assert isinstance(fn2, Function)

        assert fn1 == fn2
        assert fn1 != modcol
        assert hash(fn1) == hash(fn2)

        fn3 = modcol.collect_by_name("test_fail")
        assert isinstance(fn3, Function)
        assert fn1 != fn3

        for fn in fn1, fn2, fn3:
            assert fn != 3
            assert fn != modcol
            assert fn != [1, 2, 3]
            assert [1, 2, 3] != fn
            assert modcol != fn

    def test_getparent(self):
        module = types.ModuleType("test_module")

        class TestClass:
            def test_foo():
                pass

        module.TestClass = TestClass
        modcol = Collector(module)

        cls = modcol.collect_by_name("TestClass")
        fn = cls.collect_by_name("test_foo")

        parent = fn.getparent(Module)
        assert parent is modcol

        parent = fn.getparent(Class)
        assert parent is cls
