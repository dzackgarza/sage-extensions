r"""The even elements of the point stabilizer S3 in S4 form its A3.

Restricting parity to the supplied S3 gives a kernel of order three. The
returned generating image must equal that whole intersection.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("presented", (False, True), ids=("engine", "predicate"))
def test_parity_kernel_intersected_with_a_point_stabilizer_generates_a3(presented) -> None:
    group = Groups.S(4)
    two = Groups.C(2)
    involution = next(iter(two.group_generators()))
    parity = group.Mor(two)({
        g: involution if g.sign() == -1 else two.one()
        for g in group.group_generators()
    })
    point_stabilizer = group.subgroup((group((1, 2)), group((1, 2, 3))))
    stabilizer = group.predicate_subgroup(
        lambda g: g in point_stabilizer,
        "the stabilizer of the fourth point",
        generating_morphism=group.free_cover((group((1, 2)), group((1, 2, 3)))),
    ) if presented else point_stabilizer
    intersection = parity.kernel().intersection(stabilizer)
    group_generators = tuple(intersection.group_generators())
    generated = group.subgroup(group_generators)

    assert stabilizer.cardinality() == cardinal(6)
    assert generated.cardinality() == intersection.cardinality() == cardinal(3)
    assert group((1, 2, 3)) in generated
    assert group((1, 2)) not in generated
    assert all(g in stabilizer and parity(g) == two.one() for g in group_generators)



