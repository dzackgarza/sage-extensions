r"""The hyperplane system on toric projective plane gives its canonical projective map."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_hyperplane_map_is_the_complete_linear_system_map() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    system = plane.complete_linear_system(divisor)
    morphism = plane.associated_projective_morphism(divisor)

    assert morphism == system.associated_morphism()
    assert morphism.domain() is plane
    assert morphism.codomain() is system
