import warnings
import os

with warnings.catch_warnings(record=True) as current_warnings:
    new = not os.environ.get("USE_OLD_ABC", False)
    if new:
        from new_abc import ABC, ABCMeta, Abstract, Virtual, VirtualMeta, abstractmethod

        warning2 = current_warnings.pop()
        warning1 = current_warnings.pop()
        assert issubclass(warning1.category, DeprecationWarning)
        assert issubclass(warning2.category, DeprecationWarning)
        assert "ABC is deprecated" in str(warning1.message)
        assert "ABCMeta is deprecated" in str(warning2.message)
    else:
        from abc import ABC, ABCMeta, abstractmethod
        Virtual = None
        VirtualMeta = None

    assert not current_warnings


with warnings.catch_warnings():
    warnings.simplefilter("error")

    # === Old classes inheriting from ABC ===

    class OldAbst(ABC):
        @abstractmethod
        def check(self): assert False

    assert type(OldAbst) == ABCMeta
    if new:
        assert OldAbst.__mro__ == (OldAbst, ABC, Abstract, Virtual, object)
        assert ABCMeta.__mro__ == (ABCMeta, VirtualMeta, type, object)
    else:
        assert OldAbst.__mro__ == (OldAbst, ABC, object)
        assert ABCMeta.__mro__ == (ABCMeta, type, object)

    assert isinstance(OldAbst, ABCMeta)
    assert issubclass(OldAbst, ABC)

    if new:
        assert isinstance(OldAbst, VirtualMeta)
        assert issubclass(OldAbst, Abstract)
        assert issubclass(OldAbst, Virtual)

    assert hasattr(OldAbst, "__slots__")

    # === Old classes inheriting from ABC interfaces ===

    class OldImpl(OldAbst):
        def check(self): self.reached = True

    assert type(OldImpl) == ABCMeta
    if new:
        assert OldImpl.__mro__ == (OldImpl, OldAbst, ABC, Abstract, Virtual, object)
    else:
        assert OldImpl.__mro__ == (OldImpl, OldAbst, ABC, object)

    assert isinstance(OldImpl, ABCMeta)
    assert issubclass(OldImpl, ABC)

    if new:
        assert isinstance(OldImpl, VirtualMeta)
        assert issubclass(OldImpl, Abstract)
        assert issubclass(OldImpl, Virtual)

    assert issubclass(OldImpl, OldAbst)
    assert hasattr(OldImpl, "__slots__")

    # === Old classes registering as ABC subclasses ===

    @OldAbst.register
    class OldVirt:
        def check(self): self.reached = True

    assert type(OldVirt) == type
    assert OldVirt.__mro__ == (OldVirt, object)

    assert not isinstance(OldVirt, ABCMeta)
    assert issubclass(OldVirt, ABC)

    if new:
        assert not isinstance(OldVirt, VirtualMeta)
        assert not issubclass(OldVirt, Abstract)
        assert issubclass(OldVirt, Virtual)

    assert issubclass(OldVirt, OldAbst)

    # === Can't initialize abstract class ===

    try:
        OldAbst()
    except TypeError as ex:
        assert str(ex) == "Can't instantiate abstract class OldAbst with abstract method check"
    else:
        assert False

    # === Can initialize if all abstract methods are implemented ===

    old_impl = OldImpl()
    old_impl.check()
    assert old_impl.reached

    assert isinstance(old_impl, OldAbst)
    assert isinstance(old_impl, ABC)

    # === Virtual abstract classes also work as expected ===

    old_virt = OldVirt()
    old_virt.check()
    assert old_virt.reached

    assert isinstance(old_virt, OldAbst)
    assert isinstance(old_virt, ABC)

    # === Old classes inheriting from ABCMeta ===

    class OldMeta(ABCMeta):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.reached1 = True

    class OldMetaImpl(metaclass=OldMeta):
        def check(self): self.reached2 = True

    old_meta = OldMetaImpl()
    old_meta.check()
    assert old_meta.reached1
    assert old_meta.reached2

    # === Old classes using ABCMeta as a metaclass ===

    class OldABC(metaclass=ABCMeta):
        def check(self): self.reached = True

    old_abc = OldABC()
    old_abc.check()
    assert old_abc.reached
