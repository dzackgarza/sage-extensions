r"""The action of a null flag's stabilizer on its successive quotients.

In nU the coordinate flag has a Levi factor: every sign tuple on the null
basis extends by its contragredient, so the graded image is the full sign
group. For the rank-one flag in 2U the image is {+-1} x O(U), with
O(U) = {+-1, +-swap} of order four, because 2U = U + U splits the line.
"""

from sage_extensions.all import *


def test_complete_flag_in_three_hyperbolic_planes_has_sign_image():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    flag = IsotropicFlag(ambient, tuple(ambient.module_generators())[::2])
    image = flag.graded_quotient_action().image()
    assert image.cardinality() == cardinal(8)


def test_line_flag_in_two_hyperbolic_planes_has_full_quotient_image():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    flag = IsotropicFlag(ambient, (next(iter(ambient.module_generators())),))
    image = flag.graded_quotient_action().image()
    assert image.cardinality() == cardinal(8)
