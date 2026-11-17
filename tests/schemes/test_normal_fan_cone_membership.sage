r"""Membership in a cone of a normal fan.

CLS Def. 2.3.2 and Def. 3.1.2: the normal fan of a polytope is the fan of the
normal cones of its faces, so each of its cones contains its own rays, and the
identity of the cocharacter lattice carries every cone into itself.
"""

from sage_extensions.all import *


def _triangle_polygon():
    return ConvexPolytopes(ZZ.free_module(2))(((0, 0), (2, 0), (0, 1)))


def test_a_cone_of_a_normal_fan_contains_its_own_rays() -> None:
    fan = _triangle_polygon().normal_fan()

    assert fan.is_complete()
    for cone in tuple(fan.maximal_cones()):
        assert all(cone.contains(ray) for ray in tuple(cone.rays()))


def test_the_identity_of_the_cocharacter_lattice_is_compatible_with_a_normal_fan() -> None:
    fan = _triangle_polygon().normal_fan()
    cocharacters = fan.cocharacter_lattice()
    identity = cocharacters.module_category().Mor(cocharacters, cocharacters).identity()

    assert fan.is_compatible_with(identity, fan)
