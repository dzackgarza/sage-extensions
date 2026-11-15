"""Every name any provider declares: the same provider answers it, before and after."""

from collections import defaultdict

from sage_extensions.all import *
from sage_extensions.refine import _nearest_provider, _owned_mixins, _precedes


def old_order(category, attr):
    """The insertion loop main used, with the dead guard removed."""
    reached = defaultdict(list)
    for cat in category.all_super_categories(proper=False):
        provider = _nearest_provider(cat, attr)
        if provider is not None:
            reached[provider].append(cat)
    ordered = []
    for provider in reached:
        for index, earlier in enumerate(ordered):
            if _precedes(reached, attr, provider, earlier):
                ordered.insert(index, provider)
                break
        else:
            ordered.append(provider)
    return tuple(ordered)


def objects():
    yield "ZZ", ZZ
    yield "QQ", QQ
    yield "RR", RR
    yield "CC", CC
    yield "QQ(i)", QuadraticField(-1)
    yield "Zmod(8)", Zmod(8)
    yield "GF(4)", GF(4)
    yield "GF(9)", GF(9)
    yield "ZZ**2", ZZ**2
    yield "QQ**2", QQ**2
    yield "ZZ**3", ZZ**3
    yield "GF(3)**2", GF(3)**2
    yield "Zmod(8)**2", Zmod(8)**2
    yield "ZZ[x]", ZZ["x"]
    yield "QQ[x]", QQ["x"]
    yield "ZZ[x,y]", ZZ["x", "y"]
    yield "GF(3)[x]", GF(3)["x"]
    yield "ZZ**NN", ZZ**NN
    yield "QQ**NN", QQ**NN
    yield "M_2(QQ)", QQ.matrix_space(2)
    yield "M_2(ZZ)", ZZ.matrix_space(2)
    yield "M_2(QQ) regular", QQ.matrix_space(2).regular_module()
    yield "Lattices(ZZ)(2)", Lattices(ZZ)(2)
    yield "Lattices(QQ)(QQ**NN)", Lattices(QQ)(QQ**NN)
    yield "Zmod(4)[x]", Zmod(4)["x"]
    yield "ZZ[x]/(x^2)", AlgebrasWithChosenFinitePresentation(ZZ).an_object()


def first_declaring(order, name):
    for provider in order:
        if name in vars(provider):
            return provider
    return None


differences = 0
reorderings = 0
for entry in objects():
    name, obj = entry
    if name.endswith("an_object()"):
        continue
    category = obj.category()
    for attr in ("ParentMethods", "ElementMethods", "MorphismMethods"):
        old = old_order(category, attr)
        new = _owned_mixins(category, attr)
        if old != new:
            reorderings += 1
            print(f"### {name} / {attr}: the two orders differ")
            print("  old: " + " > ".join(p.__qualname__ for p in old))
            print("  new: " + " > ".join(p.__qualname__ for p in new))
        names = set()
        for provider in set(old) | set(new):
            names.update(vars(provider))
        for operation in sorted(names):
            before = first_declaring(old, operation)
            after = first_declaring(new, operation)
            if before is not after:
                differences += 1
                print(f"  NAME MOVED {name} / {attr} / {operation}: "
                      f"{None if before is None else before.__qualname__} -> "
                      f"{None if after is None else after.__qualname__}")
print(f"reorderings: {reorderings}; names whose provider moved: {differences}")
