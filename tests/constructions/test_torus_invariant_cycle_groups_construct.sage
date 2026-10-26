r"""The three invariant lines of P^2 freely generate its invariant curve cycles."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projective_plane_torus_invariant_curve_cycles() -> None:
    plane = RationalPolyhedralFans(ZZ.free_module(2)).projective_space_fan().toric_variety(QQ)
    cycles = plane.torus_invariant_cycle_group(1)

    assert cycles in TorusInvariantCycleGroups(ZZ)
    assert cycles.module_rank() == 3
    assert cycles.module_generating_set().cardinality() == cardinal(3)
