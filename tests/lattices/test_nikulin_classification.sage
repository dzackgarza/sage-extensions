r"""Nikulin's classification table and its smallest realization routes.

A K3 surface with a non-symplectic involution has invariant lattice determined
up to isometry by \((r, a, \delta)\): the rank, the length of the discriminant
group, and Nikulin's parity invariant.  There are 75 such triples, and each
invariant lattice is hyperbolic, of signature \((1, r-1)\).

The catalogue is a literal 75-row source table.  Runtime construction here
uses the smallest rows covering the one-block and orthogonal-sum branches;
the nontrivial gluing route has its dedicated A1^8 specimen in the focused
two-elementary tests.  This avoids reconstructing all 75 lattices merely to
recheck source data.
"""

from sage_extensions.all import *


def test_nikulins_catalogues_have_the_archived_numbers_of_rows() -> None:
    assert TwoElementary.cardinality() == 75
    assert NegativeDefTwoElementary.cardinality() == 51


def test_small_hyperbolic_table_rows_realise_one_block_and_biproduct_routes() -> None:
    for triple in ((1, 1, 1), (3, 1, 1)):
        rank, _length, _delta = triple
        lattice = TwoElementary[triple]
        assert lattice.signature_pair() == signature_pair(1, rank - 1)
        assert EvenTwoElementaryLattices(ZZ)(lattice).two_elementary_invariants() == nikulin_invariants(*triple)


def test_small_negative_definite_table_row_is_realised() -> None:
    triple = (1, 1, 1)
    (lattice,) = NegativeDefTwoElementary[triple]
    rank, _length, _delta = triple
    assert lattice.signature_pair() == signature_pair(0, rank)
    assert EvenTwoElementaryLattices(ZZ)(lattice).two_elementary_invariants() == nikulin_invariants(*triple)
