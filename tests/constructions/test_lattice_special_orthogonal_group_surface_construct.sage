r"""The explicit special-orthogonal-group spelling agrees with SO."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_special_orthogonal_group_is_so() -> None:
    lattice = NamedLattices.U

    assert lattice.special_orthogonal_group() == lattice.SO()


def test_identity_isometry_lies_in_the_special_orthogonal_group() -> None:
    lattice = NamedLattices.U

    assert lattice.identity_morphism() in lattice.special_orthogonal_group()
