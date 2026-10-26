r"""Invariant curves on projective plane generate its toric cycle group."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_invariant_curve_group_and_cycle_class_map() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    invariant_curves = plane.torus_invariant_cycle_group(1)
    cycle_class = plane.torus_invariant_cycle_class_map(1)

    assert invariant_curves.module_rank() == 3
    assert cycle_class.domain() is invariant_curves
    assert cycle_class.codomain() is plane.chow_group(1)
