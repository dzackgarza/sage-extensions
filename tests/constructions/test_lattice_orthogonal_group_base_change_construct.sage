r"""Orthogonal-group base change sends lattice isometries along scalar extension."""

from sage_extensions.all import *  # noqa: F401,F403


def test_identity_scalar_change_gives_endomorphism_of_the_same_orthogonal_group() -> None:
    lattice = NamedLattices.U
    ring_identity = ZZ.Mor(ZZ).identity()
    base_change = lattice.orthogonal_group_base_change(ring_identity)

    assert base_change.domain() is lattice.Aut()
    assert base_change.codomain() is lattice.Aut()


def test_identity_scalar_change_fixes_the_identity_isometry() -> None:
    lattice = NamedLattices.U
    ring_identity = ZZ.Mor(ZZ).identity()
    base_change = lattice.orthogonal_group_base_change(ring_identity)
    identity = lattice.identity_morphism()

    assert base_change(identity) == identity
