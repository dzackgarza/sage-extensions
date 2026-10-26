r"""Equipping a lattice with an isometry gives the canonical cyclic action."""

from sage_extensions.all import *  # noqa: F401,F403


def test_lattice_with_identity_isometry_has_trivial_cyclic_action() -> None:
    lattice = NamedLattices.U
    identity = lattice.identity_morphism()
    equivariant = lattice.with_isometry(identity)
    group = equivariant.acting_group()
    generator = group.group_generators()[0]
    e = lattice.basis_vector(0)

    assert equivariant.underlying_object() is lattice
    assert equivariant.underlying_category() == Lattices(ZZ)
    assert equivariant.action_of(generator)(e) == e


def test_lattice_with_identity_isometry_retains_the_action_functor() -> None:
    lattice = NamedLattices.U
    equivariant = lattice.with_isometry(lattice.identity_morphism())
    functor = equivariant.action_functor()

    assert functor.domain() == equivariant.acting_group().classifying_category()
    assert functor.codomain() == Lattices(ZZ)
