r"""A value a page states is recorded beside the row's, and never decides the row.

``tests/coble_gamma_co_2_incidence_rows.py`` reports what a row of the
Tits-building incidence returned.  The numbers the issue compares those rows
with -- one edge for ``O(T_Co)``, the 569160-edge integral archive's
``(569160, 527, 189720)`` for the two kernel rows and its degrees 1080 and 3 --
are statements by other sources, so the driver prints them beside what it
computed and keeps the agreement as a recorded answer.

What the row's status is reached with is the row's own contract: the endpoints
of an edge are cusps of the row, no two edges share their endpoints, and every
cusp carries an edge.  A computed value that differs from a stated one is
therefore a disagreement in the record, not a failed job, and the same run
returns the same relation whether or not a page's number is beside it.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_value_that_differs_from_the_stated_one_is_recorded_and_does_not_decide_the_row():
    r"""A disagreement is recorded, and the row that disagreed is still decided.

    The comparison answers whether the two values agree -- ``False`` for the
    archive's kernel count against a relation of one edge, ``True`` for the
    archive's plane degree against a degree sequence of three -- and neither
    answer reaches the row's status: the row of ``O(U + U)`` decides on its own
    contract, with its own counts, whether or not a number beside it agrees.
    """
    differs = incidence_page_comparison(
        "row", "the kernel row's counts (edges, lines, planes)",
        (1, 1, 1), (569160, 527, 189720),
        "the 569160-edge integral archive of #286's table",
    )
    agrees = incidence_page_comparison(
        "row", "the plane cusps' degrees", (3,), (3,),
        "the 569160-edge integral archive of #286's table",
    )
    assert differs is False
    assert agrees is True

    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    outcome = incidence_row_outcome(lattice, lattice.Aut(), "O(U + U)", 3600)
    assert outcome.status is RowStatus.DECIDED
    assert outcome.counts == (1, 1, 1)
    assert incidence_page_comparison(
        "row", "the kernel row's counts (edges, lines, planes)",
        outcome.counts, (569160, 527, 189720),
        "the 569160-edge integral archive of #286's table",
    ) is False
    assert outcome.status is RowStatus.DECIDED
