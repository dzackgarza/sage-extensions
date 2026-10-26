r"""Invariants of the doubled hyperbolic plane ``U(2)``."""

from sage_extensions.all import *  # noqa: F401,F403


def test_invariants_of_the_doubled_hyperbolic_plane() -> None:
    r"""``U(2) = [[0, 2], [2, 0]]``: rank 2, signature ``(1, 1)``, even, ``det = -4``, ``A = (Z/2)^2``.

    The Gram matrix has eigenvalues ``+-2``; ``b(x, x) = 4ab``; the cokernel of
    the correlation ``L -> L^vee`` is ``(Z/2)^2``.
    """
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    discriminant_group = lattice.discriminant_group()

    assert lattice.rank() == 2
    assert lattice.signature_pair().first() == 1
    assert lattice.signature_pair().second() == 1
    assert lattice.is_even()
    assert lattice.determinant() == -4
    assert discriminant_group.cardinality() == 4
    assert discriminant_group.invariant_factors().cardinality() == 2
    assert all(factor == 2 for factor in discriminant_group.invariant_factors())
    assert not lattice.is_isometric_to(Lattices(ZZ)("U"))
