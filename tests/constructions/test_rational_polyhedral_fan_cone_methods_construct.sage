r"""A first-quadrant fan exposes the character pairing, faces, dual semigroup, and compatibility."""

from sage_extensions.all import *  # noqa: F401,F403


def test_first_quadrant_cone_pairing_and_dual_semigroup() -> None:
    lattice = ZZ.free_module(2)
    fans = RationalPolyhedralFans(lattice)
    fan = fans((((1, 0), (0, 1)),))
    cone = fan.maximal_cones()[0]
    characters = fan.character_lattice()
    e1, e2 = lattice.module_generators()
    m1, m2 = characters.module_generators()
    character = m1 + 2 * m2
    coefficients = cone.semigroup_coefficients(character)

    assert fan.lattice() is lattice
    assert fan.character_cocharacter_pairing()(m1, e1) != fan.character_cocharacter_pairing()(m1, e2)
    assert fan.character_cocharacter_value(m1, e1) == 1
    assert fan.character_cocharacter_value(m1, e2) == 0
    assert cone.is_simplicial()
    assert cone.contains(e1 + e2)
    assert cone.relative_interior_contains(e1 + e2)
    assert not cone.relative_interior_contains(e1)
    assert cone.pair_with(character).cardinality() == cardinal(2)
    assert cone.dual_cone_contains(character)
    assert cone.orthogonal_contains(characters.zero())
    assert cone.semigroup_generators().cardinality() == cardinal(2)
    assert sum(coefficients.values(), ZZ.zero()) == ZZ(3)


def test_ray_is_face_and_identity_map_is_fan_compatible() -> None:
    lattice = ZZ.free_module(2)
    fan = RationalPolyhedralFans(lattice)((((1, 0), (0, 1)),))
    cone = fan.maximal_cones()[0]
    ray = cone.faces(1)[0]
    identity = lattice.module_category().Mor(lattice, lattice).identity()

    assert ray.is_face_of(cone)
    assert fan.maximal_cone_containing_image(identity, cone) == cone
    assert fan.is_compatible_with(identity, fan)
