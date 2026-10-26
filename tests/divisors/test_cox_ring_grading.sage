r"""The Cox ring ``S = k[x_rho]`` of a toric variety, graded by the class group.

By definition ``x_rho`` has degree ``[D_rho]`` in ``Cl(X)``, and a monomial has
the sum of the degrees of its factors.  On ``P^2`` the three rays give three
variables of one degree, the class of a line.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_cox_ring_of_the_plane_is_a_cox_ring_of_the_plane_only() -> None:
    r"""``S(P^2)`` is an object of the Cox rings of ``P^2`` and not of those of the Hirzebruch surface ``F_1``."""
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cox = plane.cox_ring()

    assert cox in CoxRings(plane)
    assert cox not in CoxRings(RationalPolyhedralFans(ZZ.free_module(2)).hirzebruch_surface_fan(1).toric_variety(QQ))


def test_the_cox_ring_of_the_plane_has_three_variables() -> None:
    r"""``P^2`` has three rays, so its Cox ring has three variables."""
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)

    assert plane.cox_ring().algebra_generating_set().cardinality() == 3


def test_the_variables_of_the_cox_ring_of_the_plane_share_the_class_of_a_line() -> None:
    r"""``deg x0 = deg x1 = deg x2 = [H] != 0`` and ``deg(x0 x1) = 2 [H]``."""
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cox = plane.cox_ring()
    x0 = cox.algebra_generator("x0")
    x1 = cox.algebra_generator("x1")

    assert cox.cox_scheme() is plane
    assert cox.generator_degree("x0") == cox.generator_degree("x1")
    assert cox.generator_degree("x1") == cox.generator_degree("x2")
    assert cox.generator_degree("x0") != plane.class_group().zero()
    assert cox.homogeneous_degree(x0 * x1) == 2 * cox.generator_degree("x0")
