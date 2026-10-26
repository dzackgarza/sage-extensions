r"""Torus-invariant curves of P^2 form an algebraic cycle group over ZZ."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_curve_cycles_are_algebraic_cycles() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cycles = plane.torus_invariant_cycle_group(1)

    assert cycles in AlgebraicCycleGroups(ZZ)
    assert cycles.cycle_scheme() is plane
    assert cycles.cycle_dimension() == 1
    assert cycles.cycle_codimension() == 1
