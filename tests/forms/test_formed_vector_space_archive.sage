r"""Rationalizations of indefinite binary integral lattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_rational_isotropy_of_a_binary_form_is_minus_the_determinant_being_a_square() -> None:
    r"""``[[2, 1], [1, -2]] (x) Q`` is indefinite and anisotropic; ``U (x) Q`` is isotropic.

    ``2a^2 + 2ab - 2b^2 = 0`` needs a rational root of ``t^2 + t - 1``, whose
    discriminant 5 is not a square; ``U`` has the isotropic vector ``e``.
    """
    lattice = Lattices(ZZ)([[2, 1], [1, -2]])
    rational = lattice.vector_space()
    hyperbolic = Lattices(ZZ)("U").vector_space()

    assert lattice.determinant() == -5
    assert rational.dimension() == 2
    assert not lattice.is_definite()
    assert rational.is_anisotropic()
    assert not hyperbolic.is_anisotropic()
