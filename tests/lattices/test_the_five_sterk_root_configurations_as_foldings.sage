r"""Semantic exploration: Sterk's five root configurations as foldings.

H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207
(1991), 4.3.5--4.3.9, pp. 19--24, prints the chamber at each of the five `0`-cusps of
\(\Gamma_{En,2}\).  This exploration reads those five chambers as **one operation**: fold a root
family by an involution of its span that is an isometry of it.

The two families are the 22-root \(\Phi_{(18,2,0)}\) and the 19-root \(\Phi_{(18,0,0)}\), both of them
in the lattice the library calls `T_dP`.  A fold of the roots \(r_v\) by an involution \(g\) of
their span takes the orbit sums \(s_O=\sum_{v\in O}r_v\); each is fixed by \(g\), so the folded
family lies in the invariant lattice \(W^g\), and the anti-invariant lattice is its orthogonal
complement in the span of the roots.  When \(g\) permutes the roots it is written
\(g(\sum_v a_v r_v)=\sum_v a_v r_{\sigma v}\) with \(\sigma\) a permutation of the vertices; when it
does not, it is written by the images of the roots.

What the fold decides.  An involution of the roots' span is given by its images: a permutation of
the roots, when it carries roots to roots, or the images themselves when it does not.  The two
forms are one datum, and the operation decides it the same way --- the rational relations must be
carried to relations, the pairings must be kept, the map must be a symmetry of the span's lattice
and must be an involution --- and then takes the orbit sums that are roots, rescaling a sum that is
a multiple of a point of the span.  A symmetry of the Coxeter diagram need not be an isometry: the
diagram records the bond \(m_{vw}\), and for roots of equal square the bond is \(|b(r_v,r_w)|\),
so a symmetry may reverse a pairing.

Three of the five folds are by permutations of the roots: 4.3.5 and 4.3.8 by two involutions of the
22-root family, 4.3.6 by the reversal of the 19-root one.  The other two are by involutions that do
not permute the roots, and they cannot be: the 22 roots have eight diagram automorphisms and
folding by all of them returns 4.3.5, 4.3.8, the identity's own family and two fourteen-root
families of invariant signature \((1,10)\), where every printed chamber's is \((1,9)\).  Sterk's
third is what the archived folding calls reflection-twisted and its fifth is the orthogonal
reflection in the span of the eight even-indexed roots, which negates them and carries each
odd-indexed root to the sum of itself with its two neighbours.  Both are written as the images of
the roots, and every number below comes from a fold: the card supplies the expected values.

The epistemic status.  The counts, the squares, the two lattices and their signatures are exact
computations of the operation, checked against card `029J`'s `cusp_diagrams` row `gamma-en-2`,
read by tag; the statement that the folded families *are* Sterk's printed chambers is carried by
those card rows and by Sterk's printed statements, not proved here.  The one fact this exploration
establishes that the rows alone do not is that each folded root is a fixed point of the involution
that produced it, and that the orbit sums the fold discards are the isotropic ones.
"""

from sage_extensions.all import *


_STATEMENTS = {
    "Sterk_1": "4.3.5",
    "Sterk_2": "4.3.6",
    "Sterk_3": "4.3.7",
    "Sterk_4": "4.3.8",
    "Sterk_5": "4.3.9",
}


def _chamber(statement):
    r"""Return card `029J`'s row of the chamber ``statement`` prints."""
    return next(
        row
        for row in card("cusp_diagrams", "029J")["rows"]["gamma-en-2"]
        if row["statement"] == statement
    )


def _wall_vectors(statement):
    r"""Return the card's walls of ``statement`` as vectors of \(T_{En}\)."""
    lattice = NamedLattices.TEn
    labels = tuple(lattice.module_generating_set())
    return tuple(
        lattice.linear_combination(
            {
                label: lattice.base_ring()(coordinate)
                for label, coordinate in zip(labels, coordinates)
                if coordinate
            }
        )
        for coordinates in _chamber(statement)["wall_vectors"]
    )


def _signature(lattice):
    return tuple(int(index) for index in lattice.signature())


def test_each_folded_root_is_a_fixed_point_of_the_involution_that_produced_it() -> None:
    r"""An orbit sum \(\sum_{v\in O}r_v\) is fixed by \(g\), so it lies in \(W^g\).

    Every root of each of the five folded families is a point of its fold's invariant lattice, and
    the isometry fixes it: \(g(s_O)=s_O\).  The sums a fold discards are the ones that are no roots,
    and at these five folds each of them is isotropic --- Sterk's fourth has the one the archived
    folding records as invariant but not a root, \(v_{22}+v_{21}\), and the third and fifth have
    orbit sums of square zero from the pairs a twisted involution negates.
    """
    for name, folding in Sterk.foldings().items():
        isometry = folding.isometry()
        invariant = folding.invariant_lattice()

        assert isometry * isometry == isometry.parent().identity()
        assert all(
            isometry(invariant.inclusion()(root)) == invariant.inclusion()(root)
            for root in folding.roots()
        )
        assert all(int(discarded.q()) == 0 for discarded in folding.discarded_sums())
        assert int(invariant.module_rank()) == 10


def test_the_two_lattices_of_each_fold_decompose_the_span_of_the_roots() -> None:
    r"""\(W^g\) and its complement are orthogonal and span the roots' span.

    For an involution the two ranks add to the rank of the span, and the signatures add too:
    each fold's span is a \((1,17)\) lattice, its invariant lattice a \((1,9)\) one and its
    anti-invariant lattice a \((0,8)\) one.  The \((1,9)\) is not a coincidence of the fold: it is
    the signature card `029J`'s own wall vectors span at every one of the five cusps.
    """
    for name, folding in Sterk.foldings().items():
        span = folding.span()
        invariant = folding.invariant_lattice()
        anti_invariant = folding.anti_invariant_lattice()
        wall_span = NamedLattices.TEn.primitive_sublattice_from(_wall_vectors(_STATEMENTS[name]))

        assert int(invariant.module_rank()) + int(anti_invariant.module_rank()) == int(
            span.module_rank()
        )
        assert _signature(span) == (1, 17)
        assert _signature(invariant) == (1, 9)
        assert _signature(anti_invariant) == (0, 8)
        assert _signature(invariant) == _signature(wall_span)


def test_the_five_folded_families_carry_the_card_counts_and_squares() -> None:
    r"""The folded families are the five printed chambers by their counts and their squares.

    Card `029J` stores, per statement, the walls of the chamber and their count; the folded family
    has that count and those squares, and its diagram is rooted in the invariant lattice rather
    than in the ambient one.
    """
    for name, folding in Sterk.foldings().items():
        walls = _wall_vectors(_STATEMENTS[name])

        assert int(folding.roots().cardinality()) == _chamber(_STATEMENTS[name])["wall_count"]
        assert tuple(sorted(int(root.q()) for root in folding.roots())) == tuple(
            sorted(int(wall.q()) for wall in walls)
        )
        assert folding.folded_diagram().root_realization() is folding.invariant_lattice()


def test_the_five_folded_lattices_answer_their_two_elementary_invariants() -> None:
    r"""All ten lattices of the five folds are even 2-elementary, and the operation answers Nikulin's triple.

    Nikulin's \((r,a,\delta)\) is the rank, the length of the discriminant group and the parity of
    its form.  For a nondegenerate integral lattice \(|A_L|=|\det L|\), so a 2-elementary
    discriminant group has \(2^a=|\det L|\) and \(r=\operatorname{rank}L\); the answer is checked
    against the lattice's own rank and determinant rather than against a printed table.
    """
    for _name, folding in Sterk.foldings().items():
        for lattice, invariant in zip(
            (folding.invariant_lattice(), folding.anti_invariant_lattice()),
            folding.two_elementary_invariants(),
            strict=True,
        ):
            assert int(invariant[0]) == int(lattice.module_rank())
            assert 2 ** int(invariant[1]) == abs(int(lattice.determinant()))
            assert int(invariant[2]) in (0, 1)
