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


def test_equivalence_witnesses_are_exact_isometries():
    lattice, group, x, r, vector = _setup()
    for source, target in (((1, 0), (1, 1)), ((5, 1), (5, 6))):
        witness = group.vector_equivalence_witness(vector(*source), vector(*target))
        assert witness(vector(*source)) == vector(*target)
        assert lattice.q(witness(x)) == lattice.q(x)
        assert witness(r) in (r, -r)
    assert group.vector_equivalence_witness(vector(5, 1), vector(5, 2)) is None


def test_orbit_representatives_of_square_fifty():
    r"""q = 50 forces x = +-5, and t is a class of Z/5 up to sign: t = 0, 1, 2."""
    lattice, group, _x, r, _vector = _setup()
    classes = tuple(group.vector_orbit_representatives(50))
    assert len(classes) == int(3)
    assert all(lattice.q(point) == 50 for point in classes)


def test_congruence_subgroup_witnesses_on_a_degenerate_lattice():
    r"""Gamma(3) on <2> + 0: e = d = 1, b = 3k. (x, t) -> (x, t + 3kx) carries (1, 1) to (1, 4),
    and no element of Gamma(3) sends (1, 1) to (1, 2), since b must be 1 modulo 3."""
    _lattice, group, _x, _r, vector = _setup()
    gamma = group.congruence_preimage(3)
    witness = gamma.vector_equivalence_witness(vector(1, 1), vector(1, 4))
    assert witness is not None and witness(vector(1, 1)) == vector(1, 4) and witness in gamma
    assert gamma.vector_equivalence_witness(vector(1, 1), vector(1, 2)) is None
