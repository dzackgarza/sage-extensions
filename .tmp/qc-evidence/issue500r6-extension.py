"""Whether each candidate order is a linear extension of the precedence relation."""

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


def old_order(reached, attr):
    ordered = []
    for provider in reached:
        for index, earlier in enumerate(ordered):
            if _precedes(reached, attr, provider, earlier):
                ordered.insert(index, provider)
                break
        else:
            ordered.append(provider)
    return tuple(ordered)


def violations(reached, attr, order):
    """Pairs the relation orders that `order` puts the wrong way round."""
    position = {provider: index for index, provider in enumerate(order)}
    return [
        (p, q)
        for p in reached
        for q in reached
        if p is not q
        and _precedes(reached, attr, p, q)
        and position[p] > position[q]
    ]


def objects():
    yield "ZZ", ZZ
    yield "QQ", QQ
    yield "QQ(i)", QuadraticField(-1)
    yield "Zmod(8)", Zmod(8)
    yield "GF(9)", GF(9)
    yield "ZZ**2", ZZ**2
    yield "Zmod(8)**2", Zmod(8)**2
    yield "ZZ[x]", ZZ["x"]
    yield "ZZ[x,y]", ZZ["x", "y"]
    yield "ZZ**NN", ZZ**NN
    yield "M_2(QQ) regular", QQ.matrix_space(2).regular_module()
    yield "Lattices(ZZ)(2)", Lattices(ZZ)(2)
    yield "Zmod(4)[x]", Zmod(4)["x"]
    yield "ZZ[x]/(x^2)", AlgebrasWithChosenFinitePresentation(ZZ).an_object()


print(f"### seed {os.environ.get('PYTHONHASHSEED')}")
for label, obj in objects():
    category = obj.category()
    for attr in ("ParentMethods", "ElementMethods", "MorphismMethods"):
        reached = reached_map(category, attr)
        new = _owned_mixins(category, attr)
        old = old_order(reached, attr)
        new_bad = violations(reached, attr, new)
        old_bad = violations(reached, attr, old)
        print(
            json.dumps(
                {
                    "obj": label,
                    "attr": attr,
                    "providers": len(reached),
                    "new-violations": [[p.__qualname__, q.__qualname__] for p, q in new_bad],
                    "old-violations": [[p.__qualname__, q.__qualname__] for p, q in old_bad],
                }
            )
        )
