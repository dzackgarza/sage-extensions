r"""Recorded ``(r,a,delta)`` invariants from the archived Oscar verification notebook.

The notebook computed these rows from the discriminant quadratic form of the
six period lattices.  The live owner already implements Nikulin's invariant;
this archive specimen preserves the recorded mathematical table rather than
porting the notebook's temporary Oscar helper.
"""

from sage_extensions.all import *


def _period_lattices():
    return (
        (NamedLattices.Sdp, (2, 2, 0)),
        (NamedLattices.SEn, (10, 10, 0)),
        (NamedLattices.LpNik, (14, 8, 0)),
        (NamedLattices.TdP, (20, 2, 0)),
        (NamedLattices.TEn, (12, 10, 0)),
        (NamedLattices.LmNik, (8, 8, 0)),
    )


def test_archived_period_lattices_retain_the_recorded_two_elementary_rows() -> None:
    for lattice, (rank, length, delta) in _period_lattices():
        assert EvenTwoElementaryLattices(ZZ)(lattice).two_elementary_invariants() == nikulin_invariants(rank, length, delta)


def test_all_six_archived_period_rows_are_coeven() -> None:
    for lattice, _row in _period_lattices():
        assert EvenTwoElementaryLattices(ZZ)(lattice).two_elementary_invariants().delta() == 0
