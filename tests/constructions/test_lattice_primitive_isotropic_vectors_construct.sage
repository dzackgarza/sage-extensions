r"""The hyperbolic plane basis vectors are primitive isotropic vectors and zero is excluded."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_primitive_isotropic_locus_contains_basis_vectors_not_zero() -> None:
    lattice = NamedLattices.U
    first, second = lattice.module_generators()
    locus = lattice.primitive_isotropic_vectors()

    assert first in locus
    assert second in locus
    assert lattice.zero() not in locus
