r"""The index of a finite-character subgroup is the index of its finite image.

A subgroup of ``O(L)`` cut out by the discriminant, determinant and spinor
characters is the full preimage of a subgroup of a finite group, so its cosets
in ``O(L)`` are the cosets of that image, and their number is a quotient of two
finite group orders rather than an enumeration of points.  The extreme case is
``Otilde(T_Co) = ker(O(T_Co) -> O(A_{T_Co}))``, whose coset space is the whole
finite image: ``46998591897600`` points, which no enumeration of cosets returns.
The expected number here is lattice card `6JRR`'s, read by tag from
``tests/cards/lattice-database-enriques.json``.

The dispatch is checked in both directions.  A subgroup with complete character
data takes the finite-image route, and a subgroup without them keeps the
generic route, which realizes the coset space and counts it; the small models
below are ones where that count is affordable, so the fast route is never taken
on trust.  A finite image order is certified from the discriminant form alone
only under all four hypotheses of Nikulin's theorem -- even, indefinite,
nondegenerate, 2-elementary -- and each lattice below that fails one of them is
asserted not to be certified.
"""

from sage_extensions.all import *


def test_the_index_of_the_discriminant_kernel_of_the_coble_lattice_is_the_discriminant_group_order():
    r"""``[O(T_Co) : Otilde(T_Co)] = |O(A_{T_Co}, q)|``, card `6JRR` of the database.

    The two orders agree because ``rho_{T_Co}`` is onto (the lattice is even,
    indefinite and 2-elementary), so the index is the finite image's own order
    and both routes above the subgroup answer it without listing a coset.
    """
    lattice = NamedLattices.Tco
    kernel = lattice.stable_orthogonal_group()
    expected = card("discriminant_forms", "6JRR")["orthogonal_group_order"]
    assert kernel.index() == expected
    assert kernel.finite_character_quotient().index() == expected


def test_the_two_routes_to_a_small_discriminant_kernel_agree():
    r"""On ``U(2)`` the finite-image index, its quotient and the coset count are all ``2``.

    ``U(2)`` is even, indefinite and 2-elementary, and its discriminant group is
    the hyperbolic plane over ``F_2``, whose orthogonal group has order two, so
    ``rho`` is onto and drops a subgroup of index two.  The computed image
    ``rho(O(L))`` is read here as well, so the index is not inferred from the
    order of the target group alone.
    """
    lattice = NamedLattices.U_2
    kernel = lattice.stable_orthogonal_group()
    assert int(lattice.discriminant_image().cardinality()) == 2
    assert kernel.index() == 2
    assert kernel.finite_character_quotient().index() == 2
    assert int(lattice.Aut().left_cosets(kernel).cardinality()) == 2


def test_a_finite_image_outside_the_theorem_keeps_the_generated_route():
    r"""``A_2`` is definite and not 2-elementary: its kernel indexes as its coset space does.

    The image ``rho(O(A_2))`` is still all of ``O(A_{A_2})``, so the two routes
    agree at a nontrivial index, but that is computed from a generating family
    of ``O(L)`` and not certified by the theorem, which does not apply to a
    definite lattice.
    """
    lattice = NamedLattices.A2
    kernel = lattice.stable_orthogonal_group()
    assert lattice.discriminant_representation_is_surjective_by_theorem() is not True
    assert kernel.index() == 2
    assert int(lattice.Aut().left_cosets(kernel).cardinality()) == 2


def test_the_finite_image_order_is_certified_only_under_all_four_hypotheses():
    r"""One lattice per failing hypothesis, and the two certified ones.

    ``U(2)`` and ``T_Co`` meet the hypotheses.  ``<2> + <2>`` is definite;
    ``A_2 + U`` is indefinite and even but ``A_L`` has order three, so it is not
    2-elementary; ``<1> + U`` is odd.  A theorem quoted beyond its hypotheses is
    what these four lines refuse.
    """
    assert NamedLattices.U_2.discriminant_representation_is_surjective_by_theorem() is True
    assert NamedLattices.Tco.discriminant_representation_is_surjective_by_theorem() is True
    definite = Lattices(ZZ)([[2, 0], [0, 2]])
    assert definite.discriminant_representation_is_surjective_by_theorem() is not True
    not_two_elementary = Lattices(ZZ)("A2") + Lattices(ZZ)("U")
    assert not_two_elementary.discriminant_representation_is_surjective_by_theorem() is not True
    odd = Lattices(ZZ)([[1]]) + Lattices(ZZ)("U")
    assert odd.discriminant_representation_is_surjective_by_theorem() is not True


def test_a_subgroup_without_character_data_indexes_by_its_coset_count():
    r"""The generic route survives: a generated subgroup and an uncharacterized predicate.

    Neither subgroup is named by a finite set of characters, so neither has a
    finite image to index by, and ``[G : H]`` is the cardinality of ``G/H``:
    three for a transposition in ``S_3``, six for a 4-cycle in ``S_4``, and
    three for the transposition subgroup re-cut out by a bare predicate.
    """
    symmetric_three = Groups.S(3)
    transposition = symmetric_three((1, 2))
    generated = symmetric_three.subgroup((transposition,))
    assert generated.index() == 3
    assert int(symmetric_three.left_cosets(generated).cardinality()) == 3
    symmetric_four = Groups.S(4)
    four_cycle = symmetric_four((1, 2, 3, 4))
    assert symmetric_four.subgroup((four_cycle,)).index() == 6
    uncharacterized = symmetric_three.predicate_subgroup(
        lambda element: element in generated,
        lambda: "lies in the transposition subgroup",
    )
    assert uncharacterized.character_data_is_complete() is False
    assert uncharacterized.index() == 3
