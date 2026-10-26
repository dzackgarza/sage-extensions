r"""Line-bundle cohomology retains its scheme, divisor, degree, and vector-space structure."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperplane_sections_on_projective_plane() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    cohomology = plane.line_bundle_cohomology(divisor, 0)

    assert cohomology in LineBundleCohomologySpaces(QQ)
    assert cohomology.cohomology_scheme() is plane
    assert cohomology.cohomology_divisor() == divisor
    assert cohomology.cohomological_degree() == 0
    assert cohomology.dimension() == 3
