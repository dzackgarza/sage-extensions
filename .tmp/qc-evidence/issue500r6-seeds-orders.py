"""The three orders for every object and level: what is a function of the seed."""

import json
import os
from collections import defaultdict

from sage_extensions.all import *
from sage_extensions.refine import _nearest_provider, _owned_mixins, _precedes


def reached_map(category, attr):
    reached = defaultdict(list)
    for cat in category.all_super_categories(proper=False):
        provider = _nearest_provider(cat, attr)
        if provider is not None:
            reached[provider].append(cat)
    return reached


def old_order(category, attr):
    """The insertion loop that `476f87cc6f` replaced."""
    reached = reached_map(category, attr)
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
            return provider.__qualname__
    return None


print(f"### seed {os.environ.get('PYTHONHASHSEED')}")
pairs = 0
for label, obj in objects():
    category = obj.category()
    for attr in ("ParentMethods", "ElementMethods", "MorphismMethods"):
        pairs += 1
        reached = reached_map(category, attr)
        walk = [provider.__qualname__ for provider in reached]
        new = [provider.__qualname__ for provider in _owned_mixins(category, attr)]
        old = [provider.__qualname__ for provider in old_order(category, attr)]
        names = set()
        for provider in reached:
            names.update(vars(provider))
        owners = {name: first_declaring(_owned_mixins(category, attr), name) for name in sorted(names)}
        print(json.dumps({"obj": label, "attr": attr, "walk": walk, "new": new, "old": old, "owners": owners}))
print(f"### pairs {pairs}")
