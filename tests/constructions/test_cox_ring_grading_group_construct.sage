r"""The Cox ring of (mathbf P^2) is graded by its divisor class group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_cox_ring_grading_group_is_class_group() -> None:
    plane = (
        RationalPolyhedralFans(ZZ.free_module(2))
        .projective_space_fan()
        .toric_variety(QQ)
    )
    cox = plane.cox_ring()

    assert cox.grading_group() is plane.class_group()
    assert cox.grading_group().module_rank() == cardinal(1)
