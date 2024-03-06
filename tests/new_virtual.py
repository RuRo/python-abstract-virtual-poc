import warnings

with warnings.catch_warnings():
    warnings.simplefilter("error")

    from new_abc import Virtual, VirtualMeta

    # === Class hierarchies inheriting from Virtual ===

    class Parent(Virtual): pass
    class Child(Parent): pass

    class Unrelated(Virtual): pass

    assert type(Parent) == VirtualMeta
    assert type(Child) == VirtualMeta
    assert type(Unrelated) == VirtualMeta

    assert Parent.__mro__ == (Parent, Virtual, object)
    assert Child.__mro__ == (Child, Parent, Virtual, object)
    assert Unrelated.__mro__ == (Unrelated, Virtual, object)
    assert VirtualMeta.__mro__ == (VirtualMeta, type, object)

    assert isinstance(Parent, VirtualMeta)
    assert isinstance(Child, VirtualMeta)
    assert isinstance(Unrelated, VirtualMeta)

    assert hasattr(Parent, "__slots__")
    assert hasattr(Child, "__slots__")
    assert hasattr(Unrelated, "__slots__")

    # === Virtually inheriting from virtual classes ===

    @Parent.register
    class VirtualParent: pass

    @Child.register
    class VirtualChild: pass

    @Unrelated.register
    class VirtualUnrelated: pass

    assert type(VirtualParent) == type
    assert type(VirtualChild) == type
    assert type(VirtualUnrelated) == type

    assert VirtualParent.__mro__ == (VirtualParent, object)
    assert VirtualChild.__mro__ == (VirtualChild, object)
    assert VirtualUnrelated.__mro__ == (VirtualUnrelated, object)

    assert not isinstance(VirtualParent, VirtualMeta)
    assert not isinstance(VirtualChild, VirtualMeta)
    assert not isinstance(VirtualUnrelated, VirtualMeta)

    # VirtualUnrelated --> Unrelated --> Virtual
    #                                       ^
    #    VirtualChild --> Child ==> Parent -'
    #                                 ^
    #                  VirtualParent -'

    classes = [
        Virtual,
        Parent, Child, Unrelated,
        VirtualParent, VirtualChild, VirtualUnrelated,
    ]

    positives = {
        (VirtualChild, Child),
        (Child, Parent),
        (VirtualChild, Parent),
        (VirtualParent, Parent),
        (VirtualUnrelated, Unrelated),
    }

    for first in classes:
        for second in classes:
            if (
                first is second or
                second is Virtual or
                (first, second) in positives
            ):
                assert issubclass(first, second), (first, second)
            else:
                assert not issubclass(first, second), (first, second)

    # === Instances of virtual classes ===

    virtual = Virtual()

    parent = Parent()
    child = Child()
    unrelated = Unrelated()

    virtual_parent = VirtualParent()
    virtual_child = VirtualChild()
    virtual_unrelated = VirtualUnrelated()

    assert type(virtual) == Virtual

    assert type(parent) == Parent
    assert type(child) == Child
    assert type(unrelated) == Unrelated

    assert type(virtual_parent) == VirtualParent
    assert type(virtual_child) == VirtualChild
    assert type(virtual_unrelated) == VirtualUnrelated

    instances = [
        virtual,
        parent, child, unrelated,
        virtual_parent, virtual_child, virtual_unrelated,
    ]
    for first in instances:
        for second in classes:
            first_type = type(first)
            if (
                first_type is second or
                second is Virtual or
                (first_type, second) in positives
            ):
                assert isinstance(first, second), (first, second)
            else:
                assert not isinstance(first, second), (first, second)

    # === Classes inheriting from VirtualMeta ===

    class NewVirtualMeta(VirtualMeta):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.reached1 = True

    class NewVirtual1(metaclass=NewVirtualMeta):
        def check(self): self.reached2 = True

    new_virt1 = NewVirtual1()
    new_virt1.check()
    assert new_virt1.reached1
    assert new_virt1.reached2

    # === Classes using VirtualMeta as a metaclass ===

    class NewVirtual2(metaclass=VirtualMeta):
        def check(self): self.reached = True

    new_virt2 = NewVirtual2()
    new_virt2.check()
    assert new_virt2.reached
