r"""The standard affine charts jointly cover projective space."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_standard_affine_embeddings_cover() -> None:
    plane = ProjectiveSpaces(QQ)(2)
    atlas = plane.standard_affine_atlas()

    assert plane.is_covered_by_open_immersions(atlas.embeddings())
