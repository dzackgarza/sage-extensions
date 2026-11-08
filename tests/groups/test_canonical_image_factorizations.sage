r"""The canonical maps C4 -> <g^2> and Z -> <g^2> are epimorphisms.

The image has order two. Its inclusion into C4 composes with the
epimorphism to the original map. An inclusion factors through its own
image by the identity automorphism of that actual subgroup.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("infinite", (False, True), ids=("cyclic-four", "infinite-cyclic"))
def test_canonical_image_factorization_retains_the_subgroup_and_group_law(infinite):
    target = Groups.C(4)
    generator = next(iter(target.group_generators()))
    if infinite:
        source = Groups.Free(1)
        label = next(iter(source.free_basis()))
        point = source.free_generator(label)
        morphism = source.Mor(target)({label: generator**2})
    else:
        source = target
        point = generator
        morphism = source.Mor(target)({generator: generator**2})
    epic, inclusion = morphism.image_factorization()
    image = morphism.image()
    assert epic.domain() is source and epic.codomain() is image
    assert inclusion.domain() is image and inclusion.codomain() is target
    assert image.cardinality() == cardinal(2)
    assert epic.is_surjective() is True
    assert inclusion.is_injective() is True
    for exponent in range(-3, 4):
        assert inclusion(epic(point**exponent)) == morphism(point**exponent) == generator**(2*exponent)
    assert epic(point**2) == image.one()
    identity, same_inclusion = inclusion.image_factorization()
    assert identity.domain() is image and identity.codomain() is image
    assert identity.is_injective() is True
    assert all(identity(value) == value for value in image)
    assert all(same_inclusion(identity(value)) == inclusion(value) for value in image)
