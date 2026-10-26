r"""Common refinements of distinguished affine covers retain their refinement maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_common_refinement_maps_to_both_covers() -> None:
    line = AffineSpaces(QQ)(1, names=("x",))
    ring = line.coordinate_algebra()
    x = ring.algebra_generator("x")
    covers = DistinguishedAffineCovers(line)
    two_chart = line.distinguished_open_cover(x, ring.one() - x)
    identity_cover = covers.an_object()
    span = two_chart.common_refinement(identity_cover)
    left = span.left_leg()
    right = span.right_leg()

    assert left.fine_cover() is span.apex()
    assert left.coarse_cover() is two_chart
    assert right.fine_cover() is span.apex()
    assert right.coarse_cover() is identity_cover
    assert left.ambient_scheme() is line
    assert right.ambient_scheme() is line
