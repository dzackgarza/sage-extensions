r"""The identity isometry has trivial real invariants and full discriminant-centralizer image."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_identity_preserves_the_positive_cone_and_has_positive_spinor_sign() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()

    assert identity.preserves_positive_cone()
    assert identity.real_spinor_norm_sign() == 1


def test_a2_identity_centralizer_maps_onto_the_discriminant_orthogonal_group() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()

    assert identity.centralizer_discriminant_image() == lattice.discriminant_quadratic_form().O()
