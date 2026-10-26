r"""The section ring of O(1) on P^2 has degree-one dimension three."""

from sage_extensions.all import *  # noqa: F401,F403


def test_hyperplane_section_ring_of_projective_plane() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    divisor = plane.hyperplane_divisor()
    ring = plane.section_ring(divisor)

    assert ring in SectionRings(QQ)
    assert ring.section_scheme() is plane
    assert ring.section_divisor() == divisor
    assert ring.graded_piece(1).module_rank() == 3
    assert ring.graded_piece(2).module_rank() == 6
