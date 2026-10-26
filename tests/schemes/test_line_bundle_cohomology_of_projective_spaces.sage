r"""Cohomology of line bundles on ``P^1`` and ``P^2`` and of quasi-coherent sheaves on affines.

Sources: Hartshorne, *Algebraic Geometry*, Thm. III.5.1 (checked): for ``X = P^r_A``,
``bigoplus_n H^0(X, O(n)) = A[x_0, ..., x_r]``, ``H^i(X, O(n)) = 0`` for ``0 < i < r``, and
``H^0(O(n)) x H^r(O(-n-r-1)) -> H^r(O(-r-1)) = A`` is a perfect pairing.  So
``h^0(P^r, O(n)) = binom(n + r, r)`` and ``h^r(P^r, O(n)) = h^0(P^r, O(-n-r-1))``.  Stacks
Project, Tag 01XB (Lemma 30.2.2, checked): ``H^p(U, F) = 0`` for ``p > 0`` on an affine ``U``.

``P^1`` and ``P^2`` are built as toric varieties of their fans, a line bundle ``O(n)`` being
``O(n D)`` for a torus-invariant prime divisor ``D``.
"""

from sage_extensions.all import *


def _toric_projective_space(rank):
    space = RationalPolyhedralFans(ZZ.free_module(rank)).projective_space_fan().toric_variety(QQ)
    return space, space.torus_invariant_prime_divisor(space.fan().cones(1)[0])


def test_sections_of_o_2_on_the_projective_line_are_the_three_quadratic_monomials() -> None:
    r"""``h^0(P^1, O(2)) = binom(3, 1) = 3``."""
    line, point = _toric_projective_space(1)

    assert line.line_bundle_cohomology(2 * point, 0).dimension() == 3


def test_o_minus_2_on_the_projective_line_has_one_dimensional_h1() -> None:
    r"""``h^1(P^1, O(-2)) = h^0(P^1, O(0)) = 1`` and ``h^0(P^1, O(-2)) = 0``."""
    line, point = _toric_projective_space(1)

    assert line.line_bundle_cohomology(-2 * point, 1).dimension() == 1
    assert line.line_bundle_cohomology(-2 * point, 0).dimension() == 0


def test_the_projective_plane_has_no_middle_cohomology_of_line_bundles() -> None:
    r"""``H^1(P^2, O(n)) = 0`` for every ``n``; checked for ``n = -1, 0, 1``."""
    plane, line = _toric_projective_space(2)

    for multiple in (-1, 0, 1):
        assert plane.line_bundle_cohomology(multiple * line, 1).dimension() == 0


def test_the_canonical_bundle_of_the_projective_plane_has_one_dimensional_h2() -> None:
    r"""``O(-3) = omega_{P^2}`` and ``h^2(P^2, O(-3)) = h^0(P^2, O) = 1``."""
    plane, line = _toric_projective_space(2)

    assert plane.line_bundle_cohomology(plane.canonical_divisor(), 2).dimension() == 1
    assert plane.line_bundle_cohomology(-3 * line, 2).dimension() == 1


def test_standard_twists_on_the_projective_plane_have_the_binomial_number_of_sections() -> None:
    r"""``h^0(P^2, O(d)) = binom(d + 2, 2)``: ``O(3)`` has 10 sections, via ``ProjectiveSpaces``."""
    plane = ProjectiveSpaces(QQ)(2)

    assert plane.O(3).global_sections().dimension() == 10


def test_a_quasi_coherent_sheaf_on_an_affine_line_has_no_higher_cohomology() -> None:
    r"""``H^0(A^1, M~) = M`` and ``H^1(A^1, M~) = 0`` for ``M = Q[x]^2`` (Stacks Tag 01XB)."""
    ring = QQ["x"]
    line = AffineSchemes(QQ)(ring)
    sheaf = QuasiCoherentSheaves(line).associated_sheaf(ring.free_module(2))

    assert sheaf.sheaf_cohomology(1).is_zero()


def test_the_hodge_numbers_of_the_projective_plane_are_those_of_its_cohomology_ring() -> None:
    r"""``H^*(P^2) = Z[h]/(h^3)`` is spanned by algebraic classes, so ``h^{p,q} = 1`` for
    ``p = q <= 2`` and ``0`` otherwise."""
    plane, line = _toric_projective_space(2)
    hodge = plane.hodge_structure()

    assert hodge.is_pure()
    assert hodge.hodge_number(1, 0) == 0
    assert hodge.hodge_number(2, 0) == 0
    assert hodge.hodge_number(0, 0) == 1
    assert hodge.hodge_number(1, 1) == 1
    assert hodge.hodge_number(2, 2) == 1
