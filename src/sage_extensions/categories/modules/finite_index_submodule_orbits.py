r"""Finite-index submodule orbits in framed free ZZ-modules.

Private computation owned by the module layer.  The caller supplies the actual
integral automorphisms of the free module; no ambient isometry image is assumed.
"""

from itertools import product
from math import prod

from sage.all import ZZ as SageZZ, matrix


def _finite_index_submodule_orbits(module, divisors, automorphisms):
    r"""One represented subobject per orbit of index-type ``divisors``.

    Full-rank submodules are enumerated by row Hermite normal form.  The
    supplied automorphisms act on their row spans; the finite orbits are
    computed exactly.  Each returned inclusion has codomain ``module``.
    """
    rank = int(module.module_rank())
    divisors = tuple(int(d) for d in divisors)
    if len(divisors) != rank or any(d < 1 for d in divisors) or any(b % a for a, b in zip(divisors, divisors[1:])):
        raise ValueError("elementary divisors must be positive, ordered by divisibility, and match the module rank")
    labels = tuple(module.module_generating_set())
    index = prod(divisors)

    def diagonal_families(remaining, size):
        if size == 0:
            if remaining == 1:
                yield ()
            return
        for d in range(1, remaining + 1):
            if remaining % d == 0:
                for tail in diagonal_families(remaining // d, size - 1):
                    yield (d, *tail)

    candidates = {}
    for diagonal in diagonal_families(index, rank):
        slots = tuple((i, j) for i in range(rank) for j in range(i + 1, rank))
        for entries in product(*(range(diagonal[j]) for i, j in slots)):
            h = matrix(SageZZ, rank, rank, 0)
            for i, d in enumerate(diagonal):
                h[i, i] = d
            for (i, j), value in zip(slots, entries, strict=True):
                h[i, j] = value
            if tuple(abs(int(d)) for d in h.elementary_divisors()) == divisors:
                candidates[tuple(tuple(int(v) for v in row) for row in h.rows())] = h

    actions = []
    for automorphism in automorphisms:
        rows = []
        for point in module.module_generators():
            coordinates = automorphism(point).to_vector()
            rows.append([int(coordinates(label)) for label in labels])
        actions.append(matrix(SageZZ, rows))
    unseen = set(candidates)
    representatives = []
    while unseen:
        start = min(unseen)
        representatives.append(candidates[start])
        frontier = [start]
        unseen.remove(start)
        while frontier:
            current = candidates[frontier.pop()]
            for action in actions:
                moved = (current * action).hermite_form()
                key = tuple(tuple(int(v) for v in row) for row in moved.rows())
                if key in unseen:
                    unseen.remove(key)
                    frontier.append(key)
    return tuple(module.subobject_on(tuple(
        module.linear_combination({label: module.base_ring()(int(value))
            for label, value in zip(labels, row, strict=True) if value})
        for row in h.rows())).inclusion() for h in representatives)


__all__ = []
