r"""The lattice-vector divisor spelling is the positive divisibility generator."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_basis_vector_divisor_is_its_divisibility() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)

    assert e.divisor() == e.div()


def test_scaled_basis_vector_divisor_tracks_the_scale() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)

    assert (3 * e).divisor() == ZZ(3)
