"""What the general Modules dual is today, and whether an evaluation image is constructible."""
import collections
import sys

from sage_extensions.all import *
import sage_extensions


def show(label, thunk):
    try:
        value = thunk()
    except BaseException as exc:  # noqa: BLE001 - a probe reports what happens
        print(f"{label}: {type(exc).__name__}: {exc}")
        return None
    print(f"{label}: {value!r}")
    return value


print("sage_extensions:", sage_extensions.__file__)
print("countable:", ZZ["x"] in CountablyInfiniteSets())
print("isinstance Iterable (new method):", isinstance(ZZ["x"], collections.abc.Iterable))


class _OldRaisingIter:
    def __iter__(self):
        raise TypeError("cannot enumerate")


print("isinstance Iterable (old style method):", isinstance(_OldRaisingIter(), collections.abc.Iterable))

for name, module in (("ZZ['x']", ZZ["x"]), ("QQ['x']", QQ["x"]), ("ZZ**2", ZZ**2)):
    print(f"--- {name}: base ring {module.base_ring()}")
    print("regular module of base:", module.base_ring().regular_module())
    iso = show("regular_module_isomorphism", lambda m=module: m.base_ring().regular_module_isomorphism())
    dual = show("dual_module", lambda m=module: m.dual_module())
    if dual is not None:
        print("dual category:", dual.category())
        print("dual is the Mor module:", dual is module.module_category().Mor(module, module.base_ring().regular_module()))
        show("dual.module_generating_set()", lambda d=dual: d.module_generating_set())
    mor = show(
        "Mor(module, R.regular_module())",
        lambda m=module: Modules(m.base_ring()).Mor(m, m.base_ring().regular_module()),
    )
    if mor is not None:
        print("mor category:", mor.category())
        show("mor.module_generating_set()", lambda x=mor: x.module_generating_set())
