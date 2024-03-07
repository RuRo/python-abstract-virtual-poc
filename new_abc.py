# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Abstract Base Classes (ABCs) according to PEP 3119."""

from _weakrefset import WeakSet


def abstractmethod(funcobj):
    """A decorator indicating abstract methods.

    Requires that the metaclass is ABCMeta or derived from it.  A
    class that has a metaclass derived from ABCMeta cannot be
    instantiated unless all of its abstract methods are overridden.
    The abstract methods can be called using any of the normal
    'super' call mechanisms.  abstractmethod() may be used to declare
    abstract methods for properties and descriptors.

    Usage:

        class C(metaclass=ABCMeta):
            @abstractmethod
            def my_abstract_method(self, arg1, arg2, argN):
                ...
    """
    funcobj.__isabstractmethod__ = True
    return funcobj


class abstractclassmethod(classmethod):
    """A decorator indicating abstract classmethods.

    Deprecated, use 'classmethod' with 'abstractmethod' instead:

        class C(ABC):
            @classmethod
            @abstractmethod
            def my_abstract_classmethod(cls, ...):
                ...

    """

    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super().__init__(callable)


class abstractstaticmethod(staticmethod):
    """A decorator indicating abstract staticmethods.

    Deprecated, use 'staticmethod' with 'abstractmethod' instead:

        class C(ABC):
            @staticmethod
            @abstractmethod
            def my_abstract_staticmethod(...):
                ...

    """

    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super().__init__(callable)


class abstractproperty(property):
    """A decorator indicating abstract properties.

    Deprecated, use 'property' with 'abstractmethod' instead:

        class C(ABC):
            @property
            @abstractmethod
            def my_abstract_property(self):
                ...

    """

    __isabstractmethod__ = True


def update_abstractmethods(cls):
    """Recalculate the set of abstract methods of an abstract class.

    If a class has had one of its abstract methods implemented after the
    class was created, the method will not be considered implemented until
    this function is called. Alternatively, if a new abstract method has been
    added to the class, it will only be considered an abstract method of the
    class after this function is called.

    This function should be called before any use is made of the class,
    usually in class decorators that add methods to the subject class.

    Returns cls, to allow usage as a class decorator.

    If cls is not an instance of ABCMeta, does nothing.
    """
    if not hasattr(cls, '__abstractmethods__'):
        # We check for __abstractmethods__ here because cls might by a C
        # implementation or a python implementation (especially during
        # testing), and we want to handle both cases.
        return cls

    abstracts = set()
    # Check the existing abstract methods of the parents, keep only the ones
    # that are not implemented.
    for scls in cls.__bases__:
        for name in getattr(scls, '__abstractmethods__', ()):
            value = getattr(cls, name, None)
            if getattr(value, "__isabstractmethod__", False):
                abstracts.add(name)
    # Also add any other newly added abstract methods.
    for name, value in cls.__dict__.items():
        if getattr(value, "__isabstractmethod__", False):
            abstracts.add(name)
    cls.__abstractmethods__ = frozenset(abstracts)
    return cls


def get_cache_token():
    """Returns the current ABC cache token.

    The token is an opaque object (supporting equality testing) identifying the
    current version of the ABC cache for virtual subclasses. The token changes
    with every call to ``register()`` on any ABC.
    """
    return VirtualMeta._abc_invalidation_counter


class VirtualMeta(type):
    """Metaclass for virtual inheritance of abstract classes.

    This metaclass implements only those parts of the old ABCMeta
    API that dealt with virtual inheritance.
    """

    # A global counter that is incremented each time a class is
    # registered as a virtual subclass of anything.  It forces the
    # negative cache to be cleared before its next use.
    # Note: this counter is private. Use `abc.get_cache_token()` for
    #       external code.
    _abc_invalidation_counter = 0

    def __new__(mcls, name, bases, namespace, /, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        # NOTE: cls.__abstractmethods__ are **NOT** set here

        # Set up inheritance registry
        cls._abc_registry = WeakSet()
        cls._abc_cache = WeakSet()
        cls._abc_negative_cache = WeakSet()
        cls._abc_negative_cache_version = VirtualMeta._abc_invalidation_counter
        return cls

    def register(cls, subclass):
        """Register a virtual subclass of an ABC.

        Returns the subclass, to allow usage as a class decorator.
        """
        if not isinstance(subclass, type):
            raise TypeError("Can only register classes")
        if issubclass(subclass, cls):
            return subclass  # Already a subclass
        # Subtle: test for cycles *after* testing for "already a subclass";
        # this means we allow X.register(X) and interpret it as a no-op.
        if issubclass(cls, subclass):
            # This would create a cycle, which is bad for the algorithm below
            raise RuntimeError("Refusing to create an inheritance cycle")
        cls._abc_registry.add(subclass)
        VirtualMeta._abc_invalidation_counter += 1  # Invalidate negative cache
        return subclass

    def _dump_registry(cls, file=None):
        """Debug helper to print the ABC registry."""
        print(f"Class: {cls.__module__}.{cls.__qualname__}", file=file)
        print(f"Inv. counter: {get_cache_token()}", file=file)
        for name in cls.__dict__:
            if name.startswith("_abc_"):
                value = getattr(cls, name)
                if isinstance(value, WeakSet):
                    value = set(value)
                print(f"{name}: {value!r}", file=file)

    def _abc_registry_clear(cls):
        """Clear the registry (for debugging or testing)."""
        cls._abc_registry.clear()

    def _abc_caches_clear(cls):
        """Clear the caches (for debugging or testing)."""
        cls._abc_cache.clear()
        cls._abc_negative_cache.clear()

    def __instancecheck__(cls, instance):
        """Override for isinstance(instance, cls)."""
        # Inline the cache checking
        subclass = instance.__class__
        if subclass in cls._abc_cache:
            return True
        subtype = type(instance)
        if subtype is subclass:
            if (cls._abc_negative_cache_version ==
                VirtualMeta._abc_invalidation_counter and
                subclass in cls._abc_negative_cache):
                return False
            # Fall back to the subclass check.
            return cls.__subclasscheck__(subclass)
        return any(cls.__subclasscheck__(c) for c in (subclass, subtype))

    def __subclasscheck__(cls, subclass):
        """Override for issubclass(subclass, cls)."""
        if not isinstance(subclass, type):
            raise TypeError('issubclass() arg 1 must be a class')
        # Check cache
        if subclass in cls._abc_cache:
            return True
        # Check negative cache; may have to invalidate
        if cls._abc_negative_cache_version < VirtualMeta._abc_invalidation_counter:
            # Invalidate the negative cache
            cls._abc_negative_cache = WeakSet()
            cls._abc_negative_cache_version = VirtualMeta._abc_invalidation_counter
        elif subclass in cls._abc_negative_cache:
            return False
        # Check the subclass hook
        ok = cls.__subclasshook__(subclass)
        if ok is not NotImplemented:
            assert isinstance(ok, bool)
            if ok:
                cls._abc_cache.add(subclass)
            else:
                cls._abc_negative_cache.add(subclass)
            return ok
        # Check if it's a direct subclass
        if cls in getattr(subclass, '__mro__', ()):
            cls._abc_cache.add(subclass)
            return True
        # Check if it's a subclass of a registered class (recursive)
        for rcls in cls._abc_registry:
            if issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                return True
        # Check if it's a subclass of a subclass (recursive)
        for scls in cls.__subclasses__():
            if issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                return True
        # No dice; update negative cache
        cls._abc_negative_cache.add(subclass)
        return False


class Abstract:
    """Base class for abstract classes.

    This class implements the core parts of the old ABCMeta API,
    excluding virtual inheritance. Inherit from this class to create
    an Abstract class.
    """
    __slots__ = ()

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        name = cls.__name__
        bases = cls.__bases__
        namespace = cls.__dict__

        # Compute set of abstract method names
        abstracts = {name
                     for name, value in namespace.items()
                     if getattr(value, "__isabstractmethod__", False)}
        for base in bases:
            for name in getattr(base, "__abstractmethods__", set()):
                value = getattr(cls, name, None)
                if getattr(value, "__isabstractmethod__", False):
                    abstracts.add(name)
        cls.__abstractmethods__ = frozenset(abstracts)


class Virtual(metaclass=VirtualMeta):
    """Helper class that provides a standard way to create classes with
    virtual inheritance support.
    """
    __slots__ = ()


# === Legacy/deprecated classes ===


class ABCMeta(VirtualMeta):
    """Legacy metaclass for Abstract Base Classes with virtual inheritance.
    """
    def __new__(mcls, name, bases, namespace, /, **kwargs):
        if Abstract not in bases:
            bases += (Abstract,)
        if Virtual not in bases:
            bases += (Virtual,)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        return cls


class ABC(metaclass=ABCMeta):
    """Legacy helper class for Abstract Base Classes with virtual inheritance.
    """
    __slots__ = ()


_ABCMeta = ABCMeta
_ABC = ABC
del ABCMeta, ABC
deprecated_names = {"ABCMeta", "ABC"}


def __getattr__(name):
    if name in deprecated_names:
        from warnings import warn
        warn(
            f"{name} is deprecated. You should use Abstract, "
            "Virtual and/or VirtualMeta instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return globals()[f"_{name}"]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
