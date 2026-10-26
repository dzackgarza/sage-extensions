r"""The primitive extension cut out by a lattice isometry, and its centralizer data.

The cited specimen is the Enriques involution on the K3 lattice: its invariant
lattice is ``U(2) + E8(-2)``, two-elementary of type ``(10, 10, 0)``, and its
coinvariant lattice is ``T_En`` of rank twelve (Barth--Peters--Van de Ven,
*Compact Complex Surfaces*, ch. VIII; Nikulin's classification of
two-elementary involutions).  Both discriminant groups then have order
``2^10``, and since the K3 lattice is unimodular the glue subgroup is all of
``A_{S_En}``, so the orthogonal sum has index ``2^10`` in the K3 lattice.

The odd specimen is the cyclic permutation of the coordinates of ``I_3``.  Its
invariant lattice is the diagonal, of square three, and its coinvariant
lattice is the rank-two root lattice orthogonal to that diagonal.  ``I_3`` is
odd while that coinvariant summand is even, so the glue of this extension is
an anti-isometry of the ``QQ/ZZ``-valued bilinear discriminant forms, and the
same criterion and the same assembly must answer there as in the even case.
"""

from sage_extensions.all import *


def _hyperbolic_swap():
    lattice = NamedLattices.U
    first, second = lattice.module_generators()[0], lattice.module_generators()[1]
    return lattice, lattice.Aut()({0: second, 1: first})


def test_the_swap_of_the_hyperbolic_plane_glues_two_rank_one_lattices() -> None:
    lattice, swap = _hyperbolic_swap()
    first, second = lattice.module_generators()[0], lattice.module_generators()[1]
    assert swap * swap == lattice.Aut().one()

    extension = swap.primitive_extension()
    assert extension.lattice is lattice
    assert extension.invariant.module_rank() == 1
    assert extension.orthogonal_complement.module_rank() == 1
    assert extension.acts_as_negation_on_coinvariants()

    invariant_vector = extension.invariant.embedded_module_generators()[
        extension.invariant.module_generating_set()[0]
    ]
    coinvariant_vector = extension.orthogonal_complement.embedded_module_generators()[
        extension.orthogonal_complement.module_generating_set()[0]
    ]
    assert invariant_vector.q() == 2
    assert coinvariant_vector.q() == -2
    assert lattice.b(invariant_vector, coinvariant_vector) == 0
    assert swap(invariant_vector) == invariant_vector
    assert swap(coinvariant_vector) == -coinvariant_vector

    # A_{Z(e+f)} and A_{Z(e-f)} both have order two and U is unimodular, so
    # the glue subgroup is the whole of the first and the index is two.
    assert extension.index() == 2
    assert extension.invariant_gluing_subgroup().cardinality() == 2
    assert extension.glue().domain() is extension.invariant_gluing_subgroup()
    extension_inclusion = extension.orthogonal_sum_inclusion()
    extension_generators = tuple(extension_inclusion.domain().module_generators())
    assert extension_inclusion.codomain() is lattice
    assert extension_inclusion.index() == 2
    assert extension_inclusion(extension_generators[0]) == invariant_vector
    assert extension_inclusion(extension_generators[1]) == coinvariant_vector
    assert invariant_vector in (first + second, -(first + second))
    assert coinvariant_vector in (first - second, second - first)


def test_the_enriques_involution_glues_S_En_to_T_En_with_index_1024() -> None:
    involution = Involutions.I_En
    extension = involution.primitive_extension()

    assert extension.lattice is NamedLattices.LK3
    assert extension.invariant.module_rank() == 10
    assert extension.orthogonal_complement.module_rank() == 12
    assert extension.acts_as_negation_on_coinvariants()
    assert (
        extension.orthogonal_complement.inclusion()
        .domain()
        .is_isometric(NamedLattices.TEn)
    )

    assert extension.invariant.discriminant_group().cardinality() == 1024
    assert extension.orthogonal_complement.discriminant_group().cardinality() == 1024
    assert extension.index() == 1024
    assert extension.invariant_gluing_subgroup().cardinality() == 1024


def test_the_enriques_cyclotomic_summands_are_the_two_eigen_sublattices() -> None:
    involution = Involutions.I_En

    assert involution.cyclotomic_summand(1).module_rank() == 10
    assert involution.cyclotomic_summand(2).module_rank() == 12
    assert involution.cyclotomic_summand(3).module_rank() == 0


def _a2_diagram_involution():
    r"""Return ``A2`` with the involution swapping its two simple roots.

    The Gram matrix of ``A2`` is symmetric under that swap, so the swap is an
    isometry.  It fixes ``a1 + a2``, of square ``-2``, and negates
    ``a1 - a2``, of square ``-6``: the invariant and coinvariant lattices are
    both of rank one and their discriminant groups have orders two and six.
    """
    lattice = Lattices(ZZ)("A2")
    labels = lattice.module_generating_set()
    first, second = lattice.module_generators()
    return lattice, lattice.Aut()({labels[0]: second, labels[1]: first})


def _a1_squared_swap():
    r"""Return A1 + A1 with the involution exchanging the two summands."""
    lattice = Lattices(ZZ)("A1") + Lattices(ZZ)("A1")
    labels = lattice.module_generating_set()
    first, second = lattice.module_generators()
    return lattice, lattice.Aut()({labels[0]: second, labels[1]: first})


def _negation(summand):
    r"""Return ``-1`` in ``O(summand)``, an isometry of every lattice."""
    return summand.Aut()(
        {
            label: -summand.module_generator(label)
            for label in summand.module_generating_set()
        }
    )


def test_the_four_sign_pairs_on_the_swap_split_of_u_glue_to_all_of_o_u() -> None:
    r"""``O(U)`` has order four and is the centralizer of the swap.

    ``O(U) = {1, -1, s, -s}`` for the swap ``s`` (it permutes the two isotropic
    lines ``ZZe``, ``ZZf`` up to sign), so it is abelian and centralizes ``s``.
    The swap splits ``U`` into ``Z(e+f) + Z(e-f) = <2> + <-2>``; each summand has
    orthogonal group ``{1, -1}``, and each discriminant group has order two, so
    every one of the four sign pairs preserves the glue and extends.
    """
    lattice, swap = _hyperbolic_swap()
    extension = swap.primitive_extension()
    invariant_summand = extension.invariant.inclusion().domain()
    coinvariant_summand = extension.orthogonal_complement.inclusion().domain()
    one = lattice.Aut().one()
    plus, minus = invariant_summand.Aut().one(), _negation(invariant_summand)
    coplus, cominus = coinvariant_summand.Aut().one(), _negation(coinvariant_summand)

    assert lattice.Aut().cardinality() == 4
    assert extension.centralizer_group().cardinality() == 4

    for invariant_part in (plus, minus):
        for coinvariant_part in (coplus, cominus):
            assert extension.pair_preserves_glue_graph(invariant_part, coinvariant_part)

    identity = extension.centralizer_element(plus, coplus)
    swap_again = extension.centralizer_element(plus, cominus)
    negated_swap = extension.centralizer_element(minus, coplus)
    negation = extension.centralizer_element(minus, cominus)
    assert identity == one
    assert swap_again == swap
    assert negation * negation == one
    assert all(
        negation(generator) == -generator for generator in lattice.module_generators()
    )
    assert negated_swap == negation * swap
    assert negated_swap != swap
    assert negated_swap != negation


def test_the_a2_diagram_involution_reassembles_across_a_nontrivial_glue() -> None:
    lattice, involution = _a2_diagram_involution()
    extension = involution.primitive_extension()

    assert extension.invariant.module_rank() == 1
    assert extension.orthogonal_complement.module_rank() == 1
    assert extension.invariant.discriminant_group().cardinality() == 2
    assert extension.orthogonal_complement.discriminant_group().cardinality() == 6
    # A_{Z(a1-a2)} is cyclic of order six, on which negation acts
    # non-trivially; the glue subgroup is its subgroup of order two, and the
    # index of the orthogonal sum is that order.
    assert extension.index() == 2
    assert extension.invariant_gluing_subgroup().cardinality() == 2
    glue = extension.glue()
    assert glue.domain().cardinality() == 2
    assert glue.codomain().cardinality() == 2
    assert glue.codomain().inclusion().codomain().cardinality() == 6

    invariant_part = extension.invariant_restriction(involution)
    coinvariant_part = extension.coinvariant_restriction(involution)
    assert extension.pair_preserves_glue_graph(invariant_part, coinvariant_part)
    assert extension.centralizer_element(invariant_part, coinvariant_part) == involution


def test_the_a1_squared_swap_centralizer_splits_one_shell_in_two() -> None:
    lattice, involution = _a1_squared_swap()
    extension = involution.primitive_extension()
    first, second = lattice.module_generators()
    invariant = first + second
    anti_invariant = first - second

    shell = lattice.vectors_of_square(-4)
    assert shell.cardinality() == 4

    # Signed permutations identify the two vectors in O(A1^2), while the
    # centralizer of the swap is {+/-1, +/-swap}; it preserves the invariant
    # and anti-invariant lines separately.
    labels = lattice.module_generating_set()
    sign_change = lattice.Aut()({labels[0]: first, labels[1]: -second})
    assert sign_change(invariant) == anti_invariant

    representatives = extension.equivariant_vector_orbit_representatives(-4)
    assert representatives.cardinality() == 2
    assert all(representative in shell for representative in representatives)
    assert sum(involution(representative) == representative for representative in representatives) == 1
    assert sum(involution(representative) == -representative for representative in representatives) == 1


def test_the_a1_squared_swap_centralizer_separates_invariant_and_anti_invariant_vectors() -> None:
    lattice, involution = _a1_squared_swap()
    centralizer = involution.primitive_extension().centralizer_group()
    first, second = lattice.module_generators()
    invariant = first + second
    anti_invariant = first - second

    assert invariant.q() == -4
    assert anti_invariant.q() == -4
    labels = lattice.module_generating_set()
    sign_change = lattice.Aut()({labels[0]: first, labels[1]: -second})
    assert sign_change(invariant) == anti_invariant

    assert centralizer.vectors_are_equivalent(invariant, -invariant)
    assert centralizer.vectors_are_equivalent(anti_invariant, -anti_invariant)
    assert not centralizer.vectors_are_equivalent(invariant, anti_invariant)


def _cubic_cyclic_permutation():
    r"""Return ``I_3`` with the cyclic permutation of its three coordinates.

    The permutation ``e1 -> e2 -> e3 -> e1`` is an isometry of ``I_3`` of
    order three.  It fixes exactly the diagonal ``ZZ(e1 + e2 + e3)``, of
    square three, and its coinvariant lattice is the rank-two root lattice
    orthogonal to that diagonal, whose Gram matrix is ``[[2,-1],[-1,2]]``.
    Both discriminant groups are cyclic of order three, and the orthogonal
    sum of the two summands has index three in ``I_3``.

    ``I_3`` is odd and its coinvariant summand is even, so this is the
    specimen on which the glue and the pair criterion have to be read on the
    ``QQ/ZZ``-valued bilinear discriminant forms although one summand
    supports a quadratic one.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    labels = lattice.module_generating_set()
    first, second, third = lattice.module_generators()
    return lattice, lattice.Aut()(
        {labels[0]: second, labels[1]: third, labels[2]: first}
    )


def test_the_cubic_cyclic_permutation_glues_an_odd_lattice_bilinearly() -> None:
    lattice, rotation = _cubic_cyclic_permutation()
    extension = rotation.primitive_extension()

    assert not lattice.is_even()
    assert extension.invariant.module_rank() == 1
    assert extension.orthogonal_complement.module_rank() == 2
    assert extension.orthogonal_complement.inclusion().domain().is_even()

    assert not extension.glue().is_quadratic()
    assert extension.invariant.discriminant_group().cardinality() == 3
    assert extension.orthogonal_complement.discriminant_group().cardinality() == 3
    assert extension.index() == 3
    assert extension.invariant_gluing_subgroup().cardinality() == 3


def test_negating_one_summand_of_the_cubic_split_breaks_the_glue_graph() -> None:
    _lattice, rotation = _cubic_cyclic_permutation()
    extension = rotation.primitive_extension()
    invariant_summand = extension.invariant.inclusion().domain()
    coinvariant_summand = extension.orthogonal_complement.inclusion().domain()

    # gamma is injective on a group of order three, so ``(x, -gamma x)`` lies
    # on the graph only where ``gamma x = -gamma x``, that is only at zero.
    # A pair that is the identity on one summand and negation on the other is
    # therefore an isometry of the orthogonal sum that does not extend to
    # I_3, and Nikulin's criterion says so.
    assert not extension.pair_preserves_glue_graph(
        invariant_summand.Aut().one(), _negation(coinvariant_summand)
    )
    assert not extension.pair_preserves_glue_graph(
        _negation(invariant_summand), coinvariant_summand.Aut().one()
    )
