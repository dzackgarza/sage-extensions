r"""The blowup of ``P^2`` at a torus-fixed point is the Hirzebruch surface ``F_1``.

Blowing up the fixed point of the smooth cone ``Cone(u, v)`` star-subdivides it by the ray
``u + v`` (Cox--Little--Schenck, *Toric Varieties*, Prop. 3.3.15 and Def. 3.3.17, checked).  For
``P^2`` this gives the fan of ``F_1`` with four rays; the exceptional curve has self-intersection
``-1`` and ``K^2`` drops from 9 to 8, so the blowup is a del Pezzo surface of degree 8.
"""

from sage_extensions.all import *


def _blowup():
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cone = next(cone for cone in plane.fan().maximal_cones()
                if cone.rays()[0] + cone.rays()[1] == plane.cocharacter_lattice()((-1, 0)))
    return plane, cone, plane.toric_fixed_point_blowup(cone)


def test_the_blowup_adds_the_sum_of_the_two_rays_of_the_cone() -> None:
    r"""For ``Cone(-e_1 - e_2, e_2)`` the new ray is ``-e_1``; the result is smooth with four rays and is ``F_1``."""
    plane, cone, blowup = _blowup()

    assert blowup.is_toric_fixed_point_blowup()
    assert blowup.blowup_source() is plane
    assert blowup.blowup_center_cone() == cone
    assert blowup.exceptional_ray().rays()[0] == blowup.cocharacter_lattice()((-1, 0))
    assert blowup.is_smooth()
    assert blowup.is_hirzebruch_surface(1)
    assert blowup.blowup_morphism().codomain() is plane
    assert blowup.is_del_pezzo()


def test_the_strict_transform_of_an_invariant_line_through_the_point() -> None:
    r"""The strict transform of ``D_{-e_1 - e_2}`` is the prime divisor of the same ray upstairs."""
    plane, cone, blowup = _blowup()
    ray = next(ray for ray in cone.faces(1) if ray.rays()[0] == plane.cocharacter_lattice()((-1, -1)))
    upstairs = next(r for r in blowup.fan().cones(1) if r.rays()[0] == blowup.cocharacter_lattice()((-1, -1)))

    assert blowup.strict_transform_divisor(plane.torus_invariant_prime_divisor(ray)) == (
        blowup.torus_invariant_prime_divisor(upstairs)
    )


def test_the_exceptional_curve_is_a_minus_one_curve() -> None:
    r"""``E^2 = -1``."""
    plane, cone, blowup = _blowup()

    assert blowup.exceptional_self_intersection() == -1


def test_the_blowup_is_a_del_pezzo_surface_of_degree_eight() -> None:
    r"""``K_{F_1}^2 = K_{P^2}^2 - 1 = 8``."""
    plane, cone, blowup = _blowup()

    assert Surfaces(blowup.scheme_base_ring()).DelPezzo()(blowup).del_pezzo_degree() == 8
