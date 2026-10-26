r"""Principal toric divisors restrict through the affine-chart divisor map."""

from sage_extensions.all import *  # noqa: F401,F403


def _projective_plane_with_maximal_cone():
    fan = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan()
    return fan.toric_variety(QQ), fan.maximal_cones()[0]


def test_local_character_divisor_map_has_the_affine_chart_divisor_group_as_codomain() -> None:
    plane, cone = _projective_plane_with_maximal_cone()
    local_principal = plane.local_character_divisor_morphism(cone)

    assert local_principal.domain() is plane.character_lattice()
    assert local_principal.codomain() is plane.local_divisor_group(cone)


def test_principal_divisor_restricts_to_the_local_character_divisor() -> None:
    plane, cone = _projective_plane_with_maximal_cone()
    character = plane.character_lattice()((1, 0))

    assert (
        plane.local_divisor_restriction(
            plane.principal_divisor_of_character(character),
            cone,
        )
        == plane.local_character_divisor_morphism(cone)(character)
    )
