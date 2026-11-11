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
    assert action.domain().supergroup() is group
    assert all(generator in gamma for generator in action.domain().group_generators())
    assert action.image().cardinality() == cardinal(2)
