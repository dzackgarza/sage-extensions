r"""A smooth simplicial cone exposes its lattice, faces, intersections, and supporting characters."""

from sage_extensions.all import *  # noqa: F401,F403


def test_first_quadrant_fan_and_cone_remaining_surface() -> None:
    lattice = ZZ.free_module(2)
    fan = RationalPolyhedralFans(lattice)((((1, 0), (0, 1)),))
    cone = fan.maximal_cones()[0]
    ray = cone.faces(1)[0]
    supporting_generators = cone.face_supporting_generators(ray)
    supporting_character = cone.face_supporting_character(ray)

    assert fan.cocharacter_lattice() is lattice
    assert fan.is_simplicial()
    assert cone.lattice() is lattice
    assert cone.character_lattice() is fan.character_lattice()
    assert cone.dimension() == 2
    assert cone.is_smooth()
    assert cone.intersection(ray) == ray
    assert supporting_generators.cardinality() == cardinal(1)
    assert ray.orthogonal_contains(supporting_character)
    assert cone.dual_cone_contains(supporting_character)
