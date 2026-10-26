r"""Archive reconciliation for intersection and cohomology data on ``P1 x P1``."""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/tests/framework/test_chow_cohomology_intersections.sage",
    "live_owner": "tests/schemes/test_framework_chow_cohomology_archive.py",
    "disposition": "reconciled-live-owner",
}


def _quadric_surface():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans.hirzebruch_surface_fan(0).toric_variety(QQ)


def _hyperbolic_picard_pair(surface):
    pairing = surface.picard_intersection_pairing()
    projection = surface.torus_invariant_cartier_class_projection()
    divisors = tuple(
        surface.torus_invariant_prime_divisor(ray)
        for ray in surface.fan().cones(1)
    )
    classes = tuple(projection(divisor) for divisor in divisors)
    return pairing, next(
        (left, right)
        for left in classes
        for right in classes
        if pairing(left, left) == 0
        and pairing(right, right) == 0
        and pairing(left, right) == 1
        and pairing(right, left) == 1
    )


def test_product_of_lines_intersection_pairing_recovers_bidegree_arithmetic() -> None:
    surface = _quadric_surface()
    pairing, (left, right) = _hyperbolic_picard_pair(surface)

    four_four = 4 * left + 4 * right
    one_two = left + 2 * right
    two_one = 2 * left + right

    assert pairing(four_four, one_two) == 12
    assert pairing(four_four, two_one) == 12
    assert pairing(four_four, four_four) == 32
    assert pairing(two_one, two_one) == 4


def test_product_of_lines_O44_and_canonical_cohomology_have_classical_dimensions() -> None:
    surface = _quadric_surface()
    four_four = 2 * surface.toric_boundary_divisor()
    positive = surface.line_bundle_cohomology_dimensions(four_four)
    canonical = surface.line_bundle_cohomology_dimensions(surface.canonical_divisor())

    assert tuple(int(value) for value in positive) == (25, 0, 0)
    assert tuple(int(value) for value in canonical) == (0, 0, 1)
