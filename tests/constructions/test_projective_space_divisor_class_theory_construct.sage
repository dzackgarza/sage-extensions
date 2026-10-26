r"""For projective space over a field, Picard and divisor class groups agree."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_picard_to_class_group_is_an_isomorphism() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    comparison = plane.picard_to_class_group_morphism()

    assert comparison.domain() is plane.picard_group()
    assert comparison.codomain() is plane.class_group()
    assert comparison(plane.picard_group().module_generator("O(1)")) == plane.class_group().module_generator("H")
