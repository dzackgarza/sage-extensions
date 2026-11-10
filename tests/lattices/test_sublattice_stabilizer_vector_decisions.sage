r"""Vector equivalence under setwise and pointwise sublattice stabilizers of indefinite lattices.

L = U, S = Z(e + 3f). O(U) = {1, -1, s, -s} with s the swap, and s(e + 3f) = 3e + f, so the
setwise stabilizer of S is {1, -1}: the orbit of e is {e, -e}, and 3f is not in it. The
pointwise stabilizer is trivial.
"""

from sage_extensions.all import *


def _line_in_u():
    lattices = Lattices(ZZ)
    ambient = lattices("U")
    e, f = tuple(ambient.module_generators())
    line = lattices([[6]])
    (label,) = tuple(line.module_generating_set())
    embedding = lattices.Mor(line, ambient)(lambda _label: e + f + f + f)
    return ambient, e, f, embedding


def test_setwise_stabilizer_of_an_indefinite_line_decides_vectors():
    ambient, e, f, embedding = _line_in_u()
    stabilizer = ambient.O().setwise_stabilizer(embedding)
    witness = stabilizer.vector_equivalence_witness(e, -e)
    assert witness is not None and witness in stabilizer and witness(e) == -e
    assert stabilizer.vector_equivalence_witness(e, f + f + f) is None


def test_pointwise_stabilizer_of_an_indefinite_line_is_trivial_on_vectors():
    ambient, e, f, embedding = _line_in_u()
    stabilizer = ambient.O().pointwise_stabilizer(embedding)
    assert stabilizer.vector_equivalence_witness(e, -e) is None
    assert stabilizer.vector_equivalence_witness(e, e) is not None


def test_orbit_set_of_the_setwise_stabilizer_on_null_vectors():
    r"""The primitive null vectors of U are +-e and +-f, so {1, -1} has the two orbits {+-e}, {+-f}."""
    from itertools import islice

    ambient, e, f, embedding = _line_in_u()
    stabilizer = ambient.O().setwise_stabilizer(embedding)
    orbits = ambient.O().vector_orbit_set(0, subgroup=stabilizer)
    first, second = islice(iter(orbits), 2)
    null = set(str(v) for v in (e, -e, f, -f))
    assert str(first) in null and str(second) in null and not orbits.equivalent(first, second)
    assert orbits.equivalent(e, -e) and not orbits.equivalent(e, f)
