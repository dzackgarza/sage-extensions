r"""Isotropic vectors of bounded height against a timelike vector."""

from sage_extensions.all import *


def test_the_isotropic_vectors_of_U_plus_A1_of_height_at_most_one_are_zero_and_plus_minus_e_f() -> None:
    r"""In ``U + A_1`` (``A_1 = <-2>``), ``v = ae + bf + cr`` is isotropic iff ``ab = c^2``.

    Height ``|(v, e+f)| = |a + b| <= 1`` with ``ab >= 0`` forces ``c = 0`` and
    ``v`` in ``{0, +-e, +-f}``.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A1")
    e, f, _root = lattice.module_generators()
    timelike = e + f

    vectors = lattice.isotropic_elements_below_height(timelike, 1)

    assert vectors.cardinality() == 5
    for expected in (lattice.zero(), e, -e, f, -f):
        assert expected in vectors
