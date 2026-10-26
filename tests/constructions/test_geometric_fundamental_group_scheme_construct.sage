r"""A geometric fundamental group retains the scheme whose realization defines it."""

from sage_extensions.all import *  # noqa: F401,F403


def test_pgl_two_fundamental_group_retains_topological_scheme() -> None:
    projective = Schemes(QQ).projective_space(3, names=("a", "b", "c", "d"))
    a = projective.coordinate_ring().algebra_generator("a")
    b = projective.coordinate_ring().algebra_generator("b")
    c = projective.coordinate_ring().algebra_generator("c")
    d = projective.coordinate_ring().algebra_generator("d")
    pgl_two = projective.basic_open(a * d - b * c)
    identity = pgl_two.point((1, 0, 0, 1))

    assert pgl_two.analytic_fundamental_group(identity).topological_scheme() is pgl_two
