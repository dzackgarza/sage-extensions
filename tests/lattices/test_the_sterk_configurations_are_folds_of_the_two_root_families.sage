r"""Sterk's five chamber configurations, and which of them are folds of the two root families.

H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*, Math. Z. 207
(1991), 4.3.5--4.3.9, pp. 19--24, prints the chamber at each of the five `0`-cusps of
\(\Gamma_{En,2}\): its walls as vectors of \(T_{En} = U\oplus U(2)\oplus E8(-2)\), twelve, ten,
twelve, eleven and fourteen of them.  Card `029J`'s `cusp_diagrams` row `gamma-en-2` stores those
walls and that count per statement, by tag, and this test reads the counts and the wall vectors
there rather than transcribing them.

`Sterk.sterk_roots()` returns the same five configurations as roots of \(T_{dP}\), and three of them
are folds of the two stored root families: the twelve-root family of 4.3.5 and the eleven-root
family of 4.3.8 by two involutions of the 22-root `(18,2,0)` family, and the ten-root family of
4.3.6 by the reversal of the 19-root `(18,0,0)` family.  The fourth and fifth are no folds of
either family: the 22 roots have eight Gram-preserving permutations and the 19 roots two, and
folding by all of them returns the three above, the identity's own family, and two further
fourteen-root families of no printed chamber.

The card is also the oracle for the folded lattice.  At every one of the five cusps the walls span
a rank-ten lattice of signature \((1,9)\) inside \(T_{En}\); the fold's invariant lattice is a
rank-ten lattice of that signature, and its orthogonal complement inside the roots' rank-eighteen
span is negative definite.
"""

from sage_extensions.all import *


_STATEMENTS = {
    "Sterk_1": "4.3.5",
    "Sterk_2": "4.3.6",
    "Sterk_3": "4.3.7",
    "Sterk_4": "4.3.8",
    "Sterk_5": "4.3.9",
}

_FOLDING_PERMUTATIONS = {
    "Sterk_1": (8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7, 18, 19, 16, 17, 20, 21),
    "Sterk_2": (16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 18, 17),
}
_FOLDING_PERMUTATIONS["Sterk_4"] = Sterk.sterk4_root_permutation()


def _chamber(statement):
    r"""Return card `029J`'s `cusp_diagrams` row of ``statement``, read by tag."""
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


def _root_family(name):
    r"""Return the roots ``name`` folds: the 22-root family, or the 19-root one for ``Sterk_2``."""
    if name == "Sterk_2":
        roots = Sterk.roots_18_0_0()
        return tuple(roots[f"w{index}"] for index in range(1, 20))
    roots = Sterk.roots_18_2_0()
    return tuple(roots[f"v{index}"] for index in range(1, 23))


def _fold(name):
    r"""Return the fold of ``name``'s root family by its stored involution."""
    return CoxeterDiagrams().from_roots(_root_family(name)).fold(_FOLDING_PERMUTATIONS[name])


def _carried(name):
    r"""Return the folded roots of ``name`` as vectors of \(T_{dP}\), their family's lattice."""
    folding = _fold(name)
    return tuple(
        folding.span().inclusion()(folding.invariant_lattice().inclusion()(root))
        for root in folding.roots()
    )


def _pairings(lattice, vectors):
    vectors = tuple(vectors)
    return sorted(
        int(lattice.b(left, right))
        for position, left in enumerate(vectors)
        for right in vectors[:position]
    )


def _signature(lattice):
    return tuple(int(index) for index in lattice.signature())


def _squares(vectors):
    return sorted(int(vector.q()) for vector in vectors)


def test_the_five_configurations_have_the_card_wall_counts() -> None:
    configurations = Sterk.sterk_roots()

    assert {
        name: configurations[name].cardinality() for name in _STATEMENTS
    } == {name: _chamber(statement)["wall_count"] for name, statement in _STATEMENTS.items()}


def test_the_folded_families_carry_the_card_squares_and_pairings() -> None:
    for name in ("Sterk_1", "Sterk_2", "Sterk_4"):
        walls = _wall_vectors(_STATEMENTS[name])
        folded = _carried(name)

        assert _squares(folded) == _squares(walls)
        assert _pairings(NamedLattices.TdP, folded) == _pairings(NamedLattices.TEn, walls)


def test_the_folded_lattices_have_the_card_chamber_signature() -> None:
    for name in ("Sterk_1", "Sterk_2", "Sterk_4"):
        folding = _fold(name)
        wall_span = NamedLattices.TEn.primitive_sublattice_from(_wall_vectors(_STATEMENTS[name]))

        assert wall_span.module_rank() == 10
        assert _signature(wall_span) == (1, 9)
        assert folding.invariant_lattice().module_rank() == wall_span.module_rank()
        assert _signature(folding.invariant_lattice()) == _signature(wall_span)
        assert (
            folding.invariant_lattice().module_rank()
            + folding.anti_invariant_lattice().module_rank()
            == folding.span().module_rank()
        )
        assert _signature(folding.span()) == (1, 17)
        assert _signature(folding.anti_invariant_lattice()) == (0, 8)


def test_the_folded_configurations_are_the_constructions_sterk_returns() -> None:
    for name in ("Sterk_1", "Sterk_2", "Sterk_4"):
        folded = _carried(name)
        stored = tuple(Sterk.sterk_roots()[name])

        assert Set(folded) == Set(stored)


def _card_key(statement):
    r"""Return the invariants card `029J` stores for ``statement``'s chamber."""
    walls = _wall_vectors(statement)
    span = NamedLattices.TEn.primitive_sublattice_from(walls)
    return (
        _chamber(statement)["wall_count"],
        tuple(_squares(walls)),
        tuple(_pairings(NamedLattices.TEn, walls)),
        int(span.module_rank()),
        _signature(span),
    )


def _fold_key(folding):
    r"""Return the same invariants of a folded family and the lattice it spans."""
    carried = tuple(
        folding.span().inclusion()(folding.invariant_lattice().inclusion()(root))
        for root in folding.roots()
    )
    return (
        int(folding.roots().cardinality()),
        tuple(_squares(carried)),
        tuple(_pairings(NamedLattices.TdP, carried)),
        int(folding.invariant_lattice().module_rank()),
        _signature(folding.invariant_lattice()),
    )


def test_the_two_root_families_fold_only_to_the_three_chambers() -> None:
    r"""The two families have eight and two diagram automorphisms, and three folds are chambers."""
    card_keys = {_card_key(statement) for statement in _STATEMENTS.values()}

    hits = set()
    for name in ("Sterk_1", "Sterk_2"):
        diagram = CoxeterDiagrams().from_roots(_root_family(name))
        cardinality = int(diagram.cardinality())
        for automorphism in diagram.Aut():
            permutation = tuple(int(automorphism(index)) - 1 for index in range(1, cardinality + 1))
            key = _fold_key(diagram.fold(permutation))
            if key in card_keys:
                hits.add(key)

    assert tuple(sorted(hits)) == tuple(
        sorted(_card_key(statement) for statement in ("4.3.5", "4.3.6", "4.3.8"))
    )
    assert tuple(sorted(hits)) == tuple(
        sorted(_fold_key(_fold(name)) for name in ("Sterk_1", "Sterk_2", "Sterk_4"))
    )
