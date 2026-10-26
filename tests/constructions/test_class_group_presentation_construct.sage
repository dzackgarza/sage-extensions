r"""A divisor class group retains the scheme and principal-divisor map presenting it."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_class_group_retains_its_presentation() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    classes = plane.class_group()
    principal = classes.principal_to_weil_morphism()

    assert classes.class_group_scheme() is plane
    assert principal.codomain().divisor_scheme() is plane
