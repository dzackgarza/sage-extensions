r"""Orthogonal groups of definite lattices over ``ZZ`` and over ``QQ``.

For a definite lattice of finite rank over ``ZZ``, ``O(L)`` is finite
(``lean-categories`` ``orthogonalGroup_finite``,
``LeanCategories/Lattices/Valued/Mass.lean:41``).  ``ZZ^2`` with the sum of
squares has ``O = {signed permutation matrices}``, the dihedral group of
order 8, every element of which sends ``e_0`` to one of ``+-e_0, +-e_1``.

Over ``QQ`` the definite plane ``V = <1> + <1>`` is a quadratic space, and
``O(V)`` contains the rotation ``r`` with ``r(e_0) = 3/5 e_0 + 4/5 e_1`` and
``r(e_1) = -4/5 e_0 + 3/5 e_1``.  With ``cos t = 3/5`` and ``sin t = 4/5``:
``cos 2t = -7/25``, ``sin 2t = 24/25``, ``cos 4t = 2 (49/625) - 1 = -527/625``
and ``sin 4t = 2 (24/25)(-7/25) = -336/625``, so
``r^4(e_0) = -527/625 e_0 - 336/625 e_1``.  That is none of ``+-e_0, +-e_1``,
so ``r^4`` is not in the 8-element group of ``ZZ^2``, and ``O(V)`` is not that
group.  No exact computation of ``O(V)`` as a finite group is supplied
(``CAT-01``): each route that computes ``O(L)`` as a finite group asserts its
hypothesis, a definite lattice over ``ZZ``, for ``V``.  Each such refusal
below is paired with the statement it makes over ``ZZ``.
"""

import pytest

from sage_extensions.all import *


def _integral_plane():
    return Lattices(ZZ)(2)


def _rational_plane():
    return Lattices(QQ)(2)


def _rotation(plane):
    r"""The isometry ``r`` of ``<1> + <1>`` over ``QQ`` with cosine ``3/5`` and sine ``4/5``."""
    labels = plane.module_generating_set()
    e0, e1 = plane.module_generators()
    three_fifths = QQ(3) / QQ(5)
    four_fifths = QQ(4) / QQ(5)
    return plane.O()({
        labels[0]: plane.scalar_multiple(three_fifths, e0) + plane.scalar_multiple(four_fifths, e1),
        labels[1]: plane.scalar_multiple(-four_fifths, e0) + plane.scalar_multiple(three_fifths, e1),
    })


def test_the_rational_plane_has_an_isometry_outside_the_group_of_its_integral_span() -> None:
    plane = _rational_plane()
    e0, e1 = plane.module_generators()
    rotation = _rotation(plane)

    assert rotation(e0).q() == 1
    assert rotation(e1).q() == 1
    assert rotation(e0).b(rotation(e1)) == 0
    square = rotation * rotation
    fourth = square * square
    assert fourth(e0) == plane.scalar_multiple(QQ(-527) / QQ(625), e0) + plane.scalar_multiple(QQ(-336) / QQ(625), e1)


def test_only_the_integral_orthogonal_group_is_placed_finite() -> None:
    assert _integral_plane().O() in Groups().Finite()
    assert _rational_plane().O() not in Groups().Finite()


def test_cardinality_is_eight_over_ZZ_and_not_the_integral_count_over_QQ() -> None:
    assert _integral_plane().O().cardinality() == 8
    with pytest.raises(AssertionError):
        _rational_plane().O().cardinality()


def test_enumeration_is_of_the_integral_group_only() -> None:
    integral = _integral_plane()
    e0, e1 = integral.module_generators()
    assert any(g(e0) == e1 and g(e1) == e0 for g in integral.O())
    assert all(g(e0) in (e0, -e0, e1, -e1) for g in integral.O())
    with pytest.raises(AssertionError):
        next(iter(_rational_plane().O()))


def test_generators_are_computed_for_the_integral_group_only() -> None:
    integral = _integral_plane().O()
    assert integral.subgroup(tuple(integral.group_generators())).cardinality() == 8
    with pytest.raises(AssertionError):
        _rational_plane().O().group_generators()


def test_structure_description_is_of_the_integral_group_only() -> None:
    assert _integral_plane().O().structure_description()
    with pytest.raises(AssertionError):
        _rational_plane().O().structure_description()


def test_square_25_splits_into_two_integral_orbits_and_one_rational_orbit() -> None:
    r"""Over ``ZZ`` the 12 vectors of square 25 form the orbits of ``(5,0)`` and ``(3,4)``.

    Signed permutations preserve the multiset of absolute coordinates, so
    ``{0, 5}`` and ``{3, 4}`` are different orbits.  Over ``QQ`` the rotation
    carries ``5 e_0`` to ``3 e_0 + 4 e_1``.
    """
    integral = _integral_plane()
    e0, e1 = integral.module_generators()
    assert integral.vectors_of_square(25).cardinality() == 12
    assert integral.O().vector_orbit_representatives(25).cardinality() == 2
    assert integral.O().vector_equivalence_witness(5 * e0, 3 * e0 + 4 * e1) is None

    rational = _rational_plane()
    f0, f1 = rational.module_generators()
    assert _rotation(rational)(rational.scalar_multiple(QQ(5), f0)) == (
        rational.scalar_multiple(QQ(3), f0) + rational.scalar_multiple(QQ(4), f1)
    )
    fibre = rational.vectors_of_square(25)
    assert rational.scalar_multiple(QQ(3), f0) + rational.scalar_multiple(QQ(4), f1) in fibre
    assert rational.scalar_multiple(QQ(3), f0) + rational.scalar_multiple(QQ(3), f1) not in fibre
    with pytest.raises(AssertionError):
        rational.O().vector_orbit_representatives(25)
    with pytest.raises(AssertionError):
        rational.O().vector_equivalence_witness(rational.scalar_multiple(QQ(5), f0), rational.scalar_multiple(QQ(3), f0) + rational.scalar_multiple(QQ(4), f1))


def test_vector_stabilizers_are_reduced_in_the_integral_group_only() -> None:
    r"""In ``ZZ^2`` the stabilizer of ``e_0`` is ``{1, e_1 -> -e_1}``."""
    integral = _integral_plane()
    e0, e1 = integral.module_generators()
    stabilizer_generators = integral.O().vector_stabilizer_generators(e0)
    assert all(g(e0) == e0 for g in stabilizer_generators)
    assert any(g(e1) == -e1 for g in stabilizer_generators)

    rational = _rational_plane()
    f0, _ = rational.module_generators()
    with pytest.raises(AssertionError):
        rational.O().vector_stabilizer_generators(f0)


def test_reflections_in_the_two_axes_are_conjugate_by_the_swap() -> None:
    r"""``diag(1,-1)`` and ``diag(-1,1)`` are conjugate by the swap ``h`` of ``e_0, e_1``."""
    integral = _integral_plane()
    labels = integral.module_generating_set()
    e0, e1 = integral.module_generators()
    first = integral.O()({labels[0]: e0, labels[1]: -e1})
    second = integral.O()({labels[0]: -e0, labels[1]: e1})
    h = first.equivariant_isometry_to(second)
    assert h * first == second * h

    rational = _rational_plane()
    labels = rational.module_generating_set()
    f0, f1 = rational.module_generators()
    rational_first = rational.O()({labels[0]: f0, labels[1]: -f1})
    rational_second = rational.O()({labels[0]: -f0, labels[1]: f1})
    with pytest.raises(AssertionError):
        rational_first.equivariant_isometry_to(rational_second)


def test_embeddings_into_the_rational_plane_are_not_enumerated_shell_by_shell() -> None:
    r"""``<1>`` embeds in ``ZZ^2`` (``e_0``), found through the finite shell of square 1.

    Into the rational plane, the identity shows ``Emb(V, V)`` is nonempty
    without enumerating a shell.
    """
    integral = _integral_plane()
    assert Lattices(ZZ)(1).Emb(integral).is_empty() is False

    rational = _rational_plane()
    assert rational.Emb(rational).is_empty() is False
    with pytest.raises(AssertionError):
        next(iter(rational.Emb(rational)))
