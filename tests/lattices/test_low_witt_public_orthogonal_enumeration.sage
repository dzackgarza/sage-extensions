r"""Public exact enumeration of low-rational-Witt-index integral orthogonal groups (#40).

No finite presentation or generated-family completeness is claimed: the test
samples the *owned elements* of a mathematically complete lazy enumeration.
"""

from sage_extensions.all import *


def _assert_exact_owned_prefix(gram):
    lattice = Lattices(ZZ)(gram)
    group = lattice.O()
    stream = iter(group)
    elements = tuple(next(stream) for _ in range(4))
    assert all(elements[i] != elements[j] for i in range(4) for j in range(i))
    assert all(element.parent() is group for element in elements)
    assert any(element != group.one() for element in elements)
    basis = tuple(lattice.module_generators())
    for g in elements:
        assert all(lattice.b(g(v), g(w)) == lattice.b(v, w) for v in basis for w in basis)
        assert all(g.inverse()(g(v)) == v for v in basis)


def test_rationally_anisotropic_rank_four_orthogonal_group_is_publicly_enumerable():
    r"""The quadratic norm form 2*(x²+y²-3z²-3w²) has Witt index 0 over Q."""
    _assert_exact_owned_prefix([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, -6, 0], [0, 0, 0, -6]])


def test_rational_witt_one_rank_four_orthogonal_group_is_publicly_enumerable():
    r"""U+<2,-4> has a rational null vector but no rational isotropic 2-plane."""
    _assert_exact_owned_prefix([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, -4]])
