"""What the precedence relation does: self-relation, symmetry, transitivity."""

import json
import os
from collections import defaultdict

from sage_extensions.all import *
from sage_extensions.refine import _nearest_provider, _precedes


def reached_map(category, attr):
    reached = defaultdict(list)
    for cat in category.all_super_categories(proper=False):
        provider = _nearest_provider(cat, attr)
        if provider is not None:
            reached[provider].append(cat)
    return reached


def objects():
    yield "ZZ", ZZ
    yield "QQ(i)", QuadraticField(-1)
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
        order = list(reached)
        holds = {(p, q): _precedes(reached, attr, p, q) for p in order for q in order}
        self_relation = [p for p in order if holds[(p, p)]]
        symmetric = [
            (p, q)
            for i, p in enumerate(order)
            for q in order[i + 1 :]
            if holds[(p, q)] and holds[(q, p)]
        ]
        untransitive = [
            (p, q, r)
            for p in order
            for q in order
            for r in order
            if len({p, q, r}) == 3
            and holds[(p, q)]
            and holds[(q, r)]
            and not holds[(p, r)]
        ][:3]
        print(
            json.dumps(
                {
                    "obj": label,
                    "attr": attr,
                    "providers": len(order),
                    "self": [p.__qualname__ for p in self_relation][:4],
                    "self-count": len(self_relation),
                    "symmetric": [
                        [p.__qualname__, q.__qualname__] for p, q in symmetric
                    ][:4],
                    "symmetric-count": len(symmetric),
                    "untransitive": [
                        [p.__qualname__, q.__qualname__, r.__qualname__]
                        for p, q, r in untransitive
                    ],
                }
            )
        )
