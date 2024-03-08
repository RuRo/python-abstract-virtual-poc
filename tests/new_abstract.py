import warnings

with warnings.catch_warnings():
    warnings.simplefilter("error")

    from new_abc import Abstract, abstractmethod

    def assert_cant_instantiate(cls, name):
        try:
            cls()
        except TypeError as ex:
            assert str(ex).startswith(f"Can't instantiate abstract class {name}")
        else:
            assert False

    # === Abstract interface classes ===

    class Abst(Abstract):
        @abstractmethod
        def check(self): assert False

    assert type(Abst) == type
    assert Abst.__mro__ == (Abst, Abstract, object)
    assert issubclass(Abst, Abstract)

    assert hasattr(Abst, "__slots__")
    assert not hasattr(Abst, "register")

    # === Classes implementing Abstract interfaces ===

    class Impl(Abst):
        def check(self): self.reached = True

    assert type(Impl) == type
    assert Impl.__mro__ == (Impl, Abst, Abstract, object)
    assert issubclass(Impl, Abstract)

    assert issubclass(Impl, Abst)
    assert hasattr(Impl, "__slots__")
    assert not hasattr(Impl, "register")

    # === Can only initialize if all abstract methods are implemented ===

    assert_cant_instantiate(Abst, "Abst")

    impl = Impl()
    impl.check()
    assert impl.reached

    assert isinstance(impl, Abst)
    assert isinstance(impl, Abstract)

    # === Adding more abstract methods after the fact works ===

    class ExtraAbst(Abst):
        @abstractmethod
        def one_more(self): assert False

    assert_cant_instantiate(ExtraAbst, "ExtraAbst")

    # === Implementing just some of the abstract methods is not sufficient ===

    class IncompleteImpl1(ExtraAbst):
        def check(self): self.reached1 = True

    class IncompleteImpl2(ExtraAbst):
        def one_more(self): self.reached2 = True

    assert_cant_instantiate(IncompleteImpl1, "IncompleteImpl1")
    assert_cant_instantiate(IncompleteImpl2, "IncompleteImpl2")

    # === Implementing all abstract methods is sufficient, also multiple inheritance works ===

    class CompleteImpl(IncompleteImpl1, IncompleteImpl2):
        pass

    complete = CompleteImpl()
    complete.check()
    assert complete.reached1
    complete.one_more()
    assert complete.reached2
