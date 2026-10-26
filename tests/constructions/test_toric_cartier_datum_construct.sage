r"""A principal toric divisor has the expected local Cartier character."""

from sage_extensions.all import *  # noqa: F401,F403


def test_principal_divisor_cartier_datum_is_the_negative_character() -> None:
    fan = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan()
    plane = fan.toric_variety(QQ)
    cone = fan.maximal_cones()[0]
    character = plane.character_lattice()((1, 0))
    divisor = plane.principal_divisor_of_character(character)

    assert plane.cartier_datum(divisor, cone) == -character
