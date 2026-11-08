r"""S3/H is the three-point action for H=Stab(1), a nonnormal subgroup.

A3 acts transitively. H fixes the first coset and exchanges the other
two. Coset transporters must give these decisions and inverse witnesses.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("transitive", (True, False), ids=("alternating", "stabilizer"))
def test_subgroup_transporters_on_nonnormal_left_cosets(transitive):
    group = Groups.S(3)
    subgroup = group.subgroup((group((2, 3)),))
    acting = group.subgroup((group((1, 2, 3)),)) if transitive else subgroup
    inclusion = acting.inclusion()
    representatives = (group.one(), group((1, 2)), group((1, 3)))
    for source in representatives:
        for target in representatives:
            witness = FiniteGSets(acting).transporter_on_left_cosets(subgroup, source, target, inclusion)
            expected = transitive or ((source(1) == 1) == (target(1) == 1))
            if not expected:
                assert witness is None
            else:
                lifted = inclusion(witness)
                assert ~target*lifted*source in subgroup
                assert ~source*(~lifted)*target in subgroup


def test_infinite_cyclic_parity_cosets_have_exact_subgroup_transporters():
    free, two = Groups.Free(1), Groups.C(2)
    label = next(iter(free.free_basis()))
    generator = free.free_generator(label)
    involution = next(iter(two.group_generators()))
    parity = free.Mor(two)({label: involution})
    even = parity.kernel()
    identity = free.Mor(free).identity()
    witness = FiniteGSets(free).transporter_on_left_cosets(even, free.one(), generator, identity)
    assert parity(witness) == involution
    assert (~generator)*witness in even
    assert (~witness)*generator in even
    assert FiniteGSets(even).transporter_on_left_cosets(even, free.one(), generator, even.inclusion()) is None


def test_preimage_of_the_squares_in_c6_is_the_whole_group():
    six = Groups.C(6)
    generator = next(iter(six.group_generators()))
    squaring = six.Mor(six)({generator: generator**2})
    squares = six.subgroup((generator**2,))
    preimage = squaring.preimage_subgroup(squares)
    assert six.left_cosets(preimage).cardinality() == cardinal(1)
    augmentation = preimage.schreier_generating_morphism()
    images = tuple(augmentation(point) for point in augmentation.domain().group_generators())
    assert six.subgroup(images).cardinality() == cardinal(6)
    assert all(squaring(point) in squares for point in images)
