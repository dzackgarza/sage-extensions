r"""The analytic fundamental group of PGL_2(C) is cyclic of order two."""

from sage_extensions.all import *  # noqa: F401,F403


def test_pgl_two_has_order_two_fundamental_group() -> None:
    projective = Schemes(QQ).projective_space(3, names=("a", "b", "c", "d"))
    a = projective.coordinate_ring().algebra_generator("a")
    b = projective.coordinate_ring().algebra_generator("b")
    c = projective.coordinate_ring().algebra_generator("c")
    d = projective.coordinate_ring().algebra_generator("d")
    pgl_two = projective.basic_open(a * d - b * c)
    identity = pgl_two.point((1, 0, 0, 1))
    pi_one = pgl_two.analytic_fundamental_group(identity)

    assert pi_one in GeometricFundamentalGroups()
    assert pi_one.cardinality() == 2
    assert pi_one.is_abelian()
    assert pi_one.base_point() == identity
