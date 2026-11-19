r"""Semantic exploration: Sterk's five root configurations as foldings.

H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207
(1991), 4.3.5--4.3.9, pp. 19--24, prints the chamber at each of the five `0`-cusps of
\(\Gamma_{En,2}\).  This exploration reads those five chambers as **one operation**: fold a root
family by a diagram involution that lifts to an isometry of its span.

The two families are the 22-root \(\Phi_{(18,2,0)}\) and the 19-root \(\Phi_{(18,0,0)}\), both of them
in the lattice the library calls `T_dP`.  A fold of the roots \(r_v\) by an involution
\(g(\sum_v a_v r_v)=\sum_v a_v r_{\sigma v}\) takes the orbit sums \(s_O=\sum_{v\in O}r_v\); each is
fixed by \(g\), so the folded family lies in the invariant lattice \(W^g\), and the anti-invariant
lattice is its orthogonal complement in the span of the roots.

What the fold decides, and what it does not.  A permutation of the roots lifts to an isometry
exactly when it keeps the pairings, and a symmetry of the Coxeter diagram need not: the diagram
records the bond \(m_{vw}\), and for roots of equal square the bond is \(|b(r_v,r_w)|\).  Three of
the five folds are by permutations of the roots; the other two are by involutions of the span that
do not permute them --- Sterk's third is what the archived folding calls reflection-twisted, and
its fifth is written as three-term sums --- which is why the operation has a second datum, the
images of the roots.  Both are read here, and nothing else is: every number below comes from a
fold, and the card supplies the expected values.

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
