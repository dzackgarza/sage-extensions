r"""The identity isometry of A2 has canonical centralizer and discriminant action."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_identity_isometry_is_an_involution_with_full_centralizer() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()

    assert identity.is_involution()
    assert identity.centralizer_group() is lattice.O()


def test_a2_identity_isometry_induces_identity_on_the_discriminant_form() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()
    discriminant = lattice.discriminant_quadratic_form()

    assert identity.discriminant_isometry() == discriminant.O().one()
    assert identity.discriminant_morphism() == discriminant.O().one()


def test_a2_identity_is_equivariantly_isometric_to_itself() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()

    assert identity.equivariant_isometry_to(identity) == identity
