r"""The double-coset adjustment when the subgroup's condition subgroup is trivial.

`OrthogonalCharacterQuotient.adjust_witness_into_subgroup` left-adjusts an ambient
witness into the subgroup `Gamma = chi^-1(S)` by an element `x` of the target
stabilizer's image `W` with `x` in `S t`, `t` the witness's image.  When `S` is
trivial that product is `W` itself -- `S 1 W = W` -- so the question is `W`'s own
membership test and the element asked for is the witness's image itself.  This file
pins the two answers of that case on the smallest model that has them:
`M = <2> + <2>`, whose `Gamma = ker rho` has `rho(Gamma)` trivial, a nontrivial
stabilizer image (the whole ambient image) and a trivial one, with witnesses inside
and outside the subgroup.

The stabilizer image `W` is the whole ambient image in the first case and trivial
in the second, so the two answers are the positive and the negative one.
"""

from sage_extensions.all import *


def _kernel_model():
    r"""`M = <2> + <2>`, its group, and the kernel of the discriminant character."""
    lattice = Lattices(ZZ)([[2, 0], [0, 2]])
    group = lattice.O()
    orthogonal = lattice.discriminant_group().orthogonal_group()
    kernel = group.discriminant_preimage(orthogonal.trivial_subgroup())
    assert kernel.character_data_is_complete()
    return lattice, group, kernel


def test_the_condition_subgroup_of_the_kernel_is_trivial() -> None:
    _lattice, group, kernel = _kernel_model()
    assert int(kernel.discriminant_image().cardinality()) == 1
    assert kernel.cardinality() < group.cardinality()


def test_a_trivial_condition_adjusts_an_outside_witness_into_the_kernel() -> None:
    _lattice, group, kernel = _kernel_model()
    quotient = kernel.finite_character_quotient()
    ambient = tuple(group.group_generators())
    outside = next(generator for generator in ambient if generator not in kernel)
    # With the whole ambient image as the stabilizer image the double coset is the
    # whole image, so an adjustment exists and it lies in the kernel.
    adjusted = quotient.adjust_witness_into_subgroup(outside, ambient)
    assert adjusted in kernel
    # The witness itself is outside the kernel, so an answer that merely handed the
    # witness back would not be an adjustment at all.
    assert adjusted != outside


def test_a_trivial_stabilizer_image_adjusts_nothing() -> None:
    _lattice, group, kernel = _kernel_model()
    quotient = kernel.finite_character_quotient()
    ambient = tuple(group.group_generators())
    outside = next(generator for generator in ambient if generator not in kernel)
    # `W = 1` leaves `S W = S` trivial, and the witness's image is not the identity:
    # there is no adjustment, and the answer is the negative one, not a raise.
    assert quotient.adjust_witness_into_subgroup(outside, (group.one(),)) is None
    # An element of the subgroup is its own adjustment and is returned unchanged.
    inside = next(generator for generator in ambient if generator in kernel)
    assert quotient.adjust_witness_into_subgroup(inside, (group.one(),)) is inside


def test_joint_discriminant_and_real_spinor_adjustment() -> None:
    r"""The factorwise permutation model also adjusts a two-character kernel."""
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    group = lattice.O()
    kernel = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    quotient = kernel.finite_character_quotient()
    assert group.cardinality() == cardinal(4)
    assert kernel.cardinality() == cardinal(1)
    assert quotient.index() == 4
    ambient = tuple(group.group_generators())
    outside = next(generator for generator in ambient if generator not in kernel)
    adjusted = quotient.adjust_witness_into_subgroup(outside, ambient)
    assert adjusted in kernel
    assert adjusted != outside
