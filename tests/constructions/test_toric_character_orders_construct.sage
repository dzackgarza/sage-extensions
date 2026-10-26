r"""A toric character's divisor multiplicities are its pairings with ray generators."""

from sage_extensions.all import *  # noqa: F401,F403


def _projective_plane_character_and_ray():
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    character = plane.character_lattice()((1, 0))
    ray = plane.fan().cones(1)[0]
    return plane, character, ray


def test_character_order_along_prime_divisor_is_the_lattice_pairing() -> None:
    plane, character, ray = _projective_plane_character_and_ray()

    assert plane.order_of_character_along_prime_divisor(
        character,
        ray,
    ) == plane.character_cocharacter_pairing()(character, ray.rays()[0])


def test_principal_divisor_multiplicity_is_the_character_order() -> None:
    plane, character, ray = _projective_plane_character_and_ray()
    divisor = plane.principal_divisor_of_character(character)

    assert plane.weil_multiplicity(
        divisor,
        ray,
    ) == plane.order_of_character_along_prime_divisor(character, ray)
