r"""Signature-(1,n) lattices expose the positive-cone subgroup and character."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperbolic_plane_identity_lies_in_positive_cone_subgroup() -> None:
    lattice = NamedLattices.U
    identity = lattice.identity_morphism()

    assert identity in lattice.positive_cone_subgroup()
    assert identity in lattice.O_component()


def test_hyperbolic_plane_component_character_is_trivial_on_identity() -> None:
    lattice = NamedLattices.U
    character = lattice.component_character()
    identity = lattice.identity_morphism()

    assert character.domain() is lattice.Aut()
    assert character(identity) == character.codomain().one()
