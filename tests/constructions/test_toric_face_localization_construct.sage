r"""A face inclusion induces the corresponding affine-chart open immersion."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_face_localization_has_the_expected_affine_chart_endpoints() -> None:
    fan = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan()
    plane = fan.toric_variety(QQ)
    cone = fan.maximal_cones()[0]
    face = cone.faces(1)[0]
    localization = plane.face_localization(face, cone)

    assert localization.domain() is plane.affine_chart(face)
    assert localization.codomain() is plane.affine_chart(cone)
