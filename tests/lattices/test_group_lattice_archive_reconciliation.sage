r"""Isotypic and coinvariant sublattices of A2 under the swap action of C2."""

import pytest

from sage_extensions.all import *


def _acted_a2():
    lattice = Lattices(ZZ)("A2")
    group = Groups.C(2)
    first, second = lattice.module_generators()
    swap = lattice.Aut()({0: second, 1: first})
    return Lattices(ZZ[group])(
        lattice,
        lambda element, vector: vector if element == group.one() else swap(vector),
    )


def test_archive_isotypic_lattice_retains_form_action_and_embedding() -> None:
    acted = _acted_a2()
    assert acted.group_module() is acted
    assert acted.unformed_module() is acted.source_group_module().unformed_module()
    assert acted.action_functor() is acted.source_group_module().action_functor()
    characters = acted.group_module().isotypic_characters()
    nontrivial = next(character for character in characters if not character.is_trivial())

    component = acted.isotypic_lattice(nontrivial)
    assert component.module_rank() == 1
    assert component.ambient_lattice() is acted
    assert component in Lattices(ZZ[acted.group()])

    generator = component.module_generators()[0]
    group_generator = acted.group().group_generators()[0]
    inclusion = component.inclusion()
    assert inclusion(component.action_of(group_generator)(generator)) == acted.action_of(
        group_generator
    )(inclusion(generator))
    assert component.determinant() == 2


def test_archive_coinvariant_lattice_is_the_formed_orthogonal_complement() -> None:
    acted = _acted_a2()
    invariant = acted.invariant_lattice()
    coinvariant = acted.coinvariant_lattice()

    assert coinvariant is acted.coinvariant_lattice()
    assert coinvariant is acted.formed_coinvariants()
    assert coinvariant.ambient_lattice() is acted
    assert coinvariant.module_rank() == 1
    assert coinvariant == invariant.orthogonal_complement()
    assert acted.module_coinvariants() is not coinvariant


def test_archive_group_lattice_mor_is_both_isometric_and_equivariant() -> None:
    acted = _acted_a2()
    group_generator = acted.group().group_generators()[0]
    action = acted.action_of(group_generator)
    labels = acted.module_generating_set()

    equivariant = acted.Mor(acted)(
        {
            label: action(acted.module_generator(label))
            for label in labels
        }
    )
    assert equivariant.domain() is acted
    assert equivariant.codomain() is acted
    for label in labels:
        generator = acted.module_generator(label)
        assert equivariant(generator) == action(generator)
        for other_label in labels:
            other = acted.module_generator(other_label)
            assert acted.b(equivariant(generator), equivariant(other)) == acted.b(
                generator, other
            )

    square = equivariant * equivariant
    assert square.parent() is acted.Mor(acted)
    for label in labels:
        generator = acted.module_generator(label)
        assert square(generator) == generator


def test_archive_group_lattice_mor_rejects_a_nonequivariant_isometry() -> None:
    acted = _acted_a2()
    labels = acted.module_generating_set()
    root = acted.module_generator(labels[0])
    reflection = acted.reflection(root)
    group_generator = acted.group().group_generators()[0]
    action = acted.action_of(group_generator)

    assert reflection * action != action * reflection
    with pytest.raises(ValueError):
        acted.Mor(acted)(
            {
                label: reflection(acted.module_generator(label))
                for label in labels
            }
        )
