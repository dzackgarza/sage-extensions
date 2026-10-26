r"""Semidirect products and split radicals from supplied actions.

The formal group construction is Mathlib.GroupTheory.SemidirectProduct,
imported by LeanCategories.Algebra.GroupTheory. For a radical R and a
nondegenerate K, the block map (r,k) -> (b(r)+t(a(k)),a(k)) preserves the
form pulled back from K. Composition gives the action t -> b t a^{-1}.
The projection to (a,b) is split by t=0, so it is onto.
"""

import pytest

from sage_extensions.all import *


def test_inversion_of_c3_by_c2_gives_the_dihedral_relation():
    normal, acting = Groups.C(3), Groups.C(2)
    automorphisms = normal.Aut()
    inversion = automorphisms(tuple(~g for g in normal.group_generators()))
    action = acting.Mor(automorphisms).elementwise(
        lambda g: automorphisms.one() if g == acting.one() else inversion
    )
    product = normal.semidirect_product(action)
    rotation = product.normal_inclusion()(normal.group_generators()[0])
    reflection = product.acting_inclusion()(acting.group_generators()[0])

    assert reflection * rotation * ~reflection == ~rotation
    assert product.cardinality() == cardinal(6)
    assert product.quotient_projection()(rotation) == acting.one()


@pytest.mark.parametrize("gram", ([[-2]], [[-2, 1], [1, -2]]))
def test_the_split_radical_extension_preserves_the_form_and_projects_to_its_factors(gram):
    radical, complement = Lattices(ZZ)([[0]]), Lattices(ZZ)(gram)
    maps = Modules(ZZ).Mor(complement, radical)
    orthogonal, general_linear = complement.O(), radical.general_linear_group()
    action = maps.automorphism_action(
        orthogonal.Mor(orthogonal).identity(),
        general_linear.Mor(general_linear).identity(),
    )
    normal = action.codomain().domain()
    extension = normal.semidirect_product(action)
    factors = action.domain()
    logarithm = maps.multiplicative_group_identification().inverse()
    lattice = radical + complement
    labels = tuple(lattice.module_generating_set())
    radical_label = radical.module_generating_set()[0]
    complement_labels = tuple(complement.module_generating_set())

    def represented(pair):
        a = factors.projection(0)(pair.acting_component())
        b = factors.projection(1)(pair.acting_component())
        shear = logarithm(pair.normal_component())
        images = {labels[0]: lattice.scalar_multiple(b(radical.module_generator(radical_label)).to_vector()(radical_label), lattice.module_generator(labels[0]))}
        for position, label in enumerate(complement_labels):
            image = a(complement.module_generator(label))
            coefficients = {labels[j + 1]: image.to_vector()(index) for j, index in enumerate(complement_labels)}
            coefficients[labels[0]] = shear(image).to_vector()(radical_label)
            images[labels[position + 1]] = lattice.linear_combination(coefficients)
        return lattice.O()(images)

    group_generators = tuple(extension.group_generators())
    for generator in group_generators:
        image = represented(generator)
        for left in lattice.module_generators():
            for right in lattice.module_generators():
                assert image(left).b(image(right)) == left.b(right)
        point = generator.acting_component()
        assert extension.quotient_projection()(extension.acting_inclusion()(point)) == point
    for left in group_generators:
        for right in group_generators:
            assert represented(left * right) == represented(left) * represented(right)
