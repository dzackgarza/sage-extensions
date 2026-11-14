r"""The joint determinant/discriminant representation of O(U(3)) is faithful.

An integral isometry of the hyperbolic plane sends its primitive null
basis to signed coordinate null vectors. Thus O(U(3)) consists of the
identity, simultaneous negation, coordinate exchange and their product.
Reduction modulo three distinguishes them all.
"""

import pytest

from sage_extensions.all import *


def test_joint_characters_of_the_scaled_hyperbolic_plane_retain_the_actual_image():
    lattice = Lattices(ZZ)("U").twist(3)
    group = lattice.O()
    subgroup = lattice.SO().intersection(lattice.stable_orthogonal_group())
    quotient = subgroup.finite_character_quotient()
    character = quotient.character_representation()
    assert character.domain() is group
    assert character.codomain() in Groups().Finite()
    assert character.codomain().cardinality() == cardinal(8)
    e, f = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    elements = tuple(
        group(dict(zip(labels, images, strict=True)))
        for images in ((e, f), (-e, -f), (f, e), (-f, -e))
    )
    images = tuple(character(element) for element in elements)
    assert Set(images).cardinality() == cardinal(4)
    for left in elements:
        for right in elements:
            assert character(left * right) == character(left) * character(right)
    for element in elements:
        assert (element in subgroup) == character(element).is_one()
    cosets = group.left_cosets(subgroup)
    assert cosets.cardinality() == cardinal(4)
    assert Set(tuple(cosets.act(element, cosets.base_point()) for element in elements)).cardinality() == cardinal(4)
    for coset in cosets:
        lift = cosets.transporter_witness(cosets.base_point(), coset)
        assert cosets.act(lift, cosets.base_point()) == coset


@pytest.mark.parametrize("condition, index", (("determinant", 2), ("spinor", 2), ("both", 4)))
def test_hyperbolic_sign_characters_retain_their_exact_coset_actions(condition, index):
    r"""The signed coordinate group of U has independent determinant and real spinor signs."""
    lattice = Lattices(ZZ)("U")
    group = lattice.O()
    subgroup = {
        "determinant": lattice.SO,
        "spinor": lattice.O_plus,
        "both": lambda: lattice.SO().intersection(lattice.O_plus()),
    }[condition]()
    character = subgroup.finite_character_quotient().character_representation()
    e, f = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    elements = tuple(
        group(dict(zip(labels, images, strict=True)))
        for images in ((e, f), (-e, -f), (f, e), (-f, -e))
    )
    assert Set(tuple(character(element) for element in elements)).cardinality() == cardinal(index)
    cosets = group.left_cosets(subgroup)
    assert cosets.cardinality() == cardinal(index)
    base = cosets.base_point()
    for element in elements:
        assert (cosets.act(element, base) == base) == (element in subgroup)
        assert (element in subgroup) == character(element).is_one()
        for point in cosets:
            assert cosets.act(~element, cosets.act(element, point)) == point
    for point in cosets:
        witness = cosets.transporter_witness(base, point)
        assert cosets.act(witness, base) == point
