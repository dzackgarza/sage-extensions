r"""Split Witt decompositions give integral sections and supplied parabolic generators.

For L = U + K, the block map id_U + gamma lifts every gamma in O(K).
The kernel of the action on K consists of the Eichler translations and
the simultaneous sign reversal on the first U. These are the split
rank-one formulas of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §3.1.
"""

import pytest

from sage_extensions.all import *


@pytest.mark.parametrize("extra", (False, True))
def test_minus_identity_has_an_integral_levi_lift(extra):
    lattice = NamedLattices.U + NamedLattices.U
    if extra:
        lattice = lattice + Lattices(ZZ)([[-2]])
    isotropic = lattice.basis_vector(0)
    reduction = isotropic.isotropic_reduction()
    levi = reduction.levi_action()
    minus_identity = reduction.O()({
        label: -reduction.module_generator(label)
        for label in reduction.module_generating_set()
    })

    lift = levi.lift(minus_identity)

    assert levi(lift) == minus_identity
    assert lift(isotropic) in (isotropic, -isotropic)
    assert all(lift(vector) in lattice for vector in lattice.module_generators())


def test_the_split_two_plane_preimage_uses_the_supplied_kernel_and_cosets():
    lattice = NamedLattices.U + NamedLattices.U
    e, f, a, b = lattice.module_generators()
    reduction = e.isotropic_reduction()
    levi = reduction.levi_action()
    parabolic, quotient = levi.domain(), levi.codomain()
    reversal = lattice.O()({
        label: -vector if vector in (e, f) else vector
        for label, vector in zip(lattice.module_generating_set(), lattice.module_generators(), strict=True)
    })
    kernel_family = (lattice.eichler_transvection(e, a), lattice.eichler_transvection(e, b), reversal)
    supplied_family = (
        *(parabolic(value) for value in kernel_family),
        *(levi.lift(value) for value in quotient.group_generators()),
    )
    levi = parabolic.Mor(quotient)(lambda value: reduction.levi_action()(value))
    levi.select_section(Sets().Mor(quotient, parabolic)(reduction.levi_action().lift))
    kernel = levi.kernel()
    kernel.select_group_resolution(generators=Set(tuple(kernel(value) for value in kernel_family)))
    parabolic.select_group_resolution(generators=Set(supplied_family))
    quotient_family = tuple(quotient.group_generators())
    image = levi.image()
    point = Sets.Δ[0](0)
    quotient.select_left_cosets(FiniteGSets(quotient).pointed_orbit(image, point, lambda _value, point: point))
    target = quotient.subgroup(quotient_family)
    preimage = levi.preimage_subgroup(target)

    augmentation = preimage.kernel_image_generating_morphism()
    family = tuple(augmentation(letter) for letter in augmentation.domain().group_generators())

    assert all(any(preimage.inclusion()(value) == parabolic(expected) for value in family) for expected in kernel_family)
    assert all(preimage.inclusion()(value)(e) in (e, -e) for value in family)
    assert target.subgroup(tuple(target(levi(preimage.inclusion()(value))) for value in family)).cardinality() == quotient.cardinality()


def test_the_given_two_plane_transvections_construct_their_subgroup():
    lattice = NamedLattices.U + NamedLattices.U
    e, _f, a, b = lattice.module_generators()
    parabolic = e.isotropic_reduction().levi_action().domain()
    first = parabolic(lattice.eichler_transvection(e, a))
    second = parabolic(lattice.eichler_transvection(e, b))

    subgroup = parabolic.subgroup((first, second))
    inclusion = subgroup.inclusion()
    family = tuple(subgroup.group_generators())

    assert family == (first, second)
    assert inclusion(subgroup.one()) == parabolic.one()
    assert first * second == second * first
    assert all(inclusion(generator)(e) == e for generator in family)
