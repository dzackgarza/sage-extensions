r"""Log pairs and the toric boundary.

Cox--Little--Schenck, *Toric Varieties*, Thm. 8.2.3: the canonical divisor of
a toric variety is minus the sum of the torus-invariant prime divisors, so the
toric boundary is anticanonical and the toric log pair is log Calabi--Yau.
"""

from sage_extensions.all import *

# One rank-two cocharacter lattice for the whole file: a free module is a
# fresh object on every construction, so building it twice would give two
# unrelated categories of fans.
_PLANE_FANS = RationalPolyhedralFans(ZZ.free_module(2))


def _projective_plane():
    return _PLANE_FANS.projective_space_fan().toric_variety(QQ)






def test_the_toric_canonical_divisor_is_minus_the_boundary() -> None:
    plane = _projective_plane()

    assert plane.canonical_divisor() == -plane.toric_boundary_divisor()
    assert plane.canonical_divisor() != plane.toric_boundary_divisor()


def test_the_toric_log_pair_is_log_calabi_yau() -> None:
    plane = _projective_plane()
    pair = plane.log_pair()

    assert pair in LogPairs(QQ)
    assert pair in ToricLogPairs(QQ)
    assert pair in Schemes(QQ)
    assert pair.scheme_base_ring() is QQ
    assert pair.log_scheme() is plane
    assert pair.boundary_divisor() == plane.toric_boundary_divisor()
    assert pair.is_toric_boundary()
    assert pair.log_canonical_divisor() == pair.boundary_divisor_group().zero()
    assert pair.is_log_calabi_yau()


def test_a_smaller_boundary_is_not_log_calabi_yau() -> None:
    r"""Dropping one of the three lines leaves ``K_X + Delta = -D_rho``, so the
    pair is no longer log Calabi--Yau and the predicate is not vacuous."""

    plane = _projective_plane()
    rays = plane.fan().cones(1)
    group = plane.torus_invariant_divisor_group()
    partial = group.zero()
    for ray in rays:
        if ray != rays[0]:
            partial = partial + plane.torus_invariant_prime_divisor(ray)
    pair = plane.log_pair(partial)

    assert not pair.is_toric_boundary()
    assert not pair.is_log_calabi_yau()
    assert pair.log_canonical_divisor() == -plane.torus_invariant_prime_divisor(
        rays[0]
    )


def test_the_hirzebruch_surface_has_four_invariant_divisors() -> None:
    surface = _PLANE_FANS.hirzebruch_surface_fan(2).toric_variety(QQ)

    assert surface.torus_invariant_divisor_group().module_generating_set().cardinality() == 4
    assert surface.log_pair().is_log_calabi_yau()
