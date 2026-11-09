r"""Pointed vectors on L = <2> + 0, coordinates (x, y), q = 2x^2.

O(L) is the matrices (x, y) -> (e x, b x + d y) with e, d = +-1 and b integral. Fixing (1, 0)
forces e = 1 and b = 0, leaving d = +-1: a stabilizer of order 2. A map sends (5, 1) to
(5, t) with e = 1 exactly when t = 5b + d, so t is +-1 modulo 5: 6 is reached and 2 is not.
"""

from sage_extensions.all import *


def _setup():
    lattice = Lattices(ZZ)([[2, 0], [0, 0]])
    x, r = tuple(lattice.module_generators())
    return lattice, lattice.O(), x, r, lambda a, b: lattice.scalar_multiple(a, x) + lattice.scalar_multiple(b, r)


def test_pointed_equivalences_and_their_negative():
    _lattice, group, _x, _r, vector = _setup()
    assert group.vectors_are_equivalent(vector(1, 0), vector(1, 1))
    assert group.vectors_are_equivalent(vector(5, 1), vector(5, 6))
    assert not group.vectors_are_equivalent(vector(5, 1), vector(5, 2))


def test_pointwise_stabilizer_has_order_two():
    lattice, group, x, r, vector = _setup()
    generators = tuple(group.vector_stabilizer_generators(vector(1, 0)))
    assert all(g(vector(1, 0)) == vector(1, 0) for g in generators)
    images = set(str(g(r)) for g in generators) | set([str(r)])
    assert images == set([str(r), str(-r)])
    assert all(g(x) == x for g in generators)
