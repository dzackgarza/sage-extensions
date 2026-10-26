r"""A point blowup exposes its blowdown and the standard Picard intersection form."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_point_blowup_blowdown_is_the_blowup_morphism() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    blowup = ProjectivePointBlowups(QQ)(plane.point_morphism((1, 1, 1)))

    assert blowup.blowdown() == blowup.blowup_morphism()


def test_projective_point_blowup_picard_pairing_has_signature_one_one() -> None:
    plane = ProjectiveSpaces(QQ)(2, names=("x", "y", "z"))
    blowup = ProjectivePointBlowups(QQ)(plane.point_morphism((1, 1, 1)))
    pairing = blowup.picard_intersection_pairing()
    H = blowup.hyperplane_picard_class()
    E = blowup.exceptional_picard_class()

    assert pairing(H, H) == 1
    assert pairing(E, E) == -1
    assert pairing(H, E) == pairing(E, H) == 0
