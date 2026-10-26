r"""Cyclotomic decompositions of finite-order isometries and their gluing."""

import pytest

from sage_extensions.all import *


def cyclic_permutation_of_Z3():
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    labels = lattice.module_generating_set()
    first, second, third = lattice.module_generators()
    return lattice.O()({labels[0]: second, labels[1]: third, labels[2]: first})


def negation_of(lattice):
    return lattice.O()(
        {
            label: -lattice.module_generator(label)
            for label in lattice.module_generating_set()
        }
    )


def test_the_three_cycle_on_Z3_splits_into_Phi1_and_Phi3_parts_glued_with_index_three() -> None:
    r"""The 3-cycle fixes Z(1,1,1) (norm 3) and acts with order 3 on the
    sum-zero sublattice A2 (discriminant 3); their sum has index
    sqrt(3 * 3 / 1) = 3 in Z^3.  A reflection of A2 does not commute with an
    order-3 rotation of A2 (the dihedral group of order 6 is nonabelian)."""
    isometry = cyclic_permutation_of_Z3()
    decomposition = isometry.cyclotomic_decomposition(3)

    assert Set(decomposition.nonzero_divisors()) == Set((1, 3))
    assert all(divisor.parent() is ZZ for divisor in decomposition.nonzero_divisors())
    assert decomposition.summand(1).module_rank() == 1
    assert decomposition.summand(3).module_rank() == 2
    assert decomposition.index() == 3
    assert decomposition.gluing_quotient().cardinality() == 3
    assert decomposition.gluing_subgroup().cardinality() == 3

    restrictions = decomposition.component_isometries()
    assert restrictions[1] == decomposition.summand(1).O().one()
    assert restrictions[3] != decomposition.summand(3).O().one()
    for divisor in decomposition.nonzero_divisors():
        inclusion = decomposition.summand(divisor).inclusion()
        assert inclusion * restrictions[divisor] == isometry * inclusion

    cyclotomic = decomposition.summand(3)
    root_reflection = cyclotomic.reflection(cyclotomic.basis_vector(0))
    assert root_reflection in cyclotomic.O()
    assert root_reflection not in decomposition.component_centralizers()[3]


def test_cyclotomic_component_tuple_lifts_exactly_when_it_preserves_the_glue() -> None:
    isometry = cyclic_permutation_of_Z3()
    decomposition = isometry.cyclotomic_decomposition(3)
    restrictions = decomposition.component_isometries()

    lifted = decomposition.lift_component_isometries(
        {1: restrictions[1], 3: restrictions[3]}
    )

    assert lifted == isometry
    assert lifted in decomposition.centralizer_group()

    incompatible = {
        1: decomposition.summand(1).O().one(),
        3: negation_of(decomposition.summand(3)),
    }
    assert incompatible[3] in decomposition.component_centralizers()[3]
    assert not decomposition.component_isometries_extend(incompatible)


def test_the_centralizer_of_minus_one_on_Z2_is_the_signed_permutation_group_of_order_8() -> None:
    r"""O(I_2) is the signed permutation group (Z/2)^2 x| S_2 of order 8, and -1
    is central in it, so its centralizer is all of O(I_2)."""
    lattice = Lattices(ZZ)([[1, 0], [0, 1]])
    minus_one = negation_of(lattice)

    assert lattice.O().cardinality() == 8
    assert minus_one.centralizer_group().cardinality() == 8
    first, second = lattice.module_generators()
    swap = lattice.O()({0: second, 1: first})
    assert swap in minus_one.centralizer_group()
    assert swap(first) == second


def swap_of_two_hyperbolic_planes():
    r"""``U + U`` with the isometry exchanging its two summands."""
    lattice = NamedLattices.U + NamedLattices.U
    labels = lattice.module_generating_set()
    e1, f1, e2, f2 = lattice.module_generators()
    return lattice, lattice.O()({labels[0]: e2, labels[1]: f2, labels[2]: e1, labels[3]: f1})


def test_the_swap_of_two_hyperbolic_planes_retains_its_owned_cyclotomic_sum_and_glue() -> None:
    r"""The swap ``f`` of ``U + U`` has ``ker(f - 1)`` the diagonal copy and
    ``ker(f + 1)`` the antidiagonal copy of ``U``, each with the form doubled:
    ``U(2)``, of rank two and discriminant group of order ``4``.  ``U + U`` is
    unimodular, so ``[L : L_1 + L_2]^2 = det(L_1) det(L_2) = 16`` and the
    index is ``4``."""
    lattice, swap = swap_of_two_hyperbolic_planes()
    decomposition = swap.cyclotomic_decomposition(2)

    assert lattice.module_generating_set() == Sets.Δ[3]
    assert Set(decomposition.nonzero_divisors()) == Set((1, 2))
    assert all(divisor.parent() is ZZ for divisor in decomposition.nonzero_divisors())
    orthogonal_sum = decomposition.orthogonal_sum()
    sum_inclusion = decomposition.orthogonal_sum_inclusion()
    restrictions = decomposition.component_isometries()
    for position, divisor in enumerate(decomposition.nonzero_divisors()):
        summand = decomposition.summand(divisor)
        assert summand.module_rank() == 2
        assert summand.discriminant_group().cardinality() == 4
        for generator in summand.module_generators():
            assert sum_inclusion(orthogonal_sum.injection(position)(generator)) == summand.inclusion()(generator)
            assert summand.inclusion()(restrictions[divisor](generator)) == swap(summand.inclusion()(generator))
        for other_position, other_divisor in enumerate(decomposition.nonzero_divisors()):
            other = decomposition.summand(other_divisor)
            projection_triangle = orthogonal_sum.projection(position) * orthogonal_sum.injection(other_position)
            expected = other.module_category().Mor(other, summand).identity() if position == other_position else other.module_category().Mor(other, summand).zero()
            for generator in other.module_generators():
                assert projection_triangle(generator) == expected(generator)
    assert decomposition.index() == 4
    assert decomposition.gluing_quotient().cardinality() == 4
    assert decomposition.gluing_subgroup().cardinality() == 4


def test_the_swap_of_two_hyperbolic_planes_has_a_glued_centralizer_containing_f_and_minus_one() -> None:
    r"""The swap and negation commute with the swap, and the component-glued
    generators generate a subgroup of its centralizer containing both."""
    lattice, swap = swap_of_two_hyperbolic_planes()
    centralizer = lattice.O().centralizer(swap)
    group_generators = tuple(centralizer.group_generators())
    assert all(generator * swap == swap * generator for generator in group_generators)
    generated = lattice.O().subgroup(group_generators)
    assert swap in generated
    assert negation_of(lattice) in generated


def test_the_centralizer_of_minus_one_on_E8_is_all_of_O_E8() -> None:
    r"""``-1`` is central in ``O(E8(-1)) = W(E8)``, of order ``696729600``
    (Conway--Sloane, *Sphere Packings, Lattices and Groups*, ch. 4, sect. 8.1),
    so its centralizer is the whole group."""
    lattice = NamedLattices.E8
    minus_one = negation_of(lattice)

    group_generators = tuple(lattice.O().centralizer(minus_one).group_generators())
    assert all(generator * minus_one == minus_one * generator for generator in group_generators)
    assert lattice.O().subgroup(group_generators).cardinality() == 696729600


def test_an_indefinite_hermitian_component_asserts_its_frontier() -> None:
    r"""The Coxeter rotation of ``A2`` has order three and fixes no vector,
    so on ``A2 + A2(-1)``, of signature ``(2, 2)``, the rotation of both
    summands has the single cyclotomic summand ``ker Phi_3 = L``: an
    indefinite hermitian lattice over ``ZZ[zeta_3]``, whose unitary group has
    no generating route, so reading its generators asserts."""
    lattice = Lattices(ZZ)([[2, -1], [-1, 2]]) + Lattices(ZZ)([[-2, 1], [1, -2]])
    labels = lattice.module_generating_set()
    a1, a2, b1, b2 = lattice.module_generators()
    rotation = lattice.O()({labels[0]: a2, labels[1]: -a1 - a2, labels[2]: b2, labels[3]: -b1 - b2})

    with pytest.raises(AssertionError):
        lattice.O().centralizer(rotation).group_generators()
