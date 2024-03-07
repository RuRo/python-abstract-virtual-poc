import warnings

with warnings.catch_warnings():
    warnings.simplefilter("error")

    from new_abc import Abstract, abstractmethod

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

    # === Can't initialize abstract class ===

    try:
        Abst()
    except TypeError as ex:
        assert str(ex).startswith("Can't instantiate abstract class Abst")
    else:
        assert False

    # === Can initialize if all abstract methods are implemented ===

    impl = Impl()
    impl.check()
    assert impl.reached

    assert isinstance(impl, Abst)
    assert isinstance(impl, Abstract)
