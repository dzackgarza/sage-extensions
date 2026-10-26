r"""Cohomology of the toric surfaces ``P^2`` and ``P^1 x P^1``.

``P^2`` is the toric variety of the fan in ``ZZ^2`` with rays ``e_1, e_2,
-e_1 - e_2``; ``P^1 x P^1`` that of the fan with rays ``±e_1, ±e_2``.  For a
torus-invariant divisor ``D``, ``H^0(X, O(D))`` is graded by the character
lattice with one-dimensional pieces exactly at the lattice points of the
polytope ``P_D`` (Cox--Little--Schenck, *Toric Varieties*, Prop. 4.3.3).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _projective_plane():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans(((1, 0), (0, 1), (-1, -1)), ((0, 1), (1, 2), (2, 0))).toric_variety(QQ)


def _p1_times_p1():
    fans = RationalPolyhedralFans(ZZ.free_module(2))
    return fans(((1, 0), (0, 1), (-1, 0), (0, -1)), ((0, 1), (1, 2), (2, 3), (3, 0))).toric_variety(QQ)


def test_the_weight_zero_piece_of_sections_of_a_torus_invariant_line_on_p2_is_one_dimensional() -> None:
    r"""``0 ∈ P_D`` for the effective divisor ``D`` of a torus-invariant line, so ``H^0(O(D))_0`` has dimension 1."""
    plane = _projective_plane()
    divisor = plane.hyperplane_divisor()

    assert plane.weight_cohomology(divisor, plane.character_lattice().zero(), 0).dimension() == 1


def test_a_weight_outside_the_polytope_of_a_line_on_p2_has_no_sections() -> None:
    r"""``3 e_1^*`` lies outside ``P_D`` for each of the three torus-invariant lines ``D``, so that piece of ``H^0`` is 0."""
    plane = _projective_plane()
    divisor = plane.hyperplane_divisor()
    characters = plane.character_lattice()
    outside = 3 * characters((1, 0))

    assert plane.weight_cohomology(divisor, outside, 0).dimension() == 0


def test_sections_of_o_1_on_p2_are_three_dimensional_with_one_weight_per_lattice_point() -> None:
    r"""``h^0(P^2, O(1)) = 3``: the polytope of a line is a unimodular triangle with three lattice points."""
    plane = _projective_plane()
    cohomology = plane.line_bundle_cohomology(plane.hyperplane_divisor(), 0)

    assert cohomology.dimension() == 3
    assert cohomology.cohomology_weight_support().cardinality() == 3
    for weight in cohomology.cohomology_weight_support():
        assert cohomology.cohomology_weight_piece(weight).dimension() == 1


def test_the_integral_cohomology_of_p2_has_ranks_1_0_1_0_1() -> None:
    r"""``H^*(P^2(CC), ZZ) = ZZ[h]/(h^3)`` with ``deg h = 2`` (Hatcher, *Algebraic Topology*, Thm. 3.12)."""
    plane = _projective_plane()

    assert [plane.integral_singular_cohomology(k).rank() for k in range(5)] == [1, 0, 1, 0, 1]
    assert all(plane.integral_singular_cohomology(k).is_torsion_free() for k in range(5))


def test_the_cycle_class_of_a_line_generates_h2_of_p2() -> None:
    r"""``cl: CH^1(P^2) = ZZ[L] -> H^2(P^2, ZZ) = ZZ`` is an isomorphism, so ``cl(L)`` generates ``H^2``.

    Derivation: if ``cl(L) = k g`` for a generator ``g`` then
    ``cl(L)^2 = k^2 g^2 = deg(L · L) = 1``, so ``k = ±1``.
    """
    plane = _projective_plane()
    cycle_class = plane.cycle_class_isomorphism(1)
    line = plane.chow_group(1)(plane.hyperplane_divisor())
    c = cycle_class.forward()(line)

    assert cycle_class.forward().is_bijective()
    assert plane.middle_cohomology_form().b(c, c) == 1


def test_the_intersection_form_on_h2_of_p2_is_the_unimodular_form_1() -> None:
    r"""On ``H^2(P^2, ZZ) = ZZ h``, ``h · h = 1``: two lines meet in one point."""
    plane = _projective_plane()
    formed = plane.middle_cohomology_form()

    assert formed.rank() == 1
    assert formed.determinant() == 1
    assert formed.is_unimodular()


def test_the_intersection_form_on_h2_of_p1_times_p1_is_the_hyperbolic_plane() -> None:
    r"""``H^2(P^1 x P^1, ZZ)`` with the intersection form is ``U``: rank 2, even, unimodular, determinant ``-1``.

    Derivation: fibre classes ``f_1, f_2`` with ``f_i^2 = 0`` and ``f_1 f_2 = 1``.
    """
    formed = _p1_times_p1().middle_cohomology_form()

    assert formed.rank() == 2
    assert formed.is_unimodular()
    assert formed.determinant() == -1
    assert formed.is_even()
    assert formed.signature_pair() == (1, 1)


def test_p2_is_simply_connected() -> None:
    r"""``pi_1(P^2(CC)) = 1``: ``P^2(CC)`` is a CW complex with cells in dimensions 0, 2, 4 only (Hatcher, Example 0.6)."""
    plane = _projective_plane()
    cone = next(iter(plane.fan().maximal_cones()))

    assert SmoothCompleteRationalToricSchemes(QQ)(plane).fundamental_group(cone).cardinality() == 1


def test_the_hodge_diamond_of_p2_is_diagonal() -> None:
    r"""``h^{p,q}(P^2) = 1`` for ``p = q ≤ 2`` and ``0`` otherwise; ``h^{2,0} = h^0(K) = 0``."""
    hodge = _projective_plane().hodge_structure()

    assert hodge.is_pure()
    assert hodge.hodge_number(0, 0) == 1
    assert hodge.hodge_number(1, 1) == 1
    assert hodge.hodge_number(2, 2) == 1
    assert hodge.hodge_number(2, 0) == 0
    assert hodge.hodge_number(1, 0) == 0


def test_p1_times_p1_has_h11_equal_to_two() -> None:
    r"""``h^{1,1}(P^1 x P^1) = b_2 = 2`` by Künneth."""
    assert _p1_times_p1().hodge_structure().hodge_number(1, 1) == 2
