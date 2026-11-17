r"""The action of a null flag's stabilizer on its successive quotients.

In nU the coordinate flag has a Levi factor: every sign tuple on the null
basis extends by its contragredient, so the graded image is the full sign
group. For the rank-one flag in 2U the image is {+-1} x O(U), with
O(U) = {+-1, +-swap} of order four, because 2U = U + U splits the line.

Under the preimage Gamma of {+-Id} in O(2U mod 3), an element reducing to
eps*Id acts on the line by a sign congruent to eps and on I^perp/I = U by an
element of O(U) congruent to eps*Id. The swap is not congruent to +-Id, so
the graded image lies in {(1, 1), (-1, -1)}, and +-Id in Gamma attain it:
the image has order two.
"""

from sage_extensions.all import *


def test_complete_flag_in_three_hyperbolic_planes_has_sign_image():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    flag = IsotropicFlag(ambient, tuple(ambient.module_generators())[::2])
    image = flag.graded_quotient_action(ambient.O()).image()
    assert image.cardinality() == cardinal(8)


def test_line_flag_in_two_hyperbolic_planes_has_full_quotient_image():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    flag = IsotropicFlag(ambient, (next(iter(ambient.module_generators())),))
    image = flag.graded_quotient_action(ambient.O()).image()
    assert image.cardinality() == cardinal(8)


def test_line_flag_in_two_hyperbolic_planes_under_a_congruence_preimage_has_image_of_order_two():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    group = ambient.O()
    representation = group.congruence_representation(3)
    labels = tuple(ambient.module_generating_set())
    negation = ambient.Aut()(dict(zip(labels, tuple(-point for point in ambient.module_generators()), strict=True)))
    gamma = group.congruence_preimage(3, representation.codomain().subgroup((representation(negation),)))
    flag = IsotropicFlag(ambient, (next(iter(ambient.module_generators())),))
    action = flag.graded_quotient_action(gamma)
    assert all(generator in gamma for generator in action.domain().group_generators())
    assert action.image().cardinality() == cardinal(2)


def test_partial_rank_one_three_flag_graded_image_respects_actual_so_subgroup():
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)("U")
    flag = IsotropicFlag(ambient, tuple(ambient.module_generators())[::2], flag_type=FlagType((1, 3)))
    action = flag.graded_quotient_action(ambient.SO())
    assert all(generator in ambient.SO() for generator in action.domain().group_generators())
    assert all(action(generator) in action.codomain() for generator in action.domain().group_generators())


def test_public_partial_rank_one_three_flag_pointwise_stabilizer_generators():
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)("U")
    basis = tuple(ambient.module_generators())[::2]
    flag = IsotropicFlag(ambient, basis, flag_type=FlagType((1, 3)))
    family = tuple(ambient.O().isotropic_stabilizer_generators(flag, flag=True, pointwise=True))
    assert family
    assert all(g(point) == point for g in family for point in basis)


def test_partial_flag_actual_special_orthogonal_setwise_and_pointwise_stabilizers():
    ambient = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)("U")
    basis = tuple(ambient.module_generators())[::2]
    flag = IsotropicFlag(ambient, basis, flag_type=FlagType((1, 3)))
    special = ambient.SO()
    setwise = flag.stabilizer(special)
    pointwise = flag.stabilizer(special, pointwise=True)
    assert all(g in special for g in setwise.group_generators())
    assert all(all(term.inclusion().is_in_image(g(term.inclusion()(x)))
                   for x in term.module_generators())
               for g in setwise.group_generators() for term in flag.terms())
    assert all(g in special and all(g(point) == point for point in basis)
               for g in pointwise.group_generators())
