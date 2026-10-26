r"""Subdiagrams of Coxeter diagrams, their types, and their automorphism orbits.

The affine \(\tilde A_2\) diagram is the triangle with every bond \(3\); its
automorphism group is the symmetric group on the three vertices.  Its
induced subdiagrams are the empty one, three vertices, three edges and the
triangle: the first seven are of type \(A_0\), \(A_1\), \(A_2\), hence
elliptic, and the triangle is parabolic.
"""

from sage_extensions.all import *


def affine_a2():
    return CoxeterDiagrams()([[1, 3, 3], [3, 1, 3], [3, 3, 1]])


def d4():
    r"""The star \(D_4\): centre \(0\) joined by bonds \(3\) to the outer nodes \(1,2,3\)."""
    return CoxeterDiagrams()(
        [[1, 3, 3, 3], [3, 1, 2, 2], [3, 2, 1, 2], [3, 2, 2, 1]]
    )


def test_affine_a2_has_seven_elliptic_subdiagrams_and_one_parabolic() -> None:
    diagram = affine_a2()

    assert diagram.subdiagram_poset().cardinality() == 8
    assert diagram.elliptic_subdiagrams().cardinality() == 7
    assert diagram.parabolic_subdiagrams().cardinality() == 1
    assert diagram.is_parabolic()


def test_the_maximal_elliptic_subdiagrams_of_affine_a2_are_its_three_edges() -> None:
    r"""Each edge is of type \(A_2\), and the only subdiagram above it is the parabolic triangle."""
    maximal = affine_a2().maximal_elliptic_subdiagrams()

    assert maximal.cardinality() == 3
    for edge in maximal:
        assert edge.cardinality() == 2
        assert edge.is_elliptic()
        assert edge.coxeter_group().cardinality() == 6


def test_the_automorphism_group_of_affine_a2_is_s3_with_three_elliptic_orbits() -> None:
    r"""\(\operatorname{Aut}(\tilde A_2)\cong S_3\); the elliptic orbits are empty, vertices, edges."""
    diagram = affine_a2()

    assert diagram.Aut().cardinality() == 6
    assert diagram.Aut().is_isomorphic(Groups.S(3))
    assert diagram.elliptic_subdiagram_orbits().cardinality() == 3
    assert diagram.parabolic_subdiagram_orbits().cardinality() == 1


def test_triality_fuses_the_sixteen_subdiagrams_of_d4_into_eight_orbits_ordered_by_inclusion() -> None:
    r"""\(D_4\): all \(2^4\) induced subdiagrams are elliptic, and \(\operatorname{Aut}=S_3\) permutes the outer nodes.

    An orbit is fixed by whether it holds the centre and by how many outer
    nodes it holds, so there are \(2\cdot 4 = 8\) orbits.  In the orbit order
    (\([H]\leq[K]\) when some member of \([H]\) is induced in some member of
    \([K]\)) the centre is not below the three outer nodes, although it is
    smaller, while an outer node and an outer pair are.
    """
    diagram = d4()
    centre = diagram.index_set()[0]
    poset = diagram.elliptic_subdiagram_orbit_poset()

    subdiagram_of_rank = diagram.induced_subdiagrams().ranking_map().inverse()

    def orbit(holds_centre: bool, outer_count: int):
        return next(
            member
            for member in poset
            if (centre in subdiagram_of_rank(member.representative()).index_set()) == holds_centre
            and subdiagram_of_rank(member.representative()).cardinality()
            == outer_count + (1 if holds_centre else 0)
        )

    assert diagram.Aut().cardinality() == 6
    assert diagram.elliptic_subdiagrams().cardinality() == 16
    assert poset.cardinality() == 8

    three_outer = orbit(False, 3)
    assert not poset.le(orbit(True, 0), three_outer)
    assert not poset.le(orbit(True, 1), three_outer)
    assert poset.le(orbit(False, 1), three_outer)
    assert poset.le(orbit(False, 2), three_outer)
    assert poset.le(orbit(False, 2), orbit(True, 2))


def test_root_pairings_separate_parallel_divergent_and_meeting_mirrors() -> None:
    r"""\(b^2-q(r)q(s)\) is \(0\), \(5\), \(-3\) for the three Grams below: parallel, divergent, meeting.

    The first two both have bond \(\infty\), so their Coxeter matrices agree;
    the third has bond \(3\).
    """
    parallel = CoxeterDiagrams()(Lattices(ZZ)([[-2, 2], [2, -2]]).module_generators())
    divergent = CoxeterDiagrams()(Lattices(ZZ)([[-2, 3], [3, -2]]).module_generators())
    meeting = CoxeterDiagrams()(Lattices(ZZ)([[-2, 1], [1, -2]]).module_generators())

    assert parallel.coxeter_matrix() == divergent.coxeter_matrix()
    assert parallel.mirrors_are_parallel(0, 1)
    assert not parallel.mirrors_are_divergent(0, 1)
    assert divergent.mirrors_are_divergent(0, 1)
    assert not divergent.mirrors_are_parallel(0, 1)
    assert meeting.coxeter_entry(0, 1) == 3
    assert not meeting.mirrors_are_parallel(0, 1)
    assert not meeting.mirrors_are_divergent(0, 1)
