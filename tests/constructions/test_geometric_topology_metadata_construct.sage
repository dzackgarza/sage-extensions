r"""Geometric topology objects retain their chosen realization data."""

from sage_extensions.all import *  # noqa: F401,F403


def test_pgl_two_fundamental_group_retains_realization() -> None:
    projective = Schemes(QQ).projective_space(3, names=("a", "b", "c", "d"))
    a = projective.coordinate_ring().algebra_generator("a")
    b = projective.coordinate_ring().algebra_generator("b")
    c = projective.coordinate_ring().algebra_generator("c")
    d = projective.coordinate_ring().algebra_generator("d")
    pgl_two = projective.basic_open(a * d - b * c)
    identity = pgl_two.point((1, 0, 0, 1))
    pi_one = pgl_two.analytic_fundamental_group(identity)

    assert pi_one.realization_description() == "PGL_2(C) deformation retracted to PU(2) ~= SO(3)"


def test_toric_projective_plane_fundamental_group_retains_realization() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    pi_one = plane.fundamental_group(next(iter(plane.fan().maximal_cones())))

    assert "complex analytic realization" in pi_one.realization_description()


def test_integral_topology_retains_theory_and_realization() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    degree_two = plane.integral_singular_cohomology(2)

    assert degree_two.cohomology_topology() == "singular cohomology of the complex analytic realization"
    assert "complex analytic realization" in degree_two.realization_description()
