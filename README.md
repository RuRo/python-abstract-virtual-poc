## Proof of Concept implementation for the `ABC` -> `Abstract` + `Virtual` split

See, [this discuss thread](https://discuss.python.org/t/make-abc-abc-a-regular-class-by-making-instancecheck-and-subclasscheck-class-methods/47547) for context. Based on CPython [`abc.py`](https://github.com/python/cpython/blob/2b379968e554f9ce0832e84f5f8a85131a3be35e/Lib/abc.py) and [`_py_abc.py`](https://github.com/python/cpython/blob/2b379968e554f9ce0832e84f5f8a85131a3be35e/Lib/_py_abc.py) at commit `2b379968`.

> If the only reason why we can't implement `ABC` without metaclasses is because it's needed for virtual inheritance, then why don't we start by separating virtual inheritance and abstract method support.
> 
> It's not immediately clear to me, why was virtual inheritance bundled together with abstract classes in the first place. The motivating examples for adding virtual inheritance in PEP-3119 seem to me like they should be represented by `Protocol`s rather than Abstract classes. So, it might just be historical happenstance that `ABC` includes virtual inheritance support rather than an intentional design decision.
> 
> So here is my proposal:
> 
> 1) Extract just the virtual inheritance parts of `ABCMeta` into a new meta class `VirtualMeta`. Also provide a helper `Virtual` class similar to the `ABC` helper for `ABCMeta`.
> 
> 2) Extract just the abstract class parts of `ABCMeta` (without virtual inheritance support) into a new **normal** class `Abstract` (implemented using `__init_subclass__`).
> 
> 3) Re-implement `ABCMeta` and `ABC` in terms of `Abstract`, `Virtual` and `VirtualMeta` classes, keeping the current behaviour. The new inheritance hierarchy will be an extension of the old hierarchy, so every existing piece of code should continue working.
> 
> 4) *(optional)* Emit deprecation warnings whenever someone imports `ABC` or `ABCMeta`, suggesting that they should use `Abstract`/`Virtual`/`VritualMeta` directly instead.
> 
> With these changes, we would have the following:
> 
> - `Abstract` - a normal class that implements **just** the abstract base class functionality of `ABC` (i.e. setting `__abstractmethods__`). It doesn't use metaclasses. Most people that don't need virtual inheritance can just replace `ABC` with `Abstract`.
> 
> - `VirtualMeta` and `Virtual` implement **just** the virtual inheritance part of `ABC` (i.e. `register`, `isinstance` and `issubclass`). As a bonus, people can now create non-abstract virtual inheritance hierarchies.
> 
> - `ABCMeta` inherits from `VirtualMeta` and automatically adds `Abstract` and `Virtual` as base classes in its `__new__` method. `ABC` is still just a helper class that does `metaclass=ABCMeta`.

Keep in mind, that the current implementation:

- Is written in pure Python.
  (The C `_warning` extension loading is disabled)

- Is not exhaustively tested or documented.
  (There are a few tests and some short docstrings, but it's probably not enough)

- If we choose to deprecate `ABC` and `ABCMeta`, we'd need to also update all of the internal uses of `ABC`/`ABCMeta` in the standard library, typeshed etc.

### Examples

You can run the provided tests with `./run_tests.sh` or `./run_tests_in_docker.sh`.
