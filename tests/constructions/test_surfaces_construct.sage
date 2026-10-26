r"""Affine and projective planes over fields are surfaces."""

from sage_extensions.all import *  # noqa: F401,F403


def test_affine_and_projective_planes_are_surfaces(field) -> None:
    affine_plane = AffineSpaces(field)(2)
    projective_plane = ProjectiveSpaces(field)(2)
    hyperplane = projective_plane.picard_group().hyperplane_class()
    pairing = projective_plane.picard_intersection_pairing()

    assert affine_plane in Surfaces(field)
    assert projective_plane in Surfaces(field)
    assert Schemes(field).Projective().is_subcategory(Schemes(field).Proper())
    assert ProjectiveSurfaces(field).is_subcategory(ProperSurfaces(field))
    assert affine_plane not in ProperSurfaces(field)
    assert projective_plane in ProperSurfaces(field)
    assert projective_plane in ProjectiveSurfaces(field)
    assert pairing(hyperplane, hyperplane) == 1
    assert projective_plane.is_del_pezzo()
    assert DelPezzoSurfaces(projective_plane.scheme_base_ring())(projective_plane).del_pezzo_degree() == 9
    assert affine_plane.dimension() == 2
    assert projective_plane.dimension() == 2
